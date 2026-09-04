# 03 — Current → target migration map

**Phase 1 proposal.** Every row is a proposal. No path in this table has been moved, renamed or
deleted. Measured against `827f871`, 2026-09-03.

## How to read this table

| Action | Meaning |
|---|---|
| `NO MOVE` | Stays exactly where it is. Where flagged ⛔, moving it **breaks the runtime silently** |
| `CREATE` | New directory or file. Every one has content on day one |
| `git mv` | Tracked file, history preserved |
| `mv` | **Untracked** file. `git mv` cannot be used; no history exists to preserve |
| `COPY` | Original stays; a derived copy is written elsewhere. Used for immutable sources |
| `EXTRACT` | A targeted read-out of one file from a ZIP. ⛔ Never an unzip over an existing path |
| `RETIRE` | Moved to `docs/archive/`. ⛔ **Never deleted** |

**Risk** is `LOW` / `MED` / `HIGH` for the *migration*, not for the artifact.

---

## Part 1 — The paths that must NOT move

⛔ **This is the most important table in the plan.** Each of these is read by `factory/` at a
hard-coded path. Moving any produces a **silent** failure — a gate reporting "nothing found", not an
`ImportError`. That is the exact failure class this repository exists to prevent, and the tidy-up
would be the thing introducing it.

| Current path | Proposed path | Action | Reason | References affected | Risk |
|---|---|---|---|---|---|
| `docs/findings.d/` | — | **NO MOVE** ⛔ | `factory/findings.py:29` (`FRAGMENTS`) reads it as data | `factory/findings.py`, `bus.py:12,138`, `switchboard.py:516,1149`, `switchboard_render.py:232`, `tests/test_findings.py`, 3 `scripts/build_r*_pack.py` | **HIGH** |
| `docs/findings.md` | — | **NO MOVE** ⛔ | `factory/findings.py:24` (`LEDGER`) | same | **HIGH** |
| `docs/artifacts/agent-factory.html` | — | **NO MOVE** ⛔ | `factory/schedule.py:46` (`ARTIFACT_REL`), `readiness.py:647` | `schedule.py`, `readiness.py`, `lanes.py:207,216` | **HIGH** |
| `docs/research/answers/` | — | **NO MOVE** ⛔ | `readiness.py:1711`, `research_run.py:366`, `synthesis.py:225` | 3 modules + `lanes.py:139` | **HIGH** |
| `docs/evidence/` | — | **NO MOVE** ⛔ | `readiness.py:1736` globs `render-pass-*.md`; 8 `render_check_*.py` write here | `readiness.py`, all render checks | **HIGH** |
| `docs/research/SYNTHESIS.md` | — | **NO MOVE** | `factory/synthesis.py:3` | `synthesis.py` | MED |
| `docs/specs/{golden-workflow-fit,control-room,terminal-configuration,architecture-v0,client-review-loop-v0}.md` | — | **NO MOVE** | Named in `factory/` docstrings: `context.py:28`, `registry.py:181`, `switchboard.py:28`, `client_review.py:33` | 4 modules | MED |
| `docs/raw_research/` | — | **NO MOVE** ⛔ | Brief: *"Do not alter files inside `docs/raw_research/`"*. 326 files | `docs/_index/*` | **HIGH** |
| `docs/release-gate/` | — | **NO MOVE** ⛔ | AF-RELEASE-GATE-01 is **BLOCKED**; deliberately untracked | — | **HIGH** |
| `factory/`, `tests/`, `scripts/`, `evaluator_service/`, `evals/`, `blueprints/`, `missions/`, `.agent-platform/`, `boot-prompts/` | — | **NO MOVE** | See `04` §1 — one Python distribution | — | — |

⚠ **`docs/artifacts/` receives one new file** (`cell-os-tracker.html`, Batch 5). An *addition* to a
runtime-coupled directory is safe; a *move within* it is not.

---

## Part 2 — Batch 1: indexes and intake conventions

| Current path | Proposed path | Action | Reason | References affected | Risk |
|---|---|---|---|---|---|
| — | `docs/_incoming/` | **CREATE** | The missing lifecycle stage. Its absence is why 2 rendered artifacts and 1 synthesis are shelved as raw research | none | LOW |
| — | `docs/_incoming/README.md` | **CREATE** | The intake contract (`04` §3) | none | LOW |
| `docs/_index/corpus_manifest.yaml` | *same* | **DELTA-EDIT** | Stale by 169 files. `coverage.files_on_disk_in_scope: 719` → 888 | `docs/_index/*` cross-refs | MED |
| `docs/_index/duplicate_clusters.md` | *same* | **DELTA-EDIT** | +DC-14, DC-15, DC-16 (`02` Part D) | none | LOW |
| `docs/_index/concept_index.yaml` | *same* | **DELTA-EDIT** | CELL OS ontology terms absent | none | MED |
| — | `docs/_index/research_registry.yaml` | **CREATE** | Does not exist. Brief task 6 | `07` | LOW |
| — | `docs/_index/research_status.md` | **CREATE** | Generated view of the above | none | LOW |
| — | `scripts/build_corpus_index.py` | **CREATE** | ⭐ Mechanical fields must stop being hand-maintained. 169-file drift in one day is the proof | none | MED |

