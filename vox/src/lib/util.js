// Utilidades de desenho: acaso com semente, ruído, curvas e traço feito à mão.
export let W = 1080;
export let H = 1920;
// Tamanho do quadro. Os estudos usam 1080x1920, o storyboard 1080x1620 (2:3).
export const tamanho = (w, h) => {
  W = w;
  H = h;
};

export const rng = (seed) => {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

export const gauss = (r) => {
  let u = 0;
  for (let i = 0; i < 6; i++) u += r();
  return (u - 3) / 1.2;
};

// Ruído de valor 2D, suave, entre -1 e 1.
export const makeNoise = (seed) => {
  const r = rng(seed);
  const p = Array.from({length: 256}, (_, i) => i);
  for (let i = 255; i > 0; i--) {
    const j = Math.floor(r() * (i + 1));
    [p[i], p[j]] = [p[j], p[i]];
  }
  const perm = new Uint16Array(512);
  for (let i = 0; i < 512; i++) perm[i] = p[i & 255];
  const val = new Float32Array(256).map(() => r() * 2 - 1);
  const h = (x, y) => val[perm[(perm[x & 255] + (y & 255)) & 511]];
  return (x, y) => {
    const xi = Math.floor(x);
    const yi = Math.floor(y);
    const xf = x - xi;
    const yf = y - yi;
    const u = xf * xf * (3 - 2 * xf);
    const v = yf * yf * (3 - 2 * yf);
    const a = h(xi, yi);
    const b = h(xi + 1, yi);
    const c = h(xi, yi + 1);
    const d = h(xi + 1, yi + 1);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  };
};
export const fbm = (n, x, y, oct = 4) => {
  let s = 0;
  let a = 0.5;
  let f = 1;
  for (let i = 0; i < oct; i++) {
    s += a * n(x * f, y * f);
    f *= 2.03;
    a *= 0.5;
  }
  return s;
};

// Catmull-Rom: curva suave que passa pelos pontos.
export const spline = (pts, closed = false, per = 14) => {
  const n = pts.length;
  const get = (i) => (closed ? pts[(i + n) % n] : pts[Math.max(0, Math.min(n - 1, i))]);
  const out = [];
  const segs = closed ? n : n - 1;
  for (let i = 0; i < segs; i++) {
    const p0 = get(i - 1);
    const p1 = get(i);
    const p2 = get(i + 1);
    const p3 = get(i + 2);
    for (let k = 0; k < per; k++) {
      const t = k / per;
      const t2 = t * t;
      const t3 = t2 * t;
      const f = (j) =>
        0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3);
      out.push([f(0), f(1)]);
    }
  }
  if (!closed) out.push(pts[n - 1]);
  return out;
};

export const lengthOf = (pts) => {
  let s = 0;
  for (let i = 1; i < pts.length; i++) s += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
  return s;
};

// Reamostra com espaçamento constante.
export const resample = (pts, step = 4, closed = false) => {
  const src = closed ? [...pts, pts[0]] : pts;
  const out = [src[0]];
  let carry = 0;
  for (let i = 1; i < src.length; i++) {
    const [x0, y0] = src[i - 1];
    const [x1, y1] = src[i];
    const seg = Math.hypot(x1 - x0, y1 - y0);
    let d = step - carry;
    while (d <= seg) {
      const t = d / seg;
      out.push([x0 + (x1 - x0) * t, y0 + (y1 - y0) * t]);
      d += step;
    }
    carry = seg - (d - step);
  }
  if (!closed) out.push(src[src.length - 1]);
  return out;
};

export const normals = (pts) =>
  pts.map((p, i) => {
    const a = pts[Math.max(0, i - 1)];
    const b = pts[Math.min(pts.length - 1, i + 1)];
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    const l = Math.hypot(dx, dy) || 1;
    return [-dy / l, dx / l];
  });

// Tremor de mão: desloca cada ponto pela normal, com ruído ao longo do comprimento.
export const wobble = (pts, amp = 1.5, freq = 0.02, seed = 1, fine = 0.35) => {
  const n = makeNoise(seed);
  const nr = normals(pts);
  let s = 0;
  return pts.map((p, i) => {
    if (i) s += Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]);
    const o = amp * n(s * freq, 0.5) + fine * n(s * 0.35, 7.5);
    return [p[0] + nr[i][0] * o, p[1] + nr[i][1] * o];
  });
};

// Polígono de um traço com largura variável (w(s) com s de 0 a 1).
export const strokePoly = (pts, w) => {
  const nr = normals(pts);
  const L = [];
  const R = [];
  pts.forEach((p, i) => {
    const hw = w(i / (pts.length - 1)) / 2;
    L.push([p[0] + nr[i][0] * hw, p[1] + nr[i][1] * hw]);
    R.push([p[0] - nr[i][0] * hw, p[1] - nr[i][1] * hw]);
  });
  return [...L, ...R.reverse()];
};

export const ellipse = (cx, cy, rx, ry, n = 72, rot = 0) =>
  Array.from({length: n}, (_, i) => {
    const a = (i / n) * Math.PI * 2;
    const x = Math.cos(a) * rx;
    const y = Math.sin(a) * ry;
    return [cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot)];
  });

export const rect = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];

export const trace = (ctx, pts, closed = true) => {
  ctx.beginPath();
  pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
  if (closed) ctx.closePath();
};

export const layer = () => {
  const c = document.createElement('canvas');
  c.width = W;
  c.height = H;
  return c;
};

// Traço de tinta com largura que respira. Desenha segmento a segmento.
export const inkStroke = (ctx, pts, {width = 3, color = '#fff', seed = 1, wVar = 0.35, colorAt = null, taper = 0} = {}) => {
  const n = makeNoise(seed);
  ctx.save();
  ctx.lineCap = 'round';
  let s = 0;
  const total = lengthOf(pts);
  for (let i = 1; i < pts.length; i++) {
    const [x0, y0] = pts[i - 1];
    const [x1, y1] = pts[i];
    s += Math.hypot(x1 - x0, y1 - y0);
    const u = s / total;
    const tp = taper ? Math.min(1, Math.sin(Math.PI * u) * taper) : 1;
    ctx.lineWidth = Math.max(0.3, width * (1 + wVar * n(s * 0.015, 0.5)) * tp);
    ctx.strokeStyle = colorAt ? colorAt(x1, y1, u) : color;
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
  }
  ctx.restore();
};

// Grão por pixel (papel).
export const grain = (ctx, seed = 3, amount = 0.05, scale = 1) => {
  const img = ctx.getImageData(0, 0, W, H);
  const d = img.data;
  const r = rng(seed);
  const n = makeNoise(seed + 11);
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const i = (y * W + x) * 4;
      const g = (r() - 0.5) * amount * 255 + n(x * 0.02 * scale, y * 0.02 * scale) * amount * 90;
      d[i] += g;
      d[i + 1] += g;
      d[i + 2] += g;
    }
  }
  ctx.putImageData(img, 0, 0);
};

export const mixHex = (a, b, t) => {
  const pa = [1, 3, 5].map((k) => parseInt(a.slice(k, k + 2), 16));
  const pb = [1, 3, 5].map((k) => parseInt(b.slice(k, k + 2), 16));
  return `rgb(${pa.map((v, k) => Math.round(v + (pb[k] - v) * t)).join(',')})`;
};
