# Mission — `marketing-model-reconstruction-v1`

**Written 2026-08-31.** Prepared under ChatGPT revision 1 (2026-08-31): run one bounded real mission
first, with manual session launching, and use it to generate evidence about what session
coordination actually needs. **Read-only. No client state may be modified.**

---

## 0. Three corrections to the premise this mission was handed

⚠ Revision 1 says to run this *"using Agent Factory's existing mission/task/DAG/state/claim
mechanisms."* Measured 2026-08-31, **that names two things that do not exist**, and misses one
blocker and one unblock. Correcting an inherited premise is a deliverable, so it is stated first.

### 0.1 There is no mission concept, and no task DAG

```
grep -rn --include=*.py -iE '\bmission\b' factory/     ->  no matches
grep -rn --include=*.py -iE 'depends_on' factory/      ->  no matches
```

`board.DEPENDS` is a **gate** dependency map, not a task DAG. `factory/lanes.py` validates every
lane's gate ids against `readiness.GATES` **at import**, so a lane must be composed of existing
readiness gates — *"Snowflake Cartographer"* cannot be a lane. Any plan that assumes it can is
planning against a system that is not there.

### 0.2 But `TaskStore` supplies both, with no new infrastructure

`factory/tasks.py` already carries exactly the shape this mission needs:

| Need | Existing mechanism |
|---|---|
| mission → task hierarchy | `create(title, actor, parent)` — `parent` is the mission task's id |
| dependency edges | `block(tid, by, actor)` / `unblock(...)`, folded into `Task.blocked_by` |
| task state | `OPEN · CLAIMED · BLOCKED · DONE · ABANDONED` |
| ownership | `claim(tid, actor)` |
| evidence, typed | `add_evidence(kind, ref, actor, basis, evidence_class)` — `basis` is validated to `MEASURED \| DERIVED \| ASSUMED` |
| **cannot close without evidence** | `close(require=...)` raises `EvidenceRequired`; *"an assumed 'proof' is not a proof"* |
| append-only, replayable | every mutation is an event; state is a fold |

**So the mission is a parent task and every task is a child of it.** Nothing new is built.

⚠ `TaskStore` has four consumers total (`demo.py`, `scripts/export_board.py`,
`scripts/local_tracker.py:964`, tests). This mission is its first real use — a wire-and-run, so
expect to find defects in it rather than in the mission.

### 0.3 The run was blocked by F90 — and manual launching is what routes around it

`boot-prompts/bootstrap-and-instruments-2026-08-31.md:6`:

> `next:` **decide F90 remedy (a)** — thread the repository through `worktrees.ensure` and the
> providers — or accept that **the first supervised run cannot happen.** Nothing else unblocks it.

F90 is *"`TeamSpec.repo` is inside the version hash and the controller ignores it, so a certified
team runs in the wrong repository."* That blocks the **automated** path — `factory.control` →
`provider` → worktree.

⭐ **Revision 1's "manual launching" sidesteps F90 entirely.** The operator starts each session in
the right directory himself; no provider resolves a repo, so the defect cannot fire. The structured
controls — task ids, dependencies, claims, contracts, evidence — all live in `TaskStore` and
`claims`, neither of which touches the provider path.

**This mission therefore does not need F90 fixed.** That is the whole reason to run it manually
first, and it should be stated in the AAR as the first measured argument for the sequence.

### 0.4 The subject is not greenfield

`boot-prompts/workflow-library-2026-08-31.md`'s `next:` is *"run `keel` on the GEP marketing
model"*, described as *"still the client-facing priority."* And two wiki pages already exist,
created 2026-08-30:

- `concepts/architecture/cross-channel-marketing-attribution.md` — *"our tiered measurement law and
  locked decisions"*
- `concepts/architecture/cross-channel-marketing-dimensional-model.md` — external evidence, graded,
  sourced from Kimball DW Toolkit, `fivetran/dbt_ad_reporting`, `snowplow/dbt-snowplow-attribution`
  and Microsoft Power BI guidance

⛔ **So ChatGPT's task B — "repo + wiki history reconstruction" — is substantially already done.**
Running it as drafted would re-derive a page written eight days ago. B is rescoped below to *read
and diff* rather than reconstruct, and the `keel` skill is the named instrument for the design half.

### 0.5 The subject is the **Navira** model, and more prior art sits in a second repo

⚠ The mission task's title says *"GEP cross-channel marketing model"*, taken from the boot prompt.
That is the **client**, and it is not wrong — but it is imprecise, and the imprecision would have
sent R2 and R3 looking for the wrong object names. Measured 2026-08-31:

