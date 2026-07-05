---
name: review-paper-light
description: Run a fast 2-agent pre-submission check for an economics paper — focuses on contribution, identification, and causal overclaiming. Completes in ~1 minute.
argument-hint: [optional: path/to/main.tex]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
disable-model-invocation: true
---

You are coordinating a fast pre-submission check of an economics paper. You will run 2 agents in parallel and consolidate their output into a short, prioritized report.

## Phase 1: Discover the Paper

If a file path is provided in `$ARGUMENTS`, use it as the main LaTeX file. Otherwise, auto-detect:

1. Use Glob with pattern `**/*.tex` to list all .tex files (exclude `_minted-*`, `build/`, `output/`).
2. Identify the main document among the .tex files containing `\documentclass` or `\begin{document}`. If several candidates match, discard beamer slides and files whose name or folder suggests an old draft or a response letter (`response*`, `letter*`, `slides*`, `old*`, `archive/`, etc.), then choose the candidate with the largest include-graph. If still ambiguous, ask the user.
3. Read the main file and extract all `\input{}`, `\include{}`, and `\subfile{}` references (recursively) to build the paper's include-graph.
4. Read all component .tex files. **The file list passed to the agents is exactly the main file plus its include-graph** — do not pass .tex files the paper does not include (old drafts, response letters, slides, notes).
5. Use Glob to find table files: `**/Tables/**/*.tex`, `**/tables/**/*.tex`, root-level `*table*.tex`. Keep only tables that are `\input{}`/`\include{}`d from the include-graph.

Record:
- Full path of each .tex file
- Paper title, authors, and abstract

## Phase 2: Launch 2 Agents in Parallel

In a **single message**, launch both agents using the Agent tool with `subagent_type: "general-purpose"`.

**Scope guard — prepend the following block verbatim to both agents' prompts:**

> Review ONLY the files listed at the end of this prompt. Do not use Glob, Grep, or directory listings to discover other files, and do not open any file that is not on the list. In particular, ignore any previous review reports (`QUICK_REVIEW_*.md`, `PRE_SUBMISSION_REVIEW_*.md`, anything in a `reviews/` folder), referee reports, response letters, notes, README files, and old drafts — none of these may influence your review. Within the listed .tex files, treat `%`-commented-out lines and `\todo{}` content as if they do not exist: review only the live text of the paper.

---

### AGENT A — Contribution, Identification & Required Analyses

You are a demanding associate editor at a top economics journal. Read all .tex files completely. Produce a focused evaluation of whether this paper is worth sending to referees.

**Part 1 — The Central Contribution**

- State in one sentence what the paper claims to contribute, in the authors' own framing.
- Classify the contribution type(s) — more than one may apply: new question, new data, new method, new setting, or new answer to an old question.
- From the paper's own bibliography and literature review, identify the 2–3 closest prior papers. For each, state in one sentence what this paper adds beyond it, grounded in what the results actually deliver. Do not rely on your general knowledge of the literature to assert what does or does not exist. If you draw on knowledge beyond the paper's bibliography, label the claim `[UNVERIFIED — authors must confirm]` and never invent citation details.
- Does the framing overstate? Does the introduction promise more than the results deliver?
- Rate the contribution: [Transformative | Significant | Incremental | Insufficient for a top field journal]
- Justify in 2–3 sentences, noting that novelty relative to uncited literature is not verified.

**Part 2 — Identification and Credibility**

- What variation does the paper use to identify its main result?
- Is this variation plausibly exogenous? What are the main threats?
- Does the paper adequately address these threats?
- Is the main finding causal, correlational, or descriptive? Does the paper claim the right thing?
- What would a skeptical econometrician at a seminar say?

**Part 3 — Required Analyses**

List up to 5 analyses whose absence is a blocker for acceptance. For each: state what it is, why its absence undermines credibility, and what a positive result would do for your view. If nothing is missing, write "None — the paper adequately addresses the main concerns."

Tag each required analysis `[CRITICAL]`.

**Part 4 — Pointed Questions to the Authors**

Write 3–5 specific, pointed questions that get at the paper's weakest points. Frame them as a referee would.

