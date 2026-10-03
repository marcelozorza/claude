"""Vídeo das eleições: apresentador em chroma key sobre papel quadriculado, legendas, recortes e imagens de apoio.
Uso: python3 montar.py INI FIM SAIDA   (tempos no filme já cortado, em segundos). LEVE=1 renderiza 540x960."""
import os, sys, json, math, re, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
A = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, A + 'lib')
from chroma import key_rgb, grade
from papel import recorte_jornal
from animfoto import estado, sombra_papel, back, ease_out, balanco
import math
FF = os.path.expanduser('~/bin/ffmpeg')
W, H, FPS = 1080, 1920, 30
RAW = A + 'C0088.MP4'
FSUB = A + 'fonts_helv/helvetica-rounded-bold-5871d05ead8de.otf'   # Helvetica Rounded Bold
FGAR = A + '../fonts/EBGaramond.ttf'
FGARI = A + '../fonts/EBGaramond-Italic.ttf'

# ---------------------------------------------------------------- trechos do bruto (tempo do bruto)
SEGS = [(40.30, 45.55), (46.55, 52.05), (53.15, 63.05), (68.00, 76.50), (77.25, 80.28), (90.40, 94.85),
        (95.30, 103.10), (106.30, 113.82), (138.30, 146.50), (150.00, 152.40), (155.10, 168.40), (171.30, 174.00),
        (174.60, 179.80), (192.80, 197.00), (208.00, 218.60), (225.00, 234.90)]
GRADE = (0.26, 0.26, 0.26)      # temperatura, matiz, saturação do apresentador (dial 0..1)
ESCALAS = [0.64, 0.80, 0.66, 0.78, 0.62, 0.80, 0.68]   # tamanho muda 20 a 30% entre frases (para mais e para menos)

def _rms():
    w = wave.open(A + 'audio16k.wav'); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float)
    fr = 160; m = len(a) // fr
    return np.sqrt((a[:m * fr].reshape(m, fr) ** 2).mean(1)) + 1e-9
_R = None
def _quieto(t, lo, hi):
    """instante mais silencioso em [t-lo, t+hi]"""
    global _R
    if _R is None: _R = _rms()
    i0, i1 = int((t - lo) * 100), int((t + hi) * 100)
    return (i0 + int(np.argmin(_R[i0:i1]))) / 100 + 0.005

def montar_segs():
    out = []; off = 0.0
    for k, (a, b) in enumerate(SEGS):
        a2 = _quieto(a, 0.10, 0.06); b2 = _quieto(b, 0.06, 0.10)
        out.append((a2, b2, off, ESCALAS[k % len(ESCALAS)])); off += b2 - a2
    return out, off
SEGM, TOTAL = montar_segs()

def src2fin(t):
    for a, b, off, _ in SEGM:
        if a - 1e-6 <= t <= b + 1e-6: return t - a + off
    return None

# ---------------------------------------------------------------- palavras e legendas
CORR = {'Descordar': 'Discordar', 'Começa': 'Começo'}
def palavras():
    d = json.load(open(A + 'transcricao.json')); todas = [w for s in d for w in s['words']]
    out = []
    for a, b, off, _ in SEGM:
        ws = [w for w in todas if a - 0.04 <= w['s'] < b - 0.06]
        for w in ws:
            out.append([w['w'].strip(), w['s'] - a + off, min(w['e'], b) - a + off])
    # correções de texto
    i = 0; res = []
    while i < len(out):
        w, s, e = out[i]
        if w.lower().startswith('hoje') and i + 2 < len(out) and out[i + 1][0].lower() == 'você' and out[i + 2][0].lower() == 'é':
            res.append(out[i]); s0, e1 = out[i + 1][1], out[i + 2][2]; d = (e1 - s0) / 3
            for j, t in enumerate(['eu', 'vou', 'ser']): res.append([t, s0 + j * d, s0 + (j + 1) * d])
            i += 3; continue
        res.append([CORR.get(w, w), s, e]); i += 1
    return res
PAL = palavras()

