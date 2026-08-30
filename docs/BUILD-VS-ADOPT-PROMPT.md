# Build vs adopt — what this system is, and which parts of it already exist as tools

**Written 2026-08-29.** Purpose: before CIP-07 (the questionnaire, on the critical path) commits us
to more building, establish **which components of this system are genuinely novel and which are
re-implementations of mature tooling.** Contains (1) a grounded description of what exists, (2) a
component-by-component build/adopt question set, (3) a research prompt to run externally or in-repo,
(4) a candidate landscape — **explicitly labelled as unverified recall**, to be checked, not trusted.

---

## Part 1 — What this actually is

### The one-sentence version

> An **evidence-gated factory for building and certifying data connectors with AI agents**, whose
> organising thesis is that *a green light from an instrument that cannot produce a red is worthless* —
> so every gate ships with proof it can fail, and "we could not measure this" is a first-class verdict
> that never rounds up to "pass".

### Measured size (`find … | xargs wc -l`, 2026-08-29)

| Area | Lines | Note |
|---|---|---|
| `factory/` | 8,886 | 38 modules — the library |
| `scripts/` | 4,918 | of which `local_tracker.py` is 2,470 — the live instrument surface |
| `tests/` | 3,873 | **304 passing** |
| `docs/` | 54,232 across 89 files | 18 research passes, a 2,422-line synthesis, findings ledger |

### The three layers that exist and run today

**1. A certification battery for a connector run — `factory/connector_contract.py`.**
Twelve assertions, each independently able to fail, ordered so that later ones catch what earlier
ones structurally cannot:

```
A1  config-satisfiable        connection + options construct for this account
A2  credential-authenticates  live auth, NOT vault presence
A3  exact-image-resolves      the digest that will run imports the connector
A4  deployment-binding        the deployment pins the digest A3 proved
A5  regression-suite          pinned suite green at the pinned revision
A6  run-completed             "necessary, insufficient — see A7"
A7  fresh-landing-proven      rows stamped with THIS run's session id
A8  load-fidelity             landed == emitted
A9  semantic-invariants       the connector's own declared meaning
A10 source-agreement          an independent second instrument
A11 no-forbidden-action       policy scan
A12 tenancy-scope             no other client's rows landed here
```

The design tell is A6→A7: "the run completed" is explicitly recorded as *insufficient*, because a
completed run that wrote nothing looks identical to a successful one. A10 requires a **second,
independent instrument** — the same corroboration rule your analysis gate uses.

**2. A measurement layer that refuses to lie — `factory/readiness.py` (1,200 lines, 27 gates).**
Four verdicts, not two:

```
PASS · FAIL · UNMEASURABLE (no instrument could be established — NOT a pass) · NOT_RUN
```

And in its own words: *"Windowing is NOT forgiving. An empty window is UNMEASURABLE, never PASS."*
Certification output self-labels provenance — the live run today prints
`REPLAYED, not a live measurement`, so a replay can never be quoted as a fresh result.

**3. An append-only, evidence-gated work ledger — `factory/tasks.py`.**
Event-sourced JSONL. The two enforcement points are the interesting part:

- `add_evidence(basis=…)` **raises** unless basis is `MEASURED | DERIVED | ASSUMED`.
- `close(status=DONE)` **refuses** unless at least one `MEASURED` or `DERIVED` item is attached —
  *"an assumed 'proof' is not a proof."*

Around these sit lane claiming with atomic cross-platform file locks (`claims.py`, 390 lines —
handles the Windows `EACCES`-vs-`EEXIST` race), git-worktree isolation per lane (`worktrees.py`),
a run ledger (`runs.py`), mutation testing (`evals.py: mutate_and_expect_failure`), Goodhart-guarded
metrics (`metrics.py` refuses an activity metric with no paired outcome metric), and a session/job
registry that surfaces blocked agents' questions to a human (`sessions.py`, plus a
WindowsTerminal-flashing hook).

**4. A live instrument surface — `scripts/local_tracker.py --serve` (2,470 lines).**
Re-measures on every HTTP request rather than serving a snapshot. Its docstring states the rule the
whole project turns on: *"A tracker that can quietly show yesterday's state is the drift this whole
project exists to remove."* The single cache it permits carries its own age inside the same string
as its number.

### What is planned but does not exist (CIP-01…20)

A **client intake platform**: a structured 20–30 question form whose answers become the
machine-checkable contract that A1–A12 later judge. The load-bearing design claim is that
**the questionnaire and the acceptance test are the same artefact** — a field the client declares
becomes an A9 semantic invariant, and a field they never declare cannot silently appear in week six
because it fails the contract on the first run. Per plan §0.4 this is a **front end on stages B1–B2**
of the existing 7-stage delivery pipeline, not a new pipeline.

