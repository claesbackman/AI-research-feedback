# beamer and TikZ notes

The technical side of the template in `assets/template/`: what the theme gives you, how a stage is written, how figures get in, how to build and check, and the traps. beamer with lualatex, pgfplots 1.16 or later, TeX Live 2019 or later.

## Contents

1. Files and how they connect
2. The preamble
3. Slide vocabulary (what the theme defines)
4. Stages: charts drawn at compile time
5. Figures from the source
6. Speaker notes, links, overlays, appendix
7. Build, screenshot, lint, present
8. Traps

## 1. Files and how they connect

`deck.tex` is the deck. It loads `theme/explorable.sty` (the look and the vocabulary) and `data/numbers.tex` (every number). A frame asks for a chart by inputting it into a stage:

```latex
\begin{stage}
\input{charts/ladder}
\end{stage}
```

and `charts/ladder.tex` draws it with pgfplots, reading its numbers from the keys and tables that `numbers.tex` defined. `build.sh` compiles three PDFs into `_build/` and copies `deck.pdf` and `deck-handout.pdf` next to `deck.tex`. `shoot.py` turns every page into a PNG and checks the log and the page edges; `check_deck.py` lints the source.

## 2. The preamble

`\documentclass[aspectratio=169, 10pt]{beamer}` then `\usepackage{theme/explorable}` and `\input{data/numbers}`. Change the title block; leave the class options. The theme sets the fonts (Fira Sans for titles and labels, Libertinus Serif for body text, IBM Plex Mono for numbers, all from TeX Live, with Helvetica Neue, Georgia and Menlo as fallbacks), the colours, the frame title, the footline with its progress bar, and the title page. When the deck cites, uncomment the biblatex lines and copy the `.bib` next to `deck.tex`.

The colour tokens are generic on purpose. Give each one a topic alias in `deck.tex` (`\colorlet{gain}{primary}`, one line per token) and paint charts with the alias. The generic names stay, because `\primaryt`, `\stat[contrast]`, `\begin{panel}[actora]` and this document depend on them.

## 3. Slide vocabulary

Every frame starts with `\begin{frame}{Title as an assertion}`. Below it, combine these. Body text is 9 pt on a 160 mm frame, which reads well at projector scale.

Layouts:

| environment / command | what it does |
|---|---|
| `\begin{beside} … \nextcol … \end{beside}` | prose (36 %) beside a stage or figure (60 %); `[c]` centres the columns vertically |
| `\begin{wideleft} … \nextcol … \end{wideleft}` | figure left (60 %), prose right (36 %) |
| `\begin{even} … \nextcol … \end{even}` | two equal columns |
| `\begin{cols} … \nextcol … \end{cols}` | two equal columns with a hairline between, for a contrast; `\setlength{\colsrule}{…}` sets the hairline's height (0.4 of the text height by default) |
| `\begin{prose} … \end{prose}` | body text; wraps the text in any layout |
| `\begin{stage} … \end{stage}` | a fixed box (50 mm) a chart fills; `[tall]` 56 mm, `[short]` 42 mm under prose |
| `\fig{figs/name.pdf}` / `\fig[tall]{…}` | a centred figure 48 mm tall (56 mm); `\figpair{a}{b}` two at 40 mm |
| `\begin{claims} \claim{Lead.}{text} … \end{claims}` | numbered claims (literature, conclusion) |
| `\begin{stats}[3] \stat{0.017}{label} … \end{stats}` | stat cards; `\stat[contrast]{…}{…}` colours the number (`primary`, `actora`, `actorb`, `ink2`) |
| `\bignum{number}{label}` | one large number with a label, for a calculator-style stage |
| `\begin{panel}[actora] … \end{panel}` | a card on paper-2 with a coloured left edge |
| `\begin{decktable} \begin{tabular}… \end{decktable}` | a booktabs table in the display face at a small size |
| `\divider[Section 1]{Claim}` | a section divider frame (also a `\section` for the PDF outline) |
| `\assertion{One sentence}` | a single large assertion, no figure |
| `\titlepage` inside `\begin{frame}[plain]` | the title frame |

Inline roles: `\q{text}` a display-face question or claim; `\source{text}` a source line; `\figcap{text}` a centred caption under a figure; `\stagecap{text}` a caption inside a stage; `\eyebrow{text}` small caps above a title; `\num{0.017}` a mono number; `\primaryt{}` `\contrastt{}` `\actorat{}` `\actorbt{}` coloured emphasis; `\colhead{Heading}` a column heading with a rule; `\ph{Heading}` a small heading anywhere in a frame; `\muted{}`; `\aside{}` an aside with a left rule; `\kbd{S}` a key cap; `\swatch{primary}` a colour chip; `\legend{…}` a centred legend row.

