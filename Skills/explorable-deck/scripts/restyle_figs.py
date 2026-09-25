#!/usr/bin/env python3
"""Recolour the converted source figures to the deck's palette.

Usage:
    python figs/restyle_figs.py            # every figs/*.svg
    python figs/restyle_figs.py Fig_Name   # named figures

convert_figs.sh turns the source's PDFs into SVG with their original colours.
This pass maps those colours onto the deck's tokens so the figures sit next to
the run-time charts without a palette change. The default MAP covers Stata's
scheme colours and the Okabe-Ito set: navy becomes ink, maroon and orange
become the primary colour, the blues become greys, and the plot background
becomes paper so the figure has no white box. Edit MAP for other sources; the
script lists every colour it left alone. Text drawn as paths is untouched, and
the mapping is idempotent.

Colour never marks a quantity that is not one of the deck's four semantic
colours, so nothing here is mapped onto contrast, actor-a or actor-b: a
figure that needs those is redrawn as a stage.
"""

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

# Keep the hex values on the right in step with theme/deck.scss.
MAP = {
    # matplotlib tab10 (first four) and ggplot2 default hues (first three)
    "#1f77b4": "#1C2224",  # tab:blue           -> ink
    "#ff7f0e": "#C4452A",  # tab:orange         -> primary
    "#2ca02c": "#4B5457",  # tab:green          -> ink-2
    "#d62728": "#C4452A",  # tab:red            -> primary
    "#f8766d": "#C4452A",  # ggplot hue 1       -> primary
    "#00ba38": "#4B5457",  # ggplot hue 2       -> ink-2
    "#619cff": "#667074",  # ggplot hue 3       -> ink-3
    "#ebebeb": "#FFFFFF",  # ggplot panel grey  -> paper
    # Stata schemes and Okabe-Ito
    "#1a476f": "#1C2224",  # Stata navy         -> ink
    "#90353b": "#C4452A",  # Stata maroon       -> primary
    "#f39189": "#C4452A",  # light red reference line -> primary
    "#d55e00": "#C4452A",  # Okabe-Ito orange   -> primary
    "#eaaf80": "#F2D9D2",  # its light fill     -> primary-soft
    "#0072b2": "#667074",  # Okabe-Ito blue     -> ink-3
    "#80b9d9": "#ECECEC",  # its light fill     -> paper-3
    "#a0a0a0": "#8A9195",  # Stata axis grey    -> a cooler grey
    "#000000": "#1C2224",  # black rules        -> ink
    "#1e2d53": "#1C2224",  # Stata dknavy       -> ink
    "#4b5775": "#4B5457",  # its lighter band   -> ink-2
    "#a65d62": "#C4452A",  # Stata dkred band   -> primary
    "#333333": "#1C2224",  # dark grey          -> ink
    "#b3b3b3": "#C9CEC6",  # light grey         -> line
    "#ffffff": "#FFFFFF",
    "#eaf2f3": "#FFFFFF",  # Stata plotregion tint -> paper, so the figure sits on the slide without a white box
    # Multi-series figures (Okabe-Ito green, sky blue, pink, orange) keep their
    # own colours: mapping several series onto one token would merge them.
}

# Colours that mark a second, third or fourth series in the source. They become
# distinct greys by default so the deck's four semantic colours keep their meaning
# (a multi-series figure whose greys cannot be told apart is redrawn as a stage).
# Pass --keep-series to leave them as the source drew them.
SERIES = {
    "#56b4e9": "#667074",  # Okabe-Ito sky blue     -> ink-3
    "#78c3ed": "#ECECEC",  # its light band         -> paper-3
    "#009e73": "#4B5457",  # Okabe-Ito green        -> ink-2
    "#33b18f": "#E2E5E3",  # its light band
    "#cc79a7": "#8A9195",  # Okabe-Ito pink         -> mid grey
    "#d694b9": "#ECECEC",  # its light band         -> paper-3
    "#e69f00": "#667074",  # Okabe-Ito orange       -> ink-3
    "#9467bd": "#8A9195",  # tab:purple
    "#8c564b": "#4B5457",  # tab:brown
}

ATTR = re.compile(r'(fill|stroke)="(#[0-9a-fA-F]{6}|rgb\([^)]*\))"')


def to_hex(color: str) -> str:
    """pdftocairo writes rgb(62.7%, 62.7%, 62.7%); pymupdf writes #a0a0a0. Normalise to hex."""
    if color.startswith("#"):
        return color.lower()
    parts = [float(x.strip().rstrip("%")) for x in color[4:-1].split(",")]
    return "#" + "".join(f"{round(v * 255 / 100):02x}" for v in parts)


def restyle(path: pathlib.Path, keep_series: bool = False) -> tuple[int, set]:
    table = MAP if keep_series else {**SERIES, **MAP}
    text = path.read_text()
    unmapped = set()
    n = 0

    def sub(m):
        nonlocal n
        key = to_hex(m.group(2))
        if key in table:
            n += 1
            return f'{m.group(1)}="{table[key]}"'
        if key.upper() not in {v.upper() for v in table.values()}:
            unmapped.add(key)
        return m.group(0)

    out = ATTR.sub(sub, text)
    if out != text:
        path.write_text(out)
    return n, unmapped


def main(only):
    keep = "--keep-series" in only
    only = {o for o in only if not o.startswith("--")}
    for path in sorted(HERE.glob("*.svg")):
        if only and path.stem not in only:
            continue
        n, unmapped = restyle(path, keep)
        flag = f"   unmapped: {', '.join(sorted(unmapped))}" if unmapped else ""
        print(f"  {n:>5} recoloured  {path.name}{flag}")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
