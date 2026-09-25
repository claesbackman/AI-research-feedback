# Deck craft

How the craft of explorable explanations translates to a slide deck, and what goes wrong. The playbook explains the principles. This document is about their form when the medium is a talk: a presenter, a room, a clock, a 1280×720 frame that does not scroll.

You are building the explorable's argument as a talk, not breaking a paper into slides. The audience gets one pass, in the order you choose, at the speed you choose. That takes away the reader's freedom to wander and gives you the presenter's voice in exchange. Use both facts.

## Four dimensions of quality

- **Writing:** the titles, read in sequence, are the argument. The slide text is what the room reads while the presenter talks: short, concrete, one idea. Everything else goes in the speaker notes.
- **Slides:** the frame feels considered, with room to breathe. Layout follows the idea. Nothing decorative competes with the content.
- **Visuals:** every stage, figure and diagram teaches the idea its slide asserts, is honest about what is measured and what is stylised, and reads from the back of the room.
- **Teaching:** the audience starts where they are, meets a concrete instance before an abstraction, earns each reversal, and leaves with a question of their own.

## Form

**One idea per slide, and room around it.** Case's pages are about half whitespace. Slides built from a paper's paragraphs come out at five percent, with three ideas each and a font shrunk to fit. If a slide is crowded, separate the ideas into two slides. Never shrink the type to make something fit: the frame is fixed and the back row is far away.

**The frame does not scroll.** A slide is 1280×720. Content that reaches the bottom edge, where the progress bar sits, is a bug. This is the one place the deck is stricter than the website, where a little scrolling was allowed.

**Titles are assertions.** "Location accounts for the gradient", not "Results: fixed effects". A reader who flips through the titles alone should get the argument. Section dividers carry the chapter headings; slides carry claims.

**Let the idea choose the layout.** Prose beside a stage for an idea that needs a picture and a sentence. A figure full width with one line under it when the figure is the point. A single assertion in large type when the sentence is the point. Two columns when the idea is a contrast. Stat cards when a number should land. A numbered claim list only on the literature slide, if there is one, and the conclusion. If three slides in a row use the same layout, ask whether the ideas really have the same shape.

**Slide text is for the room, notes are for the presenter.** Two to four short sentences on the slide. The transitions, caveats, what to say about the stage, and the answer to the obvious question go in `::: {.notes}`. A slide with a paragraph on it makes the room read instead of listen.

**Every evidence slide has a source line.** A `.source` or `.figcap` line saying what is plotted, what the sample is, and where the estimate comes from. In an academic room this is what earns trust, and it is what lets the printed PDF stand alone.

**Numbers have one home.** Every number a chart draws comes from `L.DATA` in `lib.js`. Every number in the slide prose is transcribed from the source's tables, not from another slide. Decks drift when the same figure is typed three times; when one changes, grep for the old one.

## Narrative

**Three acts, as in the playbook.** Open with a question the room wants answered before you answer it. Climb one step at a time, concrete first. End with something they could only appreciate because of what they now know, and with their question rather than yours.

**Make the room bet.** Case's "place your bets" pattern becomes a question to the room before the reveal: a show of hands, a moment of silence. Write the bet into the speaker note and design the next slide as the payoff. A reveal that follows a bet lands; a reveal that follows nothing is a chart.

**The concrete thread.** Two named characters, a specific firm, one year, one street: pick a concrete instance early and return to it. The instance is the bottom of the ladder of abstraction, and the room climbs back down to it whenever a coefficient stops meaning anything. Keep the same instance throughout. Introducing a new example on every slide costs the room the thing it had just learned.

**THEREFORE and BUT.** The slides link like a story, not a list. Each BUT is a reversal the room can see coming only once it arrives. Plan the turns in `plan.md` first; a talk with no BUT is a report.

**The tree becomes a spine and rooms.** The explorable's forks and doors have no place in a linear talk, but the questions that motivated them still arrive, from the room. Build the spine for the talk's length and put each side path in an appendix slide, a *room*. A room is reached by a link placed next to the thing that raises the question, `[detail](#slide-id)`, and carries a link back. Rooms are `visibility="uncounted"` so the deck ends, for the room, on the closing slide. The appendix is where the sandbox lives: the robustness slide, the alternative measure, the ablation, the other dataset, the thing the second questioner will ask about. The website's map and progress dots have no equivalent here; reveal's overview (**O**) and stable slide ids cover navigation.

**The static read must work.** Someone reading the printed PDF, with no presenter, must be able to follow the argument. Every animated stage draws its finished state under `?static` and in print. Every live stage has a caption that says what it shows without anyone moving the slider.

