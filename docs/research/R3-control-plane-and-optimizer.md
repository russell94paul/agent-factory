# R3 — Bounding the control plane, the sandbox, and (later) the optimizer

**Rewritten 2026-08-21 after R1 and R2 landed.** The original R3 asked how to search a *team*
configuration space and closed by asking whether building an optimizer now was the right move at
all. Both of those are now answered, independently and in the same direction, so asking them again
would burn a run confirming what we have:

- **R2:** *"Start with one end-to-end implementation agent, not the three-agent team."* The
  configuration space R3 proposed to search is a space we are no longer going to build.
- **R1:** *"The weakest parts are not primarily LLM-eval sophistication. They are control-plane
  problems."* And: *"adding another eval framework today would not materially improve your
  assurance."*

So R3 is re-scoped to what neither answer covered and both said was urgent: **bounding, orphan
reaping, sandboxing and tenancy** — with the optimizer demoted to a conditional final section,
scoped to a single-agent configuration. Prior art on config optimisation (DSPy, GEPA, TextGrad,
OpenEvolve) is **R4's** question; do not duplicate it here.

Run this any time now — R2 has landed, which was its only real dependency. Save the answer as
`docs/research/answers/R3-answer.md`.


## Run log

| Run | Dispatched | Outcome |
|---|---|---|
| 1 | *not recorded* | Answer filed **2026-08-21** (measured: the answer file's mtime). This prompt predates the run log, so when it was sent is **NOT-RECORDED** — which is not the same as never. |

> Kept because `factory.dispatch` reads a status line and the presence of an answer file, and by its own account cannot see whether a prompt was ever actually pasted anywhere. Without this table "which did I send, and when?" is not answerable from disk. **Add a row every time this prompt is dispatched.**

---

```
You are advising a small data-engineering company (about 4 engineers) whose LLM agents do software
work on their own repositories — principally migrating and maintaining data connectors along the
path vendor API -> Azure container -> Prefect 3 -> Snowflake -> BI/chat surfaces. Cloud is Azure
(Container Instances / Container Apps), orchestration is Prefect 3, code is mostly Python.

Two prior research passes have already concluded that their agent architecture is not the problem
and their control plane is. This pass is about the control plane. I want concrete implementations,
not principles.

=====================================================================
PART A — MEASURED CONTEXT
=====================================================================
[M] = measured from their production event logs on 2026-08-21 by parsing raw event files.
[R] = from an earlier internal review, NOT re-verified; treat as weaker and say so if you lean on it.

- [M] Across 14 recorded runs of an 18-stage pipeline: 1,001 stage_failed against 165
      stage_completed. A stage attempt succeeds 14.2% of the time.
- [M] 1,004 restart events, NO ATTEMPT CAP. Worst single case: 352 restarts of one stage in one
      run.
- [M] 3 of 14 runs reached a terminal completion event. 4 more sit at "stage_started" with no
      terminal event at all — neither finished nor failed.
- [M] 3 runs recorded COMPLETED while containing 115, 21 and 15 stage failures.
- [M] One pipeline is recorded as `running` in the orchestrator's own state file while its event
      log ends in stage_failed.
- [M] In the longest run, ONE stage held 92,817 of 95,098 seconds — 97.6% of the run — in a
      restart loop.
- [M] 22 gate-approval events, ZERO refusals. 14 recorded "auto-pilot: conditions met", 8 empty.
      5 of 7 gates across all pipeline templates have no programmatic check (gate_check = None).
- [M] Cost is recorded only on stage_completed, so 1,001 failed attempts contribute $0.00 and true
      spend cannot be reconstructed from the logs.
- [M] One evaluation — a full connector migration scored end to end — has a median wall-clock of
      11.3 hours across all runs and 26.4 hours across the 3 that completed.
- [M] Exactly 1 connector has a recorded successful end-to-end run.
- [R] A prior autonomous mechanism kept its attempt counter in an in-memory module-level dict, so
      every process restart handed it a fresh budget. It re-dispatched a permanently-failing stage
      every 30 minutes overnight.
- Documented incident: a stage failed on timeout, the Azure container carried on running because
  nothing killed it, the stage auto-restarted with no cap, and ten containers consumed an entire
  10-core canadacentral quota overnight, blocking every human operator.

=====================================================================
PART B — WHAT PRIOR RESEARCH ALREADY CONCLUDED (do not re-derive; critique)
=====================================================================
A previous pass recommended this control-plane prescription. I want it graded and completed, not
repeated back:

  1. Four business-level terminal states only: SUCCEEDED, FAILED, NEEDS_HUMAN, CANCELLED.
     SUCCEEDED must be impossible unless every required terminal condition and gate is satisfied.
  2. A distinction in vocabulary between EXECUTION_TERMINATED (the orchestrator stopped) and
     CONTRACT_PASS (the work is correct). "COMPLETED" may legitimately mean the former and must
     never be evidence of the latter.
  3. stage_started needs a lease/heartbeat and an explicit orphan timeout.
  4. Retries externally capped — start at 3 total attempts per stage, with same-failure repetition
     stopping earlier. The agent must have no tool by which it can mutate that cap.
  5. Concurrency limits outside the agent, reserving capacity rather than letting containers
     consume a region quota.
  6. Something deterministic must own the seam: producer_done != handoff_done. A stage is not
     complete until the downstream contract has accepted its exact output.

It also identified a Prefect-specific mechanism: if failures are captured as returned state rather
than propagated, a parent flow can return successfully and become COMPLETED even though child work
failed.

Their verifier is a hand-built 12-assertion contract with four verdicts (PASS / FAIL /
UNMEASURABLE / NOT_RUN) where UNMEASURABLE explicitly is not a pass. It was graded sound, except
that calibrating it against a single known-good run was graded FOLKLORE. Its corpus is hash-pinned
JSON, verified on load — judged honest tamper-EVIDENCE but explicitly not a security boundary,
since the agent can rewrite both corpus and manifest.

=====================================================================
PART C — THE QUESTIONS
=====================================================================
Separate ESTABLISHED PRACTICE from VENDOR CLAIM from OPEN RESEARCH throughout. For every safety
mechanism give a CONCRETE IMPLEMENTATION, not a principle. "Use a persisted counter" is not an
answer; "write to X with these transaction semantics, read before dispatch at Y, reconcile on
startup by Z" is.

1. GRADE THE PRESCRIPTION IN PART B, item by item. Which are established practice, which are
   plausible-but-unevidenced, and what is MISSING that would still let this system report success
   over work it could not see? Be specific about the four-state model — is collapsing to four
   business states standard, and where does NEEDS_HUMAN cause trouble in practice?

2. BOUNDED EXECUTION, IMPLEMENTED.
   a. A spend and attempt ceiling that SURVIVES A PROCESS RESTART. Where does the counter live,
      what writes it, what reads it before dispatch, and how is check-and-increment made atomic
      against concurrent runners? Give the storage choice and the transaction semantics.
   b. Enforcement placement: how do you guarantee the bounded party cannot raise its own cap?
      What does that look like when the "agent" has shell access and repository write permission?
   c. Same-failure detection — how do mature systems decide that attempt N is repeating attempt
      N-1 rather than making progress, and stop earlier than the hard cap?
   d. Is 3 attempts defensible as a starting cap, or is there better evidence for a different
      number or for per-error-class policies?

3. ORPHAN REAPING — the specific failure that cost them a region quota.
   Their Azure containers outlive the stage that launched them; nothing kills the workload when
   the orchestrator gives up on it. What is the established pattern for guaranteeing a launched
   workload is either finished or killed? Cover: lease/heartbeat with a reaper, cancellation
   propagation to already-dispatched cloud work, idempotent kill, and reconciliation on
   orchestrator restart when the in-flight set is unknown. Give Azure-specific mechanisms (ACI,
   Container Apps jobs) where they exist, and say where the platform simply does not help.

4. THE PREFECT TRAP, CONCRETELY. How do teams prevent programmatic state handling from producing a
   COMPLETED parent over failed children? What is the correct Prefect 3 idiom, what do
   `return_state` / `raise_on_failure` / final-state rules actually do here, and how would you
   TEST that a false COMPLETED is impossible — i.e. a negative control for terminal semantics?

5. GATES THAT CAN REFUSE. 22 approvals, 0 refusals, 5 of 7 with no predicate. Beyond adding
   predicates: how does a gate PROVE it is capable of refusing, analogously to mutation-testing an
   assertion? Is there prior art for fire-drilling approval controls in automated pipelines, and
   what does a credible drill look like for a gate that must block a real promotion?

6. SANDBOXING. For running agent-generated code that deploys infrastructure, compare Docker,
   gVisor, Firecracker, E2B, Modal, Daytona, and ephemeral cloud environments. Judge on: startup
   latency, cost per run, blast-radius containment, and whether cloud credentials can be scoped
   per sandbox so a confused or compromised run cannot reach beyond its own client. They are on
   Azure with Snowflake — weight the answer to that stack.

7. TENANCY. They serve multiple clients from shared infrastructure and have already had an
   incident where one vendor API key returned every client's accounts — 45 Google Ads accounts of
   which 6 belonged to the client in question. What is the correct isolation model, what is the
   MINIMUM gate set that must include a tenancy check, and where in the lifecycle must that check
   sit so it cannot be skipped? Is per-tenant credential scoping at the sandbox boundary
   achievable on Azure + Snowflake, and what does it cost operationally?

8. COST AND RELIABILITY TELEMETRY. Give the minimum event schema that makes spend reconstructable
   after the fact — including for attempts that failed, were killed, or orphaned a container. Then
   the harder half: how should reliability be measured INDEPENDENTLY OF RETRIES, so a run that
   succeeds on attempt 352 does not receive the same credit as one that succeeds first try? Name
   the metric and how it is computed.

9. EVALUATOR ISOLATION, IMPLEMENTED. Moving from tamper-evident to tamper-resistant. Rank the
   options — separate repository, separate credentials, separate process, signing key, external
   service — by the attack each actually stops, and say which are theatre for an internal
   4-person team whose "attacker" is an LLM agent with shell access rather than a motivated human.

10. SCAFFOLDING. Best current way to generate and maintain a multi-service Python repo skeleton of
    this kind — cookiecutter, copier, Nx, Bazel, uv workspaces, or an AI scaffolder. Judge on
    keeping GENERATED projects updatable as the template evolves (template drift is the usual
    killer), and monorepo versus polyrepo for a team of four.

11. THE OPTIMIZER — CONDITIONAL, AND LAST.
    Given a SINGLE-agent configuration (prompt, model, reasoning effort, tool set, context layout,
    retry policy) rather than a team; an evaluation costing hours of wall-clock live but under a
    second when replayed from recorded evidence; and a positive corpus of exactly one run:
    a. Which configuration dimensions actually move outcomes, and in what order of magnitude?
       Which are low-yield and can be dropped from any search?
    b. Which search method suits evaluations this expensive — successive halving / Hyperband,
       Bayesian optimisation, ablation, LLM-proposed mutations? Include sample-efficiency numbers.
       Is one-factor-at-a-time ablation the right first move rather than a search at all?
    c. What is the minimum corpus size before searching is defensible rather than overfitting to
       a single fixture? A prior pass graded one-run calibration as FOLKLORE — say what number
       replaces it and why.
    d. State plainly whether an optimizer should be built at all before the items in Q2-Q5 are
       fixed. "Not yet, and here is the ordered prerequisite list" is an acceptable and expected
       answer.
    NOTE: prior art on configuration optimisation specifically — DSPy/MIPROv2, GEPA, TextGrad,
    Trace, OpenEvolve, AlphaEvolve, karpathy/autoresearch — is being asked separately. Do not
    spend this answer on tool-by-tool assessment of those.

=====================================================================
CONSTRAINTS
=====================================================================
- Separate OBSERVED from MARKETED. Documentation asserting a feature exists is not evidence that
  adopting it improves reliability.
- Every safety mechanism gets a concrete implementation with storage, semantics and failure modes.
- Where the honest answer is "this is unsolved" or "nobody has published this", say so rather than
  reasoning to a plausible-sounding conclusion.
- We would rather be told to build less.

=====================================================================
DELIVERABLE
=====================================================================
1. A graded verdict on the Part B prescription, item by item, plus what is missing.
2. Bounded execution implemented — storage, transaction semantics, enforcement placement,
   same-failure detection, and a defensible starting cap.
3. An orphan-reaping design for Azure, including reconciliation after an orchestrator restart.
4. The correct Prefect 3 idiom for terminal semantics, and a negative control that proves a false
   COMPLETED is impossible.
5. A method for proving a gate can refuse.
6. A sandbox recommendation with cost per run on Azure.
7. A tenancy isolation model and the minimum gate set.
8. A cost-and-reliability event schema, including a retry-independent reliability metric.
9. Evaluator isolation ranked by the attack each measure stops.
10. A scaffolding recommendation.
11. The optimizer verdict — build now or not, with the ordered prerequisite list either way.
12. What remains unknown, stated separately from what you are confident about.
```
