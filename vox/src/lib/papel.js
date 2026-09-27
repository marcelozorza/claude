import {H, W, fbm, layer, lengthOf, makeNoise, mixHex, normals, resample, rng, trace, wobble} from './util';

// Papel recortado: textura, corte de tesoura, rasgo, peça com sombra e tira que gira.

// Tremor de stop motion: a cada quadro cada peça sai um pouco do lugar.
let TREMOR = {q: 0, amp: 0, n: 0};
export const tremor = (q, amp = 0.7) => {
  TREMOR = {q, amp, n: 0};
};
const desvio = () => {
  if (!TREMOR.amp) return [0, 0];
  const r = rng(TREMOR.n++ * 9973 + TREMOR.q * 7919 + 1);
  return [(r() - 0.5) * 2 * TREMOR.amp, (r() - 0.5) * 2 * TREMOR.amp];
};
// Fibras e pintas do papel colorido, em claro e escuro translúcidos.
const TEX = {};
export const texturaPapel = (seed) => {
  const k = `${seed}-${W}x${H}`;
  if (TEX[k]) return TEX[k];
  const cv = layer();
  TEX[k] = cv;
  const c = cv.getContext('2d');
  const img = c.createImageData(W, H);
  const d = img.data;
  const n = makeNoise(seed);
  const r = rng(seed);
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const i = (y * W + x) * 4;
      const v = 0.5 * n(x * 0.7, y * 0.7) + 0.3 * n(x * 0.1 + 50, y * 0.1) + (r() - 0.5) * 0.3;
      const t = v > 0 ? 255 : 0;
      d[i] = t;
      d[i + 1] = t;
      d[i + 2] = t;
      d[i + 3] = Math.min(255, Math.abs(v) * 40);
    }
  }
  c.putImageData(img, 0, 0);
  c.lineCap = 'round';
  for (let k = 0; k < 2200; k++) {
    const x = r() * W;
    const y = r() * H;
    const a = r() * Math.PI * 2;
    const l = 5 + r() * 22;
    const claro = r() < 0.75;
    c.strokeStyle = claro ? `rgba(255,255,255,${0.08 + r() * 0.16})` : `rgba(0,0,0,${0.08 + r() * 0.12})`;
    c.lineWidth = 0.5 + r() * 0.8;
    c.beginPath();
    c.moveTo(x, y);
    c.quadraticCurveTo(x + Math.cos(a + 0.6) * l * 0.5, y + Math.sin(a + 0.6) * l * 0.5, x + Math.cos(a) * l, y + Math.sin(a) * l);
    c.stroke();
  }
  return cv;
};

// Corte de tesoura: pequenas facetas e um tremor leve.
export const tesoura = (poly, seed, amp = 1.3) => {
  const r = rng(seed);
  const passo = Math.min(9, lengthOf([...poly, poly[0]]) / 40);
  return wobble(resample(poly, passo, true), amp, 0.015, seed, 0.3).map(([x, y]) => [x + (r() - 0.5) * 0.9, y + (r() - 0.5) * 0.9]);
};

// Borda rasgada: fibrosa, irregular.
export const rasgo = (pts, seed, amp = 4) => {
  const n = makeNoise(seed);
  const r = rng(seed);
  return resample(pts, 3).map(([x, y], i) => [x, y + amp * fbm(n, i * 0.08, 0.5, 3) + (r() - 0.5) * 1.6]);
};

export const desenhar = (c, forma) => {
  if (typeof forma === 'function') forma(c);
  else {
    trace(c, forma);
    c.fill();
  }
};

// Uma peça de papel: cor, fibras, espessura na borda e sombra.
export const peca = (ctx, forma, {cor, tex, texA = 0.55, sombra = [5, 9, 14, 0.55], espessura = 1.6, grad = null}) => {
  const L = layer();
  const c = L.getContext('2d');
  c.fillStyle = cor;
  desenhar(c, forma);
  c.globalCompositeOperation = 'source-atop';
  if (grad) {
    c.fillStyle = grad(c);
    c.fillRect(0, 0, W, H);
  }
  c.globalAlpha = texA;
  c.drawImage(tex, 0, 0);
  c.globalAlpha = 1;
  // Espessura: um fio claro na borda que pega luz, um fio escuro do lado oposto.
  if (espessura) {
    [[espessura, 'rgba(255,255,255,0.32)'], [-espessura, 'rgba(0,0,20,0.28)']].forEach(([o, tom]) => {
      const E = layer();
      const e = E.getContext('2d');
      e.fillStyle = tom;
      desenhar(e, forma);
      e.globalCompositeOperation = 'destination-out';
      e.translate(o, o);
      e.fillStyle = '#000';
      desenhar(e, forma);
      c.drawImage(E, 0, 0);
    });
  }
  ctx.save();
  if (sombra) {
    const [dx, dy, blur, a] = sombra;
    ctx.shadowColor = `rgba(2,6,18,${a})`;
    ctx.shadowBlur = blur;
    ctx.shadowOffsetX = dx;
    ctx.shadowOffsetY = dy;
  }
  const [tx, ty] = desvio();
  ctx.drawImage(L, tx, ty);
  ctx.restore();
};

// Tira de papel que gira: a largura muda de sinal e mostra o verso.
export const fita = (ctx, pts, {larg = 22, voltas = 2, fase = 0, frente, verso, tex, sombra = [11, 18, 16, 0.45], tom = null}) => {
  const p = resample(pts, 3);
  const nr = normals(p);
  const total = lengthOf(p);
  const L = layer();
  const c = L.getContext('2d');
  let s = 0;
  const q = p.map((pt, i) => {
    if (i) s += Math.hypot(pt[0] - p[i - 1][0], pt[1] - p[i - 1][1]);
    const phi = fase + (s / total) * voltas * Math.PI * 2;
    return {w: (larg / 2) * Math.cos(phi), luz: Math.sin(phi)};
  });
  c.lineWidth = 0.8;
  for (let i = 0; i < p.length - 1; i++) {
    const [ax, ay] = p[i];
    const [bx, by] = p[i + 1];
    const wa = q[i].w;
    const wb = q[i + 1].w;
    const lado = wa + wb >= 0;
    let cor = lado ? frente : verso;
    if (tom) cor = tom(cor, ax, ay);
    const l = q[i].luz * (lado ? 1 : -1);
    cor = l > 0 ? mixHex(cor, '#FFFFFF', 0.18 * l) : mixHex(cor, '#0A1430', -0.22 * l);
    c.fillStyle = cor;
    c.strokeStyle = cor;
    trace(c, [
      [ax + nr[i][0] * wa, ay + nr[i][1] * wa],
      [bx + nr[i + 1][0] * wb, by + nr[i + 1][1] * wb],
      [bx - nr[i + 1][0] * wb, by - nr[i + 1][1] * wb],
      [ax - nr[i][0] * wa, ay - nr[i][1] * wa],
    ]);
    c.fill();
    c.stroke();
  }
  c.globalCompositeOperation = 'source-atop';
  c.globalAlpha = 0.45;
  c.drawImage(tex, 0, 0);
  ctx.save();
  const [dx, dy, blur, a] = sombra;
  ctx.shadowColor = `rgba(2,6,18,${a})`;
  ctx.shadowBlur = blur;
  ctx.shadowOffsetX = dx;
  ctx.shadowOffsetY = dy;
  ctx.drawImage(L, 0, 0);
  ctx.restore();
};

export const hex = (c) => {
  if (c[0] === '#') return c;
  const [r, g, b] = c.match(/\d+/g).map(Number);
  return '#' + [r, g, b].map((v) => v.toString(16).padStart(2, '0')).join('');
};
