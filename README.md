<div align="center">

# Agent Factory

**A factory for *operatives*, not chat sessions.**

*An engineering platform for measurable, evidence-backed agent work — and the command surface an
operator drives it from.*

`main` @ `7b19baf` · measured 2026-09-02

[The hybrid](#part-ii--the-hybrid) · [Agent vs Operative](#part-iii--what-is-an-ai-agent-vs-an-ai-operative) · [Architecture](#part-iv--architecture) · [Status](#part-vi--status-measured-not-asserted) · [Quickstart](#part-viii--quickstart)

</div>

---

## Part 0 — The one sentence, and the one honest fact

Everything in this repository exists to make a single claim testable:

> **A team of agents did the work, and we can prove it — or we can prove we could not tell.**

That second clause is not a hedge. It is the product. Most agent platforms can tell you an agent
*ran*. This one is built to tell you whether the thing that measured it could have registered a
failure, and to refuse the word "pass" when it could not.

And the honest fact, stated before anything else on this page, because every claim below should be
read against it:

> ⛔ **The instruments are real. The subject has not yet been measured.**
> `.data/runs.jsonl` holds **10 rows and 0 `PASS`**. All **7** `agent_returned` events carry
> `dry_run=True`. **No agent has ever completed a real, non-dry-run run in this system.**

```bash
python -c "import json;r=[json.loads(l) for l in open('.data/runs.jsonl',encoding='utf-8')];print(len(r),[x.get('outcome') for x in r])"
# 10 ['FINISHED','FINISHED','FINISHED','FAIL','UNMEASURABLE','UNMEASURABLE','UNMEASURABLE','UNMEASURABLE','UNMEASURABLE','UNMEASURABLE']
python -c "import json;e=[json.loads(l) for l in open('.data/events.jsonl',encoding='utf-8')];a=[x for x in e if x.get('kind')=='agent_returned'];print(len(e),len(a),sorted({str(x.get('dry_run')) for x in a}))"
# 61 7 ['True']
```

This README states that up front deliberately. A platform whose whole thesis is *"do not confuse a
declaration with a mechanism"* would be a poor advertisement for itself if its own front page did.

---

## Part I — Why this shape

This estate has twice built mechanisms that **acted** without anything measuring whether the action
helped.

| Prior system | What it did | What measured it |
|---|---|---|
| A retired diagnostic agent | **233 diagnoses, 234 escalations, 0 fixes, over 81 days** | Nothing |
| A retired improvement loop | Ran **965 times**, recorded its own **1.6% success rate**, never adjusted | It measured itself and could not act on the measurement |

Both were capable. Neither was measurable. Capability without measurement is the failure mode this
repository is organised against, and it is the reason the build order is inverted relative to almost
every other agent framework: **the grader is built before the thing being graded.**

```
contract.py   what "done" means, and what "I could not tell" means   ← everything depends on this
evals.py      can the contract actually fail?  (negative control)
tasks.py      what a team is doing, append-only, evidence-gated
blueprint.py  the config that IS the version
deploy.py     put an agent in a repo, bounded
metrics.py    every activity metric paired with an outcome metric
```

> **Do not add a team, an optimizer or a UI until the negative-control gate passes.**
> A green suite from an instrument that cannot fail is the 965-run loop again, wearing a test badge.

⚠ **And the gate itself is weaker than its reputation.** `tests/test_eval_can_fail.py` builds a
synthetic three-assertion contract over a hardcoded dict and **never loads the corpus** — it proves
the *mutation harness* works, nothing more. The real evidence that the connector contract can fail is
`tests/test_connector_contract.py`, which calibrates all twelve assertions and enforces the property
with `test_every_assertion_has_been_proved_able_to_fail`. Cite that file, not the other one, when the
question is whether the instrument can see. (Finding `F76`.)

---

## Part II — The hybrid

### II.1 The claim

The differentiator is **not one idea**. Every individual strand below exists somewhere in the
literature or in someone else's product. What does not exist elsewhere — and what this repository is
composing — is the **join**: a system where a configuration's identity, the conditions it was graded
under, the evidence that closed its tasks, the surface it was allowed to run on, and the expiry of
its certification are all **one connected record**, and where each of them independently has the
authority to refuse.

Most agent platforms are assembled from *capability* primitives: a planner, a memory, a tool router,
a topology. This one is assembled from **refusal** primitives. Each strand's contribution is a
specific thing the system will decline to do.

> ⭐ **The thesis in one line:** other platforms can build a team. This one is built so that a team
> *cannot* be certified for work it was never measured doing — and so the system says so out loud
> rather than reporting a zero.

### II.2 The eleven strands

Maturity uses the repo's own ladder — `BUILT` (running and tested here) · `PARTIAL` (a mechanism
exists under another name) · `DESIGNED` (a spec or schema exists, no code) · `RESEARCH` (named, not
designed). Nothing below is upgraded for being a good idea.

