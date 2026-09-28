import {ellipse, rng} from '../lib/util';
import {CORAL, TINTA, adesivo, foto, marcador, pincel, recorte, salta, seta, suave, texto} from './estilo';
import {cola, fundo, surge} from './pecas';

// Lote B: o estudo de Killingsworth e Gilbert (2010) e a linha do tempo.

const ESTUDO = 'Killingsworth e Gilbert, 2010 · Science';
const etiqueta = (ctx, t, t0 = 0) => texto(ctx, ESTUDO, {y: 120, tam: 38, estilo: 'italic', etiqueta: '#FFFDF6', p: suave((t - t0) / 0.6) * 3});

// Cena 20. Milênios de história humana e o celular só no finalzinho.
const linhaTempo = (ctx, t) => {
  fundo(ctx, t, 10);
  foto(ctx, t, 0.3, 'pintura-rupestre', 420, 470, 700, {giro: -0.05, de: Math.PI + 0.3});
  const [x0, x1, y] = [90, 990, 930];
  pincel(ctx, [[x0, y], [(x0 + x1) / 2, y - 4], [x1, y]], {larg: 10, seed: 2000, seco: 0.3, ponta: 0.05, p: suave((t - 1.2) / 1.8)});
  pincel(ctx, [[x0, y - 26], [x0, y + 26]], {larg: 8, seed: 2001, p: suave((t - 1.2) / 0.3)});
  texto(ctx, '300 mil anos', {x: x0, y: y + 80, tam: 58, fonte: 'Oswald', peso: '600', alinha: 'left', p: (t - 3.0) / 0.5});
  pincel(ctx, [[x1, y - 26], [x1, y + 26]], {larg: 8, cor: CORAL, seed: 2002, p: suave((t - 3.8) / 0.3)});
  cola(ctx, t, 4.2, 'mobile_phone', x1 - 60, y - 150, 170, {giro: 0.1});
  texto(ctx, '2007', {x: x1, y: y + 80, tam: 58, fonte: 'Oswald', peso: '600', cor: CORAL, alinha: 'right', p: (t - 4.6) / 0.3});
};

