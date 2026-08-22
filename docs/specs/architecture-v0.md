# Initial architecture — v0

**Written 2026-08-22, before R8 was dispatched.** This is a **strawman to be attacked**, not a
conclusion. It exists because an open research question gets a survey back, and a concrete proposal
gets an argument back — and an argument is more useful.

Every decision carries how much evidence it rests on:

`MEASURED` we ran it and have the number · `DERIVED` computed from something measured ·
`REASONED` an argument from constraints, no measurement · `BET` a judgement call that could be wrong

---

## 1. The one-sentence shape

> Four planes with a hard boundary between them — **decide**, **run**, **prove**, **approve** — where
> an agent's isolation tier is chosen by *what it touches*, not by what it is.

The second half is the only genuinely novel claim here, and it is the one to attack first (§7).

---

## 2. Why the current shape runs out

What we have works and is capped. Both halves are measured.

| | Current | Evidence |
|---|---|---|
| Isolation unit | git worktree on the operator's machine | `MEASURED` 3 lanes, 20 commits, **zero** cross-lane conflicts |
| Concurrency ceiling | **3** | `DERIVED` max independent set of the conflict graph in `lanes.py` |
| Why capped | two lanes editing one file | `MEASURED` 41.7% conflict rate on a shared branch (R5) |
| Execution environment | the operator's shell, the operator's credentials | `MEASURED` — there is no sandbox |
| Data blast radius | unbounded | `MEASURED` — no dry-run gate, no row-count diff, no rollback capture |
| Cost | unknown | `MEASURED` — nothing records tokens or wall clock |

⭐ **The ceiling is not a concurrency limit, it is a *file* limit.** Lanes conflict because two
agents would edit `pipelines.py`. That is a property of code work. **Data work does not conflict
that way** — two agents building two views in two schemas share no file and no row. So the cap is
an artefact of treating all work as one kind. `DERIVED`

That observation is what §4 is built on, and §7 is where it might be wrong.

---

## 3. The four planes

```
┌─────────────────────────────────────────────────────────────────────────┐
│  APPROVE   humans only. merge · per-secret grant · promote to prod      │
│            never automated — finish() already refuses to merge          │
└───────────────▲─────────────────────────────────────────┬───────────────┘
                │ evidence bundle                          │ decisions
┌───────────────┴─────────────────────────────────────────▼───────────────┐
│  PROVE     readiness gates · GreenContract · findings.d · run audits    │
│            the evaluator is a SEPARATE PRINCIPAL the agent cannot be    │
└───────────────▲─────────────────────────────────────────┬───────────────┘
                │ artefacts + measurements                 │ certify request
┌───────────────┴─────────────────────────────────────────▼───────────────┐
│  RUN       the isolation ladder — T0 worktree · T1 container ·          │
│            T2 container + ephemeral warehouse clone                     │
└───────────────▲─────────────────────────────────────────┬───────────────┘
                │ claims · bus · finish                    │ dispatch
┌───────────────┴─────────────────────────────────────────▼───────────────┐
│  DECIDE    conflict graph · claims · scheduling · caps · budgets        │
│            the bespoke build plane at :8765 (does NOT import Prefect)   │
└─────────────────────────────────────────────────────────────────────────┘
```

The boundary that matters is between **RUN** and **PROVE**: the thing being measured must not be
the thing doing the measuring. R3 ranks a separate local process as **rank 5, "mostly theatre"**,
so this is currently aspirational — the evaluator has to become a principal with its own identity
and its own credentials before this diagram is honest. `REPORTED`

---

## 4. The isolation ladder — the load-bearing idea

**An agent's isolation tier is chosen by what its task touches, declared up front, and enforced —
not chosen by what kind of agent it is.**

| Tier | Environment | May touch | Cost | Use for |
|---|---|---|---|---|
| **T0** | git worktree, operator machine *(built)* | repo files only. **No network egress, no DB verbs** | free | code edits, docs, specs, tests |
| **T1** | container, egress allowlist, read-only warehouse role | repo + **SELECT** on real data | seconds to start | analysis, reconciliation, "is this number right" |
| **T2** | container + **ephemeral zero-copy clone schema**, dropped on exit | repo + full DDL/DML **inside the clone only** | clone is cheap; compute is not | building views, migrations, backfills |

Three consequences, and they are the argument:

1. **T2 removes the file-conflict cap for data work.** Two agents in two clone schemas conflict on
   nothing. The 3-lane ceiling applies to T0 code lanes and does not generalise. `DERIVED`
2. **The dangerous verb is contained by construction, not by prompt.** "Do not touch prod" in a
   prompt is a request; a role with no grant on prod is a control. This directly answers the thing
   generic agent frameworks miss — isolating a filesystem does nothing when the risk is DDL on a
   shared warehouse. `REASONED`
3. **Promotion out of a clone is an APPROVE-plane act.** The evidence-gated rule already says prove
   the target, validate at the consumer's layer, prove no regression, capture a rollback. That
   becomes the clone→real diff, which is *mechanically producible* from a T2 run. `REASONED`

**The tier is declared in the agent spec and enforced by the DECIDE plane.** An agent that asks for
a verb its tier does not carry is refused, and the refusal is an audit event — which also gives the
`refuses` gate something real to record, since **0 of 22 gate events have ever been a refusal**.
`MEASURED`

---

