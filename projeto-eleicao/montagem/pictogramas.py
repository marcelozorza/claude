"""Pictogramas de formas chapadas (referência: ISO 7001). Só formas, cores sólidas, sem contorno, sem borda, sem sombra.
A figura humana é uma cabeça redonda e barras arredondadas (tronco, braços, pernas). Tudo desenhado com supersampling para borda limpa."""
import math
import numpy as np
from PIL import Image, ImageDraw

TINTA = (36, 30, 26); VERM = (204, 34, 40); AMAR = (255, 218, 0); AZUL = (86, 150, 176); TERRA = (226, 122, 92); CINZA = (126, 128, 138); VERDE = (110, 170, 112); CREME = (255, 236, 160)
SS = 3

def _tela(w, h): return Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
def _fim(im): return im.resize((im.width // SS, im.height // SS), Image.LANCZOS)

def cap(d, a, b, w, cor):
    """barra de pontas arredondadas de a até b, com espessura w (coordenadas já em pixels de supersampling)"""
    d.line([a, b], fill=cor + (255,), width=int(w)); r = w / 2
    for p in (a, b): d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=cor + (255,))

def pessoa(cor=TINTA, pose='parado', altura=440):
    """figura de frente (parado, braços_abertos) ou de lado (caminhando, subindo). Devolve RGBA recortado, base na altura dos pés"""
    W_, H_ = 400, 470; im = _tela(W_, H_); d = ImageDraw.Draw(im); k = SS; OX = 100
    P = lambda x, y: ((x + OX) * k, y * k)
    def c(a, b, w): cap(d, P(*a), P(*b), w * k, cor)
    def cab(x, y, r): d.ellipse([(x + OX - r) * k, (y - r) * k, (x + OX + r) * k, (y + r) * k], fill=cor + (255,))
    if pose in ('parado', 'braços_abertos'):
        cab(130, 50, 38); d.rounded_rectangle([P(74, 106), P(186, 252)], radius=30 * k, fill=cor + (255,))
        ab = 8 if pose == 'parado' else 38
        for sg in (-1, 1):
            sx = 130 + sg * 68; hx = sx + sg * 150 * math.sin(math.radians(ab)); hy = 126 + 150 * math.cos(math.radians(ab)); c((sx, 128), (hx, hy), 28)
            hxp = 130 + sg * 24; c((hxp, 244), (hxp + sg * 4, 420), 38)
    elif pose in ('caminhando', 'subindo'):
        cab(142, 50, 38); c((130, 158), (124, 238), 76)                                                    # tronco com folga abaixo da cabeça
        c((134, 134), (186, 226), 26); c((126, 134), (84, 214), 26)                                       # braços em balanço
        up = 64 if pose == 'subindo' else 0
        c((122, 244), (178, 322 - up * 0.4), 36); c((178, 322 - up * 0.4), (186, 404 - up), 36)          # perna da frente (levantada ao subir)
        c((118, 244), (92, 330), 36); c((92, 330), (62, 404), 36)                                         # perna de trás
    im = _fim(im); return im.crop(im.getbbox())

def coracao(raio=90, cor=VERM):
    im = _tela(raio * 2 + 8, int(raio * 1.9) + 8); d = ImageDraw.Draw(im); k = SS
    pts = [((raio + 4 + raio * 0.055 * 16 * math.sin(t) ** 3) * k, (raio * 0.95 + 4 - raio * 0.055 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))) * k) for t in np.linspace(0, 2 * math.pi, 120)]
    d.polygon(pts, fill=cor + (255,)); im = _fim(im); return im.crop(im.getbbox())

def estrela_chapada(r=90, pontas=11, cor=AMAR):
    im = _tela(r * 2 + 8, r * 2 + 8); d = ImageDraw.Draw(im); k = SS
    d.polygon([((r + 4 + (r if i % 2 == 0 else r * 0.62) * math.cos(math.pi * i / pontas)) * k, (r + 4 + (r if i % 2 == 0 else r * 0.62) * math.sin(math.pi * i / pontas)) * k) for i in range(2 * pontas)], fill=cor + (255,)); return _fim(im)

def flecha(comp=420, cor=VERM, haste=TERRA, esp=22):
    im = _tela(comp, 80); d = ImageDraw.Draw(im); k = SS; m = 40
    d.rounded_rectangle([14 * k, (m - esp / 2 / 1.6) * k, (comp - 70) * k, (m + esp / 2 / 1.6) * k], radius=6 * k, fill=haste + (255,))
    d.polygon([((comp - 90) * k, (m - 34) * k), ((comp - 2) * k, m * k), ((comp - 90) * k, (m + 34) * k)], fill=cor + (255,))
    for sg in (-1, 1): d.polygon([(2 * k, (m + sg * 26) * k), (34 * k, (m + sg * 26) * k), (52 * k, m * k), (14 * k, m * k)], fill=cor + (255,))
    return _fim(im)

def nuvem(cor=CREME, w=300, h=190):
    im = _tela(w, h); d = ImageDraw.Draw(im); k = SS
    for cx, cy, r in ((0.24, 0.62, 0.20), (0.44, 0.42, 0.27), (0.70, 0.46, 0.24), (0.80, 0.68, 0.19), (0.52, 0.70, 0.22), (0.30, 0.70, 0.20)):
        d.ellipse([(cx * w - r * w * 0.8) * k, (cy * h - r * h) * k, (cx * w + r * w * 0.8) * k, (cy * h + r * h) * k], fill=cor + (255,))
    return _fim(im)

def disco(r, cor):
    im = _tela(r * 2 + 4, r * 2 + 4); ImageDraw.Draw(im).ellipse([2 * SS, 2 * SS, (2 * r + 2) * SS, (2 * r + 2) * SS], fill=cor + (255,)); return _fim(im)

def retangulo(w, h, cor, raio=0):
    im = _tela(w, h); ImageDraw.Draw(im).rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=raio * SS, fill=cor + (255,)); return _fim(im)

def linha(pts, cor, esp, tam):
    """polilinha grossa de pontas arredondadas, como forma chapada. tam = (largura, altura) da imagem"""
    im = _tela(*tam); d = ImageDraw.Draw(im)
    for a, b in zip(pts, pts[1:]): cap(d, (a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS), esp * SS, cor)
    return _fim(im)

def seta_chapada(comp, cor=TINTA, esp=26):
    im = _tela(comp, 90); d = ImageDraw.Draw(im); k = SS; m = 45
    d.rounded_rectangle([0, (m - esp / 2) * k, (comp - 48) * k, (m + esp / 2) * k], radius=8 * k, fill=cor + (255,)); d.polygon([((comp - 62) * k, (m - 40) * k), (comp * k, m * k), ((comp - 62) * k, (m + 40) * k)], fill=cor + (255,)); return _fim(im)

def colar(dest, src, cx, cy, rot=0.0):
    if abs(rot) > 0.02: src = src.rotate(rot, resample=Image.BICUBIC, expand=True)
    dest.alpha_composite(src, (int(cx - src.width / 2), int(cy - src.height / 2))) if (cx - src.width / 2 >= 0 and cy - src.height / 2 >= 0 and cx + src.width / 2 <= dest.width and cy + src.height / 2 <= dest.height) else _colar_cortado(dest, src, int(cx - src.width / 2), int(cy - src.height / 2))

def _colar_cortado(dest, src, x, y):
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(dest.width, x + src.width), min(dest.height, y + src.height)
    if x1 > x0 and y1 > y0: dest.alpha_composite(src.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))
