import sys, subprocess, os, math
sys.path.insert(0,'lib')
from PIL import Image
from papel import recorte_jornal
from animfoto import estado, sombra_papel
import montar
FF=os.path.expanduser('~/bin/ffmpeg'); W,H=1080,1920
BG=montar.BG
def item(path,h):
    im=Image.open(path); im.thumbnail((h*3,h)); return recorte_jornal(im)
itens=[(item('cut/folha1_3.png',720),'A'),(item('cut/folha1_2.png',560),'B'),(item('cut/folha2_5.png',900),'A'),(item('cut/folha3_5.png',760),'B')]
dur_item=2.3; saida=sys.argv[1]
enc=subprocess.Popen([FF,'-nostdin','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-vf','scale=540:960','-c:v','libx264','-b:v','1800k','-preset','fast','-pix_fmt','yuv420p',saida],stdin=subprocess.PIPE)
n=int(dur_item*len(itens)*30)
for k in range(n):
    t=k/30; fr=BG.copy(); i=min(len(itens)-1,int(t//dur_item)); u=t-i*dur_item
    im=estado(itens[i][0],u,0.6,rot=-3,modo=itens[i][1])
    if im is not None:
        im2=sombra_papel(im); fr.alpha_composite(im2,(int(540-im2.width/2),int(900-im2.height/2)))
    enc.stdin.write(fr.convert('RGB').tobytes())
enc.stdin.close(); enc.wait(); print('ok')
