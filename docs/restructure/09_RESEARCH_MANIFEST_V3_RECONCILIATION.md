# 09 — CELL OS Research Manifest v3 reconciliation

**Phase 1 addendum, bounded.** Measured 2026-09-03 against `agent-factory` @ `827f871` (`main`),
re-verified at the time of writing.
⛔ **No external research was dispatched. No Phase 2 migration was started. No tracked file was
moved, renamed or deleted.**

> ## ⭐ REVISED 2026-09-03 by Gate P0-B — three sections of this document are superseded
>
> | Section | Status after P0-B |
> |---|---|
> | **§5.2** — 13 concepts `ABSENT (corroborated)` | ⭐ **UPGRADED to `ZERO (MEASURED)`** — all four binaries read, every instrument positive-controlled. `14` §5.2 |
> | **§6.2** — the blueprint collision | ⭐ **SUPERSEDED by `15` E-02.** ⚠ `Cell Blueprint` is **not** 0 everywhere — it occurs once in the newly converted v0.1 and once in the ontology heading, though it is **never independently defined** |
> | **§7.2** — *"substantial Link specification"* | ⛔ **CORRECTED by `15` §3.** Measured, it is **one document with each Link entity mentioned once**, fields labelled *"Potential"* and semantics *"Candidate"*. The conclusion (rescope) stands; the argument was stronger than the evidence supported |
>
> **New authorities:** `14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md` (terminology),
> `15_V3_ERRATA_OVERLAY.md` (v3 errata), `16_CELL_DR_02_RESCOPED_SPEC.md` (the lane to dispatch).
> Everything else in this document stands as measured.

**Eventual destination:** `docs/research/RESEARCH_MANIFEST_V3_RECONCILIATION.md`.
Written here because `docs/restructure/` is the Phase 1 workspace and the final research paths are
Phase 2 territory. See §13.

---

## 0. What this document is, in one paragraph

`docs/research/DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` §7 was **blocked** on two documents that did not
exist in this repository. Both have now arrived, together with a third (v3) that post-dates the
Phase 1 audit. This document ingests all three, completes the blocked comparison, maps every old
prompt into v3, and returns an activation decision. **It classifies; it does not dispatch.**

---

## 1. Source intake — hashed, inventoried, provenance recorded

### 1.1 The container

```bash
sha256sum docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack.zip
# fd04c2ba90e9d260ef9985255ecf10586ff78721f565ddd7a791840d53ffad26
```

### 1.2 The four attached sources

Extracted read-only into `docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack/`.
**Hashes were taken inside the archive and again after extraction, and match byte-for-byte** — the
originals are unchanged and the ZIP is untouched.

| Source | SHA-256 | Bytes | Lines | Origin |
|---|---|---:|---:|---|
| `CELL_OS_Deep_Research_Manifest_v3.md` | `bef3b644…6cb826a5` | 26,706 | 720 | ⭐ **Outside the earlier repository corpus** |
| `CELL_OS_Optimized_Deep_Research_Prompt_Manifest_v2.md` | `bc111d5d…a5b8af72c` | 25,420 | 646 | ⭐ **Outside the earlier repository corpus** |
| `SIHRE_Recommended_Deep_Research_Report_Queue_Legacy.md` | `6d142560…1872b817af7` | 6,660 | 166 | ⭐ **Outside the earlier repository corpus** |
| `CLAUDE_PHASE1_INGEST_CELL_OS_RESEARCH_V3.md` | `01cdac38…5d0c985701` | 6,550 | 167 | Instruction document for this pass |

```bash
# regeneration
sha256sum docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack/*.md
wc -lc   docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack/*.md
```

### 1.3 ⭐ The provenance record that matters

**All three research-planning documents originated outside the earlier repository corpus.** They
were authored in project conversations on 2026-09-03 and had **no record in this repository** at the
time of the Phase 1 audit. This is stated as a measured fact, not an inference:

```bash
# performed during the Phase 1 audit, before this pack arrived
find . -path ./.git -prune -o -iname "*Optimized*" -print -o -iname "*Prompt_Manifest*" -print   # 0
grep -rIl "Recommended Deep Research Report Queue" --exclude-dir=.git .                          # 0
python  # zipfile.namelist() across 32 archives, matching optimized|manifest_v2|queue            # 0
```

**Consequence, and it is the governing one for every classification below:** the concepts these
documents introduce are `PROPOSED_EXTERNAL` — approved design inputs — **not** `IMPLEMENTED`,
`PROVEN` or `CANONICAL`. Their absence from the repository does not reject them; it means they carry
no local evidence yet.

### 1.4 The blocked comparison is now unblocked

`DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` §0 recorded both missing documents as **`NOT-PRESENT`, not
`ZERO`**, and named the most likely explanation as a hypothesis: *"both documents exist outside this
repository … the v2 manifest in particular reads like an artifact of a planning conversation."*

⭐ **That hypothesis is now confirmed.** The instrument was not blind; the documents were not here.
Recording this because the distinction is the one the corpus most often gets wrong in the other
direction.

---

## 2. Measured repository truth — preserved, and three values re-measured

v3 §2 states a repository-grounded baseline. Every value was re-verified before use. **Three have
drifted and one names a file that does not exist.**

| Baseline fact | v3 states | Re-measured 2026-09-03 | Verdict |
|---|---|---|---|
| Commit / branch | `827f871` on `main` | `827f871` on `main` | ✅ HOLDS |
| Python distributions / package shape | one dist, one flat `factory` package | one dist, flat package | ✅ HOLDS |
| Runtime modules | 68 | **68** | ✅ HOLDS |
| Runtime lines | 23,939 | **23,939** | ✅ HOLDS |
| Dependency centre | `factory/contract.py` | `factory/contract.py` | ✅ HOLDS |
| Runtime dependency | PyYAML only | PyYAML only | ✅ HOLDS |
| JS/TS production app / monorepo tooling | none | none | ✅ HOLDS |
| Hard-coded documentation paths | 7, runtime-coupled | unchanged | ✅ HOLDS |
| Test baseline | 1,016 passed · 2 failed · 2 xfailed — AMBER | not re-run this pass | ⚠ **INHERITED, NOT RE-MEASURED** (§12) |
| Recorded runs | 10 rows, 0 PASS | **10 rows** | ✅ HOLDS |
| Returned runs | 7, all dry-run | 7, all `dry_run=True` | ✅ HOLDS |
| Named CELL OS concepts in code | zero | **zero** (§5) | ✅ HOLDS |
| Index delta | 719 claimed vs **888** measured | 719 claimed vs **898** measured | ⚠ **DRIFTED — v3's figure is stale by 10** |
| Overlapping modified files | **seventeen** | **eighteen** | ⚠ **DRIFTED — v3 is short by one** |
| Code anchor `factory/forecast.py` | listed as a measured anchor | ⛔ **DOES NOT EXIST** | ⛔ **WRONG PATH** |

```bash
git rev-parse --short HEAD                                                    # 827f871
find factory -name '*.py' | wc -l                                             # 68
find factory -name '*.py' -exec cat {} + | wc -l                              # 23939
wc -l .data/runs.jsonl                                                        # 10
find docs .agent-platform blueprints missions evals boot-prompts -type f | wc -l   # 898  (manifest claims 719)
git status --porcelain | grep -c '^ M'                                        # 18
ls factory/forecast.py                                                        # No such file or directory
ls factory/projection.py                                                      # exists
```

### 2.1 ⛔ Six of seven named code anchors verify. One does not.

v3 §4.1 lists seven modules as "measured implementation anchors". Measured:

| Anchor named in v3 | Exists? |
|---|---|
| `factory/contract.py` | ✅ |
| `factory/blueprint.py` | ✅ |
| `factory/evals.py` | ✅ |
| `factory/calibration.py` | ✅ |
| `factory/readiness.py` | ✅ |
| `factory/roadmap.py` | ✅ |
| **`factory/forecast.py`** | ⛔ **absent** |

`factory/projection.py` exists and is the nearest match by name. ⚠ **Stated as a hypothesis, not a
finding** — nothing was read to establish that `projection.py` performs the role v3 attributes to
`forecast.py`. **CELL-DR-01's attachment list must cite `projection.py` or drop the anchor.** A
manifest that names a non-existent module as *measured* is the failure mode the whole baseline
exists to prevent, and it appears once in v3.

