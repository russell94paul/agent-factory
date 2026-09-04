# 01 — Repository audit

**Phase 1, read-only.** Measured 2026-09-03 against `agent-factory` @ `827f871` (branch `main`).
Nothing in this pass moved, renamed or deleted a file. The only writes are the eight planning
documents in this directory.

Every count below carries the command that produced it, per `README.md` §V.3. A number without a
command beside it is a number that has already started to rot.

---

## 0. The three findings that should change what happens next

### ⛔ 0.1 The corpus index this mission asks for already exists, and it is stale by 169 files

`docs/_index/` holds thirteen files — including six of the seven artifacts the mission brief names
as things to create. They were generated on 2026-09-02 against `fc78074`. The mission brief's task 5
says *"Do not create competing indexes if these already exist."* They exist.

They are also behind:

```bash
find docs .agent-platform blueprints missions evals boot-prompts -type f | wc -l
# 888          ← now
# 719          ← corpus_manifest.yaml `coverage.files_on_disk_in_scope`, 2026-09-02
```

That is the manifest's **own** stated regeneration command, run today. **169 files (23.5%) have
arrived since the index was written**, and they are almost entirely the CELL OS corpus.

The restructure's first job is therefore a **delta pass over an existing index**, not a new index.

### ⛔ 0.2 The CELL OS corpus is *prefix-covered* and *record-uncovered* — these are not the same thing

Sixty-three files under the indexed roots match no manifest record at all. But the more important
number is the one a naive coverage check hides: every CELL OS artifact under `docs/raw_research/`
resolves to a **single bundle record**, `AF-RAW-LOOSE`, whose `path` is the directory
`docs/raw_research/`. A path-prefix test says "covered". Reading the record says otherwise —
`AF-RAW-LOOSE` enumerates its members explicitly, and **not one CELL OS artifact is among them**.
Its `bundle_members` list names seven loose files plus `*.zip (11 sealed pack archives)`; there are
now twenty ZIPs under that root.

So: the index does not contradict the CELL OS material. It has never seen it.

This is the same shape as the estate's own recurring failure — a green check from an instrument
whose population was empty. Recorded here so the delta pass does not inherit "covered" as a finding.

### ⛔ 0.3 Seven of the concepts the mission brief names have **zero** occurrences in this repository

Measured over 1,001 text files in the working tree
(`scratchpad/term_scan.py`, reproduced in `06_TERMINOLOGY_SUPERSESSION.md` §1):

| Term from the brief | Occurrences | Files |
|---|---|---|
| Domain Plane | **0** | 0 |
| Domain Fabric | **0** | 0 |
| Domain Data Plane | **0** | 0 |
| Domain Genome | **0** | 0 |
| DOMAIN-MESH | **0** | 0 |
| DOMAIN-DB | **0** | 0 |
| CELL-Q | **0** | 0 |
| Configuration Genome | **1** | 1 |
| NERVE | 11 | 2 |
| CELL ADAPT | 13 | 2 |

The brief's provisional target tree asks for `packages/configuration-genome/`,
`packages/cell-adapt/` and `domains/quant-research/`. The brief also says *"Do not create empty
packages merely to make the repository appear sophisticated."* Those two instructions collide, and
the measurement decides it: **those directories would be empty by construction.** They are proposed
in `04_PROPOSED_TARGET_STRUCTURE.md` as documentation lanes under `docs/architecture/proposed/`,
not as code packages.

There is a second, sharper reason. The repository's own canonical ontology — recovered from
`docs/raw_research/CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip`,
`01_CANONICAL_ONTOLOGY/CELL_OS_Canonical_Terminology_vNext.md` — **does not contain the term
"Configuration Genome" at all**. It calls that concept **"Cell Blueprint / Cell Genome"**. Adopting
the brief's term would name a package after a word the project's own terminology draft does not use.
See `06_TERMINOLOGY_SUPERSESSION.md` §4.

---

## 1. Repository instructions and state

### 1.1 Instruction files — what governs, and what does not exist

| Expected by brief | Present? | Notes |
|---|---|---|
| `AGENTS.md` | **NO** | Does not exist anywhere in the tree |
| `CLAUDE.md` (repo root) | **NO** | Does not exist. Files matching `CLAUDE*` are all inbound-pack *prompts*, not instructions |
| `CONTRIBUTING.md` | **NO** | Does not exist |
| `LICENSE` | **NO** | Does not exist |
| `README.md` | **YES** | 46,811 bytes, 11 parts. **This is the governing instruction document** |

