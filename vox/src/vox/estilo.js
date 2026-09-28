import {H, W, layer, makeNoise, resample, rng, spline, trace} from '../lib/util';
import {peca, tesoura, texturaPapel} from '../lib/papel';

// Linguagem Vox: papel quadriculado cor de areia, peças recortadas com sombra,
// traço de pincel à mão, marca-texto amarelo, datilografia de relatório.

export const TINTA = '#1F1B17';
export const AREIA = '#F6E8CB';
export const CORAL = '#E4572E';
export const AZUL = '#2F6F8F';
export const AMARELO = 'rgba(255,214,10,0.55)';
export const CREME = '#F7F1E1';

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
export const suave = (v) => {
  const t = clamp01(v);
  return t * t * (3 - 2 * t);
};
export const salta = (v) => {
  const t = clamp01(v);
  return 1 + 2.2 * (t - 1) ** 3 + 1.2 * (t - 1) ** 2;
};
export const mistura = (a, b, k) => a + (b - a) * k;

// Tempo da cena em segundos, atualizado a cada quadro antes do desenho.
export const RELOGIO = {t: 0};
// Balanço de vida: depois de entrar, cada peça oscila alguns graus em torno do próprio centro.
// A fase vem da posição, para as peças não balançarem juntas. Peças grandes giram menos.
export const balanco = (cx, cy, raio = 150) => {
  const fase = cx * 0.0131 + cy * 0.0077;
  const freq = 0.3 + 0.12 * ((Math.sin(fase * 7.3) + 1) / 2);
  const amp = Math.min((3 * Math.PI) / 180, 12 / Math.max(1, raio));
  return amp * Math.sin(RELOGIO.t * freq * Math.PI * 2 + fase);
};
// Desenha girando em torno de (cx, cy) com o balanço daquela peça.
export const gira = (ctx, cx, cy, raio, desenha) => {
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(balanco(cx, cy, raio));
  ctx.translate(-cx, -cy);
  desenha();
  ctx.restore();
};

// O papel: areia, fibras, quadriculado fino e grosso, bordas um pouco mais escuras.
let PAPEL = null;
const fazPapel = () => {
  const cv = layer();
  const c = cv.getContext('2d');
  c.fillStyle = AREIA;
  c.fillRect(0, 0, W, H);
  const n = makeNoise(31);
  const img = c.getImageData(0, 0, W, H);
  const d = img.data;
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const i = (y * W + x) * 4;
      const v = 2.5 * n(x * 0.01, y * 0.01) + 2 * n(x * 0.09 + 40, y * 0.09);
      d[i] += v;
      d[i + 1] += v;
      d[i + 2] += v * 0.8;
    }
  }
  c.putImageData(img, 0, 0);
  c.globalAlpha = 0.12;
  c.drawImage(texturaPapel(7), 0, 0);
  c.globalAlpha = 1;
  const passo = 45;
  const r = rng(5);
  const linha = (maior) => {
    c.strokeStyle = maior ? 'rgba(120,150,165,0.34)' : 'rgba(120,150,165,0.17)';
    c.lineWidth = maior ? 1.6 : 1;
  };
  for (let k = 0; k * passo <= W + passo; k++) {
    const x = k * passo + 0.5;
    linha(k % 5 === 0);
    c.beginPath();
    c.moveTo(x + (r() - 0.5), 0);
    c.lineTo(x + (r() - 0.5), H);
    c.stroke();
  }
  for (let k = 0; k * passo <= H + passo; k++) {
    const y = k * passo + 0.5;
    linha(k % 5 === 0);
    c.beginPath();
    c.moveTo(0, y + (r() - 0.5));
    c.lineTo(W, y + (r() - 0.5));
    c.stroke();
  }
  // Luz quente e uniforme, sem vinheta escura.
  const v = c.createRadialGradient(W / 2, H * 0.35, 200, W / 2, H * 0.35, 1400);
  v.addColorStop(0, 'rgba(255,248,230,0.25)');
  v.addColorStop(1, 'rgba(255,236,200,0.05)');
  c.fillStyle = v;
  c.fillRect(0, 0, W, H);
  return cv;
};
export const papel = (ctx) => {
  if (!PAPEL) PAPEL = fazPapel();
  ctx.drawImage(PAPEL, -40, -40, W + 80, H + 80);
};

