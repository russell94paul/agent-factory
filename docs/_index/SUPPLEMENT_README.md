# SUPPLEMENT_README — architecture-review supplement, 2026-09-02

**For the external reviewer consolidating the Agent Factory architecture.**

This is a **narrow continuation** of the corpus-preparation pass of 2026-09-02. That pass produced
`docs/_index/` and shipped with two stated coverage holes. This one closes the first completely and
the architecture-relevant half of the second. **It resolves nothing, dispatches nothing, builds
nothing, and proposes no architecture.**

| | |
|---|---|
| `agent-factory` | `fc78074` (`main`), working tree dirty |
| `agent-army-research` (sibling) | `11c5b3d` (`main`) |
| Pass type | supplementary coverage — GAP-01, the architecture half of GAP-03, and one prior-art check |
| Dispatched | **nothing** |
| Resolved | **nothing** |

---

## 1. Newly covered — what was unavailable to the previous pass

### 1.1 Two documents, 635 KB, previously unreadable

The previous pass could not open `.docx`. Both are now converted, **read in full**, and indexed.

```
docs/raw_research/Beyond_Agent_Armies_Frontier_Architectures.docx               430,863 B  (preserved)
docs/raw_research/Agent_Factory_Frontier_Architecture_Prioritization_Pack.docx  203,671 B  (preserved)
                    ↓  scripts/docx_to_md.py  (python-docx is NOT installed; parses word/document.xml)
docs/raw_research/converted/Beyond_Agent_Armies_Frontier_Architectures.md        46,047 chars
docs/raw_research/converted/Agent_Factory_Frontier_Architecture_Prioritization_Pack.md  42,261 chars
```

**Extraction was verified, not assumed** — raw `<w:t>` characters against markdown stripped of
syntax: 38,548 → 38,251 and 32,732 → 32,519, i.e. **100.1% coverage** (the excess is hyperlink
targets the markdown adds). ⚠ **Twelve embedded figures were not extracted**; all twelve captions
survive.

**What they contain:** an eight-level organizational ladder (L1 Agent … L8 Agentic Civilization) with
an explicit refusal to make L4–L8 mandatory; **twelve architecture cards**, each with a *main failure
mode* and a *smallest useful experiment*; twelve novelty hypotheses framed for prior-art attack; a
mission-signature → topology table; a weighted P0/P1/P2/P3-Lab prioritisation with a stated method;
promotion gates G0–G7; ten experiments ranked by information gain; and a client-facing **Mission
Assurance Receipt**.

### 1.2 The sibling repository's Wave 0 — previously unindexed

Read in full: the Wave 0 synthesis, the hypothesis ledger, the research manifest, the core ontology,
the foundational laws, the product boundary, `R31`, and **8 of the 13** `architecture/*.md` stubs.
Extracted from the large answers: `R01`'s 15-concept novelty-risk map and its terminology table.
**24 findings, tagged and traced to `file:line`, in `agent_army_wave0_supplement.md` Part 2.**
⛔ **5 architecture stubs were not opened**, and one of them matters: `06-knowledge-evidence-model.md`
is named by `PRODUCT-BOUNDARY.md` as the **highest-priority convergence risk** between the two
repositories' evidence schemas.

⚠ **A correction to GAP-03's own figure.** It said the sibling was *"155 markdown files, 3.6 MB"*.
The file count is right; the byte figure is **not reproducible from any basis** — the markdown corpus
is **881 KB** (working tree 1.88 MB; 2.47 MB including `.git`). That matters because the figure was
used to argue the sibling was too large to index.

### 1.3 The single most important thing the previous pass could not know

⭐ **The two frontier documents do not cite the sibling repository, the Wave 0 synthesis, or
`RECONCILIATION.md`.** Their only internal input is `Agent Factory Vision.txt` — the file that exists
in **six byte-identical copies** in this corpus. Both are dated **2026-09-01**; Wave 0 falsified their
founding premise on **2026-08-30**.