```bash
git ls-files | grep -iE "(CLAUDE|AGENTS|CONTRIBUTING|LICENSE)"
# 40 hits, every one of them inside docs/raw_research/ or .agent-platform/bootstrap/
```

**`README.md` is the de-facto AGENTS.md and the restructure must preserve its rules verbatim.**
The four that constrain this migration:

1. **§V.1 — the five verdicts, never collapsed.** `PASS` / `FAIL` / `UNMEASURABLE` / `ERROR` /
   `NOT_RUN`, with `ERROR` dominating `FAIL`. The mission brief's status vocabulary
   (`PROVEN`/`PARTIAL`/`SPECIFIED`/`PROPOSED`/`EXPERIMENTAL`/`SUPERSEDED`/`UNKNOWN`) is a
   *different* vocabulary about artifacts, not about measurements. They must not be merged. The
   inventory in `02_ARTIFACT_INVENTORY.yaml` uses the brief's vocabulary and says so explicitly.
2. **§V.2 — the basis vocabulary.** `MEASURED` / `DERIVED` / `ASSUMED` / `PROXY`, plus the four
   absence verdicts `ZERO` / `NOT-RECORDED` / `NOT-VISIBLE` / `NOT-RETAINED`.
3. **§V.3 — counts carry their regeneration command.** Applied throughout these eight documents.
4. **§VII — `.agent-platform/bootstrap/` is a proposal from a stranger**, and must never be treated
   as a specification or as evidence a subsystem exists.

### 1.2 Git state

```bash
git rev-parse --abbrev-ref HEAD          # main
git rev-parse --short HEAD               # 827f871
git status --porcelain | wc -l           # 69
git status --porcelain | awk '{print $1}' | sort | uniq -c
#   18 M
#   51 ??
```

**The working tree is DIRTY: 18 modified, 51 untracked entries** (several of the untracked entries
are directories, so the untracked *file* count is higher — 187, see §2).

Modified files split cleanly:

| Group | Count | Overlaps the restructure? |
|---|---|---|
| `docs/evidence/client-review-readiness-2026-09-01/*.png` + `.json` | 14 | **YES** — evidence batch |
| `docs/artifacts/client-review-navira.html` | 1 | **YES** — artifact batch |
| `README.md` | 1 | **YES** — it is the governing doc |
| `.gitignore` | 1 | **YES** — ignore rules must survive the move |
| `.impeccable/config.json` | 1 | No |

**Every modified file except `.impeccable/config.json` sits in a path the restructure would touch.**
This is the single largest Phase 2 hazard and it is addressed in `08_VALIDATION_AND_ROLLBACK_PLAN.md`
§2.

### 1.3 ⚠ Four live git worktrees share this checkout

```bash
git worktree list
# C:/Users/PaulRussell/repos/agent-factory                          827f871 [main]
# C:/Users/PaulRussell/repos/agent-factory/.worktrees/finalization  e7f92f3 [mission/marketing-model-finalization]
# C:/Users/PaulRussell/repos/agent-factory/.worktrees/mission       efb05cf [mission/marketing-model-v1]
# C:/Users/PaulRussell/repos/agent-factory/.worktrees/reliability   b338324 [reliability/recurrence-preflight]
# C:/Users/PaulRussell/repos/agent-factory/.worktrees/switchboard   1d6b3a4 [switchboard/p0]
```

`.worktrees/` is gitignored, so those trees are invisible to `git status` in `main`. They each hold
a full copy of `docs/` and `factory/` at their own commit. **A restructure on `main` does not touch
them, and every one of them will conflict at merge time** — a `git mv` of a directory against a
branch that edited files inside it produces rename/edit conflicts across the whole subtree.

Five branches are checked out or live locally that are not `main`:
`mission/marketing-model-finalization`, `mission/marketing-model-v1`,
`reliability/recurrence-preflight`, `switchboard/p0`, plus `switchboard/p0-autonomy`,
`switchboard/p1`, `public/p1-code`, `docs/agent-army-research-separation`,
`fix/fifth-verdict-apparatus-error`.

**Decision required from the user** — see `05_MIGRATION_PLAN.md` §0, Decision D-1.

### 1.4 ⚠ The remote is public, and a release gate over it is BLOCKED

```bash
git remote -v
# personal  https://github.com/russell94paul/agent-factory.git (fetch)
# personal  https://github.com/russell94paul/agent-factory.git (push)
```

`docs/release-gate/AF-RELEASE-GATE-01-2026-09-01.md` (untracked, deliberately) records:

> **Status: BLOCKED — requires human authority.**
> *"Client-identifying and client-commercial content is already published on the public remote. Not
> staged, not pending — served by GitHub right now, to anyone, without authentication."*