Numbers: `\D{path}` prints a scalar from `numbers.tex`, `\D[2]{path}` rounds it to two decimals (zero-filled), `\Dv{path}` expands to it inside TikZ and pgfmath, `\Dt{\table}{row}{col}` prints a cell of a CSV table (`\Dt[3]{\ladder}{0}{beta}`). `\Dt` is not expandable, so it cannot sit inside a coordinate or a pgfmath expression; in a chart, copy the cell into a macro first with `\Dtlet{\seA}{\ladder}{0}{se}` and use `\seA`. An undefined key prints `??` in the primary colour and writes `DATA: undefined key` to the log, which `shoot.py` reports. Numbers are printed as text in the current face with a real minus sign, whether rounded or not, so a stat card's number is in the display face.

Frame options: `[plain]` for dividers and the title; `[label=name]` for any frame a `\goto` points at; `<1-3>` on a frame with a stepped stage.

## 4. Stages: charts drawn at compile time

A stage is a fixed box (50 mm tall, `[tall]` 56 mm, `[short]` 42 mm) that a chart fills. Fixed height matters: the box must not change size with what loads into it or between overlay steps, or the slide reflows on stage.

Write a chart in `charts/<name>.tex`:

```latex
\begin{tikzpicture}
\begin{axis}[deckaxis, width=\chartwidth, height=\chartheight,
  xmin=…, xmax=…, ymin=…, ymax=…, xlabel={…}, ylabel={…}]
\addplot[primary] table[x=x, y=y] {\mytable};
\addplot[fill=actora, draw=none, visible on=<2->] coordinates {…};
\node[card] at (axis cs:…) {…};
\end{axis}
\end{tikzpicture}
\stagecap{What this shows. Measured or stylised, and from where.}
```

`deckaxis` sets grey axes and ticks, display-face labels at 6.5 pt, no box, a soft horizontal grid, lines heavy enough for the back row, fixed-notation ticks, and `clip=false`. `\chartwidth` (80 mm) and `\chartheight` (42 mm) fit the `beside` layout; set `width=` and `height=` per chart for other layouts. Node styles: `card` (a following card; an `overlay` node, so it never widens the picture when it hangs outside the axis), `handle` (the handle on a line), `datalabel` (a bold label on a bar), `mech box` and `mech arrow` for mechanism diagrams. Set explicit `xmin … ymax` on every stepped chart, so the axes never move between steps, and keep a card inside the axis at every step so it does not cover a tick label.

Overlays inside a chart. The theme defines `visible on=<spec>` for any TikZ or pgfplots element: it keeps its space and turns invisible, so nothing shifts. `\addplot[visible on=<2->]` is a build-in; `\node[visible on=<2>]` a label that appears on one step. A frame whose only overlay is a `visible on` needs no overlay spec of its own: beamer counts the steps.

Stepped stages. A stage that moves something across steps (a handle along a line, a toggle between two states) declares `\stagesteps{3}` at the top of the chart and reads `\step`, which is 1, 2, 3 on the three overlays. Its frame carries `\begin{frame}<1-3>{…}`. In handout mode beamer shows every overlay at once, so `\step` returns the last step there and the printed deck shows the finished state. Never hide a stage's finished state behind `\only<1>`: the handout would show it anyway, on top of the rest.

Numbers come from `numbers.tex`: `\Dv{line/b}` inside a pgfmath expression or a coordinate, `\pgfmathsetmacro{\x}{\Dv{line/stops/\step}}` for a computed value, `\Dtlet{\seA}{\ladder}{0}{se}` to pull one cell of a table into a macro, `\addplot table {\ladder}` for a series. `\Dt` itself is for prose only. `\pgfplotstableread[col sep=comma]{data/ladder.csv}\ladder` in `numbers.tex` loads a CSV.

The template's three charts show the patterns most decks need: `stack-reveal` (a two-part bar that builds in after a bet, with hatched second components), `line-handle` (a line with a handle at three stops and a following card), `ladder` (a coefficient plot with intervals, grey where `sig = 0` in the CSV, drawn as two filtered plots from one table). Rewrite them for the topic or delete them.

## 5. Figures from the source

beamer includes PDF figures as they are, so there is no format conversion:

```sh
sh figs/convert_figs.sh ../../Figures Fig_A Fig_B     # copy, then recolour
```

`convert_figs.sh` copies `<source-dir>/<Name>.pdf` (or `.png`, `.jpg`) into `figs/` and runs `restyle_figs.py` on the PDFs, which maps the source's plot colours onto the deck tokens and turns the plot-region tint into paper so the figure sits on the slide without a box. The script needs Ghostscript (`gs`) and nothing else: it rewrites the PDF with uncompressed streams, replaces the colour operators, and rebuilds the file. The `MAP` at the top covers Stata's scheme colours, the Okabe-Ito set, matplotlib's tab10 and ggplot2's default hues. `convert_figs.sh` prints each figure's source colours before it recolours; `--dry-run` on `restyle_figs.py` lists the colours as they are now, and the script lists every colour it left alone. The first series of each palette (Stata navy, tab:blue, ggplot hue 1) becomes ink or primary; later series become greys. Colours that mark a second, third or fourth series become distinct greys (`SERIES`) so the deck's four colours keep their meaning; `--keep-series` leaves them. A multi-series figure whose greys cannot be told apart is redrawn as a stage. Keep the hex values in step with `theme/explorable.sty` if the palette changes.

