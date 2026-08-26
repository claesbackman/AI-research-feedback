---
name: paper-version
description: Convert a LaTeX research paper into a policy brief, 1-page summary, or 5-page summary for a general audience, with factual review and a standalone HTML page for GitHub Pages.
user-invocable: true
argument-hint: [brief|1page|5page]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
disable-model-invocation: true
---

# Paper Versions

Convert a LaTeX research paper project into an accessible audience-facing version, review it for accuracy, and produce a standalone HTML page.

## Input

- `$ARGUMENTS[0]` — Output format: `brief`, `1page`, or `5page` (required)

## Format definitions

- **`brief`** — A structured 2-page policy brief with fixed sections: *The Question*, *What We Do*, *Key Findings*, *Policy Implications*, *Caveats*. Formal but accessible. No jargon.
- **`1page`** — One flowing page of prose for a general audience. No section headers. Written like a short article. Leads with the main finding.
- **`5page`** — A five-page narrative summary with light structure (Background, What We Did, What We Found, Why It Matters, Limitations). Accessible to an educated non-specialist.

## Instructions

### Step 0 — Validate input

If `$ARGUMENTS[0]` is not one of `brief`, `1page`, `5page`, stop and tell the user: "Please specify a format: `brief`, `1page`, or `5page`."

Set `FORMAT` = the argument value.

---

### Step 1 — Reader Agent

Launch an Agent (subagent_type: general-purpose) with this task:

> You are reading a LaTeX research paper project. Your job is to extract the full content of the paper into a clean, structured plain-text representation that will be used by a writer agent.
>
> **Instructions:**
> 1. Find the main `.tex` file in the current directory. It is usually the file that contains `\documentclass` or `\begin{document}`. Use Glob to search for `**/*.tex` files, then identify the root file.
> 2. Read the root `.tex` file. Wherever you find `\input{...}` or `\include{...}` commands, read those files too, recursively, until you have assembled the full paper text.
> 3. Strip LaTeX markup: remove commands like `\textbf{}`, `\emph{}`, `\cite{}`, `\label{}`, `\ref{}`, `\footnote{}`, equation environments, figure environments, table environments. Keep the text content. For tables, summarize the key numbers in prose form. For figures, note what the figure shows based on the caption.
> 4. Extract and clearly label these components:
>    - **Title**
>    - **Authors**
>    - **Abstract** (verbatim)
>    - **Introduction** (full text)
>    - **Data/Empirical Setting** (if present)
>    - **Methods/Approach** (condensed)
>    - **Main Results** — list every key quantitative finding, with exact numbers, units, and confidence intervals as stated in the paper. Be exhaustive here.
>    - **Robustness/Heterogeneity** (condensed)
>    - **Conclusion**
>    - **Key claims made by the authors** — list every causal or interpretive claim the authors make explicitly, noting the exact language they use (e.g., "we find that X causes Y" vs. "X is associated with Y")
> 5. Extract figure information: scan the full `.tex` source for `\includegraphics` commands. For each one, record:
>    - The filename as specified (e.g., `figures/fig1` or `fig_results`)
>    - The caption text from the nearest `\caption{}` command
>    - Which section of the paper the figure appears in
>    List these under a **Figures** section in your output, formatted as:
>    `FIGURE: [filename] | CAPTION: [caption text] | SECTION: [section name]`
> 6. Identify the 1-2 figures that best illustrate the paper's main finding and mark them with `[KEY FIGURE]`.
> 7. Return the full extraction as structured markdown. Do not summarize or interpret — just extract.

Save the Reader Agent's output to `output/paper_extraction.md`. Create the `output/` directory if it does not exist.

After the Reader Agent finishes, scan the project directory for image files that match the extracted figure filenames. Use Glob to search for `**/*.png`, `**/*.jpg`, and `**/*.jpeg`. For each figure listed as `[KEY FIGURE]` in `paper_extraction.md`, check whether a matching PNG or JPG file exists (try the filename with and without extension, and with common path prefixes like `figures/`, `Figures/`, `fig/`). Build a list of embeddable figures — those where a `.png` or `.jpg` file was found — and save it to `output/figures_list.md` in this format:

```
EMBEDDABLE: [relative path from project root] | CAPTION: [caption text]
NOT FOUND (PDF or missing): [filename] | CAPTION: [caption text]
```

If no PNG/JPG figures are found at all, note that in `output/figures_list.md` and continue — the HTML will be text-only.

---

### Step 2 — Writer Agent

Launch an Agent (subagent_type: general-purpose) with this task, passing it the content of `output/paper_extraction.md` and the value of FORMAT:

