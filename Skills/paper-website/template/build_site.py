#!/usr/bin/env python3
"""
build_site.py

Builds a static digital edition of a LaTeX paper from one config file
(site.json, next to this script). Pipeline:

    1. read the root .tex file, follow \\input / \\include, drop comments
    2. replace every figure and table environment by text markers that carry
       the label, caption, notes and (for tables) the tabular through pandoc
    3. number sections, figures, tables and equations the way LaTeX does and
       rewrite cross references so the numbers match the PDF
    4. run pandoc (LaTeX -> HTML5, KaTeX math, citeproc with the paper's .bib)
    5. post-process: one page per section, footnotes to inline notes,
       citations linked to the references page, figure and table blocks
    6. wrap every page (paper pages and the hand-written pages in content/)
       in the site shell, write the search index and the hover-preview data
    7. with data tier 1 or 2, call site_data.py for the figure data

Run:  python3 build_site.py [--config path/to/site.json]

All paths in site.json are relative to the folder that holds site.json.
Needs pandoc. pdftoppm (poppler) converts PDF figures to PNG.
"""

import argparse
import bisect
import datetime
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The credit line is part of the template. Keep it when you adapt the site.
CREDIT_TEXT = ("Bäckman, C. (2026). AI tools for research: Claude Code skills for feedback on and "
               "communication of academic research (Version 1.0.0) [Computer software]. "
               "https://github.com/claesbackman/AI-research-feedback")
CREDIT_URL = "https://github.com/claesbackman/AI-research-feedback"

DEFAULTS = {
    "title": "", "subtitle": "", "short_title": "",
    "authors": [],                      # [{"name": "", "affiliation": "", "url": ""}]
    "year": "", "date": "",             # date as YYYY/MM/DD for Google Scholar
    "edition": "Digital edition", "status": "working paper",
    "language": "en",
    "main_tex": "", "bib": [], "csl": "", "pdf": "", "figure_dirs": [],
    "appendix_tex": [],                 # root file(s) of a separate online appendix
    "output_dir": "../Website",
    "site_url": "",
    "links": [],                        # [{"label": "Replication package", "url": "https://..."}]
    "bug_report_url": "",
    "footer": [],                       # paragraphs (HTML allowed): funding, disclaimers, data statement
    "acknowledgments": "",
    "abstract": "", "jel": "", "keywords": "",   # overrides for what the script extracts
    "description": "",
    "social_image": "",
    "citation": {"text": "", "bibtex": ""},
    "theme": {"scheme": "signature", "accent": "", "typeface": "", "dark_mode": True},
    "features": {"search": True, "outline": True, "previews": True, "cite_box": True, "table_csv": True},
    "structure": {
        "appendix_pages": "per-section",   # or "single"
        "appendix_marker": "",             # regex, if the paper does not use \appendix
        "nav_titles": {},                  # section id or slug -> short title for the contents rail
        "slugs": {},                       # section id -> page slug
        "skip_sections": [],               # section ids or titles to leave out
        "notes_commands": [],              # extra LaTeX commands that hold figure/table notes
    },
    "numbering": {"figure": "auto", "table": "auto", "equation": "auto"},
    "pages": [                             # hand-written pages, bodies in content/<slug>.html
        {"slug": "about", "title": "Data and code", "group": "notes"},
    ],
    "groups": {"explore": "Explore", "notes": "Notes"},
    "data": {"tier": 0},
    "pin_addresses": True,              # write page addresses into structure.slugs on first build
    "show_commit": True,                # show the paper's git commit in the version line
    "deploy": {"target": ""},           # folder the site is published to, for update_site.py --deploy
}

ACCENTS = {"vermilion": "#c4452a", "blue": "#1e88e5", "teal": "#0f8f85", "burgundy": "#a8324a", "slate": "#4a6078", "green": "#2e7d4f", "ochre": "#b7791f"}
TYPEFACES = {
    "plex": ('"IBM Plex Sans"', '"IBM Plex Serif"', '"IBM Plex Mono"',
             "family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:ital,wght@0,400;0,500;0,600;1,400"),
    "source": ('"Source Sans 3"', '"Source Serif 4"', '"Source Code Pro"',
               "family=Source+Code+Pro:wght@400;500&family=Source+Sans+3:wght@400;500;600;700&family=Source+Serif+4:ital,wght@0,400;0,500;0,600;1,400"),
    "sans": ('"Inter"', '"Inter"', '"IBM Plex Mono"',
             "family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600;700"),
    "signature": ('"Bricolage Grotesque"', '"Newsreader"', '"IBM Plex Mono"',
                  "family=Bricolage+Grotesque:opsz,wght@12..96,400..700&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,400..600;1,6..72,400..500"),
    "system": ("system-ui", "Georgia", "ui-monospace", ""),
}
# A scheme is the whole look: paper, ink, the four chart colours, the note colour, and a default accent and typeface.
# "signature" is the palette of the explorable decks in the same repository (vermilion, teal, ochre, blue on warm paper).
# "classic" is the neutral blue scheme, with the colours left as site.css defines them.
SCHEMES = {
    "classic": {"accent": "blue", "typeface": "plex", "light": {}, "dark": {}},
    "signature": {
        "accent": "vermilion", "typeface": "signature",
        "light": {"ink": "#1c2224", "ink-soft": "#3b4447", "muted": "#667074", "muted-light": "#8b9497",
                  "rule": "#e5e2d9", "rule-strong": "#d3cfc3", "bg": "#fdfcf9", "bg-panel": "#f7f5ef", "bg-inset": "#efece3", "bg-inset-hover": "#e7e3d8",
                  "bg-bar": "rgba(253,252,249,.96)", "note": "#0e7c68", "note-tint": "#0e7c6814", "annotation": "#b8760a", "warm-tint": "#f8efdc",
                  "series-1": "#c4452a", "series-2": "#128f78", "series-3": "#3a63b8", "series-4": "#b8760a", "series-5": "#6b5ca5",
                  "chart-grid": "#e5e2d9", "chart-axis": "#c3beb0", "chart-surface": "#fdfcf9", "neg": "#c4452a", "pos": "#3a63b8"},
        "dark": {"ink": "#ece9e2", "ink-soft": "#cdc9bf", "muted": "#9aa1a0", "muted-light": "#7b8382",
                 "rule": "#2b3032", "rule-strong": "#3c4244", "bg": "#161a1b", "bg-panel": "#1c2122", "bg-inset": "#262c2d", "bg-inset-hover": "#303637",
                 "bg-bar": "rgba(22,26,27,.94)", "note": "#4fcdb4", "note-tint": "#4fcdb41f", "annotation": "#e0a83a", "warm-tint": "#2a2418",
                 "series-1": "#ec7a60", "series-2": "#45c9b0", "series-3": "#7f9fe8", "series-4": "#e0a83a", "series-5": "#a99be3",
                 "chart-grid": "#2b3032", "chart-axis": "#555c5d", "chart-surface": "#161a1b", "neg": "#ec7a60", "pos": "#7f9fe8"},
    },
}

WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)
    print("WARNING:", msg, file=sys.stderr)


def merge(base, over):
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge(out[k], v)
        else:
            out[k] = v
    return out


def read(p):
    return Path(p).read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# LaTeX helpers
# ---------------------------------------------------------------------------
def brace_arg(s, start):
    """Return (content, end_index) of the brace group starting at s[start] == '{'."""
    if start >= len(s) or s[start] != "{":
        raise ValueError("expected a brace group")
    depth = 0
    i = start
    while i < len(s):
        if s[i] == "\\":
            i += 2
            continue
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1:i], i + 1
        i += 1
    raise ValueError("unbalanced braces")


def strip_comments(tex):
    out = []
    for line in tex.split("\n"):
        i = 0
        while i < len(line):
            if line[i] == "\\":
                i += 2
                continue
            if line[i] == "%":
                if re.search(r"\\(url|href|path)\{[^}]*$", line[:i]):      # a percent sign inside a URL is not a comment
                    i += 1
                    continue
                line = line[:i]
                break
            i += 1
        out.append(line)
    return "\n".join(out)


def expand_inputs(tex, base, depth=0, names=None):
    """Inline \\input, \\include, \\subfile, \\estinput and \\let aliases of \\input, relative to the root file's folder."""
    if depth > 20:
        return tex
    if names is None:
        names = ["input", "include", "subfile", "estinput"] + re.findall(r"\\let\s*\\([a-zA-Z]+)\s*=?\s*\\input\b", tex)
        names = list(dict.fromkeys(names))

    def repl(m):
        nm = (m.group(1) or m.group(2)).strip()
        if "#" in nm or nm.startswith("="):          # a macro definition, not a file
            return m.group(0)
        for cand in (base / nm, base / (nm + ".tex")):
            if cand.is_file():
                return "\n" + expand_inputs(strip_comments(read(cand)), base, depth + 1, names) + "\n"
        warn(f"\\input file not found, left out: {nm}")
        return ""
    return re.sub(r"\\(?:" + "|".join(names) + r")(?![a-zA-Z])(?:\s*\{([^}]+)\}|[ \t]+([^\s{}\\=]+))", repl, tex)


def envs(tex, names):
    """Yield (start, end, body, name) for each \\begin{name}...\\end{name}, name in names."""
    pat = re.compile(r"\\begin\{(" + "|".join(re.escape(n) for n in names) + r")\}(\[[^\]]*\])?")
    pos = 0
    while True:
        m = pat.search(tex, pos)
        if not m:
            return
        closing = "\\end{" + m.group(1) + "}"
        e = tex.find(closing, m.end())
        if e < 0:
            return
        yield m.start(), e + len(closing), tex[m.end():e], m.group(1)
        pos = e + len(closing)


def command_arg(body, names):
    """Content of the first \\name{...} found, for name in names (in that order)."""
    for nm in names:
        m = re.search(r"\\" + nm + r"\s*(?:\[[^\]]*\])?\s*\{", body)
        if m:
            try:
                return brace_arg(body, m.end() - 1)[0]
            except ValueError:
                continue
    return ""


def remove_commands_with_args(tex, names, nargs):
    for nm in names:
        pat = re.compile(r"\\" + nm + r"\*?(?![a-zA-Z])\s*(?:\[[^\]]*\])?")
        pos = 0
        while True:
            m = pat.search(tex, pos)
            if not m:
                break
            end = m.end()
            try:
                for _ in range(nargs):
                    m2 = re.match(r"\s*\{", tex[end:])
                    if m2:
                        _, end = brace_arg(tex, end + m2.end() - 1)
                    else:
                        m3 = re.match(r"\s*\\[a-zA-Z@]+", tex[end:])   # \renewcommand\thetable{...}
                        if m3:
                            end += m3.end()
            except ValueError:
                pos = m.end()
                continue
            tex = tex[:m.start()] + tex[end:]
            pos = m.start()
    return tex


