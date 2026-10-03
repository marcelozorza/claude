# Motion graphics da marca (Nada Errado com VC)

Peças reutilizáveis para os vídeos com apresentador em chroma key sobre papel quadriculado.

## Fundo graph paper
- `assets/graph_paper_1080x1920.png`: fundo pronto.
- `lib/fundo.py`: gera o mesmo fundo em qualquer tamanho (`fundo(W, H)`). Cor média creme `(241, 229, 201)`.

## Bola de papel (entrada e saída de fotos)
Uma imagem recortada entra como uma bola de papel que se abre e sai como uma bola que se fecha.
Não há fade nem mudança de tamanho. A folha é uma pilha de pedaços convexos. Cada dobra corta a pilha por uma reta
e gira a parte de fora por cima do resto. O verso branco passa a cobrir a foto, até restar só a bola.

```python
from papel import recorte_jornal          # foto recortada com margem de papel irregular (tesoura)
from bola import BolaPapel                # modo 'A' dobras irregulares, modo 'B' espiral
from animfoto import estado, sombra_papel # estado(item, segundos_desde_a_entrada, tempo_parado, modo='A')

item = recorte_jornal(imagem_rgba_recortada)
b = BolaPapel(item, 'A')
b.quadro(0.0)    # folha aberta
b.quadro(0.6)    # dobras
b.quadro(1.0)    # bola fechada
```
`estado()` já cuida da sequência inteira: entrada (0,5 s), parada, saída (0,5 s) e o sumiço da bola.

## Título na tela (em revisão)
Frase em tira de papel rasgado, EB Garamond itálico, com marca-texto passando conforme a fala. Entra e sai como um quadradinho
que se desdobra com as dobras reais da bola de papel. Detalhes e pendências em `HANDOFF.md`.

```python
from titulo import Titulo
t = Titulo('Lorem ipsum dolor', entrada='dobra')
t.quadro(segundos)   # RGBA 1080x1920
```

## Chroma key e cor do apresentador (`lib/chroma.py`)
- `key_rgb(frame)`: remove o verde por dominância (`g - max(r, b)`) e faz despill.
- `grade(frame, temp, matiz, sat)`: correção de cor do apresentador. O tom aprovado foi `0.26, 0.26, 0.26`.

## Dependências
Python 3, numpy, scipy, pillow.
