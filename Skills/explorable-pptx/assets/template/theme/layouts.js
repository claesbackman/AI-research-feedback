/* theme/layouts.js — the slide vocabulary: how each frame kind becomes a slide.
 *
 * A frame in deck.js is an object. `kind` picks a plain frame (title, divider,
 * assertion, appendix marker); otherwise `layout` picks the content layout and
 * the frame's fields fill its slots:
 *
 *   layout      slots and fields
 *   prose       prose; optional stats, q, aside, sources
 *   beside      prose (36 %) beside stage or fig (60 %); center: true centres the prose vertically
 *   wideleft    fig or stage (60 %) beside prose (36 %); optional stats under the prose
 *   stack       prose above a short stage
 *   fig         one figure full width, figcap under it; tall: true for a taller figure
 *   figpair     figs: [a, b] side by side, figcap under them
 *   even        left and right slots {head, prose, fig, stage}, equal columns
 *   cols        the same with a hairline between, for a contrast; optional q under the columns
 *   claims      claims: [[lead, text], ...] numbered
 *   stats       stats: [{k, l, color}] cards across the frame
 *   bignum      k, l: one large number, for a calculator-style frame
 *
 * Common fields: title (an assertion), notes (what to do and say), label (a
 * link target), source (a line or an array of lines), back (the label of the
 * frame a room returns to), eyebrow.
 *
 * Every render function gets ctx = {slide, L, T, D, frame, step, steps, links,
 * charts, meta, handout}. Positions are inches.
 */
'use strict';

