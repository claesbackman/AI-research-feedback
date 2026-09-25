# The Explorable Explanations Playbook

Distilled from Nicky Case ("How I Make Explorable Explanations" 2017, "Explorable
Explanations: Design Patterns" 2014, "4 More Design Patterns" 2018, "I Do And I
Understand" 2015, "Neurotic Neurons: Design Patterns" 2015, "Why Simulate?" 2016,
OpenVisConf 2016 talk), Bret Victor ("Explorable Explanations" 2011 + 2024 postscript,
"Up and Down the Ladder of Abstraction" 2011, "Magic Ink"), Steven Strogatz ("Writing
about Math for the Perplexed and the Traumatized" 2014), and the explorabl.es hub.

Read this once per project. It explains *why* the rules in the other references exist,
so you can apply them with judgment rather than mechanically.

## Contents

1. What an explorable explanation is (and isn't)
2. The three-act arc
3. Empathy: who you are writing for
4. Message → mechanics
5. The ladder of abstraction
6. Interaction craft (what playtesting taught Case)
7. Simulation: what it is for
8. The two visions: pedagogy vs. argument
9. Case's 2017 wishlist — the frontier this skill targets
10. Design patterns from the 2014 and 2018 posts

---

## 1. What it is (and isn't)

The hub's working definition: something that (1) teaches something and (2) is more
interactive than a quiz with one right answer. Confucius via Case: *I hear and I forget.
I see and I remember. I do and I understand.* The medium's comparative advantage is
**procedural rhetoric** (Ian Bogost) — an argument made by letting the reader operate a
system and discover its consequences, rather than being told them.

It is **not** gamification. Gamification changes *behaviour* with extrinsic rewards
(points, badges, streaks); explorables change *knowledge* by tapping intrinsic motives:
curiosity, mastery, autonomy, expression, purpose. No gold stars.

It is **not** "interactive for the sake of interactive." Victor's "Magic Ink" has a
section titled *Interaction Considered Harmful*. Interaction costs the reader effort;
spend it only where manipulating the system teaches something text or a picture cannot.

**Do & Show & Tell.** Each medium has a job:
- Text — abstract concepts.
- Graphs — broad relationships at a glance.
- Animation — temporal relationships.
- Interactives — *processes, systems, models* (cause-and-effect you can poke).
Use the cheapest medium that does the job, and let them overlap (text that drives a
diagram, a diagram that annotates text).

**The static read must work.** Victor: the piece should read as a normal explanation if
the reader never touches anything. The reader interacts to go *deeper*, not to get the
*basics*. No UI elements screaming for attention; no being teleported into a separate
"interactive mode." The author holds up their end of the conversation — a bare sandbox
with "figure it out" is not an explanation.

## 2. The three-act arc

**Act 1 — Start with 🤔.** Make the reader *love the question* before you answer it
(Strogatz). Traditional teaching fails because "it answers questions the student hasn't
thought to ask." The question can be blatant ("how do you share an idea?"), a story
(*Evolution of Trust*: how did WWI soldiers create peace in the trenches?), or a game
(*Parable of the Polygons*: drag shapes, notice something odd). The hook requires **zero
prior knowledge** — Mathigon's chocolate-box game is fully playable by someone who has
never heard of game theory.

**Act 2 — Up the ladder, slowly.** Give a **concrete experience first** — and pick it so
everything later builds on top of it (Polygons: drag shapes in one neighborhood; every
later section reuses that same neighborhood with changed rules). Then climb one step at a
time. Do not talk in the clouds while the reader is on the ground. The goal is not to
"dumb ideas down" but to "smart people up."

The steps are linked like a story, not a list. Stone & Parker: never "this happens, and
then that happens." Always **"this happens, THEREFORE that happens, BUT that happens,
THEREFORE…"** Each BUT is a counter-intuitive reversal — a *mechanical plot twist* the
reader proves to themselves by operating the system. *Trust* chains them: you both win
by cooperating BUT in one round you both cheat BUT repeated play rescues cooperation BUT
cheaters win short-term BUT cooperators win long-term BUT… A good explorable shows a new
counter-intuitive idea every few minutes.

Sometimes step back **down** from abstract to concrete (see §5).

The arc repeats at every depth: each new level opens with a question the reader now has
because of what they just understood. Case's pieces are short because each carries one idea;
in a tree, this arc is the shape of a *path*, and a subject holds many.

**Act 3 — End with 🤔.** A sandbox. "In the beginning I give the player *my* question;
at the end I want them to explore *their own*." The ending should be something the reader
could only appreciate *because* of what they learned (Earth Primer's final sandbox only
makes sense once you know the ecosystem). The true value of an open ending: *it lets the
student go beyond the teacher.* Learning starts with 🤔 and ends with more 🤔.

## 3. Empathy: who you are writing for

Strogatz's three audiences:
- **The traumatized** — humiliated by the subject somewhere; "I'm just not a math person."
- **The perplexed** — no scars, it just felt pointless; followed directions, never saw why.
- **The naturals** — it makes sense and gives them pleasure.
Almost all popular explanation is written for the naturals. The first two are underserved
and are usually the real audience. **Name which one you are writing for.** It changes
tone: the traumatized need Feynman's "it's okay not to know, that's where it gets
exciting"; a natural finds that patronizing.

Explaining well "is not mainly about the logic and clarity of the explanation (necessary
but not sufficient). It requires empathy." Three routes:
1. **Illuminate** — deliver an Aha. Often verbal: *ir-ratio-nal* numbers are those that
   aren't a ratio; *squared* because that many things form a square.
2. **Make connections** — tie it to what the reader already loves (sports, music,
   history). This sends the message *you are welcome here even if you don't care about
   the subject.*
3. **Treat the reader as a non-expert friend.** Then tactical choices make themselves:
   minimize symbol manipulation; recast ideas pictorially; avoid symbols the reader can't
   pronounce (they stop reading); don't number figures (textbook feel); put the diagram
   *in the text next to the words it illustrates*, never off at the top of the page;
   cartoonish levity refreshes the reader when the going gets tough.

Three stylistic heroes: **Feynman** (conversational voice; honest about the unknown;
master of illumination), **Gould** (hooks sideways with something light — a word, a
joke — then slides into the real subject), **Lewis Thomas** (rhythm and surprising
juxtaposition). Their common secret: they help us love the questions they're asking.

## 4. Message → mechanics

From "I Do And I Understand," the exercise that turns an idea into a playable:

1. **State the idea as a Cause → Effect chain.** "Wider audience → fewer common interests
   → more generic art." If you can't, you don't yet know what you're teaching.
2. **Turn the chain into rules.** If the chain is good, the rules are almost obvious.
   *Polygons*: (a) triangles and squares live on a grid; (b) each wants to move if fewer
   than ⅓ of neighbors are like it; (c) move unhappy shapes to random empty spots until
   nobody wants to move. Playing the rules *is* the argument — readers don't get told the
   twist, they produce it. Requirements: the **model must be visible** (whole state on
   screen — spatial if at all possible); **start simple, add complexity as the reader
   progresses**; don't apologize for simplifying — a street map is useful *because* it is
   simplified — but **acknowledge the limitations** on the page.
3. **Package it.** Don't worry about making "a real game"; form follows the message.
   Consider a narrative — characters make the abstract concrete and emotionally
   resonant. Framing controls how the lesson lands (the Arts example must not read as
   "the masses are dumb").

Case's reference examples: *The Landlord's Game* (Monopoly's origin — rent rules that
inevitably produce a monopoly), *Depression Quest* (energy level gates which choices are
available; the feedback loop becomes visceral), *Polygons* (three plot twists from three
rules plus one added rule that provides a hopeful ending).

## 5. The ladder of abstraction (Victor)

A systematic method for interactive visualization. Every system has three axes: an
**independent variable** (usually time), a **structure** (the rules/algorithm, with
parameters), and **data** (the environment/input). For each:

- **Control it.** Direct, interactive control — go forward and back, stop, jump. "We must
  not be slaves to real time." Control forces you to name your parameters.
- **Step up.** Devise a representation that shows the system for *all* values of a
  parameter at once (the car's whole trajectory instead of the car; overlaid trajectories
  for every turning rate; a metric like time-to-completion plotted against the parameter).
  Different abstractions reveal different patterns; offer more than one.
- **Step down.** Point at a spot on the abstraction to recover the concrete instance.
  "In real life you would never use a ladder that only let you go up." Insight is born
  **in the transitions** — you climb to *see* a pattern and descend to *explain* it.
  Always be able to get all the way back down to the fully concrete; surprises hide in
  details that fell through the abstraction.
- **Iterate.** Start with the absolutely simplest algorithm, explore it thoroughly (you
  learn *why* it's terrible), then make one small change and explore again.

Visual abstraction beats symbolic for intuition: the brain is a pattern-matcher; a plot
"quietly becomes more accurate" as the model improves while an equation explodes in
symbols.

## 6. Interaction craft (what playtesting taught Case)

From *Neurotic Neurons* — nine months of failed prototypes, then four weeks of the version
that worked:

1. **Huge possibility space.** Three clickable things felt like "an obtuse animation," not
   a system. Thirty neurons clickable in any order felt alive.
2. **Direct manipulation.** Click → neuron fires. Not click → character reads book →
   signal flies → neuron fires. Zero in-betweens.
3. **Juice.** Every interaction produces a generous, reactive response — visual and, where
   there is a narrator, verbal. Hand-author the starting state so the reader's *first*
   click is rewarding.
4. **Always be interactive.** Apart from a few seconds of intro/outro, something is
   always pokeable — even while text is "talking."
5. **No crap-interaction.** A click with no meaningful choice (click-to-advance, click-to-
   reveal-the-next-sentence) is crap. Exceptions: deliberate anticipation or panic. If
   the reader *must* see something, animate it automatically and let them interact
   optionally.
6. **Keep mechanics consistent; enforce constraints with mechanics you already taught.**
   Don't lock things with special-case rules — use spatial distance, an existing rule,
   something already established. Don't toggle rules on and off between sections.
7. **Clarity > cleverness.** Kill the cute metaphor that confuses people. And: **more
   clarity ≠ more exposition** — over-explaining made readers pay *less* attention and get
   *more* confused later.

From the 2014 workshop: **playtest**. Earth Primer's readers skimmed, skipped things they
didn't know, and got confused; adding content gates paradoxically made them learn *more*.
The "90% crap rule": most of the work is discarding what didn't work. This skill cannot
watch humans, so it simulates the specific failures they reveal with independent reviewers.

## 7. Simulation: what it is for

Six functions (Case): exploration (what if?), explanation (how does?), emergence,
prediction (overrated), creating futures, role-play. Simulations explain **processes** —
things that happen over many small steps. Don't use a flamethrower for a birthday candle:
if a causal loop diagram or a numbered list explains it, use that.

Systems are **loopy**, not linear: A affects B, and B affects A. Vicious and virtuous
cycles. In a loopy system there is no single root cause — which means change can start
anywhere. Simulation can **combine contradictions**: *Polygons* shows low individual bias
and high collective bias are two views of one system, so you can't understand one side
without the other. That is stronger than "presenting both sides."

Five tools for systems storytelling, cheapest first: non-interactive narrative with
multiple perspectives → causal loop diagrams → stock & flow models → probability
simulations → agent-based simulations.

## 8. The two visions

Case's explorables are **pedagogical**: the author knows the lesson and designs a path to
it. Victor's 2011 definition is **argumentative**: "a written argument whose assertions
are backed by explorable computational models, whose facts, assumptions and calculations
are all visible and editable" — the reader's role is to *critically evaluate and rebut*,
by modifying the model. His 2024 postscript laments that the term now means "any article
with interactive pictures."

Hold both. Teach clearly (Case), and make the model honest and inspectable (Victor): the
sandbox should expose the parameters the argument depends on, and the page should say
where the simplification breaks. A reader who can break your model has learned more than
one who can only confirm it.

## 9. The frontier (Case's 2017 wishlist)

Things Case wanted and couldn't yet build — and that this skill is designed to attempt:
explorables that adapt to the reader's interests and prior knowledge (non-linear);
explorables that use real data; that pose *problems*, not just puzzles; that are
partially reader-generated; that enable dialogue between learners; that are revisited
over time rather than consumed once. The tree structure, per-reader persona, shareable
state and sandbox-with-exposed-parameters in this skill are direct responses to that list.


## 10. Design patterns from the 2014 and 2018 posts

These two posts collect patterns for putting the ideas above into practice. The 2014 post includes seven patterns and two supporting notes; the 2018 post adds four more.

### The original patterns (2014)

Source: [Explorable Explanations](https://blog.ncase.me/explorable-explanations/), September 8, 2014. Case collected these patterns and considerations at a workshop.

- **Do & Show & Tell.** Choose text, graphics, animation, or interaction for what each explains best; let them work together.
- **Interest Curves.** Open with an accessible hook, develop the basics, and finish with something the reader can now appreciate.
- **Start small, build big.** Teach individual mechanics, then combine them: A, B, A+B, C, A+C, B+C, A+B+C.
- **See, Model, Apply.** Let readers generate observations, infer a pattern, and use it. In Angry Physics, shots build a graph; targets give that understanding a use.
- **Cognitive Gates.** Give readers time to investigate and acquire prerequisites before moving into material that depends on them.
- **Author-guided & Player-driven.** Readers choose their actions within an experience whose structure the author shapes.
- **Procedural Rhetoric.** Guide discovery through goals, rules, and available actions.

Two supporting notes:

- **Playtesting.** Watch people use the explanation; skipped prerequisites may reveal where gates help.
- **Gamification.** Distinguish learning from behaviour change. Consider achievement, exploration, social connection, and competition as overlapping motivations, not fixed reader types.

### Four more patterns (2018)

Source: [Explorable Explanations: 4 More Design Patterns](https://blog.ncase.me/explorable-explanations-4-more-design-patterns/), June 20, 2018.

- **Puzzle It Out.** Give readers a problem that requires understanding the system, rather than following prescribed steps. In SineRider, shaping curves to guide a sled makes the relationship between equations and curves useful. This suits subjects that can be simulated, including mathematics, programming, and science.
- **Place Your Bets!** Ask for a prediction before revealing the outcome. The difference between an expectation and the result gives the reader something to think about. Examples include drawing an expected graph in You Draw It and predicting winners in The Evolution of Trust. This works when the outcome can be checked.
- **Role Play.** Put readers inside a dilemma and let them make decisions under its constraints. A Syrian Journey explores refugees’ choices. This suits ethical, political, and philosophical questions without a single correct answer.
- **Sandbox Mode.** Let readers pursue their own questions or creations. Avoid overwhelming beginners: make the simulation simple enough to enter immediately, or introduce its parts gradually before opening the full sandbox. Examples include Learning Music and Earth Primer.