// Traço de pincel: começa rápido, termina afinando, tem bordas secas. p = quanto já foi desenhado.
export const pincel = (ctx, pts, {larg = 9, cor = TINTA, seed = 1, p = 1, seco = 0.5, ponta = 0.22} = {}) => {
  if (p <= 0) return;
  const q = resample(pts, 2.5);
  const S = [0];
  for (let i = 1; i < q.length; i++) S.push(S[i - 1] + Math.hypot(q[i][0] - q[i - 1][0], q[i][1] - q[i - 1][1]));
  const L = S[S.length - 1] || 1;
  const fim = p * L;
  const n = makeNoise(seed);
  const esq = [];
  const dir = [];
  for (let i = 0; i < q.length && S[i] <= fim; i++) {
    const a = q[Math.max(0, i - 1)];
    const b = q[Math.min(q.length - 1, i + 1)];
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    const l = Math.hypot(dx, dy) || 1;
    const u = S[i] / L;
    const entra = clamp01(u / 0.05);
    const sai = clamp01((1 - u) / ponta);
    const w = (larg / 2) * (0.35 + 0.65 * Math.sqrt(entra)) * (0.25 + 0.75 * Math.sqrt(sai)) * (1 + 0.18 * n(S[i] * 0.02, 0.5));
    esq.push([q[i][0] - (dy / l) * w, q[i][1] + (dx / l) * w]);
    dir.push([q[i][0] + (dy / l) * w, q[i][1] - (dx / l) * w]);
  }
  if (esq.length < 2) return;
  const cv = layer();
  const c = cv.getContext('2d');
  c.fillStyle = cor;
  trace(c, [...esq, ...dir.reverse()]);
  c.fill();
  // Pincel seco: falhas finas ao longo do traço.
  if (seco) {
    const r = rng(seed + 9);
    c.globalCompositeOperation = 'destination-out';
    c.lineCap = 'round';
    for (let k = 0; k < 5; k++) {
      const off = (r() - 0.5) * larg * 0.8;
      c.lineWidth = 0.6 + r() * 1.2;
      c.strokeStyle = `rgba(0,0,0,${seco * (0.3 + r() * 0.5)})`;
      c.setLineDash([4 + r() * 30, 6 + r() * 40]);
      c.lineDashOffset = r() * 50;
      const lin = [];
      for (let i = 0; i < q.length && S[i] <= fim; i += 2) {
        const a = q[Math.max(0, i - 1)];
        const b = q[Math.min(q.length - 1, i + 1)];
        const dx = b[0] - a[0];
        const dy = b[1] - a[1];
        const l = Math.hypot(dx, dy) || 1;
        lin.push([q[i][0] - (dy / l) * off, q[i][1] + (dx / l) * off]);
      }
      trace(c, lin, false);
      c.stroke();
    }
  }
  ctx.drawImage(cv, 0, 0);
};

// Laço feito à mão em volta de algo, passando um pouco do ponto de partida.
export const laco = (cx, cy, rx, ry, seed = 1, volta = 1.12) => {
  const n = makeNoise(seed);
  const a0 = -2.2 + n(1, 1) * 0.3;
  return Array.from({length: 60}, (_, i) => {
    const a = a0 + (i / 59) * Math.PI * 2 * volta;
    const k = 1 + 0.06 * n(i * 0.15, 3) + 0.05 * (i / 59);
    return [cx + Math.cos(a) * rx * k, cy + Math.sin(a) * ry * k];
  });
};

// Seta de pincel com ponta.
export const seta = (ctx, pts, {larg = 8, cor = TINTA, seed = 1, p = 1} = {}) => {
  pincel(ctx, pts, {larg, cor, seed, p: Math.min(1, p / 0.8), ponta: 0.05});
  if (p > 0.8) {
    const k = (p - 0.8) / 0.2;
    const [ax, ay] = pts[pts.length - 2];
    const [bx, by] = pts[pts.length - 1];
    const a = Math.atan2(by - ay, bx - ax);
    const t = 34 * k;
    [0.55, -0.55].forEach((d, i) => pincel(ctx, [[bx, by], [bx - Math.cos(a + d) * t, by - Math.sin(a + d) * t]], {larg: larg * 0.9, cor, seed: seed + 3 + i, ponta: 0.5}));
  }
};

