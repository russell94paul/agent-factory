# Agent Factory — research prompts, and a review of the brief that produced them

**Written 2026-08-20.** Three Deep Research prompts, ordered by dependency, plus the review that
reordered them. Paste each into ChatGPT Deep Research (or equivalent) **in order** — R1's answer
changes what R2 and R3 should ask.

> **The one-line finding:** the brief proposes roughly ten new subsystems. **Six of them are
> downstream of a single missing artifact — the eval harness — and cannot be specified, let alone
> built, until it exists.** R1 is about that artifact and nothing else.

---

## Part 0 — Review of the brain dump

### 0.1 ⛔ The sequencing objection, in this estate's own words

The brief asks to build an Agent Army, a Gym, an AgnosticOptimizer, a communication module with five
topologies, ten team types, a platform UI and a simulator. Four documents this estate already produced
say the opposite, and all four were measured rather than argued:

| Source | Measured finding |
|---|---|
| `docs/AUTORESEARCH_REVIEW.md` §9 | *"We are one phase earlier than the plan assumes… 59% of the connector fleet will not import, and the hard-gate set has no tenancy check."* |
| `docs/AUTORESEARCH_REVIEW.md` §3 | **An automated loop ran 965 times, recorded its own 1.6% success rate, and never adjusted.** |
| *Crucible* artifact | **0 of 7 crews have an eval.** *"No crew has finished one connector yet. Building the factory before that happens repeats the mistake that produced the retired agent."* |
| Retired `pipeline_agent` | **233 diagnoses → 234 escalations → 0 fixes, over 81 days.** |

**The brief is a bigger version of the thing that already failed here twice.** Not because the ideas
are wrong — most are good — but because every one of them is a mechanism that *acts*, and this estate
has now twice built mechanisms that acted without anything measuring whether the action helped.

### 0.2 ⭐ The reframe that collapses most of the brief

> **An optimizer is a search over configurations. A search needs a fitness function. The fitness
> function *is* the eval. So the AgnosticOptimizer is not a peer of the eval harness — it is what you
> get almost for free once the eval exists, and it is strictly impossible before.**

The same is true of five more items in the brief:

| Brief item | What it actually is, once you have an eval |
|---|---|
| **AgnosticOptimizer** | A search loop whose fitness function is the eval score |
| **Agentic Gym** | The eval corpus plus a scoreboard. Not a separate system |
| **Agent versioning** | Only meaningful if a version can be *re-certified* — i.e. re-run against the eval |
| **"Track all metrics to improve component by component"** | Per-component eval scores. Without them you are tracking activity, not improvement |
| **Team-selection agent** ("pick the right members for a task") | An optimizer over team composition — same fitness function, different search space |
| **"Iterate until optimal, then deploy"** | The stopping condition is an eval threshold. There is no "optimal" without one |

**Six brief items, one prerequisite.** This is why R1 is about the eval and nothing else.

### 0.3 What to cut, and why

| Item | Recommendation | Reason |
|---|---|---|
| **Agent Army (level 5)** | **Cut for now** | Crucible already asked whether levels 4–5 are *"real structure or ceremony"*. With zero certified teams, a five-level hierarchy is ceremony. Two levels — Agent, Team — until a third earns its existence with evidence |
| **Ten team types** | **Cut to one** | Crucible reduced 7 → 4 and called Debt/Draft *seats, not crews*. The brief expands to 10+, which moves backwards from your own analysis. Build the **Data Pipeline Team** — your stated priority — and let it prove the pattern |
| **Five communication topologies** | **Cut to one** | With one team you need exactly `Manager → Agent`. Every extra topology is a new seam, and **every measured failure in this estate was a seam failure** — nobody owned "did the deploy finish?", "who reads this output?" |
| **Agentic Gym as a separate system** | **Fold into the eval** | It is the eval corpus plus a scoreboard |
| **Brand video walkthrough** | **Last** | Genuinely valuable, genuinely last |
| **Platform UI** | **Keep, but thin** | One read-only view of eval scores and run history. Not a configuration studio — configuring a system nobody has certified optimises the wrong thing |

### 0.4 What is missing from the brief and must be added

1. **⛔ A persisted spend ceiling and kill switch per optimizer run.** The brief says sandboxes for
   safety — correct, and insufficient. The measured incident was an uncapped watchdog re-dispatching
   a permanently-failing stage every 30 minutes overnight, and `_recovery_attempts` living in an
   **in-memory module-level dict** so every restart handed it a fresh budget. An optimizer that
   "iterates until optimal" with an in-memory counter is that incident with a bigger bill.
