---
name: explorable-beamer
description: Build a LaTeX beamer slide deck in the explorable-explanation style (Nicky Case) — one idea per frame, assertion titles, a concrete running example, TikZ/pgfplots stages the presenter steps through, the source's own figures recoloured into the deck palette, an appendix of side rooms, and a screenshot-and-log check of every page. Use for any request for a Beamer, LaTeX or TeX presentation, talk, slides, seminar, conference, lecture, keynote or job-market deck, "turn this paper into beamer slides", a deck that must be a PDF, or for revising or reviewing a deck built this way. The sibling skill explorable-deck builds the same deck in Quarto reveal.js; use this one when the user names Beamer, LaTeX, TeX or PDF, or works in a LaTeX project. Not for a website explorable (that is explorable-explanations) or a poster.
---

# Explorable beamer deck

Build a beamer deck that teaches the way a good explorable does, but inside the frame a talk imposes: linear, timed, driven by a presenter, 160 × 90 mm with no scrolling. The explorable's non-linear tree becomes a spine of counted frames plus an appendix of side rooms. Its playables become stages the presenter steps through while talking. Its "static read must work" becomes: the handout PDF must carry the argument on its own.

The sibling skill `explorable-deck` builds the same deck in Quarto reveal.js with live, draggable stages; `explorable-explanations` builds the website version. This one produces a PDF from LaTeX, and it reuses the website's or the Quarto deck's numbers when one already exists for the topic.

## What you produce

One folder per deck, built with `sh build.sh`:

```
<deck>/
  deck.tex             the deck: one \begin{frame} per idea, a \note on every frame
  theme/explorable.sty tokens, faces, layouts, the stage, stat cards, chart styles
  data/numbers.tex     the single home of every number a chart or a sentence uses
  data/*.csv           series the charts plot, loaded by numbers.tex
  charts/*.tex         the stages: pgfplots/TikZ, one file each, input into a stage
  figs/*.pdf           the source's figures, recoloured by convert_figs.sh; committed with the deck
  figs/convert_figs.sh, figs/restyle_figs.py
  build.sh             deck.pdf, deck-handout.pdf (one page per frame), deck-notes.pdf (pdfpc)
  shoot.py             one PNG per page, the page → frame map, log messages, overflow check
  check_deck.py        lints deck.tex against the craft rules beamer does not enforce
  README.md            how to build, check, present; where the numbers come from
  plan.md              the talk script (see below)
```

`scripts/new_deck.sh <path>` copies the template in `assets/template/` and the scripts into place. Start every new deck from it: the template already solves the beamer traps listed in the notes reference, and it compiles on any TeX Live (lualatex) with no network and no font install.

## Read first

