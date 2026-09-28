import {CORAL, TINTA, adesivo, balanco, camera, foto, gira, papel, pincel, salta, seta, suave, texto} from './estilo';
import {REDE, cerebro} from './cerebro';

// Cenas novas, no mesmo estilo e com as mesmas regras: só os dois terços de cima (até y = 1280),
// sem títulos, só etiqueta de estudo, dados e texto citado.

// Faz uma peça surgir com um pequeno salto de escala e balançar em torno de (cx, cy).
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
// Adesivo que surge a partir do segundo t0.
const cola = (ctx, t, t0, nome, x, y, tam, op = {}) => surge(ctx, (t - t0) / 0.45, x, y, () => adesivo(ctx, nome, x, y, tam, op), tam / 2);
const fundo = (ctx, t, dur) => {
  camera(ctx, t, {z: 1 + 0.03 * suave(t / dur), cy: 640});
  papel(ctx);
};

// Cena 4. O "hack secreto": cadeado brilhando, com aspas irônicas.
const hack = (ctx, t) => {
  fundo(ctx, t, 8);
  cola(ctx, t, 0.3, 'locked', 540, 640, 420);
  [[330, 430, 130, 1.0], [780, 500, 110, 1.3], [720, 860, 90, 1.6]].forEach(([x, y, s, t0], i) => {
    const brilho = 1 + 0.12 * Math.sin(t * 5 + i * 2);
    cola(ctx, t, t0, 'sparkles', x, y, s * brilho);
  });
  texto(ctx, '“', {x: 290, y: 420, tam: 420, fonte: 'Caveat', cor: CORAL, p: (t - 2.4) / 0.2});
  texto(ctx, '”', {x: 800, y: 960, tam: 420, fonte: 'Caveat', cor: CORAL, p: (t - 2.7) / 0.2});
};

// Cena 5. "As telas destruíram a rede": o cérebro racha e leva um carimbo de dúvida.
const RACHAS = [
  [[700, 780], [650, 740], [630, 690], [590, 660]],
  [[700, 780], [760, 820], [790, 880], [840, 910]],
  [[700, 780], [690, 850], [720, 910], [700, 970]],
  [[650, 740], [610, 780], [570, 780]],
  [[760, 820], [800, 780], [850, 775]],
];
const telas = (ctx, t) => {
  fundo(ctx, t, 8);
  foto(ctx, t, 0.2, 'celular-cama', 400, 400, 600, {giro: -0.06, de: Math.PI + 0.5});
  cerebro(ctx, {cx: 700, cy: 820, s: 440, p: suave((t - 1.0) / 0.5)});
  gira(ctx, 700, 820, 220, () => RACHAS.forEach((r, i) => pincel(ctx, r, {larg: 6, cor: TINTA, seed: 500 + i, seco: 0, ponta: 0.6, p: suave((t - 2.2 - i * 0.15) / 0.5)})));
  // Carimbo "?": entra grande e bate no papel.
  const k = (t - 4) / 0.25;
  if (k > 0) {
    const e = 1 + 0.8 * Math.max(0, 1 - k);
    ctx.save();
    ctx.translate(290, 1060);
    ctx.rotate(-0.12 + balanco(290, 1060, 150));
    ctx.scale(e, e);
    ctx.globalAlpha = Math.min(1, k) * 0.9;
    ctx.lineWidth = 12;
    ctx.strokeStyle = CORAL;
    ctx.beginPath();
    ctx.arc(0, 0, 130, 0, Math.PI * 2);
    ctx.stroke();
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(0, 0, 108, 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillStyle = CORAL;
    ctx.font = '600 170px "Oswald"';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('?', 0, 8);
    ctx.restore();
  }
};

// Cena 7. A rede existe: as regiões acendem uma a uma e se ligam.
const redeExiste = (ctx, t) => {
  fundo(ctx, t, 9);
  const [cx, cy, s] = [540, 660, 720];
  const reg = REDE.map((_, i) => suave((t - 1.5 - i * 0.6) / 0.5));
  cerebro(ctx, {cx, cy, s, regioes: reg, pulso: Math.sin(t * 4), p: suave((t - 0.3) / 0.5)});
  // As ligações entre as regiões: é uma rede.
  const P = REDE.map(([x, y]) => [cx + x * s, cy + y * s]);
  const pares = [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]];
  gira(ctx, cx, cy, s / 2, () => pares.forEach(([a, b], i) => {
    const [x0, y0] = P[a];
    const [x1, y1] = P[b];
    const meio = [(x0 + x1) / 2 + (y1 - y0) * 0.12, (y0 + y1) / 2 - (x1 - x0) * 0.12];
    pincel(ctx, [[x0, y0], meio, [x1, y1]], {larg: 6, cor: CORAL, seed: 700 + i, seco: 0.2, p: suave((t - 4.2 - i * 0.25) / 0.6)});
  }));
};

// Balão de pensamento com coisas surgindo dentro, e o cérebro embaixo à esquerda.
const balao = (ctx, t) => {
  cerebro(ctx, {cx: 250, cy: 1080, s: 280, p: suave((t - 0.1) / 0.5)});
  cola(ctx, t, 0.5, 'thought_balloon', 600, 560, 760);
};

