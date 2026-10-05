"""Ciclo da bolinha de papel, reutilizável em qualquer animação (guardado no kit).

    bolinha chega (0,45 s) -> abre (0,55 s) -> ARTE FIXA 10 s, com o balanço que as peças já têm -> fecha em bolinha (0,55 s)
    -> a bolinha vai embora (0,75 s): cada vez MENOR e MAIS AMASSADA, em desenhos novos (não é redimensionamento), e some.

Uso:
    from bola_cena import CicloBola, DUR
    ciclo = CicloBola(camada)                 # camada(t) devolve uma imagem RGBA 1080x1920 com o que fica na tela, t de 0 a 10 s
    quadro = ciclo.frame(fundo_rgba, t)       # t de 0 a DUR (12,4 s). Devolve um RGBA 1080x1920 com o fundo e a bolinha
A bola é construída a partir do quadro inicial e do final da própria arte (recortados), então vale para foto, tira, adesivo ou grupo de peças.
Parâmetros úteis: lado_in e lado_out (-1 esquerda, 1 direita) escolhem de onde a bola chega e para onde vai, estagios = quantas bolas menores antes de sumir."""
import math
from PIL import Image
from animfoto import ease_out, ease_io, sombra_papel, _bola
from bola import estagios_amassados

CHEGA, ABRE, FICA, FECHA, VAI, FOLGA = 0.45, 0.55, 10.0, 0.55, 0.75, 0.10
DUR = round(CHEGA + ABRE + FICA + FECHA + VAI + FOLGA, 2)
T_ARTE = CHEGA + ABRE                      # instante em que a arte começa a contar os 10 s

def colar(dest, src, x, y):
    x, y = int(x), int(y); x0, y0 = max(0, x), max(0, y); x1, y1 = min(dest.width, x + src.width), min(dest.height, y + src.height)
    if x1 > x0 and y1 > y0: dest.alpha_composite(src.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))

def por(fr, im, cx, cy, rot=0.0, op=0.30):
    """cola im centrada em (cx, cy) com rotação e sombra de papel (op = 0 não põe sombra)"""
    if abs(rot) > 0.02: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if op > 0.01: im = sombra_papel(im, off=10, blur=9, op=op)
    colar(fr, im, cx - im.width / 2, cy - im.height / 2)

class CicloBola:
    def __init__(self, camada, tamanho=(1080, 1920), lado_in=-1, lado_out=1, estagios=2, fica=FICA):
        self.camada, self.tam, self.lado_in, self.lado_out, self.n_est, self.fica = camada, tamanho, lado_in, lado_out, estagios, fica
        self.dur = round(CHEGA + ABRE + fica + FECHA + VAI + FOLGA, 2); self._snap = None; self._est = None
    def _fotos(self):
        """quadro inicial e final da arte, recortados na caixa que contém tudo. Viram a folha que se dobra em bolinha."""
        if self._snap is None:
            res = []
            for t in (0.0, self.fica):
                L = self.camada(t); bb = L.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox() or (0, 0, 64, 64)
                res.append((L.crop(bb), ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)))
            self._snap = res
        return self._snap
    def _estagios(self):
        """a bolinha de saída e as bolas menores e mais amassadas, desenhadas de novo (bola.estagios_amassados)"""
        if self._est is None: self._est = estagios_amassados(_bola(self._fotos()[1][0], 'A').quadro(1.0), self.n_est)
        return self._est
    def frame(self, fundo, t):
        W, H = self.tam; fr = fundo.copy(); (img_in, c_in), (img_out, c_out) = self._fotos()
        if t < CHEGA:                                   # a bolinha chega, em arco, girando
            p = ease_out(t / CHEGA); b = _bola(img_in, 'A').quadro(1.0); x0 = c_in[0] + self.lado_in * (W / 2 + 320); y0 = c_in[1] - 650
            x = x0 + (c_in[0] - x0) * p; y = y0 + (c_in[1] - y0) * p - 330 * 4 * p * (1 - p)
            por(fr, b, x, y, rot=self.lado_in * 520 * (1 - p)); return fr
        if t < T_ARTE:                                  # abre
            u = (t - CHEGA) / ABRE; c = 1 - ease_io(u); im = _bola(img_in, 'A').quadro(c); por(fr, im, c_in[0], c_in[1], rot=-3 * c, op=0.30 * c); return fr
        if t < T_ARTE + self.fica:                      # arte parada na tela, com o balanço
            fr.alpha_composite(self.camada(t - T_ARTE)); return fr
        v = t - T_ARTE - self.fica
        if v < FECHA:                                   # fecha em bolinha
            u = v / FECHA; c = ease_io(u); im = _bola(img_out, 'A').quadro(c); por(fr, im, c_out[0], c_out[1], rot=3 * c, op=0.30 * c); return fr
        v -= FECHA
        if v < VAI:                                     # vai embora: bolas cada vez menores e mais amassadas, trocadas em stop motion, e some
            p = v / VAI; est = self._estagios(); k = min(len(est) - 1, int(p * len(est)))
            x = c_out[0] + self.lado_out * 430 * p; y = c_out[1] - 300 * math.sin(math.pi * p * 0.85) + 120 * p * p
            por(fr, est[k], x, y, rot=self.lado_out * 300 * p); return fr
        return fr
