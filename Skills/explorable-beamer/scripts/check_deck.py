"""Lint deck.tex against the craft rules that beamer will not enforce.

Usage:
    python3 check_deck.py                 # reads deck.tex next to this script
    python3 check_deck.py --minutes 20    # also compare the counts to the length table

Reports, by frame number (the title frame is 1, as in the footline and in
shoot.py's listing):
  - a frame without a \\note
  - an evidence frame (a stage, a chart, a figure) without a \\source or \\figcap line
  - a title that reads as a label (three words or fewer) rather than a claim
  - a font-size command in a frame body (\\small, \\footnotesize, \\scriptsize, \\tiny):
    the frame is fixed and the back row is far away; split the slide instead
  - [shrink] or [allowframebreaks], the same rule
  - \\only<1> or \\only<1-N>: content that should vanish still shows in the handout
  - a stepped stage (\\stagesteps{N}) whose frame does not carry <1-N>
  - a \\goto or \\hyperlink to a label no frame defines
  - a \\D{key} whose key data/numbers.tex does not define
  - \\begin{split}: amsmath owns that name; the layout is `beside`
  - the counts: frames, stages, build-ins, appendix rooms, and with --minutes a note when
    they fall outside the length table (a note, not a finding: a deck under construction is short)
Exit status 1 when a finding is listed, so it can gate a build.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(HERE, "deck.tex")
NUMBERS = os.path.join(HERE, "data", "numbers.tex")

LENGTH_TABLE = {   # minutes: (frames min, frames max, stages max, build-ins max)
    12: (8, 10, 1, 1),
    20: (13, 16, 3, 2),
    45: (25, 35, 5, 2),
}


def strip_comments(text):
    return re.sub(r"(?<!\\)%.*", "", text)


def frames(text):
    """Yield (number, label, title, body, is_appendix, line) for every frame in document order."""
    appendix_at = text.find("\\appendix")
    out, n = [], 0
    pattern = re.compile(r"\\begin\{frame\}(<[^>]*>)?(\[[^\]]*\])?(\{((?:[^{}]|\{[^{}]*\})*)\})?(.*?)\\end\{frame\}", re.S)
    for m in pattern.finditer(text):
        n += 1
        opts = m.group(2) or ""
        lab = re.search(r"label=([\w:-]+)", opts)
        out.append({
            "n": n, "overlay": m.group(1) or "", "opts": opts,
            "label": lab.group(1) if lab else None,
            "title": (m.group(4) or "").strip(), "body": m.group(5),
            "appendix": appendix_at != -1 and m.start() > appendix_at,
            "line": text.count("\n", 0, m.start()) + 1,
        })
    # \divider and \assertion expand to frames too; count them in document order
    marks = [(m.start(), "divider", m) for m in re.finditer(r"\\divider(\[[^\]]*\])?\{((?:[^{}]|\{[^{}]*\})*)\}", text)]
    marks += [(m.start(), "assertion", m) for m in re.finditer(r"\\assertion\{((?:[^{}]|\{[^{}]*\})*)\}", text)]
    for pos, kind, m in marks:
        out.append({"n": 0, "overlay": "", "opts": "", "label": None, "kind": kind,
                    "title": m.group(2) if kind == "divider" else m.group(1), "body": "", "plain": True,
                    "appendix": appendix_at != -1 and pos > appendix_at, "line": text.count("\n", 0, pos) + 1})
    out.sort(key=lambda f: f["line"])
    for i, f in enumerate(out, 1):
        f["n"] = i
    return out


def main(argv):
    minutes = None
    if "--minutes" in argv:
        minutes = int(argv[argv.index("--minutes") + 1])
    if not os.path.exists(DECK):
        sys.exit("no deck.tex here")
    raw = open(DECK, encoding="utf-8").read()
    text = strip_comments(raw)
    keys = set()
    if os.path.exists(NUMBERS):
        keys = set(re.findall(r"\\defnum\{([^}]*)\}", strip_comments(open(NUMBERS, encoding="utf-8").read())))
    chart_text = ""
    for root, _, files in os.walk(os.path.join(HERE, "charts")):
        for f in files:
            if f.endswith(".tex"):
                chart_text += strip_comments(open(os.path.join(root, f), encoding="utf-8").read())

    findings = []
    all_frames = frames(text)
    labels = {f["label"] for f in all_frames if f["label"]}
    n_main = sum(1 for f in all_frames if not f["appendix"])
    n_app = sum(1 for f in all_frames if f["appendix"])
    n_stages = n_builds = 0

    for f in all_frames:
        tag = f"frame {f['n']}" + (" (appendix)" if f["appendix"] else "") + (f": {f['title'][:40]}" if f["title"] else "")
        body, plain = f["body"], f.get("plain") or "plain" in f["opts"]
        if plain:
            continue
        # a chart file is part of the frame that inputs it: its caption and its overlays count here
        for m in re.finditer(r"\\input\{charts/([\w-]+)\}", body):
            cpath = os.path.join(HERE, "charts", m.group(1) + ".tex")
            if os.path.exists(cpath):
                body += strip_comments(open(cpath, encoding="utf-8").read())
        if "\\note{" not in body and "\\note<" not in body:
            findings.append(f"{tag}: no \\note")
        has_stage = "\\begin{stage}" in body or "\\input{charts" in body
        has_fig = "\\includegraphics" in body or "\\fig{" in body or "\\fig[" in body or "\\figpair{" in body
        if (has_stage or has_fig) and "\\source{" not in body and "\\figcap{" not in body and "\\stagecap{" not in body:
            findings.append(f"{tag}: evidence without a \\source or \\figcap line")
        if has_stage:
            n_stages += 1
        if re.search(r"\\visible<|\\pause|visible on=|\\uncover<|\\onslide<", body):
            n_builds += 1
        title = f["title"]
        words = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?|[{}]", " ", title).split()
        if title and len(words) <= 3 and f["n"] > 1 and not f["appendix"]:
            findings.append(f"{tag}: title is a label, not a claim ({' '.join(words)})")
        for cmd in ("\\small", "\\footnotesize", "\\scriptsize", "\\tiny"):
            if re.search(re.escape(cmd) + r"(?![a-zA-Z])", body):
                findings.append(f"{tag}: {cmd} in the frame body; split the slide instead of shrinking the type")
        for opt in ("shrink", "allowframebreaks"):
            if opt in f["opts"]:
                findings.append(f"{tag}: [{opt}]; what does not fit is a second frame")
        for m in re.finditer(r"\\only<(1|1-\d+)>", body):
            findings.append(f"{tag}: \\only<{m.group(1)}> vanishes in the talk but shows in the handout; use \\visible<…> or \\step")
        for m in re.finditer(r"\\stagesteps\{(\d+)\}", body):
            if f["overlay"] != f"<1-{m.group(1)}>":
                findings.append(f"{tag}: stage declares {m.group(1)} steps but the frame has no <1-{m.group(1)}>")
        for m in re.finditer(r"\\input\{charts/([\w-]+)\}", body):
            cpath = os.path.join(HERE, "charts", m.group(1) + ".tex")
            if os.path.exists(cpath):
                ct = strip_comments(open(cpath, encoding="utf-8").read())
                sm = re.search(r"\\stagesteps\{(\d+)\}", ct)
                if sm and f["overlay"] != f"<1-{sm.group(1)}>":
                    findings.append(f"{tag}: charts/{m.group(1)} declares {sm.group(1)} steps but the frame has no <1-{sm.group(1)}>")
        for m in re.finditer(r"\\(?:goto|hyperlink)\{([\w:-]+)\}", body):
            if m.group(1) not in labels:
                findings.append(f"{tag}: link to '{m.group(1)}' but no frame has label={m.group(1)}")
        for m in re.finditer(r"\\back\{([\w:-]+)\}", body):
            if m.group(1) not in labels:
                findings.append(f"{tag}: \\back to '{m.group(1)}' but no frame has label={m.group(1)}")
        if "\\begin{split}" in body:
            findings.append(f"{tag}: \\begin{{split}} is amsmath's; the layout is \\begin{{beside}}")
        if re.search(r"\\(sub)?section\{", body) or "\\framesubtitle" in body and False:
            findings.append(f"{tag}: a heading inside a frame")

    for m in re.finditer(r"\\D(?:v)?(?:\[\d+\])?\{([^}]*)\}", text + chart_text):
        key = m.group(1)
        if "\\" in key or "#" in key:
            continue
        if keys and key not in keys:
            findings.append(f"data: \\D{{{key}}} is used but data/numbers.tex does not define it")

    print(f"{n_main} frames in the talk, {n_app} in the appendix, {n_stages} stages, {n_builds} frames with a build-in")
    if minutes:
        slot = min(LENGTH_TABLE, key=lambda k: abs(k - minutes))
        lo, hi, st, bi = LENGTH_TABLE[slot]
        print(f"for a {minutes}-minute slot (nearest row: {slot} min): {lo}-{hi} counted frames, up to {st} stages, {bi} build-ins")
        notes = []
        if not lo <= n_main <= hi:
            notes.append(f"{n_main} counted frames for {minutes} minutes; the table says {lo}-{hi}")
        if n_stages > st:
            notes.append(f"{n_stages} stages for {minutes} minutes; the table says up to {st}")
        if n_builds > bi:
            notes.append(f"{n_builds} build-ins for {minutes} minutes; the table says up to {bi}")
        for n in notes:   # counts are advice while the deck is being built, so they do not fail the run
            print("  note:", n)

    if findings:
        print("\nfindings:")
        for x in dict.fromkeys(findings):
            print("  -", x)
        sys.exit(1)
    print("no findings")


if __name__ == "__main__":
    main(sys.argv[1:])