2. **A paired outcome metric for every activity metric.** Crucible: *"A self-improving loop pointed
   at the top two bars would have made this agent escalate faster and called it progress."* Any
   metric that can be gamed by doing more work must ship beside a metric that can only move when the
   work succeeded.
3. **The eval must live outside the agent's writable workspace.** An optimizer that can edit its own
   fitness function will reach 100%. `CONNECTOR_WORK_PLAN.md` already specifies a hidden verifier;
   make it a hard architectural boundary, not a convention.
4. **Promotion is a human act.** The optimizer proposes; a person promotes. The evaluator is a frozen,
   versioned artifact that the thing being evaluated cannot modify.
5. **Provenance on every agent-produced number.** `MEASURED / DERIVED / ASSUMED`, refusing to render
   when unmeasured — the discipline the published artifacts already use.
6. **Tenancy in the hard-gate set.** `AUTORESEARCH_REVIEW.md` §5 flags this as the missing gate. An
   agent fleet acting across CLIENT-A and CLIENT-B without a tenancy check in the gates is one bad filter
   away from a cross-client leak. This estate has already had one: a Windsor key returning every
   client's accounts.

### 0.5 The recommended shape

```
Phase A  Eval harness + GreenContract for ONE connector      ← R1 answers how
Phase B  Data Pipeline Team, 2 levels, 1 topology, pinned    ← the only team
Phase C  One connector end-to-end, certified by Phase A
Phase D  Optimizer over Phase B's config, fitness = Phase A  ← R3 answers how
Phase E  Second team type — chosen by what Phase C hurt
Phase F  Platform UI, Gym, versioning, army tiers
```

**Exit gate for A–C, unchanged from `CONNECTOR_WORK_PLAN.md`:** a version-locked line passes a private
eval, the exact built image passes viability checks, a second person approves the merge, and one
connector shows source → container → Prefect → warehouse GREEN with no required assertion left
unmeasured.

---

## R1 — The blocking prompt: how to build an eval harness for agentic pipeline work

**Run this first. Nothing else in the brief can be specified until it is answered.**

```
You are advising a small data-engineering company that is building an internal "agent factory" —
LLM agents organised into teams that migrate and maintain data connectors (vendor API → Azure
container → Prefect 3 → Snowflake → BI/chat surfaces).

CONTEXT — all figures below are measured from their production logs, not estimates:
- 49 connector modules; 1 proven end-to-end; 59% will not currently import.
- 976 connector run failures over 81 days. Top classes: container failed to start 389 (40%),
  SDK symbol missing 95 (10%), OAuth invalid_client 51, network timeout 47, vendor token 401 42.
  352 (36%) were never classified at all.
- A previous autonomous "fix-it" agent produced 233 diagnoses and 234 escalations and applied
  ZERO fixes in 81 days. Its error classifier was an 8-pattern substring allow-list that matched
  none of the five live failure classes.
- A separate automated loop ran 965 times, recorded its own 1.6% success rate, and never adjusted.
- They have 7 candidate agent teams and ZERO evals. Their own internal review calls the eval
  harness "the gap that blocks every other decision".
- They have a drafted "GreenContract": 11 assertions for one connector covering a session-id run
  marker, load fidelity, and source-vs-warehouse agreement.

THE QUESTION: How should they build the eval harness — and what does the current evidence say
actually works for evaluating multi-step, tool-using, side-effecting agents?

Address specifically, and separate ESTABLISHED PRACTICE from VENDOR CLAIM from OPEN RESEARCH:

1. DEFINING SUCCESS. For an agent whose output is a side effect (a deployed container, rows in a
   warehouse) rather than text, what is the state of the art in defining a pass? Compare
   assertion-based contracts, golden-output diffing, property-based checks, and LLM-as-judge —
   and say where LLM-as-judge is known to fail for side-effecting work.
2. NEGATIVE CONTROL. How do teams prove an eval can actually FAIL? What is the accepted practice
   for mutation-testing an eval suite so a green result means something? Give concrete protocols.
3. CORPUS CONSTRUCTION. Given 976 real failures of which 352 are unclassified, what is the
   defensible method for turning an incident log into an eval corpus? How many cases per failure
   class, how to avoid overfitting to the observed distribution, and how to handle the
   long tail nobody has characterised.
4. TAMPER RESISTANCE. Architecturally, how is an eval kept outside the reach of the agent it
   scores — including an agent with shell access and repo write permission? What has been shown
   to fail here?
5. NON-DETERMINISM. How do teams get a stable pass/fail from a stochastic agent? Sampling
   strategy, pass@k vs pass^k, variance budgets, and what sample size is defensible when each
   run costs real money and deploys real infrastructure.
6. COST. What does it cost, in engineering time and tokens, to stand up an eval harness of this
   kind? Cite real reported numbers where they exist and say clearly where none exist.
7. TOOLING. Evaluate the current options for this specific job — Inspect AI, OpenAI Evals,
   LangSmith, Braintrust, Promptfoo, DeepEval, and anything newer. For each: does it support
   side-effecting agents, external/hidden verifiers, and CI gating? Flag any that are primarily
   suited to text-output evaluation and would be a poor fit here.

CONSTRAINTS FOR YOUR ANSWER:
- Distinguish OBSERVED (published results, real post-mortems) from MARKETED (vendor docs).
- Where the honest answer is "nobody has published this", say so — do not fill the gap.
- Prefer sources with real deployment numbers over framework announcements.
- Give a concrete recommended sequence with a first week that produces something falsifiable.

DELIVERABLE: a recommended eval architecture, a build sequence with estimates, a tooling
recommendation with the rejected options and why, and an explicit list of what remains unknown.
```