⚠ **`corpus_manifest.yaml` is 275 KB of hand-authored interpretation.** The delta pass **adds
records and corrects `coverage`**; it does not rewrite existing records. A regeneration that
discarded the interpretive fields would destroy the corpus's most expensive artifact.

---

## Part 3 — Batch 2: raw and synthesized research

| Current path | Proposed path | Action | Reason | References affected | Risk |
|---|---|---|---|---|---|
| `…/CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip` → `01_CANONICAL_ONTOLOGY/CELL_OS_Canonical_Terminology_vNext.md` | `docs/architecture/canonical/terminology/CELL_OS_Canonical_Terminology_vNext.md` | **EXTRACT** | ⭐ The canonical ontology is inside an unopened ZIP. Nothing in the repo can grep it | `06` | MED |
| same ZIP → `01_CANONICAL_ONTOLOGY/KNOWN_TERMINOLOGY_COLLISIONS.md` | `docs/architecture/canonical/terminology/KNOWN_TERMINOLOGY_COLLISIONS.md` | **EXTRACT** | The collision register brief task 4 asks to be built — it already exists | `06` | MED |
| `docs/design/CELL_OS_Product_Technical_Design_v0.1.docx` | `docs/raw_research/converted/CELL_OS_Product_Technical_Design_v0.1.md` | **COPY** (convert) | ⭐ Highest-value unread artifact. Its cross-ref audit is searchable; the source is not. Converter exists: `scripts/docx_to_md.py`, verified 100.1% | `02` | MED |
| `…/CELL_OS_Master_…_User_Guide_v0.2.docx` | `docs/raw_research/converted/…v0.2.md` | **COPY** (convert) | Extends GAP-01 | none | LOW |
| `docs/raw_research/CELL_OS_Product_Technical_Design_v0.1_Crossreference_Audit_v1.md` | `docs/research/syntheses/…` | **COPY, then RETIRE original** | ⛔ **A synthesis shelved as a primary source.** Immutability forbids `mv`, so: copy out, leave a stub | `06` | MED |
| `docs/raw_research/cell-foundry-cross-domain-pipeline.html` | `docs/artifacts/incoming/…` | **mv** (untracked) | A rendered artifact, not research | none | LOW |
| `docs/raw_research/Agent Factory- Switchboard View.html` | `docs/artifacts/incoming/…` | **mv** (untracked) | Same. ⚠ Note the *old* name on a *new* (2026-09-02) file | none | LOW |
| `CELL_OS_NERVE_Design_Intelligence_MetaSkill_v1.zip` (repo root) | `docs/_incoming/` | **mv** (untracked) | A download in the repo root. Byte-identical copy already in `docs/design/` | none | LOW |
| `docs/raw_research/CELL_OS_Delivery_Backlog_v0.2.xlsx` | — | **NO MOVE**, ⛔ **UNREADABLE** | No `.xlsx` converter exists. Stays `NOT-VISIBLE` after Phase 2. **Decision D-5** | `04` §8.9 | — |
| `docs/raw_research/CELL OS Design Master Brief.pdf` | — | **NO MOVE**, ⛔ **UNREADABLE** | No PDF extractor | none | — |

⭐ **The pattern in this batch: `COPY`, never `mv`, out of `docs/raw_research/`.** The brief forbids
altering it, and a `mv` alters it by subtraction. Every derived copy carries a provenance header
naming the source path and SHA-256.

---

## Part 4 — Batch 3: canonical and proposed architecture