// Marca-texto: faixa amarela translúcida, bordas irregulares, passada da esquerda para a direita.
export const marcador = (ctx, x, y, w, h, p = 1, {cor = AMARELO, seed = 3} = {}) => {
  if (p <= 0) return;
  const n = makeNoise(seed);
  const ww = w * clamp01(p);
  const pts = [];
  for (let i = 0; i <= 20; i++) pts.push([x + (ww * i) / 20, y - h / 2 + 3 * n(i * 0.4, 1)]);
  for (let i = 20; i >= 0; i--) pts.push([x + (ww * i) / 20, y + h / 2 + 3 * n(i * 0.4, 7)]);
  ctx.save();
  ctx.globalCompositeOperation = 'multiply';
  ctx.fillStyle = cor;
  trace(ctx, pts);
  ctx.fill();
  ctx.restore();
};

// Peça de papel recortada, com borda branca opcional (como adesivo) e sombra sobre o quadriculado.
export const recorte = (ctx, forma, {cor = CREME, borda = 0, seed = 1, sombra = [6, 10, 14, 0.32], tex = texturaPapel(7)} = {}) => {
  const f = Array.isArray(forma) ? tesoura(forma, seed, 0.9) : forma;
  if (borda && Array.isArray(forma)) {
    peca(ctx, (c) => {
      c.lineWidth = borda * 2;
      c.lineJoin = 'round';
      c.strokeStyle = '#FFFDF6';
      trace(c, f);
      c.stroke();
      c.fillStyle = '#FFFDF6';
      c.fill();
    }, {cor: '#FFFDF6', tex, texA: 0.2, sombra, espessura: 0});
    peca(ctx, f, {cor, tex, texA: 0.3, sombra: null, espessura: 0});
  } else peca(ctx, f, {cor, tex, texA: 0.3, sombra, espessura: 1});
};

// Texto. p revela como máquina de escrever. Com etiqueta, vai sobre uma tira de papel recortado.
export const texto = (ctx, str, {x = W / 2, y, tam = 48, fonte = 'EB Garamond', cor = TINTA, alinha = 'center', p = 1, etiqueta = null, peso = '', estilo = ''} = {}) => {
  const n = Math.floor(str.length * clamp01(p) + 0.001);
  if (n <= 0) return;
  ctx.save();
  ctx.font = `${estilo} ${peso} ${tam}px "${fonte}"`;
  ctx.textAlign = alinha;
  ctx.textBaseline = 'middle';
  if (etiqueta) {
    const w = ctx.measureText(str).width;
    const xc = alinha === 'center' ? x : alinha === 'right' ? x - w / 2 : x + w / 2;
    ctx.translate(xc, y);
    ctx.rotate(balanco(xc, y, w / 2 + 22));
    ctx.translate(-xc, -y);
    const x0 = alinha === 'center' ? x - w / 2 : alinha === 'right' ? x - w : x;
    recorte(ctx, [[x0 - 22, y - tam * 0.75], [x0 + w + 22, y - tam * 0.7], [x0 + w + 20, y + tam * 0.72], [x0 - 20, y + tam * 0.75]], {cor: etiqueta, seed: str.length});
    ctx.font = `${estilo} ${peso} ${tam}px "${fonte}"`;
  }
  ctx.fillStyle = cor;
  ctx.fillText(str.slice(0, n), alinha === 'center' ? x - ctx.measureText(str).width / 2 + ctx.measureText(str.slice(0, n)).width / 2 : x, y);
  ctx.restore();
};

// Leve flutuação de câmera na mão.
export const camera = (ctx, t, {z = 1, cx = W / 2, cy = H / 2, deriva = 1} = {}) => {
  const dx = Math.sin(t * 0.7) * 5 * deriva;
  const dy = Math.cos(t * 0.53) * 4 * deriva;
  const r = Math.sin(t * 0.41) * 0.002 * deriva;
  ctx.setTransform(z * Math.cos(r), z * Math.sin(r), -z * Math.sin(r), z * Math.cos(r), cx - cx * z + dx, cy - cy * z + dy);
};

export {spline};