## Interaction, when the presenter holds the mouse

Interaction in a deck is the presenter's, not the audience's. This changes what a stage is for.

**One move per stage.** A drag, a click, a toggle: one action with a visible consequence. The presenter has to do it while talking, in front of people, on an unfamiliar projector. Two sliders that must be set in sequence is a demo that fails on stage.

**Large and legible.** Chart text at 12 to 14 px in a 1280-wide frame scales with the slide and reads from the back; hover states and tooltips do not exist for the room. If the room has to see a number, draw it as a label.

**Build-ins where the reveal is the argument.** A stage that grows in when the slide appears (`data-animate`) is the deck's version of Case's slow reveal, and it is powerful exactly once or twice per talk: the payoff after the bet, the moment the second bar catches the first. Everywhere else, draw the finished state. Fragments that release one bullet at a time are the slide equivalent of click-to-reveal-the-next-sentence, which Case calls crap-interaction: use a fragment only when the thing revealed is the BUT.

**Hand-author the starting state.** The slider starts where the picture is most interesting, the toggle starts on the side the room expects, so the first move is the reversal.

**Speaker notes say what to do.** Every stage's note names the move, what the room should notice, and what to say if the demo fails. A stage without instructions is a stage the presenter will skip.

**Keep the deck's keys working.** Stages stop pointer events from reaching reveal's swipe handler, and blur their buttons after a click, so space and the arrow keys still advance the deck. The template does this for every `.stage`.

## Visuals

**Colour encodes the argument and nothing else.** Choose at most four semantic colours, name them for what they mean in the topic, and paint everything else grey. The template ships with `primary`, `contrast`, `actor-a`, `actor-b`; rename them to the topic's words in the theme, because a chart author who writes `var(--gain)` writes the argument into the chart. A second channel, a texture or a line style, can carry a second distinction; more than two channels is decoration.

**Say what is stylised.** A stage that draws the source's slope around an illustrative level says so in its caption. A chart that shows synthetic data with the right shape says so. When the source reports a slope or a gap but no level, draw the gap or an index (purchase = 100), not a level: an invented level produces a total the room can check against what it knows, and that is the number they will remember. If a level is needed, take it from a source figure's axis and say where it came from. This is the Victor half of the playbook: the model is honest and inspectable even when it is simplified.

**The source's own figures belong in the deck.** Convert vector figures from PDF to SVG, recolour them into the deck palette, and drop the white plot box so they sit on the slide. Raster figures (micrographs, screenshots, photos) go in as they are. A recoloured figure from the source beside three sentences of prose is often the strongest evidence slide, and it costs nothing. A multi-series figure is the exception: its series colours are not the deck's and would give the four semantic colours a fifth meaning. The recolour script turns them into greys by default; if the series then cannot be told apart, redraw the figure as a stage in the palette. The source's in-figure notes (test statistics, sample lines) belong in the speaker notes, and a figure that carries them is another candidate for a redraw. Use a run-time stage when the idea needs motion, a handle, or a comparison the source's figure does not draw.

**Diagrams draw the mechanism.** A causal loop, two boxes and an arrow, a floor and a ceiling: drawn in SVG in the deck's palette, not pasted from elsewhere. If a diagram needs a legend to be read, it has too many parts.

## What goes wrong

Recurring faults from decks built this way. Check for each when reviewing.

- Slides with two or three ideas and a paragraph of prose, because a paper's paragraph was pasted in whole.
- Titles that are labels ("Data", "Results") in a deck whose other titles are claims.
- The same prose-left, chart-right layout on eight consecutive slides.
- A number in the prose that disagrees with the chart beside it, because each was typed separately.
- A stage with no caption, so the printed deck shows a chart with no meaning.
- A build-in that replays on every visit to the slide and looks broken when the presenter steps back.
- Charts that failed to draw and show only an error line, unnoticed because nobody looked at the screenshot.
- An appendix slide included in the count, so the progress bar says the talk is half over when it is nearly done.
- A heading inside a slide body, turning it into a vertical stack that swallows the arrow keys.
- Content that fits in the browser preview and is clipped at 1280×720.
- A colour used because it looked nice, meaning nothing, next to four colours that mean something.
- Speaker notes that repeat the slide text instead of saying what to do and what to say.
- A stylised total, invented to have a level to draw, that a room in the field knows is wrong.
- Plan and notes numbering slides from the hook while the screenshots number from the title, so a note points at the wrong slide.
