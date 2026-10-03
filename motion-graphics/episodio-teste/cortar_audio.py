"""Corta o áudio bruto: remove silêncios, erros e tomadas repetidas. Uso: python3 episodio-teste/cortar_audio.py <audio_bruto.mp3>
Gera audio_limpo.wav/.mp3 e cortes_audio.json. Os trechos descartados foram decididos ouvindo cada tomada (ver HANDOFF)."""
import sys, os, json, wave, subprocess, shutil
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); FF = shutil.which('ffmpeg') or os.path.expanduser('~/bin/ffmpeg')
bruto = sys.argv[1]; tmp = os.environ.get('EP_TMP2', '/tmp')
subprocess.run([FF, '-loglevel', 'error', '-y', '-i', bruto, '-ac', '1', '-ar', '44100', '-c:a', 'pcm_s16le', tmp + '/full.wav'], check=True)
w = wave.open(tmp + '/full.wav'); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
# trechos com fala: energia acima de -38 dB em janelas de 10 ms, lacunas menores que 0,25 s unidas
n = sr // 100; db = 20 * np.log10(np.sqrt((x[:len(x) // n * n].reshape(-1, n) ** 2).mean(1)) / 32768 + 1e-9); f = db > -38
runs = []; i = 0
while i < len(f):
    if f[i]:
        j = i
        while j < len(f) and f[j]: j += 1
        runs.append([i / 100, j / 100]); i = j
    else: i += 1
m = [runs[0]]
for a, b in runs[1:]:
    if a - m[-1][1] < 0.25: m[-1][1] = b
    else: m.append([a, b])
def ok(a, b):
    if b - a < 0.5 or b < 4.5: return False
    if 33.0 < a < 39.0: return False          # primeira tomada de "Na centésima" (refeita em 39,8)
    if 44.9 < a < 69.7: return False          # citação: tentativas erradas e "vou gravar tudo de novo"
    if 113.4 < a < 115.9: return False        # começo falso de "e cada repetição em graça" (refeito em 116,2)
    return True
seg = [r for r in m if ok(*r)]; mm = [seg[0]]
for a, b in seg[1:]:
    if a - mm[-1][1] < 0.45: mm[-1][1] = b
    else: mm.append([a, b])
pre, post = 0.12, 0.16; out = []; mapa = []; t = 0
for a, b in mm:
    a0 = max(0, a - pre); b0 = min(len(x) / sr, b + post); y = x[int(a0 * sr):int(b0 * sr)].copy(); f_ = int(0.012 * sr)
    y[:f_] *= np.linspace(0, 1, f_); y[-f_:] *= np.linspace(1, 0, f_)
    mapa.append({'orig': [round(a0, 2), round(b0, 2)], 'novo': [round(t, 2), round(t + len(y) / sr, 2)]}); out.append(y); t += len(y) / sr
y = np.concatenate(out); ww = wave.open(os.path.join(AQUI, 'audio_limpo.wav'), 'wb'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(sr)
ww.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes()); ww.close()
subprocess.run([FF, '-loglevel', 'error', '-y', '-i', os.path.join(AQUI, 'audio_limpo.wav'), '-c:a', 'libmp3lame', '-b:a', '192k', os.path.join(AQUI, 'audio_limpo.mp3')], check=True)
json.dump(mapa, open(os.path.join(AQUI, 'cortes_audio.json'), 'w'), indent=1); print(len(mm), 'trechos, duração', round(t, 1))
for k in mapa[-4:]: print(k['orig'], '->', k['novo'])
