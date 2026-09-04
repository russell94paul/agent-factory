# 07 — Research status audit

**Phase 1, read-only.** Measured 2026-09-03 against `827f871`. ⛔ **No research was dispatched, and
no prompt's status was inferred from the mere existence of the prompt.**

Companion: `docs/research/DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` classifies the SIHRE queue against
newer CELL OS work and produces the recommended forward queue. This document is the **registry**.

---

## 1. The population — 53 items across three disconnected queues

```bash
ls docs/research/R*.md | wc -l                              # 19 prompt files (R1..R19, no R9, +R06B)
ls docs/research/answers/ | wc -l                           # 25 (incl. README, followups, run2s)
python -c "import yaml;print(len(yaml.safe_load(open('docs/research/backlog.yaml'))['missions']))"   # 26
ls docs/raw_research/agent2_sihre_consolidation_pack/research_prompts/DR0*.md | wc -l                # 8
```

| Queue | Items | Dispatched? |
|---|---:|---|
| **R1–R19** — the executed lane programme (⚠ no R9) | 19 | 18 `COMPLETED`, 1 `NOT_RUN` |
| **RB-01–RB-26** — `docs/research/backlog.yaml` | 26 | ⛔ **0** — `status: CANDIDATES_NOT_DISPATCHED` |
| **DR01–DR08** — the SIHRE queue | 8 | ⛔ **0** — no answer file exists for any |
| *(bootstrap seed `R-EVAL-01`… )* | *7* | *`status: seed_only`; ⚠ from the stranger's pack* |

⛔ **The three queues do not reference each other.**

```bash
grep -rn "DR0[1-8]" docs/research/backlog.yaml docs/research/SYNTHESIS.md    # 0 hits
```

The 26-item backlog was generated 2026-09-02 by reading the corpus, and **never cites the eight
SIHRE prompts**. Two research planning systems have run past each other. This is the finding that
most justifies building `research_registry.yaml`.

---

## 2. R1–R19 — prompt/answer pairing, measured

Pairing was computed by filename, not assumed:

| Lane | Prompt | Answer(s) | Status |
|---|---|---|---|
| R1 | `R1-eval-harness.md` | `R1-answer-…`, `R1-followup.md` | `COMPLETED` |
| R2 | `R2-topology.md` | `R2-answer-…`, `R2-followup.md` | `COMPLETED` |
| R3 | `R3-control-plane-and-optimizer.md` + `R3-optimizer-sandbox-SUPERSEDED.md` | `R3-answer-…`, `R3-followup.md` | `COMPLETED`; ⚠ one prompt self-labels `SUPERSEDED` |
| R4 | `R4-agnostic-optimizer.md` | `R4-answer-…`, **`-run2`** | `COMPLETED` ×2 |
| R5 | `R5-build-velocity.md` | `R5-answer-…` | `COMPLETED` |
| R6 | `R6-automation-and-alerting.md` | `R6-answer-…` | `COMPLETED` |
| **R06B** | `R06B-collective-cognition-and-knowledge-architecture.md` | ⛔ **NONE** | ⛔ **`NOT_RUN`** |
| R7 | `R7-session-manager.md` | `R7-answer-…` | `COMPLETED` |
| R8 | `R8-data-engineering-agent-factory.md` (+ evidence pack) | `R8-answer-…` | `COMPLETED` |
| **R9** | ⛔ **NO PROMPT** | ⛔ **NO ANSWER** | ⛔ **DOES NOT EXIST** |
| R10–R12 | each present | each present | `COMPLETED` |
| R13 | `R13-…` (+ evidence pack) | `R13-answer-…`, **`-run2`** | `COMPLETED` ×2 |
| R14 | `R14-…` (+ evidence pack) | `R14-answer-…` | `COMPLETED` |
| R15 | `R15-source-corpus-crawl.md` | `R15-answer-…` | `COMPLETED` |
| R16 | `R16-…` (+ evidence pack) | `R16-answer-…`, `R16-outside-evidence-lane.md` | `COMPLETED` |
| R17 | `R17-data-engineering-external-survey.md` | `R17-answer-…` | `COMPLETED` ⭐ **the only pass that verified its own citations (§8)** |
| R18 | `R18-our-factory-internal-audit.md` | `R18-answer-…` | `COMPLETED` |
| R19 | `R19-work-taxonomy-and-team-selection.md` | `R19-answer-…` | `COMPLETED` |

