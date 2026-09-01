# Known-failure preflight — ✅ BUILT, and it refuses nothing

**Implementation:** `factory/preflight.py` · **Wiring:** `factory/control.py` ·
**Tests:** `tests/test_recurrence_preflight.py` · **Replay:** `scripts/replay_recurrence.py`

## The flow

```
ticket
  → run_started          the eligible set goes to disk first; nothing may precede it
  → PREFLIGHT            fold this ticket's OWN prior runs out of .data/events.jsonl
      ↳ classify each into a failure family (or UNCLASSIFIED)
      ↳ run the family's prevention check, if one exists
      ↳ render ≤200 words
      ↳ emit `preflight_checked` — recorded whether or not it had anything to say
  → prepend the packet to the agent's task text     ⭐ delivered, not just filed
  → worktree · claim · dispatch · contract · verdict
```

⛔ **A failing preflight cannot take a run down with it.** `RunController._run_preflight` catches
every exception and returns an inert `Match` recorded as `CHECK_ERROR`. The first version called
`check()` unguarded and outside every `try`: any raise propagated out of `run()`, leaving no
terminal event, a run dangling in the stream with no verdict, and the caller holding an exception
instead of a result. **WARN-ONLY has to mean inert on failure, not only inert on a match.**

⛔ **Position matters and is asserted in the suite.** The preflight sits *after* `run_started` (so
the eligible set is durable before anything else can fail) and *before* the worktree, the claim and
the agent (a preflight that ran after dispatch is a post-mortem). `tests/test_control_run.py`
pins the exact event sequence.

## ⛔ WARN-ONLY in V0 — including families whose retryability is NEVER

`Match.would_refuse` is **computed, recorded, and not read by any branch of `RunController.run`.**

The reason is measured, not cautious: there are eight replayable runs, a first-pass GREEN rate of
**zero**, and a taxonomy written this week. A hard refusal built on that would be a control derived
from a population too small to have produced a single false positive yet — and the estate has
already shipped one probe that handed itself the state it wanted to see (F18).

`tests/test_recurrence_preflight.py::test_would_refuse_is_computed_and_never_enforced` asserts the
`Match` object exposes no refusal affordance at all, so a later caller cannot quietly acquire one.

## The packet

Exactly the shape the approval specified:

```text
KNOWN_FAILURE_MATCH
previous_attempt: <run id> at <timestamp> (attempt N of this ticket)
failure_family: <FAMILY> [<rule that classified it>]
previous_verdict: FAIL | UNMEASURABLE | ERROR | NOT_RUN
previous_reason: <the assertion the family was derived from, and its detail>
required_prevention: <what the check looked at> -> CLEARED | STILL_PRESENT | NOT-RECORDED
would_refuse_under_policy: true | false
```

**MEASURED against the real stream:** mean **94.8 words / 807 characters** per packet across the six
runs that would receive one; max 95. Budget is 200 words. Regenerate with
`python scripts/replay_recurrence.py`.

⚠ **Silence is the default.** An attempt with no prior recorded failure gets an empty string, not a
"no prior failures" block. A preflight that speaks on every run is skimmed, and the run with
something to say is then the one nobody reads.

⭐ **`previous_reason` must name the assertion the family came from.** The first version returned
the first non-passing assertion, which on all six GP-327 runs was `outcome_observable` — so the
packet said `DECLARATION_WITHOUT_MECHANISM` and then explained it with a dry-run symptom. A family
and a reason that contradict each other are worse than no packet. Found by running
`scripts/replay_recurrence.py` against the real stream; **every test passed at the time**, because
they all asserted the family and none read the prose beside it. Now guarded by
`test_the_reason_names_the_assertion_the_family_came_from`.

## The prevention check — the field that makes the packet worth reading

"You failed this way before" is nearly useless alone: the operator may have just fixed it. **"You
failed this way before, and the specific blocker is still present"** is actionable, and it is the
only thing that distinguishes a legitimate retry from a repeat.

