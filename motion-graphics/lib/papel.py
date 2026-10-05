"""Recorte de jornal e animação de bola de papel (desenrola / enrola)."""
import math
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

_cache = {}
def _facetas(H, W, seed, n=110):
    k = (H, W, seed)
    if k in _cache: return _cache[k]
    r = np.random.RandomState(seed)
    pts = np.c_[r.rand(n) * W, r.rand(n) * H]
    val = r.rand(n) * 2 - 1
    gx, gy = r.randn(n) * 0.5, r.randn(n) * 0.5
    yy, xx = np.mgrid[0:H:2, 0:W:2]
    q = np.c_[xx.ravel(), yy.ravel()].astype(float)
    d, idx = cKDTree(pts).query(q, k=2)
    px = (q[:, 0] - pts[idx[:, 0], 0]); py = (q[:, 1] - pts[idx[:, 0], 1])
    fac = val[idx[:, 0]] + (gx[idx[:, 0]] * px + gy[idx[:, 0]] * py) / 60.0
    borda = 1 - np.clip((d[:, 1] - d[:, 0]) / 5.0, 0, 1)
    F = np.kron(fac.reshape(xx.shape), np.ones((2, 2)))[:H, :W]
    B = np.kron(borda.reshape(xx.shape), np.ones((2, 2)))[:H, :W]
    B = ndi.gaussian_filter(B, 0.8)
    _cache[k] = (F, B)
    return F, B

PAPEL = np.array([246, 241, 230], float)

_cache_a = {}
def _amassado(H, W, seed, n, tilt=0.30, grad=0.9, alonga=1.0, grad_k=0.10):
    """campos de um papel amassado de verdade. Cada placa (célula de Voronoi) é um plano inclinado, com degradê suave dentro dela (iluminação
    direcional) e arestas definidas entre placas. O vinco escurece conforme o ÂNGULO entre as placas vizinhas.
    Devolve (luz, vinco): luz em torno de 0 (placa voltada para a luz > 0), vinco 0..1."""
    k = (H, W, seed, n, tilt, grad, alonga, grad_k)
    if k in _cache_a: return _cache_a[k]
    r = np.random.RandomState(seed)
    pts = np.c_[r.rand(n) * W, r.rand(n) * H]; nx, ny = r.randn(n) * tilt, r.randn(n) * tilt; gx, gy = r.randn(n) * grad, r.randn(n) * grad
    yy, xx = np.mgrid[0:H:2, 0:W:2]; q = np.c_[xx.ravel(), yy.ravel()].astype(float)
    if alonga != 1.0:                                                               # placas alongadas numa direção (vincos mais longos)
        t_ = r.uniform(0, math.pi); A = np.array([[math.cos(t_), math.sin(t_)], [-math.sin(t_), math.cos(t_)]]) * np.array([[alonga], [1.0]])
        d, idx = cKDTree(pts @ A.T).query(q @ A.T, k=2)
    else: d, idx = cKDTree(pts).query(q, k=2)
    a, b = idx[:, 0], idx[:, 1]
    L = np.array([-0.45, -0.55, 0.70]); L = L / np.linalg.norm(L)
    n3 = np.stack([-nx[a], -ny[a], np.ones(len(a))], 1); n3 /= np.linalg.norm(n3, axis=1, keepdims=True)
    esc = max(H, W) / 6.0                                                           # o degradê dentro da placa acompanha o tamanho dela
    px, py = q[:, 0] - pts[a, 0], q[:, 1] - pts[a, 1]
    luz = (n3 @ L) / L[2] - 1.0 + grad_k * (gx[a] * px + gy[a] * py) / esc
    delta = np.sqrt((nx[a] - nx[b]) ** 2 + (ny[a] - ny[b]) ** 2)                      # ângulo entre as placas vizinhas
    borda = (1 - np.clip((d[:, 1] - d[:, 0]) / 3.0, 0, 1)) * np.clip(delta / (1.4 * tilt), 0, 1.3)
    up = lambda v: np.kron(v.reshape(xx.shape), np.ones((2, 2)))[:H, :W]
    res = (up(luz), np.clip(ndi.gaussian_filter(up(borda), 1.1), 0, 1.3)); _cache_a[k] = res; return res

