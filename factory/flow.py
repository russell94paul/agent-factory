"""The readiness graph as a picture — laid out from the data, never from a guess.

Thirty gates across five phases, twelve dependency edges, and a critical path. All of it already
exists in `readiness.py` and `board.py`; nothing here invents a node, an edge or a coordinate.

⭐ **The rule this module is built to satisfy:** a figure that would look identical if the numbers
were different is decoration. Every coordinate below is computed from the gate list and the
dependency map, so adding a gate moves the picture and deleting one leaves no dangling edge —
`board._validate()` already refuses to import if an edge names a gate that does not exist.

**Four verdicts, and colour is never the only carrier.** `PASS` `FAIL` `UNMEASURABLE` `NOT_RUN` each
get a distinct *shape* as well as a fill, because `UNMEASURABLE` is not a worse `FAIL` — it is "the
instrument could not see", a different claim entirely, and a reader who is colour-blind or looking at
a greyscale print must still be able to tell those two apart.

**Blocked is drawn differently from unbuilt.** A gate that cannot start because something upstream
has not passed is dashed and muted; a gate that is merely failing is solid. Those are different
situations and a diagram that renders them alike is asserting they are the same.

Pure: it computes a layout and emits SVG. It measures nothing and caches nothing, so the tracker's
"every refresh re-measures" contract is untouched.
"""
from __future__ import annotations

import html
from typing import Dict, List, Tuple

from .board import BLOCKED, DONE, READY, board, critical_path
from .readiness import FAIL, NOT_RUN, PASS, PHASES, UNMEASURABLE

# --- geometry, in one place so the picture can be retuned without hunting -------------------------
COL_W = 214          #: horizontal distance between phase columns
NODE_H = 26          #: a gate row
NODE_W = 168
GAP_Y = 7
TOP = 74             #: room for the phase header and its counts
LEFT = 22
BOTTOM_PAD = 30

#: verdict -> (fill token, glyph). The glyph is the non-colour carrier.
VERDICT_MARK = {
    PASS: ("var(--pass)", "●"),
    FAIL: ("var(--fail)", "■"),
    UNMEASURABLE: ("var(--unmeas)", "◆"),      # "could not see" — deliberately not a warning shape
    NOT_RUN: ("var(--ink3)", "○"),
}


def layout() -> Tuple[Dict[str, dict], List[dict], List[str]]:
    """(node by gate id, edges, critical path) — coordinates derived from the real gate list."""
    rows = board()
    crit = critical_path()
    critset = set(crit)

    by_phase: Dict[str, List[tuple]] = {ph: [] for ph in PHASES}
    for g, r, st, unmet in rows:
        by_phase.setdefault(g.phase, []).append((g, r, st, unmet))

    nodes: Dict[str, dict] = {}
    for ci, ph in enumerate(PHASES):
        for ri, (g, r, st, unmet) in enumerate(by_phase.get(ph, [])):
            nodes[g.id] = {
                "id": g.id, "phase": ph, "verdict": r.verdict, "state": st,
                "headline": (r.headline or "")[:96], "unmet": unmet,
                "critical": g.id in critset,
                "x": LEFT + ci * COL_W, "y": TOP + ri * (NODE_H + GAP_Y),
            }

    edges = []
    for gid, n in nodes.items():
        for dep in n["unmet"] + [d for d in _deps(gid) if d not in n["unmet"]]:
            if dep in nodes:
                edges.append({
                    "src": dep, "dst": gid,
                    "unmet": dep in n["unmet"],
                    "critical": dep in critset and gid in critset,
                })
    return nodes, edges, crit


def _deps(gid: str) -> List[str]:
    from .board import DEPENDS
    return DEPENDS.get(gid, [])


def counts() -> List[dict]:
    """Per phase: how many gates, how many passing. DERIVED from the same measure() call."""
    rows = board()
    out = []
    for ph in PHASES:
        gs = [(g, r) for g, r, st, u in rows if g.phase == ph]
        out.append({"phase": ph, "total": len(gs),
                    "passing": sum(1 for g, r in gs if r.verdict == PASS)})
    return out


def _e(t) -> str:
    return html.escape(str(t), quote=True)