**They are not a second opinion on Wave 0. They are a more elaborate development of the premise Wave 0
refuted, written without knowledge of the refutation.** Everything else in this README follows from
that.

---

## 2. Contradiction changes

**28 → 29.** One added, one amended, **none resolved, split, merged or removed.**

### CN-29 — ADDED, `⛔ BLOCKING`

> **Is an organizational design a durable asset, or does it expire with the model binding?**

**Side A** (the Prioritization Pack): twelve architectures each get **one** planning-value score, with
no model dimension among its seven weighted criteria; Phase F proposes org-genome search whose output
is certified presets, described as a *"potential long-term moat"*.

**Side B** (Wave 0, from the IMACS ablation, `arXiv:2607.25446`): four ontology terms are
**configurational** and must carry a model `binding`, because *"the winning placement flips across
model families."* The hypothesis ledger records `H07` as **SUPPORTED with a sting** — *"every learned
result is model-binding-specific and expires with the binding"* — and `H09` as **SUPPORTED**.

**Why BLOCKING.** It does not argue against building any of the twelve. It argues that **Phase F's
output has a shelf life nobody has measured**, that a quality-diversity archive may be curating
already-expired elites, and that **re-validation cadence is a prerequisite of the archive rather than
a follow-up to it**. Note that this estate's own `C-AG-01` — *the configuration IS the version* —
already implies the model is part of the configuration, so **the vocabulary is on Side B while the
inbound roadmap is on Side A**.

**What would settle it:** experiment **E3**, already written and unrun, in the sibling's Wave 0
synthesis. ⚠ Blocked behind `GAP-09` — no agent has completed a real run, so there is no winner to
flip.

### CN-01 — AMENDED, balance UNCHANGED, and the reason is stated

Two newly-read documents argue CN-01's Side A at length and **do not move it**:

1. **They add volume, not evidence** (see §1.3). `C-RS-06` governs — a more elaborate statement of an
   unevidenced position is still unevidenced.
2. **Side A is now better characterised**, which is a real gain: a synthesis can engage with a
   specific twelve-card proposal rather than a direction.
3. ⭐ **The new fact is that the two sides agree on what to do next.** Wave 0's conclusion —
   *"every surviving column entry is about evidence, verification or governance; not one is about
   organizational structure"* — matches **four of the Pack's five P0 items** (constitutional type
   system = governance; shadow twin = verification; bounded reconciliation = governance; global
   workspace = evidence). Only the mission hypergraph is structural. The two also produce **the same
   promotion-gate chain**, independently.
4. ⚠ **Do not upgrade that to corroboration.** Both are model-generated over overlapping training
   distributions. What is independent is the *input corpus*, not the reasoner. Basis: `DERIVED`.

**Net: still OPEN, Side B still stronger, remainder still needs GAP-02.** What narrowed is the
*practical* disagreement — **both sides now say build the mechanism and do not claim the category.**

### Unresolved, and worth the reviewer's attention

The other **27 are untouched**. Two of them acquired supporting material without changing:
**CN-20** (which figure supports the multi-agent decision) gains Wave 0's finding that the −3.5%
figure carries a 95% CI of **[−18.6%, +25.7%]**, **σ = 45.2%**, and a peer-reviewed title arguing
capability saturation. **CN-06 / CN-08** (evidence-vocabulary collisions) gain a candidate answer the
`agent-factory` indexes did not know existed — see §4.

---

## 3. Concept changes

**86 → 92 concepts.** Six added, one materially reinterpreted, one re-scoped.

