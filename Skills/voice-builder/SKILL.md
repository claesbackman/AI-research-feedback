---
name: voice-builder
description: Build, test and maintain a voice file from the user's own writing, so that an agent edits and drafts in their voice. Reads a folder of the user's papers or other prose, records who wrote each sample and for whom, separates habits from the quirks of one paper, writes voice.md with quoted evidence, checks every claim against the sources, wires the file into CLAUDE.md and tests it on a real paragraph. Also turns a later correction into a lasting rule. Use when the user asks to "extract my voice", "build a voice file", "make a style guide from my papers", "make the AI write like me", "update my voice file", corrects a draft that was written with an existing voice file and says it "does not sound like me", or runs /voice-builder. Not for a one-off rewrite when no voice file exists or is wanted (use prose-revision).
argument-hint: "[samples-folder] [output-file] | learn | check"
---

# voice-builder

Builds a voice file from the user's own prose and keeps it improving through corrections.

Inspired by Mihail Velikov's `voice-extractor` skill (the phased extraction and the verification gate) and by Chris Blattman's voice pack guide at claudeblattman.com/build-your-own/voice (sample notes, core and type guides, testing on real work, learning from corrections).

## Three modes

- `/voice-builder [samples-folder] [output-file]` builds the voice file. Default folder: `sample-papers/`. Default output: `voice.md` in the project root.
- `/voice-builder learn` turns a correction the user just made into a proposed change to the voice file.
- `/voice-builder check` tests an existing voice file on a real paragraph.

**Existing voice files.** Before building, look in the project and the samples folder for any `voice*.md`, in any letter case, and for a file that `CLAUDE.md` or `AGENTS.md` names as the voice file. `voice.md` and `VOICE.md` are the same file on most Macs and Windows machines, so never write to a name that matches an existing one in any case. If a voice file exists, ask whether to update it in place or write a new file under a name that does not collide. An existing voice file is not a sample.

In `learn` and `check` mode, "the voice file" is the one `CLAUDE.md` or `AGENTS.md` names. Otherwise use the one this search finds, and ask if there are several.

## Principles

These explain most of the steps below. Apply them when a case is not covered.

1. **The evidence is the user's own writing.** Do not import general style rules, your own taste, or another writer's rules. Every pattern in the file needs a quoted source.
2. **Your analysis is a hypothesis.** The user decides what is their voice. A pattern you found in one paper may be a coauthor, a copyeditor or an accident.
3. **Absence is weak evidence.** A word that does not appear in four papers is not thereby banned. Only the user can ban a word.
4. **Voice is style, not content.** Never carry facts, results, names or claims from the samples into later drafts.
5. **The file starts rough and improves by correction.** A short file the user has read and agrees with beats a long one they have not.

## Build mode

Five phases. Phases 1 and 3 end with a checkpoint where the user answers. Ask all questions for a checkpoint in one message, so that a user with fifteen minutes can finish.

Keep the two checkpoints separate, because the answers to the first decide which passages Phase 2 reads. Merge them only if the user asked for an uninterrupted run, and then mark every weight as provisional.

### Phase 1: discover and label the samples

List the files in the samples folder, including subfolders. Accept `.pdf`, `.tex`, `.md`, `.txt` and `.docx`. Sort the files before reading them:

- **One file per document.** Where several files are versions or formats of the same document, use one. Prefer the source (`.tex`, `.docx`) to a conversion, a conversion to the PDF, and the latest version to an earlier draft.
- **Check each conversion.** Confirm that it reaches the paper's conclusion. Lines that jump between unrelated sentences mean a two-column layout was interleaved. If a conversion is damaged, use another format. If there is none, take only short quotations from it and say so in the notes.
- **Set aside what is not the user's prose.** Slides, build notes, instructions, templates and existing voice files are not samples.

If fewer than three samples remain, stop and ask for more. One sample gives the voice of one paper.

Read the prose body of each sample. Skip references, appendices, table contents, figure notes and quoted material. Record which sections each paper has (introduction, data, method, results, robustness, conclusion) so that later comparisons use the same kind of passage across papers.

