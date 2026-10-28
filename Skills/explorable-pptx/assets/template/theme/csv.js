/* theme/csv.js — read a CSV into an array of row objects, numbers coerced.
 * Used by data/numbers.js:  const table = require('../theme/csv');  table('ladder.csv')
 * Paths are relative to data/. A header row is required; quoted fields are
 * not supported (the deck's tables are small and hand-written).
 */
const fs = require('fs');
const path = require('path');

module.exports = function table(file) {
  const p = path.isAbsolute(file) ? file : path.join(__dirname, '..', 'data', file);
  const lines = fs.readFileSync(p, 'utf8').split(/\r?\n/).filter((l) => l.trim() && !l.startsWith('#'));
  const head = lines[0].split(',').map((h) => h.trim());
  return lines.slice(1).map((l) => {
    const cells = l.split(',').map((c) => c.trim());
    const row = {};
    head.forEach((h, i) => {
      const v = cells[i] === undefined ? '' : cells[i];
      row[h] = v !== '' && !isNaN(Number(v)) ? Number(v) : v;
    });
    return row;
  });
};
