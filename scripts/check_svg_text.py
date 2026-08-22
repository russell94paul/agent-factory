"""Collision check for SVG text — every pair, not just the row you were thinking about.

    python scripts/check_svg_text.py                       # all figures in the artifact
    python scripts/check_svg_text.py --figure last-write   # one

Exists because a purpose-built geometry checker reported the last-write-wins figure clean while it
had THREE text collisions in it, visible to anyone who opened the page. That checker verified the
counts row — the row I happened to be worried about — and nothing else. A check that only looks
where you already suspect a problem is a check that confirms your priors.

Approximates text extents from the class-level font sizes in the artifact's own CSS, so it is a
screen for gross overlap rather than a substitute for looking. It cannot see line wrapping, font
fallback, or anything that happens at paint time. See F1 in the living-systems-ui quality gates:
this does not replace opening the page.
"""
from __future__ import annotations

import pathlib
import re
import sys

ART = pathlib.Path(__file__).resolve().parent.parent / "docs" / "artifacts" / "agent-factory.html"

# (font-size px, average advance px) per text class, read off the stylesheet.
SIZE = {"lbl": (10.5, 6.3), "num": (29, 17.5), "lbl2": (14, 7.0), "key": (12.5, 6.1),
        "cnt": (11.5, 6.4), "ck": (11, 6.2), "cv": (15, 9.0), "cn": (10.5, 5.9),
        "code": (13, 7.3), "ret": (13, 7.3), "ret2": (13, 7.3), "foot": (13.5, 6.8)}
DEFAULT = (12.0, 6.5)

ENT = {"&quot;": '"', "&#8594;": ">", "&#183;": ".", "&#8593;": "^", "&mdash;": "-", "&amp;": "&"}


def boxes(frag: str):
    out = []
    for m in re.finditer(r'<text class="([\w -]+)"[^>]*\bx="([-\d.]+)"[^>]*\by="([-\d.]+)"([^>]*)>(.*?)</text>',
                         frag, re.S):
        cls = m.group(1).split()[0]
        x, y, attrs, raw = float(m.group(2)), float(m.group(3)), m.group(4), m.group(5)
        plain = re.sub(r"<[^>]+>", "", raw)
        for k, v in ENT.items():
            plain = plain.replace(k, v)
        fs, cw = SIZE.get(cls, DEFAULT)
        w = len(plain) * cw
        x0 = x - w if 'text-anchor="end"' in attrs else (
             x - w / 2 if 'text-anchor="middle"' in attrs else x)
        out.append({"cls": cls, "x0": x0, "x1": x0 + w,
                    "y0": y - fs * .78, "y1": y + fs * .22, "t": plain.strip()})
    return out


def check(frag: str, name: str) -> int:
    bad = 0
    bs = boxes(frag)
    for i in range(len(bs)):
        for j in range(i + 1, len(bs)):
            a, b = bs[i], bs[j]
            if a["x0"] < b["x1"] and b["x0"] < a["x1"] and a["y0"] < b["y1"] and b["y0"] < a["y1"]:
                print(f"  OVERLAP  {a['cls']:5} {a['t'][:38]!r}")
                print(f"           {b['cls']:5} {b['t'][:38]!r}")
                bad += 1
    vb = re.search(r'viewBox="([-\d\s.]+)"', frag)
    if vb and bs:
        h = float(vb.group(1).split()[3]); w = float(vb.group(1).split()[2])
        for b in bs:
            if b["y1"] > h + .5 or b["x1"] > w + .5 or b["x0"] < -.5 or b["y0"] < -.5:
                print(f"  OUTSIDE viewBox  {b['cls']} {b['t'][:38]!r}")
                bad += 1
    print(f"  {name}: {len(bs)} text boxes, {bad} issue(s)")
    return bad


def main() -> int:
    src = ART.read_text(encoding="utf-8")
    want = None
    if "--figure" in sys.argv:
        want = sys.argv[sys.argv.index("--figure") + 1]
    total = 0
    found = 0
    for m in re.finditer(r"<!-- FIGURE:([\w-]+) -->(.*?)</figure>", src, re.S):
        name = m.group(1)
        if want and want not in name:
            continue
        found += 1
        total += check(m.group(2), name)
    if not found:
        print("no <!-- FIGURE:name --> blocks found" + (f" matching {want!r}" if want else ""))
        return 2
    print("clean" if total == 0 else f"{total} issue(s) — open the page and look")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
