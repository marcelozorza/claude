import json, subprocess, os, sys, numpy as np, wave
V=os.environ.get('VIDEO_DIR','./trabalho/')
FF=os.path.expanduser('~/bin/ffmpeg'); SR=48000
TRILHA=sys.argv[1] if len(sys.argv)>1 else 'trilha_jazz'
POP=sys.argv[2] if len(sys.argv)>2 else 'pop_1'
meta=json.load(open(V+'gfx/render_meta.json')); items=meta['items']; T=meta['total']
def load(path,ss=None,dur=None):
    cmd=[FF,'-nostdin','-loglevel','error']+(['-ss',str(ss)] if ss is not None else [])+['-i',path]+(['-t',str(dur)] if dur else [])+['-ac','2','-ar',str(SR),'-f','f32le','-']
    return np.frombuffer(subprocess.run(cmd,capture_output=True,check=True).stdout,np.float32).reshape(-1,2).copy()
N=int((T+0.5)*SR); voz=np.zeros((N,2),np.float32); fx=np.zeros((N,2),np.float32)
fade=int(0.015*SR); r=np.linspace(0,1,fade)[:,None]
for it in items:
    a=load(V+'input.mp4',it['a'],it['b']-it['a']); a[:fade]*=r; a[-fade:]*=r[::-1]
    i0=int(it['o0']*SR); voz[i0:i0+len(a)]+=a[:N-i0]
# normaliza a voz para pico ~ -3 dB
voz*=0.7/max(1e-6,np.abs(voz).max())
pops=[load(V+f'audio/pop_{k}.mp3') for k in (1,2,3,4)]
for j,t in enumerate(meta['pops']):
    pop=pops[j%4]; i0=int(t*SR); fx[i0:i0+len(pop)]+=pop[:N-i0]*0.55
mus=load(V+f'audio/{TRILHA}.mp3')[:N]*(0.68 if TRILHA=='trilha_jazz' else 1.0)
if len(mus)<N: mus=np.pad(mus,((0,N-len(mus)),(0,0)))
# envelope da trilha: alta na abertura e nos pops, baixa sob a fala
env=np.full(N,0.13,np.float32)
hi=[(0,4.0)]
for a,b in hi: env[int(a*SR):int(b*SR)]=0.42
k=int(0.25*SR); env=np.convolve(env,np.ones(k)/k,mode='same').astype(np.float32)
env[-int(1.5*SR):]*=np.linspace(1,0,int(1.5*SR))
mix=voz+fx+mus*env[:,None]
mix=np.clip(mix,-0.98,0.98)
out=V+'gfx/mix.wav'
w=wave.open(out,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()
print('ok',out)
