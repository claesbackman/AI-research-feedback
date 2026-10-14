# Deck craft

How the craft of explorable explanations translates to a slide deck, and what goes wrong. The playbook explains the principles. This document is about their form when the medium is a talk: a presenter, a room, a clock, a 16:9 frame that does not scroll.

You are building the explorable's argument as a talk, not breaking a paper into slides. The audience gets one pass, in the order you choose, at the speed you choose. That takes away the reader's freedom to wander and gives you the presenter's voice in exchange. Use both facts.

## Four dimensions of quality

- **Writing:** the titles, read in sequence, are the argument. The slide text is what the room reads while the presenter talks: short, concrete, one idea. Everything else goes in the speaker notes.
- **Slides:** the frame feels considered, with room to breathe. Layout follows the idea. Nothing decorative competes with the content.
- **Visuals:** every stage, figure and diagram teaches the idea its slide asserts, is honest about what is measured and what is stylised, and reads from the back of the room.
- **Teaching:** the audience starts where they are, meets a concrete instance before an abstraction, earns each reversal, and leaves with a question of their own.

## Form

**One idea per frame, and room around it.** Case's pages are about half whitespace. Slides built from a paper's paragraphs come out at five percent, with three ideas each and a font shrunk to fit. If a frame is crowded, separate the ideas into two frames. Never shrink the type to make something fit: the frame is fixed and the back row is far away. In beamer that means no `\small`, no `[shrink]`, no `[allowframebreaks]`; `check_deck.py` flags all three.

**The frame does not scroll.** A frame is 160 × 90 mm. Content that reaches the footline, where the progress bar and the frame number sit, is a bug, and beamer compiles it anyway, with at most an overfull-box line in the log. `shoot.py` checks every page for ink in the band above the footline and names the page.

**Titles are assertions.** "Location accounts for the gradient", not "Results: fixed effects". A reader who flips through the titles alone should get the argument. Dividers carry the chapter headings; frames carry claims.

**Let the idea choose the layout.** Prose beside a stage for an idea that needs a picture and a sentence. A figure full width with one line under it when the figure is the point. A single assertion in large type when the sentence is the point. Two columns when the idea is a contrast. Stat cards when a number should land. A numbered claim list only on the literature slide, if there is one, and the conclusion. If three frames in a row use the same layout, ask whether the ideas really have the same shape.

**Slide text is for the room, notes are for the presenter.** Two to four short sentences on the frame. The transitions, caveats, what to say about the stage, and the answer to the obvious question go in `\note{}`. A frame with a paragraph on it makes the room read instead of listen.

**Every evidence frame has a source line.** A `\source{}` or `\figcap{}` saying what is plotted, what the sample is, and where the estimate comes from. In an academic room this is what earns trust, and it is what lets the printed handout stand alone.

**Numbers have one home.** Every number a chart draws and every number a sentence quotes comes from `data/numbers.tex` and the CSV files it loads, through `\D{}`, `\Dv{}` and `\Dt{}`. Decks drift when the same figure is typed three times; when one changes, grep for the old one.

## Narrative

**Three acts, as in the playbook.** Open with a question the room wants answered before you answer it. Climb one step at a time, concrete first. End with something they could only appreciate because of what they now know, and with their question rather than yours.

**Make the room bet.** Case's "place your bets" pattern becomes a question to the room before the reveal: a show of hands, a moment of silence. Write the bet into the speaker note and design the next overlay step as the payoff. A reveal that follows a bet lands; a reveal that follows nothing is a chart.

**The concrete thread.** Two named characters, a specific firm, one year, one street: pick a concrete instance early and return to it. The instance is the bottom of the ladder of abstraction, and the room climbs back down to it whenever a coefficient stops meaning anything. Keep the same instance throughout. Introducing a new example on every frame costs the room the thing it had just learned.

**THEREFORE and BUT.** The frames link like a story, not a list. Each BUT is a reversal the room can see coming only once it arrives. Plan the turns in `plan.md` first; a talk with no BUT is a report.

**The tree becomes a spine and rooms.** The explorable's forks and doors have no place in a linear talk, but the questions that motivated them still arrive, from the room. Build the spine for the talk's length and put each side path in an appendix frame, a *room*. A room is reached by a link placed next to the thing that raises the question, `\goto{label}{detail}`, and carries `\back{origin}`. Rooms come after `\appendix`, so they are numbered A1, A2, … and the progress bar ends on the closing frame. The appendix is where the sandbox lives: the robustness frame, the alternative measure, the ablation, the other dataset, the thing the second questioner will ask about. The website's map and progress dots have no equivalent here; the PDF viewer's thumbnails and stable labels cover navigation.

**The static read must work.** Someone reading the printed handout, with no presenter, must be able to follow the argument. `deck-handout.pdf` collapses every frame to one page with every stage in its finished state, which is why a stepped stage reads `\step` and never hides its finished state behind `\only`. Every stage has a caption that says what it shows without anyone pressing a key.

## Stages, when the presenter holds the clicker

