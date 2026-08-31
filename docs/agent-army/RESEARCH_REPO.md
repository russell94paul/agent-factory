# Research repository

Canonical Agent Army research repository:

```text
agent-army-research          # sibling of this repository
```

```text
workspace/
├── agentic-factory/           ← you are here: what exists
└── agent-army-research/     ← what should exist
```

Open it directly in Obsidian; `HOME.md` is the navigation page and `START_HERE.md` is the entry
point for running the programme.

## Source-of-truth hierarchy

Neither repository is authoritative about everything. The split is by *kind of claim*:

| Question | Authority | Why |
|---|---|---|
| **What does the system do today?** | this repo — code, tests, and the docs the package imports | Only the code can answer it, and only tests can prove it |
| Is a change correct? | this repo — `tests/`, `factory/contract.py`, `evaluator_service/` | The verdict is computed, not asserted |
| What is the current *research* specification? | research repo — `ontology/`, `architecture/`, `governance/` | Canonical **within research**; says nothing about what is built |
| What did a research pass find? | research repo — `research/answers/` | Evidence and analysis, not product truth |
| Which finding wins when passes disagree? | research repo — `research/synthesis/` | Conflicts are resolved in one place, deliberately |
| What has been approved to build? | research repo — `implementation-handoffs/approved/`, mirrored in [APPROVED_CONCEPTS.md](APPROVED_CONCEPTS.md) | The only sanctioned crossing point |
| Was it built? | this repo — [CURRENT_STATE.md](CURRENT_STATE.md) plus the code it cites | A handoff is a decision to build, not a build |

Read the hierarchy top to bottom when they disagree: **code beats specification, specification
beats answer, answer beats intuition.** A research document that contradicts the code is a
research document that needs updating — never the other way round.

## Rules

1. **A research document is never a product specification.** If work is starting from a document
   in `agent-army-research`, an approved implementation handoff must exist first.
2. **Never claim a concept exists in production without verifying it here.** Check
   [CURRENT_STATE.md](CURRENT_STATE.md), then open the file it cites.
3. **Never rewrite this repository's architecture from a speculative document.** Research proposes;
   an ADR decides; a handoff authorises.
4. **Never auto-synchronise the two directories.** They have different truth semantics — a
   research edit overwriting a product doc silently converts a hypothesis into a claim.
5. **Corrections flow back.** If work here disproves a research assumption, say so in the research
   repo. `migration/MIGRATION-REPORT.md` §"Product discoveries" opened this ledger with three
   findings the research programme did not know.

## Working across both

```bash
git -C ../agent-army-research pull            # research is a separate history
python ../agent-army-research/scripts/validate_repo.py   # or: make validate, from that repo
```

Research runs are executed **from the research repo**, not from here. Nothing in this repository
imports, reads or depends on `agent-army-research`, and nothing should start to — the boundary is
worth more than the convenience.
