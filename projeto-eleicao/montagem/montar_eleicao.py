"""Montagem do vídeo da eleição (decupagem_v2). Apresentador com chroma sobre papel quadriculado, motion graphics do kit, vídeos de apoio e fotos do Commons.
Uso: python3 montar_eleicao.py saida.mp4 [escala]            render completo (escala 0.5 = 540x960)
     python3 montar_eleicao.py --quadros 12.5,40,88 pasta [escala]    quadros avulsos para conferência
Tempos das palavras: projeto-eleicao/transcricao.json (faster-whisper). Dados grandes ficam em ELEICAO_TRAB (padrão /home/user/trabalho)."""
import sys, os, json, shutil, subprocess
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pecas import *
from fundo import fundo

_pal = [(w.strip('.,?!:;"“”').lower(), a, b) for s in json.load(open(os.path.join(RAIZ, 'projeto-eleicao', 'transcricao.json'))) for w, a, b in s['palavras']]
def pal(txt, n=0):
    k = [i for i, p in enumerate(_pal) if p[0] == txt.lower()]; return _pal[k[n]]
def ini(txt, n=0): return pal(txt, n)[1]
def fim(txt, n=0): return pal(txt, n)[2]
DUR = 191.6
SEM_AP = os.environ.get('SEM_APRESENTADOR') == '1'      # só o fundo com as peças, sem a figura (para sobrepor depois)

def foto(nome, h=460, maxw=800):
    im = Image.open(os.path.join(FOTOS, nome + ('.png' if os.path.exists(os.path.join(FOTOS, nome + '.png')) else '.jpg'))).convert('RGBA'); im.thumbnail((maxw, h), Image.LANCZOS); return im
def F(nome, t_in, t_out, cx=W / 2, cy=CARD_CY, rot=-2.5, fase=0.0, h=460, maxw=800):
    if not any(os.path.exists(os.path.join(FOTOS, nome + e)) for e in ('.jpg', '.png')): return None
    return Foto(foto(nome, h, maxw), t_in, max(0.2, t_out - t_in - 1.0), cx, cy, h, rot, fase)
def T(texto, entra, sai, cy=215, **kw): return TituloAbs(texto, None, cy=cy, entra=entra, sai=sai, **kw)
def recorte(path, h):
    im = Image.open(path).convert('RGBA'); im.thumbnail((h * 2, h), Image.LANCZOS); return recorte_jornal(im, seed=4)

