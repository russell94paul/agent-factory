# Golden workflow fit — New Data Source → Validated Power BI Metric

**Written 2026-08-29.** An architectural test, not a plan. Paul named one real vertical —
*"add an advertising source for a client and make it correctly available in their Power BI
reporting, with evidence from source API through the rendered consumer"* — and asked whether the
objects we have can represent it cleanly.

**Answer in one line:** the *proving* half of the architecture fits it well and was in fact designed
from its failure modes; the *organising* half cannot represent it at all, because **there is no
object for the job**. Everything below is the detail behind those two clauses.

Basis labels, as everywhere here: `MEASURED` (ran it, have the number) · `DERIVED` · `REPO-BACKED`
(cited `path:line`) · `REASONED` · `ASSUMED`.

---

## 0. The measured baseline this note was written against

```bash
python -m factory.launch          # 2026-08-29
```

```
May I RUN an agent, with me watching?     SUPERVISED-OK
May I LEAVE it running, unattended?       UNATTENDED-BLOCKED
    cap FAIL · reaper FAIL · ceiling FAIL · concurrency FAIL · bounded FAIL
May I TRUST what it produced?             OUTPUT-UNCERTIFIED
    suite FAIL(21/388) · certified NOT_RUN · corpus FAIL · version FAIL · breadth FAIL
```

`MEASURED`. Sibling repo `prefect-connectors` on `chore/artefact-homes`, 29 dirty files — the
condition the suite number holds under, per `boot-prompts/execution-plane-2026-08-30.md`.

**Nothing in this note changes that position.** The golden workflow is an architectural test applied
to a system whose loop is not yet bounded. RUN-01…04 remain the critical path.

---

## 1. Current architecture mapping

