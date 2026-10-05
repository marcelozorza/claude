"""Gera cenas avulsas (um MP4 por cena, 1080x1920, 30 fps, sem áudio) sobre o papel pautado.
Uso: python3 gerar_cenas.py id_da_cena [escala] [pasta_saida]     (escala 0.5 gera 540x960 para conferência)
     python3 gerar_cenas.py id_da_cena --quadros t1,t2,... pasta   (quadros avulsos em segundos)"""
import sys, os, shutil, subprocess
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cena import *
from bola_cena import topo_minimo, TOPO_SEGURO
from fundo import fundo
from cenas_def import CENAS
_f = None; _c = None; _id = None
def _init(cid):
    global _f, _c; _f = fundo(W, H).convert('RGBA'); _c = CENAS[cid]()
def _job(a):
    k, escala, pasta = a; fr = _c.frame(_f, k / FPS)
    if escala != 1.0: fr = fr.resize((int(W * escala), int(H * escala)), Image.LANCZOS)
    fr.convert('RGB').save(os.path.join(pasta, f'f{k:05d}.jpg'), quality=95)
if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; flags = [a for a in sys.argv[1:] if a.startswith('--')]; cid = args[0]
    if '--quadros' in flags:
        ks = [int(float(x) * FPS) for x in args[1].split(',')]; pasta = args[2]; os.makedirs(pasta, exist_ok=True)
        with Pool(4, initializer=_init, initargs=(cid,)) as p: p.map(_job, [(k, 0.5, pasta) for k in ks])
        sys.exit()
    ytopo, ttopo = topo_minimo(CENAS[cid]())
    print(f'topo mais alto ocupado: y={ytopo} em t={ttopo:.2f} s (limite {TOPO_SEGURO})')
    if ytopo < TOPO_SEGURO and '--ignorar-topo' not in flags: sys.exit('ERRO: a cena invade a faixa de cima do Instagram. Descer a arte ou usar --ignorar-topo')
    escala = float(args[1]) if len(args) > 1 else 1.0; saida = args[2] if len(args) > 2 else '.'; os.makedirs(saida, exist_ok=True)
    tmp = os.path.join(os.environ.get('ELEICAO_TRAB', '/home/user/trabalho'), 'quadros_' + cid); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    N = int(DUR * FPS)
    with Pool(4, initializer=_init, initargs=(cid,)) as p: list(p.imap_unordered(_job, [(k, escala, tmp) for k in range(N)], chunksize=4))
    arq = os.path.join(saida, f'cena_{cid}_{DUR:.0f}s.mp4')
    subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(tmp, 'f%05d.jpg'), '-t', str(DUR), '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-an', arq], check=True)
    shutil.rmtree(tmp); print('ok', arq)
