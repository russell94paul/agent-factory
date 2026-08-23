# Synthesis — what four research passes concluded, and what changes

**2026-08-21, extended 2026-08-22.** Eight documents: R1 eval harness, R2 topology, R3 control
plane, R4 agnostic optimiser (twice), **R5 build velocity**, **R6 automation and alerting**, and —
added 08-22 — **R7 session manager** (§11, and graded weaker than the rest). This is the decision record. Where the answers disagree, or where they contradict
something already built or already said in this session, that is recorded rather than smoothed.

⚠ **R1–R4 asked about the product. R5–R6 asked about the process that builds it.** They are not
graded against each other, and §10 says which earlier sections they amend. One of them was answered
under a false constraint I wrote into its prompt — §10.4 — and the distortion is recorded, not
carried forward.

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

**R5 amends step 1 rather than reordering anything** (2026-08-22). Asked for the fastest path to a
certifiable end-to-end run, it ranked *"prototype a lean runner with sandbox and circuit-breakers"*
Very High and called it the gating step — which is step 1 with the caps made concrete:

```
--memory 512m --cpus 1.0 --security-opt no-new-privileges
read-only filesystem except the work directory, no network by default
circuit-break after 3–5 consecutive failures or T minutes
a human approval step before any container launch
```

So the order stands; R5 supplies the numbers step 1 was missing. Nothing in R5 or R6 moves steps
2–9.

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
| 10 | One branch/worktree per lane — §10.1, both passes agree | **not started, highest evidence** |
| 11 | CI on push in `agent-factory` — see §10.4, the premise that suppressed it was false | **not started** |
| 12 | Gate-verdict diff against last good state, as a CI step | **not started** |
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

---

## 10. R5 and R6 — the passes about how we build (added 2026-08-22)

Two passes on the build process rather than the product. Read with §5 and §7; they amend §5's step
1 (above) and add three rows to §8.

### 10.1 The convergence — and it is the strongest signal in either document

**Both passes independently recommend one branch or git worktree per parallel agent session**, and
they arrived by different routes:

- **R5, from data.** A study of ~33,000 agent-generated GitHub PRs: *same-agent* PRs in flight
  conflicted **19.8%** of the time, *different-agent* PRs **41.7%** — and most conflicts were
  **structural** (one agent deleting a file another edited), not line-level.
- **R6, as an Observed practice.** Branch-per-lane / worktree-per-agent, merged one at a time.

Agreement between independent passes is the control, divergence is the finding — so this is the
recommendation with the least room to argue. **It is also not implemented.** All five lanes in
`factory/lanes.py` point at one shared branch, `feat/readiness-generator`. At a 41.7% cross-agent
conflict rate that is a bad bet, and it is the highest-evidence unbuilt change in the programme.

The lane grouping *itself* is vindicated: R5 confirms file locality, not the dependency graph, is
the binding constraint on parallelism. `factory/lanes.py::conflicts()` already computes it.

### 10.2 Where R5 disagrees with this session — unresolved, with the deciding fact named

**R5 contradicts a recommendation made in-session.** Asked how to get team one running, the session
proposed fixing the existing orchestrator's missing attempt cap and then driving it. R5 instead
ranks *building a lean runner inside the factory repo* as the gating step, with the orchestrator
reviewed in parallel rather than repaired first.

**Not resolved here, because one checkable fact decides it:** how much of the orchestrator's
18-stage migration pipeline team one actually needs for one connector. If most of it, a "lean
runner" means reimplementing it and R5 is underestimating the work. If team one's path is genuinely
source → container → Prefect → warehouse, the orchestrator is a detour and R5 is right.

⚠ Note what R5 did *not* know: that the 18 stages exist and encode real work. Neither answer should
be adopted before someone reads the stage list.

### 10.3 What they say we already got right

- **The findings ledger.** R6 endorses a shared cross-session knowledge store; R5 names it directly
  as part of "enable safe parallelism". Built 2026-08-22, six entries at the time of writing.
