---
name: paper-website
description: Build a digital edition of an academic paper, a simple static website for an academic audience made from the paper's LaTeX source. The paper's text is split into one page per section with the PDF's own section, figure, table and equation numbers, footnotes that open in place, linked citations and a reference list, hover previews, full-text search, dark mode, a cite box, and CSV download of every table. The author decides whether the site carries data (none, figures redrawn from aggregate tables with a table view and download, or also a results explorer) and answers a short list of customization questions first. Use this whenever someone wants a website, web version, online version, HTML version, digital edition, companion site or project page for a paper, working paper, thesis chapter or article, wants to "put the paper online", "make the paper readable in a browser", "publish the paper on GitHub Pages", or asks to rebuild or restyle a site made this way. Not for a slide deck (explorable-deck, explorable-beamer, explorable-pptx), a Nicky Case style explorable (explorable-explanations), or a policy brief or summary of the paper (paper-version).
---

# Paper website

The skill turns a LaTeX paper into a static website that reads like the paper. Readers get
the full text in the paper's own numbering, so "Table 3" on the site is Table 3 in the PDF.
The site adds what a PDF cannot do: footnotes and references one click away, search, tables
that download as CSV, and, if the author wants, figures drawn from the numbers behind them.

The site is built by three Python scripts that the skill copies into the author's project, so
the author can rebuild it after every revision without the skill. Your job is to ask the
author what they want, write the configuration and the few hand-written pages, run the build,
and check the result in a browser.

Requirements: `pandoc` (required), `pdftoppm` from poppler (to turn PDF figures into PNG),
Python 3.8 or later with no extra packages, and Chrome or Chromium for the rendered check.
If `pandoc` is missing, tell the author how to install it and stop.

## Step 1. Look at the project

Before asking anything, find out what you can so the questions are short:

- the root `.tex` file (the one with `\begin{document}`), the `.bib` file, the compiled PDF
- title, subtitle, authors, affiliations, and the `\thanks` note, from the root file
- whether the paper has an appendix, a separate online appendix file, and how many figures
  and tables
- where the analysis writes its tables (`output/tables/*.csv` or similar), since that decides
  whether the data tiers are possible at all
- whether a `website_build/` folder already exists. If it does, the site has been built
  before. Do not run the questionnaire. Go to "Updating an existing site" below.

Do not read the PDF directly. Work from the LaTeX source. `pdftotext` is fine when you need
to check something against the compiled paper.

Also look for things that should not go online: draft notes, coloured comments to
coauthors, `\todo` commands. Mention them in Step 2.

## Step 2. Ask the customization questions

Always ask before building. The answers decide what the site is, and the author cannot see a
default they were never offered. Use the AskUserQuestion tool, in two rounds of at most four
questions, and put your recommendation first. The dialog takes two to four options per
question, so the options below are already grouped to fit. Skip a question only when the answer is
already clear from the conversation. Say in one line what you detected in Step 1 so the
author can correct it.

Round 1, content:

1. **Data.** Should the site carry data?
   - *No data.* Text, the paper's figures as images, tables, references. Right for most papers
     and the only safe choice when the numbers behind the figures cannot be shared.
   - *Figure data.* Chosen figures are redrawn from aggregate CSV tables, with hover values, a
     table view and a CSV download. The paper's image stays one click away.
   - *Figure data and an explorer.* Adds one page where readers slice an aggregate table by
     its dimensions (for example country by year by group).
   If no CSV tables exist in the project, say so and recommend no data.
2. **Extra pages** (multi-select). Data and code page (recommended, it also carries the
   citation and says what is not released), questions and answers page written from the
   paper, errata page, an "ask an AI about this paper" prompt on the data and code page.
3. **Appendix.** One page per appendix section, one page for the whole appendix, or leave
   the appendix out. Ask only if the paper has one. If the project has a separate online
   appendix file, say that you found it and ask whether to include it (`appendix_tex`).
4. **Links and publishing.** Where will the site live (GitHub Pages folder, a personal site,
   only local for now), which links belong in the top bar (replication package,
   pre-registration, journal page, a link for reporting problems), and whether the PDF may
   be posted on the site. The build copies the PDF to the site when `pdf` is set, so leave
   `pdf` out if a publisher's version may not be shared.

Round 2, appearance:

5. **Colour scheme.** `signature` (the default: warm paper, vermilion accent, teal notes,
   Bricolage Grotesque headings with Newsreader text, the palette of the explorable decks
   in the same repository) or `classic` (white, blue, IBM Plex). Offer a third option, "my
   own accent colour", for a hex colour such as the university's. The other accent presets
   are vermilion, blue, teal, burgundy, slate, green and ochre.
