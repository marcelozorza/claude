"""Montagem do episódio de teste (camada de motion graphics + marcador do apresentador + áudio limpo).
Uso: python3 episodio-teste/montar_episodio.py [saida.mp4] [escala]   (escala 0.5 = 540x960, 1.0 = 1080x1920)
Os tempos vêm de transcricao_limpa.json (áudio limpo). Renderiza em paralelo e junta com ffmpeg."""
import sys, os, json, math, shutil, subprocess
from multiprocessing import Pool
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..', 'lib'))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from fundo import fundo
from papel import recorte_jornal
from animfoto import estado, sombra_papel, balanco, ease_io, _bola
from titulo import Titulo, _borda, _fonte

W, H = 1080, 1920; FPS = 30
FF = shutil.which('ffmpeg') or os.path.expanduser('~/bin/ffmpeg')
TINTA = (36, 30, 26, 255)

# ------------------------------------------------------------------ tempos das palavras
_pal = [(w, a, b) for s in json.load(open(os.path.join(AQUI, 'transcricao_limpa.json'))) for w, a, b in s['palavras']]
def pal(txt, n=0):
    k = [i for i, p in enumerate(_pal) if p[0].strip('.,?!').lower() == txt.lower()]
    return _pal[k[n]]
def ini(txt, n=0): return pal(txt, n)[1]
def fim(txt, n=0): return pal(txt, n)[2]
def tempos(a, b):
    """lista de (inicio, fim) das palavras a..b (índices em _pal)"""
    return [(p[1], p[2]) for p in _pal[a:b + 1]]
def idx(txt, n=0): return [i for i, p in enumerate(_pal) if p[0].strip('.,?!').lower() == txt.lower()][n]

DUR = round(fim('ponte', 1) + 1.65, 1)        # fim da fala mais a saída do último título
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def fonte_it(tam, peso=520): return _fonte(tam, peso)

# ------------------------------------------------------------------ papel recortado (mesma estética do título)
def faixa_papel(w, h, cor, seed, amp=5, pad=26):
    """retângulo de papel colorido com borda branca fibrosa e rasgada. Devolve RGBA (w+2pad, h+2pad)."""
    Wc, Hc = int(w) + 2 * pad, int(h) + 2 * pad; r = np.random.RandomState(seed)
    def contorno(inset, sd):
        top = pad + inset + _borda(int(w), amp, sd) + 4; bot = pad + h - inset - 4 + _borda(int(w), amp, sd + 1)
        esq = pad + inset + _borda(int(h), amp, sd + 2) + 4; dir_ = pad + w - inset - 4 + _borda(int(h), amp, sd + 3)
        pts = [(pad + i, top[i]) for i in range(0, int(w), 2)] + [(dir_[j], pad + j) for j in range(0, int(h), 2)]
        pts += [(pad + w - i, bot[int(w) - 1 - i]) for i in range(0, int(w), 2)] + [(esq[int(h) - 1 - j], pad + h - j) for j in range(0, int(h), 2)]
        m = Image.new('L', (Wc * 2, Hc * 2), 0); ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
        return np.array(m.resize((Wc, Hc), Image.LANCZOS)).astype(np.float32) / 255
    ext = contorno(0, seed + 10); inte = contorno(5, seed + 30)
    gr = r.randn(Hc, Wc); fibra = ndi.gaussian_filter(r.rand(Hc, Wc), 1.2) - 0.5
    base = np.array(cor, np.float32)[None, None, :] + (gr * 2.2 + fibra * 14)[..., None]
    miolo = np.array([255, 254, 250], np.float32)[None, None, :] + (gr * 1.6)[..., None]
    rgb = miolo * (1 - inte[..., None]) + base * inte[..., None]
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), ext * 255]).astype(np.uint8), 'RGBA')

