# dynamic-delogo

IMPORTANTE: LEIA ANTES DE USAR!

esse script pede um logo e um vídeo e recodifica esse vídeo embaçando
as regiões onde acha o logo.
Como o objetivo é não deixar falsos positivos, os parametros threshold
tavg, samplef e maxtsteps são usados para achar o logo em uma média de 
frames. altere caso haja problemas.


Uso é simples:

$ python delogo-alpha-X.py -i video.mp4 -l logo.png 

vai resultar no vídeo com a região do logo embaçada. Há mais parâmetros
para otimizar a codificação final.


Para melhores resultados, use um logo com fundo transparente. O script
average.py pode lhe ajudar a gerar o logo a partir do vídeo.


Se há absoluta necessidade de não haver falsos negativos (frames em que o
script falhe em achar o logo), recomendo usar o modo lossless "-1" e depois
editar o resultado separadamente.


dependências incluem python, moviepy, numpy, ffmpeg, libx264
   libx265, libfdk_aac


para a versão 0.3: CSV editável com os timestamps e parametros de
codificação melhores. Inpaint ao invés de blur?


Usem livrimente! @crowseye


diff 0.2: adicionei a procura temporal com maxtsteps, modo lossless

diff 0.15: adicionei a opção global tsteps, output em HEVC
