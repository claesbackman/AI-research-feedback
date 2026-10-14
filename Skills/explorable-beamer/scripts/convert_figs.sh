#!/bin/sh
# Bring the source's figures into the deck, then recolour the vector ones.
#
# Usage:  sh figs/convert_figs.sh <source-dir> Name1 Name2 ...
#         sh figs/convert_figs.sh ../../Figures Fig_Income Gelbach_main
#
# Copies <source-dir>/<Name>.pdf (or .png / .jpg) to figs/<Name>.<ext> next
# to this script. beamer includes PDF figures as they are, so there is no
# format conversion; restyle_figs.py then maps the PDF's plot colours onto
# the deck palette (needs Ghostscript). Raster figures are copied unchanged.
# Re-run after regenerating any source figure.
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
fi
[ -n "$missing" ] && echo "not found in $SRC:$missing" && exit 1
exit 0
