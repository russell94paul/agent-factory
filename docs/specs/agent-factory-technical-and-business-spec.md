# Agent Factory — technical and business specification

**Written 2026-08-23.** This is the document you attach to a deep research prompt. It is the
**frozen baseline**: our own position, stated in full, *before* an outside pass looks at anything.

⚠ **It exists because the alternative has failed twice, measurably.** R12 was dispatched without one
of our standing constraints and duly recommended a tool the constraint had already ruled out
(`../research/SYNTHESIS.md` §12.2). R6 was dispatched carrying a constraint that was *false* and its
ranking bent around it (§10.4). Same class, opposite sign, same consequence: **the pass optimised
against a world we described rather than the one we have.** Everything below is written so the next
pass cannot do that — and so what comes back is a **diff**, not a survey.

**Every figure names its instrument and carries a basis:**

`[M]` measured here, instrument named · `[D]` derived from something measured ·
`[R]` reported/inherited, not re-verified · `[A]` assumed, no measurement

⭐ **The single most important sentence in this document is §3.1.** If a reader takes one thing,
take that: this is an *evidence* product, not a *process* product. It decides what the platform is,
what the UI is for, and which of the eight options in §12 are even admissible.

---

# PART I — BUSINESS

## 1. What this is, commercially

Analytic Labs (ALDC) is a small data-and-analytics consultancy. The delivery pattern is the same for
every client: pull vendor data through a connector, land it in Snowflake, model it into a star
schema, surface it in Power BI or a bespoke Next.js app. The billable unit of work is a **connector
brought to green end to end** — and the repeatable cost of that unit is the whole business question.

The Agent Factory is a bet that this unit can be manufactured by agent teams whose output is
**certified rather than believed**, and that certification is what makes it sellable.

### 1.1 The addressable surface, measured

| | Count | Instrument |
|---|---:|---|
| Client directories in `clients` | **24** | `[M]` `ls -d */` |
| Eclipse connection configs | **139** | `[M]` `find -path '*/connections/*.json'` |
| Eclipse extraction templates | **739** | `[M]` `find -path '*/templates/*.json'` |
| Snowflake warehouse view definitions | **186** | `[M]` `find -path '*/warehouse/*.sql'` |
| `report_common` reporting views | **104** | `[M]` `find -path '*report_common*/*.sql'` |
| `core_api` Python | **140 files / 30,460 LOC / 21 routers** | `[M]` `find api v1 -name '*.py'` |
| `eclipse` TypeScript | **239 files / 22,715 LOC / 18 coreAPI domains** | `[M]` `find src -name '*.ts*'` |

⚠ **739 templates is not 739 units of work**, and reading it that way is the first mistake available
here. It is the *surface* the factory could act on. How many are live, how many are dead config from
an inactive client, and how many would need migrating rather than re-pointing is **not measured**,
and no business case should be built on the raw number until it is. `[M]`/`[A]`

### 1.2 The two failures that define the product

This estate has twice built mechanisms that **acted** without anything measuring whether the action
helped:

- A retired agent produced **233 diagnoses, 234 escalations and 0 fixes over 81 days.** `[R]`
- A separate loop ran **965 times, recorded its own 1.6% success rate, and never adjusted.** `[R]`

Both were capable. **Neither was measurable.** Source: `prefect-connectors/docs/AUTORESEARCH_REVIEW.md`,
inherited and not re-measured on 2026-08-21 — weaker evidence than anything marked `[M]`, and it is
still the strongest argument in the document.

⭐ **The commercial consequence is precise.** A dashboard over the first mechanism would have shown
234 escalations climbing steadily, and a self-improving loop pointed at that number would have
optimised for *escalating faster* and called it progress. **An activity metric with no outcome
metric is not a weak metric — it is an inverted one.** That is why `factory/metrics.py` *raises*
`GoodhartViolation` rather than warning.

### 1.3 The economics as they actually stand

Three lanes ran end to end on 2026-08-22–23. `factory/runs.py` derives these from the session
transcripts. `[M]`

| Lane | Model | Output tokens | Cache read | Wall clock | Commits | Out-tokens/commit `[D]` |
|---|---|---:|---:|---:|---:|---:|
| control-plane | opus-5 | 1.23M | 322M | 22.8h | 25 | ~49k |
| artifact | sonnet-5 | 227k | 55M | 19.4h | 5 | ~45k |
| certify | sonnet-5 | 236k | 55M | 1.7h | 4 | ~59k |

