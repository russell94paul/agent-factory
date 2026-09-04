# Design delta since the SIHRE research queue

**Phase 1 deliverable, read-only.** Measured 2026-09-03 against `agent-factory` @ `827f871` (`main`).
⛔ **No research was dispatched.** Nothing was moved, renamed or deleted to produce this document.

> ## ⭐ REVISED 2026-09-03 — the two missing documents have arrived
>
> Both documents §0 recorded as `NOT-PRESENT` were delivered in
> `docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack.zip`, together with a **third**
> that post-dates this document: **CELL OS Deep Research Manifest v3**.
>
> **Three changes were made to this file, and nothing else:**
> 1. **§7 is no longer blocked** — the comparison it prepared for has been performed, in full.
> 2. ⛔ **Every `RB-` citation in §2, §3 and §6 was wrong and is corrected** — `backlog.yaml`
>    numbers its rows `RB-00A…RB-00F, RB-01…RB-20`, not `RB-01…RB-26`, and this document referenced
>    them **by position**, shifting each citation by six.
> 3. **§6 Tier 1.6 is superseded** by v3 §8.
>
> Everything else stands as measured. **The full reconciliation is
> [`docs/restructure/09_RESEARCH_MANIFEST_V3_RECONCILIATION.md`](../restructure/09_RESEARCH_MANIFEST_V3_RECONCILIATION.md)**;
> the activation decision is `13_V3_ACTIVATION_DECISION.md`. ⛔ **Still nothing dispatched.**

---

## 0. ⛔ Two named source documents do not exist. Read this before the tables.

> ✅ **RESOLVED 2026-09-03.** Both are now present at
> `docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack/`
> (v2 `bc111d5d…`, legacy queue `6d142560…`). ⭐ **The hypothesis this section stated — that both
> documents existed outside this repository — is confirmed. The instrument was not blind; the
> documents were not here.** The section is kept intact below because the distinction it draws
> (`NOT-PRESENT` versus `ZERO`) is the one this corpus most often gets wrong in the other direction.

The requirement names two inputs. Both were searched for exhaustively — by filename across the whole
tree, by content, and by `namelist()` across all 32 ZIP archives without extracting any of them.

| Named input | Found? | Search performed |
|---|---|---|
| `CELL_OS_Optimized_Deep_Research_Prompt_Manifest_v2.md` | **NOT PRESENT** | 0 hits on disk; 0 hits in 32 archives |
| The old **20-report** "Recommended Deep Research Report Queue" | **NOT PRESENT as a 20-item queue** | 0 hits for the phrase anywhere |

```bash
find . -path ./.git -prune -o -iname "*Optimized*" -print -o -iname "*Prompt_Manifest*" -print   # 0
grep -rIl "Recommended Deep Research Report Queue" --exclude-dir=.git .                          # 0
python -c "...zipfile.namelist() over 32 archives, matching optimized|manifest_v2|queue..."       # 0 relevant
```

**What does exist under the SIHRE name is a queue of EIGHT, not twenty:**

```bash
ls docs/raw_research/agent2_sihre_consolidation_pack/research_prompts/
# DR01_PRIOR_ART_AND_NOVELTY.md          DR05_HOMEOSTASIS_IMMUNITY_SELF_MODEL.md
# DR02_COGNITIVE_PORTFOLIO_THEORY.md     DR06_EVALUATION_AND_BENCHMARKS.md
# DR03_RECURSIVE_SIHRE_MORPHOLOGICAL_COGNITION.md  DR07_CROSS_DOMAIN_TRANSFER.md
# DR04_CONTEXTUAL_TRUST_KG_MESH.md       DR08_ENTITY_DEFINITION_AND_NAMING.md
# MASTER_DEEP_RESEARCH_PROMPT.md
```

**This absence is `NOT-PRESENT`, not `ZERO`** — the distinction matters here. The instrument (a
case-insensitive filename `find` plus a content `grep` plus archive namelists) is proved able to see
files of exactly this kind: it returned all eight DR prompts, the bootstrap pack's
`RESEARCH_QUEUE.yaml`, and `docs/research/backlog.yaml`. What it **cannot** see is a document that
was authored in a chat session and never saved into this repository, or one inside a `.docx`,
`.xlsx` or `.pdf` (four such CELL OS files exist and are unreadable here — `01_REPOSITORY_AUDIT.md`
§10).

