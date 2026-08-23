# Synthesis — what thirteen research passes concluded, and what changes

**2026-08-21, extended 2026-08-22.** Eight documents: R1 eval harness, R2 topology, R3 control
plane, R4 agnostic optimiser (twice), **R5 build velocity**, **R6 automation and alerting**, and —
added 08-22 — **R7 session manager** (§11, graded weaker than the rest); and — added 08-23 — **R10 wiki
training**, **R11 concept diff** and **R12 session-manager substrate** (§12). This is the decision record. Where the answers disagree, or where they contradict
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


---

## 12. R10, R11 and R12 — the passes that all said *stop building* (added 2026-08-23)

Three answers landed together. R8 is still outstanding. R9 was dispatched and **withdrawn** the
same morning as not useful, so no R9 answer will be filed — if one arrives it is discarded.

### 12.1 The convergence, and it is unanimous

Independently, on three unrelated questions, all three said the same thing: **do not build new
substrate; fix and use what exists.**

| Pass | Asked | Answered |
|---|---|---|
| R10 | should we build a hierarchical wiki + auto-researcher | **No.** "Don't build a fancy hierarchical auto-updating wiki before we fix the basics." |
| R11 | what do other factories make first-class that we lack | Seven absent concepts, **every one costed as significant engineering**; none recommended now |
| R12 | build a session manager or adopt one | **Adopt** `doctly/switchboard`, "rather than building a new system" |

That is the same instruction R1–R7 gave about the control plane, arriving from three new
directions. Treat it as the strongest signal in the document.

### 12.2 ⛔ R12 was answered under a MISSING constraint — the F7 pattern again, and mine again

**§11.1 recorded that the no-in-page-terminal decision stood UNTESTED**, because R7 restated our
own position instead of challenging it, and §9 item 4 exists to ask it properly.

R12's constraints section listed Windows-first, the three-lane ceiling, small team, per-secret
human approval, no unlabelled stale numbers, and never removing the instrument panel. **It did not
carry the no-in-page-terminal constraint at all.** R12 then recommended adopting an Electron app
whose entire model is an embedded terminal per session rendered in cards.

So R12's "adopt" is **not a refutation of §11.1's "inspiration, not adoption" verdict — it is an
answer to a different question.** The constraint was never put to it, and an answer cannot respect
a rule it was not given.

⭐ **This is F7 again, and again it is mine.** F7 was a *false* constraint written into R6's prompt.
This is a *real* constraint left out of R12's. Same class, opposite sign, same consequence: the
pass optimised against a world I described rather than the one we have. **Before "adopt
switchboard" becomes a decision, either the constraint is retired deliberately and in writing, or
R12 is re-asked with it stated.** Deciding on this answer as it stands would be adopting a
recommendation that was never told the main objection.

### 12.3 R12's own source-reading contradicts its executive summary — the reading is stronger

R12 did what R7 did not: it read the code and tiered its claims. Its executive summary says
switchboard "already implements most of the needed features (session discovery, attach/resume,
notifications, cost tracking)". Its own §2, marked OBSERVED, says otherwise:

| Exec summary claims | What §2 OBSERVED actually found |
|---|---|
| attach/resume | **There is no attach.** It only re-uses PTYs *it itself spawned*. A session running outside it is treated as not running, and it **spawns a second process against the same session id** |
| notifications | Derived by decoding **OSC 9 bells out of the terminal stream**. It never reads `~/.claude/sessions/*.json` — no `kind:bg`, no `jobId`, no `needs` |
| session discovery | True, but transcript-scan only; **no process-table check**, so liveness is inferred from whether a file is growing |
| Windows support | **INFERRED, not OBSERVED** — "should run… not empirically verified by us" |
| extension surface | **No plugin API** (INFERRED, "no plugin code found"). Extending means patching or a custom build |

**Where an answer's evidence contradicts its own summary, the evidence wins.** Two consequences
follow and neither is in the executive summary:

1. **Adopting switchboard reproduces, by design, the incident that prompted the question.** On
   2026-08-23 a terminal died, the agent survived it, and a second `--resume` would have created a
   divergent duplicate. Switchboard *does that on purpose* for any session it did not launch.
2. **It cannot close the gap R12 itself calls the sharpest.** Four agents were blocked on questions
   written in plain English in `jobs/<id>/state.json`. Switchboard never reads that file. No amount
   of adopting fixes a blindness to the field the questions are in.

