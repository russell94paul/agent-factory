# `.agent-platform` delta synthesis

**Measured 2026-09-02** against `agent-factory` @ `7b19baf` (`main`). This is a **delta
reconciliation**, not a corpus rebuild: the bootstrap pack was already read in full on 2026-08-31,
and what was missing was granularity, not coverage.

⛔ **Nothing here was implemented, and nothing was dispatched.** The pass stops at this synthesis
plus the canonical-index and research-backlog updates, by instruction. Nine concepts were promoted
into `concept_index.yaml` Section P; six mechanisms were reconciled with **no new id**, one of them
by outright rejection.

**Authority.** `.agent-platform/RECONCILIATION.md` and `PACK_CONFORMANCE.md` outrank the bootstrap
pack wherever they carry measured live-repo evidence (`.agent-platform/README.md`: everything under
`bootstrap/` is *"a proposal from a stranger"*, `C-PR-07`). Every implementation status below comes
from a grep or an import run this pass, never from what a source document says about itself.

---

## 1 · Coverage correction

### 1.1 The reported reading was substantially true. One number in it is wrong.

`PACK_CONFORMANCE.md` row 0.1 reports that the prior session read *"all 19 `docs/`, 8 schemas, 6
scripts, 13 skills"*. Checked against the tree:

```bash
find .agent-platform/bootstrap -type f | sed 's|^\.agent-platform/bootstrap/||' \
  | awk -F/ '{print (NF>1?$1:"(root)")}' | sort | uniq -c | sort -rn
```

| Reported | Measured | Verdict |
|---|---:|---|
| 19 design docs | **21** | ⛔ **MISMATCH — understates the tree by two.** `docs/` holds 21 `.md` files. |
| 8 schemas | 8 | ✅ exact |
| 6 scripts | 6 | ✅ exact |
| 13 skills | 13 | ✅ exact — thirteen directories, one `SKILL.md` each |

**Which two were missed is not recoverable from the record**, and this synthesis does not guess.
What *is* recoverable is which docs never reached the canonical index, and that is the more useful
number — see §1.2. The mismatch is small and it is reported because an inherited count is a
hypothesis (`C-PR-02`), not because it changes a conclusion. Everything else in
`PACK_CONFORMANCE.md` that this pass checked held: 110 files on disk, the four deviations are
each still true of the live tree, and `.claude/skills` still does not exist.

⚠ **`SOURCE_COVERAGE_CORRECTION.md` in the inbound pack repeats the 19 unchecked.** It is an
inherited premise and it is off by two.

### 1.2 The real gap, measured

The pack was read; the pack was not **indexed**. Regenerate:

```bash
python -c "import pathlib; r=pathlib.Path('.agent-platform/bootstrap'); \
i=pathlib.Path('docs/_index/concept_index.yaml').read_text(encoding='utf-8'); \
m=pathlib.Path('docs/_index/corpus_manifest.yaml').read_text(encoding='utf-8'); \
f=[p for p in sorted(r.rglob('*')) if p.is_file()]; \
print(len(f), sum(1 for p in f if p.as_posix() in i), sum(1 for p in f if p.as_posix() in m))"
```

| Sub-tree | Files | Cited in `concept_index.yaml` (before this pass) | Cited in `corpus_manifest.yaml` |
|---|---:|---:|---:|
| `docs/` | 21 | **6** | 1 |
| `schemas/` | 8 | **0** | 0 |
| `skills/` | 13 | **1** | 0 |
| `scripts/` | 6 | 0 | 0 |
| `diagrams/` | 19 | 0 | 0 |
| `research/` | 25 | 1 | 1 |
| `examples/` | 3 | 0 | 0 |
| root + `source/` | 15 | 3 | 4 |
| **total** | **110** | **11** | **6** |

⭐ **Zero of the eight JSON schemas had ever been named by the canonical index.** They are the most
concrete artefacts in the pack — a schema states a field list, and a field list is arguable in a way
that a design essay is not. Three of the nine promotions below exist *because* a schema was read
this pass, and each is marked `maturity: specified` for that reason.

