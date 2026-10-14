"""Screenshot every page of the built deck and check it, with poppler only.

Usage:
    python3 shoot.py              # every page of _build/deck.pdf → _shots/NN.png
    python3 shoot.py 4 5 6        # only these pages (1-based); other screenshots are kept
    python3 shoot.py --handout    # _build/deck-handout.pdf instead (one page per frame)

Prints, for every page, the frame it belongs to and its overlay step, read
from beamer's .nav file, and the title read from the page itself; then the
compile errors and warnings from the log, and every page whose content
reaches the bottom of the frame. Needs pdftoppm and pdftotext (poppler:
brew install poppler / apt install poppler-utils). No Python packages.

Screenshots are numbered by page: the title page is 01 and an overlay step
is its own page. The plan, the notes and the reviews use frame numbers, as
the footline does; the listing maps one to the other (07 is frame 5 step 2
of 3). The handout build has one page per frame, so there the two agree.

Overflow check: the theme's footline is an 8 mm band whose top 3 mm are
always empty. Any ink in that band (rows between 8 mm and 5 mm from the
bottom edge) means content has reached the footline. beamer logs at most an
"Overfull \vbox" for this, easy to miss among other messages, and the page
still compiles; this check names the page. It reads a greyscale PGM from
pdftoppm, which the standard library can parse.
"""

import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "_build")
SHOTS = os.path.join(HERE, "_shots")
W, H = 1280, 720
PAGE_MM = 90.0                      # beamer 16:9 paper height
FOOTLINE_MM, GUARD_MM = 8.0, 3.0    # keep in step with \footlineheight in the theme
INK = 235                           # a pixel darker than this counts as ink (paper3 is 236)


def run(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode:
        sys.exit(f"{' '.join(cmd[:2])} failed: {res.stderr.strip()}")
    return res.stdout


def npages(pdf):
    m = re.search(r"Pages:\s+(\d+)", run(["pdfinfo", pdf]))
    return int(m.group(1)) if m else 0


def frame_map(nav):
    """page -> (frame label, step, nsteps) from beamer's .nav file."""
    if not os.path.exists(nav):
        return {}
    text = open(nav, encoding="utf-8", errors="replace").read()
    appendix_from = None
    m = re.search(r"\\beamer@appendixpages\s*\{(\d+)\}", text)
    if m:
        appendix_from = int(m.group(1))
    out, n_main, n_app = {}, 0, 0
    for a, b in re.findall(r"\\beamer@framepages\s*\{(\d+)\}\{(\d+)\}", text):
        a, b = int(a), int(b)
        if appendix_from and a >= appendix_from:
            n_app += 1
            label = f"A{n_app}"
        else:
            n_main += 1
            label = f"frame {n_main}"
        for p in range(a, b + 1):
            out[p] = (label, p - a + 1, b - a + 1)
    return out


def title_of(pdf, page):
    text = run(["pdftotext", "-f", str(page), "-l", str(page), "-layout", pdf, "-"])
    for line in text.splitlines():
        if line.strip():
            return line.strip()[:56]
    return ""


def bottom_ink(pgm_path):
    """True if any ink lies in the guard band above the footline."""
    with open(pgm_path, "rb") as f:
        data = f.read()
    # P5 header: magic, width, height, maxval, then raw bytes
    parts, pos = [], 0
    while len(parts) < 4:
        m = re.compile(rb"\s*(#[^\n]*\n\s*)*(\S+)").match(data, pos)
        parts.append(m.group(2))
        pos = m.end()
    w, h = int(parts[1]), int(parts[2])
    pixels = data[pos + 1:]
    px_per_mm = h / PAGE_MM
    lo = int(h - FOOTLINE_MM * px_per_mm)
    hi = int(h - (FOOTLINE_MM - GUARD_MM) * px_per_mm)
    for row in range(lo, hi):
        line = pixels[row * w:(row + 1) * w]
        if any(b < INK for b in line):
            return True
    return False


def log_problems(log):
    """Errors and the warnings that matter, deduplicated, from the lualatex log."""
    if not os.path.exists(log):
        return ["no log file; run build.sh first"]
    text = open(log, encoding="utf-8", errors="replace").read()
    # lualatex wraps lines at 79 characters; join continuation lines of a message
    lines = text.splitlines()
    found = []
    for i, line in enumerate(lines):
        msg = None
        if re.match(r"^(!|.*:\d+: )", line) and ("Error" in line or line.startswith("!")):
            msg = line + " " + (lines[i + 1].strip() if i + 1 < len(lines) else "")
        elif re.match(r"^(Package \w+ Warning|LaTeX Warning|Overfull|Underfull \\vbox|Missing character)", line):
            if line.startswith("Underfull") or "Rerun" in line or "may have changed" in line:
                continue
            msg = line
            j = i + 1
            while j < len(lines) and lines[j].startswith("(") and j < i + 3:
                msg += " " + lines[j].strip()
                j += 1
        if msg:
            msg = re.sub(r"\s+", " ", msg).strip()
            if "deck.out' has changed" in msg or "rerunfilecheck" in msg:
                continue
            found.append(msg)
    return list(dict.fromkeys(found))


def main(argv):
    handout = "--handout" in argv
    only = {int(a) for a in argv if a.isdigit()}
    stem = "deck-handout" if handout else "deck"
    pdf = os.path.join(BUILD, stem + ".pdf")
    if not os.path.exists(pdf):
        sys.exit("build the deck first: sh build.sh")
    for tool in ("pdftoppm", "pdftotext", "pdfinfo"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found: brew install poppler (macOS) or apt install poppler-utils")

    shots = SHOTS + ("-handout" if handout else "")
    if not only and os.path.isdir(shots):   # a full run starts clean; numbered runs replace only their own files
        shutil.rmtree(shots)
    os.makedirs(shots, exist_ok=True)

    n = npages(pdf)
    frames = frame_map(os.path.join(BUILD, stem + ".nav"))
    print(f"{n} pages in {os.path.relpath(pdf, HERE)}" + ("" if handout else f", {len({v[0] for v in frames.values()})} frames"))

    overflow = []
    for p in range(1, n + 1):
        if only and p not in only:
            continue
        base = os.path.join(shots, f"{p:02d}")
        scale = ["-scale-to-x", str(W), "-scale-to-y", str(H)]
        run(["pdftoppm", "-png", "-r", "150", *scale, "-f", str(p), "-l", str(p), "-singlefile", pdf, base])
        run(["pdftoppm", "-gray", *scale, "-f", str(p), "-l", str(p), "-singlefile", pdf, base + "_g"])
        touches = bottom_ink(base + "_g.pgm")
        os.remove(base + "_g.pgm")
        label, step, nsteps = frames.get(p, ("", 1, 1))
        stepinfo = f" step {step}/{nsteps}" if nsteps > 1 and not handout else ""
        flag = "   <- content reaches the footline" if touches else ""
        print(f"  {p:02d}.png  {label:9s}{stepinfo:10s} {title_of(pdf, p)}{flag}")
        if touches:
            overflow.append(p)

    problems = log_problems(os.path.join(BUILD, stem + ".log"))
    print()
    if problems:
        print("log messages:")
        for m in problems:
            print("  -", m[:220])
    else:
        print("no errors or warnings in the log")
    if overflow:
        print("pages whose content reaches the footline: " + ", ".join(f"{p:02d}" for p in overflow))
    else:
        print("no page reaches the footline")
    print(f"screenshots in {os.path.relpath(shots, HERE)}/")


if __name__ == "__main__":
    main(sys.argv[1:])
