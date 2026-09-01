# Quality gates — ⛔ DESIGN, except the one that is built

**Six of seven are fully deterministic.** That is the design constraint, not a coincidence: an
agent asked to introspect on whether it handed over enough context will answer yes.

| gate | deterministic? | judgement? | human? | on failure | evidence artifact | status |
|---|---|---|---|---|---|---|
| `CONTRACT` — the handoff validates against the schema | ✅ full | – | – | `NACK_INCOMPLETE`; sender retries | the rejected document | ⛔ DESIGN |
| `DEPENDENCY` — every `blocked_by` cleared at claim time | ✅ full (`TaskStore` replay) | – | – | refuse start; `dependency_violations++` | the task event log | ⚠ **metric BUILT**, gate DESIGN |
| `CONTEXT` — every `artifacts_to_consume` ref resolves and its sha matches | ✅ full | – | – | `NACK_STALE` / `NACK_INCOMPLETE` | resolution log | ⛔ DESIGN |
| `KNOWN_FAILURE` — the matched families' prevention checks ran | ✅ match is deterministic; ⚠ the check itself may not exist | partial | – | ⛔ **WARN only in V0.** Never refuses, including `retryability: NEVER` | the packet + `preflight_checked` | ✅ **BUILT** |
| `OUTPUT_CONTRACT` — `expected_output` exists, non-empty, right evidence class | ✅ full | – | – | refuse close | file + `evidence.coverage()` | ⚠ half-built: `tasks.close(require=…)` exists and is opt-in per call |
| `VERIFICATION` — a `GreenContract` assigned the verdict | ✅ full | – | – | the verdict stands as measured; ⛔ `UNMEASURABLE` never becomes `PASS` | `verdict_assigned` | ✅ **BUILT** |
| `BLAST_RADIUS` — WRITE outside the declared `resource_claim`, or any prod/credential touch | ✅ detect | – | ⛔ **required** | refuse; `DECISION_REQUEST` to a human | `.data/credential-use.jsonl` | ⚠ ledger exists; the gate does not |

## Notes that are not obvious from the table

**`DEPENDENCY` must replay, not fold.** The question is *was this task blocked when somebody took
it*. `TaskStore`'s folded state only knows what is true now, and a task blocked after being claimed
is not a violation. `reliability.dependency_violations()` replays in file order for this reason.

**`KNOWN_FAILURE` is the only gate with a judgement component**, because the prevention check for
most families does not exist yet and `NOT-RECORDED` is the honest answer. Inventing a check that
returns `True` would be F18 — a probe that hands itself the state it wants to see.

**`BLAST_RADIUS` is the only mandatory human gate**, and it reuses the one real approval ledger in
the estate. ⚠ Note that `needs_paul` on `Lane` and `Preset` is **display-only** today: it renders,
it does not refuse. A gate built on it would be a declaration without a mechanism — the family this
estate has recorded three times.

**⛔ No gate may run pytest.** `handoff.preflight()` does, and it is correctly a *close-time report*
rather than a start-time gate. A start-time gate that costs 200 s is one people route around, and
the routing-around is invisible.
