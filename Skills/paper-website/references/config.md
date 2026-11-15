# site.json reference

All paths are relative to the folder that holds `site.json`. Only `main_tex` is required,
but a site without `title` and `authors` has an empty title page.

## Contents

1. The paper
2. Files
3. Links, footer and metadata
4. Theme and features
5. Structure and numbering
6. Pages
7. How the script reads the LaTeX
8. Troubleshooting

## 1. The paper

| Key | Meaning |
|---|---|
| `title`, `subtitle` | Shown on the title page. The contents rail shows `title`. |
| `short_title` | Top bar and browser tab. Defaults to `title`. |
| `authors` | List of `{"name", "affiliation", "url"}`. `url` is optional. |
| `year`, `date` | `year` goes into the citation. `date` (`YYYY/MM/DD`) goes into the Google Scholar tag. |
| `edition` | For example `"Digital edition · November 2026"`. Shown on the title page and under the contents. |
| `status` | `"working paper"`, `"forthcoming in the Journal of X"`, and so on. Shown after the edition and used in the default citation. |
| `abstract`, `jel`, `keywords` | Leave empty. The script takes them from the `abstract` environment and from "JEL" and "Keywords" lines near it. Fill in (HTML allowed in `abstract`) only if the extraction is wrong. |
| `acknowledgments` | Leave empty: the script takes the `\thanks` (or `\footnote`) note of `\title` and shows it at the foot of the title page. Give HTML to replace it, or `false` to show none. Read the extracted note before publishing. A `\thanks` often carries a contact address or a remark meant for referees. |
| `citation` | `{"text": "...", "bibtex": "..."}`. Leave empty for a default built from title, authors, year and status. Write both by hand for a published paper (journal, volume, DOI). |
| `language` | The `lang` attribute, default `"en"`. |

## 2. Files

| Key | Meaning |
|---|---|
| `main_tex` | The root `.tex` file. `\input`, `\include` and `\subfile` are followed. |
| `appendix_tex` | The root file (or a list of files) of a separate online appendix. Its sections are added after the paper's own appendix, its figures and tables follow its own numbering commands, and references between the two files resolve, including the label prefixes of the `xr` package (`\externaldocument[OA-]{...}`). Its sections get the next appendix letters, so check them against the PDF. |
| `bib` | One path or a list. Leave empty to use the files named in `\bibliography{}` or `\addbibresource{}`. |
| `csl` | A citation style file. Default is Chicago author-date, which is close to AER style. |
| `pdf` | The compiled paper. Copied to `paper/` on the site and linked in the top bar. Also used by the checker to compare exhibit numbers. |
| `figure_dirs` | Extra folders to search for figure files, on top of the root file's folder and `\graphicspath`. |
| `output_dir` | Where the site is written. Default `../Website`. |

## 3. Links, footer and metadata

| Key | Meaning |
|---|---|
| `site_url` | The public address, with trailing slash. Needed for the canonical link, the social preview and the Google Scholar PDF tag. Leave empty until the address is known. |
| `links` | Top-bar links: `[{"label": "Replication package", "url": "https://..."}]`. Keep to two or three. |
| `bug_report_url` | Adds "Report a problem" to the top bar. A GitHub `.../issues/new` address gets the page title filled in. |
| `footer` | List of paragraphs (HTML allowed) under every page: funding, disclaimer, data statement. |
| `description` | The search-engine description. Default is "Digital edition of the paper …". |
| `social_image` | Path inside the site to an image for link previews, for example `figures/fig_main.png`. |

The footer always ends with the credit line, and the title page always ends with the full
citation of the skill. Neither is configurable.

The contents rail shows a version line under the edition: the date of the newest `.tex`
file and the git commit of the paper's repository, the date the site was built, and, when a
PDF is linked, a sentence that the PDF is the version of record. `"show_commit": false`
leaves the commit out. `@@PAPER_VERSION@@` puts the same line into a content page.

`"deploy": {"target": "../../../claesbackman.github.io/Explorables/MyPaper"}` names the
folder the site is published to. `update_site.py` prints the copy command and runs it with
`--deploy`. See "Updating an existing site" in SKILL.md.

## 4. Theme and features

```json
"theme": {"scheme": "signature", "accent": "", "typeface": "", "dark_mode": true},
"features": {"search": true, "outline": true, "previews": true, "cite_box": true, "table_csv": true}
```

- `scheme`: the whole look. `signature` (default) is warm paper, a vermilion accent, teal
  footnote marks, and chart colours vermilion, teal, blue and ochre, set in Bricolage
  Grotesque and Newsreader. It is the palette of the explorable decks in the same
  repository, so a paper's site and its slides look like one family. `classic` is white
  paper with a blue accent in IBM Plex. Schemes are the `SCHEMES` table at the top of
  `build_site.py`. To add one, copy an entry and change the colours, light and dark.
