# Synthesis — what four research passes concluded, and what changes

**2026-08-21.** Five documents, ~293KB: R1 eval harness, R2 topology, R3 control plane, R4
agnostic optimiser (twice). This is the decision record. Where the answers disagree, or where they
contradict something already built or already said in this session, that is recorded rather than
smoothed.

Raw answers in `answers/`. Read them before overriding anything here.

---

## 1. The convergence — four independent passes, one verdict

None of the four prompts asked "should we optimise". Three of them volunteered the answer anyway,
and the fourth was asked and said no.

| | Verdict, in its own words |
|---|---|
| **R1** | *"The weakest parts are not primarily LLM-eval sophistication. They are control-plane problems."* And: *"adding another eval framework today would not materially improve your assurance."* |
| **R2** | *"Control-plane changes are more urgent than agent architecture."* |
| **R3** | *"This system should not be optimised yet. It should first be made bounded, reapable, fail-closed and independently evaluable."* |
| **R4** | *"The immediate problem is not lack of an optimiser. It is that the current experiment is not yet a reliable experiment."* |

Four passes, four literatures, one conclusion. That is as close to a settled answer as this exercise
can produce, and it should be treated as settled unless new measurement contradicts it.

**The mechanism they all name:** an optimiser cannot distinguish a better agent from a
configuration that happened to encounter fewer infrastructure failures. R4 supplies the empirical
teeth — work strengthening SWE-bench found **77% of its 500 Verified instances had at least one
semantically altered variant that survived the original tests**, and a separate analysis rejected
**19.78% of 11,041 supposedly-solved patches** once tests were strengthened. Optimise against an
under-constrained oracle and apparent performance rises while correctness does not.

## 2. What they say we got right

Worth stating, because most of this section survived contact with four reviewers.

- **The four verdicts, never collapsed.** SOUND. The labels are ours; the distinction is supported.
- **Probes refuse by default.** SOUND — *"particularly appropriate given your historical failure
  mode."*
- **The mutation registry.** SOUND **as a floor**, not as an adequacy criterion.
- **The structural repair after the partial-extraction false positive.** SOUND — *"exactly the kind
  of evaluator defect negative controls should expose."*
- **Session-stamp freshness.** SOUND.
- **`EXECUTION_TERMINATED` vs `CONTRACT_PASS`.** Graded **A**. *"Essential."*
- **Lease/heartbeat + orphan timeout.** **A**. Established distributed-systems practice.
- **External concurrency limits.** **A**, and *"urgent"*.
- **`producer_done != handoff_done`.** **A**. Completion needs a downstream acceptance receipt
  bound to the exact producer output.
- **External ownership of the retry cap.** **A-**.

**Keep the GreenContract.** R1's tooling verdict: *"Keep GreenContract as the authoritative domain
verifier. Do not replace it with a general LLM-eval framework."* Inspect AI is the only candidate
worth adding later, as a runner shell, not a replacement.

## 3. What they say we got wrong

### 3.1 The three-agent team — do not build it

R2, directly: *"Start with one end-to-end implementation agent, not the three-agent architect →
implementer → tester team."*

```
control plane → ONE worker agent (inspect, plan, implement, self-test, repair)
              → non-LLM VERIFIER, clean environment, immutable contract
              → control plane → privileged operation? → HUMAN
```

No LLM manager. No LLM architect. No LLM tester. No agent-to-agent channel. State passes through
typed persisted artefacts. The worker may run tests repeatedly for feedback but **cannot author the
authoritative PASS bit**.

Evidence: 180 configurations across 5 architectures, 3 model families, 4 agentic benchmarks —
multi-agent averaged **−3.5%**, sequential tasks degraded **39–70%**, and gains diminished once a
single-agent baseline exceeded ~45%. Anthropic's 90.2% multi-agent result is breadth-first research
at ~15× tokens, and their own guidance says coding is less parallelisable.

