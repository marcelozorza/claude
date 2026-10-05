"""Recorta elementos gerados sobre fundo cinza liso.
Remove o cinza conectado às bordas, suaviza a borda e separa peças soltas."""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

def recorta(path, thr=38, min_area=4000, separar=False):
    im = Image.open(path).convert('RGB'); a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape
    cantos = np.concatenate([a[:8, :8].reshape(-1, 3), a[:8, -8:].reshape(-1, 3), a[-8:, :8].reshape(-1, 3), a[-8:, -8:].reshape(-1, 3)])
    bg = np.median(cantos, 0)
    d = np.sqrt(((a - bg) ** 2).sum(2))
    fundo = d < thr
    lab, n = ndi.label(fundo)
    borda = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fundo_ext = np.isin(lab, list(borda))
    obj = ~fundo_ext
    obj = ndi.binary_opening(obj, iterations=2)
    obj = ndi.binary_fill_holes(obj)
    alpha = Image.fromarray((obj * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    rgba = im.convert('RGBA'); rgba.putalpha(alpha)
    if not separar:
        return [rgba.crop(rgba.getbbox())]
    lab2, n2 = ndi.label(obj)
    pecas = []
    for i, sl in enumerate(ndi.find_objects(lab2), 1):
        area = (lab2[sl] == i).sum()
        if area < min_area: continue
        m = (lab2 == i)
        p = rgba.copy(); al = np.asarray(p.getchannel('A')).copy(); al[~ndi.binary_dilation(m, iterations=3)] = 0
        p.putalpha(Image.fromarray(al)); pecas.append(((sl[0].start//300, sl[1].start), p.crop(p.getbbox())))
    return [p for _, p in sorted(pecas, key=lambda x: x[0])]

def sombra(rgba, dy=9, blur=7, op=0.30, cor=(74, 48, 22)):
    """sombra quente do guia: 0 9px 7px rgba(74,48,22,0.30) + 0 2px 1.5px rgba(0,0,0,0.20)"""
    pad = 30; W, H = rgba.width + 2 * pad, rgba.height + 2 * pad + dy
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    al = rgba.getchannel('A')
    for (yy, bl, o, c) in [(dy, blur, op, cor), (2, 1.5, 0.20, (0, 0, 0))]:
        s = Image.new('RGBA', rgba.size, c + (0,)); s.putalpha(al.point(lambda v: int(v * o)))
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.paste(s, (pad, pad + yy))
        out.alpha_composite(layer.filter(ImageFilter.GaussianBlur(bl)))
    out.alpha_composite(rgba, (pad, pad))
    return out, pad