The fifteen `docs/` files that had never been cited:

```
AUTONOMOUS_PRODUCT_LIFECYCLE  COMPUTE_AND_INTEGRATION_FABRIC  ENTREPRENEUR_SCENARIOS
EVALUATION_AND_GREEN  EXECUTION_SURFACE_POLICY  GAMIFIED_MISSION_CONTROL
MISSION_ASSEMBLY_AND_SWARMING  PATTERN_EXTRACTION_POLICY  PLATFORM_COMPLETION_FEATURES
PRODUCT_NAMING_AND_POSITIONING  REFERENCE_IMPLEMENTATIONS  REPO_INTEGRATION_PLAN
REVENUE_AND_VENTURE_FLYWHEEL  SESSION_UI_MVP  WEB_REMOTE_SESSION_RUNBOOK
```

### 1.3 What the correction does **not** license

⛔ **It is not a reason to rebuild the corpus, and it is not a reason to restore the pack's build
order.** `RECONCILIATION.md` §1.1 records that the pack's founding premise — Organization Factory,
Org-IR, Collective Cognition Fabric, Evolution Chamber — was refuted by this estate's own Wave 0
research the day before the pack was installed, with IMACS (`arXiv:2607.25446`) named as the
already-published organizational-compiler thesis. Nothing in this pass revisits that, and none of
the nine promotions depends on it.

---

## 2 · Promoted, merged and rejected

### 2.1 Promoted — nine new concepts

Each row: **source files · related concept ids · implementation status from live code · exact
benefit · smallest experiment · unlock condition · deadline effect.**

---

#### `C-GV-07` — The execution surface is a routing constraint, not a second scheduler · **PROMOTE_AS_NEW_CONCEPT**

| | |
|---|---|
| **Sources** | `.agent-platform/bootstrap/docs/EXECUTION_SURFACE_POLICY.md` · `docs/WEB_REMOTE_SESSION_RUNBOOK.md` · `.agent-platform/PACK_CONFORMANCE.md` rows 4.1–4.3 |
| **Related** | `C-GV-01` isolation ladder · `C-TM-03` parallelism bound by file locality · `C-TM-06` goal-aware orchestration · `C-CM-02` claims · `C-EV-08` scope hash |
| **Live status** | ⛔ **NOT_IMPLEMENTED, measured zero.** `grep -rniE "remote_control\|cloud_web\|preferred_surface\|execution_surface" factory/ scripts/ blueprints/ missions/ \| wc -l` → **0**. ⭐ But clause 3 of its collision rule is already built: `factory/claims.py:200-244` (`O_CREAT\|O_EXCL`, verified against the process table), `factory/worktrees.py:38-39`, `factory/lanes.py` (grouping by file locality, not by the dependency graph). `PACK_CONFORMANCE` 4.3 states the honest gap — *"honoured by discipline, not enforced; nothing allocates the worktree"*. |
| **Exact benefit** | A task that needs a local secret, a local MCP server or an unpushed file cannot be scheduled onto a surface that has none; and concurrency becomes a **predicate over declared writes** instead of an operator's assertion. This is the one recovered mechanism that reduces the operator's present multi-session friction. |
| **Smallest experiment** | Add the `execution:` block to the **five tasks of `missions/client-review-v1`** — nothing else — and write one predicate `can_run_together(a, b)` returning True only under the three collision-rule clauses. Compare its answer against what actually happened in the last week of parallel lanes. No scheduler, no dispatch. |
| **Unlock condition** | **None.** It is metadata plus a predicate over existing machinery. It does not wait on a certified team, because it schedules work rather than grading it. |
| **Deadline** | ⚠ **Touches it, and should not enter it.** The Switchboard vertical slice is the natural host and the temptation is to widen the slice. Do not. See §5. |

---

#### `C-AG-16` — The capability record: a claim bound to the conditions it was measured under · **CANONICAL_BUT_UNDER-SPECIFIED**

