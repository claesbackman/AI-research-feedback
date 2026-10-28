# Deck craft

How the craft of explorable explanations translates to a slide deck, and what goes wrong. The playbook explains the principles. This document is about their form when the medium is a talk: a presenter, a room, a clock, a 16:9 frame that does not scroll.

You are building the explorable's argument as a talk, not breaking a paper into slides. The audience gets one pass, in the order you choose, at the speed you choose. That takes away the reader's freedom to wander and gives you the presenter's voice in exchange. Use both facts.

## Four dimensions of quality

- **Writing:** the titles, read in sequence, are the argument. The slide text is what the room reads while the presenter talks: short, concrete, one idea. Everything else goes in the speaker notes.
- **Slides:** the frame feels considered, with room to breathe. Layout follows the idea. Nothing decorative competes with the content.
- **Visuals:** every stage, figure and diagram teaches the idea its slide asserts, is honest about what is measured and what is stylised, and reads from the back of the room.
- **Teaching:** the audience starts where they are, meets a concrete instance before an abstraction, earns each reversal, and leaves with a question of their own.

## Form

**One idea per frame, and room around it.** Case's pages are about half whitespace. Slides built from a paper's paragraphs come out at five percent, with three ideas each and a font shrunk to fit. If a frame is crowded, separate the ideas into two frames. Never shrink the type to make something fit: the frame is fixed and the back row is far away. In this deck that means no font size, face or fit mode in `deck.js`; the theme owns them and `check_deck.py` flags any that appear.

**The frame does not scroll.** A frame is 10 × 5.625 in. Content that reaches the footline, where the progress bar and the frame number sit, is a bug, and PowerPoint draws it anyway: an overfull text box spills past its bottom edge without a word of complaint. The build estimates every text box's height and logs the ones that probably overflow; `shoot.py` then checks every page for ink in the band above the footline and names the page.

**Titles are assertions.** "Location accounts for the gradient", not "Results: fixed effects". A reader who flips through the titles alone should get the argument. Dividers carry the chapter headings; frames carry claims.

**Let the idea choose the layout.** Prose beside a stage for an idea that needs a picture and a sentence. A figure full width with one line under it when the figure is the point. A single assertion in large type when the sentence is the point. Two columns when the idea is a contrast. Stat cards when a number should land. A numbered claim list only on the literature frame, if there is one, and the conclusion. If three frames in a row use the same layout, ask whether the ideas really have the same shape.

**Slide text is for the room, notes are for the presenter.** Two to four short sentences on the frame. The transitions, caveats, what to say about the stage, and the answer to the obvious question go in the frame's `notes`, which become PowerPoint's speaker notes. A frame with a paragraph on it makes the room read instead of listen.

**Every evidence frame has a source line.** A `source` or `figcap` saying what is plotted, what the sample is, and where the estimate comes from; a stage's own caption counts. In an academic room this is what earns trust, and it is what lets the printed handout stand alone.

**Numbers have one home.** Every number a chart draws and every number a sentence quotes comes from `data/numbers.js` and the CSV files it loads, through `{{path}}` in prose and `D` in the charts. Decks drift when the same figure is typed three times; when one changes, grep for the old one.

## Narrative

**Three acts, as in the playbook.** Open with a question the room wants answered before you answer it. Climb one step at a time, concrete first. End with something they could only appreciate because of what they now know, and with their question rather than yours.

**Make the room bet.** Case's "place your bets" pattern becomes a question to the room before the reveal: a show of hands, a moment of silence. Write the bet into the speaker note and design the next step as the payoff. A reveal that follows a bet lands; a reveal that follows nothing is a chart.

**The concrete thread.** Two named characters, a specific firm, one year, one street: pick a concrete instance early and return to it. The instance is the bottom of the ladder of abstraction, and the room climbs back down to it whenever a coefficient stops meaning anything. Keep the same instance throughout. Introducing a new example on every frame costs the room the thing it had just learned.

**THEREFORE and BUT.** The frames link like a story, not a list. Each BUT is a reversal the room can see coming only once it arrives. Plan the turns in `plan.md` first; a talk with no BUT is a report.

**The tree becomes a spine and rooms.** The explorable's forks and doors have no place in a linear talk, but the questions that motivated them still arrive, from the room. Build the spine for the talk's length and put each side path in an appendix frame, a *room*. A room is reached by a link placed next to the thing that raises the question, `[detail](#label)`, and carries `back: 'origin'`. Rooms come after the `{kind: 'appendix'}` marker, so they are numbered A1, A2, … and the progress bar ends on the closing frame. The appendix is where the sandbox lives: the robustness frame, the alternative measure, the ablation, the other dataset, the thing the second questioner will ask about. The website's map and progress dots have no equivalent here; PowerPoint's slide sorter and the room links cover navigation.

**The static read must work.** Someone reading the printed handout, with no presenter, must be able to follow the argument. `deck-handout.pptx` keeps one slide per frame, the last step of every stage, which is why a stepped stage draws its finished state on its last step and never only on an earlier one. Every stage has a caption that says what it shows without anyone pressing a key.

## Stages, when the presenter holds the clicker

