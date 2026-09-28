import {CORAL, balanco, foto, marcador, recorte, suave, texto} from './estilo';
import {cola, fundo, surge} from './pecas';

// Lote D: cenas com fotos (raw dogging, luto e "e se", mãos ocupadas, banho e louça).

// Cena 1. Raw dogging: o passageiro sem nada, e as distrações se apagando em volta.
const DISTRACOES = [['mobile_phone', 190, 330], ['open_book', 890, 330], ['headphone', 190, 1010], ['droplet', 890, 1010]];
const rawDogging = (ctx, t) => {
  fundo(ctx, t, 10);
  foto(ctx, t, 0.3, 'passageiro', 540, 660, 560, {giro: -0.03, de: Math.PI / 2, corte: [0.3, 0.05, 0.7, 0.75], prop: 0.8});
  DISTRACOES.forEach(([nome, x, y], i) => {
    const apaga = suave((t - 4.0 - i * 0.5) / 0.7);
    if (apaga >= 1) return;
    ctx.save();
    ctx.globalAlpha = 1 - apaga;
    if (apaga > 0) ctx.filter = `grayscale(${Math.min(1, apaga * 2)})`;
    cola(ctx, t, 1.4 + i * 0.3, nome, x, y, 190);
    ctx.restore();
  });
};

// Cena 18. Luto e o "e se": a janela molhada e a pergunta que volta.
const eSe = (ctx, t) => {
  fundo(ctx, t, 9);
  foto(ctx, t, 0.3, 'janela-chuva', 480, 560, 580, {giro: -0.04, de: Math.PI + 0.3, prop: 0.8});
  cola(ctx, t, 1.4, 'wilted_flower', 860, 880, 200, {giro: 0.1});
  [[250, 1010, 2.2, -0.08], [760, 1090, 3.0, 0.05], [420, 1200, 3.8, -0.04]].forEach(([x, y, t0, g]) => {
    if (t < t0) return;
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(g + balanco(x, y, 120));
    texto(ctx, '“e se…?”', {x: 0, y: 0, tam: 88, fonte: 'Caveat', cor: CORAL, p: (t - t0) / 0.5});
    ctx.restore();
  });
};

// Cena 34. Mãos ocupadas: o tricô.
const maos = (ctx, t) => {
  fundo(ctx, t, 8);
  foto(ctx, t, 0.3, 'trico', 540, 560, 800, {giro: 0.04, de: -0.4});
  cola(ctx, t, 1.5, 'yarn', 860, 950, 200, {giro: -0.08});
};

// Cena 36. Banho e louça: as ideias chegam quando as mãos estão ocupadas.
const banhoLouca = (ctx, t) => {
  fundo(ctx, t, 9);
  foto(ctx, t, 0.3, 'banho', 330, 470, 470, {giro: -0.06, de: Math.PI + 0.3, prop: 0.8});
  foto(ctx, t, 1.3, 'louca', 700, 870, 600, {giro: 0.05, de: 0.2});
  cola(ctx, t, 2.6, 'light_bulb', 850, 360, 190);
};

// Cena 0. O nome da prática, numa tira de papel recortada, com o avião ao lado.
const nome = (ctx, t) => {
  fundo(ctx, t, 6);
  surge(ctx, (t - 0.3) / 0.45, 540, 640, () => {
    recorte(ctx, [[110, 540], [970, 548], [964, 744], [116, 736]], {cor: '#FFFDF6', borda: 8, seed: 3100, sombra: [8, 14, 18, 0.3]});
    marcador(ctx, 190, 648, 700, 118, suave((t - 2.0) / 0.6), {seed: 3101});
    texto(ctx, 'raw dogging', {y: 640, tam: 150, estilo: 'italic', p: (t - 0.8) / 0.9});
  }, 440);
  cola(ctx, t, 2.8, 'airplane', 860, 430, 230, {giro: -0.12});
};

// Nome em duas linhas numa tira de papel, datilografado, com marca-texto em cada linha e um emoji ao lado.
const nomeDuasLinhas = (linhas, emoji) => (ctx, t) => {
  fundo(ctx, t, 7);
  surge(ctx, (t - 0.3) / 0.45, 540, 640, () => {
    recorte(ctx, [[90, 470], [990, 478], [984, 818], [96, 810]], {cor: '#FFFDF6', borda: 8, seed: 3200, sombra: [8, 14, 18, 0.3]});
    ctx.save();
    ctx.font = 'italic 130px "EB Garamond"';
    linhas.forEach((l, i) => {
      const y = 570 + i * 150;
      const w = ctx.measureText(l).width;
      marcador(ctx, 540 - w / 2 - 14, y + 8, w + 28, 104, suave((t - 2.4 - i * 0.35) / 0.6), {seed: 3201 + i});
    });
    ctx.restore();
    linhas.forEach((l, i) => texto(ctx, l, {y: 570 + i * 150, tam: 130, estilo: 'italic', p: (t - 0.8 - i * 0.8) / 0.8}));
  }, 450);
  cola(ctx, t, 3.3, emoji, 880, 400, 230, {giro: 0.1});
};

// A logo do canal, jogada sobre o papel como uma foto, bem grande.
const logo = (ctx, t) => {
  fundo(ctx, t, 5);
  foto(ctx, t, 0.3, 'logo-canal', 540, 640, 900, {giro: -0.04, de: Math.PI / 2 + 0.3, prop: 1});
};

export const CENAS5 = {
  '00-dmn-en': {f: nomeDuasLinhas(['Default Mode', 'Network'], 'brain'), dur: 7, sons: [[0.3, 'pop'], [0.8, 'etiqueta', 0.8], [1.6, 'etiqueta', 0.6], [3.3, 'pop']]},
  '00-dmn-pt': {f: nomeDuasLinhas(['Rede de Modo', 'Padrão'], 'brain'), dur: 7, sons: [[0.3, 'pop'], [0.8, 'etiqueta', 0.8], [1.6, 'etiqueta', 0.6], [3.3, 'pop']]},
  '00-logo': {f: logo, dur: 5, sons: [[0.3, 'swoosh', 0.8]]},
  '00-nome': {f: nome, dur: 6, sons: [[0.3, 'pop'], [0.8, 'etiqueta', 0.8], [2.8, 'swoosh', 0.7]]},
  '01-raw-dogging': {f: rawDogging, dur: 10, sons: [[0.3, 'swoosh', 0.7], ...DISTRACOES.map((_, i) => [1.4 + i * 0.3, 'pop']), ...DISTRACOES.map((_, i) => [4.0 + i * 0.5, 'bip', 0.5])]},
  '18-e-se': {f: eSe, dur: 9, sons: [[0.3, 'swoosh', 0.7], [1.4, 'pop']]},
  '34-maos': {f: maos, dur: 8, sons: [[0.3, 'swoosh', 0.7], [1.5, 'pop']]},
  '36-banho-louca': {f: banhoLouca, dur: 9, sons: [[0.3, 'swoosh', 0.7], [1.3, 'swoosh', 0.7], [2.6, 'bip']]},
};
