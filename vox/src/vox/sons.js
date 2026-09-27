// Efeitos sonoros (gerados no Magnific), cortados no ataque e normalizados a -3 dB de pico.
// O volume de cada tipo fica aqui, baixo, para ficar por baixo da voz.
export const VOLUME = {pop: 0.3, etiqueta: 0.35, caneta: 0.22, clique: 0.45, zap: 0.3, coracao: 0.35, bip: 0.2, swoosh: 0.25};
const VARIACOES = {pop: 2, etiqueta: 3, caneta: 3, clique: 3, zap: 3, coracao: 3, bip: 3, swoosh: 3};

// Cada evento: [segundo, tipo, volume relativo opcional]. As variações se alternam para o mesmo som não se repetir idêntico.
export const arquivos = (eventos) => {
  const conta = {};
  return eventos.map(([t, tipo, k = 1]) => {
    conta[tipo] = (conta[tipo] || 0) + 1;
    const v = ((conta[tipo] - 1) % VARIACOES[tipo]) + 1;
    return {t, arq: `sons/prontos/${tipo}-${v}.wav`, vol: VOLUME[tipo] * k};
  });
};
