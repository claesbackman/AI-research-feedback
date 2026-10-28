/* theme/theme.js — the explorable deck theme for PowerPoint.
 *
 * Colour encodes the argument and nothing else. Four semantic colours, named
 * generically here. Do not rename them: layouts.js, the charts and the notes
 * reference depend on the names. Instead give each one a topic alias in
 * deck.js (aliases: { gain: 'primary', ... }) and paint the charts with the
 * alias, so that whoever writes a chart writes the argument into it:
 *     primary    the quantity the talk is about
 *     contrast   its counterweight or the second component
 *     actora     the first character or group
 *     actorb     the second
 * Everything else is paper and ink.
 *
 * Hex values without '#': pptxgenjs corrupts the file on a leading '#'.
 * Keep them in step with figs/restyle_figs.py if the palette changes.
 */
module.exports = {
  colors: {
    paper: 'FFFFFF', paper2: 'F7F7F7', paper3: 'ECECEC',
    ink: '1C2224', ink2: '4B5457', ink3: '667074', line: 'C9CEC6',
    primary: 'C4452A', contrast: '128F78', actora: 'B8760A', actorb: '3A63B8',
    primarysoft: 'F2D9D2', contrastsoft: 'CFE9E2', actorasoft: 'F1E3C6', actorbsoft: 'D6E0F4',
  },

  // Four faces, all shipped with Microsoft Office on Windows and macOS, so the
  // deck renders the same on any machine with PowerPoint and nothing has to be
  // installed or embedded: a heavy grotesque for titles and big numbers, its
  // book weight for labels, a serif narrator for body text, a mono for numbers.
  // A deck shown only on machines with Fira Sans, Libertinus Serif and IBM
  // Plex Mono installed may name those here instead; LibreOffice substitutes
  // all four with different metrics, so screenshots made through it are
  // approximate (see the notes reference).
  faces: {
    display: 'Franklin Gothic Demi',
    label: 'Franklin Gothic Book',
    body: 'Georgia',
    mono: 'Consolas',
  },

  // Point sizes on a 10 × 5.625 in canvas (the 16:9 default). Body text at
  // 14 pt here is what 9 pt is on a 160 mm beamer frame. No frame may set its
  // own sizes: what does not fit at these sizes is a second frame.
  sizes: {
    title: 26, titleSlide: 36, subtitle: 16, author: 14, institute: 11,
    divider: 40, assertion: 30, eyebrow: 9.5,
    body: 14, q: 19, colhead: 14, claim: 14, aside: 12,
    source: 9.5, figcap: 11, stagecap: 10, legend: 9.5,
    stat: 40, statLabel: 12, bignum: 52, bignumLabel: 11,
    tick: 9, axisLabel: 9, dataLabel: 9.5, card: 9.5, cardStrong: 10.5,
    foot: 8, back: 9.5,
  },

  // Geometry in inches. Content sits between contentY and H − footline − guard;
  // shoot.py treats any ink in the guard band (the 0.2 in above the footline)
  // as content touching the bottom of the frame.
  geo: {
    W: 10, H: 5.625,
    mx: 0.6,                 // left and right margin
    titleY: 0.42, titleH: 0.9,
    contentY: 1.4,
    footline: 0.5, guard: 0.2,
    gap: 0.35,               // between columns
    narrow: 0.36, wide: 0.60, // column shares of the text width (beside / wideleft)
    stage: { h: 3.3, tall: 3.55, short: 2.4 },
    fig: { h: 3.2, tall: 3.5, pair: 2.6 },
    capH: 0.36,              // height reserved for a stage caption
    legendH: 0.26,
    lineHeight: 1.22,        // multiple of the point size, for height estimates
    paraSpace: 7,            // points after a paragraph
  },
};
