"""Storyboards I1 a I5 no estilo de pictograma (referência ISO 7001): formas chapadas, cor sólida, sem contorno, sem borda e sem sombra.
Uso: python3 storyboards_picto.py pasta_saida [I1 ...]"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'motion-graphics', 'lib'))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pictogramas import *
from fundo import fundo
PW, PH = 1080, 840; BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def tela(): return fundo(PW, PH).convert('RGBA')
def cola(fr, im, cx, cy, rot=0.0): colar(fr, im, cx, cy, rot)

def i1():
    ps = []; fig = pessoa(TINTA, 'parado'); fig = fig.resize((int(fig.width * 0.95), int(fig.height * 0.95)), Image.LANCZOS); cx, base = 780, 770; ch = coracao(46)
    def cena(): 
        fr = tela(); cola(fr, fig, cx, base - fig.height / 2); cola(fr, ch, cx, base - fig.height + 190); return fr
    fr = cena(); cola(fr, flecha(420), 260, base - fig.height + 192, 1); ps.append((fr, '0 s'))
    fr = cena(); cola(fr, estrela_chapada(86), cx, base - fig.height + 190); cola(fr, ch, cx, base - fig.height + 190); cola(fr, flecha(280), cx - 190, base - fig.height + 190); ps.append((fr, '1 s'))
    fr = cena(); cola(fr, flecha(240), cx - 150, base - fig.height + 190); cola(fr, flecha(420, CINZA, CINZA), 250, 280, 7); cola(fr, flecha(420, CINZA, CINZA), 240, 470, -5); ps.append((fr, '3 s'))
    fr = cena(); cola(fr, flecha(240), cx - 150, base - fig.height + 190)
    for (x, y, r) in ((380, 300, -50), (420, 470, 40)): cola(fr, flecha(420, CINZA, CINZA).crop((0, 0, 220, 80)), x - 60, y - 30, r - 25); cola(fr, flecha(420, CINZA, CINZA).crop((220, 0, 420, 80)), x + 60, y + 60, r + 35)
    ps.append((fr, '4 s'))
    fr = cena(); cola(fr, flecha(240), cx - 150, base - fig.height + 190)
    for (x, y, r) in ((110, 770, 8), (500, 772, -8)): cola(fr, flecha(420, CINZA, CINZA).crop((0, 0, 230, 80)), x, y, r); cola(fr, flecha(420, CINZA, CINZA).crop((230, 0, 420, 80)), x + 170, y - 4, r + 20)
    ps.append((fr, '6 s')); return ps

def i2():
    ps = []; fig = pessoa(TINTA, 'parado'); fig = fig.resize((int(fig.width * 0.95), int(fig.height * 0.95)), Image.LANCZOS); claras, escuras = CREME, (98, 100, 112)
    pos = [(250, 300), (540, 220), (830, 310), (190, 560), (890, 580)]
    def base(cores, desloc=(0, 0)):
        fr = tela(); cola(fr, fig, 540, 770 - fig.height / 2)
        for i, (x, y) in enumerate(pos): cola(fr, nuvem(cores[i], 270 + 20 * (i % 2), 170), x + desloc[0] * (1 + 0.4 * i), y + desloc[1] * (1 + 0.3 * i), 3 * (i - 2))
        return fr
    ps.append((base([claras] * 5), '0 s'))
    fr = base([escuras, escuras, claras, claras, claras]); L = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); ImageDraw.Draw(L).polygon([(0, 80), (520, 0), (640, 0), (140, 900), (0, 900)], fill=(70, 72, 86, 120)); fr.alpha_composite(L); ps.append((fr, '1,5 s'))
    fr = base([escuras] * 5); fr.alpha_composite(Image.new('RGBA', (PW, PH), (70, 72, 86, 70))); ps.append((fr, '3 s'))
    fr = base([escuras] * 5, (300, -170)); d = ImageDraw.Draw(fr)
    for (x, y) in ((640, 130), (760, 250), (820, 420)): cap(d, (x, y), (x + 110, y - 20), 8, TINTA)
    ps.append((fr, '5 s'))
    fr = tela(); cola(fr, fig, 540, 770 - fig.height / 2)
    for (x, y) in ((1000, 150), (950, 300)): cola(fr, nuvem(escuras, 150, 95), x, y, 4)
    ps.append((fr, '7 s')); return ps

def i3():
    ps = []
    def onda(u): c = (u * 2) % 1.0; return (c / 0.3) if c < 0.3 else (1 - (c - 0.3) / 0.7)
    def quadro(raio, ponto, bi, bx):
        fr = tela(); cola(fr, disco(raio, AMAR), 540, 330)
        pts = [(100 + 880 * u, 740 - 120 * onda(u)) for u in np.linspace(0, 1, 160)]; fr.alpha_composite(linha(pts, (206, 196, 172), 12, (PW, PH)))
        k = int(len(pts) * ponto)
        if k > 2: fr.alpha_composite(linha(pts[:k], TINTA, 14, (PW, PH)))
        if ponto > 0: x, y = pts[min(k, len(pts) - 1)]; cola(fr, disco(20, VERM), x, y)
        cola(fr, retangulo(200, 24, (226, 216, 192), 12), 200, 800); cola(fr, retangulo(420, 24, (226, 216, 192), 12), 550, 800)
        if bi > 0: cola(fr, retangulo(int(200 * bi), 24, AMAR, 12), 100 + 100 * bi, 800)
        if bx > 0: cola(fr, retangulo(int(420 * bx), 24, AZUL, 12), 340 + 210 * bx, 800)
        return fr
    ps.append((quadro(70, 0.0, 0, 0), '0 s')); ps.append((quadro(140, 0.15, 1.0, 0), '2 s')); ps.append((quadro(215, 0.30, 1.0, 0), '4 s')); ps.append((quadro(150, 0.45, 1.0, 0.5), '7 s')); ps.append((quadro(70, 0.62, 1.0, 1.0), '10 s')); return ps

def i4():
    ps = []; andando = pessoa(TINTA, 'caminhando'); subindo = pessoa(TINTA, 'subindo'); esc = 0.62
    andando = andando.resize((int(andando.width * esc), int(andando.height * esc)), Image.LANCZOS); subindo = subindo.resize((int(subindo.width * esc), int(subindo.height * esc)), Image.LANCZOS)
    tons = [(214, 140, 96), (222, 150, 98), (190, 120, 78), (226, 160, 110), (206, 134, 92), (214, 140, 96), (222, 150, 98)]
    def ladrilhos(n, caidos, x0=70):
        fr = tela()
        for i in range(n):
            x = x0 + i * 112; y = 650; r = 0
            if i < caidos: u = (caidos - i) / 4.0; y += 160 * u ** 1.5; r = 18 * u * (1 if i % 2 else -1)
            if y < 900: cola(fr, retangulo(100, 44, tons[i % 7], 6), x + 52, y, r)
        return fr
    for caidos, t in ((0, '0 s'), (4, '2 s'), (8, '4 s')): fr = ladrilhos(9, caidos); cola(fr, andando, 930, 650 - 22 - andando.height / 2); ps.append((fr, t))
    fr = tela()
    for i in range(5): h = 80 + i * 70; cola(fr, retangulo(110, h, tons[i], 0), 330 + i * 130 + 55, 800 - h / 2)
    cola(fr, subindo, 330 + 130 + 55, 800 - 150 - subindo.height / 2); ps.append((fr, '6 s'))
    fr = tela()
    for i in range(7): h = 80 + i * 70; cola(fr, retangulo(110, h, tons[i], 0), 100 + i * 130 + 55, 880 - h / 2)
    cola(fr, andando, 100 + 5 * 130 + 55, 880 - 430 - andando.height / 2); ps.append((fr, '9 s')); return ps

def i5():
    ps = []
    def eixos(fr): fr.alpha_composite(retangulo(10, 640, TINTA, 5), (105, 120)); fr.alpha_composite(retangulo(910, 10, TINTA, 5), (105, 755))
    def curva_furia(u1):
        pts = []
        for u in np.linspace(0, u1, 200):
            if u < 0.16: y = 760 - 580 * (u / 0.16) ** 2
            elif u < 0.30: y = 180 + 580 * ((u - 0.16) / 0.14) ** 1.4
            else: y = 760
            pts.append((120 + 860 * u, y))
        return pts
    azul = lambda u: 760 - 120 * u ** 0.8 - 40 * u
    curva_azul = lambda u1: [(120 + 860 * u, azul(u)) for u in np.linspace(0, u1, 200)]
    fr = tela(); eixos(fr); ps.append((fr, '0 s'))
    fr = tela(); eixos(fr); fr.alpha_composite(linha(curva_furia(0.15), VERM, 14, (PW, PH))); fr.alpha_composite(linha(curva_azul(0.15), AZUL, 14, (PW, PH))); ps.append((fr, '2 s'))
    fr = tela(); eixos(fr); fr.alpha_composite(linha(curva_furia(0.32), VERM, 14, (PW, PH))); fr.alpha_composite(linha(curva_azul(0.32), AZUL, 14, (PW, PH))); ps.append((fr, '4 s'))
    fr = tela(); eixos(fr); fr.alpha_composite(linha(curva_furia(0.32), VERM, 14, (PW, PH))); fr.alpha_composite(linha(curva_azul(1.0), AZUL, 14, (PW, PH)))
    for i, u in enumerate((0.45, 0.62, 0.78, 0.92)): cola(fr, retangulo(58, 74, [AMAR, TERRA, AZUL, AMAR][i], 4), 120 + 860 * u, azul(u) - 52, -6 + 4 * i)
    ps.append((fr, '7 s'))
    fr = tela(); cell = 84; pad = 12; forma = ['...X...', '..XXX..', '.XXXXX.', 'XXXXXXX', '...X...', '...X...', '...X...']; cores = [AMAR, TERRA, AZUL, VERDE]; k = 0
    for r, linha_ in enumerate(forma):
        for c, ch in enumerate(linha_):
            if ch == 'X': cola(fr, retangulo(cell - pad, cell - pad, cores[k % 4], 4), 540 + (c - 3) * cell, 110 + r * cell + 60, (k % 3 - 1) * 3); k += 1
    ps.append((fr, '10 s')); return ps

def folha(ident, paineis, saida):
    n = len(paineis); col = 3; lin = (n + col - 1) // col; pw, ph = 560, int(560 * PH / PW); gap = 26; topo = 84
    S_ = Image.new('RGB', (col * pw + (col + 1) * gap, topo + lin * (ph + gap) + gap), (250, 247, 240)); d = ImageDraw.Draw(S_)
    d.rectangle([0, 0, S_.width, 64], fill=TINTA); d.text((gap, 32), ident, font=ImageFont.truetype(BOLD, 34), fill=(241, 229, 201), anchor='lm')
    for i, (im, tempo) in enumerate(paineis):
        x = gap + (i % col) * (pw + gap); y = topo + (i // col) * (ph + gap); S_.paste(im.convert('RGB').resize((pw, ph), Image.LANCZOS), (x, y)); d.rectangle([x, y, x + pw, y + ph], outline=TINTA, width=3)
        d.ellipse([x + 10, y + 10, x + 56, y + 56], fill=TINTA); d.text((x + 33, y + 33), str(i + 1), font=ImageFont.truetype(BOLD, 26), fill=(241, 229, 201), anchor='mm')
        d.text((x + pw - 14, y + 14), tempo, font=ImageFont.truetype(BOLD, 22), fill=TINTA, anchor='ra')
        if i % col < col - 1 and i < n - 1: d.text((x + pw + gap / 2, y + ph / 2), '›', font=ImageFont.truetype(BOLD, 40), fill=VERM, anchor='mm')
    S_.save(saida)

if __name__ == '__main__':
    pasta = sys.argv[1]; os.makedirs(pasta, exist_ok=True); quais = sys.argv[2:] or ['I1', 'I2', 'I3', 'I4', 'I5']; fns = {'I1': i1, 'I2': i2, 'I3': i3, 'I4': i4, 'I5': i5}
    for q in quais: folha(q, fns[q](), os.path.join(pasta, f'storyboard_{q}_pictograma.png')); print('ok', q)
