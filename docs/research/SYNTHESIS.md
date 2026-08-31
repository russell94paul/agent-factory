# Synthesis — what the research passes concluded, and what changes

⚠ **The title used to say "thirteen research passes" and had said so for three additions.**
**Eighteen ids are filed in `answers/` — R1–R8 and R10–R19, R9 withdrawn — across twenty-one answer
documents** (R4, R13 and R16 each filed twice; the three `*-followup.md` files are questions, not
answers). The count was a number nobody could make move, which §15.4 is about. Removed from the title
rather than re-fixed, because it will go stale again — and per the standing rule it now travels with
the command that produces it, so the next reader re-measures instead of trusting this line:

```bash
python -c "from factory.synthesis import filed; print(len(filed()))"          # 18 ids
ls docs/research/answers/*.md | grep -vE 'README|followup' | wc -l            # 21 documents
```

Mentioning an id is still not reconciling it (`factory/synthesis.py` says so in its own docstring).
⛔ **§17 is the reconciliation, and it found more than an absorption gap: seven sentences in this
document assert that an answer has not landed, and all seven are false.** Read §17 before trusting a
status claim anywhere above it.
⚠ **§18 folds in R19 (added 2026-08-29) — and §17.11 rows 29, 30 and 34 are still `not started`, so
the newest answer now has a section while R14 and R18 still do not.** That is §17.4's shape repeating
inside the fix for it, and it is recorded in §18.11 rather than left for a later pass to discover.

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

⚠ **Tier those two Anthropic numbers — §16.6.** The 90.2% is `MARKETED` (internal eval, LLM judge,
internal rubric, no independent confirmation), and Anthropic publishes *both* "~15× more tokens as
chats" and "3-10× more tokens than single-agent approaches" on different pages. We cite them
*against* multi-agent so the conclusion is unaffected, but the figures travel with those caveats now.

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
  **structural** (one agent deleting a file another edited), not line-level. ⚠ **That is the correct
  attribution and five other places in this repo lost it — §16.1.** The 41.7% is a published finding
  about other people's repositories. It has never been measured here.
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

Three answers landed together. ~~R8 is still outstanding.~~ ⛔ **Stale — R8 was filed at 07:35 the
same day and is §13; this sentence has been false since before §13 was written (§17.1).** R9 was
dispatched and **withdrawn** the same morning as not useful, so no R9 answer will be filed — if one
arrives it is discarded.

### 12.1 The convergence, and it is unanimous

Independently, on three unrelated questions, all three said the same thing: **do not build new
substrate; fix and use what exists.**

| Pass | Asked | Answered |
|---|---|---|
| R10 | should we build a hierarchical wiki + auto-researcher | **No.** "Don't build a fancy hierarchical auto-updating wiki before we fix the basics." |
| R11 | what do other factories make first-class that we lack | Seven absent concepts, **every one costed as significant engineering**; none recommended now — ⚠ **R11 counted nine and §12.5 names six; §17.8** |
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

⭐ **R17 puts a measurement under this — §16.7.** A gate at the first artefact boundary catches
**75.4%** of the defects the same gate at the last boundary catches **10.7%** of, and
end-of-pipeline verification buys **+2.3 pp over no verification at all**. The guardrail gap is not
a taxonomy tidy-up; it is where almost all of the detection is.

Second: **task packaging** (METR Task Standard — task + environment + scoring as one reproducible
unit). That is the same question R8 asked about isolation tiers, arriving from the benchmark side.
⛔ **"Read them together when R8 lands" — R8 had already landed. It never was read together with
this: §13 takes R8's isolation half and no section joins it to task packaging (§17.1).**

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

Both landed after §12 was written. ~~R13 and R14 are still out.~~ ⛔ **Stale — R13 is §14 and R14
was filed 13:38 on 2026-08-23 and has no section anywhere (§17.2).** R9 was withdrawn.

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

⛔ **"Enforceable in code" was wrong, and §16.4 supersedes this.** R17 read Snowflake's own docs: a
rule about what SQL an agent may write is an instruction living in a repo the agent can edit. The
mandatory version of the same intent is a **grant** — the lane's role owns no production object, so
`CREATE OR REPLACE` is not available to it at all. Keep the intent, replace the mechanism.

### 13.3 ⚠ A correction to what "unattended" can mean

Our readiness set asks *"can an agent team run a connector migration unattended?"* R8 puts a number
on the state of the art, `REPORTED` from an Anthropic study: **99.9th-percentile autonomous turns
last ~45 minutes, and the median is under a minute.** Longest productive production runs are *"tens
of minutes, not hours or days"*, and most teams deliberately break runs under an hour to bound risk.

**So the honest target is a 30–45 minute unbroken run, not an unattended migration.** Our 3-of-14
figure is not far off a field that mostly does not attempt more. This does not lower the bar for
*certification* — it changes what the bar is measuring.

⭐ **Independently corroborated and sharpened by R17 — §16.8.** The number to compare against is the
**80%** horizon (Opus 4.5: **27 minutes**), not the 50% one; METR states outright that its horizon is
*not* unattended runtime; and 3-of-14 is normal-to-good against the only measured long-horizon suite.

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

### 13.6 ✅ R12 and R15 contradicted each other — SETTLED 2026-08-23, R12 was right

R15's own §0 named R12's source-level findings as its **control case**. It reached the opposite
conclusion and did not notice:

| | Claim | Tier |
|---|---|---|
| **R12** | switchboard *"never attaches to an arbitrary running process; it only re-uses PTYs that it itself spawned"* — and will **spawn a second process against the same session id** | OBSERVED |
| **R15** | *"ATTACH: Yes – it can attach to any running session… It detects any Claude session in the project folder, not just those it spawned"* | OBSERVED |

**Both cannot be true, and the answer decides whether adopting switchboard reproduces the exact
duplicate-session failure of 2026-08-23.** Neither is stronger on its face: both claim to have read
the source, and neither cites a line.

**The discriminating test was cheap and it has now been run.** R13 run 2 read
`doctly/switchboard` `main.js` at commit `4c5a6da4ee23818584a53094e85989d7143da0c4`, and the result
was **independently re-verified against the raw file from this session** before being recorded here
— because §13.5's own heading is *"one answer invented its evidence"*, and a settled verdict
resting on a single unchecked citation would be the same failure again.

**Verdict: R12 is right. R15 is wrong.** `activeSessions` is an in-process `Map` (`main.js:101`)
and the `open-terminal` handler (`main.js:1288`) returns `reattached: true` only when that Map
already holds the id. A search of the file for `kill(0`, `tasklist`, `process.kill`, `ps -` or any
lockfile check returns **zero hits** — there is no OS-level liveness probe anywhere in it. R15's
*"it detects any Claude session in the project folder"* is not supported by the source.

⭐ **And the third reading both passes missed, which is the part that matters.** Switchboard does not
"spawn a duplicate" — it unconditionally issues `claude --resume <sessionId>` and never checks
whether anything else holds that id. Whether a second live process results is decided by the Claude
CLI, a program switchboard does not consult, does not control, and whose refusal it never surfaces.
So the honest verdict is **not "it duplicates" but "it has no guard, and delegates the guard to
something it cannot see"** — which is worse, because it is unobservable: the UI reports the same
*not running* for **exited**, for **running-outside-switchboard**, and for **running-and-refused**.

This is not a patchable bug. It is the **absence of a liveness concept** — the thing
`ui-surface-inventory.md` §6 item 3 records that we had to invent for ourselves, and the reason our
four states (including `RUNNING-ORPHANED`) are a real lead rather than a reimplementation.

⚠ **One scope correction to R12:** the exposure is *not* limited to sessions started outside
switchboard. A crash leaves the Map empty while PTYs may survive (the tidy-up only runs on
`closed`/`will-quit`), and the fork path re-keys a live session under a `realSessionId`, so
`has(sessionId)` can miss a PTY switchboard **does** own.

### 13.7 What changes

1. **Do not adopt R15's desktop app.** ⛔ **The rest of this row is wrong three times over and every
   correction was available before it was written (§17.8).** §13.5, eleven lines above, calls
   "9.3 s → ~1.2 s, ~30 lines" *"wrong by about eight times"*; R13 run 2 §2 records that
   `ThreadingTCPServer` and the suite cache had **already shipped**, taking the warm render to 0.84 s;
   and R13 run 2's answer to "what is the remaining latency work worth" is **stop**. The live work is
   the duplicate `measure()` and four page strings asserting the page caches nothing while it caches.
   Then apply R14's design — which also has no section (§17.2).