- **Evidence required on close.** R6 found prior art for the `close_lane` idea — a tracker that
  refuses to close an item without evidence attached. Our version is currently a *prompt asking*,
  which is a convention, not a control.
- **Backlog growth is discovery, not failure.** R5 reads the gate set going 13 → 30 in 6.4h as
  legitimate discovery of omitted work, with the caveat that intake-vs-throughput should be tracked
  explicitly and converge. `factory/schedule.py` already measures both and refuses an ETA while
  they diverge.

### 10.4 ⛔ R6 was answered under a false constraint, and it changed the ranking

The prompt in `R6-automation-and-alerting.md` asserts, as a constraint: *"there is currently no
runner budget or appetite for one."* **That is false.** The same GitHub org runs three Actions
workflows in `prefect-connectors` (`ci.yml`, `quality-gate.yml`, `branch-sync.yml`). `agent-factory`
merely has no `.github/workflows` directory — an absence, not a constraint.

R6 explicitly deferred *"a full CI on every push"* on the strength of that sentence and ranked a
nightly scheduled gate-diff first instead. **So R6's Q1 ordering optimises against a world that was
described to it, not the one that exists**, and CI-on-push is very likely the correct first move.

Recorded as `docs/findings.md` **F7**. It is the F1 pattern — an unverified premise carried into
research — committed by the author of a prompt whose own Method note warns against it. The lesson
generalises: *a constraint asserted in a research prompt is a hypothesis like any other.*

### 10.5 What the answers could not settle

Both declared their own gaps when asked to, which is worth more than six confident answers:

| Question | Gap |
|---|---|
| When to freeze a measurement-derived backlog | R5: no studies found; inferred from agile theory |
| Drift across multiple generated surfaces | R5: no direct analogue in the literature |
| Handoffs between agent sessions | R5: little published; analogy to human handoffs |
| Alert thresholds for agent work | R6: no AI-specific guidance on where to set them |
| Multi-agent repo standards | R6: **no widely adopted standard exists** — blog posts and academic prototypes only |
| Recovering from a failed pre-close check | R6: tooling is just emerging |

The fifth row is the one to remember. There is no consensus practice for what we are about to do,
so our own measurements are the best evidence available and should be recorded as they accumulate.

### 10.6 R6's shortlist, re-ordered for the F7 correction

R6's order, with CI restored to where the corrected premise puts it:

```
1  CI on push — run the suite; the org already has Actions        ← moved up, see §10.4
2  branch/worktree per lane                                        ← §10.1, both passes
3  gate-verdict diff against the last good state, as a CI step
4  pre-push hook for fast local feedback  (bypassable: --no-verify)
5  attribution — bisect, or per-lane branches measured at merge
6  progress markers, not heartbeats: "alive ≠ working"
7  evidence required on close
```

Every one of R6's recommendations arrived with *what it catches, what it cannot catch, and how to
make it fire on purpose* — the last being the property this programme cares about most. A control
nobody has watched refuse something is decoration, so none of these is done until it has been made
to fail deliberately.

### 10.7 What got built while answering these — flagged, not pursued

Paul, 2026-08-22: *"what we have built here is a session orchestrator... I want to flag this
because it could be efficient, but let's keep on track."* Recording it because he is right and
because nobody set out to build it.

The readiness tracker began as a page that re-measured 30 gates. Over one session it acquired:
lane definitions grouped by file locality, a dependency order and a conflict map, per-lane model
recommendations, a claim/release lock, one git worktree and branch per lane, launch-into-terminal,
a pre-answer channel for declared blockers, a preflight, and generated per-lane and per-session
handoffs. That is a **session orchestrator for agent work** — the build plane's build plane.

⚠ **It is not on the gate list and nothing measures it.** No gate in the readiness set asks
whether it works, so by this programme's own standard it is unproven infrastructure with a nice
interface. Its parts have been individually exercised — claim refusal, worktree lifecycle, handoff
preflight, blocked launch — but the orchestrator as a whole has never run three lanes to
completion. Before it is trusted or extended, it should earn gates like everything else.