def papel_de_mascara(m, cor, seed, borda=6):
    """m: máscara float 0..1 (H,W). Recorte de papel com a mesma borda branca fibrosa."""
    r = np.random.RandomState(seed); Hc, Wc = m.shape
    ext = ndi.binary_dilation(m > 0.5, iterations=borda)
    ext = ndi.gaussian_filter(ext.astype(np.float32), 1.3)
    ext = np.clip((ext - 0.5) * 3 + 0.5 + (ndi.gaussian_filter(r.rand(Hc, Wc), 2) - 0.5) * 0.6, 0, 1)
    inte = ndi.gaussian_filter((m > 0.5).astype(np.float32), 1.0)
    gr = r.randn(Hc, Wc); fibra = ndi.gaussian_filter(r.rand(Hc, Wc), 1.2) - 0.5
    base = np.array(cor, np.float32)[None, None, :] + (gr * 2.0 + fibra * 12)[..., None]
    miolo = np.array([255, 254, 250], np.float32)[None, None, :] + (gr * 1.5)[..., None]
    rgb = miolo * (1 - inte[..., None]) + base * inte[..., None]
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), ext * 255]).astype(np.uint8), 'RGBA')

def colar(dest, src, x, y):
    x, y = int(x), int(y); x0, y0 = max(0, x), max(0, y); x1, y1 = min(dest.width, x + src.width), min(dest.height, y + src.height)
    if x1 > x0 and y1 > y0: dest.alpha_composite(src.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))

def compor(fr, im, cx, cy, rot=0.0, sombra=True, off=10, blur=9, op=0.30):
    if abs(rot) > 0.02: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if sombra: im = sombra_papel(im, off=off, blur=blur, op=op)
    colar(fr, im, cx - im.width / 2, cy - im.height / 2)

def bola_saida(fr, camada, t, t0, dur, cx, cy, fim_extra=0.12):
    """a camada estática se dobra e vira bola (mesma dobra das fotos). Devolve False quando já sumiu."""
    if t > t0 + dur + fim_extra: return False
    b = _bola(camada, 'A')
    if t <= t0 + dur: im = b.quadro(ease_io(clamp((t - t0) / dur))); sc = 1.0
    else: im = b.quadro(1.0); sc = max(0.01, 1 - (t - t0 - dur) / fim_extra)
    if sc != 1.0: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
    compor(fr, im, cx, cy, rot=-2 + (t - t0) * 6, op=0.30)
    return True

# ------------------------------------------------------------------ peças
class Foto:
    """foto recortada que entra e sai em bola de papel. nome pode ser um arquivo em fotos/ ou uma imagem RGBA pronta"""
    def __init__(self, nome, t0, hold, cx, cy, h, rot, fase, jornal=True):
        im = (nome.copy() if isinstance(nome, Image.Image) else Image.open(os.path.join(AQUI, 'fotos', nome + '.png')).convert('RGBA')); im.thumbnail((h * 3, h))
        self.item = recorte_jornal(im, seed=7) if jornal else im
        self.t0, self.hold, self.cx, self.cy, self.rot, self.fase = t0, hold, cx, cy, rot, fase
    def draw(self, fr, t):
        im = estado(self.item, t - self.t0, self.hold, rot=self.rot, fase=self.fase)
        if im is not None: compor(fr, im, self.cx, self.cy)
    def sons(self): return [(self.t0, 'abre'), (self.t0 + 0.5 + self.hold, 'fecha')]

class TituloAbs:
    """título cujas palavras seguem o tempo da fala. a, b = índices da primeira e da última palavra na transcrição,
    ou, com a=None, ts = lista de (inicio, fim) por palavra do texto (texto livre que sintetiza a frase)"""
    def __init__(self, texto, a, b=None, cy=270, ts=None, **kw):
        ts = ts or tempos(a, b); self.t0 = ts[0][0] - 0.85
        self.t = Titulo(texto, tempos=[(x - self.t0, y - self.t0) for x, y in ts], entrada='dobra', cy=cy, **kw)
    def draw(self, fr, t):
        u = t - self.t0
        if 0 <= u < self.t.duracao: fr.alpha_composite(self.t.quadro(u))
    def sons(self): return [(self.t0, 'abre'), (self.t0 + self.t.t_fim + self.t.ficar, 'fecha')]