Consequences for this migration, all already required by the brief's safety rules but restated
because the gate makes them concrete:

- **No push, on any branch, for any reason.** The publication boundary is *all remote refs*, not
  just `main`.
- `.gitignore` currently keeps four things out of git specifically on release-gate grounds
  (the live PBI capture, the review-pack ZIP, the architecture-supplement ZIP, generated evidence
  packs). **Those rules must be carried through the migration unchanged**; a restructure that
  re-paths an ignore rule silently un-ignores its target.

### 1.5 Languages, frameworks, build and test

| Aspect | Measurement |
|---|---|
| Language | Python only. `requires-python = ">=3.11"` |
| Runtime deps | `pyyaml>=6.0` — one |
| Optional `render` | `playwright>=1.40` (+ `python -m playwright install chromium`) |
| Optional `dev` | `pytest>=8.0`, `playwright>=1.40` |
| Build backend | `setuptools>=68` |
| Package name | `agentic-factory` v0.1.0 |
| JS / TS / Node | **None.** No `package.json`, no `node_modules`, no bundler |
| Test config | `[tool.pytest.ini_options] testpaths = ["tests"]`, `addopts = "-q"` |
| Lint / format config | **None.** No ruff, black, flake8, mypy, pre-commit, or CI config found |

```bash
git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -8
#  478 md      172 py      70 png     62 yaml
#   35 json    17 html     16 txt     11 zip
```

**There is no monorepo tooling and no reason to introduce any.** The brief's provisional
`apps/` + `packages/` tree is a JS/TS workspace idiom; this is a single Python distribution with one
flat package. See `04_PROPOSED_TARGET_STRUCTURE.md` §1.

### 1.6 Existing commands

Six slash commands exist at `.claude/commands/`, all `af-*`, all thin wrappers over
`python -m factory.autonomy`:

```bash
ls .claude/commands/
# af-pause.md  af-phase.md  af-resume.md  af-run-critical.md  af-run-dag.md  af-status.md
```

Their established shape — YAML frontmatter with a `description:`, a fenced command, and an explicit
*"do not summarise a count you did not read from the output"* instruction — is the template the
proposed `/cell-*` commands follow. See `05_MIGRATION_PLAN.md` §Batch 8.

`scripts/bootstrap.sh` is the documented setup entry point. `scripts/hooks/` holds Claude Code
hooks (4 files).

### 1.7 Test and validation baseline — measured before any change

```bash
python -m pytest
# 2 failed, 1016 passed, 2 xfailed, 7 warnings in 252.85s (0:04:12)
```

**This is the pre-migration baseline and it is not green.** Both failures are the same cause:

```
tests/test_findings.py::test_every_finding_carries_all_four_mandatory_fields
  AssertionError: findings missing mandatory fields:
  {'F101': ['BELIEVED', 'ACTUALLY', 'MEASURED BY']}
tests/test_findings.py::test_every_finding_reaches_at_least_one_lane
  AssertionError: findings attached to no lane: ['F101']
```

`docs/findings.d/F101-*.md` is missing three mandatory headings. **This is a pre-existing content
defect in a document, unrelated to any restructure.** It is recorded here so that Phase 2 cannot
claim credit for it, cannot be blamed for it, and cannot hide a *new* failure behind it.

> Verdict on the baseline: **AMBER — 1016 PASS, 2 FAIL, 2 xfail, 0 UNMEASURABLE.**
> Phase 2's acceptance condition is *"the same 2 failures, the same 1016 passes"*, not *"green"*.

**Other validation available:** none. No linter, no formatter, no CI, no link checker, no schema
validator is configured in the repository. `08_VALIDATION_AND_ROLLBACK_PLAN.md` §4 proposes the
structural substitutes and labels their limits explicitly.

---

## 2. Inventory summary

Full mechanical census: `scratchpad/census.py` → `02_ARTIFACT_INVENTORY.yaml`.

```bash
# working tree, excluding .git .data .sessions .worktrees __pycache__ .pytest_cache
# 1079 files total | 892 tracked | 187 untracked
git ls-files | wc -l   # 892
```