| # | Strand | Borrowed from | What it refuses | Where it lives | Maturity |
|---|---|---|---|---|---|
| **H1** | **Five-verdict conformance lattice** | ISO/IEC 9646 conformance testing; TTCN-3 / ITU-T Z.140 §24.2 | Refuses to let *"I could not look"* be recorded as *"I looked and it was fine."* `ERROR` dominates `FAIL` — once the apparatus breaks, the observed failure is no longer trustworthy | `factory/contract.py` | **BUILT** |
| **H2** | **Negative-control calibration** | Experimental method — the known-bad specimen | Refuses an assertion that has never been *proved able to fail*. A suite that has never gone red is not evidence | `factory/calibration.py`, `tests/test_connector_contract.py` | **BUILT** |
| **H3** | **Config-as-version-hash** | Reproducible builds / content addressing | Refuses to let a certification transfer across a silent config edit. Change model, effort, prompt, tools, prohibition or repo, and it is a **different agent** whose guarantee nobody re-checked | `factory/blueprint.py` | **BUILT** |
| **H4** | **Evidence-gated close, enforced in the store** | Clinical-trial endpoint discipline; the estate's own consumer-layer rule | Refuses to close a task without `TARGET` / `CONSUMER` / `REGRESSION` / `ROLLBACK` evidence. The refusal lives in the **store**, not in a convention someone can forget | `factory/tasks.py`, `factory/evidence.py` | **BUILT** |
| **H5** | **Counterfactual maturity ladder** | Software assurance cases | Refuses a claim that outruns its proof. `EXERCISED` must cite the evidence of running; `IMPLEMENTED_NOT_EXERCISED` must cite `module:line`; anything lower is forced to `SIMULATED` *whatever the authored file said* — enforced by a dataclass that **raises** | `factory/assertions.py` | **BUILT** (one artifact type) |
| **H6** | **Derived boards, never hand-maintained state** | Event sourcing; the derived-view principle | Refuses a `PROJECT_STATE.yaml` / `PROGRESS.yaml`. `roadmap.py` has no task list *by design*; the board is derived from gate verdicts so it cannot drift from what it reports | `factory/roadmap.py`, `factory/board.py` | **BUILT** |
| **H7** | **Absence-preserving readiness** | The estate's `ZERO` / `NOT-RECORDED` / `NOT-VISIBLE` / `NOT-RETAINED` rule | Refuses to render a missing measurement as `0%`. A goal with no measurable gate reports `NOT-MEASURED` | `factory/readiness.py` (30 gates), `factory/goals.py` | **BUILT** |
| **H8** | **File-locality lane isolation with real locks** | Git worktrees; `O_CREAT\|O_EXCL` mutual exclusion | Refuses two writers on one mutable resource. Lanes group by **file locality, not the dependency graph**; liveness is checked against the **process table**, not file existence | `factory/claims.py`, `factory/worktrees.py`, `factory/lanes.py`, `factory/sessions.py` | **BUILT** |
| **H9** | **Execution-surface routing** | `.agent-platform` execution policy; Claude Code's own surfaces (local / `--spawn worktree` / cloud) | Refuses to start work on a surface that cannot satisfy its declared needs, and refuses parallelism unless both tasks are read-only, hold separate trees, or provably disjoint write-sets | *Half built:* the locks and lanes exist; the `execution:` declaration does not | **PARTIAL** |
| **H10** | **Evidence-envelope certification (the capability record)** | A2A Agent Cards for *discovery*; SLSA/in-toto attestations for *provenance*; this estate for the *envelope* | Refuses a capability claim used outside the conditions it was measured in — a claim carries `conditions`, `evidence_count`, regression history, cost, latency and a **`valid_until`** after which it expires | `factory/registry.py` today (`unproven()` returns **4** workflows never run on real work); the envelope fields are designed, not built | **DESIGNED** |
| **H11** | **Goal-aware adaptive orchestration over canonical work** | Classical scheduling; the deadline pack's `ExecutionMandate` | Refuses to become a second scheduler. Policy recomputes READY / blocked / conflicting after every event — but **may not silently weaken a success criterion** to make a deadline | `factory/work.py`, `factory/coordination.py`, `factory/switchboard_p1.py`; the *pump* that acts on the policy is the open seam | **PARTIAL** |

Regenerate the two counts embedded above:

```bash
python -c "from factory.readiness import GATES; print(len(GATES))"          # 30
python -c "from factory import registry; print(len(registry.unproven()))"   # 4
```

### II.3 Why the composition is the thing

Take any strand alone and it is unremarkable. Take them pairwise and something appears that none of
them has on its own:

```
        H3 config-as-version ──────┐
                                   ├──► a certification is bound to an exact configuration…
        H10 evidence envelope ─────┘         …and to the conditions it was graded under
                                                              │
        H2 negative control ───────────────────────────────►  …by an instrument proved able to fail
                                                              │
        H4 evidence-gated close ───────────────────────────►  …over tasks that could not close unproven
                                                              │
        H1 five verdicts ──────────────────────────────────►  …with "could not tell" preserved, not rounded
                                                              │
                                                              ▼
                                            a claim that expires, names its envelope,
                                            and cannot be inherited by an edited agent
```

That object — a capability claim that **knows what would invalidate it** — is what a client can
actually hold. It is also what makes teams composable without lying: an operative certified on
`connector-e2e` under `sonnet/medium` against a 2-tenant corpus does not silently become an
operative certified on Power BI models under `opus/high`, because five separate mechanisms each
independently break that inheritance.