### 2.1 Three findings

**⛔ 2.1.1 — R06B is the programme's only orphan.** A prompt with no answer, and its subject
(collective cognition and knowledge architecture) is exactly the HyperMESH / DR04 territory. It
should not be run alone — **merge it into the HyperMESH lane** (`DESIGN_DELTA…` §6, Tier 1.2).

**⚠ 2.1.2 — R9 does not exist and never did.** Neither prompt nor answer. A gap in numbering, not a
missing artifact. **Recorded so no future session "finds" a missing R9 and goes looking.**

**⭐ 2.1.3 — R4 and R13 each ran twice.** `docs/_index/duplicate_clusters.md` DC-05 already covers
this: *"Research passes run twice · COMPLEMENTARY, and deliberately so."* **Not a defect** — the
registry records both runs and does not collapse them.

### 2.2 ⚠ `COMPLETED` means an answer file exists. It does not mean the answer was absorbed.

`docs/absorption-backlog.md` exists specifically because completed answers were not absorbed, and
`docs/findings.d/F75` records: *"both reconciliation checks passed over three unabsorbed answers."*

**The registry therefore carries two separate fields — `run_status` and `absorption_status` — and
must never collapse them.** A completed research pass whose findings nothing acted on is the
965-run loop again: it measured, and nothing changed.

---

## 3. RB-01–RB-26 — the candidate backlog

`status: CANDIDATES_NOT_DISPATCHED`. Distribution by the file's own `classification_vocabulary`:

| Type | Count | Note |
|---|---:|---|
| `NOT_RESEARCH` | **6** | ⭐ RB-01…RB-06 — **work items in a research queue** |
| `PRIOR_ART` | 5 | |
| `FOUNDATIONAL` | 4 | |
| `COMPARISON` | 4 | |
| `VALIDATION` | 3 | |
| `EXPERIMENT_DESIGN` | 2 | |
| `ADVERSARIAL` | 1 | |
| `IMPLEMENTATION` | 1 | |

**⭐ The six `NOT_RESEARCH` rows are the highest-value correction in the whole research estate**, and
the backlog says so itself:

> *"SIX OF THE EIGHT CRITICAL GAPS ARE NOT RESEARCH. GAP-01 is a file conversion. GAP-08 is scoring
> a second connector. GAP-09 is fixing one open finding and running the loop. GAP-26 and GAP-27 are
> decisions for a human. GAP-30 is asking a client two questions. … Buying a research answer to a
> question that measurement would settle more cheaply is this corpus's characteristic failure, and
> it has been paid for at least twice."*

**Registry action: these six carry `type: NOT_RESEARCH` and `recommended_action: MOVE_TO_TRACKER`.**
They become tickets in `docs/status/PROJECT_PROGRESS.yaml`, not prompts.

⭐ **GAP-01 — the `.docx` conversion — is measurably still open, and is now larger than when it was
filed.** It named two `.docx` files (both since converted). **Four more unreadable CELL OS binaries
have arrived since**: `CELL_OS_Product_Technical_Design_v0.1.docx` (311 KB),
`…User_Guide_v0.2.docx` (66 KB), `CELL_OS_Delivery_Backlog_v0.2.xlsx` (43 KB),
`CELL OS Design Master Brief.pdf` (249 KB). The `.docx` converter exists and works; **`.xlsx` and
`.pdf` have no converter here** (Decision D-5).

---

## 4. DR01–DR08 — the SIHRE queue

All eight: **`NOT_RUN`**. No answer file exists for any, in `docs/research/answers/` or anywhere.

```bash
ls docs/research/answers/ | grep -i "DR0"     # 0 hits
```

⛔ **The brief's rule applied literally: "Do not infer that a prompt was run merely because the
prompt exists."** Eight prompts exist. Zero answers exist. Status is `NOT_RUN`, not `STATUS_UNKNOWN`
— because the instrument (the answers directory, which demonstrably contains 24 answer files for the
R-lanes) **is proved able to see an answer if one were there.** That is a `ZERO`, not a
`NOT-RECORDED`.

Full classification against newer CELL OS work is in
`docs/research/DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` §2. Summary: **1 `STILL_REQUIRED` (DR02), 2
`ABSORBED`, 2 `PARTIALLY_SUPERSEDED`, 1 `FULLY_SUPERSEDED`, 1 `OPTIONAL_CASE_STUDY`, 1
`DEFERRED_FRONTIER`.**

