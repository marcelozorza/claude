import glob, random, subprocess, os, sys
VAR=sys.argv[1] if len(sys.argv)>1 else 'A'
V=os.environ.get('VIDEO_DIR','./trabalho/')
FF=os.path.expanduser('~/bin/ffmpeg')
TOTAL=50
EPS=['dividacao','betsagora','comovejo','investigue','bets','cachorromeme','nao-ta-bem','testo','body-positivity','senna']
clips=[V+f'clips/{e}_c2.mp4' for e in EPS]
# embaralha evitando o mesmo episódio lado a lado
random.seed({'A':7,'B':3,'C':11}[VAR]); random.shuffle(clips)
os.makedirs(V+'gfx/mos',exist_ok=True)
COLS={'A':3,'B':2,'C':4}[VAR]; tw,th,g={'A':(340,604,20),'B':(520,924,20),'C':(255,453,12)}[VAR]
ROWS=-(-4056//(th+g))+1; NT=COLS*ROWS; per=4; inputs=[]
for i in range(NT):
    sel=[clips[(i*3+k)%len(clips)] for k in range(per)]
    lst=V+f'gfx/mos/t{i}.txt'; open(lst,'w').write(''.join(f"file '{c}'\n" for c in sel)*6)
    inputs+=['-f','concat','-safe','0','-i',lst]
lay=[]; fc=''
for i in range(NT):
    col=i%COLS; row=i//COLS; x=(1080-COLS*tw-(COLS-1)*g)//2+col*(tw+g); y=row*(th+g)+(0 if col%2==1 else th//2)
    lay.append(f'{x}_{y}'); fc+=f'[{i}:v]fps=30,scale={tw}:{th},setsar=1,trim=0:{TOTAL},setpts=PTS-STARTPTS[t{i}];'
fc+=''.join(f'[t{i}]' for i in range(NT))+f"xstack=inputs={NT}:layout={'|'.join(lay)}:fill=0x1a0f2e[s];"
fc+=f"[s]pad=1080:ih:0:0:color=0x1a0f2e,crop=1080:1920:0:'min(t*25\,ih-1920)',lutrgb=r=val*0.62:g=val*0.62:b=val*0.66,format=yuv420p[o]"
subprocess.run([FF,'-nostdin','-loglevel','error','-y']+inputs+['-filter_complex',fc,'-map','[o]','-t',str(TOTAL),'-c:v','libx264','-crf','20','-preset','fast',V+f'gfx/mosaico_{VAR}.mp4'],check=True)
print('ok',len(clips))