`blueprints/orchestrator_team.yaml` is marked superseded and kept, with the unlock threshold in the
file.

### 3.2 Calibrating on one run is not calibration — FOLKLORE

The only decision graded below SOUND. The run is real and stays as `positive_real_001`; the problem
is that one case cannot calibrate anything. R1's arithmetic:

| Blind spot affects | Cases for 95% chance of seeing ≥1 |
|---|---:|
| 10% of the stratum | 29 |
| 5% | 59 |
| 1% | 299 |

> *"One example per failure class has essentially no calibration meaning."*

**The method, which is buildable now:** two distributions, never one.

- **Regression corpus** — every semantically distinct historical failure, **not frequency-weighted**.
  *"Your observed distribution is endogenous to a badly broken system"*: weighting to match event
  counts teaches the eval to imitate the runtime's defects. Deduplicate identical signatures but
  keep their count as metadata.
- **Challenge corpus** — stratified across 15 named mechanisms (identity/auth, container/bootstrap,
  SDK drift, pagination/completeness, tenant scope, schema drift, timeouts, duplicate/idempotency,
  stale state, orchestration/liveness, Snowflake load semantics, downstream BI visibility,
  evaluator failure, gate failure, tamper/reward-hacking). **Not prevalence-weighted.**
- **The 352 unclassified stay their own stratum.** *"Unclassified is itself a first-class stratum
  until someone demonstrates otherwise."* Do not redistribute them into the five known classes to
  get a clean pie chart — that is what the retired 8-pattern classifier did.
- **Manufactured positive worlds** vary structural dimensions (single vs multi-account, pagination,
  legitimate zero-row, full vs incremental, schema variants, auth forms). ⭐ These are
  **scorer-validation fixtures, not evidence the agent can create those worlds.**

### 3.3 Our tamper-evidence is not a trust boundary, and moving files will not make it one

R3 ranks the options for our actual threat model — an LLM agent with shell access, not a malicious
admin:

| Rank | Measure | Value |
|---:|---|---|
| 1 | **External evaluator service with separate identity** | Strongest real boundary |
| 2 | Separate evaluator credentials the agent cannot reach | Essential ingredient |
| 3 | Separate repo, agent has no write permission, evaluator fetches independently | Worth doing; cheap |
| 4 | Signing key held outside the agent sandbox | Useful for provenance, optional initially |
| 5 | Separate local process | **"Mostly theatre"** |

> *"Moving only the files to another directory changes nothing; moving ownership/credentials out of
> the agent's capability set does."*

This retires the plan implied by `$AGENT_FACTORY_EVALS`. The corpus does not need a different
directory — the **evaluator needs to be a service the agent cannot impersonate**. A signing key is
not required for v1 if the evaluator service is the only principal that can write verdicts.

### 3.4 Our version hash misses nine things

`blueprint.py` hashes prompt/model/effort/tools/retry/turns/budget. R2 says that is not the agent:
tool *implementation* drift (same `tools=["shell","git"]`, different CLI versions), sandbox/image
drift, model routing (provider + requested id + provider-returned metadata), context-management
drift (compaction, truncation, retrieval order), external knowledge drift, **permissions** — *"an
agent with prod credentials is not the same certified object as one without them"* — **verifier
drift** (certification against contract V4 must not silently transfer to V5), harness drift, and
side-effect replay semantics.

Verifier drift bites us today: the corpus is hash-pinned, but the contract version is not in the
agent hash, so a certification can outlive the thing that granted it.

## 4. Corrections to things said in this session

Recorded because a synthesis that quietly drops its author's errors is not a record.

**⛔ Offline replay does not make configuration search cheap.** I said it turned "32 years into a
lunch break". R3: *"Recorded evidence describes the old configuration's output. Unless you have a
simulator that faithfully changes the generated trajectory when the configuration changes, replay
is useful for evaluator regression and re-scoring, not for producing a score for an unrun candidate
configuration."* Replay scores **the evaluator**, not a candidate config. The real cost stands:

| Naive search | Migrations | Agent-hours | Wall time at 4× parallel |
|---|---:|---:|---:|
| 10 configs × 3 replicates | 30 | 792 | 8.25 days |
| 20 configs × 3 replicates | 60 | 1,584 | 16.5 days |

And that excludes the 1,001 failed attempts whose cost is unrecorded, so *"there is no honest dollar
estimate of optimisation cost"* until telemetry is fixed.

**⛔ The false `succeeded` is not Prefect.** R1 diagnosed it as Prefect's final-state rules; I
carried that into R3 as a whole question without walking the route. `orchestrator/pipelines.py` does
not import Prefect. The mechanism is a **last-write-wins per-stage status field** used as evidence
about a history — a stage that failed 100 times and succeeded on 101 reads `completed`, so
`any_failed` is False. Full writeup in `../evidence/false-succeeded-mechanism.md`. R3's Q4 answer is
therefore about the wrong plane; everything else in R3 is unaffected.

**⚠ R2's control-plane prescription assumed Prefect primitives we do not have on this plane.** It
cites Prefect's configured retry limits, tag-based concurrency and zombie handling as available.
The build plane is a bespoke engine, so attempt caps, leases, orphan timeouts and concurrency
reservation must be **built**, not enabled. Neither R1 nor R2 knew this. It changes implementation
cost, not direction.

## 5. The build order

R3's prerequisite chain and R4's sequence agree. Merged, with the two corrections above folded in:

```
1  hard external attempt / spend / concurrency budget      ← non-negotiable
2  cloud timeout + cancellation + orphan reaping + restart reconciliation
3  terminal verdict computed from append-only history, not current state
4  refusal-capable gates, with negative drills
5  tenant capability isolation at every persistence/promotion boundary
6  complete attempt/cost telemetry, including failures
7  external evaluator trust boundary (a service, not a directory)
8  expand and freeze the evaluation corpus
9  ── only here ── configuration experiments
```

Steps 1–4 are non-negotiable per R3. Steps 5–7 must also precede optimisation *"because otherwise
the optimisation score itself is not safe to trust."*

Step 3 is ours, not R3's: R3 said "Prefect failure propagation", which is the wrong plane. The
correct form is a terminal verdict derived from the append-only event log.

## 6. What not to build, and what would unlock it

From R2's deferral list and R3's do-not-optimise table.

| Do not build | Unlock evidence |
|---|---|
| Separate architect LLM | Same-budget A/B: ≥10pp terminal-success gain or ≥20% efficiency, no new seam failures |
| Mandatory tester LLM | A non-executable criterion where blinded LLM judgement demonstrably improves agreement with experts |
| `agent ↔ agent` messaging | Production-like tasks with genuine concurrent branches and ≥5pp net gain after coordination cost |
| `manager ↔ manager` | Several independently certified teams plus a measured inter-team bottleneck |
| `army → managers` / `army ↔ army` | ≥3 stable team types and evidence one manager is a real bottleneck; no production evidence found for peer-army at all |
| Dynamic team-selection LLM | ≥200 adjudicated examples plus static misrouting ≥10% |
| Ten team types | A specialist only when enough tasks show it beats the generic worker |
| Agentic gym | A stable verifier plus hundreds of clean labelled trajectories — *"training on current traces risks learning pathological loops"* |
| Framework migration | Fault injection showing an invariant our engine cannot satisfy and a candidate can |
| Supervisor tiers | Build the data model so one *could* be added; instantiate zero supervisor LLMs |

**Never optimise:** retry caps, gate thresholds, tenancy checks, timeout/concurrency limits,
evaluator thresholds or corpus. These are safety specification, not hyperparameters. *"Optimising
eventual success can simply reward more retries."* And optimising on the candidate's own score
*"changes the ruler rather than the system."*

