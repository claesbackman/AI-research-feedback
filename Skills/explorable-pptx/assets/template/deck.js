/* deck.js — an explorable deck as PowerPoint. Build with: sh build.sh
 *
 * Every frame below demonstrates one layout from theme/layouts.js. Replace the
 * content, keep the patterns: one idea per frame, title as an assertion, a
 * note on every frame that tells the presenter what to do and say. A frame
 * with a stepped stage becomes one slide per step; the frame number in the
 * footline stays the same across its steps, and the handout keeps the last.
 *
 * Prose markup: **bold**, *italic*, `mono`, [text]{primary} (or an alias),
 * {{path}} / {{path:2}} for a number from data/numbers.js, [text](#label) for
 * a link to a room. Paragraphs are separated by a blank line.
 */
module.exports = {
  meta: {
    title: 'Deck title as a claim',
    subtitle: 'Venue, month year',
    authors: 'Author One · Author Two',
    institute: 'Institution · Institution',
    date: '',
  },

  // Topic aliases for the four colour tokens, one per token, in the topic's
  // words. Charts and prose use the aliases; the generic names stay.
  aliases: {
    // gain: 'primary', yield: 'contrast', anna: 'actora', bo: 'actorb',
  },

  frames: [
    { kind: 'title',
      notes: 'Slide 1 is the title: screenshot numbers, plan numbers and note numbers all start here.' },

    { title: 'The question the room wants answered before you answer it',
      layout: 'prose',
      prose: 'One or two sentences that make the room want the answer.',
      notes: 'The hook. Ask the room to commit: a show of hands, one sentence. Then advance to the payoff.' },

    { title: 'Two cases, one reveal',
      layout: 'beside',
      prose: `**Case A earned more on the first component.** About [{{reveal.gap}} points]{primary} a year.

**Case B earned more on the second.** The two components offset, leaving the totals [about equal]{contrast}.`,
      stage: 'stack-reveal',
      notes: 'Step 1 shows the first component only. Ask for the bet, then advance: the second component builds in. Let it land before speaking.' },

    { title: 'What the literature measures, and what this adds',
      layout: 'claims',
      claims: [
        ['First strand.', 'What it did and what it could not see.'],
        ['Second strand.', 'Where it stopped.'],
        ['This talk.', 'The object we observe that they could not.'],
      ],
      notes: 'One slide, three strands at most. Say why each stopped where it did.' },

    { kind: 'divider', eyebrow: 'Section 1', title: 'The first section as a claim' },

    { label: 'gradient',
      title: 'The gradient in one picture',
      layout: 'wideleft',
      fig: 'figs/example.png',
      prose: 'One sentence about what the figure shows.',
      stats: [{ k: '{{ladder.0.beta:3}}', l: 'unit, and the magnitude between two points the room can picture. The number is read from data/numbers.js.' }],
      source: 'What is plotted, the sample, the source table or figure.',
      notes: 'Replace figs/example.png with a source figure: sh figs/convert_figs.sh <source-dir> <Name>. The side room on robustness opens from here.' },

    { title: 'A line the presenter can walk along',
      layout: 'beside',
      prose: 'Step through the three stops. The card says what a unit at that position earns.',
      stage: 'line-handle',
      source: 'Dots are stylised around the estimated line. The slope is the source’s estimate.',
      notes: 'Three steps, one per stop. Stop at the two points named on the previous slide and read the card aloud. If the projector drops a step, say the three numbers.' },

    { title: 'Adding controls removes most of the slope',
      layout: 'beside',
      prose: 'Controls are cumulative down the rows. The last row is statistically indistinguishable from zero.',
      stage: 'ladder',
      source: 'Coefficient on X with 95 percent intervals. Specification details. [robustness](#robust)',
      notes: 'Read the rows top to bottom. The point is the last row, not the first.' },

    { title: 'Three numbers the room should leave with',
      layout: 'stats',
      stats: [
        { k: '{{reveal.gap}} pp', l: 'a year, between the two cases' },
        { k: '{{ladderMeta.span}}', l: 'the span those two cases sit apart', color: 'ink2' },
        { k: '≈ 0', l: 'the total gradient, statistically', color: 'contrast' },
      ],
      notes: 'A stat-card slide breaks a run of prose-beside-figure layouts. Three numbers at most, each with the magnitude a listener can feel.' },

    { kind: 'assertion', title: 'The one sentence: the return arrives in different forms, and where you can buy decides the form' },

    { title: 'Two readings of the same fact',
      layout: 'cols',
      left: { head: 'Reading [one]{actora}', prose: 'Two sentences on what it predicts.' },
      right: { head: 'Reading [two]{actorb}', prose: 'Two sentences on what it predicts instead.' },
      q: 'The test that separates them: what we look at next.',
      notes: 'Name the two readings, then the one observation that tells them apart.' },

    { title: 'Three things to take away',
      layout: 'claims',
      claims: [
        ['', 'The first finding, with its magnitude.'],
        ['', 'The second, and why it reverses the obvious reading.'],
        ['', 'What it implies, in one sentence.'],
      ],
      notes: 'End on the room’s question, not yours.' },

    { title: 'Closing claim, the sentence they should leave with',
      layout: 'prose',
      prose: '**Thank you.**',
      source: ['Name', 'Affiliation', 'email'],
      notes: 'Leave this up during questions; the rooms are one link away.' },

    // ------------------------------------------------------------ appendix
    // Frames after the marker are numbered A1, A2, … and leave the progress bar,
    // so the count ends on the closing slide.
    { kind: 'appendix' },
    { kind: 'divider', title: 'Appendix' },

    { label: 'robust',
      title: 'A side room: the robustness a questioner will ask about',
      layout: 'figpair',
      figs: ['figs/example.png', 'figs/example.png'],
      figcap: '**Left:** what. **Right:** what. Source.',
      back: 'gradient',
      notes: 'Opened from the ladder slide. Say what changes and what does not, then go back.' },
  ],
};
