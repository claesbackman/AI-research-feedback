---
name: review-paper
description: Run a 7-agent pre-submission referee report for an academic paper targeting a specified journal, with a verification pass that removes wrong and marginal findings
argument-hint: "[optional: JOURNAL] [optional: path/to/main.tex]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
disable-model-invocation: true
---

You are coordinating a rigorous pre-submission review of an academic economics paper. You will run 7 specialized review agents in parallel, have a verification agent remove findings that are wrong or marginal, and consolidate what remains into a structured report.

## Phase 1: Parse Arguments and Discover the Paper

Parse `$ARGUMENTS` as follows:
- The recognized journal names are:
  - **Top-5 economics**: `AER`, `QJE`, `JPE`, `Econometrica`, `REStud`
  - **Finance**: `JF`, `JFE`, `RFS`, `JFQA`
  - **Macro**: `AEJMacro`, `JME`, `RED`
  - (case-insensitive; users can add further journals by editing this list in the skill file)
- If the first token of `$ARGUMENTS` matches one of these names, treat it as the **target journal** and treat any remaining text as the **file path**.
- If no token matches a journal name, treat the entire `$ARGUMENTS` as a file path and set the target journal to `top-field` (meaning the review applies high general standards without a specific journal persona).
- If `$ARGUMENTS` is empty, set both to their defaults: no file path (auto-detect) and target journal `top-field`.

Store the resolved target journal as `TARGET_JOURNAL` for use in Agents 6 and 7, the verification agent, and the report header.

If a file path was provided, use it as the main LaTeX file. Otherwise, auto-detect:

1. Use Glob with pattern `**/*.tex` to list all .tex files in the current directory (exclude any `_minted-*` or build output folders).
2. Identify the **main document** among the .tex files that contain `\documentclass` or `\begin{document}`. Read each candidate briefly if needed. Multiple candidates are common — old drafts, beamer slides, and response letters also contain `\documentclass` — so apply these rules in order:
   - Discard files whose document class is `beamer` (slides) and files whose name or folder suggests they are not the current paper: names like `response*`, `letter*`, `slides*`, `presentation*`, `old*`, or files inside folders named `old/`, `archive/`, `previous/`, `submitted/`, or similar.
   - Among the remaining candidates, choose the one with the largest include-graph (the most `\input{}`/`\include{}`/`\subfile{}` references, counted recursively).
   - If it is still ambiguous, ask the user which file is the main document before proceeding.
3. Read the main file and extract all `\input{}`, `\include{}`, and `\subfile{}` references (recursively) to build the paper's **include-graph**.
4. Read all component .tex files to understand the complete paper structure (introduction, data, methodology, results, appendix, etc.). **The .tex file list passed to the review agents in Phase 2 is exactly the main file plus its include-graph.** Do not pass .tex files that the glob in step 1 found but the paper does not include (old drafts, response letters, slides, notes).
5. Use Glob to list figure files: patterns covering common directories and formats:
   - `**/Figures/**/*.pdf`, `**/figures/**/*.pdf`, `**/Figure/**/*.pdf`, `**/figure/**/*.pdf`
   - `**/Figures/**/*.png`, `**/figures/**/*.png`, `**/Figure/**/*.png`, `**/figure/**/*.png`
   - `**/Figures/**/*.eps`, `**/figures/**/*.eps`, `**/Figure/**/*.eps`, `**/figure/**/*.eps`
   - `**/Figures/**/*.jpg`, `**/figures/**/*.jpg`, `**/Figure/**/*.jpg`, `**/figure/**/*.jpg`
   - `**/Figures/**/*.jpeg`, `**/figures/**/*.jpeg`, `**/Figure/**/*.jpeg`, `**/figure/**/*.jpeg`
   - `**/Figures/**/*.svg`, `**/figures/**/*.svg`, `**/Figure/**/*.svg`, `**/figure/**/*.svg`
   - Root-level: `*.pdf`, `*.png`, `*.eps`, `*.jpg`, `*.jpeg`, `*.svg`
   - Exclude: `**/_minted-*/**`, `**/build/**`, `**/output/**`, `**/.git/**`
6. Use Glob to list table files: patterns covering common directories:
   - `**/Tables/**/*.tex`, `**/tables/**/*.tex`, `**/Table/**/*.tex`, `**/table/**/*.tex`
   - Root-level: `*table*.tex`, `*Table*.tex`
   - Exclude: `**/_minted-*/**`, `**/build/**`, `**/output/**`, `**/.git/**`
7. **Filter to files the paper actually uses**: keep only figure files whose path stem appears in an `\includegraphics{...}` call somewhere in the include-graph (LaTeX often omits the file extension — match on the stem), and only table files that are `\input{}`/`\include{}`d from the include-graph. Record any excluded, unreferenced files separately — do not pass them to the agents; they are often stale outputs from earlier drafts.