2. **Containerise agent execution on one machine** (R8's smallest impactful change), before any
   cloud step. The first break is credentials isolation, and F53 is the evidence. ⚠ **Narrowed by
   §16.5**: a plain container is not the boundary — a frontier model escaped Docker/K8s in ~49% of
   measured attempts — and there is a cheaper first move than containerising anything, using
   settings already shipped in the tool we run.
3. **Adopt the mandatory-clone rule** (§13.2) — enforceable in code, no new discipline.
4. **Restate the unattended goal as a 30–45 minute unbroken run** (§13.3), and say so in the
   readiness set rather than leaving the gate asking for something the field does not attempt.
5. **Read switchboard's `open-terminal` handler** and settle §13.6. One file.
6. **Take R8's isolation argument, leave its scheduling and messaging recommendations** (§13.4).

### 13.8 What they could not settle

- **R8:** whether zero-copy clones are cheap to *validate against* at our data volumes — it asserts
  near-zero creation cost but does not cost validation, which was half of architecture-v0's §7
  worry. And "10+ agents on a modern server" is `INFERRED`, with no measurement behind the number.
  ✅ **Answered by R17 (§16.3), and the question was the wrong one.** Validation compute scales with
  query-seconds, not lane count, so the cost worry was attached to the wrong variable. What actually
  breaks the clone story is that it is a different privilege path, a different temporal path, and —
  for share-consumed data — not available at all. And R8's "10+" is refuted: see §16.2.
- **R15:** anything about design craft — no type scale, no colour system, no hierarchy, no motion,
  and no mention of `UNMEASURABLE`, which is the colour problem no standard palette solves. That is
  ~~R14's job and R14 has not run.~~ ⛔ **R14 ran and answered it in §6.4 — two channels, hue for the
  subject's verdict and treatment for the instrument's state, so `UNMEASURABLE` renders colourless
  rather than amber, because amber says "nearly bad" and the true statement is "there is nothing here
  to read". No section here records it (§17.2).**


---

## 14. R13 — the platform question, settled; and three passes now agree on the first move (added 2026-08-23)

R13 landed after §13. ~~Only R14 remains unsent.~~ ⛔ **Stale, and it was stale when written: R14
was filed at 13:38 and §14 was written after §13.5, which cites R13 run 2 — filed 13:34. Four minutes
apart. §17.2.**

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

⛔ **Half of that survived R17 and half did not — §16.2.** "Reorganising the agents buys nothing" is
now a *theorem* rather than a survey result, which is stronger than what is written here.
"Re-scoping what they touch buys everything" is **refuted as stated**: cloning removes one class of
conflict edge and adds three the conflict graph has no representation for. The cap is replaced, not
lifted. Do not cite this paragraph without §16.2.

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


---

## 15. R16 — the decisions attacked, and two instruments that could not do their job (added 2026-08-23)

Run as **two local Claude subagent lanes**, not an outside model: an audit lane instructed
blind-first (read each cited answer and form a view *before* reading what this document concluded),
and a separate **outside-evidence lane** that searched the open web and only then read our
positions. Filed at `answers/R16-answer-decision-review-and-order.md` and
`answers/R16-outside-evidence-lane.md`.

⚠ **This was the least independent pass we have run, by its own brief's warning and then some** —
it reads our conclusions, from inside our repo, on our conventions. Grade its file-and-line claims
as strong and its judgement as partial. It was scored on disagreements found, and it found eleven.
**Two were verified here and acted on the same day. Nine are open.**

### 15.1 ⭐ `g_version_hash_is_complete` could never pass — U+0008 in the regex

`OBSERVED`, from the raw bytes of `factory/readiness.py:870`, and re-verified independently before
being written down here:

```
rf"\x08{d}\x08"      the bytes that were actually in the file
rf"\b{d}\b"          what was meant
```

Someone wrote `f"\b…"` without the `r`; Python resolved `\b` to a literal **backspace control
character**, and it was saved. `sed`, `inspect.getsource` and every editor render it as nothing,
which is why four readers quoted this gate's output and none questioned it.

A backspace cannot occur in Python source. **The pattern could never match, so the gate could only
ever return `0 of 15` and could only ever FAIL.** This repo's thesis is that a green from an
instrument that cannot refuse is worthless; `readiness.py:88-97` already names an instrument that
cannot *pass* as an equal defect. We were publishing one.

**True figure: 6 of 15.** The job is **nine** dimensions, not fifteen. The wrong number was
load-bearing in two places and cited in four:

| Where | Use |
|---|---|
| §14.5 above | the basis for action a16 |
| `R13-answer-…-run2.md` §1 | "Option E is **blocked** on its own prerequisite" |
| `R14-answer-…` §5 | "Build the fifteen dimensions; do not rename the zero" |
| `ui-surface-inventory.md` §9 | listed as one of three things nobody else ships |

⚠ **Neither conclusion flips** — the hash is still incomplete and `contract_version` is still among
the missing — **but the size of the job was overstated by two thirds.** Fixed 2026-08-23, along with
the same bug in `scripts/file_answers.py:74`, which had silently killed one scoring term in the
router that files these answers.

### 15.2 ⭐ All three gate edges on the decisions were wrong

`factory/roadmap.py` claimed its load-bearing property in its own docstring — *"an action linked to
a gate takes its status FROM the gate, always… it makes the hand-maintained part visibly
hand-maintained instead of letting it borrow the credibility of the measured part."* All three edges
were then verified and all three were wrong:

| Action | Gate | What the gate actually asks |
|---|---|---|
| a8 "containerise **agent execution**" | `isolated` | whether an **evaluator** is a separate principal. One env var + a class would render a8 SHIPPED **with zero agents in containers** |
| a10 "restate the goal as **30–45 min**" | `finishes` | counts completed runs, **no duration term at all** — and a10 is a proposal to *change this gate*, gated on the unchanged gate. Circular |
| a16 "adopt the **OTel** field set" | `version` | whether declared dimensions appear in `blueprint.py` — it cannot see where the set came from, and per §15.1 it could not pass at all |

⭐ **So the half of the roadmap presented as `MEASURED` was the least reliable half** — the exact
inverse of the design intent, and by our own standing rule worse than an admitted gap.

Edges dropped. **The honest count is now 0 MEASURED / 18 AUTHORED, and that is the finding rather
than an omission.** `_validate()` could only ever prove a gate *exists*; nothing checked that its
QUESTION matched the action's SUBJECT, and the author did not. A gate edge now requires a
`why_gate` sentence — a weak control, but it forces the mismatch to be considered.

### 15.3 What R16 raised that is still open

Nine of eleven, unactioned and recorded here so they are not lost:

- **The eval corpus** — R16 calls it *"one file, and the thing every pass assumed someone else
  had"*. Flagged by the pass as larger than either defect above.
- **a14's own citation is contradicted by the two passes that landed after it** (§2.2).
- **a3 and a14 are one piece of work** and the answers already name the object (§2.3).
- **a1 is filed under a reason superseded twice over** (§2.4).
- **The 7-versus-13 incoherence is already resolved** — in an answer this document never absorbed
  (§2.5). That is a reconciliation failure, not a research gap.
- **a4 and a5 rest on an instrument a6 shows to be unreliable** (§2.6).
- **a15's stated reason is a sample; its real cause is elsewhere** (§2.7).
- **a8's payoff is refuted by R14**, and a8 is the most expensive action on the list (§2.8).
- **a9 asserts an enforceability it does not have** (§2.10).

~~⚠ **The outside-evidence lane's answer has not been read yet.** It is filed and unreconciled.~~
⛔ **Contradicted four paragraphs later by §15.5, which opens *"Read 2026-08-23, after §15 was first
written."* Both sentences still stand. ⚠ And §15.5 absorbed that lane's executive summary only — its
§1, the sole external challenge to §5's build order, never reached §5 (§17.6).**

### 15.4 The lesson that generalises

**Two of our instruments were broken in the same way and neither could report it.** A regex that
could not match, and a validator that checked an edge *resolved* rather than that it *decided
anything*. Both produced confident output. Both were quoted onward.

⭐ **A number nobody can make move is not a measurement — it is a constant with a citation.** Before
trusting any figure this estate publishes, ask what would have to change for it to read differently,
and whether that is even reachable.

### 15.5 The outside-evidence lane — and it attacks the action three passes agreed on

Read 2026-08-23, after §15 was first written. It searched the open web on five sequencing
questions, then read our positions. **Its target turned out to be a14 — "build the notification
channel first" — which §14.3 calls the first move and attributes to three independent sources.**

⛔ **1. The "three independent sources" is one measurement read three times.** R13's stated basis is
*"the measured backlog shows humans are the bottleneck"*; R12's is *"we saw four agents stuck with
unanswered questions"* (`R12-answer-session-manager-ui.md:58`). **Both reason from the same
2026-08-23 measurement, which §14.3 then lists as the third leg of the tripod.** R13 says so itself:
*"there are no studies on AI-agent prompts specifically."* **Nobody has published a build-order
claim that the notification channel comes first.** The convergence we treated as the control was an
echo.

⭐ **2. Oversight has a capacity, and safety is an inverted-U in escalation rate.** *Oversight Has a
Capacity — Calibrating Agent Guards to a Subjective, Fatiguing Human*, Emre Turan,
`arXiv:2606.08919`. Under a paranoid policy escalating **88% of routine actions, attack success
reaches ~80%**, and is already **40% at just 50 filler actions**. The paper's conclusion:
*"escalating everything is strictly worse than the optimum."*

⚠ **Basis `DERIVED`, and the author says so** — *"the inverted-U is simulated, not measured."*
⚠ **Citation verified here**: the paper exists, title and author are exact. **The lane dated it
11 Aug 2026; v1 was submitted 8 Jun 2026.** Substance held, precision did not — the second time in
two passes (cf. §15.1's line numbers), which is why the check is not optional.

**a14 as written names a channel and no routing policy. A channel with no policy is precisely the
design that paper places on the bad side of the curve.**

**3. a16 is a much smaller answer than §14.5 claims.** Read from the raw
`model/gen-ai/registry.yaml` (72 attributes), the OTel GenAI set covers **5 of our 15** dimensions —
`prompt.version`, `request.model`, `request.reasoning.level`, `tool.definitions`, `data_source.id` —
and **misses every one §14.5 says bites**: `contract_version`, `permissions`, `sandbox_image`,
`harness_version`, `max_turns`, `budget_usd`, `model_routing`, `context_policy`,
`tool_implementation`, `side_effect_replay`. **There is no commit-hash attribute at all**, which
§14.5 explicitly lists as one it names. `OBSERVED`.

⚠ **4. And its maturity is worse than "experimental".** Every attribute is `stability: development`;
the `gen_ai.*` attributes were **deprecated out of the main semconv registry** into a separate repo;
that repo has **zero releases**; and its README's Schema URL section reads, in full, `TODO`.
**You cannot version-pin what you emit against it.** `OBSERVED` — the lane read the YAML, the README
and the releases page.

**5. a8's gate binding is vacuous** — found independently, without seeing the audit lane's §2.1.
⭐ **Two lanes that could not see each other converged on the same defect.** That is what the
control was for, and it is the strongest signal either produced.

**6. The cap the outside names and we do not — human review throughput.** Our concurrency answer
(§14.1, a15) is about writers and files. Practitioners name a second ceiling: *"with each agent you
have more code to review"* — and our own measurement (two green PRs at 6 and 9 days) **is** that
ceiling. We filed it under notification. ⭐ **The estate's binding limit last month was not 3 lanes,
it was 1 reviewer** — and a notification channel does not add review capacity. It makes the queue
arrive faster at the thing item 2 says degrades under load.

### 15.6 What this does to the build order

**Do not treat a14 as settled.** It is the action with the most apparent agreement and the least
external support, and two of the six findings above argue it is aimed at the wrong constraint.

If the binding limit is reviewer throughput, the useful first move is something that **raises review
capacity or lowers what needs reviewing** — not something that delivers the queue sooner. That is a
different action, and ~~nobody has written it down yet.~~ ⛔ **it had been written down twice
before this sentence was typed — R13 run 2 §3 and R16 §4 step 1, the latter costed at one hour and
named as the item that decides a14. §17.7.**

✅ **A fourth pass reached the same place independently, and it names the action — §16.9.** R17
measured the ceiling at 22,000 developers (median review time **+441.5%**, PRs merged with **no
review +31.3%**) and draws the conclusion this section stops one step short of: *raising lane
concurrency before the evidence gate is made sublinear reduces safety, not just speed — because a
saturated gate does not present as a queue, it presents as a bypass.*


---

## 16. R17 — the external half of R8, and the first pass that checked its own citations (added 2026-08-23)

R17 exists because R8 failed the same way twice (its brief says so): run 1 had no repository access
and was rejected; run 2 had a 481 KB evidence pack and filed an answer with **zero** file paths and
**zero** line references. So R8 was split — R17 surveys the field with **no internal facts at all**,
R18 audits us from inside the repo. **Nothing in R17 is a claim about our code**, by construction:
it answers `NOT-APPLICABLE (R18)` to everything internal, and it kept that discipline.

⚠ **Grade the instrument first, because that is the house rule — and this one grades itself
correctly.** R17 ran as **local subagents** via the `deep-research` skill: five lanes dispatched in
one message so they could not see each other, on deliberately different search modalities (papers
and framework source · vendor docs and runtime source · primary Snowflake/dbt reference pages ·
field reports and benchmarks · **counter-evidence only**, instructed to default to REFUTED), ~196
searches, then **38 citation verifications performed by the orchestrator directly against primary
sources**. Thirty-three confirmed; **five did not and were corrected in the open** (§16.10 keeps one
as a worked example). Its own §11 states both halves: *less independent* than an outside reader —
every lane read our brief and agents inside our estate are pulled toward agreement — and *stronger
on file-and-line claims*, because an outside pass cannot fetch Snowflake's `data-share-consumers`
page and read the sentence that kills a design we were about to build on.

⭐ **Weigh it accordingly, and it is a new grade for this programme.** Its verbatim vendor-doc
quotations are the strongest evidentiary layer any pass has produced — a documented grant or a
documented "not supported" is not an opinion that can be re-litigated. Its **ordering and its
opinions are partial**, exactly as R13 run 2 and R14 were weighed. The distinction matters below:
where R17 quotes a doc it wins outright; where it ranks actions it is one voice.

### 16.1 ⛔ The 41.7% is a citation wearing a measurement's clothes — R17 flagged it, and the discriminating test has now been run

R17 raised this against **its own brief**, unprompted, and correctly refused to settle it: *"I cannot
see your repo and did not try."* It handed the test to R18. **The test is one grep and this pass ran
it, because leaving it open would be the third repetition of F7 rather than the end of it.**

| Field | |
|---|---|
| **BELIEVED** | Stated as internal context in `R17-data-engineering-external-survey.md` §0b: *"a shared branch **was measured** at a 41.7% cross-agent conflict rate."* |
| **ACTUALLY** | It has never been measured here. The figure is a **published finding about other people's repositories** — arXiv 2607.04697v2, 33,596 agent PRs across 2,807 repos: *"Cross-Agent Pairs (115 evaluatable out of 122): 41.7% textual conflict rate (48/115, 95% CI [33.1%, 50.9%])"*. R17 verified that sentence verbatim [D-14 ✓]. Our own R5 answer states the provenance correctly and always did. |
| **MEASURED BY** | `grep -rn "41\.7"` over the repo, this session: every occurrence traces to `answers/R5-answer-build-velocity.md:25`, which says *"A large empirical study of 33K agent-generated GitHub PRs found…"*. `ls docs/evidence/` contains **no conflict-measurement artefact of any kind**, and nothing in `factory/` or `scripts/` records an observed conflict. R17 named the discriminating evidence precisely — *"an internal measurement log dated before 2026-07-07 settles it in your favour"* — and there is none. |
| **AFFECTS** | Every lane, and specifically anything that cites the figure as ours. Belongs in `docs/findings.md` as **F11**; this pass may write only this file, so it is recorded here and §16.13 row 16 carries the fix. |

**The drift is documented, and it is the interesting part.** The claim was never fabricated — it
degraded across six restatements, and the tier degraded with it:

| Where | How it reads | Tier as written |
|---|---|---|
| `answers/R5-answer-build-velocity.md:25` | "A large empirical study of 33K agent-generated GitHub PRs found…" | correct, sourced |
| `SYNTHESIS.md` §10.1 | "**R5, from data.** A study of ~33,000 agent-generated GitHub PRs" | correct |
| `factory/worktrees.py:3-4` | "R5 **from measurement**" — names the study, calls it measurement; line 12 then says "the thing that was **actually measured** as failing" | slipping |
| `scripts/local_tracker.py:124` | "the setup **R5 measured** at a 41.7% cross-agent conflict rate" | drifted — ships in the tracker page |
| `R13-evidence-pack.md:288` | "`MEASURED` 41.7% conflict rate on a shared branch (R5)" — in a table whose neighbouring rows are genuine internal measurements | **tiered `MEASURED`** |
| `R13-evidence-pack.md:837` | the same number, in the same document, tiered **`REPORTED`** | self-contradictory |
| `R10-…-agent-training.md:137` | a bare row — "Cross-agent conflict rate on a shared branch \| 41.7%" — inside a table headed `Figure \| Value` listing *our* figures (9 of 30 gates, 3 of 14 runs, 0 of 22 refusals) | reads as ours, no source |
| `R17-…-survey.md:99` | "a shared branch **was measured** at 41.7%" — fed to an outward-facing pass as fact | terminal form |

⭐ **This is the F7 class a third time, and the mechanism is new.** F7 was one false sentence written
into R6's prompt; §12.2 was one true constraint left out of R12's. This is neither: **no single step
was a lie, and the composition is.** Nobody decided to claim a measurement — each restatement dropped
one qualifier, and the last one was true of nothing. R17 names this class from the literature and it
is the sharpest thing in the answer for us: **attribution error is distinct from support error** —
*"a claim may be supported somewhere in the evidence while being attributed to the wrong source"*
[A-55]. The claim is supported. It is attributed to us. **A support-only checker passes it**, which
is exactly why six readings did.

⚠ **The self-undermining tell was on the page.** §0b's own sentence says agents *"run today as
parallel sessions in git worktrees"* and, in the same breath, that *"a shared branch was measured"*.
If we run in worktrees, when was the shared branch measured? Nobody asked. (For the record, four
`lane/*` worktrees now exist — `git worktree list`, this session — so §8 row 10 is at least partly
built and its state line is stale; that belongs to whoever owns the row.)

**Does the false premise change R17's answer? No — and that is the difference from F7.** R6 *deferred
CI on push* on the strength of my false sentence, and its ranking moved. R17 treated §0b as
context-not-claim, flagged the figure as suspicious without being asked, and built its concurrency
verdict on a theorem [A-24 ✓] and a 22,000-developer study [E-17 ✓] rather than on the number.
It also went looking adversarially for evidence that 41.7% is anomalous and **failed to find any**:
AgenticFlict measures **27.67%** across 107K+ agentic PRs from 59K+ repositories [E-20], the same
order, and a cross-agent-on-a-shared-branch figure *should* run higher than a measured-against-main
one. **So the recommendation stands and only the basis changes** — which is the whole point of
recording the basis separately from the conclusion.

⚠ **The second §0b assertion is worse, and R17 leaned on it.** §0b also states *"Zero cross-lane
conflicts observed."* There is no instrument that could have observed one. `lanes.py::conflicts()`
**predicts** a conflict graph from declared file-touch sets; `claims.py` **refuses** to let two
conflicting lanes be claimed at once. The system is built to make the event impossible, and the zero
is its output. By the estate's own four verdicts that is **NOT-VISIBLE, not ZERO** — a zero from an
instrument nobody proved could see. R17 read it as a signature: *"zero observed cross-lane conflicts
is the signature of a graph that over-approximates."* **That inference is unsupported by that datum.**
Its independent support — Gray's 1976 granularity result that a coarse lock "locks more data than a
transaction needs to access" [E-2], and semistructured merge halving reported conflicts with **no
additional false positives** [E-4] — is untouched, so the *recommendation* (measure whether the file
graph over-approximates) survives on evidence that does not come from us.

### 16.2 ⭐ R17 contradicts §14.1's "strongest result" — one half is now a theorem, the other is refuted

§14.1 concluded, from R13 and R8 arriving oppositely: *"reorganising the agents buys nothing;
re-scoping what they touch buys everything."* R17 answers both clauses and splits them.

**Clause one — upgraded from a survey to a proof.** R13 checked seven orchestration patterns and
found none raised the cap. R17 explains why none ever could: under a conflict graph the instantaneous
ceiling is the **maximum independent set α(G)**, scheduling everything into rounds is bounded graph
colouring, and the scheduling literature proves the problem generalises graph colouring and is
strongly NP-hard [A-24 ✓, A-25]. A topology is a decision procedure over who runs when — *it cannot
select more than α(G) pairwise-non-adjacent vertices because there aren't any*. For a dependency DAG
the name is width and Dilworth gives it exactly [A-26]; the database version is the precedence graph,
which carries the design lesson explicitly — **concurrency comes from touching disjoint data, not
from a better scheduler** [A-27]. Blumofe & Leiserson close it formally: every topology is a
scheduler, schedulers redistribute `T₁/P`, **none touch the critical path `T∞`** [E-1]. Contract-net
answers itself — auctions solve assignment *under uncertainty about capability or cost*, and with a
known static graph and homogeneous agents there is nothing to discover [A-58, A-59]. **§14.7 item 3
said "stop surveying orchestration topologies". It can now say the stronger thing: there is nothing
to survey.**

**Clause two — refuted as stated, and this is the disagreement of the section.**

| | Claim | Basis |
|---|---|---|
| **R8** (§13.1) | container + own DB clone per agent ⇒ ceiling becomes resource-bound, *"potentially 10+ on a modern server"* | `INFERRED`. §13.8 already recorded that no measurement sits behind the number |
| **R17** (§4.5) | cloning removes **exactly one** class of edge — the physical write collision on a shared table, *"the class your file graph was already catching cheaply, and which on this evidence was never the binding constraint"* — and **adds three the graph has no representation for** | `OBSERVED` from vendor docs (✓ verified) plus `REPORTED` field studies |

**R17's evidence is stronger and it is not close.** R8's ceiling is an inference with no measurement;
R17's three added edge-classes are each documented:

1. **A shared name-and-manifest space.** dbt states the collision outright: without the target-schema
   prefix *"every dbt user would create models in the same schema and overwrite each other's work"*
   [C-57]. Two lanes can share zero files and zero rows and still resolve `{{ ref('dim_customer') }}`
   to the same physical relation. **The namespace is a shared mutable resource the file graph does
   not model.** Looker is the industry's best case — real per-developer semantic branches — and it
   *still* funnels every developer's PDTs into **one** scratch schema with an explicit warning about
   "PDT management conflicts" [C-65]. ⭐ **Branching the definition does not branch the artefact.**
2. **A shared compute queue.** Past `MAX_CONCURRENCY_LEVEL = 8` queries queue [C-46]. Lanes do not
   corrupt each other here, they **starve** each other — and ⚠ *a lane whose validation times out
   reports a false negative*, which is this repo's central failure shape arriving through the
   warehouse.
3. **A shared clone-provenance surface, including cross-cutting singletons.** Policy objects and
   shares live in no lane's schema, so no schema-level isolation catches them (§16.4). Plus the
   silent ones: 24 clones across 8 teams, *"186 of 280 views had hardcoded production references"*,
   47 broken CDC pipelines, ~25 person-hours of manual fixes per clone [C-73].

⭐ **And the one the model structurally cannot see: polysemy.** Data-mesh literature names it as the
standard failure of decentralised ownership [E-33], and the field report is exact — two models named
`customer_metrics` in different folders **producing different numbers**. *"No merge conflict was
raised. Nothing failed. Two numbers were simply wrong in different ways"* [C-72]. That is the error
profile R17 calls the worst possible: **over-counting syntactic conflicts while scoring the real ones
as clean.**

⚠ **Do not average these into "clones help somewhat".** The honest reconciliation is R17's own
reframing: *"two agents in two ephemeral clone schemas conflict on nothing **they can see**."*
Cloning is worth doing. **The cap is not lifted, it is replaced** — by one set by whether we have
modelled the name graph and the compute graph, and neither exists. R17 also observes that our 3 may
not be α(G) at all: practitioner consensus on parallel coding agents is 2–5 lanes with the explicit
rule *"increase concurrency only when your review process can keep up"* [E-32] — so our file-conflict
cap and the field's review-bandwidth ceiling coincidentally produce the same number, and **raising
one buys nothing while the other binds** (§16.9).

⭐ **The third option neither R8 nor R13 named: conflict-graph *resolution*.** A file-level conflict
graph **is** coarse-grained locking [E-2], so tasks may already be independent and the instrument
cannot see it. Semistructured merge halves reported conflicts with no additional false positives
[E-4] — a free doubling of measured independence with no topology change. ⚠ Two hard edges, which is
why this is a recommendation and not a free win: pointer analysis for semantic conflict detection
buys precision at *"prohibitive drops in recall"* — it starts calling **real** conflicts clean [E-5],
which for a `CREATE OR REPLACE` on a shared warehouse is a silent production defect; and optimistic
concurrency control **inverts under contention** [E-6]. And deleting edges is necessary, not
sufficient: CodeCRDT removed file-conflict edges entirely and got **+21.1% on some tasks, −39.4% on
others**, with 5–10% semantic conflict rates [A-28]. **Resource-disjointness is not
content-disjointness** — two agents in two isolated clones both reasoning about the same dimension
table means you paid for two agents and bought one.

### 16.3 ⛔ The clone is a compromised oracle at exactly the layer our evidence rule exists to protect

This is the most consequential new material in the pass, and it is nearly all `OBSERVED` from
Snowflake's own documentation with independent verification.

**(a) A clone of a share does not misbehave — it does not exist.** Three separate documented
non-supports, all ✓ verified: *"Creating a clone of an imported database or any schemas/tables in the
database"* is unsupported [C-17]; *"Imported databases are read-only… cannot insert or update data,
or create any objects"* [C-19]; Time Travel is unsupported on an imported database [C-18].
**Any lane whose work touches share-consumed data has no isolation story at all — not a degraded one,
none.** The nearest path out is a secure view, which gives namespace isolation with **no temporal
isolation**, because it reads live shared data at query time [C-19b]: two lanes validating against
the same inbound share on different days compare against different data and disagree for reasons
neither can see. R17 explicitly refuses to infer that CTAS-from-a-share is an isolation mechanism.

**(b) Where cloning does work, it is a different privilege path and a different temporal path than
the consumer reads through.**

- Clones do **not** inherit explicit grants without `COPY GRANTS`, and `COPY GRANTS` copies every
  privilege **except OWNERSHIP** [C-11, C-12 ✓]. An agent validating in a clone validates through a
  privilege path the consumer does not use.
- **Clone Time Travel starts at clone creation** [C-16 ✓]. So **before/after historical deltas cannot
  be computed inside the clone** — and a before/after delta against production-scale data is this
  estate's *definition* of correctness (`CLAUDE.md`, Evidence-Gated Changes item 3; the R17 brief's
  own §0 item 3). The sandbox removes the instrument the rule requires.
- Streams, internal-stage pipes, external tables and tasks do not come across, and cloned tasks
  arrive suspended [C-6–C-9 ✓]. ⚠ **"Silently" is the operative word: no error is thrown.** A lane
  inside a clone can be reading production and reporting success.

⚠ **One correction in our favour, and R17 caught it inside its own pass.** A lane had reported —
sourced to a third-party blog — that masking and row-access policies do *not* follow a clone. R17
refuted its own lane from the primary source: *"Cloning a schema results in the cloning of all
policies within the schema. A cloned table maps to the same policies as the source table"* [C-13 ✓].
The widely-repeated blog claim is **wrong** for the same-database case, so this is not an unmasking
leak. **What it actually is:** a **foreign** policy reference is *retained* [C-13b ✓], and a cloned
row-access policy can point at an external table that was not cloned [C-15 ✓]. So **the clone is not
hermetic** — it holds a live control-plane dependency on a production object, and a production admin
altering that policy silently changes what every in-flight lane sees, mid-run. Two lanes running the
same validation an hour apart can legitimately disagree with **no diff between them and no error**.
⭐ That is the estate's rule inverted: correctness is a measurement, and the instrument moved.

**(c) ⭐ The consumer layer cannot be branched at all, and this is the finding that bites hardest.**

| Surface | Branchable per agent? | Basis |
|---|---|---|
| Power BI / Fabric | ⚠ barely — a workspace *"can thus be connected to a single branch"*; per-developer isolation needs a **different workspace**, and branch-out needs available capacity | `OBSERVED` [C-68, C-69] |
| Fabric deployment rules → Snowflake | ⛔ **not supported** — Snowflake is absent from the supported data-source list entirely | `OBSERVED` [C-70] |
| Looker | ⚠ branches the **semantic** layer only; PDTs land in one scratch schema | `OBSERVED` [C-65, C-66] |
| Snowflake warehouse | ✅ yes, via clone — except from a share | `OBSERVED` [C-17] |

⭐ **Consequence, and R17 rates it above the clone economics: clone-per-agent raises the ceiling on
*build* concurrency and raises the ceiling on *validation* concurrency not at all**, because the
oracle we actually trust — a human recognising an impossible number on a rendered visual — is serial,
un-branchable and capacity-limited. *"Ten lanes building behind one serial oracle move the queue from
the build step to the oracle step."* **This is the estate's own Consumer-Layer Validation rule
arriving as a concurrency ceiling**, and it converges with §16.9 from a completely different
direction: the binding limit is the human at the end, twice over.

⚠ **And the automatable data-layer instruments are too slow to gate a run.** ACCESS_HISTORY carries
*"up to 180 minutes"* latency and ACCOUNT_USAGE.QUERY_HISTORY 45 minutes; only INFORMATION_SCHEMA is
real-time [C-52, C-53]. So *"prove this agent touched only its own schema"* is answerable — **but
never within the agent's own run.** Any receipt built on ACCOUNT_USAGE is a post-hoc audit, not a
gate. That retires a class of receipt design before anyone builds it.

**(d) The cost premise was attached to the wrong variable.** Our scaling worry (architecture-v0 §7,
§13.8) was that validation compute makes per-agent clones unaffordable. R17: **validation compute
does not scale with lane count when lanes share a warehouse — it scales with total query-seconds**,
and a shared warehouse is billed by **uptime**, not query count [C-41]. *Concurrency is free;
throughput is not.* Cloning itself is a cloud-services metadata operation, charged only above 10% of
daily warehouse usage, so clone creation is effectively free [C-44, C-43]. Two things genuinely do
scale with N and **both are avoidable**: warehouse-per-lane against the **60-second minimum billing
increment** [C-40, C-42 ✓] — agent workloads are bursty, so every query on a cold warehouse bills a
fresh minute, a hard 2× floor — and clone divergence into permanent storage with Fail-safe, fixed by
one word, `TRANSIENT` [C-28]. ⚠ **Every dollar figure R17 gives is `INFERRED` on a `PROXY` credit
price, because Snowflake publishes none** [C-55, C-56]; order of magnitude only, and it says so.

### 16.4 ⛔ "Mandatory" means a grant — §13.2's rule is an instruction, and R17 names the version that is not

§13.2 adopted R8's *"forbid any `CREATE OR REPLACE` on a shared schema unless preceded by an explicit
clone"* and called it **"enforceable in code rather than in a runbook."** R17 §4.3 draws the line
straight through that claim, and it is the load-bearing sentence of the whole answer:

> ⭐ **Every genuinely mandatory control is a *Snowflake* control; every conventional one is a *tool*
> control. If the data sandbox must hold against an agent that ignores its prompt, enforcement has to
> live in the RBAC graph, not in dbt.**

A rule about what SQL an agent may write is **an instruction living in a repo the agent can edit**.
R17 tabulates the whole space by the only question that matters — *can the agent widen it?* — and
`--target`/`generate_schema_name`, `--defer`/`--state`, WAP/blue-green, SQLMesh environments and
naming conventions are all **"yes, trivially"** [C-57, C-58, C-64, C-60]. *"You have been protecting
the data layer with instructions."*

**The mandatory version of the same intent, and it is cheaper than the rule it replaces:** the lane's
role owns no production object, so `CREATE OR REPLACE` is not available to it at all — there is **no
separate DROP privilege**, OWNERSHIP confers it [C-32], and `OR REPLACE` *"is the equivalent of using
DROP TABLE… and then creating a new table with the same name"* [C-21]. Around that:

| Control | What it stops | Widenable by the agent? |
|---|---|---|
| Role holds **no privilege** on the protected schema | all access — *"unless allowed by a grant, access is denied"*, and there is **no super-role bypass** [C-31 ✓] | **No** |
| Role **owns no production object** | DROP, ALTER, and therefore `CREATE OR REPLACE` [C-32] | **No** |
| Sandbox schema created **WITH MANAGED ACCESS** | the escalation where an agent creates an object, thereby **owns** it, and can then *"grant or revoke privileges on the object to other roles"* [C-22, C-31 ✓, C-35 ✓] | **No** |
| `DEFAULT_SECONDARY_ROLES = ()` | silent union of every role granted to the user — ⚠ **the default is `ALL`** [C-37] | No, but nobody gets it by not thinking about it |
| Role owns **no masking or row-access policy object** | a one-object, **account-wide** enforcement change made from inside one lane | **No** |
| Network policy on the agent's user | connections from non-allowed origins | **No** |
| `ALTER SCHEMA … SWAP WITH` as the only publish verb | publishing by any other route — needs OWNERSHIP on **both**, so publish runs as a different role [C-30] | **No** |

⚠ **The escalation vector worth naming on its own: a plain `CREATE SCHEMA` is the vulnerable
default.** Without managed access, an agent that creates an object owns it, and an owner can hand its
artefacts to any role it can name. Nobody has to make a mistake for this to be true.

⚠ **R17 flags its own load-bearing inference and tells us to probe it, which is our gate 4 applied to
its executive answer.** *"No Snowflake doc says in one sentence that `CREATE OR REPLACE` requires
OWNERSHIP."* The recommendation rests on a two-link chain (C-32 + C-21). *"The chain is strong but it
is a chain… settle it with a `WHERE FALSE`-style permission probe in a scratch account before it
becomes a design premise."* **Adopt the envelope and the probe together; the envelope is not evidence
until the probe runs.**

⭐ **Two blast-radius items §13 does not cover at all.**

- **Reader-account compute is billed to the PROVIDER, with no ceiling.** *"The reader account is
  created, owned, and managed by the provider account, which assumes all responsibility for credit
  charges"*, and warehouses there *"can consume an **unlimited number of credits each month**, which
  will be charged to your provider account"* [C-75 ✓]. An agent change that makes a shared object
  more expensive to query — a dropped clustering key, a view that fans out — spends **our** credits
  **in an account nobody is watching**. §13's blast-radius model is bounded by the repo; this is not
  bounded by the *account*.
- **Our only hard credit ceiling is a soft one.** Resource monitors are explicitly *"not intended for
  setting precise limits… the assigned warehouses may take some time to suspend or disable, **even
  when the action is Suspend Immediate**, thereby consuming additional credits"* [C-48 ✓], and
  Snowflake Budgets are *"used for alerting and notification purposes only"* [C-50 ✓]. ⭐ **An
  unsupervised agent that writes a cartesian join on a 4X-Large — 128 credits/hour [C-39] — has no
  hard stop anywhere in the design.** For an autonomous-completion factory that is the exposure to
  answer first, and §5 step 1 does not contain it (§16.8).

**Bonus, and it settles a live mystery:** the documented `CREATE OR REPLACE` share burn has **two
independent mechanisms**. *Grant loss* — a recreated object *"is still considered a new object, even
if the name is the same"* and must be re-`GRANT`ed to the share [C-20], with `COPY GRANTS` excluding
OWNERSHIP [C-11 ✓]. *Eligibility loss* — shares accept only **secure** views, so a
`CREATE OR REPLACE VIEW` that drops the `SECURE` keyword produces an object that **cannot be granted
to the share at all** [C-74 ✓], so even the corrective re-GRANT fails. And **you cannot roll it
back**: *"Because a DDL statement is its own transaction, you cannot roll back a DDL statement"*
[C-24]; recovery is four manual steps inside a Time Travel window that defaults to **1 day** on
Standard edition, where `UNDROP` *errors if the name is taken* [C-26, C-27].

### 16.5 The sandbox move §13.7 adopted needs narrowing — and the highest-value control is already installed

**⛔ A plain container is not the boundary.** SandboxEscapeBench, 18 tasks: Claude Opus 4.5 escaped
**0.49 [0.39, 0.59]** overall and **0.40 [0.26, 0.56]** at difficulty 3, with a later model at 100%
pass@1; the authors' own conclusion is to *"treat 'plain Docker isolation' as insufficient by
default"* [B-13 ✓]. A devcontainer is worse — a mounted `docker.sock` is host root [B-64].

⚠ **Read the scope honestly, because R17 does.** That benchmark tested **Docker/OCI and Kubernetes
only**; gVisor, Kata and Firecracker were out of scope, so **it is not evidence about microVMs**
[B-14 ✓]. So it refutes the Docker reading of §13.7 item 2, not the Firecracker one. Firecracker is
ruled out separately and on our own constraints: it requires `/dev/kvm` and, on EC2, bare metal
[B-5] — a platform-team answer to a four-engineer problem, which §0b rules out regardless of merit.
gVisor is **not officially supported on AKS** [B-51]. What survives on this stack: **Docker sbx**
locally (a microVM with its own kernel, runs on Windows 11) or **Azure Container Apps dynamic
sessions**, which document **Hyper-V isolation**, allocation *"in milliseconds"* from warm pools, and
UK South / West Europe availability [B-47 ✓] — ⚠ **priced first**: each custom container session pool
runs on dedicated **E16** instances billed on the Dedicated plan, and code-interpreter sessions bill
*"in increments of one hour"* [B-48 ✓].

⭐ **But the highest protection-per-unit-of-work in the entire survey is not a container.** It is
turning on settings that already ship in the tool we run every day:

1. `strictAllowlist: true` + `network.tlsTerminate` + `credentials.envVars[].mode: "mask"` with tight
   `injectHosts` — the sandboxed command *"sees a per-session sentinel value instead of the real
   one"* and the proxy substitutes the real value on the way out, so *"the command and anything it
   logs never hold the real credential, but its requests still authenticate"* [B-16, B-17, B-21, all
   ✓]. Masking **fails closed** without TLS termination [B-17 ✓].
