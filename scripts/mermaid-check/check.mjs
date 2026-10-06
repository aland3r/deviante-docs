// Renderiza cada bloco ```mermaid do arc42.md num Chromium e lista os que falham.
// Uso: (cd scripts/mermaid-check && npm install --silent) && node scripts/mermaid-check/check.mjs [architecture/arc42.md]
// Sai com código 1 se algum diagrama não renderizar.
import { chromium } from 'playwright-core';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const here = path.dirname(fileURLToPath(import.meta.url));
const mdPath = process.argv[2] || path.join(here, '../../architecture/arc42.md');
const md = fs.readFileSync(mdPath, 'utf8');
const blocks = [...md.matchAll(/```mermaid\n([\s\S]*?)```/g)].map(m => m[1]);

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' });
const page = await browser.newPage();
await page.setContent('<html><body></body></html>');
await page.addScriptTag({ path: path.join(here, 'node_modules/mermaid/dist/mermaid.min.js') });
const errors = await page.evaluate(async blocks => {
  mermaid.initialize({ startOnLoad: false });
  const out = [];
  for (const [i, code] of blocks.entries()) {
    try { await mermaid.render('d' + i, code); }
    catch (e) { out.push(`diagrama ${i + 1}: ${String(e.message || e).slice(0, 300)}`); }
  }
  return out;
}, blocks);
await browser.close();

console.log(`${blocks.length} diagramas, ${errors.length} com erro`);
errors.forEach(e => console.log(e));
process.exit(errors.length ? 1 : 0);
