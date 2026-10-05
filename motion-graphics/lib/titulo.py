"""Título na tela: frase destacada numa tira de papel rasgado, em EB Garamond itálico, com marca-texto passando
em cima conforme a fala.

    t = Titulo('Lorem ipsum dolor', tempos=None)      # tempos: lista de (inicio, fim) por palavra, em segundos
    t.quadro(seg)                                      # RGBA do tamanho do canvas, seg = segundos desde a entrada
    t.duracao                                          # entrada + leitura + saída

Entradas: 'desdobra' (padrão: entra como quadrado dobrado e se abre para os lados, saída inversa), 'lateral' (desliza da esquerda), 'z' (vem de trás para a frente), 'rasgo' (a tira aparece sendo rasgada)."""
import os, math
import numpy as np
from bola import BolaPapel, Peca, dobra as _dobra, _ap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTE = os.environ.get('FONTE_GARAMOND_ITALICO') or os.path.join(AQUI, '..', 'fonts', 'EBGaramond-Italic.ttf')
if not os.path.exists(FONTE): FONTE = '/root/.fonts/EBGaramond-Italic[wght].ttf'
TINTA = (36, 30, 26, 255)
CANVAS = (1080, 1920)


def _fonte(tam, peso=520):
    f = ImageFont.truetype(FONTE, tam)
    try: f.set_variation_by_axes([peso])
    except Exception: pass
    return f


def _ease_out(u): u = max(0.0, min(1.0, u)); return 1 - (1 - u) ** 3
def _ease_in(u): u = max(0.0, min(1.0, u)); return u ** 2.2
def _back(u):
    u = max(0.0, min(1.0, u)); c1 = 1.5; c3 = c1 + 1
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2


