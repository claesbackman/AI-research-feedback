/* Generic chart components (D3 v7) for figures drawn from aggregate tables.
   Charts.draw(container, spec, rows) draws one chart and returns
   { table(): html, legend: html }. Chart types:
     coef     one row per category: point estimate with an interval
     bar      one row per category: bar from zero
     line     y against a numeric x, one line per series, optional band
     event    y against a numeric x as points with intervals (event study)
     scatter  x against y, optional point labels and fitted line
   The spec names the columns: label, value, lo, hi, x, y, series. */
window.Charts = (function () {
  "use strict";
  const S = window.Site;
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const color = (k) => css("--series-" + ((k % 5) + 1));
  const num = (v) => (v === "" || v == null || isNaN(+v) ? null : +v);

  function svgIn(el, width, height, m) {
    el.innerHTML = "";
    const svg = d3.select(el).append("svg").attr("class", "chart").attr("viewBox", `0 0 ${width} ${height}`).attr("width", "100%").attr("role", "img");
    const g = svg.append("g").attr("transform", `translate(${m.left},${m.top})`);
    return { svg, g, w: width - m.left - m.right, h: height - m.top - m.bottom };
  }
  const tableHTML = (head, rows) => '<div class="table-wrap"><table class="data-table"><thead><tr>' + head.map((h) => "<th>" + S.esc(h) + "</th>").join("") +
    "</tr></thead><tbody>" + rows.map((r) => "<tr>" + r.map((c, i) => (i === 0 ? '<th scope="row">' + S.esc(c) + "</th>" : "<td>" + S.esc(c) + "</td>")).join("") + "</tr>").join("") + "</tbody></table></div>";
  const legendHTML = (names, kind) => (names.length < 2 ? "" : '<div class="legend">' + names.map((n, i) =>
    '<span class="key"><span class="swatch ' + (kind || "dot") + '" style="background:' + color(i) + '"></span>' + S.esc(n) + "</span>").join("") + "</div>");
  const seriesOf = (spec, rows) => (spec.series ? Array.from(new Set(rows.map((r) => String(r[spec.series])))) : [""]);
  const title = (spec, k, fallback) => spec[k + "_title"] || fallback || "";
  const d = (spec) => (spec.digits == null ? 2 : spec.digits);

  function axisTitles(g, w, h, spec, xt, yt, left) {
    if (xt) g.append("text").attr("class", "axis-title").attr("x", w / 2).attr("y", h + 36).attr("text-anchor", "middle").text(xt);
    if (yt) g.append("text").attr("class", "axis-title").attr("transform", "rotate(-90)").attr("x", -h / 2).attr("y", -left + 12).attr("text-anchor", "middle").text(yt);
  }
  function tipRows(titleText, pairs) {
    return '<div class="t-title">' + S.esc(titleText) + "</div>" + pairs.filter((p) => p[1] != null).map((p) =>
      '<div class="t-row"><span class="t-lab">' + S.esc(p[0]) + '</span><span class="t-val">' + S.esc(p[1]) + "</span></div>").join("");
  }

  /* coef and bar: categories down the side, values along the bottom */
  function rowsChart(el, spec, rows, bars) {
    const vcol = spec.value, lab = spec.label, ser = seriesOf(spec, rows);
    let data = rows.map((r) => ({ label: String(r[lab]), s: spec.series ? String(r[spec.series]) : "", v: num(r[vcol]), lo: num(r[spec.lo]), hi: num(r[spec.hi]), r })).filter((x) => x.v != null);
    let cats = Array.from(new Set(data.map((x) => x.label)));
    if (spec.sort) {
      const key = (c) => d3.mean(data.filter((x) => x.label === c), (x) => x.v);
      cats.sort((a, b) => (spec.sort === "ascending" ? key(a) - key(b) : key(b) - key(a)));
    }
    const left = Math.min(240, 16 + 6.4 * d3.max(cats, (c) => c.length));
    if (!data.length) throw new Error("no numeric values to draw");
    const rowH = Math.max(22, 12 + 9 * ser.length);
    const m = { top: 10, right: 24, bottom: 46, left };
    const width = 680, height = m.top + m.bottom + rowH * cats.length;
    const { g, w, h } = svgIn(el, width, height, m);
    const ext = d3.extent(data.flatMap((x) => [x.v, x.lo, x.hi].filter((v) => v != null)).concat(bars || spec.zero !== false ? [0] : []));
    const x = d3.scaleLinear().domain(ext).nice().range([0, w]);
    const y = d3.scaleBand().domain(cats).range([0, h]).padding(0.25);
    const off = (s) => (ser.length > 1 ? (ser.indexOf(s) + 0.5) * (y.bandwidth() / ser.length) : y.bandwidth() / 2);
    g.append("g").attr("class", "grid").call(d3.axisBottom(x).ticks(6).tickSize(h).tickFormat(""));
    g.append("g").attr("class", "axis").attr("transform", `translate(0,${h})`).call(d3.axisBottom(x).ticks(6));
    g.append("g").attr("class", "axis").call(d3.axisLeft(y).tickSize(0)).select(".domain").remove();
    if (x.domain()[0] < 0 && x.domain()[1] > 0 || bars) g.append("line").attr("class", "zero").attr("x1", x(0)).attr("x2", x(0)).attr("y1", 0).attr("y2", h);
    const hover = (sel) => sel.on("pointermove", (ev, p) => S.showTip(tipRows(p.label + (p.s ? " · " + p.s : ""), [[title(spec, "x", vcol), S.fmt.n(p.v, d(spec))],
      ["Interval", p.lo != null && p.hi != null ? S.fmt.n(p.lo, d(spec)) + " to " + S.fmt.n(p.hi, d(spec)) : null]]), ev)).on("pointerleave", S.hideTip);
    if (bars) {
      const bh = y.bandwidth() / ser.length;
      hover(g.selectAll("rect.bar").data(data).enter().append("rect").attr("class", "bar").attr("x", (p) => Math.min(x(0), x(p.v))).attr("width", (p) => Math.abs(x(p.v) - x(0)))
        .attr("y", (p) => y(p.label) + ser.indexOf(p.s) * bh).attr("height", Math.max(2, bh - 1)).attr("rx", 1.5).attr("fill", (p) => color(ser.indexOf(p.s))).attr("opacity", 0.88));
    }
    g.selectAll("line.ci").data(data.filter((p) => p.lo != null && p.hi != null)).enter().append("line").attr("class", "ci")
      .attr("x1", (p) => x(p.lo)).attr("x2", (p) => x(p.hi)).attr("y1", (p) => y(p.label) + off(p.s)).attr("y2", (p) => y(p.label) + off(p.s))
      .attr("stroke", (p) => (bars ? css("--chart-ink-2") : color(ser.indexOf(p.s))));
    if (!bars) hover(g.selectAll("circle").data(data).enter().append("circle").attr("class", "dot").attr("cx", (p) => x(p.v)).attr("cy", (p) => y(p.label) + off(p.s)).attr("r", 4.5).attr("fill", (p) => color(ser.indexOf(p.s))));
    axisTitles(g, w, h, spec, title(spec, "x", vcol), "", left);
    const hasCI = data.some((p) => p.lo != null);
    return {
      legend: legendHTML(ser, bars ? "bar" : "dot"),
      table: () => tableHTML([lab].concat(spec.series ? [spec.series] : [], [title(spec, "x", vcol)], hasCI ? ["Lower", "Upper"] : []),
        cats.flatMap((c) => data.filter((p) => p.label === c)).map((p) => [p.label].concat(spec.series ? [p.s] : [], [S.fmt.n(p.v, d(spec))], hasCI ? [S.fmt.n(p.lo, d(spec)), S.fmt.n(p.hi, d(spec))] : []))),
    };
  }

  /* line and event: a numeric x */
  function xyChart(el, spec, rows, points) {
    const ser = seriesOf(spec, rows);
    const data = rows.map((r) => ({ x: num(r[spec.x]), y: num(r[spec.y]), lo: num(r[spec.lo]), hi: num(r[spec.hi]), s: spec.series ? String(r[spec.series]) : "" })).filter((p) => p.x != null && p.y != null).sort((a, b) => a.x - b.x);
    if (!data.length) throw new Error("no numeric x and y values to draw");
    const m = { top: 14, right: 20, bottom: 46, left: 56 };
    const { g, w, h } = svgIn(el, 680, 360, m);
    const x = d3.scaleLinear().domain(d3.extent(data, (p) => p.x)).range([0, w]);
    if (points) x.domain([x.domain()[0] - 0.5, x.domain()[1] + 0.5]);
    const y = d3.scaleLinear().domain(d3.extent(data.flatMap((p) => [p.y, p.lo, p.hi].filter((v) => v != null)).concat(spec.zero ? [0] : []))).nice().range([h, 0]);
    const intx = data.every((p) => Number.isInteger(p.x));
    g.append("g").attr("class", "grid").call(d3.axisLeft(y).ticks(6).tickSize(-w).tickFormat(""));
    g.append("g").attr("class", "axis").attr("transform", `translate(0,${h})`).call(d3.axisBottom(x).ticks(Math.min(10, intx ? x.domain()[1] - x.domain()[0] : 10)).tickFormat(intx ? d3.format("d") : null));
    g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(6));
    if (y.domain()[0] < 0 && y.domain()[1] > 0) g.append("line").attr("class", "zero").attr("x1", 0).attr("x2", w).attr("y1", y(0)).attr("y2", y(0));
    if (spec.ref_x != null) g.append("line").attr("class", "fit").attr("x1", x(spec.ref_x)).attr("x2", x(spec.ref_x)).attr("y1", 0).attr("y2", h);
    const jitter = (s) => (points && ser.length > 1 ? (ser.indexOf(s) - (ser.length - 1) / 2) * 7 : 0);
    ser.forEach((s, k) => {
      const pts = data.filter((p) => p.s === s), c = color(k);
      if (!points && pts.some((p) => p.lo != null)) g.append("path").datum(pts.filter((p) => p.lo != null)).attr("class", "band").attr("fill", c).attr("d", d3.area().x((p) => x(p.x)).y0((p) => y(p.lo)).y1((p) => y(p.hi)));
      g.append("path").datum(pts).attr("fill", "none").attr("stroke", c).attr("stroke-width", points ? 1 : 2).attr("opacity", points ? 0.5 : 1).attr("d", d3.line().x((p) => x(p.x) + jitter(s)).y((p) => y(p.y)));
      if (points) g.selectAll(null).data(pts.filter((p) => p.lo != null)).enter().append("line").attr("class", "ci").attr("stroke", c).attr("x1", (p) => x(p.x) + jitter(s)).attr("x2", (p) => x(p.x) + jitter(s)).attr("y1", (p) => y(p.lo)).attr("y2", (p) => y(p.hi));
      if (points || pts.length <= 40) g.selectAll(null).data(pts).enter().append("circle").attr("class", "dot").attr("cx", (p) => x(p.x) + jitter(s)).attr("cy", (p) => y(p.y)).attr("r", points ? 4.5 : 3.2).attr("fill", c)
        .on("pointermove", (ev, p) => S.showTip(tipRows((s ? s + " · " : "") + title(spec, "x", spec.x) + " " + p.x, [[title(spec, "y", spec.y), S.fmt.n(p.y, d(spec))],
          ["Interval", p.lo != null && p.hi != null ? S.fmt.n(p.lo, d(spec)) + " to " + S.fmt.n(p.hi, d(spec)) : null]]), ev)).on("pointerleave", S.hideTip);
    });
    axisTitles(g, w, h, spec, title(spec, "x", spec.x), title(spec, "y", spec.y), m.left);
    const hasCI = data.some((p) => p.lo != null);
    return {
      legend: legendHTML(ser, points ? "dot" : ""),
      table: () => tableHTML([title(spec, "x", spec.x)].concat(spec.series ? [spec.series] : [], [title(spec, "y", spec.y)], hasCI ? ["Lower", "Upper"] : []),
        data.map((p) => [String(p.x)].concat(spec.series ? [p.s] : [], [S.fmt.n(p.y, d(spec))], hasCI ? [S.fmt.n(p.lo, d(spec)), S.fmt.n(p.hi, d(spec))] : []))),
    };
  }

  function scatter(el, spec, rows) {
    const ser = seriesOf(spec, rows);
    const data = rows.map((r) => ({ x: num(r[spec.x]), y: num(r[spec.y]), label: spec.label ? String(r[spec.label]) : "", s: spec.series ? String(r[spec.series]) : "" })).filter((p) => p.x != null && p.y != null);
    if (!data.length) throw new Error("no numeric x and y values to draw");
    const m = { top: 14, right: 24, bottom: 46, left: 56 };
    const { g, w, h } = svgIn(el, 680, 400, m);
    const pad = (e) => { const s = (e[1] - e[0]) * 0.06 || 1; return [e[0] - s, e[1] + s]; };
    const x = d3.scaleLinear().domain(pad(d3.extent(data, (p) => p.x))).range([0, w]);
    const y = d3.scaleLinear().domain(pad(d3.extent(data, (p) => p.y))).range([h, 0]);
    g.append("g").attr("class", "grid").call(d3.axisLeft(y).ticks(6).tickSize(-w).tickFormat(""));
    g.append("g").attr("class", "axis").attr("transform", `translate(0,${h})`).call(d3.axisBottom(x).ticks(7));
    g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(6));
    if (spec.fit && data.length > 2) {
      const mx = d3.mean(data, (p) => p.x), my = d3.mean(data, (p) => p.y);
      const b = d3.sum(data, (p) => (p.x - mx) * (p.y - my)) / d3.sum(data, (p) => (p.x - mx) ** 2), a = my - b * mx;
      const [x0, x1] = d3.extent(data, (p) => p.x);
      g.append("line").attr("class", "fit").attr("x1", x(x0)).attr("x2", x(x1)).attr("y1", y(a + b * x0)).attr("y2", y(a + b * x1));
    }
    g.selectAll("circle").data(data).enter().append("circle").attr("class", "dot").attr("cx", (p) => x(p.x)).attr("cy", (p) => y(p.y)).attr("r", 4.5).attr("fill", (p) => color(ser.indexOf(p.s)))
      .on("pointermove", (ev, p) => S.showTip(tipRows(p.label || p.s || "", [[title(spec, "x", spec.x), S.fmt.n(p.x, d(spec))], [title(spec, "y", spec.y), S.fmt.n(p.y, d(spec))]]), ev)).on("pointerleave", S.hideTip);
    if (spec.label && data.length <= 60) g.selectAll("text.label").data(data).enter().append("text").attr("class", "label").attr("x", (p) => x(p.x) + 7).attr("y", (p) => y(p.y) + 3.5).text((p) => p.label);
    axisTitles(g, w, h, spec, title(spec, "x", spec.x), title(spec, "y", spec.y), m.left);
    return {
      legend: legendHTML(ser, "dot"),
      table: () => tableHTML((spec.label ? [spec.label] : []).concat(spec.series ? [spec.series] : [], [title(spec, "x", spec.x), title(spec, "y", spec.y)]),
        data.map((p) => (spec.label ? [p.label] : []).concat(spec.series ? [p.s] : [], [S.fmt.n(p.x, d(spec)), S.fmt.n(p.y, d(spec))]))),
    };
  }

  function draw(el, spec, rows) {
    rows = rows || spec.rows;
    if (spec.type === "coef") return rowsChart(el, spec, rows, false);
    if (spec.type === "bar") return rowsChart(el, spec, rows, true);
    if (spec.type === "line") return xyChart(el, spec, rows, false);
    if (spec.type === "event") return xyChart(el, spec, rows, true);
    if (spec.type === "scatter") return scatter(el, spec, rows);
    throw new Error("unknown chart type " + spec.type);
  }
  return { draw, tableHTML, legendHTML };
})();
