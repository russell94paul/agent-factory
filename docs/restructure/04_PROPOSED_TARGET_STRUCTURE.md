# 04 — Proposed target structure

**Phase 1 proposal.** Nothing here has been created. Measured against `827f871` on 2026-09-03.

---

## 1. The brief's provisional tree, evaluated against the measurement

The brief supplies a tree and says: *"Use this only as a starting hypothesis… Adapt this structure
to the actual repository… Do not create empty packages merely to make the repository appear
sophisticated."*

Adapting it requires rejecting most of it. Here is why, item by item.

| Brief proposes | Verdict | Measurement |
|---|---|---|
| `apps/nerve/` | **REJECT as code** | No JS/TS/Node anywhere. No `package.json`. "NERVE" = 11 occurrences in 2 files, both under `docs/raw_research/`. Zero code. |
| `packages/*` (12 packages) | **REJECT** | One Python distribution (`agentic-factory`), one flat package (`factory/`, 68 modules), one runtime dep. No workspace tooling exists and none is justified. |
| `packages/operative-runtime/` | REJECT | Would be `factory/` renamed for a word with 187 occurrences, 0 in code. |
| `packages/configuration-genome/` | **REJECT — empty by construction** | "Configuration Genome" = **1 occurrence, 1 file**. And the canonical ontology calls this **"Cell Blueprint / Cell Genome"** — the brief's term is not in it. |
| `packages/cell-mesh/`, `cellbus/` | REJECT | Cell Mesh = 5 occurrences / 2 files. CellBus = 36 / 6, all prose. Zero code. |
| `packages/cell-adapt/` | **REJECT — empty by construction** | CELL ADAPT = 13 occurrences / 2 files, both `docs/raw_research/`. |
| `packages/memory/`, `governance/`, `capability-registry/`, `simulation/` | REJECT | No corresponding code. `factory/registry.py` exists but is a workflow registry, not a capability registry. |
| `packages/mission-runtime/`, `evidence/`, `observability/` | **REJECT the package; the code EXISTS** | `factory/missions.py`, `evidence.py`, `events.py`, `runs.py` already do this. A package boundary would rename working code for no gain. |
| `domains/quant-research/` | **REJECT — empty by construction** | CELL-Q = **0 occurrences**. No quant material of any kind exists in this repository. |
| `benchmarks/`, `simulations/`, `configs/`, `schemas/` (top level) | REJECT as new roots | `evals/` is the eval corpus. `blueprints/` + `missions/` are the configs. `docs/protocol/*.schema.json` + `.agent-platform/bootstrap/schemas/` are the schemas. Creating empty siblings fragments them. |
| `tests/`, `tools/` | Partially exists | `tests/` exists with 1018 tests. `tools/` would duplicate `scripts/` (43 files). |
| **`docs/` subtree** | **ACCEPT, with edits** | This is the part of the brief that fits. See §2. |
| `.claude/commands/` | **ACCEPT** | Exists with 6 `af-*` commands. `/cell-*` commands are added beside them. |

**Net: the brief's `docs/` subtree is right and its code subtree is wrong for this repository.**
That is not a criticism of the brief — it is a generic template, and §9 told me to adapt it.

⭐ **The deeper reason the code tree must be rejected**: creating `packages/configuration-genome/`
would put a directory in the repository named for a capability that has one prose mention and no
implementation. The repository's founding discipline — *"Do not claim something is implemented
because it appears in a design document"* — is violated by the *directory tree itself*, before a
single line is written. A reader running `ls packages/` would see twelve subsystems, of which two
exist.

---

## 2. Proposed target structure

Additions marked **NEW**. Everything unmarked exists today and does not move.

