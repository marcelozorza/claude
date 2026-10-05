"""Storyboards dos infográficos do roteiro do dia 05/10 (I1 a I5). Cada folha tem quadros em sequência, feitos com as peças de papel do kit.
Só número do quadro e tempo aproximado, sem texto narrando a cena. Uso: python3 storyboards.py pasta_saida"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from infograficos import *
from fundo import fundo
PW, PH = 1080, 840                                  # área de arte de cada quadro (a arte da cena fica abaixo de 15% do topo)
CINZA = (126, 128, 138)

def tela(): return fundo(PW, PH).convert('RGBA')

def flecha(cor, comp=440, seed=2):
    h = 78
    def f(d, S, P):
        X = lambda v: (v + P) * S
        d.rectangle([X(14), X(30), X(comp - 80), X(48)], fill=255); d.polygon([(X(comp - 84), X(10)), (X(comp - 4), X(39)), (X(comp - 84), X(68))], fill=255)
        d.polygon([(X(0), X(8)), (X(48), X(8)), (X(70), X(39)), (X(48), X(70)), (X(0), X(70)), (X(22), X(39))], fill=255)
    def de(d, S, P):
        X = lambda v: (v + P) * S
        d.rectangle([X(14), X(30), X(comp - 80), X(48)], fill=(176, 130, 86, 255), outline=TINTA, width=3 * S)
        d.polygon([(X(comp - 84), X(10)), (X(comp - 4), X(39)), (X(comp - 84), X(68))], fill=cor + (255,), outline=TINTA, width=3 * S)
        d.polygon([(X(0), X(8)), (X(48), X(8)), (X(70), X(39)), (X(48), X(70)), (X(0), X(70)), (X(22), X(39))], fill=cor + (255,), outline=TINTA, width=3 * S)
    return adesivo((comp, h), f, (240, 232, 214), seed, borda=6, detalhe=de)

def nuvem(cor, w=300, h=190, seed=3):
    circ = [(0.22, 0.62, 0.20), (0.42, 0.40, 0.27), (0.68, 0.45, 0.24), (0.80, 0.68, 0.19), (0.52, 0.70, 0.22), (0.30, 0.70, 0.20)]
    def f(d, S, P):
        for cx, cy, r in circ: d.ellipse([(cx * w - r * w * 0.8 + P) * S, (cy * h - r * h * 1.0 + P) * S, (cx * w + r * w * 0.8 + P) * S, (cy * h + r * h * 1.0 + P) * S], fill=255)
    return adesivo((w, h), f, cor, seed, borda=7)

def quadrado_papel(w, h, cor, seed): return faixa_papel(w, h, cor, seed, amp=3)

def seta_curva(d, pts, cor=TINTA, larg=7): 
    for a, b in zip(pts, pts[1:]): d.line([a, b], fill=cor, width=larg)

# ------------------------------------------------------------------------------------------------ I1
def i1():
    ps = []; bust = boneco(PELES[0], AZUL, 1.7, seed=3); cor1, cor2 = VERM, CINZA
    def base(): 
        fr = tela(); compor(fr, bust, 740, 560, rot=0, off=8, blur=8, op=0.25); compor(fr, coracao(2.9), 740, 610, rot=0, off=4, blur=4, op=0.2); return fr
    fr = base(); compor(fr, flecha(cor1), 270, 600, rot=2); ps.append((fr, '0 s'))                                    # 1 a flecha vem
    fr = base(); compor(fr, flecha(cor1, 300), 590, 612, rot=0); compor(fr, estrela(), 700, 530, rot=0); ps.append((fr, '1 s'))     # 2 acerta o peito
    fr = base(); compor(fr, flecha(cor1, 200), 640, 614, rot=0); compor(fr, flecha(cor2, seed=4), 250, 330, rot=8); compor(fr, flecha(cor2, seed=5), 220, 470, rot=-6); ps.append((fr, '3 s'))   # 3 vêm duas
    fr = base(); compor(fr, flecha(cor1, 200), 640, 614, rot=0)
    for (x, y, r) in ((420, 330, -50), (440, 480, 40)):                                                                # 4 partidas antes de chegar
        a = flecha(cor2, 220, 7).crop((0, 0, 230, 110)); b = flecha(cor2, 220, 8)
        compor(fr, a, x - 60, y - 30, rot=r - 25); compor(fr, b.crop((120, 0, 300, 110)), x + 70, y + 60, rot=r + 35)
    ps.append((fr, '4 s'))
    fr = base(); compor(fr, flecha(cor1, 200), 640, 614, rot=0)
    for (x, y, r) in ((300, 760, 20), (470, 770, -15)): compor(fr, flecha(cor2, 220, 9).crop((0, 0, 240, 110)), x, y, rot=r)   # 5 caídas no chão
    ps.append((fr, '6 s')); return ps

# ------------------------------------------------------------------------------------------------ I2
def i2():
    ps = []; bust = boneco(PELES[1], TERRA, 1.7, seed=4); claras = (255, 236, 160); escuras = (98, 100, 112)
    pos = [(250, 300), (540, 220), (830, 310), (190, 560), (890, 580)]
    def base(cores, desloc=(0, 0), onda=0.0):
        fr = tela(); compor(fr, bust, 540 + desloc[0] * 0, 580, rot=0, off=8, blur=8, op=0.25)
        for i, (x, y) in enumerate(pos): compor(fr, nuvem(cores[i], 270 + 20 * (i % 2), 170, seed=i + 3), x + desloc[0] * (1 + 0.4 * i), y + desloc[1] * (1 + 0.3 * i), rot=3 * (i - 2), off=6, blur=6, op=0.22)
        return fr
    ps.append((base([claras] * 5), '0 s'))                                                                                           # 1 pensamentos claros
    fr = base([escuras, escuras, claras, claras, claras]); L = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); ImageDraw.Draw(L).polygon([(0, 80), (520, 0), (640, 0), (140, 900), (0, 900)], fill=(70, 72, 86, 120)); fr.alpha_composite(L); ps.append((fr, '1,5 s'))   # 2 mancha cinza entra
    fr = base([escuras] * 5); L = Image.new('RGBA', (PW, PH), (70, 72, 86, 70)); fr.alpha_composite(L); ps.append((fr, '3 s'))     # 3 tudo escuro
    fr = base([escuras] * 5, (300, -170)); d = ImageDraw.Draw(fr)
    for (x, y) in ((640, 130), (760, 250), (820, 420)): d.line([x, y, x + 110, y - 20], fill=TINTA, width=6)                         # 4 se soltam e vão embora
    ps.append((fr, '5 s'))
    fr = tela(); compor(fr, bust, 540, 580, rot=0, off=8, blur=8, op=0.25)
    for (x, y) in ((1000, 150), (950, 300)): compor(fr, nuvem(escuras, 150, 95, seed=2), x, y, rot=4, off=4, blur=4, op=0.2)       # 5 busto sozinho, nuvens longe
    ps.append((fr, '7 s')); return ps

# ------------------------------------------------------------------------------------------------ I3
def i3():
    ps = []
    def quadro(raio, ponto, barra_in, barra_ex):
        fr = tela(); d = ImageDraw.Draw(fr)
        compor(fr, disco(raio, (255, 226, 60), 12), 540, 330, rot=0, off=10, blur=9, op=0.28)
        # onda: sobe rápido, desce devagar (um ciclo e meio). x de 100 a 980
        xs = np.linspace(0, 1, 160); y = lambda u: 0.5 - 0.5 * math.sin(math.pi * min(1, (u % 0.5) / 0.5 * 0.5 * 2) if False else 0)
        def onda(u):
            c = (u * 2) % 1.0                                       # ciclo = 0,5 do comprimento total
            return (c / 0.3) if c < 0.3 else (1 - (c - 0.3) / 0.7)    # sobe em 30%, desce em 70%
        pts = [(100 + 880 * u, 740 - 120 * onda(u)) for u in xs]; d.line(pts, fill=(180, 170, 150, 255), width=6)
        k = int(len(pts) * ponto); d.line(pts[:max(2, k)], fill=TINTA, width=9)
        if ponto > 0: x, yy = pts[min(k, len(pts) - 1)]; d.ellipse([x - 14, yy - 14, x + 14, yy + 14], fill=VERM + (255,), outline=TINTA, width=3)
        d.rounded_rectangle([100, 790, 100 + 200, 812], radius=10, outline=TINTA, width=3); d.rounded_rectangle([100, 790, 100 + 200 * barra_in, 812], radius=10, fill=AMARELO + (255,))
        d.rounded_rectangle([340, 790, 340 + 420, 812], radius=10, outline=TINTA, width=3); d.rounded_rectangle([340, 790, 340 + 420 * barra_ex, 812], radius=10, fill=AZUL + (255,))
        return fr
    ps.append((quadro(70, 0.0, 0, 0), '0 s')); ps.append((quadro(140, 0.15, 1.0, 0), '2 s')); ps.append((quadro(215, 0.30, 1.0, 0), '4 s'))
    ps.append((quadro(150, 0.45, 1.0, 0.5), '7 s')); ps.append((quadro(70, 0.62, 1.0, 1.0), '10 s')); return ps

# ------------------------------------------------------------------------------------------------ I4
def i4():
    ps = []; fig = boneco(PELES[2], TERRA, 1.1, seed=5)
    def ladrilhos(n, caidos, x0=70):
        fr = tela(); 
        for i in range(n):
            x = x0 + i * 112; y = 650; r = 0; a = 255
            if i < caidos: u = (caidos - i) / 4.0; y += 160 * u ** 1.5; r = 18 * u * (1 if i % 2 else -1)
            if y < 900: compor(fr, poligono_papel([(0, 0), (100, 0), (100, 44), (0, 44)], (214, 140, 96), 70 + i)[0], x + 52, y, rot=r, off=5, blur=5, op=0.2)
        return fr
    fr = ladrilhos(9, 0); compor(fr, fig, 930, 560, rot=0, off=5, blur=5, op=0.2); ps.append((fr, '0 s'))                          # 1 caminho inteiro, o boneco na ponta
    fr = ladrilhos(9, 4); compor(fr, fig, 930, 560, rot=0, off=5, blur=5, op=0.2); ps.append((fr, '2 s'))                          # 2 o chão de trás desaba
    fr = ladrilhos(9, 8); compor(fr, fig, 930, 560, rot=0, off=5, blur=5, op=0.2); ps.append((fr, '4 s'))                          # 3 só resta o último
    fr = tela()
    for i in range(5):                                                                                                               # 4 degraus à frente, subindo
        h = 80 + i * 70; im, x0, y0 = poligono_papel([(0, 0), (110, 0), (110, h), (0, h)], [(214, 140, 96), (222, 150, 98), (190, 120, 78), (226, 160, 110), (206, 134, 92)][i], 90 + i)
        compor(fr, im, 330 + i * 130 + 55, 800 - h / 2, rot=0, off=6, blur=6, op=0.22)
    compor(fr, fig, 330 + 130 + 55, 800 - 150 - 100, rot=0, off=5, blur=5, op=0.2); ps.append((fr, '6 s'))
    fr = tela()
    for i in range(7):                                                                                                               # 5 o boneco no alto, a escada continua
        h = 80 + i * 70; im, x0, y0 = poligono_papel([(0, 0), (110, 0), (110, h), (0, h)], [(214, 140, 96), (222, 150, 98), (190, 120, 78), (226, 160, 110), (206, 134, 92), (214, 140, 96), (222, 150, 98)][i], 90 + i)
        compor(fr, im, 100 + i * 130 + 55, 880 - h / 2, rot=0, off=6, blur=6, op=0.22)
    compor(fr, fig, 100 + 5 * 130 + 55, 880 - 360 - 100, rot=0, off=5, blur=5, op=0.2); ps.append((fr, '9 s')); return ps

# ------------------------------------------------------------------------------------------------ I5
def i5():
    ps = []
    def eixos(fr): d = ImageDraw.Draw(fr); d.line([110, 120, 110, 760], fill=TINTA, width=7); d.line([110, 760, 1010, 760], fill=TINTA, width=7); return d
    furia = lambda u: 760 - 560 * math.exp(-((u - 0.18) / 0.07) ** 2) * (1 if u < 0.30 else math.exp(-((u - 0.30) / 0.02) ** 2)) - 6 * u
    def curva_furia(u1): 
        pts = []
        for u in np.linspace(0, u1, 200):
            if u < 0.16: y = 760 - 580 * (u / 0.16) ** 2
            elif u < 0.30: y = 180 + 580 * ((u - 0.16) / 0.14) ** 1.4
            else: y = 760
            pts.append((120 + 860 * u, y))
        return pts
    azul = lambda u: 760 - 120 * u ** 0.8 - 40 * u
    def curva_azul(u1): return [(120 + 860 * u, azul(u)) for u in np.linspace(0, u1, 200)]
    fr = tela(); d = eixos(fr); ps.append((fr, '0 s'))                                                                                # 1 eixos vazios
    fr = tela(); d = eixos(fr); seta_curva(d, curva_furia(0.15), VERM, 11); seta_curva(d, curva_azul(0.15), AZUL, 11); ps.append((fr, '2 s'))      # 2 a fúria dispara
    fr = tela(); d = eixos(fr); seta_curva(d, curva_furia(0.32), VERM, 11); seta_curva(d, curva_azul(0.32), AZUL, 11); ps.append((fr, '4 s'))     # 3 despenca a zero
    fr = tela(); d = eixos(fr); seta_curva(d, curva_furia(0.32), VERM, 11); seta_curva(d, curva_azul(1.0), AZUL, 11)
    for i, u in enumerate((0.45, 0.62, 0.78, 0.92)): compor(fr, quadrado_papel(58, 74, [AMARELO, TERRA, AZUL, AMARELO][i], 20 + i), 120 + 860 * u, azul(u) - 48, rot=-6 + 4 * i, off=4, blur=4, op=0.2)   # 4 cartazes na linha
    ps.append((fr, '7 s'))
    fr = tela(); cell = 84; pad = 12; forma = ['...X...', '..XXX..', '.XXXXX.', 'XXXXXXX', '...X...', '...X...', '...X...']                                  # 5 mosaico de cartazes: seta para cima
    cores = [AMARELO, TERRA, AZUL, (110, 170, 112)]; k = 0
    for r, linha in enumerate(forma):
        for c, ch in enumerate(linha):
            if ch == 'X': compor(fr, quadrado_papel(cell - pad, cell - pad, cores[k % 4], 40 + k), 540 + (c - 3) * cell, 110 + r * cell + 60, rot=(k % 3 - 1) * 3, off=4, blur=4, op=0.2); k += 1
    ps.append((fr, '10 s')); return ps

# ------------------------------------------------------------------------------------------------ folha
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
    pasta = sys.argv[1]; os.makedirs(pasta, exist_ok=True)
    quais = sys.argv[2:] or ['I1', 'I2', 'I3', 'I4', 'I5']; fns = {'I1': i1, 'I2': i2, 'I3': i3, 'I4': i4, 'I5': i5}
    for q in quais: folha(q, fns[q](), os.path.join(pasta, f'storyboard_{q}.png')); print('ok', q)
