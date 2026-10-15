// arc42.md -> PDF. Text on A4; each Mermaid diagram on a page of its own,
// cropped to its drawing and enlarged. A diagram goes to A3 only when A4
// would shrink it below its natural (on-screen) size.
// Usage: node gerar_pdf.mjs ARC42_MD OUT_PDF
import { chromium } from 'playwright-core';
import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const here = path.dirname(new URL(import.meta.url).pathname);
const [, , mdPath = path.join(here, '../../architecture/arc42.md'), out = 'arc42.pdf'] = process.argv;

let md = fs.readFileSync(mdPath, 'utf8');
md = md.slice(md.indexOf('## 1.'));
const codes = [];
md = md.replace(/```mermaid\n([\s\S]*?)```/g, (_, c) => {
  codes.push(c);
  return `\n<div class="dg" data-i="${codes.length - 1}"></div>\n`;
});
const body = execFileSync('pandoc', ['-f', 'gfm', '-t', 'html5', '--id-prefix='], { input: md }).toString()
  .replace(/<hr \/>/g, '');

const html = `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
@page { size: A4; margin: 20mm 18mm 18mm 18mm; }
@page a4p { size: A4 portrait; margin: 12mm; }
@page a4l { size: A4 landscape; margin: 12mm; }
@page a3p { size: A3 portrait; margin: 12mm; }
@page a3l { size: A3 landscape; margin: 12mm; }
@page capa { size: A4; margin: 30mm 25mm; }
body { font-family: 'Liberation Sans', Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #111; }
h2 { font-size: 17pt; margin: 18pt 0 8pt; break-after: avoid; color: #0b3b6f; }
h2#h0, .sumario + h2 { margin-top: 0; }
h3 { font-size: 13pt; margin: 14pt 0 6pt; break-after: avoid; color: #0b3b6f; }
h4 { font-size: 11pt; break-after: avoid; }
p.lbl { break-after: avoid; margin-top: 10pt; }
p { margin: 0 0 7pt; text-align: justify; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 10pt; font-size: 10.5pt; line-height: 1.35; }
th, td { border: 0.6pt solid #9aa5b1; padding: 3pt 5pt; vertical-align: top; text-align: left; }
th { background: #e8eef5; }
td:first-child, th:first-child { white-space: nowrap; }
tr { break-inside: avoid; }
thead { display: table-header-group; }
code { font-family: 'Liberation Mono', monospace; font-size: 0.92em; background: #f1f3f5; padding: 0 2pt; border-radius: 2pt; }
ul, ol { margin: 0 0 7pt; padding-left: 18pt; }
.capa { page: capa; height: 230mm; break-after: page; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
.capa .t1 { font-size: 20pt; font-weight: bold; line-height: 1.35; }
.capa .autores { font-size: 12pt; font-weight: bold; line-height: 1.8; }
.capa .inst { font-size: 11pt; line-height: 1.7; }
.sumario { line-height: 1.32; break-after: page; }
.sumario li { break-inside: avoid; }
.sumario h1 { font-size: 17pt; color: #0b3b6f; }
.sumario ul { list-style: none; padding-left: 0; }
.sumario ul ul { padding-left: 12pt; }
.sumario a { color: #111; text-decoration: none; display: flex; }
.sumario a .pg { margin-left: auto; padding-left: 6pt; }
.sumario li { margin: 1pt 0; }
.sumario ul ul { margin: 2pt 0 4pt; }
.dginline { break-inside: avoid; margin: 6pt 0 10pt; }
.dginline > h3, .dginline > h4 { margin-top: 14pt; }
.dginline svg { display: block; margin: 4pt auto 0; }
.dgpage { break-inside: avoid; display: flex; flex-direction: column; align-items: center; }
.dgpage > h2 { break-before: auto; }
.dgpage > h2, .dgpage > h3, .dgpage > p { align-self: stretch; text-align: left; margin: 0 0 4pt; }
.dgpage .fill { flex: 1 1 auto; min-height: 0; align-self: stretch; position: relative; margin-top: 4pt; }
.dgpage svg { position: absolute; inset: 0; }
</style></head><body>
<div class="capa">
  <div class="inst">PONTIFÍCIA UNIVERSIDADE CATÓLICA DO PARANÁ</div>
  <div class="t1">Documentação Arc42: Sistema de Suporte a Decisão em Manutenção Industrial</div>
  <div class="autores">ALANDER MENEZES ARANTES DE ÁVILA<br>EMANUELLE SKOLUT JOSE</div>
  <div class="inst">6º Período – Engenharia de Software<br>Curso: Arquitetura e Soluções</div>
</div>
<div class="sumario"><h1>Sumário</h1><div id="toc"></div></div>
${body}
</body></html>`;

