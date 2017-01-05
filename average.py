#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Este é um script simples que permite você gerar uma imagem que é a  "média" 
# dos frames de um vídeo (em valores RGB). Isto permite que você possa reduzir
# efeitos de compressão e/ou ruído na hora de extrair o logo de um vídeo.
# 
# Para melhores efeitos, selecione do vídeo uma só cena onde o logo permanece
# no mesmo lugar e use este script nessa cena. 
#
# O resultado é uma imagem png. O formato foi escolhido pois suporta transparência,
# o que torna o script "delogo" mais eficiente.
#

import cv2, argparse
import numpy as np

from moviepy.editor import VideoFileClip
from numpy import zeros, array, uint8
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("basename", help="Vídeo de entrada")
parser.add_argument("ti", type=float, help="Tempo inicial", nargs='?')
parser.add_argument("tf", type=float, help="Tempo final", nargs='?')
parser.add_argument("decimate", type=int, help="Fração dos frames", nargs='?')
args = parser.parse_args()

if not args.decimate:
  args.decimate = 1

samplef = args.decimate

outname = args.basename[:-4] + "-average.png"

clip = VideoFileClip(args.basename,audio=False)

if not args.ti:
  args.ti = 0
  args.tf = clip.duration

if not args.tf or args.tf > clip.duration:
  args.tf = clip.duration

def frange(x, y, inc):
  while x < y:
    yield x
    x += inc

def average_frame(tinit,tend):
  if tinit < 0:
    tinit = 0
  if tend > clip.duration:
    tend = clip.duration
  avgmatrix = zeros(shape=(clip.h, clip.w, 3), dtype=int)
  totalframes = 0
  for f in frange(tinit, tend, 1 / clip.fps ):
    avgmatrix += clip.get_frame(f)
    totalframes += 1
  avgmatrix = (avgmatrix / totalframes).astype(np.uint8)
  return avgmatrix

img = average_frame(args.ti,args.tf)

final_img = Image.fromarray(img.astype(uint8))
final_img.save(outname)
