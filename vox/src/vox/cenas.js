import {W, ellipse} from '../lib/util';

import {AZUL, CORAL, CREME, TINTA, adesivo, balanco, gira, botao3d, interruptor3d, camera, laco, marcador, mistura, papel, pincel, recorte, salta, seta, suave, texto} from './estilo';
import {cerebro, coracaoPapel} from './cerebro';

// Cenas de infográfico no estilo Vox, 1080 x 1920, 30 quadros por segundo.
export const FPS = 30;

// Faz uma peça surgir com um pequeno salto de escala em torno de (cx, cy).
// raio: tamanho aproximado da peça, para o balanço (peças grandes giram menos).
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
const contagem = (alvo, k) => Math.round(alvo * suave(k));

// Área útil: os dois terços de cima (até y = 1280). O terço de baixo é do apresentador.
export const LIMITE = 1280;

// Cena 22a. O experimento: 15 minutos sozinho, um relógio e um botão que dá choque.
const choqueSala = (ctx, t) => {
  camera(ctx, t, {z: 1 + 0.03 * suave(t / 9), cy: 640});
  papel(ctx);
  texto(ctx, 'Wilson et al., 2014 · Science', {y: 120, tam: 38, estilo: 'italic', etiqueta: '#FFFDF6', p: suave(t / 0.6) * 3});
  // O relógio, com o arco dos 15 minutos se desenhando em volta.
  surge(ctx, (t - 0.6) / 0.5, 290, 620, () => adesivo(ctx, 'alarm_clock', 290, 620, 300, {giro: -0.06}));
  const arco = Array.from({length: 40}, (_, i) => {
    const a = -Math.PI / 2 + (i / 39) * Math.PI * 0.5 * 4 * 0.25 * 4 * 0.25 * 4;
    return [290 + Math.cos(a) * 205, 620 + Math.sin(a) * 205];
  });
  pincel(ctx, arco.slice(0, 30), {larg: 9, cor: AZUL, seed: 9, p: suave((t - 1.4) / 2.6)});
  texto(ctx, '15 min', {x: 290, y: 880, tam: 64, fonte: 'Caveat', cor: AZUL, p: (t - 3.2) / 0.5});
  // O botão: base de papel, botão vermelho 3D e o raio.
  surge(ctx, (t - 1) / 0.5, 780, 640, () => {
    botao3d(ctx, 780, 660, 120, t > 7 && t < 7.3 ? 1 : 0);
    adesivo(ctx, 'high_voltage', 930, 500, 150, {giro: 0.2});
  });
  pincel(ctx, laco(785, 640, 225, 200, 11), {larg: 9, cor: CORAL, seed: 12, p: suave((t - 3.6) / 0.8)});
};

// Cena 22b. O resultado: quantos apertaram o botão.
const choqueResultado = (ctx, t) => {
  camera(ctx, t, {z: 1 + 0.03 * suave(t / 9), cy: 640});
  papel(ctx);
  texto(ctx, 'Wilson et al., 2014 · Science', {y: 120, tam: 38, estilo: 'italic', etiqueta: '#FFFDF6', p: 3});
  const base = 1080;
  const alto = 600;
  [[320, 67, CORAL, 'homens', '12 de 18'], [760, 25, AZUL, 'mulheres', '6 de 24']].forEach(([x, v, cor, rot, n], i) => {
    const k = suave((t - 1.4 - i * 0.35) / 1.6);
    if (k <= 0) return;
    const h = alto * (v / 100) * k;
    recorte(ctx, [[x - 130, base - h], [x + 130, base - h - 3], [x + 128, base], [x - 132, base]], {cor, seed: 50 + i, sombra: [8, 14, 18, 0.3]});
    texto(ctx, `${contagem(v, (t - 1.4 - i * 0.35) / 1.6)}%`, {x, y: base - h - 70, tam: 120, fonte: 'Oswald', peso: '600'});
    texto(ctx, `${rot}`, {x, y: base + 55, tam: 60, fonte: 'Caveat', p: (t - 2.6 - i * 0.35) / 0.4});
    texto(ctx, `${n}`, {x, y: base + 108, tam: 40, estilo: 'italic', p: (t - 3 - i * 0.35) / 0.4});
  });
  pincel(ctx, [[120, base], [W - 120, base + 4]], {larg: 7, seed: 60, p: suave((t - 1.2) / 0.6)});
  marcador(ctx, 205, base - alto * 0.67 - 70, 230, 100, suave((t - 4.4) / 0.7));
};

