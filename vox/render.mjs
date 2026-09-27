// Renderiza animações em MP4. Uso: node render-anim.mjs C01-cena1 PA-passagem
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';
import {existsSync, readdirSync, mkdirSync} from 'fs';
const dir = '/opt/pw-browsers/chromium_headless_shell-1194/';
const browserExecutable = existsSync(dir) ? dir + readdirSync(dir, {withFileTypes: true}).find((d) => d.isDirectory()).name + '/headless_shell' : null;
const serveUrl = await bundle({entryPoint: './src/index.js', publicDir: './public'});
mkdirSync('out', {recursive: true});
for (const id of process.argv.slice(2)) {
  const composition = await selectComposition({serveUrl, id, browserExecutable});
  await renderMedia({composition, serveUrl, codec: 'h264', crf: 16, outputLocation: `out/${id}.mp4`, browserExecutable, concurrency: 4, timeoutInMilliseconds: 120000});
  console.log('OK', id);
}
