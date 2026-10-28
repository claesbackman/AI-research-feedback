# PowerPoint and pptxgenjs notes

The technical side of the template in `assets/template/`: what the theme gives you, how a stage is written, how figures get in, how to build and check, and the traps. pptxgenjs 4 on Node 18 or later; PowerPoint 2016 or later, Keynote or LibreOffice to show the result.

## Contents

1. Files and how they connect
2. The deck file
3. Slide vocabulary (what the layouts define)
4. Stages: charts drawn at build time
5. Figures from the source
6. Speaker notes, links, steps, appendix
7. Build, screenshot, lint, present
8. Traps

## 1. Files and how they connect

`deck.js` is the deck: a `meta` block, the colour `aliases`, and `frames`, one object per frame. `build.js` reads it with `theme/theme.js` (tokens, faces, sizes, geometry), `theme/lib.js` (the drawing helpers and the markup parser), `theme/layouts.js` (how each frame kind becomes a slide), `data/numbers.js` (every number) and `charts/*.js` (the stages), and writes `deck.pptx` with pptxgenjs. A frame asks for a chart by name:

```js
{ title: 'Adding controls removes most of the slope', layout: 'beside',
  prose: 'Controls are cumulative down the rows.', stage: 'ladder',
  source: 'Coefficient on X with 95 percent intervals.', notes: 'Read the rows top to bottom.' }
```

