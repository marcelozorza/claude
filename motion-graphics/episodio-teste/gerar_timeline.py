"""Gera previa/timeline.json (faixas com início e fim de cada peça) e previa/episodio.mp4 (vídeo leve, saltos curtos entre quadros-chave)
para a página de linha do tempo. Uso: python3 episodio-teste/gerar_timeline.py   (depois de renderizar saida/episodio_preview.mp4)"""
import sys, os, json, time, subprocess, shutil
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import montar_episodio as m
NOMES = {'escova': 'escova de dentes', 'cafe': 'café', 'celular': 'celular', 'cerebro': 'cérebro', 'caminho': 'caminho com pegadas', 'prancheta': 'prancheta',
         'ampulheta': 'ampulheta', 'maquina': 'máquina de escrever', 'livro': 'livro', 'despertador': 'despertador', 'cronometro': 'cronômetro', 'revista': 'revista', 'ponte': 'ponte'}
cena, ap = m.montar(); D = m.DUR
def cl(a, b): return [round(max(0.0, a), 2), round(min(D, b), 2)]
fotos, titulos, anim, som = [], [], [], []
for c in cena:
    if isinstance(c, m.TituloAbs):
        a, b = cl(c.t0, c.t0 + c.t.duracao); titulos.append({'ini': a, 'fim': b, 'rotulo': c.t.palavras and ' '.join(c.t.palavras), 'fica': c.t0 + c.t.duracao > D})
    elif isinstance(c, m.Foto):
        a, b = cl(c.t0, c.t0 + 1.0 + c.hold); fotos.append({'ini': a, 'fim': b, 'rotulo': NOMES.get(c.nome, c.nome), 'fica': c.t0 + 1.0 + c.hold > D})
    elif isinstance(c, m.Neuronios):
        a, b = cl(c.t_cai[0], c.t_fold + 0.67); anim.append({'ini': a, 'fim': b, 'rotulo': 'neurônios e cordão'})
    elif isinstance(c, m.BarraSolo):
        a, b = cl(c.t_in - 0.15, c.t_sobe + 0.55); anim.append({'ini': a, 'fim': b, 'rotulo': 'barra 66, 18, 254 dias'})
for t, tipo in m.eventos_sfx(cena): som.append({'ini': round(t, 2), 'fim': round(t, 2), 'rotulo': 'papel ' + tipo})
zoom = [{'ini': round(a, 2), 'fim': round(b, 2), 'rotulo': 'zoom de 30%'} for a, b in ap.zooms]
trans = json.load(open(os.path.join(AQUI, 'transcricao_limpa.json')))
fala = [{'ini': s['ini'], 'fim': s['fim'], 'rotulo': s['texto']} for s in trans]
palavras = [[w, a, b] for s in trans for w, a, b in s['palavras']]
try: h = subprocess.run(['git', '-C', AQUI, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
except Exception: h = ''
tl = {'versao': time.strftime('%d/%m %H:%M') + (' · ' + h if h else ''), 'duracao': D, 'fps': m.FPS, 'aceleracao': 1.1,
      'faixas': [{'id': 'fala', 'nome': 'Fala', 'itens': fala}, {'id': 'titulos', 'nome': 'Títulos', 'itens': titulos}, {'id': 'fotos', 'nome': 'Fotos', 'itens': fotos},
                 {'id': 'anim', 'nome': 'Animações', 'itens': anim}, {'id': 'zoom', 'nome': 'Zoom', 'itens': zoom}, {'id': 'som', 'nome': 'Papel', 'itens': som}], 'palavras': palavras}
os.makedirs(os.path.join(AQUI, 'previa'), exist_ok=True)
json.dump(tl, open(os.path.join(AQUI, 'previa', 'timeline.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
FF = shutil.which('ffmpeg') or os.path.expanduser('~/bin/ffmpeg')
subprocess.run([FF, '-nostdin', '-loglevel', 'error', '-y', '-i', os.path.join(AQUI, 'saida', 'episodio_preview.mp4'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '27', '-g', '8', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', os.path.join(AQUI, 'previa', 'episodio.mp4')], check=True)
print('ok', tl['versao'], D, 's', {f['id']: len(f['itens']) for f in tl['faixas']}, os.path.getsize(os.path.join(AQUI, 'previa', 'episodio.mp4')) // 1024, 'KB')