### 2.2 On the AMBER test baseline

v3 correctly makes AMBER "the honest baseline ceiling". **This pass did not re-run the suite**, so
1,016 / 2 / 2 is carried forward as an inherited value, not a measurement. It must be re-measured
before any migration batch, per v3 Gate P0-D and the instruction's own "remeasure any snapshot value
before using it after migration."

---

## 3. Four readiness axes, reported separately for every v3 lane

Per the instruction §3 and v3 §3.2. ⭐ **The rule applied throughout: absent mission history blocks
empirical calibration and promotion. It does not block prior-art research, mathematical formulation,
architecture design or experiment design.**

| Lane | RESEARCH | EXPERIMENT | IMPLEMENTATION | PROMOTION |
|---|---|---|---|---|
| **CELL-DR-01** Canonical architecture delta | ⚠ **BLOCKED-LOCAL** — P0-A ✅ done; P0-B, P0-C open | n/a — no experiment required | ⛔ NOT_READY | ⛔ NOT_READY |
| **CELL-DR-02** Link semantics / Link Fabric | ⚠ **READY-ON-RESCOPE** — a Link ontology already exists locally (§7) | ⛔ BLOCKED — no two-component harness exists | ⛔ NOT_READY — `CellBus` semantics unresolved | ⛔ NOT_READY |
| **CELL-DR-03** HyperMESH substrate | ⚠ **BLOCKED-LOCAL** — P0-B, P0-C open | ⛔ BLOCKED — P0-E | ⛔ NOT_READY | ⛔ NOT_READY |
| **CELL-DR-04** Operative Kernel / lifecycle | ⚠ BLOCKED on DR-01 + DR-03 | ⛔ BLOCKED — P0-E | ⚠ **PARTIAL** — `blueprint.py`, `contract.py`, `readiness.py` are real anchors | ⛔ NOT_READY |
| **CELL-DR-05** SIHRE adaptive cognition | ✅ **READY** for literature + architecture once DR-03/04 land | ⛔ **BLOCKED, HARD** — correlated-failure covariance needs repeated comparable missions | ⛔ NOT_READY | ⛔ NOT_READY |
| **CELL-DR-06** CELL ADAPT optimization | ✅ **READY** for method research once DR-04/05 land | ⛔ **BLOCKED, HARD** — ablation needs multiple comparable runs across task classes and seeds | ⚠ **PARTIAL** — `evals.py`, `calibration.py` exist with tests | ⛔ NOT_READY |
| **CELL-DR-07** Mesh / Foundry / MESA | ⚠ BLOCKED on DR-02, DR-05, DR-06 | ⛔ BLOCKED — needs real Mesh observations | ⛔ NOT_READY | ⛔ NOT_READY |
| **CELL-DR-08** Domain Plane | ⛔ **BLOCKED** — the required local Domain design record does not exist (0 occurrences, §5) | ⛔ NOT_READY | ⛔ NOT_READY | ⛔ NOT_READY |
| **CELL-DR-09** CELL-Q offline research org | ⛔ BLOCKED on DR-08 | ⛔ BLOCKED — no historical or synthetic dataset is present in this repository | ⛔ NOT_READY | ⛔ **OUT OF SCOPE BY DESIGN** (§9) |
| **CELL-DR-10** Final MESA synthesis | ⛔ BLOCKED on all accepted prior lanes | n/a | ⛔ NOT_READY | ⛔ NOT_READY |

### 3.1 Three consequences of reading the axes separately

1. ⭐ **No lane is blocked on mission history for its research axis.** DR-05 and DR-06 — the two that
   the Phase 1 delta reported as blocked outright — are blocked only on their *empirical* axes.
   Splitting the axes converts two "cannot run" verdicts into "can research now, cannot calibrate
   yet". This is the single most useful thing v3 adds to the delta.
2. ⛔ **CELL-DR-08 is the only lane blocked on an absence that no research can fix.** Its own
   readiness clause requires a local Domain design record; the Domain family measures **0
   occurrences across 998 text files**. The design must be written before the research is bought.
3. ⚠ **Two lanes carry PARTIAL implementation readiness and neither is PROVEN.** Per the
   instruction §5: `contract.py`, `evals.py` and `calibration.py` prove implementation *anchors*.
   They do not prove the end-to-end evaluation architecture. **PARTIAL, not PROVEN.**

---

## 4. v2 versus v3 — the six prepared questions, answered

`DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` §7 pre-committed six questions so the comparison would be one
pass and not another audit. Answering them in order.

### 4.1 Which of the 25 censused concepts does v2 queue, and which does it omit?

| Concept | v2 lane | v3 lane |
|---|---|---|
| Organizational Compiler / Org-IR | Lane 07 | CELL-DR-07 |
| HyperMESH | Lane 04 | CELL-DR-03 |
| CELL Foundry | Lane 07 | CELL-DR-07 |
| Shadow Execution Twin | Lane 07 | CELL-DR-07 |
| Benchmark ablation | Lanes 03, 05, 06 | CELL-DR-04, 06 |
| Morphogenetic Mesh | Lane 07 | CELL-DR-07 |
| Cognitive Economics | ⛔ **omitted** | ⛔ **omitted** |
| Operative Immune System | ⛔ **omitted** | ⛔ **omitted** |
| Capability Graph | Lane 04 | CELL-DR-03 |
| Mission Compiler | ⛔ omitted (Mission Contracts only) | CELL-DR-04 |
| Operative Canonical Layered Model | Lane 03 | CELL-DR-04 |
| Optional layers | Lane 03 | CELL-DR-01, 04 |
| Domain Plane / Genome / Compiler / Fabric / Data Plane | Lane 08 | CELL-DR-08 |
| Claims–Evidence Graph | Lane 04 | CELL-DR-03 |
| Causal World Model | ⛔ **omitted** | ⛔ **omitted** |
| Temporal Executive | ⛔ **omitted** | ⛔ **omitted** |
| Earned Authority | ⛔ omitted (authority/budgets only) | CELL-DR-04 ("Earned Authority" named in §4.2) |
| MESA | Lanes 07, 10 | CELL-DR-07, 10 |
| Recursive Operative Genesis | Lane 03 | CELL-DR-04 |
| Capability envelopes | ⛔ **omitted** | §4.2 only, no lane owns it |
| CELL-Q | Lane 09 | CELL-DR-09 |

⛔ **Five of the twenty-five are queued by neither manifest**: Cognitive Economics, Operative Immune
System, Causal World Model, Temporal Executive, capability envelopes. All five appear in v3 §4.2's
`PROPOSED_EXTERNAL` list, so **v3 declares them as approved design inputs and then assigns none of
them to a lane.** Recorded in §10 as a missing-topic finding.

### 4.2 Does v2 queue research into concepts this repository has no record of?

⛔ **Yes — heavily, and without labelling them.** v2 Lane 08 designs a Domain Plane, Domain Genome,
Domain Compiler, Domain Fabric, Domain Data Plane and Regime-Adaptive Domain Twin Mesh; Lane 09
designs the whole CELL-Q organization. Measured occurrences of every one of those terms in this
repository: **zero.**

⭐ **This is the single largest improvement v3 makes over v2.** v3 §4.2 names them
`PROPOSED_EXTERNAL`, states plainly that *"none is implemented merely because it is listed here"*,
and §10 inserts a **Local Domain** step — *"write approved Domain design record"* — as a hard
predecessor of CELL-DR-08. v2 has no equivalent gate and would have dispatched a design lane into a
vacuum.

### 4.3 Does v2 repeat DR01 (superseded) or DR07 (demoted)?

⛔ **DR01: yes.** v2 Lane 02 is a broad prior-art and novelty search across fourteen fields —
substantially DR01 re-asked. `.agent-platform/RECONCILIATION.md` §1.1 already refuted the founding
novelty premise against primary sources (`arXiv:2602.13275`; `arXiv:2607.25446`, the
organizational-compiler thesis).

✅ **v3 fixes it explicitly.** CELL-DR-01 §Scope opens: *"Validate rather than repeat the
already-completed broad novelty search."* That is the correct instruction and it is stated in the
right place.

**DR07: neither manifest repeats it.** v2 has no cross-domain mechanism-mining lane; v3 retains only
the analogy filter inside CELL-DR-07 — *"a strict filter against superficial biological or social
analogy"* — which is precisely the section the delta identified as the only part worth keeping.

