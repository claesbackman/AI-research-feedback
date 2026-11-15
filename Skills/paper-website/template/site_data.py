#!/usr/bin/env python3
"""
site_data.py

Data step of the site build (data tier 1 and 2). Called by build_site.py.

For every figure listed under data.figures in site.json it reads one CSV of
aggregates, keeps only the columns the chart needs, and writes
    <site>/data/figures.js      window.SITE_FIGURES, read by assets/figures.js
    <site>/data/<label>.csv     the plotted numbers, for download
For data.explorer it writes data/explorer.js and data/explorer.csv.

Disclosure guard. The site is public, so the script refuses a source that
looks like microdata: more rows than data.max_rows (default 2000), a column
that names a person or firm identifier, or a cell count below data.min_cell.
Set "confirmed_aggregate": true on one source to pass the first two checks
after you have looked at the file. The source files themselves are never
copied. Only the named columns reach the site.
"""

import csv
import html
import json
import re
from pathlib import Path

SENSITIVE = re.compile(r"(^|_)(id|pnr|cpr|ssn|cvr|personnummer|email|e_mail|address|adresse|birthdate|dob|firstname|lastname|surname|ip)($|_)", re.I)
COUNT_COLS = re.compile(r"^(n|n_obs|nobs|obs|count|cell_n|cellsize|cell_size|freq)$", re.I)
ROLE_KEYS = ("label", "value", "lo", "hi", "x", "y", "series", "group")


def read_table(path):
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    delim = "\t" if path.suffix.lower() in (".tsv", ".tab") else (";" if text.split("\n", 1)[0].count(";") > text.split("\n", 1)[0].count(",") else ",")
    rows = list(csv.DictReader(text.splitlines(), delimiter=delim))
    return rows, (list(rows[0].keys()) if rows else [])


def to_num(v):
    if v is None:
        return None
    s = str(v).strip()
    if s in ("", ".", "NA", "NaN", "nan"):
        return None
    try:
        return float(s)
    except ValueError:
        return s


def load(spec, base, numeric, data_cfg, name, problems):
    path = (base / spec["file"]).resolve()
    if not path.is_file():
        problems.append(f"{name}: file not found: {path}")
        return None
    rows, cols = read_table(path)
    keep = [spec[k] for k in ROLE_KEYS if spec.get(k)] + list(spec.get("dimensions", [])) + list(spec.get("columns", []))
    keep = list(dict.fromkeys(keep))
    missing = [c for c in keep if c not in cols]
    if missing:
        problems.append(f"{name}: column(s) not in {path.name}: {', '.join(missing)}. The file has: {', '.join(cols)}")
        return None
    for col, val in (spec.get("filter") or {}).items():
        vals = [str(v) for v in (val if isinstance(val, list) else [val])]
        rows = [r for r in rows if str(r.get(col)) in vals]
    ok = spec.get("confirmed_aggregate", False)
    max_rows = data_cfg.get("max_rows", 2000)
    if len(rows) > max_rows and not ok:
        problems.append(f"{name}: {path.name} has {len(rows)} rows after filtering (limit {max_rows}). A file this long is usually microdata. "
                        "Aggregate it first, or set \"confirmed_aggregate\": true on this source if every row is an aggregate.")
    bad = [c for c in keep if SENSITIVE.search(c)]
    if bad and not ok:
        problems.append(f"{name}: column name(s) that suggest identifiers: {', '.join(bad)}. Drop them, or set \"confirmed_aggregate\": true.")
    min_cell = data_cfg.get("min_cell")
    if min_cell and not any(COUNT_COLS.match(c) or c == spec.get("count") for c in cols):
        problems.append(f"{name}: data.min_cell is set but {path.name} has no count column the script recognises. Name it with \"count\": \"<column>\" on this source.")
    if min_cell:
        for c in cols:
            if COUNT_COLS.match(c) or c == spec.get("count"):
                small = [r for r in rows if isinstance(to_num(r[c]), float) and to_num(r[c]) < min_cell]
                if small:
                    problems.append(f"{name}: {len(small)} row(s) of {path.name} have {c} below the minimum cell size {min_cell}. Suppress or pool these cells.")
    scale = spec.get("scale", 1)
    digits = spec.get("round", 6)
    out = []
    for r in rows:
        o = {}
        for c in keep:
            v = to_num(r[c]) if c in numeric else r[c]
            if isinstance(v, float):
                v = round(v * (scale if c in spec.get("_scaled", ()) else 1), digits)
                v = int(v) if v == int(v) and abs(v) < 1e15 else v
            o[c] = v
        out.append(o)
    return dict(rows=out, columns=keep, source=path.name)


def write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow(["" if r[c] is None else r[c] for c in cols])