The efficiency claim is plausible and unmeasured. R5's question 2 asked what parallel agent
sessions actually save and at what coordination cost; the honest position is that we now have the
apparatus to find out and no measurement yet.

---

## 11. R7 — the session-manager pass (added 2026-08-22)

The eighth answer, filed 10:05 on 2026-08-22. It asked what should *run* the sessions, extending R5
(what parallel sessions cost) and R6 (what should watch them).

⚠ **Grade the instrument first, because that is the house rule.** R7's answer is ~16 KB against
50–70 KB for R1–R4, and self-labels most of its substance *Extrapolated*. Two of its five sections
(UI, optimisation) are general dashboard and CI advice rather than findings, and it did not answer
the one question the prompt flagged as the interesting one (§11.1). **Treat R7 as weaker evidence
than R1–R6.** Where it touches a conclusion that has measurement behind it, the measurement wins.

### 11.1 Switchboard — and the argument that was not supplied

Observed, from reading the source rather than the showcase, as the prompt demanded:

| Property | What Switchboard does |
|---|---|
| Session processes | Real PTYs via `node-pty` |
| Isolation | Worktrees **optional** — `--worktree` flag; **default reuses the project directory** |
| Persistence | Claude JSONL session history + a SQLite metadata cache; watches `~/.claude/projects` |
| Edit capture | Built-in MCP bridge |
| Interface | **Embeds a full terminal per session, rendered in cards** in an Electron app |

**Verdict: inspiration, not adoption.** Adopting it wholesale trades Windows Terminal tabs for an
Electron app and violates the no-in-page-terminal constraint. Worth cherry-picking: session
scanning, the MCP bridge, session-transition logic.

⛔ **But the prompt asked a specific question and did not get an answer.** It said: *if Switchboard
does embed terminals, the interesting question is what it gains that outweighs this — we want the
argument, not the feature.* R7 restated our constraint and concluded "without clear gains". That is
our own position handed back to us. So the no-in-page-terminal decision now stands **unchallenged,
which is not the same as tested** — and this programme does not treat those as equivalent anywhere
else. Record it as UNTESTED and ask it as a follow-up (§9, new item 4).

### 11.2 Most of R7's Item 3 describes what is already built

The "shared task list" pattern R7 recommends — claim semantics with atomic locks, one worktree per
agent, prerequisites to prevent unsafe parallelism, capped retries, blocked tasks staying visible —
is `claims.py`, `tasks.py`, `lanes.py` and `worktrees.py`. It is corroboration, not new direction,
and it is worth having: an independent pass reaching the built design is the control.

### 11.3 The genuinely new contribution — autonomy as a designed surface

R7's Item 4 is the first pass to treat **bounded autonomy as something you design rather than
something that emerges**. Five candidate auto-actions, each with its preconditions and its failure
mode:

| Auto-action | Safe if | Cannot catch | Guard |
|---|---|---|---|
| Start the next lane | Lanes independent, claims and worktrees free | — | Semaphore; require the finished lane genuinely met its pass conditions; log every launch; an override pause |
| Merge the lane | All policy checks truly satisfied (the GitLab merge-when-checks-pass model) | Logic errors, missing approvals | Explicit sign-off or a merge-when-green label; refuse if a new comment or commit lands during the wait |
| Answer a known blocker | Deterministic match on an archived case | A changed context wearing the same question | Any variation at all → human |
| Retry a failure | The failure is non-deterministic | A persistent failure — retrying is futile | Counter, small cap, then "needs attention" |
| Split a large lane | — | Agents do not know logical boundaries | **Flag, never an action** |

The governing principle matches this estate's doctrine exactly: *engineer each to refuse — no-op —
unless the preconditions are crystal clear*, and log every decision so an operator can audit why it
did or did not fire.

One tension to name: `finish.py` **deliberately never merges**. R7's auto-merge is compatible only
in its guarded form, and the guard is the whole feature. Keep `finish()` non-merging; if auto-merge
is ever built it is a separate, separately-gated mechanism.