⭐ **This is the "others cannot" argument, and it is a structural one, not a feature list.** A
platform that adds certification *after* it has a team must retrofit identity, envelope and expiry
onto records that were never built to carry them. This estate built the refusals first and has not
yet built the team. That ordering is expensive and it is the entire bet.

### II.4 Strands deliberately **not** taken

Refusals matter as much as adoptions, and each of these is on file with its reason.

| Not adopted | Why |
|---|---|
| **Org-IR / "organization compiler" as a novelty category** | Falsified before it was proposed here. Organisation-oriented MAS already has a metamodel (Moise+), a runtime (JaCaMo) and a textbook; the category name is taken twice in 2026, and **IMACS** (`arXiv:2607.25446`) *is* the organizational-compiler thesis. Mine the mechanisms; do not inherit the programme. (`.agent-platform/RECONCILIATION.md` §1.1) |
| **A mandatory Agent → Team → Manager → Master → Army hierarchy** | One fixed ladder forecloses every topology a tournament would need to compare. Topology should be data, and hierarchy a UI lens — not a runtime invariant. (`high_leverage_concepts.md` HL-09) |
| **A 22-primitive communication protocol** | A second topology is unlocked by *a second team that needs to talk to the first*. There is not yet a first. `factory/bus.py` carries **5** message kinds and raises `BusError` on anything else |
| **Heartbeats** | *Alive ≠ working.* `factory/claims.py:10-20` uses commits-ahead and dirty state as progress instead |
| **Generic auto-retry** | This estate has already watched permanent failures re-dispatched endlessly. Retry only when a deterministic classifier says *transient* and an attempt budget remains (`AttemptLedger`, max 2, dry runs excluded) |
| **Evolution chamber / optimizer** | Unlocked by a working eval — the fitness function *is* the eval score. With one connector scored, an optimizer would optimise a fixture |
| **Automatic scope degradation under deadline pressure** | Adaptation may reorder, pause and deprioritise. Dropping a required node needs a **human-authored decision with provenance**. A deadline changes scheduling urgency; it does not change what `PASS` means |

---

## Part III — What is an AI Agent vs an AI Operative

*This is the design distinction the platform is built around.*

### III.1 The short version

| | **AI Agent** | **AI Operative** |
|---|---|---|
| **What it is** | A capable process. A model, a prompt, some tools, a loop | A **certified, versioned, mandated unit of work** with an identity, an authority envelope, a measured capability record, and an expiry |
| **Identity** | A name someone chose. "The reviewer agent" | A **hash of its configuration.** Change model, effort, prompt, tools, prohibition or target repo and it is a *different operative* |
| **Authority** | Whatever its tools happen to permit | An explicit **mandate**: what it may touch, what it must not do, which surface it may run on, what budget it holds, which decisions escalate |
| **Competence** | Asserted in a description | **Measured**, with the conditions attached — task family, evidence count, success and regression history, cost, latency |
| **Trust** | Permanent until someone notices otherwise | **Expiring.** A capability record carries `valid_until`; a closed window cannot be reported as coverage |
| **Failure** | Reported as an error, or not at all | Enters a lattice: `PASS` / `FAIL` / `UNMEASURABLE` / `ERROR` / `NOT_RUN`. *"I could not look"* is never a pass |
| **Output** | A result | A result **plus the evidence that closed it**, plus what remained unmeasured |
| **What it is to the system** | A caller | A **record** — durable, addressable, auditable, and refusable |

> The distinction in one sentence:
> **An agent is something you run. An operative is something you can certify, deploy, revoke and be
> accountable for.**

An agent is a *capability*. An operative is a *capability under contract*. Every organisation that
has ever fielded people into consequential work made exactly this move — the word is borrowed
deliberately, because the properties borrowed with it are the right ones: an operative has a
**designation**, a **remit**, a **clearance**, a **record**, and a **review date**.

### III.2 The seven properties of an operative

An agent becomes an operative when — and only when — it carries all seven.

```
                        ┌─────────────────────────────────────────┐
                        │            AI OPERATIVE                 │
                        ├─────────────────────────────────────────┤
   1  DESIGNATION  ────►│ version = sha256(config)   ← not a name  │
   2  REMIT        ────►│ mandate: scope, deadline, budget, mode   │
   3  PROHIBITION  ────►│ an explicit "must not", inside the hash  │
   4  CLEARANCE    ────►│ execution surface + isolation tier       │
   5  RECORD       ────►│ capability record: conditions + evidence │
   6  EXPIRY       ────►│ valid_until — trust that decays          │
   7  ACCOUNT      ────►│ evidence-gated close; five verdicts      │
                        └─────────────────────────────────────────┘
                                          │
                    remove any one and it is an agent again
```

**1 · Designation — identity is the configuration, not the label.**
`factory/blueprint.py` states it in its own docstring: *"An agent is not a name — it is a (prompt,
model, effort, tools, retry policy) tuple."* The version is a hash of the config, so a silent upgrade
cannot inherit a guarantee nobody re-checked.