⛔ **No dollar figure is stated here, deliberately.** The repo's own standing rule is that there is
no honest cost number until *failed* attempts also record cost — today only successes do, so any
average would be computed over the survivors and would flatter. **A cost-per-outcome that omits the
failures is the 234-escalations dashboard with a currency symbol.** The research pass is asked to
respect this (§13), not to supply a number around it.

⭐ **Cache read exceeds output by 260× on the largest lane.** `[D]` That ratio is the single
most under-examined economic fact in this programme and nothing in the estate currently reasons
about it.

### 1.4 ⭐ The real bottleneck is not agent capability

| | Measured | Instrument |
|---|---|---|
| Runs finishing with no human | **3 of 14** | `[M]` orchestrator audit log |
| Gate events that were ever a *refusal* | **0 of 22** | `[M]` orchestrator audit log |
| Green PRs waiting on a human to press merge | **2, for 6 and 9 days** | `[M]` `prefect-connectors`, 2026-08-23 |
| Agents blocked on a plain-English question nobody read | **4** | `[M]` `jobs/<id>/state.json` |
| Concurrent lanes supported | **3** | `[D]` max independent set of the file-conflict graph, `lanes.py` |

⭐ **Two green PRs waited nine days for a click.** No amount of agent improvement touches that
number. **The delivery constraint is human decision latency, and it sits in the one plane that has
no user interface at all** (§8.4). This is the most commercially important finding in the document
and it was found by looking, not by reasoning.

⚠ **A refusal rate of exactly zero is not a clean bill of health** — it is indistinguishable from a
gate that cannot refuse. Absence of alarms and absence of alarm *capability* look identical from
the outside, which is this programme's founding failure wearing new clothes.

### 1.5 What changes commercially if this works

Stated as claims to be *attacked*, not as projections. None is measured.

1. **Connector onboarding becomes a priced, repeatable unit** rather than a bespoke engagement. `[A]`
2. **Certification becomes the deliverable.** "Here is the data" is a claim; "here is the data, the
   contract that judged it, the negative control proving that contract can fail, and the config hash
   of the agent that produced it" is an artefact a client can audit. **Nothing on the market sells
   this** — see §3.1. `[A]`
3. **The isolation ladder makes client-data work safe to delegate** (§6). Without it, agent work on
   a shared warehouse is not a governance question, it is a governance answer, and the answer is no. `[A]`
4. **Capacity stops being headcount-bound** at the point where the APPROVE plane stops being the
   queue. Note the ordering: **UI before capacity**, not after. `[D]` from §1.4.

---

# PART II — TECHNICAL

## 2. What is built, measured

`agent-factory` @ `8010676`, branch `feat/readiness-generator`. `[M]`

| | Count |
|---|---:|
| `factory/` modules | **29** (5,180 LOC) |
| Test modules | **16** (1,654 LOC) |
| Readiness gates registered in `readiness.GATES` | **30** — certification 8, judgement 8, handover 7, bounded 4, loop 3 |
| Research prompts written | **13** (R1–R12) |
| Answers filed | **15** |
| Findings in `docs/findings.d/` | **7** |
| Concepts enumerated from code | **26**, each citing its module |

The load-bearing ones, in our vocabulary — a survey that returns these as "gaps" has failed:

- **GreenContract** — a named set of falsifiable assertions; the root success object. `contract.py`
- **Four verdicts, never collapsed** — `PASS` / `FAIL` / `UNMEASURABLE` / `NOT_RUN`. `UNMEASURABLE`
  is raised by a probe *as an exception*, so a dark instrument cannot read as healthy.
- **The negative control** — `mutate_and_expect_failure` breaks the world and asserts the contract
  notices. Gated by `test_eval_can_fail.py`. **An eval nobody has proved can fail is decoration.**
- **The config IS the version** — an agent is a (prompt, model, effort, tools, retry, turns, budget)
  tuple; change one element and its certification does not transfer. `blueprint.py`
- **Evaluator as a principal** — a service with its own identity; three fields in, verdict out; the
  client cannot name the corpus it is scored against. `evaluator.py`, `evaluator_service/`
- **Append-only, evidence-gated task ledger** — state is a fold over events; `EvidenceRequired`
  blocks a close with no evidence. `tasks.py`
- **Activity metrics cannot exist alone** — `GoodhartViolation`. `metrics.py`
- **Parallelism bound by file locality, not the dependency graph** — one worktree per lane, claims
  that refuse overlap. `lanes.py`, `worktrees.py`, `claims.py`

## 3. The product thesis

### 3.1 ⭐ An evidence product, not a process product

From `README.md`, unchanged since the repo was founded:

