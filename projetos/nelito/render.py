import math, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 30.0
N = int(DUR * FPS)
RED = (225, 30, 30); GOLD = (232, 184, 76); WHITE = (245, 243, 238); CREAM = (236, 228, 208)
FD = 'fonts/'
_fc = {}
def font(name, size, var=None):
    k = (name, size, var)
    if k not in _fc:
        f = ImageFont.truetype(FD + name, size)
        if var: f.set_variation_by_name(var)
        _fc[k] = f
    return _fc[k]

_tc = {}
def text_img(txt, fnt, color, spacing=0, stroke=0, stroke_fill=None):
    k = (txt, id(fnt), color, spacing, stroke)
    if k in _tc: return _tc[k]
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    if spacing:
        widths = [d.textlength(c, font=fnt) for c in txt]
        w = int(sum(widths) + spacing * (len(txt) - 1)) + 2 * stroke + 4
    else:
        w = int(d.textlength(txt, font=fnt)) + 2 * stroke + 4
    asc, desc = fnt.getmetrics()
    h = asc + desc + 2 * stroke + 4
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
    if spacing:
        x = stroke + 2
        for c, cw in zip(txt, widths):
            dd.text((x, stroke + 2), c, font=fnt, fill=color, stroke_width=stroke, stroke_fill=stroke_fill); x += cw + spacing
    else:
        dd.text((stroke + 2, stroke + 2), txt, font=fnt, fill=color, stroke_width=stroke, stroke_fill=stroke_fill)
    im = im.crop(im.getbbox())
    _tc[k] = im
    return im

