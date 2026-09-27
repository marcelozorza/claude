import React, {useLayoutEffect, useRef} from 'react';
import {AbsoluteFill, Audio, Sequence, continueRender, delayRender, staticFile, useCurrentFrame} from 'remotion';
import {CENAS, FPS} from './vox/cenas';
import {tamanho} from './lib/util';
import {IMAGENS, RELOGIO} from './vox/estilo';
import {arquivos} from './vox/sons';

const FONTES = [['Special Elite', 'special-elite', {}], ['Caveat', 'caveat', {}], ['Oswald', 'oswald', {}], ['EB Garamond', 'eb-garamond', {}], ['EB Garamond', 'eb-garamond-italic', {style: 'italic'}]];
const EMOJIS = ['airplane', 'alarm_clock', 'anxious_face_with_sweat', 'brain', 'calendar', 'cooking', 'envelope', 'high_voltage', 'light_bulb', 'magnifying_glass_tilted_left', 'microscope', 'mobile_phone', 'person_in_lotus_position', 'pot_of_food', 'radio_button', 'red_circle', 'red_heart', 'stopwatch', 'thought_balloon', 'violin', 'yarn'];
let fontes = null;
const carrega = (arq) => new Promise((ok) => {
  const im = new Image();
  im.onload = () => ok([arq, im]);
  im.onerror = () => ok([arq, null]);
  im.src = staticFile('emoji/' + arq + '.png');
});

export const Cena = ({id}) => {
  const q = useCurrentFrame();
  const ref = useRef(null);
  useLayoutEffect(() => {
    const espera = delayRender('quadro ' + q);
    fontes = fontes || Promise.all([...FONTES.map(([nome, arq, d]) => new FontFace(nome, `url(${staticFile('fontes/' + arq + '.woff2')})`, d).load().then((f) => document.fonts.add(f))), ...EMOJIS.map(carrega)]).then((r) => { r.forEach((x) => Array.isArray(x) && (IMAGENS[x[0]] = x[1])); });
    fontes.then(() => {
      tamanho(1080, 1920);
      const ctx = ref.current.getContext('2d');
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, 1080, 1920);
      RELOGIO.t = q / FPS;
      CENAS[id].f(ctx, q / FPS, q);
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      continueRender(espera);
    });
  }, [id, q]);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <canvas ref={ref} width={1080} height={1920} />
      {arquivos(CENAS[id].sons || []).map(({t, arq, vol}, i) => (
        <Sequence key={i} from={Math.round(t * FPS)} layout="none">
          <Audio src={staticFile(arq)} volume={vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
