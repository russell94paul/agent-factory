"""Build `docs/research/R13-evidence-pack.md` — the internal sources R13 must be able to read.

    python scripts/build_r13_pack.py

**Why a generator and not a committed file.** Same rule as `build_r8_pack.py`: a concatenation of
files that already live in this repo is a *copy*, and a copy is stale the moment any source
changes. The output is gitignored; this script is what is versioned. Regenerate before every
dispatch.

**Why this pack differs from R8's.** R8 asks what a data-engineering agent factory should be. R13
asks what should *render* it — architecture, desktop stack, latency, approval surface, provenance,
notification. So this pack is weighted to the surfaces and the substrate that feeds them:
`local_tracker.py` (the UI as it actually exists, and the reason a page load takes 10-19 s),
`readiness.py` (the thirty probes it re-measures serially), the four prior answers that already
touched this surface, and the corrections ledger.

⚠ The pack leaves the building. It is uploaded to a third-party research tool, which means
publishing. Scan before you send:

    grep -nEi "(password|api[_-]?key|BEGIN [A-Z ]*PRIVATE KEY|AccountKey=|client_secret)" \\
        docs/research/R13-evidence-pack.md

Prose *about* credentials is expected — the per-secret approval rule is a design constraint and is
discussed throughout. A literal secret is not. Read every hit; do not count them.
"""
from __future__ import annotations

import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "research" / "R13-evidence-pack.md"

#: (section title, [(repo-relative path, why R13 needs it)]). A directory is inlined file by file.
SECTIONS = [
    ("A. Our frozen position — read this before the survey, it is what the answer must diff against", [
        ("docs/research/ui-surface-inventory.md",
         "THE required attachment. What the factory is for, the four planes and who belongs in "
         "each, what surfaces exist, what is confusing, and the constraints. R13 section 4.8's "
         "'four interfaces already exist' is enumerated here."),
        ("docs/specs/architecture-v0.md",
         "The four planes and the T0/T1/T2 isolation ladder in full, each decision tiered "
         "MEASURED/DERIVED/REASONED/BET. Section 7 is the part inviting attack."),
        ("docs/specs/terminal-configuration.md",
         "The pane layout as built, and the history behind the embedded-terminal rule that R13 "
         "section 6 reopens as an explicit question. Also the source of the 3-lane computation."),
        ("docs/specs/control-room.md",
         "The strawman R13 is being run against: the wait ledger, the slice plan with a gate per "
         "slice, the switchboard duplicate-spawn finding, and the current refusal list."),
    ]),
    ("B. Prior research on this surface — do not re-answer these, extend them", [
        ("docs/research/SYNTHESIS.md",
         "The decision record digesting R1-R7, including where answers disagreed and section 12.2 "
         "— the pass that was dispatched without a standing constraint and duly recommended a tool "
         "the constraint had ruled out. That failure is why R13 states its constraints."),
        ("docs/research/answers/R7-answer-session-manager.md",
         "What should RUN sessions: PTYs, supervision, leases, multiplexing, failure recovery."),
        ("docs/research/answers/R12-answer-session-manager-ui.md",
         "The substrate layer, and switchboard read from source — including that it re-uses only "
         "PTYs it spawned and otherwise spawns a duplicate process against the same session id. "
         "Relevant to R13 sections 4.2 and 4.7."),
        ("docs/research/answers/R11-answer-factory-concept-diff.md",
         "Concept vocabulary across nine frameworks. Observability/traces, guardrails, workflows "
         "and connector registries are all marked ABSENT here — direct input to section 4.5."),
        ("docs/research/answers/R6-answer-automation-and-alerting.md",
         "Unattended execution and the stalled-lane signal. Input to section 4.6."),
        ("docs/research/answers/R5-answer-build-velocity.md",
         "Source of the 41.7% cross-agent conflict rate and the file-locality conclusion that caps "
         "us at three lanes. Input to section 4.1's 'which of these raises the ceiling'."),
    ]),
    ("C. The surface as it actually exists — judge the code, not the description", [
        ("scripts/local_tracker.py",
         "THE existing UI, entire. Four tabs, the launch buttons, the generated per-lane .ps1, and "
         "the single-threaded socketserver.TCPServer behind the 10-19 s page load and the empty "
         "response on concurrent requests. Section 4.3's latency budget should be argued against "
         "this file, not against the summary."),
        ("factory/readiness.py",
         "All 30 gates — what is re-measured serially on every page load. Judge which probes could "
         "be incrementally invalidated and which genuinely must re-run."),
        ("factory/lanes.py",
         "The conflict graph. Verify for yourself that 'max independent set = 3' is a file-locality "
         "property and not a dependency-order one, before section 4.1 recommends against it."),
        ("factory/sessions.py",
         "Liveness from ~/.claude/sessions/<pid>.json. Note what it reads and what it ignores: "
         "`status` is present and unused, and the jobs registry with the `needs` question is not "
         "read at all. Section 4.6."),
        ("factory/runs.py",
         "The run ledger — per-lane cost, wall clock, model and commits, reconstructed from "
         "transcripts. The only provenance we currently have. Section 4.5."),
        ("factory/blueprint.py",
         "AgentSpec, TeamSpec and the version hash that covers 0 of 15 identity dimensions. "
         "AgentSpec is executed by deploy.py; nothing in the estate runs a TeamSpec. Section 4.5."),
        ("factory/claims.py",
         "Lease semantics, stale claims, crash behaviour — the DECIDE plane's only enforcement."),
        ("factory/finish.py",
         "The close protocol. It asserts, pushes, announces, releases the claim and records the "
         "run, and REFUSES to merge — the APPROVE boundary as currently drawn in code. Section 4.4."),
        ("factory/bus.py",
         "The live channel. Rooted per-worktree, which is why lanes cannot see each other and why "
         "the estate holds one event total (F71)."),
    ]),
    ("D. Corrections ledger — the defects are the evidence", [
        ("docs/findings.d/",
         "One file per finding. F70 a shared ledger cannot survive parallel lanes · F71 lanes "
         "still cannot see each other live · F72 the board number depends on where you run it · "
         "F73 a claim is not a process · F74 an invisible refusal reads as a broken feature. "
         "F74 in particular is section 4.6 stated as a defect that already happened."),
    ]),
]

