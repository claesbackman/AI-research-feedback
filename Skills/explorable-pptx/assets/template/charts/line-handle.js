/* charts/line-handle.js — a fitted line with a handle the presenter walks
 * along. Three stops, one per step; the frame gets three slides and the
 * handout shows the last stop. Step 1 is where the picture is most
 * interesting. Numbers: data/numbers.js, line.* and linedots.
 */
module.exports = {
  steps: 3,
  draw({ slide, box, L, T, D, step, steps }) {
    const P = D.line, f = (x) => P.a + P.b * (x - P.x0);
    const area = L.chartArea(box);
    const c = L.chart(slide, area, { xd: [P.xmin, P.xmax], yd: [P.ymin, P.ymax] });
    L.axisY(c, L.ticks(P.ymin, P.ymax, L.niceStep(P.ymax - P.ymin, 4)), (v) => String(v), P.ylabel);
    L.axisX(c, L.ticks(P.xmin, P.xmax, L.niceStep(P.xmax - P.xmin, 5)), (v) => String(v), P.xlabel);
    for (const d of D.linedots) L.dot(slide, c.x(d.x), c.y(d.y), 0.03, { fill: 'line' });
    L.path(c, [[P.xmin, f(P.xmin)], [P.xmax, f(P.xmax)]], { color: 'primary', width: 2 });
    const hx = P.stops[Math.min(step, steps) - 1], hy = f(hx);
    L.line(slide, c.x(hx), c.y(P.ymin), c.x(hx), c.y(hy), { color: 'line', width: 0.75, dash: 'dash' });
    L.handle(slide, c.x(hx), c.y(hy));
    L.card(slide, [{ text: `at ${L.fmtNum(hx, 0)}: `, options: {} }, { text: L.fmtNum(hy, 1), options: { bold: true } }, { text: ' units', options: {} }],
      c.x(hx), c.y(hy), { w: 1.3, h: 0.3, keepIn: c.p });
    L.stagecap(slide, box, `Dots are stylised around the estimated line. The slope (${L.fmtNum(P.b, 2)} per unit) is the source's estimate; the level is illustrative.`);
  },
};
