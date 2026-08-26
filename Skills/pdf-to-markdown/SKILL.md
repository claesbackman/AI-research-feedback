---
name: pdf-to-markdown
description: Split a PDF into chunks and convert it to readable markdown text. Use when the user wants to read, extract, or convert a PDF document.
user-invocable: true
argument-hint: [path/to/file.pdf]
allowed-tools: Read, Bash(mdls *), Bash(pdftotext *), Bash(which *), Write
---

# PDF Split & Convert

Convert a PDF file to readable markdown text. Handles large PDFs efficiently.

## Input

- `$ARGUMENTS[0]` — Path to the PDF file (required)

## Choose the method first

Before reading anything, check whether `pdftotext` (part of poppler) is available:

```bash
which pdftotext
```

- **If available** → use the **pdftotext path** below. It is 10–100× faster than the Read tool, uses no model context for the text content, and doesn't suffer from stream idle timeouts. **Always prefer this for PDFs longer than ~30 pages.**
- **If not available** → fall back to the **Read-tool path**. Warn the user that large PDFs (>40 pages) may hit stream idle timeouts when run in subagents (~12 min cap). Prefer running in the main conversation for large files.

## Resolve the path and get page count

1. If the path is relative, resolve it relative to the current working directory.
2. Run `mdls -name kMDItemNumberOfPages "<pdf_path>"` to get the total page count. If `mdls` is unavailable or returns `(null)`, use `pdftotext` or Read to probe.

## Method A — pdftotext (preferred)

Extract the full PDF to text in one shot, then trim at references/appendix and add page markers. `pdftotext` emits a form-feed character (`\f`) at every page break — use that for pagination.

Reference implementation (bash + awk):

```bash
PDF="$1"
OUT="${PDF%.pdf}.md"
TITLE=$(basename "${PDF%.pdf}")
TMPTXT=$(mktemp)

pdftotext -layout "$PDF" "$TMPTXT"

awk -v title="$TITLE" '
BEGIN {
    print "# " title
    print ""
    page = 1
    printf "---\n## Pages %d-%d\n---\n", page, page+19
    next_marker = page + 20
}
{
    # Convert form-feed page breaks to newlines and count pages
    n = gsub(/\f/, "\n")
    if (n > 0) {
        page += n
        if (page >= next_marker) {
            printf "\n---\n## Pages %d-%d\n---\n", next_marker, next_marker+19
            next_marker += 20
        }
    }

    # Build a stripped copy for heading detection.
    # CRITICAL: strip both form feeds AND embedded newlines — gsub above inserts
    # newlines into $0, which will defeat regex anchors like ^ and $ if you skip this.
    stripped = $0
    gsub(/[\f\n]/, "", stripped)
    sub(/^[ \t]+/, "", stripped)
    sub(/[ \t]+$/, "", stripped)

    if (length(stripped) > 0) {
        # References / Bibliography — standalone word, optionally numbered, short, no prose punctuation
        if (length(stripped) < 50 && stripped !~ /[(),;]/) {
            if (stripped ~ /^([0-9]+\.?[ \t]+)?(References|REFERENCES|Bibliography|BIBLIOGRAPHY)$/) exit
            if (stripped == "Works Cited") exit
        }

        # Appendix — length up to ~120 chars (some titles are long), no prose punctuation
        if (length(stripped) < 120 && stripped !~ /[(),;]/) {
            # "Appendix A" alone (bare letter, no title)
            if (stripped ~ /^Appendix[ \t]+[A-Z][0-9]*$/) exit
            # "Appendix A. Title" or "Appendix A: Title" — punctuation REQUIRED to avoid
            # matching body-text references like "Appendix H examines the effect..."
            if (stripped ~ /^Appendix[ \t]+[A-Z][0-9]*[.:][ \t]+[A-Z].*$/) exit
            # "APPENDIX A" variants
            if (stripped ~ /^APPENDIX[ \t]+[A-Z][0-9]*([ \t]+.*)?$/) exit
            # "Online Appendix [A]"
            if (stripped ~ /^Online[ \t]+Appendix([ \t]+[A-Z].*)?$/) exit
            # "Supplemental/Supplementary/Internet Appendix"
            if (stripped ~ /^(Supplement(al|ary)|Internet)[ \t]+Appendix([ \t]+.*)?$/) exit
        }
    }

    print
}
' "$TMPTXT" > "$OUT"

rm -f "$TMPTXT"
echo "Wrote $OUT ($(wc -l < "$OUT") lines)"
```

After running, **sanity-check the output**:

```bash
# Should print nothing if trimming worked
grep -cE "^[[:space:]]*(References|Bibliography|REFERENCES|BIBLIOGRAPHY)[[:space:]]*$" "$OUT"

# Eyeball last few lines — should be prose/conclusion, not body-of-table or mid-paragraph
tail -5 "$OUT"
```

If the tail looks truncated mid-paragraph, the heading detection likely fired on a false positive. If the tail shows references or appendix content, the detection missed the heading — inspect the PDF text around that area and extend the regex.

## Method B — Read tool (fallback when pdftotext unavailable)

1. Read the PDF in chunks of up to 20 pages at a time using the Read tool's `pages` parameter: 1-20, 21-40, 41-60, etc.
2. Focus on the **MAIN TEXT ONLY**. Stop including content once you hit "References", "Bibliography", "Works Cited", or an appendix section. If references appear mid-chunk, keep everything before them and drop the rest.
3. Compile output:
   - Save alongside the PDF with a `.md` extension.
   - Header: `# [Original Filename]`
   - Page markers between chunks: `---\n## Pages X-Y\n---`
   - Preserve extracted text as-is.

**Warning:** The Read tool is slow for large PDFs (roughly 30–60 seconds per 20-page chunk). A 60-page paper can take 3–4 minutes, and sub-agents have a ~13-minute stream idle timeout that this can hit. When running a batch of conversions, run them sequentially in the main conversation or use Method A.

## Heading-detection pitfalls (hard-won lessons)

These false positives broke earlier attempts — keep them in mind whether you use Method A or B:

- **Parenthetical references in body text** like `(see Appendix B.5)` — exclude lines containing `(`, `)`, `,`, or `;`.
- **Body text starting with "Appendix X ..."** like `Appendix H examines the differential effect...` — require punctuation (`.` or `:`) immediately after the appendix letter when a title follows. Bare "Appendix A" alone on a line is still valid.
- **Line-wrapped headings** — `pdftotext` can wrap `Online Appendix` across two lines if the PDF's layout is unusual. You'll see `Online` on one line and `Appendix` on the next. The regex above matches the joined form; if you see false trims at a lone `Appendix` line, inspect and tighten.
- **Form-feed at start of page** — `pdftotext` emits `\f` as the first character on every new page. After `gsub(/\f/, "\n")` on `$0`, the line has an embedded `\n` that defeats `^` / `$` anchors unless you also `gsub(/[\f\n]/, "", stripped)` on your detection copy.
- **Length thresholds** — simple "< 50 chars" is too tight for appendix titles. "Appendix A. Merging Mortgages with the Real Estate Database" is 59 chars. Use ~120 for appendix patterns, ~50 for bare References.
- **Numbered section headings** — some papers format as `7 References` or `7. References`. Allow an optional leading number.

## Report results

Tell the user:
- Method used (pdftotext vs Read tool)
- Total pages processed
- Output file path and final line count
- Where trimming occurred (last section / page number included)
- Any pages that were unreadable or empty

For batch conversions, print a summary table and note any files whose trim point looks suspicious (very short output, or output ending mid-sentence).