---

## 5. Inbound pack prompts — 38 files, status `STATUS_UNKNOWN`

```bash
find docs/raw_research -type f \( -ipath "*research_prompt*" -o -iname "*DEEP_RESEARCH*" -o -iname "*_PROMPT*.md" \) | wc -l
# 38
```

Spread across nine inbound packs. **They cannot be assigned `NOT_RUN`**, because they arrived
pre-authored from elsewhere and this repository holds no record of whether they were run before
import. ⛔ **`STATUS_UNKNOWN` is the correct verdict and it is different from `NOT_RUN`.** Collapsing
them would assert something about work done outside this repository that this repository cannot see.

⚠ **Several are duplicates of each other** — DC-09 records *"Three prompts asking for a corpus
preparation · INDEPENDENT TREATMENTS"*, and the ZEUS pack's `08_RESEARCH_PROMPTS.md` exists in
**three byte-identical copies** (DC-06, re-confirmed by hash today). **A registry that counted 38
distinct prompts would be overcounting.**

---

## 6. `docs/_index/research_registry.yaml` — proposed schema

⛔ **Does not exist today.** Neither does `research_status.md`. These are the only two of the brief's
seven named index artifacts that are missing (`01` §6).

```yaml
schema_version: 1
status: REGISTRY_ONLY_NOTHING_DISPATCHED       # ⛔ this file never dispatches anything
generated: {at: 2026-09-04, repo_head: <sha>, generator: scripts/build_research_registry.py}

# ⚠ Field provenance, per README.md §V.2:
#   GENERATED — measured from the filesystem. Never hand-edited.
#   AUTHORED  — requires reading. Merged by the generator, never overwritten.

vocabulary:
  run_status:        [NOT_RUN, IN_PROGRESS, COMPLETED, PARTIAL, SUPERSEDED,
                      MERGE_WITH_OTHER_PROMPT, STATUS_UNKNOWN]
  absorption_status: [NOT_ABSORBED, PARTIALLY_ABSORBED, ABSORBED, REJECTED]
  # ⛔ run_status and absorption_status MUST NOT be collapsed. §2.2.

queues:
  - {id: R,  name: "Lane programme",   home: docs/research/,            items: 19}
  - {id: RB, name: "Candidate backlog", home: docs/research/backlog.yaml, items: 26}
  - {id: DR, name: "SIHRE queue",      home: docs/raw_research/agent2_sihre_consolidation_pack/research_prompts/, items: 8}
  - {id: IN, name: "Inbound pack prompts", home: docs/raw_research/**,  items: 38, note: "⚠ contains duplicates — DC-06, DC-09"}

entries:
  - id: R06B
    queue: R
    prompt_path: docs/research/R06B-collective-cognition-and-knowledge-architecture.md   # GENERATED
    research_question: "..."                                                             # AUTHORED
    run_status: NOT_RUN                        # GENERATED — no answer file matches R06B
    run_status_basis: >                        # AUTHORED
      ZERO, not NOT-RECORDED. docs/research/answers/ holds 24 answer files for other lanes,
      so the instrument is proved able to see an answer if one existed.
    answer_paths: []                           # GENERATED
    run_date: null                             # GENERATED from git log --diff-filter=A
    absorption_status: NOT_ABSORBED            # AUTHORED
    scope: "collective cognition and knowledge architecture"          # AUTHORED
    overlaps: [DR04, RB-09, "HyperMESH lane"]                          # AUTHORED
    canonical_contribution: null                                       # AUTHORED
    unresolved_questions: ["..."]                                      # AUTHORED
    recommended_action: MERGE_WITH_OTHER_PROMPT                        # AUTHORED
    recommended_action_note: "Merge into the HyperMESH lane; do not run alone."

  - id: DR01
    queue: DR
    prompt_path: docs/raw_research/agent2_sihre_consolidation_pack/research_prompts/DR01_PRIOR_ART_AND_NOVELTY.md
    run_status: NOT_RUN
    absorption_status: NOT_ABSORBED
    supersession: FULLY_SUPERSEDED
    superseded_by: ".agent-platform/RECONCILIATION.md §1.1 (Wave 0); arXiv:2602.13275; arXiv:2607.25446"
    recommended_action: REJECTED
    recommended_action_note: "Already refuted against primary sources. Re-running buys a paid-for refutation."

  - id: RB-01
    queue: RB
    type: NOT_RESEARCH                        # from backlog.yaml
    run_status: NOT_RUN
    recommended_action: MOVE_TO_TRACKER
    recommended_action_note: "GAP-01, a file conversion. ⭐ Now LARGER: 4 more unreadable CELL OS binaries."
    tracker_ticket: null                      # filled when docs/status/PROJECT_PROGRESS.yaml exists

summary:                                      # GENERATED
  by_run_status: {COMPLETED: 18, NOT_RUN: 35, STATUS_UNKNOWN: 38, ...}
  by_absorption_status: {...}
  regenerate_with: "python scripts/build_research_registry.py"
```