// Imagens (emojis 3D da Microsoft, licença MIT), carregadas antes do desenho.
export const IMAGENS = {};
// Cola uma imagem como adesivo recortado: contorno branco e sombra sobre o papel.
export const adesivo = (ctx, nome, cx, cy, tam, {borda = 10, sombra = [7, 12, 16, 0.3], giro = 0, fixo = false} = {}) => {
  const im = IMAGENS[nome];
  if (!im) return;
  const S = Math.ceil(tam + borda * 2 + 4);
  const cv = document.createElement('canvas');
  cv.width = S;
  cv.height = S;
  const c = cv.getContext('2d');
  const o = borda + 2;
  if (borda) {
    for (let k = 0; k < 24; k++) {
      const a = (k / 24) * Math.PI * 2;
      c.drawImage(im, o + Math.cos(a) * borda, o + Math.sin(a) * borda, tam, tam);
    }
    c.globalCompositeOperation = 'source-in';
    c.fillStyle = '#FFFDF6';
    c.fillRect(0, 0, S, S);
    c.globalCompositeOperation = 'source-over';
  }
  c.drawImage(im, o, o, tam, tam);
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(giro + (fixo ? 0 : balanco(cx, cy, tam / 2)));
  const [dx, dy, blur, a] = sombra;
  ctx.shadowColor = `rgba(60,40,10,${a})`;
  ctx.shadowBlur = blur;
  ctx.shadowOffsetX = dx;
  ctx.shadowOffsetY = dy;
  ctx.drawImage(cv, -S / 2, -S / 2);
  ctx.restore();
};