| Concept | State | Where it lives / what is missing |
|---|---|---|
| **Job / Outcome** | ⛔ MISSING | Nothing binds a client ticket to its lanes, its contract, its evidence and its approvals. `tasks.Task` is a title with an evidence list; `Lane` is a unit of *our own build work*; `Preset` maps a ticket **type** to a config but is consumed by nothing. This is the gap. |
| **Task** | PARTIAL | `factory/tasks.py` — append-only, `parent`, `blocked_by`, evidence-gated close. Sound. But `blocked_by` is **dead in practice** (review D-1: the board's edges were hand-written in `ticket-detail.json`, not read from the store), and no run path writes to it. |
| **Agent** | EXISTS | `blueprint.AgentSpec` — prompt/model/effort/tools/turns/budget/prohibition, content-hashed. |
| **Team** | EXISTS (inert) | `blueprint.TeamSpec` — pinned agent versions, contract name, repo, prohibition; identity is now a **deny-list** so a new field is identity by default (`blueprint.NOT_IDENTITY`). ⛔ `git grep "TeamSpec\|load_team"` outside `blueprint.py` returns nothing — **nothing executes a team.** That is RUN-03. |
| **Session** | EXISTS | `factory/sessions.py` — liveness from the process table, not from file presence. |
| **Run** | PARTIAL | `factory/runs.py` — outcome + **measured** cost per lane, three RECORDED rows `MEASURED`. Keyed on **lane**, not on job. Carries no model, effort, blueprint version, or job id. R19 finding #2. |
| **Repo** | PARTIAL | `TeamSpec.repo` is a string (now inside the version hash). `factory/repo.py` resolves the *primary worktree* — a different concern, not a RepoContext. |
| **Context** | ⛔ MISSING | No typed context of any kind. `Lane.full_prompt()` is `PREAMBLE + prompt + POSTAMBLE + operator_block` — **string concatenation** (`lanes.py:88`). Context is a blob today. |
| **Artifact** | PARTIAL | `docs/evidence/*` by convention, corpus documents under `evals/`, contract JSON payloads. No typed artifact with an id, a producer and a class. |
| **Evidence** | PARTIAL — **two unjoined systems** | (a) `tasks.add_evidence(kind, ref, basis)` gates close on MEASURED\|DERIVED — but `kind` is a **free string**. (b) `ContractResult`/`AssertionResult` with four verdicts. Neither knows about the other, and neither expresses *"these four classes are mandatory"*. |
| **Gate** | EXISTS — strongly | Two deliberately separate systems: `readiness.Gate` (is the *factory* ready) and `contract.Assertion`/`GreenContract` (is the *deliverable* right). `plan_gates.py` warns in its docstring that summing them produces a number about nothing. |
| **Approval** | PARTIAL | `finish()` does five steps and **refuses to merge** — a merge is a judgement. `Lane.needs_paul` / `Preset.needs_paul` declare what a human must settle; `operator.record()` stores the answer. No typed approval bound to a job or to an environment transition. |
| **Capability / Permission** | ⛔ MISSING in code | `prohibition` is a **prose string**. The T0/T1/T2 isolation ladder exists only in `docs/specs/architecture-v0.md` §4. `grep -rn "tier" factory/*.py` → nothing. `MEASURED` |
| **Metric / Data Contract** | PARTIAL | `PbiTarget.anchors: Dict[str, float]` — a measure name and a number. **No scope, numerator, denominator, grain, currency or valid dimensions.** This is precisely the DQ-001 defect class. |

---

## 2. How the golden workflow travels through what exists

```
Business requirement ─── ⛔ no object. A ticket id lives in a JSON file the board renders.
Client context ───────── ⛔ no object.
Source investigation ── ⛔ no object; ConnectorTarget holds the *expectations*, not the API facts.
Connector impl ───────── ✅ Lane/AgentSpec can express it; ⛔ nothing executes a TeamSpec.
Source validation ────── ✅✅ connector_contract A1–A12, CALIBRATED
                              (test_every_assertion_has_been_proved_able_to_fail)
Landing / orchestration ✅ A6–A9 landed-row assertions; probes wired for A1/A5 only
Snowflake transform ──── 🟡 no contract. plan_gates.g_the_warehouse_layer_is_representable exists.
Warehouse reconcile ──── 🟡 partially expressible as A10–A12 + M9 (warehouse agreement)
Semantic model design ── ⛔ no object. A model proposal is not a reviewable artifact type.
TMDL / DAX impl ──────── ✅ Lane/AgentSpec can express it
PBI reconciliation ───── 🟡 pbi_contract M6/M7/M9 — see §3.1, the contract is UNCALIBRATED
Rendered validation ──── ✅✅ M10/M11 exist and default to Unmeasurable — the design decision
                              that would have caught GP-293
Evidence package ─────── 🟡 the four classes exist as ideas, not as a checkable requirement
Human approval ───────── 🟡 finish() refuses to merge; operator.record() stores an answer
Production ───────────── ⛔ no environment-transition gate; PbiTarget.environment is declared
                              and asserted (M2) but nothing sequences TEST→PROD
```

**The shape of the answer:** the workflow's *right-hand half* — validation, verdicts, refusal to
collapse uncertainty — is the best-developed part of this repo, because it was built from the
estate's real failures (silent-empty connectors, GP-293's painted-nothing repoint, the 965-run loop).
Its *left-hand half* — what the work is, who it is for, what it must satisfy — has no
representation at all.

### 2.1 The five lanes and four artifacts, specifically

Paul's model is **one ticket → five independent lanes → four mandatory evidence artifacts → gate →
sign-off**. Against today's objects:

| Element | Representable? |
|---|---|
| one ticket | ⛔ no Job object to hang it on |
| five lanes | ✅ `TeamSpec` + `manager_to_agent` is a fan-out; five `AgentSpec`s is exactly it |
| lane **independence** | ✅ the conflict/worktree model already enforces it for code; ⛔ not enforced for data (no clone tier) |
| four **mandatory** artifacts | ⛔ → ✅ `tasks.add_evidence` took a free-string `kind`; nothing could say which four were required or notice one missing. **Closed by N1 this session** — `factory/evidence.py` + `close(require=...)`. |
| explicit gate | ✅ `GreenContract` is exactly this |
| sign-off | 🟡 `finish()` refuses to merge; no typed approval, no environment transition |

**Three of six as read; four of six after this session's N1.** The row above is the state this note
was written against — §8 carries the after-figure, and the two are the same count under the same
definition, one dated before N1 and one after. The two still missing are missing at *write time*,
which is the distinction that decides §5.

---

## 3. Gaps this workflow demonstrates

Only gaps this vertical actually exposes. Not a wishlist.

### 3.1 ⛔ The Power BI contract exists, has never been calibrated, and the roadmap says it does not exist

