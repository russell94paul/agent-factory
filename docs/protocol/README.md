# The protocol pack — contracts with enforcement behind them

**RAPID-RELIABILITY-01, approved 2026-08-31.** Written on branch `reliability/recurrence-preflight`
in an isolated worktree; nothing here touched the active
`marketing-model-reconstruction-v1` mission or its working tree.

## Why `docs/protocol/` and not `docs/specs/`

| | holds | read it as |
|---|---|---|
| `docs/specs/` | proposed designs, some never built | **a hypothesis** |
| `docs/protocol/` | contracts that code enforces, or is committed to enforce next | **a rule** |

Mixing them makes it impossible to tell which is which, and this estate has already paid for a
declaration nobody could distinguish from a mechanism (F87, F79). Every file here says which of its
claims is **BUILT** and which is **DESIGN**, in its own header.

## What is BUILT today

| | file | status |
|---|---|---|
| known-failure preflight | [KNOWN_FAILURE_PREFLIGHT.md](KNOWN_FAILURE_PREFLIGHT.md) | ✅ **BUILT** — `factory/preflight.py`, WARN-ONLY |
| failure taxonomy | [FAILURE_TAXONOMY.yaml](FAILURE_TAXONOMY.yaml) | ✅ **BUILT** — the closed set is `preflight.FAMILIES`; the YAML is its index |
| metrics 7 & 9 | [METRICS.md](METRICS.md) | ✅ **BUILT** — `factory/reliability.py`. The other eight are DESIGN |
| the run→events join | [METRICS.md](METRICS.md) §join | ✅ **BUILT** — `runs.record(run=…)` |
| agent communication protocol | [AGENT_COMMUNICATION_PROTOCOL.md](AGENT_COMMUNICATION_PROTOCOL.md) | ⛔ **DESIGN** |
| handoff contract | [HANDOFF_CONTRACT.schema.json](HANDOFF_CONTRACT.schema.json) | ⛔ **DESIGN** |
| quality gates | [QUALITY_GATES.md](QUALITY_GATES.md) | ⛔ **DESIGN** |
| client review backend | [CLIENT_REVIEW_BACKEND.md](CLIENT_REVIEW_BACKEND.md) | ⛔ **DESIGN — DEFERRED.** A separate mission owns this |
| wow features | [CLIENT_WOW_FEATURES.md](CLIENT_WOW_FEATURES.md) | ⛔ **DESIGN — DEFERRED** |
| test harness | [TEST_HARNESS.md](TEST_HARNESS.md) | ⚠ partly built — the GP-327 fixture exists |
| rollout & budgets | [ROLLOUT.md](ROLLOUT.md) | ✅ **BUILT** for V0; the promotion rule is DESIGN |
| prompts | [prompts/](prompts/) | ⛔ **DESIGN** — none is wired to a dispatch path |

## The one hypothesis this pack is testing

> A run should not unknowingly repeat a failure whose evidence already exists in its own history.

Nothing else. Not the handoff contract, not ACK/NACK, not communication attribution, not the
taxonomy machinery. Those are `NEXT` and they are written down so they are not re-derived, **not so
they are built now.**

## The measurement that motivated it

`.data/events.jsonl`, measured 2026-08-31 —

```bash
python scripts/replay_recurrence.py            # the full shadow-mode replay
```

**Seven of the eight recorded runs are one ticket.** GP-327 ran seven times. Six ended with the same
assertion saying the same thing (`ticket_verifier` UNMEASURABLE — *the preset declares a WIRED
verifier and the controller was given no callable*), and the seventh was aborted because those six
had spent the attempt cap. Every attempt after the first had its predecessor's verdict on disk, and
**nothing read it.**

⚠ **The existing mechanism was live and silent.** `deploy.AttemptLedger` already injects prior
failures into the next prompt. `.data/attempts.json.pre-F85.bak` shows why it said nothing: both
recorded attempts are `outcome: "ok"` because the **provider** exited zero on a dry run, and
`failures()` filters on `outcome != "ok"`. The ledger reads what the provider observed; a verdict is
what a `GreenContract` assigned. Those are different questions, and the preflight reads the second.
It is a complement, not a replacement — see `factory/preflight.py`'s module docstring.

## Reading order

1. [KNOWN_FAILURE_PREFLIGHT.md](KNOWN_FAILURE_PREFLIGHT.md) — the only thing that runs today.
2. [FAILURE_TAXONOMY.yaml](FAILURE_TAXONOMY.yaml) — the ten states, and why the tenth exists.
3. [METRICS.md](METRICS.md) — what is measurable, and the six things that are NOT-RECORDED.
4. [ROLLOUT.md](ROLLOUT.md) — the budgets, and the evidence that would justify a hard refusal.
5. Everything else is design for later.

## What this pack must not become

- ⛔ A second event bus. `events.py` (durable) + `bus.py` (live) is a decided split with a written
  rationale (F70/F71) and a delivery hook.
- ⛔ A second findings system. `docs/findings.d/` is the record; the taxonomy indexes it.
- ⛔ A `HandoffContract` class inside `factory/handoff.py` — that module generates prose lane and
  session notes and is a different concept wearing the same word.
- ⛔ A `depends_on` field on `Task`. `block()` is the edge, and it is live (25 events).
- ⛔ A knowledge store, embedding index or retrieval layer. Matching is deterministic key lookup.
- ⛔ A new `PreToolUse`/`PostToolUse` hook. F95: a hook costs a whole interpreter start per tool
  call, so the second one you register is more expensive than the first one's job.
