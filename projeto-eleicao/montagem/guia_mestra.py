"""Folha guia mestra do canal: tipografia, paleta, componentes, exemplos de cena, movimento e regras. Gera uma imagem 1920x1080 com os componentes reais do kit.
Uso: python3 guia_mestra.py saida.png"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cena import *
from fundo import fundo
from titulo import Titulo, _fonte
from animfoto import _bola
from cenas_def import CENAS
GW, GH = 1920, 1080
CREME = (241, 229, 201)
def fonte_bold(tam): return ImageFont.truetype(BOLD, tam)
def texto(d, xy, s, tam=22, cor=TINTA, bold=False, ancora='la', peso=520):
    d.text(xy, s, font=fonte_bold(tam) if bold else _fonte(tam, peso), fill=cor, anchor=ancora)
def painel(d, x, y, titulo):
    texto(d, (x, y), titulo, 20, bold=True)
def regua(d, x0, x1, y): d.line([x0, y, x1, y], fill=(120, 108, 92, 255), width=2)
def cola(fr, im, cx, cy, rot=0.0, op=0.30): por(fr, im, cx, cy, rot, op)
def titulo_final(txt, cy=600, **kw):
    t = Titulo(txt, entrada='dobra', cy=cy, varredura=True, ficar=0.0, **kw); q = t.quadro(t.t_fim + 0.05, canvas=(W, H)); return q.crop(q.getchannel('A').getbbox())
def quadro_cena(cid, t, caixa, larg):
    c = CENAS[cid](); fr = c.frame(fundo(W, H).convert('RGBA'), t).crop(caixa); return fr.resize((larg, int(fr.height * larg / fr.width)), Image.LANCZOS)

def main(saida):
    fr = fundo(GW, GH).convert('RGBA'); d = ImageDraw.Draw(fr)
    d.rectangle([0, 0, GW, 72], fill=TINTA); texto(d, (36, 36), 'NADA ERRADO COM VC', 30, CREME + (255,), True, 'lm'); texto(d, (GW - 36, 36), 'FOLHA GUIA MESTRA  ·  SISTEMA VISUAL DAS ANIMAÇÕES DE PAPEL', 20, CREME + (255,), True, 'rm')
    # ------------------------------------------------ tipografia
    painel(d, 36, 100, 'TIPOGRAFIA'); texto(d, (36, 152), 'TÍTULO (EB GARAMOND ITÁLICO, MARCA-TEXTO PASSA UMA VEZ)', 14, bold=True)
    tt = titulo_final('O que é política?'); tt.thumbnail((380, 120)); cola(fr, tt, 36 + tt.width / 2 + 8, 235, -1.5)
    texto(d, (36, 336), 'NÚMERO GIGANTE', 14, bold=True); n = tira_texto('121', 78, seed=3, padx=46); n.thumbnail((170, 120)); cola(fr, n, 36 + n.width / 2 + 8, 408, -2)
    texto(d, (330, 336), 'RÓTULO', 14, bold=True); e = Etiqueta('deputados federais', 0, 1, 0, 0, tam=36).im; e.thumbnail((262, 90)); cola(fr, e, 322 + e.width / 2, 408, 2, 0.2)
    texto(d, (36, 462), 'Citação entre aspas, com a linha de crédito pequena abaixo.', 18, (96, 84, 70, 255))
    d.line([620, 100, 620, 470], fill=(120, 108, 92, 255), width=2)
    # ------------------------------------------------ paleta
    painel(d, 650, 100, 'PALETA')
    cores = [('Papel', CREME), ('Linha', (229, 215, 185)), ('Tinta', (36, 30, 26)), ('Marca-texto', (255, 226, 0)), ('Vermelho', (204, 34, 40)), ('Azul', (86, 150, 176)), ('Terracota', (226, 122, 92))]
    for i, (nm, c) in enumerate(cores):
        x = 650 + i * 86; sw = faixa_papel(66, 120, c, 20 + i, amp=3, pad=8); fr.alpha_composite(sw, (x - 8, 160))
        texto(d, (x, 300), nm, 12, bold=True); texto(d, (x, 322), '#%02X%02X%02X' % c, 12, (96, 84, 70, 255), True)
    regua(d, 650, 1240, 360); texto(d, (650, 376), 'Marca-texto amarelo é o destaque principal.', 20); texto(d, (650, 408), 'Vermelho só para carimbo, X e traço de ênfase.', 20); texto(d, (650, 440), 'Papel creme de fundo, tinta quase preta nos textos.', 20)
    d.line([1260, 100, 1260, 470], fill=(120, 108, 92, 255), width=2)
    # ------------------------------------------------ zoo de componentes
    painel(d, 1290, 100, 'ZOO DE COMPONENTES')
    foto = Image.open(os.path.join(FOTOS, 'camara.jpg')).convert('RGBA'); foto.thumbnail((250, 160)); fj = recorte_jornal(foto, seed=7); cola(fr, fj, 1400, 235, -3)
    bola = _bola(fj, 'A').quadro(1.0); bola.thumbnail((110, 110)); cola(fr, bola, 1595, 220, 8)
    car = Carimbo('CARIMBO', -1, 1e9, 0, 0, 0, tam=30, seed=4).im; fr.alpha_composite(car, (1665, 205))
    cola(fr, adesivo((300, 340), f_urna, (240, 232, 214), 3, detalhe=d_urna).resize((120, 136)), 1350, 390, -4)
    cola(fr, coracao(5.0), 1500, 390, 8); cola(fr, adesivo((340, 300), f_martelo, (240, 232, 214), 4, detalhe=d_martelo).resize((150, 132)), 1650, 395, 4)
    lg = Image.open(os.path.join(RAIZ, 'edicao-chroma', 'dados', 'logo_redondo.png')).convert('RGBA'); lg.thumbnail((120, 120)); cola(fr, lg, 1810, 395, 0, 0.3)
    regua(d, 36, GW - 36, 490)
    # ------------------------------------------------ exemplos de cena
    painel(d, 36, 510, 'EXEMPLOS DE CENA'); cx0 = 36
    for k, (cid, tt_) in enumerate((('foto_camara', 'A  FOTO COM BORDA DE JORNAL'), ('numero_121', 'B  NÚMERO GIGANTE E RÓTULO'), ('carimbos', 'C  CARIMBOS NA TELA'))):
        q = quadro_cena(cid, T_ARTE + 3.0, (0, 150, W, 980), 350); x = 36 + k * 372; texto(d, (x, 568), tt_, 14, bold=True); fr.alpha_composite(q, (x, 590)); d.rectangle([x, 590, x + q.width, 590 + q.height], outline=TINTA, width=2)
    d.line([1180, 510, 1180, 880], fill=(120, 108, 92, 255), width=2)
    # ------------------------------------------------ miniaturas de movimento
    painel(d, 1210, 510, 'MINIATURAS DE MOVIMENTO'); passos = [(0.22, 'BOLINHA CHEGA'), (0.78, 'ABRE'), (6.0, '10 S NA TELA'), (11.3, 'FECHA'), (11.78, 'VAI EMBORA')]
    sc = quadro_cena
    for k, (t, rot) in enumerate(passos):
        c = CENAS['foto_camara'](); q = c.frame(fundo(W, H).convert('RGBA'), t).crop((0, 100, W, 1000)); q = q.resize((136, int(q.height * 136 / q.width)), Image.LANCZOS)
        x = 1210 + k * 140; texto(d, (x, 568), '%d' % (k + 1), 18, bold=True); texto(d, (x + 20, 570), rot, 11, bold=True); texto(d, (x, 595 + q.height + 20), ('0,45 s', '0,55 s', '10 s', '0,55 s', '0,50 s')[k], 18); fr.alpha_composite(q, (x, 595)); d.rectangle([x, 595, x + q.width, 595 + q.height], outline=TINTA, width=2)
        if k < 4: d.text((x + 138, 595 + q.height / 2), '›', font=fonte_bold(26), fill=(204, 34, 40, 255), anchor='mm')
    texto(d, (1210, 800), 'Cena completa: 12,15 s', 20, bold=False); texto(d, (1210, 830), 'chega 0,45 · abre 0,55 · 10 s de arte · fecha 0,55 · vai 0,50', 18, (96, 84, 70, 255))
    regua(d, 36, GW - 36, 890)
    # ------------------------------------------------ palco e notas
    painel(d, 36, 910, 'O PALCO'); d.rectangle([36, 960, 1170, 1060], outline=TINTA, width=2)
    for (x, y) in ((36, 960), (1170, 960), (36, 1060), (1170, 1060)): d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(204, 34, 40, 255))
    texto(d, (603, 1010), 'papel pautado vazio, luz uniforme, pronto para as peças entrarem e saírem', 22, (96, 84, 70, 255), False, 'mm')
    d.line([1200, 900, 1200, 1060], fill=(120, 108, 92, 255), width=2)
    painel(d, 1230, 910, 'NOTAS DO SISTEMA')
    notas = ['Cada cena é um arquivo próprio e fechado. Nada sobrepõe outra cena.', 'Fundo sempre o papel pautado. Sem apresentador, legenda ou áudio.', 'Sempre 10 s de arte na tela, com balanço leve. O excesso é cortado na edição.', 'Texto só em código, EB Garamond itálico, com acentos corretos.', 'Pessoas reais só em fotos licenciadas, com crédito.']
    for i, s in enumerate(notas): texto(d, (1230, 962 + i * 22), '•  ' + s, 16)
    fr.convert('RGB').save(saida)

if __name__ == '__main__': main(sys.argv[1])