def svg() -> str:
    """The whole figure, inline, self-contained. No script, no external reference, no font."""
    nodes, edges, crit = layout()
    if not nodes:
        return '<p style="color:var(--ink3)">no gates to draw</p>'

    per_phase = counts()
    width = LEFT + len(PHASES) * COL_W
    tallest = max(len([1 for n in nodes.values() if n["phase"] == ph]) for ph in PHASES)
    height = TOP + tallest * (NODE_H + GAP_Y) + BOTTOM_PAD

    p: List[str] = []
    p.append(f'<svg viewBox="0 0 {width} {height}" width="100%" '
             f'style="max-width:{width}px;height:auto;display:block" '
             f'role="img" aria-label="Readiness gates by phase, with dependency edges">')

    # --- phase headers. The bar width is passing/total — change the number, change the picture.
    for ci, c in enumerate(per_phase):
        x = LEFT + ci * COL_W
        frac = (c["passing"] / c["total"]) if c["total"] else 0.0
        p.append(f'<text x="{x}" y="20" style="font:600 12px ui-monospace,monospace" '
                 f'fill="var(--ink)">{_e(c["phase"])}</text>')
        p.append(f'<text x="{x}" y="36" style="font:11px ui-monospace,monospace" '
                 f'fill="var(--ink3)">{c["passing"]} of {c["total"]} passing</text>')
        p.append(f'<rect x="{x}" y="44" width="{NODE_W}" height="5" rx="2" fill="var(--rule)"/>')
        if frac > 0:
            p.append(f'<rect x="{x}" y="44" width="{NODE_W * frac:.1f}" height="5" rx="2" '
                     f'fill="var(--pass)"/>')

    # --- edges first, so nodes sit on top
    for e in edges:
        a, b = nodes[e["src"]], nodes[e["dst"]]
        x1, y1 = a["x"] + NODE_W, a["y"] + NODE_H / 2
        x2, y2 = b["x"], b["y"] + NODE_H / 2
        mx = (x1 + x2) / 2
        # An unmet edge is the reason its target cannot start: solid and coloured. A satisfied one
        # is history: faint. Same geometry, different weight — the distinction is the information.
        if e["critical"]:
            stroke, w, dash = "var(--fail)", 2.2, ""
        elif e["unmet"]:
            stroke, w, dash = "var(--unmeas)", 1.4, ""
        else:
            stroke, w, dash = "var(--rule)", 1.0, ' stroke-dasharray="3 3"'
        p.append(f'<path d="M{x1:.0f},{y1:.0f} C{mx:.0f},{y1:.0f} {mx:.0f},{y2:.0f} '
                 f'{x2:.0f},{y2:.0f}" fill="none" stroke="{stroke}" '
                 f'stroke-width="{w}"{dash} opacity="0.85"/>')

    # --- nodes
    for n in sorted(nodes.values(), key=lambda z: (z["x"], z["y"])):
        fill, glyph = VERDICT_MARK.get(n["verdict"], ("var(--ink3)", "○"))
        blocked = n["state"] == BLOCKED
        # BLOCKED is dashed and muted; it is a different situation from failing and must not look
        # like one. DONE is filled; READY is outlined and waiting.
        box_dash = ' stroke-dasharray="4 3"' if blocked else ""
        box_op = "0.55" if blocked else "1"
        box_stroke = "var(--fail)" if n["critical"] else "var(--rule)"
        box_w = 2 if n["critical"] else 1
        bg = "var(--raise)" if n["state"] == DONE else "transparent"
        p.append(f'<g opacity="{box_op}">')
        p.append(f'<title>{_e(n["id"])} — {_e(n["verdict"])} · {_e(n["state"])}'
                 + (f' · waiting on {_e(", ".join(n["unmet"]))}' if n["unmet"] else "")
                 + f'\n{_e(n["headline"])}</title>')
        p.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{NODE_W}" height="{NODE_H}" rx="3" '
                 f'fill="{bg}" stroke="{box_stroke}" stroke-width="{box_w}"{box_dash}/>')
        p.append(f'<text x="{n["x"] + 9}" y="{n["y"] + 17}" '
                 f'style="font:12px ui-monospace,monospace" fill="{fill}">{glyph}</text>')
        p.append(f'<text x="{n["x"] + 24}" y="{n["y"] + 17}" '
                 f'style="font:11.5px ui-monospace,monospace" fill="var(--ink)">'
                 f'{_e(n["id"][:19])}</text>')
        p.append('</g>')

    p.append('</svg>')
    return "".join(p)
