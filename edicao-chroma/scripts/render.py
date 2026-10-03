import sys, os, json, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from label import ease
from timeline import *
V=os.environ.get('VIDEO_DIR','./trabalho/')
FF=os.path.expanduser('~/bin/ffmpeg')
W,H=1080,1920
FSUB='/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
LIMIT=None
for a in sys.argv:
    if a.startswith('--until='): LIMIT=float(a.split('=')[1])
CARD_HOLD=7.0

# ---------- pessoa: recorte do bruto y 380..1560 (1180 px), cabeça em ~y 400 do bruto
CROP_Y,CROP_H,HEAD_RAW=380,1180,400
BASE_H=1058   # altura renderizada com z=1.0 -> topo da cabeça ~ y 880
def person_geom(z):
    h=int(BASE_H*z)//2*2; w=int(1080*h/CROP_H)//2*2
    head=H-h+int((HEAD_RAW-CROP_Y)*h/CROP_H)
    return w,h,head

# ---------- linha do tempo
t=INTRO; items=[]
for s in SEGS:
    s=dict(s); s['o0']=t; s['o1']=t+(s['b']-s['a']); t=s['o1']; items.append(s)
TOTAL=t
print('duração total',round(TOTAL,2))

# ---------- legendas
words=[w for seg in json.load(open(V+'transcricao.json')) for w in seg['words']]
subs=[]
for it in items:
    ws=[w for w in words if w['s']>=it['a']-0.02 and w['s']<it['b']-0.05]
    cur=[]
    def flush():
        if cur: subs.append([cur[0][0],cur[-1][1],' '.join(c[2] for c in cur)])
    for w in ws:
        txt=FIX.get(w['w'].strip(),w['w'].strip())
        clean=txt.lower().strip('.,…?!').replace('...','')
        o0=it['o0']+(w['s']-it['a']); o1=min(it['o1'],it['o0']+(w['e']-it['a']))
        if cur and (len(' '.join(c[2] for c in cur))+len(clean)>30 or o0-cur[-1][1]>0.45): flush(); cur=[]
        cur.append([o0,o1,clean])
        if txt.endswith(('.',',')) and len(' '.join(c[2] for c in cur))>=14: flush(); cur=[]
    flush()
k=1
while k<len(subs):
    if len(subs[k][2].split())==1 and subs[k][0]-subs[k-1][1]<0.3 and len(subs[k-1][2])+len(subs[k][2])<=38:
        subs[k-1][1]=subs[k][1]; subs[k-1][2]+=' '+subs[k][2]; subs.pop(k)
    else: k+=1
for i in range(len(subs)-1):
    subs[i][1]=subs[i+1][0] if subs[i+1][0]-subs[i][1]<0.5 else subs[i][1]+0.25
subs[-1][1]+=0.3
json.dump(subs,open(V+'gfx/legendas.json','w'),ensure_ascii=False,indent=0)
fsub=ImageFont.truetype(FSUB,62)
def wrap(txt,maxc=19):
    lines=['']
    for w in txt.split():
        if lines[-1] and len(lines[-1])+1+len(w)>maxc: lines.append(w)
        else: lines[-1]=(lines[-1]+' '+w).strip()
    return wrap(txt,maxc+5) if len(lines)>2 else lines
_subcache={}
def sub_img(txt):
    if txt in _subcache: return _subcache[txt]
    lines=wrap(txt); lh=72; im=Image.new('RGBA',(W,lh*len(lines)+30),(0,0,0,0)); dd=ImageDraw.Draw(im)
    for i,l in enumerate(lines):
        w=dd.textlength(l,font=fsub); dd.text(((W-w)/2,10+i*lh),l,font=fsub,fill='#FFE600',stroke_width=7,stroke_fill='black')
    _subcache[txt]=im; return im

# ---------- cartões
def card(n,w):
    c=Image.open(V+f'comentarios/comentario_{n:02d}.png').convert('RGBA'); c=c.resize((w,int(c.height*w/c.width)),Image.LANCZOS)
    m=Image.new('L',c.size,0); ImageDraw.Draw(m).rounded_rectangle([0,0,c.width-1,c.height-1],28,fill=255); c.putalpha(m)
    pad=40; s=Image.new('RGBA',(c.width+2*pad,c.height+2*pad),(0,0,0,0))
    sh=Image.new('RGBA',c.size,(0,0,0,0)); sh.putalpha(m.point(lambda v:v*110//255))
    s.paste(sh,(pad,pad+12),sh); s=s.filter(ImageFilter.GaussianBlur(14)); s.alpha_composite(c,(pad,pad)); return s
_cc={}
def card_r(n,w,rot):
    k=(n,w,rot)
    if k not in _cc: _cc[k]=card(n,w).rotate(rot,expand=True,resample=Image.BICUBIC)
    return _cc[k]
def card_h(n,w):
    c=Image.open(V+f'comentarios/comentario_{n:02d}.png'); return int(c.height*w/c.width)
def back(t):
    t=max(0,min(1,t)); c1=1.70158; c3=c1+1; return 1+c3*(t-1)**3+c1*(t-1)**2
def put_pop(base,im,cx,cy,t_since,dur=0.22,a_mul=1.0,sc_mul=1.0):
    if t_since<0: return
    p=back(t_since/dur); sc=(0.6+0.4*p)*sc_mul; a=min(1,t_since/0.1)*a_mul
    if a<=0.01: return
    if abs(sc-1)>0.005: im=im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.BILINEAR)
    if a<1: im=im.copy(); im.putalpha(im.getchannel('A').point(lambda v:int(v*a)))
    base.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2)))

