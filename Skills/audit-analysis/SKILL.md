---
name: audit-analysis
description: Adversarially audit changed analysis code against a base ref, hunting for correctness errors in sample construction, merges, variable construction, silent failures, and clustering or fixed effects. Runs in an isolated subagent. Use before circulating results or submitting. This is not a reproducibility or paper-to-code review — use review-paper-code for that.
argument-hint: "[optional: base ref, default main]"
allowed-tools: Bash, Read, Grep, Glob, Agent
disable-model-invocation: true
---

# Audit Analysis Code

Find errors in changed empirical code before a referee does.

The audit runs in a subagent with a clean context. That isolation is the point: whoever wrote the code — including this session, if it helped — must not be able to steer the findings. Do not read the changed files yourself before launching, do not form a view, and do not answer the auditor's questions mid-run.

## Phase 1: Establish scope

Set `BASE` from `$ARGUMENTS` if given, otherwise `main`.

Run, and stop with a short explanation if any of the first three fail:

- `git rev-parse --git-dir` — must be a repository
- `git rev-parse --verify BASE` — the base ref must exist
- `git diff --stat BASE` — if empty, there is nothing to audit
- `git log BASE..HEAD --oneline` — may legitimately be empty when the work is uncommitted, or when HEAD is BASE and only the working tree has changed. Note it and drop the commit-message check from the audit.

Report to the user in two or three lines: base ref, number of changed files, number of changed lines, and whether commit messages are available. Then launch immediately.

## Phase 2: Launch the auditor

One `Agent` call, `subagent_type: "general-purpose"`. Substitute `BASE` and pass this verbatim:

> Review empirical research code adversarially. The author wants it broken now
> rather than by a referee. Read `git log BASE..HEAD` and `git diff BASE`, then
> the changed files in full. Follow variables built outside the diff.
>
> Check, and report on each of:
> - Claims vs. code: do comments and commit messages match what runs? Quote
>   both sides of any disagreement.
> - Sample: N before and after every filter, merge, and collapse. Take N from
>   logs; write "N unverified" where there is no log. Flag undocumented drops.
> - Merges: key, uniqueness on the side that needs it, fate of unmatched
>   observations, whether `_merge` is inspected, duplicate id-period pairs after.
> - Variables: trace every regressor and outcome. Units, logs vs. levels,
>   deflation, lag alignment. Does construction match the name?
> - Silent failures: missings coerced to zero, `if x > 0` true on missing,
>   `destring ... force`, `replace` that changes nothing, loops that skip.
>   In Python, `fillna(0)`, silent dtype coercion, chained assignment.
> - Estimation: clustering level and cluster count, what the fixed effects
>   absorb, weights, whether estimation N matches the sample traced above.
>
> Each finding: file, line, quoted excerpt, what is wrong, consequence for the
> results. Tag CONFIRMED (visible in the code) or SUSPECTED (needs the data).
> Style and naming are not findings. Order by consequence, worst first, ten max.
> Then one line per category: what you found, or that you found nothing. Close
> with the one thing you could not check without the data. Change nothing.

If the diff exceeds roughly 1,500 changed lines, run two auditors in parallel instead — one taking claims, sample, and merges, the other taking variables, silent failures, and estimation — and concatenate their findings. Do not split a smaller diff; the categories inform each other.

## Phase 3: Relay without softening

Pass the findings through in the order returned, worst first. Do not reclassify a SUSPECTED finding as fine, do not add reassurance, and do not open with what the code gets right. The user asked for errors.

Drop any finding that lacks a file, a line, and a quoted excerpt, and tell the user how many you dropped. Unanchored findings are the failure mode this design exists to catch — an auditor told to find errors will manufacture them if nothing forces it to point at code.

Reproduce the per-category coverage lines verbatim, including the categories that came back clean, and the closing line about what could not be checked without the data. A clean category is a claim the auditor is on the record for.

Fix nothing. If the user wants repairs, that is a separate request.
