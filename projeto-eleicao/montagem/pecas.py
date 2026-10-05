"""Peças da montagem do vídeo da eleição: cartões de vídeo, adesivos de papel desenhados, infográficos, carimbos, logo e apresentador.
Usa o kit de motion-graphics (lib/ e episodio-teste/montar_episodio.py). Canvas 1080x1920 a 30 fps."""
import sys, os, math, random
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(AQUI, '..', '..')
for p in (os.path.join(RAIZ, 'motion-graphics', 'lib'), os.path.join(RAIZ, 'motion-graphics', 'episodio-teste'), os.path.join(RAIZ, 'projeto-eleicao', 'corte')):
    if p not in sys.path: sys.path.insert(0, p)
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from papel import recorte_jornal
from animfoto import sombra_papel, balanco, ease_io, ease_out, back, _bola
from titulo import _fonte, _borda
import montar_episodio as ME
from montar_episodio import faixa_papel, papel_de_mascara, colar, compor, clamp, Foto, TituloAbs

W, H, FPS = 1080, 1920, 30
TINTA = (36, 30, 26, 255)
TRAB = os.environ.get('ELEICAO_TRAB', '/home/user/trabalho')
CACHE = os.path.join(TRAB, 'cache'); RAW = os.path.join(TRAB, 'raw'); FOTOS = os.path.join(TRAB, 'fotos')
CARD_W, CARD_H, CARD_CY = 760, 440, 575
AMARELO, TERRA, AZUL, VERM = (255, 218, 0), (226, 122, 92), (86, 150, 176), (214, 52, 56)
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

# ------------------------------------------------------------------ movimento
def queda(u, alt=900, T=0.30):
    """deslocamento vertical (px, negativo = acima) de um papel que cai e quica duas vezes"""
    if u < 0: return -alt
    if u < T: return -alt * (1 - (u / T) ** 2)
    v = u - T
    if v < 0.13: return -34 * math.sin(math.pi * v / 0.13)
    v -= 0.13
    if v < 0.09: return -11 * math.sin(math.pi * v / 0.09)
    return 0.0

def pintar(im, fn, S=2):
    """fn(d, S) desenha em uma camada RGBA ampliada S vezes, que desce e é colada sobre im (cores de detalhe com borda suave)"""
    lay = Image.new('RGBA', (im.width * S, im.height * S), (0, 0, 0, 0)); fn(ImageDraw.Draw(lay), S)
    im.alpha_composite(lay.resize(im.size, Image.LANCZOS)); return im

def adesivo(tam, forma, cor, seed=1, borda=7, detalhe=None, S=2, P=22):
    """recorte de papel (borda branca fibrosa) com a silhueta desenhada por forma(d, S, P) e detalhes coloridos por detalhe(d, S, P).
    tam = área útil (w, h). O resultado tem P px de margem em cada lado."""
    w, h = tam[0] + 2 * P, tam[1] + 2 * P
    m = Image.new('L', (w * S, h * S), 0); forma(ImageDraw.Draw(m), S, P)
    mm = np.array(m.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    im = papel_de_mascara(mm, cor, seed, borda=borda)
    if detalhe: pintar(im, lambda d, s: detalhe(d, s, P), S)
    return im

def rot_ret(cx, cy, w, h, ang):
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]

def tira_texto(texto, tam, cor=(250, 244, 226), seed=5, padx=None, fonte=None):
    f = fonte or _fonte(tam); d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    wt = d.textlength(texto, font=f); padx = padx or int(0.5 * tam) + 14; pady = int(0.36 * tam) + 10
    im = faixa_papel(int(wt + 2 * padx), int(tam * 1.1 + 2 * pady), cor, seed); d = ImageDraw.Draw(im)
    d.text((im.width / 2, im.height / 2 + 2), texto, font=f, fill=TINTA, anchor='mm'); return im

# ------------------------------------------------------------------ vídeo de apoio
VIDEOS = {  # chave: (arquivo, início na fonte, duração exibida, velocidade, posição vertical do enquadramento 0..1)
    'cama': ('/home/user/apoio/Smartphone_Bed.mp4', 0.0, 7.0, 1.0, 0.5),
    'catedral': ('/home/user/bruto/apoio/Cathedral_Brasilia.mp4', 1.0, 10.1, 1.0, 0.45),
    'escritorio': ('/home/user/bruto/apoio/Emotional_Office.mp4', 0.0, 4.7, 0.7, 0.38),
    'livro': ('/home/user/bruto/apoio/Book_Leather.mp4', 0.3, 5.0, 1.0, 0.5),
    'cruzamento': ('/home/user/bruto/apoio/Crossing_Street.mp4', 0.0, 3.4, 1.0, 0.5),
    'multidao': ('/home/user/bruto/apoio/People_Crowd.mp4', 0.0, 3.8, 1.0, 0.45),
    'microfone': ('/home/user/bruto/apoio/Microphone_Studio.mp4', 2.0, 3.2, 1.0, 0.45),
    'maternidade': ('/home/user/bruto/apoio/Pregnant_Hospital.mp4', 2.0, 3.4, 1.0, 0.4),
    'enfermaria': ('/home/user/bruto/apoio/Vertical_Video_Ward.mp4', 1.0, 7.9, 1.0, 0.4)}