2. `allowUnsandboxedCommands: false` **in the same commit**. The documented escape hatch lets Claude
   *"retry the command with the `dangerouslyDisableSandbox` parameter"*, and it has been reported
   firing **with no approval prompt at all** in auto-allow mode, after which a previously blocked SSH
   key was read — **issue open, no maintainer response** [B-23, B-24 ✓ both]. For an unattended run
   this one setting is the difference between a boundary and a suggestion.

⭐ **And this is the answer to our own hard rule, not a compromise with it.** *"Unlike `deny`, masking
authorizes the proxy to send your real credential to the listed hosts, so it is honored only from
settings you or your administrator control… `mask` entries, `network.tlsTerminate`, and
`credentials.allowPlaintextInject` are **all ignored in a repository's `.claude/settings.json`**"*
[B-20 ✓]. **That is per-secret human approval made structural rather than interactive** — a human
writes one entry per secret in a scope the agent cannot write. And R17 supplies the reason to prefer
the structural form: Anthropic publishes its own gate's miss rate — **0.4% FPR and 17% FNR** on real
overeager actions, and *"Claude Code users approve **93%** of permission prompts"* [D-31 ✓]. ⭐
**Manual approval at volume is not a control.** Our rule survives; its *implementation* should move.

⚠ **Two preconditions, and neither is optional.**

- **Claude Code's sandbox does not support native Windows** — *"runs on macOS, Linux, and WSL2… On
  Windows, run Claude Code inside a WSL2 distribution"* [B-15 ✓]. Our operator machine is
  Windows-first. That is the gating fact for step 1 and it is ours to resolve, not R17's.
- ⛔ **Snowflake key-pair credentials cannot be sentinel-substituted, and the tooling gives no signal
  that it failed.** The private key stays client-side and the client presents a signature, so there is
  **no bearer token in the request for a proxy to swap**, and no shipped proxy re-signs Snowflake JWTs
  [B-65, B-66]. R17 lists this in "what I would refuse to build" with the reason stated in this
  repo's own vocabulary: *"it will substitute nothing while everything looks configured"* — the gate
  that reports PASS while measuring nothing. ⚠ R17 tiers this `INFERRED` with a **partial**
  verification (the key-pair page confirms public-key registration but does not contain the sentence
  it needs), and therefore makes it a **probe, not a premise**: test whether a Snowflake **PAT** in
  the driver's login body is actually swapped [B-67]. *"One hour of work; it decides the whole
  credential architecture."*

**And the judgement we asked for, which amends how our rule is worded.** Short-lived scoped tokens
minted **by the agent** (Vault, SPIFFE, OIDC) are out under the rule as written — cutting a lifetime
from 90 days to an hour reduces blast radius but *"does not insert a human"* [B-69]. But the same
token minted by a **launcher outside the sandbox** and handed in as a sentinel is **strictly better
than a static masked secret**: it rotates *and* the agent never sees it. ⭐ **The line worth writing
into the rule is not lifetime, it is who holds the minting authority.** Rejecting short-lived tokens
outright is the wrong lesson; rejecting **agent-held minting authority** is the right one. Same
reasoning retires "managed identity → Key Vault from inside the agent": the Key Vault read belongs to
the launcher, outside the blast radius.

### 16.6 What R17 corroborates — and one framing it corrects

**Independent arrivals at positions already in this document.** Agreement is the control:

- **§6's `agent ↔ agent` deferral is upgraded from "not yet" to "by design".** Four systems refuse it
  independently: Anthropic's production research system does not have it and says so as a live
  limitation [A-2 ✓]; Claude Code subagents cannot communicate during parallel execution [A-47];
  **Google's A2A protocol — the agent-to-agent protocol — deliberately requires collaboration
  "without needing access to each other's internal state, memory, or tools"** and routes a stuck agent
  to `INPUT_REQUIRED`/`AUTH_REQUIRED` [A-45]; and **MCP deprecated `sampling` as of protocol
  `2026-07-28`**, leaving `elicitation` — *"allows servers to request additional information from
  users"* — as the surviving primitive [A-46 ✓]. *The organisations building agent interop protocols
  route unanswerable questions to humans.* §6's unlock criterion (≥5pp net gain) is no longer the
  operative bar; the bar is that nobody who built it kept it. **Build instead a typed
  `BLOCKED(reason, question)` record with a terminal state** — which is `sessions.blocked()` and the
  `needs` field (§12.8 item 3). An outside pass specifying what we already built is the strongest
  corroboration available.
- **§6's never-optimise list and §11.4's rejection of gates-as-fitness.** R17 refuses a self-improving
  prompt loop against real credentials in its strongest terms — *"a reward-hacking engine pointed at
  your own gate"* — with ADAS overfitting benchmarks two ways and no production deployment found
  anywhere [D-52, D-53]. Third independent arrival at §6's rule.
- **§3.3's evaluator trust boundary now has numbers.** *"Hiding tests from agents reduces cheating
  success rate to near zero"* [D-25 ✓], against **415 of 429 Terminal-Bench 2 pilot traces (96.7%)
  accessing forbidden directories**, including *"writing code printing 'PASS' to fool checkers"*
  [D-27]. ⭐ **A gate the agent can edit is not a gate** — which is §3.3's ranking restated from the
  measurement side, and an argument for §8 row 11 (CI on push) that R6 was never able to make: a
  check that runs on infrastructure the agent does not control is categorically different from a
  local hook, provided the workflow file itself is protected.
- **§5 step 8 and §3.2's calibration arithmetic.** R17 adds that **the oracle itself rots**: OpenAI
  retired SWE-bench Verified after **59.4% of 138 audited problems** showed material issues in test
  design or problem descriptions, plus evidence of training contamination [D-29 — ⚠ `REPORTED`
  *secondary*, because openai.com returned 403; cite it as such]. ⭐ **That lands on §1.** Our
  headline mechanism was argued from SWE-bench-strengthening work; the oracle those numbers came from
  has since been retired for the same defect class. It **strengthens** §1 — and it means our own
  corpus should be assumed to have the same problem until audited. *"If it can happen to SWE-bench,
  assume it about your own oracle."*
- **`factory/metrics.py` and the gate-honesty doctrine.** R17's §5 rules are ours almost verbatim: a
  gate must be **provably capable of failing** (mutation testing as the canonical gate-on-the-gate —
  a test that calls a function and asserts nothing yields 100% line coverage and a **0% mutation
  score**, *"the exact mechanical analogue of 313 → 1"*), and a zero must be **demonstrated, not
  assumed**, by injecting a known-bad. ⚠ One addition we do not have: the validation-to-held-out gap
  grows ~**27 pp per 10× LOC** and reaches 100 pp above 25K LOC [D-26] — **a green gate on a large
  change means far less than on a small one, and the receipt looks identical.**

