// Um quadro parado de uma cena. Uso: node still.mjs ID segundos
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {existsSync, readdirSync} from 'fs';
const dir = '/opt/pw-browsers/chromium_headless_shell-1194/';
const browserExecutable = existsSync(dir) ? dir + readdirSync(dir, {withFileTypes: true}).find((d) => d.isDirectory()).name + '/headless_shell' : null;
const serveUrl = await bundle({entryPoint: './src/index.js', publicDir: './public'});
const [id, ...ts] = process.argv.slice(2);
const composition = await selectComposition({serveUrl, id, browserExecutable});
for (const t of ts) {
  await renderStill({composition, serveUrl, frame: Math.round(Number(t) * composition.fps), output: `out/${id}-${t}.png`, browserExecutable, timeoutInMilliseconds: 120000});
  console.log('OK', id, t);
}
