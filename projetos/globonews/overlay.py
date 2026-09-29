from PIL import Image, ImageDraw, ImageFont
W,H=1080,1920
BLUE=(0,103,135); RED=(212,15,8); ORANGE=(217,128,0); BG=(14,18,22); WHITE=(245,242,235)
LG='../../identidade_alucinacao/fontes/LeagueGothic.ttf'
def F(s): return ImageFont.truetype(LG,s)
img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
# painel inferior
d.rectangle([0,960,W,H],fill=BG)
# cabeçalho
y=1055
hdr=F(62); t1='DATAS DE EXIBIÇÃO NO FESTIVAL DO RIO 2026'
tw=d.textlength(t1,font=hdr); d.text(((W-tw)/2,y),t1,font=hdr,fill=WHITE)
d.rectangle([60,y+80,W-60,y+84],fill=BLUE)
# cartaz
P=Image.open('../../identidade_alucinacao/cartaz.jpg').convert('RGB')
ph=640; pw=round(P.width*ph/P.height); P=P.resize((pw,ph),Image.LANCZOS)
px,py=60,y+120
img.paste(P,(px,py))
# datas
x0=px+pw+50; colw=W-60-x0
entries=[('03 OUT','SÁBADO · 17:00',['ESTAÇÃO CLARO GÁVEA 4']),
         ('05 OUT','SEGUNDA · 16:00',['CINE ODEON · CCLSR']),
         ('06 OUT','TERÇA · 21:15',['CINESYSTEM BELAS ARTES','BOTAFOGO 5'])]
big=F(104); mid=F(44); sm=F(38)
cy=py-8
for i,(dt,dh,cine) in enumerate(entries):
    d.text((x0,cy),dt,font=big,fill=ORANGE)
    cy+=100
    d.text((x0,cy),dh,font=mid,fill=WHITE); cy+=48
    for c in cine:
        d.text((x0,cy),c,font=sm,fill=(190,200,205)); cy+=40
    if i<2:
        cy+=12; d.rectangle([x0,cy,x0+colw,cy+3],fill=BLUE); cy+=10
print('fim datas',cy,'fim cartaz',py+ph,'col',x0,colw)
# tarja na emenda
bh=120; by=960-bh//2
d.rectangle([0,by,W,by+bh],fill=RED)
f=F(84); a='ALUCINAÇÃO'; b=' É DESTAQUE NA GLOBONEWS'
tw=d.textlength(a+b,font=f); tx=(W-tw)/2; ty=by+(bh-84)/2-6
d.text((tx,ty),a,font=f,fill=WHITE); d.text((tx+d.textlength(a,font=f),ty),b,font=f,fill=WHITE)
print('tarja largura',tw)
img.save('overlay.png')
