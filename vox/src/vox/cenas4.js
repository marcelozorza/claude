import {adesivo, balanco, camera, foto, papel, pincel, salta, suave, texto} from './estilo';
import {cerebro} from './cerebro';

// Lote C: Haaland, álcool/sexo/violência, monges, fera domada, Einstein e o violino, bicho acuado.

const surge = (ctx, k, cx, cy, desenha, raio = 150) => {
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
const cola = (ctx, t, t0, nome, x, y, tam, op = {}) => surge(ctx, (t - t0) / 0.45, x, y, () => adesivo(ctx, nome, x, y, tam, op), tam / 2);
const fundo = (ctx, t, dur) => {
  camera(ctx, t, {z: 1 + 0.03 * suave(t / dur), cy: 640});
  papel(ctx);
};

// Cena 3. A rota do voo: o avião cruza o mapa num arco tracejado.
const rota = (ctx, t) => {
  fundo(ctx, t, 9);
  cola(ctx, t, 0.3, 'world_map', 540, 560, 820);
  const [a, b] = [[300, 560], [790, 470]];
  const ponto = (u) => [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u - Math.sin(u * Math.PI) * 230];
  cola(ctx, t, 0.9, 'round_pushpin', a[0], a[1] - 40, 90);
  cola(ctx, t, 1.1, 'round_pushpin', b[0], b[1] - 40, 90);
  const u = suave((t - 1.6) / 3.2);
  if (u > 0) {
    const n = Math.max(2, Math.floor(u * 30));
    for (let i = 0; i < n; i += 2) pincel(ctx, [ponto(i / 30), ponto(Math.min(u, (i + 1) / 30))], {larg: 6, seed: 3000 + i, seco: 0, ponta: 0.3});
    const [x, y] = ponto(u);
    const [x2, y2] = ponto(Math.min(1, u + 0.01));
    ctx.save();
    ctx.translate(x, y);
    // O emoji do avião aponta para cima à direita (45°).
    ctx.rotate(Math.atan2(y2 - y, x2 - x) + Math.PI / 4);
    ctx.translate(-x, -y);
    adesivo(ctx, 'airplane', x, y, 130, {fixo: true});
    ctx.restore();
  }
};

// Cena 21. Álcool, sexo e violência.
const fugas = (ctx, t) => {
  fundo(ctx, t, 8);
  cola(ctx, t, 0.4, 'wine_glass', 230, 480, 320, {giro: -0.12});
  cola(ctx, t, 1.3, 'kiss_mark', 760, 560, 300);
  cola(ctx, t, 2.2, 'collision', 560, 870, 260);
  cola(ctx, t, 2.1, 'boxing_glove', 470, 960, 320, {giro: 0.15});
};

// Cena 31. Monges meditando: a rede baixa a atividade.
const monges = (ctx, t) => {
  fundo(ctx, t, 10);
  texto(ctx, 'Brewer et al., 2011 · PNAS', {y: 120, tam: 38, estilo: 'italic', etiqueta: '#FFFDF6', p: suave(t / 0.6) * 3});
  foto(ctx, t, 0.3, 'monges', 540, 430, 720, {giro: -0.04, de: Math.PI + 0.4});
  const acesa = suave((t - 1.6) / 0.6) * (1 - 0.8 * suave((t - 3.4) / 2.2));
  cerebro(ctx, {cx: 540, cy: 960, s: 440, rede: acesa, pulso: Math.sin(t * 4) * acesa, p: suave((t - 1.2) / 0.5)});
};

// Cena 32. A fera domada: o leão dorme.
const fera = (ctx, t) => {
  fundo(ctx, t, 8);
  foto(ctx, t, 0.3, 'leao-dormindo', 540, 600, 800, {giro: 0.04, de: -0.3});
  const sobe = Math.sin(t * 1.4) * 14;
  cola(ctx, t, 1.5, 'zzz', 830, 330 + sobe, 180);
};

// Cena 35. Einstein e o violino: tocar para destravar a ideia.
const violino = (ctx, t) => {
  fundo(ctx, t, 9);
  foto(ctx, t, 0.3, 'violinista', 520, 500, 760, {giro: -0.05, de: Math.PI + 0.2});
  const flutua = Math.sin(t * 1.6) * 12;
  cola(ctx, t, 1.4, 'musical_notes', 840, 260 + flutua, 170);
  cola(ctx, t, 2.6, 'light_bulb', 800, 900, 200);
};

// Cena 38. O bicho acuado: o gato assustado treme.
const acuado = (ctx, t) => {
  fundo(ctx, t, 8);
  const treme = t > 1.2 ? 1 : 0;
  ctx.save();
  ctx.translate(Math.sin(t * 43) * 3 * treme, Math.cos(t * 37) * 2 * treme);
  foto(ctx, t, 0.3, 'gato-assustado', 540, 600, 760, {giro: 0.03, de: 0.5, corte: [0.28, 0.4, 0.5, 0.6], prop: 1.1});
  ctx.restore();
};

export const CENAS4 = {
  '03-rota': {f: rota, dur: 9, sons: [[0.3, 'pop'], [0.9, 'pop', 0.6], [1.1, 'pop', 0.6], [1.6, 'swoosh']]},
  '21-fugas': {f: fugas, dur: 8, sons: [[0.4, 'pop'], [1.3, 'pop'], [2.1, 'zap', 0.8]]},
  '31-monges': {f: monges, dur: 10, sons: [[0.05, 'etiqueta'], [0.3, 'swoosh', 0.7], [1.2, 'pop'], [1.6, 'bip', 0.7]]},
  '32-fera': {f: fera, dur: 8, sons: [[0.3, 'swoosh', 0.7], [1.5, 'pop']]},
  '35-violino': {f: violino, dur: 9, sons: [[0.3, 'swoosh', 0.7], [1.4, 'pop'], [2.6, 'bip']]},
  '38-acuado': {f: acuado, dur: 8, sons: [[0.3, 'swoosh', 0.7]]},
};
