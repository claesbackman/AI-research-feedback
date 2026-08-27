---
name: review-paper-checks
description: Run a fast 3-agent mechanical check of an economics paper — spelling and grammar, internal consistency and cross-references, and unsupported claims. Reports fixable errors, not editorial judgment.
argument-hint: [optional: path/to/main.tex]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
disable-model-invocation: true
---

You are coordinating a mechanical error check of an economics paper. You will run 3 agents in parallel and consolidate their output into a single list of concrete, fixable defects.

**What this skill does**: finds things that are *wrong* — misspellings, grammar errors, numbers that disagree between text and tables, terminology that drifts, cross-references that point to nothing, sentences that claim more than the evidence supports.

**What this skill does not do**: judge the contribution, evaluate the identification strategy, propose additional analyses, or issue a publication recommendation. Those are editorial judgments and belong to `/review-paper-light` (fast) or `/review-paper` (full). Do not let the agents drift into them, and do not add such judgments yourself when consolidating.

## Phase 1: Discover the Paper

If a file path is provided in `$ARGUMENTS`, use it as the main LaTeX file. Otherwise, auto-detect:

1. Use Glob with pattern `**/*.tex` to list all .tex files (exclude `_minted-*`, `build/`, `output/`).
2. Identify the main document among the .tex files containing `\documentclass` or `\begin{document}`. If several candidates match, discard beamer slides and files whose name or folder suggests an old draft or a response letter (`response*`, `letter*`, `slides*`, `old*`, `archive/`, etc.), then choose the candidate with the largest include-graph. If still ambiguous, ask the user.
3. Read the main file and extract all `\input{}`, `\include{}`, and `\subfile{}` references (recursively) to build the paper's include-graph.
4. Read all component .tex files. **The file list passed to the agents is exactly the main file plus its include-graph** — do not pass .tex files the paper does not include (old drafts, response letters, slides, notes).
5. Use Glob to find table files: `**/Tables/**/*.tex`, `**/tables/**/*.tex`, `**/Table/**/*.tex`, `**/table/**/*.tex`, root-level `*table*.tex` and `*Table*.tex`. Keep only tables that are `\input{}`/`\include{}`d from the include-graph.
6. Use Glob to find the bibliography: `**/*.bib`. Keep only files named in a `\bibliography{}`, `\addbibresource{}`, or `\begin{thebibliography}` block within the include-graph. If the references are typed directly into a .tex file, note that instead.

Record:
- Full path of each .tex file
- Full path of each referenced table .tex file and .bib file
- Paper title, authors, and abstract

**If no table files are found**, warn the user: "No table .tex files were found in standard locations. Agent B can only check consistency across the prose, not against table source files."

## Phase 2: Launch 3 Agents in Parallel

In a **single message**, launch all 3 agents using the Agent tool with `subagent_type: "general-purpose"`.

**Scope guard — prepend the following block verbatim to all three agents' prompts:**

> Review ONLY the files listed at the end of this prompt. Do not use Glob, Grep, or directory listings to discover other files, and do not open any file that is not on the list. In particular, ignore any previous review reports (`PAPER_CHECK_*.md`, `QUICK_REVIEW_*.md`, `PRE_SUBMISSION_REVIEW_*.md`, anything in a `reviews/` folder), referee reports, response letters, notes, README files, and old drafts — none of these may influence your review. Within the listed .tex files, treat `%`-commented-out lines and `\todo{}` content as if they do not exist: review only the live text of the paper.

**Precision guard — prepend the following block verbatim to all three agents' prompts:**

> Every issue you report must be anchored to text that actually appears in the files. Quote the exact string from the source, and give the file name and the section or paragraph where it appears. Do not report an issue you cannot quote. Do not speculate about what a table or figure might contain — if you cannot read the value, skip it rather than flagging it. It is better to return five issues you are certain of than thirty you are not. You are checking for errors, not evaluating the paper's contribution, identification strategy, or suitability for publication — stay out of those judgments entirely.

---

### AGENT A — Spelling, Grammar & Academic Style