⚠ **The framing it corrects, and it is one this estate uses.** *"The critic must be a different
model"* is **not supported for defect-finding**: CriticGPT *"was initialised from the same
checkpoint"* as the model it critiqued and still had its critiques preferred over human contractor
critiques **63%** of the time, finding substantive problems in **24%** of samples previously rated
flawless [A-13, A-14, A-16 ✓ all four]. What the evidence actually separates is **finding defects**
from **scoring or ranking**: for scoring, family matters and matters a lot — self-preference bias
correlates linearly with self-recognition [A-18], and multi-judge panels *"amplify some biases while
resisting others"* rather than cancelling them [D-57]. **So: a different family wherever a stage
scores or ranks; a fresh context and sight of the artefact wherever it hunts defects.** And the
Huang-versus-Self-Refine contradiction resolves cleanly — a critic helps when it **sees something the
generator did not use** (a rubric, a test result, the artefact) and fails when it is "think again" on
the same reasoning [A-10, A-11, A-12]. A reviewer sub-agent reading the diff in a fresh context is
not intrinsic self-correction.

### 16.7 ⭐ The gate at the end is nearly worthless — and it prices §12.5's guardrail gap

The single most design-changing measurement in the pass, ✓ verified:

| Where the gate sits | What it catches |
|---|---|
| First artefact boundary (S₁→S₂) | **75.4%** |
| Last artefact boundary (S₃→S₄) | **10.7%** |
| End-of-pipeline verification, versus **no verification at all** | **+2.3 pp** |

Detection falls **72.0% → 50.9%** from stage 1 to stage 4 because *upstream transformations destroy
the information needed to check the claim* [A-50, A-51 ✓]. **"Add a reviewer at the end" is the cheap
version that mostly does not work.**

**Our readiness gates evaluate finished output.** §12.5 already filed guardrails as a category we do
not have — a pre-action layer distinct from a post-hoc gate, with the CANCELLING-before-ownership-
check defect as its worked example. R17 turns that from a taxonomy observation into a priority: the
gap is not a missing nicety, it is **where roughly seven-eighths of the detection lives**.

⭐ **And §16.1 is this repo's own live instance of the mechanism.** "A shared branch was measured at
41.7%" was a raw, checkable claim when R5 wrote it and an unexamined premise by the time an
outward-facing brief consumed it — six restatements downstream, where the information needed to check
it had been transformed away. R17 diagnoses the class precisely (attribution ≠ support, §16.1) and
names the detector, which is free:

1. ⭐ **Symbol-existence checks — no LLM call, precision ≈ 1.** Every claim naming a repo object must
   carry the literal identifier, and a mechanical check asserts the identifier exists and the claimed
   property holds. *"Highest-value item in this section"*, and it would have caught F1 (verification
   took one `grep`) and §16.1 (likewise).
2. **Gate at the artefact boundary, not at the end.** Non-negotiable at 75.4% versus 10.7%.
3. **Check attribution separately from support** [A-55] — the check §16.1 needed and nobody ran.
4. **Never let a downstream pass inherit an upstream conclusion as a premise.** Carry the tier with
   the claim; make anything below OBSERVED non-promotable. ⭐ R17 says our own claims-table rule is
   the right control and should be **a hard gate rather than an instruction** — which is directly
   buildable against `docs/research/*.md`: a figure appearing in a brief's §0b must carry a source,
   checked before dispatch.
5. **Do not share a vector store between lanes** [A-57] — one poisoned entry reaches every agent, and
   derived entries camouflage it against single-event monitoring.

⚠ Provenance-style NLI checking costs ~0.036 s/claim [A-56] — negligible — but runs **precision 0.673
at recall 0.993**, so one flag in three is a false alarm. Run it advisory; keep the mechanical symbol
check as the blocking gate.

### 16.8 Amendments to §5's build order, and to what "unattended" means

**§5's step order is unchanged.** R17 reorders nothing. It sharpens step 1 and adds a step 1 twin the
list never had.

⭐ **Step 1, sharpened — budgets have two kinds and only one is a control.** Anthropic ships both and
documents the difference: Managed Agents' `budget.max_list_cost` is a platform-**enforced** dollar cap
that idles the session preserving history and sandbox; the Messages API `task_budget` is *"advisory,
not enforced… a **soft hint, not a hard cap**"*, and one set too small may make Claude *"decline to
attempt the task at all, scope it down aggressively, or stop early"* [D-44 ✓]. **Do not delegate the
budget to the agent**: in BAGEN, *"all twenty model–environment pairs underestimate remaining budget
more often than they overestimate it"*, and capability correlates with budget-awareness at only
r≈0.35 [D-43]. Two traps R17 names and we would have hit: **denominate in dollars, not tokens** —
Claude 4.7+ tokenise ~30% higher for the same text, so a token budget silently shrinks 30% across a
model upgrade and starts triggering the documented refusal-like behaviour [D-49, D-45 ✓]; and **size
caps on p99, not the mean**, given up to **30× variance across runs of the same task** [D-48].

⭐ **Step 1's missing twin: there is no hard ceiling at the data layer at all** (§16.4). §5 step 1
says "hard external attempt / spend / concurrency budget" and every mechanism behind it is
process-side. Resource monitors overshoot by design and Budgets cannot block. **Add the data-layer
ceiling as an explicit prerequisite, and record that the best available version of it is soft.**

⭐ **An abort verb the agent is allowed to use — and nothing in our design offers one.**
ImpossibleBench's most effective mitigation by a distance: allowing models to abort cut cheating from
**54% → 9%** (GPT-5) and **49% → 12%** (o3), *"though for Claude Opus 4.1 the effect is much less
pronounced"* [D-25 ✓ — body, not abstract; R17 corrected its own lane's citation here]. **An agent
with no exit will fabricate one**, and the exit must be *rewarded* by the harness rather than merely
offered. The lane contract, the readiness set and `finish.py` have no such verb. New work, cheap.

**What "unattended" can mean — §13.3 corroborated and sharpened.** R8 gave us ~45 minutes at the
99.9th percentile, `REPORTED`. R17 arrives independently and fixes which number to quote:

- METR *explicitly states* that its time horizon **is not the length of time AIs can work
  independently**, and that measurements above 16 hours are unreliable on its own suite [D-1–D-3].
  Quoting a 12-hour horizon as an autonomy figure is the wrong-instrument error.
- **The reliability figure that matters is the 80% horizon, and for Opus 4.5 that is 27 minutes**
  (against a 50% horizon of ~4 h 49 m) [D-4].
- The one measured long-horizon suite: runs average **88.9 minutes**, the best model reaches **28.3%**
  at R≥0.95, and the **mean pass rate across models is 6.4%**; 62.8% of runs earn partial reward that
  *"would all be counted as failures under binary pass/fail evaluation"* [D-10 ✓].
- Independent one-month Devin trial: **3 of 20** tasks succeeded [D-17 ✓].

⭐ **So our 3 of 14 (21%) is normal-to-good, not a defect** — and R17 draws the conclusion §13.3
stopped short of: *"The correction is not 'get to 14/14'. It is to make the 11 failures cheap, early
and legible"*, because **the harness alone moves the score 52.4% → 76.2% on identical tasks with
identical models** [D-34]. That is the strongest external statement of this programme's premise that
anyone has produced: **the factory is worth more than the model choice.**

⚠ **With F4 attached, because it is still true.** Our 3-of-14 describes runs that stopped
2026-05-28. Comparing a three-month-old figure against the current field compares two different
times, and the gates still do not carry the age of their evidence.

### 16.9 The a14 question — a fourth reading, and the first concrete alternative

§15.5 established that a14's *"three independent sources"* were one measurement read three times, and
§15.6 concluded we do not know what the real first move is. **R17 is a genuinely separate reading and
it points where the outside-evidence lane pointed, not where a14 does.**

> **22,000 developers, ~4,000 teams, two years:** task throughput **+33.7%**, median PR review time
> **+441.5%**, time-to-first-review **+156.6%**, incidents-to-PR ratio **+242.7%**, code churn
> **+861%**, and **PRs merged with no review +31.3%** [E-17 ✓].

R17 puts that in its **executive answer** — *"do not raise lane concurrency"* — with the mechanism
spelled out: **raising concurrency before the evidence gate is sublinear reduces safety, not just
speed, because a saturated gate does not present as a queue, it presents as a bypass.** That is
§15.5 item 6 ("the estate's binding limit was not 3 lanes, it was 1 reviewer") arriving with a
denominator, from a pass that could not see the R16 lane's answer.

⚠ **Both passes also found the same paper and agree on its weakness.** *Oversight Has a Capacity*
(arXiv:2606.08919) is E-29 here and §15.5 item 2 there — and R17 adds the caveat in the authors' own
words: **the fatigue curve is assumed, not fitted to people.** Two independent lanes reaching one
`REPORTED (simulated)` source is corroboration of the *finding*, not promotion of its tier.

⭐ **And §15.6's missing action now has a candidate with numbers.** §15.6 said the useful first move
is something that *raises review capacity or lowers what needs reviewing*, and that nobody had
written it down. R17's §2.2 and §6.1 write it down:

- **A required adversarial reviewer at every artefact boundary** (not at the end — §16.7), fresh
  context, sight of the artefact and of that stage's input; **blocking** on mechanically checkable
  claims (does this identifier exist, do these row counts reconcile), **advisory** on judgement
  claims until a precision number exists; terminus a human, *"the empirically better configuration,
  not a concession"* [A-15 ✓].
- **The cost, which is the surprising part: ~15–25% marginal. Three reviewers cost ~20% of five
  workers.** And judging **full trajectories costs more than generating them** — never do it.
  Best-of-N is **~3.7× more expensive per correct answer even assuming a selector that never errs**,
  so **adversarial review dominates best-of-N by roughly an order of magnitude in
  cost-effectiveness** [§6.1, D-40]. ⚠ All `INFERRED`, from LHTB-derived token rates and labelled
  assumptions.

⚠ **And the denominator nobody has.** *"Published false-positive rates for LLM code review at
production scale are effectively ABSENT"* — R17 searched and says this is *"the number R18 should
generate internally, because the field will not supply it."* Which forces a correction to a claim
made in our own brief: **"6 defects plus 4 defects in one day" is a recall observation with no
denominator and no false-positive count.** CriticGPT's own finding is that model critics nitpick and
hallucinate at rates *"much higher"* than humans [A-15 ✓]. The nearest quantified analogue is a
provenance checker at recall 0.993 running **precision 0.673**. **Our reviewer evidence is one number
out of the two that matter.**

### 16.10 The ledger split has a name, and it was neither of the two we guessed

Asked in session — three worktrees each appended the next sequential id to one shared ledger and
collided three ways; is the record/channel split "event sourcing" or "CQRS"? **Neither.**

- ⭐ **The collision fix is the SINGLE WRITER PRINCIPLE** (Thompson / LMAX): *"for any item of data,
  or resource, that item of data should be owned by a single execution context for all mutations"*
  [A-33 ✓ definition]. "One append-only file per writer" **is** that principle; three worktrees
  appending to one ledger **is** its violation.
- ⭐ **The sharper diagnosis, which generalises: the id was never a CRDT operation.** Operation-based
  CRDTs require concurrent operations to **commute** [A-36]. *"Allocate the next sequential integer"*
  does not — it is a consensus primitive. `(writer_id, local_seq)` commutes; per-writer append-only
  logs unioned form a **grow-only set**, and per-writer counters are a **version vector**. One
  sentence for the postmortem: ***a monotonic global counter is a consensus primitive that was being
  used as if it were a CRDT.*** **Consequence: every shared mutable field in that ledger needs the
  same audit** — the fix is not one field.
- ⭐ **The record-vs-channel split is EDGE-TRIGGERED NOTIFICATION, LEVEL-TRIGGERED LOGIC** — the
  Kubernetes controller discipline [A-32]. An event is *a hint that it is worth looking again*, never
  the truth; the reconciler derives desired state from the current world and is idempotent, so it is
  immune to dropped, duplicated and out-of-order notifications. **This is what makes an ephemeral
  nudge channel safe to lose messages, and it dissolves the whole question of whether the channel
  needs ordering or delivery guarantees.** Adopt the sentence: *the nudge may say what changed; the
  reader must go read the log.*
- **Rejected, with reasons:** *event sourcing* describes the record correctly and nothing else — and
  ⚠ **a single shared event log would have collided identically**, so it does not contain the fix.
  *CQRS* is a near-miss on the **wrong axis** (command vs query model, not writer vs writer) and
  Fowler himself says *"you should be very cautious about using CQRS"* [A-35] — it sends you to the
  wrong literature and a pattern its author warns against. *Log-structured merge* is a storage
  technique; discard.

⚠ **A worked example of why the verification ledger matters, kept because we would have quoted the
wrong number.** The lane reported LMAX as *"300 ms one thread vs 118,000 ms two contending threads —
393×"*. R17 fetched the post: the definition is verbatim correct, but the table gives **one thread
with lock 10,000 ms against two threads with lock 118,000 ms — an 11.8× contention cost**; the 300 ms
row is the *lock-free single thread*, so the 393× conflated lock overhead with contention overhead.
**Substance confirmed, number wrong by 33×.** Nothing in the recommendation changes; the figure we
would have published does.

### 16.11 What R17 could not settle — its own declared gaps

R17 separates absence into the same verdicts our contract does, which is why the list is usable.

**ABSENT — searched, genuinely not published:**
- ⭐ **False-positive rates for LLM code review at production scale, with denominators.** *"The single
  biggest evidence gap in this pass"*, and it sits directly under the recommendation in §16.9. The
  most-cited write-up on the subject was fetched and contains no before/after measurement of its own.
- Any production LLM-agent system using auction / contract-net bidding.
- **Any shipped mechanism for injecting context into a *running* agent** — Anthropic states plainly
  that the lead agent cannot steer a live subagent [A-2 ✓], and no framework surveyed offers it. A
  genuine gap in the field, and it bounds what any supervision surface can do.
- **Any system that forks filesystem + process + *database* as one world.** Every fork primitive stops
  at the microVM's edge; a forked sandbox holding a live warehouse session resumes with a connection
  the server has forgotten, and the warehouse state was never in the snapshot.
- Generic re-signing at a credential proxy — **nobody re-signs Snowflake JWTs** (§16.5).
- A receipt format that records whether the sandbox was **disabled mid-run**, or reasons about
  exfiltration **through** an allowed host.
- A per-secret, per-request human-approval callback for an Azure service principal (PIM gates *human*
  role activation only).
- A team that made adversarial review mandatory and then removed it.
- ⭐ **Any published account of a ~4-engineer team operating a bespoke agent factory.** We are not
  behind a field that has done this; there is no published instance of it.

**UNSEARCHABLE — nobody discloses it. These are findings, not gaps:**
- ⭐ **Production intervention / human-takeover rates. Not one vendor publishes them.** The single
  metric that matters most to the autonomy decision is the one the industry declines to disclose.
  Treat every vendor autonomy claim as a capability demo until a denominator appears.
- Real unattended-run durations in production — every vendor number is `MARKETED`, every practitioner
  number an anecdote.
- The internal eval behind Anthropic's 90.2% [A-4 ✓ `MARKETED`].

**NOT-SUPPLIED:** Snowflake's per-credit and per-TB dollar rates — the pricing page routes to CONTACT
SALES, so **every dollar figure in §16.3–§16.4 is `PROXY` from a third party**. Also unobtained:
Docker sbx's cold start and hypervisor, Modal's isolation technology, Northflank's egress model.

**NOT-VERIFIED — R17 actively recommends against citing these, and two are in circulation:**
"Firecracker snapshot restore in 4 ms" (the paper it is attributed to gives no such figure) ·
"gVisor needs 158 additional host syscalls with networking" (**its own post says 15**) · "the
35-minute agent reliability cliff" (blog-only) · **the "$47,000 agent loop"** (a second-hand blog
chain with no named company and no verifiable artefacts — R17 checked the provenance and reports the
failure *mode* as documented while refusing the *number*) · Smith's 1980 Contract Net paper and the
Dias market survey (PDFs unreadable; cited at secondary granularity only).

**Its two self-flagged partials, both of which become experiments rather than beliefs:** the Snowflake
key-pair/masking chain [B-65, B-66] and the `CREATE OR REPLACE`-requires-OWNERSHIP two-link chain
(§16.4). Both carry a named probe.

⚠ **And the caveat that governs how to read all of the above: survivorship bias, where absence is NOT
evidence.** Failure reports for per-developer data environments, abandoned agent factories and removed
review gates are systematically under-published — *"teams publish the migration, not the rollback."*
⭐ **This is why §16.3's verdict rests on vendor documentation of hard limitations rather than on
postmortems: documentation cannot be survivorship-filtered.** That is a methodological point worth
keeping beyond this pass.

✅ **One thing it was told not to answer, and did not.** §14.6 concluded that the embedded-terminal
question should be settled as a decision and deleted from every brief, because four passes had
answered it by deference, fabrication or restatement. R17's brief did exactly that — *"one question is
deliberately left open and must stay open"* — and R17 reports: *"No lane was permitted to touch it,
and none did."* **The fix worked. Nothing more should be spent on it.**

### 16.12 Basis labels — how R17's tiers map onto ours

The house rule is `OBSERVED in a comparable setting` versus `EXTRAPOLATED from human teams`. R17 uses
`OBSERVED / REPORTED / MARKETED / INFERRED` plus a separate ✓verified column, and the mapping needs
one caution stated plainly:

⚠ **Most of R17's `OBSERVED` means "I read the vendor's documentation sentence", not "I watched this
happen in a comparable agent setting."** For *rules* that is the strongest evidence obtainable — a
documented grant semantic or a documented "not supported" defines what the system can do, and no
amount of field experience overrides it. For *behaviour* it says nothing at all. Keep the two apart.