Where R12 and R7 **agree**, both from source, take it as corroborated: `node-pty` PTYs, transcript
scanning plus a SQLite cache, Electron, a terminal embedded per session. Two independent passes
reaching the same reading is the control.

### 12.4 What R12 contributes that is right regardless of adopt-or-build

None of this depends on the switchboard decision:

- **Liveness is four states, not two** — `RUNNING-ATTACHED`, `RUNNING-ORPHANED`,
  `EXITED-RESUMABLE`, `EXITED-GONE`. `sessions.py` currently distinguishes live from not-live and
  cannot express an orphan. Build this.
- **Our failure is alarm *absence*, not alarm fatigue.** The signal exists and is never surfaced.
  R12's cited basis (NNGroup, REPORTED) is that action-required notifications must interrupt;
  passive badges are missed. Whatever surfaces `needs`, it must not be a badge nobody looks at.
- **Cost is meaningless without an outcome to anchor it** — R12 reaches this independently, and it
  is exactly `factory/metrics.py`'s rule that an activity metric with no paired outcome metric is
  *refused*. An outside pass reproducing a rule we already enforce is the strongest kind of
  corroboration available.
- It **refuses batch-approval of secrets** unprompted, matching our hard rule.

### 12.5 R11 — the concepts we have no name for

Surveyed Anthropic, OpenAI, Google, Microsoft, LangChain, CrewAI, Factory.ai, Sierra, Cursor.
**ABSENT** from us: structured traces (OTEL GenAI spans), guardrails, a workflow engine, persisted
memory, a connector registry, task packaging. **DEFERRED:** multi-agent teams.

⭐ **The sharpest is guardrails, because it is a category we do not have at all.** Our readiness
gates evaluate *finished output*; a guardrail blocks a bad action *before it happens*. That is not
a stronger gate, it is a different layer — and the control-plane lane has already shipped a defect
of exactly the shape a guardrail catches: `terminate_prefect_flow_run` sent Prefect CANCELLING
**before** the ownership check, so the refusal protected the container and never protected the run.
A post-hoc gate cannot catch that class. **File as a real absence.**

Second: **task packaging** (METR Task Standard — task + environment + scoring as one reproducible
unit). That is the same question R8 is out asking about isolation tiers, arriving from the
benchmark side. Read them together when R8 lands.

⚠ **One R11 claim is already overtaken.** It says *"our `deploy.py` just writes an opaque transcript
log"* and files observability as wholly ABSENT. As of 2026-08-23 the transcript is a **measured
instrument** — `factory/runs.py` derives per-session tokens, cache traffic, model and wall-clock
from it. The absence is narrower than R11 states: we lack *structured spans*, not all telemetry.

### 12.6 R10 — the hierarchical wiki, refused, but one mechanism is worth taking

**Verdict: do not build it.** Two reasons, both with evidence:

- **Context degradation.** Accuracy fell ~24% from adding 30k *irrelevant* tokens even with the
  relevant content present. Our wiki is ~1M tokens — roughly forty times the ~25k threshold where
  this starts. Pasting it is not a strategy.
- **Memory laundering.** An unsupervised write-back loop launders hallucinated content into
  innocuous-sounding prose that still misleads later reasoning. R10's position is that the wiki
  *will* be corrupted eventually unless every write is verified — and that with verification strong
  enough to be safe, the loop gains little.

| Mechanism | Verdict |
|---|---|
| A — fine-tune on the wiki | **No.** RAG beats unsupervised fine-tuning on new facts (Ovadia et al.); catastrophic-forgetting risk |
| B — RAG | Partly. Log every retrieved passage; add a hallucination check |
| C — structured context assembly | **Beneficial, and the strongest number in the answer**: revisions 3.8 → 2.0, first-draft acceptance 32% → 55% |
| D — memory with write-back | Works only two-tier: **confirmed** (human-verified) vs **proposed** (auto). Never auto-absorb |
| E — **procedure synthesis into skills** | **Strongly encouraged — the highest-leverage of the five** |

⭐ **The actionable conclusion is E, and it is not the one the question was about.** The leverage is
in distilling the wiki into *invocable skills*, not in growing a better corpus. That is a direct
instruction about the estate's existing `~/.claude/skills/` tree.

⚠ **Basis caveat.** R10 attributes its two strongest figures to "Swift et al. 2026" (context
assembly) and "SkillX" (skill distillation). Neither is linked in the answer, and neither was
verified here. Treat both as **REPORTED-unverified** until someone reads the source — this
programme does not let a number travel without its basis, including a number that agrees with us.