6. **Typeface.** Keep the scheme's typeface (recommended), or `plex`, `source`, or `system`
   (no web fonts, loads fastest and works offline). `sans` (Inter throughout) also exists.
7. **Reader features.** Search, hover previews, the "on this page" outline, the cite box,
   table CSV download and dark mode are all on by default. Ask one question: keep them all
   (recommended) or switch some off. Only if the author wants some off, ask which.
8. **Edition label and status.** For example "Digital edition · November 2026" and "working
   paper", "forthcoming in …", or "published in …".

If the author chose a data tier, follow up on the data once they have answered (Step 5).
If something the author asks for is not covered by the configuration, say what you would
have to hand-edit and do it in the copied theme, not in the skill folder.

## Step 3. Set up the build folder

Copy the template into the project, next to the other code (follow the project's layout,
for example `code/website_build/` or `Code/website_build/`):

```bash
python3 <this skill's folder>/scripts/install.py <project>/code/website_build
```

The folder then holds `build_site.py`, `site_data.py`, `check_site.py`, `update_site.py`,
`theme/` (CSS, JavaScript, the citation style), `content/` (the hand-written pages), and
`.template.json`, which records the template version and what was copied so the folder can
be upgraded later. Delete the content
files for pages the author did not choose (`faq.html`, `errata.html`, `explorer.html` and
`explorer.json`).

Write `site.json` in that folder. Every key is described in `references/config.md`. Read it
before writing the file. All paths are relative to `site.json`. A minimal file:

```json
{
  "title": "Paper Title",
  "subtitle": "The Part After the Colon",
  "authors": [{"name": "Jane Doe", "affiliation": "University of X", "url": "https://janedoe.org"}],
  "year": 2026,
  "edition": "Digital edition · November 2026",
  "status": "working paper",
  "main_tex": "../../Writing/main.tex",
  "pdf": "../../Writing/main.pdf",
  "output_dir": "../../Website",
  "theme": {"accent": "teal", "typeface": "plex"},
  "pages": [{"slug": "about", "title": "Data and code", "group": "notes"}]
}
```

## Step 4. Build, then fix what the build reports

```bash
python3 code/website_build/build_site.py
python3 code/website_build/check_site.py --browser
```

The build prints the pages, the exhibit numbers and its warnings. The checker lists errors
(broken links, unresolved references, missing images, unfilled template text, formulas KaTeX
cannot render) and warnings (raw LaTeX left in the text, exhibit numbers that differ from
the PDF, tables that could not be converted). Work through them. `references/config.md` has
a troubleshooting table with the usual causes: a custom notes macro, an appendix that does
not start with `\appendix`, numbering set in an unusual way, a macro pandoc cannot expand.

Fix problems in `site.json` or in the copied scripts, never by editing the paper's LaTeX,
unless the author agrees. The paper is the source of record.

Never edit the generated HTML in the output folder. The next build overwrites it.

## Step 5. Data (only if the author chose a data tier)

Read `references/data.md` first. In short:

- The site is public. Only aggregates that the paper already reports may go on it: point
  estimates and intervals, cell means, binned counts. Never microdata, and never anything
  from a restricted source (register data, proprietary data) that has not been cleared for
  release. When in doubt, ask the author and default to leaving it out.
- For every figure the author wants interactive, find the CSV the figure was drawn from,
  show the author which file and columns you will publish, and add a `data.figures` entry.
  A figure without an entry keeps its static image, which is fine.
- `site_data.py` refuses sources that look like microdata (more than 2,000 rows, identifier
  columns, cells below `data.min_cell`). Do not set `confirmed_aggregate` to get past the
  guard without the author saying the file is safe to publish.
- For the explorer, pick one long-format aggregate table with a few dimensions and one value
  column, and fill in `content/explorer.html`.

## Step 6. Write the hand-written pages

The pages in `content/` are templates. Text in `[[double brackets]]` and comments that start
with `<!-- EDIT:` are instructions to you. Replace or delete every one. The checker fails
while any remain.

- `index.html`: the title page fills itself in. Adjust the "How to read this site" list so
  it names the pages and features this site has.
- `about.html`: say what is on the site and what is not, in the author's words where you
  have them. Keep or delete the "ask an AI" panel as the author chose. Keep the "How this
  site was built" panel.
- `faq.html`: six to ten questions a seminar audience would ask, answered from the paper
  with the numbers and a link to the section, figure or table. Do not invent results. If the
  paper does not answer a question, leave the question out.
- `errata.html`: one dated line for this first edition.

Write these pages in the paper's register: plain, formal, no promotional language. Then
rebuild and run the checker again until it reports no errors.

## Step 7. Look at it, then hand over