def harvest_macros(preamble):
    """\\newcommand-style definitions from the preamble, so pandoc can expand them."""
    out = []
    for m in re.finditer(r"\\(newcommand|providecommand|DeclareMathOperator)\*?(?![a-zA-Z])", preamble):
        i = m.end()
        try:
            for _ in range(2):
                while i < len(preamble) and preamble[i] in " \t\n":
                    i += 1
                while preamble[i] == "[":
                    i = preamble.index("]", i) + 1
                if preamble[i] == "{":
                    _, i = brace_arg(preamble, i)
                else:
                    i += re.match(r"\\[a-zA-Z@]+", preamble[i:]).end()
                    while i < len(preamble) and preamble[i] == "[":
                        i = preamble.index("]", i) + 1
        except (ValueError, AttributeError, IndexError):
            continue
        d = preamble[m.start():i]
        if "@" in d or "\\if" in d or "\\def" in d:
            continue
        out.append(d)
    return "\n".join(out)


def norm_colspec(spec):
    """Reduce a tabular column specification to l, c and r."""
    out, i = [], 0
    while i < len(spec):
        c = spec[i]
        try:
            if c in "@><!":
                i += 1
                if i < len(spec) and spec[i] == "{":
                    _, i = brace_arg(spec, i)
            elif c == "*":
                n, j = brace_arg(spec, i + 1)
                sub, i = brace_arg(spec, j)
                out.append(norm_colspec(sub) * (int(n) if n.strip().isdigit() else 1))
            elif c in "pmb":
                out.append("l")
                i += 1
                if i < len(spec) and spec[i] == "{":
                    _, i = brace_arg(spec, i)
            elif c in "SDd":
                out.append("r")
                i += 1
                if i < len(spec) and spec[i] == "[":
                    i = spec.index("]", i) + 1
                while i < len(spec) and spec[i] == "{":
                    _, i = brace_arg(spec, i)
            elif c in "lcr":
                out.append(c)
                i += 1
            elif c.isalpha():
                out.append({"C": "c", "R": "r"}.get(c, "l"))
                i += 1
            else:
                i += 1
        except ValueError:
            i += 1
    return "".join(out)


TABULAR_ENVS = ["tabularx", "tabular*", "tabulary", "tabular"]


def clean_tabular(src, env):
    """Simplify one tabular-like environment so pandoc can parse it."""
    m = re.match(r"\\begin\{" + re.escape(env) + r"\}\s*(\[[^\]]*\])?\s*", src)
    i = m.end()
    try:
        if env != "tabular":
            _, i = brace_arg(src, i)          # width argument
            i += len(src[i:]) - len(src[i:].lstrip())
        spec, i = brace_arg(src, i)
    except ValueError:
        return src
    body = src[i:src.rindex("\\end{" + env + "}")]
    tab = "\\begin{tabular}{" + norm_colspec(spec) + "}" + body + "\\end{tabular}"
    tab = re.sub(r"\\tnote\{([^}]*)\}", r"\\textsuperscript{\1}", tab)
    tab = re.sub(r"\\sym\{([^}]*)\}", r"\\textsuperscript{\1}", tab)
    tab = re.sub(r"\\shortstack(?:\[[^\]]*\])?\{([^{}]*)\}", lambda m: " ".join(x.strip() for x in m.group(1).split("\\\\")), tab)
    tab = re.sub(r"\\makecell(?:\[[^\]]*\])?\{([^{}]*)\}", lambda m: " ".join(x.strip() for x in m.group(1).split("\\\\")), tab)
    tab = re.sub(r"\\cmidrule\s*(\([^)]*\))?\s*\{[^}]*\}", "", tab)
    tab = re.sub(r"\\cline\s*\{[^}]*\}", "", tab)
    tab = re.sub(r"\\multirow\{[^}]*\}\{[^}]*\}\{([^}]*)\}", r"\1", tab)
    tab = re.sub(r"\\\\\s*\[[^\]]*\]", r"\\\\", tab)             # \\[2pt]
    tab = re.sub(r"\\(addlinespace|noalign)\s*(\[[^\]]*\])?(\{[^}]*\})?", "", tab)
    tab = re.sub(r"\\(small|footnotesize|scriptsize|tiny|normalsize|singlespacing|centering)\b", "", tab)
    tab = re.sub(r"\\(hline|toprule)\s*\\(hline|toprule)", r"\\toprule", tab)
    tab = re.sub(r"\$\^\{\\dagger\}\$", r"\\textsuperscript{†}", tab)
    tab = re.sub(r"\$\^\{(\*+)\}\$", r"\\textsuperscript{\1}", tab)
    tab = re.sub(r"\$([-+]?\d[\d.,]*)\$", lambda m: m.group(1).replace("-", "−"), tab)
    tab = re.sub(r"\$\\pm\$", "±", tab)
    tab = re.sub(r"\\omit\s*", "", tab)
    return tab


def clean_notes(notes):
    notes = notes.strip()
    for _ in range(3):
        notes = re.sub(r"^\\(scriptsize|footnotesize|tiny|small|normalsize|raggedright|justify|centering|singlespacing)\s*", "", notes)
        notes = re.sub(r"^\{\s*", "", notes) if notes.startswith("{\\") and notes.count("{") > notes.count("}") else notes
        notes = re.sub(r"^\\item\s*(?!\[)", "", notes)
    notes = re.sub(r"^\\(emph|textit|textbf)\{\s*Notes?\s*[:.]?\s*\}\s*[:.]?\s*", "", notes)
    notes = re.sub(r"^Notes?\s*[:.]\s*", "", notes)
    notes = re.sub(r"\\item\[([^\]]+)\]\s*", r"\n\n(\1) ", notes)     # lettered table notes
    notes = re.sub(r"\\item\b\s*", "\n\n", notes)
    return notes.strip()


def loose_text(t):
    """Text of a float that sits outside its tabulars (panel titles, unlabelled notes), without layout commands."""
    while True:
        m = re.search(r"\\caption\*?\s*(?:\[[^\]]*\])?\s*\{", t)
        if not m:
            break
        try:
            _, e = brace_arg(t, m.end() - 1)
        except ValueError:
            break
        t = t[:m.start()] + t[e:]
    t = re.sub(r"\\label\{[^}]*\}", "", t)
    t = re.sub(r"\\(begin|end)\{[^}]*\}(\[[^\]]*\])?(\{[^{}]*\})*", " ", t)
    t = re.sub(r"\\(resizebox|scalebox|adjustbox|vspace|hspace|setlength|captionsetup)\*?(\[[^\]]*\])?(\{[^{}]*\})*", " ", t)
    t = re.sub(r"\\(centering|small|footnotesize|scriptsize|tiny|normalsize|par|noindent|bigskip|medskip|smallskip|hfill|vfill|raggedright|ContinuedFloat|singlespacing|doublespacing|linewidth|textwidth)\b", " ", t)
    t = re.sub(r"\\\\(\[[^\]]*\])?", " ", t)
    t = t.strip()
    while t.startswith(("{", "}")) or t.endswith(("{", "}")) and t.count("{") != t.count("}"):
        t = t.strip("{} \n\t")
        if not t:
            break
    if "\\def" in t or "#1" in t or "&" in t:          # estout boilerplate, or rows of a table the script could not delimit
        return ""
    return t if len(re.findall(r"[A-Za-z]", re.sub(r"\\[a-zA-Z]+", "", t))) >= 3 else ""


def longtable_body(body):
    """Rewrite the inside of a longtable as caption + label + one plain tabular."""
    body = body.lstrip()
    try:
        spec, i = brace_arg(body, 0)
    except ValueError:
        return body
    rest = body[i:]
    head = ""
    m = re.search(r"\\caption(?!\*)\s*(?:\[[^\]]*\])?\s*\{", rest)
    if m:
        try:
            _, e = brace_arg(rest, m.end() - 1)
            lab = re.match(r"\s*\\label\{[^}]*\}", rest[e:])
            e2 = e + (lab.end() if lab else 0)
            head = rest[m.start():e2]
            rest = rest[:m.start()] + re.sub(r"^\s*\\\\(\[[^\]]*\])?", "", rest[e2:])
        except ValueError:
            pass
    parts = re.split(r"\\end(?:firsthead|head|foot|lastfoot)\b", rest)
    if len(parts) > 1:                       # keep the first header and the rows, drop the repeated headers and footers
        rest = parts[0] + parts[-1]
    return head + "\n\\begin{tabular}{" + spec + "}" + rest + "\\end{tabular}\n"


def split_rows(body):
    """Split an align-like body at top-level \\\\ (not inside cases, matrices or braces)."""
    rows, cur, depth, brace, i = [], [], 0, 0, 0
    while i < len(body):
        if body.startswith("\\begin{", i):
            depth += 1
        elif body.startswith("\\end{", i):
            depth -= 1
        if body[i] == "\\" and i + 1 < len(body):
            if body[i + 1] == "\\" and depth == 0 and brace == 0:
                rows.append("".join(cur))
                cur = []
                i += 2
                m = re.match(r"\s*\[[^\]]*\]", body[i:])
                if m:
                    i += m.end()
                continue
            cur.append(body[i:i + 2])
            i += 2
            continue
        if body[i] == "{":
            brace += 1
        elif body[i] == "}":
            brace -= 1
        cur.append(body[i])
        i += 1
    rows.append("".join(cur))
    return [r for r in rows if r.strip()]


def plain(s):
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def slugify(s, maxlen=40):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    if len(s) > maxlen:
        s = s[:maxlen].rsplit("-", 1)[0]
    return s or "section"


# ---------------------------------------------------------------------------
# Numbering
# ---------------------------------------------------------------------------
class Counter:
    """One LaTeX counter (figure, table or equation) across main text and appendix."""

    def __init__(self, fmt_main, fmt_app, reset_app):
        self.fmt = {"main": fmt_main, "app": fmt_app}
        self.reset_app = reset_app
        self.n = 0
        self.where = "main"
        self.sec = None

    def next(self, where, sec):
        if where != self.where:
            self.where = where
            if self.reset_app:
                self.n = 0
        fmt = self.fmt[where]
        if "{sec}" in fmt and sec != self.sec:
            self.n = 0
        self.sec = sec
        self.n += 1
        return fmt.format(n=self.n, sec=sec or "")


def parse_the(tex, kind):
    """Format string from the first \\renewcommand{\\the<kind>}{...} in tex, or None."""
    m = re.search(r"\\renewcommand\*?\s*\{?\\the" + kind + r"\}?\s*\{", tex)
    if not m:
        return None
    try:
        d, _ = brace_arg(tex, m.end() - 1)
    except ValueError:
        return None
    d = re.sub(r"\\(arabic|roman|Roman|alph|Alph)\{" + kind + r"\}", "{n}", d)
    d = re.sub(r"\\thesection|\\(arabic|Alph|alph)\{section\}", "{sec}", d)
    d = re.sub(r"\\[a-zA-Z]+", "", d).replace(" ", "")
    return d if "{n}" in d and not re.search(r"[{}]", d.replace("{n}", "").replace("{sec}", "")) else None