| | |
|---|---|
| **Sources** | `.agent-platform/bootstrap/schemas/capability-record.schema.json` (11 properties, 3 required) · `docs/PLATFORM_COMPLETION_FEATURES.md` |
| **Related** | `C-AG-04` registry and lockfile · `C-AG-01` the configuration IS the version · `C-EV-01` GreenContract · `C-EV-10` counterfactual maturity ladder · `C-GV-06` mission assurance receipt · `C-OP-03` repo-agnostic interfaces |
| **Live status** | **PARTIAL.** `factory/registry.py` maps `(shape, layer) → workflow`, versions each workflow by the SHA of its `SKILL.md` text, carries `state: PROVEN\|DECLARED\|UNBUILT` and an `evidence` string, and `unproven()` reports 4 of 9 workflows never run on real work. ⛔ It carries **none** of `conditions`, `success_rate`, `evidence_count`, `cost`, `latency`, `valid_from`, `valid_until`. `grep -rniE "capability_record\|CapabilityRecord" factory/` → 0. `factory/certify.py` holds the certification half and is not joined to it. |
| **Exact benefit** | A certification stops silently transferring to a configuration that was never graded. `registry.py` already makes the argument for `SKILL.md`-content hashing; the record generalises it to **the conditions**, which is the part the hash cannot express. |
| **Smallest experiment** | Add `valid_until` and `conditions` to the **four rows `unproven()` already returns**, then assert in a test that a row whose window has closed cannot be reported as coverage. The rows exist; the assertion is the experiment. |
| **Unlock condition** | ⛔ **One certified team.** `.data/runs.jsonl`: 10 rows, **0 PASS**; all 7 `agent_returned` events carry `dry_run=True`. A record schema built now would be graded against nothing. |
| **Deadline** | **No.** Post-deadline. |

---

#### `C-UI-07` — The synthesis inbox: a disposition queue, derived and not stored · **CANONICAL_BUT_UNDER-SPECIFIED**

| | |
|---|---|
| **Sources** | `.agent-platform/bootstrap/docs/GAMIFIED_MISSION_CONTROL.md` §5 · `docs/SESSION_UI_MVP.md` |
| **Related** | `C-KN-02` the absorption backlog · `C-UI-01` two projections over one state · `C-UI-04` nothing on the surface is a new source of truth · `C-UI-05` an imperative verb must act · `C-RS-05` external answers land unverified |
| **Live status** | **PARTIAL, and the halves are not joined.** Content model: `docs/absorption-backlog.md`, whose `ACTION` field already includes *"reject it in writing"* and which holds **19 rows and 2 whole answers with no disposition** (`GAP-07`). Surface: `factory/switchboard_p1.py`, whose first panel is `NEEDS YOU`, fed by `sessions.blocked()` and `bus.unread(reader)`. The backlog is a markdown file no projection reads, so an unactioned research answer is invisible on the operator surface. |
| **Exact benefit** | It is the cheapest fix available for the failure this whole corpus keeps recording — a completed answer that nobody dispositioned. And because `C-KN-02` is already the source of truth, `C-UI-04` is satisfiable: the inbox adds **no new state**. |
| **Smallest experiment** | Parse `absorption-backlog.md` into rows and render the count of undispositioned ones in the `NEEDS YOU` panel. One parser, one panel line, zero new files. Then check whether the count moves in a week. |
| **Unlock condition** | **None.** ⚠ But `C-UI-05` binds: if the row cannot be dispositioned from anywhere, render it as a **count**, not as a button. |
| **Deadline** | **No** — though it is the second-cheapest item in this document and belongs immediately after it. |

---

#### `C-TM-07` — The Mission Assembly Plan: a compiled team, resolved before anything runs · **PROMOTE_AS_NEW_CONCEPT**

