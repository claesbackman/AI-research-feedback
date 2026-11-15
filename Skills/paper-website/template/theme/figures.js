/* Draws the paper figures that have data (window.SITE_FIGURES, written by
   site_data.py). A figure without data keeps the paper's static image.
   Every drawn figure gets a table view, a CSV of the plotted numbers and a
   link to the static image from the paper. */
(function () {
  "use strict";
  const S = window.Site, C = window.Charts, D = window.SITE_FIGURES || {};
  if (!C || typeof d3 === "undefined") return;

  function render(fig, spec) {
    const chart = fig.querySelector(".fig-chart"), tableBox = fig.querySelector(".fig-table");
    const ctl = fig.querySelector(".fig-controls"), links = fig.querySelector(".fig-links");
    const staticImg = fig.querySelector(".fig-static img");
    const groups = spec.group ? Array.from(new Set(spec.rows.map((r) => String(r[spec.group])))) : [];
    let group = groups[0], current = null, showTable = false;
    const rows = () => (spec.group ? spec.rows.filter((r) => String(r[spec.group]) === group) : spec.rows);

    function draw() {
      try { current = C.draw(chart, spec, rows()); }
      catch (e) { console.error(fig.id, e); return false; }
      const old = fig.querySelector(".legend");
      if (old) old.remove();
      if (current.legend) ctl.insertAdjacentHTML("afterend", current.legend);
      if (showTable) tableBox.innerHTML = current.table();
      return true;
    }
    const keep = chart.innerHTML;
    if (!draw()) { chart.innerHTML = keep; return; }

    if (groups.length > 1) {
      const wrap = document.createElement("div");
      wrap.className = "ctl-group";
      if (spec.group_title) wrap.innerHTML = '<span class="ctl-label">' + S.esc(spec.group_title) + "</span>";
      groups.forEach((gname) => {
        const b = document.createElement("button");
        b.type = "button"; b.className = "pill"; b.textContent = gname;
        b.setAttribute("aria-pressed", gname === group ? "true" : "false");
        b.addEventListener("click", () => {
          group = gname;
          wrap.querySelectorAll(".pill").forEach((p) => p.setAttribute("aria-pressed", p === b ? "true" : "false"));
          draw();
        });
        wrap.appendChild(b);
      });
      ctl.appendChild(wrap);
    }

    const tbtn = document.createElement("button");
    tbtn.type = "button"; tbtn.textContent = "Table view";
    tbtn.addEventListener("click", () => {
      showTable = !showTable;
      if (showTable) tableBox.innerHTML = current.table();
      tableBox.hidden = !showTable; chart.hidden = showTable;
      tbtn.textContent = showTable ? "Chart view" : "Table view";
    });
    links.appendChild(tbtn);
    const dl = document.createElement("button");
    dl.type = "button"; dl.textContent = "Download the plotted numbers (CSV)";
    dl.addEventListener("click", () => S.download(fig.id.replace(/[^A-Za-z0-9]+/g, "_") + ".csv", S.toCSV(spec.rows, spec.columns || Object.keys(spec.rows[0] || {}))));
    links.appendChild(dl);
    if (staticImg) {
      const a = document.createElement("a");
      a.href = staticImg.getAttribute("src"); a.target = "_blank"; a.rel = "noopener"; a.textContent = "Paper version (static image)";
      links.appendChild(a);
    }
    document.addEventListener("themechange", draw);
  }

  document.querySelectorAll("figure.paper-figure").forEach((fig) => {
    const spec = D[fig.dataset.fig];
    if (spec && spec.rows && spec.rows.length) render(fig, spec);
  });
})();