### 4.4 Does either manifest sequence the empirically-blocked lanes before a real run exists?

⛔ **v2: yes, and it has no observation gate at all.** v2 §6 runs Lane 05 (SIHRE, including
correlated experts and trust updating) and Lane 06 (CELL ADAPT, including causal experiment design
and Mesh Gradient estimation) at Wave C. **Nothing in v2 requires a single completed mission at any
point.** Its P0 preflight is a corpus audit only. A covariance estimator over zero real missions is
unestimable, and v2 does not notice.

⚠ **v3: mostly fixed, with one internal inconsistency that matters.** v3 §5 introduces **Gate P0-E**
— *"complete at least one bounded, non-dry-run, non-financial repository mission with acceptance
evidence"* — and correctly scopes it: required for covariance estimation, empirical ablation,
homeostasis calibration and performance claims; **not** required for prior-art or architecture
research. That is exactly right.

⛔ **But v3 §10 schedules P0-E in the "Observation" row, after Wave G (CELL-DR-09) and before only
the final synthesis.** The lanes P0-E unblocks — DR-05, DR-06, DR-07 — run at Waves D and E, *before*
it. **The single binding local constraint is scheduled after the work it gates.** §11 carries the
correction.

### 4.5 Do the manifests contain the two genuinely new lanes — Link semantics and product surfaces?

| | Link semantics | Product surfaces |
|---|---|---|
| Repository queues (DR, R, RB) | ⛔ absent | ⛔ absent |
| **v2** | ⛔ **absent as a lane** — "Links" appears only as a parameter inside Lanes 06 and 07 | ⛔ **absent** |
| **v3** | ⭐ **CELL-DR-02, a full lane** | ⭐ **§8, converted to a local integration-gap audit** |

⭐ **v3 covers both; v2 covers neither.** This is the second decisive improvement, and on product
surfaces v3 is better than the Phase 1 delta's own recommendation: the delta proposed a NERVE
research lane (Tier 1.6); v3 §8 says *"do not create another broad NERVE research lane by default"*
and specifies a local audit instead, dispatching external research only if the audit finds a
consequential unanswered question. **The delta's Tier 1.6 is superseded by v3 §8.**

### 4.6 Does the ordering respect measurement-before-research?

| | Local gates before dispatch | Verdict |
|---|---|---|
| **v2** | P0 corpus audit only | ⚠ **PARTIAL** |
| **v3** | P0-A intake · P0-B canon visibility · P0-C corpus integrity · P0-D migration safety · P0-E observation | ✅ **YES** |

`docs/research/backlog.yaml`'s own read-first rule — *"Buying a research answer to a question that
measurement would settle more cheaply is this corpus's characteristic failure, and it has been paid
for at least twice"* — is honoured by v3's five gates and only half-honoured by v2's one.

### 4.7 Verdict on supersession

⭐ **v3 supersedes v2 as the forward research queue.** It wins on all four axes that separate them:
`PROPOSED_EXTERNAL` labelling, the P0-E observation gate, the Link lane, and the product-surface
demotion to a local audit. **v2 is retained as historical evidence and as the source of two things
v3 dropped** — the FMEA/complexity-budget outputs (§10.1) and the SIHRE expansion (§6.4).

---

## 5. Concept census — re-measured for v3's vocabulary

The Phase 1 delta censused 25 concepts. v3 introduces terms that census did not cover. Re-run over
**998 text files**, excluding `docs/restructure/` and `DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` — this
pass's own writing, whose inclusion previously reported five absent concepts as present.

```bash
python docs/restructure/v3_census.py     # 998 text files at the time this table was measured
```

⛔ **This table is the PRE-P0-B baseline and a re-run no longer reproduces it.** Gate P0-B added the
surfaced ontology and three converted binaries to `docs/raw_research/`, so the census now scans
**1,003** files and returns higher counts for terms those documents contain. **That is the gate
working, not drift.** The post-P0-B measurements — including the revised verdicts for every concept
in this table — are in `14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md` §5 and §6, measured
per-source rather than corpus-wide.