| Root | Files | Untracked | Bytes | Character |
|---|---:|---:|---:|---|
| `docs/raw_research/` | 326 | 70 | 34.4 MB | Immutable inbound research. **Do not alter** |
| `docs/evidence/` | 160 | 49 | 68.8 MB | Per-gate evidence + render screenshots |
| `.agent-platform/bootstrap/` | 110 | 0 | 0.6 MB | ⚠ Proposal from a stranger. Not a spec |
| `factory/` | 68 | 0 | 1.2 MB | **The runtime.** Flat package, 68 modules |
| `docs/research/` | 59 | 4 | 3.8 MB | R1–R19 prompts + answers + backlog |
| `tests/` | 51 | 0 | 0.6 MB | 1018 tests |
| `scripts/` | 43 | 4 | 0.6 MB | Render checks, probes, pack builders |
| `docs/findings.d/` | 35 | 0 | 0.2 MB | **Read as data by `factory/findings.py`** |
| `docs/combined-execution-research-v2-…/` | 28 | 28 | 0.08 MB | ⚠ 100% byte-duplicate of a pack |
| `boot-prompts/` | 26 | 5 | 0.3 MB | Session handoffs |
| `docs/protocol/` | 22 | 0 | 0.08 MB | Communication protocol + schemas |
| `docs/design/` | 18 | 4 | 1.2 MB | Design pack, incl. 2 CELL OS ZIPs + a .docx |
| `docs/_index/` | 13 | 0 | 0.85 MB | **The existing corpus index** |
| `docs/` (root files) | 12 | 2 | 4.1 MB | Loose prompts + `findings.md` + a PNG |
| repo root | 11 | 6 | 4.4 MB | README, BRAIN-DUMP, pyproject, 4 ZIPs |
| `docs/marketing/` | 11 | 1 | 0.3 MB | **`cell-os-launch-v1/` — the CELL OS deck** |
| `missions/` | 13 | 0 | 0.16 MB | client-review-v1, delivery-001, presets |
| `docs/specs/` | 9 | 0 | 0.14 MB | Product/architecture specs |
| `docs/artifacts/` | 8 | 2 | 0.66 MB | Rendered HTML deliverables |
| `docs/reviews/` | 7 | 0 | 0.13 MB | Build-vs-adopt, divergence reviews |
| `.claude/commands/` | 6 | 0 | 4 KB | The six `af-*` commands |
| `docs/release-gate/` | 5 | 5 | 0.19 MB | ⛔ Publication boundary. Deliberately untracked |
| `docs/agent-army/` | 5 | 0 | 37 KB | ⭐ `CURRENT_STATE.md` outranks the index |
| `evaluator_service/` | 5 | 0 | 22 KB | The grader — separate identity, on purpose |
| `docs/diagrams/` | 4 | 4 | 4.4 MB | **3 CELL OS PNGs**, untracked |
| `docs/board/` | 4 | 0 | 0.35 MB | Board artifact + fixtures |
| `blueprints/` | 2 | 0 | 12 KB | Two team specs |
| `evals/` | 2 | 0 | 8 KB | Eval corpus + `MANIFEST.sha256` |

### 2.1 Archives — 32 ZIPs, inspected without extraction

```bash
python scratchpad/zip_survey.py   # lists namelist() per archive; nothing extracted
```

Three pairs are **byte-identical**, confirmed by `sha256sum`, not by name or size:

| SHA-256 (16) | Copies |
|---|---|
| `06d98f16a2c80bff` | `CELL_OS_NERVE_Design_Intelligence_MetaSkill_v1.zip` (repo root) = `docs/design/…` |
| `a7531f87de759f06` | `docs/design/CELL_OS_Design_Build_Operate_Pack_v0.1.zip` = `docs/raw_research/…` |
| `5708210c2784a8df` | `docs/raw_research/ZEUS_World_UI_Research_Pack.zip` = `…/agent_factory_chat_design_pack/legacy_reference/…` |

Two archives are *self-referential nests* and matter to the intake design:

- `CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip` (15.5 MB, 35 entries) contains
  `07_SOURCE_ARCHIVES/` holding `raw_research.zip`, `CELL_OS_Project_Library_Master_2026-09-02.zip`,
  `agentic_ai_concepts_pack.zip`, `operative_cell_framework_pack.zip` and
  `Agent Factory Vision.txt` — i.e. **copies of archives that also sit loose in `docs/raw_research/`.**
- `CELL_OS_Project_Library_Master_2026-09-02.zip` (9.6 MB, 361 entries) is itself a curated
  re-packaging of the earlier packs, carrying its own `00_START_HERE/FILE_MANIFEST_SHA256.csv`,
  `DUPLICATE_HASH_GROUPS.md` and `DISTRIBUTION_WARNING.md`.

⭐ **The most load-bearing document in the whole corpus is inside an unopened ZIP.**
`CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip →
01_CANONICAL_ONTOLOGY/CELL_OS_Canonical_Terminology_vNext.md` is the canonical CELL OS ontology, and
`KNOWN_TERMINOLOGY_COLLISIONS.md` beside it is the collision register the brief's task 4 asks to be
built. Both were read for this audit *from within the archive*; neither exists as a loose file.
Surfacing them is Batch 1 of the migration.