A PowerPoint deck built this way has no sliders. What a stage can do is change between steps, each step its own slide under the same frame number, and that is enough: the presenter advances, the room watches one thing change, the presenter says what it means. This changes what a stage is for.

**One dimension of change per stage.** A build-in, a handle that moves along a line, a toggle between two states: one thing changes, three or four steps at most, and each step is a point the presenter would have stopped at anyway. Two things changing at once is a demo the room cannot follow, and six steps is a flip book.

**Large and legible.** Chart text at 9 to 10 pt on a 10 in frame reads from the back; nothing can be hovered. If the room has to see a number, draw it as a label on the chart.

**Build-ins where the reveal is the argument.** A stage that completes on its second step is the deck's version of Case's slow reveal, and it is powerful exactly once or twice per talk: the payoff after the bet, the moment the second bar catches the first. Everywhere else, draw the finished state. Releasing one bullet at a time is the slide equivalent of click-to-reveal-the-next-sentence, which Case calls crap-interaction: use a step only when the thing revealed is the BUT.

**Hand-author the starting state.** Step 1 is where the picture is most interesting, the toggle starts on the side the room expects, so the first step is the reversal. The last step is the finished state, and it is what the handout prints.

**Nothing moves between steps except the thing that changes.** Every step of a stage is drawn from the same data domains into the same box, so axes and labels register exactly on top of one another; a chart that computes its domain from what is visible on the current step will jump. Set the domain from the full data, and keep a card inside the plot area on every step. Compare consecutive screenshots of every stepped stage to be sure.

**Speaker notes say what to do.** Every stage's note names the steps, what the room should notice at each, and what to say if the projector loses one. A stage without instructions is a stage the presenter will click through.

## Visuals

**Colour encodes the argument and nothing else.** Choose at most four semantic colours, name them for what they mean in the topic, and paint everything else grey. The theme ships with `primary`, `contrast`, `actora`, `actorb`; alias them to the topic's words in `deck.js` (`aliases: { gain: 'primary' }`), because a chart author who writes `gain` writes the argument into the chart. A second channel, the hatch or a dashed line, can carry a second distinction; more than two channels is decoration.

**Say what is stylised.** A stage that draws the source's slope around an illustrative level says so in its caption. A chart that shows synthetic data with the right shape says so. When the source reports a slope or a gap but no level, draw the gap or an index (purchase = 100), not a level: an invented level produces a total the room can check against what it knows, and that is the number they will remember. If a level is needed, take it from a source figure's axis and say where it came from. This is the Victor half of the playbook: the model is honest and inspectable even when it is simplified.

**The source's own figures belong in the deck.** `convert_figs.sh` copies a PDF figure in, `restyle_figs.py` recolours it into the deck palette and drops the plot-region tint so it sits on the slide, and it is rendered to a PNG that PowerPoint can place. Raster figures (micrographs, screenshots, photos) go in unchanged. A recoloured figure from the source beside three sentences of prose is often the strongest evidence frame, and it costs nothing. A multi-series figure is the exception: its series colours are not the deck's and would give the four semantic colours a fifth meaning. The recolour script turns them into greys by default; if the series then cannot be told apart, redraw the figure as a stage in the palette. The source's in-figure notes (test statistics, sample lines) belong in the speaker notes, and a figure that carries them is another candidate for a redraw. Use a stage when the idea needs steps, a handle, or a comparison the source's figure does not draw.

**Diagrams draw the mechanism.** A causal loop, two boxes and an arrow, a floor and a ceiling: drawn with the library's shapes in the deck's palette (`L.rrect`, `L.line`, `L.label`), not pasted from elsewhere. If a diagram needs a legend to be read, it has too many parts.

## What goes wrong

Recurring faults from decks built this way. Check for each when reviewing.

- Frames with two or three ideas and a paragraph of prose, because a paper's paragraph was pasted in whole.
- Titles that are labels ("Data", "Results") in a deck whose other titles are claims.
- The same prose-left, chart-right layout on eight consecutive frames.
- A number in the prose that disagrees with the chart beside it, because each was typed separately instead of read from `data/numbers.js`.
- A stage with no caption, so the handout shows a chart with no meaning.
- A stepped stage whose finished state is drawn on step 1 and not on the last step, so the handout shows the wrong picture.
- A chart whose axis jumps between steps because its domain was computed from the visible elements.
- A chart that threw and shows only "This chart failed to draw", unnoticed because nobody read the build messages or the screenshot.
- An appendix frame before the `{kind: 'appendix'}` marker, so the progress bar says the talk is half over when it is nearly done.
- A font size or face set in `deck.js`, which is the sign that two frames were forced into one.
- A text box that spills below its column, which PowerPoint draws without a word; the build's estimate and the footline check are the two nets.
- A colour used because it looked nice, meaning nothing, next to four colours that mean something.
- Speaker notes that repeat the slide text instead of saying what to do and what to say.
- A stylised total, invented to have a level to draw, that a room in the field knows is wrong.
- Plan and notes that count frames while the screenshots count slides, so a note points at the wrong one: the listing from `shoot.py` gives both, and the plan uses frame numbers.
