#!/bin/sh
# Convert the source's PDF figures to SVG for the deck, then recolour them.
#
# Usage:  sh figs/convert_figs.sh <source-dir> Name1 Name2 ...
#         sh figs/convert_figs.sh ../../Figures Fig_Income Gelbach_main
#
# Writes figs/<Name>.svg next to this script. Text becomes glyph paths, so the
# deck does not depend on the fonts the figures were built with. Uses pdftocairo
# (poppler); with pymupdf instead: doc[0].get_svg_image(text_as_path=True).
# Re-run after regenerating any source figure. The SVGs are build output.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$1; shift
if [ -z "$SRC" ] || [ $# -eq 0 ]; then echo "usage: convert_figs.sh <source-dir> Name..."; exit 1; fi
if ! command -v pdftocairo >/dev/null 2>&1; then echo "pdftocairo not found: brew install poppler, or use pymupdf"; exit 1; fi
missing=""
for n in "$@"; do
  if [ -f "$SRC/$n.pdf" ]; then pdftocairo -svg "$SRC/$n.pdf" "$HERE/$n.svg"; echo "  $n.svg"; else missing="$missing $n"; fi
done
python3 "$HERE/restyle_figs.py" "$@" >/dev/null && echo "recoloured"
[ -n "$missing" ] && echo "not found in $SRC:$missing" && exit 1
exit 0