def preparar_videos():
    import subprocess
    for chave, (arq, ss, dur, vel, fy) in VIDEOS.items():
        pasta = os.path.join(CACHE, chave)
        if os.path.isdir(pasta) and len(os.listdir(pasta)) >= int(dur * FPS) - 1: continue
        os.makedirs(pasta, exist_ok=True)
        vf = f"setpts=PTS/{vel},fps={FPS},scale={CARD_W}:{CARD_H}:force_original_aspect_ratio=increase,crop={CARD_W}:{CARD_H}:(iw-{CARD_W})/2:(ih-{CARD_H})*{fy}"
        subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-ss', str(ss), '-t', str(dur * vel + 0.2), '-i', arq, '-an', '-vf', vf, '-q:v', '3', os.path.join(pasta, '%04d.jpg')], check=True)

class CartaoVideo:
    """vídeo de apoio dentro de uma folha de papel com borda branca. Cai de cima, balança e sai subindo."""
    def __init__(self, chave, t0, t1, fase=0.0, rot=-2.0, cy=CARD_CY, cx=W / 2):
        self.chave, self.t0, self.t1, self.fase, self.rot, self.cy, self.cx = chave, t0, t1, fase, rot, cy, cx; self.nome = 'vídeo ' + chave
        self.pasta = os.path.join(CACHE, chave); self.n = len(os.listdir(self.pasta))
        self.base = faixa_papel(CARD_W + 44, CARD_H + 44, (250, 246, 236), seed=11 + len(chave)); self.pad = 26 + 22; self._c = {}
    def draw(self, fr, t):
        if t < self.t0 or t > self.t1 + 0.34: return
        u = t - self.t0; k = min(self.n, max(1, int(u * FPS) + 1))
        if k not in self._c: self._c = {k: Image.open(os.path.join(self.pasta, f'{k:04d}.jpg')).convert('RGB')}
        im = self.base.copy(); im.paste(self._c[k], (self.pad, self.pad))
        dy = 0.0; er = 0.0
        if u < 0.32: p = u / 0.32; dy = -1000 * (1 - back(p)); er = -9 * (1 - p)
        if t > self.t1: q = (t - self.t1) / 0.30; dy = -1100 * q ** 2.2; er = 6 * q
        compor(fr, im, self.cx, self.cy + dy, rot=self.rot + er + balanco(t, self.fase, 1.7 * self.fase + 1.0))
    def sons(self): return []

class Etiqueta:
    """etiqueta pequena de papel colorido com texto (pop)"""
    def __init__(self, texto, t0, t1, cx, cy, tam=62, cor=(255, 226, 60), rot=-3.0, fase=0.0):
        self.im = tira_texto(texto, tam, cor, seed=len(texto) + 3, padx=int(0.45 * tam) + 10); self.t0, self.t1, self.cx, self.cy, self.rot, self.fase = t0, t1, cx, cy, rot, fase; self.nome = 'etiqueta ' + texto[:12]
    def draw(self, fr, t):
        if t < self.t0 or t > self.t1 + 0.14: return
        u = t - self.t0; sc = 0.4 + 0.6 * back(clamp(u / 0.18)) if t <= self.t1 else max(0.05, 1 - (t - self.t1) / 0.14)
        im = self.im.resize((max(1, int(self.im.width * sc)), max(1, int(self.im.height * sc))), Image.BILINEAR)
        compor(fr, im, self.cx, self.cy, rot=self.rot + balanco(t, self.fase, 1.0), off=7, blur=7, op=0.28)
    def sons(self): return []

class Cutout:
    """recorte de papel que cai (modo 'cai'), pula (modo 'pop') ou é jogado girando (modo 'joga') e sai caindo"""
    def __init__(self, im, t0, t1, cx, cy, rot=0.0, fase=0.0, modo='cai', nome='peça', balanca=1.0):
        self.im, self.t0, self.t1, self.cx, self.cy, self.rot, self.fase, self.modo, self.nome, self.bal = im, t0, t1, cx, cy, rot, fase, modo, nome, balanca
    def draw(self, fr, t):
        if t < self.t0 or t > self.t1 + 0.36: return
        u = t - self.t0; dy = 0.0; er = 0.0; sc = 1.0; dx = 0.0
        if self.modo == 'cai': dy = queda(u); er = 0 if u > 0.3 else -8 * (1 - u / 0.3)
        elif self.modo == 'pop': sc = 0.3 + 0.7 * back(clamp(u / 0.22))
        elif self.modo == 'joga':
            if u < 0.42: p = u / 0.42; dy = -1000 * (1 - p ** 1.8); dx = 260 * (1 - p); er = 520 * (1 - p)
            else: dy = queda(u - 0.42 + 0.30) * 0.45
        if t > self.t1:
            q = (t - self.t1) / 0.30
            if self.modo == 'pop': sc = max(0.05, 1 - q)
            else: dy = 1000 * q ** 2.0; er = 9 * q
        im = self.im
        if sc != 1.0: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
        compor(fr, im, self.cx + dx, self.cy + dy, rot=self.rot + er + self.bal * balanco(t, self.fase, 1.7 * self.fase + 1.0))
    def sons(self): return []