module.exports = function makeLayouts(L, T, log) {
  const C = T.colors, F = T.faces, S = T.sizes, G = T.geo;
  const textW = G.W - 2 * G.mx;
  const contentBottom = G.H - G.footline - G.guard;
  const content = () => ({ x: G.mx, y: G.contentY, w: textW, h: contentBottom - G.contentY });

  // ---------- pieces ----------
  const title = (ctx) => {
    const f = ctx.frame;
    let y = G.titleY, h = G.titleH;
    if (f.eyebrow) { L.text(ctx.slide, f.eyebrow.toUpperCase(), { x: G.mx, y: G.titleY - 0.02, w: textW, h: 0.22 }, L.role('eyebrow')); y += 0.24; h -= 0.24; }
    const est = L.estimateHeight(f.title, textW, L.role('title'), { paraSpace: 0 });
    if (est > h + 0.05) log(`frame ${ctx.n}: the title probably runs to a third line (${f.title.slice(0, 40)}…)`);
    L.text(ctx.slide, f.title, { x: G.mx, y, w: textW, h }, L.role('title'), { valign: 'top', lineSpacing: 1.05 });
  };

  const footline = (ctx) => {
    const s = ctx.slide;
    if (ctx.appendix) {
      L.label(s, `A${ctx.appendixN}`, G.W - G.mx - 1, G.H - 0.38, 1, 0.2, { face: F.mono, size: S.foot, align: 'right' });
      return;
    }
    L.rect(s, 0, G.H - 0.03, G.W, 0.03, { fill: 'paper3' });
    L.rect(s, 0, G.H - 0.03, G.W * ctx.n / Math.max(ctx.total, 1), 0.03, { fill: 'primary' });
    L.label(s, `${ctx.n} / ${ctx.total}`, G.W - G.mx - 1, G.H - 0.38, 1, 0.2, { face: F.mono, size: S.foot, align: 'right' });
  };

  const sourceLines = (f) => (f.source ? (Array.isArray(f.source) ? f.source : [f.source]) : []);
  // A source line (or lines) at the bottom of a box
  const source = (ctx, box, lines, align = 'left') => {
    if (!lines.length) return;
    const text = lines.join('\n\n');
    const h = L.estimateHeight(text, box.w, L.role('source'), { paraSpace: 2 }) + 0.04;
    L.text(ctx.slide, text, { x: box.x, y: box.y + box.h - h, w: box.w, h }, L.role('source'), { valign: 'bottom', align, paraSpace: 2 });
    return h;
  };
  const backLink = (ctx) => {
    const f = ctx.frame;
    if (!f.back) return;
    const n = ctx.links[f.back];
    if (!n) { log(`frame ${ctx.n}: back to '${f.back}' but no frame has that label`); return; }
    ctx.slide.addText([{ text: '← back to the talk', options: { hyperlink: { slide: n }, color: C.ink3 } }],
      { x: G.mx, y: G.H - 0.38, w: 2.5, h: 0.2, fontFace: F.label, fontSize: S.back, color: C.ink3, margin: 0, isTextBox: true, valign: 'middle' });
  };

  const stage = (ctx, name, box) => {
    const chart = ctx.charts[name];
    if (!chart) { log(`frame ${ctx.n}: unknown chart '${name}'`); L.rect(ctx.slide, box.x, box.y, box.w, box.h, { fill: 'paper3' }); L.label(ctx.slide, `unknown chart: ${name}`, box.x, box.y + box.h / 2, box.w, 0.2, { align: 'center', color: C.primary }); return; }
    try { chart.draw({ slide: ctx.slide, box, L, T, D: ctx.D, step: ctx.step, steps: ctx.steps, handout: ctx.handout, frame: ctx.frame, log }); }
    catch (e) { log(`frame ${ctx.n}: chart '${name}' threw: ${e.message}`); L.label(ctx.slide, 'This chart failed to draw.', box.x, box.y + box.h / 2, box.w, 0.2, { align: 'center', color: C.primary }); }
  };

  const stats = (ctx, items, box, opts = {}) => {
    const n = items.length, gap = 0.25, w = (box.w - gap * (n - 1)) / n;
    const kh = (opts.size || S.stat) * 1.1 / 72 + 0.05;
    items.forEach((it, i) => {
      const x = box.x + i * (w + gap);
      L.text(ctx.slide, it.k, { x, y: box.y, w, h: kh }, { fontFace: F.display, fontSize: opts.size || S.stat, color: L.col(it.color || 'ink') }, { valign: 'bottom', paraSpace: 0 });
      L.text(ctx.slide, it.l, { x, y: box.y + kh + 0.06, w, h: Math.max(0.4, box.h - kh - 0.06) }, L.role('statLabel'), { paraSpace: 2 });
    });
    return kh + 0.06 + 0.6;
  };

  const colhead = (ctx, head, box) => {
    L.text(ctx.slide, head, { x: box.x, y: box.y, w: box.w, h: 0.3 }, L.role('colhead'), { valign: 'bottom' });
    L.line(ctx.slide, box.x, box.y + 0.36, box.x + box.w, box.y + 0.36, { color: 'line', width: 0.75 });
    return 0.48;
  };

  // A slot: one of prose / fig / stage, with an optional head, stats and source.
  const slot = (ctx, sl, box, opts = {}) => {
    if (!sl) return;
    let y = box.y, h = box.h;
    if (sl.head) { const dh = colhead(ctx, sl.head, { x: box.x, y, w: box.w }); y += dh; h -= dh; }
    const src = sourceLines(sl);
    let srcH = 0;
    if (src.length) srcH = source(ctx, { x: box.x, y, w: box.w, h }, src) + 0.12;
    const inner = { x: box.x, y, w: box.w, h: h - srcH };
    if (sl.stage) { stage(ctx, sl.stage, { x: inner.x, y: inner.y, w: inner.w, h: Math.min(inner.h, sl.tall ? G.stage.tall : sl.short ? G.stage.short : G.stage.h) }); return; }
    if (sl.fig) { L.image(ctx.slide, sl.fig, { x: inner.x, y: inner.y, w: inner.w, h: Math.min(inner.h, sl.tall ? G.fig.tall : G.fig.h) }); return; }
    if (sl.prose !== undefined) {
      let statsH = 0;
      if (sl.stats) { statsH = 0.95 + 0.2; }
      const est = L.estimateHeight(sl.prose, inner.w, L.role('body'));
      const avail = inner.h - statsH;
      if (est > avail + 0.05) log(`frame ${ctx.n}: prose probably overflows its column (about ${est.toFixed(1)} in of text in ${avail.toFixed(1)} in); split the frame`);
      const center = opts.center && !sl.stats && !sl.aside;   // a column with a stat card under the prose stacks from the top
      L.text(ctx.slide, sl.prose, { x: inner.x, y: inner.y, w: inner.w, h: center ? avail : Math.min(avail, est + 0.1) }, L.role('body'), { valign: center ? 'middle' : 'top' });
      if (sl.stats) stats(ctx, sl.stats, { x: inner.x, y: inner.y + Math.min(avail, est + 0.1) + 0.15, w: inner.w, h: statsH }, { size: S.stat * 0.8 });
      if (sl.aside) { const ay = inner.y + Math.min(avail, est + 0.1) + 0.15; L.line(ctx.slide, inner.x, ay, inner.x, ay + 0.5, { color: 'line', width: 1.5 }); L.text(ctx.slide, sl.aside, { x: inner.x + 0.15, y: ay, w: inner.w - 0.15, h: 0.6 }, L.role('aside')); }
    }
  };

  // ---------- layouts ----------
  const LAY = {};

  LAY.prose = (ctx) => {
    const f = ctx.frame, b = content();
    const src = sourceLines(f);
    let srcH = src.length ? source(ctx, b, src) + 0.1 : 0;
    const box = { x: b.x, y: b.y, w: Math.min(b.w, f.wide ? b.w : 7.2), h: b.h - srcH };
    let y = b.y;
    if (f.prose !== undefined) {
      const est = L.estimateHeight(f.prose, box.w, L.role('body'));
      L.text(ctx.slide, f.prose, { x: box.x, y, w: box.w, h: Math.min(box.h, est + 0.1) }, L.role('body'));
      y += Math.min(box.h, est + 0.1) + 0.25;
    }
    if (f.q) { const qh = L.estimateHeight(f.q, box.w, L.role('q')) + 0.1; L.text(ctx.slide, f.q, { x: box.x, y, w: box.w, h: qh }, L.role('q'), { lineSpacing: 1.1 }); y += qh + 0.2; }
    if (f.stats) y += stats(ctx, f.stats, { x: b.x, y, w: b.w, h: 1.3 });
    if (y > b.y + box.h + 0.05) log(`frame ${ctx.n}: content probably reaches the footline; split the frame`);
  };

  const twoCol = (ctx, leftShare, rightShare, left, right, opts = {}) => {
    const b = content();
    const lw = textW * leftShare, rw = textW * rightShare;
    const gap = textW - lw - rw;
    slot(ctx, left, { x: b.x, y: b.y, w: lw, h: b.h }, opts);
    slot(ctx, right, { x: b.x + lw + gap, y: b.y, w: rw, h: b.h }, opts);
    if (opts.rule) { const rh = ctx.frame.rule || b.h * 0.55; L.line(ctx.slide, b.x + lw + gap / 2, b.y, b.x + lw + gap / 2, b.y + rh, { color: 'line', width: 0.75 }); }
  };

  LAY.beside = (ctx) => {
    const f = ctx.frame;
    twoCol(ctx, G.narrow, G.wide,
      { prose: f.prose, source: f.source, stats: f.stats, aside: f.aside },
      f.stage ? { stage: f.stage, tall: f.tall } : { fig: f.fig, tall: f.tall },
      { center: f.center !== false });
  };
  LAY.wideleft = (ctx) => {
    const f = ctx.frame;
    twoCol(ctx, G.wide, G.narrow,
      f.stage ? { stage: f.stage, tall: f.tall } : { fig: f.fig, tall: f.tall },
      { prose: f.prose, source: f.source, stats: f.stats, aside: f.aside },
      { center: f.center !== false });
  };
  LAY.even = (ctx) => { const f = ctx.frame; twoCol(ctx, 0.48, 0.48, f.left, f.right, { center: !!f.center }); };
  LAY.cols = (ctx) => {
    const f = ctx.frame; twoCol(ctx, 0.46, 0.46, f.left, f.right, { rule: true });
    if (f.q) { const b = content(); const rh = f.rule || b.h * 0.55; L.text(ctx.slide, f.q, { x: b.x, y: b.y + rh + 0.25, w: b.w, h: b.h - rh - 0.25 }, L.role('q'), { lineSpacing: 1.1 }); }
    const src = sourceLines(f); if (src.length) source(ctx, content(), src);
  };
  LAY.stack = (ctx) => {
    const f = ctx.frame, b = content();
    const est = L.estimateHeight(f.prose || '', Math.min(b.w, 8), L.role('body'));
    const ph = Math.min(est + 0.1, b.h - G.stage.short - 0.2);
    if (f.prose) L.text(ctx.slide, f.prose, { x: b.x, y: b.y, w: Math.min(b.w, 8), h: ph }, L.role('body'));
    const sb = { x: b.x, y: b.y + ph + 0.2, w: b.w, h: G.stage.short };
    if (f.stage) stage(ctx, f.stage, sb); else if (f.fig) L.image(ctx.slide, f.fig, sb);
    const src = sourceLines(f); if (src.length) source(ctx, b, src);
  };
  LAY.fig = (ctx) => {
    const f = ctx.frame, b = content();
    const capH = f.figcap ? L.estimateHeight(f.figcap, b.w, L.role('figcap')) + 0.1 : 0;
    const h = Math.min(f.tall ? G.fig.tall : G.fig.h, b.h - capH - 0.1);
    if (f.stage) stage(ctx, f.stage, { x: b.x, y: b.y, w: b.w, h }); else L.image(ctx.slide, f.fig, { x: b.x, y: b.y, w: b.w, h });
    if (f.figcap) L.text(ctx.slide, f.figcap, { x: b.x, y: b.y + h + 0.1, w: b.w, h: capH }, L.role('figcap'), { align: 'center' });
    const src = sourceLines(f); if (src.length) source(ctx, b, src);
  };
  LAY.figpair = (ctx) => {
    const f = ctx.frame, b = content();
    const capH = f.figcap ? L.estimateHeight(f.figcap, b.w, L.role('figcap')) + 0.1 : 0;
    const h = Math.min(G.fig.pair, b.h - capH - 0.1), w = (b.w - 0.3) / 2;
    (f.figs || []).slice(0, 2).forEach((fig, i) => L.image(ctx.slide, fig, { x: b.x + i * (w + 0.3), y: b.y, w, h }));
    if (f.figcap) L.text(ctx.slide, f.figcap, { x: b.x, y: b.y + h + 0.1, w: b.w, h: capH }, L.role('figcap'), { align: 'center' });
  };
  LAY.claims = (ctx) => {
    const f = ctx.frame, b = content();
    const runs = [];
    (f.claims || []).forEach(([lead, text], i, arr) => {
      const last = i === arr.length - 1;
      if (lead) runs.push({ text: lead + ' ', options: { bold: true, fontFace: F.display, color: C.ink, bullet: { type: 'number' }, paraSpaceAfter: 10, indentLevel: 0 } });
      const body = L.runs(text, L.role('claim'), { paraSpace: 10 });
      if (!lead && body.length) body[0].options.bullet = { type: 'number' };
      body.forEach((r) => { r.options.paraSpaceAfter = 10; });
      if (!last && body.length) body[body.length - 1].options.breakLine = true;
      runs.push(...body);
    });
    ctx.slide.addText(runs, { x: b.x, y: b.y, w: Math.min(b.w, 8), h: b.h, fontFace: F.body, fontSize: S.claim, color: C.ink, valign: 'top', margin: 0, isTextBox: true, lineSpacingMultiple: G.lineHeight, fit: 'none' });
    const est = (f.claims || []).reduce((a, [lead, text]) => a + L.estimateHeight((lead || '') + ' ' + text, Math.min(b.w, 8) - 0.4, L.role('claim')) + 10 / 72, 0);
    if (est > b.h + 0.05) log(`frame ${ctx.n}: the claims probably reach the footline; fewer or shorter claims`);
    const src = sourceLines(f); if (src.length) source(ctx, b, src);
  };
  LAY.stats = (ctx) => {
    const f = ctx.frame, b = content();
    const items = f.stats || [];
    stats(ctx, items, { x: b.x, y: b.y + 0.3, w: b.w, h: 1.6 });
    if (f.prose) L.text(ctx.slide, f.prose, { x: b.x, y: b.y + 2.1, w: Math.min(b.w, 7.2), h: b.h - 2.1 }, L.role('body'));
    const src = sourceLines(f); if (src.length) source(ctx, b, src);
  };
  LAY.bignum = (ctx) => {
    const f = ctx.frame, b = content();
    L.text(ctx.slide, f.k || '', { x: b.x, y: b.y + 0.4, w: b.w, h: 1.1 }, { fontFace: F.display, fontSize: S.bignum, color: L.col(f.color || 'ink') }, { align: 'center', valign: 'bottom', paraSpace: 0 });
    L.text(ctx.slide, f.l || '', { x: b.x + 1.5, y: b.y + 1.6, w: b.w - 3, h: 0.5 }, { fontFace: F.label, fontSize: S.bignumLabel, color: C.ink3 }, { align: 'center' });
    if (f.prose) L.text(ctx.slide, f.prose, { x: b.x + 1.5, y: b.y + 2.2, w: b.w - 3, h: b.h - 2.2 }, L.role('body'), { align: 'center' });
    const src = sourceLines(f); if (src.length) source(ctx, b, src);
  };

  // ---------- plain frames ----------
  const KIND = {};
  KIND.title = (ctx) => {
    const m = ctx.meta, s = ctx.slide;
    let y = 1.1;
    if (m.subtitle) { L.text(s, m.subtitle.toUpperCase(), { x: G.mx, y, w: textW, h: 0.25 }, L.role('eyebrow')); y += 0.4; }
    const th = L.estimateHeight(m.title, textW, { fontFace: F.display, fontSize: S.titleSlide }, { paraSpace: 0 }) + 0.1;
    L.text(s, m.title, { x: G.mx, y, w: textW, h: th }, { fontFace: F.display, fontSize: S.titleSlide, color: C.ink, charSpacing: -0.5 }, { lineSpacing: 1.05 });
    y += th + 0.4;
    if (m.authors) { L.text(s, m.authors, { x: G.mx, y, w: textW, h: 0.3 }, { fontFace: F.body, fontSize: S.author, color: C.ink }); y += 0.32; }
    if (m.institute) { L.text(s, m.institute, { x: G.mx, y, w: textW, h: 0.25 }, { fontFace: F.label, fontSize: S.institute, color: C.ink3 }); y += 0.28; }
    if (m.date) L.text(s, m.date, { x: G.mx, y, w: textW, h: 0.25 }, { fontFace: F.label, fontSize: S.institute, color: C.ink3 });
  };
  KIND.divider = (ctx) => {
    const f = ctx.frame, s = ctx.slide;
    let y = 1.3;
    if (f.eyebrow) { L.text(s, f.eyebrow.toUpperCase(), { x: G.mx, y, w: textW, h: 0.25 }, L.role('eyebrow')); y += 0.4; }
    L.text(s, f.title, { x: G.mx, y, w: textW, h: 2.6 }, { fontFace: F.display, fontSize: S.divider, color: C.ink, charSpacing: -0.5 }, { lineSpacing: 1.05 });
  };
  KIND.assertion = (ctx) => {
    const f = ctx.frame;
    L.text(ctx.slide, f.title, { x: G.mx, y: 1.3, w: textW, h: 3 }, { fontFace: F.display, fontSize: S.assertion, color: C.ink, charSpacing: -0.5 }, { lineSpacing: 1.1 });
  };

  // ---------- entry ----------
  return {
    render(ctx) {
      const f = ctx.frame;
      ctx.slide.background = { color: C.paper };
      if (f.kind && KIND[f.kind]) { KIND[f.kind](ctx); return; }
      if (f.kind) { log(`frame ${ctx.n}: unknown kind '${f.kind}'`); return; }
      title(ctx);
      const lay = LAY[f.layout || 'prose'];
      if (!lay) { log(`frame ${ctx.n}: unknown layout '${f.layout}'`); return; }
      lay(ctx);
      footline(ctx);
      backLink(ctx);
    },
    isPlain: (f) => !!f.kind,
  };
};