### 11.4 Where R7 disagrees with what is built — recorded, not smoothed

**1. ⛔ R7 proposes readiness gates as the cheap fitness proxy. Reject it.**

R7: *"The cheapest proxy fitness function is likely self-consistency: did the team meet some
readiness gates (e.g. all tests pass)?"* — and then, in its own next sentence, *"even that could be
gamed."*

This is precisely the never-optimise list in §6. Gate thresholds and evaluator thresholds are
**safety specification, not hyperparameters**, and optimising against the candidate's own score
*"changes the ruler rather than the system."* This estate has shipped that error twice — the
233-diagnoses agent and the 965-run loop. An optimiser pointed at the readiness gates would learn
to pass gates, and the gates are the only thing standing between us and not knowing.

**Do not adopt.** The rest of Item 2 — heuristic routing by task shape, retrieval of what worked on
similar tickets, defer real search until there is an outcome signal — is consistent with R3 and R4
and can stand.

**2. Stale claims: R7 says revert, we say still-block.**

R7: *"If an agent crashes mid-task, its task should revert to pending after a timeout."*
`claims.py` deliberately does the opposite — stale claims still block, because *"hiding them would
make a blocked lane look free."*

**Keep ours.** R7's version requires distinguishing *crashed* from *thinking*, and R7's own prompt
records that "alive" is not knowable from outside — a session that is thinking, finished, or dead
look identical. Auto-reverting on a timer therefore reclassifies an unknown as a free lane, which
is the four-verdict error in another costume. **The condition that would change this:** a real
liveness signal that separates crashed from working. Until one exists, a stale claim is
`UNMEASURABLE`, not `available`.

### 11.5 R7's build order does not supersede §5

R7 orders: TeamSpec → work queue → autonomy guards → optimisation aids → UI.

⚠ **That is the session-manager layer only.** R7 was not asked about spend ceilings, orphan
reaping, cancellation, or the terminal verdict, and is silent on all four. **Silence is not
disagreement** — but a reader who takes R7's five steps as the plan skips §5 steps 1–4, which R3
called non-negotiable. §5 stands unchanged. R7 slots in *after* it.

Where R7 does amend §8: it puts **executing the TeamSpec** ahead of the interface, and it lands on
a measured fact worth its own row — `blueprint.py` has `TeamSpec` and `AgentSpec` with a version
hash covering composition, and **nothing executes them**. `grep` finds one caller, a test. The data
model exists; the runtime does not. That is the cheapest high-value thing R7 surfaces.

### 11.6 One finding that matters beyond this repo

R7 could not find a standard for composable team specification. Prior art is thin — CrewAI's
role/goal/backstory personas, and a minor JSON `TeamSpec` in a small project — and R7 labels our own
schema *Extrapolated* because **no standard exists**.

So a composable-team configuration surface is an **industry-wide gap, not just ours**. Two
consequences: a product survey will not find one to copy, and the design is ours to get right rather
than to adopt. It also raises the value of §11.5's row — the thing nobody has a standard for is the
thing we already have a data model for and have never run.

### 11.7 Additions to §8

| # | Change | State |
|---:|---|---|
| 13 | **Execute the `TeamSpec`** — data model exists in `blueprint.py`, one caller, and it is a test | not started — cheapest high-value item R7 surfaces |
| 14 | **Bounded-autonomy surface** — the five auto-actions, each refuse-by-default, each logged | not started |
| 15 | Gate the session orchestrator itself (§10.7 flagged it; R7 assumes it) | not started |

### 11.8 Addition to §9 — follow-ups

4. **R7 thread** — you concluded Switchboard's embedded terminals bring "no clear gains", which is
   the position the prompt asked you to challenge rather than restate. Ignoring our objection for a
   moment: *what does rendering a live terminal per session actually buy an operator that progress
   markers, transcripts and a task queue do not?* If the answer is "nothing", say so on the merits —
   that is a stronger result than agreement.
