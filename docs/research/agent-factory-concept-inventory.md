# Concept inventory — the frozen baseline for a factory-vs-factory review

**Written 2026-08-22.** This exists so a survey of other agent-development factories can produce a
*diff* rather than a list of generic advice. It is the comparison basis, and it is deliberately
written **before** any external product is looked at.

Everything in §2 was enumerated from the code on 2026-08-22 and cites the module it came from.
Everything in §3 was read from the filed research answers. §4 is the only part that is an opinion.

---

## 1. The comparison basis, declared before looking

**What counts as "a concept":** a named, load-bearing idea that changes how the factory is built —
a boundary, a verdict taxonomy, a versioned object, a gate, a protocol. Not a feature, not a vendor
product name, not a library.

**What counts as "missed":** every candidate concept found in the survey is assigned exactly one of
five verdicts, and they are never collapsed — the same discipline `contract.py` applies to
assertions, applied to the review itself:

| Verdict | Means | Is it a gap? |
|---|---|---|
| `PRESENT` | We have it, under our own name | No |
| `RENAMED` | We have it under a different name — record the mapping | No, but the vocabulary gap is worth recording |
| `DEFERRED` | We have it in the do-not-build table **with a stated unlock condition** | **No — and this is the important one** |
| `ABSENT` | Genuinely not present and not deferred | **Yes** |
| `NOT-SEARCHED` | No pass has looked at this axis at all | Yes, but a different kind — it is a hole in the *review*, not the design |

`DEFERRED` is the trap this whole document exists to avoid. `README.md` and SYNTHESIS §6 carry an
explicit do-not-build list — separate architect LLM, mandatory tester LLM, agent↔agent messaging,
manager↔manager, army tiers, dynamic team-selection, ten team types, agentic gym, framework
migration, supervisor tiers — **each with an unlock threshold**. A survey run without that list in
hand will report all ten as gaps, and be wrong ten times.

**Rule for the survey:** a vendor claim is not a design premise. Tier every claim OBSERVED /
DOCUMENTED / MARKETED, per the standing rule in `R8` §7.

---

## 2. The concept surface as built — 26 concepts, measured from code

| # | Concept | As implemented | Module |
|---:|---|---|---|
| 1 | **Definition of done as a falsifiable object** | `GreenContract` — a named set of assertions, each returning (bool, detail) | `contract.py` |
| 2 | **Four verdicts, never collapsed** | `PASS` / `FAIL` / `UNMEASURABLE` / `NOT_RUN`; `Unmeasurable` is an exception a probe raises, not a return value | `contract.py` |
| 3 | **Probes refuse by default** | `Probes` return observed facts or raise; a dark instrument cannot read as healthy | `connector_contract.py` |
| 4 | **Domain contract, generalised** | A1–A12 for any connector; ordered preflight → certification → canary | `connector_contract.py` |
| 5 | **Contract is code, "green" is data** | `ConnectorTarget` loaded from a blueprint, so one contract judges every connector | `targets.py` |
| 6 | **The negative control** | `mutate_and_expect_failure` — breaks the world and asserts the contract stops being green. Gated by `test_eval_can_fail.py` | `evals.py` |
| 7 | **Corpus as tamper-evident data, not code** | Hashed documents + `MANIFEST.sha256`; `CorpusError` rather than silent degradation | `corpus.py` |
| 8 | **Provenance travels with the verdict** | `stamp()` / `provenance()` — what this was scored against, attached to anything published | `corpus.py`, `calibration.py` |
| 9 | **The config IS the version** | An agent is a (prompt, model, effort, tools, retry, turns, budget) tuple; change one and certification does not transfer | `blueprint.py` |
| 10 | **Version completeness as a gate** | `VERSION_DIMENSIONS` + `g_version_hash_is_complete` — the nine dimensions R2 said were missing are themselves measured | `readiness.py` |
| 11 | **Append-only, evidence-gated work ledger** | Current state is a fold over events; `EvidenceRequired` blocks a close with no evidence; nothing is overwritten | `tasks.py` |
| 12 | **Activity metrics cannot exist alone** | `GoodhartViolation` raised if an activity metric is registered without an outcome metric | `metrics.py` |
| 13 | **Readiness as 30 measured gates** | Each gate measures from a named file *at run time* and carries the path it measured from | `readiness.py` |
| 14 | **The board is generated, not maintained** | Task list derived from gates + dependencies; `critical_path()` is the unparallelisable chain | `board.py` |
| 15 | **Parallelism bound by file locality** | `conflicts()` computes which lanes write the same files — explicitly *not* the dependency graph | `lanes.py` |
| 16 | **Ranking must state its reason** | `recommend()` returns (lane, score, reason) — "a bare ranking is an oracle" | `lanes.py` |
| 17 | **One worktree per lane** | Structural isolation of parallel sessions | `worktrees.py` |
| 18 | **Dynamic mutual exclusion** | `claims` with staleness; stale claims still block, because hiding them makes a blocked lane look free | `claims.py` |
| 19 | **Live channel separate from durable record** | Per-lane append-only files, read cursors, re-deliver on crash, a lane never writes another lane's file | `bus.py` |
| 20 | **Corrections ledger, routed** | `findings.md` read as data; `AFFECTS` routes a correction to the lanes it hits; `malformed()` and `nothing_to_report()` are first-class | `findings.py` |
| 21 | **Closing a lane is a mechanism** | `finish()` — assert, push, release, announce; **never merges**; `checks()` separated so the tracker can show what would refuse | `finish.py` |
| 22 | **Handoff generated from measured state** | Lane handoff and cross-lane session handoff, both assembled from measurement rather than recall | `handoff.py` |
| 23 | **Human blockers declared up front** | `needs_paul` + recorded operator answers appended to a lane's prompt | `operator.py` |
| 24 | **Evaluator as a principal, not a function** | Three fields in, verdict out; the client cannot name a corpus or manifest; the service resolves everything from its own config; write-once verdict store; `endpoint_mode()` ranks the *deployment*, not the design | `evaluator.py`, `evaluator_service/` |
| 25 | **Bounded deployment** | Worktree + turn cap + dollar cap + `AttemptLedger` persisted so a cap survives restart | `deploy.py` |
| 26 | **The research record checks itself** | `synthesis.unsynthesised()` detects filed answers the decision record has never mentioned; enforced by a test | `synthesis.py` |

