/* data/numbers.js — the single home of every number the deck uses.
 *
 * Charts read this object; prose reads it with {{path}} ({{reveal.gap}},
 * {{ladder.0.beta:3}} for three decimals). Say in a comment where each
 * number comes from (table, column, row). Prose numbers that are not in a
 * chart are transcribed from the same tables, never from another slide. When
 * a source number changes, change it here and grep deck.js for the old value.
 *
 * If an explorable or a Quarto deck already exists for this topic, replace
 * this object with its data object (and port its model functions) so the two
 * never disagree.
 *
 * Tables: table('name.csv') reads data/name.csv into an array of row objects
 * with numeric cells coerced; {{ladder.0.beta}} then reads row 0, column beta.
 */
const table = require('../theme/csv');

module.exports = {
  // ---- stack-reveal: two cases, each with two components of a total (units per year)
  // Source: <table and column>. Slopes are the source's; levels are stylised around sample means.
  reveal: {
    unit: '% per year',
    partLabels: ['first component', 'second component'],
    cases: [
      { name: 'Case A', color: 'actora', parts: [2.8, 5.8] },
      { name: 'Case B', color: 'actorb', parts: [4.1, 4.5] },
    ],
    gap: 1.4,            // a.parts[0] − b.parts[0] rounded: the number the prose quotes
    note: 'Slopes are the source’s estimates. Levels are stylised around the sample averages.',
  },

  // ---- line-handle: y = a + b·(x − x0) over [xmin, xmax]; the handle stops at three x values
  // Source: <table, specification>. The slope b is the estimate; a is an illustrative level.
  line: {
    a: 6.0, b: 0.45, x0: 10,
    xmin: 2, xmax: 18, ymin: 0, ymax: 12,
    stops: [5, 10, 15],
    xlabel: 'position (units)', ylabel: 'outcome (units)',
  },
  // stylised dots for the line-handle stage (seeded draw around the line; see data/README.md)
  linedots: table('line-dots.csv'),

  // ---- ladder: an estimate as controls are added (cumulative down the rows)
  // Columns: spec label, beta, se, sig (1 if the source's table marks it at 5 %, else 0).
  ladder: table('ladder.csv'),
  ladderMeta: {
    xlabel: 'coefficient on X (units)',
    span: '3 to 1',      // the span between the two cases, quoted on the stats frame
  },
};
