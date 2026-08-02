---
name: explain-diff
description: Explain a code change as a standalone offline HTML page with a five-question quiz. Reads the diff and the surrounding code from scratch, states the consequences for the empirical results, and saves the page outside the repository under a dated filename.
argument-hint: "[optional: git ref or range, default working tree vs HEAD]"
allowed-tools: Bash, Read, Write, Glob, Grep
disable-model-invocation: true
---

# Explain a Change

Produce one self-contained HTML page that explains a code change well enough that someone who did not write it could defend it, ending in a quiz that tests whether they actually followed.

## Scope

Set the target from `$ARGUMENTS`:

- No argument — uncommitted working tree against `HEAD`. Use `git status --short` and `git diff` (add `git diff --cached` if anything is staged).
- One ref (`abc123`, `main`) — that ref against the working tree, or against `HEAD` if the tree is clean.
- A range (`main..HEAD`, `abc123..def456`) — use it as given.

**New files are part of the change.** `git diff` shows nothing for an untracked file, so a change that only adds scripts looks empty. Always read `git status --short` for `??` entries and treat every new file as an addition to explain: read it in full, since there is no diff to read. A new robustness script is exactly the kind of change worth explaining, and it is the one the diff will hide.

Stop only when `git status --short` and the diff are both empty.

## Read from scratch

**Work only from the code and the diff.** If the conversation already contains an account of this change — yours or the user's — ignore it and read the files. A summary written earlier is a hypothesis, not evidence.

Do not stop at the diff hunks. For every changed block, read the function, script, or stage that contains it, and read what consumes its output. A three-line addition to a pipeline stage is usually only comprehensible from the two files on either side of it.

## Verify before you claim

The single most common failure here is reporting a change in results that did not happen, or missing one that did. Check, do not infer:

- **Generated files.** Tables, `.tex` bodies, and rendered figures often show as modified when only a timestamp comment or a nondeterministic tie-break changed. Diff them and look at what actually differs before calling it a result change.
- **Binary artifacts.** If an image changed, compare both versions visually. The old version lives in git rather than on disk, so extract it first — `git show HEAD:path/to/figure.png > /tmp/old-figure.png` — then read the extracted copy alongside the working-tree one. A re-render with identical content is not a finding.
- **Logs.** Compare sample sizes, observation counts, and headline coefficients between the old and new run. Identical numbers are the proof that an added block was inert; do not assert it from code reading alone.
- **Numbers you quote.** Every figure in the page should come from an output file you opened, not from the prose of the diff. If the change writes a new CSV, read it.
- **Samples.** When a new block filters data, compare its filter line by line against the filters of the existing estimation samples. Differences of one clause are the interesting ones.

## Sections

Write these five, in order, under clear headings.

**1. What this code did before.** Explore the surrounding scripts. Do not rely on the diff alone. Establish what the code produced, what consumed it, and — where it matters — what it conspicuously did not produce.

**2. What changed and why, in plain language.** No code in this section at all. Prose only. Name the problem the change solves before describing the solution.

**3. Consequences for the results.** Which sample, which coefficients, which tables, and in which direction. Be specific about magnitudes. If the answer is that nothing changed, **say so explicitly and prominently**, then show the evidence — matching observation counts, matching coefficients, timestamp-only diffs. A reader must not have to infer "no effect" from the absence of a claim. Where a change adds something rather than altering something, say what is new and what sample it rests on.

**4. Walkthrough of the changed code, grouped by purpose rather than by file.** One group per job the change does, even when a single job spans two files. Quote the code in `<pre>` blocks with the file and line range above each. Explain the lines that are load-bearing and skip the ones that are not, and say why a line is there when the reason is not obvious from reading it.

**5. Quiz.** Five multiple-choice questions, medium difficulty — hard enough that answering requires understanding the substance, not gotchas.

## Quiz rules

- **At least two questions must be about empirical consequences** rather than syntax: which observations enter the sample, what the coefficient now identifies, what would change if an assumption failed, whether a modified output file means the results moved.
- Distractors must be plausible misunderstandings — the reading someone would arrive at from a careless pass over the diff. Match the correct answer in length, grammar, specificity, and confidence. A correct answer that is visibly longer or more hedged than its distractors is a giveaway.
- **Randomise the position of the correct answer independently for each question.** Do not settle into a pattern.
- On click: report whether the answer was correct, then explain **every** option — why the right one is right and why each wrong one is wrong. The wrong-answer explanations carry most of the teaching.
- Cite the file and line each answer rests on, below the explanation.

## Page

Single HTML file. **Embed all CSS and JavaScript** so it works offline with no network access.

- Clear prose. Full sentences, not bullet fragments, wherever the content allows.
- Concrete toy examples with made-up small numbers — a four-row table showing what a reshape or a merge does beats a paragraph describing it.
- Simple HTML/CSS diagrams rather than ASCII art: flex-box pipeline boxes, positioned dots and bars for a chart, styled tables for data.
- Code in `<pre>` tags, with the file path and line range in a small monospace label above.
- Support light and dark via `prefers-color-scheme`.
- Real tables for tabular data, wrapped in an `overflow-x: auto` container.

## Provenance

Pages accumulate. Six months on, the only thing that makes one worth keeping is knowing exactly which change it describes, so record that in the page itself rather than trusting the filename.

Directly under the page title, a small block giving:

- Repository name, from `git rev-parse --show-toplevel`.
- Branch, from `git rev-parse --abbrev-ref HEAD`.
- The comparison, spelled out as the git command you actually ran — `git diff` against `HEAD`, `git diff abc123`, `main..HEAD`.
- The **full 40-character SHA** of each endpoint, from `git rev-parse`. Short SHAs collide as a repository grows; the page is the archival record, so it carries the full one.
- The date the page was written.

When the comparison involves the working tree, say so explicitly and add the list of changed and new files. An uncommitted tree is not reproducible — the state this page describes may never exist again, and a reader who later checks out the recorded SHA will not see it. That caveat belongs on the page.

## Output

Save **outside the repository**. Default directory `~/Documents/`; use a different one if the user names it. Confirm with `git status` afterwards that the repo is untouched.

Filename: today's date in `YYYY-MM-DD-` format, a short kebab-case slug of the change, then a ref tag so the file can be matched back to a commit without opening it.

- Working tree against `HEAD` — `wt-` plus the short SHA of `HEAD`, as in `2026-08-01-cluster-by-municipality-wt-e956a7e.html`.
- One ref — its short SHA.
- A range — both short SHAs joined by a hyphen, as in `a1b2c3d-def4567`.

Then tell the user the path, and follow it with a short plain-text summary of what you found — the same conclusions the page reaches, including anything you noticed while reading that the change's author might want to know. Do not make the user open the file to learn whether the results moved.