Two presentation-layer concepts sit alongside, and are unusual enough to be worth naming in any
comparison: **`crew.py`** — a persona/vocabulary skin where ids never change, and which *refuses* to
translate an epistemic label rather than returning it unchanged — and **`schedule.py`**, which
answers "when will this be done" by declining to produce a date it cannot support.

### Measured state of the gate suite
**`30` readiness gates registered** in `readiness.GATES` — by phase: certification 8, judgement 8,
handover 7, bounded 4, loop 3. `15` test modules.

⚠ An earlier draft of this file said 27, from counting `def g_` functions rather than the registry.
Three gates use check functions that do not carry the prefix. Corrected 2026-08-22 — and recorded
rather than silently fixed, because it is this document's own rule (**enumerate the registry, not
the source text**) failing on its first use. The last calibration run reported
`connector-e2e/windsorai@GEP: UNMEASURABLE (PASS=11, UNMEASURABLE=1)` — A12 blocked on undeclared
tenant scope.

---

## 3. What R1–R9 already settled — the do-not-re-ask list

Nine research documents; **seven have filed answers** (~370 KB in `answers/`). Hand this section to
any surveyor so the review does not buy the same answer twice.

| # | Asked | Status | The verdict, in one line |
|---|---|---|---|
| R1 | Grade the eval harness | answered, synthesised | Keep GreenContract as the authoritative verifier; **do not** replace it with a general LLM-eval framework. Inspect AI only later, as a runner shell. The weak parts are control-plane, not eval sophistication |
| R2 | One agent or a team | answered, synthesised | **Do not build the three-agent team.** One worker + non-LLM verifier + human for privileged ops. Multi-agent averaged −3.5% across 180 configurations; sequential tasks degraded 39–70% |
| R3 | Control plane, bounding, tenancy, optimizer | answered, synthesised | Do not optimise yet. Make it bounded, reapable, fail-closed, independently evaluable first. Tamper-evidence is not a trust boundary; an external evaluator **service** is |
| R4 | Can the optimiser be repo-agnostic | answered, synthesised | Not yet — but build repo-agnostic *interfaces* now, because they are cheap now and expensive to retrofit. Covers DSPy/MIPROv2, GEPA, TextGrad, Trace, OpenEvolve, AlphaEvolve |
| R5 | Build velocity | answered, synthesised | Lean runner with sandbox + circuit-breakers is the gating step. **Worktree per agent** — 41.7% cross-agent PR conflict rate, mostly structural |
| R6 | Automation and alerting | answered, synthesised | Branch-per-lane as observed practice, merged one at a time |
| R7 | Session manager | answered, **synthesised 2026-08-22 as §11** | Switchboard = inspiration not adoption. New: **bounded autonomy as a designed surface** (five auto-actions, each refuse-by-default). ⛔ Its proposed fitness proxy — readiness gates — is **rejected**, it is the never-optimise list. Graded **weaker evidence than R1–R6** |
| R8 | A factory for **data** engineering, not software | **written, NOT DISPATCHED** | — |
| R9 | Game-styled supervision UI | **written, NOT DISPATCHED** | — |