⚠ **And this was wrong once, in the dangerous direction.** The team hash enumerated four keys by
hand, so `repo` and the team-level `prohibition` sat *outside* it — meaning a team certified against
one repository under *"must not deploy to production"* kept the **identical version** when repointed
at another repo with the prohibition deleted. Those are exactly the two edits that change blast
radius. It is now a **deny-list, not an allow-list**: a new field is identity by default and must be
argued *out*.

**2 · Remit — the mandate is separate from the success contract.**
Deadline, budget, authority and autonomy mode live in an `ExecutionMandate`. Success lives on the
task and its evals. This separation is load-bearing:

```yaml
execution_mandate:
  goal_id: marketing-meeting-ready
  target_work_id: marketing-001-meeting-ready
  deadline: 2026-09-02T12:00:00-07:00
  mode: GUARDED            # MANUAL | GUARDED | AUTO
  max_parallel: 3
  run_mode: CRITICAL_PATH
  scope_profile: deadline_p0
```

> **A deadline changes scheduling urgency. It does not change what `PASS` means.**
> Put the deadline inside the success contract and you have built a system that passes itself when
> it runs out of time.

**3 · Prohibition — every operative carries an explicit "must not", and it is part of its identity.**
`AgentSpec.prohibition` is a first-class field inside the version hash. This is the difference
between a request and a control: *"do not touch prod"* in a prompt is a request; an operative whose
identity changes the moment that clause is deleted is a control.

**4 · Clearance — the surface is chosen from what the work declares, not from what is convenient.**
The declaration (`DESIGNED`; the collision half is `BUILT`):

```yaml
execution:
  preferred_surface: remote_control | cloud_web | either
  isolation: worktree | branch | read_only | serialized
  local_dependencies: []
  required_secrets: []
  required_mcp: []
  can_run_parallel: true
  writes: []
  gate_before_merge: true
```

The load-bearing clause is the collision rule, not the routing: **two operatives may run at once only
if both are read-only, or they hold separate worktrees, or a deterministic lock proves their mutable
resources are disjoint.** Clauses two and three are already built (`worktrees.py`, `claims.py`), and
`lanes.py` independently arrived at grouping by file locality rather than by the dependency graph.

⛔ **The open question is who writes `writes:`.** A hand-typed path list that nothing checks is the
defect family this estate has now recorded four times — a spec field nothing reads. Deriving it is
the hard half, and the same hard half as declared scope.

**5 · Record — competence is a measurement with its conditions attached.**
Today `factory/registry.py` versions a workflow by the content hash of its `SKILL.md`, on the
argument that a skill edited between two runs *is a different workflow* and its certification must
not silently transfer. The capability record generalises that from the **artifact** to the
**conditions** — the part a hash cannot express:

```yaml
capability_record:
  operative: connector-e2e@a41f0c9b3d22     # designation, not name
  task_family: connector-end-to-end
  conditions:                                # ⭐ the envelope — the differentiated layer
    corpus: windsorai-2026-08-20
    tenants_declared: 2
    surface: local/worktree
    model_binding: sonnet@medium
  evidence_count: 12
  evidence_refs: [docs/evidence/phase-a-windsorai.md]
  success_history: {pass: 12, fail: 0, regressions: 0}
  cost_usd: MEASURED
  latency_s: MEASURED
  valid_from: 2026-08-20
  valid_until: 2026-11-20                    # ⭐ trust decays
  limits_unmeasured:                         # ⭐ refuses to imply assurance outside the envelope
    - "48 connectors never scored"
    - "no live run; replayed against a recorded corpus"
```

⭐ **Do not reinvent discovery.** A2A Agent Cards already standardise identity, skills and security
requirements. The differentiated layer here is the **evidence envelope** — `conditions`,
`limits_unmeasured` and `valid_until` — not the vocabulary.

**6 · Expiry — a "best operative" is not a timeless asset.**
The sharpest open contradiction in the corpus (`CN-29`) is whether an organisational design is
durable or expires with its model binding. Current evidence says winning placement can **flip across
model families**. So a capability record without a validity window is a claim that will eventually be
false and will never announce it. An operative whose window has closed **cannot be reported as
coverage** — that assertion *is* the experiment.

**7 · Account — the operative cannot close its own work on its own word.**
The refusal lives in the store, not in a convention: `factory/tasks.py` raises `EvidenceRequired`. And
the grader is a separate identity (`evaluator_service/`), because a system that scores itself has
measured nothing. `factory/certify.py` says so about its own `--calibrate` flag in its docstring —
*"worthless as evidence that an agent did not grade itself."*

⚠ **Honest state of that last one:** grader separation is *attributed*, not yet *enforced*. It is a
`EXTEND` row, not a `KEEP` row.

### III.3 Operatives, not personalities

There is a large body of "agent persona" design that assigns traits — *conscientious*, *skeptical*,
*curious* — and hopes the model behaves accordingly. This design rejects trait language at the
configuration layer and keeps it only as a **label over compiled behaviour**.

```
    ✗  conscientiousness: high              ← a description; nothing can check it

    ✓  pre_work_requirement_check: required ← compiled behaviour; each clause is observable
       max_unresolved_assumptions: 2
       post_change_validation: required
       self_review_passes: 2
```