---

## R2 — Multi-agent topology: what is actually proven

**Run after R1. Its answer determines whether teams-of-agents beat one strong agent at all.**

```
Same company and same measured context as before (49 connectors, 1 proven, 976 failures over
81 days, a prior autonomous agent with 233 diagnoses and 0 fixes, zero evals today).

They are proposing a four-level hierarchy — Agent → Team → Team Manager → Army — with five
communication topologies (agent↔agent, manager→agent, manager↔manager, army→managers,
army↔army), a "team selection" agent that picks members for a task, and a training environment.

THE QUESTION: What does the evidence actually show about when multi-agent structure beats a
single well-scoped agent, and what is the real failure mode of the structure they propose?

Address specifically:
1. THE BASELINE. For long-horizon software tasks with tool use, is there credible evidence that
   multi-agent decomposition outperforms one strong agent with good tools and a long context?
   Cite results with numbers. Include the negative results — cases where decomposition made
   things measurably worse, and why.
2. SEAM COST. Every handoff between agents is a place context is lost. Is there published work
   quantifying that loss? This company's measured failures were ALL seam failures — nobody owned
   "did the deploy finish?", "who reads this output?", "is staging the same as production?".
   What does that predict about adding four more handoff types?
3. TOPOLOGY. For the five communication patterns above, which are supported by evidence and which
   are speculative? Is there any demonstrated case for army↔army (peer supervisor) communication
   in a production engineering setting, as opposed to a research benchmark?
4. ROUTING. On the "team selection" agent — what is the state of the art in automated
   agent/team selection, and how does it compare to a static routing table for a domain with
   fewer than ten task types? Be concrete about the crossover point.
5. FRAMEWORKS. Assess LangGraph, CrewAI, AutoGen, OpenAI Swarm/Agents SDK, Claude Agent SDK and
   any newer entrant, specifically for: durable execution across hours, human approval gates
   mid-run, per-run cost ceilings, and running untrusted generated code in a sandbox. Which of
   these are production-grade for side-effecting infrastructure work versus demo-grade?
   Note: their existing 18-stage pipeline with budgets, models, gates and a DAG already works.
   Answer explicitly whether adopting a framework would replace something that already functions.
6. STATE AND VERSIONING. How do production systems version an agent configuration (prompt +
   model + tools + effort) and tie a run's outcome back to the exact version that produced it?
   What schema do they use, and what breaks at scale?
7. THE HIERARCHY QUESTION. Given zero certified teams today, is there any evidence-backed reason
   to build supervisor tiers now rather than after one team is proven? Argue both sides, then
   give a recommendation.

CONSTRAINTS: separate OBSERVED from MARKETED. Benchmark results that do not involve real side
effects should be labelled as such. Where a vendor claims production readiness without published
evidence, say so. Prefer post-mortems and engineering blogs with real numbers over launch posts.

DELIVERABLE: a recommended minimum topology for their first team, an explicit list of what to
defer and the evidence threshold that would justify each deferred item, and a framework
recommendation including "adopt nothing new" if that is the honest answer.
```

---

## R3 — The optimizer, the sandbox, and repo scaffolding

**Run last. Its shape depends on R1's fitness function and R2's topology.**