class Descarte:
    """tira de papel que cai, fica, vira bola de papel e é jogada para fora da tela"""
    def __init__(self, im, t0, t_dobra, cx, cy, rot=-2.0, fase=0.0, lado=1, nome='descarte'):
        self.im, self.t0, self.td, self.cx, self.cy, self.rot, self.fase, self.lado, self.nome = im, t0, t_dobra, cx, cy, rot, fase, lado, nome
    def draw(self, fr, t):
        if t < self.t0 or t > self.td + 1.0: return
        u = t - self.t0
        if t < self.td:
            dy = queda(u, 800); compor(fr, self.im, self.cx, self.cy + dy, rot=self.rot + (0 if u > 0.3 else -7 * (1 - u / 0.3)) + balanco(t, self.fase, 1.0)); return
        b = _bola(self.im, 'A'); v = t - self.td
        if v < 0.45: im = b.quadro(ease_io(v / 0.45)); compor(fr, im, self.cx, self.cy, rot=self.rot + 20 * v); return
        p = (v - 0.45) / 0.50; im = b.quadro(1.0)
        x = self.cx + self.lado * 900 * p; y = self.cy - 420 * 4 * p * (1 - p) + 120 * p ** 2 - 300 * p
        sc = 1.0 - 0.35 * p; im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
        compor(fr, im, x, y, rot=self.lado * 400 * p)
    def sons(self): return []


class Rasga:
    """peça de papel que cai e, em t_rasga, se rasga ao meio: as duas metades se afastam e despencam"""
    def __init__(self, im, t0, t_rasga, cx, cy, rot=-2.0, fase=0.0, nome='rasgo'):
        self.t0, self.tr, self.cx, self.cy, self.rot, self.fase, self.nome = t0, t_rasga, cx, cy, rot, fase, nome
        w, h = im.size; r = np.random.RandomState(12); xl = w / 2 + _borda(h, 16, 33)[:h] * 1.0
        xs = np.arange(w)[None, :]; esq = (xs < xl[:, None]).astype(np.float32); a = np.array(im.getchannel('A')).astype(np.float32) / 255
        self.metades = []
        for m in (esq, 1 - esq):
            q = im.copy(); q.putalpha(Image.fromarray((a * m * 255).astype(np.uint8)))
            borda = (ndi.distance_transform_edt(m > 0.5) if False else None)
            dist = np.abs(xs - xl[:, None]); faixa = (dist < 7) & (m > 0.5) & (a > 0.5); arr = np.array(q); arr[faixa, :3] = (255, 254, 250); self.metades.append(Image.fromarray(arr))
    def draw(self, fr, t):
        if t < self.t0 or t > self.tr + 0.9: return
        u = t - self.t0
        if t < self.tr:
            im = Image.alpha_composite(self.metades[0], self.metades[1]); compor(fr, im, self.cx, self.cy + queda(u, 800), rot=self.rot + (0 if u > 0.3 else -7 * (1 - u / 0.3)) + balanco(t, self.fase, 1.0)); return
        p = (t - self.tr) / 0.85; e = p ** 1.6
        for k, m in enumerate(self.metades):
            sg = -1 if k == 0 else 1
            compor(fr, m, self.cx + sg * (18 + 340 * e), self.cy + 30 * min(1.0, p * 3) + 520 * e ** 1.5, rot=self.rot + sg * 26 * e + balanco(t, self.fase, 1.0))
    def sons(self): return []

# ------------------------------------------------------------------ desenhos
def f_urna(d, S, P):
    X = lambda v: (v + P) * S
    d.rounded_rectangle([X(30), X(120), X(270), X(330)], radius=14 * S, fill=255); d.rounded_rectangle([X(14), X(96), X(286), X(138)], radius=10 * S, fill=255); d.rectangle([X(110), X(40), X(190), X(100)], fill=255)
def d_urna(d, S, P):
    X = lambda v: (v + P) * S
    d.rounded_rectangle([X(30), X(120), X(270), X(330)], radius=14 * S, fill=AZUL + (255,), outline=TINTA, width=3 * S)
    d.rounded_rectangle([X(14), X(96), X(286), X(138)], radius=10 * S, fill=(246, 240, 224, 255), outline=TINTA, width=3 * S)
    d.rounded_rectangle([X(100), X(110), X(200), X(124)], radius=6 * S, fill=TINTA)
    d.rectangle([X(110), X(40), X(190), X(104)], fill=(255, 255, 255, 255), outline=TINTA, width=3 * S)
    for k in range(3): d.line([X(122), X(58 + 16 * k), X(178), X(58 + 16 * k)], fill=(120, 110, 100, 255), width=2 * S)
    d.rounded_rectangle([X(56), X(160), X(244), X(230)], radius=8 * S, fill=(225, 240, 235, 255), outline=TINTA, width=3 * S)
    for i in range(3):
        for j in range(3): d.ellipse([X(96 + 38 * i), X(246 + 24 * j), X(112 + 38 * i), X(262 + 24 * j) - 4], fill=(245, 240, 225, 255), outline=TINTA, width=2 * S)

def f_martelo(d, S, P):
    X = lambda v: (v + P) * S
    d.polygon([(X(x), X(y)) for x, y in rot_ret(170, 90, 200, 84, -28)], fill=255); d.polygon([(X(x), X(y)) for x, y in rot_ret(220, 175, 36, 230, -28 + 0)], fill=255)
    d.polygon([(X(x), X(y)) for x, y in rot_ret(140, 270, 230, 30, 0)], fill=255)