The archetype names still earn their place — **Scout, Surgeon, Architect, Skeptic, Auditor,
Firefighter, Guardian, Integrator, Maintainer, Investigator** — but as *presets over measurable
configuration deltas*, each of which must eventually answer four questions before it is more than
vocabulary:

1. what configuration deltas define it;
2. which mission classes it claims advantage on;
3. what measurable advantage is expected;
4. **whether it adds anything beyond prompt wording** — the question that retires most archetypes.

`factory/presets.py` already enforces the *shape* of this discipline for real ticket types: a preset
never names a model without a `model_why` and an **escalation trigger** naming the condition under
which the choice is wrong; and it separates `WIRED` / `AVAILABLE` / `UNBUILT` verifier states,
because *"a preset naming a verifier is a claim that one applies, not that one has been wired."*

> ⚠ **Basis marker on this whole section.** Properties 1–4 and 7 are `BUILT` or `PARTIAL` and cite
> running code. Properties 5 and 6 — the capability record and its expiry — are `DESIGNED`. And they
> are gated: with **0 `PASS`** in the run ledger there is nothing certified to describe. The
> operative model is the target the architecture is shaped toward, not a claim about today.

---

## Part IV — Architecture

### IV.1 Canonical runtime model

One rule governs the whole design: **there is exactly one source of truth, and every surface is a
projection of it.**

```
        Mission Preset  +  Execution Preset/Team  +  Operator inputs
                                   │
                                   ▼
                       Mission Preset Adapter          ← a compiler, not a database
                                   │
                                   ▼
        ╔══════════════════════════════════════════════════════════╗
        ║   CANONICAL:  TaskStore work + dependency events         ║
        ║   append-only · evidence-gated close · never rewritten   ║
        ╚══════════════════════════════════════════════════════════╝
                                   │
        ┌──────────────┬───────────┴────────┬──────────────────┐
        ▼              ▼                    ▼                  ▼
   readiness /    claims / sessions    guarded start /     evidence +
   work           (liveness via the    deploy              artifacts
   projection     process table)       primitives
        │              │                    │                  │
        └──────────────┴────────┬───────────┴──────────────────┘
                                ▼
                    Switchboard  — projection + action surface
                    ⛔ never a second source of truth
```

**Non-negotiables that fall out of this:**

- no second task system;
- no second mission database;
- no second scheduler;
- no `PROJECT_STATE.yaml` / `PROGRESS.yaml` — those states are already *derived by code*;
- no number is ever **first stated** on a UI surface.

### IV.2 The open seam — policy decides, but nothing acts

This is the single most valuable missing piece in the platform today, and it is narrow:

> The UI and the policy can decide that work **may** start. **No autonomous execution pump acts on
> that decision.** The P1 Switchboard's own UI says it: *`GUARDED` decides; it does not act.*

The fix is a **deterministic planner separated from side effects** — not a workflow engine:

```python
plan = autonomy.plan(state, run_context)     # pure, explainable, no side effects
for action in plan.start_actions:
    existing_start_mechanism(action.work_id, mode="AUTO")
```

Every candidate returns `START` / `WAIT` / `BLOCKED` / `HUMAN_GATE` **with a reason**. No mysterious
scalar score — an unvalidated weighting rendered as a number is a fabricated measurement.

| Mode | Behaviour |
|---|---|
| `MANUAL` | Nothing starts automatically |
| `GUARDED` | Starts only where the guarded-start policy confirms a human is not substituting for a missing control |
| `AUTO` | Starts policy-allowed READY work — still bound by hard stops, claims, conflicts and concurrency |

**Hard stops, none of which any mode may cross:** operator pause · unresolved human gate · readiness
not an explicit `PASS` · declared conflict · live claim collision · concurrency limit · safety or
permission refusal · destructive or publication action without authority.

**Wakeups are deterministic, not a framework:** an explicit `RUN DAG` / `RUN CRITICAL PATH`; after an
approval or rejection is recorded; after a completion is observed; on `RESUME`. If completion cannot
trigger in-process, a small bounded poller is acceptable. *Do not introduce Prefect, Temporal or
Celery to close this seam.*

**Idempotency is a refusal, not a lock:** before starting, re-read canonical state and confirm still
READY, no live session attached, no new claim or conflict, concurrency available, run not paused. The
second attempt must **refuse**, not duplicate.

### IV.3 Two graph scales, deliberately not merged

| Graph | What it is | Used for |
|---|---|---|
| Readiness-gate graph (`board.DEPENDS`) | 30 gates across 5 phases | Platform-readiness diagnostic |
| Task/work dependency graph | Recovered from append-only task events | Mission execution and critical path |

`RUN DAG` starts every policy-allowed READY node in a run. `RUN CRITICAL PATH` starts only
policy-allowed READY **ancestors of the selected target**, and *deprioritises* everything else —
it never deletes it.

### IV.4 Operator command surface

Desired semantics, mapped onto whatever command names already exist rather than duplicating them:

