#!/usr/bin/env python3
"""
check_site.py

Checks a built site before it is shown to anyone. Run after build_site.py:

    python3 check_site.py [--config site.json] [--browser]

Static checks: every internal link and anchor resolves, no build markers or
template placeholders are left, no unresolved cross references or citations,
no raw LaTeX commands in the text, every figure has an image, figure and
table numbers match the PDF, the data folder holds only small aggregate
files, and the credit line is on every page.

--browser also opens every page in headless Chrome and counts math that
KaTeX could not render and JavaScript errors. Needs Chrome or Chromium and a
network connection (KaTeX and D3 load from a CDN).

Exit code 1 if an error is found. Warnings do not change the exit code.
"""

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CREDIT_URL = "https://github.com/claesbackman/AI-research-feedback"
errors, warnings = [], []


def chrome():
    for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium",
              "google-chrome", "chromium", "chromium-browser", "chrome"):
        if Path(c).is_file() or shutil.which(c):
            return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "site.json"))
    ap.add_argument("--browser", action="store_true")
    args = ap.parse_args()
    cfg_path = Path(args.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    out = (cfg_path.parent / cfg.get("output_dir", "../Website")).resolve()
    regfile = out / "data" / "registry.json"
    if not regfile.exists():
        raise SystemExit(f"No built site at {out}. Run build_site.py first.")
    reg = json.loads(regfile.read_text(encoding="utf-8"))
    pages = {p: (out / f"{p}.html").read_text(encoding="utf-8") for p in reg["pages"] if (out / f"{p}.html").exists()}
    ids = {p: set(re.findall(r'\sid="([^"]+)"', h)) for p, h in pages.items()}

    # links and anchors
    for p, h in pages.items():
        for attr, url in re.findall(r'\s(href|src)="([^"]+)"', h):
            url = html.unescape(url)
            if re.match(r"([a-zA-Z][a-zA-Z0-9+.-]*:|//)", url):
                continue
            path, _, frag = url.partition("#")
            path = path.split("?")[0]
            target = p if not path else path[:-5] if path.endswith(".html") else None
            if path and not (out / path).exists():
                errors.append(f"{p}.html: broken link {url}")
                continue
            if frag and target in ids and frag not in ids[target]:
                errors.append(f"{p}.html: anchor not found: {url}")

    # leftovers
    for p, h in pages.items():
        body = re.sub(r"<script.*?</script>|<style.*?</style>|<pre.*?</pre>|<code.*?</code>", " ", h, flags=re.S)
        for m in set(re.findall(r"@@[A-Z_|a-z:0-9-]+@@", body)):
            errors.append(f"{p}.html: build marker left in the page: {m}")
        for m in set(re.findall(r"\[\[[^\]]{0,400}\]\]", re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S))):
            errors.append(f"{p}.html: template placeholder not filled in: {m}")
        if "<!-- EDIT" in h:
            errors.append(f"{p}.html: a template instruction (<!-- EDIT: ... -->) is still in the page")
        n = len(re.findall(r'class="xref unresolved"', h))
        if n:
            errors.append(f"{p}.html: {n} unresolved cross reference(s)")
        cites = {k for c in re.findall(r'<a class="cite"[^>]*>(.*?)</a>', h, flags=re.S) for k in re.findall(r"<strong>([^<?]+)\?</strong>", c)}
        if cites:
            errors.append(f"{p}.html: citation key(s) not in the .bib file: {', '.join(sorted(cites)[:8])}")
        text = re.sub(r'<span class="math[^>]*>.*?</span>', " ", body, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        raw = Counter(re.findall(r"\\[a-zA-Z]{2,}", text))
        if raw:
            warnings.append(f"{p}.html: raw LaTeX in the text: " + ", ".join(f"{k} ({v})" for k, v in raw.most_common(6)))
        if '<p class="credit">' not in h or CREDIT_URL not in h.split('<p class="credit">')[-1][:400]:
            errors.append(f"{p}.html: the credit line is missing")
        if "The image for this figure was not found" in h:
            errors.append(f"{p}.html: a figure has no image")
        n = h.count("This table could not be converted")
        if n:
            warnings.append(f"{p}.html: {n} table(s) could not be converted and point to the PDF")

    if "index" in pages and 'class="credit-full"' not in pages["index"]:
        errors.append("index.html: the full citation of the skill is missing from the title page")

    # every numbered exhibit must be on some page
    all_ids = set().union(*ids.values()) if ids else set()
    for kind, key in (("Figure", "figures"), ("Table", "tables")):
        for label, v in reg[key].items():
            if label not in all_ids:
                errors.append(f"{kind} {v['number']} ({label}) is numbered but appears on no page. It was probably inside a wrapper command that pandoc dropped.")

    # exhibit numbers against the PDF
    pdf = (cfg_path.parent / cfg["pdf"]).resolve() if cfg.get("pdf") else None
    if pdf and pdf.is_file() and shutil.which("pdftotext"):
        txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
        for kind, key in (("Figure", "figures"), ("Table", "tables")):
            in_pdf = set(re.findall(r"^\s*" + kind + r"\s+([A-Z]?\.?\d+(?:\.\d+)?)\s*[:.]", txt, flags=re.M))
            on_site = {v["number"] for v in reg[key].values()}
            if in_pdf:
                if on_site - in_pdf:
                    warnings.append(f"{kind} numbers on the site but not found as captions in the PDF: {', '.join(sorted(on_site - in_pdf))}")
                if in_pdf - on_site:
                    warnings.append(f"{kind} numbers in the PDF but not on the site: {', '.join(sorted(in_pdf - on_site))}")
        print(f"exhibit numbers compared with {pdf.name}")
    else:
        warnings.append("exhibit numbers were not compared with the PDF (no pdf in site.json, or pdftotext is not installed)")

    # data folder
    print("data folder:")
    for f in sorted((out / "data").iterdir()):
        size = f.stat().st_size
        rows = ""
        if f.suffix == ".csv":
            n = sum(1 for _ in f.open(encoding="utf-8")) - 1
            rows = f", {n} rows"
        print(f"  {f.name}: {size / 1024:.0f} KB{rows}")
        if size > 2_000_000 and f.name != "search.js":
            warnings.append(f"data/{f.name} is {size / 1e6:.1f} MB. Check that it holds aggregates only.")

    # rendered pages
    if args.browser:
        exe = chrome()
        if not exe:
            warnings.append("--browser: Chrome or Chromium not found, rendered checks skipped")
        else:
            for p in pages:
                r = subprocess.run([exe, "--headless=new", "--disable-gpu", "--virtual-time-budget=8000", "--enable-logging=stderr", "--v=0",
                                    "--dump-dom", (out / f"{p}.html").as_uri()], capture_output=True, text=True, timeout=120)
                dom = r.stdout
                bad = re.findall(r'class="katex-error"[^>]*title="([^"]*)"', dom)
                if bad:
                    errors.append(f"{p}.html: {len(bad)} formula(s) KaTeX could not render, first: {html.unescape(bad[0])[:140]}")
                red = re.findall(r'style="color:\s*#cc0000;?">([^<]{1,40})', dom)
                if red:
                    errors.append(f"{p}.html: KaTeX does not know {len(red)} command(s), shown in red: {', '.join(sorted(set(html.unescape(x) for x in red))[:6])}")
                if 'class="katex"' not in dom and 'class="math' in pages[p]:
                    warnings.append(f"{p}.html: math was not rendered (no network for the KaTeX CDN?)")
                js = [l for l in r.stderr.split("\n") if "Uncaught" in l]
                if js:
                    errors.append(f"{p}.html: JavaScript error: {js[0][-200:]}")
                if "data/figures.js" in pages[p]:
                    drawn = len(re.findall(r'<svg class="chart"', dom))
                    print(f"  {p}.html: {drawn} figure(s) drawn from data")
            print(f"rendered {len(pages)} pages in headless Chrome")

    print(f"\n{len(pages)} pages, {len(reg['figures'])} figures, {len(reg['tables'])} tables")
    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
