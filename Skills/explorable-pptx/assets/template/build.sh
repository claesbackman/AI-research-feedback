#!/bin/sh
# Build the deck with pptxgenjs:
#   deck.pptx           the talk, one slide per step
#   deck-handout.pptx   one slide per frame, finished states: the static read, for printing or sending
# plus _build/manifest.json and _build/build-log.txt for shoot.py and check_deck.py.
# Then: python3 shoot.py
# sh build.sh --fast builds deck.pptx only, for the edit-and-look loop.
# Installs pptxgenjs into node_modules/ the first time (needs node and npm).
set -e
cd "$(dirname "$0")"
if ! node -e "require('pptxgenjs')" >/dev/null 2>&1; then
  echo "installing pptxgenjs (once)"
  npm install --silent --no-audit --no-fund
fi
node build.js "$@"