def _borda(n, amp, seed, escalas=((140, 1.0), (40, 0.6), (11, 0.25), (3, 0.1))):
    """curva irregular de rasgo: soma de ruídos em várias escalas + 'lascas' ocasionais"""
    r = np.random.RandomState(seed); y = np.zeros(n)
    for per, k in escalas:
        pts = r.randn(n // per + 3)
        y += np.interp(np.arange(n), np.arange(len(pts)) * per, pts) * amp * k
    for _ in range(max(1, n // 260)):
        c = r.randint(0, n); w = r.randint(8, 26)
        y[max(0, c - w):c + w] += r.uniform(-1, 1) * amp * 1.8 * np.hanning(len(y[max(0, c - w):c + w]))
    return y


def _quebra(palavras, n_linhas):
    if n_linhas == 1: return [' '.join(palavras)]
    melhor = None
    for k in range(1, len(palavras)):
        l1, l2 = ' '.join(palavras[:k]), ' '.join(palavras[k:])
        sc = abs(len(l1) - len(l2))
        if melhor is None or sc < melhor[0]: melhor = (sc, [l1, l2])
    return melhor[1]



class TiraDobravel(BolaPapel):
    """mesmas dobras reais da bola de papel, mas a tira só se dobra até virar um quadradinho (não vira bola).
    quadro(c): c = 0 tira aberta ... c = 1 quadradinho dobrado, centralizado."""
    def __init__(self, img, seed=3):
        super().__init__(img, 'A', seed)
        r = np.random.RandomState(seed + 11)
        est = [self.estados[0]]; self.dobras = []
        def caixa(pilha):
            v = np.concatenate([_ap(p.M, p.poly) for p in pilha]); return v[:, 0].min(), v[:, 0].max(), v[:, 1].min(), v[:, 1].max()
        alvo = self.H * 0.5 * 1.3
        seq = []
        x0, x1, y0, y1 = caixa(est[0])
        for _ in range(8):
            if (x1 - x0) <= alvo: break
            a = r.uniform(-0.10, 0.10); n = np.array([math.cos(a), math.sin(a)])
            xm = x0 + (x1 - x0) * r.uniform(0.47, 0.53); d = float(n @ np.array([xm, (y0 + y1) / 2]))
            est.append(_dobra(est[-1], n, d)); self.dobras.append((n, d)); x0, x1, y0, y1 = caixa(est[-1])
        for hor in (True,):
            a = r.uniform(-0.10, 0.10)
            n = np.array([-math.sin(a), math.cos(a)]) if hor else np.array([math.cos(a), math.sin(a)])
            m = np.array([(x0 + x1) / 2, (y0 + y1) / 2]); d = float(n @ m)
            est.append(_dobra(est[-1], n, d)); self.dobras.append((n, d)); x0, x1, y0, y1 = caixa(est[-1])
        self.estados = est; self.N = len(self.dobras)

    def quadro(self, c):
        c = max(0.0, min(1.0, c))
        if c <= 1e-4: return self.img.copy()
        u = c * self.N; i = min(self.N - 1, int(u)); p = u - i
        if c >= 1.0: out = self._desenha(self.estados[self.N])
        else:
            pe = p * p * (3 - 2 * p); n, d = self.dobras[i]
            ang = math.pi * pe
            # perto de planificar, o vinco da primeira dobra some (senão fica uma linha escura no meio da tira)
            vinco = 1.0 if i > 0 else float(np.clip(ang / 1.2, 0, 1) ** 2 * (3 - 2 * np.clip(ang / 1.2, 0, 1)))
            out = self._desenha(_dobra(self.estados[i], n, d, ang=ang), vinco=vinco)
        out = self._organico(out, c, 2.0)
        k = c ** 1.2
        sh = 1 + k * (0.030 * np.clip(self.F, -1.5, 1.5) - 0.055 * self.B)
        out[..., :3] *= sh[..., None]
        im = Image.fromarray(np.dstack([np.clip(out[..., :3], 0, 255), np.clip(out[..., 3], 0, 1) * 255]).astype(np.uint8), 'RGBA')
        al = np.array(im.getchannel('A')) > 40
        ys, xs = np.nonzero(al)
        if len(ys):
            dx = self.cx - (xs.min() + xs.max()) / 2; dy = self.cy - (ys.min() + ys.max()) / 2
            im = im.transform(im.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR)
        return im


class Titulo:
    def __init__(self, texto, tempos=None, entrada='dobra', cy=560, rot=-1.6, largura_max=960, seed=3, vel=2.6, cor_marca=(255, 226, 0), credito=None, ficar=0.9, teto1=200, x_tempos=None, varredura=False, vel_px=800.0):
        self.palavras = texto.split(); self.entrada = entrada; self.cy = cy; self.rot = rot
        self.cor_marca = cor_marca; n = len(self.palavras)
        self.n_linhas = 1 if n <= 3 else 2
        self.linhas = _quebra(self.palavras, self.n_linhas)
        d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        teto = teto1 if self.n_linhas == 1 else 130
        tam = teto
        while True:
            f = _fonte(tam)
            larg = max(d.textlength(l, font=f) for l in self.linhas)
            if larg + 2 * (0.55 * tam + 20) <= largura_max or tam <= 40: break
            tam -= 2
        self.tam = tam; self.f = f
        self.lh = int(tam * 1.10)
        self.padx = int(0.55 * tam) + 20; self.pady = int(0.42 * tam) + 12
        self.w = int(larg + 2 * self.padx); self.h = int(self.lh * self.n_linhas + 2 * self.pady)
        self.credito = credito; self.cred_h = (int(0.58 * tam) + 8) if credito else 0
        self.h += self.cred_h
        self.seed = seed
        self._faixa()
        self._palavras_pos(d)
        # tempos de cada palavra (início, fim)
        self.varr = None
        if tempos is None and varredura: self.tempos = self._varredura(vel_px)       # a caneta passa uma vez, em velocidade constante, logo depois da tira abrir
        elif tempos is None:
            t0 = 0.85 if self.entrada == 'dobra' else (1.05 if self.entrada == 'desdobra' else 0.70); self.tempos = [(t0 + i / vel, t0 + (i + 0.92) / vel) for i in range(n)]
        else: self.tempos = tempos
        self.dur_entrada, self.dur_saida = {'dobra': (0.70, 0.60), 'desdobra': (1.0, 0.9)}.get(self.entrada, (0.55, 0.45)); self._folds = {}
        self.t_fim = self.tempos[-1][1]; self.ficar = ficar; self.x_tempos = x_tempos
        self.duracao = self.t_fim + ficar + self.dur_saida

    # ------------------------------------------------------------ a tira de papel rasgado
    def _faixa(self):
        pad = 40; W, H = self.w + 2 * pad, self.h + 2 * pad
        r = np.random.RandomState(self.seed)
        def contorno(inset, sd):
            top = pad + inset + _borda(self.w, 7, sd) + 8
            bot = pad + self.h - inset - 8 + _borda(self.w, 7, sd + 1)
            esq = pad + inset + _borda(self.h, 6, sd + 2) + 6
            dir_ = pad + self.w - inset - 6 + _borda(self.h, 6, sd + 3)
            pts = [(pad + i, top[i]) for i in range(0, self.w, 2)]
            pts += [(dir_[j], pad + j) for j in range(0, self.h, 2)]
            pts += [(pad + self.w - i, bot[self.w - 1 - i]) for i in range(0, self.w, 2)]
            pts += [(esq[self.h - 1 - j], pad + self.h - j) for j in range(0, self.h, 2)]
            m = Image.new('L', (W * 2, H * 2), 0); ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
            return np.array(m.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
        ext = contorno(0, 11); inte = contorno(7, 31)         # miolo branco fibroso por fora, papel colorido por dentro
        gr = r.randn(H, W)
        fibra = ndi.gaussian_filter(r.rand(H, W), 1.2) - 0.5
        papel = np.array([249, 245, 233], np.float32)
        base = papel[None, None, :] + (gr * 2.2 + fibra * 14)[..., None]
        grad = np.linspace(1.012, 0.985, H)[:, None, None]
        base = base * grad
        miolo = np.array([255, 254, 250], np.float32)[None, None, :] + (gr * 1.6)[..., None]
        rgb = miolo * (1 - inte[..., None]) + base * inte[..., None]
        rgba = np.dstack([np.clip(rgb, 0, 255), ext * 255]).astype(np.uint8)
        self.base = Image.fromarray(rgba, 'RGBA'); self.pad = pad

    def _palavras_pos(self, d):
        """(linha, x inicial, x final) de cada palavra, em pixels da tira"""
        self.pos = []
        for li, l in enumerate(self.linhas):
            larg = d.textlength(l, font=self.f); x0 = (self.w - larg) / 2; cur = ''
            for pal in l.split():
                ini = x0 + d.textlength(cur + (' ' if cur else ''), font=self.f)
                cur = (cur + ' ' + pal).strip()
                self.pos.append((li, ini, x0 + d.textlength(cur, font=self.f)))

    def _varredura(self, v):
        """passada única da caneta: velocidade constante em pixels por segundo, as linhas em sequência, sem pausa. Devolve (inicio, fim) geral."""
        lens = []; offs = []; acc = 0.0
        for li in range(self.n_linhas):
            ps = [p for p in self.pos if p[0] == li]; lens.append(ps[-1][2] - ps[0][1]); offs.append(acc); acc += lens[-1]
        t_ini = 0.85; self.varr = (t_ini, v, offs, lens)
        return [(t_ini, t_ini + acc / v)]

    # ------------------------------------------------------------ o texto e a marca-texto
    def _conteudo(self, t_leitura):
        """camada com o marca-texto (multiplicado sobre o papel) e o texto por cima, no tamanho da tira"""
        pad = self.pad; W, H = self.w + 2 * pad, self.h + 2 * pad
        S = self.tam
        # marca-texto
        mt = np.ones((H, W, 3), np.float32)
        if t_leitura > self.tempos[0][0]:
            r = np.random.RandomState(self.seed + 5)
            for li in range(self.n_linhas):
                idx = [i for i, p in enumerate(self.pos) if p[0] == li]
                x_ini = self.pos[idx[0]][1]
                # avanço da caneta nesta linha
                xp = x_ini
                if self.varr:                                   # passada única: a ponta avança sem parar, na mesma velocidade, de uma linha para a outra
                    t_ini, v, offs, lens = self.varr
                    xp = x_ini + min(lens[li], max(0.0, v * (t_leitura - t_ini) - offs[li]))
                else:
                    for i in idx:
                        _, a, b = self.pos[i]; t0, t1 = self.tempos[i]
                        if t_leitura >= t1: xp = b
                        elif t_leitura > t0: xp = a + (b - a) * ((t_leitura - t0) / (t1 - t0)); break
                        else: break
                if xp <= x_ini + 2: continue
                base_y = pad + self.pady + li * self.lh + S * 0.88
                y0 = base_y - 0.60 * S; y1 = base_y + 0.14 * S
                xa = pad + x_ini - 0.10 * S; xb = pad + xp + 0.06 * S
                m = Image.new('L', (W * 2, H * 2), 0); dm = ImageDraw.Draw(m)
                wob = lambda n: [r.uniform(-1.6, 1.6) for _ in range(n)]
                w1 = wob(4)
                # corpo da faixa com ponta "chanfrada" (caneta de ponta chata)
                dm.polygon([((xa + w1[0]) * 2, (y0 + w1[1]) * 2), ((xb + 0.05 * S) * 2, (y0 + 0.05 * S + w1[2]) * 2),
                            ((xb - 0.03 * S) * 2, (y1 + w1[3]) * 2), ((xa - 0.04 * S) * 2, (y1 + 0.02 * S) * 2)], fill=255)
                mm = np.array(m.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
                tex = ndi.gaussian_filter(r.rand(H, W), 1.0) - 0.5
                rim = mm - ndi.grey_erosion(mm, size=(5, 5))
                a_ = np.clip(mm * (0.80 + 0.30 * tex) + 0.18 * rim, 0, 1)
                cor = np.array(self.cor_marca, np.float32) / 255
                mt *= (1 - a_[..., None] * (1 - cor[None, None, :]))            # multiplicação: o texto continua escuro
        arr = np.array(self.base).astype(np.float32)
        arr[..., :3] *= mt
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
        d = ImageDraw.Draw(im)
        for li, l in enumerate(self.linhas):
            larg = d.textlength(l, font=self.f)
            d.text((pad + (self.w - larg) / 2, pad + self.pady + li * self.lh - 0.02 * S), l, font=self.f, fill=TINTA)
        if self.credito:
            fc = _fonte(max(24, int(0.42 * S)), 480); lc = d.textlength(self.credito, font=fc)
            d.text((pad + (self.w - lc) / 2, pad + self.pady + self.n_linhas * self.lh + 0.02 * S), self.credito, font=fc, fill=(110, 96, 80, 255))
        if self.x_tempos:                                                   # X de marca-texto vermelho por cima da tira inteira
            from marcador import riscar_x
            im = riscar_x(im, (t_leitura - self.x_tempos[0]) / (self.x_tempos[1] - self.x_tempos[0]), caixa=(pad, pad, pad + self.w, pad + self.h), margem=0.05)
        return im


    # ------------------------------------------------------------ desdobrar (sanfona)
    def _sanfona(self, im, c):
        """tira dobrada em sanfona vista de cima: largura projetada = c * largura aberta (c=1 aberta)"""
        Wi, Hi = im.size; K = max(2, round(Wi / Hi)); pw = Wi / K
        Wo = max(2, int(Wi * c)); sen = math.sqrt(max(0.0, 1 - c * c))
        out = im.resize((Wo, Hi), Image.LANCZOS)
        a = np.array(out).astype(np.float32)
        s = ((np.arange(Wo) + 0.5) / Wo * Wi / pw); i = np.floor(s).astype(int); f = s - i
        par = (i % 2 == 0)
        esc = np.where(par, f, 1 - f)                                  # 0 na crista, 1 no vale
        sh = 1 - sen * (0.10 + 0.34 * esc ** 1.6)
        a[..., :3] *= sh[None, :, None]
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')

    # ------------------------------------------------------------ quadro
    def quadro(self, t, canvas=CANVAS):
        W, H = canvas
        tl = t - self.dur_entrada                        # tempo de leitura (0 quando a entrada termina)
        sair = t - (self.t_fim + self.ficar)
        im = self._conteudo(t)
        # --- entrada e saída
        if t < self.dur_entrada: p = t / self.dur_entrada; saindo = False
        elif sair > 0: p = 1 - min(1.0, sair / self.dur_saida); saindo = True
        else: p = 1.0; saindo = False
        if sair >= self.dur_saida: return Image.new('RGBA', canvas, (0, 0, 0, 0))
        e = _ease_in(1 - p) if saindo else None
        dx = dy = 0.0; sc = 1.0; rot = self.rot; sombra_k = 1.0
        if self.entrada == 'lateral':
            dist = W / 2 + self.w / 2 + 60
            if not saindo:
                dx = -dist * (1 - _back(p)); rot = self.rot - 5 * (1 - _back(p))
            else:
                q = _ease_in(1 - p); dx = dist * q; rot = self.rot + 4 * q
        elif self.entrada == 'z':
            q = _back(p) if not saindo else _ease_out(p)
            sc = 0.30 + 0.70 * q if not saindo else 0.30 + 0.70 * _ease_out(p)
            rot = self.rot + (1 - min(1, p)) * (6 if not saindo else -6)
            sombra_k = 0.25 + 0.75 * min(1.0, sc)
        elif self.entrada == 'dobra':
            tt = max(0.0, min(1.0, t / self.dur_entrada if not saindo else 1 - sair / self.dur_saida))
            if tt < 1.0:
                chave = 's' if saindo else 'e'
                if chave not in self._folds: self._folds[chave] = TiraDobravel(self._conteudo(self.t_fim + max(1.0, self.ficar) if saindo else 0.0), self.seed)
                if saindo:
                    c = _ease_in(1 - tt) if False else (1 - tt) ** 1.0
                else: c = 1 - tt
                c = c * c * (3 - 2 * c) if 0 < c < 1 else c
                im = self._folds[chave].quadro(c)
                # o quadradinho chega e vai embora como se fosse jogado/recolhido sobre a mesa
                borda = 0.14
                if not saindo and tt < borda: sc = 0.35 + 0.65 * _back(tt / borda)
                if saindo and tt < borda: sc = 0.35 + 0.65 * _ease_out(tt / borda)
        elif self.entrada == 'desdobra':
            Wi, Hi = im.size; c0 = min(1.0, Hi / Wi)
            def ease_io(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
            if not saindo: tt = t / self.dur_entrada
            else: tt = 1 - sair / self.dur_saida
            tt = max(0.0, min(1.0, tt))
            desl = 1 - _ease_out(tt / 0.42)                              # 1 fora da tela, 0 no centro
            aber = ease_io((tt - 0.38) / 0.62) if not saindo else ease_io((tt - 0.38) / 0.62)
            c = c0 + (1 - c0) * aber
            if c < 0.999: im = self._sanfona(im, c)
            dist = W / 2 + Hi / 2 + 60
            dx = -dist * desl
            rot = self.rot - 6 * desl
        elif self.entrada == 'rasgo':
            pass
        from animfoto import sombra_papel, balanco
        if self.entrada == 'rasgo' and p < 1.0:
            # a tira é revelada por uma borda rasgada que avança da esquerda para a direita
            w, h = im.size; r = np.random.RandomState(self.seed + 9)
            x = (w + 80) * (_ease_out(p) if not saindo else _ease_out(p))
            borda = _borda(h, 14, self.seed + 21) * 1.0
            xs = np.arange(w)[None, :]
            lim = x - 40 + borda[:, None]
            mask = np.clip(lim - xs, 0, 1) if not saindo else np.clip(lim - xs, 0, 1)
            a = np.array(im.getchannel('A')).astype(np.float32) / 255 * mask
            im = im.copy(); im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        rot += balanco(t, self.seed, 1.0)
        if sc != 1.0: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
        if abs(rot) > 0.02: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
        im2 = sombra_papel(im, off=int(10 * sombra_k), blur=int(9 * sombra_k) + 1, op=0.30 * sombra_k + 0.05)
        out = Image.new('RGBA', canvas, (0, 0, 0, 0))
        out.alpha_composite(im2, (int(W / 2 - im2.width / 2 + dx), int(self.cy - im2.height / 2 + dy)))
        return out
