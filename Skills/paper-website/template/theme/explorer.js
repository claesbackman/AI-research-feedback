/* Results explorer: one aggregate table in long format (window.SITE_EXPLORER,
   written by site_data.py) with several dimensions and one value column.
   The reader picks the dimension on the rows, an optional dimension for
   colour, and one level (or the average) of every other dimension. The view
   is kept in the URL so it can be shared. Adapt freely for the paper. */
(function () {
  "use strict";
  const S = window.Site, C = window.Charts, X = window.SITE_EXPLORER;
  const root = document.getElementById("explorer");
  if (!root || !X || typeof d3 === "undefined") return;
  const dims = X.dimensions, lab = (k) => (X.labels && X.labels[k]) || k;
  const levels = {};
  dims.forEach((k) => { levels[k] = Array.from(new Set(X.rows.map((r) => String(r[k])))); });
  const ALL = "__all__";
  const st = { rows: X.rows_dim || dims[0], color: X.color_dim || "", sort: "value", filt: {} };
  dims.forEach((k) => { st.filt[k] = (X.defaults && X.defaults[k] != null ? String(X.defaults[k]) : ALL); });
  // state from the URL
  const p = new URLSearchParams(location.search);
  if (dims.includes(p.get("rows"))) st.rows = p.get("rows");
  if (p.has("color") && (p.get("color") === "" || dims.includes(p.get("color")))) st.color = p.get("color");
  if (p.get("sort")) st.sort = p.get("sort");
  dims.forEach((k) => { if (p.has(k) && (p.get(k) === ALL || levels[k].includes(p.get(k)))) st.filt[k] = p.get(k); });

  root.innerHTML = '<div class="panel"><div class="ctl" id="ex-ctl"></div></div>' +
    '<div class="panel"><div class="fig-head"><span class="fig-title" id="ex-title"></span></div><div id="ex-legend"></div>' +
    '<div class="fig-chart" id="ex-chart"></div><div class="fig-table" id="ex-table" hidden></div>' +
    '<p class="small muted" id="ex-note"></p><div class="fig-links"><button type="button" id="ex-tbtn">Table view</button>' +
    '<button type="button" id="ex-dl">Download this view (CSV)</button><button type="button" id="ex-link">Copy a link to this view</button><span class="copied small muted" aria-live="polite"></span></div></div>';
  const ctl = root.querySelector("#ex-ctl");

  function select(label, options, value, onChange) {
    const l = document.createElement("label");
    l.innerHTML = '<span class="ctl-label">' + S.esc(label) + "</span>";
    const s = document.createElement("select");
    options.forEach(([v, t]) => { const o = document.createElement("option"); o.value = v; o.textContent = t; if (v === value) o.selected = true; s.appendChild(o); });
    s.addEventListener("change", () => { onChange(s.value); controls(); draw(); });
    l.appendChild(s);
    ctl.appendChild(l);
  }
  function controls() {
    ctl.innerHTML = "";
    if (st.color === st.rows) st.color = "";
    select("Rows", dims.map((k) => [k, lab(k)]), st.rows, (v) => { st.rows = v; });
    select("Colour by", [["", "Nothing"]].concat(dims.filter((k) => k !== st.rows).map((k) => [k, lab(k)])), st.color, (v) => { st.color = v; });
    dims.filter((k) => k !== st.rows && k !== st.color).forEach((k) => {
      select(lab(k), [[ALL, "All (average)"]].concat(levels[k].map((v) => [v, v])), st.filt[k], (v) => { st.filt[k] = v; });
    });
    select("Order", [["value", "By value"], ["source", "As in the source"]], st.sort, (v) => { st.sort = v; });
  }

  let view = [], showTable = false, chart = null;
  function draw() {
    const free = dims.filter((k) => k !== st.rows && k !== st.color);
    const rows = X.rows.filter((r) => free.every((k) => st.filt[k] === ALL || String(r[k]) === st.filt[k]));
    const cell = d3.rollup(rows, (v) => ({ value: d3.mean(v, (r) => +r[X.value]), n: v.length,
      lo: X.lo && v.length === 1 ? +v[0][X.lo] : null, hi: X.hi && v.length === 1 ? +v[0][X.hi] : null }),
      (r) => String(r[st.rows]), (r) => (st.color ? String(r[st.color]) : ""));
    view = [];
    cell.forEach((m, a) => m.forEach((c, b) => { const o = {}; o[lab(st.rows)] = a; if (st.color) o[lab(st.color)] = b; o.value = c.value; o.lo = c.lo; o.hi = c.hi; o.cells = c.n; view.push(o); }));
    const spec = { type: "coef", label: lab(st.rows), value: "value", lo: "lo", hi: "hi", series: st.color ? lab(st.color) : null,
      x_title: X.value_label || X.value, digits: X.digits, zero: !!X.zero, sort: st.sort === "value" ? "descending" : null };
    chart = C.draw(root.querySelector("#ex-chart"), spec, view);
    root.querySelector("#ex-legend").innerHTML = chart.legend || "";
    if (showTable) root.querySelector("#ex-table").innerHTML = chart.table();
    const pinned = free.filter((k) => st.filt[k] !== ALL).map((k) => lab(k) + ": " + st.filt[k]);
    const avg = free.filter((k) => st.filt[k] === ALL).map(lab);
    root.querySelector("#ex-title").textContent = (X.value_label || X.value) + " by " + lab(st.rows).toLowerCase() + (pinned.length ? " (" + pinned.join(", ") + ")" : "");
    root.querySelector("#ex-note").textContent = avg.length ? "Each point is the unweighted mean of the cells over " + avg.join(" and ").toLowerCase() + ". Intervals are shown only where a point is a single cell." : "";
    const q = new URLSearchParams({ rows: st.rows, color: st.color, sort: st.sort });
    free.forEach((k) => q.set(k, st.filt[k]));
    try { history.replaceState(null, "", "?" + q.toString()); } catch (e) { /* file:// in some browsers */ }
  }
  root.querySelector("#ex-tbtn").addEventListener("click", (e) => {
    showTable = !showTable;
    const t = root.querySelector("#ex-table");
    if (showTable) t.innerHTML = chart.table();
    t.hidden = !showTable; root.querySelector("#ex-chart").hidden = showTable;
    e.target.textContent = showTable ? "Chart view" : "Table view";
  });
  root.querySelector("#ex-dl").addEventListener("click", () => S.download("explorer_view.csv", S.toCSV(view, Object.keys(view[0] || {}))));
  root.querySelector("#ex-link").addEventListener("click", (e) => {
    if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(() => { const s = e.target.parentElement.querySelector(".copied"); s.textContent = "Link copied."; setTimeout(() => { s.textContent = ""; }, 1800); });
  });
  document.addEventListener("themechange", draw);
  controls();
  draw();
})();
