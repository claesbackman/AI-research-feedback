/* build.js — build deck.pptx (and deck-handout.pptx) from deck.js.
 *
 *   node build.js              deck.pptx and deck-handout.pptx, _build/manifest*.json, _build/build-log.txt
 *   node build.js --fast       deck.pptx only
 *
 * A frame with a stepped stage becomes one slide per step (the chart module
 * declares `steps`); the handout keeps the last step of every frame, so it
 * shows every stage finished. Frames after {kind: 'appendix'} are rooms,
 * numbered A1, A2, … in the footline. The manifest maps every slide to its
 * frame and step for shoot.py and check_deck.py. Every warning the build
 * raises (an undefined number, an unknown chart, a link to no label, prose
 * that probably overflows) goes to the log, which shoot.py prints.
 */
'use strict';
const fs = require('fs');
const path = require('path');

const HERE = __dirname;
const BUILD = path.join(HERE, '_build');
let pptxgen;
try { pptxgen = require('pptxgenjs'); }
catch (e) { console.error('pptxgenjs not found: run  sh build.sh  (it installs it), or npm install'); process.exit(1); }

const T = require('./theme/theme');
const D = require('./data/numbers');
const deck = require('./deck');
const makeLib = require('./theme/lib');
const makeLayouts = require('./theme/layouts');

const LOG = [];
const log = (m) => { if (!LOG.includes(m)) LOG.push(m); };

// charts/*.js → { name: module }
const charts = {};
const chartDir = path.join(HERE, 'charts');
if (fs.existsSync(chartDir)) for (const f of fs.readdirSync(chartDir)) if (f.endsWith('.js')) {
  const name = f.replace(/\.js$/, '');
  charts[name] = require(path.join(chartDir, f));
  charts[name].hasCaption = /\bstagecap\s*\(/.test(fs.readFileSync(path.join(chartDir, f), 'utf8'));   // a stage's own caption counts as its source line
}

// ---------- pass 1: frames → slides ----------
function plan(frames, handout) {
  const out = [];           // one entry per slide
  let n = 0, nApp = 0, appendix = false, total = 0;
  const links = {};
  const frameList = [];
  for (const f of frames) {
    if (f.kind === 'appendix') { appendix = true; continue; }
    if (appendix) nApp += 1; else n += 1;
    const chartName = f.stage || (f.left && f.left.stage) || (f.right && f.right.stage);
    let steps = f.steps || (chartName && charts[chartName] && charts[chartName].steps) || 1;
    if (f.stage && !charts[f.stage]) log(`frame ${n}: unknown chart '${f.stage}'`);
    const fr = { frame: f, n: appendix ? nApp : n, appendix, steps, label: f.label || null };
    frameList.push(fr);
    if (f.label) links[f.label] = out.length + 1;   // the first slide of the frame
    const first = handout ? steps : 1;
    for (let s = first; s <= steps; s++) out.push({ ...fr, step: s, page: out.length + 1 });
  }
  total = n;
  return { slides: out, links, total, frameList };
}

async function build(handout) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  pres.title = deck.meta.title || 'deck';
  pres.author = deck.meta.authors || '';
  pres.theme = { headFontFace: T.faces.display, bodyFontFace: T.faces.body };
  const L = makeLib(pres, T, D, log);
  Object.assign(L.aliases, deck.aliases || {});
  const layouts = makeLayouts(L, T, log);
  const { slides, links, total, frameList } = plan(deck.frames, handout);
  L.links = links;

  for (const sl of slides) {
    const slide = pres.addSlide();
    const ctx = { slide, L, T, D, frame: sl.frame, step: sl.step, steps: sl.steps, links, charts, meta: deck.meta, handout, n: sl.n, total, appendix: sl.appendix, appendixN: sl.n, log };
    layouts.render(ctx);
    if (sl.frame.notes) slide.addNotes(L.plain(sl.frame.notes));
    else if (!sl.frame.kind) log(`frame ${sl.n}${sl.appendix ? ' (appendix)' : ''}: no notes`);
  }

  const name = handout ? 'deck-handout.pptx' : 'deck.pptx';
  await pres.writeFile({ fileName: path.join(HERE, name) });

  // the manifest: slides and frames, for shoot.py and check_deck.py
  const manifest = {
    file: name, handout, total,
    slides: slides.map((s) => ({ page: s.page, frame: s.appendix ? `A${s.n}` : s.n, step: s.step, steps: s.steps, appendix: s.appendix, title: s.frame.title ? L.plain(s.frame.title) : (s.frame.kind === 'title' ? L.plain(deck.meta.title) : ''), kind: s.frame.kind || null })),
    frames: frameList.map((fr) => {
      const f = fr.frame;
      const slots = [f, f.left || {}, f.right || {}];
      const text = JSON.stringify(f);
      return {
        n: fr.n, appendix: fr.appendix, label: fr.label, kind: f.kind || null, layout: f.kind ? null : (f.layout || 'prose'),
        title: f.title ? L.plain(f.title) : '', steps: fr.steps,
        hasStage: slots.some((s) => !!s.stage), hasFig: slots.some((s) => !!s.fig) || !!f.figs,
        hasSource: slots.some((s) => !!s.source) || !!f.figcap || slots.some((s) => s.stage && charts[s.stage] && charts[s.stage].hasCaption), hasNotes: !!f.notes,
        hasBuildIn: fr.steps > 1,
        links: [...text.matchAll(/\]\(#([\w:-]+)\)/g)].map((m) => m[1]).concat(f.back ? [f.back] : []),
        dataKeys: [...text.matchAll(/\{\{([^}:]+)(?::\d+)?\}\}/g)].map((m) => m[1].trim()),
        proseChars: slots.reduce((a, s) => a + (s.prose ? L.plain(s.prose).length : 0), 0),
      };
    }),
    labels: links,
  };
  fs.mkdirSync(BUILD, { recursive: true });
  fs.writeFileSync(path.join(BUILD, handout ? 'manifest-handout.json' : 'manifest.json'), JSON.stringify(manifest, null, 1));
  return { slides: slides.length, frames: frameList.length, total };
}

(async () => {
  const fast = process.argv.includes('--fast');
  fs.mkdirSync(BUILD, { recursive: true });
  const r = await build(false);
  let msg = `built deck.pptx: ${r.slides} slides, ${r.frames} frames (${r.total} counted)`;
  if (!fast) { const h = await build(true); msg += `; deck-handout.pptx: ${h.slides} slides`; }
  else msg += ' (--fast: handout not rebuilt)';
  fs.writeFileSync(path.join(BUILD, 'build-log.txt'), LOG.join('\n') + (LOG.length ? '\n' : ''));
  console.log(msg);
  if (LOG.length) { console.log('build messages:'); for (const m of LOG) console.log('  -', m); }
})().catch((e) => { console.error(e); process.exit(1); });
