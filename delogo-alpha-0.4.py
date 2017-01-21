#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# IMPORTANTE: LEIA ANTES DE USAR!
# esse script pede um logo e um vídeo e recodifica esse vídeo embaçando
# as regiões onde acha o logo.
# Como o objetivo é não deixar falsos positivos, os parametros threshold
# tavg e samplef são usados para achar o logo em uma media de frames.
# altere caso haja problemas.
#
# Os parâmetros de codificação em mp4 no final não estão otimizados.
#
# dependências incluem python, moviepy, numpy, ffmpeg, libx264
#   libx265, libfdk_aac
#
# Alteração no método, agora o script primeiro procura no video pelo
# logo e grava os resultados em um arquivo texto .csv. Depois o script
# faz o recode do vídeo. O .csv pode ser alterado pelo usuário de forma 
# a colocar a posição do canto superior esquerdo do logo. O formato das
# entradas deve seguir a ordem:
# 5;0.6434343434;640;24
# 6;1;430;340
# 7;1;430;340
# 8;1;430;340
# 9;0.964352323;358;653
# Vai pintar dos segundos 5 a 9 um quadrado com canto superior esquerdo no
# pont (430,340). Depois eu modifico o HOWTO para explicar essa funcionalidade
#
# O arquivo .csv fica gravado após a recodificação. Se o script for usado de 
# novo, ele pode reutilizar o .csv com a opção "-u"
#
# Usem livremente! @crowseye
#
# diff 0.4: CSV com timestamps.
# diff 0.3: troquei o blur pelo inpaint + median
# diff 0.2: adicionei a procura temporal com maxt, modo lossless
# diff 0.15: adicionei a opção global tsteps, output em HEVC

import cv2,argparse,sys,csv
import numpy as np

from moviepy.editor import VideoFileClip
from numpy import zeros, array, uint8

# command-line variables

parser = argparse.ArgumentParser(description='Este programa vai encontrar e tirar um logo do seu vídeo')
parser.add_argument('-i','--input', help='Vídeo de entrada', required=True)
parser.add_argument('-l','--logo', help='Imagem com logo', required=True)
parser.add_argument('-o','--output', help='Nome do arquivo de saída', required=False)
parser.add_argument('-q','--highq', help='Ativa o modo 2-pass, com bitrate', required=False)
parser.add_argument('-1','--lossless', help='Ativa o modo lossless (x264)', action='store_true', default=False)
parser.add_argument('-u','--use-csv', help='Use arquivo CSV', action='store_true', default=False)
parser.add_argument('-g','--generate-csv', help='Não reencode, só gere CSV', action='store_true', default=False)

args = vars(parser.parse_args())

rate = args['highq']
basename = args['input']
logomarca = args['logo']

if not args['output']:
  outname = basename[:-4] + "-delogo" + basename[-4:]
else:
  outname = args['output']
  
rcsv = args['use_csv']

csvname = basename[:-4] + "-delogo.csv"

# global variables

