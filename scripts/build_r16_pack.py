"""Build `docs/research/R16-evidence-pack.md` — the answers, not just our conclusions.

    python scripts/build_r16_pack.py

R16 reviews the eighteen decisions the research produced. It is **the least independent pass in the
programme**: every other one had its own footing — repositories, literature, source code — and this
one reads our own record. Handed only `SYNTHESIS.md` it could check internal consistency and nothing
else, and it would agree with us, because the synthesis is where we already wrote down what we think.

So the pack ships **every filed answer** alongside the synthesis. When a decision cites a pass, R16
can go and read what that pass actually said — and the gap between the two is most of what this pass
is for.

Generated and gitignored, like the others. ⚠ It leaves the building; scan before sending.
"""
from __future__ import annotations

import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "research" / "R16-evidence-pack.md"
ANSWERS = ROOT / "docs" / "research" / "answers"


def build() -> pathlib.Path:
    rows, body, total = [], [], 0

    def add(rel: str, why: str) -> None:
        nonlocal total
        p = ROOT / rel
        if not p.is_file():
            rows.append((rel, "**MISSING**", why))
            print("WARNING: missing", rel, file=sys.stderr)
            return
        text = p.read_text(encoding="utf-8", errors="replace")
        total += len(text)
        rows.append((rel, "%.0f KB" % (len(text) / 1024), why))
        body.append("\n## `%s`\n\n> %s\n\n```markdown\n%s\n```\n" % (rel, why, text))

    body.append("\n\n# A. The record under review\n")
    add("docs/research/SYNTHESIS.md",
        "The decision record. Sections 12.8, 13.7 and 14.7 hold the eighteen actions.")

    body.append("\n\n# B. The answers those decisions were drawn from — read these before agreeing\n")
    # Deliberately ordered by research id, so a reviewer can walk a decision back to its source.
    for f in sorted(ANSWERS.glob("R[0-9]*-answer*.md"),
                    key=lambda x: (int(x.name.split("-")[0][1:]), x.name)):
        rid = f.name.split("-")[0]
        add("docs/research/answers/" + f.name,
            "%s, as filed. Check any decision citing %s against what it actually says." % (rid, rid))

    body.append("\n\n# C. Corrections the programme made to itself\n")
    add("docs/research/ui-surface-inventory.md",
        "Our frozen position on the UI question, and the count of surfaces that already exist.")

    head = ["# R16 evidence pack — the answers, not just our conclusions\n",
            "**Built %s.** Upload with `R16-decision-review-and-order.md`.\n"
            % datetime.date.today().isoformat(),
            "\n⭐ **Why every answer is here.** R16 is the least independent pass in this programme: "
            "it reads our own record. Given only the synthesis it could check internal consistency "
            "and nothing else. **When a decision cites a pass, read that pass.** Several of our "
            "decisions summarise answers that do not quite support them, and finding those is most "
            "of the value.\n",
            "\n## Manifest\n", "| File | Size | Why R16 needs it |", "|---|---|---|"]
    head += ["| `%s` | %s | %s |" % r for r in rows]
    head.append("\n**Total: %.0f KB across %d sources.**\n" % (total / 1024, len(rows)))

    OUT.write_text("\n".join(head) + "\n".join(body), encoding="utf-8")
    return OUT


if __name__ == "__main__":
    out = build()
    print("wrote %s (%.0f KB)" % (out, out.stat().st_size / 1024))