| | |
|---|---|
| **Sources** | `docs/MISSION_ASSEMBLY_AND_SWARMING.md` · `schemas/mission-assembly.schema.json` (requires `participants`, `communication_routes`, `context_packets`, `gates`) · `skills/mission-assembler/SKILL.md` |
| **Related** | `C-TM-04` adaptive team formation · `C-TM-05` formations · `C-TM-06` · `C-AG-06` health and requirement vectors · `C-OR-06` mission hypergraph |
| **Live status** | **NOT_IMPLEMENTED.** No mission object, schema or lifecycle (`RECONCILIATION.md` §3). `grep -rniE "swarm"` across `factory/ scripts/ blueprints/ missions/ evals/ tests/` → 1 line, no mechanism. What exists is a lane brief plus a gate, and `blueprints/orchestrator_team.yaml` — a 3-agent blueprint **built, tested and rejected on evidence**, kept deliberately with its unlock threshold in its own header. |
| **Exact benefit** | Two refinements, not the assembler: **swarming acquires a stated precondition** (parallel exploration, diverse expertise, or independent verification — never the default), and **availability stops being idle/busy** (load, tool/env access, cost lane, latency, recent relevant experience, health, budget, permission scope). |
| **Smallest experiment** | Not runnable. The cheap precursor is to write the availability vector's field list into `C-AG-06`'s entry as a specification and see whether any field is unmeasurable today. |
| **Unlock condition** | ⛔ **Already written down and unmet** — the threshold in `orchestrator_team.yaml`'s header, plus one certified team. |
| **Deadline** | **No.** Explicitly off it. |

---

#### `C-PR-08` — Mine the mechanism, never the identity · **PROMOTE_AS_NEW_CONCEPT**

| | |
|---|---|
| **Sources** | `docs/PATTERN_EXTRACTION_POLICY.md` · `docs/REFERENCE_IMPLEMENTATIONS.md` · `skills/reference-implementation-miner/SKILL.md` · `.agent-platform/RECONCILIATION.md` §4 |
| **Related** | `C-PR-07` import without granting authority · `C-RS-06` repeated AI claims are not independent evidence · `C-KN-06` corpus as tamper-evident data · `C-VD-02` the blind instrument |
| **Live status** | ⭐ **IMPLEMENTED — practised on 2026-08-31 and never named.** Three MIT repositories mined from **source**, not READMEs: Paperclip (shallow-cloned, 6,169 files), SSSF (21 files), Inkwell (24). No code taken; obligations recorded; five SSSF patterns identified that would let this estate **delete** rather than add; and one defect **inverted rather than inherited** — SSSF ships every quality block as `["echo", "PLACEHOLDER"]`, `echo` exits 0, so a stamped repo reports `verified=True` having tested nothing. |
| **Exact benefit** | It names a practice that is currently invisible to every gate, and it carries the corollary that pays: **a mined pattern that lets you delete a subsystem is worth more than one that adds a feature.** |
| **Smallest experiment** | None needed — it has already run. The open item is that its durable artefact (`wiki/concepts/patterns/agent-control-plane-prior-art.md`) has **no in-repo home**, so a mined conclusion sits outside every gate. |
| **Unlock condition** | **None.** |
| **Deadline** | **No.** It is a naming, not a build. |

---

#### `C-OR-09` · `C-OR-10` · `C-KN-08` · `C-OP-07` — **PRESERVE_AS_FUTURE_VERTICAL** (four rows, one disposition)

| id | Concept | Sources | Live status | Unlock condition |
|---|---|---|---|---|
| `C-OR-09` | Compute and integration fabric — the node contract before the provider | `docs/COMPUTE_AND_INTEGRATION_FABRIC.md`, `schemas/compute-node.schema.json` | `grep -rniE "DGX\|compute_node\|compute node"` → **0**. Execution is synchronous Python + `subprocess`; sole runtime dep is `pyyaml` | ⛔ **A second compute surface to abstract over.** There is one. |
| `C-OR-10` | The venture vertical — product lifecycle over the existing substrate | `docs/AUTONOMOUS_PRODUCT_LIFECYCLE.md`, `REVENUE_AND_VENTURE_FLYWHEEL.md`, `PLATFORM_COMPLETION_FEATURES.md`, `schemas/opportunity-hypothesis.schema.json`, `schemas/venture-plan.schema.json`, 2 skills | `grep -rniE "venture\|opportunity_hypothesis"` → **0** | ⛔ One certified team (`README.md:96`) |
| `C-KN-08` | Customer and market learning loop | `docs/PLATFORM_COMPLETION_FEATURES.md`, `skills/customer-learning-loop/SKILL.md` | No product, no telemetry, no customer of the factory. Nothing in `factory/` reads an external signal | ⛔ `C-OR-10`, plus tenancy/privacy boundaries this estate has not settled even for the client it *does* have (`GAP-30`) |
| `C-OP-07` | Portfolio allocation under opportunity cost | `docs/PLATFORM_COMPLETION_FEATURES.md`, `skills/portfolio-experiment-manager/SKILL.md` | `grep -rniE "portfolio.*allocat\|KILL/HOLD"` → **0** | ⛔ `C-OP-04` fitness qualification gate, and an eval corpus larger than one connector (`GAP-08`) |