def d_martelo(d, S, P):
    X = lambda v: (v + P) * S
    d.polygon([(X(x), X(y)) for x, y in rot_ret(220, 175, 36, 230, -28)], fill=(176, 120, 72, 255), outline=TINTA)
    d.polygon([(X(x), X(y)) for x, y in rot_ret(170, 90, 200, 84, -28)], fill=(150, 98, 60, 255), outline=TINTA, width=3 * S)
    for off in (-72, 72): d.polygon([(X(x), X(y)) for x, y in rot_ret(170 + off * math.cos(math.radians(-28)), 90 + off * math.sin(math.radians(-28)), 18, 88, -28)], fill=(96, 62, 38, 255))
    d.polygon([(X(x), X(y)) for x, y in rot_ret(140, 270, 230, 30, 0)], fill=(176, 120, 72, 255), outline=TINTA, width=3 * S)

def f_mic(d, S, P):
    X = lambda v: (v + P) * S
    d.ellipse([X(20), X(10), X(140), X(130)], fill=255); d.polygon([(X(40), X(110)), (X(120), X(110)), (X(100), X(330)), (X(60), X(330))], fill=255)
def d_mic(d, S, P):
    X = lambda v: (v + P) * S
    d.polygon([(X(40), X(110)), (X(120), X(110)), (X(100), X(330)), (X(60), X(330))], fill=(70, 70, 78, 255), outline=TINTA, width=3 * S)
    d.ellipse([X(20), X(10), X(140), X(130)], fill=(52, 52, 58, 255), outline=TINTA, width=3 * S)
    for k in range(-2, 3): d.line([X(24), X(70 + 22 * k * 0.9), X(136), X(70 + 22 * k * 0.9)], fill=(120, 120, 130, 255), width=2 * S)
    for k in range(-2, 3): d.line([X(80 + 22 * k), X(14), X(80 + 22 * k), X(126)], fill=(120, 120, 130, 255), width=2 * S)
    d.rectangle([X(38), X(112), X(122), X(136)], fill=(200, 60, 56, 255), outline=TINTA, width=3 * S)

def pts_coracao(cx, cy, k):
    return [(cx + k * 16 * math.sin(t) ** 3, cy - k * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))) for t in np.linspace(0, 2 * math.pi, 90)]
def coracao(k=9.0, cor=VERM, seed=2):
    w, h = int(34 * k), int(32 * k)
    f = lambda d, S, P: d.polygon([((x + P) * S, (y + P) * S) for x, y in pts_coracao(w / 2, h * 0.46, k)], fill=255)
    de = lambda d, S, P: (d.polygon([((x + P) * S, (y + P) * S) for x, y in pts_coracao(w / 2, h * 0.46, k)], fill=cor + (255,), outline=TINTA, width=3 * S), d.arc([(w * 0.16 + P) * S, (h * 0.12 + P) * S, (w * 0.46 + P) * S, (h * 0.48 + P) * S], 200, 275, fill=(255, 255, 255, 190), width=int(max(3, k * 0.55)) * S))
    return adesivo((w, h), f, cor, seed, detalhe=de)

def sorriso(d_, seed=4):
    n = 200
    f = lambda d, S, P: d.ellipse([P * S, P * S, (P + n) * S, (P + n) * S], fill=255)
    def de(d, S, P):
        X = lambda v: (v + P) * S
        d.ellipse([X(0), X(0), X(n), X(n)], fill=(255, 218, 0, 255), outline=TINTA, width=4 * S)
        d.ellipse([X(56), X(60), X(80), X(96)], fill=TINTA); d.ellipse([X(120), X(60), X(144), X(96)], fill=TINTA)
        d.chord([X(46), X(88), X(154), X(176)], 10, 170, fill=TINTA); d.line([X(48), X(46), X(86), X(54)], fill=TINTA, width=5 * S); d.line([X(152), X(46), X(114), X(54)], fill=TINTA, width=5 * S)
    return adesivo((n, n), f, AMARELO, seed, detalhe=de)

def texto_recorte(txt, tam, cor, seed=3, peso=700):
    f = _fonte(tam, peso); bb = f.getbbox(txt); w, h = bb[2] - bb[0] + 20, bb[3] - bb[1] + 20
    def fm(d, S, P):
        f2 = _fonte(tam * S, peso); d.text(((P + 10) * S - bb[0] * S, (P + 10) * S - bb[1] * S), txt, font=f2, fill=255, stroke_width=3 * S, stroke_fill=255)
    return adesivo((w, h), fm, cor, seed, borda=9)