### 2.2 Duplicates — 54 content groups, 141 files, 50 cross-directory

```bash
python scratchpad/census.py census.tsv    # → census.tsv.dups.txt
# duplicate content groups: 54
# files in duplicate groups: 141
```

`docs/_index/duplicate_clusters.md` already documents thirteen clusters, DC-01 … DC-13, and every
one of them is confirmed by this hash pass. **Three clusters it does not cover** — all newer than
the index:

| New cluster | Shape | Evidence |
|---|---|---|
| **DC-14 (proposed)** | `docs/combined-execution-research-v2-2026-09-02/` is a **100% byte-identical extraction** of `docs/raw_research/agent-factory-combined-execution-research-pack-v2-2026-09-02/` | 28 of 28 files hash-match |
| **DC-15 (proposed)** | The two CELL OS ZIP pairs above | `sha256sum`, §2.1 |
| **DC-16 (proposed)** | `docs/artifacts/client-review-navira.html` = `docs/evidence/deadline-2026-09-02/fallback/client-review-navira.html`; same for `render-check-client-review.json` | hash-match ×2 |

⚠ **DC-16 is probably not a defect.** DC-08 in the existing register records the same shape and
concludes *"the identity IS the proof"* — a fallback copy that differs from the artifact would mean
the fallback was stale. This is exactly why the brief forbids discarding duplicates before
comparing them. **No duplicate is deleted by this plan.**

`Agent Factory Vision.txt` exists in **six** byte-identical copies (DC-01, confirmed). It is the sole
cited internal input of the two frontier `.docx` documents — so *"six sources agree"* would be one
source, counted six times.

---

## 3. Documentation lifecycle — what exists vs what the brief proposes

The brief's task 7 proposes:

```
Incoming → Raw Research → Synthesized Finding → Architecture Proposal
        → Architecture Decision → Canonical Specification → Implementation
        → Verification Evidence
```

**Six of those eight stages already have a physical home.** Two do not:

| Stage | Existing home | Status |
|---|---|---|
| Incoming | — | ⛔ **MISSING.** `docs/_incoming/` does not exist |
| Raw Research | `docs/raw_research/` | ✅ Exists, 326 files, immutable by convention |
| Synthesized Finding | `docs/research/answers/`, `docs/research/SYNTHESIS.md`, `docs/_index/*.md` | ✅ Exists |
| Architecture Proposal | `docs/specs/`, `.agent-platform/bootstrap/`, `docs/reviews/` | ⚠ Scattered across three roots |
| Architecture **Decision** | — | ⛔ **MISSING.** No ADR directory. Decisions live inline in README and boot-prompts |
| Canonical Specification | `README.md` §IV, `docs/protocol/`, `docs/specs/` | ⚠ Partly in README prose |
| Implementation | `factory/`, `evaluator_service/`, `scripts/` | ✅ Exists |
| Verification Evidence | `docs/evidence/` (160 files) | ✅ Exists, strongest lane in the repo |

**The two genuine gaps are Incoming and Decisions.** Everything else is a naming and consolidation
problem, not a missing capability. That is the shape of the whole restructure and it is why
`05_MIGRATION_PLAN.md` front-loads intake conventions and defers code movement to Batch 6.

### 3.1 The lifecycle rule the repository already enforces, and must keep

`docs/agent-army/CURRENT_STATE.md` and `.agent-platform/RECONCILIATION.md` are the two instruments
that map vocabulary onto code, citing `file:line`. `corpus_manifest.yaml`'s own preamble subordinates
itself to them:

> *"Where this manifest and either of those disagree, THEY are right. They were measured against
> code; this was measured against documents."*

**That precedence — code-measured beats document-measured — is the repository's existing answer to
the brief's rule "do not claim something is implemented because it appears in a design document."**
It must survive the restructure intact, and `04_PROPOSED_TARGET_STRUCTURE.md` §4 states where it
lands.

---

## 4. Code architecture — what it actually is

```bash
ls factory/*.py | wc -l     # 68
cat factory/*.py | wc -l    # 23939
```

⚠ **`README.md` §VII claims `factory/` is "66 modules, 22,817 lines". It is 68 modules and 23,939
lines.** A hand-maintained count, in the document whose §V.3 forbids hand-maintained counts. Filed
as a correction in `05_MIGRATION_PLAN.md` Batch 7.