> You are a science writer creating an accessible version of an economics research paper for a general audience.
>
> **Paper content:** [paste full content of output/paper_extraction.md]
>
> **Output format requested:** [FORMAT]
>
> **Format instructions:**
>
> For `brief` — Write a structured policy brief. Use exactly these section headers:
> - **The Question** — What problem does this paper address? (2-3 sentences)
> - **What We Do** — How do the authors study it? Data, setting, method in plain language. (3-4 sentences)
> - **Key Findings** — The main quantitative results. Report actual numbers. (4-6 bullet points, each 1-2 sentences)
> - **Policy Implications** — What do these findings suggest for policy? Be concrete. (3-5 sentences)
> - **Caveats** — Limitations the authors themselves acknowledge. (2-3 sentences)
> Total length: approximately 500-600 words.
>
> For `1page` — Write one page of flowing prose. No section headers. Open with the main finding stated plainly. Use accessible analogies where helpful. Do not use academic hedging or jargon. End with why it matters. Total length: approximately 350-400 words.
>
> For `5page` — Write a 5-page narrative summary with these light headers:
> - **Background** — Context and motivation
> - **What We Did** — Data, setting, approach
> - **What We Found** — Results in detail, with numbers
> - **Why It Matters** — Implications
> - **Limitations** — What the paper cannot establish
> Total length: approximately 1400-1600 words.
>
> **General writing rules (all formats):**
> - Write for an intelligent adult with no economics background
> - Report key numbers — do not vague them out
> - Do not overclaim causality beyond what the paper itself claims — match the paper's own language precisely
> - No passive voice where avoidable
> - No bullet points except where explicitly called for above
> - No jargon without explanation
>
> **Key findings callout:** Identify the single most important quantitative finding — the one number or result a reader should walk away remembering. Write it as a short punchy sentence (max 25 words). Mark it clearly in your output with the tag `[CALLOUT]: ` at the start of the line, e.g.:
> `[CALLOUT]: Homeowners in the top wealth decile hold 40% of all housing wealth, despite representing only 10% of households.`
> This will be displayed as a highlighted box on the webpage.
>
> Return only the finished draft (including the [CALLOUT] line), with no preamble or meta-commentary.

Save the Writer Agent's output to `output/[FORMAT]_draft.md` (e.g., `output/brief_draft.md`).

---

### Step 3 — Reviewer Agent

Launch an Agent (subagent_type: general-purpose) with this task:

> You are a fact-checker and editorial reviewer. You will compare a summary/brief of an economics paper against the original paper's extracted content, and produce a structured review report.
>
> **Original paper extraction:** [paste full content of output/paper_extraction.md]
>
> **Draft to review:** [paste full content of output/[FORMAT]_draft.md]
>
> **Your job — check for three categories of issues:**
>
> **1. Factual accuracy**
> Go through every quantitative claim, statistic, or finding stated in the draft. For each one, verify it against the original extraction. Flag anything that:
> - Uses a wrong number
> - Changes units or direction of an effect
> - Attributes a finding to the wrong group or condition
> - Omits a critical qualifier (e.g., "only for renters" or "only in the short run")
>
> **2. Overclaiming**
> Compare every causal or interpretive claim in the draft against the exact language in the original paper. Flag anywhere the draft uses stronger language than the paper (e.g., draft says "causes" when paper says "is associated with"; draft says "proves" when paper says "suggests").
>
> **3. Framing consistency**
> Flag anywhere the draft:
> - Shifts the emphasis of the findings away from what the paper presents as primary
> - Buries or omits a key finding the paper treats as central
> - Introduces an implication the paper does not make
>
> **Output format:**
> Produce a numbered list of issues found. For each issue, state:
> - **Category** (Factual / Overclaiming / Framing)
> - **Location in draft** (quote the relevant phrase)
> - **The problem** (what is wrong or overstated)
> - **Suggested fix** (what it should say instead, with reference to the source)
>
> If no issues are found in a category, say so explicitly. End with an overall verdict: PASS (ready to use with minor edits), REVISE (needs targeted fixes before use), or MAJOR REVISION (significant accuracy or framing problems).

Save the Reviewer Agent's output to `output/[FORMAT]_review.md`.

---

### Step 4 — Pause and present review

After the Reviewer Agent finishes:

1. Read `output/[FORMAT]_review.md` and display its full contents to the user.
2. Tell the user: "The draft is saved at `output/[FORMAT]_draft.md`. Edit it as needed before proceeding. When you are ready to generate the HTML, reply **proceed**. To cancel, reply **cancel**."
3. Wait for the user's response.
   - If the user says **cancel** or anything indicating they want to stop, end the skill.
   - If the user says **proceed** or any clear affirmation, continue to Step 5.

---

### Step 5 — Website Agent

Read the current contents of `output/[FORMAT]_draft.md` (which may now be edited by the user).

Launch an Agent (subagent_type: general-purpose) with this task:

> You are building a clean standalone HTML page for an economics research paper summary. This page should have no JavaScript dependencies, use a single `<style>` block in `<head>`, and be ready to deploy on GitHub Pages.
>
> **Paper title:** [extracted title from paper_extraction.md]
> **Authors:** [extracted authors from paper_extraction.md]
> **Abstract:** [extracted abstract from paper_extraction.md]
> **Format type:** [FORMAT] (brief / 1page / 5page)
> **Content:** [paste full content of output/[FORMAT]_draft.md — strip the [CALLOUT]: line from the body text, it will be rendered separately as a callout box]
> **Callout text:** [the sentence that was tagged [CALLOUT]: in the draft]
> **Embeddable figures:** [paste content of output/figures_list.md — use only lines marked EMBEDDABLE]
>
> **Build the HTML page with these requirements:**
>
> **`<head>` — Open Graph and meta tags:**
> Include these meta tags so the page looks good when shared on social media:
> ```html
> <meta charset="UTF-8">
> <meta name="viewport" content="width=device-width, initial-scale=1.0">
> <meta name="description" content="[first 150 characters of the abstract]">
> <meta property="og:title" content="[paper title]">
> <meta property="og:description" content="[first 150 characters of the abstract]">
> <meta property="og:type" content="article">
> <meta property="og:article:author" content="[authors]">
> <meta name="twitter:card" content="summary">
> <meta name="twitter:title" content="[paper title]">
> <meta name="twitter:description" content="[first 150 characters of the abstract]">
> ```
>
> **Layout and structure:**
> - Single-column, centered, max-width 740px
> - Header area: paper title, authors, format badge, today's date
> - Immediately below the header: the **callout box** (see styling below)
> - Then the body content
> - If format is `brief`, render the section headers as `<h2>` elements
> - If format is `1page` or `5page`, use `<h2>` only for the light section headers if present
> - After the body text: any embeddable figures (see figure section below)
> - Footer: "This is a [format label]. The full paper is available <a href="#">here</a>."
>
> **Callout box:**
> Render the callout sentence as a visually distinct block immediately after the header and before the body text:
> ```html
> <div class="callout">
>   <span class="callout-label">Key Finding</span>
>   <p>[callout text]</p>
> </div>
> ```
> Style it as: background #f0ebe2, left border 4px solid #8b7355, padding 1rem 1.25rem, margin 2rem 0. The label: display block, font-size 0.75rem, font-weight 700, text-transform uppercase, letter-spacing 0.08em, color #8b7355, margin-bottom 0.4rem. The paragraph: margin 0, font-size 1.05rem, font-style italic, color #1a1a1a.
>
> **Figures:**
> For each embeddable figure provided, add an `<figure>` block after the main body text and before the footer:
> ```html
> <figure>
>   <img src="[relative path from output/ — prepend ../ to the project-root-relative path]" alt="[caption text]" style="max-width:100%;height:auto;display:block;margin:0 auto;">
>   <figcaption>[caption text]</figcaption>
> </figure>
> ```
> If the figures list says "NOT FOUND" for all figures, omit the figures section entirely.
> Add a `<h2>Figures</h2>` header above the figure block only if at least one figure is embeddable.
> Figure caption style: font-size 0.85rem, color #555, text-align center, margin-top 0.5rem, font-style italic.
>
> **Full CSS (in `<style>` block in `<head>`):**
> ```css
> *, *::before, *::after { box-sizing: border-box; }
> body { font-family: system-ui, -apple-system, Georgia, serif; background: #fafaf8; color: #1a1a1a; font-size: 18px; line-height: 1.7; margin: 0; padding: 2rem 1rem; }
> .container { max-width: 740px; margin: 0 auto; }
> .header { margin-bottom: 2rem; }
> .title { font-size: 2rem; font-weight: 700; line-height: 1.25; margin: 0 0 0.4rem 0; }
> .authors { font-size: 1rem; color: #555; margin: 0 0 0.6rem 0; }
> .meta { display: flex; align-items: center; gap: 0.75rem; font-size: 0.85rem; color: #888; }
> .badge { background: #e8e4dd; color: #555; font-size: 0.8rem; padding: 3px 10px; border-radius: 20px; font-weight: 500; }
> .callout { background: #f0ebe2; border-left: 4px solid #8b7355; padding: 1rem 1.25rem; margin: 2rem 0; }
> .callout-label { display: block; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #8b7355; margin-bottom: 0.4rem; }
> .callout p { margin: 0; font-size: 1.05rem; font-style: italic; }
> h2 { font-size: 1.15rem; font-weight: 600; color: #1a1a1a; margin-top: 2rem; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
> p { margin: 0 0 1rem 0; }
> ul { margin: 0 0 1rem 0; padding-left: 1.2rem; }
> li { margin-bottom: 0.5rem; }
> figure { margin: 1.5rem 0; }
> figcaption { font-size: 0.85rem; color: #555; text-align: center; margin-top: 0.5rem; font-style: italic; }
> .footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; font-size: 0.85rem; color: #888; }
> .footer a { color: #555; }
> @media (max-width: 600px) { body { font-size: 16px; padding: 1rem 0.75rem; } .title { font-size: 1.5rem; } }
> ```
>
> Return only the complete HTML file contents, nothing else.

Save the Website Agent's output to `output/index.html`.

Tell the user: "Done. Files produced:
- `output/[FORMAT]_draft.md` — your draft
- `output/[FORMAT]_review.md` — reviewer notes
- `output/index.html` — standalone HTML page

To publish on GitHub Pages: commit the `output/` folder and enable Pages in your repo settings, or copy `index.html` to a Pages repo."
