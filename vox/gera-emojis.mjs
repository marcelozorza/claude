// Gera src/vox/emojis.js com os PNGs de public/emoji e os JPGs de public/fotos. Uso: node gera-emojis.mjs
import {readdirSync, writeFileSync} from 'fs';
const lista = (pasta, ext) => readdirSync(pasta).filter((f) => f.endsWith(ext)).map((f) => f.slice(0, -ext.length)).sort();
const emojis = lista('public/emoji', '.png');
const fotos = lista('public/fotos', '.jpg');
writeFileSync('src/vox/emojis.js', `// Gerado por gera-emojis.mjs.\nexport const EMOJIS = ${JSON.stringify(emojis)};\nexport const FOTOS = ${JSON.stringify(fotos)};\n`);
console.log(emojis.length, 'emojis,', fotos.length, 'fotos');