| Current path | Proposed path | Action | Reason | References affected | Risk |
|---|---|---|---|---|---|
| — | `docs/architecture/canonical/README.md` | **CREATE** | ⭐ The 10-tier precedence rule (`04` §4), promoted from a comment inside `corpus_manifest.yaml` | all of `docs/` | LOW |
| — | `docs/architecture/proposed/README.md` | **CREATE** | "Nothing here is implemented" | none | LOW |
| — | `docs/architecture/proposed/{nerve-switchboard,cell-mesh-and-links,cell-genome,cell-adapt,hypermesh-and-memory,sihre,domain-plane}.md` | **CREATE** (7) | Seven named subsystems with **no code**. Kept out of `packages/` deliberately (`04` §1) | `06` | LOW |
| — | `docs/decisions/README.md` + `0001-keep-one-python-distribution.md` | **CREATE** | No ADR home exists. Decisions currently live inline in README and boot-prompts | none | LOW |
| `docs/diagrams/` (4 files, untracked) | `docs/architecture/diagrams/` | **mv** | A top-level `docs/diagrams/` orphan; 3 are CELL OS | none | LOW |
| `docs/raw_research/CELL_OS_Architecture_Overview_Diagram.png` | `docs/architecture/diagrams/` | **COPY** | ⚠ **Different bytes** from `docs/diagrams/CELL OS - Architecture Overview.png` (1,282,877 vs 1,821,873). Two overview diagrams; which is current is UNKNOWN. **Decision D-6** | none | MED |
| `docs/agent-army/CURRENT_STATE.md` | — | **NO MOVE** | ⭐ Code-measured; tier 2 in the precedence rule. `canonical/README.md` **points at it** | `docs/_index/*` | — |

---

## Part 5 — Batch 4: product, UX, NERVE artifacts

| Current path | Proposed path | Action | Reason | References affected | Risk |
|---|---|---|---|---|---|
| — | `docs/product/README.md` | **CREATE** | Pointer-only index over `docs/specs/`, `docs/marketing/`, `docs/design/` | none | LOW |
| `docs/marketing/cell-os-launch-v1/` | — | **NO MOVE** | Already correct. ⭐ Where most CELL OS prose actually lives | none | — |
| `docs/design/`, `docs/specs/` | — | **NO MOVE** | Specs are named from `factory/` docstrings | — | — |
| `docs/combined-execution-research-v2-2026-09-02/` (28 files) | `docs/archive/` | **RETIRE** | ⛔ **100% byte-identical** to the extracted pack under `docs/raw_research/`. DC-14. **Never deleted** | check for links first | MED |

⚠ **DC-14 is retired, not deleted, and only after a link check.** All 28 are untracked, so this is a
plain `mv` with no history to lose — which also means **no `git revert` can undo it**. The rollback
is the recorded inverse `mv`.

---

## Part 6 — Batch 5: evidence, project status and the PROJECT TRACKER

| Current path | Proposed path | Action | Reason | References affected | Risk |
|---|---|---|---|---|---|
| `docs/evidence/` | — | **NO MOVE** ⛔ | Runtime-coupled | — | — |
| — | `docs/status/PROJECT_PROGRESS.yaml` | **CREATE** | ⭐ No tracker exists anywhere. Single source of truth (`04` §8.1) | `04` §8 | MED |
| — | `docs/status/project_progress.json` | **CREATE (generated)** | UI projection. ⛔ Never hand-edited | tracker HTML | LOW |
| — | `docs/status/PROJECT_PROGRESS.md` | **CREATE (generated)** | Readable view | none | LOW |
| — | `docs/status/forecast_history.jsonl` | **CREATE (append-only)** | Drives "what changed?" (`04` §8.4) | none | LOW |
| — | `docs/status/examples/PROJECT_PROGRESS.example.yaml` | **CREATE** | Populated 12-ticket fixture; exercises Monte Carlo | tests | LOW |
| — | `factory/progress.py` | **CREATE** | Load/validate/write. ⛔ Raises on `COMPLETE` without evidence | tests | MED |
| — | `factory/forecast.py` | **CREATE** | The Dynamic Due Date Engine (`04` §8.4) | tests | **HIGH** |
| — | `docs/artifacts/cell-os-tracker.html` | **CREATE** | PROJECT TRACKER tab. ⚠ An **addition** to a runtime-coupled dir, not a move | `render_check_tracker.py` | MED |
| — | `scripts/render_check_tracker.py` | **CREATE** | Rendered-surface validation, following the 8 existing render checks | `docs/evidence/` | MED |
| — | `tests/test_progress.py`, `tests/test_forecast.py` | **CREATE** | 10 tests incl. 2 negative controls (`04` §8.8) | — | MED |
| `docs/board/tickets.json` | — | **NO MOVE**, evaluate | Possible seed for the first ticket set. **Decision D-8** | none | LOW |
| `factory/roadmap.py`, `board.py` | — | **NO MOVE** | ⭐ **CONSUMED, not replaced.** Gate verdicts feed `verification_status` so completion stays anchored to measured gates | `progress.py` | MED |

