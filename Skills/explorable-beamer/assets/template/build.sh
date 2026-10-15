#!/bin/sh
# Build the deck three ways with latexmk (lualatex), into _build/:
#   deck.pdf          the talk, overlays as separate pages
#   deck-handout.pdf  one page per frame, finished states: the static read, for printing
#   deck-notes.pdf    slide left, speaker note right, for pdfpc --notes=right
# Copies deck.pdf next to deck.tex. Then: python3 shoot.py
# sh build.sh --fast builds deck.pdf only, for the edit-and-look loop; the handout
# and notes go stale until the next full build, which comes before shoot.py --handout.
set -e
cd "$(dirname "$0")"
mkdir -p _build
LMK="latexmk -lualatex -interaction=nonstopmode -file-line-error -outdir=_build"
$LMK deck.tex
cp _build/deck.pdf deck.pdf
if [ "$1" = "--fast" ]; then
  echo "built deck.pdf (--fast: handout and notes not rebuilt)"
  exit 0
fi
$LMK -jobname=deck-handout -pdflualatex='lualatex %O "\PassOptionsToClass{handout}{beamer}\input{%S}"' deck.tex
$LMK -jobname=deck-notes   -pdflualatex='lualatex %O "\def\NOTES{}\input{%S}"' deck.tex
cp _build/deck-handout.pdf deck-handout.pdf
echo "built deck.pdf, deck-handout.pdf, _build/deck-notes.pdf"
