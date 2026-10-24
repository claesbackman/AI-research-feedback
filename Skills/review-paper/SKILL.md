---
name: review-paper
description: Run a 6-agent pre-submission review of an academic economics paper, with a verification pass on the factual findings
argument-hint: [optional: path/to/main.tex] [optional: quick]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
disable-model-invocation: true
---

You are coordinating a pre-submission review of an academic economics paper. You will run 6 specialized review agents in parallel, verify their factual findings, and consolidate the result into a short, prioritized report.

## Phase 1: Find the Paper

Parse `$ARGUMENTS`: if it contains the word `quick`, set `VERIFY = no` and remove the word; otherwise `VERIFY = yes`. Any remaining text is the path to the main .tex file.

If no path was given:
1. Use Glob `**/*.tex` and keep files containing `\documentclass`. Discard beamer documents and files whose name or folder marks them as not the current paper (`response*`, `letter*`, `slides*`, `old*`, `archive/`, `previous/`, `submitted/`, `reviews/`).
2. If exactly one candidate remains, use it. Otherwise ask the user which file is the main document.

Then build the paper's file list from the source itself, not from folder searches:
- **.tex files**: the main file plus every file reached through `\input{}`, `\include{}`, and `\subfile{}`, recursively. Table files are part of this graph.
- **Figures**: the paths in `\includegraphics{...}` calls (resolve against `\graphicspath` if set; LaTeX often omits the extension).

Record the paper title, authors, and abstract. Pass the agents exactly this file list — never other .tex files in the folder.

## Phase 2: Launch 6 Review Agents in Parallel

In a **single message**, launch all 6 agents using the Agent tool with `subagent_type: "general-purpose"`.

**Prepend the following block verbatim to every agent's prompt:**

> Review ONLY the files listed at the end of this prompt. Do not search for or open any other file — in particular ignore previous review reports, referee reports, response letters, notes, and old drafts. Within the listed .tex files, treat `%`-commented-out lines and `\todo{}` content as if they do not exist.
>
> Report only problems. Do not list things that are fine, do not summarize the paper, and do not add preamble or closing remarks. Give every finding a location (section or file and line) and, where the finding is about specific text, quote that text exactly as it appears in the source so it can be found by search. Tag each finding `[CRITICAL]` (must fix before submission), `[MAJOR]` (a referee is likely to raise it), or `[MINOR]` (polish).

---

### AGENT 1 — Spelling, Grammar & Academic Style

You are a copy editor at a top economics journal. Read all .tex files and review the prose. Ignore LaTeX commands unless they cause visible formatting problems.

**What to check:**

1. **Spelling**: misspelled words, including proper nouns, technical terms, and commonly confused words (affect/effect, principal/principle, complement/compliment).
2. **Grammar**: subject-verb agreement, tense consistency (present tense for findings, past tense for what was done), articles, dangling modifiers, comma splices, run-ons, fragments.
3. **Awkward phrasing**: sentences that require re-reading. Suggest a clearer version.
4. **Style**:
   - Filler such as "interestingly", "importantly", "notably", "it is worth noting", "needless to say", "obviously", "clearly"
   - Tautologies ("very unique", "completely eliminate")
   - "significant" meaning large or important rather than statistically significant
   - Passive voice where active is natural ("it is shown that" → "we show that")
   - Inconsistent voice ("we find" vs. "the paper argues")
5. **Typography**: consistent hyphenation (long-run / long run; attributive vs. predicative compounds), dash usage, spacing around punctuation.
6. **Numbers**: numbers below 10 spelled out in prose; percentages written consistently (15% vs. 15 percent).

When the same problem recurs more than three times, report it once under Recurring Patterns with one example and the number of occurrences, rather than listing each instance.

**Output format:**

```
## Agent 1: Spelling, Grammar & Style

### Errors
[numbered: [TAG] Location | "exact text" → "correction" | reason]

### Recurring Patterns
[numbered: [TAG] Pattern | one example | count | global fix]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT 2 — Internal Consistency & Cross-References

You are a technical reviewer checking whether an economics paper contradicts itself. Read all .tex files, including the table files.

**What to check:**

1. **Numbers in text vs. tables**: every number quoted in the text (coefficients, percentages, sample sizes, years) must match the referenced table. Read the table source directly. State both values and their locations, e.g. "text says 1.3% (Section 4, line 212) but Table 2 column 3 shows 1.2". Numbers that appear only inside figures cannot be verified — skip them.
2. **Abstract, introduction, and conclusion vs. results**: findings previewed or summarized must match what the results sections and tables actually show, in direction and magnitude.
3. **Terminology**: key terms and variable names must keep the same meaning and name throughout.
4. **Sample**: years, number of observations, and filters must agree across abstract, data section, and table notes.
5. **Specifications**: fixed effects and controls described in the text must match what the tables report.
6. **Cross-references**: every `\ref`/`\eqref` points to an existing label, and the referenced element shows what the text says it shows.
7. **Citations**: every in-text citation has a matching bibliography entry.

**Output format:**

```
## Agent 2: Internal Consistency & Cross-References

