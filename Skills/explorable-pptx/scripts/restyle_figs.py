#!/usr/bin/env python3
"""Recolour the source's PDF figures to the deck's palette, in place.

Usage:
    python3 figs/restyle_figs.py                 # every figs/*.pdf
    python3 figs/restyle_figs.py Fig_Name        # named figures
    python3 figs/restyle_figs.py --keep-series   # leave second-series colours alone
    python3 figs/restyle_figs.py --dry-run       # list the colours in each figure as it is now, change nothing
                                                 # (convert_figs.sh prints the source colours before it recolours)

convert_figs.sh copies the source's PDFs into figs/ with their original
colours. This pass maps those colours onto the deck's tokens so the figures
sit next to the TikZ stages without a palette change. The default MAP covers
Stata's scheme colours, the Okabe-Ito set, matplotlib's tab10 and ggplot2's
default hues: navy becomes ink, maroon and orange become the primary colour,
the blues become greys, and the plot background becomes paper so the figure
has no box. Edit MAP for other sources; the script lists every colour it
left alone. Text is untouched, and the mapping is idempotent.

Colour never marks a quantity that is not one of the deck's four semantic
colours, so nothing here is mapped onto contrast, actor-a or actor-b: a
figure that needs those is redrawn as a stage.

How it works, with no Python packages: Ghostscript rewrites the PDF with
uncompressed content streams and RGB colours; the script replaces the colour
operators (rg, RG, g, G) in those streams, recomputes each stream's /Length
and the cross-reference table, and writes the result back. A figure that
Ghostscript cannot open is reported and left alone. Needs gs on the PATH
(brew install ghostscript / apt install ghostscript).
"""

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent

# Keep the hex values on the right in step with theme/explorable.sty.
MAP = {
    # matplotlib tab10 (first four) and ggplot2 default hues (first three)
    "#1f77b4": "#1C2224",  # tab:blue           -> ink
    "#2ca02c": "#4B5457",  # tab:green          -> ink-2
    "#d62728": "#C4452A",  # tab:red            -> primary
    "#f8766d": "#C4452A",  # ggplot hue 1       -> primary
    "#00ba38": "#4B5457",  # ggplot hue 2       -> ink-2
    "#619cff": "#667074",  # ggplot hue 3       -> ink-3
    "#ebebeb": "#FFFFFF",  # ggplot panel grey  -> paper
    # Stata schemes and Okabe-Ito
    "#1a476f": "#1C2224",  # Stata navy         -> ink
    "#90353b": "#C4452A",  # Stata maroon       -> primary
    "#f39189": "#C4452A",  # light red reference line -> primary
    "#d55e00": "#C4452A",  # Okabe-Ito orange   -> primary
    "#eaaf80": "#F2D9D2",  # its light fill     -> primary-soft
    "#0072b2": "#667074",  # Okabe-Ito blue     -> ink-3
    "#80b9d9": "#ECECEC",  # its light fill     -> paper-3
    "#a0a0a0": "#8A9195",  # Stata axis grey    -> a cooler grey
    "#000000": "#1C2224",  # black rules        -> ink
    "#1e2d53": "#1C2224",  # Stata dknavy       -> ink
    "#4b5775": "#4B5457",  # its lighter band   -> ink-2
    "#a65d62": "#C4452A",  # Stata dkred band   -> primary
    "#333333": "#1C2224",  # dark grey          -> ink
    "#b3b3b3": "#C9CEC6",  # light grey         -> line
    "#808080": "#8A9195",  # mid grey axes      -> a cooler grey
    "#ffffff": "#FFFFFF",
    "#eaf2f3": "#FFFFFF",  # Stata plotregion tint -> paper, so the figure sits on the slide without a box
}

# Colours that mark a second, third or fourth series in the source. They become
# distinct greys by default so the deck's four semantic colours keep their meaning
# (a multi-series figure whose greys cannot be told apart is redrawn as a stage).
SERIES = {
    "#56b4e9": "#667074",  # Okabe-Ito sky blue     -> ink-3
    "#78c3ed": "#ECECEC",  # its light band         -> paper-3
    "#009e73": "#4B5457",  # Okabe-Ito green        -> ink-2
    "#33b18f": "#E2E5E3",  # its light band
    "#cc79a7": "#8A9195",  # Okabe-Ito pink         -> mid grey
    "#d694b9": "#ECECEC",  # its light band         -> paper-3
    "#e69f00": "#667074",  # Okabe-Ito orange       -> ink-3
    "#ff7f0e": "#667074",  # tab:orange (second series) -> ink-3
    "#9467bd": "#8A9195",  # tab:purple
    "#8c564b": "#4B5457",  # tab:brown
}

NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)"
RGB_OP = re.compile(rf"(?<![\w.])({NUM})\s+({NUM})\s+({NUM})\s+(rg|RG)\b".encode())
GRAY_OP = re.compile(rf"(?<![\w.])({NUM})\s+(g|G)\b".encode())
STREAM_KW = re.compile(rb"(?<![a-z])stream\r?\n")
LENGTH = re.compile(rb"/Length\s+\d+(?:\s+0\s+R)?")


def to_hex(r, g, b):
    return "#%02x%02x%02x" % tuple(min(255, max(0, round(float(v) * 255))) for v in (r, g, b))


