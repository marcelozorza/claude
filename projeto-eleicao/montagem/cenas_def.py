"""Definição das cenas avulsas. Cada entrada devolve uma Cena. Tempos das peças são locais da arte (0 a 10 s)."""
import os
from cena import *
def _recorte(path, h):
    im = Image.open(path).convert('RGBA'); im.thumbnail((h * 2, h), Image.LANCZOS); return recorte_jornal(im, seed=4)
def adesivos_6a():
    ur = adesivo((300, 340), f_urna, (240, 232, 214), 3, detalhe=d_urna); mt = adesivo((340, 300), f_martelo, (240, 232, 214), 4, detalhe=d_martelo)
    ca = _recorte(os.path.join(RAIZ, 'motion-graphics', 'assets', 'recortes', 'folha2_3.png'), 330); K = dict(t0=0, t1=1e9, modo='fixo')
    return Cena([Cutout(ur, cx=270, cy=575, rot=-5, fase=0.4, nome='urna', **K), Cutout(ca, cx=540, cy=575, rot=3, fase=1.4, nome='cadeira', **K), Cutout(mt, cx=810, cy=575, rot=-4, fase=2.4, nome='martelo', **K)], nome='6a')
def _foto(nome, h=480, maxw=820):
    ext = '.png' if os.path.exists(os.path.join(FOTOS, nome + '.png')) else '.jpg'
    im = Image.open(os.path.join(FOTOS, nome + ext)).convert('RGBA'); im.thumbnail((maxw, h), Image.LANCZOS); return recorte_jornal(im, seed=7)
K = dict(t0=-1, t1=1e9, modo='fixo')
def foto_camara():
    return Cena([Cutout(_foto('camara'), cx=540, cy=575, rot=-2.5, fase=0.5, nome='foto câmara', **K), Etiqueta('Câmara dos Deputados', -1, 1e9, 330, 860, tam=44, rot=-3, fase=1.3)], nome='foto')
def numero_121():
    return Cena([Cutout(tira_texto('121', 230, seed=3, padx=120), cx=540, cy=520, rot=-2, fase=0.4, nome='121', **K), Etiqueta('deputados federais', -1, 1e9, 640, 700, tam=56, rot=3, fase=1.2)], nome='número')
def carimbos():
    return Cena([Carimbo('INIMIGO', -1, 1e9, 540, 400, -6, tam=130, seed=1), Carimbo('TRAIDOR', -1, 1e9, 540, 580, 4, tam=130, seed=2), Carimbo('PARASITA', -1, 1e9, 540, 760, -3, tam=130, seed=3)], nome='carimbos')
CENAS = {'6a_urna_cadeira_martelo': adesivos_6a, 'foto_camara': foto_camara, 'numero_121': numero_121, 'carimbos': carimbos}
