"""Teste do balanço nos recortes. Uso: python3 demos/demo_balanco.py  (gera demos/saida/balanco.mp4 em 540x960, exige ffmpeg)
Três recortes entram em sequência, ficam juntos na tela balançando fora de sincronia e saem."""
import sys, os, subprocess, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..', 'lib'))
from PIL import Image
from papel import recorte_jornal
from animfoto import estado, sombra_papel
from fundo import fundo
FF = shutil.which('ffmpeg') or os.path.expanduser('~/bin/ffmpeg'); W, H = 1080, 1920
BG = fundo(W, H).convert('RGBA'); REC = os.path.join(AQUI, '..', 'assets', 'recortes')

def item(nome, h):
    im = Image.open(os.path.join(REC, nome + '.png')).convert('RGBA'); im.thumbnail((h * 3, h)); return recorte_jornal(im)

# (item, entrada em s, x, y, rotação base, fase do balanço)
itens = [(item('folha1_0', 440), 0.0, 290, 620, -4, 0.0), (item('folha1_2', 300), 0.5, 800, 500, 3, 2.1), (item('folha2_3', 520), 1.0, 560, 1040, -2, 4.2)]
fim = 5.0; total = fim + 0.8

if __name__ == '__main__':
    saida = os.path.join(AQUI, 'saida', 'balanco.mp4'); os.makedirs(os.path.dirname(saida), exist_ok=True)
    enc = subprocess.Popen([FF, '-nostdin', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                            '-vf', 'scale=540:960', '-c:v', 'libx264', '-b:v', '1800k', '-preset', 'fast', '-pix_fmt', 'yuv420p', saida], stdin=subprocess.PIPE)
    for k in range(int(total * 30)):
        t = k / 30; fr = BG.copy()
        for im0, t0, x, y, rot, fase in itens:
            im = estado(im0, t - t0, fim - t0 - 0.5, rot=rot, fase=fase)
            if im is None: continue
            im2 = sombra_papel(im); fr.alpha_composite(im2, (int(x - im2.width / 2), int(y - im2.height / 2)))
        enc.stdin.write(fr.convert('RGB').tobytes())
    enc.stdin.close(); enc.wait(); print('ok', saida, round(total, 1))