| Command | Meaning |
|---|---|
| `/af-status` | Goal, target, READY/RUNNING/GATE/BLOCKED counts, critical path, active sessions, next action, fallbacks |
| `/af-run-dag <run>` | Activate the run; start all policy-allowed READY work within concurrency and conflict bounds |
| `/af-run-critical <target>` | Critical-path mode toward one target milestone |
| `/af-pause <run>` | Persist an operator pause — running work may finish, nothing new starts |
| `/af-resume <run>` | Clear the pause, recompute, start newly eligible work |
| `/af-phase <id>` | Manual recovery / targeted entry into a node. **It does not redefine dependencies** |
| `/af-retry <work-id>` | Re-attempt only after classifying the prior failure and checking the attempt budget |

> ⭐ **The ergonomic rule:** after an explicit `RUN` command, the operator should not have to type
> the next phase command when the next node is ungated and policy allows it. **The DAG runner owns
> continuation.**

---

## Part V — How to read any claim in this repository

### V.1 The five verdicts — never collapsed

Borrowed from `orchestrator/engine/gauge.py`, for the reason its docstring gives: *collapsing "I could
not look" into "I looked and it was fine" is how a measurement that never happened passes for one that
did.*

| Verdict | Means | Is it a pass? |
|---|---|---|
| `PASS` | Asserted, and the assertion held | **Yes** |
| `FAIL` | Asserted, and the assertion did not hold | No |
| `UNMEASURABLE` | The instrument declined to run — it *knows* it cannot look | **No — and this is the important one** |
| `ERROR` | The apparatus itself broke; this is not a measurement at all | No — and it **dominates `FAIL`** |
| `NOT_RUN` | Never attempted | No |

Not our invention: conformance testing standardised this in ISO/IEC 9646, and TTCN-3 carries it still
(ITU-T Z.140 §24.2) as a monotone lattice — `none < pass < inconc < fail < error`, where `inconc` is
our `UNMEASURABLE`. `ERROR` outranks `FAIL` because once the apparatus has broken we no longer know
the observed failure was real. See `factory/contract.py`.

**`UNMEASURABLE` is not a pass. A team holding an `UNMEASURABLE` is not certified.**

### V.2 The basis vocabulary — every figure carries one

`MEASURED` · `DERIVED` · `ASSUMED` · `PROXY` — and for absences, the four verdicts that must never
collapse into "zero":

| | Meaning |
|---|---|
| `ZERO` | It did not happen, **and the instrument was live and could have seen it** |
| `NOT-RECORDED` | It may have happened; nothing wrote it down |
| `NOT-VISIBLE` | The instrument cannot see this class of event at all |
| `NOT-RETAINED` | It was recorded and has since aged out |

> ⭐ **A zero from an instrument you have not proved can still see is not a measurement.**

### V.3 Counts carry their regeneration command

Every count on this page is followed by, or accompanied by, the command that produced it. This is a
hard rule and it exists because hand-maintained numbers re-rot invisibly — the number still looks
authoritative. The corpus index in this very repository claimed 112 capability rows on 2026-09-02 and
measured **124** on the same day after a delta pass. That is the rule earning its keep.

---

## Part VI — Status (measured, not asserted)

**Phase A: the contract exists, is calibrated, and certifies the recorded run green — against one
connector.**

```bash
python -m factory.certify blueprints/windsorai_client_a.yaml --calibrate
# connector-e2e/windsorai@CLIENT-A: PASS (PASS=12)
#   scored against corpus windsorai-2026-08-20 — REPLAYED, not a live measurement
```

⚠ **Read `PASS (PASS=12)` for exactly what it says.** It is a **replay** against **one** recorded
connector — not a live measurement and not a second subject. Every assertion has been shown able to
fail (`test_every_assertion_has_been_proved_able_to_fail`), but **sensitivity is not coverage**.
**48 connectors have never been scored.** See `docs/findings.d/F76`, which corrects the
widely-repeated claim that a one-file corpus means the instrument cannot fail — the real gap is
breadth, not sensitivity.

### VI.1 The ledgers

| Ledger | Size | Regenerate |
|---|---|---|
| Runs | **10 rows, 0 `PASS`** | `python -c "import json;print(len(open('.data/runs.jsonl',encoding='utf-8').readlines()))"` |
| Events | **61**, of which **7** `agent_returned`, all `dry_run=True` | `python -c "import json;print(len(open('.data/events.jsonl',encoding='utf-8').readlines()))"` |
| Task events | **273** | `python -c "print(len(open('.data/tasks.jsonl',encoding='utf-8').readlines()))"` |
| Eval corpus | **1 file** — `evals/corpus/windsorai-2026-08-20.json` | `ls evals/corpus/ \| wc -l` |
| Findings ledger | **34** | `ls docs/findings.d/*.md \| wc -l` |
| Readiness gates | **30** | `python -c "from factory.readiness import GATES; print(len(GATES))"` |
| Registry workflows never run on real work | **4** | `python -c "from factory import registry; print(len(registry.unproven()))"` |
| Runtime modules | **66 files, 22,817 lines** | `ls factory/*.py \| wc -l; cat factory/*.py \| wc -l` |

### VI.2 Capability distribution — the shape is the finding

Measured by parsing `docs/_index/current_vs_proposed.md`'s own tables:

```bash
python -c "rows=[c for c in ([x.strip() for x in l.strip().strip('|').split('|')] for l in open('docs/_index/current_vs_proposed.md',encoding='utf-8') if l.lstrip().startswith('|')) if len(c)==8 and c[0]!='Capability' and not c[0].startswith('---')]; print(len(rows))"
# 124
```

