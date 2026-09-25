/* js/deck-charts.js — the deck's stages.
 *
 * A slide asks for a chart with
 *     <div class="stage" data-chart="name"></div>
 * and adds data-animate when the chart's build-in should replay every time the
 * slide is shown. A chart is CH[name] = (el, { animate }) => optional cleanup.
 * Numbers come from LIB.DATA in js/lib.js; anything stylised says so in its caption.
 *
 * The three charts below are patterns to rewrite or delete:
 *   stack-reveal   two cases, two components, building in after the room has bet
 *   line-handle    a line the presenter walks along with a draggable handle
 *   ladder         coefficients with confidence intervals down a list of specifications
 */
(function () {
  'use strict';

  function main() {
    const L = window.LIB;
    if (!L) { console.error('deck-charts.js: load js/lib.js first'); return; }
    const D = L.DATA, S = L.svg, E = L.el;
    // ?static and reveal's ?print-pdf draw every chart in its finished state; so does a reduced-motion setting
    const STATIC = /[?&](static|print-pdf)\b/.test(location.search) || L.reduced();

    // ---------- small helpers ----------
    const wrap = (svg, style) => { const d = E('div', { class: 'chart-wrap' }, [svg]); if (style) d.style.cssText = style; return d; };
    const cap = (html) => E('p', { class: 'caption', html });
    const live = (el, sel) => { const s = el.closest('section'); return s ? s.querySelector(sel) : null; };
    // Drag along x inside an svg. Returns a cleanup function.
    const dragX = (svg, onX) => {
      let down = false;
      const pt = (e) => { const p = svg.createSVGPoint(); p.x = e.clientX; p.y = e.clientY; return p.matrixTransform(svg.getScreenCTM().inverse()); };
      const up = () => { down = false; };
      svg.style.cursor = 'ew-resize'; svg.style.touchAction = 'none';
      svg.addEventListener('pointerdown', (e) => { down = true; onX(pt(e).x); });
      svg.addEventListener('pointermove', (e) => { if (down) onX(pt(e).x); });
      window.addEventListener('pointerup', up);
      return () => window.removeEventListener('pointerup', up);
    };
    const chip = (text, pressed, onClick) => { const b = E('button', { class: 'chip', text, 'aria-pressed': pressed ? 'true' : 'false' }); b.addEventListener('click', onClick); return b; };
    const press = (container, test) => [...container.querySelectorAll('.chip')].forEach((b) => b.setAttribute('aria-pressed', test(b) ? 'true' : 'false'));

    const CH = {};

    // =====================================================================
    // stack-reveal: the payoff after a bet. The first component grows in,
    // then the second, hatched, so the room watches the totals converge.
    // =====================================================================
    CH['stack-reveal'] = (el, o) => {
      const R = D.reveal, W = 600, H = 400, base = 330, top = 40;
      const svg = S('svg', { viewBox: `0 0 ${W} ${H}`, class: 'chart' });
      const hatch = L.hatch(svg, 'h-reveal', 'var(--contrast)');
      const maxTotal = Math.max(...R.cases.map((c) => c.parts[0] + c.parts[1]));
      const scale = (v) => v / maxTotal * (base - top);
      const xs = R.cases.map((_, i) => (i + 1) * W / (R.cases.length + 1));
      const els = R.cases.map((c, i) => {
        const x = xs[i], w = 110;
        const r1 = S('rect', { x: x - w / 2, width: w, y: base, height: 0, fill: 'var(--primary)' });
        const r2 = S('rect', { x: x - w / 2, width: w, y: base, height: 0, fill: hatch, stroke: 'var(--contrast)' });
        const name = S('text', { x, y: base + 28, 'text-anchor': 'middle', class: 'lbl-big', text: c.name, fill: c.color });
        const v1 = S('text', { x: x + w / 2 + 8, y: base, class: 'lbl-mono', text: '' });
        const v2 = S('text', { x: x + w / 2 + 8, y: base, class: 'lbl-mono', text: '', fill: 'var(--contrast)' });
        svg.append(r1, r2, name, v1, v2);
        return { c, r1, r2, v1, v2, k2: 0 };
      });
      svg.appendChild(S('line', { x1: 60, x2: W - 40, y1: base, y2: base, stroke: 'var(--line)' }));
      const leg = E('div', { class: 'legend' }, [
        E('span', { style: '--c:var(--primary)', text: `${R.partLabels[0]}, ${R.unit}` }),
        E('span', { class: 'hatched', style: '--c:var(--contrast)', text: `${R.partLabels[1]}, ${R.unit}` }),
      ]);
      el.append(wrap(svg), leg, cap(R.note));
      const draw1 = (k) => els.forEach((e) => {
        const h = scale(e.c.parts[0]) * k;
        e.r1.setAttribute('y', base - h); e.r1.setAttribute('height', h);
        e.v1.setAttribute('y', base - h / 2 + 4); e.v1.textContent = L.fmtPct(e.c.parts[0] * k, 1);
        const h2 = scale(e.c.parts[1]) * e.k2; e.r2.setAttribute('y', base - h - h2); e.r2.setAttribute('height', h2);
      });
      const draw2 = (k) => els.forEach((e) => {
        e.k2 = k; const h1 = scale(e.c.parts[0]), h = scale(e.c.parts[1]) * k;
        e.r2.setAttribute('y', base - h1 - h); e.r2.setAttribute('height', h);
        e.v2.setAttribute('y', base - h1 - h / 2 + 4); e.v2.textContent = k > 0.05 ? L.fmtPct(e.c.parts[1] * k, 1) : '';
      });
      if (!o.animate) { draw1(1); draw2(1); return; }
      let t = null;
      L.tween(0, 1, 1200, draw1, () => { t = setTimeout(() => L.tween(0, 1, 1600, draw2), 1400); });
      return () => { if (t) clearTimeout(t); };
    };

    // =====================================================================
    // line-handle: a fitted line with stylised dots, a handle the presenter
    // drags, and a card that says what the line predicts at that x.
    // =====================================================================
    CH['line-handle'] = (el) => {
      const P = D.line, f = (x) => P.a + P.b * (x - P.x0);
      const c = L.chart(640, 380, { l: 58, r: 20, t: 30, b: 46 }, P.xd, P.yd);
      L.axisY(c, P.yticks, (v) => v + '%', P.ylabel);
      L.axisX(c, P.xticks, (v) => v, P.xlabel);
      const r = L.rng(11), span = P.xd[1] - P.xd[0];
      for (let k = P.xd[0] + span * 0.02; k <= P.xd[1] - span * 0.02; k += span * 0.02) {
        const v = f(k) + L.randn(r) * 0.22;
        c.g.appendChild(S('circle', { cx: c.x(k), cy: c.y(v), r: 4.5, fill: 'var(--primary)', 'fill-opacity': .75 }));
      }
      c.g.appendChild(S('path', { d: L.linePath([[c.x(P.xd[0]), c.y(f(P.xd[0]))], [c.x(P.xd[1]), c.y(f(P.xd[1]))]]), stroke: 'var(--ink)', 'stroke-width': 2, fill: 'none', 'stroke-dasharray': '3 4' }));
      const hx = S('line', { y1: c.m.t, y2: c.H - c.m.b, stroke: 'var(--ink)', 'stroke-width': 1.5 });
      const dot = S('circle', { r: 7, fill: 'var(--paper)', stroke: 'var(--ink)', 'stroke-width': 2.5 });
      const card = S('g');
      const t1 = S('text', { x: 10, y: 19, class: 'lbl' }), t2 = S('text', { x: 10, y: 38, class: 'lbl-mono' });
      card.append(S('rect', { width: 205, height: 48, rx: 6, fill: 'var(--paper)', stroke: 'var(--line)' }), t1, t2);
      c.g.append(hx, dot, card);
      const start = Math.round(P.x0 * 0.6);
      const sl = L.slider(P.xlabel, P.xd[0], P.xd[1], start, 1, (v) => String(v), 'dk-line-x');
      const set = (xv) => {
        xv = L.clamp(Math.round(xv), P.xd[0], P.xd[1]);
        const x = c.x(xv), y = c.y(f(xv));
        hx.setAttribute('x1', x); hx.setAttribute('x2', x); dot.setAttribute('cx', x); dot.setAttribute('cy', y);
        card.setAttribute('transform', `translate(${L.clamp(x + 12, c.m.l, c.W - c.m.r - 205)},${c.m.t})`);
        t1.textContent = `${P.noun} ${xv}`; t2.textContent = `≈ ${L.fmtPct(f(xv), 1)} a year`;
        sl.input.value = xv; sl.out.textContent = String(xv);
      };
      set(start);
      sl.input.addEventListener('input', () => set(+sl.input.value));
      const off = dragX(c.svg, (x) => set(c.x.invert(x)));
      el.append(wrap(c.svg), sl.row, cap(`Dots are stylised around the estimated line. The dashed line is the source's slope: <span class="num">${P.b}</span> per unit of x.`));
      return off;
    };

    // =====================================================================
    // ladder: coefficients with 95% intervals, controls cumulative down the rows
    // =====================================================================
    CH.ladder = (el) => {
      const specs = D.specs, span = D.ladderSpan;
      const W = 680, rowH = 42, top = 36, H = top + specs.length * rowH + 44;
      const los = specs.map((s) => s.beta - 1.96 * s.se), his = specs.map((s) => s.beta + 1.96 * s.se);
      const lo = Math.min(0, ...los), hi = Math.max(0, ...his), pad = (hi - lo) * 0.1 || 0.001;
      const c = L.chart(W, H, { l: 200, r: 170, t: top, b: 40 }, [lo - pad, hi + pad], [0, 1]);
      const step = L.niceStep(hi - lo), dec = Math.max(0, -Math.floor(Math.log10(step)));
      const ticks = []; for (let v = Math.ceil(lo / step) * step; v <= hi + step / 2; v += step) ticks.push(+v.toFixed(8));
      L.axisX(c, ticks, (v) => v.toFixed(dec), 'coefficient');
      c.g.appendChild(S('line', { x1: c.x(0), x2: c.x(0), y1: top - 10, y2: H - c.m.b, stroke: 'var(--ink-3)' }));
      specs.forEach((s, i) => {
        const y = top + i * rowH, mid = y + rowH / 2, l = los[i], h = his[i];
        const dead = s.sig === undefined ? (l <= 0 && h >= 0) : !s.sig; // stars from the table win over rounded SEs
        c.g.appendChild(S('text', { x: c.m.l - 12, y: mid + 5, 'text-anchor': 'end', class: 'lbl', text: s.label, fill: dead ? 'var(--ink-3)' : 'var(--ink)' }));
        const bar = S('rect', { x: Math.min(c.x(0), c.x(s.beta)), y: y + 8, width: Math.abs(c.x(s.beta) - c.x(0)), height: rowH - 16, rx: 2, fill: dead ? 'var(--paper-3)' : 'var(--primary)' });
        if (dead) bar.setAttribute('stroke', 'var(--line)');
        c.g.appendChild(bar);
        c.g.appendChild(S('line', { x1: c.x(l), x2: c.x(h), y1: mid, y2: mid, stroke: 'var(--ink)', 'stroke-width': 2 }));
        for (const v of [l, h]) c.g.appendChild(S('line', { x1: c.x(v), x2: c.x(v), y1: mid - 6, y2: mid + 6, stroke: 'var(--ink)', 'stroke-width': 2 }));
        c.g.appendChild(S('text', { x: c.x(Math.max(h, 0)) + 10, y: mid + 5, class: 'lbl-mono', fill: dead ? 'var(--ink-3)' : 'var(--ink)', text: `${L.fmtNum(s.beta, dec)} · ${L.fmtNum(s.beta * span, 2)} over ${span}` }));
      });
      el.append(wrap(c.svg), cap('Coefficient with 95% intervals, controls cumulative down the rows. Right-hand numbers: the implied gap across the named span. Grey rows are not distinguishable from zero in the source table.'));
    };

    // =====================================================================
    // Wiring
    // =====================================================================
    const draw = (el, animate) => {
      if (el._cleanup) { try { el._cleanup(); } catch (e) { /* noop */ } el._cleanup = null; }
      el.replaceChildren();
      const fn = CH[el.dataset.chart];
      if (!fn) { el.appendChild(E('p', { class: 'caption', text: 'unknown chart: ' + el.dataset.chart })); console.error('deck-charts.js: unknown chart ' + el.dataset.chart); return; }
      try { el._cleanup = fn(el, { animate: !!animate }) || null; }
      catch (e) { console.error('deck-charts.js: ' + el.dataset.chart, e); el.appendChild(E('p', { class: 'caption', text: 'This chart failed to draw.' })); }
    };

    document.querySelectorAll('.stage[data-chart]').forEach((el) => {
      el.addEventListener('pointerdown', (e) => e.stopPropagation()); // keep reveal's swipe handler off the playables
      el.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) b.blur(); }); // so space and arrows keep driving the deck
      el.addEventListener('pointerup', () => { const a = document.activeElement; if (a && a.tagName === 'INPUT') a.blur(); }); // a dragged slider would otherwise eat the arrow keys
      draw(el, false);
    });
    const animateIn = (section) => {
      if (STATIC || !section) return;
      section.querySelectorAll('.stage[data-animate]').forEach((el) => {
        if (el.dataset.animate === 'once' && el._played) return; // the payoff plays once; stepping back shows it finished
        el._played = true; draw(el, true);
      });
    };
    // Prose numbers that read L.DATA: [ ]{.data key="specs.0.beta" d="3"} → the same object the charts draw
    document.querySelectorAll('.data[data-key]').forEach((sp) => {
      const v = L.get(sp.dataset.key);
      if (v === undefined) { console.error('deck-charts.js: no L.DATA entry for ' + sp.dataset.key); sp.textContent = '?'; return; }
      sp.textContent = typeof v === 'number' && sp.dataset.d !== undefined ? L.fmtNum(v, +sp.dataset.d) : String(v);
    });
    if (window.Reveal && typeof Reveal.on === 'function') {
      Reveal.on('slidechanged', (e) => animateIn(e.currentSlide));
      if (typeof Reveal.getCurrentSlide === 'function') animateIn(Reveal.getCurrentSlide());
    }
  }

  const start = () => {
    if (window.Reveal && typeof Reveal.isReady === 'function' && Reveal.isReady()) main();
    else if (window.Reveal && typeof Reveal.on === 'function') Reveal.on('ready', main);
    else main();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
