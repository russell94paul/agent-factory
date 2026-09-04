# V3 activation decision

**Phase 1, post-P0-B.** Measured 2026-09-03 against `agent-factory` @ `827f871` (`main`).
**Eventual destination:** `docs/research/V3_ACTIVATION_DECISION.md`.
**⭐ Updated after Gate P0-B completed** — record:
[`14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md`](14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md).

⛔ **No external research dispatched. No Phase 2 migration started.**

---

## The four decisions, reported independently

| # | Decision | Verdict |
|---|---|---|
| 1 | **CELL-DR-01** | ⭐ **`CELL-DR-01_RESEARCH_READY`** |
| 2 | **CELL-DR-02 rescope** | ⭐ **`CELL-DR-02_RESCOPE_COMPLETE`** |
| 3 | **CELL-DR-02 research** | ⭐ **`CELL-DR-02_RESEARCH_READY`** — ⛔ *on the rescoped spec only* |
| 4 | **v3 activation** | **`V3_ACCEPTED_NOT_ACTIVATED`** |

⛔ **Research readiness does not imply experiment, implementation or promotion readiness.** For both
lanes the other three axes are blocked, and §5 states each separately.

---

## 1. `CELL-DR-01_RESEARCH_READY`

**Ready.** Gate P0-B closed its only hard blocker: the canon is surfaced, greppable and
hash-verified, and the attachment manifest (`12`) is complete with every path verified to exist.

⚠ **Two conditions attach to the dispatch, and neither blocks the readiness verdict:**

1. ⭐ **Ten terminology decisions await approval** (`14` §7). The lane can be dispatched without
   them, but should not be: **TD-1 is a direct contradiction between two surfaced canonical
   sources**, and a research service asked to resolve it will hand the contradiction back.
2. **Three prompt amendments must be applied** — errata E-01 (`forecast.py` does not exist), E-08
   (`Operative Kernel` is defined nowhere), E-09 (C/T/OS-MESH are defined nowhere).

**On v3's own stated condition:** v3 §7 makes CELL-DR-01 *"research-ready after P0-A through P0-C"*.
**P0-C is open.** It is assessed as **non-binding for the research axis** — it concerns corpus index
hygiene, not the questions this lane asks or the evidence it reads. ⚠ **Recorded as an explicit
departure from v3's wording rather than silently dropped.**

---

## 2. `CELL-DR-02_RESCOPE_COMPLETE`

**Complete.** `16_CELL_DR_02_RESCOPED_SPEC.md` — *Canonical Link Architecture Validation, Gap
Analysis and Advancement*. **Identifier `CELL-DR-02` retained**; the registry requires no new
versioned identifier, and the change is recorded as a scope revision of the same lane.

Every requirement of the rescope is met: it treats the ontology as prior internal work and attaches
it; enumerates what is defined; identifies incomplete contracts; requires external comparison without
adoption; **tests whether all 16 candidate fields are necessary**; **requires the 18 candidate
semantics to be reconciled into a smaller orthogonal set with a mapping**; covers lifecycle,
negotiation, trust, authority, evidence, observability, failure handling and versioning; enumerates
the **seven** connection classes (**four of which have no canonical term**); requires every proposal
to be labelled `ALREADY_DEFINED` / `REFINEMENT_OF_EXISTING` / `GENUINELY_NEW` /
`REJECTED_AS_UNNECESSARY`; and defines falsifiable questions with acceptance criteria.

### ⛔ The rescope also corrected this repository's own prior claim

`09` §7.2 called the ontology a **"substantial Link specification."** P0-B measured it:

- `Link` as an architectural entity: **0 in v0.1**, **0 in v0.2** (all 10 hits are hyperlinks,
  `work.link` board ops, *"linked Cell Image"*), **21 in the ontology alone**.
- `Link Contract`, `Link Type Registry`, `Link Fabric`, `Inter-Mesh Link`, `Cell Link`,
  `Federation Link`: **exactly one occurrence each** — their own definition headings.
- The fields are labelled ***"Potential"***; the semantics ***"Candidate"***; the document's own
  status line reads ***"design/research ontology."***

⭐ **It is one author's single-document candidate vocabulary, not a specification.** The conclusion —
rescope the lane — was right; the argument was stronger than the evidence supported, and is corrected
in `15` §3.

⚠ **And the incumbent is `CellBus`**, which v0.2 §8 gives a full typed message vocabulary with
canonical effects. **On evidence CellBus is better specified than Link Fabric**, so the lane must
justify Link Fabric *against* it (TD-6) rather than assume it supersedes it.