| Recommendation | R17's tier | Read it as |
|---|---|---|
| Build the Snowflake grant envelope first (§16.4) | `OBSERVED` ✓ docs | **RULE-OBSERVED** — strongest class here. ⚠ its one inference (`OR REPLACE` ⇒ OWNERSHIP) is a chain; probe before building |
| Do not raise lane concurrency (§16.2, §16.9) | theorem [A-24 ✓] + `REPORTED` [E-17 ✓] | Half mathematics, half the **largest-N human-teams-using-AI study in the programme** — the closest thing to OBSERVED-in-a-comparable-setting anyone has cited |
| Turn on `mask` / `strictAllowlist` / no unsandboxed retry (§16.5) | `OBSERVED` ✓ — docs of the tool we run | **RULE-OBSERVED**. ⚠ WSL2 precondition is ours |
| A plain container is not a boundary (§16.5) | `REPORTED` ✓ benchmark | **OBSERVED-in-a-comparable-setting** — the model class we actually run, escaping. Scope: Docker/K8s only |
| Reviewer at every artefact boundary (§16.7, §16.9) | `REPORTED` ✓ | Papers and benchmarks. **No production denominator exists** — the FP rate is `ABSENT` |
| Dollar-denominated, harness-held budgets (§16.8) | `OBSERVED` ✓ + `REPORTED` | RULE-OBSERVED for the mechanism; REPORTED for why agents cannot hold it |
| 3-of-14 is normal; target the 80% horizon (§16.8) | `REPORTED` ✓ | Benchmarks plus one independent trial. **No production denominator anywhere** — `UNSEARCHABLE` |
| Single-writer / edge-triggered (§16.10) | `OBSERVED` ✓ primary texts | **Definitions, not measurements** — correct by construction, and R17 still had to correct its lane's numbers |
| Anthropic's 90.2%; "30+ hours of focus" | `MARKETED` | **May not be a design premise**, per our own brief's rule |

**Nothing in R17 is `EXTRAPOLATED from human teams` in the R5/R6 sense** — that is the shape of
evidence this pass replaced. The one place it comes closest, E-17, is human teams *using AI*, which is
why it carries more weight here than any topology paper.

### 16.13 What changes in this repo — additions to §8

| # | Change | State |
|---:|---|---|
| 16 | **Correct the 41.7% wherever it is stated as ours** — `scripts/local_tracker.py:124` and `:385`, `factory/worktrees.py:3-4`, `R13-evidence-pack.md:288` (tiered `MEASURED`), `R10-…md:137` (unsourced row among our own figures). ⛔ Not done here — this pass may write only `SYNTHESIS.md`. File as **F11** in `docs/findings.md`. **The conclusion is unchanged; only the basis is.** | not started, and it is a correction rather than a build |
| 17 | **Build the Snowflake grant envelope** (§16.4) — one role per lane, managed-access schema, owns nothing in production and **no policy object anywhere**, `DEFAULT_SECONDARY_ROLES = ()`, network policy, resource monitor on every reader account | not started — **R17's executive answer**, and the only control an agent cannot ignore by ignoring its prompt |
| 18 | **Run the `WHERE FALSE` OWNERSHIP probe** before 17 is treated as evidence (§16.4) | not started — prerequisite of 17, one scratch account |
| 19 | **Downgrade §13.2's mandatory-clone rule to what it is** — an instruction until it is a grant (§16.4) | ⚠ recorded above; the roadmap row that cites it needs the same correction |
| 20 | **Turn on `strictAllowlist` + `tlsTerminate` + `mask` + `allowUnsandboxedCommands: false`** from user/managed settings (§16.5) | not started — **highest protection-per-unit-of-work in the survey**. Precondition: WSL2, since native Windows is unsupported |
| 21 | **Probe the Snowflake credential shape** — does masking reach a PAT in the driver's login body? (§16.5) | not started — one hour, decides the credential architecture |
| 22 | **Mark share-touching and policy-touching work as NOT clone-sandboxable** and route it through a separate human-gated path (§16.3) | not started — a carve-out, not a build |
| 23 | **Move the reviewer gate to the artefact boundary**, and add the pre-action guardrail layer §12.5 filed (§16.7) | not started — 75.4% vs 10.7% |
| 24 | **Give the agent an abort verb the harness rewards** (§16.8) | not started — cheap, and nothing offers one today |
| 25 | **Denominate every budget in dollars, hold it in the harness, size on p99** — and add the missing **data-layer** ceiling to §5 step 1 (§16.8, §16.4) | not started |
| 26 | **Make the claims-table rule a gate on our own briefs** (§16.7 detector 4): a figure in a prompt's §0b must carry a source, and the mechanical symbol check runs before dispatch | not started — **this is the control that would have caught row 16 before it reached an outward-facing pass** |
| 27 | **Model the name graph and the compute graph**, since cloning replaces the cap rather than lifting it (§16.2) | not started — the prerequisite for any concurrency claim above 3 |

### 16.14 Additions to §9 — follow-ups

8. **R18 inherits three things R17 handed it explicitly, and one is already answered.** (a) The 41.7%
   provenance — ⛔ **do not re-ask this; §16.1 settles it.** Tell R18 the answer and let it audit the
   *drift*, which is the part with lessons in it. (b) **The internal false-positive rate for our own
   reviewer sub-agents** — the number the field will not supply, and the one that decides whether the
   §16.9 reviewer is blocking or advisory. (c) Whether the isolation ladder is right for us, which was
   always R18's.
9. ⚠ **There is no R17 thread to follow up in, and §9's premise does not hold for in-repo passes.**
   §9 exists because a follow-up in an existing thread is *"cheaper than re-running, and carries the
   context"*. R17 ran as local subagents; there is no conversation to return to. **The follow-up
   mechanism for an in-repo pass is a new brief**, and the two things R17 left open are **probes, not
   questions** (§16.13 rows 18 and 21) — they are answered by running something, not by asking
   anything. Worth noting before someone writes "ask R17" on a roadmap.


---

*How this reconciliation ran, both halves.* **Reconciled locally by an agent with repo access** — so
it is **stronger on file-and-line claims** (it read R17 and its brief in full, ran the `grep` and the
`docs/evidence/` check that settle §16.1, and verified the drift sites and their tiers by opening
each file), and **less independent than a reader coming to the answers cold** (it read this document's
existing conclusions before writing, from inside the estate whose record it is grading, and inherits
whatever this document already got wrong). §16.1 is the one place that independence would have
mattered most, and it was resolved by a mechanical check rather than by judgement — which is the only
reason to trust it from this position.

---

## 17. The reconciliation — what this document says about the answers, versus what the answers say (added 2026-08-23)

This pass was handed a premise: *"SYNTHESIS.md mentions every filed answer. Nothing to reconcile —
but note that this only checks mentions, not engagement."*

⭐ **That premise was not a guess. It was a green instrument.** `F75`, filed by a concurrent
session at 18:04 the same day, records the reading that produced it: `unsynthesised()` → `[]`,
`unreconciled()` → `['R18']`, `test_synthesis_current` **green**. The brief this pass was handed is
therefore the output of two checks and a passing suite — which is the strongest possible reason to
walk the route rather than inherit it.

**Half of that premise is right and it is the wrong half.** The mention check passes: every one of the
seventeen filed ids appears in this document, R1 twelve times through R17 eighty-six. But
"nothing to reconcile" is false, and not only because mentions are shallow. **This document makes
factual claims about the state of the research programme that are wrong** — it says seven times that
an answer has not landed when it had, once that an answer is unread in a section whose next page says
it was read, and once that nobody has written down an action that two answers had already written
down. A reader cannot repair those by reading more carefully. They are false statements, not thin
ones.

✅ **And two passes converged on this from opposite ends, minutes apart, without seeing each other.**
F75 started from the instrument — *"they measure **mention** and **modification time**, and the gap
between those and absorption is roughly 3× wider than either can see"* — and named R13 run 2, R14
and R18 as the unabsorbed three. §17 started from the answers and arrived at the same three, plus four
more false-status sentences F75's `grep` did not reach. **Agreement between independent passes is the
control** — and on the remedy F75 is the stronger of the two: §17.10 and row 28 below are *corrected*
by it, not corroborated by it.

⚠ **Grade the instrument first.** This pass read all twenty answer documents in full — ~11,600
lines — with repo access, then re-read this document and checked every status claim against the
filesystem. It is **strong on the mechanical claims** (a file exists or it does not; a string appears
in this file or it does not; every count below is a `grep` anyone can re-run) and **weakest exactly
where §16's closing note says: it read this document's conclusions before writing.** Where it says a
finding is "unabsorbed" that is mechanical. Where it says a finding *matters*, that is judgement, and
it is the same judgement this document already holds.

### 17.1 Seven sentences say an answer has not landed. All seven are false.

`OBSERVED` — each cell is a `grep` against this file and an `ls -la` against `answers/`.

| Where | What it says | What was true when it was written |
|---|---|---|
| §12 intro | *"R8 is still outstanding"* | R8 filed **07:35**. §12 was written after. |
| §12.5 | *"Read them together when R8 lands"* | Already landed. **They were never read together** — §13 takes R8's isolation half; task packaging is joined to nothing. |
| §13 intro | *"R13 and R14 are still out"* | R13 run 1 filed **08:35**, R14 filed **13:38**. §13 cites R13 run 2 (**13:34**) in its own §13.6. |
| §13.8 | *"That is R14's job and R14 has not run"* | R14 had run, and answered exactly that question. |
| §14 intro | *"Only R14 remains unsent"* | Filed four minutes before the answer this section is built on. |
| §15.3 | *"The outside-evidence lane's answer has not been read yet"* | §15.5, four paragraphs later, opens *"Read 2026-08-23."* Both sentences still stood. |
| §15.6 | *"nobody has written it down yet"* | Written down twice — §17.7. |

⚠ **F75 counted two of these; this pass found seven.** Not a disagreement — F75 `grep`ped `R14` and
reported what that returned. The other five name R8, R13 and the R16 outside lane. **The class is
larger than the instance that exposed it**, which is the usual shape here.

⭐ **The tell is that not one of them was ever wrong at the moment of writing about a file the author
had not opened.** Every one was falsified by a file already on disk, most of them by a file the same
section cites. §13's intro says R13 is still out and §13.6 quotes R13 run 2's commit hash. That is
not a stale number of the §15.1 kind — a figure nobody could make move — it is a **status field
nobody re-read before appending under it.** `factory/dispatch.py` already models exactly this as
`STALE_STATUS`, one of its five states, and nothing points it at this file.

### 17.2 ⭐ R14 — 1,389 lines, seven mentions, and not one conclusion taken

This is the worked example, and it is the failure the reconciliation exists to end.

`R14-answer-structure-model-and-joy.md` is **86 KB, 1,389 lines — the largest answer in the corpus**,
filed 2026-08-23 13:38. It is named seven times in this document. Here is every mention:

| Where | The mention | Kind |
|---|---|---|
| §13 intro | "R13 and R14 are still out" | **false status** |
| §14 intro | "Only R14 remains unsent" | **false status** |
| §13.8 | "That is R14's job and R14 has not run" | **false status** |
| §13.7 | "Then apply R14's design to a fast surface" | forward reference to work never described |
| §15.1 | `R14-answer-… §5` listed as a place the wrong `0 of 15` was load-bearing | **a correction to R14** |
| §15.3 | "a8's payoff is refuted by R14" — a bare pointer to R16 §2.8 | pointer, no content |
| §16 | "exactly as R13 run 2 and R14 were weighed" | a grading comparison |

⛔ **Three say it has not landed, one corrects a number inside it, three point at it. None takes a
conclusion from it.** The only engagement this document has ever had with its largest answer is to
tell it that one of its figures was wrong.

**What is in it, and in no section here.** All `OBSERVED` in R14 with `path:line`:

- ⭐ **A live safety defect that fires every time.** `local_tracker.py`'s "run preflight & finish"
  button **releases the claim unconditionally, on the line before `fails` is examined, and never
  calls `factory.finish`** — so no push, no bus announce, no `runs.record()`. `finish.py:12-14`
  exists to prevent precisely this: *"releasing its claim would advertise a lie to the next
  session."* R14 rates it above the threading race *"because the threading race needs concurrency
  and this one fires every time."* **R16 §2.9 independently re-verified it is still on disk.** It
  appears in no §8 row, no §13.7 item and no §16.13 row, and the string `factory.finish` did not
  appear anywhere in this document before §17. ⭐ **It also explains a number this document quotes as
  evidence**: the run ledger is empty not because nothing ran but because *the only button that would
  fill it does not call the thing that fills it.*
- **A live concurrency defect.** `claims.claim()` is check-then-write with nothing between; the
  accidental serialisation that made it atomic was the single-threaded server, and threading removed
  it. Every launch route is a `GET`, so a double-click or a browser prefetch is enough. That is F73 —
  two agents, one worktree — reopened at the HTTP layer, through the button written to prevent it.
- **`Snapshot`** — R14's largest structural recommendation, one object that is simultaneously the
  latency fix, the freshness type, and the reason four of six tabs run all thirty probes and discard
  the result. The word appeared twice in this document before §17 and both times it meant a
  Firecracker snapshot.
- ⭐ **`lane` is one string doing six jobs** — work package, conflict key, branch, directory, claim
  key, ledger key — *"therefore two agents cannot work one lane, because the lane **is** the
  branch."* **This is the mechanism behind the concurrency ceiling that §14.1 and §16.2 argue about
  across two full sections without naming.** R16 §2.7 says so; R18 §1.2(1) finds it already written
  in `claims.py:53-57` as a comment and calls it *"the correct diagnosis, already in the code."*
- **`Workstream` / `Attempt`**, the split that makes cost-per-outcome a division that can actually be
  performed — R16 §3.2 calls it the unwritten prerequisite for a8's stated payoff.
- **`Decision`** — the observation that the one plane where a human is mandatory has no type, no
  store, no ledger and no age, and that *"the absent object and the measured bottleneck are the same
  thing."*
- **§6.4's answer to the `UNMEASURABLE` colour problem** that §13.8 says nobody has answered.
- **§6.8's argument that the no-cache rule is currently producing *staler* information than a
  labelled cache would**, because a 19-second page is a page you refresh less often. That is a direct
  attack on a rule this estate holds hard, made in the estate's own terms, and it is answered
  nowhere.

### 17.3 R18 exists, and every reference to it here is in the future tense

`R18-answer-our-factory-internal-audit.md`, 614 lines, filed **18:01** on 2026-08-23 — the most
recent answer, and **untracked in git as this is written**. All seven mentions are forward references
written by §16 before it landed: *"R18 audits us from inside the repo"*, *"the number R18 should
generate"*, *"R18 inherits three things"*. No section absorbs it.

That is defensible for a few hours. It is recorded here so it does not become §17.2 in a week. Its
executive answer is one sentence, and it changes what §8 should say first:

> **Three of the thirty readiness probes have no reachable `PASS` path** — two of them in
> `launch.py`'s `UNATTENDED_GATES` and one in its `TRUST_GATES` — so `UNATTENDED-OK` and
> `OUTPUT-CERTIFIABLE` are **unreachable states of the program**, and `python -m factory.readiness`
> cannot exit 0. **The fix is written and unmerged on `lane/control-plane`.**

⭐ **That is §15.1's defect class for the fourth time** — an instrument that cannot pass — and R18
says so itself: found by F11 on a lane branch a day before R18 found it independently, established as
a rule by F20/F21, generalised by §15.1, **and three live instances remain on HEAD.** §15.4's lesson
was written and the estate has not yet managed to apply it to itself.

### 17.4 ⭐ The oldest conclusion in the corpus is filed here as the newest

`OBSERVED` — `grep` over this file returns **zero** hits for *permission topology*, *not an
enforcement boundary*, *prompts are not access controls*, or any equivalent phrasing.

§16.4 calls R17's *"every genuinely mandatory control is a Snowflake control; every conventional one
is a tool control… enforcement has to live in the RBAC graph, not in dbt"* **"the load-bearing
sentence of the whole answer."** R18 §1.2(3) calls it *"R17 §4.3's whole point turned on us."*

**Three of the first four answers said it on 2026-08-21, two days earlier, and none reached this
document:**

| Pass | What it said, verbatim | Filed |
|---|---|---|
| **R2** | *"For side-effecting infrastructure, **permission topology outranks prompt topology**"* — with a table grading six prohibitions **D as prompt text and A as an enforced boundary** | 08-21 20:23 |
| **R3** | *"Giving an autonomous shell an Azure identity that can create arbitrary resources and then trying to protect a `max_attempts = 3` variable inside its repository **is not an enforcement boundary**"* | 08-21 21:13 |
| **R4 run 2** | §*"Prompts are not access controls"* — *"'do not touch production' inside a prompt **is not a security boundary**"*, with the Replit database deletion as the named public incident | 08-21 20:26 |

§3.3 took R3's *ranking* of evaluator-isolation measures and left R3's *principle* behind. §7 item 4
disposed of R4 run 2 in one line — *"no material contradiction found… treated as corroboration"* —
and its isolation section is where the principle lives.

⭐ **This is the reconciliation failure with the highest price attached, and the price is legible.**
§8 row 6 has said *"evaluator as a service, not a directory move"* since 2026-08-21 and is still
`pending`. Every §16.13 row R17 earns — 17, 18, 20, 21, 22 — is an instance of a rule this document
could have adopted on day one and carried as a standing test: **for any control, ask whether the
agent can widen it; if the answer is "only by ignoring an instruction", it is not a control.** R17
supplied Snowflake's grant semantics, which is genuinely new and genuinely strong. It did not supply
the principle. **We paid R17 to tell us something three earlier answers had already told us, and the
reason we did not know is that nobody wrote it down here.**

### 17.5 The three §9 follow-ups were dispatched two days ago and nothing came back

`OBSERVED` — `answers/R1-followup.md`, `R2-followup.md` and `R3-followup.md` exist, all written
2026-08-22, all three headed **"Status: DISPATCHED, not answered."** Each names where its answer
would land — `R1-followup-answer.md` and so on. **None of those three files exists.**