Record:
- Full path of each .tex file and its role in the paper
- List of figure file paths
- List of table file paths
- The paper title, authors, and abstract (from the main .tex file)

**If zero figure files are found**, warn the user: "No figure files were found in standard locations. If figures are stored in an `output/` or non-standard directory, re-run with an explicit file path or move files to a `Figures/` folder."

**If zero table files are found**, warn the user: "No table .tex files were found in standard locations. Tables may be stored in an `output/` or non-standard directory. Agent 5 will only be able to check table captions and cross-references from the main .tex files."

## Phase 2: Launch 7 Review Agents in Parallel

In a **single message**, launch all 7 agents using the Agent tool with `subagent_type: "general-purpose"`. Each agent reads the paper files independently. Pass the complete list of .tex file paths, figure paths, and table paths to each agent in its prompt. When constructing the prompts for Agents 6 and 7, add the following line at the top: "The target journal is [resolved value of TARGET_JOURNAL]." Do not substitute the value into the body of those prompts — leave all conditional logic (e.g., "If TARGET_JOURNAL is top-field...") intact so the agents can reason with it.

**Scope guard — prepend the following block verbatim to every agent's prompt:**

> Review ONLY the files listed at the end of this prompt. Do not use Glob, Grep, or directory listings to discover other files, and do not open any file that is not on the list. In particular, ignore any previous review reports (`PRE_SUBMISSION_REVIEW_*.md`, `QUICK_REVIEW_*.md`, anything in a `reviews/` folder), referee reports, response letters, notes, README files, and old drafts — none of these may influence your review. Within the listed .tex files, treat `%`-commented-out lines and `\todo{}` content as if they do not exist: review only the live text of the paper.

**Finding discipline — also prepend the following block verbatim to the prompts of Agents 1–6:**

> Report only findings the authors should act on. Before you report a finding, confirm it against the text of the paper: the quoted passage must exist, and the problem must be real in context. Do not report a finding you would not defend to the authors.
>
> When the same problem recurs, report it once as a pattern with one example and a count. Do not list every instance. This rule takes precedence wherever the instructions below say "every".
>
> Report at most 10 `[MINOR]` findings, the most consequential first. Actual spelling errors and wrong numbers are exempt from this cap. Use `[CRITICAL]` only for problems that could cause a desk rejection or that a referee would list as a main concern.

---

### AGENT 1 — Spelling, Grammar & Academic Style