> A team of agents did the work, and we can prove it — or we can prove we could not tell.

**Every session manager and agent platform on the market manages _processes_.** None of them answers
*who did this work, under what configuration, and what proves it was correct.* That is the axis this
repo is already on, and **it is the only axis where it is not starting from behind.**

This decides everything downstream. A research pass that returns "you should adopt a terminal grid"
has answered a process question we did not ask.

### 3.2 Three things nobody ships

1. **A verdict that can say "I could not tell."** Four-valued, `UNMEASURABLE` first-class. Every
   dashboard on the market is two-valued. `[M]` — this is built.
2. **Provenance to a config hash.** "This artefact was produced by *this* agent, on *this* model,
   with *this* prompt, under *this* contract version." The hash exists and covers **0 of 15
   dimensions.** `[M]` — **this is a gap with a name, not a feature.**
3. **Cost paired with an outcome, enforced.** `metrics.py` *refuses* an unanchored activity metric.
   R12 reached the same rule independently — an outside pass reproducing a rule we already enforce
   is the strongest corroboration available. `[M]`

## 4. Architecture — four planes

From `architecture-v0.md`. This is the load-bearing structure, and §12 asks whether it survives.

```
APPROVE   humans only. merge · per-secret grant · promote to prod   ← never automated
PROVE     readiness gates · GreenContract · findings.d · run audits
RUN       isolation ladder — T0 worktree · T1 container · T2 clone schema
DECIDE    conflict graph · claims · scheduling · caps · budgets     ← the :8765 build plane
```

**The boundary that matters is RUN/PROVE: the thing being measured must not be the thing doing the
measuring.** R3 ranks a separate local process as **rank 5, "mostly theatre"**, so this is currently
aspirational — the evaluator must become a principal with its own identity and credentials before
the diagram is honest. The *design* is rank 1; the gap is **a deployment change, not a code change.**

⚠ **The remaining hole in it, stated plainly:** the contract is parameterised by a blueprint the
graded party writes. **An agent that softens its own blueprint softens its own grading, process
boundary or not.** A four-rule target floor and the artefact hash narrow it; a per-connector target
pinned *by the evaluator* would close it, and nobody has written one.

## 5. ⭐ Each plane implies a different user — and only one is for a non-engineer

| Plane | Who | What they need | Exists today? |
|---|---|---|---|
| DECIDE | operator | what can start, what conflicts, what it costs | partly — Lanes tab |
| RUN | **nobody, ideally** | only the exceptions: stalled, orphaned, over-budget | Sessions tab (new) |
| PROVE | reviewer | the verdict **and what it was measured with** | partly — Gates tab |
| **APPROVE** | **anyone, including a non-engineer** | what was delivered, what proves it, approve/reject | **nothing** |

⭐ **The APPROVE plane has no surface at all, and it is also where delivery is measurably stuck
(§1.4).** The "normal user" surface and the delivery bottleneck are **the same surface**. That
coincidence is the most useful structural finding in this document.

## 6. The isolation ladder — the novel claim, and the one most likely wrong

**An agent's isolation tier is chosen by what its task _touches_, declared up front, and enforced —
not by what kind of agent it is.**

| Tier | Environment | May touch | Use for |
|---|---|---|---|
| **T0** | git worktree, operator machine *(built)* | repo files only. **No egress, no DB verbs** | code, docs, tests |
| **T1** | container, egress allowlist, read-only warehouse role | repo + **SELECT** on real data | analysis, reconciliation |
| **T2** | container + **ephemeral zero-copy clone schema**, dropped on exit | full DDL/DML **inside the clone only** | views, migrations, backfills |

Three consequences, and they are the argument:

1. **T2 removes the file-conflict cap for data work.** Two agents in two clone schemas conflict on
   nothing. The 3-lane ceiling is a property of *code* work and does not generalise. `[D]`
2. **The dangerous verb is contained by construction, not by prompt.** "Do not touch prod" in a
   prompt is a request; **a role with no grant on prod is a control.** This is what generic agent
   frameworks miss — isolating a filesystem does nothing when the risk is DDL on a shared warehouse.
3. **Promotion out of a clone is an APPROVE-plane act**, and the clone→real diff is *mechanically
   producible* from a T2 run.

⚠ **Where it is most likely wrong** — attack these first:
- A zero-copy clone is cheap to create; **the compute to validate against it is not**, and a clone
  of a *share* may not behave like the real thing. If T2 is not cheap, the argument collapses and
  the ceiling stays at 3. `[A]`