pops=[]
# abertura
INTRO_LAYOUT=[(420,230,-4),(660,420,3),(400,620,2),(680,800,-3),(410,990,-2),(670,1170,3),(420,1350,-3),(660,1530,2),(420,1710,3),(700,1790,-2)]
intro_times=[0.15,1.35]+[2.55+0.16*i for i in range(8)]
pops+=intro_times
S1_END=items[0]['o1']
def intro_state(t):
    """retorna fator de 'ir para o fundo' (0 = frente, 1 = fundo)"""
    return ease((t-INTRO)/0.5) if t>=INTRO else 0.0
def draw_intro(base,t):
    if t>=S1_END: return
    k=intro_state(t)
    a_mul=1.0
    if t>S1_END-0.3: a_mul*=1-ease((t-(S1_END-0.3))/0.3)
    sc_mul=1-0.12*k
    for i,n in enumerate(INTRO_CARDS):
        ti=intro_times[i]
        if t<ti: continue
        x,y,r=INTRO_LAYOUT[i]
        x=W/2+(x-W/2)*sc_mul; y=H/2+(y-H/2)*sc_mul
        if i==0 and t<2.55:
            if t<1.35: put_pop(base,card_r(n,960,0),W/2,H/2,t-ti); continue
            p=ease((t-1.35)/0.3); put_pop(base,card_r(n,900,0),W/2,H/2-230*p,9); continue
        if i==1 and t<2.55: put_pop(base,card_r(n,900,0),W/2,H/2+170,t-ti); continue
        if i<2 and t<2.85:
            p=ease((t-2.55)/0.3); sx,sy=(W/2,H/2-230) if i==0 else (W/2,H/2+170)
            put_pop(base,card_r(n,760,r),sx+(x-sx)*p,sy+(y-sy)*p,9); continue
        put_pop(base,card_r(n,760,r),x,y,t-ti,a_mul=a_mul,sc_mul=sc_mul)

# levas de comentários na metade de cima, sem cobrir o rosto
for it in items:
    if not it.get('cards'): continue
    w_,h_,head=person_geom(it['z'])
    top,bottom=70,head+10
    cw=820
    while True:
        hs=[card_h(n,cw)+30 for n in it['cards']]
        if sum(hs)<=bottom-top or cw<=620: break
        cw-=20
    hs=[card_h(n,cw)+30 for n in it['cards']]
    total=sum(hs); avail=bottom-top
    step=(avail-hs[-1])/max(1,len(hs)-1) if total>avail else None
    y=top; lay=[]
    for j,(n,hh) in enumerate(zip(it['cards'],hs)):
        cy=(top+j*step+hh/2) if step is not None else (top+(avail-total)/2+sum(hs[:j])+hh/2)
        cx=W/2+(-110 if j%2==0 else 110); rot=(-3,2.5,-2)[j%3]
        lay.append((n,cw,rot,cx,cy))
    it['lay']=lay
    it['ct']=[it['o0']+0.12+0.6*j for j in range(len(lay))]
    it['cend']=min(it['o1'],it['o0']+CARD_HOLD)
    pops+=it['ct']
def draw_cards(base,it,t):
    if not it.get('cards') or t>=it['cend']: return
    a_mul=1.0
    if t>it['cend']-0.25 and it['cend']<it['o1']: a_mul=1-ease((t-(it['cend']-0.25))/0.25)
    for (n,cw,rot,cx,cy),tt in zip(it['lay'],it['ct']):
        put_pop(base,card_r(n,cw,rot),cx,cy,t-tt,a_mul=a_mul)