def legendas(max_chars=22):
    chunks = []; cur = []
    def fecha():
        if cur: chunks.append(list(cur)); cur.clear()
    for w in PAL:
        txt = ' '.join(c[0] for c in cur + [w])
        if cur and (len(txt) > max_chars * 2 or (cur[-1][2] and w[1] - cur[-1][2] > 0.55)): fecha()
        cur.append(w)
        if re.search(r'[.?!]$', w[0]) or (w[0].endswith(',') and len(' '.join(c[0] for c in cur)) >= 14): fecha()
    fecha()
    for i, c in enumerate(chunks):
        ant = chunks[i - 1][-1][0] if i else '.'
        if re.search(r'[.?!]$', ant) and c[0][0][:1].islower(): c[0][0] = c[0][0][:1].upper() + c[0][0][1:]
    subs = []
    for i, c in enumerate(chunks):
        t0 = c[0][1]; t1 = chunks[i + 1][0][1] if i + 1 < len(chunks) and chunks[i + 1][0][1] - c[-1][2] < 0.6 else c[-1][2] + 0.25
        palavras_ = [x[0] for x in c]; txt = ' '.join(palavras_)
        # quebra em duas linhas equilibradas
        if len(txt) > max_chars:
            best = None
            for k in range(1, len(palavras_)):
                l1 = ' '.join(palavras_[:k]); l2 = ' '.join(palavras_[k:]); sc = abs(len(l1) - len(l2))
                if best is None or sc < best[0]: best = (sc, [l1, l2])
            linhas = best[1]
        else: linhas = [txt]
        subs.append((t0, t1, linhas))
    return subs
