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