```text
/
├── factory/                       # THE RUNTIME. 68 modules, 23,939 lines, flat. UNCHANGED.
│   ├── progress.py                # NEW ⭐ load/validate/write PROJECT_PROGRESS.yaml (§8.3)
│   └── forecast.py                # NEW ⭐ the Dynamic Due Date Engine (§8.4)
├── evaluator_service/             # the grader — separate identity, on purpose. UNCHANGED.
├── scripts/                       # 43 entry points: render checks, probes, pack builders. UNCHANGED.
│   └── hooks/
├── tests/                         # 1018 tests. UNCHANGED.
├── evals/corpus/                  # hash-verified on load via MANIFEST.sha256. UNCHANGED.
├── blueprints/                    # team specs. UNCHANGED.
├── missions/                      # mission specs + presets. UNCHANGED.
├── .agent-platform/               # ⚠ a proposal from a stranger. UNCHANGED, and never a spec.
├── boot-prompts/                  # session handoffs; router is README.md. UNCHANGED.
│
├── docs/
│   ├── _incoming/                 # NEW ⭐ the missing stage. Intake landing zone.
│   │   └── README.md              # NEW   the intake contract (§3)
│   │
│   ├── _index/                    # THE CORPUS INDEX — already exists, 13 files. DELTA, never rebuild.
│   │   ├── corpus_manifest.yaml       # existing — delta pass, +169 files
│   │   ├── concept_index.yaml         # existing — delta pass
│   │   ├── document_catalog.md        # existing — regenerate as a view
│   │   ├── current_vs_proposed.md     # existing — the capability matrix
│   │   ├── contradictions.md          # existing — hand-maintained
│   │   ├── duplicate_clusters.md      # existing — +DC-14, DC-15, DC-16
│   │   ├── supersession_candidates.md # existing — hand-maintained
│   │   ├── repo_snapshot.md           # existing
│   │   ├── high_leverage_concepts.md  # existing
│   │   ├── research_gap_candidates.md # existing
│   │   ├── agent_army_wave0_supplement.md      # existing
│   │   ├── agent_platform_delta_synthesis.md   # existing
│   │   ├── SUPPLEMENT_README.md       # existing
│   │   ├── research_registry.yaml     # NEW ⭐ machine-readable research registry (§07)
│   │   └── research_status.md         # NEW   generated readable view of the above
│   │
│   ├── architecture/              # NEW ⭐ the missing canonical/proposed separation
│   │   ├── canonical/             # NEW   only what code or tests can back
│   │   │   ├── README.md          # NEW   ⭐ the precedence rule (§4)
│   │   │   └── terminology/       # NEW
│   │   │       ├── CELL_OS_Canonical_Terminology_vNext.md   # NEW: read-only extract from the ZIP
│   │   │       └── KNOWN_TERMINOLOGY_COLLISIONS.md          # NEW: read-only extract from the ZIP
│   │   ├── proposed/              # NEW   named, unbuilt subsystems — kept OUT of code
│   │   │   ├── README.md          # NEW   "nothing here is implemented"
│   │   │   ├── nerve-switchboard.md         # NEW
│   │   │   ├── cell-mesh-and-links.md       # NEW
│   │   │   ├── cell-genome.md               # NEW  (⚠ NOT "configuration-genome" — see 06 §4)
│   │   │   ├── cell-adapt.md                # NEW
│   │   │   ├── hypermesh-and-memory.md      # NEW
│   │   │   ├── sihre.md                     # NEW
│   │   │   └── domain-plane.md              # NEW  ⚠ 0 occurrences today — a stub naming the gap
│   │   └── diagrams/              # NEW   ← docs/diagrams/ (4 files) + the CELL OS overview PNG
│   │
│   ├── decisions/                 # NEW ⭐ the second missing stage. ADRs.
│   │   ├── README.md              # NEW
│   │   └── 0001-keep-one-python-distribution.md   # NEW  (records §1 of this document)
│   │
│   ├── product/                   # NEW   product & UX specs — currently scattered
│   │   └── README.md              # NEW   pointer-only at first; no file moves in Phase 2
│   │
│   ├── research/                  # EXISTS. R1–R19 prompts + answers/ + backlog.yaml
│   │   ├── answers/               # ⛔ NO MOVE — runtime-coupled (readiness.py:1711)
│   │   ├── prompts/               # NEW   pointer README; prompts stay where code expects them
│   │   ├── syntheses/             # NEW   ← the mis-shelved Crossreference Audit
│   │   ├── r_and_d/               # NEW   speculative proposals, explicitly not canonical
│   │   ├── sources/               # EXISTS
│   │   └── backlog.yaml           # EXISTS — 26 candidates, NOT_DISPATCHED
│   │
│   ├── raw_research/              # ⛔ IMMUTABLE. 326 files. Brief forbids alteration.
│   │   └── converted/             # EXISTS — readable renderings; +3 new conversions
│   │
│   ├── evidence/                  # ⛔ NO MOVE — runtime-coupled (readiness.py:1736). 160 files.
│   ├── artifacts/                 # ⛔ NO MOVE — runtime-coupled (schedule.py:46, readiness.py:647)
│   │   └── incoming/              # NEW   ← 2 rendered artifacts mis-shelved in raw_research/
│   ├── findings.d/                # ⛔ NO MOVE — read as data by factory/findings.py:29
│   ├── findings.md                # ⛔ NO MOVE — factory/findings.py:24
│   ├── specs/                     # EXISTS — 3 files named from factory/ docstrings. NO MOVE.
│   ├── protocol/                  # EXISTS — protocol + schemas. NO MOVE.
│   ├── design/                    # EXISTS — design pack, CELL OS ZIPs, design tokens
│   ├── marketing/cell-os-launch-v1/   # EXISTS ⭐ where most CELL OS prose actually lives
│   ├── agent-army/                # EXISTS ⭐ CURRENT_STATE.md is code-measured; it outranks the index
│   ├── release-gate/              # ⛔ DELIBERATELY UNTRACKED. AF-RELEASE-GATE-01 is BLOCKED.
│   ├── reviews/  recon/  board/  case-studies/
│   │
│   ├── status/                    # NEW ⭐ the third missing stage. No tracker exists today.
│   │   ├── PROJECT_PROGRESS.yaml  # NEW   ⭐ AUTHORITATIVE — the single source of truth
│   │   ├── project_progress.json  # NEW   GENERATED UI projection (§8)
│   │   ├── PROJECT_PROGRESS.md    # NEW   GENERATED readable view — never hand-edited
│   │   └── forecast_history.jsonl # NEW   append-only P50/P80 history, for "what changed?"
│   │
│   ├── archive/                   # NEW   superseded material, moved not deleted
│   └── restructure/               # THIS DIRECTORY (Phase 1 output)
│
└── .claude/
    └── commands/                  # EXISTS: af-pause, af-phase, af-resume, af-run-critical,
                                   #         af-run-dag, af-status
                                   # NEW:    cell-session-start, cell-intake-research, cell-audit,
                                   #         cell-plan-mission, cell-implement, cell-verify,
                                   #         cell-session-close, cell-update-progress,
                                   #         cell-work  ⭐ the ticket-ID entry point (§8.6)
```