- `wiki/entities/clients/active/` holds exactly two clients — `GEP.md` and `fusion92.md`. **Navira
  is not a client; it is an entity inside GEP's marketing data.**
  `wiki/entities/repos/navira-marketing-dashboard.md:18` — *"Two entities today: Navira (role HOUSE)
  + Lectric (role AGENCY, sales-only, no ad spend)"*, dimension `REPORT_COMMON.MARKETING_DIM_AGENCY`.
- `GP-319`'s own readout is titled **"Navira Marketing Model Designs"** — 2 Navira mentions, **0
  GEP mentions**. `GP-322` is *"Navira Amazon ad-cost allocation reading 3.6× campaign spend"*.

**So `GP-*` is the GEP Jira project; the modelled subject is Navira.** The task title in the
append-only store is left as written — the store cannot be rewritten and the client name is
accurate — but every task should search for **Navira**-named objects.

⛔ **And three prior artefacts live in `aldc-launchpad`, not here:**

- `aldc-launchpad/docs/readouts/gp319-marketing-model-designs.html` — *three designs, the core-10*
- `aldc-launchpad/docs/readouts/NAVIRA-MARKETING-MODEL-GUIDE.html` and `.pdf`

**R2's scope therefore includes `aldc-launchpad/docs/readouts/`, not only the wiki.** A diff that
reads one repo and reports "no prior design exists" would be a blind instrument — three designs
already exist.

---

## 1. The mission

**`marketing-model-reconstruction-v1`** — reconstruct the requirements and candidate dimensional
design for the **GEP cross-channel marketing model**, read-only, ending in a recommendation a human
signs off.

**Instrument:** the `keel` skill for the design tasks (D2–D4). It already declares the grain before
designing, censuses every measure against every axis so an inert one cannot ship looking healthy,
and separates `MEASURED / DERIVED / NOT-REPORTED / SENTINEL` so an absence never renders as zero.

---

## 2. Tasks, dependencies and resource scope

```
   R1 ──┐
   R2 ──┼──▶ D1 ──▶ D2 ──▶ D3 ──▶ D4 ──▶ D5
   R3 ──┘
```

| id | Task | Blocked by | Resource claim | Access |
|---|---|---|---|---|
| **R1** | Stakeholder & client-evidence reconstruction — what did GEP actually ask for, and when | — | `res:gep-evidence` | READ |
| **R2** | Repo + wiki **diff**, not reconstruction — read the two existing pages, state what is locked, what is stale, what is missing | — | `res:wiki`, `res:clients-repo` | READ |
| **R3** | Snowflake / data cartography — what marketing data exists, at what grain, with what keys | — | `res:snowflake-read` | READ ⚠ credential |
| **D1** | Requirements & uncertainty synthesis — what is CONFIRMED vs SUPPORTED vs INFERRED vs ASSUMPTION vs UNKNOWN | R1, R2, R3 | `res:mission-artifacts` | WRITE |
| **D2** | Analytical question catalogue — the questions the model must answer | D1 | `res:mission-artifacts` | WRITE |
| **D3** | Candidate dimensional designs — **run `keel`**; declare the grain first | D2 | `res:mission-artifacts` | WRITE |
| **D4** | Skeptical review — try to falsify D3's grain and key claims | D3 | `res:mission-artifacts` | WRITE |
| **D5** | Recommendation + human sign-off | D4 | `res:mission-artifacts` | WRITE |

**Wave 1 is `[R1, R2, R3]` — three sessions in parallel.** All three are READ on disjoint scopes,
so `claims.task_claim()` will grant all three. Everything after is serial: D1–D5 all write
`res:mission-artifacts`, so the claim refuses a second writer. **That refusal is the negative
control** — see §5.

**R3 requires Snowflake read credentials, and they are covered by a standing grant** — see §2.1.
Wave 1 is three sessions, not two.

### 2.1 Credentials — the standing grant, and the failsafe it depends on

Paul granted standing credential use for work driven from this repo on 2026-08-31, replacing the
global ask-every-time rule **here and only here**. That moves the human gate from *before* the
retrieval to *after* it, so the "after" has to be real or the grant is indistinguishable from no
policy.

⭐ **For a read-only mission the failsafe is not a rollback — it is a proof that no rollback can be
needed.** A revert script for a mission that writes nothing is theatre. The control that actually
binds is proving, before the first real query, that the credential *cannot* mutate.

