#!/usr/bin/env python3
"""
update_site.py

Rebuilds the site after the paper has changed and says what changed.

    python3 update_site.py [--config site.json] [--no-browser] [--deploy]

It runs build_site.py and check_site.py, compares the new build with the
previous one, and writes a change report (also saved as _update_report.md):
pages added, removed, renamed or moved, figures and tables that are new, gone
or renumbered, and a draft line for the errata page.

Publishing. If site.json has "deploy": {"target": "<folder>"}, the report
ends with the command that copies the site there. --deploy runs that copy.
It refuses a target that holds anything other than an earlier build of this
site, because the copy deletes files the new build does not have. It never
commits or pushes.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def diff(old, new):
    lines = []
    ot = {p["slug"]: p["title"] for p in old.get("nav", [])}
    nt = {p["slug"]: p["title"] for p in new.get("nav", [])}
    moved = {k: v for k, v in new.get("redirects", {}).items() if k not in old.get("redirects", {})}
    for s in nt:
        if s not in ot:
            lines.append(f"- New page: {nt[s]} ({s}.html)")
        elif ot[s] != nt[s]:
            lines.append(f"- Page retitled: \"{ot[s]}\" is now \"{nt[s]}\" ({s}.html, address unchanged)")
    for s in ot:
        if s not in nt:
            to = moved.get(s)
            lines.append(f"- Page gone: {ot[s]} ({s}.html)" + (f", now redirects to {to}.html" if to else ""))
    for kind, key in (("Figure", "figures"), ("Table", "tables")):
        o, n = old.get(key, {}), new.get(key, {})
        for lab in n:
            if lab not in o:
                lines.append(f"- New {kind.lower()}: {kind} {n[lab]['number']}, {n[lab].get('title', '')} ({lab})")
            elif o[lab]["number"] != n[lab]["number"]:
                lines.append(f"- {kind} renumbered: {kind} {o[lab]['number']} is now {kind} {n[lab]['number']} ({lab})")
            elif o[lab].get("title") != n[lab].get("title"):
                lines.append(f"- {kind} {n[lab]['number']} has a new title: {n[lab].get('title', '')}")
        for lab in o:
            if lab not in n:
                lines.append(f"- {kind} removed: {kind} {o[lab]['number']}, {o[lab].get('title', '')} ({lab})")
    eo, en = old.get("equations", {}), new.get("equations", {})
    ch = [f"({eo[k]}) is now ({en[k]})" for k in en if k in eo and eo[k] != en[k]]
    if ch:
        lines.append(f"- Equations renumbered: {', '.join(ch[:8])}" + (" and more" if len(ch) > 8 else ""))
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "site.json"))
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--deploy", action="store_true")
    args = ap.parse_args()
    cfg_path = Path(args.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    out = (cfg_path.parent / cfg.get("output_dir", "../Website")).resolve()
    old = load(out / "data" / "registry.json")

    b = subprocess.run([sys.executable, str(HERE / "build_site.py"), "--config", str(cfg_path)], capture_output=True, text=True)
    print(b.stdout + b.stderr)
    if b.returncode != 0:
        sys.exit("The build failed. The published site was not touched.")
    c = subprocess.run([sys.executable, str(HERE / "check_site.py"), "--config", str(cfg_path)] + ([] if args.no_browser else ["--browser"]),
                       capture_output=True, text=True)
    new = load(out / "data" / "registry.json")
    problems = [l for l in c.stdout.split("\n") if l.startswith(("ERROR", "WARNING"))]

    rep = [f"# Site update, {new['built']}", "",
           f"Paper version {new.get('paper_date', '')}" + (f" ({new['commit']})" if new.get("commit") else "")
           + (f". Previous build: {old.get('built', 'unknown')}, paper version {old.get('paper_date', 'unknown')}"
              + (f" ({old['commit']})" if old.get("commit") else "") + "." if old else ". This is the first build."), ""]
    changes = diff(old, new) if old else []
    rep += ["## What changed", ""] + (changes or ["- No change in pages, figures, tables or equation numbers. The text may still have changed."]) + [""]
    if old and old.get("template_version") != new.get("template_version"):
        rep += [f"Template version {old.get('template_version', 'unknown')} -> {new.get('template_version')}.", ""]
    rep += ["## Checker", ""] + ([f"- {l}" for l in problems] or ["- No errors or warnings."]) + [""]
    if old:
        what = "; ".join(l[2:].split(" (")[0] for l in changes[:4]) or "text revised"
        rep += ["## Draft line for the errata page", "",
                f'`<tr><th scope="row">{new["built"]}</th><td class="al-left">Rebuilt from the version of the paper dated {new.get("paper_date", "")}. {what}.</td></tr>`',
                "", "Edit it to say what changed in substance, then add it as the first row of the table in content/errata.html.", ""]

    target = (cfg.get("deploy") or {}).get("target")
    if target:
        tgt = (cfg_path.parent / target).resolve()
        cmd = ["rsync", "-a", "--delete", "--exclude", ".git", str(out) + "/", str(tgt) + "/"]
        rep += ["## Publishing", "", "Copy the site to its public folder with:", "", "    " + " ".join(f'"{x}"' if " " in x else x for x in cmd), "",
                "Then commit and push that repository yourself.", ""]
        if args.deploy:
            prev = load(tgt / "data" / "registry.json")
            empty = not tgt.exists() or not any(tgt.iterdir())
            if c.returncode != 0:
                rep += ["NOT published: the checker reports errors. Fix them first.", ""]
            elif not empty and (prev is None or prev.get("site_title") != new.get("site_title")):
                rep += [f"NOT published: {tgt} holds files that are not an earlier build of this site. The copy would delete them. "
                        "Check deploy.target, or empty the folder yourself.", ""]
            elif not shutil.which("rsync"):
                rep += ["NOT published: rsync is not installed.", ""]
            else:
                tgt.mkdir(parents=True, exist_ok=True)
                r = subprocess.run(cmd, capture_output=True, text=True)
                rep += [f"Published to {tgt}." if r.returncode == 0 else f"The copy failed: {r.stderr.strip()[:300]}", ""]
    elif args.deploy:
        rep += ["## Publishing", "", 'NOT published: site.json has no "deploy": {"target": "..."}.', ""]

    text = "\n".join(rep)
    (cfg_path.parent / "_update_report.md").write_text(text, encoding="utf-8")
    print(text)
    sys.exit(1 if c.returncode != 0 else 0)


if __name__ == "__main__":
    main()