Then write `sample-notes.md` in the samples folder, one entry per file:

- **File**
- **Type** (journal article, working paper, grant proposal, referee report, policy brief, email, other)
- **Audience and purpose**
- **Authorship** (sole author, coauthored, and which parts are the user's own)
- **AI assistance** (none, edited with AI, drafted with AI, unknown)
- **Weight** (full, reduced, exclude)
- **Sections excluded** (sections of an otherwise usable sample that someone else wrote)

List the files set aside and why. Fill in what the file itself shows. Do not guess the rest.

**Checkpoint:** show which files you will use and which you set aside, and ask the user, in one message, for what you could not infer. Three questions matter most: which sections of each coauthored paper they wrote themselves, whether any sample was drafted or heavily edited with AI, and which sample sounds most like them. Give AI-drafted text and other people's sections weight "exclude". Learning from them would teach the file someone else's voice. Give a sample whose AI assistance is unknown weight "reduced".

If the user says they do not know or wants to move on, give every coauthored sample weight "reduced" and say so in the final report.

**The base.** Phase 2 starts from the samples with weight "full". Many researchers have only coauthored papers, so there may be none. The base is then the sample the user named as closest to their voice, or all samples with the highest weight present if they named none.

### Phase 2: extract patterns

Work from the base first. For each sample, collect:

- three opening sentences of major sections
- three transitions or hedges
- one example each of introducing a result, qualifying a claim, citing prior work and stating the contribution
- how paragraphs are built: where the main claim sits, how the paragraph ends
- sentence lengths, as a rough ratio of short, medium and long
- how the writer addresses the reader and refers to themselves
- how much background the writer gives before the point
- diction: favoured verbs, recurring phrases, typical qualifiers, punctuation habits

Copy each quotation from the file, not from memory, and keep its source file and line number with it. Retyping from recall is how invented quotations arise. Keep these working notes out of the samples folder.

### Phase 3: sort the patterns and let the user check

Sort every pattern into one of three groups:

- **Core:** appears in most samples, across types.
- **Type-specific:** appears only in one kind of writing, for example introductions of journal articles or referee reports.
- **Idiosyncratic:** appears in one sample only, or only in samples outside the base.

**Compare with existing writing instructions.** Read the project's `CLAUDE.md` or `AGENTS.md` and the global `~/.claude/CLAUDE.md`. Mark each core and type-specific pattern as new, already covered there, or in conflict with a rule there. A conflict is a rule the samples break, for example a ban on semicolons when every sample uses them.

**Checkpoint:** show the user a short table of the core and type-specific patterns, each with one quoted example and its mark, and a list of what you set aside as idiosyncratic. In one message, ask the user to settle each conflict (a stated preference beats an observed habit unless they say otherwise), and ask which patterns are wrong, which are right but habits they want to drop, whether anything they recognise in their own writing is missing, and whether there are words, phrases or formatting they never want used. Revise before writing the file.

### Phase 4: write the voice file

Write the voice file (`voice.md` unless another output was chosen) with these sections. Keep it under about 800 words plus the example passages, since the file is loaded into context on every writing task. Do not restate a pattern the user's existing writing instructions already cover. Add only what the samples contribute beyond it, such as the specific wording.

1. **When this applies.** Which kinds of writing the file covers, and which it does not.
2. **Stance.** Person, formality, how claims are hedged, how much the reader is assumed to know.
3. **Paragraphs and sentences.** Where the main claim sits, typical lengths, openers, how paragraphs end.
4. **Reasoning and uncertainty.** How results are introduced, qualified and compared with prior work.
5. **Structural moves.** How introductions, contribution statements and robustness discussions are framed.
6. **Diction.** Favoured verbs, qualifiers, transitions and recurring phrases, each with a quoted example and its source.
7. **Do not use.** What the user said in Phase 3, with the reason if they gave one. Do not list words that are merely absent from the samples. Such a list comes from your own idea of which words are common, and a later reader will treat it as a ban.
8. **Example passages.** Three to five short passages copied unchanged from the samples. For each: source, audience and purpose, what to notice, and what not to copy (the facts, names and results of that paper).
9. **Change log.** Empty at first. `learn` mode adds to it.

Write instructions as direct statements with the evidence beside them. Do not include a paragraph rewritten by you as a model of the voice. The user's own passages are the model.

**Type guides.** If the samples include a second type of writing with at least three samples and clear type-specific patterns, offer to write a separate guide for it, for example `voice-referee-report.md` or `voice-email.md`. A type guide states when it applies and only what differs from `voice.md`. With one type of writing, write `voice.md` only and do not mention this option at length.

### Phase 5: verify, install, test

**Verify.** Check the file against the sources with a script or text search, not by eye.

- **Quotations.** Every quoted phrase and every sentence of every example passage must appear in the named source. Collapse whitespace, join words hyphenated at line ends and strip LaTeX commands on both sides, then require an exact match. If a quotation fails, copy it again from the source or drop it. Never repair it from memory.
- **Location.** No quotation may come from an excluded sample or section.
- **Recurrence.** A pattern described as recurring needs a located quotation from each of two samples, or a count per sample for a phrase. Otherwise describe it as found in one sample, or drop it.
- **Not checkable by search.** Claims about paragraph structure or sentence rhythm rest on the example passages. Say so in the log.

Append a verification log to `sample-notes.md`: quotations checked and found, what was dropped or weakened, and what was not checkable. List what was dropped or weakened in the final message. This gate must be visible to the user. A voice file with invented quotations is worse than none.

**Install.** Propose one line for the project's `CLAUDE.md`, or `AGENTS.md` for Codex:

> When drafting or editing prose for me, read voice.md first and match it. If it conflicts with another writing instruction, tell me.

Show the line and where it would go, and add it only when the user agrees. If there is no `CLAUDE.md`, suggest `/init`. Mention that the same line in `~/.claude/CLAUDE.md`, with an absolute path to the file, makes the voice the default in every project.

**Test.** Ask the user for one paragraph from a current draft, or pick one from a draft in the project if they point to it. Edit it following `voice.md` and show the result beside the original, with one sentence on what changed. Ask what still sounds wrong. If they give a correction, run the `learn` steps on it. Tell the user that the real test is an ordinary request in a new conversation, where the file must load without being named.

**Final report.** Keep it short: where the files are, how many samples at each weight, what the verify step dropped, what was installed, and that `/voice-builder learn` records later corrections.

## Learn mode

Use after the user has corrected a draft or said what sounds wrong. The purpose is to make the correction last without piling up rules.

1. Compare the draft with the user's revision or feedback.
2. State the reusable lesson in one sentence, at its narrowest scope. "Shorter" is not a lesson. "In introductions, state the result in the first paragraph before the literature" is.
3. Separate style from facts and one-off choices. A change that corrects content, or fits only this document, is not a voice rule.
4. Read the voice file for guidance that already covers the point. If it exists and was not followed, the fix is to check that the file was loaded, not to add a rule.
5. Show the proposed change to the file and wait for the user to choose: keep, narrow, reject or defer. "No new rule" is a valid result.
6. If kept, edit the relevant section and add a line to the change log: date, the preference, its scope, the reason, and what it replaces.

If the user cannot say what sounds wrong, write two versions of the same passage with the same facts and the same audience, differing in one or two style choices that you name. Ask which they prefer and why, then continue from step 2.

## Check mode

1. Confirm the voice file exists and that `CLAUDE.md` or `AGENTS.md` points to it. Report if not.
2. Take a paragraph the user supplies, edit it following the file, and show both versions.
3. Check the edit in this order: meaning and facts unchanged, fit to the audience, reasoning, tone, length, structure.
4. Report which instructions in the file shaped the edit, and any that conflict with each other or with other writing instructions in `CLAUDE.md`.
5. If the user corrects the result, continue in learn mode.

## What not to do

- Do not score the voice file or the drafts. The user's judgment is the test.
- Do not read the samples for content to reuse.
- Do not add rules the samples or the user did not supply, including general advice on good writing or lists of "AI words".
- Do not edit `CLAUDE.md`, `AGENTS.md` or an existing voice file without showing the change first.
