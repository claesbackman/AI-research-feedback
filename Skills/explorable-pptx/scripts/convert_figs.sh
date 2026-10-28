#!/bin/sh
# Bring the source's figures into the deck: copy, recolour the vector ones,
# then render them to PNG for PowerPoint.
#
# Usage:  sh figs/convert_figs.sh <source-dir> Name1 Name2 ...
#         sh figs/convert_figs.sh ../../Figures Fig_Income Gelbach_main
#
# Copies <source-dir>/<Name>.pdf (or .png / .jpg) to figs/ next to this
# script. A PDF is recoloured in place by restyle_figs.py (Ghostscript), which
# maps the source's plot colours onto the deck palette and turns the plot
# background into paper, and then rendered to figs/<Name>.png at 300 dpi with
# a transparent background (pdftocairo, poppler), which is what deck.js
# places: PowerPoint cannot show a PDF. Raster figures are copied unchanged.
# Re-run after regenerating any source figure. The PNGs are committed with
# the deck so it builds on a machine without poppler or Ghostscript.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$1; shift
if [ -z "$SRC" ] || [ $# -eq 0 ]; then echo "usage: convert_figs.sh <source-dir> Name..."; exit 1; fi
missing=""; vector=""
for n in "$@"; do
  found=""
  for ext in pdf png jpg jpeg; do
    if [ -f "$SRC/$n.$ext" ]; then cp "$SRC/$n.$ext" "$HERE/$n.$ext"; echo "  $n.$ext"; found=1; [ "$ext" = pdf ] && vector="$vector $n"; break; fi
  done
  [ -z "$found" ] && missing="$missing $n"
done
if [ -n "$vector" ]; then
  if command -v gs >/dev/null 2>&1; then echo "source colours:"; python3 "$HERE/restyle_figs.py" --dry-run $vector; python3 "$HERE/restyle_figs.py" $vector; else echo "gs not found: figures copied but not recoloured (brew install ghostscript)"; fi
  if command -v pdftocairo >/dev/null 2>&1; then
    for n in $vector; do pdftocairo -png -transp -r 300 -singlefile "$HERE/$n.pdf" "$HERE/$n" && echo "  $n.png"; done
  else echo "pdftocairo not found: PDFs not rendered to PNG (brew install poppler)"; exit 1; fi
fi
[ -n "$missing" ] && echo "not found in $SRC:$missing" && exit 1
exit 0
