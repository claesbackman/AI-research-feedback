# Using AI to get feedback on your research

A collection of [Claude Code](https://claude.ai/code) skills for academic research review. This tool was developed by [Claes Bäckman](https://claesbackman.com).


## Skills in this repo

Each skill lives in its own folder containing a `SKILL.md` file:

- `Skills/review-paper/SKILL.md`: Full 8-agent referee-style paper review.
- `Skills/review-paper-light/SKILL.md`: Fast 2-agent paper check.
- `Skills/review-paper-code/SKILL.md`: Paper–code reproducibility and alignment review.
- `Skills/review-pap/SKILL.md`: Pre-analysis plan review.
- `Skills/review-grant/SKILL.md`: Grant proposal review.


## How the skills work

These are [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code). Install one into `~/.claude/skills/<name>/SKILL.md` and invoke it by typing `/<name>` (for example, `/review-paper`) inside Claude Code. The per-skill installation commands below create the required folder and download the `SKILL.md` for you.

A global install (`~/.claude/skills/`) is available in every project. A project-local install (`.claude/skills/`) applies only to that repository. Skills are picked up the next time you start Claude Code in the target directory.

Each skill sets `disable-model-invocation: true`, so a review runs only when you explicitly type its `/` command. Claude will never launch a multi-agent review on its own.

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

## License

MIT — free to use, adapt, and share.