def to_ops(hexcol):
    r, g, b = (int(hexcol[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return f"{r:.4f} {g:.4f} {b:.4f}".encode()


def recolour_stream(body, table, unmapped, count):
    def rgb(m):
        key = to_hex(m.group(1), m.group(2), m.group(3))
        if key in table and table[key].lower() != key:
            count[0] += 1
            return to_ops(table[key]) + b" " + m.group(4)
        if key.upper() not in {v.upper() for v in table.values()}:
            unmapped.add(key)
        return m.group(0)

    def gray(m):
        v = m.group(1)
        key = to_hex(v, v, v)
        if key in table and table[key].lower() != key:
            count[0] += 1
            op = b"rg" if m.group(2) == b"g" else b"RG"
            return to_ops(table[key]) + b" " + op
        if key.upper() not in {v.upper() for v in table.values()}:
            unmapped.add(key)
        return m.group(0)

    return GRAY_OP.sub(gray, RGB_OP.sub(rgb, body))


def uncompress(src, dst):
    cmd = ["gs", "-q", "-o", str(dst), "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
           "-dCompressPages=false", "-dCompressFonts=false", "-sColorConversionStrategy=RGB", str(src)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0 and dst.exists()


def dict_start(data, end):
    """Index of the '<<' that opens the dictionary whose '>>' ends at `end`."""
    depth, i = 0, end - 2
    while i >= 2:
        i -= 1
        pair = data[i - 1:i + 1]
        if pair == b">>":
            depth += 1
            i -= 1
        elif pair == b"<<":
            if depth == 0:
                return i - 1
            depth -= 1
            i -= 1
    return None


def stream_length(data, dic):
    """The stream's byte length: a direct /Length, or the integer object an indirect one points at."""
    m = re.search(rb"/Length\s+(\d+)(?:\s+0\s+R)?", dic)
    if not m:
        return None
    if not m.group(0).rstrip().endswith(b"R"):
        return int(m.group(1))
    ref = re.search(rb"(?m)^" + m.group(1) + rb" 0 obj\s*(\d+)\s*endobj", data)
    return int(ref.group(1)) if ref else None


def is_content(body):
    return b"\x00" not in body[:400] and all(b < 128 for b in body[:400]) and re.search(rb"\b(rg|RG|g|G|re|cm)\b", body) is not None


def rewrite(data, table, unmapped, count):
    """Recolour every content stream, write a direct /Length, rebuild the xref table."""
    out = bytearray()
    pos = 0
    for m in STREAM_KW.finditer(data):
        if m.start() < pos:
            continue
        gt = data.rfind(b">>", 0, m.start())
        if gt < 0:
            continue
        ds = dict_start(data, gt + 2)
        if ds is None:
            continue
        dic = data[ds:gt + 2]
        if not LENGTH.search(dic):
            continue
        length = stream_length(data, dic)
        if length is None:
            continue
        body = data[m.end():m.end() + length]
        end = data.find(b"endstream", m.end() + length)
        if end < 0:
            break
        new = recolour_stream(body, table, unmapped, count) if is_content(body) else body
        out += data[pos:ds]
        out += LENGTH.sub(b"/Length " + str(len(new)).encode(), dic, count=1) + b"\nstream\n" + new + b"\n"
        pos = end
    out += data[pos:]
    return rebuild_xref(bytes(out))


def rebuild_xref(data):
    offsets = {}
    for m in re.finditer(rb"(?m)^(\d+) 0 obj\b", data):
        offsets[int(m.group(1))] = m.start()
    trailer = re.search(rb"trailer\s*<<(.*?)>>\s*startxref", data, re.S)
    if not trailer or not offsets:
        return None
    size = max(offsets) + 1
    body_end = data.rfind(b"\nxref") + 1
    body = data[:body_end]
    xref = [b"xref", f"0 {size}".encode(), b"0000000000 65535 f "]
    for n in range(1, size):
        xref.append(f"{offsets[n]:010d} 00000 n ".encode() if n in offsets else b"0000000000 65535 f ")
    tdict = re.sub(rb"/Size\s+\d+", f"/Size {size}".encode(), trailer.group(1))
    return body + b"\n".join(xref) + b"\ntrailer\n<<" + tdict + b">>\nstartxref\n" + str(len(body)).encode() + b"\n%%EOF\n"


def restyle(path, keep_series=False, dry=False):
    table = MAP if keep_series else {**SERIES, **MAP}
    unmapped, count = set(), [0]
    with tempfile.TemporaryDirectory() as tmp:
        flat = pathlib.Path(tmp) / "flat.pdf"
        if not uncompress(path, flat):
            return None, {"ghostscript could not read this file"}
        data = flat.read_bytes()
        if dry:
            seen = set()
            for m in RGB_OP.finditer(data):
                seen.add(to_hex(m.group(1), m.group(2), m.group(3)))
            for m in GRAY_OP.finditer(data):
                seen.add(to_hex(m.group(1), m.group(1), m.group(1)))
            return 0, seen
        new = rewrite(data, table, unmapped, count)
        if new is None:
            return None, {"could not rebuild the file structure; left alone"}
        if count[0]:
            path.write_bytes(new)
    return count[0], unmapped


def main(args):
    keep = "--keep-series" in args
    dry = "--dry-run" in args
    only = {a for a in args if not a.startswith("--")}
    if not shutil.which("gs"):
        sys.exit("gs not found: brew install ghostscript (macOS) or apt install ghostscript")
    for path in sorted(HERE.glob("*.pdf")):
        if only and path.stem not in only:
            continue
        n, extra = restyle(path, keep, dry)
        if n is None:
            print(f"  {'skip':>5}             {path.name}   {', '.join(extra)}")
        elif dry:
            print(f"  colours in {path.name}: {', '.join(sorted(extra))}")
        else:
            flag = f"   unmapped: {', '.join(sorted(extra))}" if extra else ""
            print(f"  {n:>5} recoloured  {path.name}{flag}")


if __name__ == "__main__":
    main(sys.argv[1:])