- **"Data work does not conflict" is asserted, not measured.** `[A]` Two agents building two views
  can absolutely collide — on a shared dimension table, a naming convention, the same
  `REPORT_COMMON` object. The conflict graph may need *different edges*, not fewer.
- T1/T2 assume containers on Windows via WSL. Unmeasured; start-up cost is a guess. `[A]`

## 7. ⭐ The manufacturing step does not exist yet — and it is the goal

**This is the gap the whole exercise is aimed at.** Today an agent is a `Lane`: a prompt string, a
model, a gate list. **That is a launcher input, not a manufactured artefact.** The factory's output
is currently a *session*; it needs to be a **spec**.

The target object, from `architecture-v0.md` §5:

```yaml
AgentSpec:
  id: navira-view-builder
  version: 7                                # bumped on ANY field below — that is the point
  prompt_ref: prompts/view-builder@a3f9c1   # content-addressed, never inline
  model: sonnet
  effort: medium
  tools: [read, edit, bash, snowflake_ro]
  tier: T2                                  # chooses the sandbox — §6
  budget: {tokens: 400k, wall_clock: 45m, warehouse_credits: 2}
  contract: green@v5                        # which assertions certify it
  gates: [grain, no-regression, consumer-render]
  needs_human: [credential-grant, merge, promote]
```

Two rules follow, and both are already violated:

- **The version hash must cover every field.** A certification granted under `green@v4` must not
  silently transfer to `v5`. **Today it covers 0 of 15 dimensions.** `[M]`
- ⛔ **A spec field that nothing reads is worse than no field.** This month produced a `--model`
  flag built into a dead variable — **every lane announced a model it was not running on** — a
  detector silently degrading to 1 finding instead of 313, and gates reporting PASS while measuring
  nothing. **Every field needs a test asserting it reaches the process.** `[M]`

### 7.1 What "create a team from the platform and deploy to a repo" requires

Stated as a gap list, because this is the actual ask:

| # | Required | State |
|---:|---|---|
| 1 | An `AgentSpec` that is a versioned artefact, not launcher arguments | **absent** — §7 |
| 2 | A version hash covering all 15 dimensions | **0 of 15** `[M]` |
| 3 | Content-addressed prompts (`prompt_ref`, never inline) | **absent** |
| 4 | Tier declaration enforced by the DECIDE plane, refusal as an audit event | **absent**; would give the `refuses` gate its first real record |
| 5 | Bounded deployment into a repo | **built** — `deploy.py`: worktree + turn cap + dollar cap + `AttemptLedger` persisted so a cap survives restart |
| 6 | A per-repo GreenContract the team is certified against | **built for connectors** (A1–A12), **not generalised** |
| 7 | Cross-repo targeting (the 5 repos in §9) | **absent** — every path resolves from cwd, see §10.2 |
| 8 | A catalogue/registry of certified specs to deploy *from* | **absent** |

⭐ **5 of 8 are absent and they are all upstream of the UI.** A platform that composes teams before
`AgentSpec` exists would be a form over a data model that does not exist yet.

## 8. The UI — what it is for, what exists, what is confusing

### 8.1 The four live surfaces, and a fifth that died `[M]`

| Surface | Where | State |
|---|---|---|
| Orchestrator UI `:8765` | `prefect-connectors/orchestrator/static/` | `index.html` **161 KB**, `flow.js` 58 KB |
| Readiness tracker | `agent-factory/scripts/local_tracker.py` | 5 tabs, re-measures per request, **10–19 s a page** |
| `agent-factory.html` | `docs/artifacts/` | published, **goes stale silently** |
| `orchestration-bench.html` | `docs/artifacts/` | published, static |
| `platform/master/` | `aldc-launchpad` | **superseded, dead since June 2026**, per its own CLAUDE.md |

⚠ **Any new UI is the sixth thing built to look at this work**, and `platform/master` is the
cautionary case: a monorepo founded as a delivery *platform* whose platform half stopped moving in
June while the ops half carried every ticket. **"Build a new platform UI" has been tried here and it
died.** A research pass must be told this.

### 8.2 What the tracker already does that a session manager does not

Not a defence — stated so a pass does not recommend rebuilding it:

- **Every number re-measures on refresh. There is no cache.** A page that can quietly show
  yesterday's state is the exact drift this project exists to remove.
- **Verdicts are four-valued**, not a checkbox grid.
- **The board is generated from the gates**, so a task list cannot drift from what is measured.
- **`recommend()` ranks lanes** and states in writing which part is judgement — *"a bare ranking is
  an oracle."*