**Pre-flight, in order, before R3 runs a single real query:**

1. **Prove read-only.** Inspect the role's grants, and attempt one scoped write and confirm it is
   refused. Record the refusal as evidence with `evidence_class` = the target class. A role assumed
   read-only is an assumption; a role watched refusing a write is a measurement.
2. **Bound the cost.** Set a statement timeout and confirm the warehouse size before the first
   query. A runaway read is still a runaway.
3. **Capture the value only in a subshell** — `VAR=$(az keyvault secret show ...) cmd` — so it never
   becomes a variable, a log line, a tool result or a commit.
   ⚠ Sharper than it used to be: `docs/evidence/switchboard-security-preflight-2026-08-31.md`
   measured that a session manager indexes **the first 500 characters of each of the first ~16
   messages** into a substring-searchable FTS table. A credential in an early prompt becomes durably
   searchable, and Q8 of that preflight says deletion does not stick.
4. **Log the use** — `python scripts/credential_use.py --secret <NAME> --source <SOURCE> --task R3
   --access READ --purpose "..."`. Name and source only; the script refuses a value-shaped argument
   and was watched refusing one (exit 1, and **the log file is not created by a refused call**, so a
   rejected value never reaches disk).

**What the grant did NOT cover.** It removed the retrieval prompt, not the deploy gate. Any
production write, schema change, PROD promotion or shared-model edit still stops for a human and
still needs target + consumer-layer + no-regression + captured-rollback evidence. This mission is
read-only, so none of those should arise — and if one does, that is a stop condition, not a
permission question.

---

## 3. Per-task contract

Each task carries, recorded in `TaskStore` at creation:

```
task_id            from TaskStore.create()
parent             the mission task id
objective          one sentence
depends_on         via block(tid, by=...)
resource_claim     the key passed to claims.task_claim()
access             READ | WRITE
inputs             named artefacts or sources
expected_outputs   a file path under docs/evidence/marketing-model-v1/
estimate           recorded BEFORE launch — this is the point of run 1
stop_conditions    when to stop rather than push through
evidence_class     which of factory.evidence's four questions the output answers
capability_class   FAST | ROUTINE | STRONG | DEEP
model              the model actually used, recorded — not chosen per task in run 1
effort             the effort actually used, recorded
```

### 3.1 Model and effort — baseline everything, record everything, route nothing

**Run #1 baseline: Opus 5 at effort 5 for every reasoning task**, without exception, unless a task
is already deterministic and needs no LLM at all. No task drops to a cheaper model on intuition.

⛔ **No model routing is implemented in this mission.** The point of run #1 is to *record* model and
effort per task alongside duration, retries and outcome. Routing optimised before that data exists
is a guess wearing a policy's clothes — the same error as tuning a gate before anything has run.

⭐ **`capability_class` is the durable field; `model` is the record of what ran.** A contract that
names `claude-opus-5` is coupled to a model generation and rots at the next release; one that names
`DEEP` survives it. The class → model mapping is configuration, versioned separately, and is what
routing optimises *later*.

In the future Session/Mission UI these are properties of the task execution contract, carrying a
**Factory recommendation** and a **human override that wins** — never a single global default, and
never silently inherited from the parent session.

Provisional classes for this mission, recorded as `ASSUMED` and to be checked against run 1:

| Tasks | Provisional class | Why |
|---|---|---|
| R1, R2 | `STRONG` | reading and diffing existing evidence |
| R3 | `STRONG` | cartography is query + judgement about grain |
| D1, D3, D4 | `DEEP` | synthesis, grain design, adversarial falsification |
| D2, D5 | `STRONG` | catalogue and write-up over settled inputs |

All of them run at the Opus 5 / effort 5 baseline in run #1 regardless. **The table is a hypothesis
the run tests, not a routing rule the run obeys.**

**Stop conditions that apply to every task:**

- Any write to a client system → stop. This mission is read-only.
- A credential is needed that has not been explicitly approved → stop and ask.
- A Claude inference is about to be recorded as a confirmed client requirement → stop. Provenance
  is mandatory; `basis` must be `MEASURED` or `DERIVED`, never silently `ASSUMED`.
- Three refuted hypotheses on the same question → stop and re-scope rather than continue.

---

## 4. Instrumentation — recorded from run 1

Per revision 1, the coordination cost is the *point*, not a by-product. Recorded per task:

```
estimate_minutes            recorded before launch
actual_minutes              wall clock
manual_launches             operator started a session
manual_context_copies       operator pasted context by hand
status_checks               operator went looking for state
unnoticed_waiting_minutes   task READY but nobody launched it
permission_interventions    including every credential approval
dependency_mistakes         launched something whose inputs were not ready
duplicate_work              two tasks derived the same thing
conflicting_work            two sessions touched the same artefact
resume_recovery_actions
human_coordination_minutes  vs
agent_execution_minutes     vs
blocked_minutes

capability_class            the class declared before launch (hypothesis)
model                       what actually ran
effort                      what actually ran
```

⭐ **`capability_class` vs `model`/`effort` is the routing dataset.** Every task runs the Opus 5 /
effort 5 baseline, so run 1 cannot compare models — what it *can* establish is whether the declared
class predicted the work's actual difficulty, measured by duration, retries and review findings.
That is the input to routing, and it is the only honest thing one run can produce about it.

⛔ **Unknown cost is not zero.** `factory/runs.py` already draws `RECORDED / RECONSTRUCTED /
NOT-RECORDED`; use the same three verdicts here rather than defaulting a missing figure to 0.

---

## 5. Acceptance — with the negative control that makes it falsifiable

The success condition must not be a set of zeros from instruments never proved able to see. So:

| # | Claim | How it is proved |
|---|---|---|
| 1 | three tasks ran in parallel | three `task_claim` grants, three concurrent sessions |
| 2 | dependencies blocked correctly | D1 is `BLOCKED` until R1, R2, R3 all close |
| 3 | **conflicting writers were refused** | ⭐ **negative control: attempt to claim `res-mission-artifacts` from a second session while D1 holds it, and record the refusal.** ✅ **Run 2026-08-31 — watched refusing:** *"res-mission-artifacts is already running as pid 2984… Starting a second one would put two agents on the same file, and the loser's work disappears without an error."* |
| 4 | no task closed without evidence | ✅ **Run 2026-08-31 — watched refusing:** `EvidenceRequired: task 2b9aae3b cannot close as done: no MEASURED or DERIVED evidence attached (0 assumed-only item(s))`, and the refused close **appended nothing** (205 rows before and after) |
| 5 | mission survives a session ending | close a session mid-task; task state is unchanged in `TaskStore` |

**3 and 4 are the load-bearing ones.** 1, 2 and 5 can pass over an absence; 3 and 4 cannot. Both
were run before the mission, which is the right time — a guard first exercised during the work it
is guarding has not been tested, it has been trusted.

### 5.1 ⛔ The claim must record the CLAUDE session's pid, not the launching shell's

Establishing check 3 took two attempts, and the first one produced a *plausible wrong answer* rather
than an error — the shape this estate keeps paying for.

`sessions._running_pids()` runs `tasklist /FI "IMAGENAME eq claude.exe"` — **it enumerates live
Claude CLI processes only**, because `task_claim` exists to guard work a button spawns. A first
attempt claimed with a *python* pid, got `HELD-GONE`, and the second claim was granted. That reads
as *"the conflict detector is inert"* and it is not: `HELD-GONE` was the correct answer to the wrong
question. Re-run with a real live `claude.exe` pid, the guard refuses exactly as designed.

**So the operational requirement is:** whoever claims a resource must pass the **pid of the Claude
session doing the work**. A claim carrying a shell's pid, a wrapper's pid, or no pid is not a guard
— `HELD_UNVERIFIED` fails closed and refuses, but a claim naming a *dead-looking* non-Claude pid
silently frees the resource for a second writer.

⚠ This is a real limit on the mechanism, not a bug: `task_claim` can only guard work whose holder is
a `claude.exe`. Any future non-Claude worker (a scheduled job, a Python task, a container) is
outside what this guard can see, and that must be stated rather than assumed away.

---

## 6. What this mission is NOT allowed to do

No Power BI changes. No Snowflake writes. No deployment. No shared semantic-model edits. No Claude
inference promoted to a confirmed client requirement without provenance.

⚠ Credentials are now covered by a standing grant (§2.1) — so the constraint that binds is no longer
*"was it approved"* but **"was it proved read-only, bounded, uncaptured and logged."** Those four are
checkable after the fact; "he said yes" is not.

## 7. Deliberately deferred

The Session Controller (frozen per revision 1). Automated merging. Any Switchboard use — blocked by
`docs/evidence/switchboard-security-preflight-2026-08-31.md` until the redaction question is
settled. The F90 remedy, which this mission routes around rather than fixes.
