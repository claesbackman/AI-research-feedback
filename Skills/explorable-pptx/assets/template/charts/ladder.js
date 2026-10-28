/* charts/ladder.js — a coefficient as controls are added, one row per
 * specification, 95 percent intervals. A row the source's table does not
 * mark as significant (sig = 0 in data/ladder.csv) is drawn grey.
 * Significance comes from the table's stars, never from rounded standard
 * errors. Numbers: data/numbers.js, ladder (rows) and ladderMeta.
 */
module.exports = {
  steps: 1,
  draw({ slide, box, L, T, D }) {
    const rows = D.ladder, M = D.ladderMeta;
    const area = L.chartArea(box);
    const los = rows.map((r) => r.beta - 1.96 * r.se), his = rows.map((r) => r.beta + 1.96 * r.se);
    const lo = Math.min(0, ...los), hi = Math.max(0, ...his), pad = (hi - lo) * 0.12 || 0.001;
    const c = L.chart(slide, area, { xd: [lo - pad, hi + pad], yd: [rows.length - 0.5, -0.5], m: { l: 1.5, r: 0.9, t: 0.15, b: 0.42 } });
    const step = L.niceStep(hi - lo, 4), dec = Math.max(0, -Math.floor(Math.log10(step)));
    L.axisX(c, L.ticks(lo, hi, step), (v) => L.fmtNum(v, dec), M.xlabel);
    L.line(slide, c.x(0), c.p.y, c.x(0), c.p.y + c.p.h, { color: 'line', width: 0.75 });
    rows.forEach((r, i) => {
      const y = c.y(i), dead = r.sig !== undefined ? !r.sig : (los[i] <= 0 && his[i] >= 0);
      const col = dead ? 'ink3' : 'primary';
      L.label(slide, r.spec, c.p.x - 1.5, y - 0.1, 1.42, 0.2, { align: 'right', color: dead ? T.colors.ink3 : T.colors.ink, size: 10 });
      L.line(slide, c.x(los[i]), y, c.x(his[i]), y, { color: col, width: 1.5 });
      L.line(slide, c.x(los[i]), y - 0.06, c.x(los[i]), y + 0.06, { color: col, width: 1.5 });
      L.line(slide, c.x(his[i]), y - 0.06, c.x(his[i]), y + 0.06, { color: col, width: 1.5 });
      L.dot(slide, c.x(r.beta), y, 0.055, { fill: col });
      L.label(slide, L.fmtNum(r.beta, dec), c.x(Math.max(his[i], 0)) + 0.1, y - 0.1, 0.8, 0.2, { face: T.faces.mono, color: dead ? T.colors.ink3 : T.colors.ink });
    });
    L.stagecap(slide, box, 'Point estimate with 95 percent interval; controls are cumulative down the rows. Grey: not distinguishable from zero in the source’s table.');
  },
};
