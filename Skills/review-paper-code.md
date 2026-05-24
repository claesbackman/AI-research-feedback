---
name: review-paper-code
description: Review research code for reproducibility and quality, extract the paper's claims, compare paper to code, and write a constructive markdown report. Empirical mode handles LaTeX papers with Stata/R/Python analysis code; theory mode (--theory) handles analytical papers with numerical-calibration/symbolic support code (Python, Julia, MATLAB, Mathematica), mapping propositions and figures to the code that verifies them. Auto-detects mode.
user-invocable: true
argument-hint: [optional: --theory|--empirical] [optional: path/to/main.tex] [optional: path/to/code_dir] [optional: main|full]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# Review Paper Code

Review a research project's paper and code for reproducibility, code quality, and paper-code alignment. Be constructive, concrete, and calibrated. Treat gaps as items to verify, not accusations. The review adapts to whether the project is empirical or analytical (theory) — see Phase 1.

## Scope

This skill supports:
- LaTeX papers
- Stata (`.do`), R (`.R`, `.r`), and Python (`.py`) code

Default review depth:
- `main`: prioritize the main paper, main scripts, and core outputs
- `full`: inspect all detected code files in scope

If no depth is provided, default to `main`.

## Phase 1: Discover the Project

First parse `$ARGUMENTS`:
- Scan for a mode flag in any position: `--theory` (aliases `theory`, `--analytical`) sets `REVIEW_MODE = theory`; `--empirical` (aliases `empirical`, `--archival`) sets `REVIEW_MODE = empirical`. Remove the matched token before further parsing. If no flag is present, set `REVIEW_MODE = auto`.
- If one argument looks like a `.tex` path, use it as `PAPER_FILE`.
- If one argument looks like a directory path, use it as `CODE_DIR`.
- If one argument is `main` or `full`, use it as `REVIEW_DEPTH`.

In `theory` mode the "code" being reviewed is the paper's **numerical/analytical support**: calibration scripts, numerical-example generators, simulation of equilibria, symbolic-algebra (e.g., SymPy/Mathematica) derivations, and the scripts that produce the paper's figures. The review reframes "reproducibility" as "can the numerical examples and figures be regenerated" and "paper-to-code mapping" as "does the code verify the propositions and produce the figures the paper claims." Languages in scope additionally include Python and Mathematica/`.nb`, MATLAB (`.m`), and Julia (`.jl`) where present.

If any of the above are missing, auto-detect them.

### 1. Find the paper

Use Glob to search for `**/*.tex`, excluding obvious build folders such as `_minted-*`, `build/`, `output/`, `.git/`, `node_modules/`.

Identify the main paper file as the best candidate containing `\documentclass` or `\begin{document}`.

If multiple candidates exist, prefer:
1. A path explicitly provided in `$ARGUMENTS`
2. A file in `Writing/`, `writing/`, `Paper/`, `paper/`, `Draft/`, or the repo root
3. The file that appears to include the most component files via `\input{}` / `\include{}`

Record the result as `PAPER_FILE`.

### 2. Find the code

If `CODE_DIR` was not provided, look for likely code roots in this order:
- `Code/`
- `Analysis/`
- `code/`
- `analysis/`
- `scripts/`
- `src/`
- `programs/`
- `replication/`

If no single directory is clearly best, use the repo root and limit later discovery to likely code files.

Record the result as `CODE_DIR`.

### 3. Find code files

Within `CODE_DIR` and subdirectories, find:
- `**/*.do`
- `**/*.R`
- `**/*.r`
- `**/*.py`

If `REVIEW_MODE = theory` (or `auto`), additionally find:
- `**/*.jl` (Julia)
- `**/*.m` (MATLAB/Octave)
- `**/*.nb`, `**/*.wl`, `**/*.wls` (Mathematica/Wolfram)
- `**/*.ipynb` (notebooks, common for calibration)

Exclude obvious caches, environments, and generated folders where appropriate.