⚠ **The script excludes three things and says why in its own source**: `docs/restructure/` (this
pass's writing), `DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` (the previous pass's writing), and
`docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack/` (**the three manifests are the
source of the vocabulary being censused** — counting them would report the proposal as evidence of
the repository's design state). **The count is regenerable; do not restate these numbers by hand.**

| Term | Occurrences | Files | In `factory/` | Verdict |
|---|---:|---:|---:|---|
| Org-IR | 182 | 78 | 0 | DOC-ONLY — ⛔ novelty refuted (IMACS) |
| SIHRE | 121 | 26 | 0 | DOC-ONLY |
| HyperMESH | 118 | 31 | 0 | DOC-ONLY |
| Evolution Chamber | 101 | 58 | 0 | ⭐ DOC-ONLY — **2nd most-cited, and in no v3 lane** |
| Mission Control | 90 | 55 | 2 | PARTIAL — the only new term with any code presence |
| Stigmergic | 55 | 35 | 0 | ⭐ DOC-ONLY — **dropped from v3** |
| Shadow Twin | 48 | 25 | 0 | DOC-ONLY (v3 says "Shadow **Execution** Twin" — 0 occurrences) |
| Temporal Echelon | 39 | 16 | 0 | ⭐ DOC-ONLY — **dropped from v3** |
| CellBus | 39 | 6 | 0 | DOC-ONLY — ⚠ collides with Link (§6.6) |
| Organizational Compiler | 32 | 20 | 0 | DOC-ONLY |
| Mission Hypergraph | 27 | 13 | 0 | DOC-ONLY |
| Mission Contract | 20 | 13 | **1** | PARTIAL |
| Morphogenetic | 20 | 8 | 0 | DOC-ONLY |
| OS-MESH / T-MESH / C-MESH | 17 / 13 / 11 | 1 / 5 / 4 | 0 | DOC-ONLY |
| Briefing Room | 16 | 12 | 0 | DOC-ONLY |
| NERVE | 14 | 3 | 0 | ⚠ see §8 |
| CELL ADAPT | 13 | 2 | 0 | DOC-ONLY |
| Cell Studio | 13 | 5 | 0 | DOC-ONLY |
| ORCA | 11 | 1 | 0 | DOC-ONLY |
| Operative Cell / Cell Mesh | 10 / 10 | 4 / 3 | 0 | DOC-ONLY |
| Cell Genome | 7 | 3 | 0 | ⚠ §6.2 |
| Cell Image | 4 | 3 | 0 | ⭐ **§6.2 — v3 omits this term entirely** |
| Mission Compiler | 3 | 3 | 0 | NEAR-ABSENT |
| Capability Graph / OPC | 2 / 2 | 2 / 2 | 0 | NEAR-ABSENT |
| CELL Foundry · Configuration Genome · Mesh Gradient · Earned Authority | 1 each | 1 each | 0 | NEAR-ABSENT |
| **Cell Blueprint** | **0** | 0 | 0 | ⛔ **ABSENT — §6.2** |
| **Link Fabric · Link Contract · Link Type Registry** | **0** | 0 | 0 | ⛔ ABSENT in text — ⚠ **but see §7** |
| Operative Kernel · Operative Canonical Layered Model | **0** | 0 | 0 | ⛔ ABSENT |
| Claims–Evidence Graph · Causal World Model · Temporal Executive | **0** | 0 | 0 | ⛔ ABSENT |
| Operative Immune System · Cognitive Economics · Experience-to-Doctrine | **0** | 0 | 0 | ⛔ ABSENT |
| Domain Plane · Genome · Compiler · Fabric · Data Plane | **0** | 0 | 0 | ⛔ ABSENT |
| MESA · Recursive Operative Genesis · CELL-Q · capability envelope | **0** | 0 | 0 | ⛔ ABSENT |
| Capability Lab · Regime-Adaptive · Shadow Execution Twin | **0** | 0 | 0 | ⛔ ABSENT |

### 5.1 ⭐ Zero of the new concepts exist in runtime code. That verdict is now stronger, not weaker.

`Mission Control` (2) and `Mission Contract` (1) are the only terms with any occurrence under
`factory/`, and neither is a component. **The v3 baseline row "Named new CELL OS concepts in code:
zero" holds.**

### 5.2 ⭐ Thirteen `ABSENT` verdicts are now corroborated by a second, independent instrument

The Phase 1 delta correctly cautioned that fifteen zeroes were **`NOT-VISIBLE`, not `ZERO`**, because
the scan could not read four CELL OS binaries — chiefly the 31-page
`CELL_OS_Product_Technical_Design_v0.1.docx` (311 KB).

⭐ **A second instrument exists and was not used in the first pass.**
`docs/raw_research/CELL_OS_Product_Technical_Design_v0.1_Crossreference_Audit_v1.md` is a **525-line
cross-reference audit of that exact `.docx`**, written 2026-09-03, which reports its object model,
mesh vocabulary and runtime boundaries in detail.

```bash
F=docs/raw_research/CELL_OS_Product_Technical_Design_v0.1_Crossreference_Audit_v1.md
for t in "Domain Plane" "Domain Genome" "Domain Fabric" "Domain Data" "CELL-Q" "MESA" \
         "Causal World" "Temporal Executive" "Earned Authority" "Capability Graph" \
         "Immune" "Cognitive Economics" "Recursive Operative" "capability envelope"; do
  printf "%-28s %s\n" "$t" "$(grep -ic "$t" $F)"
done
# every one returns 0
```

**Reconciliation of the two instruments:** the text scan and the `.docx` audit **agree** on all
thirteen. The agreement is the control; there is no divergence to investigate.

⚠ **The honest verdict is therefore `ABSENT (corroborated)`, not `ABSENT (proved)`.** An audit is
selective — it reports what it reviewed, not everything the document contains. The `.docx` itself
remains unconverted, and `.xlsx` and `.pdf` still have no converter here (Decision D-5). **Gate P0-B
is what closes this properly**, and it is still open.

⭐ **What the audit *does* prove is more interesting than what it does not:** it names `Cell Genome`,
`Cell Image`, `CELL Kernel`, `ORCA`, `CellBus` and the organizational compiler — so the v0.1 design
is *not* silent on the entity model. It is silent specifically on the **Domain family and CELL-Q**.
Those two are genuinely new to v3, exactly as v3 §4.2 claims.

---

## 6. Terminology — what the ontology settles, and the four decisions it does not

The instruction §6 names six items requiring explicit decisions. Measured against the canonical
ontology, read read-only from
`docs/raw_research/CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip`
(`01_CANONICAL_ONTOLOGY/CELL_OS_Canonical_Terminology_vNext.md`, 12,055 B, and
`KNOWN_TERMINOLOGY_COLLISIONS.md`, 1,174 B).

| # | Decision required | Covered by the existing collision register? | Status |
|---|---|---|---|
| 1 | Operative Cell vs Cell | ✅ **YES** — row 2: *"Is there a real semantic distinction or should one be retired?"* | **DECISION FRAMED, NOT TAKEN** |
| 2 | Cell Blueprint vs Cell Genome vs Configuration Genome | ⛔ **NO** | ⭐ **RE-STATED — §6.2** |
| 3 | C-MESH, T-MESH, OS-MESH | ⚠ **PARTIAL** — row 4 covers HyperMESH sublabels, not the C/T/OS triple | **DECISION FRAMED, NOT TAKEN** |
| 4 | SIHRE expansion | ⛔ **NO** — the ontology never expands the acronym | ✅ **CLOSED — §6.4** |
| 5 | OPC | ⛔ **NO** — absent from the ontology | ⛔ **OPEN — §6.5** |
| 6 | Link vs CellBus semantics | ⛔ **NO** | ⛔ **OPEN — §6.6** |

⭐ **Two of six are covered by the register that already exists. Four are not.** The register is six
rows long and was written before the Link and Domain vocabulary arrived.

### 6.1 What surfacing the ontology closes

`DESIGN_DELTA` §2 recorded DR08 as **already answered** by this ontology. Confirmed by reading it:
it delivers the core hierarchy (Model → Operative Runtime → Operative → Cell Mesh → Cell →
Organization → CELL OS), the Operative's defining properties, the collision register, and a canonical
short statement. **DR08's disposition is `LOCAL_MEASUREMENT`: surface the file. It is not research.**

### 6.2 ⛔ The blueprint collision is mis-stated in v3 — in both directions

v3 §4.3 states: *"Cell Blueprint, Cell Genome and Configuration Genome currently appear to describe
overlapping ideas. factory/blueprint.py is the implementation anchor. Research must not create a
fourth synonym."*

**Measured:**

| Term | Occurrences | Files | Status |
|---|---:|---:|---|
| **`Cell Blueprint`** | **0** | 0 | ⛔ **Does not appear anywhere in this repository** |
| `Cell Genome` | 7 | 3 | present |
| `Configuration Genome` | 1 | 1 | present, once |
| **`Cell Image`** | **4** | 3 | ⭐ **present — and v3 does not mention it** |
| **`TeamSpec` / `AgentSpec`** | the actual API of `factory/blueprint.py` | ⭐ **the only names with running code and tests** |

```bash
grep -n "class " factory/blueprint.py
# class AgentSpec:   /   class TeamSpec:      <- "Blueprint" appears only in the filename
```

**Three corrections follow:**

1. ⛔ **v3 names a term that does not exist** (`Cell Blueprint`) and **omits one that does**
   (`Cell Image`).
2. ⭐ **The ontology has already decided part of this.** It carries a single heading —
   **"Cell Blueprint / Cell Genome"** — defining them as *one* concept (the declarative versioned
   source specification), and defines **Cell Image** separately as *"a resolved, immutable, versioned
   deployment artifact"*. **Blueprint and Genome are synonyms by declaration; Image is a distinct
   compilation stage.** That is a real distinction, not a collision.
3. ⛔ **The anchor is a filename, not an API.** `factory/blueprint.py` exposes `TeamSpec` and
   `AgentSpec`. Neither noun appears in any CELL OS design document. **So the instruction's
   "do not introduce a fourth synonym" arrives when there are already five names in play**, four of
   them doc-only and one of them — the only one with tests — invisible to every design document.

**Required decision, restated correctly:** choose one name for the declarative spec
(`Blueprint` | `Genome`), keep `Cell Image` as the resolved artifact, and **state the mapping to
`TeamSpec`/`AgentSpec`** so the code and the canon can refer to the same thing. Retire
`Configuration Genome` (1 occurrence) rather than promote it.

### 6.3 Operative Cell vs Cell — framed, not taken

Both the ontology's §"Known terminology collisions" item 2 and `KNOWN_TERMINOLOGY_COLLISIONS.md` row
2 ask the same question and neither answers it. Measured: `Operative Cell` 10 occurrences / 4 files.
**CELL-DR-01 owns this decision; its Required-output list already includes a collision register.**

### 6.4 ✅ SIHRE expansion — closed by ingesting v2

The ontology never expands the acronym. **v2 Lane 05 does**, in its opening line:

> *"the **Self-Improving Heterogeneous Reasoning Ensemble** should become a configurable cognition
> fabric for Operatives and Cell Meshes"*

⭐ **This is a concrete deliverable of the ingest.** SIHRE has 121 occurrences across 26 files in
this repository and its expansion was, until now, recorded nowhere in it. **Basis: SOURCED to v2
(`bc111d5d…`), not measured locally.**

### 6.5 ⛔ OPC — an undefined abbreviation on a customer-facing surface

```bash
grep -rIn "OPC" --exclude-dir=.git --exclude-dir=.worktrees . | grep -v docs/restructure
# boot-prompts/cell-os-deck-2026-09-03.md:27   -> "docs/diagrams/CELL OS - Building your first OPC.png"
# docs/marketing/cell-os-launch-v1/cell-os-deck.html:1549 -> "Build-Your-First-OPC"
```

Two occurrences, **both product/marketing**, plus a diagram file
`docs/diagrams/CELL OS - Building your first OPC.png`. **The term is absent from the canonical
ontology entirely.**

⚠ **Stated as a hypothesis, not a finding: OPC most likely abbreviates "Operative Cell."** Nothing in
the repository states it. ⛔ **This is the worst kind of open term — it is already in a deck and a
diagram, and it has no definition anywhere.** Decide it or remove it from the deck.

### 6.6 ⛔ Link vs CellBus — the collision v3 creates and does not resolve

Measured: `CellBus` = **39 occurrences / 6 files**; `Link Fabric`, `Link Contract`, `Link Type
Registry` = **0 each**. The ontology defines both:

- **CellBus** — *"typed internal event/communication fabric for claims, requests, evidence,
  decisions, escalations, artifacts and state changes"*
- **Link Fabric** — *"runtime infrastructure for creating, enforcing, observing and optimizing Links
  across Operatives, Meshes, Cells and external systems"*

⛔ **Those two definitions overlap substantially and nothing separates them.** v3 CELL-DR-02 lists
*"CellBus relationship"* as the last item of its scope and *"integration map for contract.py and
CellBus"* as an output — so it knows the collision exists and defers it into the lane. That is
acceptable **provided the lane is told the collision is real and pre-existing**, which §7 supplies.

---

## 7. ⭐ Link semantics — explicit coverage confirmed, and a rescope that must happen first

### 7.1 Coverage — confirmed

**Required work item 8 is satisfied.** v3 gives Link semantics a full dedicated lane,
**CELL-DR-02 — Link Semantics, Link Contracts and Link Fabric**, whose scope covers Link as a
first-class typed entity, Link Contract, Link Type Registry, Link Fabric, ownership and authority,
directionality and multiplicity, sync/async/event links, reliability/ordering/idempotency, capability
and trust requirements, evidence and provenance flow, budgets/latency/failure policy, link health and
degradation, local/cross-Mesh/federated links, reconfiguration and compatibility, and the CellBus
relationship.

**This closes the gap the Phase 1 delta identified as the single Tier-1 lane with no blocker and no
home in any existing queue.**

### 7.2 ⛔ But it is not greenfield, and dispatching it as written would buy back what we hold

The canonical ontology — **unsurfaced, sitting inside
`CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip`** — already contains a substantial Link
specification:

| CELL-DR-02 asks for | The ontology already supplies |
|---|---|
| Link as a first-class typed entity | ✅ *"A first-class, typed, governed, measurable relationship between two CELL OS entities"* |
| Canonical Link schema | ⚠ **16 candidate fields** — source/destination, relationship type, direction, protocol/schema, authority, trust, context filter, bandwidth/rate, latency class, cost ceiling, privacy/security policy, verification requirements, activation conditions, fallback, lifetime, evidence requirements |
| Link Type Registry | ✅ named, with the design rule *"prefer this to hundreds of hard-coded enums"* |
| Link Contract | ✅ defined |
| Link Fabric | ✅ defined |
| Link semantics taxonomy | ⚠ **18 candidate semantics** — communication, delegation, authority, knowledge, capability, consultation, escalation, event, synchronization, consensus, competition, adversarial challenge, supervision, resource allocation, temporal handoff, subscription, trust, federation |
| Local / cross-Mesh / federated links | ✅ Inter-Mesh Link, Cell Link, CELL OS Federation Link — with an explicit naming ruling: *"**Do not call this Cell Mesh**"* |
| A visual | ✅ `05_VISUALS/Link_Fabric.mmd` |

⭐ **This is the DR08 failure repeating.** The Phase 1 delta's headline finding was that DR08's answer
was *"sitting in an unopened ZIP"*. **CELL-DR-02's starting point is in the same unopened ZIP**, and
v3 — written without the ontology visible — specifies the lane as though nothing existed.

**Required rescope, and it costs nothing to apply:**

> CELL-DR-02 must be dispatched as **"validate, formalise and complete the existing CELL OS Link
> ontology"**, with `CELL_OS_Canonical_Terminology_vNext.md` attached, **not** as "define Link
> semantics from first principles." Its genuine open questions are the **formal semantics**
> (reliability, ordering, idempotency, failure/recovery state machine), the **compatibility and
> reconfiguration rules**, the **adversarial/degraded tests**, and the **CellBus boundary** (§6.6) —
> none of which the ontology addresses.

⚠ **This is exactly the condition v3 §13 lists last: "no local measurement is being misclassified as
external research."** Unrescoped, CELL-DR-02 fails that condition. **Rescoped, it passes.**

---

## 8. NERVE and product surfaces — the premise is corroborated, the reuse is not evidenced

**Required work item 9 asks for confirmation that completed NERVE research is reused and only
integration gaps remain. That confirmation cannot be given as stated. Here is what is measured.**

### 8.1 The identifiers v2 and v3 use do not exist here

```bash
grep -rIl "NERVE-DESIGN\|SWITCHBOARD-UX" --exclude-dir=.git .    # 0 files
```

v2 §2 lists *"SWITCHBOARD-UX and NERVE-DESIGN research"* among completed work; v3 §8 says they
*"already exist"*. **Neither identifier appears anywhere in this repository.** ⛔ That is a `ZERO`
from an instrument proved able to see identifiers of exactly this kind — it returned every `DR0*`,
`R1*` and `RB-*` id on request.

### 8.2 The research does exist — inside unopened archives

The premise is right; the naming is wrong. Located by archive namelist scan:

| Artifact | Location | Bytes | Surfaced? |
|---|---|---:|---|
| `DEEP_RESEARCH_REPORT.md` (design intelligence) | `CELL_OS_NERVE_Design_Intelligence_MetaSkill_v1.zip` — ⚠ **two byte-identical copies**, repo root and `docs/design/` | 14,230 | ⛔ **NO** |
| `08_NERVE_DESKTOP_MOBILE.md` | `docs/raw_research/CELL_OS_Design_Intelligence_Consolidation_v1.zip` | 1,359 | ⛔ **NO** |
| `Switchboard_UI_UX_Deep_Research_Report.md` | `docs/raw_research/SWITCHBOARD_UI_UX_RESEARCH_PACK_v1.zip` | — | ⛔ **NO** |
| `design-rationale.md`, `api-contract.md` | `docs/raw_research/zeus-switchboard-redesign-pack/` | — | ✅ extracted |

**`NERVE` measures 14 occurrences across 3 files in the working tree, and not one of them is a
research artifact** — they are the v0.1 cross-reference audit, a world-design brief, and the Phase 1
delta itself.

### 8.3 Verdict

| Claim | Verdict |
|---|---|
| Completed NERVE / Switchboard research **exists** | ✅ **CONFIRMED** — located, four artifacts, three still inside archives |
| It is **reused** by the current corpus | ⛔ **NOT EVIDENCED** — no tracked document cites any of them; no index record exists |
| **Only integration gaps remain** | ⚠ **UNVERIFIABLE** — cannot be assessed while the reports are unread |

⭐ **v3 §8's instruction is nevertheless correct and should stand**: do not open a broad NERVE
research lane; run a local integration-gap audit. **Add one precondition:** the audit's first step is
surfacing the four artifacts above, because an integration-gap audit that has not read the design
research will invent gaps rather than find them.

⚠ **One implementation fact the audit will need:** Switchboard is **not** purely a prototype.
`factory/switchboard.py`, `factory/switchboard_p1.py` and `factory/switchboard_render.py` exist on
`main`, with `tests/test_switchboard.py` and rendered evidence at
`.worktrees/switchboard/docs/evidence/switchboard-p0-2026-09-01/`. The audit question *"which
prototype components are purely visual"* has a real answer here and it is not "all of them."

---

## 9. Domain family and CELL-Q — recorded as proposed external design inputs, boundary verified

**Required work items 10 and 11.**

### 9.1 Recorded as `PROPOSED_EXTERNAL`

| Concept | Occurrences (998 text files) | v0.1 `.docx` audit | Classification |
|---|---:|---:|---|
| Domain Plane | 0 | 0 | **PROPOSED_EXTERNAL** |
| Domain Genome | 0 | 0 | **PROPOSED_EXTERNAL** |
| Domain Compiler | 0 | 0 | **PROPOSED_EXTERNAL** |
| Domain Fabric | 0 | 0 | **PROPOSED_EXTERNAL** |
| Domain Data Plane | 0 | 0 | **PROPOSED_EXTERNAL** |
| Regime-Adaptive Domain Twin | 0 | 0 | **PROPOSED_EXTERNAL** |
| CELL-Q | 0 | 0 | **PROPOSED_EXTERNAL** |

⭐ **Repository absence does not reject them.** They are user-approved external design inputs, and
they are recorded in `docs/restructure/10_PROPOSED_research_registry.yaml` under
`external_design_inputs` with `maturity: PROPOSED_EXTERNAL` and their provenance hash. **What
absence *does* mean is that CELL-DR-08 has no local design record to research against**, which is
why v3 §10 correctly inserts "write approved Domain design record" as its predecessor — and why that
step is a **local write, not a research dispatch**.

### 9.2 ✅ CELL-Q boundary — verified, three independent statements

```bash
grep -in "live[- ]account\|brokerage\|real-money\|order execution\|investment recommend" \
  docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack/CELL_OS_Deep_Research_Manifest_v3.md
```

| Line | Statement |
|---:|---|
| 13 | *"CELL-Q exists to stress-test … through historical replay, synthetic environments, offline experiments and paper research. It does not define the generic platform and **must not introduce live-account execution into the initial scope**."* |
| 174 | Common contract rule 16 — *"**Do not provide live-account integration, order-execution instructions or specific investment recommendations.**"* |
| 533 | CELL-DR-09 §Scope and boundary — *"**Exclude live accounts, brokerage connectivity, real-money execution, specific trades and investment recommendations.**"* |

✅ **CELL-Q remains limited to historical replay, synthetic environments, offline experiments and
paper research.** The boundary is stated three times, at three levels — north star, common contract,
and lane scope — and no counter-statement exists anywhere in v3. The legacy queue's Report 18
(NeuroFusion-13) carries the same restriction, and v2 §1 carries it too.

⚠ **One boundary gap worth noting:** v3's Required-output list for CELL-DR-09 includes *"simulated
multi-model allocation"* and a *"drift state machine"* with states through PAPER-ACTIVE. Those remain
inside the paper/simulation boundary as written. **The line to watch in the report ingestion protocol
is any output that would need a live data feed to be meaningful.**

---

## 10. Missing topics, duplicated lanes and sequencing errors

**Required work item 12.**

### 10.1 ⛔ Missing topics — six, ranked by how much evidence the corpus already holds

| # | Missing from all ten v3 lanes | Evidence it matters | Where it came from |
|---|---|---|---|
| 1 | ⭐ **Failure-mode & effects analysis + complexity budget** | v2 Lane 02 required a full FMEA, a complexity-budget model and *"the minimum complexity budget for a useful first implementation"*. Legacy Report 3 is the same question. **v3 folds Lane 02's prior-art half into CELL-DR-01 and drops the FMEA half entirely** — §9's disposition table never mentions v2 Lane 02 | v2 Lane 02 · Legacy 3 |
| 2 | ⭐ **Evolution Chamber** | **101 occurrences / 58 files — the second most-cited concept in the corpus.** Named in v2 Lane 01 and in the ontology (*"Evolution Chamber / Crucible"*). **Appears in no v3 lane scope** | Corpus + v2 |
| 3 | **Stigmergic Fields, Global Workspace, Temporal Echelons** | 55/35, and 39/16 occurrences respectively. All three are in v2 Lane 07's scope. **All three dropped from CELL-DR-07** | v2 Lane 07 |
| 4 | **Operative Performance & Capability Lab** | Legacy Report 19 — contextual capability scoring, calibration tests, temporal holdouts, regression testing, confidence intervals. v3 has fragments (DR-04's readiness schema, DR-06's ablation) but **no lane owns the benchmark suite end-to-end**. `Capability Lab` = 0 occurrences | Legacy 19 |
| 5 | **Observability and trace standards for agent runs** | `RB-02`, priority HIGH. CELL-DR-02 covers *link* observability and CELL-DR-07 an organizational debugger; **run-level tracing is unowned** | RB-02 |
| 6 | **Isolation / adversarial security** | `RB-08`, priority HIGH, `type: ADVERSARIAL`. CELL-DR-04 lists *"deployment and isolation"* as a scope word; **no lane owns a threat model** | RB-08 |

⚠ **Plus five `PROPOSED_EXTERNAL` concepts v3 declares and then assigns to no lane** (§4.1): Cognitive
Economics, Operative Immune System, Causal World Model, Temporal Executive, capability envelopes.
Recommended disposition: **DEFERRED_EXPERIMENT** — keep them in the registry as declared inputs,
do not open lanes for them until CELL-DR-01 rules on whether the layered model needs them.

### 10.2 ⚠ Duplicated lanes — two, both minor and both fixable in the prompt

| Duplication | Where | Fix |
|---|---|---|
| **Prior art re-opened** | CELL-DR-01 scope includes *"existing multi-agent, organizational and workflow-system prior art"* — the ground DR01 and Wave 0 already covered, and where the org-compiler thesis was already refuted | Attach `.agent-platform/RECONCILIATION.md` §1.1 and state that the refutation is an input, not a question. **v3's "validate rather than repeat" instruction already does most of this work** |
| **Correlated failure owned twice** | CELL-DR-05 scope: *"correlated expert failure"*. CELL-DR-06 scope: *"interaction effects, Shapley approximations, causal experiment design"* | Boundary is implicit but not stated. **Assign the estimator to DR-05 and the experiment design to DR-06**, explicitly |

### 10.3 ⛔ Sequencing errors — three

**⛔ 10.3.1 — P0-E is scheduled after the lanes it unblocks.** v3 §10 places the "Observation" row
(P0-E) between Wave G (CELL-DR-09) and the Final synthesis. But §5 correctly states P0-E gates
*"local covariance estimation, empirical ablation, homeostasis threshold calibration [and]
performance claims"* — which live in **CELL-DR-05, CELL-DR-06 and CELL-DR-07, at Waves D and E**.
**Correction: move P0-E into Local 0, or at latest run it concurrently with Wave A.** It has no
dependency on any research lane, and every empirical branch downstream waits on it.

**⛔ 10.3.2 — P0-E is gated behind the documentation migration.** v3 §5 opens Gate P0-E with *"After
the safe migration gates permit it…"*. That makes the highest-value action in the entire programme —
one real, non-dry-run mission — a dependent of a documentation restructure. ⭐ **Nothing about
completing one agent run requires the docs to be reorganised first.** The two are independent.
**Correction: unbind P0-E from P0-D.**

**⚠ 10.3.3 — CELL-DR-02 is sequenced correctly but scoped as though P0-B had not happened.** Its
readiness clause says *"research-ready after P0-B"* — and P0-B is exactly what reveals that most of
its Required-output list already exists (§7). **Correction: the rescope in §7.2 must be applied
between P0-B and dispatch**, or the lane will be dispatched against a stale scope.

### 10.4 ✅ Sequencing v3 gets right, and should be credited

- **CELL-DR-01 first, as validation rather than a fresh novelty search** — corrects the SIHRE queue's
  worst error (DR01 first, already refuted).
- **DR08 closed by surfacing a file, not by research** — corrects "the cheapest item sequenced last".
- **Link semantics promoted to lane 02** — corrects its absence from every prior queue.
- **RB `NOT_RESEARCH` items converted to project tickets** — corrects work items sitting in a
  research queue where they can be dispatched by accident.
- **Product surfaces demoted to a local audit** — better than the Phase 1 delta's own Tier 1.6.

---

## 11. ⛔ Corrections to previously published Phase 1 findings

Per the standing rule that correcting an inherited premise is a deliverable, and must be fixed
wherever it was published.

### 11.1 ⭐ Every RB cross-reference in the Phase 1 documents points at the wrong row

`docs/research/backlog.yaml` does **not** number its 26 missions `RB-01…RB-26`. It numbers them
**`RB-00A…RB-00F` then `RB-01…RB-20`**.

```bash
python -c "import yaml; d=yaml.safe_load(open('docs/research/backlog.yaml',encoding='utf-8')); \
print([m['research_id'] for m in d['missions']])"
# ['RB-00A','RB-00B','RB-00C','RB-00D','RB-00E','RB-00F','RB-01',...,'RB-20']   # 26 items
```

`DESIGN_DELTA_SINCE_SIHRE_QUEUE.md`, `07_RESEARCH_STATUS_AUDIT.md` and the v3 ingest instruction all
cite the range "RB-01–RB-26" and reference rows **by position**, which silently shifts every citation
by six:

| Cited as | Actually is | The row that ID really names |
|---|---|---|
| "RB-17 — error correlation between agent configurations" | **RB-11** | *A crosswalk for the six evidence vocabularies* |
| "RB-12 — which agent-configuration parameters actually change outcomes" | **RB-06** | *Credit assignment across a team* |
| "RB-09 — the store-capability half" | **RB-03** | *An evaluation protocol for organizational and agent-team designs* |
| "RB-15 — ablation" | **RB-09** | *Rank ladder versus absence table* |
| "the six NOT_RESEARCH rows, RB-01…RB-06" | **RB-00A…RB-00F** | RB-01…RB-06 are five prior-art/foundational lanes and one comparison lane |
| "RB-03 in the backlog" (one real agent run) | **RB-00C** | *What none of the existing knowledge stores can do* |

⛔ **Every one of those citations currently points a reader at a different research question than the
one intended**, and in each case the row actually named is a plausible-looking research item — so the
error does not announce itself. **Corrected in the revised `DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` §2,
§3 and §6, and in the mapping at §12 below.**

### 11.2 Two drifted counts

| Claim | Published as | Re-measured | Where to fix |
|---|---|---|---|
| Corpus index delta | 719 claimed vs **888** measured | 719 vs **898** | v3 §2; regenerate rather than restate |
| Overlapping modified files | **seventeen** | **eighteen** | v3 §5 Gate P0-D |

⭐ **Neither number should be restated by hand.** Both now carry their regeneration command (§2).

### 11.3 One wrong path in v3

`factory/forecast.py` does not exist (§2.1). `factory/projection.py` is the nearest match, unverified.

---

## 12. Old-to-v3 mapping — every prompt, with a required-vocabulary disposition

Vocabulary: `COMPLETED_REUSE` · `MERGED_INTO_V3` · `NARROW_FOLLOWUP` · `LOCAL_MEASUREMENT` ·
`IMPLEMENTATION_TICKET` · `DEFERRED_EXPERIMENT` · `SUPERSEDED` · `REJECTED`.

### 12.1 Repository SIHRE queue — DR01–DR08 (all `NOT_RUN`)

| Prompt | v3 destination | Disposition |
|---|---|---|
| DR01 Prior art and novelty | CELL-DR-01 (delta only) | **SUPERSEDED** — refuted on primary sources by Wave 0 |
| DR02 Cognitive portfolio theory | CELL-DR-05 | **MERGED_INTO_V3**; empirical half **DEFERRED_EXPERIMENT** (P0-E) |
| DR03 Recursive SIHRE / morphological cognition | CELL-DR-05 + CELL-DR-07 | **MERGED_INTO_V3** |
| DR04 Contextual trust / KG Mesh | CELL-DR-03 | **MERGED_INTO_V3** |
| DR05 Homeostasis / immunity / self-model | CELL-DR-04 + CELL-DR-05 | **MERGED_INTO_V3**; thresholds **DEFERRED_EXPERIMENT**. ⭐ Synthetic fault injection may proceed before a natural drift event |
| DR06 Evaluation and benchmarks | CELL-DR-04 / 06 / 09 | **MERGED_INTO_V3** |
| DR07 Cross-domain mechanism mining | CELL-DR-07 (analogy filter only) | **NARROW_FOLLOWUP** |
| DR08 Entity definition and naming | Gate P0-B | ⭐ **LOCAL_MEASUREMENT** — surface the ontology; not research |

### 12.2 Executed lane programme — R1–R19 + R06B

| Lane | Disposition |
|---|---|
| R1–R8, R10–R19 (18 answered; R4 and R13 ran twice, deliberately) | **COMPLETED_REUSE** — attach as prior evidence; do not re-ask |
| R9 | ⚠ **does not exist and never did** — numbering gap, recorded so nobody hunts for it |
| **R06B** Collective cognition and knowledge architecture | **MERGED_INTO_V3** → CELL-DR-03. The programme's only orphan prompt |

### 12.3 Candidate backlog — `RB-00A…RB-00F`, `RB-01…RB-20` (correct IDs)

| ID | Title | v3 destination | Disposition |
|---|---|---|---|
| RB-00A | Convert the two `.docx` and index them | Gate P0-B | **LOCAL_MEASUREMENT** ⭐ *now larger — 4 unreadable binaries* |
| RB-00B | Score a second real connector end to end | — | **IMPLEMENTATION_TICKET** |
| RB-00C | **Complete one real agent run** | **Gate P0-E** | ⭐ **LOCAL_MEASUREMENT — the binding constraint** |
| RB-00D | Settle two tenancy questions with the client | — | **IMPLEMENTATION_TICKET** |
| RB-00E | Enumerate the knowledge stores | CELL-DR-03 input | **LOCAL_MEASUREMENT** |
| RB-00F | Disposition every open absorption row | — | **IMPLEMENTATION_TICKET** |
| RB-01 | What organisation-oriented MAS already provides | CELL-DR-01 | **SUPERSEDED** — Wave 0 answered it |
| RB-02 | Observability and trace standards for agent runs | ⛔ none | **NARROW_FOLLOWUP** — missing topic §10.1 |
| RB-03 | What none of the existing knowledge stores can do | CELL-DR-03 | **MERGED_INTO_V3** |
| RB-04 | Topology-task fit | CELL-DR-07 | **MERGED_INTO_V3** |
| RB-05 | Compensation and rollback semantics | CELL-DR-04 | **MERGED_INTO_V3** |
| RB-06 | Which config parameters actually change outcomes | CELL-DR-06 | **MERGED_INTO_V3**; empirical half **DEFERRED_EXPERIMENT** |
| RB-07 | Which health metrics predict mission outcome | CELL-DR-04 | **MERGED_INTO_V3**; validation **DEFERRED_EXPERIMENT** |
| RB-08 | What container isolation does not defend against | ⛔ none | **NARROW_FOLLOWUP** — missing topic §10.1 |
| RB-09 | Evaluation protocol for org and team designs | CELL-DR-06 | **MERGED_INTO_V3** |
| RB-10 | Near-miss capture in high-reliability organisations | CELL-DR-07 (weakly) | **NARROW_FOLLOWUP** |
| RB-11 | **Error correlation between agent configurations** | CELL-DR-05 | **MERGED_INTO_V3**; empirical half **DEFERRED_EXPERIMENT** ⭐ *the twin of DR02* |
| RB-12 | Credit assignment across a team | CELL-DR-06 | **MERGED_INTO_V3** |
| RB-13 | Audit this repository against RB-01/RB-02 findings | — | **LOCAL_MEASUREMENT** |
| RB-14 | Does APPROVE leave the building? | — | **LOCAL_MEASUREMENT** |
| RB-15 | Rank ladder versus absence table | — | **LOCAL_MEASUREMENT** |
| RB-16 | Four planes versus five layers | CELL-DR-01 | **MERGED_INTO_V3** |
| RB-17 | Crosswalk for the six evidence vocabularies | — | **IMPLEMENTATION_TICKET** |
| RB-18 | Mid-run human approval and escalation | CELL-DR-04 + CELL-DR-05 | **MERGED_INTO_V3** |
| RB-19 | Task and environment packaging standards | ⛔ none | **NARROW_FOLLOWUP** |
| RB-20 | Interop — MCP, A2A, AGNTCY | CELL-DR-02 (partial) | **NARROW_FOLLOWUP** — v3 covers protocol *comparison*, not the adoption decision |

### 12.4 Legacy twenty-report SIHRE queue

| # | Report | v3 destination | Disposition |
|---:|---|---|---|
| 1 | SIHRE × CELL OS canonical crosswalk | CELL-DR-01 | **MERGED_INTO_V3** |
| 2 | SIHRE prior art and novelty | CELL-DR-01 | **SUPERSEDED** |
| 3 | **SIHRE failure modes and complexity audit** | ⛔ none | ⭐ **NARROW_FOLLOWUP** — missing topic §10.1 #1 |
| 4 | SIHRE-guided hybrid optimization | CELL-DR-06 | **MERGED_INTO_V3** |
| 5 | Mixed-variable Configuration Genome optimization | CELL-DR-06 | **MERGED_INTO_V3** |
| 6 | Cognitive portfolio optimization and correlated failure | CELL-DR-05 | **MERGED_INTO_V3**; empirical **DEFERRED_EXPERIMENT** |
| 7 | Mesh Gradient, interaction effects, causal contribution | CELL-DR-06 | **MERGED_INTO_V3** |
| 8 | Optimization acceleration and search efficiency | CELL-DR-06 | **MERGED_INTO_V3** |
| 9 | SIHRE cognitive kernel for Operative Cells | CELL-DR-04 + CELL-DR-05 | **MERGED_INTO_V3** |
| 10 | Dynamic cognitive topology / morphological cognition | CELL-DR-05 | **MERGED_INTO_V3** |
| 11 | Contextual trust, regime inference, non-stationarity | CELL-DR-05 | **MERGED_INTO_V3** |
| 12 | Value of Information and selective verification | CELL-DR-05 | **MERGED_INTO_V3** |
| 13 | Operative homeostasis, cognitive immunity, recovery | CELL-DR-04 | **MERGED_INTO_V3**; thresholds **DEFERRED_EXPERIMENT** |
| 14 | Capability & Evidence Graph / transactive memory | CELL-DR-03 | **MERGED_INTO_V3** |
| 15 | Recursive SIHRE across Operative and MESH layers | CELL-DR-07 | **MERGED_INTO_V3** |
| 16 | Calculus × topology for adaptive Mesh optimization | ⛔ none | **DEFERRED_EXPERIMENT** — the legacy file itself defers it |
| 17 | Discover & Invent protocol | CELL-DR-07 (Foundry) | **MERGED_INTO_V3** |
| 18 | NeuroFusion-13 as a SIHRE case study | CELL-DR-09 follow-on | **DEFERRED_EXPERIMENT** — offline/replay only |
| 19 | **Operative Performance & Capability Lab** | fragments in CELL-DR-04/06 | ⭐ **NARROW_FOLLOWUP** — missing topic §10.1 #4 |
| 20 | Final CELL OS adaptive intelligence architecture | CELL-DR-10 | **MERGED_INTO_V3** |

### 12.5 v2 manifest lanes

| v2 | v3 destination | Disposition |
|---|---|---|
| P0 preflight | Gates P0-A…P0-D | **MERGED_INTO_V3** — ⭐ *this addendum is its P0-A execution* |
| Lane 01 Canonical crosswalk | CELL-DR-01 | **MERGED_INTO_V3** |
| **Lane 02 Prior art, novelty, failure modes, complexity budget** | CELL-DR-01 (prior-art half only) | ⛔ **MERGED_INTO_V3 (PARTIAL)** — FMEA and complexity budget **dropped**; see §10.1 #1 |
| Lane 03 Operative layered model / lifecycle / genesis | CELL-DR-04 | **MERGED_INTO_V3** |
| Lane 04 HyperMESH substrate | CELL-DR-03 | **MERGED_INTO_V3** |
| Lane 05 SIHRE cognition | CELL-DR-05 | **MERGED_INTO_V3** — ⭐ *sole source of the SIHRE expansion, §6.4* |
| Lane 06 CELL ADAPT optimization | CELL-DR-06 | **MERGED_INTO_V3** |
| Lane 07 Meshes / Foundry / MESA | CELL-DR-07 | ⚠ **MERGED_INTO_V3 (PARTIAL)** — Stigmergic Fields, Global Workspace, Temporal Echelons, Evolution Chamber dropped |
| Lane 08 Domain Genome / Fabric / quant data | CELL-DR-08 | **MERGED_INTO_V3** |
| Lane 09 CELL-Q research foundry | CELL-DR-09 | **MERGED_INTO_V3** |
| Lane 10 MESA final synthesis | CELL-DR-10 | **MERGED_INTO_V3** |
| **v2 as a whole** | — | **SUPERSEDED** by v3 as the forward queue; retained as historical evidence |

### 12.6 Inbound pack prompts — 38 files

Unchanged from `07_RESEARCH_STATUS_AUDIT.md` §5: **`STATUS_UNKNOWN`, deduplicated.** They arrived
pre-authored and this repository holds no record of whether they were run before import. ⛔
`STATUS_UNKNOWN` is not `NOT_RUN`. Several are byte-identical duplicates (DC-06, DC-09) and a registry
counting 38 distinct prompts would overcount.

---

## 13. Write-boundary compliance

The instruction requires six outputs and forbids silently violating the Phase 1 write boundary. The
current Phase 1 protocol is **read-only with respect to existing content**; new Phase 1 analysis
lives in `docs/restructure/` and `docs/research/`. All Phase 1 documents are **untracked** —
`git ls-files --error-unmatch` returns "did not match any file(s) known to git" for both
`docs/restructure/01_REPOSITORY_AUDIT.md` and `docs/research/DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` — so
every write below is additive and reversible.

| Required output | Written to | Eventual destination |
|---|---|---|
| Revised design delta | `docs/research/DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` — **revised in place** | same (already a Phase 1 deliverable) |
| v3 reconciliation | `docs/restructure/09_RESEARCH_MANIFEST_V3_RECONCILIATION.md` (this file) | `docs/research/RESEARCH_MANIFEST_V3_RECONCILIATION.md` |
| Proposed research registry | `docs/restructure/10_PROPOSED_research_registry.yaml` | `docs/_index/research_registry.yaml` |
| Proposed research status | `docs/restructure/11_PROPOSED_research_status.md` | `docs/_index/research_status.md` |
| Next research run | `docs/restructure/12_NEXT_RESEARCH_RUN.md` | `docs/research/NEXT_RESEARCH_RUN.md` |
| v3 activation decision | `docs/restructure/13_V3_ACTIVATION_DECISION.md` | `docs/research/V3_ACTIVATION_DECISION.md` |
| Source intake (Gate P0-A) | `docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack/` — extracted, hashes verified | same |

⛔ **`docs/_index/` was deliberately not written to.** Those files carry regeneration commands and are
asserted current by tests; a hand-authored registry dropped in beside them would be the
hand-maintained-count failure this corpus has already suffered twice. **The registry proposal is a
proposal until a generator exists** (`07_RESEARCH_STATUS_AUDIT.md` §6 specifies the hybrid
generated/authored split).

---

## 14. Method and limits

**Measured this pass:** SHA-256 of the pack and all four sources, inside the archive and after
extraction; `git rev-parse`, worktree list, modified-file count; 68 modules / 23,939 lines; 10 run
rows; corpus index delta by the manifest's own command (898 vs 719 claimed); a 56-term census over
998 text files with `docs/restructure/` and the Phase 1 delta excluded; existence check on all seven
v3-named code anchors; `factory/blueprint.py` class names; the correct `research_id` values in
`backlog.yaml`; the v0.1 `.docx` cross-reference audit grepped for 14 concept families; archive
namelist scans for NERVE and Switchboard research; three CELL-Q boundary statements in v3.

**Read in full:** v3, v2, the legacy twenty-report queue, the ingest instruction,
`DESIGN_DELTA_SINCE_SIHRE_QUEUE.md`, `07_RESEARCH_STATUS_AUDIT.md`,
`CELL_OS_Canonical_Terminology_vNext.md` and `KNOWN_TERMINOLOGY_COLLISIONS.md` (read-only from the
archive, nothing extracted).

**Not read, and therefore a stated limit:**
- the four CELL OS binaries (669 KB) — §5.2's thirteen `ABSENT` verdicts are **corroborated, not
  proved**, until Gate P0-B converts them;
- `DEEP_RESEARCH_REPORT.md` and the Switchboard UI/UX report inside their archives — §8's
  "only integration gaps remain" is therefore **unverifiable**, not refuted;
- the test suite — the AMBER baseline is **inherited, not re-measured** (§2.2).

**Not attempted:** any research dispatch, any external search, any Phase 2 migration, any move or
deletion of a tracked file, any write to `docs/_index/`, any promotion to canonical.

⚠ **One instrument note carried forward, and one added.** On the first Phase 1 run the census
included `docs/restructure/` and returned non-zero counts for five concepts, **every hit being that
pass's own writing from an hour earlier**. This pass excludes `docs/restructure/`,
`DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` **and the intake directory** — the three ingested manifests are
the source of the vocabulary being censused, and counting them would report the proposal as evidence
of the repository's design state. **The census was run before extraction (998 files) and re-runs to
the same 998 files and the same figures after it**, which is the check that the exclusion is
correct rather than merely convenient. Any future census must extend the exclusion to this document.

📝 **Skill gap:** nothing in the repository's tooling enforces "a census must exclude the pass's own
output and its own sources." It has now been got wrong once and got right twice by hand.