### The theses worth testing against the market

These are what make it more than a bag of scripts, and they are what the research below must price:

1. **Negative controls as a shipping requirement.** Every gate must demonstrate it can fail.
   Precedent: a `bash-guard.sh` in this estate exited 127 and blocked nothing for months while
   reporting success.
2. **`UNMEASURABLE` as a verdict distinct from failure.** Absence of an instrument must not render
   as a pass — nor as a fault.
3. **Provenance labels enforced at the API boundary**, not by convention. You cannot close work as
   done with assumed evidence, because the function raises.
4. **Replay vs live is always stated.** A score carries whether it was measured or replayed.
5. **The spec and the test are one artefact**, elicited from a non-technical stakeholder.
6. **Instruments re-measure by default**; caching requires the number to carry its own age.

---

## Part 2 — The build-vs-adopt questions, component by component

Ordered by **how likely I think it is that a mature tool already does this** — highest first, since
those are where adoption saves the most and where re-implementation costs most.

| # | Component | Where it lives | The question |
|---|---|---|---|
| 1 | **Data contract: declare a feed's grain, required fields, invariants, tenancy** | `contract.py`, `connector_contract.py`, planned CIP-08/10 | Is there a standard contract format + validator to adopt rather than invent? Would adopting one make the questionnaire an editor for a **standard** artefact rather than a bespoke one? |
| 2 | **Assertion battery over landed data** (A7–A10: freshness, row-count fidelity, semantic invariants, source agreement) | `connector_contract.py` | These are canonical data-quality checks. Is A1–A12 re-implementing an existing assertion framework, and what would be lost by delegating A7–A10 to one and keeping only the parts that are genuinely ours (A3/A4 digest-pinning, A12 tenancy)? |
| 3 | **Readiness scorecard: N gates over a service, with levels** | `readiness.py` (27 gates) | Service-maturity scorecards are a whole product category. Does an existing one support a **four-verdict** model including `UNMEASURABLE`, or do they all collapse to pass/fail? *(This is the sharpest discriminating question in the document.)* |
| 4 | **Mutation testing / proving a check can fail** | `evals.py`, `scripts/mutate_readiness_probes.py` | Mature tools exist for mutating *code*. Do any exist for mutating *a gate's input* to prove the gate reacts? Is our negative-control discipline a thin wrapper over one? |
| 5 | **Durable, append-only, resumable work ledger** | `tasks.py`, `runs.py`, `claims.py` | This is event sourcing plus a distributed lock, hand-rolled onto JSONL and files. Is a durable-execution engine the right substrate, or is it far too heavy for a 3-lane single-workstation ceiling? |
| 6 | **Agent orchestration: spawn N bounded agents in isolated worktrees** | `deploy.py`, `lanes.py`, `worktrees.py` | Several frameworks do multi-agent orchestration. Ours adds per-session dollar caps and a persisted retry ledger. Are those now built in elsewhere? ⚠ Note `deploy.py` is currently **unwired** — nothing calls it — so adopting here costs the least. |
| 7 | **Client-facing intake form → structured artefact** | planned CIP-09/10/11 | Form builders and schema-driven form generators are commodity. Building a bespoke form is almost certainly wrong. Which one emits JSON/YAML conforming to a schema, and can **pre-fill from a live schema probe** so clients confirm rather than type? |
| 8 | **Eval corpus with held-out fixtures + manifest hashing** | `evals/`, `MANIFEST.sha256`, `corpus.py` | Eval-harness tooling has matured fast. Is our corpus/replay mechanism a worse version of an existing harness? |
| 9 | **Lineage / "which object does the consumer actually read"** | not built; recurring pain in the estate | Column-level lineage is a mature category and would directly serve the evidence rule about proving the target before deploying. |
| 10 | **The composite: evidence-gated agent delivery with refusal semantics** | the whole thing | **Probably genuinely novel.** The research must confirm nobody has assembled this, and if someone has, whether they solved the refusal-semantics problem better. |

**Working hypothesis to attack:** items 1, 2, 3, 7, 8 and 9 are largely solved by existing tools;
items 4 and 10 are where the original contribution is; items 5 and 6 are judgement calls dominated
by "the ceiling is three lanes on one Windows workstation", which rules out most heavyweight
infrastructure regardless of merit.

---

## Part 3 — The prompt

*Paste into a deep-research tool with live web access, or run in-repo with the `prospect` /
`deep-research` skill. It is written to be adversarial about its own conclusion, because the
comfortable answer ("keep building, ours is special") is the expensive one.*

---