// Cartão recortado com borda branca, onde vai cada painel.
const cartao = (ctx, x0, y0, x1, y1, seed) => recorte(ctx, [[x0, y0], [x1, y0 + 4], [x1 - 3, y1], [x0 + 2, y1 - 2]], {cor: '#FBF6E9', borda: 8, seed, sombra: [8, 12, 18, 0.28]});
const pisca = (t, a, b) => (t > a ? Math.min(1, (t - a) / 0.25) : 0) * (b === undefined ? 1 : t < b ? 1 : Math.max(0, 1 - (t - b) / 0.25));

// Cena 8. Raichle, 2001: na tarefa acende uma rede, parado acende outra.
const raichle = (ctx, t) => {
  camera(ctx, t, {z: 1 + 0.05 * suave(t / 10), cy: 640});
  papel(ctx);
  texto(ctx, 'Raichle et al., 2001 · PNAS', {y: 120, tam: 38, estilo: 'italic', etiqueta: '#FFFDF6', p: suave(t / 0.6) * 3});
  // O cérebro de quem está parado, sem fazer nada: as regiões acendem uma a uma.
  const r = suave((t - 2.2) / 3);
  cerebro(ctx, {cx: 540, cy: 680, s: 740, rede: r, pulso: Math.sin(t * 4) * r, p: suave((t - 0.3) / 1.6), seed: 6});
  gira(ctx, 540, 680, 740 / 2, () => [[-0.39, -0.06], [0.2, -0.26], [0.34, -0.06], [0.0, 0.2]].forEach(([x, y], i) => {
    pincel(ctx, laco(540 + x * 740, 680 + y * 740, 100, 80, 30 + i), {larg: 7, cor: CORAL, seed: 40 + i, p: suave((t - 5.4 - i * 0.45) / 0.6)});
  }));
};

// Cena 13. Não tem botão de desligar: o interruptor desce, a rede apaga e volta sozinha.
const interruptor = (ctx, t) => {
  camera(ctx, t, {z: 1 + 0.03 * suave(t / 8), cy: 640});
  papel(ctx);
  const desligadas = [[1.4, 1.9], [3.2, 3.6], [4.7, 5.0], [5.9, 6.15]];
  const off = desligadas.some(([a, b]) => t > a && t < b);
  const r = off ? 0.08 : 1;
  cerebro(ctx, {cx: 540, cy: 520, s: 470, rede: r * suave((t - 0.6) / 0.6), pulso: Math.sin(t * 5), seed: 8});
  // O interruptor.
  surge(ctx, (t - 0.8) / 0.5, 540, 1010, () => {
    interruptor3d(ctx, 540, 1010, off);
  });
  if (off) [[680, 980, 730, 960], [690, 1020, 745, 1020], [680, 1060, 730, 1080]].forEach(([a, b, c, d], i) => pincel(ctx, [[a, b], [c, d]], {larg: 6, seed: 40 + i, seco: 0}));
  gira(ctx, 540, 520, 470 / 2, () => pincel(ctx, laco(540, 520, 290, 210, 13), {larg: 8, cor: CORAL, seed: 14, p: suave((t - 6.4) / 0.8)}));
};

// Cena 19. O exame de sexta: a mente volta ao assunto dezenas de vezes por dia, sem nenhuma informação nova.
const DIAS = ['SEG', 'TER', 'QUA', 'QUI', 'SEX'];
const exame = (ctx, t) => {
  camera(ctx, t, {z: 1 + 0.03 * suave(t / 14), cy: 640});
  papel(ctx);
  // Só o calendário, no meio da área útil. O marca-texto passa de dia em dia até a sexta.
  const dia = Math.min(4, Math.floor(Math.max(0, t - 3) / 1.9));
  const xs = [150, 345, 540, 735, 930];
  const y0 = 540;
  DIAS.forEach((d, i) => {
    surge(ctx, (t - 1.4 - i * 0.12) / 0.4, xs[i], y0 + 100, () => {
      recorte(ctx, [[xs[i] - 82, y0], [xs[i] + 82, y0 + 2], [xs[i] + 80, y0 + 200], [xs[i] - 81, y0 + 198]], {cor: '#FBF6E9', borda: 6, seed: 60 + i});
      recorte(ctx, [[xs[i] - 82, y0], [xs[i] + 82, y0 + 2], [xs[i] + 82, y0 + 45], [xs[i] - 82, y0 + 45]], {cor: i === 4 ? CORAL : '#8C9BA3', seed: 70 + i, sombra: null});
      texto(ctx, d, {x: xs[i], y: y0 + 24, tam: 36, fonte: 'Oswald', peso: '600', cor: '#FBF6E9'});
      if (i === 4) {
        adesivo(ctx, 'envelope', 930, y0 + 128, 120, {borda: 6});
      } else texto(ctx, '?', {x: xs[i], y: y0 + 125, tam: 70, fonte: 'Caveat', cor: '#8C9BA3'});
    });
  });
  if (t > 3 && t < 12.6) marcador(ctx, xs[dia] - 90, y0 + 100, 180, 210, 1, {cor: 'rgba(255,214,10,0.35)', seed: 90 + dia});
};