### Contradictions
[numbered: [TAG] Location 1 ↔ Location 2 | what conflicts, with both values]

### Broken References and Citations
[numbered: [TAG] Location | problem]

### Terminology Drift
[numbered: [TAG] Term | how it varies, with locations | recommended standard]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT 3 — Unsupported Claims

You are a skeptical econometrician enforcing claim discipline: no sentence may claim more than the evidence supports. Read all .tex files. Work at the level of individual sentences — the overall research design is Agent 6's job.

**What to check:**

1. **Causal language without causal identification**: "causes", "leads to", "drives", "because of", "due to", "results in" applied to findings the design does not identify causally.
2. **Mechanisms stated as facts**: explanations for why a result holds that are asserted rather than tested or argued.
3. **Generalization beyond the sample**: broad or present-day policy claims from a narrow or historical sample without stated reasoning.
4. **Unverified priority claims**: "we are the first", "no prior study". Flag each as an assertion the authors must confirm; do not judge whether it is true.
5. **Statistical vs. economic significance**: significance reported without magnitude, or "significant" used to mean important.
6. **Hedging**: claims stated too strongly, and strong results hedged so much the point is lost.

Report at most the 12 most important findings. Quote every sentence you flag.

**Output format:**

```
## Agent 3: Unsupported Claims

[numbered: [TAG] Location | "exact sentence" | why it overclaims | suggested rewrite]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT 4 — Mathematics, Equations & Notation

You are a mathematical economist reviewing the formal content of an economics paper. Read all .tex files, focusing on equations, definitions, and derivations.

**What to check:**

1. **Correctness**: derivations follow from stated assumptions; no algebraic or arithmetic errors.
2. **Regression specifications**: each written equation matches its verbal description, the controls and fixed effects named in the text, and the table columns that estimate it.
3. **Notation**: each symbol means one thing throughout; indices are used consistently ($i$, $t$, $g$); every symbol is defined at or before first use.
4. **Equation references**: referenced equations are numbered and the references point to the right equation.
5. **Definitions of rates and units**: annualization and growth-rate formulas are correct; percent vs. percentage point is respected; log approximations are flagged.
6. **Inference**: standard error and clustering notation matches how the paper describes inference.
7. **LaTeX math formatting**: `*` for multiplication, text in math mode without `\text{}`, unbalanced or unsized delimiters.

**Output format:**

```
## Agent 4: Mathematics, Equations & Notation

### Errors
[numbered: [TAG] Equation/location | error | correction]

### Specification Mismatches
[numbered: [TAG] Equation ↔ text/table | discrepancy]

### Notation
[numbered: [TAG] Symbol | problem, with locations | resolution]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT 5 — Tables, Figures & Their Documentation

You are a journal production editor checking that every table and figure is complete, self-contained, and correctly described. Read all .tex files, including the table files. Figure image files cannot be read: judge figures from their captions, notes, and the text that describes them, and say so when the source gives too little to judge.

**For every table, check:**
1. The caption describes what the table contains, so it can be read without the body of the paper.
2. Column headers state the dependent variable and what differs across columns.
3. Notes cover: sample, dependent variable and units, controls, fixed effects, how standard errors are computed and clustered, what is in parentheses, and the significance-star thresholds.
4. Standard errors and N are reported in every column; differing samples across columns are explained.
5. The table is referenced in the text, and the text describes it correctly.

**For every figure, check:**
1. The caption describes what is plotted and is self-contained.
2. Notes cover: sample, what is plotted (raw data or residuals), what points and intervals represent, data source; for binscatters, the number of bins and absorbed controls.
3. Coefficient, event-study, and binscatter plots show confidence intervals, according to the notes.
4. The figure is referenced in the text, and the text describes it correctly.

**Across the paper:** consistent decimal places, star conventions, and fixed-effect indicators (Yes/No vs. checkmarks).

**Output format:**