- `accent`: empty for the scheme's own, or `vermilion`, `blue`, `teal`, `burgundy`,
  `slate`, `green`, `ochre`, or `"#rrggbb"`. The script derives the link colour and the
  dark-mode variants.
- `typeface`: empty for the scheme's own, or `signature`, `plex`, `source`, `sans`,
  `system`. `system` loads no web fonts.
- `dark_mode`: `false` removes the toggle and keeps the site light.
- `search`: a search box over the full text. The index is one file, loaded on first use.
- `outline`: an "on this page" list of subsections on wide screens.
- `previews`: hovering over a citation shows the reference, over a figure or table number
  shows its title (and a thumbnail for figures), over a footnote mark shows the note.
- `cite_box`: the "Cite this paper" box on the title page.
- `table_csv`: a "Download this table (CSV)" link under every table.

For anything else (spacing, a logo, a different layout), edit `theme/site.css` in the
project's copy. Colours are CSS variables at the top of the file, with a dark block below.

## 5. Structure and numbering

```json
"structure": {
  "appendix_pages": "per-section",
  "appendix_marker": "",
  "nav_titles": {"sec:results": "Results"},
  "slugs": {"sec:results": "results"},
  "skip_sections": ["Acknowledgements"],
  "notes_commands": ["fignotes"]
},
"numbering": {"figure": "auto", "table": "auto", "equation": "auto"}
```

- Every `\section` becomes one page. The page address comes from the section title.
  `slugs` maps a section's `\label` (or pandoc's automatic id, the title in lower case with
  hyphens) to a shorter address. `nav_titles` gives a shorter title for the contents rail.
- The first build writes every section's address into `slugs` (the script edits
  `site.json` to do so), so that the address stays the same when the title changes. Set
  `"pin_addresses": false` at the top level to stop that. A page that disappears is
  replaced by a redirect to where its section went, or to the title page.
- `appendix_pages`: `"per-section"` or `"single"`. To leave the appendix out, list its
  section labels or titles in `skip_sections`.
- `appendix_marker`: a regular expression for where the appendix starts, for papers that do
  not use `\appendix`, `\begin{appendix}` or `\begin{appendices}`. Example:
  `"\\\\section\\*\\{Online Appendix\\}"`.
- `skip_sections`: section labels or titles to leave off the site. "References" and
  "Bibliography" headings are always skipped, the reference list has its own page.
- `notes_commands`: names of the paper's own macros that hold figure or table notes, without
  the backslash. Known already: `\caption*`, `\floatfoot`, `\figurenotes`, `\tablenotes`,
  `\fignote(s)`, `\tabnote(s)`, `\note(s)`, `\legend`, the `tablenotes` and `figurenotes`
  environments, a `minipage` without a graphic, and trailing text that starts with "Notes:".
- `numbering`: `"auto"` follows every `\renewcommand{\thefigure}{...}`, `\numberwithin` and
  `\setcounter{figure}{k}` in the order they appear in the source, so an appendix that
  restarts its numbering in each section (A1, B1, B2, C1) comes out as in the PDF. To override, give
  `{"main": "{n}", "appendix": "A{n}", "reset_in_appendix": true}`. `{n}` is the counter,
  `{sec}` the section number or appendix letter. With `{sec}` the counter restarts in every
  section.

## 6. Pages

```json
"pages": [
  {"slug": "explorer", "title": "Results explorer", "group": "explore"},
  {"slug": "faq", "title": "Questions and answers", "group": "notes"},
  {"slug": "errata", "title": "Errata and notes", "group": "notes"},
  {"slug": "about", "title": "Data and code", "group": "notes"}
],
"groups": {"explore": "Explore", "notes": "Notes"}
```

Each entry needs `content/<slug>.html`, the body of the page. An optional
`content/<slug>.json` can set `wide` (a wider column), `scripts` (script addresses to load),
`description` and `head`. If the author wants no extra pages at all, set `"pages": []`,
otherwise the default data and code page is expected. The title page is `content/index.html` and is always built. With
data tier 2 the explorer page is added to the list automatically.

Tokens the build fills in, in any content file: `@@TITLE@@`, `@@SUBTITLE@@`, `@@EDITION@@`,
`@@BYLINE@@`, `@@ABSTRACT@@`, `@@JEL@@`, `@@KEYWORDS@@`, `@@ACKNOWLEDGMENTS@@`,
`@@CITE_BOX@@`, `@@CITE_TEXT@@`, `@@CITE_BIBTEX@@`, `@@SITE_URL@@`, `@@PDF@@`,
`@@FIRST_PAGE@@`, `@@FIRST_TITLE@@`, `@@BUILD_DATE@@`, `@@DATA_FILES@@`, `@@CREDIT@@`.
`<!--IF JEL-->…<!--END-->` keeps its content only if that token is not empty.

