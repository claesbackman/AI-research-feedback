# <Deck title>

A PowerPoint deck for *<source>*, about <N> minutes plus an appendix. Built
with pptxgenjs from `deck.js`; the four faces ship with Microsoft Office, so
the deck shows the same on any machine with PowerPoint and nothing has to be
installed or embedded.

```
deck.js                   the deck: one frame per idea, notes on every frame
plan.md                   the talk script the deck was built from
theme/theme.js            tokens, faces, sizes, geometry
theme/lib.js              the drawing helpers and the prose markup parser
theme/layouts.js          how each frame kind becomes a slide
data/numbers.js           the single home of every number a chart or a sentence uses
data/*.csv                series the charts plot, read by numbers.js
charts/*.js               the stages, drawn at build time as shapes in the palette
figs/convert_figs.sh      copies the source's figures in, recolours the PDFs, renders PNGs
figs/restyle_figs.py      maps the source's plot colours onto the deck palette (Ghostscript)
figs/*.png                the source's figures, recoloured; regenerate with convert_figs.sh, do not edit
build.js, build.sh        deck.pptx, deck-handout.pptx, _build/manifest.json
shoot.py                  one PNG per slide, the slide → frame map, build messages, overflow check
check_deck.py             lints the deck against the craft rules PowerPoint does not enforce
_build/, _shots/          build and screenshot output (gitignored), node_modules/ too
```

## Building and checking

```sh
sh build.sh                    # installs pptxgenjs the first time, then builds both decks
sh build.sh --fast             # deck.pptx only, while editing
python3 shoot.py               # _shots/NN.png for every slide, with its frame and step
python3 check_deck.py --minutes <N>
```

## Presenting

`deck.pptx` has one slide per step; PowerPoint's slideshow steps through it
with the arrow keys, and presenter view shows the notes on the second screen.
`deck-handout.pptx` has one slide per frame with every stage in its finished
state: that is the file to print or send (or `_build/deck-handout.pdf` after
`python3 shoot.py --handout`).

## Where the numbers come from

Charts and prose read `data/numbers.js` (<which tables>) and the CSV files
it loads. Change a number there and nowhere else.

## Stages

| frame | stage | the steps |
|---|---|---|
| | | |

## Conventions

- Four colours carry the argument, aliased in `deck.js`: **<alias>** = primary <hex>,
  **<alias>** = contrast <hex>, **<alias>** = actora <hex>, **<alias>** = actorb <hex>. Grey is everything else.
- Titles are assertions; read in sequence they are the talk.
- Frames after `{kind: 'appendix'}` are rooms, numbered A1, A2, …, and the progress bar ends on the closing frame.
- A stage is a fixed-height box; a stepped stage declares `steps` in its chart module and becomes one slide per step.
- No font size, face or fit mode in `deck.js`: what does not fit is a second frame.