// Foto impressa jogada sobre o papel: entra de fora girando e erguida, derrapa, assenta inclinada e balança.
// larg: largura da foto com a borda. de: ângulo de onde ela vem (radianos, 0 = direita). corte: [x, y, w, h] em frações da imagem.
export const foto = (ctx, t, t0, nome, cx, cy, larg, {giro = 0.05, de = 0.6, corte = null, prop = null} = {}) => {
  const im = IMAGENS['foto/' + nome];
  const k = (t - t0) / 0.6;
  if (!im || k <= 0) return;
  const [sx, sy, sw, sh] = corte ? [corte[0] * im.width, corte[1] * im.height, corte[2] * im.width, corte[3] * im.height] : [0, 0, im.width, im.height];
  const razao = prop || sw / sh;
  const borda = larg * 0.045;
  const w = larg - borda * 2;
  const h = w / razao;
  // Voo: sai de longe e desacelera, com um pequeno passo além do ponto e volta.
  const u = Math.min(1, k);
  const vai = 1 - Math.pow(1 - u, 3);
  const passa = Math.sin(Math.min(1, k) * Math.PI) * 0.04;
  const dist = 1500 * (1 - vai) - 30 * passa;
  const x = cx + Math.cos(de) * dist;
  const y = cy + Math.sin(de) * dist;
  const ergue = 1 - suave(Math.min(1, k * 1.15));
  const ang = giro + (1 - vai) * 0.9 * (Math.cos(de) >= 0 ? 1 : -1) + (k >= 1 ? balanco(cx, cy, larg / 2) : 0);
  const esc = 1 + 0.08 * ergue;
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(ang);
  ctx.scale(esc, esc);
  ctx.shadowColor = `rgba(60,40,10,${0.3 + 0.1 * ergue})`;
  ctx.shadowBlur = 16 + 30 * ergue;
  ctx.shadowOffsetX = 8 + 26 * ergue;
  ctx.shadowOffsetY = 14 + 40 * ergue;
  ctx.fillStyle = '#FFFDF6';
  ctx.fillRect(-larg / 2, -(h + borda * 2) / 2, larg, h + borda * 2);
  ctx.shadowColor = 'transparent';
  ctx.imageSmoothingQuality = 'high';
  // A imagem cobre a janela da foto, sem deformar.
  const r0 = sw / sh;
  let [cx0, cy0, cw, ch] = [sx, sy, sw, sh];
  if (r0 > razao) {
    cw = sh * razao;
    cx0 = sx + (sw - cw) / 2;
  } else {
    ch = sw / razao;
    cy0 = sy + (sh - ch) / 2;
  }
  ctx.drawImage(im, cx0, cy0, cw, ch, -w / 2, -h / 2, w, h);
  // Um brilho leve de papel fotográfico.
  const g = ctx.createLinearGradient(-w / 2, -h / 2, w / 2, h / 2);
  g.addColorStop(0, 'rgba(255,255,255,0.10)');
  g.addColorStop(0.5, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(-w / 2, -h / 2, w, h);
  ctx.restore();
};

// Botão vermelho em volume, no mesmo acabamento dos emojis 3D: caixa escura e cúpula brilhante.
export const botao3d = (ctx, cx, cy, r, aperta = 0) => {
  ctx.save();
  ctx.shadowColor = 'rgba(60,40,10,0.3)';
  ctx.shadowBlur = 18;
  ctx.shadowOffsetX = 8;
  ctx.shadowOffsetY = 14;
  const cil = (y, rx, ry, h, topo, lado1, lado2) => {
    const g = ctx.createLinearGradient(cx - rx, 0, cx + rx, 0);
    g.addColorStop(0, lado1);
    g.addColorStop(0.45, lado2);
    g.addColorStop(1, lado1);
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.ellipse(cx, y + h, rx, ry, 0, 0, Math.PI);
    ctx.lineTo(cx - rx, y);
    ctx.ellipse(cx, y, rx, ry, 0, Math.PI, 0, true);
    ctx.closePath();
    ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.fillStyle = topo;
    ctx.beginPath();
    ctx.ellipse(cx, y, rx, ry, 0, 0, Math.PI * 2);
    ctx.fill();
  };
  cil(cy, r * 1.35, r * 0.48, r * 0.5, (() => {
    const g = ctx.createLinearGradient(0, cy - r * 0.5, 0, cy + r * 0.5);
    g.addColorStop(0, '#6C7780');
    g.addColorStop(1, '#474F57');
    return g;
  })(), '#2B3238', '#59636C');
  const h = r * (0.34 - 0.2 * aperta);
  const y = cy - h;
  const topo = ctx.createRadialGradient(cx - r * 0.3, y - r * 0.15, r * 0.05, cx, y, r);
  topo.addColorStop(0, '#FF9A8C');
  topo.addColorStop(0.35, '#F2493A');
  topo.addColorStop(1, '#A81E16');
  cil(y, r * 0.85, r * 0.3, h, topo, '#8E1A13', '#D8392B');
  ctx.fillStyle = 'rgba(255,255,255,0.55)';
  ctx.beginPath();
  ctx.ellipse(cx - r * 0.32, y - r * 0.08, r * 0.22, r * 0.07, -0.2, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
};

// Interruptor de parede em volume: espelho claro com bisel e tecla que desce.
export const interruptor3d = (ctx, cx, cy, desligado) => {
  const w = 240;
  const h = 330;
  ctx.save();
  ctx.shadowColor = 'rgba(60,40,10,0.3)';
  ctx.shadowBlur = 20;
  ctx.shadowOffsetX = 8;
  ctx.shadowOffsetY = 14;
  const g = ctx.createLinearGradient(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2);
  g.addColorStop(0, '#FFFFFF');
  g.addColorStop(1, '#D9D3C6');
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.roundRect(cx - w / 2, cy - h / 2, w, h, 26);
  ctx.fill();
  ctx.shadowColor = 'transparent';
  // Rebaixo da tecla.
  ctx.fillStyle = '#BDB5A5';
  ctx.beginPath();
  ctx.roundRect(cx - 52, cy - 105, 104, 210, 14);
  ctx.fill();
  // Tecla: a metade que está para cima fica em evidência.
  const t = ctx.createLinearGradient(0, cy - 100, 0, cy + 100);
  t.addColorStop(0, desligado ? '#E9E4D8' : '#FFFFFF');
  t.addColorStop(0.5, desligado ? '#FFFFFF' : '#F1ECE1');
  t.addColorStop(0.5, desligado ? '#F1ECE1' : '#C9C1B1');
  t.addColorStop(1, desligado ? '#C9C1B1' : '#E9E4D8');
  ctx.fillStyle = t;
  ctx.beginPath();
  ctx.roundRect(cx - 44, cy - 97, 88, 194, 10);
  ctx.fill();
  ctx.fillStyle = desligado ? '#9AA6AE' : '#E4572E';
  ctx.beginPath();
  ctx.arc(cx, desligado ? cy + 60 : cy - 60, 9, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
};