| ID | Concept | Status | Why it matters here |
|---|---|---|---|
| `C-OR-06` | **Mission hypergraph** — typed mission graph | **PARTIAL, already** | `board.py:108` computes a critical path over 30 gates and 11 declared edges (live output: **2 hops**); `F98` records **25 live block edges** at ticket scale. The Pack ranks this **P0 #1 at Effort 3/5 as though greenfield** |
| `C-OR-07` | **Constitutional type system** — organizations that fail to compile | NOT_IMPLEMENTED | ⛔ Blocked behind the sibling's open question: *is there any boundary that can actually enforce authority?* |
| `C-OR-08` | **Quality-diversity organization archive** | NOT_IMPLEMENTED | ⛔ Two blockers: the simulation substrate is measured `ABSENT` everywhere, and **CN-29** |
| `C-KN-07` | **Knowledge metabolism** — decay, contradiction load, forgetting | NOT_IMPLEMENTED | The only place in the corpus treating knowledge as having a **maintenance cost**. ⚠ Stated in terms of `Claim`, a noun Wave 0 deprecated |
| `C-GV-06` | **Mission Assurance Receipt** | **PARTIAL, already** | ⭐ **The highest value-to-machinery ratio recovered.** Every one of its nine sections has a producer in `factory/`. *"The record is a join, not a new subsystem."* → `HL-15` |
| `C-TM-06` | **Goal-aware adaptive/dynamic orchestration** | **PARTIAL, already** | Recorded **before** any design work so the prior art and the `T∞` bound are on file first. See §5 |

**Materially reinterpreted:**

