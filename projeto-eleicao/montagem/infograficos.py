"""Cenas de infográfico das falas 22c, 22d e 23 (Mina Cikara e a ladeira). Peças desenhadas por código, com a estética de recorte de papel.
Cada classe tem draw(fr, t) com t LOCAL da arte (0 a 10 s). Experimento pedido pelo usuário: ver até onde o desenho por código chega."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cena import *
from bola import bola_realista

def disco(r, cor, seed):
    m = np.zeros((2 * r + 60, 2 * r + 60), np.float32); yy, xx = np.ogrid[:m.shape[0], :m.shape[1]]; m[(xx - r - 30) ** 2 + (yy - r - 30) ** 2 <= r * r] = 1.0
    return papel_de_mascara(m, cor, seed, borda=7)

def poligono_papel(pts, cor, seed, S=2):
    """recorte de papel (borda branca fibrosa) com a forma dos pontos. Devolve (imagem, x, y) do canto da imagem"""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]; x0, y0, x1, y1 = int(min(xs)) - 30, int(min(ys)) - 30, int(max(xs)) + 30, int(max(ys)) + 30
    m = Image.new('L', ((x1 - x0) * S, (y1 - y0) * S), 0); ImageDraw.Draw(m).polygon([((x - x0) * S, (y - y0) * S) for x, y in pts], fill=255)
    mm = np.array(m.resize((x1 - x0, y1 - y0), Image.LANCZOS)).astype(np.float32) / 255
    return papel_de_mascara(mm, cor, seed, borda=6), x0, y0

def estrela(n=10, r1=70, r2=42, cor=VERM, seed=3):
    """explosão de papel (símbolo de dor): estrela de pontas com um ponto de exclamação"""
    tam = int(2 * r1 + 10)
    def f(d, S, P):
        pts = [((tam / 2 + (r1 if i % 2 == 0 else r2) * math.cos(math.pi * i / n) + P) * S, (tam / 2 + (r1 if i % 2 == 0 else r2) * math.sin(math.pi * i / n) + P) * S) for i in range(2 * n)]
        d.polygon(pts, fill=255)
    def de(d, S, P):
        pts = [((tam / 2 + (r1 if i % 2 == 0 else r2) * math.cos(math.pi * i / n) + P) * S, (tam / 2 + (r1 if i % 2 == 0 else r2) * math.sin(math.pi * i / n) + P) * S) for i in range(2 * n)]
        d.polygon(pts, fill=cor + (255,), outline=TINTA, width=3 * S)
        d.text(((tam / 2 + P) * S, (tam / 2 + P) * S), '!', font=ImageFont.truetype(BOLD, int(r1 * 1.15) * S), fill=(255, 255, 255, 255), anchor='mm')
    return adesivo((tam, tam), f, cor, seed, borda=6, detalhe=de)

def seta(d, a, b, cor=TINTA, larg=7, cab=22):
    """seta reta de a até b em uma ImageDraw RGBA"""
    ang = math.atan2(b[1] - a[1], b[0] - a[0]); d.line([a, (b[0] - cab * 0.6 * math.cos(ang), b[1] - cab * 0.6 * math.sin(ang))], fill=cor, width=larg)
    p1 = (b[0] - cab * math.cos(ang - 0.45), b[1] - cab * math.sin(ang - 0.45)); p2 = (b[0] - cab * math.cos(ang + 0.45), b[1] - cab * math.sin(ang + 0.45)); d.polygon([b, p1, p2], fill=cor)

def pulso(t, t0, dur=0.55, amp=0.3):
    u = (t - t0) / dur; return amp * math.sin(math.pi * u) if 0 <= u <= 1 else 0.0

def pop(t, t0, dur=0.22):
    return 0.0 if t < t0 else 0.35 + 0.65 * back(clamp((t - t0) / dur))

def com_escala(im, sc):
    return im if abs(sc - 1.0) < 0.01 else im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)

# ----------------------------------------------------------------------------------------- 22c
class DorDeFora:
    """dois grupos de bonecos de papel. A dor de alguém do grupo faz o coração grande pulsar. A dor de alguém de fora mal mexe no coração pequeno"""
    def __init__(self):
        self.nome = 'grupos'; self.cin, self.cout = (300, 640), (780, 640)
        self.d_in = disco(190, (255, 241, 196), 8); self.d_out = disco(190, (226, 220, 208), 9)
        self.b_in = [boneco(PELES[i], c, 0.60, seed=i + 1) for i, c in zip((0, 1, 2, 3, 4), (AZUL, TERRA, AZUL, (110, 170, 120), TERRA))]
        self.b_out = [boneco((176, 176, 178), (132, 132, 140), 0.60, seed=i + 7) for i in range(5)]
        self.h_in = coracao(5.4); self.h_out = coracao(2.6, cor=(176, 128, 130), seed=6)
        self.dor = estrela(); self.off = [(-100, 30), (-52, -40), (0, 34), (52, -40), (100, 30)]
        self.et_in = Etiqueta('nosso grupo', -1, 1e9, 300, 330, tam=50, rot=-3, fase=0.5); self.et_out = Etiqueta('de fora', -1, 1e9, 780, 330, tam=50, rot=3, fase=1.7, cor=(226, 220, 208))
        self.menos = Etiqueta('sente menos', 4.5, 1e9, 780, 785, tam=54, rot=-2, fase=2.2, cor=(255, 226, 60))
        self.sa = Image.new('RGBA', (170, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(self.sa); seta(d, (85, 8), (85, 118), VERM + (255,), 20, 46)
    def _grupo(self, fr, t, centro, discos, bonecos, fase):
        cx, cy = centro
        compor(fr, discos, cx, cy, rot=balanco(t, fase, 1.0) * 0.5, off=8, blur=8, op=0.25)
        for i in sorted(range(5), key=lambda k: self.off[k][1]):
            ox, oy = self.off[i]; b = bonecos[i]; compor(fr, b, cx + ox, cy + oy - 10 + 2.0 * math.sin(t * 2.0 + i * 1.3 + fase), rot=balanco(t, fase + i, 1.0) * 1.2, off=5, blur=5, op=0.22)
    def draw(self, fr, t):
        self._grupo(fr, t, self.cin, self.d_in, self.b_in, 0.4); self._grupo(fr, t, self.cout, self.d_out, self.b_out, 1.9)
        # corações: o grande pulsa forte com a dor de um do grupo, o pequeno quase não mexe com a dor de alguém de fora
        s_in = 1.0 + 0.035 * math.sin(t * 3.0) + pulso(t, 1.1, 0.5, 0.22) + pulso(t, 1.7, 0.5, 0.20)
        s_out = 1.0 + 0.02 * math.sin(t * 3.0) + pulso(t, 4.1, 0.5, 0.05)
        compor(fr, com_escala(self.h_in, s_in), self.cin[0], 498 + 3 * math.sin(t * 2), rot=balanco(t, 0.3, 1.0), off=7, blur=7, op=0.25)
        compor(fr, com_escala(self.h_out, s_out), self.cout[0], 508 + 3 * math.sin(t * 2 + 1), rot=balanco(t, 2.1, 1.0), off=5, blur=5, op=0.22)
        # explosão de dor: primeiro num do grupo (1,0 a 2,8 s), depois num de fora (4,0 a 5,8 s)
        for (t0, t1, centro, k) in ((1.0, 2.8, self.cin, 1), (4.0, 5.8, self.cout, 3)):
            if t0 <= t <= t1 + 0.15:
                sc = pop(t, t0) if t <= t1 else max(0.05, 1 - (t - t1) / 0.15); ox, oy = self.off[k]
                compor(fr, com_escala(self.dor, 0.8 * sc), centro[0] + ox + 30, centro[1] + oy - 150, rot=balanco(t, 3.0, 1.0) * 2, off=6, blur=6, op=0.25)
        if 4.4 <= t <= 8.5: compor(fr, com_escala(self.sa, pop(t, 4.4)), self.cout[0], 580, rot=0, sombra=False)

# ----------------------------------------------------------------------------------------- 22d
class PrazerNoCerebro:
    """cérebro com uma região que se acende em laranja (prazer). Um sorriso de papel salta de lá"""
    def __init__(self):
        self.nome = 'cérebro'; im = Image.open(os.path.join(RAIZ, 'motion-graphics', 'episodio-teste', 'fotos', 'cerebro.png')).convert('RGBA'); im.thumbnail((700, 560)); self.im = im
        self.cx, self.cy = 540, 625; self.alvo = (im.width * 0.50, im.height * 0.60)
        self.sorriso = sorriso(None); self.sorriso.thumbnail((170, 170)); self.et = Etiqueta('PRAZER', 1.0, 1e9, 250, 790, tam=60, rot=-3, fase=0.8, cor=(255, 226, 60))
    def _brilho(self, k):
        w, h = self.im.size; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); d = np.sqrt((xx - self.alvo[0]) ** 2 + (yy - self.alvo[1]) ** 2)
        g = np.clip(1 - d / (95 * (0.85 + 0.25 * k)), 0, 1) ** 1.6; a = np.array(self.im.getchannel('A')).astype(np.float32) / 255
        out = np.zeros((h, w, 4), np.float32); out[..., 0], out[..., 1], out[..., 2] = 255, 120, 30; out[..., 3] = g * a * 255 * (0.55 + 0.45 * k); return Image.fromarray(out.astype(np.uint8), 'RGBA')
    def draw(self, fr, t):
        k = 0.5 + 0.5 * math.sin(t * 3.2) if t >= 0.8 else 0.0
        im = self.im.copy(); im.alpha_composite(self._brilho(k))
        compor(fr, im, self.cx, self.cy, rot=-2 + balanco(t, 0.6, 1.0), off=10, blur=9, op=0.30)
        px, py = self.cx - im.width / 2 + self.alvo[0], self.cy - im.height / 2 + self.alvo[1]
        if t >= 0.8:                                                 # raios ao redor da região acesa
            L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
            for a in range(0, 360, 40):
                r0, r1 = 62 + 8 * k, 92 + 14 * k; ca, sa_ = math.cos(math.radians(a + 8 * math.sin(t))), math.sin(math.radians(a + 8 * math.sin(t))); d.line([px + r0 * ca, py + r0 * sa_, px + r1 * ca, py + r1 * sa_], fill=(255, 120, 30, 230), width=8)
            fr.alpha_composite(L)
        if t >= 2.4:                                                 # o sorriso salta para fora do cérebro
            u = t - 2.4; dy = -125 * math.sin(math.pi * clamp(u / 0.7)) if u < 0.7 else 0.0; sc = pop(t, 2.4)
            compor(fr, com_escala(self.sorriso, sc), px + 190, py - 110 + dy + 6 * math.sin(t * 2.5), rot=balanco(t, 1.3, 1.0) * 3 + 10, off=8, blur=8, op=0.28)


def _f_broto_fn(d, S, P):
    X = lambda v: (v + P) * S
    d.polygon([(X(92), X(250)), (X(108), X(250)), (X(112), X(120)), (X(88), X(120))], fill=255)
    for ang, base in ((-150, (100, 160)), (-30, (100, 110))):
        d.polygon([(X(x), X(y)) for x, y in _folha_pts(ang, base)], fill=255)
def _folha_pts(ang, base, comp=85, larg=34):
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang)); pts = []
    for u in np.linspace(0, math.pi, 20): pts.append((base[0] + comp * (u / math.pi) * ca - larg * math.sin(u) * sa, base[1] + comp * (u / math.pi) * sa + larg * math.sin(u) * ca))
    for u in np.linspace(math.pi, 0, 20): pts.append((base[0] + comp * (u / math.pi) * ca + larg * math.sin(u) * sa, base[1] + comp * (u / math.pi) * sa - larg * math.sin(u) * ca))
    return pts
def _d_broto_fn(d, S, P):
    X = lambda v: (v + P) * S
    d.polygon([(X(92), X(250)), (X(108), X(250)), (X(112), X(120)), (X(88), X(120))], fill=(86, 140, 80, 255), outline=TINTA)
    for ang, base, cor in ((-150, (100, 160), (110, 176, 100)), (-30, (100, 110), (84, 150, 90))):
        d.polygon([(X(x), X(y)) for x, y in _folha_pts(ang, base)], fill=cor + (255,), outline=TINTA, width=3 * S)
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang)); d.line([X(base[0]), X(base[1]), X(base[0] + 80 * ca), X(base[1] + 80 * sa)], fill=TINTA, width=2 * S)

# ----------------------------------------------------------------------------------------- 23
class Ladeira:
    """cartão de papel com uma ladeira de camadas de papel e um broto. Uma pedra facetada rola ladeira abaixo, em ciclo"""
    CW, CH, K, Y0, R, PAD = 920, 520, 0.34, 215, 56, 26
    def __init__(self):
        self.nome = 'ladeira'; li = lambda x: self.Y0 + self.K * x; self.li = li; self.base = faixa_papel(self.CW, self.CH, (246, 240, 222), 41)
        al = np.array(self.base.getchannel('A')) > 128; self.inner = ndi.binary_erosion(al, iterations=11)
        a, b = -60, self.CW + 60; cam = [([(a, li(a)), (b, li(b)), (b, 700), (a, 700)], (146, 92, 62), 31), ([(a, li(a) + 46), (b, li(b) + 46), (b, 700), (a, 700)], (190, 120, 78), 32),
               ([(a, li(a) + 104), (b, li(b) + 104), (b, 700), (a, 700)], (222, 150, 98), 33), ([(a, li(a) - 4), (b, li(b) - 4), (b, li(b) + 28), (a, li(a) + 28)], (112, 170, 112), 34)]
        self.camadas = [poligono_papel(p, c, sd) for p, c, sd in cam]
        self.broto = adesivo((200, 260), lambda d, S, P: _f_broto_fn(d, S, P), (120, 176, 112), 5, detalhe=lambda d, S, P: _d_broto_fn(d, S, P))
        rocha = bola_realista(self.R * 1.9, (320, 320), (160, 160), seed=4, n_fac=60, irr=1.6); arr = np.array(rocha).astype(np.float32); arr[..., :3] *= np.array([0.50, 0.50, 0.55])
        self.rocha = Image.fromarray(arr.astype(np.uint8), 'RGBA'); self.rocha = self.rocha.crop(self.rocha.getchannel('A').getbbox())
        self.et1 = tira_texto('o terreno já é fértil', 60, seed=4); self.et2 = Etiqueta('ladeira abaixo', 0, 1e9, 0, 0, tam=58, cor=(255, 226, 60)).im
    def _rocha(self, t):
        """ciclo de 3,2 s: aparece no alto (pop), dá uma balançada, rola ladeira abaixo, sai pela direita"""
        P = 3.2; ph = (t - 0.2) % P if t >= 0.2 else 0.0; phi = math.atan(self.K); xa, xb = 400.0, 960.0
        if ph < 0.3: x, sc, rot = xa, 0.3 + 0.7 * back(ph / 0.3), 0.0
        elif ph < 0.8: x, sc, rot = xa, 1.0, -6 * math.sin((ph - 0.3) / 0.5 * 2 * math.pi)                      # empurrãozinho antes de rolar
        elif ph < 2.6: u = (ph - 0.8) / 1.8; x = xa + (xb - xa) * u * u; sc = 1.0; rot = -math.degrees((x - xa) / self.R)
        else: return None
        return x + self.R * math.sin(phi) * sc, self.li(x) - self.R * math.cos(phi) * sc, rot, sc, ph, x
    def draw(self, fr, t):
        P = self.PAD; c = self.base.copy(); L = Image.new('RGBA', c.size, (0, 0, 0, 0))
        for im, x0, y0 in self.camadas: compor(L, im, P + x0 + im.width / 2, P + y0 + im.height / 2, rot=0, off=6, blur=7, op=0.22)
        bx = 170; by = self.li(bx) - 4
        compor(L, self.broto, P + bx, P + by - self.broto.height / 2 + 20, rot=3.5 * math.sin(t * 1.4) + balanco(t, 0.2, 1.0), off=6, blur=6, op=0.2)
        r = self._rocha(t)
        if r is not None:
            sx, sy, rot, sc, ph, x = r; phi = math.atan(self.K)
            if 0.8 < ph < 2.6:                                                                                 # riscos de velocidade atrás da pedra
                d = ImageDraw.Draw(L)
                for k, off in enumerate((-24, 0, 24)):
                    a = (P + sx - (62 + 26 * k) * math.cos(phi) - off * math.sin(phi), P + sy - (62 + 26 * k) * math.sin(phi) + off * math.cos(phi)); d.line([a, (a[0] - 80 * math.cos(phi), a[1] - 80 * math.sin(phi))], fill=TINTA, width=6)
            compor(L, com_escala(self.rocha, sc), P + sx, P + sy, rot=rot, off=8, blur=8, op=0.30)
        la = np.array(L.getchannel('A')).astype(np.float32); la[~self.inner] = 0; L.putalpha(Image.fromarray(la.astype(np.uint8))); c.alpha_composite(L)
        compor(fr, c, 540, 610, rot=-1.2 + balanco(t, 0.7, 1.0) * 0.8, off=10, blur=9, op=0.30)

def _cena(pecas): return Cena(pecas)
CENAS_INFO = {'22c_dor_de_quem_esta_fora': lambda: _cena([DorDeFora()]), '22d_prazer_com_a_dor': lambda: _cena([PrazerNoCerebro()]), '23_terreno_fertil_ladeira': lambda: _cena([Ladeira()])}
