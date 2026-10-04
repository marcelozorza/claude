import numpy as np
from scipy import ndimage as ndi
def key_rgb(a, lo=22, hi=68, spill=0.92):
    """a: HxWx3 uint8 (fundo verde). Devolve HxWx4 uint8 com alfa e despill."""
    f = a.astype(np.float32)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    s = g - np.maximum(r, b)                      # dominância do verde
    alfa = 1 - np.clip((s - lo) / (hi - lo), 0, 1)
    alfa = ndi.grey_erosion(alfa, size=(3, 3)) * 0.5 + alfa * 0.5   # morde um pouco a borda
    alfa = np.clip(alfa * 1.04 - 0.02, 0, 1)
    lim = np.maximum(r, b) * spill + 4
    g2 = np.minimum(g, lim)
    out = np.dstack([r, g2, b, alfa * 255])
    return np.clip(out, 0, 255).astype(np.uint8)


def grade(rgba, temp=0.18, matiz=0.18, sat=0.18):
    """correção de cor do apresentador (valores 0..1 equivalem ao dial do editor: 0.18 ~ 18 de 100).
    temp > 0 esquenta (mais vermelho, menos azul), matiz > 0 puxa para magenta (menos verde), sat > 0 satura."""
    f = rgba[..., :3].astype(np.float32)
    f[..., 0] *= 1 + 0.38 * temp
    f[..., 2] *= 1 - 0.42 * temp
    f[..., 1] *= 1 - 0.16 * matiz
    luma = f @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    f = luma[..., None] + (f - luma[..., None]) * (1 + sat)
    out = rgba.copy(); out[..., :3] = np.clip(f, 0, 255).astype(np.uint8)
    return out