def boneco(pele, roupa, esc=1.0, seed=1, corpo=False):
    w, h = int(150 * esc), int(210 * esc)
    def f(d, S, P):
        X = lambda v: (v + P) * S
        d.ellipse([X(w * 0.27), X(0), X(w * 0.73), X(h * 0.40)], fill=255); d.rounded_rectangle([X(w * 0.06), X(h * 0.40), X(w * 0.94), X(h)], radius=int(26 * esc) * S, fill=255)
    def de(d, S, P):
        X = lambda v: (v + P) * S
        d.rounded_rectangle([X(w * 0.06), X(h * 0.40), X(w * 0.94), X(h)], radius=int(26 * esc) * S, fill=roupa + (255,), outline=TINTA, width=3 * S)
        d.rectangle([X(w * 0.40), X(h * 0.34), X(w * 0.60), X(h * 0.46)], fill=pele + (255,))
        d.ellipse([X(w * 0.27), X(0), X(w * 0.73), X(h * 0.40)], fill=pele + (255,), outline=TINTA, width=3 * S)
        d.ellipse([X(w * 0.40), X(h * 0.15), X(w * 0.45), X(h * 0.20)], fill=TINTA); d.ellipse([X(w * 0.55), X(h * 0.15), X(w * 0.60), X(h * 0.20)], fill=TINTA)
        d.arc([X(w * 0.42), X(h * 0.19), X(w * 0.58), X(h * 0.31)], 20, 160, fill=TINTA, width=2 * S)
    return adesivo((w, h), f, roupa, seed, borda=6, detalhe=de)

PELES = [(236, 190, 150), (200, 140, 100), (146, 98, 66), (96, 62, 44), (246, 214, 180), (176, 118, 82), (122, 80, 54)]
ROUPAS = [TERRA, AZUL, (255, 218, 0), (110, 170, 120), (170, 120, 180), (240, 150, 60), (90, 110, 180)]

def fila_de_bonecos(n=7):
    """bonecos de papel de vários tons de pele, de mãos dadas (braços ligando um ao outro)"""
    esp = 140; w, h = int(esp * (n - 1) + 120), 270
    def corpo(d, S, P, cheio=True):
        X = lambda v: (v + P) * S
        for i in range(n):
            cx = 60 + esp * i
            d.ellipse([X(cx - 30), X(0), X(cx + 30), X(62)], fill=255); d.rounded_rectangle([X(cx - 40), X(60), X(cx + 40), X(190)], radius=20 * S, fill=255)
            d.rectangle([X(cx - 36), X(186), X(cx - 8), X(262)], fill=255); d.rectangle([X(cx + 8), X(186), X(cx + 36), X(262)], fill=255)
            if i < n - 1: d.rounded_rectangle([X(cx + 30), X(112), X(cx + esp - 30), X(134)], radius=10 * S, fill=255)
    def de(d, S, P):
        X = lambda v: (v + P) * S
        for i in range(n):
            cx = 60 + esp * i; pele = PELES[i % len(PELES)]; roupa = ROUPAS[i % len(ROUPAS)]
            if i < n - 1: d.rounded_rectangle([X(cx + 30), X(112), X(cx + esp - 30), X(134)], radius=10 * S, fill=roupa + (255,), outline=TINTA, width=3 * S); d.ellipse([X(cx + esp / 2 - 14), X(108), X(cx + esp / 2 + 14), X(138)], fill=PELES[(i + 3) % len(PELES)] + (255,), outline=TINTA, width=3 * S)
            d.rectangle([X(cx - 36), X(186), X(cx - 8), X(262)], fill=(70, 66, 80, 255), outline=TINTA, width=3 * S); d.rectangle([X(cx + 8), X(186), X(cx + 36), X(262)], fill=(70, 66, 80, 255), outline=TINTA, width=3 * S)
            d.rounded_rectangle([X(cx - 40), X(60), X(cx + 40), X(190)], radius=20 * S, fill=roupa + (255,), outline=TINTA, width=3 * S)
            d.ellipse([X(cx - 30), X(0), X(cx + 30), X(62)], fill=pele + (255,), outline=TINTA, width=3 * S)
            d.ellipse([X(cx - 14), X(24), X(cx - 8), X(30)], fill=TINTA); d.ellipse([X(cx + 8), X(24), X(cx + 14), X(30)], fill=TINTA); d.arc([X(cx - 12), X(30), X(cx + 12), X(50)], 20, 160, fill=TINTA, width=2 * S)
    return adesivo((w, h), corpo, (255, 218, 0), 9, borda=8, detalhe=de)

def aperto_de_mao(seed=6):
    w, h = 760, 400
    def poly(cx, cy, rw, rh, ang): return rot_ret(cx, cy, rw, rh, ang)
    def f(d, S, P):
        X = lambda v: (v + P) * S
        for cx, cy, rw, rh, ang in ((140, 190, 300, 110, -6), (620, 190, 300, 110, 6)): d.polygon([(X(x), X(y)) for x, y in poly(cx, cy, rw, rh, ang)], fill=255)
        d.rounded_rectangle([X(250), X(130), X(510), X(270)], radius=44 * S, fill=255)
    def de(d, S, P):
        X = lambda v: (v + P) * S
        for (cx, cy, rw, rh, ang), cor in zip(((140, 190, 300, 110, -6), (620, 190, 300, 110, 6)), (AZUL, TERRA)): d.polygon([(X(x), X(y)) for x, y in poly(cx, cy, rw, rh, ang)], fill=cor + (255,), outline=TINTA, width=3 * S)
        d.rounded_rectangle([X(250), X(130), X(510), X(270)], radius=44 * S, fill=PELES[0] + (255,), outline=TINTA, width=3 * S)
        d.rounded_rectangle([X(330), X(130), X(510), X(270)], radius=44 * S, fill=PELES[2] + (255,), outline=TINTA, width=3 * S)
        for k in range(4): d.line([X(340), X(150 + 28 * k), X(430), X(150 + 28 * k)], fill=TINTA, width=3 * S)
        d.arc([X(236), X(150), X(300), X(250)], 90, 270, fill=TINTA, width=3 * S)
    return adesivo((w, h), f, AZUL, seed, borda=8, detalhe=de)