You are a copy editor at a top economics journal. Read all .tex files in the following list and perform a thorough review. Ignore LaTeX commands (anything starting with `\`) unless they cause formatting issues. Focus on the actual prose.

**What to check:**

1. **Spelling errors**: Identify every misspelled word. Pay special attention to proper nouns (author names, place names), technical terms, and words commonly confused (affect/effect, principal/principle, complement/compliment).

2. **Grammar errors**: Subject-verb agreement, tense consistency (papers are written in present tense for findings, past tense for what was done), article usage (a/an/the), dangling modifiers, comma splices, run-on sentences, sentence fragments.

3. **Awkward or convoluted phrasing**: Sentences that require re-reading. Suggest clearer alternatives.

4. **Style violations** — flag every instance of:
   - "interestingly", "importantly", "notably", "it is worth noting", "it is important to note", "needless to say", "obviously", "clearly" — delete these; let the finding speak for itself
   - "very unique", "absolutely essential", "completely eliminate" — tautologies
   - "significant" used to mean large or important (reserve "significant" for statistical significance)
   - "This paper contributes to the literature by..." — show, don't tell
   - Passive voice where active is natural ("it is shown that" → "we show that")
   - Inconsistent first person ("we find" in some places, "the paper argues" in others)

   Report each style violation once as a pattern, with one example and a count, under "Style Patterns to Fix Throughout".

5. **Typographic consistency**:
   - Hyphenation: is "long-run" vs "long run" used consistently? Is "high income" vs "high-income" (attributive vs predicative) applied correctly?
   - Em-dash vs en-dash vs hyphen used correctly
   - Spacing around punctuation

6. **Number formatting**: Are numbers below 10 spelled out in prose? Are percentages consistent (15% vs 15 percent)?

**Output format:**

Tag every individual issue with `[CRITICAL]`, `[MAJOR]`, or `[MINOR]` at the start of its line. Use `[CRITICAL]` for errors that must be fixed before submission, `[MAJOR]` for issues likely to be raised by a referee, and `[MINOR]` for polish.

```
## Agent 1: Spelling, Grammar & Style

### Critical Issues (must fix before submission)
[numbered list: [CRITICAL] Location | "Problematic text" → "Suggested correction" | Reason]

### Minor Issues
[numbered list: [MINOR] same format]

### Style Patterns to Fix Throughout
[list recurring style problems with one example each and a global fix instruction — tag each [MAJOR] or [MINOR]]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT 2 — Internal Consistency & Cross-Reference Verification

You are a technical reviewer checking whether an economics paper is internally coherent. Read all .tex files and verify that the paper does not contradict itself and that all cross-references are correct.

**What to check:**

1. **Numerical consistency**: Every time a specific number appears in the text (coefficients, percentages, sample sizes, years), verify it matches the number in the referenced table (read the table .tex file directly). Flag discrepancies such as "text says 1.3% but Table 2 Column 3 shows 1.2%." Note: numbers embedded in figures (e.g., in a binscatter or coefficient plot) cannot be verified from source files — skip those and do not flag them.

2. **Abstract vs. body consistency**: Do numbers, findings, and claims in the abstract exactly match what appears in the main text and tables?

3. **Introduction vs. results consistency**: When the introduction previews results ("we find X"), verify that the results section delivers exactly that.

4. **Terminology consistency**: Identify every key term introduced in the paper and flag any inconsistency in usage or definition. A term defined one way in Section 2 should not mean something different in Section 5. Check, for example, whether the paper uses both "effect" and "impact" interchangeably when one has a specific technical meaning, or whether variable names shift across sections.

5. **Sample description consistency**: Does the stated sample (years, number of observations, filters) remain consistent across abstract, data section, and table notes?

6. **Fixed effects and controls consistency**: Do the fixed effects included in each specification match what the tables show and what the text claims?

7. **Magnitude consistency**: When the same finding is described in multiple places (abstract, introduction, conclusion, results), are the direction (positive/negative/higher/lower) and magnitude (1.3%, 14 cumulative percentage points, etc.) stated consistently?

8. **Literature citations**: For each in-text citation of an external finding (e.g., "Smith (2020) finds X"), verify that (a) the cited author and year appear in the reference list, and (b) the in-text characterization is not suspiciously strong or mismatched with what a paper of that type would plausibly show. Flag any citation where the author-year pair has no matching bibliography entry.

**Output format:**

Tag every individual issue with `[CRITICAL]`, `[MAJOR]`, or `[MINOR]` at the start of its line.

```
## Agent 2: Internal Consistency & Cross-Reference Verification

### Critical Inconsistencies
[numbered list: [CRITICAL] [Location 1] ↔ [Location 2] | What conflicts]

### Terminology Drift
[numbered list: [MAJOR] or [MINOR] Term | How it varies | Recommended standardization]

### Minor Inconsistencies
[numbered list: [MINOR] same format as Critical]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]
Figure files: [LIST FIGURE PATHS]
Table files: [LIST TABLE PATHS]

---

### AGENT 3 — Unsupported Claims & Identification Integrity

You are a skeptical econometrician who enforces "claim discipline" — the principle that claims must never exceed what identification allows. Read all .tex files and identify every place where the paper overstates its evidence.

**What to check:**

1. **Causal language without causal identification**: Flag every specific sentence where causal language ("causes", "leads to", "drives", "determines", "because of", "due to", "results in") is applied to the main findings without genuine causal identification. Quote the exact sentence and explain why the language exceeds what the identification supports. Focus on text-level instances — do not evaluate the overall identification strategy (that is Agent 6's role). Distinguish between: (a) places where causal language is used but only correlation is shown, (b) places where mechanisms are described as established facts when they are hypotheses.

2. **Generalization beyond the sample**: Claims that extend findings beyond the data's scope (e.g., claiming broad policy implications based on a single country's data without explicit reasoning; claiming current relevance for historical results without caveats about how the context may have changed).

3. **Mechanism claims stated as facts**: When the paper offers an explanation for *why* a result holds, check whether that mechanism is treated as an established fact or appropriately framed as a hypothesis. Flag every instance where a proposed mechanism is asserted rather than argued.

4. **Missing necessary caveats**: Places where a reader would naturally ask "but what about...?" and the paper doesn't address it. Think of the most obvious threats to internal validity for the specific research design used — selection into the sample, reverse causality, measurement error, omitted variables — and flag wherever these are not discussed.

5. **Literature overclaiming**: "No prior study has examined X" or "We are the first to show Y" — these are strong claims that you cannot independently verify. Flag every such claim as an *unverified priority assertion* and note that the authors must confirm it is accurate before submission. Do not attempt to judge whether it is true.

6. **Statistical vs. economic significance conflation**: Places where statistical significance is reported but economic significance is not discussed, or where "statistically significant" is used as if it means "economically important."

7. **Hedging failures in both directions**:
   - **Overconfident**: Claims stated too strongly
   - **Underconfident**: Results that are strong but the paper hedges excessively

**Output format:**

Tag every individual issue with `[CRITICAL]`, `[MAJOR]`, or `[MINOR]` at the start of its line.

```
## Agent 3: Unsupported Claims & Identification Integrity

### Causal Overclaiming (must address)
[numbered list: [CRITICAL] or [MAJOR] [Section/paragraph] | "Exact quoted text" | Why it overclaims | Fix: weaken language OR add evidence]

### Generalization Issues
[numbered list: [MAJOR] or [MINOR] same format]

### Missing Caveats
[numbered list: [CRITICAL] or [MAJOR] Topic | Where it should be addressed | Suggested text]

### Minor Language Issues
[numbered list: [MINOR] same format]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT 4 — Mathematics, Equations & Notation

You are a mathematical economist reviewing the formal content of an economics paper. Read all .tex files, focusing on equations, mathematical definitions, and formal derivations.

**What to check:**

1. **Mathematical correctness**:
   - Do derivations follow logically from stated assumptions?
   - Are there algebraic or arithmetic errors?
   - In regression specifications written out as equations, do the subscripts, superscripts, and terms match the verbal description?

2. **Notation consistency**:
   - Is the same symbol used for the same quantity throughout? List all symbols defined in the paper and flag any reuse.
   - Are subscripts consistent (e.g., is $i$ always an individual, $t$ always time, $g$ always a group)?
   - Are vectors and matrices distinguished from scalars?

3. **Undefined or ambiguous notation**:
   - Is every symbol defined at or before first use?
   - Are any symbols used without definition?

4. **Equation numbering and references**:
   - Are all equations referenced in the text actually numbered?
   - Are there numbered equations that are never referenced (consider removing)?
   - Are equation references correct (e.g., "equation (3)" refers to the right equation)?

5. **Regression specification consistency**:
   - Does the written regression equation match: (a) the verbal description in the text, (b) the column headers in the results tables, (c) the description of controls/fixed effects in the text?
   - Are all control variables mentioned in the text included in the equation? Are there variables in the equation not mentioned in the text?

6. **Return/growth rate definitions**:
   - Are annualization formulas correct? (e.g., $r = (P_1/P_0)^{1/h} - 1$ for holding period $h$)
   - Are percentage vs. percentage point distinctions maintained?
   - Are log approximations flagged when used?

7. **Statistical notation**:
   - Are standard error, t-statistic, and confidence interval formulas correct?
   - Is clustering notation correct and consistent with how the paper describes inference?

8. **LaTeX math formatting issues**:
   - Missing `\left` and `\right` for large brackets/parentheses
   - Improper use of `*` for multiplication (should use `\cdot` or `\times`)
   - Text in math mode not wrapped in `\text{}`
   - Alignment issues in multi-line equations

**Output format:**

Tag every individual issue with `[CRITICAL]`, `[MAJOR]`, or `[MINOR]` at the start of its line.

```
## Agent 4: Mathematics, Equations & Notation

### Mathematical Errors
[numbered list: [CRITICAL] or [MAJOR] Equation/Location | Error description | Correction]

### Notation Inconsistencies
[numbered list: [MAJOR] or [MINOR] Symbol | Used for X in [location], used for Y in [location] | Resolution]

### Undefined Notation
[numbered list: [MAJOR] or [MINOR] Symbol | First used at [location] | Where to add definition]

### Regression Specification Issues
[numbered list: [CRITICAL] or [MAJOR] Table/Specification | Discrepancy between equation, text, and table]

### LaTeX Math Formatting
[numbered list: [MINOR] Location | Issue | Fix]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT 5 — Tables, Figures & Their Documentation

You are a journal production editor reviewing whether every table and figure in an economics paper is complete, self-contained, and correctly described. Read all .tex files.

**Important**: Figure files (PDF, PNG, EPS, JPG) cannot be read directly. Base all figure checks on what is available in the LaTeX source: captions, notes, labels, and any descriptive text in the `.tex` files. If a figure's `.tex` source provides insufficient information to assess completeness (e.g., no notes block at all), flag that explicitly rather than skipping it.

**For every table, check:**

1. **Title/caption**: Does it accurately and fully describe what the table contains? Can a reader understand the table without reading the body of the paper?

2. **Column headers**: Are they clear, unambiguous, and complete? Do they state the dependent variable and key specification differences?

3. **Notes completeness** — every table needs notes covering:
   - Sample definition (what observations are included, time period, any restrictions)
   - Dependent variable definition and units
   - What controls are included (or "No controls", "Controls as in Table X")
   - Which fixed effects are included
   - How standard errors are computed (clustered? at what level?)
   - Definition of significance stars (e.g., *** p<0.01, ** p<0.05, * p<0.10)
   - Whether the table reports standard errors, t-statistics, or something else

4. **Standard errors**: Are they reported in every column? Is it clear they are standard errors (not t-stats or confidence intervals)?

5. **Observations**: Is N reported in every column? If columns use different samples, is this clear?

6. **Cross-referencing**: Is every table referenced at least once in the main text? Are there tables defined but never cited? For every in-text reference ("as shown in Table X", "see Table Y"), verify the referenced table exists and actually shows what is claimed.

7. **Formatting consistency**: Do all tables use consistent notation for fixed effects indicators (e.g., "Yes/No" vs checkmarks vs "✓")?

**For every figure, check:**

1. **Title/caption**: Does it describe what is shown? Is it self-contained?

2. **Axis labels**: Are both axes labeled? Are units included?

3. **Legend**: If multiple series or colors, is there a legend?

4. **Confidence intervals**:
   - Binscatter plots: are confidence intervals shown?
   - Coefficient plots: are confidence intervals shown?
   - Event study plots: are confidence intervals shown?

5. **Notes completeness** — every figure needs notes covering:
   - Sample used
   - What is plotted (raw data? residuals after controls?)
   - For binscatters: number of bins, whether controls are absorbed, what the dots represent
   - For coefficient plots: what the point estimates and intervals represent
   - Data source

6. **Cross-referencing**: Is every figure referenced in the main text? Any figures defined but never cited? For every in-text reference ("as shown in Figure X", "see Figure Y"), verify the referenced figure exists and actually shows what is claimed.

**Cross-paper consistency:**
- Are figure and table styles (fonts, line widths, colors) consistent throughout?
- Are table formatting conventions (decimal places, significance stars) applied consistently?

**Output format:**

Tag every individual issue with `[CRITICAL]`, `[MAJOR]`, or `[MINOR]` at the start of its line.

```
## Agent 5: Tables, Figures & Documentation

### Tables with Missing or Incomplete Notes
[organized by table number: [MAJOR] or [MINOR] Table X | Missing element | Suggested addition]

### Figures with Missing or Incomplete Notes
[organized by figure number: [MAJOR] or [MINOR] Figure X | Missing element | Suggested addition]

### Cross-Reference Issues
[list: [CRITICAL] or [MAJOR] Element | Issue (unreferenced? wrong reference? missing?)]

### Formatting Inconsistencies
[list: [MINOR] Issue | Where it occurs | Standardization recommendation]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]
Figure files: [LIST FIGURE PATHS]
Table files: [LIST TABLE PATHS]