---

## 3. `CELL-DR-02_RESEARCH_READY`

**Ready — on `16_CELL_DR_02_RESCOPED_SPEC.md` only.**

⛔ **The v3 original scope must not be dispatched.** It would purchase a vocabulary this repository
already owns.

⚠ **One dependency the rescope does not remove:** `05_VISUALS/Link_Fabric.mmd` is still inside
`CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip` and was not surfaced. Surface it with the lane
if the diagram is needed; it is not a blocker.

---

## 4. `V3_ACCEPTED_NOT_ACTIVATED`

**v3 remains accepted as the forward queue and is not activated.** Two of v3 §13's seven activation
conditions remain unmet — down from three.

| v3 §13 condition | Before P0-B | Now |
|---|---|---|
| All attached source manifests indexed | ✅ MET | ✅ MET |
| Queue reconciliation complete | ✅ MET | ✅ MET |
| **The canonical ontology is visible** | ⛔ NOT MET | ⭐ **MET** — surfaced, 3-way hash verified |
| **Binary-document visibility gaps resolved or explicitly bounded** | ⛔ NOT MET | ⭐ **MET at the stronger reading — resolved.** All four binaries read, each instrument proved live by positive control |
| CELL-DR-01 has a verified attachment list | ⚠ PARTIAL | ⭐ **MET** — every path verified to exist |
| No local measurement misclassified as external research | ⚠ CONDITIONAL | ⭐ **MET** — CELL-DR-02 rescoped (`16`) |
| **The active worktree and overlapping edits are protected** | ⛔ NOT MET | ⛔ **NOT MET** — 5 worktrees, 18 modified tracked files, no decision recorded |

⛔ **Plus one condition v3 does not list and this pass added:** ten terminology decisions await
approval, and **TD-1 is a contradiction between two canonical sources.** Activating a queue whose
first lane must resolve a contradiction no human has ruled on would push a decision into a research
service that cannot take it.

> **Activation therefore needs exactly two things: the terminology approvals (minutes), and the
> P0-D worktree decision (a judgement call about five checkouts).** Neither is research.

---

## 5. Readiness on all four axes — never collapsed

| Lane | RESEARCH | EXPERIMENT | IMPLEMENTATION | PROMOTION |
|---|---|---|---|---|
| **CELL-DR-01** | ⭐ **READY** | `NOT_APPLICABLE` | ⛔ `NOT_READY` | ⛔ `NOT_READY` |
| **CELL-DR-02** (rescoped) | ⭐ **READY** | ⛔ `BLOCKED` — no two-component harness; `Link*` = 0 in `factory/` and `tests/` | ⛔ `NOT_READY` — TD-6 undecided; `contract.py` is the dependency centre | ⛔ `NOT_READY` |
| CELL-DR-03 | ⚠ `READY_ON_DEPENDENCY` (after DR-01) | ⛔ `BLOCKED` — P0-E | ⛔ | ⛔ |
| CELL-DR-04 | ⚠ `READY_ON_DEPENDENCY` — ⛔ **and TD-8 first** | ⛔ `BLOCKED` — P0-E | ⚠ `PARTIAL` | ⛔ |
| CELL-DR-05 | ✅ `READY_ON_DEPENDENCY` | ⛔ **`BLOCKED, HARD`** — covariance needs *repeated comparable* missions | ⛔ | ⛔ |
| CELL-DR-06 | ✅ `READY_ON_DEPENDENCY` | ⛔ **`BLOCKED, HARD`** — ⭐ *protocol design may proceed now* | ⚠ `PARTIAL` | ⛔ |
| CELL-DR-07 | ⚠ `READY_ON_DEPENDENCY` — ⛔ **and TD-3 first** | ⛔ `BLOCKED` | ⛔ | ⛔ |
| CELL-DR-08 | ⛔ `BLOCKED` — the Domain design record does not exist | ⛔ | ⛔ | ⛔ |
| CELL-DR-09 | ⛔ `BLOCKED` — after DR-08; no dataset present | ⛔ | ⛔ | ⛔ `OUT_OF_SCOPE` by design |
| CELL-DR-10 | ⛔ `NOT_READY` | `NOT_APPLICABLE` | ⛔ | ⛔ |