> ### Research task: build-vs-adopt for an evidence-gated agent delivery factory
>
> I have a working Python system (~14k lines, 304 tests) that uses AI agents to build and certify
> data connectors, and I am about to invest heavily in its next component. Before I do, I need to
> know **which parts of it are re-implementations of mature tooling**, so I can adopt instead of
> build, and **which parts are genuinely novel**, so I can concentrate my effort there.
>
> **What the system does**
>
> 1. **Certifies a data-connector run** against 12 ordered assertions: config constructs; credential
>    performs a live auth (not merely "a secret exists in the vault"); the exact container digest
>    that will run imports the connector; the deployment pins that digest; a pinned regression suite
>    is green at the pinned revision; the run completed; rows landed stamped with *this* run's
>    session id; landed row count equals emitted; declared semantic invariants hold; an independent
>    second instrument agrees with the source; a policy scan finds no forbidden action; and every
>    landed row is within the declared tenant scope.
> 2. **Reports four verdicts, never two:** PASS, FAIL, **UNMEASURABLE** (no instrument could be
>    established — explicitly *not* a pass), NOT_RUN. An empty measurement window is UNMEASURABLE.
> 3. **Labels provenance on every result** — a replayed score is printed as "REPLAYED, not a live
>    measurement" and can never be quoted as fresh.
> 4. **Enforces evidence at the API boundary** — an append-only event-sourced task store where
>    attaching evidence requires a basis of MEASURED / DERIVED / ASSUMED, and closing work as *done*
>    raises an exception unless MEASURED or DERIVED evidence is attached.
> 5. **Requires negative controls** — every gate must ship with a demonstration that it can fail,
>    because a guard script here once exited 127 and blocked nothing for months while reporting
>    success.
> 6. **Orchestrates bounded agents** in isolated git worktrees with per-lane claims, per-session
>    dollar caps and a persisted retry ledger.
> 7. **Serves a live instrument surface** that re-measures on every request rather than serving a
>    cached snapshot; the one permitted cache must carry its own age in the same string as its value.
> 8. **Planned next:** a client-facing questionnaire whose answers become the machine-checkable
>    contract the 12 assertions later judge — i.e. the spec and the acceptance test are one artefact.
>
> **Constraints that disqualify otherwise-good answers**
>
> - Small team, **one Windows workstation**, no platform team, no SaaS budget assumed. A sandbox
>   feature that requires WSL2 or Linux is not adoptable as-is — say so explicitly if it applies.
> - Concurrency ceiling is **three lanes**, and it is a *file* ceiling, not a compute one. Do not
>   recommend infrastructure designed for hundreds of concurrent workers without pricing the
>   operational cost of running it for three.
> - The existing stack is Python, Prefect, Snowflake, Power BI, git worktrees.
> - Adopting a tool must not cost the four-verdict model. **Collapsing UNMEASURABLE into FAIL or
>   PASS is a disqualifying regression**, not a minor tradeoff.
>
> **What I want back**
>
> For **each** of these ten components, answer separately:
> data contract format/validator · assertion battery over landed data · service readiness scorecard
> · mutation testing of gates · durable append-only work ledger · bounded multi-agent orchestration
> · client intake form → structured artefact · eval corpus with held-out fixtures · column-level
> lineage · the composite system.
>
> For each, give me:
>
> | Field | Requirement |
> |---|---|
> | **Verdict** | ADOPT / ADAPT / BUILD — one word, committed |
> | **Best candidate** | name, URL, licence, and **whether it is actively maintained** (last release date, not vibes) |
> | **What it does that I would delete** | be specific about which of my modules becomes unnecessary |
> | **What it cannot do** | specifically: does it support a verdict meaning "not measurable", or force pass/fail? |
> | **Migration cost** | rough, and say what would have to be rewritten |
> | **Evidence tier** | OBSERVED (I read the source or docs) / REPORTED (a third party says so) / MARKETED (vendor claim). **A vendor claim is never sufficient for an ADOPT verdict.** |
>
> **Then answer the four questions I actually care about:**
>
> 1. **Which single component would save me the most work if I adopted rather than built?** Name one.
> 2. **Which of my ideas is genuinely uncommon?** Specifically: (a) UNMEASURABLE as a first-class
>    verdict, (b) evidence-basis enforced at the API boundary rather than by convention, (c) negative
>    controls mandatory for every gate, (d) spec-and-test-as-one-artefact elicited from a
>    non-technical stakeholder. For each, tell me if prior art exists and name it.
> 3. **What am I about to build that already exists and I clearly do not know about?** This is the
>    most valuable thing you can tell me.
> 4. **What is the strongest argument that I should NOT adopt anything** and should keep the
>    hand-rolled stack? Steelman it — small team, no platform overhead, full control of semantics.
>
> **Rules for your answer**
>
> - **Cite by URL and state what you actually read** — repo, docs page, or release notes. State the
>   line or section. If you could not access something, say NOT-VERIFIED rather than inferring.
> - **State the size of every source you read** (line or page count). A summary read as if complete
>   is worse than no read: an external review of this repo once judged a 2,422-line decision record
>   having seen 422 lines of it, and did not know.
> - Distinguish **ABSENT** (I searched and it does not exist) from **NOT-FOUND** (I could not find
>   it) from **EXISTS-BUT-UNMAINTAINED**. These are different answers and I will act on them
>   differently.
> - Prefer **specific repos over categories**. "Use a data quality framework" is useless; "use X, it
>   does A7–A10, here is the file that implements it" is the answer.
> - If a component has **no good candidate**, say so plainly. A confident BUILD verdict is a real
>   finding, not a failure to search.