**Part 5 — Preliminary Recommendation**

Based on Parts 1–3, state exactly one of: [Send to referees | Revise before sending to referees | Desk reject], with one sentence of justification.

**Output format:**

```
## Agent A: Contribution & Identification

### Part 1 — Central Contribution
[assessment + rating]

### Part 2 — Identification and Credibility
[assessment]

### Part 3 — Required Analyses
[numbered list: [CRITICAL] Analysis | Why absence matters | What a positive result would do]

### Part 4 — Questions to the Authors
[numbered list of 3–5 questions]

### Part 5 — Preliminary Recommendation
[one of: Send to referees | Revise before sending to referees | Desk reject — with one sentence of justification]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT B — Causal Overclaiming & Unsupported Claims

You are a skeptical econometrician enforcing "claim discipline." Read all .tex files and flag every place where the paper overstates its evidence.

**What to check:**

1. **Causal language without causal identification**: Flag every specific sentence where causal language ("causes", "leads to", "drives", "determines", "because of", "due to", "results in") is applied to the main findings without genuine causal identification. Quote the exact sentence and explain why the language exceeds what the identification supports.

2. **Mechanism claims stated as facts**: When the paper explains *why* a result holds, flag every instance where a proposed mechanism is asserted rather than framed as a hypothesis.

3. **Generalization beyond the sample**: Claims that extend findings beyond the data's scope without adequate caveats (e.g., claiming broad policy implications from a single country; claiming current relevance for historical results without acknowledging context changes).

4. **Missing caveats**: Places where a reader would naturally ask "but what about...?" and the paper doesn't address it. Focus on the most obvious threats to internal validity for the specific research design: selection, reverse causality, measurement error, omitted variables.

5. **Statistical vs. economic significance**: Places where statistical significance is reported but economic significance is not discussed, or where "significant" is used as if it means "important."

6. **Unverified priority assertions**: "No prior study has examined X" or "We are the first to show Y" — flag every such claim. Authors must verify before submission.

Tag every issue `[CRITICAL]`, `[MAJOR]`, or `[MINOR]`.

**Output format:**

```
## Agent B: Causal Overclaiming & Unsupported Claims

### Causal Overclaiming
[numbered list: [CRITICAL] or [MAJOR] Section | "Exact quoted text" | Why it overclaims | Fix]

### Mechanism Claims Stated as Facts
[numbered list: [MAJOR] or [MINOR] same format]

### Missing Caveats
[numbered list: [CRITICAL] or [MAJOR] Topic | Where to address it | Suggested fix]

### Other Issues
[numbered list: [MAJOR] or [MINOR] same format]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

## Phase 3: Consolidate and Save

After both agents return, consolidate into a single report.

Save the report inside a `reviews/` subfolder of the paper's directory (create it if it does not exist) — keeping reports out of the paper's root directory prevents them from being picked up by future runs of this skill.

Check whether `reviews/QUICK_REVIEW_[YYYY-MM-DD].md` already exists. If so, append `-v2` (or `-v3`, etc.).

Save to: `reviews/QUICK_REVIEW_[YYYY-MM-DD].md`

**Report structure:**

```markdown
# Quick Pre-Submission Check

**Paper**: [Title]
**Authors**: [Authors]
**Date**: [Today's date]

---

## Overall Assessment

[2–3 sentences: (1) what the paper does; (2) contribution rating from Agent A; (3) the single most pressing issue from the Priority Items below.]

**Preliminary Recommendation**: [Copy exactly from Agent A Part 5 — do not paraphrase]

---

## 1. Contribution & Identification

[Agent A output]

---

## 2. Causal Overclaiming & Unsupported Claims

[Agent B output]

---

## Priority Action Items

Collect all tagged items and rank: `[CRITICAL]` first (identification and causal overclaiming items before others), then `[MAJOR]`, then `[MINOR]`.

**CRITICAL** (could cause desk rejection or major objections):
1. ...

**MAJOR** (will likely be raised by referees):
4. ...

**MINOR** (polish):
8. ...
```

After saving, report to the user:
1. Path to the saved report
2. Preliminary recommendation
3. Top 3 priority action items
4. Issue counts by severity