// Cena 9. Vantagem evolutiva: a mente antecipa o predador, a chuva, a comida.
const vantagem = (ctx, t) => {
  fundo(ctx, t, 9);
  balao(ctx, t);
  foto(ctx, t, 1.2, 'leao', 600, 540, 470, {giro: 0.05, de: -0.4, corte: [0.28, 0.2, 0.5, 0.75]});
  cola(ctx, t, 2.0, 'cloud_with_rain', 860, 360, 160);
  cola(ctx, t, 2.5, 'meat_on_bone', 400, 760, 150);
};

// Cena 10. Defeito evolutivo: a mesma máquina, agora girando em preocupações modernas.
const defeito = (ctx, t) => {
  fundo(ctx, t, 9);
  balao(ctx, t);
  const itens = ['envelope', 'money_with_wings', 'mobile_phone', 'bell'];
  const vel = 0.5 + 0.12 * Math.max(0, t - 2);
  const giro = (t - 2) * vel;
  itens.forEach((nome, i) => {
    const a = giro + (i / itens.length) * Math.PI * 2;
    const x = 600 + Math.cos(a) * 190;
    const y = 580 + Math.sin(a) * 120;
    cola(ctx, t, 1.3 + i * 0.35, nome, x, y, 140);
  });
  foto(ctx, t, 4.0, 'estresse-computador', 690, 1060, 470, {giro: 0.06, de: 0.3});
};

// Cena 11. Cabeça vazia, oficina: engrenagem, ferramentas e o diabinho dentro da cabeça.
const oficina = (ctx, t) => {
  fundo(ctx, t, 8);
  cola(ctx, t, 0.3, 'bust_in_silhouette', 540, 700, 620);
  surge(ctx, (t - 1.2) / 0.45, 540, 540, () => {
    ctx.save();
    ctx.translate(540, 540);
    ctx.rotate(t * 0.9);
    ctx.translate(-540, -540);
    adesivo(ctx, 'gear', 540, 540, 190, {fixo: true});
    ctx.restore();
  });
  cola(ctx, t, 1.9, 'hammer_and_wrench', 400, 650, 140, {giro: -0.2});
  cola(ctx, t, 2.6, 'smiling_face_with_horns', 690, 650, 140);
};

// Galhos: árvore de cenários que se abre a partir de um ponto, nível por nível.
const galhos = (x0, y0, niveis, abre, sobe, seed) => {
  const r = [];
  const cresce = (x, y, ang, nivel, id) => {
    if (nivel >= niveis) return;
    const len = sobe * Math.pow(0.85, nivel);
    const x1 = x + Math.sin(ang) * len;
    const y1 = y - Math.cos(ang) * len;
    const meio = [(x + x1) / 2 + Math.cos(ang) * 12 * (id % 2 ? 1 : -1), (y + y1) / 2];
    r.push({pts: [[x, y], meio, [x1, y1]], nivel, fim: nivel === niveis - 1, x1, y1, ang, seed: seed + r.length});
    const d = abre * Math.pow(0.97, nivel);
    cresce(x1, y1, ang - d, nivel + 1, id * 2);
    cresce(x1, y1, ang + d, nivel + 1, id * 2 + 1);
  };
  cresce(x0, y0, 0, 0, 1);
  return r;
};
const ARVORE = galhos(540, 1080, 4, 0.5, 200, 800);
const PONTAS = ['cloud_with_rain', 'money_with_wings', 'fire', 'anxious_face_with_sweat', 'envelope', 'wilted_flower', 'bell', 'hourglass_not_done'];

// Cena 12. Galhos de cenários: cada pensamento se abre em outros.
const cenarios = (ctx, t) => {
  fundo(ctx, t, 10);
  cerebro(ctx, {cx: 540, cy: 1130, s: 240, p: suave((t - 0.1) / 0.5)});
  let n = 0;
  ARVORE.forEach((g) => {
    pincel(ctx, g.pts, {larg: 12 - g.nivel * 2, cor: TINTA, seed: g.seed, seco: 0.3, p: suave((t - 0.7 - g.nivel * 0.75) / 0.75)});
    if (g.fim) {
      cola(ctx, t, 3.8 + n * 0.12, PONTAS[n % PONTAS.length], g.x1 + Math.sin(g.ang) * 55, g.y1 - Math.cos(g.ang) * 55, 95);
      n++;
    }
  });
};

// Cena 15. Plantar, prever, resolver andando.
const plantar = (ctx, t) => {
  fundo(ctx, t, 9);
  foto(ctx, t, 0.3, 'maos-plantando', 330, 400, 500, {giro: -0.05, de: Math.PI + 0.4});
  seta(ctx, [[610, 380], [680, 350], [740, 380]], {larg: 8, seed: 900, p: suave((t - 1.8) / 0.5)});
  cola(ctx, t, 2.4, 'crystal_ball', 850, 440, 250);
  seta(ctx, [[820, 620], [760, 740], [680, 800]], {larg: 8, seed: 901, p: suave((t - 3.7) / 0.5)});
  cola(ctx, t, 4.3, 'person_walking', 500, 920, 300);
  cola(ctx, t, 5.2, 'light_bulb', 620, 740, 140);
};