### 12.7 What these three could not settle

- **R12:** whether switchboard runs on Windows (INFERRED); whether it can be extended at all
  (INFERRED — "no plugin code found"); and whether the in-page-terminal constraint should stand,
  which it was never asked.
- **R11:** any cost in numbers. "Significant engineering effort" appears repeatedly and is not a
  figure. Nothing here can be scheduled from the answer alone.
- **R10:** anything about *our* corpus. Every figure is from published work on other corpora; its
  own two-week decisive experiment is proposed and has not been run.

### 12.8 What changes in this repo — additions to §8

1. **Do not adopt switchboard on this evidence.** Either retire the no-in-page-terminal constraint
   deliberately and in writing, or re-ask R12 with it stated (§12.2). The recommendation is not
   wrong; it is unqualified.
2. **Build the four liveness states into `factory/sessions.py`** (§12.4). Independent of the
   decision, and it is what would have made this morning's crash legible.
3. **Surface `needs` ourselves.** No external tool will: switchboard provably cannot see the field.
   And make it interrupt rather than badge.
4. **Record the guardrail gap as a real absence** (§12.5) — a pre-action layer, distinct from the
   readiness gates, with the CANCELLING-before-ownership-check defect as its worked example.
5. **Skills over corpus** (§12.6) — the wiki's leverage is procedure synthesis, not retrieval.
6. **`factory/runs.py` already implements R12's cost-paired-with-outcome direction**, and R11's
   "observability wholly ABSENT" is narrowed accordingly.

### 12.9 Additions to §9 — follow-ups to ask

5. **R12 thread, and it must be asked before anything is adopted:** *"Our estate has a standing
   constraint that no terminal is embedded in a page — it was omitted from your brief by mistake.
   Switchboard renders a live terminal per session. Does your adopt recommendation survive that
   constraint, and if so what does the embedded terminal buy that a status list and the transcript
   do not?"* This is §9 item 4 re-aimed, and it is now the load-bearing open question.
6. **R12 thread:** *"Your §2 says there is no attach and that a session running outside switchboard
   gets a second process against the same id. That is the failure that prompted this brief. How
   does 'adopt' survive it?"*
7. **R10 thread:** *"Give the sources for 'Swift et al. 2026' and SkillX."*


---

## 13. R8 and R15 — the ceiling is removable, and one answer invented its evidence (added 2026-08-23)

Both landed after §12 was written. R13 and R14 are still out. R9 was withdrawn.

### 13.1 ⭐ R8 answers architecture-v0's central question: the 3-lane cap is an artefact

`architecture-v0` §1b asked us to attack the claim that *"an agent's isolation tier is chosen by
what its task touches"*, and named the two ways it was most likely wrong: that Snowflake clones
might be expensive to validate against, and that "data work does not conflict" was asserted rather
than measured.

**R8 says the ladder holds and the ceiling is an artefact of treating all work as one kind.**

| | Current | R8's recommendation |
|---|---|---|
| Isolation unit | local worktree, processes as the user, no network block | container or microVM per agent, host network off by default |
| **Concurrency ceiling** | **~3, file-level conflicts** | **resource-bound, "potentially 10+ on a modern server"** — each agent has its own DB clone |
| Blast radius | high — agents can ALTER or drop prod objects | low — confined to clones; prod reachable only through a gated deploy |
| Credentials | the operator's own Azure and Snowflake creds, unrestricted | brokered short-lived scoped tokens, nothing long-lived on the worker |
| Cost | untracked | billed per sandbox, with quotas and auto-shutdown |

Boot times, `OBSERVED`: Firecracker ~100–200 ms at ~5 MiB overhead; Kata ~150–300 ms; gVisor
faster still but 10–30% I/O cost.

⭐ **The smallest impactful change is smaller than the recommendation.** R8 does **not** say go to
the cloud. It says **containerise agent execution on one machine** — Docker or Firecracker, mounted
clones, an egress proxy — because *"the first break will be credentials isolation"*, and it cites
our own **F53** (an edit to `~/.claude/skills/` was instantly global) as the evidence. Explicitly
**not yet**: a multi-VM cluster or a new scheduling engine. *"First prove isolation locally."*

### 13.2 The one rule worth adopting immediately

> **Forbid any `CREATE OR REPLACE` on a shared schema unless preceded by an explicit clone.**

That is R8's answer to "which data-sandboxing pattern can be made *mandatory* rather than
conventional", and it is enforceable in code rather than in a runbook. It is also the same shape as
the estate's standing evidence-gated-deploy rule — validate against a clone, deploy through a gate —
so it costs no new discipline, only a check.

