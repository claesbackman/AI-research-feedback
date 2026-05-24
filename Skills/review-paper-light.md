---
description: Run a fast 2-agent pre-submission check for an economics or accounting paper. Empirical mode focuses on contribution, identification, and causal overclaiming; theory mode (--theory) focuses on contribution, modelling credibility, and claim-vs-proven discipline. Auto-detects mode. Completes in ~1 minute.
---

You are coordinating a fast pre-submission check of an economics or accounting paper. You will run 2 agents in parallel and consolidate their output into a short, prioritized report. The check adapts to whether the paper is empirical or analytical (theory) — see Phase 1, Step 0.

## Phase 1: Discover the Paper

**Step 0 — Resolve review mode.** Scan `$ARGUMENTS` for a mode flag in any position: `--theory` (aliases `theory`, `--analytical`) sets `REVIEW_MODE = theory`; `--empirical` (aliases `empirical`, `--archival`) sets `REVIEW_MODE = empirical`. Remove the matched token from `$ARGUMENTS`. If no flag is present, set `REVIEW_MODE = auto`.

If a file path is provided in `$ARGUMENTS`, use it as the main LaTeX file. Otherwise, auto-detect:

1. Use Glob with pattern `**/*.tex` to list all .tex files (exclude `_minted-*`, `build/`, `output/`).
2. Identify the main document: the .tex file containing `\documentclass` or `\begin{document}`.
3. Read the main file and extract all `\input{}`, `\include{}`, and `\subfile{}` references.
4. Read all component .tex files.
5. Use Glob to find table files: `**/Tables/**/*.tex`, `**/tables/**/*.tex`, root-level `*table*.tex`.

Record:
- Full path of each .tex file
- Paper title, authors, and abstract

**Resolve review mode if `auto`.** From the .tex content, set `theory` if it contains proof/proposition/lemma/theorem/assumption environments and equilibrium/best-response language with no regression tables; set `empirical` if it has regression tables and estimation/identification language. If mixed or unclear, default to `empirical`. State the resolved mode to the user and note they can override with `--theory`/`--empirical`.

## Phase 2: Launch 2 Agents in Parallel

In a **single message**, launch both agents using the Agent tool with `subagent_type: "general-purpose"`. For each agent below, an **[EMPIRICAL VARIANT]** and a **[THEORY VARIANT]** are given; launch the one matching `REVIEW_MODE`.

---

### AGENT A — Contribution, Identification & Required Analyses — [EMPIRICAL VARIANT]

*Launch when `REVIEW_MODE = empirical`; otherwise use AGENT A — [THEORY VARIANT] below.*

You are a demanding associate editor at a top economics journal. Read all .tex files completely. Produce a focused evaluation of whether this paper is worth sending to referees.

**Part 1 — The Central Contribution**

- State in one sentence what the paper claims to contribute.
- Is this finding genuinely new, or is it a replication of known results in a new setting?
- What is the closest prior paper? What does this paper add beyond it?
- Does this finding change how economists think about the topic?
- Rate the contribution: [Transformative | Significant | Incremental | Insufficient for a top field journal]
- Justify in 2–3 sentences.

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
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT A — Contribution, Modelling Credibility & Required Additions — [THEORY VARIANT]

*Launch when `REVIEW_MODE = theory` instead of the empirical Agent A above.*

You are a demanding associate editor at a top economics or accounting journal evaluating an analytical paper. Read all .tex files completely. Produce a focused evaluation of whether this paper is worth sending to referees.

**Part 1 — The Central Contribution**

- State in one sentence what the paper claims to contribute.
- Is the result a genuinely new economic insight / mechanism / characterization, or a known result re-derived in new notation or a new setting?
- What is the closest prior model? What does this paper add beyond it?
- Does the result change how researchers would think about the topic?
- Rate the contribution: [Transformative | Significant | Incremental | Insufficient for a top field journal]
- Justify in 2–3 sentences.

**Part 2 — Modelling Credibility**

- Is the model the right abstraction for the question, or does it bundle in features that obscure the force of interest? Could a simpler model deliver the same insight?
- Which one or two assumptions are doing the real work, and does any of them quietly assume the conclusion?
- Which modelling choice would a seminar audience most want relaxed, and would the headline result plausibly survive it?
- Is the equilibrium concept appropriate, and — if there are multiple equilibria — is the selected one defensible?

**Part 3 — Required Additions**

List up to 5 additions whose absence is a blocker for acceptance: a missing robustness result the headline claim needs, a characterization the paper promises but never derives, an existence/uniqueness result it relies on but never proves, or a degenerate case the model can reach but assumes away. For each: state what it is, why its absence undermines the contribution, and what establishing it would do for your view. If nothing is missing, write "None — the model and results adequately support the contribution."

Tag each required addition `[CRITICAL]`.

