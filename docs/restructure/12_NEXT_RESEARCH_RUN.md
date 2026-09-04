# NEXT_RESEARCH_RUN

⛔ **Nothing has been dispatched. This file names the next action; it does not take it.**

**Eventual destination:** `docs/research/NEXT_RESEARCH_RUN.md`.
**Phase 1, post-P0-B.** Measured 2026-09-03 against `agent-factory` @ `827f871` (`main`).
**⭐ Rewritten after Gate P0-B completed** — record:
[`14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md`](14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md).

---

## ⭐ The next action

> ## **Approve the ten terminology decisions in `14` §7. Then dispatch CELL-DR-01.**

**The blocker is no longer a missing file. It is a decision only a human can take.**

Gate P0-B surfaced the canon, and the canon **disagrees with itself** in ways a research service
cannot resolve and must not be asked to guess at:

| The decision that most blocks CELL-DR-01 | Why it cannot be researched |
|---|---|
| ⭐ **TD-1 — Cell Mesh: team topology or OS federation?** | Two surfaced canonical sources **directly contradict each other**. The ontology says *"a Cell Mesh is **not** OS federation"*; v0.1 §5 is titled *"CELL Mesh — **Federation of CELL OS Nodes**"* |
| **TD-8 — Operative Kernel or CELL Kernel?** | `Operative Kernel` = **0** in every canonical source. **CELL-DR-04 is built around a term nothing defines**, and the canonical `CELL Kernel` may be a different thing entirely |
| **TD-3 — C-MESH / T-MESH / OS-MESH** | **0 in every canonical source.** A lane asked to distinguish three undefined concepts will invent the distinction |
| **TD-9 — Organism or Organization?** | Two design documents say one; the ontology hierarchy says the other. A genuine tie |

⚠ **Dispatching CELL-DR-01 before these are settled buys a research pass that will re-derive the
contradiction and hand it back.** The decisions cost minutes; the lane costs a full pass.

---

## The ordered queue

### Wave Local-0 — not research

| # | Action | Gate | Status |
|---|---|---|---|
| ~~L0.1~~ | ~~Surface the canonical ontology~~ | P0-B | ⭐ **DONE** — 3-way hash match |
| ~~L0.2~~ | ~~Convert the two `.docx`~~ | P0-B | ⭐ **DONE** — 100% body coverage measured |
| ~~L0.3~~ | ~~Decide `.xlsx` / `.pdf` handling~~ | P0-B | ⭐ **DONE** — both read. ⛔ Decision D-5 was wrong; `pdftotext`, `fitz`, `pdfminer` all present |
| **L0.4** | Surface the 4 NERVE / Switchboard design-research artifacts | P0-B | ⛔ **OPEN** — the one P0-B task not attempted |
| **L0.5** | ⭐ **Complete one real, non-dry-run agent run** | **P0-E** | ⛔ **OPEN — the binding constraint on everything empirical** |
| **L0.6** | Run the corpus index delta; add the CELL OS records | P0-C | ⛔ **OPEN and widened — 719 claimed vs 916 measured, delta 197** |
| **L0.7** | Resolve the worktree decision; protect the 18 modified files; re-measure the AMBER baseline | P0-D | ⛔ **OPEN** |
| **L0.8** | Give `RB-00A…RB-00F` tracker dispositions | — | ⛔ OPEN |
| **L0.9** | Write the approved **Domain design record** | — | ⛔ OPEN — the only thing that can unblock CELL-DR-08 |
| ⭐ **L0.10** | **Approve the ten terminology decisions** (`14` §7) | — | ⛔ **OPEN — now the top of the queue** |

⚠ **L0.6 note, and it is not a defect:** P0-C's gap **grew** from 179 to 197 because P0-B surfaced
files. Surfacing canon adds unindexed files by construction. Run the index delta *after* L0.4, not
before.

### Wave A — the first research dispatch

| Lane | Condition | Status |
|---|---|---|
| **CELL-DR-01** | L0.10 (terminology decisions) | ⭐ **RESEARCH_READY** — see below |

⚠ **P0-C and P0-D remain open and do not block it.** v3 §7 made CELL-DR-01 *"research-ready after
P0-A through P0-C"*. **P0-C is assessed as non-binding for the research axis** — it concerns index
hygiene, not the questions this lane asks or the evidence it reads. Recorded rather than silently
dropped.

### Wave B and beyond

| Wave | Lanes | Condition |
|---|---|---|
| B | **CELL-DR-02** (⛔ **rescoped spec only — `16`**) and CELL-DR-03 | after A |
| C | CELL-DR-04 | after A and B — ⛔ **resolve TD-8 first** |
| D | CELL-DR-05, CELL-DR-06 | after C — **research axes only** |
| E | CELL-DR-07 | after D and CELL-DR-02 — ⛔ **resolve TD-3 first** |
| Local | Write the Domain design record | ⛔ required before F |
| F · G | CELL-DR-08 · CELL-DR-09 | in order |
| Final | CELL-DR-10 | after all accepted reports |

⛔ **P0-E belongs in Local-0, not after Wave G** (errata E-05, E-06).

---

## Exact attachment manifest for CELL-DR-01

⭐ **Every path below was verified to exist at the time of writing.** The two entries that were
placeholders in the previous version are now real files.

