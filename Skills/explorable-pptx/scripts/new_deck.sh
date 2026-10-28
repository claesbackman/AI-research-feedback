#!/bin/sh
# Scaffold a new explorable PowerPoint deck from the skill's template.
#
# Usage:  sh ~/.claude/skills/explorable-pptx/scripts/new_deck.sh <path/to/deck>
#
# Copies assets/template/ (deck.js, build.js, build.sh, package.json, theme/,
# charts/, data/, figs/, README.md, plan.md, .gitignore) and the scripts
# (shoot.py, check_deck.py, figs/convert_figs.sh, figs/restyle_figs.py) into
# the target folder. Refuses to overwrite an existing deck.js.
set -e
SKILL=$(cd "$(dirname "$0")/.." && pwd)
DEST=$1
if [ -z "$DEST" ]; then echo "usage: new_deck.sh <path/to/deck>"; exit 1; fi
if [ -f "$DEST/deck.js" ]; then echo "$DEST/deck.js exists; not overwriting"; exit 1; fi
mkdir -p "$DEST"
cp -R "$SKILL/assets/template/." "$DEST/"
cp "$SKILL/scripts/shoot.py" "$SKILL/scripts/check_deck.py" "$DEST/"
cp "$SKILL/scripts/convert_figs.sh" "$SKILL/scripts/restyle_figs.py" "$DEST/figs/"
rm -rf "$DEST/_build" "$DEST/_shots" "$DEST/_shots-handout" "$DEST/node_modules" "$DEST/deck.pptx" "$DEST/deck-handout.pptx"
echo "deck scaffolded in $DEST"
echo "next: add topic aliases for the four colour tokens in deck.js, fill data/numbers.js,"
echo "      bring figures in with: sh figs/convert_figs.sh <source-dir> Name...,"
echo "      then: cd $DEST && sh build.sh && python3 shoot.py && python3 check_deck.py --minutes <N>"
