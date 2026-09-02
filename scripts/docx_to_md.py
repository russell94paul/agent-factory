"""Convert a .docx to Markdown by parsing word/document.xml directly.

No python-docx in this environment. Preserves heading levels, list nesting,
tables and hyperlinks; drops images (records them as placeholders).

Usage: python scripts/docx_to_md.py <in.docx> <out.md>
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def load_rels(z):
    rels = {}
    try:
        root = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    except KeyError:
        return rels
    for rel in root:
        rels[rel.get("Id")] = rel.get("Target")
    return rels


def run_text(run):
    out = []
    for node in run.iter():
        tag = node.tag
        if tag == W + "t":
            out.append(node.text or "")
        elif tag == W + "tab":
            out.append("\t")
        elif tag == W + "br":
            out.append("\n")
    return "".join(out)


def para_style(p):
    ppr = p.find(W + "pPr")
    if ppr is None:
        return None, None, None
    st = ppr.find(W + "pStyle")
    style = st.get(W + "val") if st is not None else None
    numpr = ppr.find(W + "numPr")
    ilvl = None
    numid = None
    if numpr is not None:
        il = numpr.find(W + "ilvl")
        ni = numpr.find(W + "numId")
        ilvl = int(il.get(W + "val")) if il is not None else 0
        numid = ni.get(W + "val") if ni is not None else None
    return style, ilvl, numid


def inline(p, rels):
    """Render a paragraph's runs with bold/italic and hyperlinks."""
    parts = []
    for child in p:
        if child.tag == W + "hyperlink":
            txt = "".join(run_text(r) for r in child.findall(W + "r"))
            rid = child.get(R + "id")
            target = rels.get(rid) if rid else None
            if txt.strip():
                parts.append("[%s](%s)" % (txt, target) if target else txt)
        elif child.tag == W + "r":
            txt = run_text(child)
            if not txt:
                if child.find(".//" + W + "drawing") is not None or child.find(
                    ".//" + W + "pict"
                ) is not None:
                    parts.append("![image]")
                continue
            rpr = child.find(W + "rPr")
            bold = rpr is not None and rpr.find(W + "b") is not None
            ital = rpr is not None and rpr.find(W + "i") is not None
            core = txt.strip()
            if core and bold and ital:
                txt = txt.replace(core, "***" + core + "***", 1)
            elif core and bold:
                txt = txt.replace(core, "**" + core + "**", 1)
            elif core and ital:
                txt = txt.replace(core, "*" + core + "*", 1)
            parts.append(txt)
    return "".join(parts)


HEAD = re.compile(r"^Heading(\d)$", re.I)


def render_para(p, rels):
    style, ilvl, numid = para_style(p)
    text = inline(p, rels).strip()
    if not text:
        return ""
    if style:
        m = HEAD.match(style)
        if m:
            return "#" * min(int(m.group(1)), 6) + " " + text
        if style.lower() in ("title",):
            return "# " + text
        if style.lower() in ("subtitle",):
            return "## " + text
        if "quote" in style.lower():
            return "> " + text
    if numid is not None:
        return "  " * (ilvl or 0) + "- " + text
    return text


def render_table(tbl, rels):
    rows = []
    for tr in tbl.findall(W + "tr"):
        cells = []
        for tc in tr.findall(W + "tc"):
            txt = " ".join(
                inline(p, rels).strip() for p in tc.findall(W + "p")
            ).strip()
            cells.append(txt.replace("|", "\\|") or " ")
        rows.append(cells)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [" "] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |"]
    out.append("|" + "|".join([" --- "] * width) + "|")
    for r in rows[1:]:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def convert(path):
    z = zipfile.ZipFile(path)
    rels = load_rels(z)
    root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    lines = []
    for child in body:
        if child.tag == W + "p":
            lines.append(render_para(child, rels))
        elif child.tag == W + "tbl":
            lines.append("")
            lines.append(render_table(child, rels))
            lines.append("")
    out = []
    blank = False
    for ln in lines:
        if ln == "":
            if blank:
                continue
            blank = True
        else:
            blank = False
        out.append(ln)
    return "\n".join(out).strip() + "\n"


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    md = convert(src)
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(md)
    print("%s -> %s  (%d chars, %d lines)" % (src, dst, len(md), md.count("\n") + 1))