def calendario():
    w, h = 400, 470
    f = lambda d, S, P: d.rounded_rectangle([(P) * S, (P + 14) * S, (P + w) * S, (P + h) * S], radius=10 * S, fill=255)
    def de(d, S, P):
        X = lambda v: (v + P) * S
        d.rounded_rectangle([X(0), X(14), X(w), X(h)], radius=10 * S, fill=(252, 250, 244, 255), outline=TINTA, width=3 * S)
        d.rounded_rectangle([X(0), X(14), X(w), X(120)], radius=10 * S, fill=VERM + (255,), outline=TINTA, width=3 * S); d.rectangle([X(2), X(100), X(w - 2), X(120)], fill=VERM + (255,))
        for x in (90, 200, 310): d.rounded_rectangle([X(x - 9), X(0), X(x + 9), X(46)], radius=8 * S, fill=(80, 80, 88, 255), outline=TINTA, width=3 * S)
        d.text((X(w / 2), X(70)), 'OUTUBRO', font=ImageFont.truetype(BOLD, 40 * S), fill=(255, 255, 255, 255), anchor='mm')
        d.text((X(w / 2), X(290)), 'HOJE', font=_fonte(150 * S, 640), fill=TINTA, anchor='mm')
    return adesivo((w, h + 14), f, (250, 246, 236), 5, detalhe=de)

def traco_marca_texto(p, y=745, larg=96, cor=(232, 36, 40, 205)):
    """traço de marca-texto vermelho de ponta a ponta, desenhado da esquerda para a direita (p 0..1)"""
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); n = 60
    pts = [(-60 + (W + 120) * i / n * min(1.0, p), y + 10 * math.sin(i * 0.5) + 6 * math.sin(i * 1.3 + 1)) for i in range(int(n * p) + 1)]
    for a, b in zip(pts, pts[1:]): d.line([a, b], fill=cor, width=larg)
    if pts: d.ellipse([pts[-1][0] - larg / 2, pts[-1][1] - larg / 2, pts[-1][0] + larg / 2, pts[-1][1] + larg / 2], fill=cor)
    return L

class Marcador:
    """traço de marca-texto vermelho riscando a tela de ponta a ponta"""
    def __init__(self, t0, t1, y=745): self.t0, self.t1, self.y = t0, t1, y; self.nome = 'marca-texto'
    def draw(self, fr, t):
        if t < self.t0 or t > self.t1: return
        p = ease_out(clamp((t - self.t0) / 0.45)); fr.alpha_composite(traco_marca_texto(p, self.y))
    def sons(self): return []

class Grade81:
    """81 quadradinhos de papel (9x9). 28 viram amarelos"""
    T = 52; G = 8
    def __init__(self, t0, t1, ty0, ty1, cx=540, cy=635):
        self.t0, self.t1, self.ty0, self.ty1, self.cx, self.cy = t0, t1, ty0, ty1, cx, cy; self.nome = 'grade 81'
        self.cinza = [faixa_papel(self.T, self.T, (222, 214, 198), 40 + i, amp=2, pad=8) for i in range(6)]
        self.amar = [faixa_papel(self.T, self.T, (255, 218, 0), 60 + i, amp=2, pad=8) for i in range(6)]
    def draw(self, fr, t):
        if t < self.t0 or t > self.t1 + 0.36: return
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); u = t - self.t0; passo = self.T + self.G; x0 = self.cx - 4 * passo; y0 = self.cy - 4 * passo
        for i in range(81):
            r, c = divmod(i, 9); ui = u - 0.03 * r - 0.012 * c
            if ui < 0: continue
            dy = queda(ui, 700, 0.26)
            amarelo = i < 28 and t >= self.ty0 + (self.ty1 - self.ty0) * i / 28
            im = (self.amar if amarelo else self.cinza)[i % 6]; sc = 1.0
            if amarelo: pop = t - (self.ty0 + (self.ty1 - self.ty0) * i / 28); sc = 1.0 + 0.30 * math.sin(math.pi * clamp(pop / 0.18))
            if sc != 1.0: im = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR)
            colar(L, sombra_papel(im, off=4, blur=4, op=0.25), x0 + c * passo - im.width / 2 + self.T / 2 - 18, y0 + r * passo + dy - im.height / 2 + self.T / 2 - 18)
        extra = 0.0; q = 0.0
        if t > self.t1: q = (t - self.t1) / 0.30; extra = 1000 * q ** 2.0
        L = L.rotate(balanco(t, 2.2, 1.0) * 0.6 - 8 * q, resample=Image.BICUBIC, center=(self.cx, self.cy)); colar(fr, L, 0, int(extra))
    def sons(self): return []