If `REVIEW_DEPTH = main`, prioritize:
- Master scripts such as `main.do`, `master.do`, `run_all.R`, `main.R`, `main.py`, `run.py`
- Files referenced by those scripts
- Files that generate tables, figures, or final datasets
- If no master script exists, select the most central files and cap the initial review set at a reasonable number

If `REVIEW_DEPTH = full`, include all detected code files.

Record:
- `CODE_FILES_ALL`
- `CODE_FILES_REVIEWED`
- languages present

### 4. Find supporting documentation

Look for:
- `README.md`, `README.txt`, `readme.md`
- `requirements.txt`, `environment.yml`, `pyproject.toml`
- `renv.lock`, `DESCRIPTION`

Record relevant files as available.

### 5. Handle ambiguity gracefully

If you find a paper and at least some code, continue even if discovery is imperfect.

Only stop if you cannot find either:
- a main paper file, or
- any relevant Stata, R, or Python code files

If you stop, tell the user briefly what was missing and what paths they can pass explicitly.

Before proceeding, tell the user:
- the paper file chosen
- the code directory chosen
- the number of code files detected and the number selected for review
- the review depth
- the resolved review mode (and that it can be overridden with `--theory`/`--empirical`)
- any ambiguity worth noting

## Phase 2: Read the Paper

Read `PAPER_FILE`.

Recursively read files referenced by:
- `\input{}`
- `\include{}`
- `\subfile{}`

**Resolve review mode if `auto`.** Set `theory` if the paper contains proof/proposition/lemma/theorem/assumption environments and equilibrium/optimization language with no regression tables; set `empirical` if it has regression tables and estimation language. If mixed, default to `empirical` but extract both summaries below.

**[EMPIRICAL MODE] Extract a compact working summary for later cross-checking:**
- Paper title
- Main research question
- Main sample description
- Main data sources
- Main dependent variables
- Main explanatory variables or treatments
- Main estimation methods
- Fixed effects and clustering, if stated
- Main sample restrictions
- Main tables and figures only
- Headline quantitative claims only

Do not try to extract every statistic in the paper. Prioritize the main empirical design and the outputs most likely to map to code.

**[THEORY MODE] Extract instead:**
- Paper title and the central question
- The list of formal results (propositions, lemmas, corollaries, theorems) with a one-line statement of each
- The key parameters and their roles (e.g., precision, persistence/correlation, cost, threshold parameters), and any stated parameter ranges
- Every numerical example or calibration described in the text, with the parameter values stated for it
- Every figure that plots a model object (value/payoff against a parameter, a threshold, a region diagram), with what it is said to show and which result it illustrates
- Any closed-form expressions the paper says were obtained or verified by symbolic computation
- Headline qualitative claims that a numerical check could corroborate (a sign, a monotonicity, a single crossing, a non-monotonicity/U-shape)

Store this as `PAPER_SUMMARY`.

## Phase 3: Launch 2 Agents in Parallel

In a single message, launch both agents using the Agent tool with `subagent_type: "general-purpose"`. For each agent, an **[EMPIRICAL VARIANT]** and a **[THEORY VARIANT]** prompt are given; use the one matching `REVIEW_MODE`.

Each agent must produce a compact, high-signal output. Do not ask for exhaustive per-file prose on every file unless the project is very small.

---

### AGENT A: Code Reproducibility and Quality

Store as `CODE_REVIEW_SUMMARY`.

**[EMPIRICAL VARIANT]** Prompt *(use when `REVIEW_MODE = empirical`)*:

> You are reviewing research code for reproducibility and code quality in a social science / economics project.
>
> Files in scope:
> - Reviewed code files: [insert `CODE_FILES_REVIEWED`]
> - README / documentation files: [insert discovered supporting files or "none found"]
>
> Review the files and produce a compact report focused on the most decision-relevant findings.
>
> Check:
> 1. Hardcoded absolute paths or machine-specific assumptions
> 2. Randomized procedures without an obvious seed in local or upstream execution context
> 3. Outputs that appear to be consumed but not obviously generated in the reviewed pipeline
> 4. Data inputs and whether path conventions are consistent
> 5. Dependency management and software requirements
> 6. Run order and presence of a master script or documented pipeline
> 7. Large commented-out blocks, weak script structure, or hard-to-follow long files
> 8. Opaque transformations, unexplained filters, recodes, merges, or thresholds that are important for interpretation
>
> Use these labels:
> - PASS: looks solid
> - NOTE: minor improvement opportunity
> - VERIFY: worth human confirmation before treating as a problem
> - MISSING: expected project support file or documentation is absent
>
> Output exactly these sections:
>
> ## Overall
> 3-6 bullets on the overall state of the codebase.
>
> ## Top Findings
> Up to 10 items total, ordered by importance.
> Format each item as:
> - [LABEL] Short finding title — file(s): line reference(s) if available — why it matters — what to check next
>
> ## Strengths
> 3-8 bullets with genuine positives.
>
> ## Reproducibility Checklist
> One line each for:
> - Relative paths
> - Random seed practice
> - Outputs generated by pipeline
> - Dependency management
> - Run order
> - README / documentation
>
> Use this format:
> - Check name: PASS / NOTE / VERIFY / MISSING — brief note
>
> ## File Notes
> Include brief notes only for files that have a VERIFY, NOTE, or especially strong positive signal.
> Use at most 1-3 bullets per file.
>
> Be calibrated. If something might be handled in an upstream script, say so.

**[THEORY VARIANT]** Prompt *(use when `REVIEW_MODE = theory`)*:

> You are reviewing the numerical and analytical support code for an economic-theory paper. The code typically calibrates a model, generates numerical examples, computes thresholds/equilibria, performs symbolic derivations, and produces the paper's figures. There is usually no external dataset — "reproducibility" means a reader can re-run the scripts and regenerate the same numbers and figures.
>
> Files in scope:
> - Reviewed code files: [insert `CODE_FILES_REVIEWED`]
> - README / documentation files: [insert discovered supporting files or "none found"]
>
> Review the files and produce a compact report focused on the most decision-relevant findings.
>
> Check:
> 1. Hardcoded absolute paths or machine-specific assumptions
> 2. Stochastic procedures (Monte Carlo, random parameter draws) without a fixed seed — flag, since theory figures are expected to be exactly reproducible
> 3. Figures/numbers that the paper shows but that no reviewed script appears to generate
> 4. Parameter values: are the parameters hardcoded in scattered places or centralized? Do the values used match those stated in the paper? Flag silent disagreements between a value in the code and the same value in the text
> 5. Numerical-method soundness: root-finders / optimizers / fixed-point iterations without convergence checks or tolerances; reliance on a single starting value where multiplicity is possible; integration or grid resolution that could be too coarse for the claimed feature
> 6. Whether the code distinguishes a verified closed-form from a numerical approximation, and whether any symbolic result is checked against the paper's stated expression
> 7. Dependency/environment capture (Python/Julia/MATLAB/Mathematica versions and key package versions) and run order / master script
> 8. Opaque transformations or magic constants whose role is not explained
>
> Use these labels:
> - PASS: looks solid
> - NOTE: minor improvement opportunity
> - VERIFY: worth human confirmation before treating as a problem
> - MISSING: expected support file or documentation is absent
>
> Output exactly these sections:
>
> ## Overall
> 3-6 bullets on the overall state of the calibration/numerical code.
>
> ## Top Findings
> Up to 10 items, ordered by importance.
> Format: - [LABEL] Short finding title — file(s): line reference(s) if available — why it matters — what to check next
>
> ## Strengths
> 3-8 bullets with genuine positives.
>
> ## Reproducibility Checklist
> One line each for:
> - Relative paths
> - Seed practice (for any stochastic step)
> - Figures/numbers generated by the scripts
> - Parameter values centralized and matching the paper
> - Numerical-method robustness (tolerances, convergence, multiplicity handling)
> - Environment/version capture
> - Run order / master script
> - README / documentation
>
> Use this format: - Check name: PASS / NOTE / VERIFY / MISSING — brief note
>
> ## File Notes
> Brief notes only for files with a VERIFY, NOTE, or strong positive signal. At most 1-3 bullets per file.
>
> Be calibrated. If something might be handled in an upstream script, say so.