// Cena 29: bpm mostrado e fase acumulada da batida (integral do bpm), para desenho e som baterem juntos.
const voltaPanico = (t) => (t < 1.5 ? 0 : Math.pow((t - 1.5) / 14.5, 1.6) * 5);
const bpmPanico = (t) => 70 + voltaPanico(t) * 22;
const FASE_PANICO = (() => {
  const passo = 1 / 240;
  const f = [0];
  for (let i = 1; i <= 16 * 240; i++) f.push(f[i - 1] + (bpmPanico((i - 0.5) * passo) / 60) * passo);
  return f;
})();
const fasePanico = (t) => FASE_PANICO[Math.max(0, Math.min(FASE_PANICO.length - 1, Math.round(t * 240)))];

// Cena 29. O ciclo do pânico: seis etapas em roda, e uma bolinha que gira cada vez mais rápido.
const ETAPAS = [['pensamento', 'ruim'], ['adrenalina'], ['coração e', 'respiração', 'disparam'], ['o cérebro', 'percebe'], ['medo do', 'próprio corpo'], ['"vou', 'morrer"']];
const panico = (ctx, t) => {
  camera(ctx, t, {z: 1 + 0.04 * suave(t / 16), cy: 640});
  papel(ctx);
  const C = [540, 690];
  const R = 390;
  // Posição da bolinha: cada volta mais rápida.
  const volta = voltaPanico(t);
  const ang = (i) => -Math.PI / 2 + (i / 6) * Math.PI * 2;
  for (let i = 0; i < 6; i++) {
    const a0 = ang(i) + 0.3;
    const a1 = ang(i + 1) - 0.3;
    const arco = Array.from({length: 16}, (_, k) => {
      const a = a0 + ((a1 - a0) * k) / 15;
      return [C[0] + Math.cos(a) * R, C[1] + Math.sin(a) * R];
    });
    seta(ctx, arco, {larg: 7, seed: 200 + i, p: suave((volta * 6 - i) * 1.2)});
  }
  for (let i = 0; i < 6; i++) {
    const [x, y] = [C[0] + Math.cos(ang(i)) * R, C[1] + Math.sin(ang(i)) * R];
    const perto = Math.max(0, 1 - Math.abs(((volta * 6 - i + 3) % 6) - 3) * 2.5);
    surge(ctx, volta * 6 - i + 0.6, x, y, () => {
      const linhas = ETAPAS[i];
      const w = 230;
      const h = 52 * linhas.length + 36;
      recorte(ctx, [[x - w / 2, y - h / 2], [x + w / 2, y - h / 2 + 3], [x + w / 2 - 2, y + h / 2], [x - w / 2 + 1, y + h / 2 - 2]], {cor: perto > 0.3 ? '#FFE8A3' : '#FBF6E9', borda: 6, seed: 220 + i});
      linhas.forEach((l, j) => texto(ctx, l, {x, y: y - ((linhas.length - 1) * 52) / 2 + j * 52, tam: 36}));
    });
  }
  if (t > 1.5) {
    const a = ang(0) + volta * Math.PI * 2;
    recorte(ctx, ellipse(C[0] + Math.cos(a) * R, C[1] + Math.sin(a) * R, 22, 22, 20), {cor: CORAL, seed: 240, sombra: [3, 5, 6, 0.35]});
  }
  // No centro, o coração acelera junto, no ritmo exato do bpm escrito.
  const bate = Math.max(0, Math.sin(fasePanico(t) * Math.PI * 2)) ** 6;
  adesivo(ctx, 'red_heart', C[0], C[1] + 10, 230 * (1 + 0.12 * bate));
  texto(ctx, `${Math.round(bpmPanico(t))} bpm`, {x: C[0], y: C[1] + 170, tam: 40, fonte: 'Oswald', peso: '600', p: t > 2 ? 1 : 0});
};

// Linha de batimento que corre da direita para a esquerda.
const ecg = (ctx, x0, x1, y, t, bpm, seed, cor = TINTA) => {
  const pts = [];
  const periodo = 60 / bpm;
  for (let x = x0; x <= x1; x += 4) {
    const tt = t - (x1 - x) / 260;
    const f = ((tt % periodo) + periodo) % periodo / periodo;
    let v = 0;
    if (f > 0.1 && f < 0.13) v = -18;
    else if (f >= 0.13 && f < 0.16) v = 70;
    else if (f >= 0.16 && f < 0.19) v = -30;
    else if (f > 0.35 && f < 0.45) v = -10 * Math.sin(((f - 0.35) / 0.1) * Math.PI);
    pts.push([x, y - v]);
  }
  pincel(ctx, pts, {larg: 5, cor, seed, seco: 0.2, ponta: 0.02});
};

