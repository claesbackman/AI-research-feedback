# Data on the site

## The three tiers

| `data.tier` | What the site carries | When to choose it |
|---|---|---|
| `0` | No data files. Figures are the paper's images. Tables are HTML and download as CSV. | The default. Always right when the underlying numbers are restricted or the author is unsure. |
| `1` | Chosen figures are drawn in the browser from aggregate CSV tables. Each gets hover values, a table view, a CSV download and a link to the paper's image. | The analysis already writes the plotted numbers to CSV (coefficient tables, event-study estimates, group means). |
| `2` | Tier 1 plus one explorer page over a long-format aggregate table. | The paper has a natural cube of results, such as country by year by group, that readers will want to slice. |

A figure with no entry under `data.figures` keeps its static image at every tier. It is fine
to make two figures interactive and leave ten as images.

## Disclosure rules

The output folder is published as it is. Treat every file in its `data/` folder as public
forever, since copies persist after deletion.

1. **Aggregates only.** Point estimates, intervals, cell means, shares, binned counts. One
   row per estimate or per cell, never one row per person, household, firm or response.
2. **Only what the paper already reports or draws.** The site is not the place to release
   new numbers. If a table is finer than anything in the paper, ask the author.
3. **Restricted sources need the author's explicit yes.** Administrative registers,
   proprietary data, survey microdata under a licence: output from these is often subject to
   disclosure review (minimum cell sizes, export approval). Ask whether the file has been
   cleared for publication. If the author is not sure, use tier 0.
4. **Show before publishing.** For each source, tell the author the file, the columns that
   will be published and the row count, and get a yes.

`site_data.py` enforces a floor under these rules. It stops the build, before any page is
written, when a source

- has more than `data.max_rows` rows after filtering (default 2,000),
- has a published column whose name suggests an identifier (`id`, `pnr`, `cpr`, `ssn`,
  `email`, `address`, `birthdate` and similar),
- has a count column (`n`, `obs`, `count`, `cell_n`, …) below `data.min_cell`, if that key
  is set. Set it when the data provider has a minimum cell size, for example `"min_cell": 5`.

A refused source writes nothing to the site, and data files from an earlier build that are
no longer configured are deleted.

`"confirmed_aggregate": true` on a source passes the first two checks. Set it only after the
author has confirmed the file is an aggregate that may be published. The minimum cell size
cannot be overridden. Pool or suppress the cells instead.

Only the columns named in the entry are written to the site. The source file is never
copied.

## Figure entries

```json
"data": {
  "tier": 1,
  "max_rows": 2000,
  "figures": {
    "fig:main-coef": {
      "file": "../../output/tables/tab_main.csv",
      "type": "coef",
      "label": "country", "value": "estimate", "lo": "ci_lo", "hi": "ci_hi",
      "scale": 100, "digits": 1, "sort": "descending",
      "x_title": "Difference from the baseline (percentage points)",
      "columns": ["p_value"],
      "description": "Country effects with 95 percent intervals"
    }
  }
}
```

The key is the figure's `\label`. Files are CSV (comma or semicolon) or TSV, with a header
row. Stata: `export delimited`. R: `write.csv`.

Chart types and the columns they need:

| `type` | Draws | Required | Optional |
|---|---|---|---|
| `coef` | One row per category, a point with an interval | `label`, `value` | `lo`, `hi`, `series`, `sort` |
| `bar` | One row per category, a bar from zero | `label`, `value` | `lo`, `hi`, `series`, `sort` |
| `line` | Lines over a numeric x, with a shaded band | `x`, `y` | `lo`, `hi`, `series`, `ref_x`, `zero` |
| `event` | Points with intervals over a numeric x (event study) | `x`, `y` | `lo`, `hi`, `series`, `ref_x`, `zero` |
| `scatter` | Points, optionally labelled, optionally with a fitted line | `x`, `y` | `label`, `series`, `fit` |

Options for every type:

- `series`: a column that splits the marks by colour, with a legend. Up to five levels read
  well.
- `group`: a column whose levels become buttons above the chart, one level shown at a time.
  `group_title` labels the buttons. Use it for "by outcome" or "by sample" variants of one
  figure.
- `filter`: `{"column": "value"}` or `{"column": ["a", "b"]}`, applied before anything else.
- `scale`: multiply `value`, `lo`, `hi` and `y` (for example 100 for percentage points).
- `digits`: decimals in hover values and the table view. `round`: decimals kept in the file.
- `x_title`, `y_title`: axis titles. Write them as the paper does, with units.
- `sort`: `"descending"` or `"ascending"` by value. Without it, rows keep the file's order.
- `ref_x`: a dashed vertical line, for example the last pre-treatment period.
- `zero`: for `line`, `event` and the explorer, `true` forces zero into the axis. `coef`
  includes zero unless `zero` is `false`. `bar` always starts at zero.
- `count`: the name of the column that holds the cell count, when `data.min_cell` is set
  and the column is not called `n`, `obs`, `count` or similar. The build stops if
  `min_cell` is set and it cannot find a count column.
- `columns`: extra columns to publish in the CSV without plotting them (p-values, N).
- `description`: the line shown in the data table on the data and code page.

Choosing: a figure that shows estimates by group is `coef`. Dynamic effects around an event
are `event` with `ref_x`. A time series is `line`. A cross-section of two variables is
`scatter`. If a figure fits none of these (maps, heatmaps, densities, multi-panel
composites), leave it static. A forced fit that looks different from the paper's figure
confuses readers more than an image does.

After the build, compare each drawn figure with the paper's image, which is one click away
under the figure. Same ordering, same sign convention, same units. If they differ, the
entry is wrong.

## The explorer (tier 2)

```json
"explorer": {
  "title": "Results explorer",
  "file": "../../output/tables/cell_means.csv",
  "dimensions": ["country", "year", "group"],
  "value": "mean", "lo": "ci_lo", "hi": "ci_hi",
  "value_label": "Mean outcome",
  "labels": {"country": "Country", "year": "Year", "group": "Group"},
  "defaults": {"year": "2020"},
  "rows_dim": "country", "color_dim": "group",
  "digits": 2,
  "description": "Cell means by country, year and group"
}
```

The table is long format: one row per cell, a column per dimension, one value column. The
reader chooses which dimension goes on the rows, an optional dimension for colour, and one
level or "All (average)" for each remaining dimension. "All" is the unweighted mean of the
cells shown, and the page says so. If an unweighted mean of cells is not meaningful for
this table (for example cells of very different size), give every dimension a default level
in `defaults` and say in the page's lead sentence what one point is.

Three or four dimensions work. With more, drop the least interesting ones with `filter`.
The view is kept in the page address, so a reader can link to a particular slice.

Fill in `content/explorer.html`: the title and one sentence that says what the table is and
what one point is. The explorer script is `theme/explorer.js` in the project's copy. Adapt
it when the paper needs something specific. The scripts load their data with script tags,
not `fetch`, so the site also works when opened from disk.

## The data and code page

`@@DATA_FILES@@` in `content/about.html` becomes a table of every published file with its
contents, row count and columns. Under it, write what the numbers are and, in the next
panel, what is not released and how a researcher can get access. This page is what a reader
looks for when deciding whether the results can be checked, so be exact.
