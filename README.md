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
para otimizar a codificação final, veja o arquivo .py para detalhes.


Para melhores resultados, use um logo com fundo transparente e com alto 
contraste. O script average.py pode lhe ajudar a gerar o logo a partir de uma 
cena do vídeo.

Se há absoluta necessidade de não haver falsos negativos (frames em que o
script falhe em achar o logo), recomendo usar o modo lossless "-1" e depois
editar o resultado separadamente.

O CSV informa os pontos problemáticos onde o algoritmo teve dificuldade de
achar o logo. Todos os segundos em que o segundo número da linha é menor que
o threshold (0.29 atualmente) vão ser ignorados na hora do inpaint. Este arquivo 
CSV pode ser editado para que o próprio usuário coloque a posição do logo no
segundo determinado.

dependências incluem python, moviepy, opencv, numpy, ffmpeg, libx264
   libx265, libfdk_aac

Usem livremente! @crowseye

diff 0.4: CSV editável com os timestamps

diff 0.3: troquei o blur pelo inpaint + median

diff 0.2: adicionei a procura temporal com maxtsteps, modo lossless

diff 0.15: adicionei a opção global tsteps, output em HEVC