// Cena 23. As 2.250 pessoas do estudo, um ponto para cada uma.
const COLS = 50;
const LINS = 45;
const ORDEM = (() => {
  const r = rng(2300);
  const a = Array.from({length: COLS * LINS}, (_, i) => i);
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(r() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  const pos = new Array(a.length);
  a.forEach((v, k) => (pos[v] = k));
  return pos;
})();
const pontos = (ctx, t) => {
  fundo(ctx, t, 10);
  etiqueta(ctx, t);
  const n = COLS * LINS;
  ctx.save();
  for (let i = 0; i < n; i++) {
    const k = (t - 1.0 - (4.0 * ORDEM[i]) / n) / 0.25;
    if (k <= 0) continue;
    const c = i % COLS;
    const l = Math.floor(i / COLS);
    const r = 5.5 * Math.min(1, salta(k));
    ctx.fillStyle = '#4A4038';
    ctx.beginPath();
    ctx.arc(99 + c * 18, 250 + l * 18, r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
  texto(ctx, '2.250', {y: 1150, tam: 120, fonte: 'Oswald', peso: '600', p: (t - 5.3) / 0.3});
};

// Cartão de notificação: sino, e a pergunta do aplicativo entre aspas.
const notificacao = (ctx, k, y, linhas, seed) => {
  surge(ctx, k, 540, y, () => {
    const h = 50 * linhas.length + 54;
    recorte(ctx, [[80, y - h / 2], [1000, y - h / 2 + 3], [998, y + h / 2], [82, y + h / 2 - 2]], {cor: '#FFFDF6', borda: 6, seed, sombra: [6, 10, 14, 0.28]});
    adesivo(ctx, 'bell', 150, y, 80, {borda: 5, fixo: true});
    linhas.forEach((l, j) => texto(ctx, l, {x: 215, y: y - ((linhas.length - 1) * 50) / 2 + j * 50, tam: 42, alinha: 'left'}));
  }, 460);
};
// Cena 24. O aplicativo tocava em horas aleatórias e fazia três perguntas.
const notificacoes = (ctx, t) => {
  fundo(ctx, t, 10);
  etiqueta(ctx, t);
  foto(ctx, t, 0.3, 'celular-maos', 540, 520, 600, {giro: -0.04, de: Math.PI / 2, corte: [0.2, 0.05, 0.6, 0.85]});
  notificacao(ctx, (t - 2.0) / 0.45, 895, ['“Como você está se sentindo agora?”'], 2400);
  notificacao(ctx, (t - 3.6) / 0.45, 1015, ['“O que você está fazendo agora?”'], 2401);
  notificacao(ctx, (t - 5.2) / 0.45, 1165, ['“Está pensando em algo diferente', 'do que está fazendo?”'], 2402);
};

// Cena 25. Mente vagando em 46,9% do tempo.
const fatia = (cx, cy, r, a0, a1, n = 60) => [[cx, cy], ...Array.from({length: n + 1}, (_, i) => {
  const a = a0 + ((a1 - a0) * i) / n;
  return [cx + Math.cos(a) * r, cy + Math.sin(a) * r];
})];
const porcento = (ctx, t) => {
  fundo(ctx, t, 8);
  etiqueta(ctx, t);
  const [cx, cy, r] = [540, 620, 340];
  surge(ctx, (t - 0.4) / 0.45, cx, cy, () => {
    recorte(ctx, ellipse(cx, cy, r, r, 90), {cor: '#FBF6E9', borda: 8, seed: 2500, sombra: [8, 14, 18, 0.28]});
    const k = suave((t - 1.2) / 1.8);
    if (k > 0.002) recorte(ctx, fatia(cx, cy, r - 14, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * 0.469 * k), {cor: CORAL, seed: 2501, sombra: [3, 5, 6, 0.2]});
  }, r);
  cola(ctx, t, 3.2, 'thought_balloon', cx + 150, cy - 70, 150);
  texto(ctx, '46,9%', {y: 1110, tam: 130, fonte: 'Oswald', peso: '600', p: (t - 3.0) / 0.3});
};

// Cena 26. A escala de felicidade: com a mente no que está fazendo, a pessoa fica mais feliz.
const escala = (ctx, t) => {
  fundo(ctx, t, 9);
  etiqueta(ctx, t);
  const [x0, x1, y] = [130, 950, 780];
  pincel(ctx, [[x0, y], [x1, y]], {larg: 12, seed: 2600, seco: 0.2, ponta: 0.05, p: suave((t - 0.5) / 1.0)});
  [[x0, '0'], [x1, '100']].forEach(([x, s], i) => {
    pincel(ctx, [[x, y - 28], [x, y + 28]], {larg: 8, seed: 2601 + i, p: suave((t - 1.2) / 0.3)});
    texto(ctx, s, {x, y: y + 80, tam: 48, fonte: 'Oswald', peso: '600', p: (t - 1.4) / 0.3});
  });
  // Posições relativas, sem números: vagando fica abaixo de focado.
  const xf = x0 + (x1 - x0) * 0.66;
  const xv = x0 + (x1 - x0) * 0.56;
  cola(ctx, t, 2.0, 'round_pushpin', xf, y - 50, 90);
  pincel(ctx, [[xf, y - 90], [xf, y - 330]], {larg: 4, cor: '#8C9BA3', seed: 2610, seco: 0, p: suave((t - 2.1) / 0.3)});
  cola(ctx, t, 2.2, 'slightly_smiling_face', xf, y - 420, 190);
  cola(ctx, t, 3.4, 'round_pushpin', xv, y - 50, 90);
  pincel(ctx, [[xv, y - 90], [xv, y - 150]], {larg: 4, cor: '#8C9BA3', seed: 2611, seco: 0, p: suave((t - 3.5) / 0.3)});
  cola(ctx, t, 3.6, 'thought_balloon', xv - 40, y - 240, 190);
};

// Cena 27. O nome do estudo, citado.
const nomeEstudo = (ctx, t) => {
  fundo(ctx, t, 8);
  etiqueta(ctx, t);
  surge(ctx, (t - 0.5) / 0.45, 540, 640, () => {
    recorte(ctx, [[110, 420], [970, 426], [966, 860], [114, 856]], {cor: '#FFFDF6', borda: 8, seed: 2700, sombra: [8, 14, 18, 0.3]});
    marcador(ctx, 190, 735, 700, 90, suave((t - 3.6) / 0.7), {seed: 2701});
    texto(ctx, '“A wandering mind', {y: 560, tam: 80, estilo: 'italic', p: (t - 1.0) / 1.0});
    texto(ctx, 'is an unhappy mind”', {y: 735, tam: 80, estilo: 'italic', p: (t - 2.1) / 1.0});
  }, 440);
};

// Arco suave de x0 a x1 na altura y, com flecha (curva negativa sobe).
const arco = (x0, x1, y, curva) => Array.from({length: 24}, (_, i) => {
  const u = i / 23;
  return [x0 + (x1 - x0) * u, y + curva * Math.sin(u * Math.PI)];
});

// Cena 28. A seta do tempo: a mente vaga antes, a infelicidade vem depois (e não o contrário).
const setaTempo = (ctx, t) => {
  fundo(ctx, t, 9);
  etiqueta(ctx, t);
  seta(ctx, [[120, 1060], [540, 1056], [960, 1060]], {larg: 9, cor: '#8C9BA3', seed: 2800, p: suave((t - 0.4) / 1.0)});
  cola(ctx, t, 1.0, 'thought_balloon', 280, 660, 280);
  seta(ctx, arco(390, 690, 470, -90), {larg: 10, cor: CORAL, seed: 2801, p: suave((t - 1.8) / 0.8)});
  cola(ctx, t, 2.6, 'pensive_face', 800, 660, 260);
  seta(ctx, arco(690, 390, 860, 80), {larg: 8, cor: '#8C9BA3', seed: 2802, p: suave((t - 4.0) / 0.8)});
  cola(ctx, t, 5.0, 'cross_mark', 540, 920, 110);
};

export const CENAS3 = {
  '20-linha-tempo': {f: linhaTempo, dur: 10, sons: [[0.3, 'swoosh', 0.7], [1.2, 'swoosh', 0.5], [4.2, 'pop'], [4.6, 'bip']]},
  '23-pontos': {f: pontos, dur: 10, sons: [[0.05, 'etiqueta'], [5.3, 'bip']]},
  '24-notificacoes': {f: notificacoes, dur: 10, sons: [[0.05, 'etiqueta'], [0.3, 'swoosh', 0.7], [2.0, 'bip'], [3.6, 'bip'], [5.2, 'bip']]},
  '25-porcento': {f: porcento, dur: 8, sons: [[0.05, 'etiqueta'], [0.4, 'pop'], [1.2, 'swoosh', 0.6], [3.0, 'bip'], [3.2, 'pop']]},
  '26-escala': {f: escala, dur: 9, sons: [[0.05, 'etiqueta'], [2.0, 'pop'], [2.2, 'pop'], [3.4, 'pop'], [3.6, 'pop']]},
  '27-nome-estudo': {f: nomeEstudo, dur: 8, sons: [[0.05, 'etiqueta'], [0.5, 'pop']]},
  '28-seta-tempo': {f: setaTempo, dur: 9, sons: [[0.05, 'etiqueta'], [1.0, 'pop'], [2.6, 'pop'], [5.0, 'clique']]},
};