class Neuronios:
    """dois neurônios de papel caem na mesa. Um cordão liga os dois, engrossa a cada disparo e acaba arrastando um para perto do outro"""
    R = 92
    def __init__(self, cy=620):
        self.cy = cy; self.sp = [self._neuronio((226, 122, 92), 4), self._neuronio((86, 150, 176), 9)]
        self.t_cai = (ini('neurônio') - 0.45, ini('outro') - 0.25)
        self.t_fio = ini('primeira') - 0.4; self.t_x = ini('décima'); self.t_y = ini('centésima'); self.t_z = ini('engrossou') - 0.9
        self.t_fold = fim('engrossou') + 0.25
        t3 = ini('centésima') + 0.5
        self.pulsos = [(ini('primeira') + 0.35, 0.9, 12)] + [(ini('décima') + 0.7 + 0.6 * k, 0.55, 18) for k in range(3)] + [(t3 + 0.35 * k, 0.30, 24) for k in range(6)]
        self.disp = [(ini('disparar'), 0), (ini('muitas'), 1), (ini('muitas') + 0.35, 0), (ini('muitas') + 0.7, 1), (ini('dispara'), 0), (ini('dispara', 1) + 0.05, 1)]       # (tempo, neurônio) disparos soltos, ainda sem ligação
        self.t_mt = ini('ponte') + 0.1
        self.A0, self.B0 = (210, 350), (870, 350)
        self._final = None

    def _neuronio(self, cor, seed):
        R = self.R; S = 2; N = int(R * 5.2); r = np.random.RandomState(seed)
        m = Image.new('L', (N * S, N * S), 0); d = ImageDraw.Draw(m); c = N * S / 2
        ang = np.linspace(0, 2 * np.pi, 48, endpoint=False); rad = R * S * (1 + ndi.gaussian_filter1d(r.randn(48), 2, mode='wrap') * 0.30)
        d.polygon([(c + rr * math.cos(a), c + rr * math.sin(a)) for rr, a in zip(rad, ang)], fill=255)
        def ramo(x, y, a, L, w0, prof):
            pts = [(x, y)]; n = 9
            for i in range(n):
                a += r.uniform(-0.35, 0.35); x += math.cos(a) * L / n; y += math.sin(a) * L / n; pts.append((x, y))
                wi = max(2, w0 * (1 - i / n) * S); d.ellipse([x - wi, y - wi, x + wi, y + wi], fill=255)
                if i == 4 and prof > 0:
                    for sg in (-1, 1): ramo(x, y, a + sg * r.uniform(0.6, 0.9), L * 0.55, w0 * 0.55, prof - 1)
        for k in range(7):
            a = 2 * np.pi * k / 7 + r.uniform(-0.2, 0.2)
            ramo(c + math.cos(a) * R * S * 0.85, c + math.sin(a) * R * S * 0.85, a, R * S * r.uniform(0.95, 1.2), 7, 1)
        mm = np.array(m.resize((N, N), Image.LANCZOS)).astype(np.float32) / 255
        im = papel_de_mascara(mm, cor, seed + 100, borda=5)
        # núcleo: outro recorte de papel, mais escuro, por cima
        nm = Image.new('L', (N * 2, N * 2), 0); ImageDraw.Draw(nm).ellipse([N - 0.36 * R * 2, N - 0.36 * R * 2, N + 0.36 * R * 2, N + 0.36 * R * 2], fill=255)
        nu = papel_de_mascara(np.array(nm.resize((N, N), Image.LANCZOS)).astype(np.float32) / 255, tuple(int(v * 0.72) for v in cor), seed + 200, borda=3)
        im.alpha_composite(nu)
        return im

    def _pos(self, t):
        """posição dos dois neurônios (A, B), com queda e arrasto"""
        pos = []
        for k, base in enumerate((self.A0, self.B0)):
            x, y = base; u = t - self.t_cai[k]
            if u < 0: pos.append(None); continue
            T = 0.38
            if u < T: y -= 700 * (1 - (u / T) ** 2)
            elif u < T + 0.14: y -= 20 * math.sin(math.pi * (u - T) / 0.14)
            pos.append([x, y])
        if pos[1] is not None and pos[0] is not None:
            p = ease_io(clamp((t - self.t_y - 0.5) / 2.0)); pos[1][0] -= 70 * p; pos[0][0] += 18 * p
            if self.t_y + 0.5 < t < self.t_y + 2.6: pos[1][0] += 3 * math.sin(t * 38)
        return pos

    def _largura(self, t):
        w = 5.0
        w += 10 * ease_io(clamp((t - self.t_x) / 0.25)); w += 21 * ease_io(clamp((t - self.t_y) / 0.25)); w += 10 * ease_io(clamp((t - self.t_z) / 0.3))
        return w

    def _curva(self, a, b, u):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 70
        return ((1 - u) ** 2 * a[0] + 2 * u * (1 - u) * mx + u * u * b[0], (1 - u) ** 2 * a[1] + 2 * u * (1 - u) * my + u * u * b[1])

    def camada(self, t):
        pos = self._pos(t)
        if pos[0] is None: return None
        L = Image.new('RGBA', (W, 700), (0, 0, 0, 0)); S = 2
        a = tuple(pos[0]); b = tuple(pos[1]) if pos[1] is not None else None
        # flashes
        fl = [0.0, 0.0]
        for tt, k in self.disp: fl[k] = max(fl[k], clamp(1 - (t - tt) / 0.30) if t >= tt else 0)
        for (t0, dur, rr) in self.pulsos:
            if t >= t0 + dur: fl[1] = max(fl[1], clamp(1 - (t - t0 - dur) / 0.22) * (0.35 if rr < 15 else 1.0))
            if t >= t0: fl[0] = max(fl[0], clamp(1 - (t - t0) / 0.18) * 0.6)
        # cordão
        if b is not None and t > self.t_fio:
            prog = ease_io(clamp((t - self.t_fio) / 0.35)); w = self._largura(t)
            cm = Image.new('RGBA', (W * S, 700 * S), (0, 0, 0, 0)); dc = ImageDraw.Draw(cm); n = 60
            pts = [self._curva(a, b, prog * i / n) for i in range(n + 1)]
            for (x, y) in pts: dc.ellipse([(x - w / 2 - 2.5) * S, (y - w / 2 - 2.5) * S, (x + w / 2 + 2.5) * S, (y + w / 2 + 2.5) * S], fill=(150, 112, 68, 255))
            for (x, y) in pts: dc.ellipse([(x - w / 2) * S, (y - w / 2) * S, (x + w / 2) * S, (y + w / 2) * S], fill=(208, 170, 118, 255))
            if w > 12:                                                       # torção do cordão
                for i in range(2, n - 1, 2):
                    (x0, y0), (x1, y1) = pts[i], pts[i + 1]; dx, dy = x1 - x0, y1 - y0; ln = math.hypot(dx, dy) or 1; nx, ny = -dy / ln, dx / ln
                    dc.line([((x0 - nx * w * 0.42 - dx * 0.5) * S, (y0 - ny * w * 0.42 - dy * 0.5) * S), ((x0 + nx * w * 0.42 + dx * 0.9) * S, (y0 + ny * w * 0.42 + dy * 0.9) * S)], fill=(160, 122, 78, 255), width=max(2, int(w * 0.10 * S)))
            if t > self.t_mt:                                                # marca-texto amarelo passa pelo cordão
                pm = ease_io(clamp((t - self.t_mt) / 0.8)); lay = Image.new('RGBA', cm.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
                for i in range(int(n * pm)):
                    (x0, y0), (x1, y1) = pts[i], pts[i + 1]; dl.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=(255, 226, 0, 150), width=int((w + 14) * S))
                alpha = np.array(cm.getchannel('A')) > 0; la = np.array(lay.getchannel('A')); la[~ndi.binary_dilation(alpha, iterations=int(5 * S))] = 0
                lay.putalpha(Image.fromarray(la)); cm.alpha_composite(lay)
            L.alpha_composite(cm.resize((W, 700), Image.LANCZOS))
            for (t0, dur, rr) in self.pulsos:                                # pulso de luz (papel amarelo) correndo pelo cordão
                if t0 <= t < t0 + dur:
                    x, y = self._curva(a, b, ease_io((t - t0) / dur)); pm = Image.new('RGBA', (int(rr * 2 + 24), int(rr * 2 + 24)), (0, 0, 0, 0))
                    ImageDraw.Draw(pm).ellipse([6, 6, 6 + rr * 2 + 12, 6 + rr * 2 + 12], fill=(255, 254, 250, 255)); ImageDraw.Draw(pm).ellipse([12, 12, 12 + rr * 2, 12 + rr * 2], fill=(255, 218, 0, 255))
                    colar(L, sombra_papel(pm, off=3, blur=3, op=0.3), x - pm.width / 2 - 9, y - pm.height / 2 - 9)
        # neurônios (por cima do cordão)
        for k, (p, sp) in enumerate(zip(pos, self.sp)):
            if p is None: continue
            im = sp.copy()
            if fl[k] > 0:
                ring = Image.new('RGBA', sp.size, (0, 0, 0, 0)); rc = sp.width / 2; rr = self.R + 14 + 10 * fl[k]
                ImageDraw.Draw(ring).ellipse([rc - rr, rc - rr, rc + rr, rc + rr], outline=(255, 222, 0, int(235 * fl[k])), width=9)
                im = Image.alpha_composite(ring, im); sc = 1 + 0.07 * fl[k]; im = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR)
            im = im.rotate(balanco(t, 1.7 * k + 0.5, 2.0 + k) * 1.4 + (-6 if k == 0 else 5), resample=Image.BICUBIC, expand=True)
            colar(L, im, p[0] - im.width / 2, p[1] - im.height / 2)
        return L

    def final(self):
        if self._final is None:
            L = self.camada(self.t_fold - 0.01); self._final = L.crop(L.getbbox())
        return self._final
    def sons(self): return [(self.t_fold, 'fecha')]

    def draw(self, fr, t):
        if t < self.t_cai[0] or t > self.t_fold + 0.55 + 0.15: return
        if t < self.t_fold:
            L = self.camada(t)
            if L is not None: compor(fr, L, W / 2, self.cy, op=0.28, off=9, blur=8)
        else:
            bola_saida(fr, self.final(), t, self.t_fold, 0.55, W / 2, self.cy)