---

### AGENT B: Paper-to-Code Mapping

Store as `MAPPING_SUMMARY`.

**[EMPIRICAL VARIANT]** Prompt *(use when `REVIEW_MODE = empirical`)*:

> You are mapping a research paper's main empirical claims to its code implementation.
>
> Inputs:
> - Paper summary: [insert `PAPER_SUMMARY`]
> - Reviewed code files: [insert `CODE_FILES_REVIEWED`]
> - Code directory: [insert `CODE_DIR`]
>
> Read the code files as needed and identify whether the paper's core empirical design appears in the code.
>
> Focus on the main paper elements only:
> 1. Main tables and figures
> 2. Main variables and treatments
> 3. Main sample restrictions and time period
> 4. Main estimation methods
> 5. Fixed effects and clustering, if central
> 6. Main datasets or intermediate analysis files
>
> Use these confidence labels:
> - HIGH: clear and specific match
> - MEDIUM: plausible match but not airtight
> - LOW: weak or indirect match
> - NOT FOUND: no plausible match found in reviewed files
>
> Output exactly these sections:
>
> ## Verified Matches
> Up to 10 bullets.
> Format:
> - Paper element -> Code evidence -> HIGH / MEDIUM -> brief note
>
> ## Items To Verify
> Up to 12 bullets.
> Format:
> - Paper element -> Code evidence or absence -> LOW / NOT FOUND / MEDIUM -> why this deserves a check
>
> ## Likely Discrepancies
> Only include items where paper and code appear to point in different directions.
> Use up to 8 bullets.
>
> ## Coverage Notes
> 3-6 bullets on what was easy to match, what was ambiguous, and what may sit outside the reviewed files.
>
> Be conservative. Do not mark a match HIGH unless the specification, output, or variable mapping is genuinely clear.

**[THEORY VARIANT]** Prompt *(use when `REVIEW_MODE = theory`)*:

> You are mapping an economic-theory paper's formal results and numerical exhibits to its support code. The goal is to check whether the code actually verifies the propositions and generates the figures the paper claims, and whether the parameters used are consistent with the paper.
>
> Inputs:
> - Paper summary (results, parameters, numerical examples, figures): [insert `PAPER_SUMMARY`]
> - Reviewed code files: [insert `CODE_FILES_REVIEWED`]
> - Code directory: [insert `CODE_DIR`]
>
> Read the code as needed and assess these mappings:
> 1. Each numbered figure that plots a model object -> the script and code block that generates it
> 2. Each numerical example stated in the text (with its parameter values) -> the code that produces those numbers; check the values match
> 3. Each comparative-statics / qualitative claim the paper says it illustrates numerically (a sign, monotonicity, single crossing, non-monotonicity/U-shape) -> code that computes it; check the code actually exhibits that feature over the stated range, not just at one point
> 4. Each closed-form expression the paper says was derived or checked symbolically -> the symbolic computation, and whether it confirms the stated expression
> 5. Each threshold / equilibrium object the paper defines -> its computation in code, including how multiplicity or boundary cases are handled
> 6. Parameter definitions in code -> parameter definitions in the paper (flag any value that silently differs)
>
> Use these confidence labels: HIGH (clear, specific match), MEDIUM (plausible, not airtight), LOW (weak/indirect), NOT FOUND (no plausible match in reviewed files).
>
> Output exactly these sections:
>
> ## Verified Matches
> Up to 10 bullets. Format: - Paper element (result/figure/example) -> Code evidence (file:block) -> HIGH / MEDIUM -> brief note
>
> ## Items To Verify
> Up to 12 bullets. Format: - Paper element -> Code evidence or absence -> LOW / NOT FOUND / MEDIUM -> why this deserves a check
>
> ## Likely Discrepancies
> Only where paper and code point in different directions — e.g., a parameter value in code differs from the text, a figure's qualitative shape in code differs from the claimed shape, or a numerical example's reported number is not what the code produces. Up to 8 bullets.
>
> ## Coverage Notes
> 3-6 bullets on what was easy to match, what was ambiguous, and what may sit outside the reviewed files (e.g., a proof step never checked numerically).
>
> Be conservative. Do not mark a match HIGH unless the figure, number, or expression mapping is genuinely clear.