class Barra:
    """barra de papel que sobe de 99 para 121 (rótulo numérico acompanha)"""
    PX = 2.7; BASE = 745; LARG = 250
    def __init__(self, t0, t_sobe, t1, v0=99, v1=121):
        self.t0, self.ts, self.t1, self.v0, self.v1 = t0, t_sobe, t1, v0, v1; self.nome = 'barra'; self.f = _fonte(120, 640); self.f2 = _fonte(46, 520)
    def draw(self, fr, t):
        if t < self.t0 or t > self.t1 + 0.36: return
        u = t - self.t0; v = self.v1 if t > self.ts + 0.6 else (self.v0 + (self.v1 - self.v0) * ease_io(clamp((t - self.ts) / 0.6)) if t > self.ts else self.v0)
        v *= back(clamp(u / 0.35)) if u < 0.35 else 1.0
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); cx = W / 2
        d.rounded_rectangle([cx - 330, self.BASE, cx + 330, self.BASE + 7], radius=3, fill=TINTA)
        alt = max(8, v * self.PX); S = 2
        b = Image.new('RGBA', (self.LARG * S, int(alt * S) + 40), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
        bd.rounded_rectangle([0, 0, self.LARG * S - 1, int(alt * S) + 80], radius=14 * S, fill=TINTA); bd.rounded_rectangle([6 * S, 6 * S, self.LARG * S - 1 - 6 * S, int(alt * S) + 80], radius=10 * S, fill=AMARELO + (255,))
        b = b.resize((self.LARG, int(alt) + 20), Image.LANCZOS).crop((0, 0, self.LARG, int(alt))); colar(L, sombra_papel(b, off=8, blur=8, op=0.22), cx - self.LARG / 2 - 27, self.BASE - alt - 27)
        if t > self.ts - 0.05:
            ya = self.BASE - self.v0 * self.PX
            for x in range(int(cx - 330), int(cx + 330), 26): d.line([x, ya, x + 14, ya], fill=(120, 108, 92, 255), width=3)
            d.text((cx + 345, ya), 'há 4 anos', font=self.f2, fill=(110, 98, 84, 255), anchor='lm')
        num = str(int(round(v))); d.text((cx, self.BASE - alt + 78), num, font=self.f, fill=TINTA, anchor='mm')
        extra = 0.0; q = 0.0
        if t > self.t1: q = (t - self.t1) / 0.30; extra = 1000 * q ** 2.0
        L = L.rotate(balanco(t, 3.3, 1.2) * 0.5 - 8 * q, resample=Image.BICUBIC, center=(cx, self.BASE)); colar(fr, L, 0, int(extra))
    def sons(self): return []

class Circulos:
    """dois círculos de bonecos: dentro (coração grande) e fora (coração pequeno, que vira sorriso)"""
    def __init__(self, t0, t1, t_sorri):
        self.t0, self.t1, self.ts = t0, t1, t_sorri; self.nome = 'círculos'
        def disco(r, cor, seed):
            m = np.zeros((2 * r + 60, 2 * r + 60), np.float32); yy, xx = np.ogrid[:m.shape[0], :m.shape[1]]; m[(xx - r - 30) ** 2 + (yy - r - 30) ** 2 <= r * r] = 1.0
            return papel_de_mascara(m, cor, seed, borda=7)
        self.d_in = disco(185, (255, 241, 196), 8); self.d_out = disco(185, (226, 220, 208), 9)
        self.in_b = [boneco(PELES[i], ROUPAS[1], 0.62, seed=i + 1) for i in (0, 1, 2, 3, 4)]; self.out_b = [boneco(PELES[i], ROUPAS[0], 0.62, seed=i + 7) for i in (4, 5, 6, 0, 1)]
        self.h_big = coracao(5.4); self.h_small = coracao(2.2, cor=(150, 60, 66), seed=6); self.smile = sorriso(None); self.smile.thumbnail((92, 92))
        self.c_in, self.c_out = (300, 575), (790, 575)
    def _grupo(self, centro, bonecos, disco, coracao_im, ext=None):
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cx, cy = centro; colar(g, sombra_papel(disco, off=8, blur=8, op=0.25), cx - disco.width / 2 - 24, cy - disco.height / 2 - 24)
        for i, b in enumerate(bonecos):
            a = math.radians(-90 + 72 * i + 36); px, py = cx + 118 * math.cos(a), cy + 100 * math.sin(a) + 6
            colar(g, sombra_papel(b, off=4, blur=4, op=0.22), px - b.width / 2 - 12, py - b.height / 2 - 12)
        ci = coracao_im; colar(g, sombra_papel(ci, off=5, blur=5, op=0.22), cx - ci.width / 2 - 15, cy + 8 - ci.height / 2 - 15)
        return g
    def draw(self, fr, t):
        if t < self.t0 or t > self.t1 + 0.36: return
        u = t - self.t0
        if not hasattr(self, '_g'):
            self._g = (self._grupo(self.c_in, self.in_b, self.d_in, self.h_big), self._grupo(self.c_out, self.out_b, self.d_out, self.h_small), self._grupo(self.c_out, self.out_b, self.d_out, self.smile))
        for k, cen in enumerate((self.c_in, self.c_out)):
            g = self._g[k if not (k == 1 and t >= self.ts) else 2]; dy = queda(u - 0.18 * k, 800)
            if t > self.t1: q = (t - self.t1) / 0.30; dy = 1000 * q ** 2.0
            g = g.rotate(balanco(t, 1.0 + 2 * k, 1.0) * 0.7, resample=Image.BICUBIC, center=cen); colar(fr, g, 0, int(dy))
    def sons(self): return []

class Carimbo:
    """carimbo que bate direto na tela (sem fundo de papel). Impacto: começa grande, bate e treme"""
    def __init__(self, texto, t0, t1, cx, cy, rot=-5.0, tam=130, cor=(204, 34, 40), seed=1):
        self.t0, self.t1, self.cx, self.cy, self.rot = t0, t1, cx, cy, rot; self.nome = 'carimbo ' + texto
        f = ImageFont.truetype(BOLD, tam); d = ImageDraw.Draw(Image.new('RGB', (1, 1))); wt = d.textlength(texto, font=f); w, h = int(wt + 90), int(tam * 1.35 + 40); S = 2
        im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([6 * S, 6 * S, (w - 6) * S, (h - 6) * S], radius=14 * S, outline=cor + (255,), width=9 * S); d.rounded_rectangle([22 * S, 22 * S, (w - 22) * S, (h - 22) * S], radius=8 * S, outline=cor + (255,), width=3 * S)
        d.text((w * S / 2, h * S / 2 + 4 * S), texto, font=ImageFont.truetype(BOLD, tam * S), fill=cor + (255,), anchor='mm'); im = im.resize((w, h), Image.LANCZOS)
        r = np.random.RandomState(seed); ru = ndi.gaussian_filter(r.rand(h, w), 1.3); a = np.array(im.getchannel('A')).astype(np.float32) * np.clip((ru - 0.30) * 6, 0, 1) * 0.92
        im.putalpha(Image.fromarray(a.astype(np.uint8))); self.im = im
    def draw(self, fr, t):
        if t < self.t0 or t > self.t1: return
        u = t - self.t0; sc = 1.0; sx = 0.0; sy = 0.0
        if u < 0.09: sc = 2.0 - 1.0 * (u / 0.09)
        elif u < 0.30: sc = 1.0 + 0.04 * math.sin(math.pi * (u - 0.09) / 0.21); sx = 7 * math.sin(u * 90) * (1 - (u - 0.09) / 0.21); sy = 5 * math.cos(u * 70) * (1 - (u - 0.09) / 0.21)
        im = self.im
        if sc != 1.0: im = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR)
        im = im.rotate(self.rot, resample=Image.BICUBIC, expand=True); colar(fr, im, self.cx + sx - im.width / 2, self.cy + sy - im.height / 2)
    def sons(self): return []