- **`C-OR-04`** (higher-order structures) — raised `idea → designed`. Its blocking note (*"the most
  relevant source HAS NOT BEEN READ"*) is replaced by the content: the L1–L8 ladder and twelve cards.
  Three counter-arguments are now attached to it, all previously unstated: Wave 0's `DO NOT BUILD` on
  supervisor tiers; the CRITICAL prior-art risk on every non-hierarchical mechanism in the catalog;
  and — for stigmergic fields specifically — R01's *"what survives as ours"* column reading
  **"Nothing at the mechanism level."**
- **`C-EV-10`** (`Counterfactual`) — ⚠ **flagged as NOT the same object as the Shadow Twin**, and a
  synthesis must not conflate them. `factory/assertions.py`'s `Counterfactual` has no `status` field
  and is deliberately un-renderable beside a real outcome — a *documentation* object. The Shadow Twin
  is a *runtime* organization.

⭐ **The distribution finding.** `concept_index.yaml`'s own summary says almost everything arriving
from an inbound pack is `NOT_IMPLEMENTED`. **Three of these six are `PARTIAL`** — the mechanisms are
already here and the source documents propose them as new P0 substrate. **That is the opposite of the
pattern, and it means the frontier documents' effort estimates are wrong in this estate rather than
their direction.**

---

## 4. Research changes — 26 missions, assessed, NONE dispatched

Recorded in full at `docs/research/backlog.yaml` → `supplementary_assessment_2026_09_02`. **No
`priority:` field was edited**; that block is an argument for a human, not a change.

| | Mission | Assessment |
|---|---|---|
| ✅ **Done** | `RB-00A` | Converted, read, indexed. Its `unblocks: [RB-01, RB-02, RB-05]` is satisfied |
| ⬆ **Rise** | `RB-01` — what organisation-oriented MAS provides | Now the top research-shaped mission. It gained a concrete target list: twelve architectures with prior-art anchors the documents themselves supply. **Add to scope: does IMACS's model-binding result generalise (CN-29)** — the highest-value external question now open |
| ⬆ **Rise** | `RB-09` — evaluation protocol for organizational designs | ⭐ **Argues for `CRITICAL`, and is currently `HIGH`.** Three things converged on it: two independently-written promotion-gate chains that **agree** (so RB-09 can adopt rather than derive); a ten-dimension evaluation framework with an explicit Pareto rule; and CN-29, which means any organizational evaluation must carry a model binding or it measures something with an unmeasured shelf life |
| ↔ **Rise in value, not priority** | `RB-04` — topology-task fit | Its **output shape** should change: the twelve cards plus the mission-signature table are most of the comparison harness it was going to invent. It should now **validate and correct an existing table**. ⛔ That table is model-generated and unevidenced — it is the hypothesis under test, never a source |
| ⬇ **Fall (relative only)** | `RB-02` — trace standards | Still the best-scoped mission. It falls only relative to RB-01 and RB-09, which acquired concrete targets this pass while RB-02 acquired none |
| 🔀 **Merge** | `RB-16` + the three-axis model | ⭐ Wave 0 promoted a **third and better-argued** decomposition this backlog does not know exists: **standing / basis / window** as three orthogonal axes, of which the nine existing vocabularies are different collapses — *"the most substantive original contribution of W0"*, and explicitly *descriptive of code that already exists* |
| ⚠ **May become `NOT_RESEARCH`** | `RB-17` — evidence-vocabulary crosswalk | **Conditional, and unverified.** If the sibling's 90 KB vocabulary crawl already contains the crosswalk — which the three-axis model implies but this pass did not check, having not read the file — then RB-17 is a **reading** task. ⭐ **Read the crawl first.** It is the same shape as `RB-00A`, and that paid |
| **Split** | — | none |
| **Remove** | — | none |
| ➕ **New candidate, not dispatched** | `RB-21` — do the twelve cards' failure modes occur here? | `LOW`, and **probably premature**: with zero completed runs there is no population in which a coordination pathology could be observed |

⭐ **Twenty of the twenty-six are unaffected by everything read this pass.** 635 KB of documents and a
sibling research programme moved the order of six missions and the priority of none. **The binding
constraint is unchanged: `RB-00C` / `GAP-09` — no agent has ever completed a real run.**

**Gaps: 42 → 43.** `GAP-01` **closed** (`LOW` residual on twelve un-extracted figures); `GAP-03`
downgraded `HIGH → MEDIUM` and its byte figure corrected; **`GAP-43` added** (`MEDIUM`) — see §5.

---

## 5. The new orchestration concept — checked, not designed

**Goal-Aware Adaptive/Dynamic Orchestration** was checked against both repositories for prior art.
**No novelty is claimed. Nothing was designed. Nothing was dispatched.** Full map:
`agent_army_wave0_supplement.md` Part 4.

**Result: thirteen of the fourteen named sub-ideas already exist here.**

⭐ **Four are running code, and this was measured, not read:**

| | Where |
|---|---|
| dynamic critical path | `factory/board.py:108 critical_path()`, rendered `roadmap.py:276`, drawn `flow.py:52` |
| adaptive task prioritization | `factory/coordination.py:100 prioritise()` — orders human interventions by transitive downstream-blocked count, critical-path membership, wait time and session liveness, and **renders its reasoning** |
| mutable DAG | `docs/findings.d/F98` — 25 live block edges on `.data/tasks.jsonl` |
| deadline-aware scheduling | `factory/schedule.py` — ⭐ **built as a refusal**: it declines to emit a completion date until scope velocity settles, because *"an ETA computed from pass-rate alone divides by a denominator that is still growing, and every such estimate flatters"* |

⛔ **Two hard constraints the reviewer must carry.**

1. **The scheduling half is already bounded by a proof this corpus holds.** `SYNTHESIS.md:1389`,
   Blumofe & Leiserson: *"every topology is a scheduler, schedulers redistribute `T₁/P`, **none touch
   the critical path `T∞`**"* — alongside the α(G) / Dilworth ceiling and *"concurrency comes from
   touching disjoint data, not from a better scheduler."*
   ⭐ **So the honest framing is not "a better scheduler". It is "a mechanism that mutates `T∞` by
   changing scope, evidence requirements or gates."** A design that does not say which side of that
   line it sits on cannot be evaluated.
2. **Wave 0's type argument forbids the obvious object.** Authority, budget and deadline are
   `Mandate`, not `Contract`: *"a GreenContract's fold is meaningful only because every member is
   falsifiable; adding permissions breaks the property the object exists for."*

**Exactly one member of the list has zero occurrences in either repository: *scope degradation as a
deadline approaches*.** The adjacent mechanisms all degrade on the wrong trigger — `admit() →
DEGRADED` on **missing capability**, `HorizonWorkItem.expiry` on **elapsed speculation**, and
`schedule.py` refuses to name a deadline at all.

⛔ **And the precondition is unmet.** `factory/schedule.py:26`: *"'Ahead or behind schedule' needs a
target, and there isn't one. **No deadline has been stated anywhere in the programme.**"*
**A deadline-aware orchestrator currently has no deadline to be aware of.** `schedule.py` already
accepts `--target YYYY-MM-DD`. **Stating a target is a one-line action and it is the precondition for
every part of GAP-43.**

---

## 6. Deadline impact

> **Does any newly recovered evidence materially alter these five immediate priorities?**

| | Priority | Verdict |
|---|---|---|
| 1 | **Marketing Model meeting-ready delivery** | ⛔ **NO. Explicitly no.** Nothing read this pass bears on it. Its open items are credential retrieval, warehouse-mode exercise and the PBI DAX instrument — all measurements against a live system, none of which any document here informs. **Proceed unchanged.** |
| 2 | **Switchboard mission execution vertical slice** | ⛔ **NO.** ⓘ **One optional, non-blocking note**: `C-OR-06` and `C-TM-06` record that `board.py:108`, `coordination.py:100` and `F98`'s 25 block edges already implement most of what the Pack calls P0 #1. That is an argument **for** the slice as scoped, not a change to it. Do not widen the slice on the strength of it. **Proceed unchanged.** |
| 3 | **Sales Model bounded changes** | ⛔ **NO.** Untouched by anything in this supplement. **Proceed unchanged.** |
| 4 | **Broader Agent Factory architecture** | ⚠ **YES, in three specific ways, none of which is a stop.** (a) **CN-29** — any roadmap phase producing certified organizational presets has an unmeasured shelf life; a synthesis should say so rather than discover it later. (b) **Effort re-costing** — three of the Pack's P0/near-P0 items are already partly built here, so its effort column is wrong in this estate. (c) **Terminology** — `SP-15`: seven headline names in the frontier documents are ones Wave 0 ruled against, including four hard collisions (**EOS®**, Doctrine PHP ORM, StarCraft, and Gartner's DTO Magic Quadrant, the last rated **BLOCKING**). Renaming is cheap; re-importing the collision is not. |
| 5 | **Research program** | ⚠ **YES, narrowly.** `RB-09` argues for `CRITICAL`; `RB-01` gained a target list and a new question; `RB-17` may not be research at all. ⭐ **But the program's binding constraint is unchanged** — `RB-00C` / `GAP-09`. Nothing recovered this pass changes it, and nothing in any corpus can. |