// Cena 33. Os dois estados: parado, a rede em chamas e o corpo em alerta; fazendo algo, a rede baixa e o corpo calmo.
const doisEstados = (ctx, t) => {
  camera(ctx, t, {z: 1 + 0.03 * suave(t / 12), cy: 640});
  papel(ctx);
  // Os dois painéis seguem a mesma grade: situação à esquerda, cérebro no meio, coração e bpm à direita, ECG embaixo.
  const painel = (y0, seed, {situacao, giro, rede, tarefa = 0, pulso = 0, bpm, cor}) => {
    const cy = y0 + 240;
    cartao(ctx, 70, y0, 1010, y0 + 530, seed);
    adesivo(ctx, situacao, 190, cy, 170, {giro});
    cerebro(ctx, {cx: 490, cy, s: 270, rede, tarefa, pulso, seed: seed + 4});
    const b = Math.max(0, Math.sin(t * (bpm / 60) * Math.PI * 2)) ** 6;
    adesivo(ctx, 'red_heart', 830, cy - 25, 150 * (1 + 0.12 * b));
    texto(ctx, `${bpm} bpm`, {x: 830, y: cy + 95, tam: 40, fonte: 'Oswald', peso: '600'});
    ecg(ctx, 110, 970, y0 + 465, t, bpm, 295 + seed, cor);
  };
  surge(ctx, (t - 0.2) / 0.5, 540, 375, () => painel(110, 5, {situacao: 'airplane', giro: -0.15, rede: suave((t - 0.8) / 0.8), pulso: Math.sin(t * 7), bpm: 132, cor: CORAL}), 470);
  surge(ctx, (t - 2.6) / 0.5, 540, 935, () => painel(670, 6, {situacao: 'yarn', giro: -0.05, rede: 0.3 * suave((t - 3.2) / 0.8), tarefa: 0.5 * suave((t - 3.2) / 0.8), bpm: 66, cor: AZUL}), 470);
};

// Sons: batidas de coração nos picos da animação (sin(t * f * 2π) no máximo), entre t0 e t1.
const batidas = (t0, t1, f, k = 1) => {
  const r = [];
  for (let n = Math.ceil(t0 * f - 0.25); (n + 0.25) / f < t1; n++) r.push([(n + 0.25) / f, 'coracao', k]);
  return r;
};
// Cena 29: uma batida em cada pico do desenho do coração.
const sonsPanico = () => {
  const r = [[0.05, 'pop']];
  for (let q = 1; q < 16 * 30; q++) {
    const t = q / 30;
    if (Math.floor(fasePanico(t) - 0.25) > Math.floor(fasePanico(t - 1 / 30) - 0.25)) r.push([t, 'coracao', 0.8]);
  }
  // Cada caixa entra quando a bolinha chega perto dela.
  for (let i = 1; i < 6; i++) {
    for (let q = 0; q < 16 * 30; q++) {
      if (voltaPanico(q / 30) * 6 - i + 0.6 > 0) {
        r.push([q / 30, 'pop']);
        break;
      }
    }
  }
  return r;
};

export const CENAS = {
  '08-raichle': {f: raichle, dur: 12, sons: [
    [0.05, 'etiqueta'], [0.3, 'pop'], [2.2, 'bip', 0.8],
  ]},
  '13-sem-botao': {f: interruptor, dur: 8, sons: [
    [0.8, 'pop'],
    [1.4, 'clique'], [1.9, 'clique', 0.7], [3.2, 'clique'], [3.6, 'clique', 0.7],
    [4.7, 'clique'], [5.0, 'clique', 0.7], [5.9, 'clique'], [6.15, 'clique', 0.7],
  ]},
  '19-exame': {f: exame, dur: 14, sons: [
    ...[0, 1, 2, 3, 4].map((i) => [1.4 + i * 0.12, 'pop', 0.7]),
  ]},
  '22a-choque-sala': {f: choqueSala, dur: 9, sons: [
    [0.05, 'etiqueta'], [0.6, 'pop'], [1.0, 'pop'],
    [7.0, 'clique'], [7.03, 'zap'],
  ]},
  '22b-choque-resultado': {f: choqueResultado, dur: 9, sons: [
    [1.4, 'swoosh'], [1.75, 'swoosh'],
  ]},
  '29-panico': {f: panico, dur: 16, sons: sonsPanico()},
  '33-dois-estados': {f: doisEstados, dur: 12, sons: [
    [0.2, 'pop'], [2.6, 'pop'],
    ...batidas(0.4, 12, 132 / 60, 0.6),
    ...batidas(2.8, 12, 66 / 60, 0.6),
  ]},
};