> ⚠ **Most likely explanation, stated as a hypothesis and not as a finding:** both documents exist
> outside this repository. The v2 manifest in particular reads like an artifact of a planning
> conversation. **Paste them in, or drop them into `docs/_incoming/`, and §7 of this document can be
> completed properly.**

### 0.1 What this document therefore does

It does the analysis that the available evidence supports, and marks the rest as blocked:

| Requirement | Status |
|---|---|
| Classify every old report into the 7 categories | ✅ **DONE** — for the 8 DR prompts that exist (§2), and extended to the full 53-item research population (§3) |
| Identify design additions post-dating the queue | ✅ **DONE** — all 25 named concepts censused (§4) |
| Compare findings against the v2 manifest | ✅ **DONE 2026-09-03** — the manifest arrived; comparison completed at §7 |
| Identify anything missing or mis-sequenced | ✅ **DONE** — extended to v2, v3 and the legacy 20 in `09` §10 |
| Produce the recommended final prompt queue | ✅ **DONE** (§6) — ⚠ **superseded as the operative queue by `12_NEXT_RESEARCH_RUN.md`** |
| Exact next research action | ✅ **DONE** (§8) |
| Do not dispatch research | ✅ **HONOURED** — nothing dispatched |

---

## 1. The actual research population

The requirement assumes one queue. The repository holds **three**, and they do not reference each
other. That disconnection is itself a finding.

| Queue | Items | Where | Status |
|---|---|---|---|
| **DR01–DR08** — the SIHRE queue | 8 | `docs/raw_research/agent2_sihre_consolidation_pack/research_prompts/` | ⛔ **All 8 `NOT_RUN`.** No answer file exists for any |
| **R1–R19** — the executed lanes (no R9) | 19 | `docs/research/` + `answers/` | 18 `COMPLETED`, 1 `NOT_RUN` (R06B) |
| **RB-00A–RB-00F, RB-01–RB-20** — the candidate backlog | 26 | `docs/research/backlog.yaml` | All `CANDIDATES_NOT_DISPATCHED`. ⚠ *ID scheme corrected 2026-09-03 — it is **not** a contiguous RB-01…RB-26* |
| Bootstrap seed (`R-EVAL-01` …) | 7 | `.../agent-factory-bootstrap-pack/docs/08-research-backlog/RESEARCH_QUEUE.yaml` | `status: seed_only`. ⚠ From the stranger's pack |

**Total: 53 distinct research items** (60 counting the bootstrap seed, which duplicates several).

⛔ **The critical structural finding: the SIHRE queue and the R-lane programme have never been
reconciled.** R1–R19 ran to completion without an answer file for any DR prompt, and
`docs/research/backlog.yaml` — generated 2026-09-02 with 26 candidates — **does not cite DR01–DR08
once**. The queue the requirement asks me to compare against newer work was, on the evidence,
never compared against *any* work.

```bash
grep -rn "DR0[1-8]" docs/research/backlog.yaml docs/research/SYNTHESIS.md   # 0 hits
```

---

## 2. DR01–DR08 classified

Classification is against: `docs/research/answers/` (18 completed lanes),
`docs/_index/current_vs_proposed.md` (the 124-row capability matrix), `docs/agent-army/CURRENT_STATE.md`
(code-measured), `.agent-platform/RECONCILIATION.md`, and the canonical ontology recovered from
`CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip`.