**The actual architecture: one flat Python package.** `factory/` has no subpackages — 68 sibling
modules in a single namespace. `evaluator_service/` is a deliberately separate 5-module package
("a separate identity, on purpose"). `scripts/` is 43 loose entry points. There is one
distribution, `agentic-factory`.

Measured intra-package coupling (fan-in, distinct importing modules):

```bash
grep -rhoE "from factory\.[a-z_]+|from \.[a-z_]+ import" factory/ scripts/ tests/ \
  | sed -E 's/.*factory\.//; s/from \.//; s/ import//' | sort | uniq -c | sort -rn | head -10
#  21 contract     18 lanes      16 tasks      16 readiness    10 client_review_render
#   9 board         7 provider    7 deploy      6 connector_contract  6 case_study_render
```

`contract.py` is the root of the dependency graph, exactly as `README.md` §I describes
("the grader is built before the thing being graded"). The graph is shallow and centred — this is a
**cohesive flat package**, not an accidental one.

### 4.1 Would a monorepo help? No — and the measurement says why

| Test for splitting | Result |
|---|---|
| More than one deployable unit? | **No.** One distribution, one optional-extra set |
| More than one language or toolchain? | **No.** Python only |
| Independent release cadence per module? | **No.** No versioning below the distribution |
| A module with zero coupling to `contract.py`? | **Few.** `contract` has the highest fan-in |
| Team boundaries requiring ownership split? | **No.** Single author |
| Existing workspace tooling to build on? | **None** |

**Recommendation: keep one Python distribution.** If `factory/` is ever split, the natural seam is
*by fan-in tier*, not by the brief's concept names — a `factory/core/` (contract, evidence, tasks,
claims), a `factory/orchestration/` (lanes, deploy, dispatch, control, autonomy, coordination) and a
`factory/surfaces/` (switchboard*, client_review*, case_study*, *_render). That is a ~68-file
`git mv` plus every import in `factory/`, `scripts/` and `tests/`, for zero functional gain today.

**It is explicitly out of scope for this migration.** `04_PROPOSED_TARGET_STRUCTURE.md` §3 records
the seam as a documented logical architecture so the option stays open without being taken.

### 4.2 ⛔ The runtime reads `docs/` as data — moving those paths breaks the build

Seven hard-coded `docs/` paths in `factory/`, each a live dependency, not a comment:

| Module:line | Path | Effect if moved |
|---|---|---|
| `factory/findings.py:24` | `docs/findings.md` | `findings.by_lane()` returns nothing |
| `factory/findings.py:29` | `docs/findings.d/` | **Breaks `tests/test_findings.py` (already failing)** |
| `factory/schedule.py:46` | `docs/artifacts/agent-factory.html` (`ARTIFACT_REL`) | Schedule gate blind |
| `factory/readiness.py:647` | `docs/artifacts/agent-factory.html` | Readiness gate blind |
| `factory/readiness.py:1711` | `docs/research/answers/` | Answer-currency gate blind |
| `factory/readiness.py:1736` | `docs/evidence/render-pass-*.md` | Render gate blind |
| `factory/research_run.py:366`, `factory/synthesis.py:225` | `docs/research/answers/` | Synthesis reports "answer file not found" |

⭐ **Every one of these fails *silently* — as a gate that reports "nothing found" rather than as an
import error.** That is precisely the failure class this repository exists to prevent, and it would
be introduced *by* the tidy-up. Consequence, carried into the plan:

> **`docs/findings.d/`, `docs/findings.md`, `docs/research/answers/`, `docs/artifacts/` and
> `docs/evidence/` DO NOT MOVE.** They are code interface, not documentation layout.

---

## 5. Incoming downloads (brief task 3)

**`docs/_incoming/` does not exist.**

```bash
ls -d docs/_incoming    # ls: cannot access 'docs/_incoming': No such file or directory
```

Inbound material is landing directly in `docs/raw_research/` (and, for three CELL OS files, in
`docs/design/` and the repo root). Of the three files the brief names as examples:

| Named in brief | Found? | Where | Size |
|---|---|---|---|
| `CELL_OS_Recursive_Operative_Genesis_Architecture_Review_v1.md` | **NOT PRESENT** | — | — |
| `CELL_Foundry_Deep_Research_and_MESA_Synthesis_Protocol_v1.md` | **NOT PRESENT** | — | — |
| `cell-foundry-cross-domain-pipeline.html` | **PRESENT**, untracked | `docs/raw_research/` | 19,497 B |