// Cena 16. Bumerangue: o pensamento vai e volta, e vai de novo.
const bumerangue = (ctx, t) => {
  fundo(ctx, t, 8);
  const [bx, by] = [260, 780];
  const volta = (u) => {
    // Elipse que sai do cérebro e volta para ele.
    const a = Math.PI + 0.4 + u * Math.PI * 2;
    return [620 + Math.cos(a) * 360, 620 - Math.sin(a) * 250];
  };
  const lances = [[1.0, 3.6], [4.2, 6.8]];
  const ativo = lances.find(([a, b]) => t >= a && t <= b);
  // Rastro tracejado do lance atual.
  if (ativo) {
    const u = suave((t - ativo[0]) / (ativo[1] - ativo[0]));
    const rastro = Array.from({length: 40}, (_, i) => volta((u * i) / 39));
    ctx.save();
    ctx.setLineDash([6, 22]);
    pincel(ctx, rastro, {larg: 5, cor: '#8C9BA3', seed: 950, seco: 0, ponta: 0.1});
    ctx.restore();
  }
  const chegou = lances.some(([, b]) => t > b && t < b + 0.3);
  cerebro(ctx, {cx: bx, cy: by, s: 330 * (chegou ? 1.05 : 1), p: suave((t - 0.2) / 0.5)});
  const u = ativo ? suave((t - ativo[0]) / (ativo[1] - ativo[0])) : 0;
  const [x, y] = ativo ? volta(u) : volta(0);
  if (t > 0.6) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(ativo ? t * 14 : 0.4);
    ctx.translate(-x, -y);
    adesivo(ctx, 'boomerang', x, y, 150, {fixo: true});
    ctx.restore();
  }
};

// Cena 17. Os galhos crescem e batem na parede: não há saída.
const parede = (ctx, t) => {
  fundo(ctx, t, 9);
  // Parede de tijolos à direita.
  for (let l = 0; l < 7; l++) {
    for (let c = 0; c < 2; c++) {
      const x = 850 + c * 150;
      const y = 260 + l * 135;
      cola(ctx, t, 0.3 + l * 0.05 + c * 0.03, 'brick', x, y, 170);
    }
  }
  cerebro(ctx, {cx: 190, cy: 700, s: 260, p: suave((t - 0.6) / 0.5)});
  const alvos = [360, 540, 700, 860, 1040];
  alvos.forEach((ya, i) => {
    const t0 = 1.4 + i * 0.6;
    const pts = [[300, 700], [520, 700 + (ya - 700) * 0.5 + (i % 2 ? 30 : -30)], [760, ya]];
    pincel(ctx, pts, {larg: 9, cor: TINTA, seed: 1000 + i, seco: 0.3, p: suave((t - t0) / 0.6)});
    cola(ctx, t, t0 + 0.6, 'collision', 770, ya, 110);
  });
};

export const CENAS2 = {
  '04-hack': {f: hack, dur: 8, sons: [[0.3, 'pop'], [1.0, 'bip', 0.6], [1.3, 'bip', 0.6], [1.6, 'bip', 0.6]]},
  '05-telas': {f: telas, dur: 8, sons: [[0.2, 'swoosh', 0.7], [1.0, 'pop'], [4.0, 'clique']]},
  '07-rede': {f: redeExiste, dur: 9, sons: [[0.3, 'pop'], ...REDE.map((_, i) => [1.5 + i * 0.6, 'bip', 0.7])]},
  '09-vantagem': {f: vantagem, dur: 9, sons: [[0.1, 'pop'], [0.5, 'pop'], [1.2, 'swoosh', 0.7], [2.0, 'pop'], [2.5, 'pop']]},
  '10-defeito': {f: defeito, dur: 9, sons: [[0.1, 'pop'], [0.5, 'pop'], ...[0, 1, 2, 3].map((i) => [1.3 + i * 0.35, 'pop']), [4.0, 'swoosh', 0.7]]},
  '11-oficina': {f: oficina, dur: 8, sons: [[0.3, 'pop'], [1.2, 'pop'], [1.9, 'pop'], [2.6, 'pop']]},
  '12-cenarios': {f: cenarios, dur: 10, sons: [[0.1, 'pop'], ...Array.from({length: 8}, (_, i) => [3.8 + i * 0.12, 'pop', 0.6])]},
  '15-plantar': {f: plantar, dur: 9, sons: [[0.3, 'swoosh', 0.7], [2.4, 'pop'], [4.3, 'pop'], [5.2, 'bip']]},
  '16-bumerangue': {f: bumerangue, dur: 8, sons: [[0.2, 'pop'], [1.0, 'swoosh'], [3.6, 'pop'], [4.2, 'swoosh'], [6.8, 'pop']]},
  '17-parede': {f: parede, dur: 9, sons: [[0.3, 'pop', 0.7], [0.6, 'pop'], ...[0, 1, 2, 3, 4].map((i) => [2.0 + i * 0.6, 'clique', 0.8])]},
};
