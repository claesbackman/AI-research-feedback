# Quarto and reveal.js notes

The technical side of the template in `assets/template/`: what the theme gives you, how a stage is written, how figures get in, how to render and check, and the traps. Quarto 1.10 with the built-in reveal.js.

## Contents

1. Files and how they connect
2. The YAML header
3. Slide vocabulary (classes the theme defines)
4. Stages: run-time charts
5. Figures from the source
6. Speaker notes, links, fragments, appendix
7. Render, preview, screenshot, export
8. Traps

## 1. Files and how they connect

`index.qmd` is the deck. Its header points at `theme/deck.scss` (the look), `theme/fonts.html` (injected into `<head>`), and `js/include.html` (appended after the body, loads `lib.js` then `deck-charts.js`). A slide asks for a chart with a raw HTML block:

```markdown
```{=html}
<div class="stage" data-chart="name"></div>
```
```

and `deck-charts.js` draws `CH['name']` into it once reveal is ready. `lib.js` holds the drawing helpers and `L.DATA`, the one object every chart reads its numbers from. `lib.js` exposes `window.LIB`; the charts alias it as `L`, so in the browser console type `LIB.DATA`.

## 2. The YAML header

The template header sets `width: 1280, height: 720, margin: 0.06`, `center: true`, `transition: fade`, `hash: true` (stable `#/slide-id` links), `slide-number: c/t` shown only in the speaker view, `auto-stretch: false` (so a lone image is sized by the theme, not stretched to the slide), and `html-math-method: katex`. Change the title block; leave the geometry. Add `bibliography: references.bib` and copy the `.bib` into the folder when the deck cites; then `@key` renders AER-style and a slide containing `::: {#refs}` collects the list.

## 3. Slide vocabulary

Every slide starts with `## Title as an assertion`. Below it, combine these containers. All font sizes in the theme are relative to a 30 px root, so `.prose` at 0.66em is about 20 px on the slide, which reads well at projector scale.

Layouts:

| container | what it does |
|---|---|
| `::: {.split}` | prose (400 px) beside a stage or figure |
| `::: {.split .wide-left}` | figure left, prose (400 px) right |
| `::: {.split .even}` | two equal columns |
| `::: {.split .even .cols}` | two columns with a hairline between, for a contrast |
| `::: {.split .center-v}` | vertically centre the two halves |
| `::: {.stack}` | prose above a stage |
| `::: {.prose}` | body text at slide size; wraps the text in any layout |
| `::: {.figwrap}` | centred figure, 440 px tall; `.tall` 500 px, `.pair` two figures at 370 px; `.raster` for a PNG or photo (no blend) |
| `::: {.claims}` | a bulleted list rendered as numbered claims (literature, conclusion) |
| `::: {.stats}` / `::: {.stat}` | stat cards: `[0.017]{.k}` the number, `[label]{.l}` under it; `.stats.two`, `.stats.col` |
| `::: {.panel}` | a bordered card; `.panel.actor-a` / `.actor-b` colour its edge, `.panel.quiet` no fill |
| `.two-up` / `.case` | two named cases side by side inside a stage, a glyph over a name (the hook screenshot) |
| `.bignum` | one large number with a `<small>` label, for a calculator-style stage |
| `.legend` | a chart legend row; `--c` sets the swatch colour, `.hatched` the hatched swatch |
| markdown table | renders in the display face at half size with hairlines |
| `::: {.notes}` | speaker notes |
| `[]{.data key="path" d="2"}` | an empty span filled at load from `L.DATA` (`path` like `specs.0.beta`, `d` decimals), so a prose number and its chart read one object |

Inline roles: `[text]{.q}` a display-face question or claim; `[text]{.source}` a source line; `[text]{.figcap}` a centred caption under a figure; `[text]{.eyebrow}` small caps above a title; `[0.017]{.num}` a tabular monospace number; `[text]{.primary-t}` `.contrast-t` `.actor-a-t` `.actor-b-t` coloured emphasis; `[Heading]{.colhead}` a column heading; `[Heading]{.ph}` a small heading anywhere in a slide; `[text]{.muted-t}`; `[text]{.note}` an aside with a left rule; `[key]{.kbd}` a key cap. Stat numbers take a colour suffix: `[4.5]{.k .c}` contrast, `.a` `.b` the actors, `.f` ink.

Colour tokens are generic on purpose. Give each one a topic alias in `deck.scss` (`--gain: var(--primary);` in the `:root` block, one line per token) and paint charts with the alias. The generic names stay, because `.primary-t`, `.stat .k.c`, `.panel.actor-a` and this table depend on them.