```bash
find . -path ./.git -prune -o -iname "*Recursive*" -print -o -iname "*MESA*" -print -o -iname "*Foundry*" -print
# ./docs/raw_research/agent2_sihre_consolidation_pack/04_recursive_sihre_and_morphological_cognition.md
# ./docs/raw_research/agent2_sihre_consolidation_pack/research_prompts/DR03_RECURSIVE_SIHRE_MORPHOLOGICAL_COGNITION.md
# ./docs/raw_research/cell-foundry-cross-domain-pipeline.html
```

⚠ The two absent files are named in the brief with the phrase *"Do not assume these examples are
present. Report exactly what is found."* They are reported absent. **Their absence is `NOT-PRESENT`,
not `ZERO`** — this instrument (a case-insensitive `find` over the whole tree, minus `.git`) can see
files by name but cannot see a file that was downloaded and never saved here, nor content inside the
unopened ZIPs. `CELL_OS_Frontier_Audit_Research_Pack.zip` and
`CELL_OS_Project_Library_Master_2026-09-02.zip` were namelist-scanned and neither contains them.

**The 24 CELL OS artifacts that ARE present** are inventoried individually in
`02_ARTIFACT_INVENTORY.yaml` §cell_os with classification and destination. Twenty of the twenty-four
are untracked.

---

## 6. Existing indexes — validated (brief task 5)

| Brief expects | Present | Bytes | Verdict |
|---|---|---|---|
| `docs/_index/corpus_manifest.yaml` | ✅ | 275,762 | Valid YAML, 168 records, 719 files claimed → **stale by 169** |
| `docs/_index/document_catalog.md` | ✅ | 48,170 | Companion prose view |
| `docs/_index/concept_index.yaml` | ✅ | 196,274 | Valid YAML |
| `docs/_index/duplicate_clusters.md` | ✅ | 18,852 | DC-01…DC-13; **3 new clusters uncovered** |
| `docs/_index/contradictions.md` | ✅ | 37,818 | Present |
| `docs/_index/supersession_candidates.md` | ✅ | 20,288 | Present, advisory by design |
| `docs/_index/current_vs_proposed.md` | ✅ | 39,906 | **The capability matrix.** 10 parts + summary |
| `docs/_index/research_registry.yaml` | ❌ | — | **Does not exist** → propose |
| `docs/_index/research_status.md` | ❌ | — | **Does not exist** → propose |

Six more exist that the brief does not name: `repo_snapshot.md`, `high_leverage_concepts.md`,
`research_gap_candidates.md`, `agent_army_wave0_supplement.md`,
`agent_platform_delta_synthesis.md`, `SUPPLEMENT_README.md`.

**Machine-generated vs hand-maintained — the recommendation.** The manifest's own header admits
*"generator: manual corpus-preparation pass (no script produced these records)"*, splitting fields
into mechanical (path/bytes/sha256/first_committed, measured) and interpretive (topic, concepts,
status, authored by reading). That split is right and should be **enforced by tooling**:

| File | Should be | Why |
|---|---|---|
| `corpus_manifest.yaml` mechanical fields | **GENERATED** by `scripts/build_corpus_index.py` | 169-file drift in one day proves hand-maintenance fails |
| `corpus_manifest.yaml` interpretive fields | **HAND-MAINTAINED**, merged by the generator | Requires reading |
| `duplicate_clusters.md` | **GENERATED** hash table + hand-written verdicts | The hashing is mechanical; "is this a defect?" is not |
| `document_catalog.md`, `research_status.md` | **GENERATED** views | Never edit a view |
| `contradictions.md`, `supersession_candidates.md`, `current_vs_proposed.md` | **HAND-MAINTAINED** | Pure judgement |
| `research_registry.yaml` | **HYBRID** — file pairing generated, status/overlap authored | See `07_RESEARCH_STATUS_AUDIT.md` |

**No competing index is proposed.** The two new files are additive; the seven existing ones get a
delta pass. Details in `05_MIGRATION_PLAN.md` Batch 1.

---

## 7. Scope boundary — the sibling repository

`corpus_manifest.yaml` `coverage.not_indexed` names it, and it exists:

```bash
ls -d ~/repos/agent-army-research                        # exists
find ~/repos/agent-army-research -name "*.md" | wc -l    # 155
```

> *"A SEPARATE REPOSITORY, and the authoritative home of Agent Army research since 2026-08-30. …
> An architecture reviewer who has not read it is missing the research half of the programme."*

**It is out of scope for this restructure** (the brief scopes "this repository") but it is *not* out
of scope for the terminology decision: renaming Agent Army → CELL OS vocabulary in
`agent-factory` while the authoritative research home keeps the old vocabulary would split the
programme's language across two repos. Flagged as Decision **D-4** in `05_MIGRATION_PLAN.md` §0.

