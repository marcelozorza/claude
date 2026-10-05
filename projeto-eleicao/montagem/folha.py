"""Folha de conferência: junta quadros jpg de uma pasta em uma grade. Uso: python3 folha.py pasta saida.png [colunas]"""
import sys, os
from PIL import Image
pasta, saida = sys.argv[1], sys.argv[2]; col = int(sys.argv[3]) if len(sys.argv) > 3 else 3
fs = sorted(f for f in os.listdir(pasta) if f.endswith('.jpg')); ims = [Image.open(os.path.join(pasta, f)) for f in fs]
w, h = ims[0].size; k = 0.5; w2, h2 = int(w * k), int(h * k); lin = (len(ims) + col - 1) // col
S = Image.new('RGB', (w2 * col, h2 * lin), (255, 255, 255))
for i, im in enumerate(ims): S.paste(im.resize((w2, h2)), ((i % col) * w2, (i // col) * h2))
S.save(saida)