## 5. The agent as an artefact

Today an agent is a `Lane`: a prompt string, a model, a gate list. That is a launcher input. The
`hash` gate wants 15 dimensions and covers **0**. `MEASURED`

```yaml
AgentSpec:
  id: navira-view-builder
  version: 7                    # bumped on ANY field below — that is the point
  prompt_ref: prompts/view-builder@a3f9c1     # content-addressed, never inline
  model: sonnet
  effort: medium
  tools: [read, edit, bash, snowflake_ro]
  tier: T2                      # <- chooses the sandbox, §4
  budget: {tokens: 400k, wall_clock: 45m, warehouse_credits: 2}
  contract: green@v5            # which assertions must pass to be certified
  gates: [grain, no-regression, consumer-render]
  needs_human: [credential-grant, merge, promote]
```

Two rules that follow:

- **The version hash covers every field.** A certification granted under `green@v4` must not
  silently transfer to `v5` — R3 names `contract_version` as the dimension that bites now. `REPORTED`
- **A spec with a field nothing reads is worse than no field.** This month produced a `--model` flag
  in a dead variable, a detector degrading to 1 finding instead of 313, and gates reporting PASS
  while measuring nothing. **Every field needs a test asserting it reaches the process.** `MEASURED`

**Manufacturing**: a new agent is made from a blueprint + a target, and the factory's own output is
a *spec*, not a session. That is the manufacturing step the repo currently does not have. `BET`

---

## 6. Communication — mostly built, one thing deliberately not

| Need | Mechanism | State |
|---|---|---|
| Durable corrections between agents | `docs/findings.d/`, one file per finding, in git | built |
| Live nudge during a run | `.data/bus/`, one append-only file per writer, hook-injected | built today |
| Claiming a resource | `factory/claims.py` — refuses overlap, does not auto-expire | built |
| Closing out | `factory/finish.py` — assert, push, announce, release, **never merge** | built today |
| Agent asks another agent a question | **not built, deliberately** | F71 OPEN |

The record and the channel are separate because one file could not be both: three isolated
worktrees each appended their own `F11` and `F12` and would have destroyed two of each on merge.
`MEASURED`

**Request/response between agents stays unbuilt until a real case appears.** Every question that
actually arose needed a *human* — a credential grant, a go/no-go. Building agent-to-agent dialogue
before a case exists is inventing a requirement. `REASONED`

**The reviewer becomes structural.** On 2026-08-22 an independent reviewer found **6 real defects**
in one lane's own diff, and another found 4 more — "three of them mine and one of them severe". That
is currently a habit inside a prompt. It should be a required stage between RUN and PROVE. `MEASURED`

---

## 7. Where this is most likely wrong — attack these first

1. **The isolation ladder may not survive contact with Snowflake's actual clone semantics.** A
   zero-copy clone is cheap to create; the compute to validate against it is not, and a clone of a
   share may not behave like the real thing. If T2 is not actually cheap, §4 collapses and the
   ceiling stays at 3. **This is the single highest-value thing for R8 §2.3 to check.** `BET`
2. **"Data work does not conflict" is asserted, not measured.** Two agents building two views can
   absolutely conflict — on a shared dimension table, on a naming convention, on the same
   `REPORT_COMMON` object. The conflict graph may just need different edges, not fewer. `BET`
3. **Four planes may be three.** PROVE and APPROVE may not separate cleanly when the evidence a
   human needs is itself produced by the thing being judged. `REASONED`
4. **T1/T2 assume containers on Windows via WSL**, unmeasured here, and start-up cost is a guess.
5. **This whole document assumes the lane model is the right abstraction.** R8 is explicitly asked
   whether worktree-on-one-machine is a stepping stone or a dead end. If it is a dead end, most of
   §4 survives (the ladder is about *what is touched*) and most of §3 does not.

---

## 8. Sequence — smallest change, largest effect first

| # | Change | Why first | Cost |
|---|---|---|---|
| 1 | **Run the loop once, for real, with the new primitives** | Two gates read UNMEASURABLE because nothing has run. No architecture decision should precede a single real run. | hours |
| 2 | **Instrument cost** — tokens + wall clock on the `finished` bus event | Every claim about a cheap lane is currently reasoning. Cheapest possible measurement. | hours |
| 3 | **AgentSpec + a real version hash** | Unlocks certification meaning anything; 0 of 15 dimensions today. | days |
| 4 | **T1 container with an egress allowlist** | First actual isolation. Proves the container story on Windows before anything depends on it. | days |
| 5 | **Reviewer as a required stage** | Highest measured defect yield of anything we did this month. | days |
| 6 | **T2 ephemeral clone** | The big one, and the one most likely to be wrong — do it after 4 proved the container path. | weeks |
| 7 | Corpus strata (1 case → 29+) | Certification cannot detect anything until this moves. | weeks |

**Not yet:** agent-to-agent dialogue, a self-improving prompt loop, remote/distributed execution,
any framework migration. Each needs a case that does not exist.

---

## 9. What this does not change

- **Merging stays human.** `finish()` refuses it and should keep refusing.
- **Per-secret approval stays human.** Any tier that self-serves credentials is out, however elegant.
- **Evidence-gated deploys stay.** Prove the target, validate at the consumer's layer, prove no
  regression, capture a rollback. The ladder is a way to *produce* that evidence mechanically, never
  a way around it.