- **Launching a lane claims it first**, refuses on conflict, and refuses if a live session already
  occupies the worktree.

### 8.3 What is actually confusing — observed, not imagined `[M]`

1. Five live sessions shared one name, inherited from the boot prompt. *(fixed)*
2. Six sessions shared one working directory, so cwd did not disambiguate either. *(fixed)*
3. **A terminal died and its agent kept working, invisibly, for minutes.** *Alive*, *visible* and
   *attachable* are three different properties and nothing distinguished them. *(fixed — four
   liveness states)*
4. **Four agents blocked on questions written in plain English** in `jobs/<id>/state.json`, which
   nothing read. ⭐ **Not alarm fatigue — alarm *absence*.** *(shown, not yet answerable)*
5. A finished lane left no trace — `finish()` deleted the claim and that was the record. *(fixed)*
6. **Two green PRs waited 6–9 days for a human.** **NOT ADDRESSED.**
7. **A page load takes 10–19 s** and two concurrent requests return empty — single-threaded server.
   **NOT ADDRESSED.**
8. Two servers can hold one port and you verify against the stale one. **NOT ADDRESSED.**

⭐ **Items 1–5 were _legibility_ problems and are mostly fixed. Item 6 is a _throughput_ problem and
no UI built so far touches it.** A research pass must not blur that distinction.

### 8.4 The two requirements, stated as budgets

Paul's ask is "speed and ease of monitoring". Made falsifiable:

- **Speed.** Current: **10–19 s per page**, and **two concurrent requests return empty**. `[M]` The
  target is interactive latency without introducing a cache — because "every number re-measures on
  refresh" (§8.2) is a *correctness* property, not a performance compromise. ⭐ **The interesting
  question is therefore not "how do we cache this" but "how does a page stay honest and fast at the
  same time" — and if a figure must be cached, it carries its age in the same string.**
- **Monitoring.** The measured failure is **alarm absence**, not alarm fatigue. Whatever surfaces a
  blocked agent's question must **interrupt**, not badge — passive badges are missed, and ours was
  missed for days.

## 9. The estate — deploy targets, infrastructure, access

Repos the factory would deploy into. Access is stated by **name only** — no value appears in this
document or any research prompt, and none is needed to answer one.

| Repo | Role | Scale |
|---|---|---|
| `prefect-connectors` | Prefect v3 data plane **+ the orchestrator/build plane**. First team's target | `[R]` 424 tests |
| `clients` | Per-client Eclipse JSON + Snowflake SQL. **No application code** | `[M]` 24 dirs, 139 conns, 739 templates, 384 SQL |
| `core_api` | Eclipse control-plane backend (FastAPI, Cosmos DB) | `[M]` 140 files, 30,460 LOC, 21 routers |
| `eclipse` | Next.js 15 App Router UI over `core_api` | `[M]` 239 files, 22,715 LOC, 18 domains |
| `wiki` | The knowledge base. R10 says its leverage is **skills, not retrieval** | `[M]` ~1M tokens |
| `agent-factory` | The factory itself | `[M]` §2 |

**Infrastructure**: Snowflake (`PROD_DG1_GEP` / `TEST_DG1_GEP` and per-client equivalents), Power BI
semantic models, Prefect v3, Azure (Container Apps, Cosmos DB, Blob), GitHub Actions, on-prem Docker
agents for the legacy `connector` runtime.

**Credential classes that exist** — named, never valued: Snowflake role credentials per environment;
vendor API keys and refresh tokens (`CORE_DEV/account_secret.json`); Power BI service principal;
Azure SAS tokens; GitHub tokens.

⛔ **Per-secret human approval is a hard rule. There is no batch-approval of credentials, ever**,
and any recommendation that assumes one is inadmissible regardless of merit.

⚠ **Tenancy is declared, not discovered.** Six Navira account ids are declared in
`windsorai.py:23` — verified 2026-05-29, **twelve weeks before use**, and the source itself says
*"confirm against a live pull before activation."* A PASS means *"the landing matched what we
declared"*, never *"what we declared is still correct."* ⭐ **Never read tenancy scope from landed
rows** — "which accounts arrived" is not "which were requested", and that gap is the A9 hole exactly.

## 10. Measured state, and two instrument caveats

### 10.1 Readiness

**10 of 30 gates pass** on the operator's machine, 2026-08-23. `[M]`

### 10.2 ⚠ The board's number depends on which directory you run it from

Re-measured for this document in a Linux container at the same commit: **6 PASS, 4 FAIL, 18
UNMEASURABLE, 2 NOT_RUN.** `[M]` `python -m factory.readiness`, cwd `/home/user/agent-factory`.

