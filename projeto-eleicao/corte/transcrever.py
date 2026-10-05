"""Transcreve o bruto com tempo por palavra. Uso: python3 transcrever.py audio16k.wav saida.json"""
import sys, json
from faster_whisper import WhisperModel
m = WhisperModel('medium', device='cpu', compute_type='int8')
seg, _ = m.transcribe(sys.argv[1], language='pt', word_timestamps=True, beam_size=5, condition_on_previous_text=False,
                      initial_prompt='Bolsonaro, Câmara, Senado, Bernard Crick, Jan-Werner Müller, Elon Musk, Joe Rogan, Mina Cikara, empatia, extrema direita.')
out = [{'ini': round(s.start, 2), 'fim': round(s.end, 2), 'texto': s.text.strip(), 'palavras': [(w.word.strip(), round(w.start, 2), round(w.end, 2)) for w in s.words]} for s in seg]
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
for s in out: print(f"[{s['ini']:6.1f}-{s['fim']:6.1f}] {s['texto']}")