⛔ **`factory/forecast.py` is the highest-risk item in the whole plan** — the only new module doing
non-trivial computation, and the only one that can produce a **confident wrong number**. Its two
negative-control tests (`test_forecast_refuses_below_eight_active_days`,
`test_forecast_moves_in_the_right_direction`) are not optional; without them it is exactly the
"capable but unmeasured" shape `README.md` Part I is organised against.

---

## Part 7 — Batch 6: code

| Current path | Proposed path | Action | Reason | References affected | Risk |
|---|---|---|---|---|---|
| `factory/` (68 modules) | — | **NO MOVE** | One distribution, one flat package, fan-in centred on `contract.py` (`04` §1, §6) | — | — |
| `factory/readiness.py` (1,948 lines, fan-in 16) | — | **NO MOVE**, recorded | ⭐ The one real refactor candidate. Split by its own 5 phases, **not** by CELL OS concept. Out of scope | — | — |
| `factory/registry.py` (fan-in 1) | — | **NO MOVE**, recorded | ⭐ A registry almost nothing consults. Possibly correct, possibly unwired. A finding, not a migration | — | — |
| — | `packages/`, `apps/`, `domains/` | ⛔ **NOT CREATED** | 7 of the brief's named concepts have **0 occurrences**; `configuration-genome` has 1. Empty by construction | — | — |

**Only two files are added to `factory/` in the entire migration** — `progress.py` and
`forecast.py` — and both exist because the tracker requirement needs them. No existing module moves.

---

## Part 8 — Batches 7–8: references and commands

| Current path | Proposed path | Action | Reason | References affected | Risk |
|---|---|---|---|---|---|
| `README.md` §VII repo map | *edit in place* | **EDIT** | ⚠ Claims `factory/` is "66 modules, 22,817 lines"; measures **68 / 23,939**. Add the regeneration command per its own §V.3 | — | LOW |
| `README.md` §VII | *edit in place* | **EDIT** | Add `docs/_incoming/`, `architecture/`, `decisions/`, `status/`, `product/`, `archive/` | — | LOW |
| `.gitignore` | *edit in place* | **EDIT** | ⛔ Add `docs/status/project_progress.json`? **NO** — the tracker must be committed for phone sessions (`04` §8.6). Verify no rule silently un-ignores after moves | release gate | **HIGH** |
| 219 relative `.md` links across `docs/` | *rewrite affected* | **EDIT** | Only links into moved paths | link check | MED |
| — | `.claude/commands/cell-{session-start,intake-research,audit,plan-mission,implement,verify,session-close,update-progress}.md` | **CREATE** (8) | Brief task 10. Follow the `af-*` shape | none | LOW |
| — | `.claude/commands/cell-work.md` | **CREATE** | ⭐ The ticket-ID entry point (`04` §8.6). `/cell-work CELL-042` | `PROJECT_PROGRESS.yaml` | MED |
| `.claude/commands/af-*.md` (6) | — | **NO MOVE** | Orthogonal: `/af-status` reads the running DAG, `/cell-status` reads project state | — | — |

⛔ **The `.gitignore` row is HIGH risk and it is not obvious why.** Four of its rules exclude files
**by path** on release-gate grounds. Re-pathing a rule during a restructure silently *un-ignores* its
target, and the target of one of them is a live client-data capture. **`.gitignore` is verified
before and after every batch**, not just this one.

---

## Part 9 — Summary of moves

| Category | Count | Action |
|---|---|---|
| Paths that must NOT move (runtime-coupled or immutable) | 10 groups | NO MOVE |
| Directories created | 9 | CREATE |
| Files created (docs) | ~20 | CREATE |
| Files created (code) | 5 | CREATE |
| Slash commands created | 9 | CREATE |
| `git mv` of tracked files | **0** | — |
| `mv` of untracked files | ~35 | mv |
| `COPY` out of immutable roots | 4 | COPY |
| `EXTRACT` from archives | 2 | EXTRACT |
| `RETIRE` to `docs/archive/` | 29 | RETIRE |
| Files deleted | **0** | ⛔ none |

⭐ **Zero tracked files move.** The entire migration is *additive plus untracked-file tidying*. That
is not a compromise — it is what the measurement produced: everything tracked is either
runtime-coupled, immutable, or already correctly placed. The repository's real problem is **two
missing lifecycle stages and a stale index**, not a bad layout.

**Consequence for rollback:** because no tracked file moves, `git checkout` restores the tracked tree
completely. The rollback risk is concentrated entirely in the ~35 untracked `mv`s and 29 `RETIRE`s,
which git cannot undo. Handled in `08_VALIDATION_AND_ROLLBACK_PLAN.md` §3.4 by a recorded,
executable inverse-move manifest written *before* each batch runs.
