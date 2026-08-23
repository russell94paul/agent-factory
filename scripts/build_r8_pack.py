"""Build `docs/research/R8-evidence-pack.md` — the internal sources R8 must be able to read.

    python scripts/build_r8_pack.py

**Why a generator and not a committed file.** R8 run 1 had web access but no repository access, so
it could not read one internal source and asserted internal facts more confidently than the
evidence allowed. The fix is to hand the researcher the sources — but a 489 KB concatenation of
files that already live in this repo is a *copy*, and a copy is stale the moment any source
changes. Same rule as `tracker.html`: the pack is a view, the files are the source of truth. So the
output is gitignored and this script is what is versioned. Regenerate before every dispatch.

⚠ The pack leaves the building. It is uploaded to a third-party research tool, which means
publishing. Scan before you send:

    grep -nEi "(password|api[_-]?key|BEGIN [A-Z ]*PRIVATE KEY|AccountKey=|client_secret)" \\
        docs/research/R8-evidence-pack.md

Every hit on 2026-08-23 was prose *about* credentials plus one HMAC formula in R3 — no secret. That
is a fact about that day, not a property of the script: re-run it.
"""
from __future__ import annotations

import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "research" / "R8-evidence-pack.md"

#: (section title, [(repo-relative path, why R8 needs it)]). A directory is inlined file by file.
SECTIONS = [
    ("A. Completed research answers — the internal sources run 1 could not read", [
        ("docs/research/answers/R1-answer-eval-harness.md",
         "R1 answer — eval harness. Source of the 29-cases-for-a-10%-blind-spot derivation."),
        ("docs/research/answers/R1-followup.md", "R1 follow-up."),
        ("docs/research/answers/R2-answer-topology.md",
         "R2 answer — build-plane topology and the 3-role sketch."),
        ("docs/research/answers/R2-followup.md",
         "R2 follow-up — establishes the bespoke :8765 engine and the Prefect boundary."),
        ("docs/research/answers/R3-answer-control-plane.md",
         "R3 answer — control plane, isolation-as-evidence, optimizer ranking."),
        ("docs/research/answers/R3-followup.md", "R3 follow-up."),
        ("docs/research/answers/R5-answer-build-velocity.md",
         "R5 answer — source of the 41.7% conflict rate and the lane/file-locality conclusions."),
        ("docs/research/answers/R6-answer-automation-and-alerting.md",
         "R6 answer — unattended execution, alerting, the stalled-lane signal."),
        ("docs/research/answers/R7-answer-session-manager.md",
         "R7 answer — PTYs, supervision, leases, multiplexing."),
    ]),
    ("B. The strawman R8 is asked to attack", [
        ("docs/specs/architecture-v0.md", "The T0/T1/T2 isolation ladder in full."),
        ("docs/specs/terminal-configuration.md", "The agent-terminal spec behind R8 section 2.6."),
    ]),
    ("C. Factory implementation — read the code, do not trust the handoff", [
        ("factory/lanes.py",
         "Conflict graph. Verify whether 'max independent set = 3' is a file-conflict property."),
        ("factory/worktrees.py", "What isolation exists today; what host state stays shared."),
        ("factory/claims.py", "Lease semantics, stale claims, crash behaviour."),
        ("factory/bus.py", "Live channel: delivery, ordering, persistence, failure."),
        ("factory/finish.py", "Close protocol: what evidence actually blocks release."),
        ("factory/readiness.py",
         "All 30 gates. Judge whether they are meaningful, independent, enforceable, fail-open."),
        ("factory/dispatch.py",
         "Research-prompt state machine. Relevant to R8 section 2.2 on record-vs-channel."),
        ("factory/runs.py",
         "The lane run ledger and per-lane measured cost. Relevant to R8's cost-control row."),
    ]),
    ("D. Corrections ledger — including the collision it is currently suffering", [
        ("docs/findings.d/", "Post-split ledger, one file per finding (main)."),
        ("docs/findings.md",
         "Pre-split ledger on main: F1-F10. F1 is the context-poisoning instance R8 2.2 asks about."),
        (".worktrees/artifact/docs/findings.md",
         "artifact lane: F50-F53. F53 is the globally-shared ~/.claude/skills/ leak."),
        (".worktrees/certify/docs/findings.md", "certify lane: F30-F32."),
        (".worktrees/control-plane/docs/findings.md",
         "control-plane lane: F11-F34, written against the OLD single-file ledger. F20/F21 COLLIDE "
         "with main's findings.d ids and git merges it clean."),
    ]),
]

HEADER = """
## Why this file exists

R8 run 1 had web access but **no repository access**. It could not read a single internal source,
so it treated internal facts more confidently than the evidence supported, and its own assessment
was that the external survey is salvageable while *"the comparison against your actual factory is
not yet sufficiently grounded."* This pack removes that excuse.

## The rule for this run

1. **Every internal claim you make must cite a file and a line from this pack.** Not the R8 prompt's
   summary tables — those are a handoff, and in this estate a handoff is a hypothesis.
2. **If something you need is not in this pack, say `NOT-SUPPLIED` and name it.** Do not infer it,
   and do not fall back to the prompt's prose. A gap you name is worth more than a gap you fill.
3. **`MARKETED` may not be a design premise** — unchanged from the prompt's section 7.
4. Where this pack and the R8 prompt disagree, **the pack wins** and the disagreement is a finding.

## Manifest
"""


def _read(rel: str):
    p = ROOT / rel
    if p.is_dir():
        parts = ["----- %s -----\n\n%s" % (f.name, f.read_text(encoding="utf-8", errors="replace"))
                 for f in sorted(p.glob("*.md"))]
        return "\n\n".join(parts)
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

    head = ["# R8 evidence pack — the internal sources, verbatim\n",
            "**Built %s from `ALDC-io/agent-factory` @ working tree.** Upload this whole file with "
            "`R8-data-engineering-agent-factory.md`.\n" % datetime.date.today().isoformat(),
            HEADER, "| File | Size | Why R8 needs it |", "|---|---|---|"]
    head += ["| `%s` | %s | %s |" % row for row in manifest]
    head.append("\n**Total: %.0f KB.**\n" % (total / 1024))

    OUT.write_text("\n".join(head) + "\n".join(body), encoding="utf-8")
    # A missing source is reported loudly. A pack that silently omits a file the prompt promises
    # is how the researcher ends up inferring again — the exact failure this script exists to fix.
    if missing:
        print("WARNING: %d source(s) missing and NOT in the pack:" % len(missing), file=sys.stderr)
        for m in missing:
            print("  -", m, file=sys.stderr)
    return OUT


if __name__ == "__main__":
    out = build()
    print("wrote %s (%.0f KB)" % (out, out.stat().st_size / 1024))
    print("\nBefore uploading, scan it — it is leaving the building:")
    print('  grep -nEi "(password|api[_-]?key|BEGIN [A-Z ]*PRIVATE KEY|client_secret)" "%s"'
          % out.name)