class Grafico:
    """barras de papel que caem sobre a mesa. O mito dos 21 dias é riscado de vermelho"""
    BASE = 740; ESC = 2.4
    def __init__(self, cy=520):
        self.cy = cy
        self.barras = [  # (dias, x, tempo da queda, cor, legenda)
            (21, 215, ini('21') - 0.25, (232, 228, 218), 'mito'),
            (18, 435, ini('18') - 0.3, (214, 170, 120), 'mais rápido'),
            (66, 655, ini('66') - 0.3, (214, 170, 120), 'mediana'),
            (254, 875, ini('254') - 0.3, (214, 170, 120), 'mais lento')]
        self.sp = [faixa_papel(172, max(38, d * self.ESC), cor, 40 + i, amp=4) for i, (d, x, tq, cor, lg) in enumerate(self.barras)]
        self.t_x = ini('livro') + 0.05; self.t_mt = ini('66') + 0.05; self.t_fold = fim('254') + 0.35; self._final = None
        self.f_val = fonte_it(54, 560); self.f_leg = fonte_it(42, 480)

    def sons(self): return [(self.t_fold, 'fecha')]

    def _x_vermelho(self, L, bx, by_top, bh, p):
        d = ImageDraw.Draw(L); S = 1
        for k, ((x0, y0), (x1, y1)) in enumerate([((bx - 78, by_top - 72), (bx + 78, by_top + bh + 6)), ((bx + 78, by_top - 72), (bx - 78, by_top + bh + 6))]):
            pr = clamp(p * 2 - k)
            if pr <= 0: continue
            n = 24
            for i in range(int(n * pr)):
                u0, u1 = i / n, (i + 1) / n; wob = lambda u: 4 * math.sin(u * 7 + k * 2)
                d.line([(x0 + (x1 - x0) * u0 + wob(u0), y0 + (y1 - y0) * u0), (x0 + (x1 - x0) * u1 + wob(u1), y0 + (y1 - y0) * u1)], fill=(232, 36, 40, 215), width=15)

    def camada(self, t, final=False):
        L = Image.new('RGBA', (W, 900), (0, 0, 0, 0)); vis = False
        for i, (d, x, tq, cor, lg) in enumerate(self.barras):
            u = t - tq
            if u < 0: continue
            vis = True; sp = self.sp[i]; h = max(38, d * self.ESC)
            if u < 0.32: dy = -1100 * (1 - (u / 0.32) ** 2)
            elif u < 0.46: dy = -16 * math.sin(math.pi * (u - 0.32) / 0.14)
            else: dy = 0
            compor(L, sp, x, self.BASE - h / 2 + dy, rot=balanco(t, 1.3 * i + 0.4, 2.1) * 0.5, off=8, blur=8, op=0.30)
            if u > 0.46:                                                # número e legenda aparecem quando a barra assenta
                dr = ImageDraw.Draw(L); top = self.BASE - h + 4
                txt = f'{d} dias'; tw = dr.textlength(txt, font=self.f_val)
                if i == 2 and t > self.t_mt:                           # marca-texto na mediana
                    pm = ease_io(clamp((t - self.t_mt) / 0.7)); lay = Image.new('RGBA', (W, 900), (0, 0, 0, 0))
                    ImageDraw.Draw(lay).rectangle([x - tw / 2 - 8, top - 62, x - tw / 2 - 8 + (tw + 16) * pm, top - 8], fill=(255, 226, 0, 170)); L.alpha_composite(lay)
                dr.text((x - tw / 2, top - 62), txt, font=self.f_val, fill=TINTA)
                lw = dr.textlength(lg, font=self.f_leg); dr.text((x - lw / 2, self.BASE + 28), lg, font=self.f_leg, fill=(96, 84, 70, 255))
                if i == 0 and t > self.t_x: self._x_vermelho(L, x, self.BASE - h, h, ease_io(clamp((t - self.t_x) / 0.7)))
        return L if vis else None

    def draw(self, fr, t):
        if t < self.barras[0][2] or t > self.t_fold + 0.55 + 0.15: return
        if t < self.t_fold:
            L = self.camada(t)
            if L is not None: colar(fr, L, 0, self.cy - 450)
        else:
            if self._final is None:
                L = self.camada(self.t_fold - 0.01); self._final = L.crop(L.getbbox())
            bola_saida(fr, self._final, t, self.t_fold, 0.55, W / 2, self.cy + 40)

