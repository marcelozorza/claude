"""Fundo graph paper da marca: papel creme quadriculado com fibras e amassados leves (1080x1920).
Uso: from fundo import fundo; fundo().save('graph_paper.png')"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from papel import _ruido, _facetas


def fundo(W=1080, H=1920):
    alvo = np.array([241, 229, 201], np.float32)          # cor média aprovada
    im = Image.new('RGB', (W, H), tuple(int(x) for x in alvo)); d = ImageDraw.Draw(im)
    for x in range(0, W, 54): d.line([(x, 0), (x, H)], fill=(229, 215, 185), width=1)
    for y in range(0, H, 54): d.line([(0, y), (W, y)], fill=(229, 215, 185), width=1)
    a = np.array(im).astype(np.float32)
    F1, B1 = _facetas(H, W, 12, n=46)                     # placas grandes e vincos
    F2, B2 = _facetas(H, W, 29, n=210)                    # amassados menores
    F1 = ndi.gaussian_filter(F1, 7); F2 = ndi.gaussian_filter(F2, 4)
    B1 = ndi.gaussian_filter(B1, 2.6); B2 = ndi.gaussian_filter(B2, 1.8)
    ond = (ndi.gaussian_filter(_ruido((H, W), 260, 5), 4) - 0.5) * 0.05
    nuv = (_ruido((H, W), 110, 8) - 0.5) * 0.02
    fib = (_ruido((H, W), 4, 6) - 0.5) * 0.016
    gr = np.random.RandomState(4).randn(H, W) * 0.006
    luz = 1 + 0.011 * np.clip(F1, -1.5, 1.5) + 0.006 * np.clip(F2, -1.5, 1.5) - 0.022 * B1 - 0.012 * B2 + ond + nuv + fib + gr
    v = np.linspace(-1, 1, H)[:, None] ** 2 * 0.03 + np.linspace(-1, 1, W)[None, :] ** 2 * 0.03
    out = a * (luz - v)[..., None]
    out *= (alvo / out.reshape(-1, 3).mean(0))
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')


if __name__ == '__main__':
    fundo().convert('RGB').save(sys.argv[1] if len(sys.argv) > 1 else 'graph_paper_1080x1920.png')