`factory/pbi_contract.py` is 472 lines defining M1–M12, including the two assertions only a renderer
can make. `MEASURED`:

```bash
grep -rln "pbi_contract" tests/ factory/ scripts/     # (nothing)
```

**Zero tests, zero callers.** Meanwhile `roadmap.TEAMS["Power BI Data Model Designer"]` reads
*"No contract exists for what its output must satisfy"* — which `python -m factory.launch` renders
verbatim as the team's blocker. That sentence was true when written and is now false.

⭐ **The correction makes the blocker sharper, not softer.** The connector contract earns its
standing from `test_every_assertion_has_been_proved_able_to_fail` — twelve assertions each *watched
refusing*. The PBI contract has no such proof. So the honest blocker is **"a contract exists and
nobody has shown it can fail"**, which is a different and more actionable thing than "no contract
exists". A contract never watched refusing is decoration — this repo's own standing rule.

### 3.2 ⛔ Evidence class is a free string

`tasks.add_evidence(tid, kind, ref, actor, basis)` validates `basis` and not `kind`. The four classes
Paul names — target proof, consumer-layer correctness, regression proof, rollback — cannot be
required, counted, or reported as missing. A job closing with four pieces of evidence that are all
the same class is indistinguishable from one that satisfied all four.

**This is a write-time gap.** Rows already written carry an unparseable `kind`; rows written from
here on can carry a typed one. That is the whole argument for fixing it now rather than later.

### 3.3 ⛔ The run ledger cannot attribute anything

`runs.record()` writes lane, outcome, basis, detail, problems, branch, commits, cost. It does not
write which job, which team, which blueprint version, or which agent versions. R19 established the
same finding independently and drew the right conclusion: **the missing fields are missing at write
time, and no amount of waiting fixes it.** Every §13 PoC measurement Paul asks for — rework time,
defects found by validators vs after sign-off, did this configuration help — is a join on fields that
do not exist.

### 3.4 ⛔ Context is a string, and the wiki requirement makes that a decision rather than an accident

`Lane.full_prompt()` concatenates four strings. Every context concept Paul names — CompanyContext,
RepoContext, ClientContext, SourceContract, DatasetContract, MetricContract, ContextPack, provenance,
freshness — has to survive as *structure* to be resolvable, projectable from the wiki, or
attributable. Text that has already been concatenated cannot be filtered per lane, cannot carry a
freshness stamp, and cannot say where it came from.

⚠ **The requirement is a projection, not a second source of truth.** `~/repos/wiki` stays canonical;
`factory-wiki` is a derived, task-oriented view of it. That constrains the schema in one specific
way: **every context item must carry a reference back to the wiki page it was derived from, and a
freshness/status stamp**, or the projection becomes an unfalsifiable copy — the exact failure the
corpus module already solved for eval data (`EVIDENT / ATTRIBUTED / SEPARABLE`).

### 3.5 🟡 No metric semantics — the DQ-001 shape

`PbiTarget.anchors: Dict[str, float]` says *"`ACOS` should equal 0.34"*. It cannot say *"`ACOS`'s
denominator is Amazon-attributed sales while the page it appears on shows all-channel spend."* A
technically-correct DAX measure under a label whose scope differs from its denominator passes every
assertion in M1–M12 and is still the defect that got escalated by the client. The business/semantic
validator has nothing structured to read.

### 3.6 🟡 No capability model, so `prohibition` is a request

The isolation ladder is designed (`architecture-v0.md` §4) and absent from code. Until an agent's
tier is a declared field the DECIDE plane enforces, *"must not deploy to production"* is a sentence
in a prompt. For this workflow that matters at exactly two hops — the Snowflake DDL step and the
Power BI deploy step — which are also the two with production blast radius.

---

## 4. What is NOT a gap

Recorded so nobody rebuilds it:

- **The four verdicts.** `PASS / FAIL / UNMEASURABLE / NOT_RUN` already exist, are never collapsed,
  and `UNMEASURABLE` already blocks promotion (`certify.main` returns non-zero for it). The
  verdict-model requirement is satisfied today.
- **Evidence basis.** `MEASURED | DERIVED | ASSUMED`, enforced at close.
- **Independent validation as a principal.** `evaluator.py` exists precisely so the graded agent is
  not the grader; `--calibrate` vs `--remote` are documented as *not* two flavours of one thing.
