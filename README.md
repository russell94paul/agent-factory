# Agent Factory — skeleton

A **foundation**, not a framework. Everything here exists to make one claim testable:

> A team of agents did the work, and we can prove it — or we can prove we could not tell.

## Why this shape

This estate has twice built mechanisms that *acted* without anything measuring whether the action
helped. A retired agent produced **233 diagnoses, 234 escalations and 0 fixes over 81 days**. A
separate loop ran **965 times, recorded its own 1.6% success rate, and never adjusted**. Both were
capable. Neither was measurable.

So the ordering here is deliberate and non-negotiable:

```
contract.py   what "done" means, and what "I could not tell" means   ← everything depends on this
evals.py      can the contract actually fail?  (negative control)
tasks.py      what a team is doing, append-only, evidence-gated
blueprint.py  the config that IS the version
deploy.py     put an agent in a repo, bounded
metrics.py    every activity metric paired with an outcome metric
```

**Do not add a team, an optimizer or a UI until `pytest tests/test_eval_can_fail.py` passes.**
That test is the whole point: it proves the instrument can register a failure. A green suite from
an instrument that cannot fail is the 965-run loop again.

⚠ **That gate passes today, and it is weaker than its reputation.** `test_eval_can_fail.py` builds a
synthetic three-assertion contract over a hardcoded dict and **never loads the corpus** — it proves
the *mutation harness* works, nothing more. The real evidence that the connector contract can fail
is `tests/test_connector_contract.py`, which calibrates all twelve assertions and enforces the
property with `test_every_assertion_has_been_proved_able_to_fail`. Cite that file, not this one,
when the question is whether the instrument can see. (F76.)

## Status

**Phase A: the contract exists, is calibrated, and now certifies the recorded run green — against
one connector.**

```bash
python -m factory.certify blueprints/windsorai_gep.yaml --calibrate
# connector-e2e/windsorai@GEP: PASS (PASS=12)
#   scored against corpus windsorai-2026-08-20 — REPLAYED, not a live measurement
```

All twelve assertions pass against the recorded 2026-08-20 windsorai run. A12 previously blocked on
an undeclared tenant scope and no longer does — *"every row within the 2 declared tenant(s)"*.
Evidence and open questions:
[`docs/evidence/phase-a-windsorai.md`](docs/evidence/phase-a-windsorai.md).

⚠ **Read `PASS (PASS=12)` for exactly what it says.** It is a *replay* against **one** recorded
connector, not a live measurement and not a second subject. The contract's assertions have each been
shown able to fail — `tests/test_connector_contract.py` enforces that with
`test_every_assertion_has_been_proved_able_to_fail` — but sensitivity is not coverage. What remains
open is breadth: 48 connectors have never been scored. See
[`docs/findings.d/F76`](docs/findings.d/F76-the-eval-can-fail-what-it-cannot-do-is-generalise.md),
which corrects the widely-repeated claim that the one-file corpus means the instrument cannot fail.

Team scope for team one is **source -> container -> Prefect -> warehouse**. Power BI is out until
a team has proved it can land rows.

## Quickstart

```bash
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q                                        # all four gates must pass
python -m factory.demo                           # end-to-end on a fake connector
```

## The four verdicts — never collapsed

Borrowed from `orchestrator/engine/gauge.py`, for the reason its docstring gives: *collapsing
"I could not look" into "I looked and it was fine" is how a measurement that never happened passes
for one that did.*

| Verdict | Means | Is it a pass? |
|---|---|---|
| `PASS` | Asserted, and the assertion held | **Yes** |
| `FAIL` | Asserted, and the assertion did not hold | No |
| `UNMEASURABLE` | The instrument could not run | **No — and this is the important one** |
| `NOT_RUN` | Never attempted | No |

`UNMEASURABLE` is not a pass. A contract whose instruments are dark reports `UNMEASURABLE`, and a
team holding an `UNMEASURABLE` is not certified.

## What is deliberately absent

| Not here | Unlocked by |
|---|---|
| Optimizer | A working eval — the fitness function *is* the eval score |
| Agent Army / supervisor tiers | One certified team, plus evidence a tier helps |
| More than one comms topology | A second team that actually needs to talk to the first |
| Gym | It is the eval corpus plus a scoreboard; build the corpus first |
| Platform UI | Numbers worth looking at |

Each is cheap to add *after* its precondition and expensive to unwind before it.