**One more file, outside the tree above:**
`docs/artifacts/cell-os-tracker.html` — the PROJECT TRACKER tab added to the primary CELL OS
artifact. It is listed separately because `docs/artifacts/` is runtime-coupled and **the new file is
an addition to that directory, not a move within it**. See §8.5.

### 2.1 What this proposal does NOT create

Stated explicitly, because an omission that is a decision should not read like an oversight:

- **No `apps/`, no `packages/`, no `domains/`.** §1.
- **No `benchmarks/`, `simulations/`, `configs/`, `schemas/`, `tools/` at top level.** Each would
  duplicate an existing root while holding nothing.
- **No `docs/benchmarks/`, `docs/simulations/`, `docs/operations/`.** Zero source material exists
  for any of the three. They are added when the first file arrives, not before.
- **No `domains/quant-research/`.** See §5.

**Nine directories are created, and every one has content on day one** — either a moved/copied file
or a README that carries a rule the repository currently enforces only by convention.

---

## 3. `docs/_incoming/` — the intake contract

The single structural gap that best explains what the audit found. Without a landing zone, inbound
downloads land wherever the browser put them, and the evidence is visible:

- Two rendered HTML artifacts filed as *raw research*.
- One synthesis (`CELL_OS_Product_Technical_Design_v0.1_Crossreference_Audit_v1.md`) filed as *raw
  research* — a derived opinion shelved as a primary source.
- Three CELL OS files in `docs/design/`, one ZIP loose in the **repository root**.
- A whole 28-file directory (`docs/combined-execution-research-v2-2026-09-02/`) that is a second,
  out-of-convention extraction of a pack already extracted under `docs/raw_research/`.

`docs/_incoming/README.md` states the contract:

1. **Everything inbound lands here first.** No exceptions, including ZIPs.
2. **Nothing is promoted without classification** into exactly one of: raw research · synthesized
   research · canonical architecture · rendered artifact · proposal · design asset.
3. **Promotion preserves the original.** Files move to `raw_research/` (sealed) or are *copied* to
   a derived location; extracts carry a provenance header naming source archive + SHA-256.
4. **⛔ Promotion to `architecture/canonical/` requires implementation evidence or a passing test,
   and an explicit written rationale.** A research report never becomes canonical automatically.
5. **`_incoming/` is not a store.** A file still sitting here after classification is a queue item,
   surfaced by `/cell-intake-research`.

---

## 4. Canonical vs proposed — the rule, and where it lands

The lifecycle in the brief's task 7 needs one thing to be enforceable rather than aspirational: a
statement of **which document wins when two disagree.** The repository already has that rule, in
`corpus_manifest.yaml`'s own preamble:

> *"Where this manifest and either of those disagree, THEY are right. They were measured against
> code; this was measured against documents."*

`docs/architecture/canonical/README.md` promotes it from a comment inside one YAML file to the
governing rule of the architecture tree:

```text
PRECEDENCE — highest first. A lower tier never overrides a higher one.

  1. Code and passing tests            factory/, tests/, evaluator_service/
  2. Code-measured instruments         docs/agent-army/CURRENT_STATE.md
                                       .agent-platform/RECONCILIATION.md, PACK_CONFORMANCE.md
  3. Verification evidence             docs/evidence/
  4. Canonical specification           docs/architecture/canonical/, docs/protocol/, README.md §IV
  5. Architecture decisions            docs/decisions/
  6. Document-measured index           docs/_index/
  7. Architecture proposals            docs/architecture/proposed/, docs/specs/
  8. Synthesized research              docs/research/answers/, syntheses/, SYNTHESIS.md
  9. Raw research                      docs/raw_research/   ← immutable, and lowest authority
 10. A proposal from a stranger        .agent-platform/bootstrap/   ← never a specification

⭐ A document does not gain authority by being newer, longer, or more confident.
   It gains authority by being lower-numbered.
```

⚠ **Tier 9 being lowest is deliberate and can read as backwards.** Raw research is *immutable* —
which makes it trustworthy as a record of what was said, and worthless as a claim about what is
true here. Immutability and authority are different properties.

---

## 5. The quantitative-research boundary (brief task 12)

```bash
grep -riE "CELL-Q|CELL_Q" --exclude-dir=.git .    # 0 hits
```

**Nothing quantitative exists in this repository.** No market data, no backtest, no broker
integration, no model registry, no trading code, no financial data of any kind.

**The proposal is therefore to define the boundary before there is anything to bound**, in one
document — `docs/architecture/proposed/domain-plane.md` — and to create no `domains/` tree:

| Permitted when the first CELL-Q file arrives | Excluded from this plan and from any future one |
|---|---|
| Historical data (stored, versioned, hash-manifested like `evals/corpus/`) | ⛔ Live brokerage or exchange connectivity |
| Synthetic data generation | ⛔ Order placement, of any size, in any venue |
| Offline experiments and replay | ⛔ Live-account credentials, API keys, session tokens |
| Backtesting methodology (as *methodology*, documented) | ⛔ Any production trading integration |
| Paper portfolios (simulated positions only) | ⛔ Real-money position or balance state |
| Benchmarking and drift research | ⛔ Anything reading a live account |
| Model registries (versioned artifacts) | |

