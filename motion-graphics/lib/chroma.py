import numpy as np
from scipy import ndimage as ndi
def key_rgb(a, lo=22, hi=68, spill=0.92):
    """a: HxWx3 uint8 (fundo verde). Devolve HxWx4 uint8 com alfa e despill."""
    f = a.astype(np.float32)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    s = g - np.maximum(r, b)                      # dominância do verde
    alfa = 1 - np.clip((s - lo) / (hi - lo), 0, 1)
    alfa = ndi.grey_erosion(alfa, size=(3, 3)) * 0.5 + alfa * 0.5   # morde um pouco a borda
    alfa = np.clip(alfa * 1.04 - 0.02, 0, 1)
    lim = np.maximum(r, b) * spill + 4
    g2 = np.minimum(g, lim)
    out = np.dstack([r, g2, b, alfa * 255])
    return np.clip(out, 0, 255).astype(np.uint8)


def grade(rgba, temp=0.18, matiz=0.18, sat=0.18):
    """correção de cor do apresentador (valores 0..1 equivalem ao dial do editor: 0.18 ~ 18 de 100).
    temp > 0 esquenta (mais vermelho, menos azul), matiz > 0 puxa para magenta (menos verde), sat > 0 satura."""
    f = rgba[..., :3].astype(np.float32)
    f[..., 0] *= 1 + 0.38 * temp
    f[..., 2] *= 1 - 0.42 * temp
    f[..., 1] *= 1 - 0.16 * matiz
    luma = f @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    f = luma[..., None] + (f - luma[..., None]) * (1 + sat)
    out = rgba.copy(); out[..., :3] = np.clip(f, 0, 255).astype(np.uint8)
    return out


def key_robusto(a, lo=26, hi=60, spill=0.92, corte_y=None, borda=10, miolo=2, max_buraco=1800):
    """chroma key para figura inteira sobre pano verde, com luz irregular. a: HxWx3 uint8. Devolve HxWx4 uint8.
    1) alfa pela dominância do verde, com limiares baixos (derruba o feixe de luz, que fica verde claro)
    2) fica só o maior bloco conectado (a figura), tapa buracos e torna o miolo opaco (acaba com as manchas na camisa preta)
    3) a borda macia vem do alfa original, só perto da figura (descarta restos soltos do pano)
    corte_y: linha a partir da qual tudo é transparente (peça escura que corta a cintura)."""
    f = a.astype(np.float32); r, g, b = f[..., 0], f[..., 1], f[..., 2]
    s = g - np.maximum(r, b)
    a0 = 1 - np.clip((s - lo) / (hi - lo), 0, 1)
    if corte_y is not None: a0[corte_y:] = 0
    nucleo = a0 > 0.5
    lab, n = ndi.label(nucleo)
    if n == 0: return key_rgb(a)
    tam = ndi.sum(nucleo, lab, range(1, n + 1)); fig = lab == (1 + int(np.argmax(tam)))
    buracos = ndi.binary_fill_holes(fig) & ~fig                            # só tapa buracos pequenos (manchas da camisa), nunca o vão entre braço e corpo
    lb, nb = ndi.label(buracos)
    if nb:
        ar = ndi.sum(buracos, lb, range(1, nb + 1)); pequenos = np.isin(lb, 1 + np.where(ar < max_buraco)[0]); fig = fig | pequenos
    miolo_m = ndi.binary_erosion(fig, iterations=miolo)
    perto = ndi.binary_dilation(fig, iterations=borda)
    alfa = np.maximum(a0 * perto, miolo_m.astype(np.float32))
    alfa = ndi.gaussian_filter(alfa, 0.6)
    alfa = np.clip((alfa - 0.10) / 0.7, 0, 1)                              # aperta a borda: tira o aro cinza de pixels metade pano, metade pele ou camisa
    lim = np.maximum(r, b) * spill + 4
    out = np.dstack([r, np.minimum(g, lim), b, alfa * 255])
    return np.clip(out, 0, 255).astype(np.uint8)


def limpa_pretos(rgba, limiar=60, suave=36, tira_cor=0.85, borra=2.2):
    """áreas escuras (camisa preta) saem do vídeo com blocos de compressão em tons esverdeados. Tira a cor e suaviza a luz só onde é escuro."""
    out = rgba.astype(np.float32); rgb = out[..., :3]
    luma = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    w = np.clip((limiar - luma) / suave, 0, 1)                           # 1 nas sombras profundas, 0 acima do limiar
    luma_b = ndi.gaussian_filter(luma, borra)
    alvo_l = luma * (1 - w) + luma_b * w                                  # suaviza o xadrez de luz
    cor = rgb - luma[..., None]
    rgb2 = alvo_l[..., None] + cor * (1 - tira_cor * w)[..., None]        # tira o tom verde dos blocos
    out[..., :3] = np.clip(rgb2, 0, 255)
    return out.astype(np.uint8)
