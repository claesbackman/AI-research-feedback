"""Screenshot every slide of the deck and report anything that does not fit.

Usage:
    python shoot.py           # every slide
    python shoot.py 4 5 6     # only these slides (1-based)

Requires playwright (pip install playwright && playwright install chromium).
shoot_chrome.py does the same with the installed Chrome and no extra dependency.

Writes PNGs to _shots/ (gitignored) and prints console errors plus any slide
whose content runs past the 1280x720 frame (or the footer, if the deck sets one).
"""

import os
import sys
import shutil

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = "file:///" + os.path.join(HERE, "index.html").replace("\\", "/")
SHOTS = os.path.join(HERE, "_shots")

W, H = 1280, 720


def main(only):
    if not only and os.path.isdir(SHOTS):
        shutil.rmtree(SHOTS)
    os.makedirs(SHOTS, exist_ok=True)

    problems = []
    with sync_playwright() as p:
        # Set PLAYWRIGHT_CHROMIUM_EXECUTABLE when the browser playwright wants
        # is not the one installed (a pinned build in CI, for instance).
        exe = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
        browser = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        page.on("console", lambda m: problems.append(f"console {m.type}: {m.text}")
                if m.type == "error" else None)
        page.on("pageerror", lambda e: problems.append(f"pageerror: {e}"))

        page.goto(INDEX)
        page.wait_for_timeout(1200)
        total = page.evaluate("Reveal.getTotalSlides()")
        print(f"{total} counted slides, plus any marked uncounted")

        page.evaluate("Reveal.slide(0, 0)")
        i = -1
        while True:
            i += 1
            if i:
                if page.evaluate("Reveal.isLastSlide()"):
                    break
                page.evaluate("Reveal.next()")
            page.wait_for_timeout(700)
            if only and (i + 1) not in only:
                continue
            title = page.evaluate(
                "() => { const s = Reveal.getCurrentSlide();"
                " const h = s && s.querySelector('h1,h2');"
                " return h ? h.textContent.trim().slice(0, 48) : '(title)'; }")
            # Reveal scales the stage, so measure in screen pixels against the
            # viewport rather than trusting scrollHeight on the section. The
            # floor is the footer, not the window: the footer is painted
            # outside the slide, so content that reaches it collides with it
            # while still sitting inside the viewport.
            over = page.evaluate(
                "() => { const s = Reveal.getCurrentSlide(); if (!s) return 0;"
                " let top = 1e9, bot = 0, left = 1e9, right = 0;"
                " for (const el of s.querySelectorAll('*')) {"
                "   if (el.offsetParent === null && el.tagName !== 'SECTION') continue;"
                "   const b = el.getBoundingClientRect();"
                "   if (b.height < 1) continue;"
                "   top = Math.min(top, b.top); bot = Math.max(bot, b.bottom);"
                "   left = Math.min(left, b.left); right = Math.max(right, b.right); }"
                " const f = document.querySelector('.reveal .footer');"
                " const fr = f ? f.getBoundingClientRect() : null;"
                " const floor = fr && fr.height ? fr.top : window.innerHeight;"
                " return Math.round(Math.max(0, bot - floor) + Math.max(0, -top)"
                "   + Math.max(0, right - window.innerWidth) + Math.max(0, -left)); }")
            name = f"{i + 1:02d}.png"
            page.screenshot(path=os.path.join(SHOTS, name))
            flag = f"   OVERFLOWS by {over}px" if over > 8 else ""
            print(f"  {name}  {title}{flag}")
            if over > 8:
                problems.append(f"slide {i + 1} ({title}) overflows by {over}px")

        browser.close()

    if problems:
        print("\nproblems:")
        for s in dict.fromkeys(problems):
            print("  -", s)
    else:
        print("\nno console errors, nothing overflows")


if __name__ == "__main__":
    main({int(a) for a in sys.argv[1:] if a.isdigit()})