class Apresentador:
    """marcador do apresentador: o recorte do print, tamanho zero e zoom de 30% em frases de ênfase"""
    S0, TOPO, ZOOM = 0.927, 898, 1.3
    def __init__(self, zooms):
        self.im = Image.open(os.path.join(AQUI, 'saida', 'apresentador_recorte.png')); self.zooms = zooms; self.cache = {}
    def draw(self, fr, t):
        m = self.ZOOM if any(a <= t < b for a, b in self.zooms) else 1.0
        if m not in self.cache:
            s = self.S0 * m; self.cache[m] = self.im.resize((int(self.im.width * s), int(self.im.height * s)), Image.LANCZOS)
        p = self.cache[m]; fr.alpha_composite(p, ((W - p.width) // 2, H - int((H - self.TOPO) * m)))

# ------------------------------------------------------------------ roteiro visual
def montar():
    """linha do tempo. Faixa central (y 400 a 850): fotos e infográficos, sem intervalo. Faixa de cima (cy=270): título que sintetiza a frase."""
    neu = Neuronios(cy=620)
    art = [  # (nome, t0, hold, cx, cy, h, rot, fase)
        ('escova', -0.35, 1.45, 270, 450, 440, -6, 0.0), ('cafe', ini('café') - 0.35, 0.9, 780, 400, 400, 4, 2.1), ('celular', ini('celular') - 0.35, 1.1, 400, 650, 600, -3, 4.2),
        ('despertador', 4.0, 1.5, 780, 600, 380, 5, 1.1), ('cerebro', 6.1, 2.0, 540, 580, 430, -3, 3.0), ('maquina', 8.95, 4.6, 540, 600, 470, 2, 5.0),
        ('revista', 32.3, 2.1, 300, 600, 360, -5, 2.6),
        ('escova', 40.0, 4.35, 210, 600, 300, -6, 0.0), ('cafe', 40.55, 3.8, 520, 520, 280, 4, 2.1), ('celular', 41.1, 3.25, 860, 600, 420, -3, 4.2), ('despertador', 42.9, 1.45, 540, 720, 320, 5, 1.1),
        ('cronometro', 45.35, 1.45, 540, 580, 430, -3, 3.7), ('livro', ini('livro') - 1.0, 4.5, 270, 520, 290, -4, 1.0), ('prancheta', ini('2010') - 0.4, 4.4, 270, 520, 300, 3, 3.3),
        ('ampulheta', 67.2, 2.7, 540, 600, 480, -2, 0.7), ('ponte', 70.6, DUR - 70.6 - 1.0, 540, 620, 330, 2, 5.5)]
    cena = [Foto(a[0], a[1], a[2], a[3], a[4] + (0 if a[0] in ('livro', 'prancheta') else 40), *a[5:]) for a in art]     # fotos 40 px mais baixas: não encostam nos títulos
    cena.append(neu)
    cena.append(Foto(neu.final().copy(), 35.25, 4.15, 540, 690, 330, -2, 2.0, jornal=False))        # o par de neurônios ligados volta como lembrete da citação
    cena.append(Grafico())
    T = lambda texto, ts, ficar=0.1, **kw: TituloAbs(texto, None, cy=240, ts=ts, ficar=ficar, **kw)
    cena += [
        T('Tudo no automático', [(3.62, 3.9), (3.9, 4.2), (4.2, 4.7)], 0.0),
        T('Uma explicação no cérebro que cabe numa frase', [(6.18, 6.42), (6.42, 6.9), (6.9, 7.12), (7.12, 7.5), (8.18, 8.46), (8.46, 8.62), (8.62, 8.94), (8.94, 9.24)], 0.2),
        T('Donald Hebb, 1949', [(11.4, 11.9), (11.9, 12.28), (12.28, 13.0)], 0.25),
        T('A ligação fica mais forte', [(17.0, 17.1), (17.1, 17.54), (17.7, 17.98), (17.98, 18.34), (18.34, 18.6)], 0.1),
        T('Quanto mais repete, mais firme a ponte', [(22.64, 23.3), (23.3, 24.0), (24.6, 25.6), (25.6, 26.8), (27.0, 28.0), (28.0, 28.9), (28.9, 29.9)], 0.0),
        T('Décadas depois, Carla Shatz', [(31.44, 31.84), (31.84, 32.3), (33.22, 33.6), (33.6, 33.98)], 0.2),
        TituloAbs('“Neurônios que disparam juntos ficam ligados”', idx('neurônios', 1), idx('ligados'), cy=260, credito='Carla Shatz, 1992', ficar=0.35),
        T('Mesma rotina', [(41.46, 42.16), (42.16, 42.9)], 0.0),
        TituloAbs('Um caminho pronto', idx('caminho') - 1, idx('pronto'), cy=240, ficar=0.4),
        T('O mito dos 21 dias', [(47.3, 47.4), (47.4, 47.64), (47.64, 47.88), (48.02, 48.4), (48.4, 48.84)], 0.15),
        T('Livro de 1960', [(50.6, 50.9), (50.9, 51.0), (51.0, 51.26)], 0.1),
        T('Estudo 2010: 96 pessoas', [(55.08, 55.7), (55.7, 56.6), (57.54, 58.1), (58.1, 58.64)], 0.0),
        T('Mediana: 66 dias', [(60.4, 60.86), (61.14, 61.86), (61.86, 62.42)], 0.1),
        T('Cérebro em construção', [pal('cérebro')[1:], pal('ainda')[1:], (fim('ainda'), ini('cada') - 0.75 - 0.6 - 0.02)], 0.0),
        TituloAbs('Cada repetição engrossa a ponte', idx('cada'), idx('ponte', 1), cy=240)]
    zooms = [(ini('cabe') - 0.05, fim('frase')), (ini('neurônios', 1) - 0.05, fim('ligados')), (ini('mediana') - 0.05, fim('dias', 1)), (ini('cada') - 0.05, fim('ponte', 1) + 0.3)]
    return cena, Apresentador(zooms)

_fundo = None; _cena = None; _ap = None
def _init():
    global _fundo, _cena, _ap
    _fundo = fundo(W, H).convert('RGBA'); _cena, _ap = montar()

def quadro(k, escala, pasta):
    t = k / FPS; fr = _fundo.copy()
    for c in _cena: c.draw(fr, t)
    _ap.draw(fr, t)
    if escala != 1.0: fr = fr.resize((int(W * escala), int(H * escala)), Image.LANCZOS)
    fr.convert('RGB').save(os.path.join(pasta, f'f{k:05d}.jpg'), quality=93)

def _job(a): return quadro(*a)

def _cobertura(k):
    """fração da área de cima (y < 860) coberta por peças, sem fundo e sem apresentador"""
    t = k / 5.0; L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for c in _cena: c.draw(L, t)
    a = np.array(L.getchannel('A'))[:860] > 40
    return t, float(a.mean()), float(a[:430].mean())

def eventos_sfx(cena):
    return sorted(e for c in cena if hasattr(c, 'sons') for e in c.sons())

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; flags = [a for a in sys.argv[1:] if a.startswith('--')]
    if '--auditar' in flags:
        with Pool(4, initializer=_init) as p: r = sorted(p.map(_cobertura, range(int(DUR * 5)), chunksize=8))
        vazio = [(t, c, ct) for t, c, ct in r if c < 0.045]
        print('quadros com a área de cima quase vazia (cobertura < 4,5%):', len(vazio), 'de', len(r), ' (amostragem de 0,2 s)')
        ini_, ant = None, None
        for t, c, ct in vazio + [(1e9, 0, 0)]:
            if ini_ is None: ini_ = ant = t
            elif t - ant > 0.25: print(f'  vazio de {ini_:.1f} s a {ant + 0.2:.1f} s'); ini_ = ant = t
            else: ant = t
        topo = [t for t, c, ct in r if ct < 0.03]
        print('tempo total sem nada na metade superior (y < 430):', round(len(topo) * 0.2, 1), 's')
        sys.exit()
    saida = args[0] if args else os.path.join(AQUI, 'saida', 'episodio_preview.mp4')
    escala = float(args[1]) if len(args) > 1 else 0.5
    ks = [int(x) for x in args[2].split(',')] if len(args) > 2 else None          # quadros avulsos para conferência
    pasta = os.environ.get('EP_TMP', os.path.join(AQUI, 'saida', 'quadros')); os.makedirs(pasta, exist_ok=True)
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    N = int(DUR * FPS); lista = ks if ks else list(range(N))
    with Pool(4, initializer=_init) as p:
        for i, _ in enumerate(p.imap_unordered(_job, [(k, escala, pasta) for k in lista], chunksize=4)):
            if i % 200 == 0: print(i, '/', len(lista), flush=True)
    if not ks:
        from mixar_audio import mixar
        ev = eventos_sfx(montar()[0]); audio = os.path.join(AQUI, 'saida', 'audio_final.wav'); print(mixar(ev, audio, DUR))
        subprocess.run([FF, '-nostdin', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(pasta, 'f%05d.jpg'), '-i', audio,
                        '-t', str(DUR), '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', saida], check=True)
        shutil.rmtree(pasta); print('ok', saida)