```
Same company, same measured context. Assume they now have (a) an eval harness that can score one
agent team on one connector migration, and (b) a minimum team topology.

They want an "AgnosticOptimizer" — a configurable component that can be pointed at any degrading
part of the system and search for a better configuration. Inspiration cited: karpathy/autoresearch.
Every optimizer iteration must run in a fresh sandbox for safety. They also want a repo skeleton
they can spin up quickly.

THE QUESTION: How should the optimizer be built, bounded, and scaffolded?

Address specifically:
1. SEARCH SPACE. For an agent configuration — prompt, model, reasoning effort, tool set, context
   layout, retry policy — what is the evidence on which dimensions actually move outcomes, and in
   what order of magnitude? Which are known to be low-yield and can be dropped from the search?
2. METHOD. Compare evolutionary/mutation search, Bayesian optimisation, bandit methods, and
   LLM-proposed mutations (an LLM suggesting the next configuration to try). Which suit a search
   where each evaluation costs minutes-to-hours and real money? Include sample-efficiency numbers.
3. OVERFITTING. With a small eval corpus, how do teams stop the optimizer overfitting to it?
   Held-out sets, rotating corpora, adversarial cases — what actually works, and what is the
   published evidence on optimizer-induced eval degradation (Goodhart in practice)?
4. BOUNDING. This is the highest-risk part. Their prior autonomous mechanism ran with an
   in-memory attempt counter that reset on every restart, and re-dispatched a permanently-failing
   stage every 30 minutes overnight. What are the established patterns for: a persisted spend
   ceiling that survives restarts, a hard iteration cap, a kill switch reachable by a human
   mid-run, and detecting a search that is not converging? Give concrete implementations.
5. SANDBOXING. For running agent-generated code that deploys infrastructure — compare Docker,
   gVisor, Firecracker, E2B, Modal, Daytona, and ephemeral cloud environments. Judge on: startup
   latency, cost per run, blast-radius containment, and whether cloud credentials can be scoped
   per sandbox. They are on Azure (ACI/Container Apps) with Snowflake; weight the answer
   accordingly.
6. TENANCY. They serve multiple clients (CLIENT-A, CLIENT-B) from shared infrastructure. What is the
   correct isolation model for an optimizer that touches client data paths, and what is the
   minimum gate set that must include a tenancy check? They have already had one incident where a
   single vendor API key returned every client's accounts.
7. SCAFFOLDING. What is the current best way to generate and maintain a multi-service Python repo
   skeleton of this kind — cookiecutter, copier, Nx, Bazel, uv workspaces, or an AI scaffolder?
   Judge specifically on: keeping generated projects updatable as the template evolves (drift is
   the usual killer), and monorepo-vs-polyrepo for a team of this size.
8. AUTORESEARCH. Assess github.com/karpathy/autoresearch honestly — what it is, what it does and
   does not provide, its maturity, and whether it is a suitable base or better treated as a
   reference design. Do not assume it does what its name suggests; check.

CONSTRAINTS: separate OBSERVED from MARKETED. For every safety mechanism, give a concrete
implementation, not a principle. Where the honest answer is "this is unsolved", say so.

DELIVERABLE: an optimizer architecture with explicit bounds and a kill switch, a sandbox
recommendation with cost per iteration, a scaffolding recommendation, and a verdict on
autoresearch as base-vs-reference.
```

---

## Part 1b — Two things the brief missed, and one correction to Part 0

### ⭐ "How do we deploy a team or agent to work on a repo?" — you already have this

**Measured in `orchestrator/server.py`, 2026-08-20.** The mechanism exists and runs today:

| Step | Implementation |
|---|---|
| Isolate | `_create_worktree()` → `git worktree add <path> -b <branch>` into `.sessions/`, then `git submodule update --init --recursive`. `.sessions/.gitignore` is written as `*` so worktrees never pollute the parent |
| Launch | `claude -p --verbose --output-format stream-json --max-turns N --max-budget-usd B --model M`, with `cwd` set to the worktree |
| Permission | `--dangerously-skip-permissions` **only** when running in a worktree; otherwise `--permission-mode auto`. Isolation is what earns the elevated permission |
| Observe | stdout streamed to `orchestrator/data/sessions/{sid}.jsonl` — 42 transcripts exist |
| Reclaim | `_remove_worktree()` → `git worktree remove --force` + `git branch -D` |

**So "deploy an agent to a repo" is solved.** What is *not* solved is deploying a **team**: several
agents against one worktree with an ownership rule, or several worktrees with a merge order. That is
the actual open question, and it is narrow. Add to **R2** as question 8:

```
8. TEAM-TO-REPO DEPLOYMENT. This company already deploys a SINGLE agent to a repo by creating a
   git worktree and launching a CLI agent inside it with a turn cap and a dollar cap. For a TEAM
   of agents working the same change, what are the established patterns — one shared worktree with
   a locking or ownership discipline, one worktree per agent with a defined merge order, or a
   single writer with reviewers who only read? Give concrete evidence of what fails: lost updates,
   merge storms, agents overwriting each other's fixes. Include how human review fits when several
   agents contributed to one diff.
```