⭐ **Said plainly: the newly recovered evidence changes how the architecture should be described and
sequenced. It changes nothing about what to ship next.** Priorities 1–3 proceed exactly as planned.

---

## 7. Architecture-review warnings

**Seven things to understand before consolidating.**

1. ⛔ **The two frontier documents are not independent evidence for their own thesis.** Their sole
   internal input is a file that exists in six byte-identical copies, and they do not cite the
   research that refuted their premise two days earlier. Weigh them as **one well-argued proposal**,
   not as corroboration of the vision documents they restate.
2. ⭐ **But the convergence between them and Wave 0 is real and is the most decision-relevant fact
   here.** Four of five P0 items are exactly what Wave 0 says survives prior-art attack, and two
   independently-written promotion-gate chains agree. ⚠ Tier it `DERIVED`, medium confidence —
   independent *corpora*, not independent *reasoners* (`C-RS-06`).
3. ⛔ **CN-29 is the one new blocking disagreement, and it is about durability, not direction.** If
   organizational configuration is model-binding-specific, the roadmap's optimisation phases produce
   assets that expire. Do not resolve it by choosing a side — **E3 is written and unrun.**
4. ⚠ **The effort column is wrong in this estate.** Three items scored as greenfield are partly
   built. A synthesis that adopts the Pack's sequencing without re-costing will under-value work
   already done and over-cost work already started.
