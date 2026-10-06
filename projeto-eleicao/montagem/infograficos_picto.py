"""Cenas de infográfico no estilo de pictograma (ISO 7001): formas chapadas, sem contorno, sem borda, sem sombra.
Cada classe tem draw(fr, t) com t LOCAL da arte (0 a 10 s). Id da cena com número: I1_duas_dores."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pictogramas as P
from cena import Cena, W, H, Image

def _spring(u, k=5.0, f=3.0): return math.exp(-k * u) * math.sin(2 * math.pi * f * u) if u > 0 else 0.0
def _clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def _escala(im, s): return im if abs(s - 1.0) < 0.01 else im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)

class Pedaco:
    """metade de uma flecha partida: cai com gravidade, gira, bate no chão, dá um pulinho e fica"""
    G = 2600.0
    def __init__(self, im, x0, y0, xf, yf, tb, rot_fim, giro, vy0=-170.0, col=None):
        self.col = col or P.colar
        self.im, self.x0, self.y0, self.xf, self.yf, self.tb, self.rf, self.giro, self.vy0 = im, x0, y0, xf, yf, tb, rot_fim, giro, vy0
        self.ul = (-vy0 + math.sqrt(vy0 * vy0 + 2 * self.G * (yf - y0))) / self.G                       # tempo até o chão
    def draw(self, fr, t):
        u = t - self.tb
        if u < 0: return
        a = _clamp(u / self.ul)
        x = self.x0 + (self.xf - self.x0) * a
        y = self.y0 + self.vy0 * u + 0.5 * self.G * u * u if u < self.ul else self.yf
        if u >= self.ul: y -= 16 * math.sin(math.pi * _clamp((u - self.ul) / 0.22))                    # pulinho ao bater
        rot = self.rf * a + self.giro * math.sin(math.pi * a)
        self.col(fr, self.im, x, y, rot)

class DuasDores:
    """uma flecha vermelha acerta o peito (dor inevitável). Duas flechas cinzas partem antes de chegar e caem (dores evitáveis)"""
    FIG_H, CX, PISO, COMP = 400, 800, 765, 340
    PEITO_K, DY_A, DY_B = 0.38, -140, 125
    col = staticmethod(P.colar)
    def _sprites(self):
        fig = P.pessoa(P.TINTA, 'parado'); self.fig = _escala(fig, self.FIG_H / fig.height)
        self.cor = P.coracao(39); self.estrela = P.estrela_chapada(100, 11, P.AMAR)
        self.fv = P.flecha(self.COMP, P.VERM, P.TERRA, 22); self.fc = P.flecha(self.COMP, P.CINZA, P.CINZA, 22)
    def __init__(self):
        self.nome = 'duas dores'; self._sprites()
        self.topo = self.PISO - self.fig.height; self.peito = self.topo + self.PEITO_K * self.fig.height
        w = self.fc.width; meio = w // 2; self.cauda = self.fc.crop((0, 0, meio, self.fc.height)); self.ponta = self.fc.crop((meio, 0, w, self.fc.height))
        self.x_acerto = self.CX - 10 - self.fv.width / 2                                                  # centro da flecha vermelha cravada
        h = w / 4; chao = self.PISO - 18
        cfg = [(3.0, 4.0, self.peito + self.DY_A, 490, 430, 590), (3.4, 4.6, self.peito + self.DY_B, 300, 100, 260)]   # início do voo, quebra, altura, centro da quebra, destinos
        self.voos = cfg; self.pedacos = []
        for (ti, tb, y, xq, xc, xp) in cfg:
            self.pedacos.append(Pedaco(self.cauda, xq - h, y, xc, chao, tb, -9, -45, -150, self.col)); self.pedacos.append(Pedaco(self.ponta, xq + h, y, xp, chao, tb, 7, 55, -210, self.col))
    def draw(self, fr, t):
        # figura: recua quando a flecha acerta (0,9 s) e respira devagar depois
        u = t - 0.9; rec = -7.0 * _spring(u) if u > 0 else 0.0; dx = 10 * max(0.0, _spring(u, 6.0, 2.5)) if u > 0 else 0.0
        sway = 0.9 * math.sin(2 * math.pi * t / 3.2); fig = self.fig.rotate(rec + sway, resample=Image.BICUBIC, expand=True)
        self.col(fr, fig, self.CX + dx, self.PISO - self.fig.height / 2)
        pulso = 1.0 + 0.04 * math.sin(2 * math.pi * t / 1.2) + (0.38 * math.sin(math.pi * _clamp(u / 0.5)) if u > 0 else 0.0)
        if 0 <= u < 0.75: self.col(fr, _escala(self.estrela, 0.4 + 0.95 * math.sin(math.pi * _clamp(u / 0.75))), self.CX + dx - 6, self.peito)
        self.col(fr, _escala(self.cor, pulso), self.CX + dx - 4, self.peito)
        # flecha vermelha: voa em aceleração, crava e treme
        if t < 0.9:
            a = (t / 0.9) ** 1.8; x = -self.COMP / 2 - 60 + (self.x_acerto + self.COMP / 2 + 60) * a
            self.col(fr, self.fv, x, self.peito, 0)
        else: self.col(fr, self.fv, self.x_acerto + dx, self.peito, 2.5 * _spring(u, 4.0, 3.5))
        # flechas cinzas: voam e partem no ar
        for (ti, tb, y, xq, _, _) in self.voos:
            if ti <= t < tb:
                a = (t - ti) / (tb - ti); x = -self.COMP / 2 - 60 + (xq + self.COMP / 2 + 60) * (1 - (1 - a) ** 1.3)
                self.col(fr, self.fc, x, y, 0)
        for p in self.pedacos: p.draw(fr, t)
    def sons(self): return []

class DuasDoresPapel(DuasDores):
    """a mesma cena no estilo antigo: recortes de papel com borda branca fibrosa, contorno de tinta e sombra"""
    PEITO_K, DY_A, DY_B = 0.64, -150, 45
    def _sprites(self):
        import pecas, infograficos, storyboards
        self.fig = pecas.boneco(pecas.PELES[0], pecas.AZUL, 1.8, seed=3); self.cor = pecas.coracao(3.1); self.estrela = infograficos.estrela(r1=84, r2=50)
        self.fv = storyboards.flecha(pecas.VERM, self.COMP); self.fc = storyboards.flecha(storyboards.CINZA, self.COMP, 4)
        self._compor = pecas.compor
    def col(self, fr, im, x, y, rot=0.0): self._compor(fr, im, x, y, rot=rot, off=8, blur=8, op=0.25)

CENAS_PICTO = {'I1_duas_dores': lambda: Cena([DuasDores()]), 'I1_duas_dores_papel': lambda: Cena([DuasDoresPapel()])}
