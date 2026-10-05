"""Chroma key e cor do apresentador, quadro a quadro. Uso: python3 chroma_quadro.py entrada.mp4 saida_dir [t1 t2 ...] (testa quadros em segundos)"""
import sys, os, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'motion-graphics', 'lib'))
import numpy as np
from PIL import Image
from chroma import key_robusto, grade, limpa_pretos
CORTE_Y = 1550          # linha da cintura: abaixo dela há uma peça escura que não faz parte da figura
COR = (0.26, 0.26, 0.26)  # temperatura, matiz, saturação aprovados
def processa(a):
    """a: HxWx3 uint8 do bruto. Devolve HxWx4 uint8 com a figura recortada, limpa e com a cor aprovada."""
    return grade(limpa_pretos(key_robusto(a, corte_y=CORTE_Y)), *COR)
if __name__ == '__main__':
    from fundo import fundo
    ent, saida = sys.argv[1], sys.argv[2]; os.makedirs(saida, exist_ok=True); bg = fundo(1080, 1920).convert('RGBA')
    for t in [float(x) for x in sys.argv[3:]]:
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(t), '-i', ent, '-frames:v', '1', os.path.join(saida, 'orig.png')], check=True)
        pe = Image.fromarray(processa(np.array(Image.open(os.path.join(saida, 'orig.png')).convert('RGB'))), 'RGBA'); c = bg.copy(); c.alpha_composite(pe); c.convert('RGB').save(os.path.join(saida, f'teste_{t:.0f}s.png'))