def montar():
    fundo_pecas = []; frente = []; add = fundo_pecas.append
    # ---- 1 abertura
    add(CartaoVideo('cama', 0.0, 7.0, fase=0.3, rot=-2.0)); add(Etiqueta('1º turno', 0.4, 3.8, 250, 345, tam=58, rot=-5, fase=1.2))
    add(F('camara', 7.1, 11.0, fase=0.5, rot=-3)); add(F('constituicao', 10.9, 15.1, fase=1.5, rot=2.5))
    add(T('121', 7.1, 15.0, cy=205, teto1=160)); add(Etiqueta('deputados federais', 8.1, 15.0, 540, 395, tam=50, rot=-2, fase=2.0))
    add(Barra(15.1, 15.9, 17.1)); add(T('+22', 15.1, 17.1, cy=205, teto1=160))
    add(F('senado', 17.2, 19.8, fase=2.1, rot=-2)); add(Grade81(19.8, 22.4, 20.5, 21.7)); add(T('28 de 81', 17.3, 22.4, cy=205))
    add(F('urna', 22.5, 25.2, fase=3.0, rot=2.5, h=420)); add(T('contra as pesquisas', 22.6, 27.1, cy=205))
    add(Descarte(tira_texto('pesquisas', 120, seed=2), 25.0, 26.2, W / 2, 560, rot=-3, lado=1, nome='papel pesquisas'))
    add(CartaoVideo('catedral', 27.2, 37.2, fase=0.8, rot=1.5)); add(T('onde se fazem as leis', 27.3, 31.9, cy=215))
    # ---- 2 a tese
    add(T('“usar a política para romper com a política”', 32.1, 37.1, cy=215))
    ur = adesivo((300, 340), f_urna, (240, 232, 214), 3, detalhe=d_urna); mt = adesivo((340, 300), f_martelo, (240, 232, 214), 4, detalhe=d_martelo)
    ca = recorte(os.path.join(RAIZ, 'motion-graphics', 'assets', 'recortes', 'folha2_3.png'), 330)
    add(Cutout(ur, 37.4, 40.4, 270, 575, rot=-5, fase=0.4, nome='urna')); add(Cutout(ca, 38.3, 40.4, 540, 575, rot=3, fase=1.4, nome='cadeira')); add(Cutout(mt, 39.2, 40.4, 810, 575, rot=-4, fase=2.4, nome='martelo'))
    add(Descarte(tira_texto('política', 110, seed=8), 40.6, 43.4, 540, 440, rot=-3, lado=1, fase=0.7, nome='política')); add(Descarte(tira_texto('democracia', 110, seed=9), 41.5, 43.8, 540, 650, rot=2.5, lado=-1, fase=1.9, nome='democracia'))
    add(Logo(44.9, 47.7, cy=570, d=500, modo='joga')); add(CartaoVideo('escritorio', 47.6, 52.2, fase=1.1, rot=-2.5)); add(T('vergonha da própria empatia', 48.8, 52.1, cy=215))
    # ---- 3 o que é política
    add(T('O que é política?', 52.3, 59.9, cy=215)); add(CartaoVideo('livro', 55.0, 59.9, fase=0.9, rot=2.0))
    add(T('“a forma pacífica de lidar com interesses diferentes”', 60.1, 68.7, cy=215))
    add(CartaoVideo('cruzamento', 68.8, 72.2, fase=0.2, rot=-1.5)); add(CartaoVideo('multidao', 72.0, 75.6, fase=1.6, rot=2.0)); add(T('Você é gente', 72.7, 75.5, cy=215))
    # ---- 4 Müller
    add(Logo(75.7, 80.3, cy=570, d=500)); add(T('o povo verdadeiro', 80.4, 83.3, cy=215))
    for txt, w_, cy_, rt, sd in (('INIMIGO', 'inimigo', 330, -6, 1), ('TRAIDOR', 'traidor', 500, 4, 2), ('PARASITA', 'parasita', 670, -3, 3)): frente.append(Carimbo(txt, ini(w_), 85.6, 540, cy_, rt, tam=130, seed=sd))
    ap = aperto_de_mao(); add(Rasga(ap, 85.7, 87.5, 540, 560, rot=-2, fase=0.6, nome='aperto de mão'))
    # ---- 5 Musk
    mk = F('musk', 88.5, 92.3, 400, 570, rot=-4, fase=0.2, h=500, maxw=420); add(mk)
    add(Cutout(adesivo((160, 340), f_mic, (240, 232, 214), 6, detalhe=d_mic), 89.2, 92.2, 720, 600, rot=12, fase=1.0, nome='microfone adesivo'))
    add(CartaoVideo('microfone', 92.3, 95.4, fase=0.7, rot=-2.0)); add(T('“a fraqueza fundamental da civilização ocidental é a empatia”', 95.3, 100.5, cy=215))
    add(F('musk', 95.5, 100.6, 300, 600, rot=-3, fase=0.5, h=470, maxw=400)); add(F('rogan', 95.9, 100.6, 790, 600, rot=3, fase=1.5, h=470, maxw=330))
    add(T('empatia suicida', 100.5, 109.8, cy=215, teto1=170))
    add(CartaoVideo('maternidade', 109.9, 113.1, fase=0.4, rot=-2.0)); add(CartaoVideo('enfermaria', 113.1, 120.8, fase=1.3, rot=2.0))
    frente.append(Carimbo('AMEAÇA À CIVILIZAÇÃO', ini('deixar'), 120.8, 540, 480, -4, tam=62, seed=5))
    # ---- 6 a música brasileira
    add(Logo(120.9, 124.8, cy=570, d=500)); add(T('“Direitos humanos para humanos direitos.”', 124.7, 128.55, cy=205)); add(T('“Bandido bom é bandido morto.”', 126.8, 128.55, cy=280))
    add(Logo(128.7, 133.7, cy=570, d=500)); add(T('morte', 135.4, 136.9, cy=215, teto1=170))
    # ---- 7 a ciência
    add(T('A ciência', 136.9, 139.6, cy=215)); add(Cutout(recorte(os.path.join(RAIZ, 'motion-graphics', 'episodio-teste', 'fotos', 'cerebro.png'), 400), 137.0, 139.6, 540, 570, rot=-3, fase=0.5, nome='cérebro'))
    ch = coracao(11.0); add(Cutout(ch.rotate(26, resample=Image.BICUBIC, expand=True), 139.6, 141.5, 540, 575, rot=0, fase=0.2, nome='coração torto', balanca=3.0)); add(T('já nasce torta', 139.6, 141.4, cy=215))
    add(T('lacuna de empatia entre grupos', 141.3, 146.6, cy=215))
    add(Circulos(146.7, 158.0, ini('prazer'))); add(T('prazer com a dor do outro', ini('prazer') - 0.2, 158.0, cy=215))
    add(T('“não pode participar do processo democrático”', 158.0, 165.1, cy=215))
    # ---- 8 fecho
    add(Cutout(texto_recorte('?', 520, AMARELO, 4), 165.2, 167.0, 540, 570, rot=-6, fase=0.7, nome='interrogação')); add(T('um limite', 166.9, 172.6, cy=205, teto1=120))
    add(Cutout(calendario(), 167.1, 172.6, 540, 575, rot=-3, fase=1.1, nome='calendário')); add(Marcador(167.9, 172.6, y=745))
    add(Cutout(fila_de_bonecos(), 172.7, 175.9, 540, 560, rot=-1.5, fase=0.3, nome='bonecos')); add(T('Todo mundo é gente', 172.6, 175.9, cy=215, teto1=200))
    add(F('congresso', 176.1, 182.2, fase=2.2, rot=-2)); add(Foto(Image.open(os.path.join(RAIZ, 'motion-graphics', 'episodio-teste', 'fotos', 'prancheta.png')).convert('RGBA'), 182.3, 1.8, W / 2, CARD_CY, 420, 3, 0.4))
    add(T('“a fraqueza fundamental da civilização ocidental é a empatia”', 185.2, 188.9, cy=215, x_abs=(186.9, 187.7)))
    add(Logo(189.0, 191.7, cy=570, d=500))
    zooms = [(52.2, 55.0), (60.3, 64.3), (80.6, 83.3), (133.8, 136.8), (141.5, 146.5), (158.2, 163.7), (185.4, 188.8)]
    return [p for p in fundo_pecas if p is not None], frente, zooms

