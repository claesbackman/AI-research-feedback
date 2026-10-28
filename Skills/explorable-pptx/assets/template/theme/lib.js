/* theme/lib.js — drawing helpers for the deck and the stages.
 *
 * makeLib(pres, theme, data, log) returns L, the object every layout and chart
 * draws with. All positions are inches on the 10 × 5.625 in canvas. Colours
 * are token names ('primary', 'ink3') or topic aliases set in deck.js; L.col
 * resolves them to hex. Text in prose, captions and stat labels is written in
 * the deck's markup and parsed by L.runs:
 *
 *     **bold**  *italic*  `mono`
 *     [text]{primary}  [text]{contrast} [text]{actora} [text]{actorb}   coloured emphasis (or an alias)
 *     [text]{muted}  [text]{num}                                        grey, or the mono face
 *     {{reveal/gap}}  {{ladder.0.beta:3}}                               a number from data/numbers.js, :d decimals
 *     [text](#label)                                                    a link to the frame with that label
 *
 * A number that data/numbers.js does not define prints ?? in the primary
 * colour and writes "DATA: undefined key" to the build log, which shoot.py
 * reports.
 */
'use strict';

module.exports = function makeLib(pres, T, D, log) {
  const L = {};
  const C = T.colors, F = T.faces, S = T.sizes, G = T.geo;
  const aliases = {};
  L.aliases = aliases;                           // filled by build.js from deck.aliases
  L.links = {};                                  // label → slide number, set by build.js before rendering

  // ---------- colours and numbers ----------
  L.col = (name) => {
    if (!name) return C.ink;
    if (/^[0-9A-Fa-f]{6}$/.test(name)) return name.toUpperCase();
    const key = aliases[name] || name;
    if (C[key]) return C[key];
    log(`COLOUR: unknown colour '${name}'`);
    return C.primary;
  };
  const MINUS = '−';
  L.get = (path) => {
    const parts = String(path).split(/[./]/);
    let o = D;
    for (const k of parts) { if (o == null) return undefined; o = o[k]; }
    return o;
  };
  L.num = (path, d) => {
    const v = L.get(path);
    if (v === undefined) { log(`DATA: undefined key ${path}`); return null; }
    return L.fmtNum(v, d);
  };
  L.fmtNum = (x, d) => {
    if (typeof x !== 'number') return String(x);
    const s = d === undefined ? String(Math.abs(x)) : Math.abs(x).toFixed(d);
    return (x < 0 ? MINUS : '') + s;
  };
  L.fmtPct = (x, d = 1) => L.fmtNum(x, d) + '%';
  L.fmtInt = (x) => Math.round(x).toLocaleString('en');
  L.clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  L.lerp = (a, b, t) => a + (b - a) * t;
  // A tick step giving about n ticks over a range, at 1, 2 or 5 × a power of ten
  L.niceStep = (range, n = 5) => {
    const raw = Math.abs(range) / n || 1, p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p;
    return (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p;
  };
  L.ticks = (lo, hi, step) => { const out = []; for (let v = Math.ceil(lo / step) * step; v <= hi + step / 2; v += step) out.push(+v.toFixed(8)); return out; };
  // Seeded RNG (mulberry32) so stylised dots are identical on every build
  L.rng = (seed) => { let a = seed >>> 0; return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
  L.randn = (r) => { let u = 0, v = 0; while (u === 0) u = r(); while (v === 0) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };

  // ---------- text ----------
  // Base run options for a role. Every text box names its face and size, so a
  // change here changes the whole deck.
  const ROLE = {
    body:     () => ({ fontFace: F.body, fontSize: S.body, color: C.ink }),
    label:    () => ({ fontFace: F.label, fontSize: S.tick, color: C.ink3 }),
    source:   () => ({ fontFace: F.label, fontSize: S.source, color: C.ink3 }),
    figcap:   () => ({ fontFace: F.body, fontSize: S.figcap, color: C.ink2 }),
    stagecap: () => ({ fontFace: F.body, fontSize: S.stagecap, color: C.ink3 }),
    q:        () => ({ fontFace: F.display, fontSize: S.q, color: C.ink }),
    colhead:  () => ({ fontFace: F.display, fontSize: S.colhead, color: C.ink }),
    eyebrow:  () => ({ fontFace: F.display, fontSize: S.eyebrow, color: C.ink3, charSpacing: 2 }),
    title:    () => ({ fontFace: F.display, fontSize: S.title, color: C.ink, charSpacing: -0.5 }),
    card:     () => ({ fontFace: F.label, fontSize: S.card, color: C.ink }),
    legend:   () => ({ fontFace: F.label, fontSize: S.legend, color: C.ink2 }),
    statLabel:() => ({ fontFace: F.body, fontSize: S.statLabel, color: C.ink2 }),
    aside:    () => ({ fontFace: F.body, fontSize: S.aside, color: C.ink2 }),
    back:     () => ({ fontFace: F.label, fontSize: S.back, color: C.ink3 }),
  };
  L.role = (name) => (ROLE[name] || ROLE.body)();

  // Parse the markup into pptxgenjs runs. opts.links maps labels to slide numbers.
  const INLINE = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\{[\w-]+\}|\[[^\]]+\]\(#[\w:-]+\)|\[[^\]]+\]\([^)]+\)|\{\{[^}]+\}\})/;
  const parseInline = (para, base, opts) => {
    const runs = [];
    for (const piece of para.split(INLINE).filter((s) => s !== '')) {
      let m;
      const o = { ...base };
      if ((m = /^\*\*([^*]+)\*\*$/.exec(piece))) { runs.push(...parseInline(m[1], { ...o, bold: true }, opts)); continue; }
      if ((m = /^\*([^*]+)\*$/.exec(piece))) { runs.push(...parseInline(m[1], { ...o, italic: true }, opts)); continue; }
      if ((m = /^`([^`]+)`$/.exec(piece))) { runs.push({ text: m[1], options: { ...o, fontFace: F.mono, fontSize: (base.fontSize || S.body) * 0.92 } }); continue; }
      if ((m = /^\[([^\]]+)\]\{([\w-]+)\}$/.exec(piece))) {
        const tok = m[2];
        if (tok === 'num') { o.fontFace = F.mono; o.fontSize = (base.fontSize || S.body) * 0.92; }
        else if (tok === 'muted') { o.color = C.ink3; }
        else { o.color = L.col(tok); o.bold = true; }
        runs.push(...parseInline(m[1], o, opts)); continue;
      }
      if ((m = /^\[([^\]]+)\]\(#([\w:-]+)\)$/.exec(piece))) {
        const links = opts.links || L.links || {}; const n = links[m[2]];
        if (n) { o.hyperlink = { slide: n, tooltip: m[2] }; o.color = C.ink2; }
        else { log(`LINK: no frame has label '${m[2]}'`); o.color = C.primary; }
        runs.push({ text: m[1], options: o });
        runs.push({ text: ' \u2192', options: { ...base, color: C.ink3 } });
        continue;
      }
      if ((m = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(piece))) { runs.push({ text: m[1], options: { ...o, hyperlink: { url: m[2] }, color: C.ink2 } }); continue; }
      if ((m = /^\{\{([^}:]+)(?::(\d+))?\}\}$/.exec(piece))) {
        const v = L.num(m[1].trim(), m[2] === undefined ? undefined : +m[2]);
        if (v === null) runs.push({ text: '??', options: { ...o, color: C.primary, bold: true } }); else runs.push({ text: v, options: o });
        continue;
      }
      runs.push({ text: piece, options: o });
    }
    return runs;
  };
  L.runs = (text, base = {}, opts = {}) => {
    const out = [];
    const paras = String(text).replace(/\r/g, '').split(/\n\s*\n/).map((p) => p.replace(/\s*\n\s*/g, ' ').trim()).filter(Boolean);
    paras.forEach((para, pi) => {
      const last = pi === paras.length - 1;
      const runs = parseInline(para, base, opts);
      // paragraph properties go on every run of the paragraph; the break on its last run
      runs.forEach((r) => { r.options.paraSpaceAfter = last ? 0 : (opts.paraSpace !== undefined ? opts.paraSpace : G.paraSpace); if (opts.align) r.options.align = opts.align; });
      if (!last && runs.length) runs[runs.length - 1].options.breakLine = true;
      out.push(...runs);
    });
    return out;
  };
  // Plain text of a markup string (for notes, estimates, manifest)
  L.plain = (text) => String(text).replace(/\{\{([^}:]+)(?::(\d+))?\}\}/g, (_, p, d) => L.num(p.trim(), d === undefined ? undefined : +d) || '??')
    .replace(/\[([^\]]+)\]\{[\w-]+\}/g, '$1').replace(/\[([^\]]+)\]\([^)]*\)/g, '$1').replace(/[*`]/g, '');

  // Average glyph width as a fraction of the point size, per face, for the
  // overflow estimate (the screenshots are the real check).
  const GLYPH = { [F.body]: 0.50, [F.label]: 0.46, [F.display]: 0.50, [F.mono]: 0.60 };
  L.estimateHeight = (text, w, role = {}, opts = {}) => {
    const size = role.fontSize || S.body, face = role.fontFace || F.body, g = GLYPH[face] || 0.5;
    const paras = L.plain(text).split(/\n\s*\n/).map((p) => p.replace(/\s+/g, ' ').trim()).filter(Boolean);
    const charsPerLine = Math.max(8, Math.floor((w * 72) / (size * g)));
    let lines = 0;
    for (const p of paras) lines += Math.max(1, Math.ceil(p.length / charsPerLine));
    const ps = opts.paraSpace !== undefined ? opts.paraSpace : G.paraSpace;
    return (lines * size * G.lineHeight + Math.max(0, paras.length - 1) * ps) / 72;
  };

  // A text box. box = {x, y, w, h}. opts override the role (align, valign, bold, ...).
  L.text = (slide, text, box, role = {}, opts = {}) => {
    const runs = Array.isArray(text) ? text : L.runs(text, role, opts);
    slide.addText(runs, {
      x: box.x, y: box.y, w: box.w, h: box.h,
      fontFace: role.fontFace || F.body, fontSize: role.fontSize || S.body, color: role.color || C.ink,
      align: opts.align || 'left', valign: opts.valign || 'top', margin: 0, isTextBox: true,
      bold: !!opts.bold, italic: !!opts.italic, rotate: opts.rotate || 0, fit: 'none', wrap: opts.wrap !== false,
      charSpacing: role.charSpacing, lineSpacingMultiple: opts.lineSpacing || G.lineHeight,
    });
  };
  // A one-line label for charts: no wrap, exact placement.
  L.label = (slide, str, x, y, w, h, opts = {}) => {
    slide.addText(String(str), {
      x, y, w, h, fontFace: opts.face || F.label, fontSize: opts.size || S.tick, color: opts.color || C.ink3,
      bold: !!opts.bold, align: opts.align || 'left', valign: opts.valign || 'middle', margin: 0, isTextBox: true,
      rotate: opts.rotate || 0, wrap: false, fit: 'none',
    });
  };

  // ---------- shapes ----------
  const SH = pres.shapes;
  L.line = (slide, x1, y1, x2, y2, opts = {}) => {
    const w = Math.abs(x2 - x1), h = Math.abs(y2 - y1);
    if (w < 1e-6 && h < 1e-6) return;
    slide.addShape(SH.LINE, {
      x: Math.min(x1, x2), y: Math.min(y1, y2), w, h,
      line: { color: L.col(opts.color || 'line'), width: opts.width || 1, dashType: opts.dash || 'solid', transparency: opts.transparency || 0 },
      flipV: (x2 - x1) * (y2 - y1) < 0,
    });
  };
  const fillOpts = (opts) => {
    const o = {};
    if (opts.fill) o.fill = { color: L.col(opts.fill), transparency: opts.transparency || 0 };
    if (opts.line) o.line = { color: L.col(opts.line), width: opts.width || 0.75, dashType: opts.dash || 'solid' };
    return o;
  };
  L.rect = (slide, x, y, w, h, opts = {}) => { if (w <= 0 || h <= 0) return; slide.addShape(SH.RECTANGLE, { x, y, w, h, ...fillOpts(opts) }); };
  L.rrect = (slide, x, y, w, h, opts = {}) => slide.addShape(SH.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: opts.radius || 0.05, ...fillOpts(opts) });
  L.dot = (slide, cx, cy, r, opts = {}) => slide.addShape(SH.OVAL, { x: cx - r, y: cy - r, w: 2 * r, h: 2 * r, ...fillOpts(opts) });
  // The hatched rectangle: the second visual channel. Soft fill plus diagonal
  // strokes clipped to the box.
  L.hatchRect = (slide, x, y, w, h, color, opts = {}) => {
    if (w <= 0 || h <= 0) return;
    const c = L.col(color), gap = opts.gap || 0.09;
    L.rect(slide, x, y, w, h, { fill: c, transparency: 84, line: c, width: opts.width || 0.75 });
    for (let k = gap; k < w + h; k += gap) {   // (x − x0) + (y − y0) = k, slope −1, lower-left to upper-right
      const xs = x + Math.max(0, k - h), ys = y + Math.min(k, h);
      const xe = x + Math.min(k, w), ye = y + Math.max(0, k - w);
      L.line(slide, xs, ys, xe, ye, { color: c, width: opts.width || 0.75 });
    }
  };
  // A following card: text on paper with a hairline, anchored above or beside a point.
  L.card = (slide, text, x, y, opts = {}) => {
    const w = opts.w || 1.6, h = opts.h || 0.36, anchor = opts.anchor || 'above';
    let bx = x - w / 2, by = y - h - 0.12;
    if (anchor === 'right') { bx = x + 0.12; by = y - h / 2; }
    if (anchor === 'left') { bx = x - w - 0.12; by = y - h / 2; }
    if (anchor === 'below') { by = y + 0.12; }
    if (opts.keepIn) { bx = L.clamp(bx, opts.keepIn.x, opts.keepIn.x + opts.keepIn.w - w); by = L.clamp(by, opts.keepIn.y, opts.keepIn.y + opts.keepIn.h - h); }
    L.rrect(slide, bx, by, w, h, { fill: 'paper', line: 'line', width: 0.75, radius: 0.04 });
    const runs = Array.isArray(text) ? text : L.runs(text, ROLE.card());
    slide.addText(runs, { x: bx + 0.08, y: by, w: w - 0.16, h, fontFace: F.label, fontSize: S.card, color: C.ink, valign: 'middle', align: opts.align || 'left', margin: 0, isTextBox: true, wrap: true, fit: 'none' });
  };
  L.handle = (slide, x, y, opts = {}) => L.dot(slide, x, y, opts.r || 0.075, { fill: opts.color || 'primary', line: 'paper', width: 1.5 });
  L.swatch = (slide, x, y, color, opts = {}) => {
    const s = opts.size || 0.12;
    if (opts.hatched) L.hatchRect(slide, x, y, s, s, color, { gap: 0.04, width: 0.6 }); else L.rect(slide, x, y, s, s, { fill: color });
  };

  // ---------- the stage ----------
  // A stage box is {x, y, w, h}. The caption sits in the bottom capH; a legend
  // above it. L.chartArea returns what is left for the picture.
  L.chartArea = (box, opts = {}) => {
    let h = box.h - (opts.caption === false ? 0 : G.capH) - (opts.legend ? G.legendH : 0);
    return { x: box.x, y: box.y, w: box.w, h };
  };
  L.stagecap = (slide, box, text) => L.text(slide, text, { x: box.x, y: box.y + box.h - G.capH, w: box.w, h: G.capH }, ROLE.stagecap(), { align: 'center', valign: 'bottom', paraSpace: 0 });
  // items: [{label, color, hatched}]
  L.legend = (slide, box, items, opts = {}) => {
    const y = box.y + box.h - (opts.caption === false ? 0 : G.capH) - G.legendH + 0.02;
    const widths = items.map((it) => 0.2 + it.label.length * S.legend * 0.46 / 72 + 0.22);
    const total = widths.reduce((a, b) => a + b, 0);
    let x = box.x + Math.max(0, (box.w - total) / 2);
    items.forEach((it, i) => {
      L.swatch(slide, x, y + 0.05, it.color, { hatched: it.hatched });
      L.label(slide, it.label, x + 0.18, y, widths[i] - 0.2, 0.22, { size: S.legend, color: C.ink2 });
      x += widths[i];
    });
  };

  // ---------- charts ----------
  // A chart frame inside a box: margins m (inches) for the axis labels, data
  // domains xd and yd. Returns c with c.x(v), c.y(v) mapping data to inches,
  // and the plot rectangle c.p = {x, y, w, h}.
  L.chart = (slide, box, opts = {}) => {
    const m = { l: 0.55, r: 0.2, t: 0.3, b: 0.42, ...(opts.m || {}) };
    const p = { x: box.x + m.l, y: box.y + m.t, w: box.w - m.l - m.r, h: box.h - m.t - m.b };
    const [x0, x1] = opts.xd, [y0, y1] = opts.yd;
    const x = (v) => p.x + (v - x0) / (x1 - x0) * p.w;
    const y = (v) => p.y + p.h - (v - y0) / (y1 - y0) * p.h;
    x.invert = (px) => x0 + (px - p.x) / p.w * (x1 - x0);
    return { slide, box, m, p, x, y, xd: opts.xd, yd: opts.yd };
  };
  // Grey axes and ticks, label-face tick labels, a soft horizontal grid, no box.
  L.axisX = (c, ticks, fmt = (v) => String(v), label, opts = {}) => {
    const s = c.slide, yb = c.p.y + c.p.h;
    if (opts.line !== false) L.line(s, c.p.x, yb, c.p.x + c.p.w, yb, { color: 'line', width: 0.75 });
    for (const t of ticks) {
      const tx = c.x(t);
      if (opts.ticks !== false) L.line(s, tx, yb, tx, yb + 0.05, { color: 'line', width: 0.75 });
      L.label(s, fmt(t), tx - 0.4, yb + 0.06, 0.8, 0.18, { align: 'center', ...(opts.label || {}) });
    }
    if (label) L.label(s, label, c.p.x, yb + 0.23, c.p.w, 0.18, { align: 'right', color: C.ink2 });
  };
  L.axisY = (c, ticks, fmt = (v) => String(v), label, opts = {}) => {
    const s = c.slide;
    if (opts.line !== false) L.line(s, c.p.x, c.p.y, c.p.x, c.p.y + c.p.h, { color: 'line', width: 0.75 });
    for (const t of ticks) {
      const ty = c.y(t);
      if (opts.grid !== false) L.line(s, c.p.x, ty, c.p.x + c.p.w, ty, { color: 'paper3', width: 0.75 });
      L.label(s, fmt(t), c.p.x - 0.62, ty - 0.09, 0.56, 0.18, { align: 'right' });
    }
    if (label) L.label(s, label, c.p.x, c.p.y - 0.26, c.p.w, 0.18, { align: 'left', color: C.ink2 });
  };
  // A polyline through data points [[x, y], ...]
  L.path = (c, pts, opts = {}) => { for (let i = 1; i < pts.length; i++) L.line(c.slide, c.x(pts[i - 1][0]), c.y(pts[i - 1][1]), c.x(pts[i][0]), c.y(pts[i][1]), { color: opts.color || 'primary', width: opts.width || 2, dash: opts.dash }); };
  // A bold label on or beside a bar
  L.dataLabel = (slide, str, x, y, opts = {}) => L.label(slide, str, x - 0.5, y - 0.1, 1, 0.2, { align: 'center', bold: true, size: S.dataLabel, ...opts, color: opts.color ? L.col(opts.color) : C.ink2 });

  // ---------- figures ----------
  // Pixel size of a PNG or JPEG, from its header, so a figure can be placed at
  // a fixed height with the width following.
  L.imageSize = (file) => {
    const fs = require('fs');
    const buf = fs.readFileSync(file);
    if (buf.slice(1, 4).toString() === 'PNG') return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
    if (buf[0] === 0xFF && buf[1] === 0xD8) {
      let i = 2;
      while (i < buf.length) {
        if (buf[i] !== 0xFF) { i++; continue; }
        const marker = buf[i + 1];
        if (marker >= 0xC0 && marker <= 0xCF && ![0xC4, 0xC8, 0xCC].includes(marker)) return { h: buf.readUInt16BE(i + 5), w: buf.readUInt16BE(i + 7) };
        i += 2 + buf.readUInt16BE(i + 2);
      }
    }
    return null;
  };
  // Place an image inside a box at the box height (or less), centred, width following
  L.image = (slide, file, box) => {
    const fs = require('fs');
    if (!fs.existsSync(file)) { log(`FIG: ${file} not found`); L.rect(slide, box.x, box.y, box.w, box.h, { fill: 'paper3' }); L.label(slide, `missing: ${file}`, box.x, box.y + box.h / 2 - 0.1, box.w, 0.2, { align: 'center', color: C.primary }); return; }
    const sz = L.imageSize(file) || { w: 4, h: 3 };
    let h = box.h, w = h * sz.w / sz.h;
    if (w > box.w) { w = box.w; h = w * sz.h / sz.w; }
    slide.addImage({ path: file, x: box.x + (box.w - w) / 2, y: box.y + (box.h - h) / 2, w, h });
  };

  return L;
};