**Related ids across the four:** `C-OR-02`, `C-TM-06`, `C-GV-02`, `C-OP-01`, `C-OP-02`, `C-OP-04`,
`C-OP-05`, `C-KN-01`, `C-KN-07`, `C-EV-06`, `C-VD-02`, `C-VD-03`, `C-PR-03`, `C-GV-01`.

**Exact benefit of preserving them at all** — three transferable ideas, available today at zero
build cost:

1. ⭐ `opportunity-hypothesis.schema.json` **requires** a `falsification` field. That is `C-PR-03`
   (*state the kill condition before building*) arrived at independently, in a commercial coat.
2. `C-OP-07` refuses the single scalar reward and makes `MORE_EVIDENCE` a first-class outcome —
   the same move as `C-EV-06` making *"missing"* sayable, from a different direction.
3. `venture-plan.schema.json` requires **both** `success_criteria` and `failure_criteria`. Most of
   this estate's gates require only the first.

**Deadline: no, for all four.** They are the rows most likely to leak into the critical path and
the ones this pass is most explicit about keeping out.

---

### 2.2 Merged into existing concepts — no new id

| Mechanism | Source | Disposition | Merge target | The rule that governs it |
|---|---|---|---|---|
| **Evidence-gated autonomy ladder** (L0–L7, each with a required proof) | `docs/AUTONOMY_LADDER.md`, `schemas/platform-progress.schema.json`, `skills/roadmap-rank-tracker/SKILL.md` | **MERGE_INTO_EXISTING** | `C-EV-04` readiness as measured gates · `C-EV-05` the board is generated · `C-TM-02` unlock conditions · `C-GV-02` bounded autonomy · `RB-15` | ⛔ **Never a parallel `PROGRESS.yaml`.** `factory/readiness.py` holds **30 gates across 5 phases** — MEASURED: `python -c "import factory.readiness as r,collections;print(len(r.GATES),collections.Counter(g.phase for g in r.GATES))"` → `30 {'judgement': 8, 'certification': 8, 'handover': 7, 'bounded': 4, 'loop': 3}`. `factory/roadmap.py` refuses to hold a task list *on principle*. What the ladder adds is **an operator-facing projection**: `LOCKED / EXPERIMENTAL / PROVISIONAL / EARNED` — MEASURED absent, `grep -rniE "LOCKED\|EXPERIMENTAL\|PROVISIONAL\|EARNED" factory/*.py` returns no vocabulary. ⚠ And the ladder imposes a **total order** the 5 phases do not have; that is the question added to `RB-15`. |
| **Promotion Board** | `docs/GAMIFIED_MISSION_CONTROL.md` §6 | **REJECT_AS_DUPLICATE_SOURCE_OF_TRUTH** | `C-EV-05`, `C-UI-01`, `C-UI-04` | It *is* `board.py` with rank labels. `platform-progress.schema.json` (`currentRank`, `ranks`, `updatedAt`) is exactly the hand-maintained twin `roadmap.py` exists to refuse. Render the labels **from the gates** or not at all. |
| **Commercial autonomy policy** | `docs/COMMERCIAL_AUTONOMY_POLICY.md` | **ALREADY_CANONICAL** | `C-GV-02` — the file is *already* in its `source_documents` list | Autonomy is named auto-actions each refusing by default, not a slider. The commercial specialisation (money, public claims, outreach, privacy, contracts, deployment) is five more named actions, not a new mechanism. ⛔ Constraint kept verbatim: **revenue may not rewrite evaluator rules** — the same rule as *"no optimizer may define its own promotion test"*. |
| **Conditional swarming + rich availability** | `docs/MISSION_ASSEMBLY_AND_SWARMING.md` | **MERGE_INTO_EXISTING** | `C-TM-07` (new) + `C-AG-06` health/requirement vectors | Whether availability and health are one object or two is unresolved in **both** sources, and is recorded as such rather than decided here. |
| **Rich typed message envelope** | `schemas/message-event.schema.json` (15 properties) | **MERGE_INTO_EXISTING** | `C-CM-01` durable record vs live channel · `C-CM-03` typed messages at four moments · `C-CM-04` communication-defect attribution · `RB-02` | ⛔ **Do not replace `factory/bus.py`.** Its 5 `KINDS` are *"every kind here is one that actually happened on 2026-08-22 and had no channel at the time"*; `factory/events.py` holds 9 closed kinds whose terminal members must carry a `Verdict`. Genuinely absent: `correlation_id`, `causation_id`, `provenance_refs` — MEASURED: `grep -rniE "correlation_id\|causation_id" factory/` → **0**. ⚠ These should map onto **OpenTelemetry** messaging/GenAI conventions before becoming a proprietary trajectory shape. That is `RB-02`, and the envelope is now one of its inputs. |
| **Research job lifecycle / state machine** | `schemas/research-job.schema.json` | ⛔ **REJECT_AS_DUPLICATE_SOURCE_OF_TRUTH** | `C-RS-01`, `C-RS-04`, `docs/research/backlog.yaml`, sibling `agent-army-research/` | `PACK_CONFORMANCE` 3.3/3.4 already deviated from generating the pack's queue, and the reason still holds: `agent-army-research/` has 26 prompts, an A–E evidence-tier protocol, a hypothesis ledger and a graduation rule. **One field is worth borrowing and nothing else** — `execution_surface`, which is `C-GV-07` and belongs there, not in a second queue. |

