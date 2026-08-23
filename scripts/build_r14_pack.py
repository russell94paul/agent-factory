"""Build `docs/research/R14-evidence-pack.md` — the code R14 is asked to attack.

    python scripts/build_r14_pack.py

R14 is the INWARD pass: is our decomposition right, are our objects the right objects, and what
would make this a joy to use. It is worth very little without the source — its §2 says so and
names a read order. The R13 pack was weighted for the *UI* question and omits three modules R14
opens with (`contract.py`, `worktrees.py`, `board.py`), so R14 gets its own.

**Ordered, not alphabetical.** The sections below follow R14 §2's read order exactly —
`contract.py` first because everything depends on what "done" and "I could not tell" mean, and the
concurrency primitives early because two of them have no tests and that is one of the three
structural facts R14 is asked to judge.

Generated and gitignored, same rule as the others: a concatenation of files that already live here
is a copy, and a copy is stale on the next edit.

⚠ It leaves the building. Scan before sending:

    grep -nEi "(password|api[_-]?key|BEGIN [A-Z ]*PRIVATE KEY|client_secret)" \\
        docs/research/R14-evidence-pack.md
"""
from __future__ import annotations

import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "research" / "R14-evidence-pack.md"

SECTIONS = [
    ("A. Our own position — what the answer must diff against, not re-derive", [
        ("docs/research/ui-surface-inventory.md",
         "Our frozen position on the UI question, written before looking outward."),
        ("docs/specs/architecture-v0.md",
         "The four planes, and the isolation ladder. A strawman, explicitly."),
        ("docs/specs/control-room.md",
         "The control-room strawman written against R12's answer."),
        ("docs/specs/terminal-configuration.md",
         "The pane layout, the latency budget, and the model-per-lane table."),
    ]),
    ("A2. An unfiled proposal that predates three of our passes — extend it or refute it", [
        ("docs/research/sources/amt-agent-management-terminal.md",
         "⭐ Found unfiled on 2026-08-23, dated 08-22. Proposes an Agent-Management Terminal: "
         "Interrupt Inbox, Agent Radar, Collision Detection, Terminal Genome, Resurrection "
         "Capsules. It covers R12/R13/R15's ground and none of them was given it. It is a VISION "
         "with no evidence tier and nothing measured against this repo — treat it as a proposal to "
         "argue with, not a finding. Say which parts survive contact with the code in section B."),
    ]),
    ("B. The code, in R14 section 2's read order — judge the bones", [
        ("factory/contract.py",
         "READ FIRST. What 'done' and 'I could not tell' mean. Everything depends on it."),
        ("factory/readiness.py",
         "1,029 lines, 12% of the codebase, two modules depend on it. God-object or legitimate "
         "gate registry? R14 section 2.1 asks you to decide and name the seam."),
        ("factory/lanes.py",
         "The conflict graph — file locality, not dependency order. The 3-lane ceiling lives here."),
        ("factory/claims.py",
         "Who holds which lane. ⚠ NO TESTS — and it is a concurrency-safety primitive."),
        ("factory/worktrees.py",
         "One worktree per lane. ⚠ NO TESTS — the other concurrency-safety primitive."),
        ("factory/finish.py",
         "assert -> push -> announce -> release. Never merges. The only real hub in the package."),
        ("factory/runs.py",
         "The run ledger and per-lane cost. Note it resolves state to the PRIMARY worktree, "
         "deliberately breaking the convention bus/claims/operator follow — section 2.1 fact 3."),
        ("factory/sessions.py",
         "Liveness, the four states, and the blocked-question join."),
        ("factory/bus.py",
         "The live channel. Roots at parent.parent/.data, so inside a worktree it is per-lane."),
        ("factory/board.py",
         "Tasks GENERATED from gates, so a hand-list cannot drift. ⚠ NO TESTS."),
        ("factory/metrics.py",
         "Refuses an activity metric with no paired outcome metric. Small, and load-bearing."),
        ("factory/evaluator.py",
         "The agent's only route to a verdict. R3 called a separate local process 'mostly theatre'."),
    ]),
    ("C. The interface as it exists — the thing being redesigned", [
        ("scripts/local_tracker.py",
         "The whole UI: 5 tabs, re-measures per request, single-threaded server. The 30 serial "
         "probes take 9.3 s measured — this file is why the page takes 10-19 s."),
    ]),
    ("D. The record, and the defects — the corrections ledger IS the evidence", [
        ("docs/research/SYNTHESIS.md",
         "The decision record. Section 12 is most recent; do not re-answer R11/R12/R13."),
        ("docs/findings.d/",
         "One file per finding, post-split."),
        ("docs/findings.md",
         "Pre-split ledger: F1-F10."),
    ]),
]


def _read(rel: str) -> str:
    p = ROOT / rel
    if p.is_dir():
        return "\n\n".join(
            "----- %s -----\n\n%s" % (f.name, f.read_text(encoding="utf-8", errors="replace"))
            for f in sorted(p.glob("*.md")))
    return p.read_text(encoding="utf-8", errors="replace")


def build() -> pathlib.Path:
    manifest, body, total, missing = [], [], 0, []
    for title, files in SECTIONS:
        body.append("\n\n# %s\n" % title)
        for rel, why in files:
            if not (ROOT / rel).exists():
                manifest.append((rel, "**MISSING**", why))
                missing.append(rel)
                continue
            text = _read(rel)
            total += len(text)
            manifest.append((rel, "%.0f KB" % (len(text) / 1024), why))
            lang = "python" if rel.endswith(".py") else "markdown"
            body.append("\n## `%s`\n\n> %s\n\n```%s\n%s\n```\n" % (rel, why, lang, text))

    head = [
        "# R14 evidence pack — the bones, in the order R14 asks for them\n",
        "**Built %s from `ALDC-io/agent-factory`.** Upload with "
        "`R14-structure-model-and-joy.md`.\n" % datetime.date.today().isoformat(),
        "\n## The rule for this pass\n",
        "1. **Ground every structural claim in a file and a line from this pack.** Not the "
        "prompt's summary — that is a handoff, and in this estate a handoff is a hypothesis.\n"
        "2. **If something you need is not here, write `NOT-SUPPLIED` and name it.** Do not infer "
        "it. A gap you name is worth more than a gap you fill.\n"
        "3. Where this pack and the prompt disagree, **the pack wins**, and the disagreement is a "
        "finding we want reported.\n"
        "4. Section B is in **reading order, not alphabetical**. `contract.py` is first because "
        "everything depends on what a verdict means.\n",
        "\n## Manifest\n", "| File | Size | Why R14 needs it |", "|---|---|---|"]
    head += ["| `%s` | %s | %s |" % row for row in manifest]
    head.append("\n**Total: %.0f KB.**\n" % (total / 1024))

    OUT.write_text("\n".join(head) + "\n".join(body), encoding="utf-8")
    if missing:
        print("WARNING: %d source(s) missing and NOT in the pack:" % len(missing), file=sys.stderr)
        for m in missing:
            print("  -", m, file=sys.stderr)
    return OUT


if __name__ == "__main__":
    out = build()
    print("wrote %s (%.0f KB)" % (out, out.stat().st_size / 1024))