---

## 8. Secrets and private data

```bash
grep -rInE "(AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|xox[baprs]-[0-9A-Za-z-]{10,}|gh[pousr]_[0-9A-Za-z]{30,}|sk-[A-Za-z0-9]{32,})" \
  --exclude-dir=.git --exclude-dir=.data --exclude-dir=.worktrees --exclude-dir=__pycache__ .
# tests/test_switchboard_p1.py:943  ("-----BEGIN RSA PRIVATE KEY-----", "PRIVATE KEY-----")
# tests/test_switchboard_p1.py:944  ("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ012345", "ABCDEFGHIJ")
```

**Verdict: `ZERO` credential values found — and the instrument is proved live**, because it returned
the two deliberate fixtures in the redaction test. A sweep that had found nothing at all would have
been indistinguishable from a broken regex.

⚠ **This is a credential-shaped-string scan, not a privacy audit.** It says nothing about
client-identifying content, which AF-RELEASE-GATE-01 measured separately and found **already
public**. This migration adds no new files with such content; it also removes none.

---

## 9. Working-tree safety verdict

> ## **AMBER — safe to migrate under four preconditions, not safe to migrate as-is.**

| # | Condition | Why |
|---|---|---|
| 1 | **Commit or stash the 17 overlapping modified files first.** | 14 evidence PNGs, `client-review-navira.html`, `README.md` and `.gitignore` all sit in paths a batch would touch. `git mv` over a dirty path is where "do not overwrite unrelated user changes" gets violated. |
| 2 | **Decide the worktree question (D-1).** | Four live worktrees on four branches will all conflict at merge. |
| 3 | **Accept the AMBER test baseline.** | 2 failures pre-exist. Phase 2 acceptance is *"same 2, same 1016"*, not *"green"*. |
| 4 | **Confirm no concurrent session is writing.** | Multiple sessions share this checkout; `git status` moved between commands during this very audit. Re-measure `HEAD` and `status` immediately before each batch. |

**A fifth condition is advisory, not blocking:** the untracked material (187 files, incl. all 20
CELL OS artifacts and the release-gate directory) is *deliberately* untracked in at least one case.
`git mv` cannot move an untracked file, so those moves are `mv` + no history — and re-pathing an
untracked file that a `.gitignore` rule names by path can silently un-ignore it. Handled explicitly
in `05_MIGRATION_PLAN.md` §Batch 2 and `08_VALIDATION_AND_ROLLBACK_PLAN.md` §3.4.

---

## 10. Method and limits of this audit

**What was measured directly:** git state, worktrees, branches, remotes; file census with SHA-256
over 1,079 files; ZIP namelists over 32 archives (nothing extracted); a 31-term regex census over
1,001 text files; the full pytest suite; manifest coverage computed against the filesystem;
research prompt/answer pairing; `grep` for runtime `docs/` path dependencies; a credential-shape scan.

**What was read but not exhaustively:** `README.md` (headings + 4 sections in full);
`corpus_manifest.yaml` (schema, coverage block, 2 bundle records — not all 168);
`CELL_OS_Canonical_Terminology_vNext.md` (in full, from the archive); `backlog.yaml` (parsed, titles
only).

**What was NOT read and is stated as a gap, not papered over:**

| Not read | Bytes / count | Consequence |
|---|---|---|
| `docs/raw_research/CELL_OS_Master_…_User_Guide_v0.2.docx` | 66,022 | Content unindexed. Extends GAP-01 |
| `docs/design/CELL_OS_Product_Technical_Design_v0.1.docx` | 311,438 | **The v0.1 technical design.** Only its cross-reference audit was read |
| `docs/raw_research/CELL_OS_Delivery_Backlog_v0.2.xlsx` | 43,536 | Delivery plan unindexed |
| `docs/raw_research/CELL OS Design Master Brief.pdf` | 248,668 | Unindexed |
| Interiors of 32 ZIPs | ~34 MB | Namelists only, except the 2 ontology files |
| The 155 md files in `~/repos/agent-army-research` | 3.6 MB | Out of scope, but see §7 |

⛔ **The CELL OS `.docx`/`.xlsx`/`.pdf` set is the single largest blind spot, and it is the same
blind spot GAP-01 recorded for the two earlier `.docx` files.** The repository already has the fix —
`scripts/docx_to_md.py`, which parses `word/document.xml` directly and was verified at 100.1%
character coverage. It is proposed as Batch 2's first act. **`.xlsx` and `.pdf` have no converter
here**; those two remain `NOT-VISIBLE` after Phase 2 unless a converter is added.