const MM = 96 / 25.4;
const MINPX = +(process.env.MINPX ?? 0);
const MAXH = +(process.env.MAXH ?? 190);
const SHRINK = +(process.env.SHRINK ?? 0.7);
const PAGES = { a4p: [210, 297], a4l: [297, 210], a3p: [297, 420], a3l: [420, 297] };

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 1300, height: 1000 } });
await page.addInitScript(() => { Object.defineProperty(screen, 'availWidth', { get: () => 1200 }); });
await page.setContent(html, { waitUntil: 'load' });
await page.addScriptTag({ path: path.join(here, 'node_modules/mermaid/dist/mermaid.min.js') });
const report = await page.evaluate(async ({ codes, PAGES, MM, MINPX, MAXH }) => {
  mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'loose' });
  // Sumário from the h2/h3 headings
  const toc = document.getElementById('toc');
  let ul = document.createElement('ul'), sub = null;
  toc.appendChild(ul);
  document.querySelectorAll('body > h2, body > h3').forEach((h, k) => {
    if (!h.id) h.id = 'h' + k;
    const li = document.createElement('li');
    li.innerHTML = `<a href="#${h.id}">${h.textContent}</a>`;
    if (h.tagName === 'H2') { ul.appendChild(li); sub = document.createElement('ul'); li.appendChild(sub); }
    else if (sub) sub.appendChild(li);
  });
  const probe = s => {
    s.removeAttribute('style');
    const inv = s.getScreenCTM().inverse();
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const e of s.querySelectorAll('text, rect, path, line, polygon, polyline, circle, ellipse, foreignObject, image')) {
      if (e.closest('defs, marker')) continue;
      const r = e.getBoundingClientRect();
      if (!r.width && !r.height) continue;
      for (const [px, py] of [[r.left, r.top], [r.right, r.bottom]]) {
        const pt = new DOMPoint(px, py).matrixTransform(inv);
        x0 = Math.min(x0, pt.x); y0 = Math.min(y0, pt.y); x1 = Math.max(x1, pt.x); y1 = Math.max(y1, pt.y);
      }
    }
    const pad = 8, w = x1 - x0 + 2 * pad, h = y1 - y0 + 2 * pad;
    const fonts = [...s.querySelectorAll('text, foreignObject div, foreignObject span, foreignObject p')]
      .filter(t => t.textContent.trim()).map(t => parseFloat(getComputedStyle(t).fontSize)).filter(Boolean);
    return { w, h, vb: `${x0 - pad} ${y0 - pad} ${w} ${h}`, fmin: Math.min(...fonts) };
  };
  // bold-only lines work as small headings: keep them with what follows
  document.querySelectorAll('body > p').forEach(p => { const b = p.querySelector('strong'); if (b && b.textContent.trim() === p.textContent.trim()) p.classList.add('lbl'); });
  const out = [];
  for (const div of document.querySelectorAll('.dg')) {
    const i = +div.dataset.i;
    const { svg } = await mermaid.render('m' + i, codes[i]);
    const wrap = document.createElement('div');
    wrap.className = 'dgpage';
    div.replaceWith(wrap);
    // bring the caption (short bold line) and an h3 right above it onto the page
    const take = [];
    wrap.insertAdjacentHTML('beforeend', svg);
    const pre = probe(wrap.querySelector('svg'));
    // every diagram stays in the text flow at column width, together with the
    // heading and caption right above it (the block never splits across pages)
    {
      const s = wrap.querySelector('svg');
      wrap.className = 'dginline';
      let prev = wrap.previousElementSibling;
      const cap = [];
      while (prev && prev.tagName === 'P' && prev.textContent.length < 400 && cap.length < 2) { cap.unshift(prev); prev = prev.previousElementSibling; }
      if (prev && /^H[34]$/.test(prev.tagName)) cap.unshift(prev);
      cap.reverse().forEach(e => wrap.prepend(e));
      const capH = cap.reduce((acc, e) => acc + e.getBoundingClientRect().height + 10, 0);
      const colW = 174 * MM, colH = MAXH * MM - capH;
      const inl = Math.min(colW / pre.w, colH / pre.h, 1.3);
      s.removeAttribute('style');
      s.setAttribute('viewBox', pre.vb);
      s.setAttribute('width', pre.w * inl);
      s.setAttribute('height', pre.h * inl);
      out.push({ i, k: 'inline', fmin: pre.fmin, eff: +(pre.fmin * inl).toFixed(1), sc: +inl.toFixed(2) });
      continue;
    }
    wrap.innerHTML = '';
    let prev = wrap.previousElementSibling;
    while (prev && prev.tagName === 'P' && prev.textContent.length < 400 && take.length < 3) { take.unshift(prev); prev = prev.previousElementSibling; }
    if (prev && prev.tagName === 'H3') {
      take.unshift(prev); prev = prev.previousElementSibling;
      // a short section opening (h2 + intro) right above also joins, so it is not left alone on a page
      const intro = [];
      while (prev && prev.tagName === 'P' && intro.length < 2) { intro.unshift(prev); prev = prev.previousElementSibling; }
      if (prev && prev.tagName === 'H2' && intro.reduce((a, e) => a + e.textContent.length, 0) < 700) take.unshift(prev, ...intro);
    }
    take.forEach(e => wrap.appendChild(e));
    wrap.insertAdjacentHTML('beforeend', svg);
    // the short analysis right below also joins (it would otherwise sit alone on a page)
    const after = [];
    let next = wrap.nextElementSibling;
    while (next && next.tagName === 'P' && after.length < 2 && after.reduce((a, e) => a + e.textContent.length, 0) + next.textContent.length < 900) { after.push(next); next = next.nextElementSibling; }
    if (next && !/^H[23]$/.test(next.tagName) && next.tagName !== 'DIV') after.length = 0;
    after.forEach(e => wrap.appendChild(e));
    const s = wrap.querySelector('svg');
    s.removeAttribute('style');
    // crop to what is actually drawn (getBBox counts hidden helpers)
    const inv = s.getScreenCTM().inverse();
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const e of s.querySelectorAll('text, rect, path, line, polygon, polyline, circle, ellipse, foreignObject, image')) {
      if (e.closest('defs, marker')) continue;
      const r = e.getBoundingClientRect();
      if (!r.width && !r.height) continue;
      const cs = getComputedStyle(e);
      if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
      for (const [px, py] of [[r.left, r.top], [r.right, r.bottom]]) {
        const pt = new DOMPoint(px, py).matrixTransform(inv);
        x0 = Math.min(x0, pt.x); y0 = Math.min(y0, pt.y); x1 = Math.max(x1, pt.x); y1 = Math.max(y1, pt.y);
      }
    }
    const bb = { x: x0, y: y0, width: x1 - x0, height: y1 - y0 };
    const pad = 8;
    const w = bb.width + 2 * pad, h = bb.height + 2 * pad;
    s.setAttribute('viewBox', `${bb.x - pad} ${bb.y - pad} ${w} ${h}`);
    s.style.display = 'none';
    const headFor = pw => {
      wrap.style.width = (pw - 24) + 'mm';
      return [...take, ...after].reduce((a, e) => a + e.getBoundingClientRect().height + 8, 0) + 16;
    };
    const fit = k => {
      const [pw, ph] = PAGES[k];
      const aw = (pw - 24) * MM, ah = (ph - 24) * MM - headFor(pw);
      return Math.min(aw / w, ah / h);
    };
    const a4 = /^\s*classDiagram/.test(codes[i]) ? 'a4l' : ['a4p', 'a4l'].sort((x, y) => fit(y) - fit(x))[0];
    const a3 = ['a3p', 'a3l'].sort((x, y) => fit(y) - fit(x))[0];
    const fonts = [...s.querySelectorAll('text, foreignObject div, foreignObject span, foreignObject p')]
      .filter(t => t.textContent.trim()).map(t => parseFloat(getComputedStyle(t).fontSize)).filter(Boolean);
    const fmin = Math.min(...fonts);
    const fa4 = fit(a4);
    const k = fmin * fa4 >= MINPX ? a4 : a3;
    const sc = fit(k);
    wrap.style.width = (PAGES[k][0] - 24) + 'mm';
    wrap.style.height = (PAGES[k][1] - 26) + 'mm';
    s.style.display = '';
    const box = document.createElement('div');
    box.className = 'fill';
    s.replaceWith(box);
    box.appendChild(s);
    s.setAttribute('width', '100%');
    s.setAttribute('height', '100%');
    wrap.style.page = k;
    out.push({ i, k, fmin, eff: +(fmin * fa4).toFixed(1), a4: +fa4.toFixed(2), sc: +sc.toFixed(2), cap: take.map(e => e.textContent).join(' / ').slice(0, 60) });
  }
  return out;
}, { codes, PAGES, MM, MINPX, MAXH });
console.table(report);
const pdfOpts = {
  preferCSSPageSize: true, printBackground: true, displayHeaderFooter: true,
  headerTemplate: '<span></span>',
  footerTemplate: '<div style="width:100%;font-size:8px;color:#777;text-align:center;font-family:Arial"><span class="pageNumber"></span></div>',
};
const tmp = out + '.tmp.pdf';
const norm = t => t.replace(/\s+/g, '');
const pageTexts = () => execFileSync('pdftotext', ['-enc', 'UTF-8', tmp, '-']).toString().split('\f').map(norm);
// blank space left at the bottom of each page, in mm (from a coarse raster)
const gaps = () => {
  const dir = fs.mkdtempSync(path.join(path.dirname(out), '.gap'));
  execFileSync('pdftoppm', ['-r', '20', '-gray', tmp, path.join(dir, 'p')]);
  const res = fs.readdirSync(dir).sort().map(f => {
    const b = fs.readFileSync(path.join(dir, f));
    // PGM: header 'P5\nW H\n255\n'
    const hdr = b.toString('latin1', 0, 40).split(/\s+/);
    const W = +hdr[1], H = +hdr[2];
    const off = b.length - W * H;
    const bottom = Math.round(H * (279 / 297));
    let last = 0;
    for (let y = 0; y < bottom; y++) for (let x = 0; x < W; x++) if (b[off + y * W + x] < 200) { last = y; break; }
    return (bottom - last) / H * 297;
  });
  fs.rmSync(dir, { recursive: true });
  return res;
};
// shrink a diagram pushed to the next page when the space it left behind can hold it
// at no less than SHRINK of its size; one diagram per round, since the rest reflows
for (let round = 0; round < 40; round++) {
  await page.pdf({ ...pdfOpts, path: tmp });
  const texts = pageTexts(), gap = gaps();
  const blocks = await page.evaluate(MM => [...document.querySelectorAll('.dginline')].map((b, k) => {
    const s = b.querySelector('svg');
    const first = b.firstElementChild === s ? null : b.firstElementChild.textContent;
    return { k, key: first ? first.replace(/\s+/g, '').slice(0, 40) : null, blockMM: b.getBoundingClientRect().height / MM, svgMM: s.getBoundingClientRect().height / MM, done: b.dataset.done === '1' };
  }), MM);
  let changed = false;
  for (const bl of blocks) {
    if (!bl.key) continue;
    const n = texts.findIndex((t, j) => j > 1 && t.startsWith(bl.key));
    if (n < 2 || gap[n - 1] < 20) continue;
    // 1st choice: the text that follows the diagram in its section moves up into the gap
    const moved = await page.evaluate(({ k, room, MM }) => {
      const b = document.querySelectorAll('.dginline')[k];
      const e = b.nextElementSibling;
      if (!e || /^H[1-4]$/.test(e.tagName) || e.classList.contains('dginline')) return false;
      if (e.getBoundingClientRect().height / MM > room) return false;
      if (/^H[34]$/.test(b.firstElementChild.tagName) && b.firstElementChild.nextElementSibling.tagName !== 'svg') b.before(b.firstElementChild);
      b.before(e);
      return true;
    }, { k: bl.k, room: gap[n - 1] - 6, MM });
    if (moved) { console.log(`texto depois do diagrama ${bl.k} subiu para a página ${n}`); changed = true; break; }
    // 2nd choice: shrink the diagram, down to SHRINK of its size
    if (bl.done) continue;
    const room = gap[n - 1] - 8;
    const target = bl.svgMM - (bl.blockMM - room);
    if (target / bl.svgMM < SHRINK) continue;
    await page.evaluate(({ k, f }) => {
      const b = document.querySelectorAll('.dginline')[k], s = b.querySelector('svg');
      s.setAttribute('width', +s.getAttribute('width') * f);
      s.setAttribute('height', +s.getAttribute('height') * f);
      b.dataset.done = '1';
    }, { k: bl.k, f: target / bl.svgMM });
    console.log(`diagrama ${bl.k}: reduzido a ${(target / bl.svgMM * 100).toFixed(0)}% para caber na página ${n}`);
    changed = true;
    break;
  }
  if (!changed) break;
}
// find the page of each heading, then write the numbers into the Sumário
const pages = pageTexts();
const heads = await page.evaluate(() => [...document.querySelectorAll('#toc a')].map(a => a.textContent.replace(/\s+/g, ' ').trim()));
let from = 2;
const nums = heads.map(h => {
  const key = h.replace(/\s+/g, '').slice(0, 30);
  for (let n = from; n < pages.length; n++) if (pages[n].includes(key)) { from = n; return n + 1; }
  return '';
});
await page.evaluate(nums => document.querySelectorAll('#toc a').forEach((a, k) => { a.insertAdjacentHTML('beforeend', `<span class="pg">${nums[k]}</span>`); }), nums);
await page.pdf({ ...pdfOpts, path: tmp });
// cover without page number
await page.evaluate(() => { document.body.innerHTML = document.querySelector('.capa').outerHTML; });
const capa = out + '.capa.pdf';
await page.pdf({ ...pdfOpts, displayHeaderFooter: false, path: capa });
await browser.close();
execFileSync('python3', ['-c', `
import sys
from pypdf import PdfReader, PdfWriter
c, b, o = sys.argv[1:4]
w = PdfWriter()
w.add_page(PdfReader(c).pages[0])
for p in PdfReader(b).pages[1:]: w.add_page(p)
w.add_metadata({'/Title': 'Documentação Arc42: Deviante', '/Author': 'Alander Menezes Arantes de Ávila; Emanuelle Skolut Jose'})
w.write(o)
`, capa, tmp, out]);
fs.rmSync(tmp); fs.rmSync(capa);
