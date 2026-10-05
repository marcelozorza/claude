"""Cena padrão. Cada cena é um arquivo de vídeo independente sobre o papel pautado, sem nada fora dela:
  a bolinha de papel chega, abre, fica 10 s com a arte na tela (com o balanço leve), fecha em bolinha e vai embora.
Nenhuma outra peça aparece junto da abertura ou do fechamento. O excesso é cortado pelo usuário na edição.
Uso no código: Cena(pecas).frame(fundo, t) com t em segundos de 0 a DUR. As peças usam o tempo LOCAL da arte (0 a 10 s)."""
import sys, os
from pecas import *
sys.path.insert(0, os.path.join(RAIZ, 'motion-graphics', 'lib'))
from bola_cena import CicloBola, CHEGA, ABRE, FICA, FECHA, VAI, FOLGA, DUR, T_ARTE, por

class Cena(CicloBola):
    """cena = ciclo da bolinha em volta de uma lista de peças (peças com draw(fr, t), t local da arte de 0 a 10 s)"""
    def __init__(self, pecas, lado_in=-1, lado_out=1, nome='cena'):
        self.pecas, self.nome = pecas, nome; super().__init__(self.camada_pecas, (W, H), lado_in, lado_out)
    def camada_pecas(self, t):
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for p in self.pecas: p.draw(L, t)
        return L
