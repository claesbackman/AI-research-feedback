/* charts/stack-reveal.js — two cases, two components each. The second
 * component builds in on step 2: the payoff after a bet. The frame that
 * shows this stage gets two slides, one per step, and the handout shows
 * step 2. Numbers: data/numbers.js, reveal.*.
 */
module.exports = {
  steps: 2,
  draw({ slide, box, L, T, D, step }) {
    const R = D.reveal, cases = R.cases;
    const area = L.chartArea(box, { legend: true });
    const maxTotal = Math.max(...cases.map((c) => c.parts[0] + c.parts[1]));
    const c = L.chart(slide, area, { xd: [0, cases.length], yd: [0, maxTotal * 1.18], m: { l: 0.55, r: 0.2, t: 0.3, b: 0.4 } });
    const step5 = L.niceStep(maxTotal, 3);
    L.axisY(c, L.ticks(0, maxTotal * 1.1, step5), (v) => String(v), R.unit);
    const bw = Math.min(1.1, c.p.w / cases.length * 0.45);
    cases.forEach((k, i) => {
      const cx = c.x(i + 0.5), x = cx - bw / 2, y0 = c.y(0);
      const h1 = y0 - c.y(k.parts[0]);
      L.rect(slide, x, y0 - h1, bw, h1, { fill: k.color });
      L.label(slide, k.name, cx - 1, y0 + 0.08, 2, 0.26, { face: T.faces.display, size: 13, color: L.col(k.color), align: 'center' });
      if (step >= 2) {
        const h2 = y0 - c.y(k.parts[1]);
        L.hatchRect(slide, x, y0 - h1 - h2, bw, h2, k.color);
        L.dataLabel(slide, L.fmtNum(k.parts[0] + k.parts[1], 1), cx, y0 - h1 - h2 - 0.14, { color: k.color });
        L.label(slide, L.fmtNum(k.parts[0], 1), x + bw + 0.06, y0 - h1 / 2 - 0.1, 0.6, 0.2, { face: T.faces.mono, color: T.colors.ink2 });
        L.label(slide, L.fmtNum(k.parts[1], 1), x + bw + 0.06, y0 - h1 - h2 / 2 - 0.1, 0.6, 0.2, { face: T.faces.mono, color: T.colors.ink2 });
      } else {
        L.dataLabel(slide, L.fmtNum(k.parts[0], 1), cx, y0 - h1 - 0.14, { color: k.color });
      }
    });
    L.line(slide, c.p.x, c.y(0), c.p.x + c.p.w, c.y(0), { color: 'line', width: 0.75 });
    L.legend(slide, box, [{ label: R.partLabels[0], color: 'ink2' }, { label: R.partLabels[1], color: 'ink2', hatched: true }]);
    L.stagecap(slide, box, R.note);
  },
};
