import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math, random, subprocess, sys
FI=os.path.join(os.environ.get('FONTS_DIR','./fontes/'),'EBGaramond-Italic.ttf')
W=1080
def font(size,wght=500):
    f=ImageFont.truetype(FI,size)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f
def ease(t): t=max(0,min(1,t)); return 1-(1-t)**3
def paper(w,h,seed=1):
    rng=np.random.default_rng(seed)
    base=np.zeros((h,w,4),np.uint8); base[...,0]=251; base[...,1]=248; base[...,2]=240; base[...,3]=255
    n=rng.normal(0,3.2,(h,w)); 
    for c in range(3): base[...,c]=np.clip(base[...,c]+n,0,255)
    im=Image.fromarray(base,'RGBA')
    # borda levemente irregular
    m=Image.new('L',(w,h),0); d=ImageDraw.Draw(m)
    pts=[(rng.uniform(0,4),rng.uniform(0,5)),(w-rng.uniform(0,4),rng.uniform(0,8)),(w-rng.uniform(0,3),h-rng.uniform(0,4)),(rng.uniform(0,3),h-rng.uniform(0,3))]
    d.polygon(pts,fill=255); im.putalpha(m); return im
def hl_shape(w,h,seed=2):
    rng=np.random.default_rng(seed); m=Image.new('L',(w,h),0); d=ImageDraw.Draw(m)
    top=[(x,rng.uniform(0,h*0.12)) for x in np.linspace(0,w,12)]
    bot=[(x,h-rng.uniform(0,h*0.12)) for x in np.linspace(w,0,12)]
    d.polygon(top+bot,fill=255); return m.filter(ImageFilter.GaussianBlur(1.2))
class Label:
    """lines: lista de linhas; hl: lista de (linha, texto_destacado)"""
    def __init__(s,lines,hl=(),size=96,rot=-1.5,seed=1):
        s.lines=lines; s.hl=hl; s.f=font(size); s.size=size; s.rot=rot; s.seed=seed
        d=ImageDraw.Draw(Image.new('RGB',(1,1)))
        s.lh=int(size*1.18); s.padx=int(size*0.55); s.pady=int(size*0.30)
        s.ws=[d.textlength(l,font=s.f) for l in lines]
        s.w=int(max(s.ws)+2*s.padx); s.h=int(s.lh*len(lines)+2*s.pady)
        s.paper=paper(s.w,s.h,seed)
        s.nchar=sum(len(l) for l in lines)
        # caixas dos destaques
        s.boxes=[]
        for li,t in hl:
            l=lines[li]; i=l.index(t); x0=s.padx+d.textlength(l[:i],font=s.f); x1=x0+d.textlength(t,font=s.f)
            y0=s.pady+li*s.lh+size*0.42; y1=s.pady+li*s.lh+size*1.02
            s.boxes.append((x0-12,y0,x1+10,y1))
    def frame(s,t,t_type=None,t_hl=None,t_out=None):
        """t em segundos desde a entrada"""
        t_type=t_type if t_type is not None else 0.25
        dur_type=min(0.9,0.035*s.nchar)
        t_hl=t_hl if t_hl is not None else t_type+dur_type+0.15
        pd=60; C=Image.new('RGBA',(s.w+2*pd,s.h+2*pd),(0,0,0,0))
        # sombra
        sh=Image.new('RGBA',(s.w,s.h),(0,0,0,0)); sh.putalpha(s.paper.getchannel('A').point(lambda v:v*70//255))
        C.alpha_composite(sh,(pd+6,pd+14)); C=C.filter(ImageFilter.GaussianBlur(12))
        P=s.paper.copy()
        # marca-texto
        for k,(x0,y0,x1,y1) in enumerate(s.boxes):
            p=ease((t-t_hl-k*0.35)/0.45)
            if p>0:
                ww=int((x1-x0)*p); hh=int(y1-y0)
                if ww>2:
                    m=hl_shape(int(x1-x0),hh,s.seed+k).crop((0,0,ww,hh))
                    col=Image.new('RGBA',(ww,hh),(250,226,70,255)); col.putalpha(m.point(lambda v:v*215//255))
                    P.alpha_composite(col,(int(x0),int(y0)))
        # texto digitado
        d=ImageDraw.Draw(P); shown=int(max(0,(t-t_type))/max(dur_type,1e-3)*s.nchar) if t>=t_type else 0
        c=0
        for li,l in enumerate(s.lines):
            n=max(0,min(len(l),shown-c)); c+=len(l)
            if n: d.text((s.padx,s.pady+li*s.lh),l[:n],font=s.f,fill=(22,20,18,255))
        C.alpha_composite(P,(pd,pd))
        # entrada: pop de escala
        sc=0.85+0.15*ease(t/0.22) if t<0.22 else 1.0
        a=ease(t/0.15)
        if t_out is not None and t>t_out: a*=1-ease((t-t_out)/0.2)
        R=C.rotate(s.rot,expand=True,resample=Image.BICUBIC)
        if sc!=1: R=R.resize((int(R.width*sc),int(R.height*sc)),Image.BICUBIC)
        if a<1: R.putalpha(R.getchannel('A').point(lambda v:int(v*a)))
        return R