### 2.3 Nothing was labelled `RESEARCH_REQUIRED`

Deliberately. The label was available and every candidate for it turned out to be answerable by
reading the repo or by a measurement this estate can already take. That is this corpus's
characteristic failure recorded in `backlog.yaml`'s own preamble — *"buying a research answer to a
question that measurement would settle more cheaply"* — and the delta pass declined to repeat it.
The three genuinely external questions became **additions to missions that already exist** (§3),
not new research.

---

## 3 · Research changes

⛔ **Nothing dispatched.** All changes are to candidate records.

### 3.1 ID collision, corrected

The inbound `RESEARCH_ADDENDUM.yaml` proposes `RB-21` … `RB-24`. ⛔ **`RB-21` is already taken** —
`backlog.yaml` `supplementary_assessment_2026_09_02.new_candidates_recorded_not_dispatched`
holds *"Do the twelve architecture cards' failure modes occur in this estate?"* (LOW, blocked by
`RB-00C`). The four new candidates are therefore filed as **`RB-22` … `RB-25`**.

### 3.2 Three existing missions gain sources and one question each

| Mission | Change |
|---|---|
| **RB-15** — rank ladder versus absence table | +3 sources (`AUTONOMY_LADDER.md`, `platform-progress.schema.json`, `roadmap-rank-tracker/SKILL.md`) and one question: *can rank be a derived projection over independent gates without imposing a false total order or creating a second source of truth?* ⭐ This is the sharpest form the mission has had, because the pack supplies a concrete eight-rung ladder to test the estate's five unordered phases against. |
| **RB-20** — interop as a factory primitive (MCP, A2A, AGNTCY) | +3 sources (`COMPUTE_AND_INTEGRATION_FABRIC.md`, `capability-record.schema.json`, `compute-node.schema.json`) and three questions, the load-bearing one being **which capability fields are A2A Agent-Card discovery and which are the local evidence envelope**. This is where `C-AG-16` gets settled. |
| **RB-02** — observability and trace standards | +2 sources (`message-event.schema.json`, `COMMUNICATION_PROTOCOL.md`) and one question on mapping `correlation_id`/`causation_id`/provenance onto OpenTelemetry rather than a proprietary trajectory. ⚠ `RB-02` is also `HL-08`'s prerequisite, so this addition is on the estate's own keystone. |

