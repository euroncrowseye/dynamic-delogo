Rodando o delogo-alpha-0.3.py:

1. Preliminares:

a) Instale o python:

- Escolha a versão apropriada de https://www.python.org/downloads/release/python-2713/ para 32 ou 64 bits e rode o instalador. 
  Escolha o diretório padrão (C:\Python27\)
- Certifique-se que a opção “pip” no instalador está marcada.
- Adicione C:\Python27\ aos diretórios do $PATH: clique com o botão da direita em “meu computador”, selecione “configurações 
  avançadas do sistema” e “variáveis de ambiente”. Na janela “Variáveis do sistema” role até achar “Path” e edite o valor adicionando 
  “;C:\Python27\” (sem as aspas) no final. Não esqueça o ponto-e-vírgula!

b) Instale o ffmpeg com suporte a todos os codecs:

- Vá em https://sourceforge.net/projects/ffmpeg-hi/ e escolha a versão apropriada para o seu sistema.
- Descompactifique em C:\Program Files\ffmpeg\
- Renomeie ffmpeg-hi8-heaac.exe para ffmpeg.exe
- Adicione C:\Program Files\ffmpeg\ aos diretórios do $PATH: clique com o botão da direita em “meu computador”, selecione “configurações 
  avançadas do sistema” e “variáveis de ambiente”. Na janela “Variáveis do sistema” role até achar “Path” e edite o valor adicionando 
  “;C:\Program Files\ffmpeg\” (sem as aspas) no final. Não esqueça o ponto-e-vírgula!

b) Instale o opencv e moviepy:

- Abra uma linha de comando 
- Digite “c:\Python27\python.exe -m pip install opencv-python” (sem as aspas)
- Digite “c:\Python27\python.exe -m pip install moviepy” (sem as aspas)

c) Baixe o GIMP https://www.gimp.org e o AVIDemux2: http://avidemux.sourceforge.net/download.html e instale como quiser. Não 
   é necessário mas ajuda.

d) Baixe os scripts delego-alpha-0.3.py e average.py para um diretório no seu computador (vamos usar C:\project\

2. Mãos à obra - I: Gerando o logo

a) Copie o vídeo que você quer tirar o logo para o mesmo diretório do script (C:\project\). Vamos chamar o vídeo de video.mp4

b) Abra o vídeo com o AVIDemux2 e navegue entre os keyframes usando as setas para cima e/ou para baixo. 
- Procure uma cena em que o logo aparece com alto contraste (logo branco sobre tela preta). Clique na seta para cima e clique em A 
  (botão abaixo do vídeo).
- Aperte a seta para cima duas ou três vezes, certifique-se que o logo não mudou de lugar. Aperte B.
- Mude o “Output Format” para “MP4 Muxer”  e selecione “Salvar”. Coloque o nome como “video-excerto.mp4”. Não selecione “MP4v2 Muxer” 
  e não mude o “Video Output” ou o “Audio Output”! 

c) Agora é hora de rodar o primeiro script:
- Digite “python average.py video-excerto.mp4” e aguarde alguns segundos.
- verifique que, após o script rodar, há um arquivo chamado video-excerto-average.png no mesmo diretório.

d) Abra o arquivo video-excerto-average.png no GIMP.
- Ache a região do logo e dê zoom. 
- Selecione a região cuidadosamente para deixar uma caixa bem justa ao redor do logo. Copie.
- Crie um novo documento com a área copiada (Arquivo > Criar > Da Área de Transferência). 
- Aumente o contraste de forma a deixar apenas o logo visível. Selecione por cor (U) tudo que não é logo. Inverta (Selecionar > Inverter) 
  e copie.
- Cole o resultado em um novo arquivo (Arquivo > Criar > Da Área de Transferência), chame o arquivo de “logo.png”

3. Mãos à obra - II: Rode o script!
- Volte à linha de comando e digite “python delogo-alpha-0.3.py -i video.mp4 -l logo.png” (sem as aspas)
- Espere algumas horas. Uma barra de progresso vai aparecer enquanto o vídeo é recodificado.

4. Abra o resultado no AVIDemux2 para se certificar que não há logo.