SUBS = legendas()
_fsub = ImageFont.truetype(FSUB, 64)
_subc = {}
def sub_img(linhas):
    k = '|'.join(linhas)
    if k in _subc: return _subc[k]
    lh = 76; im = Image.new('RGBA', (W, lh * len(linhas) + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(linhas):
        w = d.textlength(l, font=_fsub); d.text(((W - w) / 2, 10 + i * lh), l, font=_fsub, fill='#FFE600', stroke_width=8, stroke_fill='black')
    _subc[k] = im; return im

def achar(txt, n=0, fim=False):
    """tempo da n-ésima ocorrência da palavra (início, ou fim se fim=True)"""
    alvo = re.sub(r'[^\wÀ-ÿ]', '', txt.lower()); k = 0
    for w, s, e in PAL:
        if re.sub(r'[^\wÀ-ÿ]', '', w.lower()) == alvo:
            if k == n: return e if fim else s
            k += 1
    raise KeyError(txt)

# ---------------------------------------------------------------- fundo
def fundo():
    """papel creme quadriculado, com fibras e amassados leves (mesma cor média de antes)"""
    from papel import _ruido, _facetas
    from scipy import ndimage as ndi
    alvo = np.array([241, 229, 201], np.float32)
    im = Image.new('RGB', (W, H), tuple(int(x) for x in alvo)); d = ImageDraw.Draw(im)
    for x in range(0, W, 54): d.line([(x, 0), (x, H)], fill=(229, 215, 185), width=1)
    for y in range(0, H, 54): d.line([(0, y), (W, y)], fill=(229, 215, 185), width=1)
    a = np.array(im).astype(np.float32)
    F1, B1 = _facetas(H, W, 12, n=46)
    F2, B2 = _facetas(H, W, 29, n=210)
    F1 = ndi.gaussian_filter(F1, 7); F2 = ndi.gaussian_filter(F2, 4)
    B1 = ndi.gaussian_filter(B1, 2.6); B2 = ndi.gaussian_filter(B2, 1.8)
    ond = (ndi.gaussian_filter(_ruido((H, W), 260, 5), 4) - 0.5) * 0.05
    nuv = (_ruido((H, W), 110, 8) - 0.5) * 0.02
    fib = (_ruido((H, W), 4, 6) - 0.5) * 0.016
    gr = np.random.RandomState(4).randn(H, W) * 0.006
    luz = 1 + 0.011 * np.clip(F1, -1.5, 1.5) + 0.006 * np.clip(F2, -1.5, 1.5) - 0.022 * B1 - 0.012 * B2 + ond + nuv + fib + gr
    v = np.linspace(-1, 1, H)[:, None] ** 2 * 0.03 + np.linspace(-1, 1, W)[None, :] ** 2 * 0.03
    out = a * (luz - v)[..., None]
    out *= (alvo / out.reshape(-1, 3).mean(0))      # mantém a cor média aprovada
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')
BG = fundo()

# ---------------------------------------------------------------- elementos
class Recorte:
    """foto recortada (papel de jornal) que se desenrola de uma bola de papel e se enrola de volta"""
    def __init__(self, src, a0, a1, cx, cy, h, rot=-3, atraso=-0.10, crop=None, modo='A'):
        self.modo = modo
        im = src.copy() if isinstance(src, Image.Image) else Image.open(src).convert('RGBA')
        if crop: im = im.crop(crop)
        im.thumbnail((h * 3, h)); self.img = recorte_jornal(im, seed=int(abs(hash(str(src)[:40])) % 97))
        self.t0 = a0 + atraso; self.t1 = a1; self.cx, self.cy, self.rot = cx, cy, rot
        self.hold = max(0.35, self.t1 - self.t0 - 0.5)
        self.fase = (cx * 0.013 + cy * 0.007) % (2 * math.pi)          # recortes simultâneos balançam fora de sincronia
    def item_at(self, t): return self.img
    def pos_pos(self, im, t): return im
    def draw(self, fr, t):
        im = estado(self.item_at(t), t - self.t0, self.hold, rot=self.rot, modo=self.modo, fase=self.fase)
        if im is None: return
        im = self.pos_pos(im, t)
        im2 = sombra_papel(im)
        fr.alpha_composite(im2, (int(self.cx - im2.width / 2), int(self.cy - im2.height / 2)))
    @property
    def fim(self): return self.t0 + 0.55 + self.hold + 0.6

class Video:
    """imagem de apoio em tela cheia (clipe 1080x1920 já preparado)"""
    def __init__(self, path, a0, a1, ss=0.0):
        self.path = path; self.t0 = a0; self.t1 = a1; self.ss = ss; self.k = -2; self.p = None; self.last = None
    def _open(self, k):
        if self.p: self.p.kill()
        self.p = subprocess.Popen([FF, '-nostdin', '-loglevel', 'error', '-ss', f'{self.ss + k / FPS:.3f}', '-i', self.path, '-vf', f'fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'],
                                  stdout=subprocess.PIPE, bufsize=10 ** 8)
    def draw(self, fr, t):
        if not (self.t0 <= t < self.t1): return
        k = int(round((t - self.t0) * FPS))
        if k != self.k:
            if self.p is None or k != self.k + 1: self._open(k)
            buf = self.p.stdout.read(W * H * 4)
            if len(buf) == W * H * 4: self.last = Image.frombuffer('RGBA', (W, H), buf, 'raw', 'RGBA', 0, 1)
            self.k = k
        if self.last is not None: fr.alpha_composite(self.last)

def _gar(size, italic=False, wght=500):
    f = ImageFont.truetype(FGARI if italic else FGAR, size)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f
def _papel(w, h, seed=1):
    rng = np.random.default_rng(seed); b = np.zeros((h, w, 4), np.uint8); b[..., 0] = 252; b[..., 1] = 249; b[..., 2] = 241; b[..., 3] = 255
    n = rng.normal(0, 3.0, (h, w))
    for c in range(3): b[..., c] = np.clip(b[..., c] + n, 0, 255)
    return Image.fromarray(b, 'RGBA')
def _cartao(w, h, seed):
    p = _papel(w, h, seed); m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    rng = np.random.default_rng(seed)
    d.polygon([(rng.uniform(0, 5), rng.uniform(0, 5)), (w - rng.uniform(0, 5), rng.uniform(0, 7)), (w - rng.uniform(0, 4), h - rng.uniform(0, 5)), (rng.uniform(0, 4), h - rng.uniform(0, 4))], fill=255)
    p.putalpha(m); return p

class Estudo:
    """etiqueta no alto com o autor/ano/revista e um cartão com o título e o resumo, atrás do apresentador"""
    def __init__(self, a0, a1, autores, revista, titulo, resumo, cartao_y=250, rot=-2):
        self.t0 = a0; self.t1 = a1; self.rot = rot; self.cy = cartao_y
        f1 = _gar(44, True); f2 = _gar(33, True)
        d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        w = int(max(d.textlength(autores, font=f1), d.textlength(revista, font=f2)) + 70); h = 150
        lab = _cartao(w, h, 11); ld = ImageDraw.Draw(lab)
        ld.text(((w - d.textlength(autores, font=f1)) / 2, 20), autores, font=f1, fill=(40, 34, 28, 255))
        ld.text(((w - d.textlength(revista, font=f2)) / 2, 82), revista, font=f2, fill=(90, 80, 68, 255))
        self.lab = sombra_papel(lab, off=6, blur=5, op=0.35)
        # cartão do resumo
        ft = _gar(74, False, 600); fr_ = _gar(46)
        cw = 940; linhas = []
        for par in resumo:
            atual = ''
            for pal in par.split():
                if d.textlength((atual + ' ' + pal).strip(), font=fr_) > cw - 100: linhas.append(atual); atual = pal
                else: atual = (atual + ' ' + pal).strip()
            if atual: linhas.append(atual)
        tl = []; atual = ''
        for pal in titulo.split():
            if d.textlength((atual + ' ' + pal).strip(), font=ft) > cw - 100: tl.append(atual); atual = pal
            else: atual = (atual + ' ' + pal).strip()
        if atual: tl.append(atual)
        ch = 50 + len(tl) * 86 + 26 + len(linhas) * 60 + 40
        card = _cartao(cw, ch, 21); cd = ImageDraw.Draw(card); y = 40
        for l in tl: cd.text((50, y), l, font=ft, fill=(30, 26, 22, 255)); y += 86
        cd.line([(50, y + 6), (cw - 50, y + 6)], fill=(200, 60, 40, 255), width=4); y += 26
        for l in linhas: cd.text((50, y), l, font=fr_, fill=(70, 62, 52, 255)); y += 60
        self.card = sombra_papel(card, off=12, blur=11, op=0.30)
    def _pop(self, t, t0, t1):
        if t < t0 or t >= t1: return None
        if t < t0 + 0.22: return max(0.05, back((t - t0) / 0.22))
        if t > t1 - 0.12: return max(0.05, 1 - (t - (t1 - 0.12)) / 0.12)
        return 1.0
    def draw(self, fr, t):
        s = self._pop(t, self.t0, self.t1)
        if s is None: return
        u = t - self.t0
        c = self.card.resize((int(self.card.width * s), int(self.card.height * s)), Image.BILINEAR).rotate(self.rot + balanco(u, 0.8, 2.4), resample=Image.BICUBIC, expand=True)
        fr.alpha_composite(c, (int(W / 2 - c.width / 2), int(self.cy - c.height / 2)))
        l = self.lab.resize((int(self.lab.width * s), int(self.lab.height * s)), Image.BILINEAR).rotate(balanco(u, 4.6, 0.3), resample=Image.BICUBIC, expand=True)
        fr.alpha_composite(l, (int(W / 2 - l.width / 2), int(115 - l.height / 2)))


class Logo:
    """cartão do logo: desenrola de uma bola de papel no fim e fica até o último quadro"""
    def __init__(self, t0, dur_in=1.0):
        self.img = Image.open(A + 'cut/logo_card.png').convert('RGBA'); self.t0 = t0; self.d = dur_in
    def draw(self, fr, t):
        u = t - self.t0
        if u < 0: return
        if u >= self.d: fr.alpha_composite(self.img); return
        from animfoto import _bola, ease_io
        p = u / self.d; c = 1 - ease_io(p)
        sc = 0.55 + 0.45 * back(min(1, u / 0.08)) if u < 0.08 else 1.0
        im = _bola(self.img, 'A').quadro(c)
        if sc != 1.0: im = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR)
        im2 = sombra_papel(im, off=14, blur=12, op=0.35)
        fr.alpha_composite(im2, (int(W / 2 - im2.width / 2), int(H / 2 - im2.height / 2)))
    @property
    def fim(self): return self.t0 + self.d + 2.2


def _traco(size, p0, p1, prog, larg, seed):
    """traço de marca-texto vermelho, translúcido, com textura, de p0 até a fração prog do caminho p1"""
    from scipy import ndimage as ndi
    w, h = size; S = 2
    m = Image.new('L', (w * S, h * S), 0); d = ImageDraw.Draw(m)
    n = max(2, int(80 * prog)); rng = np.random.RandomState(seed)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); nx, ny = -math.sin(ang), math.cos(ang)
    ant = None
    for k in range(n + 1):
        u = prog * k / n
        wob = 7 * math.sin(u * 7 + seed)
        q = (p0[0] + (p1[0] - p0[0]) * u + nx * wob, p0[1] + (p1[1] - p0[1]) * u + ny * wob)
        if ant: d.line([(ant[0] * S, ant[1] * S), (q[0] * S, q[1] * S)], fill=255, width=int(larg * S))
        ant = q
    mm = np.array(m).astype(np.float32) / 255
    mm = ndi.gaussian_filter(mm, 1.4)
    ruido = ndi.gaussian_filter(rng.rand(h * S, w * S), 2.5) - 0.5
    borda = mm - ndi.grey_erosion(mm, size=(int(larg * 0.30) * 2 + 1,) * 2)
    alfa = np.clip(mm * (0.56 + 0.30 * ruido) + 0.20 * borda, 0, 1)
    alfa = np.array(Image.fromarray((alfa * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    lay = np.zeros((h, w, 4), np.uint8); lay[..., 0] = 232; lay[..., 1] = 36; lay[..., 2] = 40; lay[..., 3] = (alfa * 255).astype(np.uint8)
    return Image.fromarray(lay, 'RGBA')

class RecorteX(Recorte):
    """recorte com um X de marca-texto vermelho desenhado por cima (dois traços)"""
    def __init__(self, src, a0, a1, cx, cy, h, tx0, tx1, rot=-3):
        super().__init__(src, a0, a1, cx, cy, h, rot=rot)
        self.tx0, self.tx1 = tx0, tx1; self.cache = {}
        W_, H_ = self.img.size; self.a = np.array(self.img.getchannel('A'))
    def _com_x(self, p):
        k = round(p, 2)
        if k in self.cache: return self.cache[k]
        w, h = self.img.size; larg = h * 0.12
        base = self.img.copy()
        for i, (p0, p1) in enumerate([((w * 0.20, h * 0.20), (w * 0.82, h * 0.82)), ((w * 0.82, h * 0.18), (w * 0.20, h * 0.84))]):
            pr = min(1, max(0, p * 2 - i))
            if pr <= 0: continue
            camada = _traco((w, h), p0, p1, pr, larg, 3 + i)
            al = np.array(camada.getchannel('A')).astype(np.float32) * (np.array(self.img.getchannel('A')).astype(np.float32) / 255)
            camada.putalpha(Image.fromarray(al.astype(np.uint8)))
            base.alpha_composite(camada)
        self.cache[k] = base; return base
    def item_at(self, t):
        if t < self.tx0: return self.img
        return self._com_x(min(1.0, (t - self.tx0) / (self.tx1 - self.tx0)))

class Botao(Recorte):
    """botão vermelho que é apertado por um dedo (afunda e solta raios)"""
    def __init__(self, src, a0, a1, cx, cy, h, t_press, dedo, h_dedo=620):
        super().__init__(src, a0, a1, cx, cy, h, rot=0)
        self.tp = t_press
        d = Image.open(dedo).convert('RGBA'); d.thumbnail((h_dedo * 3, h_dedo)); self.dedo = d
        al = np.array(d.getchannel('A')); ys = np.where(al.max(1) > 128)[0]; yb = ys.max()
        xs = np.where(al[yb - 6] > 128)[0]; self.ponta = (int(xs.mean()), yb)
        self.dd = sombra_papel(d, off=8, blur=7, op=0.28)
    def pos_pos(self, im, t):
        if self.tp <= t < self.tp + 0.3 and im is not None:
            f = 0.90 + 0.10 * min(1, (t - self.tp) / 0.3)
            im = im.resize((im.width, int(im.height * f)), Image.BILINEAR)
        return im
    def draw(self, fr, t):
        super().draw(fr, t)
        u = t - self.tp
        if not (-0.55 <= u < 0.75): return
        alvo = (self.cx + 6, self.cy - self.img.height * 0.28)           # topo do botão
        if u < 0: off = 700 * (1 - ease_out((u + 0.55) / 0.55))
        elif u < 0.30: off = -16 * math.sin(math.pi * u / 0.30)
        else: off = 700 * ((u - 0.30) / 0.45) ** 2
        pad = 21
        fr.alpha_composite(self.dd, (int(alvo[0] - self.ponta[0] - pad), int(alvo[1] - off - self.ponta[1] - pad)))
        if 0 <= u < 0.30:
            d = ImageDraw.Draw(fr); r0 = 90 + 150 * (u / 0.30); r1 = r0 + 60
            for k in range(8):
                a = k * math.pi / 4 + 0.2
                d.line([(alvo[0] + r0 * math.cos(a), alvo[1] + r0 * math.sin(a) * 0.8), (alvo[0] + r1 * math.cos(a), alvo[1] + r1 * math.sin(a) * 0.8)], fill=(255, 205, 40, 255), width=14)

def siluetas_img():
    """duas silhuetas (azul e vermelha) e um X no meio: lado A e lado B"""
    S = 2; w, h = 1000 * S, 560 * S
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def pessoa(cx, cor):
        d.ellipse([cx - 95 * S, 40 * S, cx + 95 * S, 230 * S], fill=cor)
        d.pieslice([cx - 190 * S, 250 * S, cx + 190 * S, 250 * S + 640 * S], 180, 360, fill=cor)
        d.rectangle([cx - 190 * S, 560 * S, cx + 190 * S, h], fill=(0, 0, 0, 0))
        d.rectangle([cx - 40 * S, 215 * S, cx + 40 * S, 300 * S], fill=cor)
    pessoa(200 * S, (46, 108, 222, 255)); pessoa(800 * S, (226, 60, 48, 255))
    for ang in (45, -45):
        b = Image.new('RGBA', (w, h), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
        bd.rounded_rectangle([500 * S - 150 * S, 290 * S - 26 * S, 500 * S + 150 * S, 290 * S + 26 * S], radius=26 * S, fill=(34, 30, 28, 255))
        im.alpha_composite(b.rotate(ang, center=(500 * S, 290 * S), resample=Image.BICUBIC))
    im = im.resize((1000, 560), Image.LANCZOS)
    ruido = (np.random.RandomState(2).randn(560, 1000) * 5)[..., None]
    a = np.array(im).astype(np.float32); a[..., :3] = np.clip(a[..., :3] + ruido, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')

# ---------------------------------------------------------------- roteiro visual
def beats():
    """só motion graphics (sem imagens de apoio em vídeo)"""
    E = []; C = lambda n: A + f'cut/{n}.png'
    # 1: gancho
    E.append(Recorte(C('folha1_2'), achar('dinheiro'), achar('tudo', 0, True), 430, 560, 540, rot=-5))
    E.append(Recorte(A + 'urna_still.png', achar('urna'), achar('você', 1, True), 800, 690, 650, rot=4))
    # 3: megafone proibido (X de marca-texto)
    tx = achar('campanha') - 0.10
    E.append(RecorteX(C('folha3_0'), achar('canal'), achar('aparecer', 0, True) + 0.2, 540, 640, 640, tx, tx + 0.85, rot=-3))
    # 4: vendas, comércio, produção, joinha em "legítimo"
    fim4 = achar('legítimo') - 0.55
    E.append(Recorte(C('folha1_0'), achar('vendas'), fim4, 255, 650, 420, rot=-4))
    E.append(Recorte(C('folha1_2'), achar('comércio'), fim4, 560, 470, 300, rot=3))
    E.append(Recorte(C('folha1_1'), achar('produção'), fim4, 850, 640, 440, rot=4))
    E.append(Recorte(C('folha3_1'), achar('legítimo') - 0.05, achar('legítimo', 0, True) + 0.55, 540, 640, 620, rot=-3))
    # 5: raiva e urgência
    E.append(Recorte(C('folha1_3'), achar('raiva', 0), achar('urgente', 0, True), 320, 600, 520, rot=-4))
    E.append(Recorte(C('folha1_4'), achar('urgente', 0), achar('urgente', 0, True) + 0.3, 800, 600, 380, rot=5))
    # 6 e 7: estudos
    E.append(Estudo(achar('Estudos'), achar('momento', 0, True) + 0.2, 'Lerner e Keltner, 2001', 'Journal of Personality and Social Psychology',
                    'Fear, anger, and risk',
                    ['Quem está com raiva sente certeza e controle: faz estimativas de risco mais otimistas e escolhe opções mais arriscadas. O medo produz o efeito contrário.'], cartao_y=360))
    E.append(Recorte(C('folha1_5'), achar('enxerga'), achar('momento', 0, True), 780, 790, 330, rot=4))
    E.append(Estudo(achar('pesquisas'), achar('recuperar', 0, True) + 0.25, 'Kahneman e Tversky, 1979', 'Econometrica',
                    'Prospect theory: an analysis of decision under risk',
                    ['Diante de ganhos, as pessoas evitam o risco. Diante de perdas, passam a buscar o risco. Perder pesa mais do que ganhar.'], cartao_y=380))
    E.append(Recorte(C('folha2_0'), achar('perdendo'), achar('recuperar', 0, True), 300, 800, 330, rot=-4))
    # 8: lado A e lado B
    E.append(Recorte(siluetas_img(), achar('todo'), achar('primeiro', 0, True), 540, 650, 560, rot=-2))
    # 9: pergunta
    E.append(Recorte(C('folha2_2'), achar('empurrando'), achar('séria', 0, True), 300, 600, 460, rot=-4))
    E.append(Recorte(C('folha2_1'), achar('olhar'), achar('direito', 0, True) + 0.5, 800, 620, 430, rot=5))
    # 11: a porta (no meio, 50% maior)
    E.append(Recorte(C('folha2_5'), achar('porta', 1), achar('fazer', 2, True), 540, 700, 840, rot=0))
    # 12: político assustado
    E.append(Recorte(C('folha3_2'), achar('político', 1), achar('poder', 0, True) + 0.3, 540, 640, 680, rot=-2))
    # 13: tirar ele de lá (cadeira no meio, 50% maior)
    E.append(Recorte(C('folha2_3'), achar('tirar'), achar('depois', 0, True), 540, 680, 705, rot=2))
    # 14: apertar o botão
    E.append(Botao(C('folha3_3'), achar('apertar') - 0.2, achar('botão', 0, True) + 0.9, 540, 780, 480, achar('botão'), C('folha3_4')))
    # 15: pensar com calma
    E.append(Recorte(C('folha3_5'), achar('pensar') - 0.2, achar('calma', 0, True) + 0.6, 540, 650, 700, rot=-2))
    # fim: logo
    E.append(Logo(TOTAL + 0.15))
    return E
ELEMS = beats()

# ---------------------------------------------------------------- apresentador
def pres_frames(t0, t1):
    for a, b, off, sc in SEGM:
        s = max(t0, off); e = min(t1, off + (b - a))
        if e <= s + 1e-6: continue
        dur = e - s; ss = a + (s - off)
        w = int(round(W * sc)); h = int(round(1260 * sc))
        p = subprocess.Popen([FF, '-nostdin', '-loglevel', 'error', '-ss', f'{ss:.3f}', '-i', RAW, '-t', f'{dur + 0.05:.3f}',
                              '-vf', f'crop=1080:1260:0:300,scale={w}:{h}:flags=lanczos,fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                             stdout=subprocess.PIPE, bufsize=10 ** 8)
        n = int(round(dur * FPS))
        for k in range(n):
            buf = p.stdout.read(w * h * 3)
            if len(buf) < w * h * 3: break
            yield s + k / FPS, Image.fromarray(grade(key_rgb(np.frombuffer(buf, np.uint8).reshape(h, w, 3)), *GRADE), 'RGBA'), (W - w) // 2, H - h
        p.kill()

def audio(out):
    fc = []; n = len(SEGM)
    for i, (a, b, off, _) in enumerate(SEGM):
        d = b - a
        fc.append(f'[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,pan=mono|c0=0.5*c0+0.5*c1,afade=t=in:d=0.012,afade=t=out:st={d - 0.012:.3f}:d=0.012[a{i}]')
    fc.append(''.join(f'[a{i}]' for i in range(n)) + f'concat=n={n}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=9[o]')
    subprocess.run([FF, '-nostdin', '-loglevel', 'error', '-y', '-i', RAW, '-filter_complex', ';'.join(fc), '-map', '[o]', '-ar', '48000', out], check=True)

def render(t0, t1, saida):
    solo = os.environ.get('BGONLY') == '1'          # só o fundo: sem apresentador, sem legenda, sem áudio
    leve = os.environ.get('LEVE') == '1'
    if solo:
        vf = (['-vf', 'scale=540:960', '-c:v', 'libx264', '-b:v', '1500k', '-preset', 'fast'] if leve else ['-c:v', 'libx264', '-crf', '17', '-maxrate', '12M', '-bufsize', '24M', '-preset', 'medium']) + ['-pix_fmt', 'yuv420p', '-movflags', '+faststart']
        enc = subprocess.Popen([FF, '-nostdin', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an'] + vf + [saida], stdin=subprocess.PIPE)
        n = int(round((t1 - t0) * FPS))
        for k in range(n):
            t = t0 + k / FPS; fr = BG.copy()
            for el in ELEMS:
                if not isinstance(el, Logo): el.draw(fr, t)
            for el in ELEMS:
                if isinstance(el, Logo): el.draw(fr, t)
            enc.stdin.write(fr.convert('RGB').tobytes())
            if k % 150 == 0: print(f'{t:.1f}s', flush=True)
        enc.stdin.close(); enc.wait(); print('ok', saida); return
    aud = A + 'audio_final.wav'
    if not os.path.exists(aud): audio(aud)
    vf = ['-vf', 'scale=540:960', '-c:v', 'libx264', '-b:v', '1100k', '-preset', 'fast', '-movflags', '+faststart'] if leve else ['-c:v', 'libx264', '-crf', '18', '-preset', 'medium']
    enc = subprocess.Popen([FF, '-nostdin', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-ss', f'{t0:.3f}', '-i', aud, '-map', '0:v', '-map', '1:a'] + vf +
                           ['-af', 'apad', '-t', f'{t1 - t0:.3f}', '-c:a', 'aac', '-b:a', '160k', '-pix_fmt', 'yuv420p', saida], stdin=subprocess.PIPE)
    def quadros():
        ult = t0 - 1.0 / FPS
        for t, pr, x, y in pres_frames(t0, min(t1, TOTAL)):
            ult = t; yield t, (pr, x, y)
        t = ult + 1.0 / FPS
        while t < t1 - 1e-6:
            yield t, None; t += 1.0 / FPS
    for t, p in quadros():
        fr = BG.copy()
        for el in ELEMS:
            if not isinstance(el, Logo): el.draw(fr, t)
        if p: fr.alpha_composite(p[0], (p[1], p[2]))
        s = next((s for s in SUBS if s[0] <= t < s[1]), None)
        if s: fr.alpha_composite(sub_img(s[2]), (0, 1470))
        for el in ELEMS:
            if isinstance(el, Logo): el.draw(fr, t)
        enc.stdin.write(fr.convert('RGB').tobytes())
        if int(t * FPS) % 150 == 0: print(f'{t:.1f}s', flush=True)
    enc.stdin.close(); enc.wait(); print('ok', saida)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('TOTAL', round(TOTAL, 2));
        for s in SUBS: print(f'{s[0]:6.2f}-{s[1]:6.2f}', ' / '.join(s[2]))
    else:
        render(float(sys.argv[1]), float(sys.argv[2]), sys.argv[3])
