"""Lint the deck against the craft rules PowerPoint will not enforce.

Usage:
    python3 check_deck.py                 # reads _build/manifest.json (sh build.sh writes it) and deck.js
    python3 check_deck.py --minutes 20    # also compare the counts to the length table

Reports, by frame number (the title frame is 1, as in the footline and in
shoot.py's listing):
  - a frame without notes
  - an evidence frame (a stage or a figure) without a source or figcap line
  - a title that reads as a label (three words or fewer) rather than a claim
  - a font size, a face or a fit mode set in deck.js: the theme owns those;
    what does not fit at the theme's sizes is a second frame
  - a link or a back to a label no frame defines
  - a {{number}} data/numbers.js does not define (from the build log)
  - a stage, a chart or a figure the build could not draw (from the build log)
  - prose the build estimates to overflow its column (from the build log)
  - the counts: frames, stages, build-ins, appendix rooms, and with --minutes a note when
    they fall outside the length table (a note, not a finding: a deck under construction is short)
Exit status 1 when a finding is listed, so it can gate a build.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "_build", "manifest.json")
LOG = os.path.join(HERE, "_build", "build-log.txt")
DECK = os.path.join(HERE, "deck.js")

LENGTH_TABLE = {   # minutes: (frames min, frames max, stages max, build-ins max)
    12: (8, 10, 1, 1),
    20: (13, 16, 3, 2),
    45: (25, 35, 5, 2),
}


def main(argv):
    minutes = None
    if "--minutes" in argv:
        minutes = int(argv[argv.index("--minutes") + 1])
    if not os.path.exists(MANIFEST):
        sys.exit("no _build/manifest.json here: sh build.sh first")
    m = json.load(open(MANIFEST))
    frames = m["frames"]
    labels = set(m.get("labels", {}))
    findings = []

    n_main = sum(1 for f in frames if not f["appendix"])
    n_app = sum(1 for f in frames if f["appendix"])
    n_stages = sum(1 for f in frames if f["hasStage"])
    n_builds = sum(1 for f in frames if f["hasBuildIn"])

    for f in frames:
        tag = f"frame {'A' if f['appendix'] else ''}{f['n']}" + (f": {f['title'][:40]}" if f["title"] else "")
        if f["kind"]:
            continue
        if not f["hasNotes"]:
            findings.append(f"{tag}: no notes")
        if (f["hasStage"] or f["hasFig"]) and not f["hasSource"]:
            findings.append(f"{tag}: evidence without a source or figcap line")
        words = f["title"].split()
        if f["title"] and len(words) <= 3 and f["n"] > 1 and not f["appendix"]:
            findings.append(f"{tag}: title is a label, not a claim ({f['title']})")
        for lab in f["links"]:
            if lab not in labels:
                findings.append(f"{tag}: link to '{lab}' but no frame has label: '{lab}'")

    # deck.js must not set type sizes or faces: the theme owns them
    if os.path.exists(DECK):
        src = open(DECK, encoding="utf-8").read()
        for pat, why in ((r"\bfontSize\b", "a font size"), (r"\bfontFace\b", "a font face"), (r"\bfit\s*:\s*['\"]shrink", "fit: shrink"), (r"\bautoFit\b", "autoFit")):
            for mm in re.finditer(pat, src):
                line = src.count("\n", 0, mm.start()) + 1
                findings.append(f"deck.js:{line}: {why} set in the deck; the theme owns type sizes, split the frame instead")

    # the build's own findings
    if os.path.exists(LOG):
        for line in open(LOG, encoding="utf-8").read().splitlines():
            if line.strip():
                findings.append(line.strip())

    print(f"{n_main} frames in the talk, {n_app} in the appendix, {n_stages} stages, {n_builds} frames with steps or a build-in")
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
