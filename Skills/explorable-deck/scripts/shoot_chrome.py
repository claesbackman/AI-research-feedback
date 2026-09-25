"""Screenshot every slide with headless Google Chrome, no playwright needed.

Usage:
    python shoot_chrome.py           # every slide, appendix included
    python shoot_chrome.py 4 5 6     # only these slides (1-based)

Writes PNGs to _shots/ (gitignored) and prints every console message the page
emitted, so a chart that failed to draw shows up as a line here. Slower than
shoot.py, which uses playwright and also measures overflow, but it needs only
the Chrome that is already installed. Set CHROME to point at another binary.

Charts are captured in their finished state (the deck's ?static switch), so an
animated build-in never leaves a half-drawn chart in a screenshot.

Headless Chrome's --window-size includes its own toolbar, so a 1280x720 window
gives a shorter layout viewport and Chrome then re-lays out for the capture,
which leaves SVG text at stale positions. The script measures that offset once
with a probe page and enlarges the window so the layout viewport is 1280x720.
"""

import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "index.html")
SHOTS = os.path.join(HERE, "_shots")
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
W, H = 1280, 720

BASE_FLAGS = ["--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
              "--enable-logging=stderr", "--v=0"]


def chrome(url, out, budget, height):
    cmd = [CHROME, *BASE_FLAGS, f"--virtual-time-budget={budget}", f"--window-size={W},{height}",
           f"--screenshot={out}", url]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return [re.sub(r"^\[[^\]]*\]\s*", "", l) for l in res.stderr.splitlines() if "CONSOLE" in l]


def viewport_offset():
    """How many pixels of window height headless Chrome spends on its own UI."""
    probe = os.path.join(SHOTS, "_probe.html")
    with open(probe, "w") as f:
        f.write("<script>console.log('VP ' + innerWidth + 'x' + innerHeight)</script>")
    for line in chrome("file://" + probe, os.path.join(SHOTS, "_probe.png"), 500, H):
        m = re.search(r"VP (\d+)x(\d+)", line)
        if m:
            return H - int(m.group(2))
    return 0


class SlideCounter(HTMLParser):
    """Counts top-level <section> elements inside .slides, which is what reveal indexes."""

    def __init__(self):
        super().__init__()
        self.depth = 0
        self.in_slides = False
        self.titles = []
        self._grab = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "div" and "slides" in (a.get("class") or "").split():
            self.in_slides = True
        if not self.in_slides:
            return
        if tag == "section":
            self.depth += 1
            if self.depth == 1:
                self.titles.append(a.get("id", ""))
        if tag in ("h1", "h2") and self.depth == 1:
            self._grab = True

    def handle_endtag(self, tag):
        if self.in_slides and tag == "section":
            self.depth -= 1
        if tag in ("h1", "h2"):
            self._grab = False

    def handle_data(self, data):
        if self._grab and data.strip() and self.titles:
            self.titles[-1] = data.strip()[:48]
            self._grab = False


def main(only):
    if not os.path.exists(INDEX):
        sys.exit("render the deck first: quarto render index.qmd")
    if not only and os.path.isdir(SHOTS):   # a full run starts clean; numbered runs replace only their own files
        shutil.rmtree(SHOTS)
    os.makedirs(SHOTS, exist_ok=True)

    offset = viewport_offset()
    height = H + offset
    print(f"headless Chrome spends {offset}px on its own UI, using a {W}x{height} window")

    parser = SlideCounter()
    parser.feed(open(INDEX, encoding="utf-8").read())
    titles = parser.titles
    print(f"{len(titles)} slides (appendix included)")

    problems = []
    for i, title in enumerate(titles):
        if only and (i + 1) not in only:
            continue
        name = f"{i + 1:02d}.png"
        console = chrome(f"file://{INDEX}?static#/{i}", os.path.join(SHOTS, name), 5000, height)
        console = [c for c in console if "reveal.js" not in c.lower()]  # reveal logs its version on start
        flag = f"   {len(console)} console message(s)" if console else ""
        print(f"  {name}  {title}{flag}")
        problems.extend(f"slide {i + 1} ({title}): {c}" for c in console)

    for f in ("_probe.html", "_probe.png"):
        try:
            os.remove(os.path.join(SHOTS, f))
        except OSError:
            pass

    if problems:
        print("\nconsole output:")
        for p in dict.fromkeys(problems):
            print("  -", p)
    else:
        print("\nno console output")


if __name__ == "__main__":
    main({int(a) for a in sys.argv[1:] if a.isdigit()})