def prune(out, keep=()):
    """Remove data files an earlier build published that this build does not."""
    d = out / "data"
    if d.is_dir():
        for f in d.iterdir():
            if (f.suffix == ".csv" or f.name in ("figures.js", "explorer.js")) and f.name not in keep:
                f.unlink()


def build(cfg, reg, out, warn):
    d = cfg["data"]
    base = cfg["_base"]
    data_dir = out / "data"
    problems, listing, figures = [], [], {}
    pending = []          # (path, rows, columns) or (path, text): nothing is written until every source has passed

    for label, spec in (d.get("figures") or {}).items():
        if label not in reg.figures:
            warn(f"data.figures: no figure with label {label} in the paper. Labels: {', '.join(reg.figures)}")
            continue
        typ = spec.get("type")
        need = {"coef": ("label", "value"), "bar": ("label", "value"), "line": ("x", "y"), "event": ("x", "y"), "scatter": ("x", "y")}.get(typ)
        if not need:
            problems.append(f"{label}: type must be coef, bar, line, event or scatter")
            continue
        if any(not spec.get(k) for k in need):
            problems.append(f"{label}: a {typ} chart needs {' and '.join(need)}")
            continue
        numeric = {spec[k] for k in ("value", "lo", "hi", "x", "y") if spec.get(k)}
        spec["_scaled"] = {spec[k] for k in ("value", "lo", "hi", "y") if spec.get(k)}
        got = load(spec, base, numeric, d, label, problems)
        if not got:
            continue
        bad = [c for c in numeric if any(isinstance(r[c], str) for r in got["rows"])]
        if bad:
            problems.append(f"{label}: column(s) {', '.join(sorted(bad))} must be numeric for a {typ} chart, but hold text. "
                            "For categories on the axis use type coef or bar.")
            continue
        if typ in ("coef", "bar"):
            keys = [(r[spec["label"]], r.get(spec.get("series")), r.get(spec.get("group"))) for r in got["rows"]]
            if len(set(keys)) < len(keys):
                warn(f"{label}: several rows share one {spec['label']}. Add \"series\" or \"group\" (or a \"filter\") so each mark is one row.")
        fname = re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_") + ".csv"
        pending.append((data_dir / fname, got["rows"], got["columns"]))
        pub = {k: v for k, v in spec.items() if k not in ("file", "filter", "confirmed_aggregate", "_scaled", "scale", "round", "description")}
        pub.update(rows=got["rows"], columns=got["columns"], csv="data/" + fname)
        figures[label] = pub
        listing.append((fname, f"Figure {reg.figures[label]['number']}: " + (spec.get("description") or reg.figures[label].get("title", "")), len(got["rows"]), got["columns"]))

    ex = d.get("explorer") if int(d.get("tier", 0)) >= 2 else None
    if ex:
        if not ex.get("dimensions") or not ex.get("value"):
            problems.append("data.explorer needs dimensions (a list of columns) and value (one column)")
        else:
            ex["_scaled"] = {ex[k] for k in ("value", "lo", "hi") if ex.get(k)}
            got = load(ex, base, set(ex["_scaled"]), d, "explorer", problems)
            if got:
                pending.append((data_dir / "explorer.csv", got["rows"], got["columns"]))
                pub = {k: v for k, v in ex.items() if k not in ("file", "filter", "confirmed_aggregate", "_scaled", "scale", "round", "description", "title", "intro")}
                pub["rows"] = got["rows"]
                pending.append((data_dir / "explorer.js", "window.SITE_EXPLORER = " + json.dumps(pub, ensure_ascii=False, separators=(",", ":")) + ";\n"))
                listing.append(("explorer.csv", ex.get("description") or "The table behind the results explorer", len(got["rows"]), got["columns"]))

    if problems:
        raise SystemExit("Data step stopped before any page was written. Fix these sources:\n  - " + "\n  - ".join(problems))

    pending.append((data_dir / "figures.js", "window.SITE_FIGURES = " + json.dumps(figures, ensure_ascii=False, separators=(",", ":")) + ";\n"))
    prune(out, keep={p[0].name for p in pending})
    for item in pending:
        if len(item) == 3:
            write_csv(*item)
        else:
            item[0].write_text(item[1], encoding="utf-8")
    print(f"data: {len(figures)} figure(s) with data" + (", explorer" if ex else ""))
    if not listing:
        return ""
    rows = "".join(f'<tr><th scope="row"><a href="data/{f}"><code>{f}</code></a></th><td class="al-left">{html.escape(desc)}</td>'
                   f'<td>{n}</td><td class="al-left"><code>{html.escape(", ".join(cols))}</code></td></tr>' for f, desc, n, cols in listing)
    return ('<table class="est"><thead><tr><th>File</th><th class="al-left">Contents</th><th>Rows</th><th class="al-left">Columns</th></tr></thead>'
            f"<tbody>{rows}</tbody></table>")
