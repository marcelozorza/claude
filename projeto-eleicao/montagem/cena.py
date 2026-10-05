"""Cena padrão. Cada cena é um arquivo de vídeo independente sobre o papel pautado, sem nada fora dela:
  a bolinha de papel chega, abre, fica 10 s com a arte na tela (com o balanço leve), fecha em bolinha e vai embora.
Nenhuma outra peça aparece junto da abertura ou do fechamento. O excesso é cortado pelo usuário na edição.
Uso no código: Cena(pecas).frame(fundo, t) com t em segundos de 0 a DUR. As peças usam o tempo LOCAL da arte (0 a 10 s)."""
import math
from pecas import *
from animfoto import ease_in, _bola
CHEGA, ABRE, FICA, FECHA, VAI, FOLGA = 0.45, 0.55, 10.0, 0.55, 0.50, 0.10
DUR = round(CHEGA + ABRE + FICA + FECHA + VAI + FOLGA, 2)
T_ARTE = CHEGA + ABRE                      # instante em que a arte começa a contar os 10 s

def por(fr, im, cx, cy, rot=0.0, op=0.30):
    """cola im centrada em (cx, cy) com rotação e sombra de papel (op = 0 não põe sombra)"""
    if abs(rot) > 0.02: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if op > 0.01: im = sombra_papel(im, off=10, blur=9, op=op)
    colar(fr, im, cx - im.width / 2, cy - im.height / 2)

class Cena:
    def __init__(self, pecas, lado_in=-1, lado_out=1, nome='cena'):
        self.pecas, self.lado_in, self.lado_out, self.nome = pecas, lado_in, lado_out, nome; self._snap = None
    def camada(self, t):
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for p in self.pecas: p.draw(L, t)
        return L
    def _fotos(self):
        """quadro inicial e final da arte, recortados na caixa que contém tudo. Viram a folha que se dobra em bolinha."""
        if self._snap is None:
            res = []
            for t in (0.0, FICA):
                L = self.camada(t); bb = L.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox() or (0, 0, 64, 64)
                res.append((L.crop(bb), ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)))
            self._snap = res
        return self._snap
    def frame(self, fundo, t):
        fr = fundo.copy(); (img_in, c_in), (img_out, c_out) = self._fotos()
        if t < CHEGA:                                   # a bolinha chega, em arco, girando
            p = ease_out(t / CHEGA); b = _bola(img_in, 'A').quadro(1.0); x0 = c_in[0] + self.lado_in * (W / 2 + 320); y0 = c_in[1] - 650
            x = x0 + (c_in[0] - x0) * p; y = y0 + (c_in[1] - y0) * p - 330 * 4 * p * (1 - p)
            por(fr, b, x, y, rot=self.lado_in * 520 * (1 - p)); return fr
        if t < T_ARTE:                                  # abre
            u = (t - CHEGA) / ABRE; c = 1 - ease_io(u); im = _bola(img_in, 'A').quadro(c); por(fr, im, c_in[0], c_in[1], rot=-3 * c, op=0.30 * c); return fr
        if t < T_ARTE + FICA:                           # arte parada na tela, com o balanço
            fr.alpha_composite(self.camada(t - T_ARTE)); return fr
        v = t - T_ARTE - FICA
        if v < FECHA:                                   # fecha em bolinha
            u = v / FECHA; c = ease_io(u); im = _bola(img_out, 'A').quadro(c); por(fr, im, c_out[0], c_out[1], rot=3 * c, op=0.30 * c); return fr
        v -= FECHA
        if v < VAI:                                     # a bolinha é jogada para fora
            p = (v / VAI); b = _bola(img_out, 'A').quadro(1.0); x1 = c_out[0] + self.lado_out * (W / 2 + 360); y1 = c_out[1] - 260
            x = c_out[0] + (x1 - c_out[0]) * p ** 1.5; y = c_out[1] + (y1 - c_out[1]) * p - 360 * 4 * p * (1 - p) * 0.0 - 260 * math.sin(math.pi * p) + 420 * p ** 3
            por(fr, b, x, y, rot=self.lado_out * 460 * p); return fr
        return fr
