# Using AI to get feedback on your research

A collection of [Claude Code](https://claude.ai/code) skills for academic research review. This tool was developed by [Claes Bäckman](https://claesbackman.com).


## Skills in this folder

- `Skills/review-paper.md`: Full referee-style paper review command.
- `Skills/review-paper-light.md`: Fast 2-agent paper check.
- `Skills/review-paper-code.md`: Paper-code reproducibility and alignment review.
- `Skills/review-pap.md`: Pre-analysis plan review command.
- `Skills/review-grant.md`: Grant proposal review command.


## Skills

### `review-paper` — Pre-Submission Referee Report

Runs a rigorous pre-submission review of an academic paper, simulating the scrutiny of a specific journal's editorial board. Six specialized review agents run in parallel and consolidate their findings into a single structured report.

**What it reviews:**

| Agent | Focus |
|---|---|
| 1 | Spelling, grammar, and academic style |
| 2 | Internal consistency and cross-reference verification |
| 3 | Unsupported claims and identification integrity |
| 4 | Mathematics, equations, and notation |
| 5 | Tables, figures, and their documentation |
| 6 | Contribution evaluation (adversarial journal-specific referee) |

**Installation:**

```bash
mkdir -p ~/.claude/commands && curl -o ~/.claude/commands/review-paper.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper.md
```

For a project-local install:

```bash
mkdir -p .claude/commands && curl -o .claude/commands/review-paper.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper.md
```

**Usage:**

```text
/review-paper
/review-paper QJE
/review-paper JF path/to/main.tex
/review-paper --theory TAR path/to/main.tex
/review-paper JAE --empirical path/to/main.tex
```

**Review mode (theory vs. empirical):**

The command runs in one of two modes. **Empirical mode** is the original behaviour (identification, causal overclaiming, regression-spec and table checks). **Theory mode** retargets three of the six agents for analytical/game-theoretic papers: claim discipline becomes "does the prose claim more than the propositions prove" (including undriven comparative statics and equilibrium-selection sleight of hand); the math agent audits proofs, assumption invocation, boundary cases, and equilibrium-concept consistency rather than regression specs; and the contribution agent evaluates modelling credibility (is the model the right abstraction, which assumptions do the work, do results survive perturbation) rather than econometric identification. Tables/figures checks are reinterpreted for calibration plots and region diagrams.

The mode is set by a `--theory` or `--empirical` flag, which may appear in any position. If no flag is given, the command auto-detects from the paper (proof/proposition environments and equilibrium language → theory; regression tables and estimation language → empirical) and falls back to empirical when signals are mixed. For reliability, pass the flag explicitly until you have seen auto-detection behave on your papers.

**Supported journals:**

| Category | Journals |
|---|---|
| Top-5 economics | `AER`, `QJE`, `JPE`, `Econometrica`, `REStud` |
| Finance | `JF`, `JFE`, `RFS`, `JFQA` |
| Macro | `AEJMacro`, `JME`, `RED` |
| Accounting | `TAR`, `JAR`, `JAE`, `CAR`, `RAST`, `AOS` |

If no journal is specified, the command applies high general standards without a specific journal persona. If no path is provided, it auto-detects the main `.tex` file.

**Output:**

Saves a consolidated report to `PRE_SUBMISSION_REVIEW_[YYYY-MM-DD].md` in the current directory, automatically appending `-v2`, `-v3`, and so on if a file already exists.

**Customization:**

- Add journals or fields by editing the recognized journal names list in the skill file.
- Add project-specific context in your prompt or in a local `CLAUDE.md` file.
- Adjust folder discovery or save paths directly in the skill if your project structure differs from the default assumptions.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent. (Verify the agent-spawning interface against your current Claude Code version; the commands assume `subagent_type: "general-purpose"`.)
- A LaTeX paper. The skill reads `.tex` files and optionally inspects figure and table files.

### `review-paper-light` — Quick Paper Check

Runs a fast 2-agent pre-submission check for an economics paper. It focuses on contribution, identification, causal overclaiming, and unsupported claims, and is designed for quick iteration before a full review.

**Installation:**

```bash
mkdir -p ~/.claude/commands && curl -o ~/.claude/commands/review-paper-light.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper-light.md
```

For a project-local install:

```bash
mkdir -p .claude/commands && curl -o .claude/commands/review-paper-light.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-paper-light.md
```

**Usage:**

```text
/review-paper-light
/review-paper-light path/to/main.tex
/review-paper-light --theory path/to/main.tex
```

In **theory mode** (`--theory`, or auto-detected), the two agents become: contribution + modelling credibility (is the model the right abstraction, which assumptions do the work, would the result survive a relaxed assumption, plus required additions like a missing robustness result or unproven existence claim), and claim discipline (prose claims exceeding proven results, undriven comparative statics, equilibrium-selection and existence/uniqueness overreach). In empirical mode the original contribution/identification and causal-overclaiming agents run.

If no path is provided, the command auto-detects the main `.tex` file.

**Output:**

Saves a short prioritized report to `QUICK_REVIEW_[YYYY-MM-DD].md` in the current directory, automatically versioning the filename if one already exists.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A LaTeX paper.

### `review-paper-code` — Paper-Code Reproducibility Review

Runs a paper-code review. In **empirical mode** it discovers the main LaTeX paper and analysis code, checks reproducibility and code quality, maps the paper's main empirical claims to the code, and writes a constructive report. In **theory mode** (`--theory`, or auto-detected) it treats the code as the paper's numerical/analytical support — calibration scripts, numerical-example generators, equilibrium/threshold computation, symbolic derivations, and figure-producing scripts — and maps the paper's propositions, numerical examples, and figures to the code that verifies and generates them.

**What it reviews:**

| Area | Empirical focus | Theory focus |
|---|---|---|
| Paper discovery | Main `.tex` file and included sections | Same |
| Code discovery | Stata, R, Python in analysis folders | Adds Julia, MATLAB, Mathematica/Wolfram, notebooks |
| Reproducibility | Paths, seeds, outputs, dependencies, run order | Parameter values match paper, seeds for stochastic steps, figures regenerated, numerical-method robustness, symbolic checks, environment capture |
| Code quality | Structure, commented-out code, opaque transforms | Same, plus convergence/tolerance/multiplicity handling and magic constants |
| Alignment | Tables, variables, sample restrictions, methods, clustering, FEs | Propositions, numerical examples, figures, thresholds/equilibria, parameter consistency |

**Usage:**

```text
/review-paper-code
/review-paper-code path/to/main.tex
/review-paper-code path/to/main.tex path/to/code_dir
/review-paper-code path/to/main.tex path/to/code_dir full
/review-paper-code --theory path/to/main.tex path/to/code_dir
```

**Review depth:**

- `main`: default; focuses on main scripts and core outputs
- `full`: reviews all detected code files in scope

The `--theory` / `--empirical` flag may appear in any position; if omitted, the mode is auto-detected from the paper.

**Output:**

Writes a report to `code_review_report.md` in the current working directory.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A LaTeX paper plus analysis code (Stata/R/Python in empirical mode; Python/Julia/MATLAB/Mathematica calibration or symbolic code in theory mode).

### `review-pap` — Pre-Analysis Plan Review

Runs a 6-agent pre-submission review of a pre-analysis plan (PAP). The command auto-detects the main PAP and supporting files, then evaluates writing quality, specification completeness, internal consistency, identification strategy, statistical analysis, implementation details, and registry or journal fit.

**Installation:**

```bash
mkdir -p ~/.claude/commands && curl -o ~/.claude/commands/review-pap.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-pap.md
```

For a project-local install:

```bash
mkdir -p .claude/commands && curl -o .claude/commands/review-pap.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-pap.md
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

If no target is specified, the command defaults to `top-journal`. If no path is provided, it auto-detects the main PAP file.

**Supporting files it can inspect:**

- Power calculations and sample-size worksheets
- Survey instruments and questionnaires
- Randomization protocols and sampling frames
- Code skeletons and mock tables
- Data dictionaries and ethics materials

**Output:**

Saves a consolidated report to `PAP_REVIEW_[YYYY-MM-DD].md` in the current directory.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A PAP in a readable format such as `.md`, `.txt`, or `.tex`. The skill can also attempt to work with `.pdf` and `.docx`, while noting accessibility limitations if needed.

### `review-grant` — Grant Proposal Review

Runs a 6-agent pre-submission panel review of a grant proposal. The command auto-detects the main proposal and supporting documents, then evaluates clarity, compliance signals, internal consistency, significance, innovation, research design, feasibility, budget logic, team readiness, and fit to the target funder or program.

**Installation:**

```bash
mkdir -p ~/.claude/commands && curl -o ~/.claude/commands/review-grant.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-grant.md
```

For a project-local install:

```bash
mkdir -p .claude/commands && curl -o .claude/commands/review-grant.md \
  https://raw.githubusercontent.com/claesbackman/AI-research-feedback/main/Skills/review-grant.md
```

**Usage:**

```text
/review-grant
/review-grant NSF
/review-grant NIH path/to/proposal.pdf
```

**Supported funders/programs:**

- US federal science and health: `NSF`, `NIH`, `ERC`, `HorizonEurope`
- General proposal standards: `major-funder`, `foundation`

If no target is specified, the command defaults to `major-funder`. If no path is provided, it auto-detects the main proposal file.

**Supporting files it can inspect:**

- Budgets and budget justifications
- Timelines and workplans
- Biosketches, CVs, and personnel documents
- Data-management plans, mentoring plans, and facilities statements
- Letters of support, appendices, and supplementary materials

**Output:**

Saves a consolidated report to `GRANT_PROPOSAL_REVIEW_[YYYY-MM-DD].md` in the current directory.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent.
- A proposal in a readable format such as `.md`, `.txt`, or `.tex`. The skill can also attempt to work with `.pdf` and `.docx`, while noting accessibility limitations if needed.

## License

MIT — free to use, adapt, and share.
