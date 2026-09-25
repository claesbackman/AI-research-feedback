#!/bin/sh
# Scaffold a new explorable deck from the skill's template.
#
# Usage:  sh ~/.claude/skills/explorable-deck/scripts/new_deck.sh <path/to/deck>
#
# Copies assets/template/ (index.qmd, theme/, js/, README.md, plan.md, .gitignore)
# and the scripts (shoot_chrome.py, shoot.py, figs/convert_figs.sh,
# figs/restyle_figs.py) into the target folder. Refuses to overwrite an
# existing index.qmd.
set -e
SKILL=$(cd "$(dirname "$0")/.." && pwd)
DEST=$1
if [ -z "$DEST" ]; then echo "usage: new_deck.sh <path/to/deck>"; exit 1; fi
if [ -f "$DEST/index.qmd" ]; then echo "$DEST/index.qmd exists; not overwriting"; exit 1; fi
mkdir -p "$DEST/figs" "$DEST/theme" "$DEST/js"
cp -R "$SKILL/assets/template/." "$DEST/"
cp "$SKILL/scripts/shoot_chrome.py" "$SKILL/scripts/shoot.py" "$DEST/"
cp "$SKILL/scripts/convert_figs.sh" "$SKILL/scripts/restyle_figs.py" "$DEST/figs/"
echo "deck scaffolded in $DEST"
echo "next: add topic aliases for the four colour tokens in theme/deck.scss, fill L.DATA in js/lib.js,"
echo "      convert figures with: sh figs/convert_figs.sh <source-dir> Name...,"
echo "      then: cd $DEST && quarto render index.qmd && python shoot_chrome.py"
