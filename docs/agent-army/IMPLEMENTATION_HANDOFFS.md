# Implementation handoffs

Research ideas that have formally graduated into implementation work in this repository.

## Active handoffs: none

| SOURCE RESEARCH FILE | TARGET AREA IN CODE | STATUS | COMMIT / PR |
|---|---|---|---|
| _(none)_ | — | — | — |

No handoff has been proposed, approved, rejected or completed. All four directories in
`agent-army-research/implementation-handoffs/` are empty apart from their `.gitkeep`.

## The promotion path

A handoff is the **only** sanctioned way research becomes work here.

```text
Deep Research
      ↓
Research Answer                 agent-army-research/research/answers/
      ↓
Evidence Audit                  claude-skills/evidence-auditor
      ↓
Wave Synthesis                  research/synthesis/
      ↓
Canonical Research Spec         ontology/ | architecture/ | governance/
      ↓
Architecture Decision           adr/
      ↓
Approved Implementation Handoff implementation-handoffs/approved/   ← the bridge
      ↓
Agentic Factory Implementation    this repository
      ↓
Tests / Benchmarks              tests/, evals/, evaluator_service/
      ↓
Completion Evidence             back to implementation-handoffs/completed/
```

Two rules make the path real rather than decorative:

1. **A research document is never itself a ticket.** Work that begins from `architecture/` or
   `design/` without a handoff has skipped the audit and the synthesis, which is exactly how a
   speculative diagram becomes a production schema.
2. **The path runs both ways.** When implementation finishes — or fails, or discovers the research
   premise was wrong — the outcome is written back to
   `implementation-handoffs/completed/` (or `rejected/`). A handoff with no return leg leaves the
   research programme believing something shipped that did not.

## Handoff lifecycle and where it lives

| Stage | Directory | Meaning |
|---|---|---|
| `proposed` | `implementation-handoffs/proposed/` | Drafted from synthesis; not yet decided |
| `approved` | `implementation-handoffs/approved/` | ADR accepted; **this repository may act on it** |
| `completed` | `implementation-handoffs/completed/` | Implemented, tested, evidence attached |
| `rejected` | `implementation-handoffs/rejected/` | Declined, with the reason — kept, never deleted |

Template: `agent-army-research/implementation-handoffs/HANDOFF_TEMPLATE.md`.

## Row format

| Field | Rule |
|---|---|
| `SOURCE RESEARCH FILE` | Path to the file in `implementation-handoffs/approved/`, not to the answer or the architecture note |
| `TARGET AREA IN CODE` | Concrete: module or package. `factory/bus.py`, not "the event system" |
| `STATUS` | `NOT STARTED` / `IN PROGRESS` / `BLOCKED` / `COMPLETE` / `ABANDONED` |
| `COMMIT / PR` | Required at `COMPLETE`. A completion with no commit is a claim |

Every handoff must carry acceptance tests and a rollback before it is approved — the same standard
the rest of this repository applies to a delivery (`factory/evidence.py`: `TARGET`, `CONSUMER`,
`REGRESSION`, `ROLLBACK`).

## Before proposing the first one

Read [CURRENT_STATE.md](CURRENT_STATE.md) first. Two facts will shape any early handoff:

- Nothing in the research vocabulary is implemented here — no missions, intent contracts, staff
  mesh, doctrine or federation. A handoff that assumes a substrate will not find one.
- The three-agent team blueprint was **tested and rejected on measured evidence**
  (`blueprints/orchestrator_team.yaml`), and `README.md` gates Agent Army work on *"one certified
  team, plus evidence a tier helps"*. A handoff that proposes supervisor tiers has to clear that
  threshold, which is written down and quantified.