⭐ **Structural enforcement, not a promise.** `.gitignore` already carries a precedent — the live
PBI capture is excluded *unconditionally* because "the DAX result rows are the client's commercial
data." The same mechanism should carry a `LOCAL_ONLY` rule for any credential-bearing path before
the first quant file exists. **An ignore rule written after the file arrives is written too late.**

---

## 6. Module boundaries (brief task 8)

Each boundary the brief names, measured. `factory/` module names are real files; **"—" means no code
exists**.

| Boundary | Existing implementation | Intended responsibility | Coupling today | Recommended interface | Code now, or research? |
|---|---|---|---|---|---|
| Operative runtime | `factory/` (68 modules) | Turn a spec into bounded work | Centred on `contract.py` (fan-in 21) | Keep flat; `contract.py` is already the seam | **CODE — exists, do not rename** |
| Mission Contracts & DAGs | `missions.py`, `contract.py`, `workplan.py`, `flow.py`, `blueprint.py` | What "done" means; the work graph | High, intentional | `contract.Verdict` | **CODE — exists** |
| Cell Genome (brief: "Configuration Genome") | `blueprint.py` + `blueprints/*.yaml` + `presets.py` | The config that IS the version | Fan-in 6 + 5 | `AgentSpec` / `TeamSpec` | **CODE — exists under a different name.** ⚠ Renaming is a terminology decision, not a code one |
| Cell Mesh orchestration | `lanes.py` (18), `coordination.py`, `deploy.py`, `dispatch.py`, `control.py`, `teamplan.py` | Grouping, dispatch, priority | Fan-in 18 on `lanes` | `lanes.by_locality()` | **CODE — exists** |
| CellBus | `bus.py`, `events.py` | Typed event fabric | Low fan-in | append-only ledger | **PARTIAL** — a bus exists; "CellBus" as specified (typed claims/evidence/escalations) does not |
| Memory / HyperMESH | **—** | Organizational cognition substrate | n/a | n/a | **RESEARCH.** 117 occurrences, 0 in code |
| Evidence & verification | `evidence.py`, `verifiers.py`, `assertions.py`, `calibration.py`, `evals.py` | TARGET/CONSUMER/REGRESSION/ROLLBACK | Moderate | `EvidenceRequired` | **CODE — the strongest lane in the repo** |
| Authority & governance | `claims.py`, `operator.py`, `plan_gates.py`, `launch.py` | Locks, the supervised/guarded boundary | Moderate | `O_CREAT\|O_EXCL` verified against the process table | **CODE — exists** |
| Observability & Replay | `events.py`, `runs.py`, `sessions.py`, `session.py`, `metrics.py` | The ledgers; cost RECORDED/RECONSTRUCTED/NOT-RECORDED | Moderate | `.data/*.jsonl` | **CODE — exists.** Replay-as-debugger does not |
| Readiness & health | `readiness.py` (1,948 lines, fan-in 16), `goals.py`, `board.py`, `work.py`, `roadmap.py` | 30 gates / 5 phases; `NOT-MEASURED` is sayable | **Highest in the package** | gate verdicts | **CODE — exists.** ⚠ The one real refactor candidate |
| CELL ADAPT | **—** | Configuration optimization from replay | n/a | n/a | **RESEARCH.** 13 occurrences, 2 files |
| SIHRE | **—** | (expansion unresolved — see 06 §5) | n/a | n/a | **RESEARCH.** 62 occurrences, 22 files, 0 in code |
| Domain Plane | **—** | — | n/a | n/a | **⛔ NOT EVEN RESEARCH. 0 occurrences.** |
| Simulation | `demo.py`, `evals/corpus/` | Replay against a fixed corpus | Low | `MANIFEST.sha256` | **PARTIAL** |
| Benchmarking | `metrics.py`, `calibration.py`, `reliability.py` | Activity metric paired with outcome metric | Moderate | — | **PARTIAL** |
| Registries | `registry.py` | (shape, layer) → workflow, versioned by SKILL.md hash | Fan-in 1 | `unproven()` | **CODE — exists.** ⚠ Fan-in 1: nearly unwired |
| NERVE UI | `switchboard.py`, `switchboard_p1.py`, `switchboard_render.py` (3,403 lines) | Projection + action surface | Self-contained | HTML render | **CODE — exists as "Switchboard".** ⚠ NERVE is the *proposed rename*; see 06 §3 |

**Two findings fall out of this table and neither is a naming problem:**

1. ⭐ **`readiness.py` is 1,948 lines with fan-in 16** — the largest module and among the most
   depended-upon. If anything in `factory/` warrants splitting, it is this one, and the split is by
   *phase* (its own 5-phase structure), not by CELL OS concept. **Out of scope here**; recorded so
   the option is visible.
2. ⭐ **`registry.py` has fan-in 1.** A registry nearly nothing consults. Possibly correct
   (`unproven()` is a guard), possibly a built-but-unwired module. **A finding for a future session,
   not for this migration.**