**Neither run is wrong.** 18 gates read UNMEASURABLE because they resolve
`FACTORY.parent/"prefect-connectors"` and `FACTORY.parent/"aldc-launchpad"`, neither of which exists
here. This is [[F72]], and the rule it produced stands: **state the cwd with any before/after claim.**

⭐ **It is also a finding about the architecture, not just the instrument.** §6 proposes running
agents in containers (T1/T2). **A readiness board that reads 10 on the operator's machine and 6 in a
container cannot certify anything running in one.** The measurement plane is not yet portable, and
that is upstream of the isolation ladder.

### 10.3 ⛔ The corpus integrity check has never passed off Windows — new, found writing this

`evals/MANIFEST.sha256` pins `c3fbfed8…`; the file in git hashes to `c5eb1cb9…`. Not tampering:

```
sha256(bytes as stored in git, LF)              = c5eb1cb9…   ← what any Linux/CI checkout sees
sha256(same bytes with CRLF line endings)       = c3fbfed8…   ← what the manifest pins
```

The manifest was pinned against the **Windows working-tree bytes**; git stores LF. Both files landed
in one commit (`0f1a09b`) and neither has changed since, so **the tamper-evidence mechanism has been
red on every non-Windows checkout since the day it was written**, and the `corpus` gate FAILs there.

⭐ **It does not merely turn a gate red — the test suite cannot collect.**
`tests/test_connector_contract.py` imports a module that calls `corpus.load()` at module scope, so
`CorpusError` aborts the run. Measured on Linux at the same commit: `[M]`

```
as committed                                  1 collection error,  7 failed,  98 passed
manifest re-pinned to the bytes git stores                         1 failed, 134 passed
```

**36 tests either failed or never ran because of a line-ending conversion.** (The single remaining
failure is unrelated: a test feeds `lane_from_cwd` a hard-coded `C:\repos\...` path.)

⭐ **This is the T1/T2 blocker in miniature, and it is the same shape as §10.2.** A containerised
agent would read the corpus as tampered and refuse to certify — correctly, by its own rules, for a
reason that has nothing to do with the corpus. **The trust boundary the certification story rests
on does not survive the move to the environment §6 proposes running agents in**, and CI on
`ubuntu-latest` could never have run this suite. Filed as [[F75]], with the discriminating test.

## 11. What is settled — the do-not-re-ask list

**Hand this to any researcher.** Twelve passes, ~370 KB of answers. Re-asking buys the same answer
at full price, and a pass that "discovers" one of these has produced nothing.

| # | Asked | Verdict, in one line |
|---|---|---|
| R1 | Grade the eval harness | Keep GreenContract as the authoritative verifier. **Do not** add a general LLM-eval framework. The weak parts are control-plane, not eval sophistication |
| R2 | One agent or a team | ⛔ **Do not build the three-agent team.** One worker + non-LLM verifier + human for privileged ops. Multi-agent averaged **−3.5%** across 180 configurations; sequential tasks degraded **39–70%** |
| R3 | Control plane, tenancy, optimiser | **Do not optimise yet.** Bounded, reapable, fail-closed, independently evaluable first. Tamper-evidence is not a trust boundary; an evaluator **service** is |
| R4 | Repo-agnostic optimiser | Not yet — but build repo-agnostic *interfaces* now: cheap now, expensive to retrofit |
| R5 | Build velocity | Lean runner + sandbox + circuit-breakers is the gating step. Worktree per agent — **41.7%** cross-agent conflict rate |
| R6 | Automation and alerting | Branch per lane, merged one at a time. ⚠ answered under a **false** constraint — §10.4 of SYNTHESIS |
| R7 | Session manager | Switchboard = **inspiration, not adoption.** Its proposed fitness proxy (readiness gates) is **rejected** — that is the never-optimise list |
| R8 | Data-engineering factory | outstanding |
| R10 | Hierarchical wiki | **No.** ~24% accuracy loss from 30k *irrelevant* tokens; our wiki is ~1M. ⭐ The win is **procedure synthesis into skills**, not a better corpus |
| R11 | Concept diff vs other factories | 7 absent concepts, **every one costed as "significant engineering"**; none recommended now. Sharpest: **guardrails** — a *pre-action* layer, categorically different from a post-hoc gate |
| R12 | Session-manager substrate | ⛔ **Answered under a MISSING constraint.** Its own OBSERVED §2 contradicts its summary: **there is no attach**, and it spawns a *duplicate against a live session id* — which *is* the incident that prompted the question |

