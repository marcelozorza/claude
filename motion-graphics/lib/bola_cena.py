"""Ciclo da bolinha de papel, reutilizável em qualquer animação (guardado no kit).

    bolinha chega (0,60 s) -> abre (0,55 s) -> ARTE FIXA 10 s, com o balanço que as peças já têm -> fecha em bolinha (0,55 s)
    -> a bolinha vai embora (0,60 s). Chegada e saída fazem o mesmo arco balístico, uma espelhando a outra: a bola aparece (ou some) no
    estágio apertado, uma bola MENOR e MAIS AMASSADA desenhada de novo (não é redimensionamento), e troca para a bola normal.

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

CHEGA, ABRE, FICA, FECHA, VAI, FOLGA = 0.60, 0.55, 10.0, 0.55, 0.60, 0.10
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
    def __init__(self, camada, tamanho=(1080, 1920), lado_in=-1, lado_out=1, estagios=1, fica=FICA):
        self.camada, self.tam, self.lado_in, self.lado_out, self.n_est, self.fica = camada, tamanho, lado_in, lado_out, estagios, fica
        self.dur = round(CHEGA + ABRE + fica + FECHA + VAI + FOLGA, 2); self._snap = None; self._est = {}
    def _fotos(self):
        """quadro inicial e final da arte, recortados na caixa que contém tudo. Viram a folha que se dobra em bolinha."""
        if self._snap is None:
            res = []
            for t in (0.0, self.fica):
                L = self.camada(t); bb = L.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox() or (0, 0, 64, 64)
                res.append((L.crop(bb), ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)))
            self._snap = res
        return self._snap
    def _estagios(self, qual):
        """a bola normal e as bolas menores e mais amassadas, desenhadas de novo (bola.estagios_amassados). qual = 0 entrada, 1 saída"""
        if qual not in self._est: self._est[qual] = estagios_amassados(_bola(self._fotos()[qual][0], 'A').quadro(1.0), self.n_est)
        return self._est[qual]
    @staticmethod
    def _arco(centro, lado, p):
        """arco balístico da bolinha: p = 0 no ponto de pouso, p = 1 no ponto mais longe (a saída percorre de 0 a 1, a chegada de 1 a 0)"""
        return centro[0] + lado * 430 * p, centro[1] - 120 * math.sin(math.pi * p * 0.85) + 90 * p * p
    def frame(self, fundo, t):
        W, H = self.tam; fr = fundo.copy(); (img_in, c_in), (img_out, c_out) = self._fotos()
        if t < CHEGA:                                   # a bolinha chega pelo mesmo arco da saída, de trás para a frente: apertada, depois normal
            p = 1 - t / CHEGA; est = self._estagios(0); k = min(len(est) - 1, int(p * len(est))); x, y = self._arco(c_in, self.lado_in, p)
            por(fr, est[k], x, y, rot=-3 + self.lado_in * 300 * p); return fr
        if t < T_ARTE:                                  # abre
            u = (t - CHEGA) / ABRE; c = 1 - ease_io(u); im = _bola(img_in, 'A').quadro(c); por(fr, im, c_in[0], c_in[1], rot=-3 * c, op=0.30 * c); return fr
        if t < T_ARTE + self.fica:                      # arte parada na tela, com o balanço
            fr.alpha_composite(self.camada(t - T_ARTE)); return fr
        v = t - T_ARTE - self.fica
        if v < FECHA:                                   # fecha em bolinha
            u = v / FECHA; c = ease_io(u); im = _bola(img_out, 'A').quadro(c); por(fr, im, c_out[0], c_out[1], rot=3 * c, op=0.30 * c); return fr
        v -= FECHA
        if v < VAI:                                     # vai embora: a bola normal, depois a apertada, trocadas em stop motion, e some
            p = v / VAI; est = self._estagios(1); k = min(len(est) - 1, int(p * len(est))); x, y = self._arco(c_out, self.lado_out, p)
            por(fr, est[k], x, y, rot=3 + self.lado_out * 300 * p); return fr
        return fr


TOPO_SEGURO = 288          # 15% de 1920. A faixa de cima do quadro é coberta pela interface do Instagram: nada pode entrar nela

def topo_minimo(ciclo, passo=0.15):
    """menor y (mais alto na tela) ocupado por qualquer peça, incluindo a bolinha em voo e as sombras, ao longo de toda a cena.
    Devolve (y, t). Serve para garantir que nada invada a faixa de cima (y < TOPO_SEGURO)."""
    W, H = ciclo.tam; vazio = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pior = (H, 0.0); t = 0.0
    while t <= ciclo.dur:
        bb = ciclo.frame(vazio, t).getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
        if bb and bb[1] < pior[0]: pior = (bb[1], t)
        t += passo
    return pior
