#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# IMPORTANTE: LEIA ANTES DE USAR!
# esse script pede um logo e um vídeo e recodifica esse vídeo embaçando
# as regiões onde acha o logo.
# Como o objetivo é não deixar falsos positivos, os parametros threshold
# tavg, samplef e maxtsteps são usados para achar o logo em uma média de 
# frames. altere caso haja problemas.
#
# Para melhores resultados, use um logo com fundo transparente. O script
# average.py pode lhe ajudar a gerar o logo a partir do vídeo.
#
# Os parâmetros de codificação em mp4 no final não estão otimizados.
#
# dependências incluem python, moviepy, numpy, ffmpeg, libx264
#   libx265, libfdk_aac
#
# para a versão 0.3: CSV editável com os timestamps e parametros de
# codificação melhores. Inpaint ao invés de blur?
#
# Usem livrimente! @crowseye
#
# diff 0.2: adicionei a procura temporal com maxtsteps, modo lossless
# diff 0.15: adicionei a opção global tsteps, output em HEVC

import cv2,argparse,sys
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

args = vars(parser.parse_args())

rate = args['highq']
basename = args['input']
logomarca = args['logo']

if not args['output']:
  outname = basename[:-4] + "-delogo" + basename[-4:]
else:
  outname = args['output']

# global variables

clip = VideoFileClip(basename)
logo = cv2.imread(logomarca) # Arial 9 or 10. Condensed
mask = cv2.equalizeHist(cv2.cvtColor( logo, cv2.COLOR_RGB2GRAY ))
fps = clip.fps
h, w = logo.shape[:-1]

# control variables

threshold = .3  # parece ser o limite para opencv ver algo
tavg = 1        # deve acompanhar as mudanças de posição
samplef = 4     # maior = mais rápido e match mais instável
tsteps = 4      # quantos passos devemos cobrir
maxtsteps = 10  # até quantos passos devemos dar

# initialize variables

everyf = tavg*fps
tmax = zeros(shape=tsteps, dtype=float)
box = zeros(shape=(tsteps,2), dtype=int)
favg = zeros(shape=(tsteps,clip.h, clip.w,3), dtype=int)

# auxiliary functions

def frange(x, y, inc):
  while x < y:
    yield x
    x += inc

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
  avgmatrix = (avgmatrix / totalframes).astype(np.uint8)
  return avgmatrix

def match(haystack,needle,loc_ant):
  res = cv2.matchTemplate(haystack,needle, cv2.TM_CCOEFF_NORMED)
  rmin, rmax, loc_min, loc_max = cv2.minMaxLoc(res)
  return [rmax,loc_max]

def draw_blur(frame, x, y):
#  cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255)) 
  sub_frame = frame[y:y+h, x:x+w]
#  sub_frame = cv2.inpaint(sub_frame,mask,3,cv2.INPAINT_TELEA)
  sub_frame = cv2.GaussianBlur(sub_frame, (3,31), 15)
  frame[y:y+sub_frame.shape[0], x:x+sub_frame.shape[1]] = sub_frame
  return frame

def process_frames(get_frame,t):
  global tmax,favg,everyf
  if t*fps/everyf - np.fix(t*fps/everyf) < 1 / everyf:
    if t == 0:
      for x in range(1,tsteps):
        favg[x] = average_frame(t+(x-1)*tavg,t+x*tavg)
    else:
      for x in range(tsteps-1):
        favg[x] = favg[x+1]
      favg[tsteps-1] = average_frame(t+(tsteps-2)*tavg,t+(tsteps-1)*tavg)
    for x in range(tsteps-1):
      tmax[x],box[x] = match(favg[x].astype(np.uint8),logo,box[x])
    for x in range(maxtsteps):
      tmax[tsteps-1],box[tsteps-1] = match(favg[tsteps-1].astype(np.uint8),logo,box[tsteps-1])
      if tmax[tsteps-1] > threshold or t+(x+tsteps-1)*tavg > clip.duration:
        break
      else: 
        favg[tsteps-1] = average_frame(t+(x+tsteps-1)*tavg,t+(x+tsteps)*tavg)
  frame = clip.get_frame(t)
  for x in range(tsteps):
    frame = draw_blur(frame, box[x][0], box[x][1])
  return frame

out = clip.fl(process_frames)

if args['lossless']:
  out.write_videofile(outname, codec = "libx264", preset = "ultrafast", ffmpeg_params = ['-crf', '0' ], audio_codec = 'libfdk_aac' )  
elif args['highq']:
  out.write_videofile(outname, codec = "libx265", preset = "medium", bitrate = rate, ffmpeg_params = [ '-pass', '1', '-pix_fmt', 'yuv420p' ], audio_codec = 'libfdk_aac' )  
  out.write_videofile(outname, codec = "libx265", preset = "medium", bitrate = rate, ffmpeg_params = [ '-pass', '2', '-pix_fmt', 'yuv420p' ], audio_codec = 'libfdk_aac' )  
else:
  out.write_videofile(outname, codec = "libx265", preset = "fast", ffmpeg_params = ['-crf', '18', '-pix_fmt', 'yuv420p'], audio_codec = 'libfdk_aac' )  