- **Provenance on a verdict.** Every certification records the corpus id and hash it was scored
  against, and prints `REPLAYED, not a live measurement`.
- **Rollback-before-mutation.** `PbiTarget.rollback_path` with M1 asserting it was captured *first*.
- **Refusal to merge.** `finish()` already draws the human-approval boundary in the right place.
- **Parallelism by conflict, not by count.** `lanes.py` groups by file locality and states that the
  ceiling is a *file* limit; `architecture-v0.md` §4 observes data work does not conflict that way.

---

## 5. NOW vs LATER

The test applied: **can this be reconstructed afterwards?** If yes, it waits. If the information is
lost at write time, it is NOW.

### Change during the PoC

| # | Change | Why now |
|---|---|---|
| **N1** | **Typed evidence classes** — `factory/evidence.py` with `TARGET / CONSUMER / REGRESSION / ROLLBACK`, and `tasks.add_evidence` validating `kind` against it | Write-time. Every row recorded with a free-string kind is unclassifiable forever. Gives the "four mandatory artifacts" a home that can report *missing*, not just *absent*. |
| **N2** | **Join keys on the run ledger** — `runs.record()` gains `job`, `team`, `team_version`, `agent_versions`, each defaulting to an explicit `NOT-RECORDED` rather than being omitted | Write-time, and R19's #1 finding. An omitted field reads as "no such question"; a `NOT-RECORDED` field reads as "nobody measured this", which is the honest state and shows up on the board. |
| **N3** | **`factory/context.py`** — typed `ContextRef` (kind, id, source, provenance, freshness, status, confidence) and `ContextPack`, with `Lane.full_prompt()` routed through it | Structural. Every further prompt-assembly decision made against a raw string is a decision to keep context unstructured, which is the one thing the wiki requirement asks to avoid. The seam has a live caller today. |
| **N4** | **Correct the stale PBI-team blocker** in `roadmap.TEAMS` — from *"no contract exists"* to *"a contract exists and no test has watched it refuse"* | Free, and the current text makes `python -m factory.launch` state something false about a file in this repo. |

**Explicitly NOT in the NOW set, with the reason:**

- **No `Job` object yet.** It is the largest gap (§1) and it is *reconstructible* — a job id is a
  string, and N2 reserves the column for it. Building it before **RUN-04** (`ticket → team entry
  point`) makes it exactly the speculative abstraction with zero callers that
  `execution-plane-2026-08-30.md` refuses on `RepoDeployer`'s evidence. **RUN-04 is its writer, and
  RUN-04 is two tickets away.**
- **No `AgentSpec.tier` field.** Adding it later re-hashes every agent version and voids
  certifications — but that is the deny-list working *as designed*, and today's certification
  covers one connector against one replayed corpus. The cost of invalidating it later is near zero.
- **No MetricContract yet.** See LATER; gated on one real metric being expressed by hand first.

### Add after the PoC

| Change | Gated on |
|---|---|
| **`Job` / outcome object** and its append-only store | RUN-04. It is the dominant UI object and the thing five lanes hang off. |
| **`MetricContract`** — scope, numerator, denominator, grain, currency, valid_dimensions, source_of_truth | One real metric expressed by hand first. `PbiTarget.anchors` should accept the richer form *alongside* the float shorthand so pinned blueprints do not break. |
| **Calibrate `pbi_contract`** — the `test_every_assertion_has_been_proved_able_to_fail` treatment for M1–M12 | Before any Power BI agent is dispatched. This is the real content of §3.1 and it is a proper ticket, not a note. |
| **Capability / tier enforcement** (T0/T1/T2, the ephemeral clone) | A second execution backend. A prose prohibition is honest about being prose until then. |
| **`factory-wiki` projection pipeline** | Paul's own condition: validate the schema against one real client workflow first. N3 makes the schema expressible without committing to an extraction pipeline. |
| **Warehouse GreenContract** (the Snowflake hop) | A real transformation to score. Today only the connector hop and the PBI hop have contracts; the middle has `plan_gates.g_the_warehouse_layer_is_representable` and nothing else. |
| **Environment-transition gate** (TEST → PROD as a sequenced, approved act) | The Job object. `PbiTarget.environment`/`allow_environments` already carry the declaration. |
| **Selector / optimiser over configurations** | The dispatch record from N2 having real rows in it. R19: anything presented as an optimiser before then is speculative. |