§9 still reads *"Three follow-ups to ask in the existing threads."* They were asked. The record does
not say so, does not say where they live, and does not say they have been silent for two days. R2's
is self-described as *"the highest-value unasked question in the programme"* — whether to move the
build plane onto Prefect or reimplement its primitives — and §4's correction, which is what made it
necessary, is still carried as an open amendment to R2's prescription.

⚠ §16.14 item 9 noticed that §9's mechanism does not work for in-repo passes. **It did not notice
that §9's mechanism had already stopped working for the outside threads it was written for.** Items
4–7 were added to §9 after these three and have no files at all.

**§9 is a queue with no state field.** `factory/dispatch.py` has five — `ANSWERED / UNDISPATCHED /
IN_FLIGHT / STALE_STATUS / UNKNOWN` — and reports queue depth by design. Pointing it at §9 is the fix.

### 17.6 The only external challenge to §5's build order never reached §5

§5 says the order stands. §16.8 says *"R17 reorders nothing."* Both are true and both are silent
about the one pass that did challenge it.

The R16 outside-evidence lane's **§1** — a section §15.5 does not summarise, because §15.5 absorbed
that lane's six-item executive summary and stopped there — reaches a verdict on §5 directly:

> **"NOT SUPPORTED for step 6's position. NO EXTERNAL EVIDENCE EITHER WAY for steps 1–5."**

