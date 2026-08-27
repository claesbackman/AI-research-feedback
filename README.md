# Using AI to get feedback on your research

A collection of [Claude Code](https://claude.ai/code) skills for reviewing and understanding academic research. This tool was developed by [Claes Bäckman](https://claesbackman.com).


## Skills in this repo

Each skill lives in its own folder containing a `SKILL.md` file:

- `Skills/review-paper/SKILL.md`: Full 8-agent referee-style paper review.
- `Skills/review-paper-light/SKILL.md`: Fast 2-agent paper check.
- `Skills/review-paper-checks/SKILL.md`: Fast 3-agent mechanical check — spelling, internal consistency, unsupported claims.
- `Skills/review-paper-code/SKILL.md`: Paper–code reproducibility and alignment review.
- `Skills/review-pap/SKILL.md`: Pre-analysis plan review.
- `Skills/review-grant/SKILL.md`: Grant proposal review.
- `Skills/explain-diff/SKILL.md`: Explain a code change as an offline HTML page with a quiz.
- `Skills/audit-analysis/SKILL.md`: Adversarial audit of changed analysis code, run by an isolated subagent.
- `Skills/paper-version/SKILL.md`: Turn a LaTeX paper into a policy brief, one-page, or five-page summary with a standalone HTML page.
- `Skills/pdf-to-markdown/SKILL.md`: Convert a PDF to readable markdown, trimmed at the references.


## How the skills work

These are [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code). Install one into `~/.claude/skills/<name>/SKILL.md` and invoke it by typing `/<name>` (for example, `/review-paper`) inside Claude Code. The per-skill installation commands below create the required folder and download the `SKILL.md` for you.

A global install (`~/.claude/skills/`) is available in every project. A project-local install (`.claude/skills/`) applies only to that repository. Skills are picked up the next time you start Claude Code in the target directory.

The review skills, `audit-analysis`, and `paper-version` set `disable-model-invocation: true`, so they run only when you explicitly type their `/` command. Claude will never launch a multi-agent review on its own. `pdf-to-markdown` is the exception: Claude may also reach for it when you ask it to read a PDF.

## Install everything at once

**Without a terminal (Windows Explorer, macOS Finder).** [Download the repository as a zip](https://github.com/claesbackman/AI-research-feedback/archive/refs/heads/main.zip), unzip it, and copy each folder inside `Skills/` (for example `review-paper`, `review-paper-light`) into `~/.claude/skills/`. That is a hidden folder in your user folder — `C:\Users\you\.claude\skills` on Windows, `/Users/you/.claude/skills` on macOS. Restart VS Code or Claude Code afterwards.

**With a terminal (macOS, Linux, WSL).** One line installs every skill globally:

```bash
git clone --depth 1 https://github.com/claesbackman/AI-research-feedback.git /tmp/airf && mkdir -p ~/.claude/skills && cp -R /tmp/airf/Skills/. ~/.claude/skills/ && rm -rf /tmp/airf
```

Re-run the same line later to update. The per-skill `curl` commands below install one skill at a time.

> **Already installed these as slash commands?** Custom commands and skills have merged in Claude Code, so any existing `~/.claude/commands/<name>.md` file keeps working and still provides `/<name>`. To avoid two definitions of the same command, delete the old `~/.claude/commands/<name>.md` file after installing the skill version.


## Skills

### `review-paper` — Pre-Submission Referee Report

Runs a rigorous pre-submission review of an academic paper, simulating the scrutiny of a specific journal's editorial board. Eight specialized review agents run in parallel and consolidate their findings into a single structured report. The review only reads the paper's own source files (the main .tex file and everything it includes) and ignores old drafts, response letters, and previous review reports in the same folder.

**What it reviews:**

| Agent | Focus |
|---|---|
| 1 | Spelling, grammar, and academic style |
| 2 | Internal consistency and cross-reference verification |
| 3 | Unsupported claims and identification integrity |
| 4 | Mathematics, equations, and notation |
| 5 | Tables, figures, and their documentation |
| 6 | Referee assessment (identification, analyses, positioning, journal fit) |
| 7 | Contribution advocate (steelman, grounded in the paper's own bibliography) |
| 8 | Contribution skeptic (attack, grounded in the paper's own bibliography) |

Agents 7 and 8 independently rate the central contribution from opposite directions. The report reconciles them in a synthesis section that states where they agree, names the crux of any disagreement, and flags novelty claims that cannot be verified from the paper's own bibliography.

**Installation:**

```bash
mkdir -p ~/.claude/skills/review-paper && curl -o ~/.claude/skills/review-paper/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper/SKILL.md
```

For a project-local install:

```bash
mkdir -p .claude/skills/review-paper && curl -o .claude/skills/review-paper/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper/SKILL.md
```

**Usage:**

```text
/review-paper
/review-paper QJE
/review-paper JF path/to/main.tex
```

**Supported journals:**

| Category | Journals |
|---|---|
| Top-5 economics | `AER`, `QJE`, `JPE`, `Econometrica`, `REStud` |
| Finance | `JF`, `JFE`, `RFS`, `JFQA` |
| Macro | `AEJMacro`, `JME`, `RED` |

If no journal is specified, the skill applies high general standards without a specific journal persona. If no path is provided, it auto-detects the main `.tex` file.

**Output:**

Saves a consolidated report to `reviews/PRE_SUBMISSION_REVIEW_[YYYY-MM-DD].md`, automatically appending `-v2`, `-v3`, and so on if a file already exists. Reports live in a `reviews/` subfolder so they cannot contaminate future runs.

**Customization:**

- Add journals or fields by editing the recognized journal names list in the skill file.
- Add project-specific context in your prompt or in a local `CLAUDE.md` file.
- Adjust folder discovery or save paths directly in the skill if your project structure differs from the default assumptions.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A LaTeX paper. The skill reads `.tex` files and optionally inspects figure and table files.

### `review-paper-light` — Quick Paper Check

Runs a fast 2-agent pre-submission check for an economics paper. It focuses on contribution, identification, causal overclaiming, and unsupported claims, and is designed for quick iteration before a full review.

**Installation:**

```bash
mkdir -p ~/.claude/skills/review-paper-light && curl -o ~/.claude/skills/review-paper-light/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper-light/SKILL.md
```

For a project-local install:

```bash
mkdir -p .claude/skills/review-paper-light && curl -o .claude/skills/review-paper-light/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper-light/SKILL.md
```

**Usage:**

```text
/review-paper-light
/review-paper-light path/to/main.tex
```

If no path is provided, the skill auto-detects the main `.tex` file.

**Output:**

Saves a short prioritized report to `reviews/QUICK_REVIEW_[YYYY-MM-DD].md`, automatically versioning the filename if one already exists.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A LaTeX paper.

### `review-paper-checks` — Mechanical Paper Check

Runs a fast 3-agent check for things that are *wrong* in a paper rather than things that are debatable: spelling and grammar, internal consistency (numbers in the text against numbers in the tables, abstract against results, terminology drift, broken cross-references and citations), and unsupported claims (causal language the design does not license, mechanisms asserted as facts, missing caveats, unverified priority assertions).

It deliberately does not judge the contribution, evaluate the identification strategy, or issue a recommendation. Use `review-paper-light` or `review-paper` for that. Run `review-paper-checks` on a draft you already believe in, shortly before submission.

**Installation:**

```bash
mkdir -p ~/.claude/skills/review-paper-checks && curl -o ~/.claude/skills/review-paper-checks/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper-checks/SKILL.md
```

For a project-local install:

```bash
mkdir -p .claude/skills/review-paper-checks && curl -o .claude/skills/review-paper-checks/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper-checks/SKILL.md
```

**Usage:**

```text
/review-paper-checks
/review-paper-checks path/to/main.tex
```

If no path is provided, the skill auto-detects the main `.tex` file and follows its `\input{}` graph.

**Output:**

Saves a prioritized fix list to `reviews/PAPER_CHECK_[YYYY-MM-DD].md`, automatically versioning the filename if one already exists. Afterwards it offers to apply the unambiguous mechanical fixes (spelling, grammar, broken references) directly to the `.tex` files, leaving every claim-level item for you to judge.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A LaTeX paper. Table `.tex` files and a `.bib` file, if present, let the consistency and citation checks run.

### `review-paper-code` — Paper-Code Reproducibility Review

Runs a paper-code review for empirical research projects. It discovers the main LaTeX paper and analysis code, checks reproducibility and code quality, maps the paper's main empirical claims to the code, and writes a constructive report highlighting strengths, gaps to verify, and concrete next steps.

**What it reviews:**

| Area | Focus |
|---|---|
| Paper discovery | Main `.tex` file and included sections |
| Code discovery | Stata, R, and Python scripts in common analysis folders |
| Reproducibility | Paths, seeds, outputs, dependencies, run order, documentation |
| Code quality | Structure, commented-out code, opaque transforms, major thresholds |
| Paper-code alignment | Tables, variables, sample restrictions, methods, clustering, fixed effects |

**Installation:**

```bash
mkdir -p ~/.claude/skills/review-paper-code && curl -o ~/.claude/skills/review-paper-code/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper-code/SKILL.md
```

For a project-local install:

```bash
mkdir -p .claude/skills/review-paper-code && curl -o .claude/skills/review-paper-code/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper-code/SKILL.md
```

**Usage:**

```text
/review-paper-code
/review-paper-code path/to/main.tex
/review-paper-code path/to/main.tex path/to/code_dir
/review-paper-code path/to/main.tex path/to/code_dir full
```

**Review depth:**

- `main`: default; focuses on main scripts and core outputs
- `full`: reviews all detected code files in scope

**Output:**

Writes a report to `reviews/code_review_report.md`, creating the `reviews/` folder if needed.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A LaTeX paper plus Stata, R, or Python analysis code.

### `review-pap` — Pre-Analysis Plan Review

Runs a 6-agent pre-submission review of a pre-analysis plan (PAP). The skill auto-detects the main PAP and supporting files, then evaluates writing quality, specification completeness, internal consistency, identification strategy, statistical analysis, implementation details, and registry or journal fit.

**Installation:**

```bash
mkdir -p ~/.claude/skills/review-pap && curl -o ~/.claude/skills/review-pap/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-pap/SKILL.md
```

For a project-local install:

```bash
mkdir -p .claude/skills/review-pap && curl -o .claude/skills/review-pap/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-pap/SKILL.md
```

**Usage:**

```text
/review-pap
/review-pap AEA
/review-pap QJE path/to/pap.tex
```

**Supported targets:**

- Trial registries: `AEA`, `EGAP`, `OSF`, `ClinicalTrials`, `ISRCTN`
- Journal standards: `AER`, `QJE`, `JPE`, `RESTUD`, `AEJ`, `JEEA`
- General standards: `top-journal`, `working-paper`

If no target is specified, the skill defaults to `top-journal`. If no path is provided, it auto-detects the main PAP file.

**Supporting files it can inspect:**

- Power calculations and sample-size worksheets
- Survey instruments and questionnaires
- Randomization protocols and sampling frames
- Code skeletons and mock tables
- Data dictionaries and ethics materials

**Output:**

Saves a consolidated report to `reviews/PAP_REVIEW_[YYYY-MM-DD].md`, automatically versioning the filename if one already exists.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A PAP in a readable format such as `.md`, `.txt`, or `.tex`. The skill can also attempt to work with `.pdf` and `.docx`, while noting accessibility limitations if needed.

### `review-grant` — Grant Proposal Review

Runs a 6-agent pre-submission panel review of a grant proposal. The skill auto-detects the main proposal and supporting documents, then evaluates clarity, compliance signals, internal consistency, significance, innovation, research design, feasibility, budget logic, team readiness, and fit to the target funder or program.

**Installation:**

```bash
mkdir -p ~/.claude/skills/review-grant && curl -o ~/.claude/skills/review-grant/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-grant/SKILL.md
```

For a project-local install:

```bash
mkdir -p .claude/skills/review-grant && curl -o .claude/skills/review-grant/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-grant/SKILL.md
```

**Usage:**

```text
/review-grant
/review-grant NSF
/review-grant NIH path/to/proposal.pdf
```

**Supported funders/programs:**

- US federal science and health: `NSF`, `NIH`
- International research funders: `ERC`, `HorizonEurope`
- General proposal standards: `major-funder`, `foundation`

If no target is specified, the skill defaults to `major-funder`. If no path is provided, it auto-detects the main proposal file.

**Supporting files it can inspect:**

- Budgets and budget justifications
- Timelines and workplans
- Biosketches, CVs, and personnel documents
- Data-management plans, mentoring plans, and facilities statements
- Letters of support, appendices, and supplementary materials

**Output:**

Saves a consolidated report to `reviews/GRANT_PROPOSAL_REVIEW_[YYYY-MM-DD].md`, automatically versioning the filename if one already exists.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A proposal in a readable format such as `.md`, `.txt`, or `.tex`. The skill can also attempt to work with `.pdf` and `.docx`, while noting accessibility limitations if needed.

### `explain-diff` — Explain a Code Change

Explains a change to your analysis code well enough that someone who did not write it could defend it. This is the one skill here that is not a review. It is aimed at the coauthor who needs to understand what an AI assistant or a collaborator just did to the estimation pipeline, and at your future self returning to a project after six months.

The skill reads the diff and the surrounding code from scratch, ignoring any account of the change that already exists in the conversation, then writes a self-contained HTML page you open in a browser.

The idea comes from Geoffrey Litt's [Understanding is the new bottleneck](https://www.geoffreylitt.com/2026/07/02/understanding-is-the-new-bottleneck), which argues that once agents write most of the code, the scarce resource is not verification but the researcher's own grasp of the system — you need the concepts in your head to think about what to do next. Litt proposes explainer documents and embedded quizzes as a deliberate speed regulator. This skill is that proposal applied to empirical research code, where the thing you must not lose track of is what happened to the sample and the coefficients.

**What the page contains:**

| Section | Content |
|---|---|
| 1 | What the code did before, established by reading the surrounding scripts |
| 2 | What changed and why, in plain language with no code |
| 3 | Consequences for the results — which sample, which coefficients, which tables, and in which direction |
| 4 | Walkthrough of the changed code, grouped by purpose rather than by file |
| 5 | A five-question multiple-choice quiz with explanations for every option |

Section 3 is the point of the skill. It requires verification rather than inference: comparing observation counts and coefficients between runs, checking whether a modified table file differs in its numbers or only in a timestamp, and reading any new output file before quoting a figure from it. When nothing about the results changed, the page has to say so explicitly and show the evidence.

At least two quiz questions must test empirical consequences rather than syntax — which observations enter the sample, what the coefficient now identifies, what would change if an assumption failed.

**Installation:**

```bash
mkdir -p ~/.claude/skills/explain-diff && curl -o ~/.claude/skills/explain-diff/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/explain-diff/SKILL.md
```

For a project-local install:

```bash
mkdir -p .claude/skills/explain-diff && curl -o .claude/skills/explain-diff/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/explain-diff/SKILL.md
```

**Usage:**

```text
/explain-diff
/explain-diff abc123
/explain-diff main..HEAD
```

With no argument the skill explains the uncommitted working tree against `HEAD`, including files that are new and therefore invisible to `git diff`. A single ref is compared against the working tree. A range is used as given.

**Output:**

Writes one HTML file **outside the repository**, saved to `~/Documents/` unless you name another directory. Keeping the page out of the repo means it never lands in a commit or in your paper's folder, and the skill confirms with `git status` afterwards that nothing in the project changed. You also get a plain-text summary in the terminal, so you do not have to open the page to learn whether the results moved.

Filenames end in a ref tag so the pages stay matchable to commits as they accumulate: `2026-08-01-cluster-by-municipality-wt-e956a7e.html` for a working tree against `HEAD`, or the short SHAs for a ref or a range. The page itself carries the full 40-character SHAs, the branch, and the exact comparison. When the comparison involves an uncommitted working tree, the page says so and lists the files, because that state is not reproducible later from the SHA alone.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code). No subagents are used, so this skill runs in a single context.
- A git repository. Everything else — Stata, R, Python, LaTeX — is optional.

### `audit-analysis` — Adversarial Audit of Changed Analysis Code

Finds errors in changed empirical code before a referee does. The skill hands the diff to a subagent with a clean context and tells it to break the code. That isolation is the point: whoever wrote the code — including the current Claude session, if it helped — cannot steer the findings. It is the concrete form of the "fresh agent with no stake in the code" check, and it complements `review-paper-code`, which asks whether the paper matches the code rather than whether the code is right.

**What the auditor checks:**

| Area | Focus |
|---|---|
| Claims vs. code | Do comments and commit messages match what actually runs? |
| Sample | N before and after every filter, merge, and collapse, taken from logs |
| Merges | Keys, uniqueness, fate of unmatched observations, duplicate id-period pairs |
| Variables | Units, logs vs. levels, deflation, lag alignment, name vs. construction |
| Silent failures | Missings coerced to zero, `if x > 0` on missing, `destring ... force`, `fillna(0)` |
| Estimation | Clustering level and count, what the fixed effects absorb, weights, estimation N |

Every finding must cite a file, a line, and a quoted excerpt, and is tagged CONFIRMED (visible in the code) or SUSPECTED (needs the data). Unanchored findings are dropped and counted. The auditor also reports, category by category, where it found nothing, and closes with the one thing it could not check without the data.

**Installation:**

```bash
mkdir -p ~/.claude/skills/audit-analysis && curl -o ~/.claude/skills/audit-analysis/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/audit-analysis/SKILL.md
```

For a project-local install:

```bash
mkdir -p .claude/skills/audit-analysis && curl -o .claude/skills/audit-analysis/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/audit-analysis/SKILL.md
```

**Usage:**

```text
/audit-analysis
/audit-analysis main
/audit-analysis abc123
```

With no argument the working tree and commits are audited against `main`. Pass a branch, tag, or commit to audit against that instead. Diffs above roughly 1,500 changed lines are split across two auditors.

**Output:**

Findings are relayed in the terminal, worst first, without softening. Nothing is written or changed in the repository. If you want repairs, that is a separate request.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A git repository with Stata, R, or Python analysis code. Logs improve the sample checks but are not required.

### `paper-version` — Policy Brief, One-Page, or Five-Page Summary

Turns a LaTeX research paper into a version for a non-specialist audience, checks it against the paper, and produces a standalone HTML page ready for GitHub Pages. Four agents run in sequence: a reader extracts the paper's content and claims verbatim, a writer drafts the requested format, a reviewer compares every number and causal claim in the draft against the extraction, and — after you have read the review and edited the draft — a fourth agent builds the page.

**Formats:**

| Argument | Output |
|---|---|
| `brief` | Two-page policy brief with fixed sections: The Question, What We Do, Key Findings, Policy Implications, Caveats (500–600 words) |
| `1page` | One page of flowing prose for a general reader, leading with the main finding (350–400 words) |
| `5page` | Narrative summary with light structure: Background, What We Did, What We Found, Why It Matters, Limitations (1,400–1,600 words) |

The reviewer flags three kinds of problem: wrong or misattributed numbers, causal language stronger than the paper's own, and shifts in emphasis away from what the paper treats as central. The skill pauses after the review so you can edit the draft before the page is built.

**Installation:**

```bash
mkdir -p ~/.claude/skills/paper-version && curl -o ~/.claude/skills/paper-version/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/paper-version/SKILL.md
```

For a project-local install:

```bash
mkdir -p .claude/skills/paper-version && curl -o .claude/skills/paper-version/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/paper-version/SKILL.md
```

**Usage:**

```text
/paper-version brief
/paper-version 1page
/paper-version 5page
```

Run it from the paper's project folder. The skill finds the main `.tex` file and follows `\input` and `\include`.

**Output:**

Writes to an `output/` folder in the project: `paper_extraction.md`, `[format]_draft.md`, `[format]_review.md`, and `index.html`. PNG or JPG versions of the paper's key figures are embedded when they exist in the project.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A LaTeX paper.

### `pdf-to-markdown` — Convert a PDF to Readable Markdown

Converts a PDF to a markdown file saved next to it, with page markers every twenty pages and the text trimmed at the references or appendix so the main text is what enters the context window. Useful before running any of the review skills on a paper you only have as a PDF, and for reading long documents without spending context on the bibliography.

When `pdftotext` (part of poppler) is installed the conversion runs in one shot outside the model and takes seconds regardless of length. Without it the skill falls back to reading the PDF in twenty-page chunks, which works but is slow for long documents.

**Installation:**

```bash
mkdir -p ~/.claude/skills/pdf-to-markdown && curl -o ~/.claude/skills/pdf-to-markdown/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/pdf-to-markdown/SKILL.md
```

For a project-local install:

```bash
mkdir -p .claude/skills/pdf-to-markdown && curl -o .claude/skills/pdf-to-markdown/SKILL.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/pdf-to-markdown/SKILL.md
```

Recommended: `brew install poppler` (macOS) or `apt install poppler-utils` (Linux, WSL) for the fast path.

**Usage:**

```text
/pdf-to-markdown path/to/paper.pdf
```

**Output:**

`path/to/paper.md`, plus a short report: method used, pages processed, where the text was trimmed, and any unreadable pages.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code). No subagents are used.
- Optional: `pdftotext`. The page-count step uses macOS `mdls` when available and probes the file otherwise.

## License

MIT — free to use, adapt, and share.