Also settled and worth not re-litigating: the build order (SYNTHESIS §5, nine steps, optimisation
last), the never-optimise list (retry caps, gate thresholds, tenancy checks, timeouts, evaluator
thresholds, corpus — *safety specification, not hyperparameters*), and the screening order for when
search does start (model ≫ effort ≫ tool interface ≫ context layout ≫ prompt structure ≫ wording).

### Baseline currency — closed 2026-08-22
The repo's own currency gate was red when this file was written:
```
factory.synthesis.unsynthesised() -> ['R7']     pytest tests/test_synthesis_current.py -> FAILED
```
R7 has since been read and folded in as `SYNTHESIS.md` §11. Re-measured:
```
factory.synthesis.unsynthesised() -> []         pytest tests/test_synthesis_current.py -> PASSED
```
**The baseline is frozen.** R8 and R9 remain written-but-not-dispatched, and the survey should not
pre-empt them — R8 in particular owns the data-engineering framing and would collide.

---

## 4. Where the survey should actually look

Given §2 and §3, most single concepts a generic survey would return are already `PRESENT` or
`DEFERRED`. These are the axes where I can find **no pass that has looked at all** — the
`NOT-SEARCHED` list, and therefore the whole value of the exercise:

1. **Product-concept vocabulary from named factories.** R1–R9 are literature- and practice-driven.
   No pass has asked what **Claude Agent SDK / Agent Teams / Skills, OpenAI AgentKit, Google ADK +
   Agent Engine, Microsoft Agent Framework + Foundry, LangGraph Platform, CrewAI, Factory.ai,
   Cognition, Sierra** ship *as concepts* — what objects they make first-class that we have no name
   for. This is the closest thing to a literal answer to "concepts we may have missed".
2. **Observability and trace standards.** R1 was scoped to *eval frameworks* and concluded "don't
   add one" — that verdict does not cover **tracing**. OpenTelemetry's GenAI semantic conventions,
   Langfuse / LangSmith / W&B Weave trace stores, and the question of whether a certified run should
   emit a standard-shaped trajectory are untouched. `deploy.py` streams a transcript; there is no
   structured trajectory object.
3. **Task and environment packaging standards.** METR's task standard, Inspect's task format,
   SWE-Gym / verifiers-style environment packaging. Relevant because the deferred "agentic gym" is
   partly a packaging question, and a standard format would make the corpus portable.
4. **Interop as a factory primitive.** MCP is used across the estate but is not a factory concept
   here; A2A / AGNTCY agent-interop protocols were deferred as *messaging topology* (correctly), but
   not examined as an **interface standard** — a different question.
5. **Post-run learning.** Nothing in §2 accrues knowledge between certifications. No pass has asked
   whether it should, or what would make it safe. Genuinely `ABSENT`, not `DEFERRED` — there is no
   unlock condition recorded for it either way, which is itself the finding.
6. **Mid-run human approval and escalation.** `operator.py` handles blockers *declared before the
   session*. R5 calls for "a human approval step before any container launch" and it is unbuilt.
   R9 asks what the operator *sees*, not what the approval **workflow** is. The gap between those
   two is unexamined.
7. **Compensation and rollback semantics.** "Side-effect replay semantics" is listed as a missing
   version dimension, and R8 §0 names the sharp version — `git revert` does not undo a dropped
   table. Nobody has designed the compensating action.

### Two axes deliberately excluded from the survey
- **Anything R1–R6 settled.** Re-asking buys the same answer at full price.
- **Team topology.** R2 answered it with 180 configurations of evidence. A product survey will
  return marketing that contradicts it; that is not new information.

---

## 5. How to use this file

1. ~~Fold R7 into `SYNTHESIS.md`~~ — **done 2026-08-22**, gate green.
2. Run the survey against §4's seven axes only, with §1's five verdicts and §3's do-not-re-ask list
   in hand.
3. Every returned concept gets one verdict and a citation. A concept with no citation is a rumour.
4. The output is a **diff**, not a list: `ABSENT` items become candidate gates in `readiness.py`;
   `RENAMED` items become vocabulary notes; `DEFERRED` items get their unlock condition re-checked
   against whatever new evidence the survey found.
