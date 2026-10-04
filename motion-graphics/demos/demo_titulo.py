"""Testes do título na tela. Uso: python3 demos/demo_titulo.py  (gera demos/saida/titulo_dobra.mp4 em 540x960, exige ffmpeg)"""
import sys, os, subprocess, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..', 'lib'))
from titulo import Titulo
from fundo import fundo
FF = shutil.which('ffmpeg') or os.path.expanduser('~/bin/ffmpeg'); W, H = 1080, 1920
BG = fundo(W, H).convert('RGBA')

def render(lista, saida, folga=0.35):
    ts = [Titulo(tx, entrada=en) for tx, en in lista]
    total = sum(t.duracao + folga for t in ts)
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    enc = subprocess.Popen([FF, '-nostdin', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                            '-vf', 'scale=540:960', '-c:v', 'libx264', '-b:v', '1600k', '-preset', 'fast', '-pix_fmt', 'yuv420p', saida], stdin=subprocess.PIPE)
    for k in range(int(total * 30)):
        t = k / 30; acc = 0
        for T in ts:
            if t < acc + T.duracao + folga: u = t - acc; break
            acc += T.duracao + folga
        fr = BG.copy(); fr.alpha_composite(T.quadro(u)); enc.stdin.write(fr.convert('RGB').tobytes())
    enc.stdin.close(); enc.wait(); print('ok', saida, round(total, 1))

if __name__ == '__main__':
    render([('Lorem', 'dobra'), ('Lorem ipsum dolor', 'dobra'), ('Lorem ipsum dolor sit amet consectetur', 'dobra'),
            ('Lorem ipsum dolor sit amet consectetur adipiscing elit sed do', 'dobra')], os.path.join(AQUI, 'saida', 'titulo_dobra.mp4'))
