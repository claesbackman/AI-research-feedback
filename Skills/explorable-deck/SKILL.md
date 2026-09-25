---
name: explorable-deck
description: Build a Quarto reveal.js slide deck in the explorable-explanation style (Nicky Case) — one idea per slide, assertion titles, a concrete running example, run-time SVG stages the presenter drives live, the source's own figures recoloured into the deck palette, and an appendix of side rooms. Use for any request for a presentation, talk, slides, a seminar, conference, lecture, keynote or job-market deck, a Quarto or reveal.js deck, "turn this paper into slides", "a deck like the explorable", or for revising a deck built this way. Prefer it over .pptx skills unless the user names PowerPoint, Beamer, LaTeX or Google Slides. Not for a website explorable (that is explorable-explanations) or a poster.
---

# Explorable deck

Build a Quarto reveal.js deck that teaches the way a good explorable does, but inside the frame a talk imposes: linear, timed, driven by a presenter, 1280×720 with no scrolling. The explorable's non-linear tree becomes a spine of counted slides plus an appendix of side rooms. Its playables become stages the presenter operates while talking. Its "static read must work" becomes: the printed PDF must carry the argument on its own.

The sibling skill `explorable-explanations` builds the website version. This one produces a deck, and it reuses the website's models and numbers when one already exists for the topic.

## What you produce

One folder per deck, rendered with `quarto render index.qmd`:

