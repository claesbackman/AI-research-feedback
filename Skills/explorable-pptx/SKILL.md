---
name: explorable-pptx
description: Build a PowerPoint (.pptx) slide deck in the explorable-explanation style (Nicky Case) — one idea per frame, assertion titles, a concrete running example, stages drawn as native shapes in the deck palette that the presenter steps through, the source's own figures recoloured into the palette, an appendix of side rooms, speaker notes on every slide, and a screenshot-and-log check of every page through PowerPoint itself. Use for any request for a PowerPoint, pptx or Keynote presentation, talk, slides, seminar, conference, lecture, keynote or job-market deck, "turn this paper into PowerPoint slides", "a PowerPoint version of the explorable deck", a deck a coauthor must edit in PowerPoint, or for revising or reviewing a deck built this way. The sibling skills explorable-deck (Quarto reveal.js) and explorable-beamer (LaTeX) build the same deck in those formats; use this one when the user names PowerPoint, pptx, Keynote or Google Slides, or needs a file coauthors can edit. Not for a website explorable (that is explorable-explanations) or a poster.
---

# Explorable PowerPoint deck

Build a PowerPoint deck that teaches the way a good explorable does, but inside the frame a talk imposes: linear, timed, driven by a presenter, 10 × 5.625 in with no scrolling. The explorable's non-linear tree becomes a spine of counted frames plus an appendix of side rooms. Its playables become stages the presenter steps through while talking. Its "static read must work" becomes: the handout must carry the argument on its own.

The sibling skill `explorable-deck` builds the same deck in Quarto reveal.js with live, draggable stages, `explorable-beamer` builds it in LaTeX beamer, and `explorable-explanations` builds the website version. This one produces a `.pptx` with pptxgenjs from a declarative `deck.js`, so coauthors can open and edit it in PowerPoint, Keynote or Google Slides, and it reuses the website's or a sibling deck's numbers when one already exists for the topic.

## What you produce

One folder per deck, built with `sh build.sh`:

```
<deck>/
  deck.js              the deck: meta, colour aliases, one frame object per idea, notes on every frame
  theme/theme.js       tokens, faces, sizes, geometry
  theme/lib.js         the drawing helpers (chart frame, axes, shapes, cards, hatch) and the prose markup parser
  theme/layouts.js     the slide vocabulary: how each frame kind becomes a slide
  data/numbers.js      the single home of every number a chart or a sentence uses
  data/*.csv           series the charts plot, loaded by numbers.js
  charts/*.js          the stages: one module each, `steps` and `draw(ctx)`
  figs/*.png           the source's figures, recoloured and rendered by convert_figs.sh; committed with the deck
  figs/convert_figs.sh, figs/restyle_figs.py
  build.js, build.sh   deck.pptx, deck-handout.pptx (one slide per frame), _build/manifest.json, build-log.txt
  shoot.py             one PNG per slide, the slide → frame map, build messages, overflow check
  check_deck.py        lints the deck against the craft rules PowerPoint does not enforce
  README.md            how to build, check, present; where the numbers come from
  plan.md              the talk script (see below)
```

`scripts/new_deck.sh <path>` copies the template in `assets/template/` and the scripts into place. Start every new deck from it: the template already solves the pptxgenjs and PowerPoint traps listed in the notes reference, and it builds with Node and npm alone (the first `sh build.sh` installs pptxgenjs into `node_modules/`). The four faces ship with Microsoft Office, so nothing is installed or embedded on the presenting machine.

## Read first