Slide attributes: `## Section title {.divider .center}` for a divider; `{visibility="uncounted"}` for appendix slides; `{visibility="hidden"}` to keep a slide in the file but out of the deck.

## 4. Stages: run-time charts

A stage is a fixed box (440 px tall, `.tall` 500 px, 380 px inside `.stack`) that a chart function fills. Fixed height matters: the box must not change size with what loads into it, or the slide reflows on stage.

Write a chart in `deck-charts.js`:

```js
CH['my-chart'] = (el, o) => {
  const c = L.chart(640, 380, { l: 58, r: 20, t: 30, b: 46 }, [xmin, xmax], [ymin, ymax]);
  L.axisY(c, ticks, fmt, 'y label'); L.axisX(c, ticks, fmt, 'x label');
  // draw into c.g with S('path'|'circle'|'rect'|'text', attrs); c.x(v) and c.y(v) map data to pixels
  el.append(wrap(c.svg), cap('What this shows. Measured or stylised, and from where.'));
  return cleanup;   // optional: remove window listeners, clear timers
};
```

Helpers in scope: `L.chart`, `L.axisX/Y`, `L.scale`, `L.linePath`, `L.slider`, `L.toggle`, `L.hatch`, `L.tween`, `L.rng/randn` (seeded, so stylised dots are stable), `L.fmtPct/fmtInt`, `S` (svg element), `E` (html element), `wrap` (the flex box a chart sits in), `cap` (a caption paragraph), `live(el, sel)` (find an element in the same slide, to write a running sentence into a `[]{.live-note}` span), `dragX(svg, onX)` (drag along x), `chip(text, pressed, onClick)` and `press(container, test)` for chip rows.

Behaviour the wiring provides: `data-animate` replays the chart with `o.animate = true` every time the slide is shown, `data-animate="once"` only the first time (so stepping back does not replay the payoff); `?static` on the URL, reveal's `?print-pdf`, and a reduced-motion setting all draw finished states; an unknown chart name prints itself in the stage and logs an error; a chart that throws prints "This chart failed to draw" and logs the error; pointer events inside a stage do not reach reveal's swipe handler; buttons blur after a click so the keyboard keeps driving the deck.

The template's example charts (`stack-reveal`, `line-handle`, `ladder`) show the three patterns most decks need: a two-part bar that builds in after a bet, a line with a draggable handle and a following card, and a coefficient plot with intervals. Rewrite them for the topic or delete them.

Controls: a slider row is `L.slider(label, min, max, value, step, fmt, id)` → `{row, input, out}`; a toggle is `L.toggle(label, checked, id)` → `{row, input}`; chips are buttons with `aria-pressed`. A single slider row goes straight into the stage; when a stage has several controls, group them in `E('div', {class: 'ctl'})`. Not `.controls`.

## 5. Figures from the source

Two kinds. Vector figures (PDF, SVG, from Stata, R, matplotlib) are converted and recoloured. Raster figures (PNG, JPG, TIFF: micrographs, screenshots, photos) go in as they are inside `::: {.figwrap .raster}`; if a raster figure carries the source's palette, crop it or redraw it as a stage.

reveal.js cannot show a PDF as an image, so every vector figure is converted to SVG:

```sh
sh figs/convert_figs.sh ../../Figures Fig_A Fig_B     # pdftocairo, then restyle
```

`convert_figs.sh` writes `figs/<name>.svg` with text as glyph paths (no font dependency) and runs `restyle_figs.py`, which maps the source's plot colours onto the deck tokens and turns the plot background into paper so the figure sits on the slide without a white box. The `MAP` at the top of `restyle_figs.py` covers Stata's scheme colours, the Okabe-Ito set, matplotlib's tab10 and ggplot2's default hues; extend it when the script lists a colour it left alone, and keep its hex values in step with `deck.scss` if the palette changes. Colours that mark a second, third or fourth series become distinct greys (`SERIES`), so the deck's four colours keep their meaning; `--keep-series` leaves them as the source drew them. A multi-series figure whose greys cannot be told apart is redrawn as a stage. Multi-series figures keep their series colours on purpose. If `pdftocairo` is missing, `pip install pymupdf` and use `page.get_svg_image(text_as_path=True)`.

Place a figure with `::: {.figwrap}` and `![](figs/name.svg)`. The theme sets the height and lets the width follow, and blends converted figures with the paper (`mix-blend-mode: multiply`) so a white plot box disappears. `.raster` switches the blend off, which a photo or a dark screenshot needs. The converted SVGs are committed with the deck so it renders on a machine without poppler.

## 6. Speaker notes, links, fragments, appendix