**When search does start**, screen in this order: model (very high — published work shows 9–13pp
differences between backends), reasoning effort (high, no transferable number), tool interface
(high), context layout (high–medium), system-prompt structure (medium), prompt micro-wording (low —
*"do not spend live 11-hour evaluations searching commas"*).

## 7. Where the answers disagree

The most useful section, per the rule that agreement is the control and divergence is the finding.

1. **How agnostic, how soon.** R4 is more permissive than R3: *"build a single-repository optimiser
   first, but put it behind repository-agnostic interfaces from day one"* — the goal being *"one
   working optimiser, many-repo-shaped interfaces"*. R3 simply says not yet. **Resolution:** they
   are compatible. R4 is talking about interface shape, which is cheap now and expensive to
   retrofit; R3 is talking about when to run a search. Adopt both.
2. **Three attempts.** R2 proposes it; R3 grades it **B** — *"a defensible safety default, not
   validated for this workload"* — and grades same-failure detection **C+**, noting *"'same
   failure' for an LLM software agent has no mature standard definition."* **Resolution:** ship 3
   as a policy default, record it as ASSUMED, and revisit from data.
3. **Four terminal states.** R2 proposes exactly four; R3 grades **B+** and says four is *not* an
   industry standard — it is a useful **external business-outcome projection over a richer internal
   lifecycle** (`RESERVED`, `DISPATCHING`, `RUNNING`, `CANCEL_REQUESTED`, `REAPING`, `ORPHANED`).
   It also flags `NEEDS_HUMAN` as incoherent if a run can be resumed from it — either close the run
   and create a continuation with `parent_run_id`, or model `PAUSED_FOR_HUMAN` separately.
   **Resolution:** adopt R3's refinement.
4. **Two R4 runs.** Both reach the same verdict from different framings. No material contradiction
   found; the second is longer on cost and isolation. Treated as corroboration.

## 8. What changes in this repo

Ordered by the build order above, with what already exists noted.

| # | Change | State |
|---:|---|---|
| 1 | `blueprints/orchestrator_team.yaml` marked superseded | **done** |
| 2 | Record the false-`succeeded` mechanism | **done** — `../evidence/false-succeeded-mechanism.md` |
| 3 | Readiness gates for the build order — one gate per prerequisite | **next** |
| 4 | Version hash: add the nine missing dimensions, contract version first | pending |
| 5 | Corpus: regression + challenge split, 15 strata, unclassified as its own | pending — largest single item |
| 6 | Evaluator as a service with its own identity, not a directory move | pending — retires the `$AGENT_FACTORY_EVALS` plan |
| 7 | Single-worker topology blueprint replacing the three-agent one | pending |
| 8 | Repo-agnostic *interfaces* (contract, environment, evaluator) without the agnostic optimiser | pending — cheap now, expensive later |

Items 1–4 of the build order are changes to `prefect-connectors`, not here — and they are the
factory's first team's work, not hand work. That is the point of the factory. Doing them by hand
would be doing the team's job manually; the reason to fix them first is that the team cannot be
certified until the loop it runs in can tell success from failure.

## 9. Three follow-ups to ask in the existing threads

Cheaper than re-running, and they carry the context. None require a new prompt.

1. **R3 thread** — the false-`succeeded` correction: our verdict is computed from a last-write-wins
   status field in a bespoke engine, not Prefect. What is the correct design for a terminal verdict
   computed from append-only history, and what negative control proves a false `succeeded` is
   impossible?
2. **R2 thread** — our build plane is not Prefect, so your prescription's retry limits, concurrency
   reservation and zombie handling are not available primitives. What must we build, what does it
   cost, and does it change your recommendation — **including whether to move the build plane onto
   Prefect rather than reimplement its primitives?**
3. **R1 thread** — one-liner: the COMPLETED-over-failures defect is not Prefect but a
   last-write-wins status field. Does anything else in your answer depend on that misattribution?