```
<deck>/
  index.qmd            the deck: YAML header, one `##` per slide, `::: {.notes}` on every slide
  theme/deck.scss      tokens, faces, layouts, the stage, controls, figure frames
  theme/fonts.html     the three web fonts (system fallbacks in the theme)
  js/lib.js            drawing helpers and L.DATA, the single home of every number a chart uses
  js/deck-charts.js    the stages: CH['name'] = (el, {animate}) => cleanup
  js/include.html      the script tags Quarto appends to the body
  figs/*.svg           the source's figures, converted from PDF and recoloured (build output)
  figs/convert_figs.sh, figs/restyle_figs.py
  shoot_chrome.py      screenshots every slide, prints console messages
  README.md            how to render, check, present; where the numbers come from
  plan.md              the talk script (see below)
```

`scripts/new_deck.sh <path>` copies the template in `assets/template/` and the scripts into place. Start every new deck from it: the template already solves the reveal.js traps listed in the notes reference.

## Read first

1. [The Explorable Explanations Playbook](references/playbook.md): Nicky Case, Bret Victor, Steven Strogatz. Read §1–4 and §10 closely and skim the rest once per project. It explains why the craft rules exist so you can apply them with judgment. Its three-act arc, ladder of abstraction, empathy for the perplexed reader, and message → mechanics apply to a talk unchanged. Its §6 (interaction craft) and §9 (the frontier) describe the website; for a talk, the interaction section of `deck-craft.md` overrides them.
2. [Deck craft](references/deck-craft.md): how the explorable craft translates to slides, and what goes wrong. Read before planning, and again when reviewing.
3. [Quarto and reveal.js notes](references/quarto-reveal-notes.md): the template's layout vocabulary, the stage API, the figure pipeline, rendering, screenshots, PDF export, and the traps. Read before building.
4. Look at the four screenshots in [references/example-deck/](references/example-deck/) of a finished deck built this way (a hook with two characters, an animated reveal stage, a paper figure beside prose, a coefficient plot), and at Case's [Evolution of Trust](references/evolution-of-trust/) for the broader vibe. The example deck is a housing-returns paper (Bäckman, D'Lima and Khorunzhina, "Anna and Bo"); if the source is that paper or a neighbour of it, borrow nothing from the examples but the register. For any topic, take the register, not the content: the topic decides the colours, the characters and the shapes.

## Working rhythm

1. **Read the source.** The paper, notes, or codebase, and any existing explorable for the topic. If one exists, its `lib.js` data object and chart code are the deck's starting material: copy them rather than redrawing, so the two never disagree on a number.
2. **Fix the frame** before writing a slide: the audience (Strogatz's traumatized, perplexed or naturals, and which one the slide text is written for), the length in minutes, the venue. When the user has not said, assume a 20-minute conference talk for a mixed academic room, and say so. Length changes the shape, not just the count:

   | slot | counted slides | stages | build-ins | bets | literature slide |
   |---|---|---|---|---|---|
   | 12 min | 8–10 | 1 | 1 | 1 | no, one sentence on the hook |
   | 20 min | 13–16 | 2–3 | 1–2 | 1–2 | one slide |
   | 45+ min | 25–35 | 3–5 | 2 | one before each BUT | one slide, plus recap slides as cognitive gates |

   Everything a questioner might want goes in the appendix; in a long lecture the rooms move into the spine.
3. **Write `plan.md`** as a scriptwriter: the one big thing in a sentence, the cause → effect chain with its THEREFORE and BUT turns, then slide by slide what the room sees, what the presenter does with each stage, what they should notice, and which appendix room each question opens. Name the characters and the four semantic colours here.
4. **Scaffold** with `scripts/new_deck.sh`. Give each of the four colour tokens a topic alias in `theme/deck.scss` (`--gain: var(--primary);`) and paint the charts with the aliases; never rename the generic tokens, because the classes and the notes reference depend on them. Fill `L.DATA` and convert the source figures you will use. If a `dataviz` skill is available, its rules on marks and colour apply inside the palette; the palette itself comes from this theme.
5. **Build the hook and the first section**, render, screenshot, and look at every screenshot yourself before going on. In an interactive session, show this batch to the user before building the rest.
6. **Build the rest.** Every stage has a caption that says whether it is measured or stylised, a finished state for `?static` and print, and a speaker note that says what to do with it. Every evidence slide has a source line. Titles are assertions.
7. **Check**: `quarto render index.qmd`, then `python shoot_chrome.py`. Fix every console message and every slide whose content reaches the bottom edge of the frame, where the progress bar and menu button sit. Read all the screenshots, not just the ones you changed.
8. **Adversarial review** with independent subagents, using the prompts below. Then fix what they found.
9. **Creative director pass**, prompt below, and apply the ideas that survive the craft rules.
10. **Write the deck's README** and tell the user where the deck is, how to present it (S speaker view, F fullscreen, O overview, E print view then print to PDF), and which stages are live.

## Review prompts

Run these as separate subagents after the deck renders cleanly. Each reads `index.qmd`, `js/deck-charts.js`, `plan.md`, the craft reference, and the screenshots in `_shots/`.

**Four-dimension judges.** One subagent per dimension, each told to find violations of `references/deck-craft.md` and to list them by slide number with the sentence or element at fault, no fixes:

- *Writing*: do the titles read as the argument in sequence, is each slide one idea, does the slide text say only what the room should read while the presenter talks, are numbers reported with their magnitude and their source?
- *Slides*: does anything crowd or overflow, is whitespace doing its job, do layouts vary with the idea, is anything decorative competing with the content?
- *Visuals*: does colour encode the argument and nothing else, does every stage and figure teach the idea its slide asserts, is every stylised element labelled as such, would it read from the back of the room?
- *Teaching*: where does the reader start, is the concrete instance established before the abstraction, are the BUT turns earned, does the ending give the room its own question?

**The audience member.** One subagent:

```
Put yourself in the shoes of Maria, a sharp researcher in the talk's own field, in the fourth row at 4 p.m. on the second day of a conference. She has seen three hundred decks and likes about ten of them. She is not hostile, but her attention is a resource the speaker has to earn on every slide.

Go through the deck in order, from the code and the screenshots, and say exactly where she stops following: a slide that jumps to a new idea without setting it up, a title that is a label rather than a claim, a number without a magnitude she can feel, a chart she has to decode, a promise from an earlier slide left unfulfilled, a stage whose point she cannot see from her seat, a slide that says what the previous one said. Be blunt and specific, slide by slide. Point at problems only; do not propose fixes.
```

Treat what she finds as the opportunity it is, and build the second version properly rather than patching sentences.

**Creative director.** One subagent, after structure and writing are settled:

```
Act as creative director for this deck. Review the theme, the chart code and the screenshots. Assume structure, teaching and writing are already right. Your job is personality: what would make someone recognise this deck from one slide across the room?

Think at two scales. The whole deck: colour, type, a recurring visual motif or material that belongs to this topic, motion that carries meaning. Individual slides: a distinctive treatment for the hook, the reveal, the dividers, the closing slide; a small drawn illustration or visual joke that makes one idea stick.

Be a radical thinker with tasteful restraint. Keep the clarity and the fixed frame; projectors and print flatten shaders and 3D, so personality comes from drawing, type and colour. Propose your strongest ideas with a concrete description of how two or three existing slides would change, so the result can be pictured before it is built. If an image-generation skill is available in this session you may use it; otherwise everything is drawn in SVG or CSS.
```

## Rules that break decks

The full list with reasons is in the notes reference. The ones that fail silently:

- A `###` or any heading inside a slide body makes pandoc open a nested section, and reveal.js turns the slide into a vertical stack. Use `[Text]{.colhead}` for a column heading or `[Text]{.ph}` for a small heading anywhere else.
- Never name a class `.controls`; reveal.js hides it.
- Appendix slides carry `{visibility="uncounted"}` so the count ends on the closing slide.
- Slides do not scroll. What does not fit is a second slide, not a smaller font.
- Numbers come from `L.DATA` or the source's tables, never from another slide's prose. A number that also appears in a chart is written as `[]{.data key="specs.0.beta" d="3"}` so the prose reads the same object the chart does. Significance comes from the table's stars (`sig: true/false` in `L.DATA`), not from rounded standard errors, because the two disagree in exactly the marginal rows a talk cares about.
- Slide numbers, in the plan, the notes and the reviews, are the screenshot numbers: the title slide is 01.
- Room links are `[text](#slide-id)`. Quarto adds the `/` itself; `#/slide-id` in the source renders as `#//slide-id` and opens the title slide.
- Screenshots are taken with `?static` so build-in animations do not leave half-drawn charts.
