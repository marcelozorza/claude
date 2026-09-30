import os
from PIL import Image
U=os.environ.get('PRINTS_DIR','./prints/')
S=1220/900
# (arquivo, tipo, topo do cabeçalho, base, fim do nome) em coordenadas 900x2000
C=[
('468384f7','c',630,785,0),('ee7d3281','c',1008,1210,0),('37b58923','c',900,1010,0),
('03adcf27','c',893,1095,0),('b47fdc5b','c',852,965,0),('7b275cf2','c',642,798,0),
('7b275cf2','c',1142,1345,0),('283a1e52','c',385,495,0),('b7a1f97e','c',340,452,0),
('a309c6dc','c',340,495,0),('a309c6dc','c',795,905,0),('e7406b2d','c',288,398,0),
('e7406b2d','c',948,1150,0),('e887e0f9','c',443,600,0),('8040886b','c',388,500,0),
('8040886b','c',593,705,0),('c4be9aa1','c',316,428,0),('c4be9aa1','c',1228,1382,0),
('c3022135','c',797,908,0),('c3022135','c',1253,1362,0),('5de59f9a','c',772,930,0),
('5de59f9a','c',1365,1522,0),('942d4903','c',1145,1345,0),('942d4903','c',383,585,0),
('275bb9ad','c',537,780,0),('f927b32e','c',318,565,0),('f927b32e','c',1070,1225,0),
('2abbc168','c',587,697,0),
('e644ce36','n',632,850,740),('e644ce36','n',1278,1385,385),('32b82ec6','n',1007,1380,530),
('80e2346a','n',663,1040,520),('80e2346a','n',1120,1280,740),('e53e4f29','n',793,955,740),
('e53e4f29','n',1493,1652,740),
]
def pix(im,box):
    box=tuple(int(v*S) for v in box); r=im.crop(box)
    w,h=r.size; r=r.resize((max(1,w//18),max(1,h//18)),Image.BILINEAR).resize((w,h),Image.NEAREST)
    im.paste(r,box)
for i,(f,t,top,bot,xe) in enumerate(C,1):
    im=Image.open(U+f+'-image.jpg').convert('RGB')
    if t=='c':
        pix(im,(22,top-8,135,top+92)); pix(im,(145,top-4,700,top+48)); box=(15,top-18,885,max(bot,top+128))
        if top+128>bot: im.paste((255,255,255),tuple(int(v*S) for v in (15,bot,760,top+128)))
    else:
        pix(im,(40,top-5,182,top+135)); pix(im,(208,top-4,xe,top+52)); box=(30,top-18,755,bot)
    im.crop(tuple(int(v*S) for v in box)).save(f'comentario_{i:02d}.png')
print(len(C))