_fundo = None; _cena = None; _frente = None; _ap = None
def _init():
    global _fundo, _cena, _frente, _ap
    _fundo = fundo(W, H).convert('RGBA'); _cena, _frente, z = montar(); _ap = Apresentador(z)

def quadro(k, escala, pasta):
    t = k / FPS; fr = _fundo.copy()
    for c in _cena: c.draw(fr, t)
    if not SEM_AP: _ap.draw(fr, t)
    for c in _frente: c.draw(fr, t)
    if escala != 1.0: fr = fr.resize((int(W * escala), int(H * escala)), Image.LANCZOS)
    fr.convert('RGB').save(os.path.join(pasta, f'f{k:05d}.jpg'), quality=95 if SEM_AP else 92)
def _job(a): return quadro(*a)

def mixar_voz(eventos, saida, dur):
    """voz do bruto e som de papel nas tiras de título (mesmo critério do kit: só nos títulos)"""
    import mixar_audio as MA
    SR = MA.SR; n = int(dur * SR); v = MA._ler(os.path.join(TRAB, 'voz.wav'), 2); voz = np.zeros((n, 2), np.float32); voz[:min(n, len(v))] = v[:n]
    p = MA._ler(MA.ARQ_PAPEL, 2); abre = MA._segmento(p, 0.56, 1.16); fecha = MA._segmento(p, 1.20, 1.75); rng = np.random.RandomState(5); sfx = np.zeros((n, 2), np.float32)
    for t, tipo in eventos:
        y = (abre if tipo == 'abre' else fecha) * 10 ** (rng.uniform(-1.5, 1.0) / 20); i = int(t * SR)
        if 0 <= i < n: m = min(len(y), n - i); sfx[i:i + m] += y[:m]
    out = np.clip(voz + sfx * 0.9, -1, 1)
    import wave
    with wave.open(saida, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())
    return saida

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; flags = [a for a in sys.argv[1:] if a.startswith('--')]
    preparar_videos()
    if '--quadros' in flags:
        ks = [int(float(x) * FPS) for x in args[0].split(',')]; pasta = args[1]; escala = float(args[2]) if len(args) > 2 else 0.5; os.makedirs(pasta, exist_ok=True)
        with Pool(4, initializer=_init) as p: p.map(_job, [(k, escala, pasta) for k in ks]); sys.exit()
    saida = args[0]; escala = float(args[1]) if len(args) > 1 else 0.5; pasta = os.path.join(TRAB, 'quadros'); shutil.rmtree(pasta, ignore_errors=True); os.makedirs(pasta)
    N = int(DUR * FPS)
    with Pool(4, initializer=_init) as p:
        for i, _ in enumerate(p.imap_unordered(_job, [(k, escala, pasta) for k in range(N)], chunksize=4)):
            if i % 300 == 0: print(i, '/', N, flush=True)
    if SEM_AP:
        subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(pasta, 'f%05d.jpg'), '-t', str(DUR), '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-an', saida], check=True)
        shutil.rmtree(pasta); print('ok', saida); sys.exit()
    if not os.path.exists(os.path.join(TRAB, 'voz.wav')): subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-i', '/home/user/bruto/brutoempatia.mp4', '-vn', '-ac', '2', '-ar', '44100', os.path.join(TRAB, 'voz.wav')], check=True)
    cena = montar()[0]; ev = sorted(e for c in cena if isinstance(c, TituloAbs) for e in c.sons() if e[0] < DUR - 0.3)
    audio = mixar_voz(ev, os.path.join(TRAB, 'audio_final.wav'), DUR)
    subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(pasta, 'f%05d.jpg'), '-i', audio, '-t', str(DUR), '-c:v', 'libx264', '-preset', 'medium', '-crf', '24', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', saida], check=True)
    shutil.rmtree(pasta); print('ok', saida)