| Highest level reached | Reading |
|---|---|
| **Validated** | It ran here, on real state, and was observed |
| **Validated (partial)** | Usually replayed, or run against a fixture rather than a live subject |
| **Implemented, never exercised** | The code exists and is tested; nothing has run it on real work |
| **Partial** | A mechanism exists under a different name |
| **Specified / Designed only** | A contract, schema or design exists. Nothing is built |
| **Research only** | Named in a document. Not designed |

⭐ **The distribution is sharply bimodal, and that is the finding.**

- **Nearly everything validated is a measurement or a control** — the verdict lattice, negative
  controls, evidence classes, readiness gates, rendered validation, the findings ledger, the failure
  preflight, the publication boundary. This estate's built capability is *knowing whether something
  worked*.
- **Almost nothing about doing the work is validated.** The capability that would make all of it mean
  something — an operative completing a real run — has **never happened**.

### VI.3 The corpus behind the design

| Artifact | Size | What it is |
|---|---|---|
| `docs/_index/corpus_manifest.yaml` | **168** artifact records | Every inbound document, with provenance |
| `docs/_index/concept_index.yaml` | **101** concept ids | Named *and unnamed* ideas, with maturity and evidence |
| `docs/_index/contradictions.md` | **29** contradictions | Real disagreements, evidence on both sides, nothing resolved by fiat |
| `docs/_index/high_leverage_concepts.md` | 17 entries | Candidates ranked by value-to-cost, **nothing selected** |
| `docs/research/backlog.yaml` | **31** mission ids | Candidate research. ⛔ **Nothing dispatched** |
| `docs/raw_research/` | **13** extracted packs | Inbound research, unsealed and searchable |

```bash
grep -cE '^- id: ' docs/_index/corpus_manifest.yaml                          # 168
grep -oE '\bC-[A-Z]{2}-[0-9]{2}\b' docs/_index/concept_index.yaml | sort -u | wc -l   # 101
grep -c '^## CN-' docs/_index/contradictions.md                              # 29
grep -oE '\bRB-[0-9A-Z]{2,3}\b' docs/research/backlog.yaml | sort -u | wc -l # 31
ls -d docs/raw_research/*/ | wc -l                                           # 13
```

---

## Part VII — Repository map

```
factory/                 the runtime — 66 modules, 22,817 lines
├── contract.py          the five verdicts; what "done" and "I could not tell" mean
├── evals.py             can the contract fail?  the negative control
├── calibration.py       known-bad specimens per assertion
├── tasks.py             canonical append-only work; raises EvidenceRequired on close
├── evidence.py          TARGET / CONSUMER / REGRESSION / ROLLBACK classes
├── blueprint.py         AgentSpec / TeamSpec — the config that IS the version
├── presets.py           ticket type + size → starting configuration, with reasons
├── registry.py          (shape, layer) → workflow, versioned by SKILL.md hash; unproven()
├── assertions.py        the counterfactual maturity ladder — a dataclass that raises
├── readiness.py         30 gates across 5 phases; NOT-MEASURED is sayable
├── goals.py             validates gate grouping on import
├── board.py             derives the roadmap from gate verdicts
├── roadmap.py           has no task list, by design
├── work.py              readiness / operability projection
├── coordination.py      priority over downstream blockers and critical-path membership
├── claims.py            O_CREAT|O_EXCL locks verified against the process table
├── worktrees.py         per-write-task isolation
├── lanes.py             grouping by file locality, not the dependency graph
├── sessions.py          liveness from the process table, not file existence
├── deploy.py            bounded dispatch; AttemptLedger, max 2
├── launch.py            the supervised / guarded readiness boundary
├── switchboard*.py      projection + action surface (P1 validated)
├── runs.py / events.py  the ledgers; cost RECORDED / RECONSTRUCTED / NOT-RECORDED
├── certify.py           certification entry point
├── findings.py          reads docs/findings.d/ as data; by_lane() briefs an operative
└── …                    schedule, handoff, synthesis, client_review, case_study, …

evaluator_service/       the grader — a separate identity, on purpose
blueprints/              team specs (windsorai_client_a, orchestrator_team — built and rejected)
missions/                client-review-v1, delivery-001
evals/corpus/            the eval corpus, hash-verified on load via MANIFEST.sha256
docs/_index/             the corpus index — manifest, concepts, contradictions, capability matrix
docs/research/           backlog + dependency graph.  ⛔ nothing dispatched
docs/findings.d/         34 addressable findings; merges with the branch
docs/evidence/           per-gate evidence, including rendered-surface screenshots
docs/raw_research/       13 extracted inbound packs
.agent-platform/         an imported design pack + its reconciliation.  ⚠ NOT a source of truth
boot-prompts/            session handoffs — the router is boot-prompts/README.md
scripts/                 render checks, tracker, meeting_ready, corpus pinning
```

⚠ **`.agent-platform/bootstrap/` is a proposal from a stranger.** It was written without access to
this repository. Where it describes a subsystem, treat the description as a proposal — never as a
specification, and never as evidence the subsystem exists. `RECONCILIATION.md` and
`PACK_CONFORMANCE.md` beside it were written *here, from measurement*, and outrank it.

