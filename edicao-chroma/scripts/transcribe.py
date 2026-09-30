import os
from faster_whisper import WhisperModel
import json
m=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=4)
segs,info=m.transcribe('audio16k.wav',language='pt',word_timestamps=True,vad_filter=False,beam_size=5,initial_prompt='Nada Errado com VC. Globo, Band, Abril, Folha.')
out=[]
for s in segs:
    out.append({'start':s.start,'end':s.end,'text':s.text,'words':[{'w':w.word,'s':w.start,'e':w.end,'p':w.probability} for w in s.words]})
    print(f'[{s.start:7.2f} - {s.end:7.2f}] {s.text}',flush=True)
json.dump(out,open('transcricao.json','w'),ensure_ascii=False,indent=1)