### Canonical sources — surfaced by Gate P0-B
| Path | SHA-256 | Note |
|---|---|---|
| `docs/raw_research/CELL_OS_Frontier_Audit_Research_Pack/01_CANONICAL_ONTOLOGY/CELL_OS_Canonical_Terminology_vNext.md` | `dfebc108…3222a95` | ⭐ 3-way verified |
| `docs/raw_research/CELL_OS_Frontier_Audit_Research_Pack/01_CANONICAL_ONTOLOGY/KNOWN_TERMINOLOGY_COLLISIONS.md` | `e0a81e3c…0622380b` | ⭐ 3-way verified |
| `docs/raw_research/converted/CELL_OS_Product_Technical_Design_v0.1.md` | *(derived)* | from `.docx` `30131d25…40ee3713`, 100% body coverage |
| `docs/raw_research/converted/CELL_OS_Master_Research_Design_Development_Operations_User_Guide_v0.2.md` | *(derived)* | from `.docx` `724cb7db…0ab071f0`, 100% body coverage |
| `docs/raw_research/converted/CELL_OS_Design_Master_Brief.txt` | *(derived)* | ⚠ a **design brief prompt**, not a specification |
| `docs/raw_research/CELL_OS_Product_Technical_Design_v0.1_Crossreference_Audit_v1.md` | — | the independent audit of the v0.1 |

### The forward queue and its history
- `docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack/CELL_OS_Deep_Research_Manifest_v3.md` — `bef3b644…`
  ⛔ **must be read together with `15_V3_ERRATA_OVERLAY.md`**
- `…/CELL_OS_Optimized_Deep_Research_Prompt_Manifest_v2.md` — `bc111d5d…`
- `…/SIHRE_Recommended_Deep_Research_Report_Queue_Legacy.md` — `6d142560…`

### Phase 1 measurements
- ⭐ `docs/restructure/14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md` — **the reconciliation and the ten decisions**
- ⭐ `docs/restructure/15_V3_ERRATA_OVERLAY.md` — **twelve errata; apply before using v3**
- `docs/restructure/09_RESEARCH_MANIFEST_V3_RECONCILIATION.md` — ⚠ §5.2, §6.2 and §7.2 revised by `14` and `15`
- `docs/restructure/01_REPOSITORY_AUDIT.md`, `04_PROPOSED_TARGET_STRUCTURE.md`, `06_TERMINOLOGY_SUPERSESSION.md`, `07_RESEARCH_STATUS_AUDIT.md`
- `docs/research/DESIGN_DELTA_SINCE_SIHRE_QUEUE.md` (revised)
- `docs/_index/current_vs_proposed.md`, `concept_index.yaml`, `contradictions.md`, `duplicate_clusters.md`, `supersession_candidates.md`, `repo_snapshot.md`

### Completed research to reuse, not re-ask
- `docs/research/SYNTHESIS.md` · `docs/research/answers/` (18 lanes)
- `docs/research/agent-factory-concept-inventory.md` §3 — ⭐ the do-not-re-ask list
- `docs/research/backlog.yaml` — ⚠ **cite by `research_id`, never by position**
- ⭐ `.agent-platform/RECONCILIATION.md` §1.1 — the organizational-compiler refutation, **an input**

### Code anchors — the implementation, not a description of it
`factory/contract.py` (dependency centre) · `factory/blueprint.py` (⭐ exposes **`TeamSpec`** /
**`AgentSpec`** — 70 occurrences in `factory/`+`tests/`, and **zero** in any design document) ·
`factory/evals.py` · `factory/calibration.py` · `factory/readiness.py` · `factory/roadmap.py` ·
`factory/projection.py` ⚠ *(nearest candidate for v3's non-existent `forecast.py`; **role
unverified** — do not present it as an equivalent)*

### Instructions to carry with the attachment set
1. **Validate; do not repeat the completed broad novelty search.**
2. ⛔ **Never infer implementation from documentation.** **Zero CELL OS architectural concepts exist
   in `factory/` or `tests/`.** The only implemented entities in the terminology family are
   `TeamSpec` and `AgentSpec`.
3. **Report the four readiness axes separately.**
4. **Distinguish novelty of a primitive from novelty of a combination, implementation
   differentiation and practical utility.**
5. ⭐ **Three object models exist and none is identical** (`14` §6.1.2). Reconcile them; do not pick
   one silently.
6. **The Blueprint family has five names** (`14` §6, TD-7). Do not add a sixth.
7. **`PARTIAL`, not `PROVEN`, for the evaluation architecture.**

---

## What must NOT be dispatched

| | Why |
|---|---|
| ⛔ **The v3 original CELL-DR-02** | Superseded by `16_CELL_DR_02_RESCOPED_SPEC.md`. The original re-derives a vocabulary we own |
| **CELL-DR-04, before TD-8** | It is built around `Operative Kernel` — **0 occurrences in every canonical source** |
| **CELL-DR-07, before TD-3** | C-MESH / T-MESH / OS-MESH are defined nowhere |
| **Repository DR01 / v2 Lane 02's prior-art half** | Already refuted — `arXiv:2602.13275`, `arXiv:2607.25446` |
| **A broad NERVE research lane** | v3 §8 is right — a local integration-gap audit, after L0.4 |
| **CELL-DR-08** | The Domain design record it researches against does not exist |
| **Any empirical branch of CELL-DR-05/06/07** | 10 runs, 0 PASS, 7/7 dry-run |
| **The legacy twenty-report queue as a batch** | Its own header forbids it |
| **`RB-00A…RB-00F`** | ⭐ Work items, not research |

---

## Status

    NOT-DISPATCHED
    Gates P0-A, P0-B: COMPLETE
    Gates P0-C, P0-D, P0-E: OPEN  (none blocks CELL-DR-01's research axis)
    CELL-DR-01: RESEARCH_READY, pending approval of the ten terminology decisions
    CELL-DR-02: RESEARCH_READY on the rescoped spec only
    Next action: L0.10 — approve the ten terminology decisions in 14 §7. No dispatch.