A PDF has no sliders. What a stage can do is change between overlay steps, and that is enough: the presenter steps, the room watches one thing change, the presenter says what it means. This changes what a stage is for.

**One dimension of change per stage.** A build-in, a handle that moves along a line, a toggle between two states: one thing changes, three or four steps at most, and each step is a point the presenter would have stopped at anyway. Two things changing at once is a demo the room cannot follow, and six steps is a flip book.

**Large and legible.** Chart text at 6.5 to 7.5 pt in a 160 mm frame scales with the slide and reads from the back; nothing can be hovered. If the room has to see a number, draw it as a label on the chart.

**Build-ins where the reveal is the argument.** A stage that completes on the next step (`visible on=<2->`) is the deck's version of Case's slow reveal, and it is powerful exactly once or twice per talk: the payoff after the bet, the moment the second bar catches the first. Everywhere else, draw the finished state. `\pause` that releases one bullet at a time is the slide equivalent of click-to-reveal-the-next-sentence, which Case calls crap-interaction: use an overlay only when the thing revealed is the BUT.

**Hand-author the starting state.** Step 1 is where the picture is most interesting, the toggle starts on the side the room expects, so the first step is the reversal. The last step is the finished state, and it is what the handout prints.

**Nothing moves between steps except the thing that changes.** An element that disappears with `\only` gives its space back and the axis shifts. The theme's `visible on` keeps the space, the stage is a fixed-height box, and cards are `overlay` nodes that do not count towards the picture's width, so steps register exactly on top of one another. Compare consecutive screenshots of every stepped stage to be sure.

**Speaker notes say what to do.** Every stage's note names the steps, what the room should notice at each, and what to say if the projector loses one. A stage without instructions is a stage the presenter will click through.

## Visuals

**Colour encodes the argument and nothing else.** Choose at most four semantic colours, name them for what they mean in the topic, and paint everything else grey. The theme ships with `primary`, `contrast`, `actora`, `actorb`; alias them to the topic's words in `deck.tex` (`\colorlet{gain}{primary}`), because a chart author who writes `gain` writes the argument into the chart. A second channel, a hatch pattern or a line style, can carry a second distinction; more than two channels is decoration.

**Say what is stylised.** A stage that draws the source's slope around an illustrative level says so in its caption. A chart that shows synthetic data with the right shape says so. When the source reports a slope or a gap but no level, draw the gap or an index (purchase = 100), not a level: an invented level produces a total the room can check against what it knows, and that is the number they will remember. If a level is needed, take it from a source figure's axis and say where it came from. This is the Victor half of the playbook: the model is honest and inspectable even when it is simplified.

**The source's own figures belong in the deck.** beamer includes the source's PDF figures as they are, so there is no conversion; `restyle_figs.py` recolours them into the deck palette and drops the plot-region tint so they sit on the slide. Raster figures (micrographs, screenshots, photos) go in unchanged. A recoloured figure from the source beside three sentences of prose is often the strongest evidence frame, and it costs nothing. A multi-series figure is the exception: its series colours are not the deck's and would give the four semantic colours a fifth meaning. The recolour script turns them into greys by default; if the series then cannot be told apart, redraw the figure as a stage in the palette. The source's in-figure notes (test statistics, sample lines) belong in the speaker notes, and a figure that carries them is another candidate for a redraw. Use a stage when the idea needs steps, a handle, or a comparison the source's figure does not draw.

**Diagrams draw the mechanism.** A causal loop, two boxes and an arrow, a floor and a ceiling: drawn in TikZ in the deck's palette (`mech box`, `mech arrow`), not pasted from elsewhere. If a diagram needs a legend to be read, it has too many parts.

## What goes wrong

Recurring faults from decks built this way. Check for each when reviewing.

- Frames with two or three ideas and a paragraph of prose, because a paper's paragraph was pasted in whole.
- Titles that are labels ("Data", "Results") in a deck whose other titles are claims.
- The same prose-left, chart-right layout on eight consecutive frames.
- A number in the prose that disagrees with the chart beside it, because each was typed separately instead of read from `data/numbers.tex`.
- A stage with no caption, so the handout shows a chart with no meaning.
- A stepped stage whose finished state is hidden behind `\only<1>`, so the handout shows the wrong step, or every step at once.
- A chart whose axis jumps between steps because an element was removed with `\only` instead of hidden with `visible on`.
- Charts that failed to draw, or drew with a pgfkeys error, unnoticed because nobody read the log or the screenshot.
- An appendix frame before `\appendix`, so the progress bar says the talk is half over when it is nearly done.
- A frame body with `\small`, `[shrink]` or `[allowframebreaks]`, which is the sign that two frames were forced into one.
- Content that runs below the footline, which beamer compiles with at most an overfull-box line.
- A colour used because it looked nice, meaning nothing, next to four colours that mean something.
- Speaker notes that repeat the slide text instead of saying what to do and what to say.
- A stylised total, invented to have a level to draw, that a room in the field knows is wrong.
- Plan and notes that count frames while the screenshots count pages, so a note points at the wrong one: the listing from `shoot.py` gives both, and the plan uses frame numbers.
