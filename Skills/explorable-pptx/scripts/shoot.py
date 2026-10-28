"""Screenshot every slide of the built deck and check it.

Usage:
    python3 shoot.py              # every slide of deck.pptx → _shots/NN.png
    python3 shoot.py 4 5 6        # only these slides (1-based); other screenshots are kept
    python3 shoot.py --handout    # deck-handout.pptx instead (one slide per frame) → _shots-handout/

Converts the .pptx to PDF, rasterises every page, and prints, for every
page, the frame it belongs to and its step (from _build/manifest.json, which
build.js writes) and the frame's title; then every message from the build
log (undefined numbers, unknown charts, links to no label, prose that
probably overflows); then every page whose content reaches the bottom of
the frame. Needs pdftoppm and pdfinfo (poppler: brew install poppler / apt
install poppler-utils) and one converter:

  - Microsoft PowerPoint on macOS, driven by AppleScript (the default there):
    the screenshots are what the deck will look like. The script launches
    PowerPoint in the background if it is not running and leaves it running,
    because a cold launch costs up to a minute and the export itself takes
    seconds. A first run may ask you to allow automation. A run that stalls is
    killed after a timeout and retried once.
  - LibreOffice (`soffice`) anywhere else, or with PPTX2PDF=soffice: fonts are
    substituted with different metrics, so the screenshots are approximate.

Screenshots are numbered by slide: the title slide is 01 and a step is its
own slide. The plan, the notes and the reviews use frame numbers, as the
footline does; the listing maps one to the other (07 is frame 5 step 2 of 3).
The handout build has one slide per frame, so there the two agree.

Overflow check: the theme's footline is a 0.5 in band whose top 0.2 in
(the guard) is always empty. Any ink in the guard band means content has
reached the footline. PowerPoint does not clip an overfull text box, so this
is the check that catches a frame which is too tall. It reads a greyscale
PGM from pdftoppm, which the standard library can parse.
"""

import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "_build")
SHOTS = os.path.join(HERE, "_shots")
W, H = 1280, 720
PAGE_IN = 5.625                       # canvas height, inches (LAYOUT_16x9)
FOOTLINE_IN, GUARD_IN = 0.5, 0.2      # keep in step with geo.footline and geo.guard in theme/theme.js
INK = 235                             # a pixel darker than this counts as ink (paper3 is 236)
POWERPOINT = "/Applications/Microsoft PowerPoint.app"
EXPORT_TIMEOUT = 300

APPLESCRIPT = '''
on run argv
  set inPath to item 1 of argv
  set outPath to item 2 of argv
  with timeout of 600 seconds
    tell application "Microsoft PowerPoint"
      open (POSIX file inPath)
      set pres to active presentation
      save pres in (POSIX file outPath) as save as PDF
      close pres saving no
    end tell
  end timeout
  return "exported"
end run
'''


def run(cmd, **kw):
    res = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if res.returncode:
        sys.exit(f"{' '.join(cmd[:2])} failed: {res.stderr.strip()}")
    return res.stdout


def converter():
    want = os.environ.get("PPTX2PDF", "").lower()
    if want in ("powerpoint", "soffice"):
        return want
    if platform.system() == "Darwin" and os.path.isdir(POWERPOINT):
        return "powerpoint"
    if shutil.which("soffice"):
        return "soffice"
    sys.exit("no converter: install LibreOffice (soffice on the PATH) or, on macOS, Microsoft PowerPoint")


def powerpoint_ready():
    """Launch PowerPoint in the background if needed and wait until it answers."""
    subprocess.run(["open", "-g", "-a", "Microsoft PowerPoint"])
    for _ in range(90):
        try:
            r = subprocess.run(["osascript", "-e", 'tell application "Microsoft PowerPoint" to get version'], capture_output=True, text=True, timeout=20)
            if r.returncode == 0:
                return True
        except subprocess.TimeoutExpired:
            pass
        time.sleep(1)
    return False


def to_pdf(pptx, pdf):
    if os.path.exists(pdf):
        os.remove(pdf)
    how = converter()
    if how == "powerpoint":
        script = os.path.join(BUILD, "export_pdf.applescript")
        with open(script, "w") as f:
            f.write(APPLESCRIPT)
        for attempt in (1, 2):
            if not powerpoint_ready():
                print("  PowerPoint did not start")
                break
            try:
                res = subprocess.run(["osascript", script, pptx, pdf], capture_output=True, text=True, timeout=EXPORT_TIMEOUT)
            except subprocess.TimeoutExpired:
                print(f"  PowerPoint did not finish in {EXPORT_TIMEOUT}s (a dialog is probably open); killing it and retrying" if attempt == 1 else "  PowerPoint stalled twice")
                subprocess.run(["pkill", "-9", "-x", "Microsoft PowerPoint"])
                continue
            if res.returncode == 0 and os.path.exists(pdf):
                return
            print("  PowerPoint export failed:", res.stderr.strip()[:300])
            if attempt == 1:
                print("  restarting PowerPoint and retrying")
                subprocess.run(["pkill", "-9", "-x", "Microsoft PowerPoint"])
                time.sleep(2)
        if shutil.which("soffice"):
            print("  falling back to LibreOffice")
            how = "soffice"
        else:
            sys.exit("could not export the PDF with PowerPoint; open deck.pptx by hand and check for a dialog, or install LibreOffice")
    if how == "soffice":
        env = dict(os.environ, SAL_USE_VCLPLUGIN="svp")
        profile = os.path.join(BUILD, "lo_profile")
        res = subprocess.run(["soffice", f"-env:UserInstallation=file://{profile}", "--headless", "--convert-to", "pdf", "--outdir", BUILD, pptx], capture_output=True, text=True, env=env, timeout=300)
        made = os.path.join(BUILD, os.path.splitext(os.path.basename(pptx))[0] + ".pdf")
        if res.returncode or not os.path.exists(made):
            sys.exit(f"soffice failed: {res.stderr.strip()[:300]}")
        if made != pdf:
            os.replace(made, pdf)


