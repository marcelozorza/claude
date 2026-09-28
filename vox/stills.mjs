// Vários quadros parados com um só bundle. Uso: node stills.mjs ID:segundos ID:segundos ...
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {existsSync, readdirSync, mkdirSync} from 'fs';
const dir = '/opt/pw-browsers/chromium_headless_shell-1194/';
const browserExecutable = existsSync(dir) ? dir + readdirSync(dir, {withFileTypes: true}).find((d) => d.isDirectory()).name + '/headless_shell' : null;
const serveUrl = await bundle({entryPoint: './src/index.js', publicDir: './public'});
mkdirSync('out', {recursive: true});
for (const par of process.argv.slice(2)) {
  const [id, t] = par.split(':');
  const composition = await selectComposition({serveUrl, id, browserExecutable});
  await renderStill({composition, serveUrl, frame: Math.round(Number(t) * composition.fps), output: `out/${id}-${t}.png`, browserExecutable, timeoutInMilliseconds: 120000});
  console.log('OK', id, t);
}