def _ruido(shape, escala, seed):
    r = np.random.RandomState(seed)
    h, w = shape
    g = r.rand(max(2, h // escala + 2), max(2, w // escala + 2))
    return ndi.zoom(g, (h / g.shape[0] * 1.0, w / g.shape[1] * 1.0), order=3)[:h, :w]

def recorte_jornal(rgba, borda=18, seed=3, ruido_borda=7):
    """foto recortada com margem de papel irregular, como recorte de tesoura em jornal"""
    a = np.array(rgba.convert('RGBA'))
    h, w = a.shape[:2]
    pad = borda + 20
    A = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.uint8); A[pad:pad + h, pad:pad + w] = a
    m = A[..., 3] > 128
    dist = ndi.distance_transform_edt(~m)
    n = _ruido(m.shape, 38, seed) * 2 - 1
    lim = borda + ruido_borda * n
    papel_mask = (dist <= lim)
    papel_mask = ndi.binary_fill_holes(papel_mask)
    papel_mask = ndi.binary_opening(papel_mask, iterations=2)
    out = np.zeros_like(A)
    gr = (np.random.RandomState(seed).rand(*m.shape) * 10 - 5)[..., None]
    out[..., :3] = np.clip(PAPEL + gr, 0, 255).astype(np.uint8)
    out[..., 3] = (papel_mask * 255).astype(np.uint8)
    # foto por cima
    fa = (A[..., 3:4] / 255.0)
    out[..., :3] = (A[..., :3] * fa + out[..., :3] * (1 - fa)).astype(np.uint8)
    alpha = Image.fromarray(out[..., 3]).filter(ImageFilter.GaussianBlur(0.8))
    res = Image.fromarray(out); res.putalpha(alpha)
    return res

def _suave(u): return u * u * (3 - 2 * u)

def desenrola(img, c, seed=7, bola=0.30):
    """c = 1 bola de papel, c = 0 imagem aberta. Devolve RGBA do mesmo tamanho de img."""
    if c <= 0.001: return img.copy()
    src = np.array(img.convert('RGBA')).astype(np.float32)
    H, W = src.shape[:2]
    cy, cx = (H - 1) / 2, (W - 1) / 2
    M = 0.5 * max(H, W)
    Rb = 0.5 * min(H, W) * bola * 1.9
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    r = np.sqrt(dx * dx + dy * dy) + 1e-6
    k = _suave(c)
    esc = 1.0 / (1.0 - k + k * (Rb / M))
    pin = 1.0 + 0.30 * k * (r / M) ** 1.5
    n1 = _ruido((H, W), 70, seed) - 0.5
    n2 = _ruido((H, W), 24, seed + 1) - 0.5
    sx = cx + dx * esc * pin + (n1 * 14 + n2 * 4) * k * esc * 0.6
    sy = cy + dy * esc * pin + (n1[::-1] * 14 + n2[::-1] * 4) * k * esc * 0.6
    out = np.zeros_like(src)
    for ch in range(4):
        out[..., ch] = ndi.map_coordinates(src[..., ch], [sy, sx], order=1, mode='constant', cval=0)
    # vincos: ruído em crista em duas escalas
    def crista(esc_, sd):
        n = _ruido((H, W), esc_, sd) - 0.5
        return 1 - np.clip(np.abs(n) * 9, 0, 1)
    vinco = 0.55 * crista(30, seed + 2) + 0.45 * crista(11, seed + 3)
    F, B = _facetas(H, W, seed + 9)
    sombra = 1 + k * (0.07 + 0.15 * np.clip(F, -1.5, 1.5) - 0.18 * vinco - 0.22 * B)
    # esfera com luz vinda de cima à esquerda
    nx, ny = dx / Rb, dy / Rb
    rr = np.clip(np.sqrt(nx * nx + ny * ny), 0, 1)
    nz = np.sqrt(np.clip(1 - rr * rr, 0, 1))
    lamb = np.clip(-0.45 * nx - 0.55 * ny + 0.7 * nz, 0, 1)
    esfera = 1 - k * (1 - (0.74 + 0.36 * lamb))
    fator = (sombra * esfera)[..., None]
    mix = (k ** 1.6) * 0.95
    cor = (out[..., :3] * (1 - mix) + PAPEL * mix) * fator
    out[..., :3] = np.clip(cor, 0, 255)
    alfa = out[..., 3] / 255.0
    circ = 1 - np.clip((r - Rb * (1 + 0.05 * n1 * 4)) / 5.0, 0, 1)
    w = np.clip((k - 0.80) / 0.2, 0, 1)
    out[..., 3] = np.clip(alfa * (1 - w) + circ * w, 0, 1) * 255
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def anima(item, c, seed=7, bola=0.30):
    """Papel de fundo (mesma silhueta do recorte) que amassa em bola, com a foto por cima SEM mudar de tamanho:
    a foto só é cortada pela silhueta do papel, que vai ficando redonda, até a bola engolir a imagem.
    c = 0 aberto, c = 1 bola."""
    if c <= 0.001: return item.copy()
    H, W = item.size[1], item.size[0]
    blank = Image.new('RGBA', item.size, tuple(int(x) for x in PAPEL) + (255,))
    blank.putalpha(item.getchannel('A'))
    B = np.array(desenrola(blank, c, seed, bola)).astype(np.float32)
    S = B[..., 3] / 255.0
    P = np.array(item.convert('RGBA')).astype(np.float32)
    aP = P[..., 3] / 255.0
    k = _suave(c)
    # sombra do amassado também sobre a foto
    shade = np.clip(B[..., :3] / PAPEL, 0.5, 1.2) ** 0.95
    # máscara da foto: silhueta do papel erodida, cada vez mais redonda
    Rb = 0.5 * min(H, W) * bola * 1.9
    dist = ndi.distance_transform_edt(S > 0.5)
    e = (k ** 1.15) * Rb * 1.02
    vis = np.clip((dist - e) / 2.2, 0, 1) * aP
    rgb = B[..., :3] * (1 - vis[..., None]) + np.clip(P[..., :3] * shade, 0, 255) * vis[..., None]
    out = np.dstack([rgb, S * 255])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