---

## 6. Decisions being made now that would make the golden workflow hard later

Stated as a checklist for the sessions that follow.

1. ⛔ **Assembling prompts by string concatenation.** Addressed by N3. Every new call site that
   concatenates instead of appending a `ContextRef` re-opens it.
2. ⛔ **Writing run rows without a job/config key.** Addressed by N2.
3. ⛔ **Free-string evidence kinds.** Addressed by N1.
4. ⚠ **Treating "a contract exists" as "a contract works."** §3.1 is the live example. The
   distinguishing test is whether anything has been *watched refusing*.
5. ⚠ **Letting the readiness gates and the delivery contracts merge.** They answer different
   questions about different repos; `plan_gates.py` already refuses to sum them and that must hold
   when a Job starts carrying both.
6. ⚠ **Modelling lanes as one flat parallel set.** The real DAG has *dependent* stages
   (connector → warehouse → PBI) with *independent* validators fanning off each. Five equal lanes is
   the fan-out, not the whole graph. `board.DEPENDS` + `teamplan._layers` already compute topological
   layers and are the right primitive to reuse.

---

## 7. What this note does not claim

It has not been validated against a real ticket. It is a reading of the code as of 2026-08-29
against a workflow description, and its §1 verdicts are `REPO-BACKED` while its §5 ordering is
`REASONED`. The first real client job to travel this path will correct it, and that correction is
worth more than anything further that could be designed in advance.

---

## 8. The two requirements this note records

Written out as requirements rather than only as gaps, so a cold session finds them by searching
for what was asked rather than for what was missing.

### R-A — the delivery shape

> **one ticket → five independent lanes → four mandatory evidence artifacts → explicit gate →
> sign-off**

The architecture must be able to represent this. Status after this session: **four of six elements
represented** (five lanes ✅, four artifacts ✅ *new*, explicit gate ✅, lane independence ✅ for
code). Still unrepresented: **the ticket** (no Job object — RUN-04) and **sign-off** (no typed
approval bound to an environment transition). §2.1 has the row-by-row.

The five lanes are **not a flat parallel set**. The real graph is a pipeline with validators
fanning off each stage — source → warehouse → semantic model, each with an independent validator,
plus one semantic/business validator that depends on none of them and can run first. `board.DEPENDS`
+ `teamplan._layers` already compute topological layers and are the primitive to reuse.

### R-B — the operational knowledge layer

> The company wiki holds the majority of company, engineering, client, architecture, data, metric,
> historical-issue and operating knowledge. Agent Factory must **not** ingest that corpus blindly
> into every agent prompt. A `factory-wiki` layer should be a **derived, task-oriented projection**
> of the existing wiki — never a second independent source of truth. Agents receive **context packs
> relevant to their lane/task**, not the whole corpus.

Kinds the architecture must eventually resolve: `CompanyContext`, `RepoContext`, `ClientContext`,
`SourceContract`, `DatasetContract`, `MetricContract`, `ContextPack`, plus provenance/source
reference and knowledge freshness/confidence/status.

**Extraction is deliberately NOT built.** The schema gets validated against one real client
workflow before anything is automated across the wiki. What landed this session is only the
schema allowance — `factory/context.py` — chosen so that no decision taken between now and then
requires context to be one unstructured blob:

| Constraint | How it is held |
|---|---|
| every item points back at its origin | `ContextRef.source` is **required and non-empty**; construction raises without it |
| freshness is a measurement, not a label | `status` defaults to `UNVERIFIED`; `CURRENT` without a `checked` date raises |
| fresh and trustworthy are different questions | `status` and `confidence` are separate fields |
| selection, not ingestion | `ContextPack.of_kind()`; an agent asks for the kinds its lane needs |
| provenance is queryable without parsing prose | `ContextPack.sources()` |
| the seam has a real caller today | `Lane.context()`; `full_prompt` renders it **byte-identical** to the concatenation it replaced (`tests/test_context_pack.py`) |

⚠ **`ContextRef.data` is deliberately untyped.** The structured payload for a `MetricContract` —
numerator, denominator, scope, grain, currency, valid dimensions — is the schema that R-B says to
validate against one real workflow first. Fixing it in code now would be guessing at the answer to
the question this exercise exists to ask.