Place a figure with `\fig{figs/name.pdf}`: the theme sets the height and lets the width follow, capped at the column width. The recoloured PDFs are committed with the deck (the template `.gitignore` does not exclude `figs/`) so it builds on a machine without Ghostscript.

## 6. Speaker notes, links, overlays, appendix

Notes: `\note{…}` at the end of the frame, after the content. `build.sh` makes `_build/deck-notes.pdf` with the slide on the left and the note on the right, for `pdfpc --notes=right`.

Links between frames: give the target `[label=name]` and write `\goto{name}{why?}` next to the thing that raises the question; the room carries `\back{origin}`. Both are hyperref links, so they work in every PDF viewer.

Math in prose: `$S^A$` and `$\lambda$` set in Libertinus Math. Prose numbers go through `\D`, which prints as text.

Overlays in prose: `\visible<2->{…}` or `\pause`. Use them only where the appearing thing is the argument's turn. `\only<1>{…}` is not for the deck: the handout shows it anyway.

Appendix: `\appendix` then `\divider{Appendix}` then the rooms. Frames after `\appendix` are numbered A1, A2, … in the footline and leave the progress bar, so the count ends at the closing frame. `appendixnumberbeamer` handles the frame counter.

## 7. Build, screenshot, lint, present

```sh
sh build.sh                        # _build/deck.pdf, deck-handout.pdf, deck-notes.pdf; deck.pdf copied out
sh build.sh --fast                 # deck.pdf only, about a third of the time; handout and notes go stale
python3 shoot.py                   # every page → _shots/NN.png, page → frame map, log messages, overflow
python3 shoot.py 3 4 12            # pages by number; the other screenshots are kept
python3 shoot.py --handout         # the handout instead: one page per frame → _shots-handout/
python3 check_deck.py --minutes 20 # lint deck.tex; the counts against the length table are printed as notes
```

`shoot.py` needs only poppler (`pdftoppm`, `pdftotext`, `pdfinfo`). It prints, for every page, the frame and overlay step it belongs to (from beamer's `.nav` file) and the title read from the page itself, then every error and warning from the log (compile errors, undefined keys, missing characters, overfull boxes, pgfkeys errors inside a chart), then every page with ink in the empty band above the footline, which is how a frame that is too tall shows up. Screenshots are numbered by page: the title page is 01 and a step is its own page. The plan, the notes and the reviews use frame numbers, as the footline does, and the listing maps one to the other. Look at every screenshot.

Present: `deck.pdf` full screen in any PDF viewer, arrow keys to step. Notes on a second screen: `pdfpc --notes=right _build/deck-notes.pdf`. Print or send: `deck-handout.pdf`, one page per frame with every stage finished.

## 8. Traps

- **`split` is taken.** amsmath, which beamer loads, owns `\begin{split}`; the layout is `beside`. The lint flags the other.
- **`\only<1>` in a stage.** Handout mode shows every overlay at once, so a state hidden with `\only` reappears in the printed deck, on top of the others. Use `visible on` for build-ins and `\step` for moving parts.
- **An element removed between steps.** `\only` gives its space back and pgfplots re-fits the axis. `visible on` keeps the space. Set explicit axis limits on every stepped chart anyway.
- **Node styles and axis styles live on different key paths.** `card`, `handle`, `datalabel` are `\tikzset` styles and work on nodes inside an axis; `deckaxis` is a `\pgfplotsset` style and goes in the axis options. A style on the wrong path gives "I do not know the key", which the log check reports.
- **Numbers are text.** `\D`, `\Dt` and tick labels print in the current face with a real minus. They are always fixed notation; an axis that needs `10^6` is an axis that should be rescaled by hand (thousands, millions) and labelled.
- **Fixed stage height.** Never let a stage size itself from its content. If a chart needs more room, use `[tall]` or move the prose above it with `[short]`.
- **Overflow is quiet.** A frame that runs off the page compiles, with at most an `Overfull \vbox` line in the log. `shoot.py` names the page; read its last lines.
- **`\section` inside a frame** or any sectioning command in a frame body breaks the outline. `\divider` issues the section.
- **Frame options with a bracket in the title** (`\begin{frame}{A [bracketed] title}`) need the title in braces as shown; beamer reads `[…]` first as options.
- **hyperref and the author line.** Spacing commands (`\;`, `\,`) in `\author` or `\title` produce "Token not allowed" warnings; use `~` or `\texorpdfstring`.
- **`\pause` in a column** pauses the whole frame from that point, including the other column. Prefer `visible on` inside the stage.
- **Fonts.** The theme loads Fira Sans, Libertinus Serif, IBM Plex Mono and Libertinus Math by file name from TeX Live. A TeX install without them falls back to the system faces named in the theme, in different metrics; the log then shows a fontspec warning and the screenshots need a second look.
- **Negative coefficients.** The ladder chart handles either sign and reads `sig` from the CSV to grey a row; do not derive significance from rounded standard errors.
- **Git.** `_build/` and `_shots/` are build output (the template `.gitignore` covers them). `deck.pdf` and `deck-handout.pdf` may be committed when the deck is shared as a file.