**Four independent passes converged without being asked:** *"the weakest parts are control-plane
problems"* · *"control-plane changes are more urgent than agent architecture"* · *"this system should
not be optimised yet"* · *"the current experiment is not yet a reliable experiment."* **Treat as
settled unless new measurement contradicts it.**

⭐ **Never optimise:** retry caps, gate thresholds, tenancy checks, timeouts, evaluator thresholds,
the corpus. **These are safety specification, not hyperparameters.** *"Optimising eventual success
can simply reward more retries"*, and optimising on the candidate's own score *"changes the ruler
rather than the system."*

**When search does start**, screen in this order: model (very high — 9–13pp between backends) ≫
reasoning effort ≫ tool interface ≫ context layout ≫ system-prompt structure ≫ prompt wording
(*"do not spend live 11-hour evaluations searching commas"*).

## 12. What is deferred — with its unlock condition

⚠ **This table is the reason a naive survey returns ten false gaps.** Every row is a deliberate
non-decision with a stated threshold, not an oversight.

| Deferred | Unlocked by |
|---|---|
| Separate architect LLM | Same-budget A/B: ≥10pp terminal-success gain or ≥20% efficiency, no new seam failures |
| Mandatory tester LLM | A non-executable criterion where blinded LLM judgement improves agreement with experts |
| `agent ↔ agent` messaging | Production-like tasks with genuine concurrent branches and ≥5pp net gain after coordination cost |
| `manager ↔ manager`, army tiers | Several independently certified teams **plus a measured inter-team bottleneck** |
| Dynamic team-selection LLM | ≥200 adjudicated examples plus static misrouting ≥10% |
| Ten team types | A specialist only once tasks show it beats the generic worker |
| Agentic gym | A stable verifier **plus hundreds of clean labelled trajectories** — *"training on current traces risks learning pathological loops"* |
| Framework migration | Fault injection showing an invariant our engine cannot satisfy and a candidate can |
| The optimiser (`autoresearch`) | Steps 1–8 of the build order (§14) |

## 13. Genuinely absent — the real gap list

Not deferred, not renamed. **Nothing here has a stated unlock condition, which is itself the finding.**

1. **Guardrails as a pre-action layer.** Our gates evaluate *finished output*; a guardrail blocks a
   bad action *before* it happens. ⭐ Worked example already shipped:
   `terminate_prefect_flow_run` sent Prefect `CANCELLING` **before** the ownership check — so the
   refusal protected the container and never protected the run. **A post-hoc gate cannot catch that
   class.**
2. **Structured traces.** `runs.py` derives tokens, cache traffic, model and wall-clock from a
   transcript — so telemetry is *not* wholly absent, but there is **no structured trajectory
   object**: no span, no typed event stream, nothing another tool could read. OTEL GenAI semantic
   conventions are unexamined.
3. **Task/environment packaging** as one reproducible unit (METR task standard shape).
4. **The manufacturing step** — §7. The factory produces sessions, not specs.
5. **The APPROVE surface** — §5, §8.3 item 6. **The measured bottleneck has no UI.**
6. **Post-run learning.** Nothing accrues knowledge between certifications, and no pass has asked
   whether it should.
7. **Mid-run human approval.** `operator.py` handles blockers declared *before* a session. R5's
   *"human approval step before any container launch"* is unbuilt.
8. **Compensating actions.** ⭐ **`git revert` does not undo a dropped table.** Nobody has designed
   the rollback semantics the isolation ladder implies.

## 14. The build order — optimisation is step 9 of 9

R3's prerequisite chain and R4's sequence, merged. **Steps 1–4 are non-negotiable per R3.**

```
1  hard external attempt / spend / concurrency budget
2  timeout + cancellation + orphan reaping + restart reconciliation
3  terminal verdict computed from append-only history, not current state
4  refusal-capable gates, with negative drills
5  tenant capability isolation at every persistence/promotion boundary
6  complete attempt/cost telemetry, INCLUDING FAILURES
7  external evaluator trust boundary (a service, not a directory)
8  expand and freeze the evaluation corpus (1 case → 29+ strata)
9  ── only here ── configuration experiments
```

⭐ **Steps 1–4 are changes to `prefect-connectors`, and they are the first team's work, not hand
work. That is the entire point of the factory.** Doing them by hand is doing the team's job
manually. The reason they come first is that **a team cannot be certified until the loop it runs in
can tell success from failure.**