def counter_events(tex, kind):
    """Places where the paper changes a counter: (position, "fmt", format) and (position, "set", value)."""
    ev = []
    for m in re.finditer(r"\\renewcommand\*?\s*\{?\\the" + kind + r"\}?\s*\{", tex):
        f = parse_the(tex[m.start():], kind)
        if f:
            ev.append((m.start(), "fmt", f))
    for m in re.finditer(r"\\setcounter\{" + kind + r"\}\{(\d+)\}", tex):
        ev.append((m.start(), "set", int(m.group(1))))
    return sorted(ev)


def detect_counter(kind, preamble, main, app, override):
    """Starting format of a counter. Changes inside the text are followed by counter_events()."""
    within = re.search(r"\\numberwithin\{" + kind + r"\}\{section\}", preamble + main)
    fmt_main = parse_the(preamble, kind) or ("{sec}.{n}" if within else "{n}")
    fmt_app = "{sec}.{n}" if re.search(r"\\numberwithin\{" + kind + r"\}\{section\}", app) else fmt_main
    c = Counter(fmt_main, fmt_app, False)
    c.fixed = False
    if isinstance(override, dict):
        c = Counter(override.get("main", fmt_main), override.get("appendix", fmt_app), override.get("reset_in_appendix", True))
        c.fixed = True                    # numbering set by hand in site.json: ignore what the source says
    return c


def section_lookup(tex, where):
    """Function pos -> label of the numbered section that contains pos."""
    starts = [m.start() for m in re.finditer(r"\\section\s*(?:\[[^\]]*\])?\s*\{", tex)]

    def at(pos):
        k = bisect.bisect_right(starts, pos)
        if k == 0:
            return ""
        return str(k) if where == "main" else (chr(64 + k) if k <= 26 else str(k))
    return at


# ---------------------------------------------------------------------------
# 1-3. Preprocess the LaTeX
# ---------------------------------------------------------------------------
class Registry:
    def __init__(self):
        self.figures = {}
        self.tables = {}
        self.equations = {}
        self.order = []
        self.sublabels = {}      # label of a subfigure -> (label of its figure, panel letter)
        self.extra_dirs = []


FIG_ENVS = ["figure*", "figure", "sidewaysfigure"]
TAB_ENVS = ["table*", "table", "sidewaystable"]
NOTE_COMMANDS = ["caption\\*", "floatfoot", "figurenotes", "tablenotes", "fignote", "fignotes", "tabnote", "tabnotes", "note", "notes", "Notes", "legend"]


def find_notes(body, cfg, anchor_pat):
    """Notes of a float: a notes command, a notes environment, a minipage, or trailing 'Notes:' text."""
    notes = command_arg(body, NOTE_COMMANDS + cfg["structure"]["notes_commands"])
    if notes:
        return notes
    for s, e, b, nm in envs(body, ["tablenotes", "figurenotes", "fignotes", "tabnotes", "minipage"]):
        if nm == "minipage":
            b = re.sub(r"^\s*(\[[^\]]*\])*\s*\{[^}]*\}", "", b)      # position and width arguments
            if "\\includegraphics" in b or "\\begin{tabular" in b:
                continue
        notes = b
    if notes:
        return notes
    last = 0
    for m in re.finditer(anchor_pat, body):
        last = m.end()
    m = re.search(r"(?:\\(?:emph|textit|textbf)\{)?\s*Notes?\s*[:.]", body[last:])
    if m:
        tail = body[last + m.start():]
        tail = re.sub(r"\\label\{[^}]+\}", "", tail)
        return tail.strip().rstrip("}").strip()
    return ""