5. ⛔ **`Counterfactual` and Shadow Twin are different objects.** `factory/assertions.py`'s
   `Counterfactual` has no `status` field, deliberately, so it cannot be rendered beside a real
   outcome. Conflating them would put a documentation object on a runtime critical path.
6. ⛔ **Terminology carries costs the documents do not price.** Seven headline names are ones Wave 0
   ruled against, four of them hard collisions. **This is cheap to fix and expensive to publish.**
7. ⛔ **The evidence chain has a known weak link, and it is disclosed rather than hidden.** No arXiv
   id, DOI or standard cited by Wave 0 was verified **by this pass** — every one is tagged
   `PRIOR SYNTHESIS`, never `SOURCE FACT`-verified-here. Wave 0's own methodological finding is why:
   *"two WebFetch summaries were wrong in this wave, in opposite directions… **a fetch summary is a
   lead, not evidence.**"* If a load-bearing decision rests on IMACS or on the TTCN-3 lattice, **open
   the artefact.**

---

## 8. Coverage limitations of THIS pass

| | |
|---|---|
| ⛔ | **595 KB of the sibling's 881 KB of markdown was not read** — including the entire 90 KB vocabulary crawl and the 30 KB adversarial-refutation source, whose conclusions reached this pass only through the synthesis that quotes them. ⭐ **The crawl is now the highest-value unread thing in either repository**: it is the derivation of the three-axis model that would settle GAP-05 / CN-06 / RB-17. |
| ⛔ | **Twelve embedded figures were not extracted** from the two `.docx` (8 + 4). Captions survive. Opening them in Word is minutes of work. |
| ⛔ | **No citation was independently verified.** See warning 7. |
| ⛔ | **Nothing was re-measured in `corpus_manifest.yaml`.** No pre-existing `sha256` was recomputed; if a file changed on disk between the two passes, the manifest does not know it. |
| ⛔ | **Nothing was dispatched, resolved, built or decided.** 29 contradictions open, 43 gaps open, 26 missions unlaunched, 0 of 19 absorption rows closed. |
| ⚠ | **Judgements here are `DERIVED` from reading**, except the code inventory in Part 4 §4.2 of the supplement, which is `MEASURED` and shows its commands. |

---

## 9. Manifest of this supplement

| Path | What |
|---|---|
| `SUPPLEMENT_README.md` | this file |
| `docs/_index/agent_army_wave0_supplement.md` | ⭐ the substance — Wave 0 recovered and tagged, the five collisions, the adaptive-orchestration prior art |
| `docs/raw_research/converted/*.md` | the two newly readable documents |
| `scripts/docx_to_md.py` | the converter, so the extraction is reproducible |
| `docs/_index/corpus_manifest.yaml` | two records rewritten, two added, an `amended` block |
| `docs/_index/document_catalog.md` | rows in *Agent armies*, *Organizational architecture*, and the limits table |
| `docs/_index/concept_index.yaml` | 6 concepts added, `C-OR-04` rewritten, counts re-measured |
| `docs/_index/contradictions.md` | **CN-29** added, **CN-01** amended |
| `docs/_index/supersession_candidates.md` | **SP-15** — vocabulary superseded, content preserved |
| `docs/_index/current_vs_proposed.md` | 8 rows added to Part 3, GAP-01 limit closed |
| `docs/_index/high_leverage_concepts.md` | **HL-15** — the Mission Assurance Receipt |
| `docs/_index/research_gap_candidates.md` | GAP-01 closed, GAP-03 downgraded and corrected, **GAP-43** added |
| `docs/research/backlog.yaml` | `RB-00A` marked done, `supplementary_assessment_2026_09_02` added |
| `docs/research/dependency_graph.md` | Wave 0 is 5, not 6; one chain shortened |

**Not included, deliberately:** `duplicate_clusters.md` and `repo_snapshot.md` were not modified by
this pass and are unchanged from the original review pack.
