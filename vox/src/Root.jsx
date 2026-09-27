import React from 'react';
import {Composition} from 'remotion';
import {Cena} from './Cena';
import {CENAS, FPS} from './vox/cenas';

export const Root = () => (
  <>
    {Object.entries(CENAS).map(([id, c]) => (
      <Composition key={id} id={id} component={Cena} durationInFrames={Math.round(c.dur * FPS)} fps={FPS} width={1080} height={1920} defaultProps={{id}} />
    ))}
  </>
);
