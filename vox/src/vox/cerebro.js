import {CORAL, IMAGENS, adesivo, recorte, salta} from './estilo';

// Cérebro: emoji 3D da Microsoft (Fluent Emoji, licença MIT), de lado, a frente virada para a esquerda.
// Unidades onde a largura do cérebro é 1 e o centro dele é (0, 0).
// No PNG de 256 px o cérebro ocupa 224 px de largura, centrado em (132, 126).
const LARG = 224 / 256;
const DX = (128 - 132) / 224;
const DY = (128 - 126) / 224;

// Rede de modo padrão (coral) e rede de tarefa (azul), em aproximação lateral:
// pré-frontal medial, pré-cúneo e cingulado posterior, giro angular, temporal lateral.
export const REDE = [[-0.39, -0.06, 0.1, 0.085], [0.2, -0.26, 0.09, 0.075], [0.34, -0.06, 0.08, 0.075], [0.0, 0.2, 0.12, 0.06]];
export const TAREFA = [[-0.24, -0.25, 0.085, 0.07], [-0.07, -0.3, 0.07, 0.06], [0.13, -0.13, 0.08, 0.065]];

// rede e tarefa: intensidade de 0 a 1 de cada rede. p: entrada do adesivo (0 a 1, com salto).
export const cerebro = (ctx, {cx, cy, s = 600, rede = 0, tarefa = 0, p = 1, pulso = 0, seed = 1} = {}) => {
  if (p <= 0) return;
  const e = p < 1 ? salta(p) : 1;
  ctx.save();
  ctx.translate(cx, cy);
  ctx.scale(e, e);
  ctx.translate(-cx, -cy);
  const tam = s / LARG;
  const [ix, iy] = [cx + DX * s, cy + DY * s];
  ctx.imageSmoothingQuality = 'high';
  adesivo(ctx, 'brain', ix, iy, tam, {borda: Math.max(8, s * 0.018)});
  // As regiões acendem por cima do emoji, presas ao contorno dele.
  const im = IMAGENS.brain;
  const acende = (lista, cor, k) => {
    if (k <= 0.01 || !im) return;
    const S = Math.ceil(tam);
    const cv = document.createElement('canvas');
    cv.width = S;
    cv.height = S;
    const c = cv.getContext('2d');
    c.imageSmoothingQuality = 'high';
    // Brilho: núcleo claro e halo na cor da rede.
    const [r, g, b] = cor === CORAL ? [255, 96, 40] : [40, 140, 210];
    lista.forEach(([x, y, rx], i) => {
      const bt = 1 + pulso * 0.08 * Math.sin(i * 1.7);
      const gx = S / 2 + (x - DX) * s;
      const gy = S / 2 + (y - DY) * s;
      const R = rx * s * 1.9 * bt * (0.6 + 0.4 * k);
      const gr = c.createRadialGradient(gx, gy, 0, gx, gy, R);
      gr.addColorStop(0, `rgba(255,236,190,${0.95 * k})`);
      gr.addColorStop(0.35, `rgba(${r},${g},${b},${0.85 * k})`);
      gr.addColorStop(1, `rgba(${r},${g},${b},0)`);
      c.fillStyle = gr;
      c.fillRect(gx - R, gy - R, R * 2, R * 2);
    });
    // Mantém o brilho só dentro do cérebro.
    c.globalCompositeOperation = 'destination-in';
    c.drawImage(im, 0, 0, S, S);
    ctx.drawImage(cv, ix - S / 2, iy - S / 2);
  };
  acende(TAREFA, 'azul', tarefa);
  acende(REDE, CORAL, rede);
  ctx.restore();
};

// Coração de papel que bate.
export const coracaoPapel = (ctx, cx, cy, r, bate = 0, cor = CORAL, seed = 70) => {
  const k = 1 + 0.12 * bate;
  const pts = Array.from({length: 60}, (_, i) => {
    const a = (i / 60) * Math.PI * 2;
    const x = 16 * Math.sin(a) ** 3;
    const y = -(13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a));
    return [cx + (x / 16) * r * k, cy + (y / 16) * r * k];
  });
  recorte(ctx, pts, {cor, seed, borda: 6});
};
