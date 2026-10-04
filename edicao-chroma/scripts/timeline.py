import os
# Linha do tempo v3
FPS=30
INTRO=4.0
# z = tamanho relativo (1.0 = topo da cabeça um pouco acima do meio); bg = variação do mosaico; cards = leva de comentários
SEGS=[
 dict(a=70.05,b=79.80,bg='mosA',z=1.0,cards=None),                  # faz três meses... (comentários da abertura ao fundo)
 dict(a=80.10,b=82.84,bg='mosB',z=1.28,cards=[4,17,20]),           # o resultado são esses comentários
 dict(a=83.06,b=88.95,bg='mosC',z=1.15,cards=[13,16,23]),           # oásis de informação séria
 dict(a=96.22,b=99.85,bg='mosA',z=0.85,cards=[26,25,32]),          # quase 10 mil seguidores
 dict(a=121.48,b=125.95,bg='mosB',z=1.0,cards=[5,8,11]),           # enquanto a internet...
 dict(a=125.95,b=130.42,bg='mosC',z=1.3,cards=[3,19,24]),          # aqui tem investigação...
 dict(a=150.06,b=156.45,bg='mosA',z=0.9,cards=[15,27,28]),         # vídeos de até três minutos
 dict(a=156.65,b=159.00,bg='mosB',z=1.2,cards=[2,18,9]),           # já são mais de 40 vídeos
]
INTRO_CARDS=[2,18,1,21,6,12,14,22,7,9]
FIX={'você,':'vc','editor':'editora','para':'pra'}