1. [The Explorable Explanations Playbook](references/playbook.md): Nicky Case, Bret Victor, Steven Strogatz. Read §1–4 and §10 closely and skim the rest once per project. It explains why the craft rules exist so you can apply them with judgment. Its three-act arc, ladder of abstraction, empathy for the perplexed reader, and message → mechanics apply to a talk unchanged. Its §6 (interaction craft) and §9 (the frontier) describe the website; for a talk, the stages section of `deck-craft.md` overrides them.
2. [Deck craft](references/deck-craft.md): how the explorable craft translates to slides, and what goes wrong. Read before planning, and again when reviewing.
3. [beamer and TikZ notes](references/beamer-notes.md): the template's layout vocabulary, the stage conventions, the figure pipeline, building, screenshots, the lint, and the traps. Read before building.
4. Look at the four screenshots in [references/example-deck/](references/example-deck/) of a finished deck built in this style (a hook with two characters, a reveal stage, a paper figure beside prose, a coefficient plot). They are from the Quarto sibling of a housing-returns paper (Bäckman, D'Lima and Khorunzhina, "Anna and Bo"); the register is the same in beamer. If the source is that paper or a neighbour of it, borrow nothing from the examples but the register. For any topic, take the register, not the content: the topic decides the colours, the characters and the shapes.

## Review level

The build and its checks always run. The subagent review is the slow part of a run: five or six agents each read the whole deck and every screenshot, and a second version is built after them. It is worth most once the user has seen the deck and settled the content, so it runs only when asked:

| level | how the user asks | what runs after the checks |
|---|---|---|
| none (default) | a plain request for a deck | the self-check only; the handover says review was skipped and how to ask for it |
| `review` | "with review", "review the deck", `/explorable-beamer review` | the four judges and Maria, then a second version |
| `full` | "full review", "with the creative director", `/explorable-beamer full` | the above, then the creative director |

A request to review a deck that already exists skips steps 1–6: run the final check in step 7 so the screenshots are current, then steps 8–11 at the level asked. "Review" on its own means `review`.

## Working rhythm

1. **Read the source.** The paper, notes, or codebase, and any existing explorable or Quarto deck for the topic. If one exists, its data object is the deck's starting material: transcribe it into `data/numbers.tex` rather than retyping from the paper, so the two never disagree on a number.
2. **Fix the frame** before writing a slide: the audience (Strogatz's traumatized, perplexed or naturals, and which one the slide text is written for), the length in minutes, the venue. When the user has not said, assume a 20-minute conference talk for a mixed academic room, and say so. Length changes the shape, not just the count:

   | slot | counted frames | stages | build-ins | bets | literature slide |
   |---|---|---|---|---|---|
   | 12 min | 8–10 | 1 | 1 | 1 | no, one sentence on the hook |
   | 20 min | 13–16 | 2–3 | 1–2 | 1–2 | one frame |
   | 45+ min | 25–35 | 3–5 | 2 | one before each BUT | one frame, plus recap frames as cognitive gates |

   Everything a questioner might want goes in the appendix; in a long lecture the rooms move into the spine. `check_deck.py --minutes N` compares the deck to this table.
3. **Write `plan.md`** as a scriptwriter: the one big thing in a sentence, the cause → effect chain with its THEREFORE and BUT turns, then frame by frame what the room sees, what the presenter does with each stage (which steps, what each shows), what they should notice, and which appendix room each question opens. Name the characters and the four semantic colours here.
4. **Scaffold** with `scripts/new_deck.sh`. Give each of the four colour tokens a topic alias in `deck.tex` (`\colorlet{gain}{primary}`) and paint the charts with the aliases; never rename the generic tokens, because the commands and the notes reference depend on them. Fill `data/numbers.tex` and bring in the source figures you will use. If a `dataviz` skill is available, its rules on marks and colour apply inside the palette; the palette itself comes from this theme.
5. **Build the hook and the first section**, then `sh build.sh --fast` and `python3 shoot.py`, and look at every screenshot yourself before going on. In an interactive session, show this batch to the user before building the rest.
6. **Build the rest.** Every stage has a caption that says whether it is measured or stylised, a finished state that the handout prints, and a speaker note that says what to do with each step. Every evidence frame has a source line. Titles are assertions.
7. **Check.** While building, iterate with `sh build.sh --fast` (deck.pdf only) and `python3 shoot.py`. Its listing, log check and overflow check cover every page each time. Look at the screenshots of the frames you changed, and at every frame touched by a change to the theme, `numbers.tex` or a shared chart. Fix every log message and every page whose content reaches the footline as they appear. When the deck is complete, run the final check once: `sh build.sh`, then `python3 shoot.py`, then `python3 check_deck.py --minutes N`. Fix every finding, read all the screenshots, and read the handout once (`python3 shoot.py --handout`) to confirm every stage prints finished.
8. **Self-check**, at every level: go through "What goes wrong" in `references/deck-craft.md` against the source and the screenshots you have already read, and fix what you find. This is your own pass, with no subagents.
9. **Review**, at `review` and `full` only: the four judges and Maria, prompts below. Then build the second version from what they found and run the final check again.
10. **Creative director**, at `full` only, prompt below. Apply the ideas that survive the craft rules and run the final check again.
11. **Write the deck's README** and tell the user where the deck is, how to present it (`deck.pdf` full screen, `pdfpc --notes=right _build/deck-notes.pdf` for notes, `deck-handout.pdf` to print or send), and which stages have steps. If no review ran, close with one line saying so and how to ask for it: "review the deck" runs the judges and Maria, and "full review" adds the creative director.

## Review prompts

Run these at the `review` and `full` levels only, after the final check passes. Launch the four judges and Maria together in one message so they run in parallel; the creative director comes after the second version. Each reads `deck.tex`, `charts/*.tex`, `plan.md`, the craft reference, and the screenshots in `_shots/`.

**Four-dimension judges.** One subagent per dimension, each told to find violations of `references/deck-craft.md` and to list them by frame number with the sentence or element at fault, no fixes:

- *Writing*: do the titles read as the argument in sequence, is each frame one idea, does the slide text say only what the room should read while the presenter talks, are numbers reported with their magnitude and their source?
- *Slides*: does anything crowd or overflow, is whitespace doing its job, do layouts vary with the idea, is anything decorative competing with the content?
- *Visuals*: does colour encode the argument and nothing else, does every stage and figure teach the idea its frame asserts, is every stylised element labelled as such, would it read from the back of the room?
- *Teaching*: where does the reader start, is the concrete instance established before the abstraction, are the BUT turns earned, does the ending give the room its own question?

**The audience member.** One subagent:

```
Put yourself in the shoes of Maria, a sharp researcher in the talk's own field, in the fourth row at 4 p.m. on the second day of a conference. She has seen three hundred decks and likes about ten of them. She is not hostile, but her attention is a resource the speaker has to earn on every slide.

Go through the deck in order, from the code and the screenshots, and say exactly where she stops following: a frame that jumps to a new idea without setting it up, a title that is a label rather than a claim, a number without a magnitude she can feel, a chart she has to decode, a promise from an earlier frame left unfulfilled, a stage whose point she cannot see from her seat, a frame that says what the previous one said. Be blunt and specific, frame by frame. Point at problems only; do not propose fixes.
```

Treat what she finds as the opportunity it is, and build the second version properly rather than patching sentences.

**Creative director.** One subagent, at the `full` level, after the second version is built and structure and writing are settled:

```
Act as creative director for this deck. Review the theme, the chart code and the screenshots. Assume structure, teaching and writing are already right. Your job is personality: what would make someone recognise this deck from one slide across the room?

Think at two scales. The whole deck: colour, type, a recurring visual motif or material that belongs to this topic, overlay steps that carry meaning. Individual frames: a distinctive treatment for the hook, the reveal, the dividers, the closing frame; a small drawn illustration or visual joke that makes one idea stick.

Be a radical thinker with tasteful restraint. Keep the clarity and the fixed frame; projectors and print flatten everything, so personality comes from drawing, type and colour, all in TikZ. Propose your strongest ideas with a concrete description of how two or three existing frames would change, so the result can be pictured before it is built.
```

## Rules that break decks

The full list with reasons is in the notes reference. The ones that fail silently:

- A frame that is too tall still compiles; beamer logs at most an overfull box that is easy to miss. `shoot.py` names every page with ink in the band above the footline; fix it with a second frame, never with `\small`, `[shrink]` or `[allowframebreaks]`, which the lint rejects.
- Handout mode shows every overlay at once. A stepped stage reads `\step` and declares `\stagesteps{N}` with `<1-N>` on its frame; a build-in uses `visible on=<2->`; nothing a stage needs is hidden behind `\only<1>`.
- `visible on` keeps an element's space; `\only` gives it back and the axis moves between steps. Every stepped chart also sets explicit axis limits.
- Appendix frames come after `\appendix`, so they are numbered A1, A2, … and the progress bar ends on the closing frame.
- Numbers come from `data/numbers.tex` through `\D`, `\Dv` and `\Dt`, never from another frame's prose. Inside a chart coordinate only `\Dv` and a macro set with `\Dtlet` work; `\Dt` is for prose. Significance comes from the table's stars (`sig` in the CSV), not from rounded standard errors, because the two disagree in exactly the marginal rows a talk cares about.
- Page numbers in `_shots/` count overlay steps as pages; the plan and the notes use frame numbers, and `shoot.py` prints the map between the two. The title frame is 1 in both.
- The layout is `beside`, not `split`: amsmath owns that name.
- Node styles (`card`, `handle`, `datalabel`) are TikZ keys; `deckaxis` is a pgfplots key. On the wrong path they produce a pgfkeys error that the log check reports and the chart ignores.
