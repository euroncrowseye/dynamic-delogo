#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Este script analisa o vídeo de entrada e gera "matches" com 
# o logo, pela linha de comando:
# python generate.csg -i video.mp4 -l logo.png
#
# e grava um csv (arquivo texto com valores separados por
# ponto-e-vírgula ';') com o segundo, o valor do "match" (quanto
# maior, melhor, e a posição x e y do canto superior esquerdo do
# logo. 
# Por exemplo, uma linha do video-timecodes.csv pode ser:
#
# 15;0.8723234245453;150;655
#
# Que significa que entre o segundo 15 e 16 do vídeo o logo foi 
# encontrado na posição x=150 e y=655 com aproximadamente 0.87 de 
# match.
#
# Por enquanto o objetivo desde script é diagnosticar os intervalos
# em que o script "delogo" pode ter problemas para encontrar o logo,
# e assim minimizar o trabalho de verificação. Por enquanto, um match
# de 0.30 ou superior indica que o script conseguiu achar o logo.
#
# Futuramente a ideia é incorporar o algoritmo preditivo deste script 
# no delogo, e assim eliminar a possibilidade de falsos negativos.
#

import csv,cv2,argparse,sys
import numpy as np

from moviepy.editor import VideoFileClip
from numpy import zeros, array, uint8

# command-line variables

parser = argparse.ArgumentParser(description='Este programa vai encontrar e tirar um logo do seu vídeo')
parser.add_argument('-i','--input', help='Vídeo de entrada', required=True)
parser.add_argument('-l','--logo', help='Imagem com logo', required=True)
args = vars(parser.parse_args())

basename = args['input']
logomarca = args['logo']

# global variables

clip = VideoFileClip(basename)
logo = cv2.imread(logomarca) # Arial 9 or 10. Condensed
fps = clip.fps
h, w = logo.shape[:-1]
border=1
submask = cv2.cvtColor( logo, cv2.COLOR_RGB2GRAY )
_,submask = cv2.threshold( submask, 127, 255, cv2.THRESH_BINARY)
pad = 10
mask = np.zeros(shape=(h+pad,w+pad),dtype=uint8)
mask[pad/2:h+pad/2,pad/2:w+pad/2] = submask

# control variables

threshold = .3  # parece ser o limite para opencv ver algo
tavg = 1        # deve acompanhar as mudanças de posição
samplef = 4     # maior = mais rápido e match mais instável

# initialize variables

tmax = np.zeros(shape=(int(clip.duration/tavg)+1),dtype=float)
box = np.zeros(shape=(int(clip.duration/tavg)+1,2),dtype=int)

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

def match(haystack,needle):
  res = cv2.matchTemplate(haystack,needle, cv2.TM_CCOEFF_NORMED)
  rmin, rmax, loc_min, loc_max = cv2.minMaxLoc(res)
  return [rmax,loc_max]

for x in range(int(clip.duration/tavg)+1):
  favg = average_frame(x*tavg,x*tavg+tavg)
  tmax[x],box[x] = match(favg.astype(np.uint8),logo)
  print x, tmax[x], box[x]

outname = basename[:-4] + "-timecodes.csv"

#np.savetxt( outname, (tmax, box), delimiter=';')

file = open(outname, "wb")
writer = csv.writer(file, delimiter=';')
writer.writerow([tavg])
for x in range(int(clip.duration/tavg)+1):
    writer.writerow([x, tmax[x], box[x,0], box[x,1]])
file.close()