---

## 7. What this structure buys, stated as a testable claim

> After Phase 2, a reader can answer *"is this built?"* for any named CELL OS concept **by looking
> at which directory the document is in** — and be right, because `canonical/` admits nothing that
> code or a test cannot back, and `proposed/` says so in its README.

Today that question requires reading `docs/agent-army/CURRENT_STATE.md`,
`.agent-platform/RECONCILIATION.md` and `docs/_index/current_vs_proposed.md`, and knowing that all
three outrank `docs/raw_research/`. The structure makes the precedence legible from the path.

That claim is falsifiable, and Batch 9 tests it: **pick three concepts at random, resolve each from
its path alone, and check the answer against `CURRENT_STATE.md`.** If the paths disagree with the
code-measured instrument, the structure is wrong and the instrument is right.

---

## 8. PROJECT TRACKER — design (added 2026-09-03 by operator requirement)

**Phase 1 proposal only.** Nothing below is implemented. It is built in Batch 5 and Batch 8, after
the Phase 2 approval conditions in `05_MIGRATION_PLAN.md` §0 are met.

### 8.0 Existing progress artifacts — preserved, not replaced

The requirement says *"Preserve any useful existing progress artifact rather than creating a
conflicting tracker."* Four were found. **None is a project tracker, and all four survive:**

| Existing artifact | What it actually is | Disposition |
|---|---|---|
| `factory/roadmap.py` + `board.py` | Derives a roadmap from **gate verdicts**. `roadmap.py` "has no task list, by design" | ⭐ **KEEP AND CONSUME.** Its gate verdicts become the `verification_status` input, so tracker completion is anchored to measured gates rather than to self-report |
| `.claude/commands/af-status.md` | Runtime status over `factory.autonomy` — live run state, not project state | KEEP. Orthogonal. `/cell-status` reads the tracker; `/af-status` reads the running DAG |
| `docs/board/tickets.json` + `index.html` | A board artifact with fixtures | KEEP. Evaluate in Batch 5 as a **migration source** for the first ticket set — Decision D-8 |
| `.agent-platform/bootstrap/schemas/platform-progress.schema.json` | A **schema from the stranger's pack**, no instrument behind it | READ FOR IDEAS ONLY. ⚠ README §VII forbids treating it as a specification |

⭐ **`roadmap.py` is the important one.** The repository already refuses to let a task list assert
progress; progress is derived from gate verdicts. A tracker that lets a human type "COMPLETE" would
be a regression against that discipline. §8.2 carries the constraint into the schema.

### 8.1 The single source of truth, and the generated views

```
docs/status/PROJECT_PROGRESS.yaml     ⭐ AUTHORITATIVE. Hand-edited + Claude-edited. In git.
        │
        ├── project_progress.json     GENERATED. UI projection. Regenerate; never hand-edit.
        ├── PROJECT_PROGRESS.md       GENERATED. Readable view. Never hand-edit.
        └── forecast_history.jsonl    APPEND-ONLY. One row per forecast run → "what changed?"
```

**Rule, enforced by a test, not by a comment:** `project_progress.json` and `PROJECT_PROGRESS.md`
are regenerated from the YAML and compared byte-for-byte with what is on disk. A drifted view fails
the suite. This is the same mechanism as the existing `tests/test_tracker_is_current.py`.

⛔ **The artifact holds no progress values of its own.** `cell-os-tracker.html` fetches
`project_progress.json`. A number typed into HTML is a number nothing can regenerate — the exact
failure the estate's own §V.3 rule exists to stop, and which `README.md` §VII is currently
committing (its "66 modules / 22,817 lines" measures 68 / 23,939).

### 8.2 The state model

Nine states, as specified:

```
NOT_STARTED → READY → IN_PROGRESS → VERIFYING → COMPLETE
                 ↘ BLOCKED ↗    ↘ NEEDS_HUMAN ↗
                                    DEFERRED   SUPERSEDED
```

⛔ **`COMPLETE` requires acceptance evidence and is refused without it.** Enforced in
`factory/progress.py`, not documented in prose — precedent: `factory/tasks.py` already
`raise EvidenceRequired` on close, and `docs/protocol/` already defines the evidence classes.

```yaml
# a COMPLETE ticket without this block is a ValidationError, not a warning
acceptance_evidence:
  kind: TEST | RENDER | GATE | ARTIFACT | RESEARCH_ANSWER | MEASUREMENT
  ref: "tests/test_progress.py::test_forecast_is_reproducible"   # or a path, gate id, or commit
  verified_at: 2026-09-04
  verified_by: pytest | render_check | human
```

⚠ **`VERIFYING` is not a courtesy state.** It is where a ticket sits when work is done and evidence
is not yet in. Without it, the pressure is to mark `COMPLETE` and backfill — which is how a claim
becomes a fact. It maps to the repository's existing `UNMEASURABLE`: *the work may be fine; the
instrument has not looked yet.*

### 8.3 `docs/status/PROJECT_PROGRESS.yaml` — schema