⚠ **Correction to §0.4 item 1.** Per-session bounding is *not* missing — `--max-turns` and
`--max-budget-usd` are already passed on every launch. What does not survive a restart is
`_recovery_attempts` in `pipeline_agent.py:47`, a module-level in-memory dict, so
`MAX_RECOVERIES_PER_STAGE = 2` resets to zero on every orchestrator restart. **The session is
bounded; the re-dispatch loop is not.** That is the specific hole an optimizer must not inherit.

### The task tracker agents can update

Partly present, and the gap is specific:

| Exists | Where |
|---|---|
| Stage status per pipeline | `orchestrator/data/pipelines.json` — status, timings, cost, tokens, `result_data` per stage |
| Agents writing to Jira | `orchestrator/stage_scripts/jira_ops.py` — `transition_ticket` runs as a pipeline stage today |
| Failure ledger | `orchestrator/engine/logbook.py` — fingerprints, occurrences, related. **Written, never served** |

**The gap:** there is no lightweight task record an agent can create, claim, update and close
*without* a Jira round-trip — and Jira is the wrong granularity for "I am on step 3 of 7". Board
`docs/PREFECT_BOARD.md` is a human artifact, not an API.

**Recommendation — build this today, it is small and it unblocks team coordination:** a
file-backed task store beside `pipelines.json` with an append-only event log, exposed on the
existing `server.py` routes. Minimum schema: `id`, `parent`, `title`, `owner` (agent or human),
`status`, `blocked_by`, `evidence[]`, `created/updated`, and an `events[]` append log. Two rules
that matter more than the schema:

1. **Append, never overwrite.** An agent that sets a field wholesale destroys what another agent
   wrote — this estate has already lost 693 characters of guidance to exactly that.
2. **A task closes only with evidence attached.** `status: done` with an empty `evidence[]` is
   rejected by the store, not by convention. That is the smallest possible version of the
   GreenContract discipline, and it is what stops a team reporting 234 completions and 0 outcomes.

---

## Part 2 — Recommended document sections, once the research lands

For the combined technical spec / multi-tab artifact. Ordered by what a reader needs first.

| # | Section | Why it earns a place |
|---|---|---|
| 1 | **What is measured today** | Every figure with `MEASURED / DERIVED / ASSUMED`. Opens with reality, not ambition |
| 2 | **The one-page system map** | Three planes — build, data, serving. Drill into any box; every edge labelled with what crosses it |
| 3 | **The eval harness** | The precondition. What a pass means, how it is proved able to fail, where it lives |
| 4 | **Anatomy of an agent** | The config that *is* the version: prompt, model, effort, tools, context, retry policy |
| 5 | **Anatomy of a team** | Composition, the single topology, who owns the outcome, the prohibition each member carries |
| 6 | **The Data Pipeline Team, in full** | The only team. End-to-end, with its GreenContract |
| 7 | **The optimizer** | Search space, fitness, bounds, kill switch, sandbox — bounds before capabilities |
| 8 | **Metrics** | Every activity metric paired with an outcome metric; the Goodhart guard for each |
| 9 | **Versioning & run history** | Schema, retention, how a run ties back to the exact config |
| 10 | **Tenancy & the gate set** | The missing gate. Blast radius per client |
| 11 | **Deployment** | Repos, infrastructure, credentials, and the actual sequence to stand a team up |
| 12 | **What we deliberately did not build** | The deferred list with the evidence threshold that would unlock each |

**Layout guidance:** sections 1–3 are the spine and should be readable in five minutes. Sections
4–7 are the reference and should be drill-down. Section 12 is the one most technical documents omit
and the one that most protects the next reader.

---

## Part 3 — Open questions for Paul, not for the researcher

1. **Does the Data Pipeline Team include Snowflake and Power BI, or stop at the warehouse?** The
   brief asks both ways. Recommendation: **stop at the warehouse for team one.** Adding the BI
   surface adds the 50-measure catalogue problem to a team that has not yet proven it can land rows.
2. **GP-318 e2e today** — that is delivery work with a client deadline, and it competes directly
   with Phase A. It should win, and this program should assume it does.
3. **Is the AgnosticOptimizer allowed to touch client-facing paths at all?** Recommendation: no,
   not until the tenancy gate exists.
4. **`claude-in-chrome` was not connected** when this was written, so autonomous browser research
   was not possible. These prompts are written to be pasted into Deep Research by hand.