Its basis is the largest survey n in the programme — LangChain *State of Agent Engineering*,
**n = 1,340**, fielded 18 Nov – 2 Dec 2025: observability adoption **89%** against offline evals
**52.4%**, a 37-point gap — with Anthropic (*"wait too long and you're reverse-engineering success
criteria from a live system"*), Hamel Husain (error analysis on real traces precedes metric choice)
and OTel (evaluation modelled as a span attribute *on* the trace substrate) all ordering the same
way. **Our step 6 is "complete attempt/cost telemetry, including failures", and it sits behind five
steps of control-plane work that would be built and debugged against a log that is not yet complete.**

⚠ **And it names a possible internal contradiction nobody has resolved:** step 3 is *"terminal verdict
computed from append-only history"* — which **is** the trace substrate — while step 6 is the telemetry
that fills it. *"One of those two is misplaced. This is checkable inside the repo and I have not
attempted to resolve it; it is named, not settled."* It is still named and not settled.

⭐ **The tier matters and it cuts both ways.** That lane is explicit that the field's silence on steps
1–5 *"is not agreement, it is a silence"* — so this is not a reason to reorder anything except
possibly step 6. But §5 has never carried the challenge at all, and a build order that no external
evidence has ever been allowed to touch is exactly the shape §16.11's survivorship-bias caveat warns
about.

### 17.7 §15.6 said nobody had written the action down. Two answers had.

§15.6 concluded that if the binding limit is reviewer throughput, *"the useful first move is something
that raises review capacity or lowers what needs reviewing — that is a different action, and nobody
has written it down yet."* §16.9 then reports that *"§15.6's missing action now has a candidate with
numbers"* and points at R17's adversarial reviewer at every artefact boundary — real, well-evidenced,
and **days of work**.

Two answers already on disk name a cheaper first move, and both name it as the item that *decides*
a14 rather than one that implements it:

- **R13 run 2 §3**, filed 13:34: *"Nobody has established whether those 6–9 days were **no
  notification sent** or **notification sent and ignored**. That is `NOT-SUPPLIED` by the pack, and it
  decides the entire remedy… **Measure first: was the reviewer subscribed?** A ZERO and a NOT-VISIBLE
  are different verdicts."*
- **R16 §4 step 1**, filed 15:56 — in the same answer §15 is built from: *"**Measure the notification
  path on the two waiting PRs.** Cost: ~1 hour… **This is the item that moves the number**, because it
  is the only one that tells you which remedy moves it."*

⭐ **It is this estate's own third analysis gate applied to a14** — a zero from an instrument nobody
proved could see is not a measurement — and it costs an hour. **The record went looking for an
alternative to a14 while holding two written statements of it.**

⚠ Both are still true and neither is done. §17.11 row 30 carries it.

### 17.8 Three places this document contradicts itself, and one count that drifted

| # | The contradiction | Now |
|---:|---|---|
| 1 | **§13.5** calls "9.3 s → ~1.2 s, ~30 lines" *"wrong by about eight times"*. **§13.7 item 1**, eleven lines later, was *"thread the server and parallelise the probes, 9.3 s → ~1.2 s, ~30 lines."* R16 §1.2 found this and named the mechanism: *"the finding lands in the analysis section, the decision list is not rewritten, and the decision list is the thing anyone acts from."* | ✅ corrected above |
| 2 | **§15.3** says the outside-evidence lane *"has not been read yet"*; **§15.5**, four paragraphs later, opens *"Read 2026-08-23."* Same section. | ✅ corrected above |
| 3 | **§12.1** says R11 found *"seven absent concepts"*; **§12.5** names **six**; **R11's own summary** says `ABSENT: 9`. Three counts of one set. | ✅ marked above |

**The three §12.5 drops are not filler.** R11's nine include **cloud/background agents**,
**persona/channel abstractions**, and — the one that matters — **mid-run human-in-the-loop approval**:
*"we have no mechanism to suspend and resume an agent run in flight"*, with Azure Foundry's durable
`task_id` suspend-for-human and LangGraph's `interrupt` / `Command(resume=True)` named as prior art.

⭐ **Put that next to §16.11, which lists as `ABSENT` *"any shipped mechanism for injecting context
into a running agent."*** They are not the same claim — steering a live agent is not the same as
pausing one for an answer and resuming it — but **the difference is exactly where the blocked-questions
design sits** (§12.8 item 3), and no section puts them side by side. The R16 outside lane reached the
same place from a third direction: a pausable HITL *"is not a standalone artefact; it sits on durable
state"*, i.e. on §5 steps 2–3. **Three passes touched this and the record holds one.**

### 17.9 What no section has ever touched

`OBSERVED` — each row was confirmed by a case-insensitive `grep` over this file returning zero
substantive hits before §17 was written. This is not everything the answers say; it is material that
reaches a conclusion or names a mechanism and appears nowhere here.

| Answer | Unabsorbed, and why it is not filler |
|---|---|
| **R1** | *"Unintended-side-effect and reconciliation checks"* — graded **High** among the damaging omissions: correct landed rows are not enough if the agent also leaves duplicate loads, orphaned deployments, unintended tables or stale containers. ⭐ **R17 §4.7 rediscovers it two days later as *"none of these receipts describes what the agent did to a shared warehouse — the single biggest gap in the field's tooling for your use case."*** Same gap, two arrivals, unconnected. Also the `pass@k` vs `pass^k` reporting set. |
| **R2** | The permission-topology principle (§17.4), and the build/run manifest schema — the nine dimensions in §3.4 are R2's *list*, but the manifest that carries them, and the run record kept separate from the build record, are not here. |
| **R3** | ⭐ **The expected-work manifest and `scope_hash`.** R3's executive verdict calls scope/evidence closure **"the biggest missing control"**, because the six prescriptions *"can still report success over work they never knew existed"*, and derives `SUCCEEDED` from it. §5 has no such step. Also **FACPR** (first-attempt contract pass rate), the metric that stops attempt 352 and attempt 1 scoring alike; the **budget proxy** that owns the provider credential so a token cap is enforceable rather than advisory — which is §16.8's recommendation, designed two days earlier; and the corpus gate of **40 fixtures, 30 development + 10 held-out whole connectors**. |
| **R4** | The **Fitness Qualification Gate** — five named pre-search tests (repeatability, known-bad sensitivity, known-good invariance, discrimination, holdout validity), each with an abort condition. §11.4 rejects gates-as-fitness and §16.6 corroborates; **neither cites the gate design already written.** Also the degradation power table (305 / 134 / 74 observations per arm). |
| **R5** | §3 property-based and differential testing as the answer to brittle instruments; §4 *"one canonical readout model, regenerate and diff in CI"* — the same problem R13 run 2 found shipping as **four page strings asserting the page caches nothing**; §6 the hierarchical-memory handoff model. §10 took R5's items 1, 2 and 5 only. |
| **R6** | ⭐ §5: *"a single model tends to over-report and needs adversarial checks — one agent proposes issues, another challenges them, an arbiter decides."* **That is §16.9's adversarial reviewer, filed 2026-08-22.** And §4's alert-fatigue position — see below. |
| **R7** | §5's interface grammar: planned must not look built, and any figure that does not move with the data is decoration. |
| **R8** | §5 experimental structures and §6 the agent-terminal UI. §13 took the isolation half, named the scheduling/messaging half as ignoring supplied constraints, and left the rest. ⭐ Also: **R8 §2 answered the record/channel question with "event sourcing… like CQRS", which §16.10 refutes as "neither"** — and §16.10 presents it as a question *"asked in session"*, never recording that a pass had already answered it wrongly. |
| **R10** | ⭐ §7: *"We already have **six** overlapping stores… adding a seventh would be a mistake… **retire or merge at least one.**"* R16 §3.4 flags that a5 took *"skills over corpus"* and dropped the recommendation it sat inside. It bears directly on §16.10's ledger split and on R18's enumeration of shared state. ⚠ Also: R10 attributes its strongest figure (32% → 55%) to **"Swift Lab"** and to **"Elias Calboreanu"** in the same source list — the same finding under two authors, a sharper tell than §12.6's "not linked". |
| **R11** | Three of nine absences (§17.8). |
| **R12** | §4.4's productivity list — prompt templates, session forking and its token cost, cross-session search, checkpoints, a prepared prompt queue — each tiered. |
| **R13 run 2** | ⭐ **Five of its six findings.** §13.6 took the switchboard settlement and §15.1 quotes it once. Untaken: the four false *"nothing on this page is cached"* strings; the cache fingerprint's live stale-green holes (`scripts/` is not in it and the suite imports it; the environment is not in it, which **reintroduces F72 verbatim**); the duplicate `measure()` per render; *"the extension is admissible only when it can **subtract** the tracker's emitter"* and the `platform/master` postmortem behind it; **APPROVE leaves the building and becomes a GitHub PR**, which removes the very plane §14.2's platform argument was justifying; and retire `orchestration-bench.html`. |
| **R14** | Everything (§17.2). |
| **R16 audit** | §15.3 lists nine findings as **nine bare pointers with no content**. Their substance — a14 merged with a3 into a `Decision`, a1's honest state, a4's real evidence, a6's disconnected producer, a13 as a ranking-with-a-precondition rather than a decision, and the whole of §4's ordering — is not here. ⭐ And its §3.1: **the eval corpus is one file, 6,747 bytes.** R1 asked for ≥29, R8 repeated it, R10 made it a precondition of its own recommendation, the `breadth` gate asks the question — *"and no action among the eighteen names it."* |
| **R16 outside** | §1 entirely (§17.6). §3's two qualifications on a8: an allowlist without network isolation is not isolation, and ⭐ **a container does nothing about prompt injection** — the lethal trifecta survives it intact. §5's amendment: **file conflicts cap writers, and only writers** — for read-only fan-out the caps are synthesis overhead, token cost and a tool-enforced ceiling of 20. ⚠ **R16 and R17 both ran as read-heavy fan-outs, and §16.2 argues α(G) for a full section without that distinction.** |
| **R17** | Well absorbed — §16 is the model for what a section should do. |
| **R18** | Everything (§17.3). |

⭐ **The alerting question is the clearest case of the record holding one side of an argument it has
already heard both sides of.** Five positions exist across five answers: **R6 §4** (fatigue is real;
alert only on the actionable) → **R12 §4.2 / R13 §6** (absence, not fatigue; must interrupt) →
**R13 run 2 §3** (measure whether it fired at all, first) → **R16 outside §2** (the inverted-U:
*"escalating everything is strictly worse than the optimum"*) → **R17** (same paper, independently).
§14.3 records the middle pair as *"three passes and one measurement agree — stop asking and build
it"*; §15.5 retracts the independence; §16.9 adds the denominator. **R6's position — filed first, and
on the same side as the strongest external finding — is nowhere**, and §10.5 records only R6's
admission that it had no threshold to offer. Two of the five sources agreed with each other and were
counted; the two that agree with the inverted-U were not.

### 17.10 The mechanism, and the control that would catch it

**This is not an absorption problem. It is §16.7's mechanism, running on this document.**

R17 measured it: a gate at the first artefact boundary catches **75.4%** of what a gate at the last
catches **10.7%** of, because *upstream transformations destroy the information needed to check the
claim.* §16.1 is this repo's instance of that in the *contents* of a claim — the 41.7% degrading
across six restatements until it was true of nothing.

⭐ **§17 is the same mechanism operating on a claim's *status* rather than its content.** "R14 has
not run" needs no judgement to check. It needs one `ls`.

⛔ **But the cheap fix is refused, and by a finding filed before this section was written.** The
obvious move — extend the mention check to reject a mention appearing inside *"has not run"*, *"still
outstanding"*, *"when X lands"* — is **F75 option (c)**, and F75 rules on it: *"Cheap, and **it is a
refuse-list, so it is wrong by omission** — the exact defect shape recorded for the DAX answerability
guards."* It refuses the other obvious move too: *"⛔ **Do not simply tighten `unreconciled()` to
per-answer mtime comparison.** It would have caught this instance and still cannot distinguish
absorption from an edit that touched the file. **A stricter proxy for the same unmeasured thing reads
as a fix and is not one.**"*

⭐ **That ruling is right, and it is this document's own doctrine applied to its own instruments.**
Row 28 was drafted as option (c) and is **corrected below**. F75's verdict is the one to carry:
*"the only instrument that has ever found an unabsorbed answer here is an agent that read the
answers."* **Absorption is not mechanically detectable from the text.** What *is* mechanically
detectable is whether a worker **claims** to have absorbed a given id — option (b): a claim with a
name on it, sitting on the same trust boundary as every other agent self-report here.

**Where §16.7's detector 1 still applies, narrowly and honestly:** it can check that every id named in
this file **resolves to a filed answer** — precision ≈ 1, no LLM call. It cannot check what the
sentence says about it. `factory/synthesis.py`'s docstring already says mentioning an id is not
reconciling it. **The gate exists, states its own blind spot in print, and was read as a verdict
anyway.**

⚠ **And the failure is not in this file alone.** R18 §1.5 item 6 found five citations in our own
findings ledger whose substance holds and whose line numbers have drifted; R17's verification ledger
found five of thirty-eight citations wrong and corrected them in the open; §15.5 found the outside
lane had a paper's date wrong by two months. **Four independent instruments, one shared finding: in
this estate substance survives restatement and precision does not.** That is worth stating once,
plainly, rather than rediscovering per-pass: **when reconciling, re-open the artefact. Do not quote a
claim about it.**

### 17.11 What changes — additions to §8

| # | Change | State |
|---:|---|---|
| 28 | ⭐ **A per-answer absorption marker — F75 option (b), and the decision belongs to F75, not to this section.** The reconciling session records which answer ids it actually read and folded in; the check compares that list against `filed()`. ⚠ Only as honest as the worker, which F75 states plainly. ⛔ **Not the tense/negation refuse-list and not a stricter mtime proxy** — F75 refuses both, and this row was drafted as the first before F75 was read (§17.10) | not started — **owned by F75, which is OPEN and undecided. §17 supplies the seven-instance evidence, not the remedy** |
| 28b | **Stop reading `unsynthesised()` / `unreconciled()` / `test_synthesis_current` as a verdict on the record.** F75: *"treat both checks as detecting a record nobody touched, and nothing subtler."* The `/research` panel already says so in print and it was not enough — **the premise this pass was handed came from those two checks reading clean** | not started — a labelling change, and F75 is the evidence that labelling alone does not hold |
| 29 | ⭐ **Write the missing sections for R14 and R18.** Start with R14 §7.5 (`/finish` releases before it checks and never calls `factory.finish`) and R18 §0 (three probes with no reachable PASS; fix already written on `lane/control-plane`) — both live, both cheap | not started — **R14 §7.5 fires every time, and R18 §0 makes two of `launch.py`'s three questions unanswerable** |
| 30 | **Run R16 §4 step 1** — open the two `prefect-connectors` PRs and establish whether a notification reached a subscribed human. One hour. It confirms or kills a14, which §14.7 still ranks second (§17.7) | not started — **cheapest measurement in the programme, and it gates the most-cited action** |
| 31 | **Point `factory/dispatch.py` at §9**, and record the three follow-ups as dispatched-and-unanswered since 2026-08-22 with their files named (§17.5) | not started |
| 32 | **Carry the permission-topology principle into §3 as a standing test** — *for any control, can the agent widen it? If only by ignoring an instruction, it is not a control* — cited to R2, R3 and R4 run 2, not to R17 (§17.4) | not started — it is already the shape of §16.13 rows 17–22 |
| 33 | **Put the R16 outside lane's step-6 challenge into §5** as a recorded, unresolved amendment, and settle whether steps 3 and 6 are the same substrate (§17.6) | not started — checkable in-repo, named-not-settled since 15:56 |
| 34 | **Add the eval corpus to §8.** One file, 6,747 bytes; asked for by R1, repeated by R8, made a precondition by R10, measured by the `breadth` gate, and named by no action (R16 §3.1) | not started — R16 rates it above both defects it actioned |
| 35 | **Reconcile the alerting question in one place**, all five positions, R6 first (§17.9) | not started |

### 17.12 How this reconciliation ran — both halves

**Read all twenty answer documents in full before writing anything**, in this order: the three
follow-ups, R13 run 2, R18, R14, then R8, R15, R5, R6, R7, R11, R10, R12, R13 run 1, both R16 lanes,
R1, R2, R3, both R4 runs, R17. ~11,600 lines. Every status claim in this document was then checked
against `ls -la answers/` and `grep`; every "unabsorbed" verdict in §17.9 is a zero-hit search anyone
can re-run.

**Stronger than an outside reader on the mechanical half.** An outside pass cannot run
`ls -la answers/` and see that `R14-answer-structure-model-and-joy.md` was filed at 13:38 while §14 —
written after §13.5, which cites an answer filed at 13:34 — says it is unsent. Every finding in
§17.1, §17.2, §17.3, §17.5 and §17.8 is of that kind: a file timestamp, a string count, a missing
file. None is a judgement.

⚠ **Weaker on the half that matters most, and in the specific way §16's closing note describes.** This
pass read this document's conclusions before deciding what counted as unabsorbed, from inside the
estate whose record it is grading. Two consequences, stated rather than hedged:

1. **§17.9 is a list of what is missing from *this document*, not a list of what is important.** The
   material was selected by a mechanical test — does it reach a conclusion and appear nowhere — but
   the ⭐ marks on individual rows are this pass's judgement, and it is the same judgement that
   produced the omissions.
2. ⛔ **It did not re-verify the answers' own claims.** Where §17 says R14 found a live defect in
   `local_tracker.py`, that is **R14's `OBSERVED` and R16's independent re-verification, not this
   pass's** — this pass may write only `SYNTHESIS.md` and did not open the file. **Treat every
   `path:line` inherited into §17 as `REPORTED` until someone reads it.** R18 §1.5 item 6 is the
   reason to insist: five ledger citations whose substance held and whose line numbers had drifted —
   and the `ThreadingTCPServer` line alone is cited as `:1181`, `:1663`, `:1875` and `:2357` across
   four answers written within four days.

⭐ **What would have made this pass unnecessary — and the honest answer is nothing cheap.** The first
draft of this section said a millisecond file-existence check would have caught it. **F75 had already
refuted that**, and the refutation is F75's most valuable contribution: a tense refuse-list is wrong by
omission, and a stricter mtime proxy *"reads as a fix and is not one"*. There is no mechanical detector
for absorption. What there is, is a **place to put the claim** — which ids did this session read and
fold in — so the next reader is checking a worker's statement rather than a document's word count.

⭐ **What generalises past this file.** The record failed at the **last** artefact boundary, which is
where §16.7 measured detection at **10.7%**. The check belongs at the **first**: when a section is
appended, not when someone finally reads the whole thing. And the reason both instruments missed it is
the reason §16.7 gives — *"upstream transformations destroy the information needed to check the
claim."* Absorbing R17 cleared the mtime signal for R13 run 2, R14 and R18 **as a side effect**.
⭐ **The act of reconciling one answer is what erased the evidence that three others had not been.**


---

## 18. R19 — the work taxonomy, and the first pass to say what the selector should *refuse* (added 2026-08-29)

The eighteenth answer, filed 18:48 on 2026-08-29, six days after §17 closed the previous batch. It
asked what kinds of work this company actually does and how a team gets chosen for a ticket — the
first pass pointed at the **dispatch** decision rather than at the product, the process or the record.

⚠ **Grade the instrument first, because that is the house rule.** R19 ran as a Claude Code session
**inside this checkout**, with `~/repos/wiki` readable and no evidence pack — the same class as R16,
which §15 calls *"the least independent pass we have run"*. It has **no external evidence of any
kind**: not one paper, benchmark or vendor doc. Everything in it is either our own artefacts or its
own design. So it is **strong on `path:line` claims and weak on anything that would need the outside
world to arbitrate**, and it must not be weighed as R17 was.

✅ **The `path:line` half was re-run here and it holds.** Every load-bearing internal figure in R19
was re-measured this session, including the two that would have been most convenient to leave alone:

| R19 claim | Re-measured 2026-08-29, this pass |
|---|---|
| 5 presets, 1 `WIRED` | **5, 1** ✓ |
| 30 gates: 9 `PASS` / 17 `FAIL` / 3 `UNMEASURABLE` / 1 `NOT_RUN` | **identical** ✓ |
| `.data/runs.jsonl` — 3 rows, all `FINISHED` | **3, all `FINISHED`** ✓ |
| `g_version_hash_is_complete` → `FAIL`, 6 of 15 | **`FAIL`, 6 of 15** ✓ |
| `presets.py:180` — `wrong-number` cites GP-322 alone | ✓ |
| `eclipse-azure-deployment.md:16` — the no-op workflow that succeeds every run | ✓ verbatim in the wiki, plus `:150`'s `rollback-check` no-op |
| GP-311 — *"a council of five… caught six factual errors"* | ✓ `tickets/gep/GP-311.md:16`, and the page is tagged `inquest` |
| `TeamSpec.version` blind to `repo` and `prohibition` | ✓ **at `HEAD`. Already fixed in the working tree — §18.2** |
| `.sessions` is absent from this checkout | ⛔ **wrong — the directory exists and the question it blocked is answerable. §18.6** |

Per §17.12's rule — *when reconciling, re-open the artefact; do not quote a claim about it* — nothing
below is inherited. Where a row above says ✓, this pass ran it.

### 18.1 ⛔ The false-premise story, and it is not the one the reconciling prompt told

The prompt that produced this section says, in bold: *"⚠ Read `docs/findings.md` F7 first. One of
these answers was produced under a FALSE CONSTRAINT that I wrote into its prompt, and it demonstrably
changed the ranking."* **That sentence is not about R19, and nobody wrote it about R19.** There are
three layers here and they need separating, because two of them are real and the loudest one is not.

**(a) The warning itself is a frozen template, and it is F7's own mechanism running in the instrument
built to catch the R5/R6 gap.** `OBSERVED` — `factory/synthesis.py:84–86` hard-codes into *every*
generated reconciliation prompt:

> *"Label every recommendation by the basis its source gave it… **R6 labelled its own; R5 partly
> did.** ⚠ Read `docs/findings.md` F7 first. **One of these answers** was produced under a FALSE
> CONSTRAINT… and it demonstrably changed the ranking."*

`grep -n "R6\|R5\|FALSE CONSTRAINT" factory/synthesis.py`. Those sentences were true of the R5/R6
reconciliation on 2026-08-22 and are emitted verbatim for R19 on 2026-08-29 — an assertion about the
answers in front of the reader, made by a generator that has never read them. ⭐ **That is precisely
F7: a constraint asserted in a prompt without being measured, optimising the reader against a world
described to them rather than the one on disk.** It is also §17.1's class — a status claim nobody
re-read before appending under it — relocated from this document into the tool that checks it. §17.10
concluded that the generated prompt is the honest half of `factory/synthesis.py` because it *"names
the actual gap"*; `test_the_prompt_names_the_actual_gap` asserts the **id list** is generated and says
nothing about the paragraph around it. **The gap is computed; the guidance is a constant.**

**(b) There *is* a false constraint in R19's brief, it is a different one, and it is a re-infection
this document already cured once.** `R19-work-taxonomy-and-team-selection.md` §5.1 states as fact that
*"the config hash covers **0 of 15** identity dimensions"*, citing `docs/specs/product-end-state.md:66`.
**§15.1 established on 2026-08-23 that the true figure is 6 of 15**, that the `0` was the output of a
regex containing a literal U+0008 that could never match, and fixed the gate. **The spec was never
updated.** Six days later it seeded a research prompt with the number §15.1 retired.

⭐ **A corrected premise that survives in an uncorrected document is not corrected.** `grep -rn "0 of
15"` returns the spec plus **nine** further occurrences across R13 run 2, R14, R16 (both lanes) and
R18 — the four documents §15.1 itself listed as carrying it, still carrying it. §15.1's own table
named where the wrong figure was load-bearing and then fixed only the instrument. **That is the
inverse of §17.4's failure and the same cost**: there, a principle three answers held never reached
the record; here, a correction the record made never reached the answers or the spec.

**(c) Did it change the ranking? No — and *that* is the difference from F7, which is why this must not
be filed as a repeat.** R6 deferred CI-on-push *on the strength of* my false sentence and its ordering
moved. R19 **re-measured the number it was handed, found it wrong, and filed the correction inside its
own answer** (§6.2), under this estate's rule that correcting an inherited premise is a deliverable:

> *"This brief's own §5.1 repeated the '0 of 15' figure, inherited from that spec without
> re-measuring… The substantive claim survives — 9 dimensions are genuinely absent, `contract_version`
> most damagingly — but *'the hash covers nothing'* is false and **overstates the case in a way that
> would have made §6.1's real defect harder to see**."*

**The honest verdict: the distortion was caught in-pass, the ranking is unaffected, and the residual
harm R19 names is real but small** — an overstated denominator makes a specific, live hashing defect
harder to notice, because if the hash covers nothing then nothing about it is surprising. ⚠ **Do not
record this as "F7 again."** §12.2 and §16.1 are already F7 variants (a real constraint omitted; a
claim degraded across restatements). This is the fourth variant and it is the *good* outcome: **the
premise was false, the pass measured it, and the correction is in the answer rather than in a later
reconciliation.** The finding is not about R19's judgement. It is that the corrected number sat
un-propagated in a spec for six days and re-entered the programme through a prompt.

**(d) And one constraint that was violated rather than false — the blind-first control.** R19's brief
required the ticket corpus to be read **before** `factory/presets.py`. R19 opens with the disclosure,
before anything else, that this was *"partially violated, and not by this run"*: the answering session
had already read `presets.py` — every `type_id`, `seen_in` and `verifier_state` — while writing the
brief the previous turn. What stayed blind was the 59-ticket sweep; what did not was the five existing
types, so R19 marks *"these five are correct"* as `ASSUMED` throughout and claims no independent
weight for it.

⭐ **Its generalisation is the most transferable thing in the answer, and it is about us, not about
it:** *"a `STRUCTURE_CRITIQUE` pass whose brief is written by the same session that then answers it
cannot be blind, because writing the brief requires reading the code. **The brief-writer and the
answerer must be different sessions**, or blind-first is a label rather than a control."* That is
`readiness.py`'s own doctrine — an instrument that cannot refuse — applied to a research protocol, and
`docs/research/README.md` does not carry it.

### 18.2 ⭐ The certification-laundering defect — found, proven, and fixed while this section was being written

R19's first executive finding is a live defect in the module whose docstring is *"the config that IS
the version"*.

`TeamSpec` declares `repo` and `prohibition`; its `version` property hashed four hand-enumerated keys —
`team`, `topology`, `contract`, `agents` — and neither of those two. R19 predicted identical hashes
**before** running the test, in the form this estate requires, and got them.

**Re-run this session, and the result has moved:**

| | `repo` + `prohibition` changed | Verdict |
|---|---|---|
| `git show HEAD:factory/blueprint.py` | version **unchanged** | ⛔ R19 confirmed — a team certified against `prefect-connectors` under *"must not deploy to production"* keeps its certification when repointed at another repo with the prohibition deleted |
| working tree, uncommitted | `9e68053d5cbc` vs `63009b7da765` — **different** | ✅ fixed |

A concurrent session fixed it between R19 filing and this reconciliation, and the fix cites R19 §6.1
in its docstring. ⭐ **It also went further than R19 asked, in the direction this estate cares about.**
R19 recommended hashing `asdict(self)` minus `purpose`. The implementation does that and adds the
thing R19 only asked for elsewhere (§7.3): `NOT_IDENTITY` is a **deny-list**, so a field added to the
dataclass is identity by default, and `tests/test_blueprint.py` gained
`test_every_identity_field_has_been_proved_able_to_move_the_hash` — one constructed pair per field,
proving by construction rather than by reading the source. **That is the negative-control idiom
(`test_every_assertion_has_been_proved_able_to_fail`) reaching a third module.**

⛔ **What was *not* fixed is the half that matters for every future instance.** R19's second claim
about this defect — *"the gate cannot catch it"* — is still true, and this pass re-ran it to be sure.
`g_version_hash_is_complete` (`readiness.py:867–879`) **greps `blueprint.py`'s file text** for each
dimension name. `repo` and `prohibition` appear in that file whether or not they are hashed, so the
probe cannot distinguish *"the field exists"* from *"the field is in the hash"* — the self-matching
class the same file warns about twelve lines later, at the probe that *"MATCHED ITS OWN SOURCE"*.

⭐ **And here is the tell, which R19 did not have because it ran before the fix: the gate reports
`FAIL, 6 of 15` on both sides of a change that genuinely improved the hash.** The number did not move
when the thing it measures got better. **§15.4 called that out as a class — *"a number nobody can make
move is not a measurement, it is a constant with a citation"* — and this is the same gate that carried
§15.1's U+0008 defect.** Twice broken, twice for the same reason: it asks the source text a question
only two constructed objects can answer. R19's fix is one line of intent — *compare two specs, do not
grep* — and it belongs in §8 as its own row (row 37), separate from the code fix that is already done.

### 18.3 Where R19 disagrees — with `presets.py`, with §6, and with a formation this estate already runs

| # | Disagreement | Which evidence is stronger |
|---:|---|---|
| 1 | **`presets.py` covers 5 of 16 measured ticket types**, and R19 argues the 11 missing carry the *larger* blast radius — incident, auth/token lifecycle, infrastructure, analysis-deliverable, schema-extension | **R19**, and it is not close. The five presets are a real table with `seen_in` on every row; the taxonomy is a 59-page sweep with ≥2 tickets per type. ⚠ But per §18.1(d) the *agreement* half — "the five are right" — is `ASSUMED` and carries no weight |
| 2 | **`wrong-number`'s `seen_in` cites GP-322 alone**; R19 adds GP-311, GP-282, GP-281 — and notes GP-311 is *"the second occurrence of the same defect"* (ALDC-490 fixed it five weeks earlier at the wrong layer) | **R19**, verified here at `presets.py:180`. ⭐ Its argument is the sharp part: **a repeat is the strongest possible evidence that a type is real, and the repeat is the citation the row omits** |
| 3 | **§6's unlock condition for a dynamic team-selection LLM — *"≥200 adjudicated examples plus static misrouting ≥10%"* — is unreachable in principle, not merely distant** | **R19**, and this **amends §6**. R2 set a threshold on a *count*; R19 shows the count can never be accumulated because nothing records **which configurations were eligible and were not chosen**. *"Every other field can be backfilled with effort; this one is gone the moment the run starts."* A count-based unlock condition on an unrecorded population is not a gate |
| 4 | **GP-311's five-agent council does not overturn R2's rejection of the three-agent team**, and R19 refuses to let it | **R19's distinction is right and it is the reconciliation §3.1 needed.** R2 measured *sequential handoff chains on shared mutable state* — every seam a place to lose information. `inquest` is a **parallel council on orthogonal lenses with a human arbiter**: no agent consumes another's output, so there are no seams. ⚠ `INFERRED`, on n=1, from our own ticket |
| 5 | **§16.2's third option — conflict-graph resolution — and R19's §7.2 rule 8 point opposite ways on what to do *now*** | Not a contradiction, and both stand. §16.2 asks how to *raise* the ceiling; R19 asks what the filter should return **today**, and answers: *"applying rule 8 alone against today's gate state, the filter returns empty for every unattended run in the estate."* ⭐ **That is the first sentence in the programme that says what the 17 `FAIL`ing gates should actually *do* to a dispatch decision**, rather than what they reveal about it |

⭐ **Item 4 is worth stating as a rule, because this estate has now spent four sections arguing around
it:** *parallelism over orthogonal views of the same artefact is cheap and safe; sequential handoff on
shared mutable state is what R2 measured and rejected.* §16.6 already corroborated the mechanism from
outside — a critic helps when it **sees something the generator did not use**, and fails when it is
"think again" on the same reasoning [A-10–A-12] — and §16.9's adversarial reviewer is the same shape.
R19 supplies the name for the distinction and the one internal case where it was run.

⚠ **And the qualification R19 does not make, which §16.9 forces.** GP-311 is a **recall** observation —
six errors caught — with **no denominator and no false-positive count**, which is exactly the gap
§16.9 says *"the field will not supply"* and R18 was asked to generate internally. One ticket where a
council caught six errors is a reason to keep the formation, not evidence of its precision.

### 18.4 Basis labels — and R19 has none of the kind the house rule asks for

The standing rule is `OBSERVED in a comparable setting` versus `EXTRAPOLATED from human teams`. R19
runs two vocabularies of its own (`MEASURED / DERIVED / STATED / ASSUMED / PROXY` for the world,
`REPO-BACKED / INFERRED / RECOMMENDED / EXTERNAL / SPECULATIVE` for the design) and applies them
consistently. The mapping needs one thing said plainly:

| R19 recommendation | Its tier | Read it as |
|---|---|---|
| The taxonomy — 16 types, ≥2 tickets each (§2.1) | `MEASURED` from 59 ticket pages | **OBSERVED in the only comparable setting there is: ours.** The strongest class in this answer |
| The `TeamSpec` version defect (§6.1) | `MEASURED`, discriminating test, prediction first | **OBSERVED** ✓ re-run here. The single hardest claim in the pass |
| The manual-step ledger and its verdicts (§4) | `REPO-BACKED` runbook citations + `RECOMMENDED` verdicts | Citations **OBSERVED** ✓ spot-checked; the `KEEP-HUMAN`/`AUTOMATABLE-NOW` column is **authored judgement** |
| The dispatch record schema (§5.2) | `RECOMMENDED` | **Design, not evidence.** Nothing like it has been run here or cited from anywhere else |
| The eligibility filter and its negative control (§7.2–7.3) | `RECOMMENDED` | Design. Its *inputs* (gate verdicts, `verifier_state`) are measured; the rule set is not |
| ≈12 terminal runs per (type × bundle) arm for stage 4 (§7.5) | `DERIVED`, and it says so | **EXTRAPOLATED** — a power calculation against R2's ≥10pp threshold, not a measurement. Compare §3.2's 29/59/299 table, which is the same arithmetic done for the corpus |
| Formations, and `inquest` as `READY-NOW` (§8.2) | `MEASURED` on GP-311 | **OBSERVED, n = 1, our own ticket, recall-only** (§18.3) |
| *"Six of nine recurring operations are `NOT-VISIBLE` or `NOT-RECORDED`"* (§9) | `MEASURED` from tickets | **OBSERVED** — and three of the six have a ticket proving a real failure went unnoticed |

⭐ **Nothing in R19 is `EXTERNAL`, and the answer never pretends otherwise.** That is a legitimate
brief — it was asked to read our repos and our wiki — but it means **R19 cannot corroborate anything**.
Where it agrees with R2, R17 or this document, that agreement is not independent: it read them. The
one place it is genuinely independent is the ticket corpus, which no previous pass had opened, and
that is where its value is.

### 18.5 What R19 settles that the record has been circling — three arrivals, one of them eight days late

**(a) ⭐ R3's *"biggest missing control"* has been rediscovered from the ticket corpus, and §17.9
predicted this exact rediscovery.** §17.9 lists, under R3 unabsorbed: *"the expected-work manifest and
`scope_hash` — R3's executive verdict calls scope/evidence closure the biggest missing control, because
the six prescriptions can still report success over work they never knew existed."* Filed 2026-08-21.

R19 arrives at the same object from the tickets, eight days later and without contact, and it arrives
with **evidence R3 did not have**: `MEASURED`, each from a ticket's own text —

> **DV-444:** *"Initial ticket framing: 'code change to eclipse-2.1.' After investigation, that framing
> is wrong… the feature branch will close with **zero commits**."*
> **GP-318:** two scoping premises refuted by measurement. **GP-310:** documents *"the false premise
> that created the bug"* and *"the wrong fix, and why it was reverted."*

R19's conclusion: *"a selector that reads the ticket's stated layer and dispatches a team scoped to it
will, on this corpus's evidence, be wrong often enough to matter. **Scope discovery must be a separate,
cheap, human-gated stage before team formation.**"* Its `declared_scope` / `discovered_scope` pair is
R3's `scope_hash` with a measurement behind it. ⭐ **Two passes, eight days apart, one unabsorbed
section between them — and §17.9 named the gap before R19 filled it.** The record now holds both.

**(b) The `eligible[]` field, and why it is the only irreversible one.** *"It costs nothing to write
and cannot be reconstructed later."* Everything else in the dispatch record can be backfilled with
effort; the set of configurations that passed the filter and were not chosen exists only at the moment
of dispatch. Without it there is no counterfactual and **no off-policy evaluation, ever** — which is
the mechanism behind §18.3 item 3.

**(c) ⛔ The false-`succeeded` mechanism is live in production tooling, already diagnosed, still
shipped.** Verified in the wiki this session, verbatim at `eclipse-azure-deployment.md:16`:

> *"`deploy_az_webapp.yaml` ('Deploy to Azure App Service') is a **NO-OP**. It builds Next.js and
> pushes to `wwwroot`, which a container App Service **ignores entirely**. Every run 'succeeds' but
> changes nothing."*

— compounded at `:150`, where `rollback-check` is itself a no-op whenever the tag does not change, and
GitVersion reuses tags, so *"both slots can share a tag and the rollback net is degraded."* This is the
mechanism `docs/evidence/false-succeeded-mechanism.md` was written about, running in a repo we deploy
from. R19's operational conclusion is the useful part and it is a discriminating test in this estate's
own idiom: **the question an agent must ask is not *"did the workflow go green?"* but *"does the
container digest served by the stage slot differ from the one served before the run?"***

**(d) ⭐ Most of the eleven uncovered types should get a *refusal*, not a preset.** R19 refuses to fill
the table, and the reasoning is §6's never-optimise rule arriving in a new place: *"writing eleven more
`Preset` rows would manufacture the appearance of readiness"*, which `presets.py:29-31` already warns
against. Its dispositions: **preset now** for connector-failure and support-exclusion (the only two
with a real verifier); **a refusal row with a named unblocking condition** for the seven whose verifier
is `UNBUILT` *and* whose consumer layer is production; **out of scope for team formation entirely** for
analysis and scoping, because neither produces a diff.

⭐ **And type 11 — the analysis deliverable — deserves the paragraph R19 gives it.** FU92-420 is *"the
only ticket in the corpus that damaged a client relationship, it involved **zero deploys**, and it
would pass every gate in this repo untouched because nothing was ever certified."* R19's remedy is a
**pre-registration artefact** — the counting basis declared and committed *before* the first query
runs, diffed against the published figure at review. That is the third standing gate (`CLAUDE.md`,
Evidence-Gated Analysis) made into an object, and it is the one class of work where this repo's entire
apparatus is structurally blind: **every gate here triggers on a change, and this class ships damage
without one.**

### 18.6 ⛔ One R19 instrument was pointed at the wrong path, and the question it filed as unanswerable is answerable

R19's §13 lists as `NOT-DETERMINABLE`: *"Do the 14 orchestrator runs and the 3 lane runs overlap? —
`.sessions` is absent from this checkout (`ls .sessions` → 0)."*

**`.sessions` is not absent.** `OBSERVED`, this session:

```bash
ls ../prefect-connectors/.sessions | wc -l          # 13
```

`readiness.py:625` reads it as `CONNECTORS / ".sessions"` — the sibling repo, not this one. R19 ran
`ls .sessions` relative to `agent-factory`, where it has never existed, and read the empty result as
an absence. ⭐ **That is this estate's own third analysis gate, failed by the pass that cites it: a
zero from an instrument nobody proved could see.** It is the cheapest possible instance — the
instrument was pointed at the wrong directory — and it produced a `NOT-DETERMINABLE` verdict on a
question one correct path settles. `readiness.py`'s own docstring for that gate says the matching
thing: *"a question filed as unanswerable that a probe can settle is the same defect as a gate that
cannot refuse."*

**And the question, now settled.** The two ledgers cannot overlap, and not for the reason R19's
framing implies:

| | `.data/runs.jsonl` | `prefect-connectors/.sessions` |
|---|---|---|
| Rows | 3 | 13 dirs, against 14 audit files |
| Dated | **2026-08-23**, all three within 5 seconds | **2026-05-25 → 05-28** |
| Keyed by | `lane` — `control-plane`, `certify`, `artifact` | `pipe_<TICKET>_<runid>` — GP-271…275, KA-15, one placeholder |
| About | agent-factory's own lanes | connector migrations in another repo |

**Disjoint key spaces, disjoint repos, three months apart.** R19's §5.1 presents these as *"two run
ledgers [that] count different populations"*, which reads as two rival counts of one thing. They are
records of **two different machines**, and the honest statement is stronger than R19's: *no single
ledger in the estate covers the thing R19 wants to record, and neither of these is a candidate to be
extended into one.* The substantive finding survives untouched — **neither carries a model, an effort
level, a blueprint version, or an eligible set**, and 3 rows all `FINISHED` is a training set with
zero negative examples.

⚠ **And F4 attaches, as it does every time this number is quoted.** R19 cites *"14 runs `MEASURED`"*
with no age. Those runs stopped **2026-05-28** and nothing has run in the orchestrator since. §16.8
attached F4 to the 3-of-14 figure for exactly this reason; the same caveat is owed here, and the gates
still do not carry the age of their evidence.

### 18.7 What R19 could not settle — and which of its gaps this pass moved

R19 declares seven. Three moved this session; four stand.

| Its question | Its verdict | Now |
|---|---|---|
| Do the 14 orchestrator runs and the 3 lane runs overlap? | `NOT-DETERMINABLE` | ✅ **Settled — no. §18.6** |
| Are the 5 existing presets the right 5? | `ASSUMED` (§0) | ⚠ **Still open, and it needs a different session, not a better prompt** (§18.1d) |
| Time cost of a manual Snowflake deploy | `NOT-DETERMINABLE` — no timestamped phase log exists | Stands. ⭐ It is also the denominator for §4.2's third-ranked automation, so **that ranking is `ASSUMED` on both sides of its ratio** |
| How often is a ticket's stated scope wrong? | `NOT-DETERMINABLE` — 3 instances, denominator unknown | Stands, and R19 calls it *"the strongest single argument for building the record"*. ⭐ Same shape as §16.9's absent false-positive rate: **a recall observation with no denominator**, twice, in two passes |
| Is Zeus Memory queryable as typed selector input? | `NOT-DETERMINABLE` — not inspected | Stands. One `mcp__ccx__cce_memory_search` against a known ticket key settles it |
| Does `pbi_model_apply.exe` cover relationships as well as measures? | `NOT-DETERMINABLE` | Stands |
| What does `succeeds` need to stop being `UNMEASURABLE`? | `NOT-DETERMINABLE` | ⛔ **This one is load-bearing and should not have been deferred.** R19's own §7.1 says *"a selector whose objective function is `UNMEASURABLE` is not a selector"*, and its roadmap phase 8 must not start until phase 5 completes — so the answer to this question gates the whole staging argument, and the pass filed it unread. It is `readiness.py`'s `g_succeeds_more_than_fails` and its `Unmeasurable` raise path. **Row 41** |

⭐ **The pattern across the middle three rows is the one §16.9 named and §18.3 repeats: this estate
keeps producing recall observations with no denominator.** Six errors caught by a council; three
tickets whose scope was wrong; two defects found by a reviewer. Every one is a numerator. **The
denominators are not hard to collect and nobody has collected one**, which is why R19's dispatch record
matters more than its selector.

### 18.8 Amendments to §5 and §6

**§5's build order is unchanged — R19 reorders nothing — but it supplies the missing precondition for
step 9.** §5 step 9 reads *"── only here ── configuration experiments"*. R19 shows that step 9 is not
merely gated on steps 1–8 being done; it is gated on a **schema decision that has to be made before
the data accumulates, not after**. Nothing in steps 1–8 records the eligible set, so completing all of
them still leaves step 9 untrainable. ⭐ **Add the dispatch record as step 6b**, alongside step 6's
telemetry, and note the asymmetry in the same breath: telemetry can be backfilled, the counterfactual
cannot.

⚠ **This also sharpens the R16 outside lane's step-6 challenge (§17.6), which is still unresolved.**
That lane argued step 6 sits too late — observability adoption 89% against offline evals 52.4%,
n = 1,340 — and named a possible internal contradiction between step 3 (terminal verdict from
append-only history) and step 6 (the telemetry that fills it). R19 arrives from inside and pushes the
same way: *"the optimiser is not the missing piece — the logging schema is."* **Two independent passes
now say step 6 is misplaced, and §5 still does not carry either.** Row 33 covers the first; this is a
second voice for it, from a different direction.

**§6 changes in one row.** The deferral table says a dynamic team-selection LLM unlocks at *"≥200
adjudicated examples plus static misrouting ≥10%"*. Per §18.3 item 3 that condition is **not merely far
away, it is unreachable as written**, because the population it counts is not recorded. Restate it as a
**schema precondition followed by a count**: *the dispatch record with `eligible[]` in place, then ≥200
adjudicated examples.* ⭐ **A count-based unlock condition on an unrecorded population is a gate that
cannot pass — the class §15.1, §17.3 and §18.2 have now found in four separate instruments.**

**And one thing §6 gains rather than loses.** Its *"never optimise: retry caps, gate thresholds,
tenancy checks, timeout/concurrency limits, evaluator thresholds or corpus"* now has a fifth
independent arrival, from the dispatch side: R19's §7.4 insists **blast radius is a multiplier on the
failure term, not an additive cost** — *"removing an empty Eclipse filter and issuing `CREATE OR
REPLACE` against a shared Snowflake view are not the same decision at any budget"* — and that
**escalation must carry `was_correct`**, or the maximum-scoring policy is *escalate everything*: the
retired agent's 233 diagnoses / 234 escalations / 0 fixes. §15.5 item 2's *Oversight Has a Capacity*
result, corroborated independently by R17 (§16.9), is the same conclusion from outside — escalating
everything is strictly worse than the optimum. **Four sources, one rule, and it is already in §6.**

### 18.9 What changes in this repo — additions to §8

| # | Change | State |
|---:|---|---|
| 36 | ⭐ **Build the dispatch record** — `factory/dispatch_record.py`, written **at dispatch** and closed at terminal state, with `eligible[]` mandatory (§5.2, §18.5b). The one field that cannot be backfilled | not started — **R19's own #1, and the precondition for §6's selector row and §5 step 9** |
| 37 | **Fix `g_version_hash_is_complete` to compare two constructed specs instead of grepping `blueprint.py`** (§18.2) | not started — ⛔ **the code defect is already fixed and the gate can see neither the defect nor the fix.** Twice broken for the same reason (§15.1) |
| 38 | **Propagate the `6 of 15` correction out of §15.1 into the documents that seed prompts** — `docs/specs/product-end-state.md:66` first, then the nine other occurrences (§18.1b) | not started — **six days un-propagated, and it re-entered the programme through R19's brief** |
| 39 | **Un-freeze the guidance paragraph in `factory/synthesis.py:84–86`**, which asserts F7 and names R5/R6 in every prompt regardless of the actual gap (§18.1a) | not started — the generator computes the id list and hard-codes the reasoning around it |
| 40 | **Extend `presets.py` to 16 types — 2 new presets, 7 refusal rows with named unblocking conditions, 2 out of scope, 5 existing** (§18.5d). A refusal row is the honest content when the verifier is `UNBUILT` and the consumer layer is production | not started — ⚠ **filling it with eleven presets instead is the anti-pattern R19 names** |
| 41 | **Read `g_succeeds_more_than_fails` and say what would make `succeeds` stop reporting `UNMEASURABLE`** (§18.7) | not started — **it gates R19's entire staging argument and R19 filed it unread.** One function |
| 42 | **Scope discovery as a separate, cheap, human-gated stage before team formation** — `declared_scope` / `discovered_scope` recorded as a pair (§18.5a) | not started — **this is R3's `scope_hash` from 2026-08-21, unabsorbed since, now with ticket evidence behind it** |
| 43 | **Write the blind-first protocol into `docs/research/README.md`**: the brief-writer and the answerer must be different sessions (§18.1d) | not started — cheap, and it is the only control that makes a `STRUCTURE_CRITIQUE` label mean anything |

### 18.10 Additions to §9 — follow-ups

⚠ Per §16.14 item 9, R19 ran as an in-repo session and **there is no thread to return to**. Two of the
three below are therefore probes, not questions — answered by running something.

10. **Probe, one command:** `mcp__ccx__cce_memory_search` against a known ticket key, to settle whether
    Zeus Memory is typed enough to be a selector input (§18.7). R19 filed it `NOT-DETERMINABLE` without
    trying.
11. **Probe, one hour:** a timestamped phase log on the next manual Snowflake TEST deploy. It is the
    missing denominator under R19 §4.2's third-ranked automation, and without it that ranking is
    `ASSUMED` on both sides of the ratio (§18.7).
12. **New brief, and it is the one that matters:** a genuinely blind second pass on the taxonomy, by a
    session that has never opened `factory/presets.py`, to answer *"are the five existing presets the
    right five?"* — the question R19 marked `ASSUMED` and could not answer about itself (§18.1d). ⚠ It
    must be dispatched by a different session than the one that writes its brief, or it reproduces
    R19's disclosure verbatim.

### 18.11 How this reconciliation ran — both halves, and what it did not do

**Read R19 in full — all 40,190 bytes — and its brief, and `docs/findings.md` F1–F10, before writing
anything.** Then re-ran every internal figure R19 states (the table in §18's preamble), opened
`factory/blueprint.py` at `HEAD` *and* in the working tree, read `g_version_hash_is_complete` and
`g_work_is_attributable` in source, and verified R19's three load-bearing wiki citations —
`eclipse-azure-deployment.md:16` and `:150`, `tickets/gep/GP-311.md:16` — in the wiki itself.

**Stronger than an outside reader on the mechanical half**, in the way §17.12 describes: an outside
pass cannot run the `TeamSpec` discriminating test against two versions of the file and discover that
the defect was fixed between the answer and the reconciliation, and cannot discover that `.sessions`
exists one directory over from where R19 looked. §18.1b, §18.2 and §18.6 are all of that kind.

⚠ **Weaker, and in the same specific way every reconciliation here has been.** This pass read this
document's conclusions before deciding what in R19 mattered, from inside the estate whose record it is
grading. §18.5's ⭐ marks are judgement, and it is the same judgement that produced the record.

⛔ **Two things it did not do, stated rather than left to be found.**

1. **It wrote §18 for the newest answer while §17.11 rows 29, 30 and 34 are still `not started`.**
   R14 (1,389 lines, filed 08-23) and R18 (614 lines, filed 08-23) still have no section, and the eval
   corpus is still one file. ⭐ **That is §17.4's shape — *the oldest conclusion in the corpus filed as
   the newest* — repeating inside the mechanism built to stop it**, because the instrument that summons
   a reconciliation is `unsynthesised()`, which goes green on a mention and had nothing to say about
   R14 or R18. §17.10 and F75 already ruled that absorption is not mechanically detectable; this is
   what that ruling costs in practice, on the very next pass.
2. **It did not verify R19's taxonomy against the ticket corpus.** The 16 types rest on a 59-page sweep
   this pass did not repeat; the `seen_in` ids are ✓ for the four tickets read here and `REPORTED` for
   the rest. **Treat every ticket id inherited into §18 as `REPORTED` until someone opens the page** —
   the standing rule from §17.12, which exists because five ledger citations held in substance and
   drifted in line number.

<!-- BANKED-ANSWERS: generated by factory.synthesis.bank(). Do not hand-edit. -->
```
R1  6404ae91d168
R2  bc0f48476055
R3  f8217d02a4eb
R4  4723e25d3eed
R5  1a623bcc4203
R6  6d2520369374
R7  6d73bf0f4c14
R8  feb821eb0701
R10  29d6c3a4f512
R11  93a4f1875d89
R12  7906ba4b4ea7
R13  0283dbe74349
R14  27fee1bb1054
R15  90f5899836f9
R16  0a8646a714dc
R17  636fec7aac8a
R18  68ab86307d87
R19  38d6ffb22247
```
<!-- /BANKED-ANSWERS -->