def preprocess(cfg, reg):
    root = cfg["_main_tex"]
    base = root.parent
    full = expand_inputs(strip_comments(read(root)), base)
    if "\\begin{document}" in full:
        preamble, doc = full.split("\\begin{document}", 1)
    else:
        preamble, doc = "", full
    doc = doc.split("\\end{document}")[0]
    while True:                                   # floats inside \afterpage{...} would be dropped by pandoc
        m = re.search(r"\\afterpage\s*\{", doc)
        if not m:
            break
        try:
            inner, end = brace_arg(doc, m.end() - 1)
        except ValueError:
            break
        doc = doc[:m.start()] + inner + doc[end:]

    # abstract, JEL codes, keywords
    abstract = ""
    for s, e, b, _ in envs(doc, ["abstract"]):
        abstract = b
    first_sec = re.search(r"\\section\*?\s*(?:\[[^\]]*\])?\s*\{", doc)
    front = doc[:first_sec.start()] if first_sec else doc
    jel = re.search(r"JEL[^:\n]{0,30}:\s*([^\n\\]+)", front)
    kw = re.search(r"Key\s?words[^:\n]{0,5}:\s*([^\n\\]+)", front)
    clean = lambda m: re.sub(r"[{}]", "", m.group(1)).strip(" .") if m else ""
    abstract = re.split(r"(?:\\begin\{flushleft\}|\\noindent|\\bigskip|\\medskip|\\vspace\{[^}]*\}|\s)*(?:\\(?:textbf|emph|textit|textsc)\{)?\s*(?:JEL|Key\s?words)", abstract, maxsplit=1)[0]
    thanks = ""
    tm = re.search(r"\\title\s*(?:\[[^\]]*\])?\s*\{", full)
    if tm:
        try:
            title_src, _ = brace_arg(full, tm.end() - 1)
            thanks = command_arg(title_src, ["thanks", "footnote"])
        except ValueError:
            pass
    reg.front = dict(abstract=abstract.strip(), jel=clean(jel), keywords=clean(kw), thanks=thanks.strip())

    if not first_sec:
        raise SystemExit("No \\section found in the paper. The site needs sections to split the text into pages.")
    body = doc[first_sec.start():]
    lead = re.sub(r"\\begin\{abstract\}.*?\\end\{abstract\}", "", front, flags=re.S)
    lead = lead.split("\\maketitle")[-1]
    lead_text = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})*", "", lead)
    if len(lead_text.strip()) > 1500:      # the paper opens without an Introduction heading
        body = "\\section{Introduction}\n" + lead.strip() + "\n\n" + body

    # main text / appendix
    marker = cfg["structure"]["appendix_marker"] or r"\\appendix\b|\\begin\{appendix\}|\\begin\{appendices\}"
    m = re.search(marker, body)
    main, app = (body[:m.start()], body[m.end():]) if m else (body, "")
    if not m and cfg["structure"]["appendix_marker"]:
        warn("structure.appendix_marker matched nothing in the paper. Check the regular expression (in JSON every LaTeX backslash is four backslashes).")
    # anything after the bibliography that is not an appendix still belongs to the appendix part
    if app.strip():
        head = re.split(r"\\section\*?\s*(?:\[[^\]]*\])?\s*\{", app, maxsplit=1)[0]
        head_text = re.sub(r"\\(renewcommand|setcounter)\*?[^\n]*", "", head)
        if len(re.sub(r"\\[a-zA-Z]+\*?", "", head_text).strip()) > 200 or "\\begin{" in head_text:
            app = "\\section{Appendix}\\label{app:auto}\n" + app

    # a separate online appendix: its own root file, appended to the appendix part
    extra_macros = []
    for apath in cfg["_appendix_tex"]:
        afull = expand_inputs(strip_comments(read(apath)), apath.parent)
        apre, adoc = afull.split("\\begin{document}", 1) if "\\begin{document}" in afull else ("", afull)
        adoc = adoc.split("\\end{document}")[0]
        extra_macros.append(harvest_macros(apre))
        fs = re.search(r"\\section\*?\s*(?:\[[^\]]*\])?\s*\{", adoc)
        abody = adoc[fs.start():] if fs else "\\section{Online Appendix}\n" + adoc.split("\\maketitle")[-1]
        # the xr package: \externaldocument[P-]{file} puts a prefix on the other file's labels
        own = [l for l in re.findall(r"\\label\{([^}]+)\}", abody)]
        pm = [m.group(1) or "" for m in re.finditer(r"\\externaldocument\s*(?:\[([^\]]*)\])?\s*\{([^}]*)\}", preamble)
              if Path(m.group(2)).stem == apath.stem]
        prefix = pm[0] if pm else ""
        back = [m.group(1) for m in re.finditer(r"\\externaldocument\s*\[([^\]]+)\]", apre)]
        def relabel(m):
            cmd, labs = m.group(1), [x.strip() for x in m.group(2).split(",")]
            out_ = []
            for lab in labs:
                if lab in own:
                    lab = prefix + lab
                else:
                    for b in back:
                        if lab.startswith(b):
                            lab = lab[len(b):]
                            break
                out_.append(lab)
            return "\\" + cmd + "{" + ",".join(out_) + "}"
        if prefix or back:
            abody = re.sub(r"\\(label|ref|eqref|autoref|cref|Cref|pageref|nameref)\{([^}]+)\}", relabel, abody)
        abody = re.sub(r"\\appendix\b|\\begin\{appendi(?:x|ces)\}", "", abody)
        app = (app + "\n\n" if app.strip() else "") + abody
        reg.extra_dirs.append(apath.parent)

    num = cfg["numbering"]
    counters = {k: detect_counter(k, preamble, main, app, num.get(k)) for k in ("figure", "table", "equation")}

    def stepper(tex, kind, where):
        """Next number of a counter at a position, after applying the counter changes before it."""
        sec_at = section_lookup(tex, where)
        ev, k = counter_events(tex, kind), [0]
        c = counters[kind]

        def step(pos):
            while k[0] < len(ev) and ev[k[0]][0] < pos:
                _, typ, val = ev[k[0]]
                k[0] += 1
                if c.fixed:
                    continue
                if typ == "fmt":
                    c.fmt[where] = val
                else:
                    c.n, c.where = val, where
            return c.next(where, sec_at(pos))
        return step

    def process_figures(tex, where):
        step = stepper(tex, "figure", where)
        pieces, pos = [], 0
        for s, e, body_, _ in envs(tex, FIG_ENVS):
            pieces.append(tex[pos:s])
            images = re.findall(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", body_)
            subcaps, sublabs = [], []
            outer = body_
            for ss, se, sb, _ in envs(body_, ["subfigure"]):
                subcaps.append(re.sub(r"\\label\{[^}]+\}", "", command_arg(sb, ["caption"])).strip())
                sublabs.append(re.findall(r"\\label\{([^}]+)\}", sb))
                outer = outer.replace(body_[ss:se], "")
            for c in re.findall(r"\\subfloat\s*\[([^\]]*)\]", body_):
                subcaps.append(re.sub(r"\\label\{[^}]+\}", "", c).strip())
                sublabs.append(re.findall(r"\\label\{([^}]+)\}", c))
            outer = re.sub(r"\\subfloat\s*\[[^\]]*\]", "", outer)
            label = re.search(r"\\label\{([^}]+)\}", outer)
            number = step(s)
            label = label.group(1) if label else f"fig:auto-{number}"
            for k, labs in enumerate(sublabs):
                for lab in labs:
                    if lab != label:
                        reg.sublabels[lab] = (label, chr(97 + k) if k < 26 else str(k + 1))
            cap = ""
            cm = re.search(r"\\caption(?!\*)\s*(?:\[[^\]]*\])?\s*\{", outer)
            if cm:
                cap, _ = brace_arg(outer, cm.end() - 1)
            cap = re.sub(r"\\label\{[^}]+\}", "", cap)
            notes = find_notes(outer, cfg, r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{[^}]+\}|\\caption(?!\*)")
            if cm and notes and cap and notes.strip() == cap.strip():
                notes = ""
            reg.figures[label] = dict(number=number, images=images, where=where,
                                      subcaptions=subcaps if len(subcaps) == len(images) else [])
            reg.order.append(("fig", label))
            if len(subcaps) == len(images):
                cap += "".join(f"\n\n@@SUB@@ {c}" for c in subcaps)
            pieces.append(f"\n\n@@FIG|{label}|START@@\n\n{cap}\n\n@@FIG|{label}|NOTES@@\n\n{clean_notes(notes)}\n\n@@FIG|{label}|END@@\n\n")
            pos = e
        pieces.append(tex[pos:])
        return "".join(pieces)

    def process_tables(tex, where):
        step = stepper(tex, "table", where)
        pieces, pos = [], 0
        for s, e, body_, env_name in envs(tex, TAB_ENVS + ["longtable"]):
            pieces.append(tex[pos:s])
            if env_name == "longtable":
                body_ = longtable_body(body_)
            label = re.search(r"\\label\{([^}]+)\}", body_)
            continued = r"\ContinuedFloat" in body_ and bool(reg.order) and reg.order[-1][0] == "tab"
            if continued:
                number = reg.tables[reg.order[-1][1]]["number"]
            else:
                number = step(s)
            if label:
                label = label.group(1)
            elif continued:
                label = reg.order[-1][1] + "-cont"
            else:
                label = f"tab:auto-{number}"
            cap = ""
            cm = re.search(r"\\caption(?!\*)\s*(?:\[[^\]]*\])?\s*\{", body_)
            if cm:
                cap, _ = brace_arg(body_, cm.end() - 1)
            cap = re.sub(r"\\label\{[^}]+\}", "", cap)
            spans = [(ts, te, nm) for ts, te, _, nm in envs(body_, TABULAR_ENVS)]
            tabulars = [(body_[ts:te], nm) for ts, te, nm in spans]
            # short text before or between the tabulars is a panel title
            titles, prev = [], 0
            for ts, te, _ in spans:
                t = loose_text(body_[prev:ts])
                titles.append(t if len(t) < 200 else "")
                prev = te
            images = re.findall(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", body_) if not tabulars else []
            notes = find_notes(body_, cfg, r"\\end\{tabular[x*y]?\}|\\includegraphics\s*(?:\[[^\]]*\])?\s*\{[^}]+\}")
            head_src = (tabulars[0][0] if tabulars else "").split(r"\midrule")[0]
            head_src = re.split(r"\\toprule|\\hline", head_src)[-1] if re.search(r"\\toprule|\\hline", head_src) else head_src
            n_head = len([r for r in re.split(r"\\\\", head_src) if r.strip() and "&" in r]) if r"\midrule" in (tabulars[0][0] if tabulars else "") else 0
            reg.tables[label] = dict(number=number, where=where, n_head=n_head, images=images)
            reg.order.append(("tab", label))
            if not tabulars and not images:
                warn(f"Table {number} ({label}) has no tabular environment the script can read. The page points to the PDF.")
            if not notes and spans:                     # trailing text without a "Notes:" label
                tail = loose_text(body_[spans[-1][1]:])
                notes = tail if len(tail) > 20 else ""
            tab_clean = "\n\n".join((f"@@PANEL@@ {ti}\n\n" if ti else "") + clean_tabular(t, nm) for (t, nm), ti in zip(tabulars, titles))
            pieces.append(f"\n\n@@TAB|{label}|START@@\n\n{cap}\n\n@@TAB|{label}|BODY@@\n\n{tab_clean}\n\n@@TAB|{label}|NOTES@@\n\n{clean_notes(notes)}\n\n@@TAB|{label}|END@@\n\n")
            pos = e
        pieces.append(tex[pos:])
        return "".join(pieces)

    def process_equations(tex, where):
        step = stepper(tex, "equation", where)
        pat = re.compile(r"\\begin\{(equation|align|gather|multline|eqnarray|alignat|flalign)(\*?)\}(.*?)\\end\{\1\2\}", re.S)

        subranges = [(a, b) for a, b, _, _ in envs(tex, ["subequations"])]
        sub = {"i": None, "parent": "", "k": 0}

        def num_at(pos):
            for i, (a, b) in enumerate(subranges):
                if a <= pos < b:                      # 2.4a, 2.4b: one parent number, a letter per equation
                    if sub["i"] != i:
                        sub.update(i=i, parent=step(pos), k=0)
                    sub["k"] += 1
                    return sub["parent"] + chr(96 + sub["k"])
            return step(pos)

        def repl(m):
            env, star, body_ = m.group(1), m.group(2), m.group(3)
            if env == "alignat":
                body_ = re.sub(r"^\s*\{[^}]*\}", "", body_)
            if env == "eqnarray":
                body_ = re.sub(r"&\s*(=|\\leq|\\geq|\\le|\\ge|<|>|\\approx|\\equiv|\\sim)\s*&", r"&\1 ", body_)
            if env in ("equation", "multline"):
                labels = re.findall(r"\\label\{([^}]+)\}", body_)
                body_ = re.sub(r"\\label\{[^}]+\}", "", body_).strip()
                if env == "multline":
                    body_ = "\\begin{gathered}" + body_ + "\\end{gathered}"
                if star or re.search(r"\\(nonumber|notag)\b", body_):
                    return "\\[ " + re.sub(r"\\(nonumber|notag)\b", "", body_) + " \\]"
                own_tag = re.search(r"\\tag\*?\{([^}]*)\}", body_)
                n = own_tag.group(1) if own_tag else num_at(m.start())
                for lab in labels:
                    reg.equations[lab] = n
                if own_tag:
                    return f"\\[ {body_} \\]"
                return f"\\[ {body_} \\tag{{{n}}} \\]"
            inner = "gather" if env == "gather" else "align"
            if star:
                body_ = re.sub(r"\\label\{[^}]+\}|\\(nonumber|notag)\b", "", body_)
                return "\\[\\begin{" + inner + "ed}" + body_.strip() + "\\end{" + inner + "ed}\\]"
            rows = []
            for row in split_rows(body_):
                labels = re.findall(r"\\label\{([^}]+)\}", row)
                row = re.sub(r"\\label\{[^}]+\}", "", row).strip()
                if re.search(r"\\(nonumber|notag)\b", row):
                    rows.append(re.sub(r"\\(nonumber|notag)\b", "\\\\notag ", row))
                    continue
                own_tag = re.search(r"\\tag\*?\{([^}]*)\}", row)
                n = own_tag.group(1) if own_tag else num_at(m.start())
                for lab in labels:
                    reg.equations[lab] = n
                if own_tag:
                    rows.append(row)
                    continue
                rows.append(f"{row} \\tag{{{n}}}")
            return "\\[\\begin{" + inner + "}" + " \\\\ ".join(rows) + "\\end{" + inner + "}\\]"
        return re.sub(r"\\(begin|end)\{subequations\}", "", pat.sub(repl, tex))

    main = process_equations(process_tables(process_figures(main, "main"), "main"), "main")
    app = process_equations(process_tables(process_figures(app, "app"), "app"), "app") if app.strip() else ""
    tex = main + ("\n\n@@APPENDIX@@\n\n" + app if app else "")

    # commands that only matter on paper, or that pandoc does not know
    tex = remove_commands_with_args(tex, ["renewcommand", "setcounter", "addcontentsline", "setlength", "addtocounter"], 2)
    tex = remove_commands_with_args(tex, ["bibliographystyle", "bibliography", "printbibliography", "thispagestyle", "pagestyle",
                                          "vspace", "hspace", "linespread", "pagenumbering", "numberwithin", "graphicspath"], 1)
    tex = re.sub(r"\\(centerfloat|clearpage|cleardoublepage|newpage|pagebreak|appendix|centering|singlespacing|onehalfspacing|doublespacing|"
                 r"par|noindent|bigskip|medskip|smallskip|vfill|hfill|FloatBarrier|maketitle|tableofcontents|listoffigures|listoftables|"
                 r"phantomsection|printbibliography|normalsize)\b", "", tex)
    tex = re.sub(r"\\(scriptsize|footnotesize|tiny|small|large|Large|LARGE)\b", "", tex)
    tex = re.sub(r"\\(begin|end)\{(center|landscape|appendix|appendices|singlespace|doublespace|onehalfspace|spacing|flushleft|flushright)\}(\{[^}]*\})?", "", tex)
    reg.macros = "\n".join(dict.fromkeys(x for x in [harvest_macros(preamble)] + extra_macros if x))
    reg.bib_from_tex = [b.strip() for m in re.finditer(r"\\(?:bibliography|addbibresource)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", full)
                        for b in m.group(1).split(",")]
    reg.graphicspath = re.findall(r"\{([^{}]+)\}", (re.search(r"\\graphicspath\s*\{((?:\{[^{}]*\}\s*)+)\}", full) or [None, ""])[1])
    return tex


# ---------------------------------------------------------------------------
# 4. pandoc
# ---------------------------------------------------------------------------
def run_pandoc(tex, cfg, reg, cite=True):
    cmd = ["pandoc", "-f", "latex", "-t", "html5", "--wrap=none", "--katex"]
    if cite and cfg["_bib"]:
        cmd += ["--citeproc", "--csl", str(cfg["_csl"])]
        for b in cfg["_bib"]:
            cmd += ["--bibliography", str(b)]

    def run(src):
        return subprocess.run(cmd, input=src, capture_output=True, text=True, cwd=cfg["_main_tex"].parent)
    try:
        r = run(reg.macros + "\n\n" + tex) if reg.macros else run(tex)
        if r.returncode != 0 and reg.macros:
            warn("pandoc failed with the preamble macros, retrying without them. Macros from the preamble will show as raw commands.")
            r = run(tex)
    except FileNotFoundError:
        raise SystemExit("pandoc is not installed. Install it (brew install pandoc, or https://pandoc.org/installing.html) and run again.")
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        raise SystemExit("pandoc failed. The preprocessed source is in _preprocessed.tex next to site.json. "
                         "The line number in the message above refers to that file.")
    if r.stderr.strip():
        for line in r.stderr.strip().split("\n")[:15]:
            warn("pandoc: " + line)
    return r.stdout


# ---------------------------------------------------------------------------
# 5. Post-process pandoc HTML
# ---------------------------------------------------------------------------
def strip_p(s):
    s = s.strip()
    s = re.sub(r"^<p>", "", s)
    s = re.sub(r"</p>$", "", s)
    return s.strip()


def postprocess(h, cfg, reg):
    def fig_block(m):
        label = m.group(1)
        parts = re.split(r"<p>@@SUB@@\s*", m.group(2))
        cap = strip_p(parts[0])
        subs = [strip_p(x) for x in parts[1:]]
        notes = strip_p(m.group(3))
        info = reg.figures[label]
        info["title"] = plain(cap)
        imgs = []
        for k, src in enumerate(info.get("web", [])):
            sub = subs[k] if k < len(subs) and len(subs) == len(info.get("web", [])) else ""
            if sub:
                sub = f"({chr(97 + k)}) " + sub
            imgs.append(f'<a class="fig-img" href="{src}" target="_blank" rel="noopener"><img src="{src}" alt="{html.escape(plain(cap))}" loading="lazy"></a>'
                        + (f'<div class="fig-sub">{sub}</div>' if sub else ""))
        cols = " cols-2" if len(imgs) > 1 else ""
        static = f'<div class="fig-static{cols}">' + "".join(f"<div>{i}</div>" for i in imgs) + "</div>" if imgs else '<p class="muted small">The image for this figure was not found. See the PDF.</p>'
        return (
            f'<figure class="paper-figure" id="{label}" data-fig="{label}">'
            f'<div class="fig-head"><span class="fig-label">Figure {info["number"]}</span><span class="fig-title">{cap}</span></div>'
            f'<div class="fig-controls"></div>'
            f'<div class="fig-body"><div class="fig-chart">{static}</div><div class="fig-table" hidden></div></div>'
            + (f'<figcaption class="fig-notes"><span class="notes-label">Notes:</span> {notes}</figcaption>' if notes else "")
            + '<div class="fig-links"></div></figure>'
        )
    h = re.sub(r"<p>@@FIG\|([^|]+)\|START@@</p>(.*?)<p>@@FIG\|\1\|NOTES@@</p>(.*?)<p>@@FIG\|\1\|END@@</p>", fig_block, h, flags=re.S)

    def tab_block(m):
        label = m.group(1)
        cap = strip_p(m.group(2))
        body = m.group(3).strip()
        notes = m.group(4).strip()
        notes = re.sub(r"</?p>", lambda mm: "" if mm.group(0) == "<p>" else "<br>", notes).strip()
        notes = re.sub(r"(<br>\s*)+$", "", notes)
        info = reg.tables[label]
        info["title"] = plain(cap)
        body = body.replace("<table>", '<table class="est">')
        body = re.sub(r"<p>@@PANEL@@\s*(.*?)</p>", r'<p class="tab-panel">\1</p>', body, flags=re.S)
        body = re.sub(r"<colgroup>.*?</colgroup>", "", body, flags=re.S)
        body = re.sub(r'<(td|th)([^>]*?) style="text-align: (left|center|right);"', r'<\1\2 class="al-\3"', body)
        if "<thead>" not in body and info.get("n_head") and "<tbody>" in body:
            rows = re.findall(r"<tr[^>]*>.*?</tr>", body, flags=re.S)
            n = min(info["n_head"], len(rows) - 1)
            if n > 0:
                head = "".join(rows[:n]).replace("<td", "<th").replace("</td>", "</th>")
                rest = body.split(rows[n - 1], 1)[1]
                body = body[:body.index("<tbody>")] + "<thead>" + head + "</thead><tbody>" + rest
        if info.get("web"):
            body = "".join(f'<a class="fig-img" href="{s}" target="_blank" rel="noopener"><img src="{s}" alt="{html.escape(plain(cap))}" loading="lazy"></a>' for s in info["web"])
        elif "<table" not in body or "<td" not in body:
            if "<table" in body:
                warn(f"Table {info['number']} ({label}) came out empty. Its body is probably loaded by a macro the script does not follow.")
            body = '<p class="muted small">This table could not be converted. See the PDF.</p>'
        return (
            f'<div class="paper-table" id="{label}">'
            f'<div class="tab-head"><span class="tab-label">Table {info["number"]}</span><span class="tab-title">{cap}</span></div>'
            f'<div class="tab-scroll">{body}</div>'
            + (f'<div class="tab-notes"><span class="notes-label">Notes:</span> {notes}</div>' if notes else "")
            + '<div class="tab-links"></div></div>'
        )
    h = re.sub(r"<p>@@TAB\|([^|]+)\|START@@</p>(.*?)<p>@@TAB\|\1\|BODY@@</p>(.*?)<p>@@TAB\|\1\|NOTES@@</p>(.*?)<p>@@TAB\|\1\|END@@</p>", tab_block, h, flags=re.S)

    # Math: some pandoc versions emit the TeX without delimiters, KaTeX auto-render needs them
    def delim(m):
        kind, body = m.group(1), m.group(2)
        if not body.lstrip().startswith(("\\(", "\\[")):
            body = ("\\(" + body + "\\)") if kind == "inline" else ("\\[" + body + "\\]")
        ident = ""
        if kind == "display":
            by_num = {v: k for k, v in reversed(list(reg.equations.items()))}
            labs = [by_num[t] for t in re.findall(r"\\tag\{([^}]+)\}", body) if t in by_num]
            if labs:
                ident = f' id="{labs[0]}"'
                body = "".join(f'<a id="{x}"></a>' for x in labs[1:]) + body
        return f'<span class="math {kind}"{ident}>{body}</span>'
    h = re.sub(r'<span class="math (inline|display)">(.*?)</span>', delim, h, flags=re.S)

    # Headings: number them as the paper does, remember the numbers for \ref
    numbers, sections = {}, []
    out, pos = [], 0
    in_app = False
    app_pos = h.find("<p>@@APPENDIX@@</p>")
    n1 = {"main": 0, "app": 0}
    cur, cur_num, n2, n3 = None, "", 0, 0
    for m in re.finditer(r"<h([1-4])([^>]*)>(.*?)</h\1>", h, flags=re.S):
        out.append(h[pos:m.start()])
        pos = m.end()
        level, attrs, title = m.group(1), m.group(2), m.group(3)
        hid = (re.search(r'id="([^"]+)"', attrs) or [None, ""])[1]
        unnum = "unnumbered" in attrs
        if app_pos >= 0 and m.start() > app_pos:
            in_app = True
        if level == "1":
            where = "app" if in_app else "main"
            if unnum:
                cur_num = ""
            else:
                n1[where] += 1
                cur_num = str(n1[where]) if where == "main" else (chr(64 + n1[where]) if n1[where] <= 26 else str(n1[where]))
            cur, n2, n3 = hid, 0, 0
            numbers[hid] = cur_num
            sections.append(dict(id=hid, title=plain(title), number=cur_num, where=where))
            out.append(f'<h1 id="{hid}"><span class="sec-num">{cur_num}</span>{title}</h1>')
        elif level == "2":
            num = ""
            if not unnum and cur_num:
                n2 += 1
                n3 = 0
                num = f"{cur_num}.{n2}"
            numbers[hid] = num
            out.append(f'<h2 id="{hid}"><span class="sec-num">{num}</span>{title}</h2>')
        elif level == "3":
            num = ""
            if not unnum and cur_num and n2:
                n3 += 1
                num = f"{cur_num}.{n2}.{n3}"
            numbers[hid] = num
            out.append(f'<h3 id="{hid}"><span class="sec-num">{num}</span>{title}</h3>')
        else:
            out.append(f'<h4 id="{hid}" class="runin">{title}</h4>')
    out.append(h[pos:])
    h = "".join(out).replace("<p>@@APPENDIX@@</p>", "")

    # Cross references
    app_ids = {s["id"] for s in sections if s["where"] == "app"}
    unresolved = set()

    def resolve(target, rtype, text):
        kind, href = None, target
        if target in reg.figures:
            text, kind = reg.figures[target]["number"], "Figure"
        elif target in reg.sublabels:
            href, letter = reg.sublabels[target]
            text, kind = reg.figures[href]["number"] + letter, "Figure"
        elif target in reg.tables:
            text, kind = reg.tables[target]["number"], "Table"
        elif target in reg.equations:
            text, kind = reg.equations[target], "Equation"
            if rtype == "eqref" or rtype.startswith(("ref+", "auto")):
                text = f"({text})"
        elif numbers.get(target):
            text, kind = numbers[target], ("Appendix" if target in app_ids else "Section")
        else:
            unresolved.add(target)
            return f'<a href="#{target}" class="xref unresolved">{text}</a>'
        if rtype.startswith(("ref+", "auto")):
            text = f"{kind} {text}"
        return f'<a href="#{href}" class="xref">{text}</a>'

    def ref_repl(m):
        targets = [t.strip() for t in m.group(1).split(",") if t.strip()]
        out_ = [resolve(t, m.group(2), t if len(targets) > 1 else m.group(3)) for t in targets]
        return out_[0] if len(out_) == 1 else ", ".join(out_[:-1]) + " and " + out_[-1]
    h = re.sub(r'<a href="#([^"]+)" data-reference-type="([^"]+)" data-reference="[^"]*">(.*?)</a>', ref_repl, h, flags=re.S)
    if unresolved:
        warn("unresolved cross references: " + ", ".join(sorted(unresolved)[:20]))

    # Citations -> references page
    missing = {k for c in re.findall(r'<span class="citation"[^>]*>(.*?)</span>', h, flags=re.S) for k in re.findall(r"<strong>([^<?]+)\?</strong>", c)}
    if missing:
        warn("citation keys not found in the .bib file: " + ", ".join(sorted(missing)[:20]))
    h = re.sub(r'<span class="citation" data-cites="([^"]+)">(.*?)</span>',
               lambda m: f'<a class="cite" href="references.html#ref-{m.group(1).split()[0]}" data-cites="{m.group(1)}">{m.group(2)}</a>', h, flags=re.S)

    refs = ""
    rm = re.search(r'<div id="refs" class="references[^"]*"[^>]*>(.*?)</div>\s*(?=<section id="footnotes"|$)', h, flags=re.S)
    if rm:
        refs = rm.group(0)
        h = h.replace(refs, "")
        refs = re.sub(r'<div id="refs"[^>]*>', "", refs, count=1)
        if refs.rstrip().endswith("</div>"):
            refs = refs.rstrip()[:-6]

    # Footnotes -> inline notes
    notes = {}
    fm = re.search(r'<section id="footnotes"[^>]*>(.*?)</section>', h, flags=re.S)
    if fm:
        for chunk in re.split(r'(?=<li id="fn\d+">)', fm.group(1)):
            li = re.match(r'<li id="(fn\d+)">', chunk)
            if not li:
                continue
            body = chunk[li.end():].rsplit("</li>", 1)[0]
            # a note is shown inline, so lists and other blocks inside it become plain lines
            body = re.sub(r"</?(ul|ol|blockquote|div)[^>]*>", "", body)
            body = re.sub(r"<li[^>]*>", '<span class="fn-p">• ', body).replace("</li>", "</span>")
            body = re.sub(r'<a href="#fnref\d+" class="footnote-back"[^>]*>.*?</a>', "", body)
            body = body.replace("<p>", '<span class="fn-p">').replace("</p>", "</span>")
            notes[li.group(1)] = body.strip()
        h = h.replace(fm.group(0), "")

    def fn_repl(m):
        fid, n = m.group(1), m.group(2)
        return (f'<span class="fn"><button type="button" class="fn-ref" aria-expanded="false" aria-controls="{fid}" title="Show note {n}">{n}</button>'
                f'<span class="fn-body" id="{fid}" hidden><span class="fn-num">{n}</span> {notes.get(fid, "")}</span></span>')
    h = re.sub(r'<a href="#(fn\d+)" class="footnote-ref" id="fnref\d+" role="doc-noteref"><sup>(\d+)</sup></a>', fn_repl, h)
    return h, refs, sections


def assign_pages(h, sections, cfg):
    """Split the HTML at <h1> and give every section a page. Returns (pages, bodies, anchors)."""
    st = cfg["structure"]
    reserved = {"index", "references"} | {p["slug"] for p in cfg["pages"]}
    skip = {s.lower() for s in st["skip_sections"]} | {"references", "bibliography"}
    by_id = {s["id"]: s for s in sections}
    pages, bodies, anchors, used = [], {}, {}, set()
    cfg["_page_ids"] = {}
    for c in re.split(r'(?=<h1 id=")', h):
        m = re.match(r'<h1 id="([^"]*)"', c)
        if not m:
            if plain(c):
                warn("text before the first section was left out: " + plain(c)[:80])
            continue
        sec = by_id[m.group(1)]
        if sec["id"].lower() in skip or sec["title"].lower() in skip:
            continue
        if sec["where"] == "app" and st["appendix_pages"] == "single":
            slug = "appendix"
        else:
            slug = st["slugs"].get(sec["id"]) or slugify(sec["title"])
            if sec["where"] == "app" and not slug.startswith("appendix"):
                slug = "appendix-" + slug
            base, k = slug, 2
            while slug in used or slug in reserved:
                slug = f"{base}-{k}"
                k += 1
        if slug not in used:
            used.add(slug)
            cfg["_page_ids"][slug] = sec["id"]
            single = sec["where"] == "app" and st["appendix_pages"] == "single"
            title = "Appendix" if single else sec["title"]
            title = st["nav_titles"].get(sec["id"]) or st["nav_titles"].get(slug) or title
            pages.append(dict(slug=slug, title=title, group="paper", num="" if single else sec["number"]))
            bodies[slug] = ""
        bodies[slug] += c
        for a in re.findall(r' id="([^"]+)"', c):
            anchors[a] = slug
    return pages, bodies, anchors


def pin_slugs(cfg):
    """Write each new section's page address into site.json, so a later change of title does not move the page."""
    new = {sid: slug for slug, sid in cfg["_page_ids"].items() if slug != "appendix" and sid not in cfg["structure"]["slugs"]}
    if not new or not cfg.get("pin_addresses", True):
        return
    path = cfg["_path"]
    raw = json.loads(read(path))
    raw.setdefault("structure", {}).setdefault("slugs", {}).update(new)
    path.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"pinned {len(new)} page address(es) in {path.name} (structure.slugs)")


REDIRECT = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Moved</title>
<meta http-equiv="refresh" content="0; url={to}"><link rel="canonical" href="{to}">
<meta name="robots" content="noindex"></head>
<body><p>This page has moved to <a href="{to}">{to}</a>.</p>
<script>location.replace("{to}" + location.hash);</script></body></html>
"""


def fix_links(h, anchors, this_slug):
    def repl(m):
        slug = anchors.get(m.group(1))
        if slug is None or slug == this_slug:
            return m.group(0)
        return f'<a href="{slug}.html#{m.group(1)}"'
    return re.sub(r'<a href="#([^"]+)"', repl, h)


# ---------------------------------------------------------------------------
# Figures: copy the paper's images into the site
# ---------------------------------------------------------------------------
def stage_images(cfg, reg, out):
    figdir = out / "figures"
    figdir.mkdir(exist_ok=True)
    base = cfg["_main_tex"].parent
    dirs = [base] + [base / g for g in reg.graphicspath] + cfg["_figure_dirs"]
    dirs += [d2 for d in reg.extra_dirs for d2 in [d] + [d / g for g in reg.graphicspath]]
    taken = {}

    def stage(ref):
        ref = ref.strip()
        src = None
        for d in dirs:
            p = d / ref
            for cand in ([p] if p.suffix else []) + [p.with_name(p.name + ext) for ext in (".pdf", ".png", ".jpg", ".jpeg", ".svg", ".eps")]:
                if cand.is_file():
                    src = cand
                    break
            if src:
                break
        if not src:
            warn(f"figure file not found: {ref}")
            return None
        stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", src.stem)
        if taken.get(stem, src) != src:
            stem += "_" + hashlib.md5(str(src).encode()).hexdigest()[:6]
        taken[stem] = src
        ext = src.suffix.lower()
        if ext in (".png", ".jpg", ".jpeg", ".svg"):
            dst = figdir / (stem + ext)
            if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
                shutil.copy2(src, dst)
            return "figures/" + dst.name
        dst = figdir / (stem + ".png")
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            return "figures/" + dst.name
        if ext == ".pdf" and shutil.which("pdftoppm"):
            subprocess.run(["pdftoppm", "-png", "-r", "200", "-singlefile", str(src), str(dst.with_suffix(""))], capture_output=True)
        elif ext == ".pdf" and shutil.which("sips"):
            subprocess.run(["sips", "-s", "format", "png", str(src), "--out", str(dst)], capture_output=True)
        elif shutil.which("magick"):
            subprocess.run(["magick", "-density", "200", str(src), str(dst)], capture_output=True)
        if dst.exists():
            return "figures/" + dst.name
        # a PNG with the same name next to the PDF is a fine substitute
        alt = src.with_suffix(".png")
        if alt.is_file():
            shutil.copy2(alt, dst)
            return "figures/" + dst.name
        warn(f"could not convert {src.name} to PNG (install poppler for pdftoppm)")
        return None

    for info in list(reg.figures.values()) + list(reg.tables.values()):
        info["web"] = [w for w in (stage(i) for i in info.get("images", [])) if w]


# ---------------------------------------------------------------------------
# 6. Site shell
# ---------------------------------------------------------------------------
def mix(hex_, other, t):
    a = [int(hex_.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(other.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def theme_head(cfg):
    th = cfg["theme"]
    scheme = SCHEMES.get(th.get("scheme") or "signature")
    if scheme is None:
        warn(f"theme.scheme {th.get('scheme')!r} is not known, using signature")
        scheme = SCHEMES["signature"]
    name = th.get("accent") or scheme["accent"]
    accent = ACCENTS.get(name, name)
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
        warn(f"theme.accent {name!r} is not a preset or a #rrggbb colour, using the scheme's accent")
        accent = ACCENTS[scheme["accent"]]
    ui, serif, mono, families = TYPEFACES.get(th.get("typeface") or scheme["typeface"], TYPEFACES[scheme["typeface"]])
    fonts = ""
    if families:
        fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                 f'<link href="https://fonts.googleapis.com/css2?{families}&display=swap" rel="stylesheet">\n')
    tokens = lambda d: "".join(f"--{k}:{v};" for k, v in d.items())
    light = tokens(scheme["light"]) + f"--accent:{accent};--accent-ink:{mix(accent, '#000000', .22)};"
    dark = tokens(scheme["dark"]) + f"--accent:{mix(accent, '#ffffff', .15)};--accent-ink:{mix(accent, '#ffffff', .45)};"
    css = (f":root{{{light}"
           f"--font-ui:{ui},system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;"
           f"--font-serif:{serif},Georgia,'Times New Roman',serif;"
           f"--font-mono:{mono},ui-monospace,'SF Mono',Menlo,Consolas,monospace}}")
    if th.get("dark_mode", True):
        css += f"@media (prefers-color-scheme: dark){{:root:not([data-theme=light]){{{dark}}}}}:root[data-theme=dark]{{{dark}}}"
    boot = ('<script>(function(){try{var t=localStorage.getItem("site-theme");if(t)document.documentElement.setAttribute("data-theme",t)}catch(e){}})()</script>\n'
            if th.get("dark_mode", True) else '<script>document.documentElement.setAttribute("data-theme","light")</script>\n')
    return fonts + boot + f"<style>{css}</style>"


def site_accent(cfg):
    th = cfg["theme"]
    scheme = SCHEMES.get(th.get("scheme") or "signature", SCHEMES["signature"])
    name = th.get("accent") or scheme["accent"]
    return ACCENTS.get(name, name)


class Site:
    def __init__(self, cfg, pages):
        self.cfg = cfg
        self.pages = pages
        self.short = cfg["short_title"] or cfg["title"]
        self.pdf = ("paper/" + cfg["_pdf"].name) if cfg["_pdf"] else ""
        self.build = datetime.date.today().isoformat()
        self.paper_date, self.commit = paper_version(cfg)
        self.version_line = f"Paper version {self.paper_date}" + (f" ({self.commit})" if self.commit and cfg.get("show_commit", True) else "")

    def nav(self, active):
        items = []
        groups = [("paper", None)] + [(k, v) for k, v in self.cfg["groups"].items()]
        for group, title in groups:
            members = [p for p in self.pages if p["group"] == group]
            if title and members:
                items.append(f'<li class="nav-group">{html.escape(title)}</li>')
            for p in members:
                cls = ' class="active"' if p["slug"] == active else ""
                items.append(f'<li{cls}><a href="{p["slug"]}.html"><span class="nav-num">{p["num"]}</span><span>{html.escape(p["title"])}</span></a></li>')
        return '<ul class="nav-list">' + "".join(items) + "</ul>"

    def prev_next(self, active):
        slugs = [p["slug"] for p in self.pages]
        i = slugs.index(active)
        parts = []
        if i > 0:
            p = self.pages[i - 1]
            parts.append(f'<a class="pn prev" href="{p["slug"]}.html"><span class="pn-dir">Previous</span><span class="pn-title">{html.escape(p["title"])}</span></a>')
        else:
            parts.append("<span></span>")
        if i < len(self.pages) - 1:
            p = self.pages[i + 1]
            parts.append(f'<a class="pn next" href="{p["slug"]}.html"><span class="pn-dir">Next</span><span class="pn-title">{html.escape(p["title"])}</span></a>')
        return '<nav class="prevnext">' + "".join(parts) + "</nav>"

    def outline(self, body):
        if not self.cfg["features"]["outline"]:
            return ""
        heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, flags=re.S)
        if len(heads) < 2:
            return ""
        items = "".join(f'<li><a href="#{i}">{html.escape(plain(t.replace("</span>", " </span>")))}</a></li>' for i, t in heads)
        return f'<nav class="outline" aria-label="On this page"><div class="outline-title">On this page</div><ul>{items}</ul></nav>'

    def byline(self):
        out = []
        for a in self.cfg["authors"]:
            nm = html.escape(a.get("name", ""))
            if a.get("url"):
                nm = f'<a href="{html.escape(a["url"])}" target="_blank" rel="noopener">{nm}</a>'
            out.append(f'<div><div class="name">{nm}</div><div class="affil">{html.escape(a.get("affiliation", ""))}</div></div>')
        return '<div class="byline">' + "".join(out) + "</div>"

    def meta(self, slug, title, desc):
        c = self.cfg
        url = (c["site_url"].rstrip("/") + "/") if c["site_url"] else ""
        tags = [f'<meta property="og:title" content="{html.escape(title)}">',
                f'<meta property="og:description" content="{html.escape(desc)}">',
                '<meta property="og:type" content="article">',
                f'<meta name="generator" content="paper-website skill. {html.escape(CREDIT_TEXT)}">']
        if url:
            tags.append(f'<meta property="og:url" content="{url}{"" if slug == "index" else slug + ".html"}">')
            tags.append(f'<link rel="canonical" href="{url}{"" if slug == "index" else slug + ".html"}">')
            if c["social_image"]:
                tags.append(f'<meta property="og:image" content="{url}{c["social_image"]}">')
        if slug == "index":
            full = full_title(c)
            tags.append(f'<meta name="citation_title" content="{html.escape(full)}">')
            tags += [f'<meta name="citation_author" content="{html.escape(a.get("name", ""))}">' for a in c["authors"]]
            date = c["date"] or str(c["year"] or datetime.date.today().year)
            tags.append(f'<meta name="citation_publication_date" content="{html.escape(date)}">')
            if url and self.pdf:
                tags.append(f'<meta name="citation_pdf_url" content="{url}{self.pdf}">')
        return "\n".join(tags)

    def shell(self, slug, title, body, scripts=(), wide=False, description="", head=""):
        c = self.cfg
        f = c["features"]
        page_title = self.short if slug == "index" else f"{title} · {self.short}"
        authors = ", ".join(a.get("name", "") for a in c["authors"])
        desc = description or c["description"] or f"Digital edition of the paper {c['title']}" + (f", by {authors}" if authors else "") + "."
        links = []
        if c["bug_report_url"]:
            sep = "&" if "?" in c["bug_report_url"] else "?"
            bug = c["bug_report_url"] + (sep + "title=" + urllib.parse.quote(f"Website: {title}") if "github.com" in c["bug_report_url"] else "")
            links.append(f'<a href="{bug}" target="_blank" rel="noopener">Report a problem</a>')
        links += [f'<a href="{html.escape(l["url"])}" target="_blank" rel="noopener">{html.escape(l["label"])} ↗</a>' for l in c["links"]]
        if self.pdf:
            links.append(f'<a href="{self.pdf}" target="_blank" rel="noopener">PDF ↗</a>')
        search = ('<div class="search" id="search"><input type="search" id="search-input" placeholder="Search the paper" aria-label="Search the paper" autocomplete="off">'
                  '<div class="search-results" id="search-results" hidden></div></div>') if f["search"] else ""
        toggle = '<button type="button" class="theme-toggle" id="theme-toggle" aria-label="Switch between light and dark" title="Light / dark">◐</button>' if c["theme"].get("dark_mode", True) else ""
        slugs = {p["slug"] for p in self.pages}
        foot_links = [f'<a href="{s}.html">{html.escape(next(p["title"] for p in self.pages if p["slug"] == s))}</a>' for s in ("about", "errata", "faq") if s in slugs]
        if self.pdf:
            foot_links.append(f'<a href="{self.pdf}" target="_blank" rel="noopener">PDF</a>')
        who = "; ".join(a.get("name", "") + (", " + a["affiliation"] if a.get("affiliation") else "") for a in c["authors"])
        footer = (f"<p>{html.escape(who)}.</p>" if who else "") + "".join(f"<p>{p}</p>" for p in c["footer"])
        script_tags = "".join(f'<script src="{s}"></script>' for s in scripts)
        return f"""<!doctype html>
<!-- Built with the paper-website skill.
     {CREDIT_TEXT} -->
<html lang="{c['language']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page_title)}</title>
<meta name="description" content="{html.escape(desc)}">
{self.meta(slug, page_title, desc)}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.11/katex.min.css">
<link rel="stylesheet" href="assets/site.css">
{theme_head(c)}
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
{head}
</head>
<body class="{'wide' if wide else ''}" data-page="{slug}">
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <button class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="sidebar"><span class="burger">☰</span> Contents</button>
  <a class="site-title" href="index.html">{html.escape(self.short)}</a>
  {search}
  <nav class="top-links">
    {"".join(links)}
  </nav>
  {toggle}
</header>
<div class="layout">
<aside class="sidebar" id="sidebar">
  <div class="sidebar-inner">
    <a class="sidebar-title" href="index.html">{html.escape(c['title'])}</a>
    {self.nav(slug)}
    <div class="sidebar-foot">{html.escape(c['edition'])}<br>{html.escape(self.version_line)}<br>Site built {self.build}{"<br>The PDF is the version of record." if self.pdf else ""}</div>
  </div>
</aside>
<main id="main" class="main">
{self.outline(body) if not wide else ""}
<article class="read">
{body}
{self.prev_next(slug)}
</article>
<footer class="site-foot">
  {footer}
  <p>{" · ".join(foot_links)}</p>
  <p class="credit">Built with <a href="{CREDIT_URL}" target="_blank" rel="noopener">AI tools for research</a> (Bäckman, 2026).</p>
</footer>
</main>
</div>
<script>window.SITE = {json.dumps({"features": f, "page": slug})};</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.11/katex.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.11/contrib/auto-render.min.js"></script>
{'<script src="data/meta.js"></script>' if f["previews"] else ""}
<script src="assets/site.js"></script>
{script_tags}
</body>
</html>
"""


def paper_version(cfg):
    """Date of the paper's source and the commit it was built from, for the version line."""
    tdir = cfg["_main_tex"].parent
    files = [cfg["_main_tex"]] + [f for f in tdir.glob("*.tex")] + cfg["_appendix_tex"]
    date = datetime.date.fromtimestamp(max(f.stat().st_mtime for f in files)).isoformat()
    commit = ""
    try:
        r = subprocess.run(["git", "-C", str(tdir), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
        if r.returncode == 0:
            commit = r.stdout.strip()
            d = subprocess.run(["git", "-C", str(tdir), "status", "--porcelain", "--", "."], capture_output=True, text=True)
            if d.stdout.strip():
                commit += ", with uncommitted changes"
    except OSError:
        pass
    return date, commit


def template_version():
    f = HERE / "VERSION"
    return read(f).strip() if f.exists() else "unknown"


def full_title(cfg):
    t, sub = cfg["title"], cfg["subtitle"]
    return t + ((" " if t.rstrip().endswith(("?", "!")) else ": ") + sub if sub else "")


def citation(cfg):
    c = cfg["citation"]
    authors = [a.get("name", "") for a in cfg["authors"]]
    year = str(cfg["year"] or datetime.date.today().year)
    full = full_title(cfg)
    text = c.get("text")
    if not text:
        def inv(n):
            parts = n.split()
            return f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else n
        names = authors[:1] and [inv(authors[0])] + authors[1:]
        who = names[0] if len(names) == 1 else (", ".join(names[:-1]) + ", and " + names[-1]) if names else ""
        affil = cfg["authors"][0].get("affiliation", "") if len(cfg["authors"]) == 1 else ""
        text = f"{who}. {year}. \u201c{full}.\u201d {(cfg['status'] or 'working paper').capitalize()}" + (f", {affil}." if affil else ".")
    bib = c.get("bibtex")
    if not bib:
        key = slugify(authors[0].split()[-1] if authors else "paper") + year + slugify(cfg["title"]).split("-")[0]
        note = (cfg["status"] or "working paper").capitalize() + (". " + cfg["site_url"] if cfg["site_url"] else "")
        bib = ("@unpublished{" + key + ",\n  author = {" + " and ".join(authors) + "},\n  title  = {" + full + "},\n  year   = {" + year
               + "},\n  note   = {" + note + "}\n}")
    return text, bib


def cite_box(cfg):
    if not cfg["features"]["cite_box"]:
        return ""
    text, bib = citation(cfg)
    return ('<div class="citebox"><h2>Cite this paper</h2>'
            f'<p class="cite-text" id="cite-text">{html.escape(text)}</p>'
            f'<pre id="cite-bib">{html.escape(bib)}</pre>'
            '<p><button type="button" class="pill" data-copy="cite-text">Copy citation</button> '
            '<button type="button" class="pill" data-copy="cite-bib">Copy BibTeX</button> <span class="copied small muted" aria-live="polite"></span></p></div>')


def search_index(bodies, pages):
    """One entry per h1/h2 block: page, anchor, heading, plain text."""
    titles = {p["slug"]: p["title"] for p in pages}
    idx = []
    for slug, body in bodies.items():
        body = re.sub(r"<table.*?</table>", " ", body, flags=re.S)
        body = re.sub(r'<span class="math[^>]*>.*?</span>', " ", body, flags=re.S)
        body = re.sub(r'<button[^>]*class="fn-ref".*?</button>', " ", body, flags=re.S)
        body = re.sub(r'<nav class="prevnext">.*?</nav>', " ", body, flags=re.S)
        for chunk in re.split(r"(?=<h[12][ >])", body):
            m = re.match(r'<h[12](?: id="([^"]*)")?[^>]*>(.*?)</h[12]>', chunk, flags=re.S)
            text = plain(chunk[m.end():] if m else chunk)
            if not text:
                continue
            idx.append({"p": slug, "pt": titles.get(slug, ""), "a": m.group(1) if m and m.group(1) else "",
                        "h": plain(m.group(2).replace("</span>", " </span>")) if m else titles.get(slug, ""), "t": text})
    return idx


def js_file(path, name, obj):
    path.write_text(f"window.{name} = " + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


# ---------------------------------------------------------------------------
def load_config(path):
    cfg = merge(DEFAULTS, json.loads(read(path)))
    base = path.parent

    def P(x):
        return (base / x).resolve()
    if not cfg["main_tex"]:
        raise SystemExit("site.json: main_tex is required (the paper's root .tex file).")
    cfg["_base"] = base
    cfg["_path"] = path
    cfg["_main_tex"] = P(cfg["main_tex"])
    if not cfg["_main_tex"].is_file():
        raise SystemExit(f"main_tex not found: {cfg['_main_tex']}")
    cfg["_out"] = P(cfg["output_dir"])
    cfg["_pdf"] = P(cfg["pdf"]) if cfg["pdf"] else None
    if cfg["_pdf"] and not cfg["_pdf"].is_file():
        warn(f"pdf not found: {cfg['_pdf']}")
        cfg["_pdf"] = None
    cfg["_figure_dirs"] = [P(d) for d in cfg["figure_dirs"]]
    atex = cfg["appendix_tex"] if isinstance(cfg["appendix_tex"], list) else [cfg["appendix_tex"]]
    cfg["_appendix_tex"] = [P(a) for a in atex if a]
    for a in cfg["_appendix_tex"]:
        if not a.is_file():
            raise SystemExit(f"appendix_tex not found: {a}")
    cfg["_csl"] = P(cfg["csl"]) if cfg["csl"] else HERE / "theme" / "chicago-author-date.csl"
    bib = cfg["bib"] if isinstance(cfg["bib"], list) else [cfg["bib"]]
    cfg["_bib"] = [P(b) for b in bib if b]
    return cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "site.json"))
    args = ap.parse_args()
    cfg = load_config(Path(args.config).resolve())
    out = cfg["_out"]
    content = cfg["_base"] / "content"

    reg = Registry()
    tex = preprocess(cfg, reg)
    if not cfg["_bib"]:
        tdir = cfg["_main_tex"].parent
        for b in reg.bib_from_tex:
            for cand in (tdir / b, tdir / (b + ".bib")):
                if cand.is_file():
                    cfg["_bib"].append(cand)
                    break
        if not cfg["_bib"]:
            warn("no .bib file found. Citations will show as keys and there is no references page. Set \"bib\" in site.json.")
    (cfg["_base"] / "_preprocessed.tex").write_text(tex, encoding="utf-8")

    for d in ("assets", "data", "figures"):
        (out / d).mkdir(parents=True, exist_ok=True)
    stage_images(cfg, reg, out)

    h = run_pandoc(tex, cfg, reg)
    (cfg["_base"] / "_pandoc.html").write_text(h, encoding="utf-8")
    h, refs, sections = postprocess(h, cfg, reg)
    paper_pages, bodies, anchors = assign_pages(h, sections, cfg)
    anchors.update({k: "references" for k in re.findall(r' id="(ref-[^"]+)"', refs)})
    pin_slugs(cfg)

    # data (tier 1 and 2), before any page is written so a refused source leaves the old site intact
    tier = int(cfg["data"].get("tier", 0))
    data_files = ""
    import site_data
    if tier >= 1:
        data_files = site_data.build(cfg, reg, out, warn)
    else:
        site_data.prune(out)

    # page registry: title page, main sections, references, appendix, hand-written pages
    extra = [dict(slug=p["slug"], title=p["title"], group=p.get("group", "notes"), num="") for p in cfg["pages"]]
    if tier >= 2 and cfg["data"].get("explorer") and not any(p["slug"] == "explorer" for p in extra):
        extra.insert(0, dict(slug="explorer", title=cfg["data"]["explorer"].get("title", "Results explorer"), group="explore", num=""))
    main_pages = [p for p in paper_pages if not p["slug"].startswith("appendix")]
    app_pages = [p for p in paper_pages if p["slug"].startswith("appendix")]
    pages = [dict(slug="index", title="Title and abstract", group="paper", num="")] + main_pages
    if refs.strip():
        pages.append(dict(slug="references", title="References", group="paper", num=""))
    pages += app_pages + extra
    site = Site(cfg, pages)

    # theme assets and the PDF
    for f in (HERE / "theme").iterdir():
        if f.suffix in (".css", ".js", ".svg", ".png", ".ico", ".woff2"):
            shutil.copy2(f, out / "assets" / f.name)
    accent = site_accent(cfg)
    fav = out / "assets" / "favicon.svg"
    if fav.exists() and re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
        fav.write_text(read(fav).replace("#1e88e5", accent), encoding="utf-8")
    if cfg["_pdf"]:
        (out / "paper").mkdir(exist_ok=True)
        shutil.copy2(cfg["_pdf"], out / "paper" / cfg["_pdf"].name)

    fig_scripts = ["https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js", "data/figures.js", "assets/charts.js", "assets/figures.js"] if tier >= 1 else []
    written = []
    for p in paper_pages:
        body = fix_links(bodies[p["slug"]], anchors, p["slug"])
        bodies[p["slug"]] = body
        (out / f"{p['slug']}.html").write_text(site.shell(p["slug"], p["title"], body, scripts=fig_scripts), encoding="utf-8")
        written.append(p["slug"])
    if refs.strip():
        refs_body = f'<h1><span class="sec-num"></span>References</h1><div class="references csl-bib-body hanging-indent">{refs}</div>'
        (out / "references.html").write_text(site.shell("references", "References", refs_body), encoding="utf-8")
        written.append("references")

    # hand-written pages
    f0 = reg.front
    abs_html = cfg["abstract"] or (strip_p(run_pandoc(f0["abstract"], cfg, reg, cite=False)) if f0["abstract"] else "")
    first = main_pages[0] if main_pages else None
    abs_html = re.sub(r'<span class="math (inline|display)">(.*?)</span>',
                      lambda m: m.group(0) if m.group(2).lstrip().startswith(("\\(", "\\[")) else
                      f'<span class="math {m.group(1)}">' + ("\\(" + m.group(2) + "\\)" if m.group(1) == "inline" else "\\[" + m.group(2) + "\\]") + "</span>",
                      abs_html, flags=re.S)
    ack = cfg["acknowledgments"]          # "" = take the \thanks note of the title, false = show none
    if ack == "":
        ack = strip_p(run_pandoc(f0["thanks"], cfg, reg)).replace("</p>\n<p>", "<br><br>") if f0.get("thanks") else ""
    ack = ack or ""
    tokens = {
        "@@TITLE@@": html.escape(cfg["title"]), "@@SUBTITLE@@": html.escape(cfg["subtitle"]),
        "@@EDITION@@": html.escape(cfg["edition"] + (" · " + cfg["status"] if cfg["status"] else "")),
        "@@BYLINE@@": site.byline(), "@@ABSTRACT@@": abs_html,
        "@@JEL@@": html.escape(cfg["jel"] or f0["jel"]), "@@KEYWORDS@@": html.escape(cfg["keywords"] or f0["keywords"]),
        "@@ACKNOWLEDGMENTS@@": ack, "@@CITE_BOX@@": cite_box(cfg),
        "@@CITE_TEXT@@": html.escape(citation(cfg)[0]), "@@CITE_BIBTEX@@": html.escape(citation(cfg)[1]),
        "@@SITE_URL@@": (cfg["site_url"].rstrip("/") + "/") if cfg["site_url"] else "",
        "@@PDF@@": site.pdf, "@@CREDIT@@": html.escape(CREDIT_TEXT).replace(CREDIT_URL, f'<a href="{CREDIT_URL}" target="_blank" rel="noopener">{CREDIT_URL}</a>'),
        "@@FIRST_PAGE@@": (first["slug"] + ".html") if first else "#",
        "@@FIRST_TITLE@@": html.escape(first["title"]) if first else "",
        "@@BUILD_DATE@@": site.build, "@@PAPER_VERSION@@": html.escape(site.version_line),
    }
    hand = [dict(slug="index", title="Title and abstract")] + extra
    pending = []
    for p in hand:
        f = content / f"{p['slug']}.html"
        if not f.exists():
            warn(f"content/{p['slug']}.html is missing, the page was not written")
            continue
        meta = json.loads(read(content / f"{p['slug']}.json")) if (content / f"{p['slug']}.json").exists() else {}
        pending.append((p, read(f), meta))

    tokens["@@DATA_FILES@@"] = data_files or '<p class="small muted">This site carries no data files.</p>'

    for p, body, meta in pending:
        for k, v in tokens.items():
            body = body.replace(k, v)
        body = re.sub(r"<!--IF (\w+)-->(.*?)<!--END-->", lambda m: m.group(2) if tokens.get(f"@@{m.group(1)}@@") else "", body, flags=re.S)
        if p["slug"] == "index":
            body += f'\n<p class="credit-full">This site was built with the paper-website skill. Please cite it as: {tokens["@@CREDIT@@"]}</p>'
        body = fix_links(body, anchors, p["slug"])
        bodies[p["slug"]] = body
        (out / f"{p['slug']}.html").write_text(
            site.shell(p["slug"], p["title"], body, scripts=meta.get("scripts", []), wide=meta.get("wide", False),
                       description=meta.get("description", ""), head=meta.get("head", "")), encoding="utf-8")
        written.append(p["slug"])

    # hover previews and search
    if cfg["features"]["previews"]:
        ref_map = {k: v.strip() for k, v in re.findall(r'<div id="ref-([^"]+)"[^>]*>(.*?)</div>\s*(?=<div id="ref-|$)', refs, flags=re.S)}
        x = {k: {"k": "Figure", "n": v["number"], "t": v.get("title", ""), "i": (v.get("web") or [""])[0]} for k, v in reg.figures.items()}
        x.update({k: {"k": "Table", "n": v["number"], "t": v.get("title", "")} for k, v in reg.tables.items()})
        js_file(out / "data" / "meta.js", "SITE_META", {"refs": ref_map, "xrefs": x})
    if cfg["features"]["search"]:
        js_file(out / "data" / "search.js", "SITE_SEARCH", search_index(bodies, pages))

    # registry. A page a previous build wrote and this one does not becomes a redirect to where its section went
    regfile = out / "data" / "registry.json"
    redirects = {}
    if regfile.exists():
        try:
            old = json.loads(read(regfile))
            redirects = {k: v for k, v in old.get("redirects", {}).items() if k not in written}
            for slug in old.get("pages", []):
                if slug in written:
                    continue
                sid = old.get("sections", {}).get(slug)
                redirects[slug] = anchors.get(sid, "index") if sid else "index"
        except (ValueError, OSError):
            pass
    redirects = {k: (v if v in written else "index") for k, v in redirects.items()}
    for slug, to in redirects.items():
        (out / f"{slug}.html").write_text(REDIRECT.format(to=to + ".html"), encoding="utf-8")
        print(f"redirect: {slug}.html -> {to}.html")
    regfile.write_text(json.dumps(
        {"site_title": cfg["title"], "template_version": template_version(), "built": site.build,
         "paper_date": site.paper_date, "commit": site.commit,
         "pages": written, "nav": pages, "sections": cfg["_page_ids"], "redirects": redirects,
         "figures": {k: {"number": v["number"], "images": v.get("web", []), "title": v.get("title", "")} for k, v in reg.figures.items()},
         "tables": {k: {"number": v["number"], "title": v.get("title", "")} for k, v in reg.tables.items()},
         "equations": reg.equations, "anchors": anchors, "credit": CREDIT_TEXT}, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"site written to {out}")
    print("pages:", ", ".join(p["slug"] for p in pages))
    print("figures:", ", ".join(v["number"] for v in reg.figures.values()))
    print("tables:", ", ".join(v["number"] for v in reg.tables.values()))
    print("equations:", len(reg.equations), "labelled")
    print(f"{len(WARNINGS)} warning(s)")


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    main()