1. [The Explorable Explanations Playbook](references/playbook.md): Nicky Case, Bret Victor, Steven Strogatz. Read §1–4 and §10 closely and skim the rest once per project. It explains why the craft rules exist so you can apply them with judgment. Its three-act arc, ladder of abstraction, empathy for the perplexed reader, and message → mechanics apply to a talk unchanged. Its §6 (interaction craft) and §9 (the frontier) describe the website; for a talk, the stages section of `deck-craft.md` overrides them.
2. [Deck craft](references/deck-craft.md): how the explorable craft translates to slides, and what goes wrong. Read before planning, and again when reviewing.
3. [PowerPoint and pptxgenjs notes](references/pptx-notes.md): the deck file and its markup, the layout vocabulary, the stage API, the figure pipeline, building, screenshots, the lint, presenting, and the traps. Read before building.
4. Look at the four screenshots in [references/example-deck/](references/example-deck/) of a finished deck built in this style (a hook with two characters, a reveal stage, a paper figure beside prose, a coefficient plot). They are from the Quarto sibling of a housing-returns paper (Bäckman, D'Lima and Khorunzhina, "Anna and Bo"); the register is the same in PowerPoint. If the source is that paper or a neighbour of it, borrow nothing from the examples but the register. For any topic, take the register, not the content: the topic decides the colours, the characters and the shapes.

## Review level

The build and its checks always run. The subagent review is the slow part of a run: five or six agents each read the whole deck and every screenshot, and a second version is built after them. It is worth most once the user has seen the deck and settled the content, so it runs only when asked:

| level | how the user asks | what runs after the checks |
|---|---|---|
| none (default) | a plain request for a deck | the self-check only; the handover says review was skipped and how to ask for it |
| `review` | "with review", "review the deck", `/explorable-pptx review` | the four judges and Maria, then a second version |
| `full` | "full review", "with the creative director", `/explorable-pptx full` | the above, then the creative director |

A request to review a deck that already exists skips steps 1–6: run the final check in step 7 so the screenshots are current, then steps 8–11 at the level asked. "Review" on its own means `review`.

## Working rhythm

1. **Read the source.** The paper, notes, or codebase, and any existing explorable, Quarto deck or beamer deck for the topic. If one exists, its data object is the deck's starting material: copy it into `data/numbers.js` (the Quarto sibling's `L.DATA` drops in as is) rather than retyping from the paper, so the two never disagree on a number.
2. **Fix the frame** before writing a slide: the audience (Strogatz's traumatized, perplexed or naturals, and which one the slide text is written for), the length in minutes, the venue. When the user has not said, assume a 20-minute conference talk for a mixed academic room, and say so. Length changes the shape, not just the count:

   | slot | counted frames | stages | build-ins | bets | literature frame |
   |---|---|---|---|---|---|
   | 12 min | 8–10 | 1 | 1 | 1 | no, one sentence on the hook |
   | 20 min | 13–16 | 2–3 | 1–2 | 1–2 | one frame |
   | 45+ min | 25–35 | 3–5 | 2 | one before each BUT | one frame, plus recap frames as cognitive gates |

   Everything a questioner might want goes in the appendix; in a long lecture the rooms move into the spine. `check_deck.py --minutes N` compares the deck to this table.
3. **Write `plan.md`** as a scriptwriter: the one big thing in a sentence, the cause → effect chain with its THEREFORE and BUT turns, then frame by frame what the room sees, what the presenter does with each stage (which steps, what each shows), what they should notice, and which appendix room each question opens. Name the characters and the four semantic colours here.
4. **Scaffold** with `scripts/new_deck.sh`. Give each of the four colour tokens a topic alias in `deck.js` (`aliases: { gain: 'primary', … }`) and paint the charts with the aliases; never rename the generic tokens, because the layouts and the notes reference depend on them. Fill `data/numbers.js` and bring in the source figures you will use. If a `dataviz` skill is available, its rules on marks and colour apply inside the palette; the palette itself comes from this theme.
5. **Build the hook and the first section**, then `sh build.sh --fast` and `python3 shoot.py`, and look at every screenshot yourself before going on. In an interactive session, show this batch to the user before building the rest.
6. **Build the rest.** Every stage has a caption that says whether it is measured or stylised, a finished state on its last step that the handout keeps, and a speaker note that says what to do with each step. Every evidence frame has a source line. Titles are assertions.
7. **Check.** While building, iterate with `sh build.sh --fast` (deck.pptx only) and `python3 shoot.py`. Its listing, build messages and overflow check cover every slide each time. Look at the screenshots of the frames you changed, and at every frame touched by a change to the theme, `numbers.js` or a shared chart. Fix every build message and every page whose content reaches the footline as they appear. When the deck is complete, run the final check once: `sh build.sh`, then `python3 shoot.py`, then `python3 check_deck.py --minutes N`. Fix every finding, read all the screenshots, and read the handout once (`python3 shoot.py --handout`) to confirm every stage prints finished.
8. **Self-check**, at every level: go through "What goes wrong" in `references/deck-craft.md` against the source and the screenshots you have already read, and fix what you find. This is your own pass, with no subagents.
9. **Review**, at `review` and `full` only: the four judges and Maria, prompts below. Then build the second version from what they found and run the final check again.
10. **Creative director**, at `full` only, prompt below. Apply the ideas that survive the craft rules and run the final check again.
11. **Write the deck's README** and tell the user where the deck is, how to present it (`deck.pptx` in PowerPoint's slideshow with presenter view for the notes, `deck-handout.pptx` to print or send), and which stages have steps. If no review ran, close with one line saying so and how to ask for it: "review the deck" runs the judges and Maria, and "full review" adds the creative director.

## Review prompts

Run these at the `review` and `full` levels only, after the final check passes. Launch the four judges and Maria together in one message so they run in parallel; the creative director comes after the second version. Each reads `deck.js`, `charts/*.js`, `plan.md`, the craft reference, and the screenshots in `_shots/`.

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

Think at two scales. The whole deck: colour, type, a recurring visual motif or material that belongs to this topic, steps that carry meaning. Individual frames: a distinctive treatment for the hook, the reveal, the dividers, the closing frame; a small drawn illustration or visual joke that makes one idea stick.

Be a radical thinker with tasteful restraint. Keep the clarity and the fixed frame; projectors and print flatten everything, so personality comes from drawing, type and colour, all drawn with the library's shapes. Propose your strongest ideas with a concrete description of how two or three existing frames would change, so the result can be pictured before it is built.
```

## Rules that break decks

The full list with reasons is in the notes reference. The ones that fail silently:

- A text box that is too tall still builds; PowerPoint spills the text below the box without a word. The build logs an estimate for every box and `shoot.py` names every page with ink in the band above the footline; fix it with a second frame, never with a smaller size, which the lint rejects.
- The handout draws every stage at its last step. A stepped stage reads `step` and draws its finished state on step `steps`; nothing a stage needs is drawn only on step 1.
- Every step of a stage is drawn from the same data domains into the same box, so axes never move between steps. Set `xd` and `yd` from the full data, not from what the step shows.
- Appendix frames come after `{ kind: 'appendix' }`, so they are numbered A1, A2, … and the progress bar ends on the closing frame.
- Numbers come from `data/numbers.js` through `{{path}}` in prose and `D` in the charts, never from another frame's prose. Significance comes from the table's stars (`sig` in the CSV), not from rounded standard errors, because the two disagree in exactly the marginal rows a talk cares about.
- Slide numbers in `_shots/` count steps as slides; the plan and the notes use frame numbers, and `shoot.py` prints the map between the two. The title frame is 1 in both.
- Colours are token names or aliases resolved by `L.col`; a hex value with `#` corrupts the file, and `line: { width: 0 }` on a shape still draws a black outline, so filled shapes take no `line` at all.
- PowerPoint's first export after a cold launch can take a minute; `shoot.py` leaves PowerPoint running. If an export stalls, a dialog is open in PowerPoint.