---

## Part 4 — Candidate landscape

⚠ **BASIS: `RECALLED / UNVERIFIED`.** This is my prior knowledge, not a search result. I have not
opened any of these, checked whether they are maintained, or confirmed they do what I remember.
**Treat every row as a lead to check, never as a finding** — this is exactly the class of claim this
repo's own rules say must be verified before it is acted on. It exists to stop the research above
starting from a blank page, nothing more.

| Component | Leads worth checking first |
|---|---|
| **Data contracts** ⭐ | `datacontract-cli`, Open Data Contract Standard (Bitol/Linux Foundation), PayPal's data contract template, Gable, Schemata. **Check this first** — it is the closest thing to CIP-08/10, and adopting a standard would make the questionnaire an editor for a portable artefact instead of a bespoke one. |
| **Assertions over landed data** ⭐ | Great Expectations, Soda Core, dbt tests + `dbt-expectations`, Dagster asset checks, Elementary, deepchecks. Directly overlaps A7–A10. |
| **Readiness scorecards** ⭐ | Cortex, OpsLevel, Backstage + Soundcheck, Port, Score/Humanitec. Overlaps `readiness.py` almost exactly in *shape* — the discriminating question is whether any supports a fourth verdict. |
| **Mutation testing** | `mutmut`, `cosmic-ray`, Stryker. These mutate source code; whether anything mutates *gate inputs* is the real question. |
| **Durable/append-only execution** | Temporal, Restate, DBOS; plus plain event-sourcing patterns. Very likely too heavy for a three-lane ceiling — but worth pricing once so the decision is recorded rather than assumed. |
| **Agent orchestration** | LangGraph, AutoGen, CrewAI, OpenHands, SWE-agent, Aider. Cheapest place to adopt, since `deploy.py` is unwired today. |
| **Eval harnesses** | Inspect (UK AISI), promptfoo, DeepEval, Ragas, Braintrust, OpenAI Evals. Relevant to `evals/` + corpus + manifest hashing. |
| **Observability for agent runs** | Langfuse, LangSmith, W&B Weave, OpenLLMetry. |
| **Lineage** | OpenLineage/Marquez, SQLMesh column lineage, sqlglot lineage, dbt exposures. Would serve the "prove which object the consumer reads" rule directly. |
| **Policy gates** | Open Policy Agent + Conftest, Semgrep. Candidate substrate for A11. |
| **Schema evolution / breaking changes** | Buf (protobuf), Confluent Schema Registry compatibility modes. Relevant to "an undeclared field cannot appear in week six". |
| **Intake forms** | Formbricks (OSS), Typeform/Tally, plus JSON-Schema-driven form generators (`react-jsonschema-form`, JSONForms). Almost certainly ADOPT — do not hand-build a form. |

**My honest prior, to be attacked rather than believed:** the strongest adopt candidates are
**data contracts** (CIP-08/10) and **intake forms** (CIP-09/10); the strongest build case is the
**refusal semantics** — `UNMEASURABLE` as a verdict and evidence-basis enforced in code — which I do
not recall seeing as a first-class feature in any scorecard or data-quality product. If that holds
after checking, it is also the thing worth writing up publicly.

---

## How to run this

- **External:** paste Part 3 into a deep-research tool with live web access. Then verify a sample of
  its citations against the real repos before acting — an external pass on this repo has already
  been caught reporting a fixed bug as live, from a truncated read it did not disclose.
- **In-repo:** the `prospect` skill covers exactly this shape ("should we build X", incumbent study,
  build-vs-defer, evidence tiering, ABSENT vs UNSEARCHABLE) and will tier claims rather than accept
  vendor copy. `deep-research` is the alternative if the answer wanted is a survey rather than a
  decision.
- **Either way:** the output belongs in `docs/reviews/`, and every ADOPT verdict should become a
  ticket in `.data/tasks.jsonl` with the migration cost as its acceptance criterion.
