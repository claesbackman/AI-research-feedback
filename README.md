# AI tools for research

A collection of [Claude Code](https://claude.ai/code) skills for academic research. Some give you feedback on a paper, a pre-analysis plan, a grant proposal, or the code behind a result. Others help you communicate your results, by turning a paper into a policy brief or a slide deck. A few are utilities that make the rest easier to use. The tools were developed by [Claes Bäckman](https://claesbackman.com). For a broader introduction to using AI in research, including how these skills fit into a workflow, see the [AI workshop](https://claesbackman.com/ai_workshop/index.html) page.


## Skills in this repo

Each skill lives in its own folder under `Skills/` with a `SKILL.md` file. Some skills also ship templates and helper scripts in the same folder.

**Feedback on your writing.** A family of review skills that read a document and write a structured report with findings you can act on. They cover a full referee-style review of a paper, a quick check of the contribution and identification, a mechanical check of spelling and internal consistency, a review of a pre-analysis plan, and a review of a grant proposal.

- `review-paper`, `review-paper-light`, `review-paper-checks`, `review-pap`, `review-grant`

**Feedback on your code.** Skills that check whether the analysis code does what the paper says it does, hunt for errors in a recent change, or explain a change well enough that a coauthor could defend it.

- `review-paper-code`: Paper–code reproducibility and alignment review.
- `audit-analysis`: Adversarial audit of changed analysis code, run by an isolated subagent.
- `explain-diff`: Explain a code change as an offline HTML page with a quiz.

**Communicating your results.** Skills that turn a finished paper into something for a different audience.

- `paper-version`: Policy brief, one-page, or five-page summary with a standalone HTML page.
- `explorable-deck`: A Quarto reveal.js slide deck built around a running example and live, presenter-driven figures.
- `explorable-beamer`: The same deck in LaTeX beamer, with TikZ stages the presenter steps through, a handout build, and a screenshot-and-log check of every page.

**Utilities.**

- `pdf-to-markdown`: Convert a PDF to readable markdown, trimmed at the references.


## How the skills work

These are [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code). A skill is a folder containing a `SKILL.md` file, installed under `~/.claude/skills/<name>/` and invoked by typing `/<name>` (for example, `/review-paper`) inside Claude Code.

A global install (`~/.claude/skills/`) is available in every project. A project-local install (`.claude/skills/`) applies only to that repository. Skills are picked up the next time you start Claude Code in the target directory.

The review skills, `audit-analysis`, `explain-diff`, and `paper-version` set `disable-model-invocation: true`, so they run only when you explicitly type their `/` command. Claude will never launch a multi-agent review on its own. `pdf-to-markdown`, `explorable-deck` and `explorable-beamer` are the exceptions: Claude may reach for them on its own when you ask it to read a PDF or to make a presentation. The two deck skills still run their multi-agent review only when you ask for it, for example with `/explorable-beamer review`, or `full` to add the creative director.


## Installation

### Everything at once

**Without a terminal (Windows Explorer, macOS Finder).** [Download the repository as a zip](https://github.com/claesbackman/AI-research-feedback/archive/refs/heads/main.zip), unzip it, and copy each folder inside `Skills/` (for example `review-paper`, `explorable-deck`) into `~/.claude/skills/`. That is a hidden folder in your user folder, `C:\Users\you\.claude\skills` on Windows and `/Users/you/.claude/skills` on macOS. Restart VS Code or Claude Code afterwards.

**With a terminal (macOS, Linux, WSL).** One line installs every skill globally:

```bash
git clone --depth 1 https://github.com/claesbackman/AI-research-feedback.git /tmp/airf && mkdir -p ~/.claude/skills && cp -R /tmp/airf/Skills/. ~/.claude/skills/ && rm -rf /tmp/airf
```

Re-run the same line later to update.

### One skill at a time

Every skill except `explorable-deck` and `explorable-beamer` is a single `SKILL.md` file. Replace `<name>` with the skill's folder name:

```bash
mkdir -p ~/.claude/skills/<name> && curl -o ~/.claude/skills/<name>/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/<name>/SKILL.md
```

For a project-local install, use `.claude/skills/<name>` as the target instead of `~/.claude/skills/<name>`.

`explorable-deck` and `explorable-beamer` ship a template, reference notes, and helper scripts alongside their `SKILL.md`, so they need the whole folder (replace the name as needed):

```bash
git clone --depth 1 https://github.com/claesbackman/AI-research-feedback.git /tmp/airf && mkdir -p ~/.claude/skills && cp -R /tmp/airf/Skills/explorable-deck ~/.claude/skills/ && rm -rf /tmp/airf
```

> **Already installed these as slash commands?** Custom commands and skills have merged in Claude Code, so any existing `~/.claude/commands/<name>.md` file keeps working and still provides `/<name>`. To avoid two definitions of the same command, delete the old `~/.claude/commands/<name>.md` file after installing the skill version.


## Feedback on your writing: the review skills

The review skills share one design. Each launches several specialised review agents in parallel, each with its own focus such as writing quality, internal consistency, unsupported claims, identification, or fit to a target journal, registry, or funder. The findings are consolidated into a single prioritised report saved under `reviews/` in the project folder, with the date in the filename and `-v2`, `-v3`, and so on appended when a file already exists. Reports live in their own subfolder so they cannot contaminate future runs. The skills read only the document's own source files and ignore old drafts, response letters, and previous review reports.

| Command | What it does | Agents | Report |
|---|---|---|---|
| `/review-paper` | Full review of a paper: language, internal consistency, unsupported claims, mathematics, tables and figures, and a referee assessment of identification and required analyses. A verifier agent then checks the factual findings and drops the ones that do not hold; add `quick` to skip it | 6 | `PRE_SUBMISSION_REVIEW_[date].md` |
| `/review-paper-light` | Fast check of contribution, identification, and causal overclaiming, for quick iteration | 2 | `QUICK_REVIEW_[date].md` |
| `/review-paper-checks` | Mechanical check of spelling, internal consistency, cross-references, and unsupported claims, with no editorial judgment. Offers to apply the unambiguous fixes to the `.tex` files afterwards | 3 | `PAPER_CHECK_[date].md` |
| `/review-pap` | Pre-analysis plan review covering specification completeness, identification, statistical analysis, and implementation | 6 | `PAP_REVIEW_[date].md` |
| `/review-grant` | Grant proposal panel review covering significance, innovation, design, feasibility, budget logic, and team | 6 | `GRANT_PROPOSAL_REVIEW_[date].md` |

**Usage.** The review skills take an optional path; `review-pap` and `review-grant` also take an optional target:

```text
/review-paper
/review-paper path/to/main.tex quick
/review-pap AEA
/review-grant ERC path/to/proposal.pdf
```

If no path is given, the skill auto-detects the main file and follows its `\input{}` graph. If no target is given, it applies high general standards without a specific persona.

| Skill | Recognised targets |
|---|---|
| `review-pap` | Registries: `AEA`, `EGAP`, `OSF`, `ClinicalTrials`, `ISRCTN`. Journals: `AER`, `QJE`, `JPE`, `RESTUD`, `AEJ`, `JEEA`. General: `top-journal` (default), `working-paper` |
| `review-grant` | `NSF`, `NIH`, `ERC`, `HorizonEurope`, `major-funder` (default), `foundation` |

Add journals or funders by editing the recognised names list in the skill file. Add project-specific context in your prompt or in a local `CLAUDE.md`.

**Which paper review to run.** `review-paper-checks` is for a draft you already believe in, shortly before submission, when you want to find things that are wrong rather than things that are debatable. `review-paper-light` is for a quick read of the argument while the paper is still moving. `review-paper` is the full report once the draft is close to final.

**Requirements.** [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent. The paper reviews expect a LaTeX paper. The pre-analysis plan and grant reviews accept `.md`, `.txt`, or `.tex`, and will attempt `.pdf` and `.docx` while noting any accessibility limits. Both also inspect supporting files when present, such as power calculations, survey instruments, budgets, timelines, and CVs.


## Feedback on your code

### `review-paper-code` — Paper-Code Reproducibility Review

Discovers the main LaTeX paper and the analysis code, checks reproducibility and code quality, maps the paper's main empirical claims to the code, and writes a constructive report with strengths, gaps to verify, and next steps.

| Area | Focus |
|---|---|
| Paper discovery | Main `.tex` file and included sections |
| Code discovery | Stata, R, and Python scripts in common analysis folders |
| Reproducibility | Paths, seeds, outputs, dependencies, run order, documentation |
| Code quality | Structure, commented-out code, opaque transforms, major thresholds |
| Paper-code alignment | Tables, variables, sample restrictions, methods, clustering, fixed effects |

**Usage:**

```text
/review-paper-code
/review-paper-code path/to/main.tex
/review-paper-code path/to/main.tex path/to/code_dir
/review-paper-code path/to/main.tex path/to/code_dir full
```

The default depth, `main`, focuses on the main scripts and core outputs. `full` reviews every detected code file in scope. The report is written to `reviews/code_review_report.md`.

**Requirements:** Claude Code with the `general-purpose` subagent, a LaTeX paper, and Stata, R, or Python analysis code.

### `audit-analysis` — Adversarial Audit of Changed Analysis Code

Finds errors in changed empirical code before a referee does. The skill hands the diff to a subagent with a clean context and tells it to break the code. That isolation is the point: whoever wrote the code, including the current Claude session if it helped, cannot steer the findings. It complements `review-paper-code`, which asks whether the paper matches the code rather than whether the code is right.

| Area | Focus |
|---|---|
| Claims vs. code | Do comments and commit messages match what actually runs? |
| Sample | N before and after every filter, merge, and collapse, taken from logs |
| Merges | Keys, uniqueness, fate of unmatched observations, duplicate id-period pairs |
| Variables | Units, logs vs. levels, deflation, lag alignment, name vs. construction |
| Silent failures | Missings coerced to zero, `if x > 0` on missing, `destring ... force`, `fillna(0)` |
| Estimation | Clustering level and count, what the fixed effects absorb, weights, estimation N |

Every finding must cite a file, a line, and a quoted excerpt, and is tagged CONFIRMED (visible in the code) or SUSPECTED (needs the data). Unanchored findings are dropped and counted. The auditor also reports, category by category, where it found nothing, and closes with the one thing it could not check without the data.

**Usage:**

```text
/audit-analysis
/audit-analysis main
/audit-analysis abc123
```

With no argument the working tree and commits are audited against `main`. Pass a branch, tag, or commit to audit against that instead. Diffs above roughly 1,500 changed lines are split across two auditors.

**Output:** Findings are relayed in the terminal, worst first, without softening. Nothing is written or changed in the repository. If you want repairs, that is a separate request.

**Requirements:** Claude Code with the `general-purpose` subagent, and a git repository with Stata, R, or Python analysis code. Logs improve the sample checks but are not required.

### `explain-diff` — Explain a Code Change

Explains a change to your analysis code well enough that someone who did not write it could defend it. It is aimed at the coauthor who needs to understand what an AI assistant or a collaborator just did to the estimation pipeline, and at your future self returning to a project after six months.

The skill reads the diff and the surrounding code from scratch, ignoring any account of the change that already exists in the conversation, then writes a self-contained HTML page you open in a browser.

The idea comes from Geoffrey Litt's [Understanding is the new bottleneck](https://www.geoffreylitt.com/2026/07/02/understanding-is-the-new-bottleneck), which argues that once agents write most of the code, the scarce resource is not verification but the researcher's own grasp of the system. Litt proposes explainer documents and embedded quizzes as a deliberate speed regulator. This skill is that proposal applied to empirical research code, where the thing you must not lose track of is what happened to the sample and the coefficients.

| Section | Content |
|---|---|
| 1 | What the code did before, established by reading the surrounding scripts |
| 2 | What changed and why, in plain language with no code |
| 3 | Consequences for the results: which sample, which coefficients, which tables, and in which direction |
| 4 | Walkthrough of the changed code, grouped by purpose rather than by file |
| 5 | A five-question multiple-choice quiz with explanations for every option |

Section 3 is the point of the skill. It requires verification rather than inference: comparing observation counts and coefficients between runs, checking whether a modified table file differs in its numbers or only in a timestamp, and reading any new output file before quoting a figure from it. When nothing about the results changed, the page has to say so explicitly and show the evidence. At least two quiz questions test empirical consequences rather than syntax.

**Usage:**

```text
/explain-diff
/explain-diff abc123
/explain-diff main..HEAD
```

With no argument the skill explains the uncommitted working tree against `HEAD`, including files that are new and therefore invisible to `git diff`. A single ref is compared against the working tree. A range is used as given.

**Output:** One HTML file saved **outside the repository**, in `~/Documents/` unless you name another directory, so it never lands in a commit or in your paper's folder. The skill confirms with `git status` afterwards that nothing in the project changed. Filenames end in a ref tag, for example `2026-08-01-cluster-by-municipality-wt-e956a7e.html`, so the pages stay matchable to commits. The page itself carries the full SHAs, the branch, and the exact comparison. You also get a plain-text summary in the terminal.

**Requirements:** Claude Code and a git repository. No subagents are used. Stata, R, Python, and LaTeX are all optional.


## Communicating your results

### `paper-version` — Policy Brief, One-Page, or Five-Page Summary

Turns a LaTeX research paper into a version for a non-specialist audience, checks it against the paper, and produces a standalone HTML page ready for GitHub Pages. Four agents run in sequence: a reader extracts the paper's content and claims verbatim, a writer drafts the requested format, a reviewer compares every number and causal claim in the draft against the extraction, and, after you have read the review and edited the draft, a fourth agent builds the page.

| Argument | Output |
|---|---|
| `brief` | Two-page policy brief with fixed sections: The Question, What We Do, Key Findings, Policy Implications, Caveats (500–600 words) |
| `1page` | One page of flowing prose for a general reader, leading with the main finding (350–400 words) |
| `5page` | Narrative summary with light structure: Background, What We Did, What We Found, Why It Matters, Limitations (1,400–1,600 words) |

The reviewer flags three kinds of problem: wrong or misattributed numbers, causal language stronger than the paper's own, and shifts in emphasis away from what the paper treats as central. The skill pauses after the review so you can edit the draft before the page is built.

**Usage:**

```text
/paper-version brief
/paper-version 1page
/paper-version 5page
```

Run it from the paper's project folder. The skill finds the main `.tex` file and follows `\input` and `\include`.

**Output:** An `output/` folder in the project containing `paper_extraction.md`, `[format]_draft.md`, `[format]_review.md`, and `index.html`. PNG or JPG versions of the paper's key figures are embedded when they exist in the project.

**Requirements:** Claude Code with the `general-purpose` subagent, and a LaTeX paper.

### `explorable-deck` — Slide Deck in the Explorable-Explanation Style

Builds a presentation from a paper, a set of notes, or a codebase as a [Quarto](https://quarto.org) reveal.js deck. The design follows the explorable-explanation tradition of Nicky Case and Bret Victor, adapted to the constraints of a talk: one idea per slide, titles that are assertions and read as the argument in sequence, a concrete running example introduced before any abstraction, and figures drawn at run time as stages the presenter operates while talking. The paper's own figures are converted from PDF and recoloured into the deck's palette. Everything a questioner might want goes into an appendix of uncounted slides linked from the main line, and the printed PDF has to carry the argument on its own. It is the talk-shaped sibling of the [`explorable-explanations`](https://github.com/nityeshaga/claude-home-base/tree/main/plugins/creative/skills/explorable-explanations) skill from the claude-home-base repository, which builds the website version as a non-linear tree of short interactive pages. When an explorable already exists for the topic, the deck reuses its data and chart code so the two never disagree on a number.

The skill first fixes the frame (audience, length, venue) and writes a talk script in `plan.md` before building any slide. If you have not said otherwise it assumes a 20-minute conference talk for a mixed academic room. Every number in a chart lives in one data object that the prose also reads from, so the two cannot disagree. After the deck renders, the skill screenshots every slide, fixes every console error and every slide whose content runs off the frame, and checks the deck against a list of common faults.

**Review.** The multi-agent review is optional. It is the slowest part of a run, and it is most useful once you have seen the deck and settled its content. By default the skill stops after its own checks and tells you that it skipped the review. You can ask for the review when you build the deck, or later on a finished one:

| Level | How to ask | What runs after the checks |
|---|---|---|
| none (default) | `/explorable-deck` | Nothing more |
| `review` | `/explorable-deck review`, or "review the deck" | Four review agents for writing, slides, visuals, and teaching, plus a simulated audience member, all in parallel. The skill then builds a second version from their findings |
| `full` | `/explorable-deck full`, or "full review" | The above, then a creative director who proposes a visual identity for the deck |

Build without review while the content is still moving, and run `review` before a talk that matters.

**Usage:**

```text
/explorable-deck
/explorable-deck 12-minute seminar talk from paper/main.tex
/explorable-deck review 20-minute talk from paper/main.tex
/explorable-deck review slides/
```

The last line reviews a deck that already exists in `slides/`.

Claude may also pick this skill on its own when you ask for a presentation, talk, or slides.

**Output:** One folder per deck containing `index.qmd`, the theme, the chart code, converted figures, `plan.md`, and a README that says how to render, check, and present it. Render with `quarto render index.qmd` and open `index.html` in a browser. While presenting, `S` opens the speaker view with notes, `F` goes fullscreen, `O` shows the overview, and `E` switches to the print view for exporting a PDF.

**Requirements:**

- Claude Code with the `general-purpose` subagent for the optional review passes.
- [Quarto](https://quarto.org/docs/get-started/) on your path.
- Python 3 and Google Chrome, for the screenshot check. Optionally `playwright` instead of Chrome.
- `pdftocairo` (part of poppler, `brew install poppler` on macOS) if you want the paper's PDF figures converted into the deck.
- Install the whole `Skills/explorable-deck` folder, not just `SKILL.md`. See [Installation](#one-skill-at-a-time).

### `explorable-beamer` — The Same Deck in LaTeX Beamer

Builds the same kind of deck as `explorable-deck`, under the same design rules, as a LaTeX beamer PDF. Use it when the talk has to be a PDF or the project already lives in LaTeX. Because a PDF cannot run live figures, the stages are TikZ and pgfplots charts that the presenter steps through with overlays. The paper's own PDF figures go in directly and are recoloured into the deck's palette. Every number a chart draws or a sentence quotes comes from one file, `data/numbers.tex`. When a Quarto deck or a website explorable already exists for the topic, the skill transcribes its numbers instead of retyping them from the paper.

One build produces three PDFs: the talk with each overlay step on its own page, a handout with one page per frame in its finished state for printing or sending, and a notes version with each slide beside its speaker note. While editing, `sh build.sh --fast` builds only the talk, in about a third of the time. The check screenshots every page, reports errors and warnings from the LaTeX log, and names any page whose content reaches the footline, which beamer compiles with only an easily missed log line. A lint then flags label titles, missing speaker notes and source lines, shrunk type, and overlays that would print wrongly in the handout.

Review works as in `explorable-deck`: none by default, `review` for the four review agents and the audience member, and `full` to add the creative director.

**Usage:**

```text
/explorable-beamer
/explorable-beamer 20-minute conference talk from paper/main.tex
/explorable-beamer review slides/
/explorable-beamer full 45-minute job-market talk from paper/main.tex
```

Claude may also pick this skill on its own when you ask for a Beamer, LaTeX, or PDF presentation.

**Output:** One folder per deck containing `deck.tex`, the theme, the charts, the data file, the recoloured figures, `plan.md`, and a README that says how to build, check, and present it. `sh build.sh` writes `deck.pdf` to present full screen in any PDF viewer, `deck-handout.pdf` to print or send, and `_build/deck-notes.pdf` for speaker notes on a second screen with `pdfpc --notes=right _build/deck-notes.pdf`.

**Requirements:**

- Claude Code with the `general-purpose` subagent for the optional review passes.
- TeX Live 2019 or later with `lualatex`, `latexmk`, and pgfplots 1.16 or later. The template needs no network access and no font installation.
- Python 3 and poppler (`brew install poppler` on macOS, `apt install poppler-utils` on Linux), for the screenshot check.
- Ghostscript (`brew install ghostscript`) if you want the paper's PDF figures recoloured. Without it they are copied in unchanged.
- Optionally [pdfpc](https://pdfpc.github.io/) to present with speaker notes.
- Install the whole `Skills/explorable-beamer` folder, not just `SKILL.md`. See [Installation](#one-skill-at-a-time).


## Utilities

### `pdf-to-markdown` — Convert a PDF to Readable Markdown

Converts a PDF to a markdown file saved next to it, with page markers every twenty pages and the text trimmed at the references or appendix so the main text is what enters the context window. Useful before running any of the review skills on a paper you only have as a PDF, and for reading long documents without spending context on the bibliography.

When `pdftotext` (part of poppler) is installed the conversion runs in one shot outside the model and takes seconds regardless of length. Without it the skill falls back to reading the PDF in twenty-page chunks, which works but is slow for long documents. Recommended: `brew install poppler` (macOS) or `apt install poppler-utils` (Linux, WSL).

**Usage:**

```text
/pdf-to-markdown path/to/paper.pdf
```

**Output:** `path/to/paper.md`, plus a short report: method used, pages processed, where the text was trimmed, and any unreadable pages.

**Requirements:** Claude Code. No subagents are used. `pdftotext` is optional but recommended.


## How to cite

If you use these skills in your research, please cite the repository. GitHub's "Cite this repository" button on the repo page exports the reference in APA or BibTeX format from the `CITATION.cff` file. In BibTeX:

```bibtex
@misc{backman2026aitools,
  author       = {B{\"a}ckman, Claes},
  title        = {{AI} tools for research: {Claude Code} skills for feedback on and communication of academic research},
  year         = {2026},
  version      = {1.0.0},
  howpublished = {\url{https://github.com/claesbackman/AI-research-feedback}}
}
```


## License

MIT — free to use, adapt, and share.
