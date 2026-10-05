import math
from PIL import Image, ImageFilter
from papel import anima
def ease_out(u): return 1 - (1 - u) ** 3
def ease_in(u): return u ** 2.2
def back(u):
    c1 = 1.70158; c3 = c1 + 1; return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2
def sombra_papel(rgba, off=10, blur=9, op=0.30):
    a = rgba.getchannel('A'); sh = Image.new('RGBA', rgba.size, (74, 48, 22, 0)); sh.putalpha(a.point(lambda v: int(v * op)))
    pad = blur * 3; big = Image.new('RGBA', (rgba.width + 2 * pad, rgba.height + 2 * pad), (0, 0, 0, 0)); big.paste(sh, (pad, pad + off)); big = big.filter(ImageFilter.GaussianBlur(blur))
    big.alpha_composite(rgba, (pad, pad)); return big
_cache = {}
def _bola(item, modo):
    from bola import BolaPapel
    k = (id(item), modo)
    if k not in _cache: _cache[k] = (item, BolaPapel(item, modo, seed=3 if modo == 'A' else 5, realista=True))   # guarda o item para o id não ser reaproveitado
    return _cache[k][1]
def ease_io(u): return u * u * (3 - 2 * u)
def balanco(t, fase=3.0, fase2=1.0):
    """balanço de poucos graus no próprio eixo (papel solto sobre a mesa). Duas senoides sobrepostas, cerca de 2 graus.
    fase=3, fase2=1 é o balanço do título. Elementos na tela ao mesmo tempo devem usar fases diferentes."""
    return 1.3 * math.sin(2 * math.pi * t / 2.9 + fase) + 0.5 * math.sin(2 * math.pi * t / 1.7 + fase2)
def estado(item, u, hold, dur_in=0.5, dur_out=0.5, rot=-3, modo='A', fase=0.0):
    """u = segundos desde a entrada. Entrada: a bola de papel se abre (as dobras se desfazem e a foto aparece).
    Saída: o papel se dobra sobre si mesmo, o verso branco cobre a foto e vira bola.
    fase: defasagem do balanço, para que recortes simultâneos não balancem juntos."""
    if u < 0 or u > dur_in + hold + dur_out + 0.12: return None
    b = _bola(item, modo)
    if u < dur_in:
        p = u / dur_in; c = 1 - ease_io(p); sc = 1.0; r = rot + (1 - p) * -8
        if u < 0.08: sc = 0.55 + 0.45 * back(u / 0.08)
        im = b.quadro(c)
    elif u < dur_in + hold:
        sc = 1.0 + 0.008 * math.sin(u * 3); r = rot; im = item
    elif u < dur_in + hold + dur_out:
        p = (u - dur_in - hold) / dur_out; c = ease_io(p); sc = 1.0; r = rot + p * 8
        im = b.quadro(c)
    else:
        p = (u - dur_in - hold - dur_out) / 0.12; sc = max(0.01, 1 - p); r = rot + 8; im = b.quadro(1.0)
    r += balanco(u, fase, 1.7 * fase + 1.0)
    if sc != 1.0: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
    if abs(r) > 0.05: im = im.rotate(r, resample=Image.BICUBIC, expand=True)
    return im