and `charts/ladder.js` draws it with the library, reading its numbers from `D` (the object `numbers.js` exports). The build also writes `_build/manifest.json` (every slide's frame, step and title) and `_build/build-log.txt` (every warning), which `shoot.py` and `check_deck.py` read. `build.sh` installs pptxgenjs into `node_modules/` the first time and runs the build.

## 2. The deck file

`meta` carries the title block (`title`, `subtitle` as the eyebrow, `authors`, `institute`, `date`). `aliases` gives each of the four colour tokens a name in the topic's words (`{ gain: 'primary', yield: 'contrast', anna: 'actora', bo: 'actorb' }`); charts and prose use the aliases, and the generic names stay, because the layouts, the stat-card colours and this document depend on them.

`frames` is the talk in order. A frame with `kind` is a plain frame: `title` (the title slide, from `meta`), `divider` (an `eyebrow` and a `title`), `assertion` (one large sentence), `appendix` (the marker after which frames are rooms). Every other frame has a `title` written as an assertion, a `layout`, the fields that layout fills, and `notes`.

Prose is written in a small markup, parsed by `lib.js`:

| markup | what it does |
|---|---|
| a blank line | a new paragraph |
| `**text**`, `*text*`, `` `text` `` | bold, italic, the mono face |
| `[text]{primary}` `{contrast}` `{actora}` `{actorb}`, or an alias | coloured bold emphasis |
| `[text]{muted}`, `[0.017]{num}` | grey; the mono face for a number |
| `{{reveal.gap}}`, `{{ladder.0.beta:3}}` | a number from `numbers.js`, with `:d` decimals; printed with a real minus sign |
| `[why?](#label)` | a link to the frame with that `label`, followed by an arrow |
| `[text](https://…)` | an external link |

Markup nests (`[{{reveal.gap}} points]{primary}` works). A `{{key}}` that `numbers.js` does not define prints `??` in the primary colour and writes `DATA: undefined key` to the build log.

## 3. Slide vocabulary

Every content frame starts with its title at the top left in the display face. Below it, the layout places the slots. Body text is 14 pt on a 10 in frame, which reads well at projector scale.

| layout | fields | what it does |
|---|---|---|
| `prose` | `prose`, `q`, `stats`, `source` | body text; `q` a display-face question under it; `wide: true` lets it use the full width |
| `beside` | `prose` + `stage` or `fig`, `source`, `stats`, `aside` | prose (36 %) beside a stage or figure (60 %); the prose is centred vertically unless it carries stats, or `center: false` |
| `wideleft` | `fig` or `stage` + `prose`, `source`, `stats` | figure left (60 %), prose right (36 %) |
| `stack` | `prose`, `stage` or `fig`, `source` | prose above a short stage |
| `fig` | `fig` or `stage`, `figcap`, `source` | one figure full width with a caption; `tall: true` for a taller one |
| `figpair` | `figs: [a, b]`, `figcap` | two figures side by side |
| `even` | `left`, `right` | two equal columns, each a slot `{head, prose, fig, stage, source}` |
| `cols` | `left`, `right`, `q`, `rule` | the same with a hairline between, for a contrast; `q` under the columns; `rule` the hairline's height in inches |
| `claims` | `claims: [[lead, text], …]` | numbered claims (literature, conclusion); an empty lead gives a plain number |
| `stats` | `stats: [{k, l, color}]`, `prose` | stat cards across the frame: `k` the number, `l` the label, `color` a token or alias |
| `bignum` | `k`, `l`, `prose`, `color` | one large number with a label, for a calculator-style frame |

Common fields: `notes` (the speaker note), `label` (a link target), `source` (a line, or an array of lines for the closing frame), `back` (the label a room returns to), `eyebrow` (small caps above the title), `tall` (a taller stage or figure), `steps` (overrides the chart's step count).

The slot in a column takes `head` (a column heading with a rule), then one of `prose`, `fig` or `stage`, plus `source` at the bottom of the column, `stats` under the prose, and `aside` (a short note with a rule at its left).

## 4. Stages: charts drawn at build time

A stage is a fixed box a chart fills: 3.3 in tall beside prose (`tall` 3.55 in, 2.4 in under prose in `stack`). Fixed height matters: the box must not change size between steps, or the frame reflows on stage.

Write a chart in `charts/<name>.js`:

```js
module.exports = {
  steps: 3,                                    // slides this stage produces; 1 for a static chart
  draw({ slide, box, L, T, D, step, steps, handout, log }) {
    const area = L.chartArea(box, { legend: false });          // what is left after the caption (and a legend)
    const c = L.chart(slide, area, { xd: [0, 100], yd: [0, 12], m: { l: 0.55, r: 0.2, t: 0.3, b: 0.42 } });
    L.axisY(c, L.ticks(0, 12, 4), (v) => String(v), 'y label');
    L.axisX(c, L.ticks(0, 100, 20), (v) => String(v), 'x label');
    L.path(c, [[0, 2], [100, 9]], { color: 'primary', width: 2 });     // c.x(v), c.y(v) map data to inches
    L.dot(slide, c.x(50), c.y(5.5), 0.07, { fill: 'primary', line: 'paper', width: 1.5 });
    L.card(slide, [{ text: 'at 50: ', options: {} }, { text: '5.5', options: { bold: true } }], c.x(50), c.y(5.5), { w: 1.2, keepIn: c.p });
    L.stagecap(slide, box, 'What this shows. Measured or stylised, and from where.');
  },
};
```

The library, all positions in inches: `L.chart`, `L.axisX`, `L.axisY`, `L.ticks`, `L.niceStep`, `L.path`; shapes `L.line` (any direction; `dash: 'dash'`), `L.rect`, `L.rrect`, `L.dot`, `L.hatchRect` (the second visual channel: a soft fill with diagonal strokes clipped to the box), `L.card` (a following card, `anchor: 'above' | 'right' | 'left' | 'below'`, `keepIn` a box it must stay inside), `L.handle`, `L.swatch`; text `L.label` (one line, exact placement: `face`, `size`, `color`, `bold`, `align`, `rotate`), `L.text` (wrapped markup in a box with a role), `L.dataLabel` (a bold label over a bar), `L.legend(slide, box, [{label, color, hatched}])`, `L.stagecap`; numbers `L.fmtNum(x, d)` (real minus), `L.fmtPct`, `L.fmtInt`, `L.num(path, d)`, `L.get(path)`; `L.rng(seed)` and `L.randn` for stylised dots that are identical on every build; `L.col(name)` resolves a token or alias to hex. Colours are passed as names (`'primary'`, `'ink3'`, an alias); hex is accepted without `#`.

Steps. The module's `steps` is how many slides the frame produces; `draw` is called once per step with `step` = 1 … `steps`, and in the handout once with `step = steps`. Draw every step from the same data domains into the same box (set `xd` and `yd` from the full data, not from what the step shows) so nothing moves but the thing that changes. A build-in is `steps: 2` with the second component drawn when `step >= 2`; a handle is `steps: 3` with its position read from `stops[step − 1]`. The frame needs no `steps` of its own; it reads the chart's.

Numbers come from `D`: `D.reveal.cases`, `D.line.b`, `D.ladder` (an array of row objects from `table('ladder.csv')` in `numbers.js`). Anything stylised says so in the caption.

The template's three charts show the patterns most decks need: `stack-reveal` (a two-part bar that builds in after a bet, hatched second components), `line-handle` (a line with a handle at three stops and a following card), `ladder` (a coefficient plot with intervals, grey where `sig = 0` in the CSV). Rewrite them for the topic or delete them.

Native PowerPoint charts (`slide.addChart`) are available through pptxgenjs, and the user can edit their data in PowerPoint afterwards. They cannot draw error bars, hatching, a handle or a card, and their frame is PowerPoint's. Use one only for a plain bar or line the user has asked to be able to edit; everything else is drawn with the library, in the palette.

## 5. Figures from the source

PowerPoint cannot place a PDF, so every vector figure is copied, recoloured and rendered:

```sh
sh figs/convert_figs.sh ../../Figures Fig_A Fig_B     # copy, recolour the PDF, render figs/Fig_A.png
```

`convert_figs.sh` copies `<source-dir>/<Name>.pdf` (or `.png`, `.jpg`) into `figs/`, runs `restyle_figs.py` on the PDFs (Ghostscript: maps the source's plot colours onto the deck tokens and turns the plot-region tint into paper so the figure sits on the slide without a box), then renders each PDF to `figs/<Name>.png` at 300 dpi with a transparent background (`pdftocairo`). The `MAP` at the top of `restyle_figs.py` covers Stata's scheme colours, the Okabe-Ito set, matplotlib's tab10 and ggplot2's default hues; `convert_figs.sh` prints each figure's source colours before it recolours and the script lists every colour it left alone, so a figure drawn in a custom colour (this project's event-study blue, for instance) gets a line added to `MAP`. Colours that mark a second, third or fourth series become distinct greys (`SERIES`); `--keep-series` leaves them. A multi-series figure whose greys cannot be told apart is redrawn as a stage. Keep the hex values in step with `theme/theme.js` if the palette changes.

Place a figure with `fig: 'figs/Name.png'` in a `beside`, `wideleft`, `fig` or `stack` frame, or `figs: [a, b]` in `figpair`. The layout sets the height and lets the width follow, capped at the column width, reading the PNG's pixel size from its header. The PNGs are committed with the deck so it builds on a machine without poppler or Ghostscript.

## 6. Speaker notes, links, steps, appendix

Notes: `notes: '…'` on every frame becomes PowerPoint's speaker note on each of the frame's slides. Presenter view (⌥⌘P on a Mac, Alt+F5 on Windows) shows them on the second screen.

Links between frames: give the target `label: 'name'` and write `[why?](#name)` next to the thing that raises the question; the room carries `back: 'origin'`, which draws "← back to the talk" at the bottom left. Both are slide hyperlinks that work in PowerPoint, Keynote and the exported PDF. A link to a label no frame defines is logged and drawn in the primary colour so it is noticed.

Steps: a frame with a stepped stage becomes one slide per step, under the same frame number in the footline; the presenter advances through them with the usual key. Prose does not step; the thing that changes is in the stage. (PowerPoint's own click animations are not used: pptxgenjs cannot write them, one slide per step prints and exports correctly everywhere, and the handout build keeps the last step of each frame.)

Appendix: `{ kind: 'appendix' }` then a divider then the rooms. Frames after the marker are numbered A1, A2, … and leave the progress bar, so the count ends at the closing frame.

## 7. Build, screenshot, lint, present

```sh
sh build.sh                        # deck.pptx, deck-handout.pptx, _build/manifest.json, build-log.txt
sh build.sh --fast                 # deck.pptx only; the handout goes stale
python3 shoot.py                   # every slide → _shots/NN.png, the slide → frame map, build messages, overflow
python3 shoot.py 3 4 12            # slides by number; the other screenshots are kept
python3 shoot.py --handout         # the handout instead: one slide per frame → _shots-handout/
python3 check_deck.py --minutes 20 # lint; the counts against the length table are printed as notes
```

`shoot.py` exports the `.pptx` to PDF and rasterises it with poppler (`pdftoppm`, `pdfinfo`). On macOS with Microsoft PowerPoint installed it drives PowerPoint by AppleScript, so the screenshots are what the deck will look like: it launches PowerPoint in the background if needed and leaves it running, because a cold launch can take a minute while the export of a whole deck takes seconds; the first run may ask you to allow automation. Anywhere else, or with `PPTX2PDF=soffice`, it uses LibreOffice, which substitutes the faces with different metrics, so overflow and fit are approximate there. It prints, for every slide, the frame and step it belongs to and the frame's title (from the manifest), then every build message (undefined numbers, unknown charts, links to no label, prose the build estimates to overflow, a chart that threw), then every page with ink in the guard band above the footline, which is how a frame that is too tall shows up. Screenshots are numbered by slide: the title slide is 01 and a step is its own slide. The plan, the notes and the reviews use frame numbers, as the footline does, and the listing maps one to the other. Look at every screenshot.

`check_deck.py` reads the manifest and `deck.js`: a frame without notes, evidence without a source line, a title that is a label, a font size or face set in the deck, a link to no label, and everything in the build log; `--minutes` compares the counts to the length table.

Present: `deck.pptx` in PowerPoint's slideshow, arrow keys to step; presenter view for the notes. Keynote and Google Slides open it too (Keynote substitutes the faces). Print or send: `deck-handout.pptx`, one slide per frame with every stage finished, or export it to PDF from PowerPoint (`_build/deck-handout.pdf` after `shoot.py --handout`).

Validation: pptxgenjs writes a package PowerPoint opens as is. `shoot.py` checks that every part parses. If the pptx skill's `validate.py` is available in the session, run it on `deck.pptx` once before handing over; it reports the chart and slide faults PowerPoint refuses.

## 8. Traps

- **PowerPoint's cold launch.** The first export after PowerPoint starts can take a minute; later ones take seconds. `shoot.py` keeps PowerPoint running for that reason. Do not kill it between runs, and if an export stalls, a dialog is open in PowerPoint: look at the app.
- **Colour names must resolve.** pptxgenjs takes hex without `#` and corrupts the file on `#C4452A`; the library resolves every token and alias through `L.col`, so pass names, never hex with a hash, and never a name the theme does not know (it logs `COLOUR: unknown`).
- **A shape with `line: { width: 0 }` still draws a black outline.** `L.rect` draws no outline unless `line` is given a colour.
- **Overflow is quiet.** A text box whose content is taller than the box spills below it. The build logs an estimate; `shoot.py` names the page. Fix it with a second frame, never with a smaller size (which the lint rejects).
- **Arrows and symbols.** `→`, `←`, `≈`, `−` render in all four faces; `↗` falls back to an emoji face in Georgia, which is why links use `→`.
- **Fonts.** The four faces (Franklin Gothic Demi and Book, Georgia, Consolas) ship with Office on Windows and macOS. A deck opened in Keynote or LibreOffice is shown in substitutes; a deck sent to a machine without Office needs the handout PDF. To use Fira Sans, Libertinus Serif and IBM Plex Mono as the siblings do, install them on every machine the deck will be shown on and change `faces` in `theme/theme.js`.
- **Fixed stage height.** Never let a stage size itself from its content. If a chart needs more room, use `tall: true` or move the prose above it with `stack`.
- **Steps and the handout.** The handout calls `draw` with `step = steps`; a stage that draws its interesting state only on step 1 prints the wrong picture. The last step is the finished state.
- **A card near the edge.** Pass `keepIn: c.p` so a following card stays inside the plot area on every step instead of hanging off the stage.
- **Figures are PNG.** A figure edited after conversion must be re-run through `convert_figs.sh`; the PNG, not the PDF, is what the deck places.
- **Negative coefficients.** `ladder.js` handles either sign and reads `sig` from the CSV to grey a row; do not derive significance from rounded standard errors.
- **Numbers.** `data/numbers.js` for charts and prose alike. When a source number changes, grep `deck.js` for the old value.
- **Git.** `_build/`, `_shots/`, `_shots-handout/` and `node_modules/` are build output (the template `.gitignore` covers them). `deck.pptx` and `deck-handout.pptx` may be committed when the deck is shared as a file; `figs/*.png` are committed.