| family | check | verdict |
|---|---|---|
| `DECLARATION_WITHOUT_MECHANISM` | is `verifiers.REGISTRY` able to supply a callable for this preset, and does the preset say `WIRED`? | `CLEARED` / `STILL_PRESENT` |
| every other family | none exists yet | `NOT-RECORDED` |
| a check that **raises** | — | ⚠ `CHECK_ERROR`, never `NOT-RECORDED` |

`NOT-RECORDED` is honest and currently common. Inventing a check that returns `True` would be a
probe that hands itself the state it wants to see.

⚠ **A crashed check and a missing check are different facts.** The first version reported both as
`NOT-RECORDED` — `COLLAPSED_STATE`, reproduced inside the module that names the family. A broken
check needs fixing; a missing one needs writing, and only the first means the taxonomy's coverage
number is a lie. `CHECK_ERROR` is now its own value and carries the exception in `prevention_error`.

The check is a registry lookup and a field read: no subprocess, no network, no pytest. That is what
keeps the whole preflight inside its 200 ms budget.

## Matching is deterministic key lookup — ⛔ no retrieval, no similarity

The key is the **normalised ticket id** — `preflight.ticket_key`, which is `control.Ticket.key`'s
rule: lowercase, punctuation collapsed to dashes, truncated at 64. Not embeddings, not fuzzy text,
not "reason about which past failures look relevant". The estate's sole runtime dependency is
`pyyaml` and this does not change that.

⚠ **Normalised, because the raw id lost identity.** The stream records `ticket.id` verbatim, so
`GP-327` and `gp-327` were two tickets to a raw match — while `worktrees.path_for` and
`claims._task_path` both take `Ticket.key`, so the two ids already share a worktree, a claim and an
attempt-cap key. The preflight would have been the estate's only dissenter, and it would have
dissented by staying **silent**. This is a false-negative fix and cannot widen a match beyond what
the claim system already treats as one work item. The two definitions exist separately only because
`control` imports `preflight`; `test_the_ticket_key_agrees_with_the_controllers` asserts they agree,
including at the truncation and empty-string edges.

Cross-ticket matching (family → other tickets that hit it) is **NEXT**, and it is the point at which
the ≤3-packet cap in `ROLLOUT.md` starts to bind. Today one ticket's own history is a single packet,
so the cap is not yet load-bearing.

## What it records — every field in §6 of the approval

Ten fields ride on the `preflight_checked` event:

`attempt_number` · `prior_attempt_count` · `prior_terminal_verdict` · `prior_failure_family` ·
`same_family_as_prior` · `prevention_check_available` · `prevention_check_result` ·
`prevention_detail` · `context_packet_words` · `warning_emitted` · `would_refuse` · `policy`

Three more are **derived at read time** by `preflight.invocations()` from the same run's later
events: `run_started` · `eventual_verdict` · `eventual_failure_family`.

⭐ **Derived, not stored, on purpose.** Storing them would mean writing a value before it is known.
The join is what answers the only question worth asking — *did showing a run its previous failure
change the outcome?* — and without it we would be measuring that warnings were generated, which is
an activity metric with no outcome anchor. `factory.metrics` raises `GoodhartViolation` on exactly
that, and `reliability.metric_set()` anchors `known_failure_warnings` to `first_pass_green_rate` so
the 234/0 signature is caught in one line by `suspicious()`.

## Shadow-mode result on the real history

| | |
|---|---|
| runs in the stream | 8 |
| would have emitted a warning | **6** (GP-327 attempts 2–7) |
| would have been silent | 2 (GP-327 attempt 1; GP-401, a first attempt) |
| marked `would_refuse` | **5** — attempts 2, 3, 5, 6, 7 |
| not marked, and correctly so | attempt 4 — its predecessor was `UNBOUNDED_RETRY`, which has no prevention check, so nothing could confirm the blocker was still present |

Full output: `docs/evidence/recurrence-preflight-2026-08-31/replay-shadow-mode.txt`.
