import {adesivo, balanco, camera, papel, salta, suave} from './estilo';

// Peças comuns a todas as cenas: entrada com salto, balanço de vida e o fundo de papel.

// Faz uma peça surgir com um pequeno salto de escala e balançar em torno de (cx, cy).
// raio: tamanho aproximado da peça (peças grandes balançam menos).
export const surge = (ctx, k, cx, cy, desenha, raio = 150) => {
  if (k <= 0) return;
  const e = salta(k);
  ctx.save();
  ctx.translate(cx, cy);
  ctx.scale(e, e);
  ctx.rotate(balanco(cx, cy, raio));
  ctx.translate(-cx, -cy);
  desenha();
  ctx.restore();
};

// Emoji 3D colado como adesivo, surgindo a partir do segundo t0.
export const cola = (ctx, t, t0, nome, x, y, tam, op = {}) => surge(ctx, (t - t0) / 0.45, x, y, () => adesivo(ctx, nome, x, y, tam, op), tam / 2);

// Emoji carimbado: cai de cima, maior, e bate no papel com um tranco.
export const carimba = (ctx, t, t0, nome, x, y, tam, {giro = -0.1} = {}) => {
  const k = (t - t0) / 0.22;
  if (k <= 0) return;
  const u = Math.min(1, k);
  const e = 1 + 0.9 * (1 - u) * (1 - u) - (k > 1 && k < 1.6 ? 0.06 * Math.sin((k - 1) * Math.PI / 0.6) : 0);
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(e, e);
  ctx.globalAlpha = Math.min(1, u * 1.5);
  ctx.translate(-x, -y);
  adesivo(ctx, nome, x, y, tam, {giro});
  ctx.restore();
};

// Papel quadriculado com a câmera flutuando e um zoom lento ao longo da cena.
export const fundo = (ctx, t, dur) => {
  camera(ctx, t, {z: 1 + 0.03 * suave(t / dur), cy: 640});
  papel(ctx);
};