def paste(canvas, im, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if alpha <= 0.01: return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        a = im.getchannel('A').point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_in_out(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def clamp01(x): return min(max(x, 0.0), 1.0)
def slam(t, t0, big=1.6):
    """scale that slams from big to 1 in 0.15s after t0"""
    p = (t - t0) / 0.15
    if p < 0: return None
    return 1 + (big - 1) * (1 - ease_out(p))

rng = np.random.default_rng(7)
# precomputed layers
yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
VIGN = np.clip(1.15 - r ** 2 * 0.9, 0.25, 1.0)[..., None].astype(np.float32)
GRAIN = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(8)]
DUST = rng.uniform(0, 1, (160, 4))  # x,y,speed,size

def radial_bg(color, cx=0.5, cy=0.45, spread=0.55, base=6):
    rr = np.sqrt(((xx / W - cx) / spread) ** 2 + ((yy / H - cy) / (spread * 1.6)) ** 2)
    g = np.clip(1 - rr, 0, 1) ** 2
    arr = base + g[..., None] * np.array(color, np.float32)[None, None, :]
    return np.clip(arr, 0, 255).astype(np.uint8)

BG_RED = radial_bg((120, 10, 10)); BG_BLUE = radial_bg((20, 50, 110)); BG_GOLD = radial_bg((110, 80, 20))
BG_DARK = radial_bg((40, 40, 45)); BG_SPOT = radial_bg((90, 90, 95), cy=0.2, spread=0.4)

def newspaper_layer(seed):
    rs = random.Random(seed)
    im = Image.new('RGBA', (W + 400, H + 400), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cols = 4; cw = (W + 400) // cols
    for c in range(cols):
        y = rs.randint(0, 120)
        while y < H + 400:
            if rs.random() < 0.08:
                d.rectangle([c * cw + 20, y, c * cw + cw - 20, y + 60], fill=(200, 200, 200, 70)); y += 90; continue
            ww = rs.randint(int(cw * 0.6), cw - 40)
            d.rectangle([c * cw + 20, y, c * cw + 20 + ww, y + 10], fill=(200, 200, 200, 40)); y += 22
    return im.filter(ImageFilter.GaussianBlur(1.5)).rotate(-8, resample=Image.BICUBIC)
NEWS = newspaper_layer(3)

def tv_static(t):
    n = rng.integers(0, 255, (H // 6, W // 6), dtype=np.uint8)
    im = Image.fromarray(n).resize((W, H), Image.NEAREST).convert('RGB')
    return np.asarray(im)

def scanlines(arr, strength=0.25):
    arr = arr.astype(np.float32); arr[::4] *= (1 - strength); return arr

def dust(canvas, t, color=(255, 255, 255), n=120):
    d = ImageDraw.Draw(canvas)
    for i in range(n):
        x0, y0, sp, sz = DUST[i]
        x = (x0 * W + math.sin(t * 0.7 + i) * 30) % W
        y = (y0 * H - t * (20 + sp * 60)) % H
        s = 1 + sz * 3; a = int(60 + 120 * sp)
        d.ellipse([x - s, y - s, x + s, y + s], fill=color + (a,))

def light_beam(canvas, t, x=W / 2, top=-100, color=(255, 240, 210), a=70, spread=520):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    flick = 0.85 + 0.15 * math.sin(t * 40) * math.sin(t * 13)
    d.polygon([(x - 40, top), (x + 40, top), (x + spread, H), (x - spread, H)], fill=color + (int(a * flick),))
    canvas.alpha_composite(lay.filter(ImageFilter.GaussianBlur(40)))

# ---------------- timeline (seconds) ----------------
CUTS = [0, 1.2, 4.0, 6.3, 9.0, 12.6, 15.7, 18.3, 20.8, 23.45, 25.3, 28.0, 30.0]
HITS = [4.0, 9.0, 9.5, 11.36, 12.6, 13.7, 15.24, 15.7, 17.06, 18.3, 20.8, 21.4, 22.12, 23.45, 28.0]  # flash + shake moments

def scene(t):
    if t < 1.2: return s_intro(t)
    if t < 4.0: return s_pais(t)
    if t < 6.3: return s_homem(t)
    if t < 9.0: return s_type(t)
    if t < 12.6: return s_sensa(t)
    if t < 15.7: return s_tv(t)
    if t < 18.3: return s_eva(t)
    if t < 20.8: return s_cinema(t)
    if t < 23.45: return s_triade(t)
    if t < 28.0: return s_nome(t)
    return s_final(t)

def base(arr): return Image.fromarray(arr).convert('RGBA')

def s_intro(t):
    c = base(np.full((H, W, 3), 4, np.uint8))
    fl = 0.0 if (int(t * 30) % 7 == 0) else 1.0
    a = clamp01((t - 0.15) / 0.5) * fl
    paste(c, text_img('BASEADO EM FATOS REAIS', font('Oswald.ttf', 72), WHITE, spacing=10), W / 2, H / 2, alpha=a)
    paste(c, text_img('(INFELIZMENTE)', font('Oswald.ttf', 44), (170, 170, 170), spacing=8), W / 2, H / 2 + 90, alpha=clamp01((t - 0.7) / 0.3) * fl)
    return c

def s_pais(t):
    c = base(BG_DARK)
    lt = t - 1.2
    paste(c, NEWS, W / 2 + lt * 25, H / 2 - lt * 40, scale=1.05 + lt * 0.02)
    dust(c, t)
    z = 1 + lt * 0.03
    lines = [('NUM PAÍS ONDE', 1.2, 'Anton.ttf', 96, WHITE, 640), ('A REALIDADE', 2.08, 'Anton.ttf', 150, WHITE, 800),
             ('JÁ PARECE', 2.94, 'Anton.ttf', 96, WHITE, 960)]
    for txt, t0, f, s, col, y in lines:
        if t >= t0:
            p = ease_out((t - t0) / 0.35)
            paste(c, text_img(txt, font(f, s), col), W / 2, y + (1 - p) * 40, scale=z, alpha=p)
    sc = slam(t, 3.26, 2.2)
    if sc:
        paste(c, text_img('PIADA', font('Anton.ttf', 330), RED), W / 2, 1260, scale=sc * z, rot=-4)
    return c

def s_homem(t):
    c = base(BG_SPOT)
    light_beam(c, t, a=60)
    dust(c, t, (255, 240, 210))
    lt = t - 4.0
    z = 1 + lt * 0.04
    if t >= 4.04: paste(c, text_img('UM HOMEM', font('Anton.ttf', 170), WHITE), W / 2, 700, scale=z, alpha=ease_out((t - 4.04) / 0.3))
    if t >= 4.74: paste(c, text_img('TEVE UMA IDEIA', font('Anton.ttf', 110), WHITE), W / 2, 880, scale=z, alpha=ease_out((t - 4.74) / 0.3))
    sc = slam(t, 5.32, 1.8)
    if sc:
        jit = (random.Random(int(t * 30)).uniform(-6, 6)) if t < 5.9 else 0
        paste(c, text_img('PERIGOSA', font('Anton.ttf', 230), RED), W / 2 + jit, 1100, scale=sc * z)
    return c

PAPER = None
def s_type(t):
    global PAPER
    if PAPER is None:
        n = rng.normal(0, 6, (H, W, 1)).astype(np.float32)
        PAPER = np.clip(np.array(CREAM, np.float32)[None, None] + n, 0, 255).astype(np.uint8)
    c = base(PAPER)
    lt = t - 6.3
    z = 1.0 + lt * 0.035
    full1, full2 = 'TRANSFORMAR', 'A PIADA'
    n = int(clamp01((t - 6.32) / 1.1) * (len(full1) + len(full2)))
    s1 = full1[:n]; s2 = full2[:max(0, n - len(full1))]
    cursor = '_' if int(t * 4) % 2 == 0 else ' '
    f = font('SpecialElite.ttf', 120)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if s1: paste(lay, text_img(s1 + (cursor if not s2 else ''), f, (30, 28, 26)), W / 2, 760)
    if s2: paste(lay, text_img(s2 + cursor, f, (30, 28, 26)), W / 2, 900)
    paste(c, lay, W / 2, H / 2, scale=z)
    sc = slam(t, 7.6, 2.5)
    if sc:
        paste(c, text_img('EM', font('Anton.ttf', 110), RED), W / 2, 1080, scale=sc * z, rot=6)
    sc = slam(t, 8.12, 2.8)
    if sc:
        st = text_img('NOTÍCIA', font('Anton.ttf', 250), RED)
        box = Image.new('RGBA', (st.width + 80, st.height + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(box)
        d.rectangle([4, 4, box.width - 5, box.height - 5], outline=RED, width=14)
        box.alpha_composite(st, (40, 35))
        paste(c, box, W / 2, 1300, scale=sc * z * 0.95, rot=8, alpha=0.93)
    return c

def s_sensa(t):
    lt = t - 9.0
    if t < 11.3:
        c = base(BG_RED); dust(c, t)
        sc = slam(t, 9.5, 2.0)
        paste(c, text_img('EM', font('Oswald.ttf', 70), WHITE, spacing=16), W / 2, 640, alpha=ease_out(lt / 0.3))
        if sc:
            paste(c, text_img('2009', font('Anton.ttf', 420), WHITE), W / 2, 930, scale=sc * (1 + (t - 9.5) * 0.05))
        if t >= 10.3:
            paste(c, text_img('ELE AJUDOU A CRIAR', font('Oswald.ttf', 64), WHITE, spacing=6), W / 2, 1260, alpha=ease_out((t - 10.3) / 0.3))
        return c
    # masthead
    c = base(BG_DARK)
    z = 1 + (t - 11.3) * 0.05
    band = Image.new('RGBA', (W + 200, 560), CREAM + (255,)); d = ImageDraw.Draw(band)
    d.line([(60, 60), (band.width - 60, 60)], fill=(20, 20, 20), width=6)
    d.line([(60, 480), (band.width - 60, 480)], fill=(20, 20, 20), width=6)
    d.line([(60, 494), (band.width - 60, 494)], fill=(20, 20, 20), width=2)
    band.alpha_composite(text_img('ANO I  ·  2009  ·  EDIÇÃO EXTRA', font('Oswald.ttf', 30), (40, 40, 40), spacing=6), (band.width // 2 - 260, 80))
    m = text_img('Sensacionalista', font('PlayfairDisplay.ttf', 150, 'Black'), (15, 15, 15))
    band.alpha_composite(m, ((band.width - m.width) // 2, 190))
    s = text_img('UM JORNAL ISENTO DE VERDADE', font('Oswald.ttf', 40), RED, spacing=8)
    band.alpha_composite(s, ((band.width - s.width) // 2, 410))
    sc = slam(t, 11.36, 1.5) or 1
    paste(c, band, W / 2, H / 2, scale=sc * z * 0.9, rot=-3)
    return c

def s_tv(t):
    lt = t - 12.6
    st = tv_static(t)
    arr = (st.astype(np.float32) * (0.9 if lt < 0.25 else 0.18)).astype(np.uint8)
    c = base(arr)
    if lt >= 0.25:
        d = ImageDraw.Draw(c)
        paste(c, text_img('ESCREVEU PARA', font('Oswald.ttf', 60), WHITE, spacing=10), W / 2, 560, alpha=ease_out((lt - 0.25) / 0.3))
        # TV frame
        fr = Image.new('RGBA', (900, 620), (0, 0, 0, 0)); fd = ImageDraw.Draw(fr)
        fd.rounded_rectangle([0, 0, 899, 619], radius=60, outline=WHITE + (230,), width=10)
        paste(c, fr, W / 2, 1000)
        if t < 15.24:
            sc = slam(t, 13.7, 1.8)
            if t >= 12.95 and t < 13.7:
                paste(c, text_img('TV GLOBO', font('Oswald.ttf', 70), GOLD, spacing=12), W / 2, 1000, alpha=0.9)
            if sc:
                paste(c, text_img('CASSETA', font('Anton.ttf', 170), WHITE), W / 2, 900, scale=sc)
                paste(c, text_img('& PLANETA', font('Anton.ttf', 150), GOLD), W / 2, 1090, scale=sc)
        else:
            sc = slam(t, 15.24, 2.0)
            paste(c, text_img('ZORRA', font('Anton.ttf', 300), RED), W / 2, 1000, scale=sc)
        paste(c, text_img('● REC', font('Oswald.ttf', 44), RED), 180, 260, alpha=1.0 if int(t * 2) % 2 == 0 else 0.2)
    out = np.asarray(c.convert('RGB'))
    return base(scanlines(out, 0.35).astype(np.uint8))

def s_eva(t):
    lt = t - 15.7
    c = base(BG_BLUE); dust(c, t, (180, 200, 255))
    z = 1 + lt * 0.04
    if t >= 15.75: paste(c, text_img('LEVOU O', font('Oswald.ttf', 70), WHITE, spacing=14), W / 2, 700, alpha=ease_out((t - 15.75) / 0.4))
    if t >= 16.4: paste(c, text_img('DRAMA', font('PlayfairDisplay.ttf', 200, 'Black'), WHITE), W / 2, 860, scale=z, alpha=ease_out((t - 16.4) / 0.4))
    if t >= 17.0:
        p = ease_out((t - 17.0) / 0.6)
        paste(c, text_img('FILHAS DE EVA', font('PlayfairDisplay.ttf', 100, 'Bold'), GOLD, spacing=4), W / 2, 1100 + (1 - p) * 30, scale=z, alpha=p)
        paste(c, text_img('SÉRIE · 2021', font('Oswald.ttf', 40), (200, 210, 230), spacing=10), W / 2, 1210, alpha=p * 0.9)
    return c

def s_cinema(t):
    lt = t - 18.3
    silence = t >= 19.75
    c = base(np.full((H, W, 3), 5, np.uint8))
    light_beam(c, t, x=W / 2, top=-100, a=0 if silence else 80, spread=600)
    d = ImageDraw.Draw(c)
    # film strip edges
    off = (t * 600) % 80
    for x0 in (30, W - 90):
        d.rectangle([x0 - 10, 0, x0 + 70, H], fill=(18, 18, 18, 255))
        y = -80 + off
        while y < H:
            d.rounded_rectangle([x0 + 12, y, x0 + 48, y + 44], radius=6, fill=(230, 230, 220, 255) if not silence else (60, 60, 60, 255)); y += 80
    if not silence:
        if t >= 18.4: paste(c, text_img('E O RISO', font('Anton.ttf', 150), WHITE), W / 2, 760, alpha=ease_out((t - 18.4) / 0.3))
        sc = slam(t, 19.3, 1.7)
        if sc:
            paste(c, text_img('PARA O CINEMA', font('Anton.ttf', 130), GOLD), W / 2, 940, scale=sc)
            paste(c, text_img('DETETIVE MADEINUSA', font('Oswald.ttf', 54), WHITE, spacing=10), W / 2, 1080, alpha=ease_out((t - 19.35) / 0.3))
    else:
        # silêncio dramático: só um fio de luz piscando
        a = 0.5 + 0.5 * math.sin((t - 19.75) * 18)
        paste(c, text_img('...', font('Anton.ttf', 120), (120, 120, 120)), W / 2, H / 2, alpha=a * 0.6)
    return c

def s_triade(t):
    words = [(20.8, 'JORNALISTA', WHITE, BG_DARK), (21.4, 'HUMORISTA', GOLD, BG_GOLD), (22.12, 'ROTEIRISTA', RED, BG_RED)]
    cur = [w for w in words if t >= w[0]][-1]
    c = base(cur[3]); dust(c, t)
    sc = slam(t, cur[0], 2.4)
    paste(c, text_img(cur[1], font('Anton.ttf', 210), cur[2]), W / 2, H / 2, scale=sc * (1 + (t - cur[0]) * 0.06))
    # contador de palavras anteriores
    y = 1260
    for w in words:
        if w[0] < cur[0]:
            paste(c, text_img(w[1], font('Oswald.ttf', 48), (150, 150, 150), spacing=12), W / 2, y); y += 70
    return c

def s_nome(t):
    lt = t - 23.45
    c = base(BG_GOLD); dust(c, t, (255, 220, 150), 160)
    light_beam(c, t, a=50, spread=700)
    z = 1 + lt * 0.025
    sc = slam(t, 23.45, 1.9)
    nm = gold_text('NELITO', 300); sn = gold_text('FERNANDES', 170)
    sweep = (lt * 900) % 2400 - 600
    paste(c, shine(nm, sweep), W / 2, 720, scale=sc * z)
    paste(c, shine(sn, sweep - 200), W / 2, 960, scale=sc * z)
    if t >= 25.4:
        paste(c, text_img('SEU PRÓXIMO FILME', font('Oswald.ttf', 78), WHITE, spacing=6), W / 2, 1250, alpha=ease_out((t - 25.4) / 0.35))
    sc2 = slam(t, 26.55, 2.0)
    if sc2:
        paste(c, text_img('JÁ TEM ROTEIRISTA.', font('Anton.ttf', 130), WHITE), W / 2, 1400, scale=sc2)
    return c

_gc = {}
def gold_text(txt, size):
    if (txt, size) in _gc: return _gc[(txt, size)]
    m = text_img(txt, font('Anton.ttf', size), (255, 255, 255))
    a = m.getchannel('A')
    grad = np.linspace(0, 1, m.height)[:, None]
    top = np.array([255, 236, 170]); mid = np.array([214, 158, 46]); bot = np.array([120, 78, 18])
    g = grad[..., 0]
    rows = np.array([top + (mid - top) * (v / 0.5) if v < 0.5 else mid + (bot - mid) * ((v - 0.5) / 0.5) for v in g])
    arr = np.repeat(rows[:, None, :], m.width, axis=1).astype(np.uint8)
    im = Image.fromarray(arr).convert('RGBA'); im.putalpha(a)
    # sombra
    sh = Image.new('RGBA', (im.width + 40, im.height + 40), (0, 0, 0, 0))
    s = Image.new('RGBA', im.size, (0, 0, 0, 200)); s.putalpha(a.point(lambda v: v * 0.8))
    sh.alpha_composite(s, (26, 30)); sh = sh.filter(ImageFilter.GaussianBlur(10)); sh.alpha_composite(im, (20, 20))
    _gc[(txt, size)] = sh
    return sh

def shine(im, x):
    lay = Image.new('L', im.size, 0); d = ImageDraw.Draw(lay)
    d.polygon([(x, 0), (x + 90, 0), (x - 60, im.height), (x - 150, im.height)], fill=170)
    lay = lay.filter(ImageFilter.GaussianBlur(18))
    a = np.minimum(np.asarray(lay, np.float32), np.asarray(im.getchannel('A'), np.float32)).astype(np.uint8)
    w = Image.new('RGBA', im.size, (255, 255, 255, 0)); w.putalpha(Image.fromarray(a))
    out = im.copy(); out.alpha_composite(w); return out

def s_final(t):
    lt = t - 28.0
    c = base(np.full((H, W, 3), 6, np.uint8))
    sc = slam(t, 28.0, 1.4)
    paste(c, gold_text('NELITO FERNANDES', 128), W / 2, 760, scale=sc)
    paste(c, text_img('ROTEIRO  ·  HUMOR  ·  JORNALISMO', font('Oswald.ttf', 46), WHITE, spacing=8), W / 2, 900, alpha=ease_out(lt / 0.4))
    # billing block
    bb = ['SENSACIONALISTA  ·  CASSETA & PLANETA  ·  ZORRA',
          'FILHAS DE EVA  ·  DETETIVE MADEINUSA',
          'AUTOR DE “MÁRIO, QUE MÁRIO?”']
    for i, l in enumerate(bb):
        paste(c, text_img(l, font('LeagueGothic.ttf', 52), (175, 175, 175), spacing=3), W / 2, 1180 + i * 62, alpha=ease_out((lt - 0.2 - i * 0.12) / 0.4))
    paste(c, text_img('EM BREVE NO SEU PROJETO', font('Anton.ttf', 80), RED), W / 2, 1480, alpha=ease_out((lt - 0.6) / 0.4))
    return c

# ---------------- post ----------------
def post(img, t, fi):
    arr = np.asarray(img.convert('RGB')).astype(np.float32)
    # hit: shake + flash + rgb split
    hit = max([0] + [1 - (t - h) / 0.25 for h in HITS if 0 <= t - h < 0.25])
    cut = max([0] + [1 - (t - h) / 0.12 for h in CUTS[1:-1] if 0 <= t - h < 0.12])
    if hit > 0:
        rs = random.Random(fi)
        dx, dy = int(rs.uniform(-1, 1) * 28 * hit), int(rs.uniform(-1, 1) * 28 * hit)
        arr = np.roll(arr, (dy, dx), axis=(0, 1))
        k = int(14 * hit)
        if k:
            arr[..., 0] = np.roll(arr[..., 0], k, axis=1); arr[..., 2] = np.roll(arr[..., 2], -k, axis=1)
    flash = max(hit * 0.55, cut * 0.9)
    if flash > 0: arr = arr + (255 - arr) * flash
    g = GRAIN[fi % 8]
    g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
    arr = arr * VIGN + g * 9
    # letterbox-free global fade in/out
    fade = clamp01(t / 0.3) * clamp01((DUR - t) / 0.5)
    arr *= fade
    return np.clip(arr, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for ts in sys.argv[1:]:
            t = float(ts); Image.fromarray(post(scene(t), t, int(t * FPS))).resize((360, 640)).save(f'prev_{ts}.png')
        sys.exit()
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', 'video.mp4'], stdin=subprocess.PIPE)
    for fi in range(N):
        t = fi / FPS
        p.stdin.write(post(scene(t), t, fi).tobytes())
        if fi % 90 == 0: print(fi, flush=True)
    p.stdin.close(); p.wait()