class Logo:
    """logo redondo do canal. 'pop' (escala, 0,22 s) ou 'joga' (jogado sobre o papel, gira e quica)"""
    def __init__(self, t0, t1, cx=540, cy=560, d=500, modo='pop'):
        im = Image.open(os.path.join(RAIZ, 'edicao-chroma', 'dados', 'logo_redondo.png')).convert('RGBA'); im.thumbnail((d, d), Image.LANCZOS); self.im = im
        self.t0, self.t1, self.cx, self.cy, self.modo = t0, t1, cx, cy, modo; self.nome = 'logo'
    def draw(self, fr, t):
        if t < self.t0 or t > self.t1 + 0.16: return
        u = t - self.t0; sc = 1.0; dy = 0.0; rot = 0.0; dx = 0.0
        if self.modo == 'pop': sc = 0.15 + 0.85 * back(clamp(u / 0.22))
        else:
            if u < 0.42: p = u / 0.42; dy = -1000 * (1 - p ** 1.8); dx = 220 * (1 - p); rot = 520 * (1 - p)
            else: dy = queda(u - 0.12, 0)
            rot += 4 * math.sin(u * 2.2)
        if t > self.t1: sc *= max(0.05, 1 - (t - self.t1) / 0.16)
        im = self.im
        if sc != 1.0: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
        compor(fr, im, self.cx + dx, self.cy + dy, rot=rot, off=12, blur=11, op=0.30)
    def sons(self): return []

# ------------------------------------------------------------------ apresentador
class Apresentador:
    """figura do bruto com chroma key, cor e corte aprovados (CORTE_Y). Ocupa cerca de 60% da tela embaixo, com zoom de 30% em algumas frases."""
    TOPO_RAW, S0, ZOOM, CX = 190, 1.15, 1.3, 462      # CX: centro horizontal da figura no quadro original (extensão medida: x 58 a 873)
    def __init__(self, zooms):
        from chroma_quadro import processa, CORTE_Y
        self.processa, self.corte, self.zooms = processa, CORTE_Y, zooms
    def draw(self, fr, t):
        k = min(5747, max(1, int(t * FPS) + 1))
        raw = np.array(Image.open(os.path.join(RAW, f'{k:05d}.jpg')).convert('RGB'))
        pe = Image.fromarray(self.processa(raw), 'RGBA').crop((0, self.TOPO_RAW, W, self.corte))
        m = self.ZOOM if any(a <= t < b for a, b in self.zooms) else 1.0
        s = self.S0 * m; pe = pe.resize((int(pe.width * s), int(pe.height * s)), Image.LANCZOS)
        colar(fr, pe, W / 2 - self.CX * s, H - pe.height)