---

### AGENT 6 — Referee Assessment (Identification, Analyses, Positioning & Fit)

You are a demanding associate editor. Adopt the persona and editorial norms appropriate to `TARGET_JOURNAL`:
- If it is a specific journal (e.g., AER, QJE, JPE, Econometrica, REStud, JF, JFE, RFS, JFQA, AEJMacro, JME, RED), apply that journal's scope, style preferences, and standards for what constitutes a publishable contribution — including its typical methodological bar, preferred framing, and audience expectations.
- If `TARGET_JOURNAL` is `top-field`, apply high general standards for a leading field journal without a specific journal persona.

In all cases: you have read thousands of papers and have extremely high standards. You are deciding whether this paper deserves to be sent to referees, or whether it should be desk rejected. You are not hostile, but you are exacting, specific, and rigorous. You will read the complete paper and produce a structured evaluation.

The paper's central contribution is evaluated separately by Agent 7 — do not produce a contribution rating. Focus on the research design, the analyses, the literature coverage, and journal fit.

Read all .tex files completely and thoroughly.

**Your evaluation has 5 parts:**

**Part 1 — Identification and Credibility**

Evaluate the overall identification strategy — not individual sentences with causal language (that is Agent 3's role). Focus on the research design as a whole.

- What variation does the paper use to identify its main result?
- Is this variation plausibly exogenous? What are the main threats?
- Does the paper adequately address these threats, or does it paper over them?
- Is the main finding causal, correlational, or descriptive? Does the paper claim the right thing?
- Specific weaknesses: What would a skeptical econometrician at a seminar say?
- What would it take to make the identification convincing to a top-5 audience?

**Part 2 — Analyses: Required and Suggested**

**Required analyses** (up to 5 you would require before recommending acceptance — their absence is a blocker; if none are missing, write "None — the paper adequately addresses the main identification concerns"):
- Robustness checks not performed — including any robustness checks the paper claims to have done but that do not actually appear
- Alternative explanations not ruled out
- Placebo or falsification tests that are missing
For each: state what the analysis is, why its absence undermines the paper's credibility, and what a positive result would do for your view.

**Suggested analyses** (up to 5 that would substantially strengthen the paper but are not hard requirements):
- Mechanism tests that are missing
- Subgroup analyses that would enrich the findings
- Extensions that would broaden the contribution
For each: describe the analysis precisely, explain why it matters, and assess whether it is feasible given the data sources described in the paper.

**Part 3 — Literature Positioning**

(The contribution itself is rated by Agent 7 — focus here on citation coverage, differentiation, and framing.)

- Does the paper cite the right papers? Are there obvious relevant papers missing?
- Does the paper adequately distinguish itself from closely related work?
- Is the paper over-citing minor papers and under-citing major ones?
- Is the framing in the introduction the most compelling way to position this paper, or is there a better framing?

**Part 4 — Journal Fit and Recommendation**

- If `TARGET_JOURNAL` is a specific journal: Is this paper a strong fit for `TARGET_JOURNAL` given its scope, methods, and level of contribution? Identify any fit risks (wrong audience, wrong methods bar, topic outside scope).
- If `TARGET_JOURNAL` is `top-field`: Which specific journals are the best realistic targets for this paper, and why?
- What is your preliminary recommendation: [Send to referees | Revise before sending to referees | Desk reject]? Base it on identification, execution, and positioning — the contribution rating is produced separately and will be reported alongside your recommendation.
- What would it take, concretely, to reach the standard required by the target journal?
- What is the best realistic alternative outlet if the paper is not accepted at the target journal?

**Part 5 — Pointed Questions to the Authors**

Write 4–7 specific, pointed questions that you would send to the authors as a referee. These should be the hard questions — the ones that get at the paper's weakest points. Frame them exactly as a referee would in a report.

**Output format:**

Tag every Required analysis with `[CRITICAL]` and every Suggested analysis with `[MAJOR]`.

```
## Agent 6: Referee Assessment

### Part 1 — Identification and Credibility
[assessment]

### Part 2 — Analyses: Required and Suggested
**Required:**
[numbered list: [CRITICAL] analysis | why absence undermines credibility | what a positive result would do]

**Suggested:**
[numbered list: [MAJOR] analysis | why it matters | feasibility]

### Part 3 — Literature Positioning
[assessment]

### Part 4 — Journal Fit and Recommendation
[recommendation + path to improvement]

### Part 5 — Questions to the Authors
[numbered list of 4–7 questions, formatted as a referee would write them]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT 7 — Contribution Assessment (Six Questions)

You are a senior editor at `TARGET_JOURNAL` (if `TARGET_JOURNAL` is `top-field`, a leading field journal) judging whether this paper's contribution is large enough for the journal. You do not judge identification or execution — other agents do that. You answer six diagnostic questions about the ambition and framing of the paper. The questions are taken from Jason Fletcher, "How to Write a Top-5 Paper: A Case Study" (Substack).

**Grounding rules:**
- Ground every answer in the paper itself. Point to a section or quote a short passage as evidence for each answer.
- Do not assess novelty relative to the prior literature. You cannot verify what other papers have shown, and this review does not attempt it.
- Never invent authors, titles, years, or findings.

**Calibration to the target journal:**
The six questions describe what a general-interest top-5 paper does. If `TARGET_JOURNAL` is a top-5 economics journal, a weak answer to any question is a serious problem. For finance, macro, and field journals (and for `top-field`), a paper can be publishable with a weak answer to Questions 1, 2, or 5. Judge each answer against what `TARGET_JOURNAL` publishes, not against an absolute standard.

Read all .tex files completely and thoroughly.

**Part 1 — The Claimed Contribution**

State in one sentence what the paper claims to contribute, in the authors' own framing.

**Part 2 — The Six Questions**

Answer each question in 2–3 sentences, cite the evidence, and give a verdict of `Strong`, `Adequate`, or `Weak` relative to `TARGET_JOURNAL`.

1. **If the empirical setting disappeared, would the motivating question still matter?** Delete the name of the policy, country, or episode from the paper. State what is left: a general question that economists already care about, or only a description of that one setting.

2. **Is the main contribution a new fact in one setting, or an explanation that can travel across settings?** State which it is. If the paper offers an explanation, say whether the paper tests it or only proposes it.

3. **Can a reader outside the immediate subfield repeat the paper's central claim in one sentence?** Write that sentence yourself, using only the abstract and introduction. If you cannot write it without subfield jargon or without listing several separate findings, say so.

4. **Do later sections escalate one argument, or do they mostly add outcomes and robustness checks?** Walk through the results sections in order. State whether each section raises the stakes of the previous one, or whether the sections sit side by side with no single idea connecting them.

5. **Does the evidence change a canonical calculation, resolve a contradiction, or reorganize an established literature?** Name the calculation, contradiction, or literature if there is one. If the paper only documents a consequence without connecting it to something a large literature treats as central, say so.

6. **What is the boldest interpretation the evidence can responsibly support, and what additional test would make that interpretation credible?** State the interpretation in one sentence. It must not exceed what the paper's research design can support. Then compare it with what the paper currently claims: the paper may be claiming less than it could, or more than it should. Describe the one additional test precisely enough that the authors could run it.

**Part 3 — Rating and the Single Most Valuable Change**

- Rate the contribution: [Transformative | Significant | Incremental | Insufficient for target journal]. Justify in 2–3 sentences that refer to the answers above.
- State the single change that would most strengthen the contribution. It will usually come from Question 4 or Question 6. Make it concrete: which reframing, which restructuring, or which analysis.

Keep the whole output under 500 words.

**Output format:**

```
## Agent 7: Contribution Assessment

### The Claimed Contribution
[one sentence]

### The Six Questions
1. **Does the question survive without the setting?** [Strong | Adequate | Weak] — [2–3 sentences with evidence]
2. **New fact or portable explanation?** [Strong | Adequate | Weak] — [2–3 sentences with evidence]
3. **One-sentence claim for an outsider?** [Strong | Adequate | Weak] — "[the sentence]" [1–2 sentences]
4. **Escalating argument or added outcomes?** [Strong | Adequate | Weak] — [2–3 sentences with evidence]
5. **Changes a calculation, contradiction, or literature?** [Strong | Adequate | Weak] — [2–3 sentences with evidence]
6. **Boldest responsible interpretation and the test that supports it** — [interpretation | how it compares with the current claim | the additional test]

### Rating
[rating + 2–3 sentence justification]

### Single Most Valuable Change
[one concrete change]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

## Phase 3: Verify the Findings

The review agents produce more findings than the authors should act on. Some findings are wrong, some are marginal, and some repeat each other. Before writing the report, run one verification agent that removes them.

**Check for agent failures first**: if any of Agents 1–7 returned no output or clearly malformed output, note it. That agent contributes no findings, and its section in the report becomes a placeholder (see Phase 4).

**Prepare the findings list**: collect every finding tagged `[CRITICAL]` or `[MAJOR]` from Agents 1–6 and give each a unique ID made of the agent number and a running number (for example `A3-2` for the second finding from Agent 3). Copy each finding in full, including its location and quoted text. Do not include `[MINOR]` findings, the untagged prose in Agent 6 Parts 1, 3, 4, and 5, or anything from Agent 7. Those are not verified.

Launch one agent with `subagent_type: "general-purpose"`. Prepend the scope guard from Phase 2 and the line "The target journal is [resolved value of TARGET_JOURNAL]." Then give it the prompt below, followed by the findings list and the same .tex, figure, and table file lists the review agents received.

---

### VERIFICATION AGENT

You are a senior editor checking a draft referee report before it is sent to the authors. The draft contains findings from six reviewers. Your job is to remove findings that are wrong or that do not matter, so that the authors spend their time on the issues that do. You do not add new findings.

Read all .tex files and the table files. Then judge each finding in the list with these three tests, in order.

**Test 1 — Is the finding correct?** Check it against the paper.
- If the finding quotes text, confirm that the quoted text appears in the live text of the paper and that the finding reads it correctly in context.
- If the finding claims a mismatch between two places (text and table, abstract and results, equation and description), open both places and confirm the mismatch.
- If the finding says something is missing (a caveat, a definition, a table note, a robustness check), search the paper, including the appendix, and confirm that it is missing.
- If you cannot confirm the finding, the verdict is `DROP`.

**Test 2 — Does the finding matter?** A finding matters if at least one of these holds:
- A referee at `TARGET_JOURNAL` would raise it in a report.
- Fixing it would change a reader's confidence in the main results.
- It would mislead or confuse a careful reader about what the paper does or finds.

If none holds, the verdict is `DROP`. If the finding is correct and matters but its severity tag overstates it, the verdict is `DOWNGRADE` (`[CRITICAL]` to `[MAJOR]`, or `[MAJOR]` to `[MINOR]`). Reserve `[CRITICAL]` for problems that could cause a desk rejection or that a referee would list as a main concern.

**Test 3 — Is the finding a duplicate?** If two findings describe the same underlying problem, keep the more specific one and give the other the verdict `MERGE` with the ID of the finding it merges into.

Rules:
- Do not keep a finding because it is harmless to include. The default for a finding you cannot confirm or cannot defend as material is `DROP`.
- Do not drop a finding because the fix is costly or because the authors will dislike it. Required analyses from Agent 6 are dropped only if the paper already contains the analysis or if the concern it addresses does not apply to this paper's design.
- Judge every finding. Do not skip any ID.

**Output format:**

```
## Verification

| ID | Verdict | Final severity | Merged into | Reason (15 words or fewer) |
|----|---------|----------------|-------------|----------------------------|
| A1-1 | KEEP / DOWNGRADE / DROP / MERGE | CRITICAL / MAJOR / MINOR / — | ID or — | ... |
```

The findings to verify are: [FINDINGS LIST WITH IDS]
The .tex files are: [LIST ALL TEX FILE PATHS HERE]
Figure files: [LIST FIGURE PATHS]
Table files: [LIST TABLE PATHS]

---

**Apply the verdicts** before writing the report:
- `KEEP`: the finding stays as written.
- `DOWNGRADE`: change the finding's tag to the final severity and move it to the matching subsection of its agent's output if that output is organized by severity.
- `DROP`: delete the finding. It does not appear anywhere in the report, and the report does not mention that findings were removed.
- `MERGE`: delete the finding and keep the one it merges into.

Record the number of findings dropped and merged for the user-facing summary.

**If the verification agent fails** (no output, malformed output, or IDs missing from the table), keep all unverified findings as tagged and add this line under the report header: "**Note**: findings in this report were not verified."

## Phase 4: Consolidate and Save

Consolidate the verified findings into a single structured report. The report must not print any finding twice: the Priority Action Items list gives one line per `[CRITICAL]` and `[MAJOR]` finding, and the full finding appears once in its agent's section.

**Save location**: save the report inside a `reviews/` subfolder of the paper's directory (create it if it does not exist). Keeping reports out of the paper's root directory prevents them from being picked up by future runs of this skill.

**Before saving**, check whether `reviews/PRE_SUBMISSION_REVIEW_[YYYY-MM-DD].md` already exists. If it does, append `-v2` (or `-v3`, etc.) to avoid overwriting.

Save the report to:

`reviews/PRE_SUBMISSION_REVIEW_[YYYY-MM-DD].md`

where `[YYYY-MM-DD]` is today's date.

**Report structure:**

```markdown
# Pre-Submission Referee Report

**Paper**: [Title]
**Authors**: [Authors]
**Date**: [Today's date]
**Review Standard**: [TARGET_JOURNAL — if top-field, write "Leading Field Journal"; otherwise write the specific journal name]

---

## Overall Assessment

[3–4 sentences synthesized as follows: (1) what the paper does — from Agent 7 "The Claimed Contribution"; (2) where the contribution stands — from Agent 7's rating and its weakest answers among the six questions; (3) the single most critical issue — the top CRITICAL item from the Priority Action Items list below. Do not introduce judgments not already present in the agent outputs.]

**Contribution Rating**: [Copy the rating from Agent 7]

**Preliminary Recommendation**: [Copy exactly from Agent 6 Part 4 — do not paraphrase. If Agent 7 rates the contribution "Insufficient for target journal", append: "Note: the contribution is rated below the target journal's bar, which makes desk rejection likely regardless of execution."]

---

## Priority Action Items

[One line per finding: a short statement of the problem and the section of this report where the full finding appears. List only CRITICAL and MAJOR findings that survived verification. MINOR findings appear only in the sections below.

Order: `[CRITICAL]` items from Agent 3 and Agent 6 Part 1 first, then `[CRITICAL]` from Agent 6 Part 2, then remaining `[CRITICAL]` items by agent order, then all `[MAJOR]` items in the same agent order.

If Agent 7's rating is Incremental or Insufficient, insert one additional item at the very top of the CRITICAL list stating the contribution gap and Agent 7's Single Most Valuable Change. If the rating is Transformative or Significant, add the Single Most Valuable Change as the first MAJOR item.]

**CRITICAL** (must fix — these could cause desk rejection or major referee objections):
1. ...
2. ...

**MAJOR** (should fix — will likely be raised by referees):
3. ...
4. ...

---

## 1. Central Contribution

[Agent 7 output]

Novelty relative to the prior literature has not been assessed in this review.

---

## 2. Referee Assessment (Identification, Analyses, Positioning & Fit)

[Agent 6 output, after applying the verification verdicts]

---

## 3. Unsupported Claims & Identification Integrity

[Agent 3 output, after applying the verification verdicts]

---

## 4. Internal Consistency & Cross-Reference Verification

[Agent 2 output, after applying the verification verdicts]

---

## 5. Mathematics, Equations & Notation

[Agent 4 output, after applying the verification verdicts]

---

## 6. Tables, Figures & Documentation

[Agent 5 output, after applying the verification verdicts]

---

## 7. Spelling, Grammar & Style

[Agent 1 output, after applying the verification verdicts]
```

Rules for the agent sections:
- Preserve each agent's structure, but delete any subsection that has no findings left. If a whole section has no findings left, write "No issues that warrant action."
- If an agent failed, write a placeholder in its section (e.g., "Agent did not return output") and mention it in the user-facing summary.

After saving, report to the user:
1. The path to the saved report
2. The preliminary recommendation from Agent 6 and the contribution rating from Agent 7
3. The top 5 priority action items
4. How many findings remain in each severity category, and how many were removed in verification
5. If any table or figure files on disk were excluded as unreferenced in Phase 1, their count and a one-line note that they were not reviewed