### 3.3 Four new candidates — recorded, not dispatched

| id | Title | Priority | Why not now |
|---|---|---|---|
| **RB-22** | Execution surface routing and multi-session scheduler | `HIGH_AFTER_DEADLINE_IF_NOT_IMPLEMENTED` | ⭐ **Experiment first, research second.** The five-task pilot in §2.1 is cheaper than the prior-art pass and would tell us whether routing is needed at all. |
| **RB-23** | Evidence-backed capability record and certification boundary | `HIGH_AFTER_TWO_REAL_WORKLOADS` | Blocked by `RB-00C`. There is nothing certified to write a record about. |
| **RB-24** | Synthesis inbox and research disposition workflow | `MEDIUM` | Experiment first — 19 undispositioned rows already exist as a before-measurement. |
| **RB-25** | Venture lifecycle, customer learning and portfolio allocation | `DEFER_UNTIL_CERTIFIED_TEAM` | ⛔ Gated by `README.md:96`. Recorded so the schemas are not lost. |

### 3.4 Dependency graph

No edge changed. `RB-22`–`RB-25` are recorded as candidates and are **not** in a wave.
`backlog.yaml`'s `summary.missions: 26` is therefore unchanged, exactly as `RB-21` was left
uncounted. The graph's binding constraint is still `RB-00C` — **no agent has ever completed a real
run** — and nothing in this pack changes that. Nothing in any pack can.

---

## 4 · Implementation-plan changes

**Three, and only one of them is near-term.**

1. **`C-GV-07` moves up, as an experiment on five tasks.** Not a router, not a scheduler: an
   `execution:` block on `missions/client-review-v1`'s tasks plus one `can_run_together()`
   predicate, checked retrospectively against a week of real parallel lanes. It is the only
   recovered mechanism whose unlock condition is *none*, and the only one that reduces the
   operator's present friction. **After the deadline.**

2. **`C-UI-07` becomes a one-line addition to a surface that already exists.** Parse
   `absorption-backlog.md`, render the undispositioned count in `switchboard_p1`'s `NEEDS YOU`
   panel. No new source of truth (`C-UI-04`), no new file, and there is already a
   before-measurement: 19 rows.

3. **`C-AG-16` is scoped as a `registry.py` extension and explicitly not a new registry.** Two
   fields (`conditions`, `valid_until`) on the four rows `unproven()` already returns, plus one
   test asserting an expired claim is not coverage. ⛔ **Still blocked** on one certified team.

**What did NOT change.** The nine-step build order in `SYNTHESIS` §5; the four deviations in
`PACK_CONFORMANCE.md`; `README.md`'s absence table; the refusal to build above Rank 3. No promoted
concept is scheduled, and six of the nine are explicitly gated behind conditions that are unmet
today.

**Effort correction, carried forward.** `SUPPLEMENT_README.md` recorded that the frontier packs'
effort estimates are wrong in this estate because several P0 items are already partly built. The
same is true here for two of nine: `C-AG-16` and `C-UI-07` are **joins**, not subsystems. The
inbound `CRUCIAL_FEATURES_DELTA.md` prices the capability record as a "major future multiplier"
without noticing that `registry.py` already versions a workflow by the hash of its text.

---

## 5 · Deadline Impact

### ⛔ None. The current ordering stands, unchanged.

```
1. Marketing Model meeting-ready delivery
2. Switchboard runnable mission vertical slice
3. Sales bounded patch
4. post-deadline measurement / research
```

**This ordering is corroborated by live repo evidence, not only by the inbound pack.**
`docs/_index/SUPPLEMENT_README.md` records the same four priorities and returns ⛔ **NO** against
each of the first three when the last 635 KB of the corpus was read. This pass reaches the same
verdict against a different source, and the two are independent: that pass read two `.docx` and a
sibling repository; this one read a 110-file bootstrap tree and eight JSON schemas.

