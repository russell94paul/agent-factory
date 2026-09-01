# Rollout — budgets, the kill criteria, and how a refusal would ever be earned

## Performance budget

| item | budget | measured | rationale |
|---|---|---|---|
| envelope serialization | < 50 ms | n/a (design) | it is a dict and one `json.dumps` |
| preflight | **< 200 ms** | ✅ **MEASURED: 49 ms at 1,000 runs, 188 ms at 5,000** | ⛔ no pytest, no subprocess. ⚠ The first version was **quadratic** — 3,726 ms at 500 runs, 12,666 ms at 1,000 — and crossed this budget before anyone ran it at scale. Fixed by `events.fold_all()`; guarded by a read-count test, not a timing test |
| context added per run | **≤ 3 packets, ≤ 600 words total** | ✅ **94.8 words mean, 95 max, one packet** (`scripts/replay_recurrence.py`) | a hard cap, not a target; over is a bug |
| required ACKs per mission | ≤ 1 per cross-agent handoff | 7 for `marketing-model-reconstruction-v1` (derived from its 8 tasks) | design |
| human gates per mission | ≤ 2 | design | more and they get clicked through |
| new hooks | ⛔ **zero** | ✅ none added | F95 — a Claude Code hook costs a whole interpreter start on every tool call |

**Token overhead, MEASURED and DERIVED:** 807 characters mean per packet (MEASURED). At ~3.6
chars/token that is **~224 tokens** (DERIVED — the divisor is an estimate, not a tokenizer run).
Against a task prompt plus a repo context pack this is not material, and it is paid **only on a
repeat attempt** — a first attempt receives an empty string.

## Which tasks BYPASS the machinery

- single-agent and single-turn work;
- read-only work with no downstream consumer;
- ⚠ **`--plan` / dry runs** — F85: two plan-only invocations spent the whole attempt cap and made
  a ticket permanently unrunnable. A dry run must not pay a reliability tax it cannot benefit from;
- anything inside one agent's own turn.

The preflight already self-bypasses: no prior recorded failure ⇒ empty packet ⇒ nothing prepended.

## ⛔ V0 is WARN-ONLY. How a refusal would be earned.

The approval is explicit: **do not hard-refuse on recurrence, including families marked
`retryability: NEVER`.** `would_refuse` is recorded and not acted on.

The promotion rule must be **evidence-based, not a threshold picked now**. Before any refusal is
proposed, all five of these must be answerable from `preflight.invocations()`:

1. **False-positive rate of the match.** How often did a `warning_emitted` run turn out to have a
   genuinely different cause? Requires `eventual_failure_family` ≠ `prior_failure_family` to be
   inspected case by case, not counted.
2. **`refused_starts_later_shown_legitimate` in shadow.** How many `would_refuse=true` runs went on
   to a PASS or to a different family? On the historical replay this is **unanswerable** — none of
   the seven produced a PASS, so the shadow policy has never been contradicted *or* confirmed.
3. **Recurrence after warning.** Did `eventual_failure_family == prior_failure_family` fall once
   the packet was delivered? ⭐ **This is the hypothesis.** If it does not move, the packet is being
   delivered and ignored — `CHANNEL_WITH_NO_READER`, reproduced by the fix for it.
4. **Unclassified share.** If `unclassified_share()` climbs above ~50% of *classified* failures,
   the taxonomy is too narrow and a refusal built on family identity is refusing on a coin flip.
5. **Does the prevention check actually distinguish changed from unchanged attempts?** Today
   exactly one family has a check. A refusal policy resting on one check, on one family, on one
   ticket, is a policy with a sample size of one.

⛔ **No number is proposed here for any of the five.** Choosing "3 consecutive same-family failures"
today would be exactly the arbitrary constant this estate keeps finding — documented, accurate, and
then used as a cut-off four lines later.

## Kill criteria — stated before the evidence, so they cannot be chosen to fit it

Withdraw or rework the patch if:

1. `refused_starts_later_shown_legitimate` > 0 → the shadow policy is wrong; it stays shadow.
2. Median added context > 200 words → the packet is a dump; cut it.
3. After 10 further runs, `unclassified_share` > 50% → the taxonomy does not fit the failures.
4. ⭐ Recurrence stays flat while the preflight fires → the packet is delivered and ignored. This is
   the outcome to watch hardest, because it is this repository's most-repeated family reproducing
   itself inside its own remedy.
5. `reliability.metric_set().suspicious()` reports `known_failure_warnings` climbing over a zero
   `first_pass_green_rate` for more than one measurement period **without** a wired verifier landing
   — i.e. we are counting our own noise.

## Implementation priority (unchanged from the approval)

| class | items |
|---|---|
| **BUILD_NOW** ✅ done | run id · `failure_family` · attempt-history preflight · packet · metrics 7 & 9 · GP-327 replay test |
| **NEXT** | typed `HandoffContract` as a task evidence row · ACK/NACK discriminators · taxonomy enforcement in the findings suite · metrics 1/2/4 · a **typed provider exception** so a cap refusal stops being UNCLASSIFIED |
| **EXPERIMENT** | `ContextPack` injection (measure token cost first) · CURRENT-vs-V1 comparison · cross-ticket family matching |
| **DEFER** | client-review backend · all six wow features · anything touching the live mission |
| **REJECT** | `QUESTION`/`ANSWER` message types (F71 is OPEN and says don't) · `PROGRESS` (F73: alive ≠ working) · `TASK_ASSIGN` (duplicates the eligible set) · a second bus, findings store, hook, or `depends_on` field |

## The known gap this patch leaves open, named rather than buried

`ProviderError` is raised from a bare `RuntimeError`, so a cap-exhausted refusal and a terminal that
would not open are **indistinguishable to the caller**. The classifier therefore matches one literal
message prefix (`"attempt cap reached"`) and `tests/test_recurrence_preflight.py::test_the_cap_message_rule_has_not_rotted`
asserts `deploy.py` still emits it — the F19 anchor. Every other provider refusal is `UNCLASSIFIED`.

**The real fix is a typed exception in `provider.py`.** It is NEXT, not now, because it touches the
dispatch path the active mission will use.