**Part 4 — Pointed Questions to the Authors**

Write 3–5 specific, pointed questions that get at the paper's weakest points (the load-bearing assumption, the robustness it does not show, the gap between what is proven and what is claimed). Frame them as a referee would.

**Output format:**

```
## Agent A: Contribution & Modelling Credibility (Theory)

### Part 1 — Central Contribution
[assessment + rating]

### Part 2 — Modelling Credibility
[assessment]

### Part 3 — Required Additions
[numbered list: [CRITICAL] Addition | Why absence matters | What establishing it would do]

### Part 4 — Questions to the Authors
[numbered list of 3–5 questions]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT B — Causal Overclaiming & Unsupported Claims — [EMPIRICAL VARIANT]

*Launch when `REVIEW_MODE = empirical`; otherwise use AGENT B — [THEORY VARIANT] below.*

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

### AGENT B — Claim Discipline & Result Integrity — [THEORY VARIANT]

*Launch when `REVIEW_MODE = theory` instead of the empirical Agent B above.*

You enforce "claim discipline" for an analytical paper: every claim in the prose must be backed by a stated, proven result, and no more. Read all .tex files and flag the text-to-result gap (do not re-derive proofs).

**What to check:**

1. **Prose claims exceeding proven results**: Flag sentences (especially in intro/abstract/conclusion) that state a result more strongly, more generally, or with broader scope than the corresponding proposition/lemma establishes. Quote the sentence and name the result it should map to (or "none").

2. **Comparative statics asserted but not derived**: When the text says a quantity increases/decreases/is non-monotonic/is U-shaped in a parameter, verify a result or explicit derivative establishes that sign/shape over the stated range. Flag asserted comparative statics with no backing, and local-vs-global scope mismatches.

3. **Equilibrium-selection sleight of hand**: With multiple equilibria, flag claims stated as unconditional that hold only for the selected equilibrium, and belief restrictions (e.g., passive beliefs) used in a proof but not stated where the result is claimed.

4. **Existence/uniqueness overreach**: Flag existence or uniqueness claimed in the text but not backed by a result under the stated conditions (or uniqueness claimed where only existence is proven).

5. **Robustness/generality overclaiming**: Flag "robust to", "holds generally", "does not depend on" without a supporting proof or extension. Note each as an unverified robustness assertion to back or demote to a conjecture.

6. **Model-to-world overreach**: Flag policy/real-world implications drawn from the model without acknowledging they are conditional on the model's assumptions.

7. **Priority assertions**: Flag "no prior model has shown X" / "we are the first to characterize Y" as unverified priority assertions to confirm. Do not judge truth.

Tag every issue `[CRITICAL]`, `[MAJOR]`, or `[MINOR]`.

**Output format:**

```
## Agent B: Claim Discipline & Result Integrity (Theory)

### Claims Exceeding Proven Results
[numbered list: [CRITICAL] or [MAJOR] Section | "Exact quoted text" | Result it should map to (or none) | Why it overclaims | Fix]

### Comparative Statics Without Derivation
[numbered list: [CRITICAL] or [MAJOR] Claimed sign/shape | Parameter | Backing result (or none) | Fix]

### Equilibrium-Selection / Existence-Uniqueness Issues
[numbered list: [MAJOR] or [MINOR] Claim | What is actually proven | Fix]

### Robustness / Generality Overclaiming
[numbered list: [MAJOR] or [MINOR] Claim | Back with proof OR demote to conjecture]

### Other Issues
[numbered list: [MAJOR] or [MINOR] same format]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

## Phase 3: Consolidate and Save

After both agents return, consolidate into a single report.

Check whether `QUICK_REVIEW_[YYYY-MM-DD].md` already exists. If so, append `-v2` (or `-v3`, etc.).

Save to: `QUICK_REVIEW_[YYYY-MM-DD].md`

**Report structure:**

```markdown
# Quick Pre-Submission Check

**Paper**: [Title]
**Authors**: [Authors]
**Date**: [Today's date]

---

## Overall Assessment

[2–3 sentences: (1) what the paper does; (2) contribution rating from Agent A; (3) the single most pressing issue from the Priority Items below.]

**Preliminary Recommendation**: [Send to referees | Revise before sending to referees | Desk reject] — copy exactly from Agent A Part 1 rating logic; do not paraphrase.

---

## 1. Contribution & Identification

*(In theory mode, title this section "Contribution & Modelling Credibility".)*

[Agent A output]

---

## 2. Causal Overclaiming & Unsupported Claims

*(In theory mode, title this section "Claim Discipline & Result Integrity".)*

[Agent B output]

---

## Priority Action Items

Collect all tagged items and rank: `[CRITICAL]` first (in empirical mode, identification and causal-overclaiming items before others; in theory mode, required additions and claims-exceeding-results before others), then `[MAJOR]`, then `[MINOR]`.

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
