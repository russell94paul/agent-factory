# Agent Communication Protocol v1 — ⛔ DESIGN. Nothing here is built.

**Priority: NEXT.** It is written down so it is not re-derived, **not so it is built now.** The
hypothesis under test is much smaller (see [README](README.md)), and this protocol is not required
to prove it.

## The envelope

⚠ **Not a new module and not a new stream.** `factory/protocol.py` would hold only the dataclass and
its validators; the write path is `events.RunLog._emit`, and the closed `KINDS` tuple grows by one
entry per message type. ⛔ `factory/bus.py` remains the live ephemeral channel and is not touched.

```
protocol_version  "1"                    run          events.py run id — the join
mission_id        task parent id         task_id      TaskStore id
sender/receiver   {kind: agent|manager|task|human, id}
message_type      one of six (below)     seq          monotonic per RunLog; the authority
```

Body, every field mapped onto something that already exists:

| field | reuses |
|---|---|
| `objective` | `Ticket.prompt_task` / task title |
| `inputs` / `outputs` | `context.ContextRef` — already carries source + checked-on + `UNVERIFIED` default |
| claim states | ⭐ `tasks.add_evidence` already has `MEASURED\|DERIVED\|ASSUMED`. Add `INFERRED` and `UNKNOWN` **to that vocabulary**, do not start a second one |
| `decisions` | promoted to a finding with `KIND=DESIGN` when durable |
| `blocked` / `unlocked` | `TaskStore.block()` / `unblock()` — live, 25 edges |
| `verification` | `contract.Verdict`, the enum. `events._verdict_value` already refuses a string |
| `required_receiver_behavior` | closed enum: `CONSUME · VERIFY_THEN_CONSUME · DECIDE · NONE` |
| `ack_required` | bool, defaulted by message type |
| `failure_family` | ✅ already built — `preflight.FAMILIES` |

## Six message types, not eleven

| keep | why |
|---|---|
| `HANDOFF` | carries state across a boundary. The whole point |
| `BLOCKED` | already a bus kind and a task event; the only thing that stops a waiter waiting |
| `DECISION_REQUEST` | the only one that must reach a human |
| `FAILURE` | carries `failure_family` |
| `COMPLETE` | terminal; already `run_finished` |
| `ACK` / `NACK` | without it, `HANDOFF` is a broadcast — which is what we have now |

**Rejected, with reasons:**

- ⛔ `QUESTION` / `ANSWER` — **F71 is OPEN and says do not build this until a real case appears.**
  Every real cross-lane question so far needed a *human* (a credential approval, a go/no-go).
  Building agent-to-agent request/response before one exists is inventing a requirement.
- ⛔ `PROGRESS` — F73 and R6: *alive ≠ working*. A progress ping is a heartbeat wearing a report's
  clothes.
- ⛔ `TASK_ASSIGN` — `agent_dispatched` plus the eligible set already record this. A second record
  of the same fact is where contradictions come from.
- ⛔ `DECISION` — a `HANDOFF` whose body carries a decision.
- ⛔ `WARNING` — `ACK_WITH_WARNINGS` carries it. A kind nobody must act on is decoration.

## Boundaries — four moments, never a tool call

Task claim · task close · cross-agent handoff · human decision request. `bus.py`'s `MAX_LEN = 2000`
applies: longer than that is a document and belongs in `docs/evidence/`.

## Acknowledgement — six states, each with a deterministic discriminator

| state | test | meaning |
|---|---|---|
| `ACK` | every `outputs[].ref` resolves; no NACK condition | consumed |
| `ACK_WITH_WARNINGS` | resolves, but ≥1 load-bearing claim is `INFERRED`/`ASSUMED` | consumed, uncertainty carried |
| `NACK_INCOMPLETE` | an `outputs[].ref` does not resolve on disk | a caught missing artifact |
| `NACK_CONTRADICTORY` | a claim contradicts one already `MEASURED` upstream in the same mission | caught contradiction |
| `NACK_STALE` | referenced artifact's sha/mtime is newer than the handoff's | caught stale context |
| `NACK_UNVERIFIED` | `verification` is `UNMEASURABLE`/`NOT_RUN` but behavior is `CONSUME` | ⭐ the UNMEASURABLE-as-PASS collapse, intercepted |

⭐ **A NACK is a SUCCESS event.** It records `UNMEASURABLE` on the *handoff*, never `FAIL` on the
mission, and increments `handoff_intercepts` — an **outcome** metric, so `factory.metrics` will
accept a defect-count activity metric anchored to it.

**ACK required** when the handoff crosses agents, unlocks a blocked task, or
`required_receiver_behavior != NONE`. **Not required** for same-agent sequential steps, `COMPLETE`
on a leaf task, or anything inside one turn.