HEADER = """
## Why this file exists

R13 is a survey pass with web access. Without the repository it can only diff against the prompt's
own summary tables — and in this estate **a handoff is a hypothesis, not a finding**. A prior pass
answered confidently about internals it could not read; a second was dispatched without a standing
constraint and recommended a tool that constraint had ruled out. This pack removes both excuses.

## The rule for this run

1. **Every internal claim you make must cite a file and a line from this pack**, not the prompt's
   summary. Where the pack and the prompt disagree, **the pack wins and the disagreement is a
   finding we want reported.**
2. **If something you need is not here, say `NOT-SUPPLIED` and name it.** Do not infer it and do
   not fall back to the prompt's prose. A gap you name is worth more than a gap you fill.
3. **`MARKETED` may not be a design premise** — unchanged from the prompt's section 7. Assume any
   capability whose source or documentation you have not seen is absent until proven otherwise.
4. **The embedded-terminal question in section 6 is genuinely open.** Our own documents in part A
   argue the standing refusal. Do not treat that as our answer — argue it on the merits, and if
   your recommended architecture depends on it, give both branches.

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

    head = ["# R13 evidence pack — the internal sources, verbatim\n",
            "**Built %s from `ALDC-io/agent-factory` @ working tree.** Upload this whole file with "
            "`R13-architecture-and-ui-survey.md`.\n" % datetime.date.today().isoformat(),
            HEADER, "| File | Size | Why R13 needs it |", "|---|---|---|"]
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