| # | Report | Classification | Evidence |
|---|---|---|---|
| **DR01** | Prior Art and Novelty Boundary for Agent 2.0 | **FULLY_SUPERSEDED** | ⭐ Wave 0 in the sibling repo already ran this and **falsified the founding premise**: *"Artificial Organization Engineering is organisation-oriented MAS, which has a metamodel (Moise+), a runtime (JaCaMo) and a textbook; the category name is taken twice in 2026 (Waites `arXiv:2602.13275`; IMACS `arXiv:2607.25446`, which IS the organizational-compiler thesis)."* `.agent-platform/RECONCILIATION.md` §1.1. Re-running DR01 buys a refutation already paid for. |
| **DR02** | Cognitive Portfolio Theory for team selection | **STILL_REQUIRED** | 🔴 **The single strongest survivor.** Correlated-failure-aware team composition is untouched: **RB-11** (*"Error correlation between agent configurations"*, `EXPERIMENT_DESIGN`) and **RB-06** (*"Which agent-configuration parameters actually change outcomes"*) both circle it without covering the portfolio objective. ⚠ *IDs corrected 2026-09-03 — previously cited as RB-17 and RB-12 by position.* ⚠ **Blocked on data, not on research** — `.data/runs.jsonl` holds 10 rows, 0 `PASS`, all 7 `agent_returned` events `dry_run=True`. A covariance estimator over zero real missions is unestimable. |
| **DR03** | Recursive SIHRE / morphological cognition | **PARTIALLY_SUPERSEDED** | R2 (topology) and **RB-04** (*"Topology-task fit"*) cover the topology-selection half. The *recursive* half — one contract reused across Expert→Agent→Team→Army→Factory — survives and is now better named by the canonical ontology's **Mesh Hierarchy** (*"a hierarchical Mesh can contain sub-Meshes that use completely different architectures"*). **Rescope to recursive control stability and uncertainty propagation only.** |
| **DR04** | Contextual Trust, Transactive Memory, Agent KG Mesh | **ABSORBED_INTO_NEW_LANE** | Absorbed by **HyperMESH** (117 occurrences / 31 files) and by the ontology's **Contextual Trust / Capability Model** (*"trust is contextual rather than a single global score: operative × capability × mission type × environment × time"*) — which is DR04's thesis, restated more precisely. **RB-03** covers the store-capability half. **Retire DR04; fold its graph schema and Goodhart-resistance sections into the HyperMESH lane.** |
| **DR05** | Homeostasis, immunity, digital twin | **DEFERRED_FRONTIER** | Maps to **Operative Immune System** (6 occurrences / 6 files) and **Reliability Corps / Self-Maintenance** in the ontology. ⛔ Its stated goal — *"turn Agent Health into operational control rather than a dashboard score"* — is unreachable while `factory/readiness.py` has never scored a non-dry-run mission. **Gate behind the first real run.** |
| **DR06** | Evaluation framework and benchmarks | **PARTIALLY_SUPERSEDED** | R1 (eval harness) ran and `factory/evals.py` + `calibration.py` + `contract.py` exist as **code with tests** — the negative-control gate is built. What survives is DR06's **ablation and component-contribution** design (the requirement's "benchmark ablation": 36 occurrences / 24 files, **0 in code**) and its **stop/go criteria per feature**. **Rescope to ablation design only.** |
| **DR07** | Cross-domain mechanism mining (40+ mechanisms) | **OPTIONAL_CASE_STUDY** | R17's own §8 verification ledger and `backlog.yaml`'s read-before-dispatch rule #6 both warn: *"REPEATED AI CLAIMS ARE NOT INDEPENDENT EVIDENCE. Five of the nine inbound packs carry the same source file byte-for-byte."* A prompt asking for *"at least 40 candidate mechanisms"* is a generator of plausible unfalsifiable analogies. ⚠ **Its own step 5 — "what would be superficial anthropomorphism" — is the only part worth keeping.** Demote. |
| **DR08** | Entity definition and naming | **ABSORBED_INTO_NEW_LANE** | ⭐ **Already answered.** `CELL_OS_Canonical_Terminology_vNext.md` delivers the taxonomy, the minimum defining properties (Operative's seven), the collision register (`KNOWN_TERMINOLOGY_COLLISIONS.md`) and both naming registers DR08 asked for. **The answer exists inside an unopened ZIP.** Surfacing it (Batch 2 of the migration) closes DR08 outright. |

### 2.1 Distribution

| Classification | Count | Reports |
|---|---|---|
| STILL_REQUIRED | **1** | DR02 |
| ABSORBED_INTO_NEW_LANE | 2 | DR04, DR08 |
| PARTIALLY_SUPERSEDED | 2 | DR03, DR06 |
| FULLY_SUPERSEDED | 1 | DR01 |
| OPTIONAL_CASE_STUDY | 1 | DR07 |
| DEFERRED_FRONTIER | 1 | DR05 |
| REJECTED | 0 | — |

⭐ **One of eight survives intact, and it is blocked on a missing measurement rather than on missing
research.** That is the shape of the whole delta: the queue was written when the estate had no
runs; it now has instruments and still no runs.

---

## 3. The other 45 items, in brief

**R1–R19** (18 completed): none is superseded by CELL OS work. They measured *this* estate; CELL OS
is a vocabulary and product layer over it. `docs/research/agent-factory-concept-inventory.md` §3
holds the do-not-re-ask list, and re-asking *"buys the same answer at full price"*. **R06B
(collective cognition and knowledge architecture) has a prompt and no answer** — the only orphan in
the executed programme, and it overlaps DR04/HyperMESH directly. **Classification:
`STILL_REQUIRED`, and it should be merged into the HyperMESH lane rather than run alone.**

**RB-00A–RB-00F and RB-01–RB-20**: all `CANDIDATES_NOT_DISPATCHED`. Six carry `type: NOT_RESEARCH`
— **they are `RB-00A` … `RB-00F`**, not RB-01…RB-06 — and the backlog's
own read-first note is unambiguous:

> *"⭐ SIX OF THE EIGHT CRITICAL GAPS ARE NOT RESEARCH. GAP-01 is a file conversion. GAP-08 is
> scoring a second connector. GAP-09 is fixing one open finding and running the loop. GAP-26 and
> GAP-27 are decisions for a human. GAP-30 is asking a client two questions. Buying a research
> answer to a question that measurement would settle more cheaply is this corpus's characteristic
> failure, and it has been paid for at least twice."*

**Classification for all six: `REJECTED` as research — they are work items.** They belong in
`docs/status/PROJECT_PROGRESS.yaml` as tickets, not in a prompt queue. This is the single largest
correction available to the queue.

---

## 4. Design additions that post-date the SIHRE queue

All 25 named concepts, censused over the working tree with `docs/restructure/` excluded (those are
this Phase 1 pass's own documents — including them would have counted my own writing as evidence
of the project's design state, and did on the first run).

```bash
python scratchpad/delta_scan.py     # 1001 text files; docs/restructure/ excluded
```

| Concept | Occurrences | Files | In `factory/` code? | Verdict |
|---|---:|---:|:---:|---|
| Organizational Compiler / Org-IR / Cell-IR | 189 | 77 | **0** | DOC-ONLY — ⛔ and **refuted as novel** (IMACS) |
| HyperMESH | 117 | 31 | **0** | DOC-ONLY |
| CELL Foundry | 52 | 1 | **0** | DOC-ONLY — ⚠ 52 hits in **one** file |
| Shadow Execution Twin | 38 | 20 | **0** | DOC-ONLY |
| Benchmark ablation | 36 | 24 | **0** | DOC-ONLY |
| Morphogenetic Mesh | 20 | 8 | **0** | DOC-ONLY |
| Cognitive Economics | 8 | 6 | **0** | DOC-ONLY |
| Operative Immune System | 6 | 6 | **0** | DOC-ONLY |
| Capability Graph | 1 | 1 | **0** | ⚠ NEAR-ABSENT |
| Mission Compiler | 1 | 1 | **0** | ⚠ NEAR-ABSENT |
| Operative Canonical Layered Model | **0** | 0 | 0 | ⛔ **ABSENT** |
| Optional layers | **0** | 0 | 0 | ⛔ **ABSENT** |
| Domain Plane | **0** | 0 | 0 | ⛔ **ABSENT** |
| Domain Genome | **0** | 0 | 0 | ⛔ **ABSENT** |
| Domain Compiler | **0** | 0 | 0 | ⛔ **ABSENT** |
| Domain Fabric | **0** | 0 | 0 | ⛔ **ABSENT** |
| Domain Data Plane | **0** | 0 | 0 | ⛔ **ABSENT** |
| Claims–Evidence Graph | **0** | 0 | 0 | ⛔ **ABSENT** |
| Causal World Model | **0** | 0 | 0 | ⛔ **ABSENT** |
| Temporal Executive | **0** | 0 | 0 | ⛔ **ABSENT** |
| Earned Authority | **0** | 0 | 0 | ⛔ **ABSENT** |
| MESA | **0** | 0 | 0 | ⛔ **ABSENT** |
| Recursive Operative Genesis | **0** | 0 | 0 | ⛔ **ABSENT** |
| Capability envelopes | **0** | 0 | 0 | ⛔ **ABSENT** |
| CELL-Q | **0** | 0 | 0 | ⛔ **ABSENT** |

### 4.1 The three findings in that table

**⛔ 4.1.1 — Zero of twenty-five exist in code.** Not one appears in `factory/` (68 modules, 23,939
lines) or `evaluator_service/`. Every one of these is a **named idea**, and the repository's own
governing rule applies: *"Do not claim something is implemented because it appears in a design
document."*

**⛔ 4.1.2 — Fifteen of twenty-five have zero occurrences anywhere in the repository.** They are not
under-documented; they are **not here at all**. They exist in the requirement text and in
conversations this repository has no record of. That includes the entire **Domain** family (Plane,
Genome, Compiler, Fabric, Data Plane — 0/0/0/0/0) and **CELL-Q** (0), which is why
`04_PROPOSED_TARGET_STRUCTURE.md` §1 refuses to create `packages/` and `domains/` directories for
them: those trees would be empty by construction.

⚠ **A necessary caveat on 4.1.2, because a zero from a blind instrument is not a measurement.** The
scan reads 1,001 **text** files. It cannot see inside the four unreadable CELL OS binaries
(`CELL_OS_Product_Technical_Design_v0.1.docx` 311 KB, `…User_Guide_v0.2.docx` 66 KB,
`CELL_OS_Delivery_Backlog_v0.2.xlsx` 43 KB, `CELL OS Design Master Brief.pdf` 249 KB) or inside 32
ZIPs beyond their namelists. **Several of these fifteen are plausibly defined in the v0.1 technical
design.** Correct verdict for those: **`NOT-VISIBLE`, not `ZERO`** — and converting the two `.docx`
(Batch 2, converter already exists and was verified at 100.1% coverage) is what would change it.

**⭐ 4.1.3 — The most-cited new concept is the one already refuted.** "Organizational Compiler /
Org-IR" leads the table at 189 occurrences across 77 files — and `.agent-platform/RECONCILIATION.md`
§1.1 records that `arXiv:2607.25446` (IMACS) **is the organizational-compiler thesis, published five
weeks before the pack proposing it**. The vocabulary is spreading through the corpus faster than the
refutation is.

---

## 5. What changed between the queue and now — the design delta stated plainly

| Dimension | At SIHRE queue time | Now | Consequence for the queue |
|---|---|---|---|
| Entity term | Open question (DR08) | **Settled**: Operative / Cell Mesh / Cell / Organization / CELL OS | DR08 → ABSORBED |
| Novelty of the org-compiler thesis | Assumed open (DR01) | **Refuted on primary sources** | DR01 → FULLY_SUPERSEDED |
| Memory/trust substrate | Ungrouped (DR04) | Named **HyperMESH** + Contextual Trust Model | DR04 → ABSORBED |
| Topology | Ungrouped (DR03) | **Mesh Architecture / Topology / Hierarchy**, three distinct concepts | DR03 → PARTIALLY_SUPERSEDED |
| Eval | Design question (DR06) | **Built**: `contract.py`, `evals.py`, `calibration.py`, tests | DR06 → rescope to ablation |
| Runs to learn from | 0 | **Still 0** (10 rows, 0 PASS, all dry_run) | DR02 blocked, DR05 gated |
| Link semantics | Absent | **First-class**: Link, Link Contract, Link Type Registry, Link Fabric | ⭐ **NEW LANE, unqueued** |
| Product surfaces | Absent | NERVE, Mission Control, Briefing Room, Cell Studio, Replay | ⭐ **NEW LANE, unqueued** |
| Domain / CELL-Q | Absent | **Still absent (0 occurrences)** | ⛔ Cannot be queued; nothing to research yet |

⭐ **The two genuinely new research lanes the old queue could not have contained are Link semantics
and Product surfaces**, and neither appears in DR01–DR08, R1–R19, or the RB backlog. They are the real
gap — not the Domain family, which is not yet an idea in this repository.

---

## 6. Recommended final prompt queue — provisional

⚠ **PROVISIONAL.** Sequencing against `CELL_OS_Optimized_Deep_Research_Prompt_Manifest_v2.md` is
impossible while that file is absent (§7). This queue is sequenced against the repository.

**Ordering principle, taken from `backlog.yaml`'s own read-first block: measurement before research,
and nothing dispatched that measurement would settle more cheaply.**

### Tier 0 — Not research. Do these; do not buy answers to them.

| # | Action | Replaces | Why |
|---|---|---|---|
| 0.1 | **Surface the canonical ontology from the ZIP** | **DR08 entirely** | The answer already exists. `Batch 2`. Zero research cost |
| 0.2 | **Convert the 2 CELL OS `.docx`** | Part of §4.1.2 | Converter exists, verified 100.1%. Turns 15 `NOT-VISIBLE` verdicts into real ones |
| 0.3 | **Complete one real, non-dry-run agent run** | **Unblocks DR02 and DR05** | ⭐ The binding constraint on the entire queue |
| 0.4 | Give the 6 `NOT_RESEARCH` backlog rows dispositions | **`RB-00A`…`RB-00F`** (GAP-01, 08, 09, 30, 04, 07) | They are tickets |

### Tier 1 — Research, in dependency order

| # | Lane | From | Blocked by |
|---|---|---|---|
| 1.1 | **Link semantics and Link Contracts** → v3 **CELL-DR-02** | ⭐ NEW — in no existing queue | ⚠ **Not "nothing" — REVISED.** A Link ontology already exists inside `CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip`. **Rescope before dispatch** — `09` §7.2 |
| 1.2 | **HyperMESH** — memory, contextual trust, provenance → **CELL-DR-03** | DR04 + R06B + **RB-03** merged | Tier 0.1 |
| 1.3 | **Ablation and component contribution** → **CELL-DR-06** | DR06 rescoped + **RB-09** | Tier 0.3 for *measured* ablation; ⭐ the **protocol may be designed now** |
| 1.4 | **Cognitive portfolio / correlated failure** → **CELL-DR-05** | **DR02 intact** + **RB-11** | ⛔ Tier 0.3, hard — and ⭐ **one run is not enough**; needs repeated comparable missions |
| 1.5 | **Recursive Mesh Hierarchy control stability** → **CELL-DR-07** | DR03 rescoped | 1.1 (Links define the recursion) |
| 1.6 | ~~**Product surfaces — NERVE information architecture**~~ | ⭐ NEW; R12/R13 adjacent | ⛔ **SUPERSEDED by v3 §8** — run a *local integration-gap audit*, not a research lane |

### Tier 2 — Deferred frontier

| # | Lane | From | Unlock condition |
|---|---|---|---|
| 2.1 | Homeostasis / immunity / self-model | DR05 | ≥ 1 real run **and** a measured drift event |
| 2.2 | Cross-domain mechanism mining | DR07, demoted | Only the anthropomorphism-filter section |
| 2.3 | Domain Plane / Domain Genome / CELL-Q | — | ⛔ **Cannot be queued.** 0 occurrences. Write the design first |

### Sequencing errors this correction fixes

1. **DR01 was first and is fully superseded** — the queue opened with a question already answered
   against primary sources.
2. **DR02 was second and is unrunnable** — it needs mission history that does not exist. Sequenced
   second, it would have consumed a full research pass to conclude "insufficient data".
3. **DR08 was last and is the cheapest** — its answer is sitting in an unopened ZIP.
4. **Link semantics is absent from every queue** and is the only Tier-1 lane with no blocker.
5. **Six work items sit in a research backlog**, where they cannot be worked and can be dispatched
   by accident.

---

## 7. ✅ Comparison against the v2 manifest — COMPLETE

**Performed 2026-09-03 on arrival.** v2 (`bc111d5d…`, 646 lines) and the legacy twenty-report queue
(`6d142560…`, 166 lines) were read in full, alongside a third document that post-dates this one:
**CELL OS Deep Research Manifest v3** (`bef3b644…`, 720 lines).

The six questions §7 pre-committed to, answered in order. **Full working: `09` §4.**

### 7.1 Which of the 25 concepts does v2 queue?

Twenty of twenty-five. ⛔ **Five are queued by neither v2 nor v3**: Cognitive Economics, Operative
Immune System, Causal World Model, Temporal Executive, capability envelopes. All five appear in
v3 §4.2's `PROPOSED_EXTERNAL` list — **declared as approved design inputs, then assigned to no lane.**

### 7.2 ⛔ Does v2 queue research into ideas this repository has no record of? **Yes — heavily.**

v2 Lane 08 designs the Domain Plane, Genome, Compiler, Fabric and Data Plane; Lane 09 designs the
whole CELL-Q organization. **Measured occurrences of every one of those terms here: zero.** v2
labels none of them and gates none of them.

⭐ **This is the single largest improvement v3 makes.** v3 §4.2 marks them `PROPOSED_EXTERNAL` —
*"none is implemented merely because it is listed here"* — and §10 inserts **"write approved Domain
design record"** as a hard predecessor of CELL-DR-08. **The prediction this section made on
2026-09-03 — that a manifest queueing the 15 `ABSENT` concepts would need the design written before
the research is bought — is exactly what v3 concluded independently.**

### 7.3 ⛔ Does v2 repeat DR01? **Yes.** Does it repeat DR07? **No.**

v2 Lane 02 is a broad prior-art and novelty search across fourteen fields — substantially DR01
re-asked, over ground `.agent-platform/RECONCILIATION.md` §1.1 already lost against primary sources.
✅ **v3 fixes it in the right place**: CELL-DR-01 opens *"Validate rather than repeat the
already-completed broad novelty search."* Neither manifest repeats DR07; v3 keeps only its analogy
filter, which is the part §2 said was worth keeping.

### 7.4 ⛔ Does v2 sequence the blocked lanes before a real run? **Yes — and it has no run gate at all.**

v2 §6 runs Lane 05 (correlated experts, trust updating) and Lane 06 (causal experiment design, Mesh
Gradient) at Wave C. **Nothing in v2 requires a single completed mission at any point.** Its P0
preflight is a corpus audit only. ⭐ **The error §6 of this document corrects is v2's central
structural defect, and v2 does not notice it.**

⚠ **v3 mostly fixes it** with **Gate P0-E** — *"at least one bounded, non-dry-run, non-financial
repository mission with acceptance evidence"* — correctly scoped to gate calibration and performance
claims without gating prior-art or architecture research. ⛔ **But v3 §10 schedules P0-E after the
waves it unblocks, and §5 gates it behind the documentation migration. Both are corrected in
`09` §10.3.**

### 7.5 ⭐ Does either contain the two genuinely new lanes? **v3 does. v2 does not.**

| | Link semantics | Product surfaces |
|---|---|---|
| Repository queues | ⛔ absent | ⛔ absent |
| **v2** | ⛔ **absent as a lane** — a parameter inside Lanes 06/07 | ⛔ **absent** |
| **v3** | ⭐ **CELL-DR-02, a full lane** | ⭐ **§8, a local integration-gap audit** |

**The two lanes §5 of this document identified as the real gap were found independently by v3, and
by nothing else.** On product surfaces v3 is better than this document's own Tier 1.6 — see §6.

### 7.6 Does the ordering respect measurement-before-research? **v2 partially; v3 yes** — five local
gates against v2's one.

### 7.7 ⭐ Verdict, and the finding that changes what happens next

**v3 supersedes v2 as the forward queue** — `V3_ACCEPTED_NOT_ACTIVATED` (`13_V3_ACTIVATION_DECISION.md`).
v2 is retained as historical evidence, and as the **sole source** of two things v3 drops: the SIHRE
acronym expansion (*Self-Improving Heterogeneous Reasoning Ensemble*, Lane 05) and the FMEA plus
complexity-budget outputs (Lane 02).

⛔ **The correction this comparison forces on §6 of this document:** Tier 1.1 (Links) was named the
one Tier-1 lane with **no blocker**, dispatchable today. **That is now false.** The canonical
ontology — still unopened, in `CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip` — already
defines Link, Link Contract, Link Type Registry, Link Fabric, Inter-Mesh Link, Cell Link and
Federation Link, with sixteen candidate Link fields, eighteen candidate Link semantics and a
diagram.

⭐ **This is §2's DR08 finding repeating with a different filename.** The answer to the lane everyone
wanted to dispatch first is sitting in the same unopened archive. **Tier 0.1 was the right next
action for a reason this document did not yet know.**

---

## 8. ⭐ The exact next research action

> ## **Dispatch nothing. Do Tier 0.1 first: surface the canonical ontology from the ZIP.**

```bash
# Read-only. Extracts nothing over an existing path.
python -c "
import zipfile
z = zipfile.ZipFile('docs/raw_research/CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip')
for n in ('CELL_OS_Canonical_Terminology_vNext.md', 'KNOWN_TERMINOLOGY_COLLISIONS.md'):
    p = 'CELL_OS_Frontier_Audit_Research_Pack/01_CANONICAL_ONTOLOGY/' + n
    open('docs/architecture/canonical/terminology/' + n, 'wb').write(z.read(p))
"
```

**Why this and not a research prompt — four reasons, each measured:**

1. **It closes DR08 for zero research cost.** The taxonomy, minimum defining properties, collision
   register and both naming registers DR08 asks for already exist.
2. **It unblocks the terminology decision** that `06_TERMINOLOGY_SUPERSESSION.md` cannot settle while
   the ontology is ungreppable. Nothing in the repository can currently search its own canon.
3. **It is the cheapest item in the queue** — two file reads, no dispatch, no cost.
4. ⭐ **It is a measurement, and every research lane above it is blocked on one.** The single fact
   governing this entire queue is that `.data/runs.jsonl` holds 10 rows and 0 `PASS`, with all 7
   `agent_returned` events carrying `dry_run=True`. **The estate has instruments and no
   observations.** Buying more research into how to compose teams, when no team has ever completed a
   real mission here, is precisely the failure `README.md` Part I is organised against — a retired
   loop that ran 965 times, measured its own 1.6% success rate, and never acted on it.

**Then, in order:** Tier 0.2 (convert the `.docx` — turns fifteen `NOT-VISIBLE` verdicts into real
ones and may well populate the Domain family), Tier 0.3 (**one real run** — the binding constraint),
and only then Tier 1.1 (Links) as the first genuine dispatch.

> ⭐ **REVISED 2026-09-03 — a fifth reason, and it strengthens the other four.** The same archive
> also holds the **Link ontology** that Tier 1.1 was written to produce: Link, Link Contract, Link
> Type Registry, Link Fabric, sixteen candidate fields, eighteen candidate semantics, plus
> `05_VISUALS/Link_Fabric.mmd`. **Tier 1.1 / CELL-DR-02 must be rescoped from "define Link
> semantics" to "validate, formalise and complete the existing Link ontology" before it is
> dispatched** (`09` §7.2). Its genuinely open questions are the formal reliability/ordering/
> idempotency semantics, the failure and recovery state machine, the compatibility and
> reconfiguration rules, adversarial-link tests, and the **Link Fabric versus CellBus boundary**
> (`CellBus` measures 39 occurrences; `Link Fabric` measures 0, and the ontology's two definitions
> overlap). ⛔ **Dispatching it unrescoped would buy back an artifact this repository already owns —
> which is the failure this whole document was written to prevent.**

---

## 9. Method and limits

**Measured:** filename + content + archive-namelist search for both named documents (0 hits);
25-concept regex census over 1,001 text files with `docs/restructure/` excluded; the full research
population (8 + 19 + 26 + 7); `grep` for DR-prompt citations in `backlog.yaml` and `SYNTHESIS.md`
(0 hits); all 8 DR prompts read in full; `CELL_OS_Canonical_Terminology_vNext.md` and
`KNOWN_TERMINOLOGY_COLLISIONS.md` read in full from inside the archive.

**Not read, and therefore a limit on §4.1.2:** the four unreadable CELL OS binaries (669 KB
combined) and the interiors of 32 ZIPs beyond namelists. Fifteen concepts are recorded `ABSENT` from
text; several are more accurately **`NOT-VISIBLE`** and Tier 0.2 is what resolves them.

**Not attempted:** any dispatch, any external search, any promotion to canonical.

### 9.1 ⛔ Revision note 2026-09-03 — a systematic citation error, corrected

Every `RB-` citation in this document originally pointed at the wrong backlog row.
`docs/research/backlog.yaml` numbers its 26 missions **`RB-00A`…`RB-00F`, then `RB-01`…`RB-20`** —
not a contiguous `RB-01`…`RB-26`. This document referenced them **by position**, shifting each
citation by six.

```bash
python -c "import yaml; d=yaml.safe_load(open('docs/research/backlog.yaml',encoding='utf-8')); \
print([m['research_id'] for m in d['missions']])"
```

| Was cited as | Corrected to | What the wrongly-cited ID actually names |
|---|---|---|
| RB-17 — error correlation | **RB-11** | a crosswalk for the six evidence vocabularies |
| RB-12 — which config parameters change outcomes | **RB-06** | credit assignment across a team |
| RB-10 — topology-task fit | **RB-04** | near-miss capture in high-reliability organisations |
| RB-09 — the store-capability question | **RB-03** | an evaluation protocol for org and team designs |
| RB-15 — ablation | **RB-09** | rank ladder versus absence table |
| RB-01…RB-06 — the six `NOT_RESEARCH` rows | **RB-00A…RB-00F** | five prior-art/foundational lanes and one comparison |

⭐ **In every case the row wrongly cited is a plausible-looking research item, so the error never
announced itself.** It is the same class as the instrument error recorded above: a measurement that
looked right and was not. **Recorded rather than silently fixed, because the mechanism — inferring
an identifier from a position instead of reading it — will otherwise be repeated.**

⚠ **One instrument error, caught and corrected, recorded because it is the same class this document
warns about.** The first census run included `docs/restructure/` and returned non-zero counts for
Domain Plane (5), Domain Genome (1), Domain Fabric (1), CELL-Q (5) and MESA (1) — **every one of
those hits was this Phase 1 pass's own writing from an hour earlier.** Uncorrected, it would have
reported five absent concepts as present, on evidence I had just authored. The corrected scan
excludes `docs/restructure/` and every figure in §4 comes from it.