```yaml
schema_version: 1
project: CELL OS
generated: {at: 2026-09-04, by: "factory.progress", repo_head: <sha>}

current_mission: CELL-M-03
current_phase: P2
current_session: {id: <uuid>, started: <iso>, focus: "..."}

calendar:
  planned_days_per_week: 4          # ⭐ operator input, the only planning assumption
  flow_efficiency: 0.65             # measured from IN_PROGRESS→COMPLETE vs elapsed; DERIVED

phases:
  - {id: P0, title: Restructure, status: IN_PROGRESS, milestones: [M-01, M-02]}

milestones:
  - {id: M-01, title: "Indexes and intake", phase: P0, epics: [E-01], depends_on: [], target: null}
    # ⛔ `target` is null on purpose. Dates are FORECAST, never typed.

epics:      [{id: E-01, title: ..., milestone: M-01, tickets: [CELL-001, ...]}]

research_lanes:                      # joins docs/_index/research_registry.yaml — never duplicates it
  - {id: R20, registry_ref: "research_registry.yaml#R20", status: NOT_RUN,
     blocks: [E-04], ingested: false, synthesized: false, canonical_integration: NOT_STARTED}

architecture_decisions:
  - {id: ADR-0001, title: "Keep one Python distribution", status: ACCEPTED,
     path: docs/decisions/0001-keep-one-python-distribution.md, blocks: []}

tickets:
  - id: CELL-001
    title: "Delta-pass the corpus index over the 169 new files"
    phase: P0
    epic: E-01
    subsystem: index                # index|architecture|research|nerve|runtime|evidence|governance
    kind: IMPLEMENTATION            # RESEARCH | IMPLEMENTATION | DECISION | VALIDATION
    required: true                  # required vs optional for the milestone
    priority: CRITICAL
    owner: claude                   # claude | human | either
    status: READY
    maturity: SPECIFIED             # PROVEN|PARTIAL|SPECIFIED|PROPOSED|EXPERIMENTAL|SUPERSEDED
    points: 5
    uncertainty: 1.3                # multiplier; 1.0 well-understood … 2.5 speculative
    depends_on: []
    blocks: [CELL-004]
    session_command: "/cell-work CELL-001"     # ⭐ §8.6 — the copyable string
    acceptance:
      - "corpus_manifest.yaml coverage.files_on_disk_in_scope == find(...) | wc -l"
    acceptance_evidence: null       # REQUIRED before status may become COMPLETE
    history:
      - {at: 2026-09-04, from: NOT_STARTED, to: READY, session: <uuid>, note: "..."}

blockers:
  - {id: B-01, ticket: CELL-004, opened: 2026-09-04, kind: NEEDS_HUMAN,
     description: "Worktree decision D-1", probability_persists_7d: 0.4}

scope_log:                           # ⭐ every add/remove, so scope growth is MEASURED not felt
  - {at: 2026-09-04, delta_points: +5, reason: "PROJECT TRACKER requirement added", tickets: [CELL-030]}

rework_log:
  - {at: ..., ticket: CELL-00x, points: 2, reason: "acceptance evidence rejected"}

velocity:                            # ⭐ ALL DERIVED. Never hand-written.
  active_days: []                    # [{date, accepted_points, tickets:[...]}]
  smoothed_active_day_velocity: null
  observed_days_per_week_28d: null

forecast:                            # ⭐ ALL GENERATED by factory/forecast.py
  computed_at: null
  method: null                       # MONTE_CARLO | LOW_CONFIDENCE_HEURISTIC
  p50: null
  p80: null
  confidence: null                   # HIGH | MEDIUM | LOW | INSUFFICIENT_HISTORY
  drivers: []
  movement_since_last: []

next_recommended_session: null       # GENERATED by §8.7
last_updated: null
```

⭐ **Design rule visible in the schema: every field is marked as operator input, DERIVED, or
GENERATED.** Only `calendar.planned_days_per_week`, ticket definitions, and status transitions with
evidence are hand-written. Velocity and forecast are computed or absent. That is `README.md` §V.2's
basis vocabulary applied to a data file.

### 8.4 `factory/forecast.py` — the Dynamic Due Date Engine

Implements the specified quantities exactly:

```python
remaining_effort      = Σ(remaining_points × uncertainty_multiplier)
active_day_velocity   = accepted_points / active_project_days
effective_days_week   = 0.60 × planned_days_per_week + 0.40 × observed_28d
weekly_capacity       = robust_active_day_velocity × effective_days_week × flow_efficiency
smoothed_velocity     = 0.30 × today + 0.70 × previous_smoothed        # EWMA
```

`robust_active_day_velocity` uses the **median of the trailing 10 active days**, not the mean — one
extraordinary day must not move the date.

**Monte Carlo, ≥1,000 runs**, each: sample weekly active days from observed history blended with the
plan; sample accepted points per active day from recent active days; respect `depends_on`; apply
`uncertainty` ranges; roll each open blocker against `probability_persists_7d`; apply the observed
rework rate; advance until all `required: true` work in the milestone is COMPLETE.
Report P50, P80, confidence, and the top drivers.

⛔ **The gate that keeps this honest:**

```python
if len(active_days) < 8:
    method     = "LOW_CONFIDENCE_HEURISTIC"
    confidence = "INSUFFICIENT_HISTORY"
    # P50/P80 are emitted as a RANGE with an explicit banner. No Monte Carlo is run.
```