### 13.3 ⚠ A correction to what "unattended" can mean

Our readiness set asks *"can an agent team run a connector migration unattended?"* R8 puts a number
on the state of the art, `REPORTED` from an Anthropic study: **99.9th-percentile autonomous turns
last ~45 minutes, and the median is under a minute.** Longest productive production runs are *"tens
of minutes, not hours or days"*, and most teams deliberately break runs under an hour to bound risk.

**So the honest target is a 30–45 minute unbroken run, not an unattended migration.** Our 3-of-14
figure is not far off a field that mostly does not attempt more. This does not lower the bar for
*certification* — it changes what the bar is measuring.

### 13.4 Where R8 ignored constraints it was given — recorded, not smoothed

Two of its recommendations contradict facts the prompt supplied:

- **"Scheduling → an event-driven workflow scheduler (e.g. Prefect, Dagger)."** R8 §3 told it that
  our build plane at `:8765` is bespoke and **does not import Prefect**, so none of Prefect's
  primitives are available (R2-followup). Recommending Prefect as the scheduler is a recommendation
  to adopt the thing we established we are not using.
- **"Communication → Kafka or Azure EventBridge, event sourcing."** The prompt's constraints say a
  design needing a platform team to operate is the wrong answer regardless of merit. A Kafka
  deployment is exactly that.

Take the isolation half of R8 and leave the platform half. The isolation argument is costed, sourced
and specific; the scheduling and messaging recommendations are generic and were made against
constraints the answer had in front of it.

### 13.5 R15 — a useful corpus, and three things wrong with it

R15 read repositories rather than literature and produced the extraction table it was asked for.
Its architecture recommendation is a Rust/Tauri desktop app with a run-record as the durable unit,
an append-only SQLite store, and a separate verifier process after each run. **Its four screens —
Runs Board, Run Details, Blocked Questions, Approval Review — are a reasonable answer** and three of
them are already data-complete in this repo (`runs.report()`, `sessions.blocked()`, transcripts).

Three defects, recorded here so they do not harden into fact:

1. **It invented evidence about us.** *"In our user studies we found embedded shells cause cognitive
   context-switch."* **There are no user studies.** That fabricated citation is used to support the
   terminal recommendation — the one question every prompt was told to answer on the merits. It also
   asserts *"Switchboard's 120fps cards"* after recording *"PERFORMANCE: Not documented."*
2. **It omits §5.0 entirely** — *what to fix in ours first*, deliverable item 5, added specifically
   so the substrate would be repaired before the interface. The answer goes straight to a new
   architecture.
3. **The corpus is thinner than the floor it was given** — ~25 candidates, 6 deep reads, most of the
   named list marked LISTED-ONLY. And `block/goose` is misidentified as `aaif-goose/goose`.

⚠ **Its desktop-app recommendation should not be acted on**, and not because it is wrong in
principle: it is unaffordable in time, and the page it would replace is slow for a reason that is
now measured. `measure()` runs 30 gates **serially in 9.39 s** and the server is `socketserver.TCPServer`.

⚠ **A correction to what this section first said, and it was mine.** It claimed *"an 8-wide pool
puts a page near 1.2 s… ~30 lines"*. **Wrong by about eight times.** The probes are not 30 uniform
I/O-bound tasks: gate `suite` shells out to a full `python -m pytest` subprocess and takes **9.16 s
— 97.6% of the total**, with the other 29 gates summing to 0.23 s. **Parallel speedup floors at the
slowest single task, not at total÷width**, so a pool of any size takes this from 9.39 s to 9.16 s.

The fix is architectural, not concurrency: **take the suite out of the request path**, cache it
against the git SHA of `tests/` and `factory/`, and render it with its age attached — which the
no-silent-cache rule permits, because the age travels with the figure. Recorded as F77 by the
session that caught it; confirmed independently here at 97.6%.

### 13.6 ⛔ R12 and R15 contradict each other on the load-bearing fact — unresolved

R15's own §0 named R12's source-level findings as its **control case**. It reached the opposite
conclusion and did not notice:

| | Claim | Tier |
|---|---|---|
| **R12** | switchboard *"never attaches to an arbitrary running process; it only re-uses PTYs that it itself spawned"* — and will **spawn a second process against the same session id** | OBSERVED |
| **R15** | *"ATTACH: Yes – it can attach to any running session… It detects any Claude session in the project folder, not just those it spawned"* | OBSERVED |