```
## Agent 5: Tables, Figures & Documentation

### Tables
[by table: [TAG] Table X | missing or wrong element | suggested fix]

### Figures
[by figure: [TAG] Figure X | missing or wrong element | suggested fix]

### Consistency Across Exhibits
[numbered: [TAG] issue | where | standard to adopt]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]
The figures included in the paper are: [LIST FIGURE PATHS]

---

### AGENT 6 — Referee: Contribution, Identification & Required Analyses

You are an experienced, demanding referee in economics. You are not hostile, but you are specific: every point must refer to something in this paper, and a point that could be written about any paper should not be written. Read all .tex files completely.

**Part 1 — Contribution (at most 150 words)**
- State in one sentence what the paper contributes, as a reader would summarize it after the introduction.
- Does the introduction make this contribution clear within its first two paragraphs? If not, say what is missing or buried.
- Name the single table or figure that carries the paper, and say whether that result is strong enough to carry it.

Do not rate the contribution and do not judge novelty against literature the paper does not cite.

**Part 2 — Identification**
- What variation identifies the main result, and what are the most serious threats to it in this setting?
- Which threats does the paper address convincingly, and which does it leave open?
- Is the main finding causal, correlational, or descriptive — and does the paper claim the right one?

**Part 3 — Analyses**
- **Required** (at most 5, tag `[CRITICAL]`): robustness checks, placebo tests, or alternative explanations whose absence undermines the main result. Include analyses the paper says it ran but that do not appear. For each: what to run, why it matters, and what a reassuring result would look like.
- **Suggested** (at most 3, tag `[MAJOR]`): mechanism tests or extensions that would substantially strengthen the paper and are feasible with the data described.

If nothing is required, write "None".

**Part 4 — Questions to the Authors**
Write 3–5 pointed questions a referee would send, aimed at the paper's weakest points.

**Output format:**

```
## Agent 6: Referee Assessment

### Contribution
[≤150 words]

### Identification
[assessment]

### Required Analyses
[numbered: [CRITICAL] analysis | why | what a reassuring result looks like]

### Suggested Analyses
[numbered: [MAJOR] analysis | why | feasibility]

### Questions to the Authors
[numbered]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

## Phase 3: Verify the Findings

Agents misquote text and misread tables. Check their findings before they reach the report.

**Step 1 — Quote check (all agents).** For every finding that quotes text from the paper, Grep the paper's .tex files for a distinctive fragment of the quote (five words or so; LaTeX source may break lines and contain commands, so try a shorter fragment before concluding it is missing). Drop any finding whose quoted text does not exist in the source, and count how many you dropped.

**Step 2 — Verifier agent (skip if `VERIFY = no`).** Collect every `[CRITICAL]` and `[MAJOR]` finding from Agents 2, 4, and 5, plus any `[CRITICAL]` finding from Agent 3. Number them and launch one `general-purpose` agent with the same scope-guard block and file list, and this task:

> Below is a numbered list of findings that other reviewers made about this paper. For each, check the paper's source and decide whether the finding is correct. Do not look for new problems. For each finding reply with one line: `[number] CONFIRMED | REJECTED | UNCERTAIN — one-sentence reason`. Mark REJECTED when the source contradicts the finding (for example, the numbers actually match, the label exists, the note is present, the equation is correct). Mark UNCERTAIN only when the source cannot settle the question.

Then:
- Remove REJECTED findings from the report.
- Keep UNCERTAIN findings, appending `(unverified)`.
- Leave CONFIRMED findings unchanged.

Do not verify Agent 1 findings or Agent 6's assessments; those are judgments the source cannot settle.

## Phase 4: Consolidate and Save

If any agent returned no output or malformed output, insert a placeholder section ("Agent did not return output") and mention it in your summary to the user.

Give every remaining finding an ID: the agent number and its position, e.g. `2.3` for the third finding of Agent 2. Each finding appears **once** in the report, in its agent's section; the priority list refers to findings by ID and does not repeat them.

Save the report to `reviews/PRE_SUBMISSION_REVIEW_[YYYY-MM-DD].md` in the paper's directory (create `reviews/` if needed; if the file exists, append `-v2`, `-v3`, etc.).

**Report structure:**

```markdown
# Pre-Submission Review

**Paper**: [Title]
**Authors**: [Authors]
**Date**: [Today's date]
**Verification**: [e.g. "Quote check removed 3 findings; verifier confirmed 21, rejected 4, uncertain 2" — or "Verifier skipped (quick mode)"]

## Summary

[3–4 sentences, using only material from the agents: what the paper does (Agent 6 Contribution), the biggest threat to the main result (Agent 6 Identification), and the most serious mechanical problem found by Agents 2–5.]

## Fix First

[The 10 most important findings, as one line each: `ID — short description`. Order: CRITICAL findings from Agent 6 and Agent 3, then CRITICAL from Agents 2, 4, 5, then MAJOR findings by the same order. If there are fewer than 10 CRITICAL and MAJOR findings, list them all.]

**Counts**: [CRITICAL n | MAJOR n | MINOR n]

---

## 1. Referee Assessment
[Agent 6]

## 2. Unsupported Claims
[Agent 3]

## 3. Internal Consistency & Cross-References
[Agent 2]

## 4. Mathematics, Equations & Notation
[Agent 4]

## 5. Tables, Figures & Documentation
[Agent 5]

## 6. Spelling, Grammar & Style
[Agent 1]
```

After saving, report to the user:
1. The path to the saved report
2. The Fix First list
3. The counts by severity, and the verification line