This is the brief's own instruction — *"Do not pretend the forecast is statistically mature"* — and
it is the same rule as `README.md` §V.1's `UNMEASURABLE`. **A forecast from an instrument with no
history is not a forecast.** The UI must render the low-confidence state visibly differently, not as
a normal date with a small caveat.

**Forecast movement.** Every run appends to `forecast_history.jsonl`; the delta is attributed by
re-running the simulation with one input reverted at a time:

```
P50 moved 4 days earlier
  + 7 accepted points completed          (−3 days)
  + observed work frequency 2.8 → 3.4/wk (−2 days)
  − 2 points of new scope                (+1 day)
  − CELL-004 blocked on decision D-1     (+0 days, not on critical path)
```

Damping, as required: movement is clamped to **±15% of remaining calendar per run**, and a single
missed day cannot move P50 by more than the smoothing allows. **No streaks, no failure state for a
quiet day.**

### 8.5 Tracker UI architecture

**`docs/artifacts/cell-os-tracker.html` — a PROJECT TRACKER tab inside the existing CELL OS artifact
shell. The shell is not redesigned.** It adopts `docs/design/claude-design/cell-os.global.yaml`
tokens and the `docs/marketing/cell-os-launch-v1/` visual system.

```
cell-os-tracker.html
   └── fetch("project_progress.json")     ⛔ the ONLY data source. No inline numbers.
         ├── Executive overview   weighted completion · phase · milestone · P50 · P80 ·
         │                        confidence · planned-vs-observed days/wk · accepted velocity ·
         │                        blockers · scope change · next recommended action
         ├── Roadmap              phases, milestones, dependencies, forecast dates
         ├── Ticket board         filter: phase·subsystem·status·priority·owner·
         │                        research-vs-implementation·required-vs-optional·blocker·maturity
         ├── Research tracker     completed · NOT_RUN · active lane · dependency readiness ·
         │                        ingestion · synthesis · canonical integration
         ├── Architecture maturity   PROVEN|PARTIAL|SPECIFIED|PROPOSED|EXPERIMENTAL|SUPERSEDED heatmap
         ├── Evidence coverage    % of COMPLETE claims carrying acceptance_evidence
         └── Next Best Session    persistent panel (§8.7)
```

Visualisations, per requirement: burn-up (completed vs total scope, so scope growth is *visible* as
a rising ceiling); forecast fan chart (P50/P80 bands); phase/milestone timeline; dependency DAG with
critical path; maturity heatmap; research-lane progress; capability-unlock constellation; momentum
sparkline; blocker-aging panel; "What changed?" panel driven by `forecast_history.jsonl`; milestone
completion moments.

⭐ **Two things this tracker must refuse to do**, both of which follow from the repository's own
discipline rather than from taste:

1. **Never render a completion % whose evidence coverage is not shown beside it.** A weighted
   completion of 60% with 20% evidence coverage is one number, not two.
2. **Never show a P50 date in the same visual weight as a measured number** when
   `confidence: INSUFFICIENT_HISTORY`. It is `PROXY` basis and must look like it.

**Rendering is validated the way every other surface here is** — `scripts/render_check_tracker.py`
following the eight existing `render_check_*.py`, capturing light/dark × 760/1100/1440 plus a no-JS
pass into `docs/evidence/`. Per the global rule, a query-layer pass is not a rendered-surface pass.

### 8.6 ⭐ Linking tickets to sessions — the ticket ID *is* the command

The operator asked for the most efficient phone-first route, with no Switchboard.

**One command, parameterised by ticket ID:**

```
/cell-work CELL-042
```

`.claude/commands/cell-work.md` reads `docs/status/PROJECT_PROGRESS.yaml`, resolves `CELL-042`, and
from the ticket's own `phase`, `kind` and `status` dispatches to the right protocol —
`cell-plan-mission` for a `READY` `IMPLEMENTATION` ticket, `cell-intake-research` for a `RESEARCH`
lane, `cell-verify` for one in `VERIFYING`. **The data already knows the phase; the operator should
not have to.**

Each ticket row in the tracker renders a copy-chip emitting exactly its `session_command` string.

```
Phone:  open published tracker → tap ticket → copy → paste into Claude Code (web/mobile)
```

Rejected alternatives, and why:

| Alternative | Rejected because |
|---|---|
| Per-phase commands (`/cell-phase-3-implement CELL-042`) | Forces the operator to know the phase. The YAML knows it. Eight commands to maintain instead of one. |
| A URL scheme that launches a session from the artifact | No supported mechanism exists. Building on one would be guesswork, and the brief forbids inferring capability. |
| Driving it through Switchboard | Operator explicitly excluded it, and `switchboard*.py` is 3,403 lines of surface this does not need. |

⚠ **One honest limitation, stated rather than discovered later:** a Claude Code session started from
a phone still needs the repository. Claude Code on web operates on a cloud checkout, so
`PROJECT_PROGRESS.yaml` must be **committed** for a phone session to see current state. That makes
`/cell-session-close` committing the tracker a *functional requirement* of the phone workflow, not
housekeeping. It does **not** imply pushing — Decision D-2 in `05_MIGRATION_PLAN.md` §0 covers
whether a cloud checkout is in play at all.

### 8.7 The Claude session-update protocol

Bound to the eight steps in the requirement, each mapped to a command that enforces it:

| # | Step | Command | Enforcement |
|---|---|---|---|
| 1 | Read progress at session start | `/cell-session-start` | Prints current mission + tickets; refuses to proceed if the YAML fails schema validation |
| 2 | Identify active mission and tickets | `/cell-session-start` | Reads `current_mission`, filters `READY`/`IN_PROGRESS` |
| 3 | **Update status only with evidence** | `/cell-verify` | ⛔ `factory.progress` raises on `COMPLETE` without `acceptance_evidence` |
| 4 | Record scope changes and blockers | `/cell-update-progress` | Appends to `scope_log` / `blockers`; a scope change with no reason is rejected |
| 5 | Update accepted effort | `/cell-update-progress` | Appends an `active_days` row. **Accepted points only** — closures without evidence score zero |
| 6 | Recalculate forecast | `/cell-update-progress` | Runs `factory.forecast`; appends to `forecast_history.jsonl` |
| 7 | Write a session summary | `/cell-session-close` | Appends to ticket `history` + regenerates both views |
| 8 | Recommend next best session | `/cell-session-close` | Writes `next_recommended_session` |

**Next Best Session** is computed, not chosen: rank unblocked `READY` tickets by
`(critical_path_membership × unblock_count × priority_weight) / (points × uncertainty)`, filter by
available session length, and exclude anything whose prerequisite artifacts are absent. Rendered as:

```
NEXT BEST SESSION
Ingest CELL-DR-01 and resolve terminology conflicts
Estimated focus: 60–90 minutes
Unlocks: Lanes 02, 03 and 04
```

⚠ **`owner: human` tickets are surfaced separately and never recommended to Claude.** The seven
decisions in `05_MIGRATION_PLAN.md` §0 are the first such rows, and a tracker that quietly proposed
Claude resolve them would be answering questions that are the operator's to answer.

### 8.8 Validation tests

| Test | Asserts | Why this one |
|---|---|---|
| `test_progress_schema_validates` | The YAML matches schema; unknown keys rejected | A silently-ignored key is a silently-lost ticket |
| `test_complete_requires_evidence` | `COMPLETE` without `acceptance_evidence` raises | ⭐ **The load-bearing test.** Mirrors `tasks.py`'s `EvidenceRequired` |
| `test_views_are_current` | Regenerated `.json`/`.md` match disk byte-for-byte | Mirrors `tests/test_tracker_is_current.py` |
| `test_no_progress_number_is_hand_written_in_html` | No numeric literal in the tracker HTML outside the fetch path | ⛔ The rule that stops README §VII's drift recurring |
| `test_forecast_is_reproducible` | Same inputs + seed → same P50/P80 | An irreproducible forecast is not a measurement |
| `test_forecast_refuses_below_eight_active_days` | `< 8` active days ⇒ `LOW_CONFIDENCE_HEURISTIC`, no Monte Carlo | ⭐ **The negative control.** Proves the honesty gate can fire |
| `test_forecast_moves_in_the_right_direction` | +velocity ⇒ earlier; +scope ⇒ later; +blocker ⇒ later-or-equal | Catches a sign error that would otherwise look plausible |
| `test_dependencies_are_acyclic` | Ticket graph is a DAG | A cycle makes the simulation non-terminating |
| `test_every_ticket_command_resolves` | Every `session_command` names a ticket that exists | ⭐ Stops a phone copy-chip from pasting a dead command |
| `test_scope_growth_is_logged` | Total points change ⇒ a `scope_log` row | Unlogged scope growth is how a date slips invisibly |

⭐ **The two starred negative controls matter more than the positive tests.** The repository's own
`evals.py` exists to answer *"can the contract actually fail?"*, and a forecast engine that has never
been shown refusing is in exactly the position `README.md` Part I describes: capable, unmeasured.

### 8.9 Example populated state, and migration from an existing tracker

Batch 5 delivers `docs/status/examples/PROJECT_PROGRESS.example.yaml` — a populated 12-ticket,
3-milestone state with 10 active days of synthetic velocity, sufficient to exercise Monte Carlo and
serve as the tests' fixture.

**Migration source.** There is no tracker to migrate *from*. The first real ticket set is seeded from
material that already exists, in this precedence:

1. `05_MIGRATION_PLAN.md`'s ten batches → the P0 phase (this is the only fully-specified work today).
2. `docs/research/backlog.yaml` — 26 `NOT_DISPATCHED` candidates → research lanes, by reference.
3. `docs/_index/research_gap_candidates.md` — GAP-01, -08, -09, -26, -27, -30 → tickets, most of
   which the backlog already marks `type: NOT_RESEARCH` (i.e. **do them, don't research them**).
4. `docs/board/tickets.json` — evaluate as a source (**Decision D-8**).
5. ⛔ `docs/raw_research/CELL_OS_Delivery_Backlog_v0.2.xlsx` — **the natural seed, and unreadable.**
   No `.xlsx` converter exists here. **Decision D-5.**

⚠ **Seeding from the migration plan first is deliberate.** A tracker seeded from the CELL OS delivery
backlog would open with ~100 tickets for a product whose canonical architecture is still in an
unopened ZIP — and would immediately produce a P50 date for work nobody has scoped. Ten batches with
real acceptance criteria give the forecast engine something it can actually measure, and eight
active days of history before it is allowed to state a date at all.