Notes: `::: {.notes}` at the end of the slide. Press **S** in the browser for the speaker view.

Links between slides: reveal gives each slide an id from its title (`hash: true`); `[why?](#slide-id)` jumps there and `[back](#origin-id)` returns. Write `#slide-id`, not `#/slide-id`: Quarto rewrites the anchor to `#/slide-id` itself, and a source `#/slide-id` renders as `#//slide-id`, which opens the title slide. Set ids explicitly with `## Title {#my-id}` rather than relying on the generated one.

Math in prose: `$S^A$` and `$\lambda$` render through KaTeX. A literal caret or `^` in prose is a caret on the slide.

Fragments: `::: {.fragment}` or `[text]{.fragment}` appear on the next keypress. Use them only where the appearing thing is the argument's turn.

Appendix: a divider `## Appendix {.divider .center visibility="uncounted"}` then every appendix slide with `{visibility="uncounted"}`. The progress bar and the slide count then end at the closing slide.

## 7. Render, preview, screenshot, export

```sh
quarto render index.qmd            # index.html + index_files/
quarto preview index.qmd           # live reload while editing
python shoot_chrome.py             # every slide → _shots/NN.png, prints console messages
python shoot_chrome.py 3 4 12      # slides by number; the other screenshots are kept
python shoot.py                    # playwright variant, also measures overflow (if installed)
```

`shoot_chrome.py` needs only the Chrome already installed (the macOS default path; set `CHROME=` to point elsewhere). It measures headless Chrome's toolbar height with a probe page and enlarges the window so the layout viewport is exactly 1280×720: with a mis-sized window Chrome re-lays out just before the capture and SVG text lands at stale positions in the PNG, a capture artefact that looks like a deck bug. It loads each slide with `?static`, so build-ins are captured finished.

Look at every screenshot. Overflow shows as content touching the bottom edge or clipped at the top, since `center: true` centres the overflowing block; a failed chart shows as an error line inside its stage; a console message names the slide.

Export: **E** in the browser opens the print view; print to PDF at 1280×720 (landscape, no margins). For a single emailable HTML file, `quarto render index.qmd -M embed-resources:true`; the scripts and SVGs inline cleanly, the fonts still come from the network and fall back to system faces without it.

## 8. Traps

- **Headings inside a slide.** Pandoc wraps a `###` in its own `<section>`, and reveal.js treats the slide as a vertical stack: the down arrow starts navigating inside it and the overview shows a column. Use `[Text]{.ph}` or `[Text]{.colhead}` spans for headings inside a slide.
- **`.controls`.** reveal.js uses this class for its navigation arrows and hides any other element with it. Control rows are `.ctl`.
- **Content before the first `##`.** Anything between the YAML header and the first slide title, an HTML comment included, becomes a blank untitled slide after the title slide. Put comments inside a slide.
- **Vertical stacks in general.** Do not use `---` separators or `#` level-one headings inside the deck body unless a stack is intended.
- **Math.** `html-math-method: katex` renders `$...$` without the MathJax CDN. If the deck must work with no network at all, hand-write the one formula as HTML in `.eq`.
- **Fonts.** The three faces load from Google Fonts. The theme names system fallbacks, so the deck presents offline, in different metrics. Check the screenshots once with the network off if the venue is uncertain.
- **Stage height.** Never let a stage size itself from its content. If a chart needs more room, use `.tall` or move it to `.stack`.
- **Animation on revisit.** `data-animate` replays on every entry; `data-animate="once"` plays the first time only. Use `once` for the payoff so stepping back during questions does not replay it.
- **Two dates on the title.** `date: today` in the header prints a date under the authors; if the subtitle already carries venue and month, leave `date` out.
- **The menu button.** Quarto's reveal menu draws a hamburger bottom-left on every slide and in every screenshot. `menu: false` in the YAML removes it; keep it if the presenter wants to jump by title during questions.
- **Negative coefficients.** `CH.ladder` handles either sign and reads `sig: false` from `L.DATA.specs` to grey a row; do not derive significance from rounded standard errors.
- **Cleanup.** A chart that adds a `window` listener or a timer returns a function that removes it; the wiring calls it before redrawing.
- **Numbers.** `L.DATA` for charts, the source's tables for prose. When a source number changes, grep the `.qmd` for the old value.
- **`quarto render` from another directory** resolves paths relative to the `.qmd`, so `figs/` and `js/` paths in the header and body stay relative.
- **Git.** `index_files/`, `.quarto/` and `_shots/` are build output (the template `.gitignore` covers them). `index.html` may be committed when the deck is shared as a file.