⛔ **Calibrating on one run is not calibration.** A blind spot affecting 10% of a stratum needs **29
cases** for a 95% chance of being seen once; 5% needs 59; 1% needs 299. We have **one**. The
prescription is two distributions — a regression corpus of every distinct historical failure (**not**
frequency-weighted, because the observed distribution is endogenous to a broken system) and a
challenge corpus across 15 mechanisms.

## 15. Constraints any recommendation must respect

**These are stated because omitting one has already cost us a research pass (§0).**

- **Windows-first** on the operator's machine. WSL exists; say what changes. ⚠ And see §10.2/§10.3 —
  Windows-first has *already* produced two platform-dependent instruments.
- **Three concurrent lanes.** A design assuming ten agents answers a question we do not have.
- **Small team.** Anything needing a platform team to operate is wrong regardless of merit.
- **Per-secret human approval is a hard rule.** No batch-approval of credentials, ever.
- **No unlabelled stale numbers.** A cached figure carries its age *in the same string*.
- **The existing instrument panel is never removed**, only added to.
- **Merging stays human.** `finish()` refuses it and should keep refusing.
- **Evidence-gated deploys stay**: prove the target, validate at the consumer's layer, prove no
  regression, capture a rollback.
- ⚠ **The no-in-page-terminal constraint is UNDER REVIEW and must be settled before dispatch** —
  §16.1.

## 16. ⛔ Open decisions — Paul settles these BEFORE any prompt is dispatched

**A research pass cannot respect a rule it was not given, and cannot decide a question we own.**

### 16.1 The in-page terminal — SETTLED 2026-08-23: asked, not asserted

**Decision: it goes to the research pass as an open question (R13 `E8`), not as a constraint.**

It has now cost two passes in opposite directions. R7 was handed our position and returned it with
citations, teaching us nothing. R12 was never told the constraint existed and recommended an
Electron app whose whole model is an embedded terminal per session — so its "adopt" is not a
refutation of R7, it is an answer to a different question.

⭐ **Both failure modes have the same cause: we controlled the answer instead of asking the
question.** Asserting `RETIRED` would buy back our own position a third time. So R13 states neither,
names both prior failures inside the prompt, and tells the pass to take a side and defend it.
Paul's own position — *"terminal mode needs to exit"* — is deliberately withheld from the fence so
what comes back is evidence rather than an echo.

⚠ **`E8` gates `E1` and `E7`.** Grade it first. If a third pass ducks it, the question is not
answerable from the literature and we settle it with the week-long experiment `E8(e)` asks for.

### 16.2 The five remaining owner questions

| # | Question | Blocks |
|---:|---|---|
| 2 | Is the landing table one account or two? 20 rows across 18 campaigns on one date **cannot** be unique on `(account_id, campaign_id, date)` | If one account, the declared primary key is wrong and **the calibration world is built on a mistake** |
| 3 | Which Jira ticket does this work belong to? Nothing in either repo records one | Traceability; the `ticket` gate |
| 4 | Is the target *internal capacity* or *a client-facing product*? §1.5 differs sharply by answer | The whole UI scope |
| 5 | Does the platform deploy to all five repos in §9, or only `prefect-connectors` first? | §7.1 item 7 |
| 6 | Is the corpus manifest re-pinned to LF, or does CI stay Windows? (§10.3) | Every container tier |

---

## 17. How to use this document

1. **Attach it whole** to the deep research prompt in `../research/R13-platform-and-manufacturing.md`.
   Do not paraphrase it into a summary first — §11 and §12 are the parts that stop a generic answer,
   and a summary is exactly what drops them.
2. **Settle §16.1 in writing first.** Then state the decision in the prompt.
3. **Grade what comes back as a diff**, not a survey. Every returned concept gets exactly one
   verdict — `PRESENT` / `RENAMED` / `DEFERRED` / `ABSENT` / `NOT-SEARCHED` — and a citation.
   ⭐ **A concept with no citation is a rumour.**
4. **File the answer at `docs/research/answers/R13-answer-*.md`** and nowhere else.
   `factory/synthesis.py` globs exactly one directory; an answer filed elsewhere can never appear in
   `unsynthesised()`, so the currency test can never go red for it — **and a research record that
   silently omits a landed answer is the failure this programme exists to prevent.**
5. **Fold it into `SYNTHESIS.md` before acting on it**, recording disagreements rather than
   smoothing them. ⭐ **Where an answer's own evidence contradicts its executive summary, the
   evidence wins** — that rule has already caught R12.

## See also

`architecture-v0.md` · `../research/ui-surface-inventory.md` ·
`../research/agent-factory-concept-inventory.md` · `../research/SYNTHESIS.md` · `../findings.d/`