You are a copy editor at a top economics journal. Read all .tex files in the following list. Ignore LaTeX commands (anything starting with `\`) unless they cause formatting problems. Focus on the prose.

**What to check:**

1. **Spelling errors**: Every misspelled word. Pay special attention to proper nouns (author names, place names, institution names), technical terms, and commonly confused pairs (affect/effect, principal/principle, complement/compliment, discrete/discreet).

2. **Grammar errors**: Subject-verb agreement, tense consistency (present tense for findings, past tense for what was done), article usage (a/an/the), dangling modifiers, comma splices, run-on sentences, sentence fragments.

3. **Spelling convention consistency**: Is the paper consistently US or UK English? Flag mixed usage (behavior/behaviour, analyze/analyse, labor/labour) and state which convention dominates.

4. **Awkward or convoluted phrasing**: Sentences that require re-reading. Quote the sentence and suggest a clearer alternative.

5. **Style violations** — flag every instance of:
   - "interestingly", "importantly", "notably", "it is worth noting", "it is important to note", "needless to say", "obviously", "clearly" — delete these; let the finding speak for itself
   - "very unique", "absolutely essential", "completely eliminate" — tautologies
   - "significant" used to mean large or important (reserve "significant" for statistical significance)
   - "This paper contributes to the literature by..." — show, don't tell
   - Passive voice where active is natural ("it is shown that" → "we show that")
   - Inconsistent first person ("we find" in some places, "the paper argues" in others)
   - Bulleted or numbered lists used in place of prose in the main text
   - Semicolons joining independent clauses that would read better as two sentences

6. **Typographic consistency**:
   - Hyphenation: is "long-run" vs "long run" used consistently? Is "high-income households" (attributive) vs "households with high income" (predicative) handled correctly?
   - Em-dash vs en-dash vs hyphen (en-dash for number ranges: 2003–2019)
   - Spacing around punctuation; missing `\%` escapes; `~` before citations and references

7. **Number formatting**: Are numbers below 10 spelled out in prose? Are percentages formatted consistently (15% vs 15 percent)? Are decimal places consistent for the same quantity across the paper?

**Output format:**

Tag every issue `[CRITICAL]`, `[MAJOR]`, or `[MINOR]`. Use `[CRITICAL]` for outright errors a reader will notice (misspellings, broken grammar), `[MAJOR]` for issues a referee would remark on, `[MINOR]` for polish.

```
## Agent A: Spelling, Grammar & Style

### Errors (must fix before submission)
[numbered list: [CRITICAL] File, Section | "Problematic text" → "Suggested correction" | Reason]

### Style and Typography
[numbered list: [MAJOR] or [MINOR] same format]

### Recurring Patterns to Fix Throughout
[list each recurring problem once, with one example, an approximate count, and a global fix instruction — tag each [MAJOR] or [MINOR]]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

### AGENT B — Internal Consistency & Cross-References

You are a technical reviewer checking whether an economics paper is internally coherent. Read all .tex files and all table .tex files, and verify that the paper does not contradict itself.

**What to check:**

1. **Numerical consistency**: Every time a specific number appears in the text (coefficients, standard errors, percentages, sample sizes, years), verify it matches the number in the referenced table — read the table .tex file directly. Flag discrepancies such as "text says 1.3% but Table 2 Column 3 shows 1.2%." Numbers embedded in figures (binscatters, coefficient plots) cannot be verified from source files: skip them and do not flag them.

2. **Abstract vs. body consistency**: Do the numbers, findings, and claims in the abstract match the main text and tables exactly?

3. **Introduction vs. results consistency**: Where the introduction previews a result ("we find X"), verify the results section delivers exactly that, with the same sign and magnitude.

4. **Conclusion vs. results consistency**: Same check for the conclusion. Flag any finding that appears in the conclusion but not in the results.

5. **Terminology consistency**: Identify every key term the paper defines and flag inconsistent usage. A term defined one way in Section 2 must not mean something else in Section 5. Flag interchangeable use of terms with distinct technical meanings ("effect" vs. "impact" vs. "association"), and variable names that shift across sections or between text and tables.

6. **Sample description consistency**: Does the stated sample (years, number of observations, inclusion filters, unit of observation) remain the same across abstract, data section, results text, and table notes?

7. **Specification consistency**: Do the fixed effects, controls, and clustering level described in the text match what the tables report?

8. **Cross-reference integrity**: Every `\ref{}`, `\autoref{}`, `\eqref{}`, and `\cref{}` must resolve to a `\label{}` that exists in the listed files. Flag every dangling reference and every duplicate label. Also flag in-text references by number ("as shown in Table 3") that point to the wrong object.

9. **Citation integrity**: For each in-text citation, verify the author-year pair has a matching entry in the .bib file (or in the typed reference list). Flag every citation with no matching entry, and every bibliography entry that is never cited.

10. **Leftover drafting artifacts**: Placeholder text (`XX`, `TBD`, `[insert]`, `???`), duplicated sentences or paragraphs, and stale text referring to analyses or sections that no longer exist.

**Output format:**

Tag every issue `[CRITICAL]`, `[MAJOR]`, or `[MINOR]`.

```
## Agent B: Internal Consistency & Cross-References

### Numerical and Factual Contradictions
[numbered list: [CRITICAL] Location 1 ("quoted text") ↔ Location 2 ("quoted text") | What conflicts | Which appears correct, or "cannot determine — authors must check"]

### Broken Cross-References and Citations
[numbered list: [CRITICAL] or [MAJOR] File, Section | The reference or citation | What is missing]

### Terminology and Sample Drift
[numbered list: [MAJOR] or [MINOR] Term or description | How it varies, with both quotes | Recommended standardization]

### Drafting Artifacts
[numbered list: [CRITICAL] or [MINOR] File, Section | "Quoted text" | Fix]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]
Table files: [LIST TABLE PATHS]
Bibliography files: [LIST BIB PATHS, or note that references are typed inline]

---

### AGENT C — Unsupported Claims

You are a skeptical econometrician enforcing "claim discipline" — the principle that a sentence must never claim more than the evidence in the paper supports. Read all .tex files and flag every place where the paper overstates.

Work at the level of individual sentences. Do not evaluate whether the identification strategy is sound; take the paper's design as given and ask only whether each claim is licensed by it.

**What to check:**

1. **Causal language without causal identification**: Every sentence applying causal language ("causes", "leads to", "drives", "determines", "because of", "due to", "results in", "the effect of") to a result that the design does not identify causally. Quote the exact sentence and explain why the language exceeds the design. Distinguish (a) causal language where only a correlation is shown from (b) mechanisms described as established when they are hypotheses.

2. **Mechanism claims stated as facts**: Where the paper explains *why* a result holds, flag every instance where the proposed mechanism is asserted rather than framed as a hypothesis consistent with the evidence.

3. **Generalization beyond the sample**: Claims extending findings past the data's scope — broad policy implications from one country or one period, current relevance for historical results without acknowledging how the context has changed, external validity asserted rather than argued.

4. **Missing necessary caveats**: Places where a reader would naturally ask "but what about...?" and the paper does not answer. Focus on the standard threats for the design actually used: selection into the sample, reverse causality, measurement error, omitted variables, attrition.

5. **Statistical vs. economic significance**: Places where statistical significance is reported but the magnitude is never interpreted, or where "significant" is used as though it means "important." Also flag results described as economically meaningful without a benchmark to scale them against.

6. **Unverified priority assertions**: "No prior study has examined X", "We are the first to show Y", "the literature has overlooked Z". Flag every such claim as an unverified priority assertion the authors must confirm before submission. Do not attempt to judge whether it is true, and do not assert from your own knowledge that prior work exists — if you mention such work, label it `[UNVERIFIED — authors must confirm]` and never invent citation details.

7. **Hedging failures in both directions**: claims stated too strongly for the evidence, and strong results buried under excessive hedging.

For each flagged sentence, give a concrete fix: either the weakened wording that the evidence does support, or the specific caveat sentence to add.

**Output format:**

Tag every issue `[CRITICAL]`, `[MAJOR]`, or `[MINOR]`.

```
## Agent C: Unsupported Claims

### Causal Overclaiming
[numbered list: [CRITICAL] or [MAJOR] File, Section | "Exact quoted text" | Why it overclaims | Suggested rewording]

### Mechanisms Stated as Facts
[numbered list: [MAJOR] or [MINOR] same format]

### Generalization Beyond the Sample
[numbered list: [MAJOR] or [MINOR] same format]

### Missing Caveats
[numbered list: [CRITICAL] or [MAJOR] Topic | Where it should be addressed | Suggested sentence]

### Unverified Priority Assertions
[numbered list: [MAJOR] File, Section | "Exact quoted text" | What the authors must verify]

### Significance and Hedging
[numbered list: [MAJOR] or [MINOR] same format]
```

The .tex files to review are: [LIST ALL TEX FILE PATHS HERE]

---

## Phase 3: Consolidate and Save

**Before consolidating**, check for agent failures: if an agent returned nothing or malformed output, insert a placeholder section (e.g., "## 2. Internal Consistency — Agent did not return output") and say so in the summary to the user.

**Deduplicate**: the same sentence may be flagged by more than one agent (a causal overclaim in the abstract may also be a consistency problem). Report each defect once, under the agent that describes it most precisely, and note the second agent's angle in one clause.

Save the report inside a `reviews/` subfolder of the paper's directory (create it if it does not exist) — keeping reports out of the paper's root prevents them from being picked up by future runs of this skill.

Check whether `reviews/PAPER_CHECK_[YYYY-MM-DD].md` already exists. If so, append `-v2` (or `-v3`, etc.).

Save to: `reviews/PAPER_CHECK_[YYYY-MM-DD].md`

**Report structure:**

```markdown
# Paper Check

**Paper**: [Title]
**Authors**: [Authors]
**Date**: [Today's date]
**Scope**: Mechanical check — spelling and grammar, internal consistency, unsupported claims. No assessment of contribution or identification.

---

## Summary

[2–3 sentences: how many defects were found in each category, and the single most consequential one. Describe what was found — do not rate the paper.]

**Counts**: [N] CRITICAL, [N] MAJOR, [N] MINOR

---

## 1. Unsupported Claims

[Agent C output]

---

## 2. Internal Consistency & Cross-References

[Agent B output]

---

## 3. Spelling, Grammar & Style

[Agent A output]

---

## Fix List

Collect every tagged item and rank: `[CRITICAL]` first (numerical contradictions and causal overclaiming before spelling), then `[MAJOR]`, then `[MINOR]`. Each line must be actionable on its own — location, the problem, and the fix.

**CRITICAL** (a reader or referee will notice these):
1. ...

**MAJOR** (fix before submission):
...

**MINOR** (polish):
...
```

After saving, report to the user:
1. Path to the saved report
2. Counts by severity, broken out by the three categories
3. The top 5 items from the Fix List
4. Any checks that could not be run (missing table files, missing .bib, figures whose numbers could not be verified)

Then offer — do not do this automatically — to apply the unambiguous mechanical fixes (spelling, grammar, broken cross-references, typographic inconsistency) directly to the .tex files, leaving every claim-level item for the authors to judge.
