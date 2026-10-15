# <Deck title>

A beamer deck for *<source>*, about <N> minutes plus an appendix. Built with
lualatex; the theme loads its faces from TeX Live, so it compiles on any
TeX Live without a network or a font install.

```
deck.tex                  the deck: one frame per idea, a \note on every frame
plan.md                   the talk script the deck was built from
theme/explorable.sty      tokens, faces, layouts, the stage, stat cards, chart styles
data/numbers.tex          the single home of every number a chart or a sentence uses
data/*.csv                series the charts plot, read by numbers.tex
charts/*.tex              the stages, drawn at compile time with pgfplots and TikZ
figs/convert_figs.sh      copies the source's figures in, then recolours the PDFs
figs/restyle_figs.py      maps the source's plot colours onto the deck palette (Ghostscript)
figs/*.pdf                the source's figures, recoloured; regenerate with convert_figs.sh, do not edit
build.sh                  deck.pdf, deck-handout.pdf, _build/deck-notes.pdf
shoot.py                  one PNG per page, the page → frame map, log messages, overflow check
check_deck.py             lints deck.tex against the craft rules beamer does not enforce
_build/, _shots/          build and screenshot output (gitignored)
```

## Building and checking

```sh
sh build.sh                    # three PDFs with latexmk (lualatex)
sh build.sh --fast             # deck.pdf only, while editing
python3 shoot.py               # _shots/NN.png for every page, with its frame and step
python3 check_deck.py --minutes <N>
```

## Presenting

`deck.pdf` has one page per overlay step; any PDF viewer in full-screen mode
steps through it with the arrow keys. For notes on a second screen use
`_build/deck-notes.pdf` with [pdfpc](https://pdfpc.github.io/)
(`pdfpc --notes=right _build/deck-notes.pdf`) or Skim's presentation mode.
`deck-handout.pdf` has one page per frame with every stage in its finished
state: that is the file to print or send.

## Where the numbers come from

Charts and prose read `data/numbers.tex` (<which tables>) and the CSV files
it loads. Change a number there and nowhere else.

## Stages

| frame | stage | the move |
|---|---|---|
| | | |

## Conventions

- Four colours carry the argument, aliased in `deck.tex`: **<alias>** = primary <hex>,
  **<alias>** = contrast <hex>, **<alias>** = actora <hex>, **<alias>** = actorb <hex>. Grey is everything else.
- Titles are assertions; read in sequence they are the talk.
- Frames after `\appendix` are rooms, numbered A1, A2, …, and the progress bar ends on the closing frame.
- A stage is a fixed-height box; a stepped stage declares `\stagesteps{N}` and its frame carries `<1-N>`.
- No font-size commands in a frame body, no `[shrink]`, no `[allowframebreaks]`: what does not fit is a second frame.
