/* Shared behaviour: navigation drawer, inline notes, math rendering, theme
   toggle, search, hover previews, table downloads, copy buttons, and the
   small utilities the chart scripts use. No dependencies. */
(function () {
  "use strict";
  const F = (window.SITE && window.SITE.features) || {};
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // ---- navigation drawer (small screens) ----
  const toggle = document.getElementById("nav-toggle");
  const sidebar = document.getElementById("sidebar");
  if (toggle && sidebar) {
    toggle.addEventListener("click", () => {
      const open = sidebar.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", (e) => {
      if (sidebar.classList.contains("open") && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }
  const active = document.querySelector(".nav-list li.active");
  if (active && sidebar) {
    const r = active.getBoundingClientRect(), s = sidebar.getBoundingClientRect();
    if (r.bottom > s.bottom || r.top < s.top) active.scrollIntoView({ block: "center" });
  }

  // ---- theme toggle: follows the system until the reader chooses ----
  const tt = document.getElementById("theme-toggle");
  if (tt) {
    tt.addEventListener("click", () => {
      const root = document.documentElement;
      const cur = root.getAttribute("data-theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      const next = cur === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("site-theme", next); } catch (e) { /* private window */ }
      document.dispatchEvent(new CustomEvent("themechange"));
    });
  }

  // ---- inline notes (footnotes) ----
  document.querySelectorAll(".fn-ref").forEach((btn) => {
    btn.addEventListener("click", () => {
      const body = document.getElementById(btn.getAttribute("aria-controls"));
      const open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", open ? "false" : "true");
      if (body) body.hidden = open;
    });
  });
  function openTarget() {
    if (!location.hash) return;
    let el = null;
    try { el = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (e) { return; }
    if (el && el.classList.contains("fn-body")) {
      el.hidden = false;
      const b = document.querySelector('[aria-controls="' + el.id + '"]');
      if (b) b.setAttribute("aria-expanded", "true");
    }
  }
  openTarget();

  // ---- math ----
  function renderMath() {
    if (typeof renderMathInElement !== "function") return;
    renderMathInElement(document.body, {
      delimiters: [
        { left: "\\[", right: "\\]", display: true },
        { left: "\\(", right: "\\)", display: false },
      ],
      throwOnError: false,
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", renderMath);
  else renderMath();

  // ---- tooltip ----
  let tipEl = null;
  function tip() {
    if (!tipEl) {
      tipEl = document.createElement("div");
      tipEl.className = "tip";
      tipEl.style.display = "none";
      document.body.appendChild(tipEl);
    }
    return tipEl;
  }
  function showTip(html, ev, cls) {
    const t = tip();
    t.className = "tip" + (cls ? " " + cls : "");
    t.innerHTML = html;
    t.style.display = "block";
    moveTip(ev);
  }
  function moveTip(ev) {
    const t = tip(), pad = 14;
    let x = ev.clientX + pad, y = ev.clientY + pad;
    const r = t.getBoundingClientRect();
    if (x + r.width > window.innerWidth - 8) x = Math.max(8, ev.clientX - r.width - pad);
    if (y + r.height > window.innerHeight - 8) y = Math.max(8, ev.clientY - r.height - pad);
    t.style.left = x + "px";
    t.style.top = y + "px";
  }
  function hideTip() { if (tipEl) tipEl.style.display = "none"; }

  // ---- hover previews: citations, cross references, footnotes ----
  if (F.previews && window.matchMedia("(hover: hover)").matches) {
    const M = window.SITE_META || { refs: {}, xrefs: {} };
    const previewFor = (a) => {
      if (a.classList.contains("fn-ref")) {
        const b = document.getElementById(a.getAttribute("aria-controls"));
        return b && a.getAttribute("aria-expanded") !== "true" ? b.innerHTML : null;
      }
      if (a.classList.contains("cite")) {
        const keys = (a.dataset.cites || "").split(/\s+/).filter((k) => M.refs[k]);
        return keys.length ? keys.map((k) => "<div>" + M.refs[k] + "</div>").join('<div style="height:.4rem"></div>') : null;
      }
      const id = decodeURIComponent((a.getAttribute("href") || "").split("#")[1] || "");
      const x = M.xrefs[id];
      if (!x) return null;
      return '<span class="t-kind">' + x.k + " " + esc(x.n) + "</span>" + esc(x.t) + (x.i ? '<img src="' + x.i + '" alt="">' : "");
    };
    document.querySelectorAll("a.cite, a.xref, .fn-ref").forEach((a) => {
      a.addEventListener("pointerenter", (ev) => {
        const h = previewFor(a);
        if (h) { showTip(h, ev, "preview"); if (window.renderMathInElement) renderMathInElement(tip(), { delimiters: [{ left: "\\(", right: "\\)", display: false }], throwOnError: false }); }
      });
      a.addEventListener("pointerleave", hideTip);
      a.addEventListener("click", hideTip);
    });
  }

  // ---- outline: mark the subsection being read ----
  const outline = Array.from(document.querySelectorAll(".outline a"));
  if (outline.length) {
    const heads = outline.map((a) => document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1)))).filter(Boolean);
    const spy = () => {
      let k = 0;
      heads.forEach((h, i) => { if (h.getBoundingClientRect().top < 120) k = i; });
      outline.forEach((a, i) => a.classList.toggle("here", i === k));
    };
    document.addEventListener("scroll", spy, { passive: true });
    spy();
  }

  // ---- copy buttons: <button data-copy="element-id"> ----
  document.querySelectorAll("[data-copy]").forEach((b) => {
    b.addEventListener("click", () => {
      const el = document.getElementById(b.dataset.copy);
      if (!el) return;
      const done = () => {
        const s = b.parentElement.querySelector(".copied");
        if (s) { s.textContent = "Copied."; setTimeout(() => { s.textContent = ""; }, 1800); }
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(el.textContent).then(done, () => {});
      else {
        const r = document.createRange(); r.selectNodeContents(el);
        const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
        try { document.execCommand("copy"); done(); } catch (e) { /* leave the text selected */ }
      }
    });
  });

  // ---- downloads ----
  function download(filename, text, type) {
    const blob = new Blob([text], { type: type || "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();
  }
  const q = (v) => (v == null ? "" : /[",\n]/.test(String(v)) ? '"' + String(v).replace(/"/g, '""') + '"' : String(v));
  function toCSV(rows, cols) {
    return [cols.map(q).join(",")].concat(rows.map((r) => cols.map((c) => q(r[c])).join(","))).join("\n");
  }
  // every paper table can be saved as CSV, read from the table itself
  if (F.table_csv) {
    document.querySelectorAll(".paper-table").forEach((box) => {
      const table = box.querySelector("table"), links = box.querySelector(".tab-links");
      if (!table || !links) return;
      const b = document.createElement("button");
      b.type = "button"; b.textContent = "Download this table (CSV)";
      b.addEventListener("click", () => {
        const lines = Array.from(table.rows).map((tr) => {
          const cells = [];
          Array.from(tr.cells).forEach((c) => {
            cells.push(q(c.textContent.trim().replace(/−/g, "-")));
            for (let k = 1; k < (c.colSpan || 1); k++) cells.push("");
          });
          return cells.join(",");
        });
        const label = (box.querySelector(".tab-label") || {}).textContent || "table";
        download(label.toLowerCase().replace(/[^a-z0-9]+/g, "_") + ".csv", lines.join("\n"));
      });
      links.appendChild(b);
    });
  }

  // ---- search: the index (data/search.js) loads on first use ----
  const input = document.getElementById("search-input"), box = document.getElementById("search-results");
  if (input && box) {
    let index = null, loading = false, sel = -1;
    const load = () => {
      if (index || loading) return;
      loading = true;
      const s = document.createElement("script");
      s.src = "data/search.js";
      s.onload = () => { index = (window.SITE_SEARCH || []).map((e) => Object.assign({ lt: e.t.toLowerCase(), lh: e.h.toLowerCase() }, e)); run(); };
      document.head.appendChild(s);
    };
    const mark = (text, terms) => {
      let out = esc(text);
      terms.forEach((t) => { out = out.replace(new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>"); });
      return out;
    };
    function run() {
      const terms = input.value.toLowerCase().split(/\s+/).filter((t) => t.length > 1);
      sel = -1;
      if (!terms.length || !index) { box.hidden = true; return; }
      const hits = [];
      index.forEach((e) => {
        let score = 0;
        for (const t of terms) {
          const inH = e.lh.includes(t), n = e.lt.split(t).length - 1;
          if (!inH && !n) return;
          score += (inH ? 8 : 0) + Math.min(n, 6);
        }
        hits.push({ e, score });
      });
      hits.sort((a, b) => b.score - a.score);
      box.innerHTML = hits.length ? hits.slice(0, 12).map(({ e }) => {
        const i = Math.max(0, e.lt.indexOf(terms[0]) - 60);
        const snip = (i > 0 ? "…" : "") + e.t.slice(i, i + 190) + (i + 190 < e.t.length ? "…" : "");
        return '<a href="' + e.p + ".html" + (e.a ? "#" + encodeURIComponent(e.a) : "") + '"><div class="sr-head">' + mark(e.h, terms) +
          (e.pt && e.pt !== e.h ? '<span class="sr-page">' + esc(e.pt) + "</span>" : "") + '</div><div class="sr-text">' + mark(snip, terms) + "</div></a>";
      }).join("") : '<div class="sr-empty">No match in the paper.</div>';
      box.hidden = false;
    }
    input.addEventListener("focus", load);
    input.addEventListener("input", () => { load(); run(); });
    input.addEventListener("keydown", (e) => {
      const items = Array.from(box.querySelectorAll("a"));
      if (e.key === "Escape") { box.hidden = true; input.blur(); }
      else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!items.length) return;
        sel = (sel + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
        items.forEach((a, i) => a.classList.toggle("sel", i === sel));
        items[sel].scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter" && items.length) { location.href = items[Math.max(sel, 0)].href; }
    });
    document.addEventListener("click", (e) => { if (!box.contains(e.target) && e.target !== input) box.hidden = true; });
    document.addEventListener("keydown", (e) => {
      if (e.key === "/" && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) { e.preventDefault(); input.focus(); }
    });
  }

  // ---- utilities for the chart scripts ----
  const fmt = {
    n: (x, d) => (x == null || x === "" || isNaN(x) ? "–" : (+x).toFixed(d == null ? 2 : d)),
    int: (x) => (x == null || isNaN(x) ? "–" : Math.round(x).toLocaleString("en-GB")),
    signed: (x, d) => (x == null || isNaN(x) ? "–" : (x > 0 ? "+" : "") + (+x).toFixed(d == null ? 2 : d)),
  };
  const qs = (name) => new URLSearchParams(location.search).get(name);
  window.Site = { fmt, showTip, moveTip, hideTip, esc, download, toCSV, qs };
})();