**`docs/_index/research_status.md` is a GENERATED view of this file** — never hand-edited, and
asserted current by `tests/test_views_are_current`, mirroring the existing
`tests/test_tracker_is_current.py`.

⭐ **Hybrid generation is the point.** Pairing, dates and run-status are mechanical and **must** be
generated — the corpus index drifted by 169 files in one day when its mechanical fields were
hand-maintained. Overlap, canonical contribution and recommended action require reading and must be
authored, then merged rather than overwritten.

---

## 7. Registry → tracker join

`docs/status/PROJECT_PROGRESS.yaml` carries `research_lanes` **by reference only** (`04` §8.3):

```yaml
research_lanes:
  - {id: R06B, registry_ref: "research_registry.yaml#R06B", status: NOT_RUN,
     blocks: [E-04], ingested: false, synthesized: false, canonical_integration: NOT_STARTED}
```

⛔ **The tracker must never duplicate the registry's fields.** Two files holding the same status is
how they disagree. The registry owns research status; the tracker owns *what that status blocks*.

The Research Tracker view (`04` §8.5) renders from the join: completed · `NOT_RUN` · active lane ·
dependency readiness · ingestion · synthesis · canonical integration.

---

## 8. Recommended actions

| # | Action | Why |
|---|---|---|
| 1 | Build `research_registry.yaml` + `research_status.md` (Batch 1) | The only two missing index artifacts; three queues currently cannot see each other |
| 2 | ⭐ Move the 6 `NOT_RESEARCH` rows to the tracker as tickets | They cannot be worked from a research queue and can be dispatched by accident |
| 3 | Merge R06B into the HyperMESH lane | The programme's only orphan prompt; overlaps DR04 and RB-09 |
| 4 | Mark DR01 `REJECTED`, DR07 `OPTIONAL_CASE_STUDY` | Already refuted / low-yield by the corpus's own rule #6 |
| 5 | Record all 38 inbound prompts as `STATUS_UNKNOWN`, deduplicated | ⛔ `STATUS_UNKNOWN` ≠ `NOT_RUN`, and 3 copies of one prompt is one prompt |
| 6 | ⛔ **Dispatch nothing** | See §9 |

---

## 9. ⭐ The one fact that governs the whole research programme

```bash
python -c "import json;r=[json.loads(l) for l in open('.data/runs.jsonl',encoding='utf-8')];print(len(r),[x.get('outcome') for x in r])"
# 10 ['FINISHED','FINISHED','FINISHED','FAIL','UNMEASURABLE','UNMEASURABLE','UNMEASURABLE','UNMEASURABLE','UNMEASURABLE','UNMEASURABLE']
python -c "import json;e=[json.loads(l) for l in open('.data/events.jsonl',encoding='utf-8')];a=[x for x in e if x.get('kind')=='agent_returned'];print(len(e),len(a),sorted({str(x.get('dry_run')) for x in a}))"
# 61 7 ['True']
```

**10 runs, 0 `PASS`, all 7 `agent_returned` events `dry_run=True`. No agent has ever completed a
real, non-dry-run run in this system.** (`README.md` Part 0, re-verified today.)

Nineteen research lanes have completed. Twenty-six candidates and eight SIHRE prompts wait. And the
subject of all of it — a team of agents doing real work — **has never been measured once.**

⭐ **DR02 (cognitive portfolio / correlated failure) is the only SIHRE prompt that survives
supersession intact, and it is unrunnable**: a covariance estimator over correlated agent failure
needs mission history, and there is none. DR05 is gated on the same absence.

> **The highest-value next action in the entire research programme is not research.** It is
> completing one real, non-dry-run agent run — RB-03 in the backlog, filed there under
> `type: NOT_RESEARCH`, exactly where the corpus's own read-first rule says such things belong.

`docs/research/DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` §8 gives the exact ordered next actions.