Open the site and look at it before telling the author it is done. At minimum, take
screenshots of the title page, one results page with a figure and a table, and (if built)
the explorer:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --window-size=1500,1700 --virtual-time-budget=8000 --screenshot=/tmp/page.png \
  "file://<absolute path>/Website/index.html"
```

Check that figures are where the paper has them, table headers and notes came through,
equations render, and nothing overflows. Open every page that has tables, not just one.
Regression tables are where conversion fails most often, and for a few of them compare the
numbers with the LaTeX source. The pages open from disk, so the author can also
double-click `index.html`.

Then tell the author, briefly: where the site is, how to update it after the next revision
(`python3 code/website_build/update_site.py`), what the checker still warns about, which tables or figures fell back to "see the
PDF", and how to publish. Publishing is copying the output folder to any static host. For
GitHub Pages that is a `docs/` folder or a repository of its own. Do not push or deploy
unless the author asks. If the project is private or the data are restricted, remind the
author that everything in the output folder becomes public when it is published, and list
what is in its `data/` folder.

## Updating an existing site

A site is updated for one of three reasons. Find out which from what the author says, and
ask only about what they want changed.

**The paper changed.** Run the update, which builds, checks and compares with the previous
build:

```bash
python3 code/website_build/update_site.py
```

Read the report it prints (also saved as `_update_report.md`). Then:

- Fix what the checker reports, as in Step 4.
- If figures, tables or equations were renumbered, or pages were retitled or removed, read
  the hand-written pages (`content/index.html`, `faq.html`, `about.html`) for text that
  still describes the old paper: numbers quoted in an answer, "Table 3" written out in a
  sentence, a finding that changed. Links written as `<a href="#label">` follow the paper
  by themselves. Numbers and claims typed into the text do not.
- Add a dated line to `content/errata.html`. The report drafts one. Rewrite it to say what
  changed in substance (a corrected estimate, a new section), not the mechanics.
- Update `edition` in `site.json` if the author wants a new edition label, and rebuild.

Page addresses do not move when a section title changes. The first build writes each
section's address into `structure.slugs` in `site.json`, keyed by the section's `\label`.
A section without a `\label` is keyed by its title, so retitling it does create a new page.
The old address then becomes a redirect to the title page. To avoid that, ask the author
to label the section, or move its entry in `structure.slugs` to the new key before
building. A page whose section is removed becomes a redirect, so links from other sites
keep working.

**The author wants a different look or different pages.** Change `site.json` or the content
files and rebuild. No questionnaire. Confirm the change in a screenshot.

**The skill's template is newer than the project's copy.** `.template.json` in the build
folder records the version installed. Compare it with `template/VERSION` in this skill. To
upgrade, run the installer again on the same folder:

```bash
python3 <this skill's folder>/scripts/install.py <project>/code/website_build
```

It replaces the scripts and the theme, and never touches `site.json` or `content/`. A file
the author edited by hand is kept, and the new version is written beside it as
`<name>.new`. Merge the author's changes into the new file, delete the `.new` file, rebuild,
and look at the site again, since a template upgrade can change every page. Offer the
upgrade when you notice the version is behind. Do not run it unasked.

**Publishing an update.** If `site.json` has `"deploy": {"target": "<folder>"}`, the update
report ends with the copy command, and `update_site.py --deploy` runs it. The copy makes
the target identical to the new build, which deletes files there that the build does not
have. The script therefore refuses when the checker reports errors, and when the target
holds anything other than an earlier build of this site. Run `--deploy` only when the
author asks for the site to be published. It never commits or pushes. Leave that to the
author unless they ask.

## Rules that do not bend

- **The credit line stays.** Every page carries the footer line "Built with AI tools for
  research (Bäckman, 2026)". The build adds the full citation to the foot of the title
  page, and the data and code page carries it too:
  Bäckman, C. (2026). AI tools for research: Claude Code skills for feedback on and
  communication of academic research (Version 1.0.0) [Computer software].
  https://github.com/claesbackman/AI-research-feedback. The checker fails if it is missing.
  Do not remove it when customizing the theme.
- **No microdata on the site.** Aggregates only, and only what the author has confirmed.
- **Numbers match the PDF.** If the site's exhibit numbers differ from the PDF, fix the
  numbering before anything else. A reader who cites "Table 4" from the site must find the
  same table in the paper.
- **The site says what the paper says.** Do not rewrite, shorten or "improve" the paper's
  text on the way to HTML. Hand-written pages may summarize, and must not add claims.

## Reference files

- `references/config.md`: every `site.json` key, how the script reads the LaTeX, and the
  troubleshooting table. Read before writing `site.json`.
- `references/data.md`: the data tiers, the disclosure rules, chart types with examples, and
  the explorer. Read before adding any data.