| Priority | Does the delta change it? |
|---|---|
| 1 · **Marketing Model** | ⛔ **No.** Nothing in `.agent-platform/bootstrap/` bears on it. Its open items are credential retrieval, warehouse-mode exercise and the PBI DAX instrument — measurements against a live system that no design document informs. **Proceed unchanged.** |
| 2 · **Switchboard vertical slice** | ⛔ **No — and this is the row that needs guarding.** `C-GV-07` and `C-UI-07` both land naturally in the Switchboard, and both are cheap. That is precisely why they must not be added: a slice that grows because two cheap things fit is how a vertical slice stops being one. ⭐ Note for **after** the slice ships, not during: `C-UI-07`'s two halves already exist and only need joining. **Do not widen the slice.** |
| 3 · **Sales bounded patch** | ⛔ **No.** Untouched by anything in this pack. **Proceed unchanged.** |
| 4 · **Post-deadline** | ⚠ **Yes, in ordering only.** `C-GV-07` (as the five-task experiment) is the first item, ahead of `RB-22`'s prior-art pass — experiment before research, because the experiment is cheaper and could retire the mission. `C-UI-07` second. Everything else waits on `RB-00C`. |

### What is explicitly barred from the critical path

⛔ **Venture (`C-OR-10`), Org-IR (`C-OR-02`, refuted as novel), the capability market
(`C-CM-06`), gamified mission control, and the compute fabric (`C-OR-09`).** Every one is either
gated behind a certified team — `.data/runs.jsonl`: **10 rows, 0 PASS**, all 7 `agent_returned`
events `dry_run=True` — or behind *"numbers worth looking at"* (`README.md:98`), and the ledger
supplies none.

### One honest note about the deadline itself

⚠ **The estate's own scheduler still says no deadline exists.** `factory/schedule.py:26`: *"'Ahead
or behind schedule' needs a target, and there isn't one. No deadline has been stated anywhere in
the programme."* The four-priority ordering above lives in documents; it is not a date any
instrument can measure against. `python -m factory.schedule --target YYYY-MM-DD` makes it
measurable immediately, and stating the target is a one-line action, not a research mission
(`GAP-43`). This is recorded, not acted on — naming the date is the operator's call.

---

## Basis register — the weakest claims in this document

| Claim | Basis |
|---|---|
| `docs/` holds 21 files, not 19 | **MEASURED**, `find`, this pass |
| Every "0 occurrences" above | **MEASURED**, `grep -rniE` over `factory/ scripts/ blueprints/ missions/ evals/ tests/`, this pass. ⚠ The instrument was shown able to return non-zero on adjacent terms in the same run, so these are ZERO, not NOT-VISIBLE |
| 30 gates across 5 phases | **MEASURED**, by importing `factory.readiness`, this pass |
| 10 runs / 0 PASS / 7 dry-run dispatches | **INHERITED** from `RECONCILIATION.md` §1.2, dated 2026-08-31, **not re-measured this pass**. Its regeneration command is in that document |
| Which two `docs/` files went unread | ⛔ **NOT-RECORDED.** Not recoverable, and not guessed |
| Effort claims ("cheap", "one line") | **ASSUMED.** No implementation was attempted; these are judgements, and the experiments are specified so they can be falsified cheaply |
| The four-priority deadline ordering | **DERIVED** from `SUPPLEMENT_README.md` and the inbound pack, which agree. ⚠ No instrument in the repo measures against it |

## What this pass deliberately did not do

- **No implementation.** Hard stop, by instruction.
- **No research dispatched.** `RB-22`–`RB-25` are candidates; the three expanded missions gained
  sources and questions, not a launch.
- **No corpus rebuild**, and no restoration of the bootstrap pack's build order.
- **No revisiting of the Wave 0 refutation.** `RECONCILIATION.md` §1.1 stands.
- **No new source of truth.** Every promotion names the existing module it extends.