# ---------- logo redondo quando fala "nada errado com vc"
LOGO_SRC=(72.30,75.60)
_logo=Image.open(V+'gfx/logo_redondo.png').convert('RGBA'); _logo=_logo.resize((500,500),Image.LANCZOS)
it0=items[0]; LOGO_T0=it0['o0']+LOGO_SRC[0]-it0['a']; LOGO_T1=it0['o0']+LOGO_SRC[1]-it0['a']
pops.append(LOGO_T0)
def draw_logo(base,t):
    if LOGO_T0<=t<LOGO_T1:
        out=1-ease((t-(LOGO_T1-0.25))/0.25) if t>LOGO_T1-0.25 else 1.0
        put_pop(base,_logo,W/2,470,t-LOGO_T0,dur=0.28,a_mul=out,sc_mul=0.85+0.15*out)

# ---------- fundo
def build_bg():
    out=V+'gfx/bg_track.mp4'
    rng=lambda v:'+'.join(f'between(t,{it["o0"]:.3f},{it["o1"]:.3f})' for it in items if it['bg']==v) or '0'
    fc=(f"[0:v]fps=30,setsar=1[a];[1:v]fps=30,setsar=1[b];[2:v]fps=30,setsar=1[c];"
        f"[a][b]overlay=enable='{rng('mosB')}'[x];[x][c]overlay=enable='{rng('mosC')}',format=yuv420p[o]")
    subprocess.run([FF,'-nostdin','-loglevel','error','-y','-i',V+'gfx/mosaico_A.mp4','-i',V+'gfx/mosaico_B.mp4','-i',V+'gfx/mosaico_C.mp4','-filter_complex',fc,'-map','[o]','-t',f'{TOTAL:.3f}','-c:v','libx264','-crf','16','-preset','fast',out],check=True)
    return out

def person_reader(it):
    dur=it['b']-it['a']; w,h,_=person_geom(it['z'])
    vf=f"fps=30,crop=1080:{CROP_H}:0:{CROP_Y},format=yuva444p,chromakey=0x5ACD2A:0.13:0.06,despill=type=green:mix=0.6:expand=0.2,scale={w}:{h},format=rgba"
    p=subprocess.Popen([FF,'-nostdin','-loglevel','quiet','-ss',f'{it["a"]:.3f}','-i',V+'input.mp4','-t',f'{dur:.3f}','-vf',vf,'-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,bufsize=10**8)
    return p,w,h
def composite(bg,p,w,h):
    x0=(W-w)//2; y0=H-h
    sx=max(0,-x0); ex=min(w,W-x0); X0=max(0,x0)
    pp=p[:,sx:ex]; a=pp[...,3:4].astype(np.float32)/255.0
    region=bg[y0:y0+h,X0:X0+(ex-sx)].astype(np.float32)
    bg[y0:y0+h,X0:X0+(ex-sx)]=(pp[...,:3]*a+region*(1-a)).astype(np.uint8)

def main():
    bgf=build_bg() if (not os.path.exists(V+'gfx/bg_track.mp4') or '--rebuild-bg' in sys.argv) else V+'gfx/bg_track.mp4'
    N=int(round((LIMIT or TOTAL)*FPS))
    bgp=subprocess.Popen([FF,'-nostdin','-loglevel','quiet','-i',bgf,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,bufsize=10**8)
    outv=V+'gfx/video_only.mp4'
    enc=subprocess.Popen([FF,'-nostdin','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',outv],stdin=subprocess.PIPE)
    cur=None; pr=None; last=None
    for f in range(N):
        t=f/FPS
        raw=bgp.stdout.read(W*H*3)
        if len(raw)<W*H*3: break
        bg=np.frombuffer(raw,np.uint8).reshape(H,W,3).copy()
        it=next((i for i in items if i['o0']<=t<i['o1']),None)
        if t<INTRO: bg=(bg*0.6).astype(np.uint8)
        img=None
        if t<S1_END and t>=INTRO:
            img=Image.fromarray(bg).convert('RGBA'); draw_intro(img,t); bg=np.array(img.convert('RGB'))
        if it is not None:
            if cur is not it:
                if pr: pr[0].kill()
                pr=person_reader(it); cur=it
            p,w,h=pr; buf=p.stdout.read(w*h*4)
            if len(buf)==w*h*4: last=(np.frombuffer(buf,np.uint8).reshape(h,w,4),w,h)
            if last is not None: composite(bg,*last)
        img=Image.fromarray(bg).convert('RGBA')
        if t<INTRO: draw_intro(img,t)
        if it is not None: draw_cards(img,it,t)
        draw_logo(img,t)
        s=next((s for s in subs if s[0]<=t<s[1]),None)
        if s: img.alpha_composite(sub_img(s[2]),(0,1470))
        enc.stdin.write(img.convert('RGB').tobytes())
        if f%150==0: print(f'{t:.1f}s',flush=True)
    enc.stdin.close(); enc.wait()
    json.dump(dict(items=[{k:v for k,v in i.items() if k not in ('lay',)} for i in items],pops=sorted(pops),total=TOTAL),open(V+'gfx/render_meta.json','w'),indent=1)
if __name__=='__main__': main()
