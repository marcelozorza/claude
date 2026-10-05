"""Risco de marca-texto vermelho (X) desenhado sobre uma peça de papel, preso à forma da peça."""
import math
import numpy as np
from PIL import Image, ImageDraw
def riscar_x(im, p, margem=0.07, larg=None, cor=(232, 36, 40, 215), caixa=None):
    """im: RGBA. p: progresso 0..1 (o primeiro traço vai de 0 a 0,5, o segundo de 0,5 a 1). Devolve cópia com o X.
    caixa: (x0, y0, x1, y1) região onde o X é desenhado (padrão: a imagem toda)."""
    if p <= 0: return im
    x0, y0, x1, y1 = caixa or (0, 0, im.width, im.height); w, h = x1 - x0, y1 - y0
    larg = larg or 0.085 * min(w, h)
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    mx, my = w * margem, h * margem
    tracos = [((x0 + mx, y0 + my), (x1 - mx, y1 - my)), ((x1 - mx, y0 + my), (x0 + mx, y1 - my))]
    for k, ((ax, ay), (bx, by)) in enumerate(tracos):
        pr = max(0.0, min(1.0, p * 2 - k))
        if pr <= 0: continue
        n = 28; ang = math.atan2(by - ay, bx - ax); nx, ny = -math.sin(ang), math.cos(ang)
        pts = []
        for i in range(int(n * pr) + 1):
            u = pr * i / max(1, int(n * pr)); wob = 0.02 * min(w, h) * math.sin(u * 7 + k * 2)
            pts.append((ax + (bx - ax) * u + nx * wob, ay + (by - ay) * u + ny * wob))
        for a, b in zip(pts, pts[1:]): d.line([a, b], fill=cor, width=int(larg))
        for q in (pts[0], pts[-1]): d.ellipse([q[0] - larg / 2, q[1] - larg / 2, q[0] + larg / 2, q[1] + larg / 2], fill=cor)
    a = np.array(lay.getchannel('A')).astype(np.float32) * (np.array(im.getchannel('A')).astype(np.float32) / 255)
    lay.putalpha(Image.fromarray(a.astype(np.uint8)))
    out = im.copy(); out.alpha_composite(lay); return out