clip = VideoFileClip(basename)
logo = cv2.imread(logomarca)
fps = clip.fps
h, w = logo.shape[:-1]
border=1
submask = cv2.cvtColor( logo, cv2.COLOR_RGB2GRAY )
_,submask = cv2.threshold( submask, 127, 255, cv2.THRESH_BINARY)
pad = 10
mask = np.zeros(shape=(h+pad,w+pad),dtype=np.uint8)
mask[pad//2:h+pad//2,pad//2:w+pad//2] = submask

# control variables

threshold = .29 # parece ser o limite para opencv ver algo
tavg = 1        # deve acompanhar as mudanças de posição
samplef = 4     # maior = mais rápido e match mais instável
maxt = 15       # até quantos passos devemos dar

# initialize variables

everyf = tavg*fps
tmax = np.zeros(shape=(int(clip.duration/tavg)+3),dtype=float)
box = np.zeros(shape=(int(clip.duration/tavg)+3,2),dtype=int)

# auxiliary functions

def frange(x, y, inc):
  while x < y:
    yield x
    x += inc

def progress_bar(progress):
  barLength = 40 # Modify this to change the length of the progress bar
  status = ""
  if isinstance(progress, int):
    progress = float(progress)
  if not isinstance(progress, float):
    progress = 0
    status = "error: progress var must be float\r\n"
  if progress < 0:
    progress = 0
    status = "Halt...\r\n"
  if progress >= 1:
    progress = 1
    status = "Done...\r\n"
  block = int(round(barLength*progress))
  text = "\rPercent: [{0}] {1:.2f}% {2}".format( "="*block + " "*(barLength-block), progress*100, status)
  sys.stdout.write(text)
  sys.stdout.flush()

# main functions

def average_frame(tinit,tend):
  if tinit < 0:
    tinit = 0
  if tend > clip.duration:
    tend = clip.duration
  avgmatrix = zeros(shape=(clip.h, clip.w, 3), dtype=np.int16)
  totalframes = 0
  for f in frange(tinit, tend, samplef / fps ):
    avgmatrix += clip.get_frame(f)
    totalframes += 1
  avgmatrix = (avgmatrix // totalframes).astype(np.uint8)
  return avgmatrix

def match(haystack,needle):
  padded_frame = np.full(shape=(clip.h+h,clip.w+w,3),fill_value=128,dtype=np.uint8)
  padded_frame[0:clip.h,0:clip.w] = haystack
  res = cv2.matchTemplate(padded_frame,needle, cv2.TM_CCOEFF_NORMED)
  rmin, rmax, loc_min, loc_max = cv2.minMaxLoc(res)
  return [rmax,loc_max]

def generate_timecodes():
  global tmax, box
  print("Matching frames for logo...")
  for x in range(int(clip.duration/tavg)+1):
    favg = average_frame(x*tavg,x*tavg+tavg)
    tmax[x+1],box[x+1] = match(favg.astype(np.uint8),logo)
    progress_bar( x/(clip.duration/tavg) )
  sys.stdout.write('\n')
  tmax[0] = tmax[1]
  box[0,0] = box[1,0]
  box[0,1] = box[1,1]
  tmax[int(clip.duration/tavg)+2] = tmax[int(clip.duration/tavg)+1]
  box[int(clip.duration/tavg)+2,0] = box[int(clip.duration/tavg)+1,0]
  box[int(clip.duration/tavg)+2,1] = box[int(clip.duration/tavg)+1,1]
  return

def draw_blur(frame, x, y):
  padded_frame = np.full(shape=(clip.h+pad,clip.w+pad,3),fill_value=128,dtype=np.uint8)
  padded_frame[pad//2:clip.h+pad//2,pad//2:clip.w+pad//2] = frame
  sub_frame = padded_frame[y:y+h+pad, x:x+w+pad]
  thismask = mask
  if y+h > clip.h:
    thismask = mask[0:clip.h-y+pad,0:w+pad]
  if x+w > clip.w:
    thismask = mask[0:h+pad,0:clip.w-x+pad]
  sub_frame = cv2.inpaint(sub_frame,thismask,5,cv2.INPAINT_TELEA)
  if x == 0 and y == 0:
    sub_frame = cv2.GaussianBlur(sub_frame, (3,7), 7)
  else:
    sub_frame = cv2.medianBlur(sub_frame, 3)
  padded_frame[y:y+sub_frame.shape[0], x:x+sub_frame.shape[1]] = sub_frame
#  cv2.rectangle(padded_frame, (x,y), (x+w+pad,y+h+pad), (0,0,255))
  frame = padded_frame[pad//2:clip.h+pad//2,pad//2:clip.w+pad//2]
  return frame

def process_frames(get_frame,t):
  global tmax,box,everyf
  x = int(t/tavg)
  y = 0
  z = 2
  while tmax[x-y] < threshold and y < maxt and x-y > 0:
    y += 1
  while tmax[x+z] < threshold and z < maxt and x+z < int(clip.duration/tavg)+1:
    z += 1
  frame = clip.get_frame(t)
  frame = draw_blur(frame, box[x-y,0], box[x-y,1])
  frame = draw_blur(frame, box[x+z,0], box[x+z,1])
  return frame

if rcsv:
  with open(csvname, 'r') as f:
    reader = csv.reader(f, delimiter=';')
    x = 0
    for row in reader:
      if x == 0:
        tavg = float(row[0])
        x += 1
      else:
        _, tmax[x], box[x,0], box[x,1] = row
        x += 1
    tmax[0] = tmax[1]
    box[0,0] = box[1,0]
    box[0,1] = box[1,1]
    tmax[x] = tmax[x-1]
    box[x,0] = box[x-1,0]
    box[x,1] = box[x-1,1]
else:
  generate_timecodes()
  file = open(csvname, "w")
  writer = csv.writer(file, delimiter=';')
  writer.writerow([tavg])
  for x in range(int(clip.duration/tavg)+1):
    writer.writerow([x, tmax[x+1], box[x+1,0], box[x+1,1]])
  file.close()

if not args['generate_csv']:
  out = clip.fl(process_frames)
  if args['lossless']:
    out.write_videofile(outname, codec = "libx264", preset = "ultrafast", ffmpeg_params = ['-crf', '0' ], audio_codec = 'libfdk_aac' )  
  elif args['highq']:
    out.write_videofile(outname, codec = "libx265", preset = "medium", bitrate = rate, ffmpeg_params = [ '-pass', '1', '-pix_fmt', 'yuv420p' ], audio_codec = 'libfdk_aac' )  
    out.write_videofile(outname, codec = "libx265", preset = "medium", bitrate = rate, ffmpeg_params = [ '-pass', '2', '-pix_fmt', 'yuv420p' ], audio_codec = 'libfdk_aac' )  
  else:
    out.write_videofile(outname, codec = "libx265", preset = "medium", ffmpeg_params = ['-crf', '16', '-pix_fmt', 'yuv420p'], audio_codec = 'libfdk_aac' )  