def npages(pdf):
    m = re.search(r"Pages:\s+(\d+)", run(["pdfinfo", pdf]))
    return int(m.group(1)) if m else 0


def bottom_ink(pgm_path):
    """True if any ink lies in the guard band above the footline."""
    with open(pgm_path, "rb") as f:
        data = f.read()
    parts, pos = [], 0
    while len(parts) < 4:
        m = re.compile(rb"\s*(#[^\n]*\n\s*)*(\S+)").match(data, pos)
        parts.append(m.group(2))
        pos = m.end()
    w, h = int(parts[1]), int(parts[2])
    pixels = data[pos + 1:]
    px_per_in = h / PAGE_IN
    lo = int(h - (FOOTLINE_IN + GUARD_IN) * px_per_in)
    hi = int(h - FOOTLINE_IN * px_per_in)
    for row in range(lo, hi):
        line = pixels[row * w:(row + 1) * w]
        if any(b < INK for b in line):
            return True
    return False


def package_ok(pptx):
    """Every part of the package parses as XML (our own output, so the stdlib parser is fine)."""
    from xml.dom import minidom
    bad = []
    with zipfile.ZipFile(pptx) as z:
        for name in z.namelist():
            if name.endswith(".xml") or name.endswith(".rels"):
                try:
                    minidom.parseString(z.read(name))
                except Exception as e:  # noqa: BLE001
                    bad.append(f"{name}: {e}")
    return bad


def main(argv):
    handout = "--handout" in argv
    only = {int(a) for a in argv if a.isdigit()}
    stem = "deck-handout" if handout else "deck"
    pptx = os.path.join(HERE, stem + ".pptx")
    if not os.path.exists(pptx):
        sys.exit("build the deck first: sh build.sh")
    for tool in ("pdftoppm", "pdfinfo"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found: brew install poppler (macOS) or apt install poppler-utils")
    os.makedirs(BUILD, exist_ok=True)
    manifest_path = os.path.join(BUILD, "manifest-handout.json" if handout else "manifest.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {"slides": []}
    by_page = {s["page"]: s for s in manifest.get("slides", [])}

    shots = SHOTS + ("-handout" if handout else "")
    if not only and os.path.isdir(shots):   # a full run starts clean; numbered runs replace only their own files
        shutil.rmtree(shots)
    os.makedirs(shots, exist_ok=True)

    pdf = os.path.join(BUILD, stem + ".pdf")
    print(f"exporting {stem}.pptx to PDF with {converter()}")
    to_pdf(pptx, pdf)
    n = npages(pdf)
    nframes = len({s["frame"] for s in manifest.get("slides", [])})
    print(f"{n} pages in {os.path.relpath(pdf, HERE)}" + (f", {nframes} frames" if nframes else ""))
    if by_page and n != len(by_page):
        print(f"  the manifest expects {len(by_page)} slides; rebuild (sh build.sh) so the listing matches")

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
        s = by_page.get(p, {})
        label = (f"A{s['frame'][1:]}" if str(s.get("frame", "")).startswith("A") else f"frame {s['frame']}") if s else ""
        stepinfo = f" step {s['step']}/{s['steps']}" if s and s.get("steps", 1) > 1 and not handout else ""
        flag = "   <- content reaches the footline" if touches else ""
        print(f"  {p:02d}.png  {label:9s}{stepinfo:10s} {s.get('title', '')[:56]}{flag}")
        if touches:
            overflow.append(p)

    print()
    log = os.path.join(BUILD, "build-log.txt")
    msgs = [l for l in open(log).read().splitlines() if l.strip()] if os.path.exists(log) else []
    bad = package_ok(pptx)
    if msgs or bad:
        print("build messages:")
        for m in msgs:
            print("  -", m[:220])
        for b in bad:
            print("  - package:", b[:220])
    else:
        print("no build messages")
    if overflow:
        print("pages whose content reaches the footline: " + ", ".join(f"{p:02d}" for p in overflow))
    else:
        print("no page reaches the footline")
    print(f"screenshots in {os.path.relpath(shots, HERE)}/")


if __name__ == "__main__":
    main(sys.argv[1:])