A link to a label in the paper is written `<a href="#tab:main">Table 2</a>`. The build
points it at the page that holds the label. A button with `data-copy="some-id"` copies the
text of the element with that id.

## 7. How the script reads the LaTeX

- Comments are dropped and inputs inlined: `\input`, `\include`, `\subfile`, `\estinput`
  and any command the preamble defines with `\let\name=\input`. Floats inside
  `\afterpage{}` are unwrapped. The text before the first `\section` is the title
  page and is not converted, except the abstract.
- `\newcommand`, `\providecommand` and `\DeclareMathOperator` definitions from the preamble
  are passed to pandoc so the paper's macros expand. If pandoc fails on them, the build
  retries without and says so.
- Figures (`figure`, `figure*`, `sidewaysfigure`): label, caption, notes and every
  `\includegraphics` file. PDF and EPS graphics are converted to PNG at 200 dpi. Subfigure
  captions are kept as panel titles.
- Tables (`table`, `table*`, `sidewaystable`, `longtable`): label, caption, notes and every `tabular`,
  `tabularx`, `tabular*` or `tabulary` inside. Column specifications are reduced to left,
  centre and right. `\multicolumn` survives. `\multirow`, `\cmidrule`, `\sym`, `\tnote`
  and siunitx or dcolumn columns are simplified. A table that is an image is shown as an
  image.
- Equations: `equation`, `align`, `gather`, `multline`, `eqnarray`, `alignat`, `flalign`
  are numbered as LaTeX numbers them (every unstarred row without `\nonumber`).
- `\ref`, `\eqref`, `\autoref`, `\cref` become links with the PDF's number. A list such
  as `\cref{fig:a,tab:b}` becomes "Figure 1 and Table 2". A reference to a subfigure label
  becomes "1a" and links to the figure. `subequations` are numbered 2.4a, 2.4b, and an
  equation with its own `\tag{}` keeps it. `\pageref` and `\nameref` have no meaning on
  the site and come out empty. Rephrase around them if the paper uses them.
- Citations go through pandoc's citeproc with the paper's `.bib`. natbib and biblatex
  commands both work.
- The intermediate files `_preprocessed.tex`, `_pandoc.html` and `_update_report.md` are
  written next to `site.json`. Add them to `.gitignore`. Commit `.template.json`.

## 8. Troubleshooting

| Symptom | Usual cause and fix |
|---|---|
| "pandoc failed", with a line number | The line refers to `_preprocessed.tex`. Usually an unbalanced brace or an environment pandoc does not know. If the source is mid-edit, build from a clean copy of the writing folder. |
| Figure or table notes are missing | The paper uses its own notes macro. Add its name to `structure.notes_commands`. |
| Notes appear inside the caption | The notes are written inside `\caption{}`. Leave it, or move the split into the macro list if the paper has a pattern. |
| Appendix exhibits are numbered 9, 10, … but the PDF says A1, A2 | The counter is reset in a way the script did not see (a class file or package). Set `numbering.figure` and `numbering.table` by hand. |
| Appendix sections appear as sections 9, 10 | No `\appendix` in the source. Set `structure.appendix_marker`. |
| A table shows "could not be converted" | The body is loaded by a macro the script does not follow (for example `\estauto`, or a home-made wrapper around `\input`), or the table has nested tabulars. The build names each such table. Options: export the table as a plain `tabular`, show it as an image, or leave the pointer to the PDF. Tell the author which tables these are. |
| Table header rows are not bold or the header is one row short | The header is separated by `\hline` instead of `\midrule`. Cosmetic. Fix by hand only if the author cares. |
| Raw commands such as `\cellcolor` in the text | A macro pandoc does not know. Define it for pandoc by adding a `\newcommand` to the preamble copy, or strip it in `preprocess()` in the project's `build_site.py`. |
| "numbered but appears on no page" | The float sits inside a wrapper command pandoc drops. Unwrap it in `preprocess()` the way `\afterpage` is. |
| The checker says KaTeX does not know a command (shown in red) | For example `\mathds`. Add a `\newcommand` to the paper's preamble copy that maps it to a supported command (`\mathbb`). |
| "figure file not found" | The graphic lives outside the folders searched. Add the folder to `figure_dirs`. |
| "could not convert … to PNG" | Install poppler (`brew install poppler`) for `pdftoppm`. |
| Citations show as bold keys with a question mark | The key is not in the `.bib` file given. Check `bib`. |
| A formula shows in red | KaTeX does not support a command in it. The checker prints the formula. Replace the command with a KaTeX-supported one in a macro passed through the preamble. |
| The outline or search is missing | Switched off in `features`, or the page has fewer than two subsections. |
| Old pages linger after a section was renamed | The build removes pages it wrote earlier and no longer writes. Pages copied in by hand are left alone. |
