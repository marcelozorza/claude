"""Animação de recorte que vira bola de papel (e o inverso), por dobras de verdade.

Ideia: a folha (foto + margem de papel) é uma pilha de pedaços convexos. Cada dobra corta a pilha por uma reta e gira
a parte de fora por cima do resto, em 180 graus. Na metade da dobra o pedaço fica em pé (encurta com o cosseno) e,
passando dos 90 graus, mostra o VERSO branco do papel. Depois de algumas dobras a foto some debaixo dos versos brancos
e o que sobra é arredondado e sombreado como uma bola.

    b = BolaPapel(imagem_rgba, modo='A')   # 'A' dobras de canto, 'B' espiral
    b.quadro(c)                              # c = 0 aberto ... c = 1 bola fechada
Para a entrada use o tempo invertido (c de 1 até 0)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

PAPEL = np.array([247, 242, 232], np.float32)


def _ap(M, P):
    P = np.asarray(P, np.float64)
    return P @ M[:2, :2].T + M[:2, 2]


def _area(P):
    P = np.asarray(P); x, y = P[:, 0], P[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _corta(P, n, d):
    """divide o polígono convexo P pela reta n.q = d. Devolve (lado n.q<=d, lado n.q>=d)."""
    keep, fold = [], []
    m = len(P)
    for i in range(m):
        a, b = P[i], P[(i + 1) % m]
        da, db = n @ a - d, n @ b - d
        if da <= 0: keep.append(a)
        if da >= 0: fold.append(a)
        if da * db < 0:
            t = da / (da - db); ip = a + (b - a) * t
            keep.append(ip); fold.append(ip)
    ok = lambda L: np.array(L) if len(L) >= 3 and _area(np.array(L)) > 25 else None
    return ok(keep), ok(fold)


class Peca:
    __slots__ = ('poly', 'M', 'verso', 'luz')
    def __init__(s, poly, M, verso, luz=1.0): s.poly, s.M, s.verso, s.luz = poly, M, verso, luz


def _refl(n, d):
    nx, ny = n
    return np.array([[1 - 2 * nx * nx, -2 * nx * ny, 2 * d * nx], [-2 * nx * ny, 1 - 2 * ny * ny, 2 * d * ny], [0, 0, 1]])


def _giro(n, d, c):
    """projeção de um pedaço girado de um ângulo cujo cosseno é c, em torno da reta n.q = d"""
    nx, ny = n; k = 1 - c
    return np.array([[1 - k * nx * nx, -k * nx * ny, k * d * nx], [-k * nx * ny, 1 - k * ny * ny, k * d * ny], [0, 0, 1]])


def dobra(pilha, n, d, ang=None, luz_fixa=None):
    """aplica uma dobra na pilha. ang=None dobra completa (180 graus). Senão ang em radianos (0..pi)."""
    keeps, folds = [], []
    c = -1.0 if ang is None else math.cos(ang)
    Mt = _refl(n, d) if ang is None else _giro(n, d, c)
    for pc in pilha:
        Pc = _ap(pc.M, pc.poly)
        k, f = _corta(Pc, n, d)
        Mi = np.linalg.inv(pc.M)
        if k is not None: keeps.append(Peca(_ap(Mi, k), pc.M, pc.verso, pc.luz))
        if f is not None:
            verso = (not pc.verso) if c < 0 else pc.verso
            luz = pc.luz
            if ang is not None: luz = pc.luz * (0.74 + 0.26 * abs(c))
            folds.append(Peca(_ap(Mi, f), Mt @ pc.M, verso, luz))
    return keeps + folds[::-1]


def _extensao(pilha, n, centro):
    v = np.concatenate([_ap(p.M, p.poly) for p in pilha])
    return float(((v - centro) @ n).max())


class BolaPapel:
    def __init__(self, img, modo='A', seed=3):
        self.img = img.convert('RGBA')
        self.W, self.H = self.img.size
        self.tex = np.array(self.img).astype(np.float32)
        self.cx, self.cy = self.W / 2, self.H / 2
        rng = np.random.RandomState(seed)
        c = np.array([self.cx, self.cy])
        base = [Peca(np.array([[0, 0], [self.W, 0], [self.W, self.H], [0, self.H]], np.float64), np.eye(3), False)]
        self.estados = [base]; self.dobras = []
        R = max(self.W, self.H) / 2
        if modo == 'A':
            alvos = [0.64, 0.58, 0.52, 0.47, 0.42, 0.37, 0.32, 0.27, 0.22]; passo = 2.4; jit = 0.30
        else:
            alvos = [0.68, 0.62, 0.56, 0.51, 0.46, 0.41, 0.36, 0.31, 0.26, 0.21]; passo = 2 * math.pi / 5.4; jit = 0.10
        phi = rng.uniform(0, 2 * math.pi)
        for t in alvos:
            n = np.array([math.cos(phi), math.sin(phi)])
            e = _extensao(self.estados[-1], n, c)
            r = min(R * t, e - 0.12 * R)
            if r > 0.06 * R and e - r > 0.05 * R:
                d = float(n @ c + r)
                self.dobras.append((n, d))
                self.estados.append(dobra(self.estados[-1], n, d))
            phi += passo + rng.uniform(-jit, jit)
        self.N = len(self.dobras)
        # sombreamento de amassado (placas e vincos, bem suaves)
        from papel import _facetas
        F, B = _facetas(self.H, self.W, seed + 40, n=70)
        self.F = ndi.gaussian_filter(F, 4); self.B = ndi.gaussian_filter(B, 1.6)
        self.var = rng.uniform(-0.02, 0.02, 200)
        from papel import _ruido
        self.dx = (ndi.gaussian_filter(_ruido((self.H, self.W), 90, seed + 70), 3) - 0.5) * 2
        self.dy = (ndi.gaussian_filter(_ruido((self.H, self.W), 90, seed + 71), 3) - 0.5) * 2
        self._cache = {}

    # ---------------------------------------------------------------- desenho de uma pilha
    def _desenha(self, pilha, apaga_foto=0.0):
        H, W = self.H, self.W
        out = np.zeros((H, W, 4), np.float32)
        D = np.zeros((H, W), np.float32)          # sombra já aplicada (não acumula entre dezenas de pedaços)
        for idx, pc in enumerate(pilha):
            P = _ap(pc.M, pc.poly)
            x0, y0 = int(max(0, math.floor(P[:, 0].min()) - 1)), int(max(0, math.floor(P[:, 1].min()) - 1))
            x1, y1 = int(min(W, math.ceil(P[:, 0].max()) + 2)), int(min(H, math.ceil(P[:, 1].max()) + 2))
            if x1 - x0 < 2 or y1 - y0 < 2: continue
            w, h = x1 - x0, y1 - y0
            mi = Image.new('L', (w * 2, h * 2), 0)
            ImageDraw.Draw(mi).polygon([((x - x0) * 2, (y - y0) * 2) for x, y in P], fill=255)
            m = np.array(mi.resize((w, h), Image.BILINEAR)).astype(np.float32) / 255
            m = np.clip(m * 1.6, 0, 1)                          # costura sem frestas entre pedaços vizinhos
            ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            Mi = np.linalg.inv(pc.M)
            sx = Mi[0, 0] * xs + Mi[0, 1] * ys + Mi[0, 2]
            sy = Mi[1, 0] * xs + Mi[1, 1] * ys + Mi[1, 2]
            a_tex = ndi.map_coordinates(self.tex[..., 3], [sy, sx], order=1, cval=0) / 255
            a = m * a_tex
            if not pc.verso:
                rgb = np.stack([ndi.map_coordinates(self.tex[..., k], [sy, sx], order=1, cval=0) for k in range(3)], -1)
                if apaga_foto > 0: rgb = rgb * (1 - apaga_foto) + PAPEL * apaga_foto * 0.97
            else:
                rgb = np.broadcast_to(PAPEL, (h, w, 3)).copy()
                rgb += (np.random.RandomState(idx).randn(h, w, 1) * 1.6)
            lum = pc.luz * (1 + self.var[idx % 200])
            rgb = rgb * lum
            reg = out[y0:y1, x0:x1]
            # sombra projetada sobre o que está embaixo
            if idx > 0:
                sh = ndi.gaussian_filter(m, 4.0)
                sh = np.roll(np.roll(sh, 4, 0), 3, 1)
                Dr = D[y0:y1, x0:x1]
                s_ = 0.26 * sh * reg[..., 3] * (1 - a)
                nd = np.maximum(Dr, s_)
                reg[..., :3] *= ((1 - nd) / (1 - Dr))[..., None]
                D[y0:y1, x0:x1] = nd
            # contorno (vinco) do pedaço
            borda = m - ndi.grey_erosion(m, size=(3, 3))
            rgb = rgb * (1 - 0.14 * np.clip(borda * 2, 0, 1))[..., None]
            ra = reg[..., 3:4]
            reg[..., :3] = reg[..., :3] * (1 - a[..., None]) + rgb * a[..., None]
            reg[..., 3:4] = ra + a[..., None] * (1 - ra)
            D[y0:y1, x0:x1] *= (1 - a)
        return out

    # ---------------------------------------------------------------- quadro
    def quadro(self, c, bola_a=0.78):
        """c de 0 (aberto) a 1 (bola)"""
        c = max(0.0, min(1.0, c))
        k = (c, )
        if c <= 1e-4: return self.img.copy()
        cd = min(1.0, c / bola_a)                      # parte das dobras
        u = cd * self.N
        i = min(self.N - 1, int(u)); p = u - i
        pilha = self.estados[i]
        af = max(0.0, min(1.0, (c - 0.93) / 0.05)) if c < 1 else 1.0
        if cd >= 1.0: out = self._desenha(self.estados[self.N], af)
        else:
            pe = p * p * (3 - 2 * p)                    # ease dentro de cada dobra
            n, d = self.dobras[i]
            out = self._desenha(dobra(pilha, n, d, ang=math.pi * pe))
        out = self._organico(out, c, bola_a)
        return self._acabamento(out, c, bola_a)

    def _organico(self, out, c, bola_a):
        """deformação suave: retas viram bordas levemente onduladas, como papel de verdade"""
        amp = 9.0 * min(1.0, c / bola_a) ** 1.3
        if amp < 0.3: return out
        H, W = self.H, self.W
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        sx = xx + self.dx * amp; sy = yy + self.dy * amp
        res = np.empty_like(out)
        for k in range(4): res[..., k] = ndi.map_coordinates(out[..., k], [sy, sx], order=1, mode='constant', cval=0)
        return res

    def _acabamento(self, out, c, bola_a):
        H, W = self.H, self.W
        prog = min(1.0, c / bola_a)
        k = prog ** 1.2
        sh = 1 + k * (0.045 * np.clip(self.F, -1.5, 1.5) - 0.085 * self.B)     # placas e vincos do amassado
        out[..., :3] *= sh[..., None]
        q = max(0.0, (c - bola_a) / (1 - bola_a))
        if q <= 0:
            return Image.fromarray(np.dstack([np.clip(out[..., :3], 0, 255), np.clip(out[..., 3], 0, 1) * 255]).astype(np.uint8), 'RGBA')
        a0 = out[..., 3]
        ys, xs = np.nonzero(a0 > 0.5)
        if len(ys) == 0:
            return Image.new('RGBA', (W, H), (0, 0, 0, 0))
        cy, cx = ys.mean(), xs.mean(); R = math.sqrt(len(ys) / math.pi)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        # 1) as pontas são puxadas para dentro, como o papel sendo engolido por si mesmo
        Rm = max(R * 1.8, 1.0)
        f = 1 + 1.15 * q * (dist / Rm) ** 2 * 2.2
        sx, sy = cx + (xx - cx) * f, cy + (yy - cy) * f
        out = np.stack([ndi.map_coordinates(out[..., k_], [sy, sx], order=1, mode='constant', cval=0) for k_ in range(4)], -1)
        # 2) o que passa do círculo é dobrado para dentro (cortado) e o círculo se completa com papel
        ang = np.arctan2(yy - cy, xx - cx)
        irr = 1 + 0.045 * np.sin(5 * ang + 1.3) + 0.03 * np.sin(8 * ang + 0.4) + 0.02 * np.sin(13 * ang)
        borda = R * 0.98 * irr
        disco = np.clip((borda - dist) / 1.8 + 0.5, 0, 1)
        permitido = np.clip((borda * (1 + 0.9 * (1 - q) ** 1.5) - dist) / 1.8 + 0.5, 0, 1)
        a = np.clip(np.maximum(out[..., 3] * permitido, disco * min(1.0, q * 2.5)), 0, 1)
        nx, ny = (xx - cx) / (R * 1.0), (yy - cy) / (R * 1.0)
        rr = np.clip(np.sqrt(nx * nx + ny * ny), 0, 1)
        nz = np.sqrt(np.clip(1 - rr * rr, 0, 1))
        lamb = np.clip(-0.45 * nx - 0.55 * ny + 0.75 * nz, 0, 1)
        esf = 1 - q * (1 - (0.60 + 0.46 * lamb))
        crum = 1 + q * (0.10 * np.clip(self.F, -1.5, 1.5) - 0.22 * self.B)
        papel = PAPEL[None, None, :] * (1 + 0.05 * np.clip(self.F, -1.5, 1.5) - 0.10 * self.B)[..., None]
        fora = np.clip(1 - out[..., 3:4], 0, 1)
        out[..., :3] = out[..., :3] * (1 - fora) + papel * fora
        out[..., :3] = np.where((a[..., None] > 0.02), out[..., :3], 0)
        out[..., :3] *= (esf * crum)[..., None]
        # 3) leva a bola para o centro do quadro
        dx, dy = (self.cx - cx) * q ** 1.4, (self.cy - cy) * q ** 1.4
        res = np.dstack([np.clip(out[..., :3], 0, 255), a * 255]).astype(np.uint8)
        im = Image.fromarray(res, 'RGBA')
        return im.transform(im.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR)