⭐ **`PROMOTION_READINESS` is `NOT_READY` for every lane, without exception.** Per
`factory/assertions.py`, even fully built code that no mission invoked is `IMPLEMENTED_NOT_EXERCISED`,
never `EXERCISED`. **Zero CELL OS concepts exist in `factory/` or `tests/`** — the only implemented
entities in the entire terminology family are `TeamSpec` (32) and `AgentSpec` (38), and they appear
in **none** of the four canonical documents.

---

## 6. Exact missing evidence for every blocked verdict

| Blocked verdict | Exact missing evidence or decision |
|---|---|
| `V3_ACCEPTED_NOT_ACTIVATED` | (a) the P0-D worktree decision — which of 5 checkouts is authoritative, and how the 18 modified tracked files are protected; (b) approval of the ten terminology decisions in `14` §7 |
| CELL-DR-02 `EXPERIMENT` | a minimal two-component test harness. Nothing in `factory/` can exercise a Link — `Link*` = 0 occurrences |
| CELL-DR-02 `IMPLEMENTATION` | **TD-6** — the Link Fabric ↔ CellBus boundary. ⚠ `contract.py` is the dependency centre; implementation must not begin on an undecided boundary |
| CELL-DR-04 `RESEARCH` | **TD-8** — `Operative Kernel` (0 everywhere) versus `CELL Kernel` (4/4/1/27), which may be a *different* thing: system-wide control plane, not per-Operative |
| CELL-DR-07 `RESEARCH` | **TD-3** — C-MESH / T-MESH / OS-MESH are defined in no canonical source |
| CELL-DR-08 `RESEARCH` | **a local Domain design record.** The whole family measures `ZERO (MEASURED)` across all four canonical sources. ⛔ No research can supply this; it must be written |
| CELL-DR-09 `EXPERIMENT` | no historical or synthetic dataset is present in this repository |
| All `EXPERIMENT` axes gated on P0-E | ⭐ **one bounded, non-dry-run mission with acceptance evidence** — `RB-00C`. Measured today: 10 runs, 0 PASS, 7/7 `dry_run=True` |
| All `PROMOTION` axes | runtime implementation plus exercise evidence. None exists for any CELL OS concept |

---

## 7. ⭐ The finding P0-B produced that most changes what happens next

**Before P0-B, the blocker was a file nobody had opened. After P0-B, the blocker is that the canon
disagrees with itself.**

| | The canon says | And also says |
|---|---|---|
| **Cell Mesh** | ontology: *"a coordinated team/topology of Operatives. **A Cell Mesh is not OS federation.**"* (12 hits) | v0.1 §5 heading: *"**CELL Mesh — Federation of CELL OS Nodes**"* (11 hits) |
| **Kernel** | v3 CELL-DR-04 is built on *"Operative Kernel"* | `Operative Kernel` = **0** in every canonical source; `CELL Kernel` = 4 / 4 / 1 / 27 |
| **Persistent organization** | ontology hierarchy: **Organization** | v0.1 **and** v0.2 object models: **Organism** |
| **The Cell specification** | ontology heading: *"Cell Blueprint / Cell Genome"* | v0.1 §2 specifies **`Cell Genome`** in seven facets; the code calls it **`TeamSpec`** |

⭐ **v0.2 silently resolves the Cell Mesh contradiction in the ontology's favour** — it drops Cell
Mesh from its object model and uses `Federation` — **but never says it is doing so**, and v0.1
remains in the corpus asserting the opposite.

> **The next action is not research and not a file operation. It is ten decisions, and a human has
> to take them.** They are enumerated with evidence and a recommendation each in
> `14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md` §7.

---

## 8. ⚠ A procedural finding worth more than any of the above

The `.xlsx` returned a **clean, plausible, entirely false table of zeroes — twice** — before the
third reader worked. `sharedStrings.xml` exists but is empty; there are no `<t>` nodes; the workbook
stores strings as `t="str"` with the text in `<x:v>`.

⛔ **Two of the three instruments this gate depended on were blind, and both failed silently in the
direction that would have confirmed what we already believed.** Only the positive control — *does the
reader return any content at all?* — caught it.

⭐ **Every zero published by this gate is accompanied by a positive control proving the instrument
could see.** That is the reason the twenty-four `NOT-VISIBLE` verdicts can be recorded as
`ZERO (MEASURED)` rather than as another round of inference.

---

    PHASE 1 P0-B COMPLETE — NO EXTERNAL RESEARCH DISPATCHED — NO PHASE 2 MIGRATION STARTED