**Both cannot be true, and the answer decides whether adopting switchboard reproduces the exact
duplicate-session failure of 2026-08-23.** Neither is stronger on its face: both claim to have read
the source, and neither cites a line.

**The discriminating test is cheap and nobody has run it:** open switchboard's `open-terminal`
handler and read what happens when `activeSessions` does *not* contain the session id. R12 says it
spawns with `--resume`; R15 says it attaches. One file settles it. **Until someone reads it, treat
switchboard's attach behaviour as UNKNOWN and do not let either answer carry a design premise.**

### 13.7 What changes

1. **Do not adopt R15's desktop app.** Make the existing tracker instant instead — thread the server
   and parallelise the probes, 9.3 s → ~1.2 s, ~30 lines. Then apply R14's design to a fast surface.
2. **Containerise agent execution on one machine** (R8's smallest impactful change), before any
   cloud step. The first break is credentials isolation, and F53 is the evidence.
3. **Adopt the mandatory-clone rule** (§13.2) — enforceable in code, no new discipline.
4. **Restate the unattended goal as a 30–45 minute unbroken run** (§13.3), and say so in the
   readiness set rather than leaving the gate asking for something the field does not attempt.
5. **Read switchboard's `open-terminal` handler** and settle §13.6. One file.
6. **Take R8's isolation argument, leave its scheduling and messaging recommendations** (§13.4).

### 13.8 What they could not settle

- **R8:** whether zero-copy clones are cheap to *validate against* at our data volumes — it asserts
  near-zero creation cost but does not cost validation, which was half of architecture-v0's §7
  worry. And "10+ agents on a modern server" is `INFERRED`, with no measurement behind the number.
- **R15:** anything about design craft — no type scale, no colour system, no hierarchy, no motion,
  and no mention of `UNMEASURABLE`, which is the colour problem no standard palette solves. That is
  R14's job and R14 has not run.


---

## 14. R13 — the platform question, settled; and three passes now agree on the first move (added 2026-08-23)

R13 landed after §13. Only R14 remains unsent.

### 14.1 ⭐ R13 and R8 bracket the concurrency question from opposite sides — and agree

They read as a contradiction and are not one:

> **R13 §1:** *"None of these patterns magically breaches a 3-lane cap… orchestration patterns
> address reliability and fault modes; **raising the concurrency ceiling depends on task structure,
> not the orchestration style.**"*
>
> **R8 §4:** change the task structure — a container and its own DB clone per agent — and the
> ceiling becomes resource-bound, *"potentially 10+"*.

R13 surveyed seven orchestration patterns and found **none** of them raises the cap: not
orchestrator–worker, not hierarchical, not blackboard, not actor/supervisor, not contract-net, not
stigmergic, not generator–critic. Then it names the mechanism that would — task structure — which
is precisely what R8 recommends changing.

⭐ **Two independent passes, from opposite directions, converge on the same answer: reorganising
the agents buys nothing; re-scoping what they touch buys everything.** That is the strongest
result in this document, and it retires the idea that a cleverer topology is worth pursuing.

### 14.2 The platform question is settled, and it settles against R15

| | Recommends | Argument |
|---|---|---|
| **R15** | a **Rust/Tauri desktop app** | lean binary, fast start |
| **R13** | a **VS Code extension** | the operator is already in VS Code, so cold start is *nothing*; Monaco, LSP, Git, diffs and file-watching come free; *"the line past which we rebuild an IDE is reached as soon as we start re-implementing code editing, syntax highlighting, search, diffing, branching"* |

**R13's argument is stronger and it is also the cheaper one**, which matters because the operator's
stated constraint on 2026-08-23 was that a desktop app is unaffordable in time. R13 puts Electron
out on weight (100–200 MB for a hello-world; Slack and Discord over 500 MB), keeps Tauri/Wails as
the runner-up, and notes a TUI as a last-resort fallback.

**Take R13's platform answer over R15's.** Note it also resolves the repo-integration ask directly:
opening files, diffs, staging and committing are things VS Code already does, and building them
again is the definition of rebuilding an IDE.

⚠ **But R13 was arguing partly blind.** Its §8 says: *"We must build on top of the existing four
interfaces (and one dead one). **Without detail on those, we assume multiple UIs (CLI, web panel,
maybe Slack bot)**."* It never read `ui-surface-inventory.md`, which describes those four surfaces
precisely and was its named attachment. So its **migration section is guesswork and should be
discounted**, while its platform, latency and approval sections — which did not need the inventory —
stand.

### 14.3 Three independent sources now name the same first move

R13's executive summary picks **urgent human notification** as the first change to make, *"since
the measured backlog shows humans are the bottleneck (agents queue for days)."*

That is the third independent arrival at the same conclusion:

| Source | Basis |
|---|---|
| Measurement, 2026-08-23 | two PRs green and waiting **6 and 9 days**; four agents blocked on written questions nobody read |
| R12 §4.2 | *alarm absence*, not alarm fatigue — action-required notifications must interrupt |
| R13 §6 | *"Our failure is not over-alerting (fatigue) but under-alerting"* |

R13 adds the evidence tier honestly: there are **no studies on AI-agent prompts specifically**, so
it borrows from incident management — passive channels (email) take hours, SMS/phone/vibration get
under five minutes. `REPORTED`, and labelled as such.

**When three passes and one measurement agree, stop asking and build it.**

### 14.4 The non-engineer approval question — answered, and the answer is "nobody has"

R13 surveyed GitHub Agentic Workflows, Copilot Workspace, Graphite, Factory.ai Droid and Cursor
Cloud Agents. The state of the art is **pull-request gating with AI assistance**: work arrives as a
diff, with evidence in the PR body, and a human approves. Copilot Workspace makes *every step*
subject to approval; Cursor found that gating every step causes fatigue and now classifies by risk.

> **"We found no off-the-shelf tool targeting business users reviewing code changes."**

So the APPROVE-plane surface for a non-engineer is genuinely unbuilt, and R13 names what it would
have to show: **context** (why, in plain language), **proof** (tests, logs), **cost** (tokens,
time), and **provenance** (which agent, which config).

### 14.5 Provenance — a small, adoptable answer for the 0-of-15 hash

R13 recommends aligning to the **OpenTelemetry GenAI semantic conventions** (`gen_ai.*` — agent
identity, model version, token counts) and emitting a **simple JSON provenance record per commit**,
SLSA/in-toto in shape but not in ceremony. Explicitly **skip** cryptographic signing, TEEs and full
attestation as over-engineering at our size, and skip data-lineage tooling because our inputs are
code and git already records ancestry.

That is directly actionable against the config hash covering **0 of 15 dimensions**: the dimensions
it names — model ID, prompt version, tool versions, commit hash, agent ID — are the hash.

### 14.6 ⛔ Three passes have now avoided the terminal question rather than answering it

- **R7** restated our own position back to us.
- **R15** answered it with a **fabricated user study** (§13.5).
- **R13 §9** says: *"The operator has indicated the terminal should remain an escape hatch only.
  Therefore, we will not build the UI around an embedded shell."*

That third one is deference, not argument. R13 §6 asked it to argue the question **on the merits**
and to give both branches; it took our position as a premise instead.

**The practical consequence is small and the methodological one is not.** Practically, every pass
now points the same way and the operator's own position is that terminal mode should exit — so the
decision is not in doubt. Methodologically, **we have paid four times for an answer to a question
none of them answered**, and the reason is the same each time: we stated our position inside the
question. A question you cannot ask neutrally should be settled as a decision and removed from the
brief, not carried into a fifth pass.

**Action: write it as a decision, and stop asking.**

### 14.7 What changes — additions to §13.7

1. **Platform: a VS Code extension**, not a desktop app (§14.2). Cheapest, and it inherits the
   editor, Git and diffs rather than rebuilding them.
2. **Build the notification channel first** (§14.3). Three passes and one measurement agree.
3. **Stop surveying orchestration topologies** (§14.1). Seven were checked and none moves the cap.
4. **Config hash: adopt the OTel GenAI field set** (§14.5) — it is a list of the dimensions we are
   missing, already written down.
5. **Discount R13's migration section** (§14.2) — it guessed our surfaces.
6. **Settle the terminal question as a decision and delete it from every prompt** (§14.6).

### 14.8 What R13 could not settle

- **Our conflict graph specifically.** It reasons about a 3-lane cap in the abstract and never
  opens `lanes.py`, so "which topology suits *our* graph" is unanswered — though §14.1 makes that
  moot.
- **Whether a VS Code extension can host the approval surface well.** It recommends the platform
  and the surface separately and never checks that the second fits inside the first.
- **Anything measured about our latency.** Its budget (first paint <100 ms, interaction <50–100 ms,
  full re-measure <500 ms) is from user-perception guidelines, `INFERRED` — not from profiling the
  9.3 s we measured.