## Phase 4: Synthesize

After both agents return, synthesize the results yourself.

Do not launch another critic agent by default. Instead:
- compare the two outputs for agreement and tension
- downgrade any overconfident claims
- note where limited file coverage or naming ambiguity weakens confidence

If the repo is unusually complex and a second-pass critic is truly necessary, you may launch one additional agent. Otherwise, keep the workflow lean.

Create:
- `OVERALL_ASSESSMENT`: 2-4 sentences leading with what works
- `TOP_ACTIONS`: 3-8 concrete next steps, ordered by importance
- `MATCHED_ITEMS`: high-confidence paper-code matches
- `VERIFY_ITEMS`: gaps or ambiguous matches worth checking
- `NOT_FOUND_ITEMS`: important paper elements with no plausible code match in reviewed files

## Phase 5: Write the Report

Write the final report to the current working directory as:
- `code_review_report.md`

**In theory mode**, keep the same structure but: title the report "Numerical Support Review: [Paper Title]"; in the Reproducibility Checklist, replace the rows below with the theory checklist rows (parameter values match paper; seed practice for any stochastic step; figures/numbers regenerated by scripts; numerical-method robustness; symbolic results checked against stated expressions; environment/version capture; run order); and retitle "Paper-Code Consistency" as "Results/Figures-to-Code Consistency", mapping propositions, numerical examples, and figures rather than tables and regressions.

Use this structure:

```markdown
# Code Review Report: [Paper Title]

*Reviewed: [today's date] | Mode: [REVIEW_MODE] | Languages: [languages found] | Depth: [REVIEW_DEPTH] | Paper: [PAPER_FILE filename]*

## Overall Assessment

[2-4 sentences. Lead with strengths. Then summarize the main reproducibility or alignment issues worth checking.]

## What's Working Well

- [Specific positive]
- [Specific positive]
- [Specific positive]

## Reproducibility Checklist

| Check | Status | Details |
|---|---|---|
| Relative file paths | [PASS / NOTE / VERIFY / MISSING] | [...] |
| Random seed practice | [PASS / NOTE / VERIFY / MISSING] | [...] |
| Outputs generated by pipeline | [PASS / NOTE / VERIFY / MISSING] | [...] |
| Dependency management | [PASS / NOTE / VERIFY / MISSING] | [...] |
| Run order documented | [PASS / NOTE / VERIFY / MISSING] | [...] |
| README / documentation | [PASS / NOTE / VERIFY / MISSING] | [...] |

## Code Quality Summary

[Short prose summary grouped by module, pipeline stage, or only the files with notable findings. Do not force one paragraph per file if the project is large.]

## Paper-Code Consistency

### Matched
- [High-confidence match]

### Items To Verify
- [Paper element] — [what the paper says] — [what the code appears to do] — [why it is worth checking] — [specific suggested next step]

### Not Found In Reviewed Files
- [Important paper element] — [brief note]

## Suggested Next Steps

1. ...
2. ...
3. ...

## Appendix: Compact Evidence

### Code Review Summary
[Paste `CODE_REVIEW_SUMMARY`]

### Paper Summary
[Paste the compact `PAPER_SUMMARY`]

### Mapping Summary
[Paste `MAPPING_SUMMARY`]
```

Keep the final report readable. Prefer concise, high-signal summaries over exhaustive dumps.

## Final User Message

After writing the report, tell the user:
- that the code review is complete
- that the report was written to `code_review_report.md`
- the `Overall Assessment`
- 3-5 bullets from `What's Working Well`
- the top 3 suggested next steps