---

## Part VIII — Quickstart

```bash
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium            # the browser; pip cannot fetch it
pytest -q                                        # all four gates must pass
python -m factory.demo                           # end-to-end on a fake connector
```

`scripts/bootstrap.sh` runs all of the above.

⚠ **The browser step is a real step, not a nicety.** `pip install` provides the Playwright driver and
not a browser, so anything that validates a rendered page — and **no client-facing artifact is
certified without one** — fails without it. Check an environment before trusting it:

```bash
python scripts/meeting_ready.py --check-env      # names everything missing, in one message
```

Then the two things worth doing first:

```bash
python -m factory.certify blueprints/windsorai_client_a.yaml --calibrate   # the replay
python -c "from factory import registry; [print(w) for w in registry.unproven()]"  # what is uncertified
```

---

## Part IX — What is deliberately absent

Each of these is cheap to add *after* its precondition and expensive to unwind before it. This table
is a gate, not a wish list.

| Not here | Unlocked by |
|---|---|
| Optimizer | A working eval — the fitness function *is* the eval score |
| Agent Army / supervisor tiers | **One certified team**, plus evidence a tier helps |
| More than one comms topology | A second team that actually needs to talk to the first |
| Gym | The eval corpus plus a scoreboard — build the corpus first |
| Platform UI | Numbers worth looking at |
| Org-IR / organization compiler | A second workload proving presets cannot express the needed variation |
| Evolution / config search | Multiple real runs, ≥2 model families compared, a revalidation cadence, **and an evaluator the actor cannot rewrite** |
| Venture / commercial loop | One certified team that can repeatedly deliver |

⛔ **Zero teams are certified.** Every row above sits behind that.

---

## Part X — Roadmap

The order is evidence-driven; each stage's entry condition is the previous stage's output.

| Stage | What it proves | Entry condition |
|---|---|---|
| **1 · Prove the loop** | Multiple real runs across two workload classes; structured trajectories; evidence and artifact linkage; operator-safe auto-advance | **One real non-dry-run run.** This is the binding constraint on everything |
| **2 · Make configuration measurable** | Complete config identity dimensions; `TUNABLE` / `DECLARED` / `MEASURED` / `DERIVED` / `POLICY` field classes; same task across configurations; outcomes bound to exact bindings | Stage 1 |
| **3 · Richer teams** | Team presets as data; team-level evals; **failure-correlation metrics**; supervisors only where evidence shows benefit | Stage 2 |
| **4 · Organization representation** | Prior-art-aligned metamodel; topology as a configurable graph; typed authority boundaries | Only if real workloads outgrow presets |
| **5 · Adaptive organization search** | Replay with a separated evaluator; model-binding-aware archive; revalidation cadence; promotion gates | Stage 3 + metrics that resist gaming |
| **6 · Bounded self-maintenance** | observe → diagnose → propose → **validate externally** → quarantine/fallback → human-approved promotion | Never lets the actor rewrite its own grader |
| **7 · Certified capability routing** | The evidence envelope; A2A-aligned discovery; deterministic mission assembly from certified records | ≥2 real workloads |
| **8 · Bounded venture vertical** | Opportunity hypotheses → bounded validation → mission graph → customer signal → `KILL/HOLD/IMPROVE/SCALE` | One certified team. A *vertical over the same substrate*, never a second engine |

⭐ **The most valuable next action in this entire document is not on that table.** It is `RB-00C` /
`GAP-09`: fix one open finding (`F90` — make the controller **refuse** a ticket whose `repo` is not
this checkout, *then* thread the repository through) and complete **one real run**. That single
measurement converts roughly a dozen research questions into observations, and it is the gate under
Stage 1.

---

## Part XI — Provenance of this document

**Written 2026-09-02** against `agent-factory` @ `7b19baf` (`main`), by grounding in:

- `docs/raw_research/agent-factory-combined-execution-research-pack-v2-2026-09-02/` — extracted for
  this pass (28 files); its predecessor deadline pack extracted alongside it;
- `docs/_index/` — the corpus index (manifest, concepts, contradictions, capability matrix,
  high-leverage candidates);
- `.agent-platform/RECONCILIATION.md` and `PACK_CONFORMANCE.md` — the measured reconciliation of the
  imported design pack;
- the running code in `factory/`, and the four ledgers under `.data/`.

**Every count on this page was re-measured today**, and each carries the command that produced it.
None was inherited from a prior document.

### Limits of this README

- ⛔ It describes an architecture whose central subject — a real agent run — **has not happened**.
  Sections marked `BUILT` cite running code; sections marked `DESIGNED` are targets.
- ⚠ Part III properties **5 (Record)** and **6 (Expiry)** are designed, not built, and are gated
  behind the first real run. The operative model is where the architecture points, not where it is.
- ⚠ Grader separation (Part III·7) is **attributed, not enforced**.
- ⚠ Twelve figures embedded in two converted `.docx` sources were never extracted, so a capability
  expressed only in a diagram may still be missing from the corpus index (`GAP-01` residual).
- ⛔ Nothing in `docs/research/backlog.yaml` has been dispatched. Where this page names a research
  question, it is open.
