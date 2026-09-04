# 15 — CELL OS Deep Research Manifest v3: repository-local errata and interpretation overlay

**Phase 1 overlay.** Measured 2026-09-03 against `agent-factory` @ `827f871` (`main`).

> ## ⛔ This overlay does not modify the ingested source.
>
> `docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack/CELL_OS_Deep_Research_Manifest_v3.md`
> is **immutable** — SHA-256 `bef3b644958de44cae37efff1d3fdededb77fd94e55db446fb6a679c6eb826a5`,
> verified unchanged after this pass. Corrections live **here**, beside it, and are applied when the
> manifest is *used*. The source is evidence of what was proposed; this overlay is evidence of what
> is true.

**Precedence when this overlay and v3 disagree:** this overlay, and only where it cites measured
evidence or a surfaced canonical source. Every entry below carries one. Uncited disagreement is not
an erratum — it is an opinion, and none is recorded here.

---

## 1. Errata index

| # | v3 location | Class | Severity |
|---|---|---|---|
| **E-01** | §4.1 implementation anchors | Non-existent path | ⛔ **blocks an attachment list** |
| **E-02** | §4.3 naming collision | Incomplete + names a term that is never defined | ⛔ **misdirects a decision** |
| **E-03** | §2 baseline — index delta | Stale count | ⚠ |
| **E-04** | §5 Gate P0-D — overlapping files | Stale count | ⚠ |
| **E-05** | §10 execution order — P0-E placement | Sequencing error | ⛔ **inverts the queue's value** |
| **E-06** | §5 Gate P0-E — dependency on P0-D | Unnecessary dependency | ⛔ |
| **E-07** | §7 CELL-DR-02 scope | Written as greenfield; ontology exists | ⚠ **but far thinner than first reported — §3** |
| **E-08** | §7 CELL-DR-04 — "Operative Kernel" | Term absent from every canonical source | ⛔ **new, from P0-B** |
| **E-09** | §7 CELL-DR-07 — C/T/OS-MESH | Terms absent from every canonical source | ⛔ **new, from P0-B** |
| **E-10** | §9 legacy disposition table | Omits v2 Lane 02 entirely | ⚠ |
| **E-11** | §5 Gate P0-B — `.xlsx`/`.pdf` tooling | Inherited "no converter" is false | ⚠ **new, from P0-B** |
| **E-12** | §4.2 `PROPOSED_EXTERNAL` list | Five concepts declared, no lane assigned | ⚠ |

---

## 2. Errata detail

### E-01 — ⛔ `factory/forecast.py` does not exist

**v3 §4.1** lists seven modules as *"measured implementation anchors"*. Six verify. One does not.

```bash
ls factory/forecast.py       # No such file or directory
ls factory/projection.py     # exists
```

| Anchor | Verified |
|---|---|
| `contract.py` · `blueprint.py` · `evals.py` · `calibration.py` · `readiness.py` · `roadmap.py` | ✅ 6/6 |
| **`forecast.py`** | ⛔ **absent** |

⚠ **`factory/projection.py` is the nearest match by name and remains `UNVERIFIED`.** Nothing has been
read to establish that it performs the role v3 attributes to `forecast.py`. **It must not be
substituted into an attachment list as an equivalent** — cite it as *"nearest candidate, role
unverified"* or drop the anchor. Verifying it is a one-file read that this pass did not perform.

**Basis: MEASURED** (existence), **ASSUMED** (the `projection.py` relationship).

### E-02 — ⛔ The Blueprint/Genome family is larger than three, and one of v3's three is never defined

**v3 §4.3:** *"Cell Blueprint, Cell Genome and Configuration Genome currently appear to describe
overlapping ideas. factory/blueprint.py is the implementation anchor. Research must not create a
fourth synonym."*

**Measured across the four canonical sources surfaced by P0-B, plus code:**

| Term | v0.1 | v0.2 | ontology | `factory/`+`tests/` | Status |
|---|---:|---:|---:|---:|---|
| **`Cell Genome`** | **10** | 1 | 1 | 0 | ⭐ **Best-evidenced.** v0.1 §2 gives a seven-facet specification |
| **`Cell Image`** | **18** | **23** | 1 | 0 | ⭐ **v3 omits it entirely.** First-class entity in v0.2's object model |
| **`Cell Blueprint`** | 1 | 0 | 1 | 0 | ⚠ **Never independently defined.** `onto` hit is the compound heading *"Cell Blueprint / Cell Genome"*; the v0.1 hit is lowercase prose |
| **`Configuration Genome`** | **0** | **0** | **0** | 0 | ⛔ **Zero in every canonical source.** External-manifest term only |
| **`TeamSpec`** | 0 | 0 | 0 | ⭐ **32** | ⭐ **Implemented.** `factory/blueprint.py`; `tests/test_blueprint.py` |
| **`AgentSpec`** | 0 | 0 | 0 | ⭐ **38** | ⭐ **Implemented** |

**Four corrections to v3 §4.3:**

1. ⛔ **`Cell Image` must be included.** It is the most-used term in the family (41 occurrences across
   v0.1 + v0.2) and it is **not a synonym** — the ontology and v0.2 both define it as the *resolved,
   immutable deployment artifact*, distinct from the declarative spec. Omitting it from the collision
   set risks a decision that collapses a real distinction.
2. ⛔ **`TeamSpec` and `AgentSpec` must be included.** They are the **only implemented entities in the
   family**, and they appear in **none** of the four design documents. The anchor v3 cites is a
   *filename*; the API is these two names.
3. ⚠ **`Cell Blueprint` is not a peer of the other two.** It is never independently defined.
4. ⛔ **`Configuration Genome` should be retired, not adjudicated.** Zero occurrences in every
   canonical source.

> ⭐ **The instruction "do not introduce a fourth synonym" arrives when the family already holds
> five names, and the two with running code are invisible to every design document.**

**Superseding statement — use this in place of v3 §4.3:**

> The declarative, versioned Cell specification is **`Cell Genome`**. Its resolved, immutable,
> attested deployment artifact is **`Cell Image`**. `Cell Blueprint` is an alias of `Cell Genome` and
> should be retired. `Configuration Genome` has zero canonical occurrences and should be retired.
> The implementation anchor is `factory/blueprint.py`, whose entities are **`TeamSpec`** and
> **`AgentSpec`**; the canonical decision must state the `Cell Genome ↔ TeamSpec`/`AgentSpec`
> mapping so code and canon can name the same thing. **Do not introduce a sixth name.**

**Basis: MEASURED.** Full table and method: `14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md` §6.

### E-03 — ⚠ Index delta: v3 says 888, measured 898

```bash
find docs .agent-platform blueprints missions evals boot-prompts -type f | wc -l   # 898
grep -n "files_on_disk_in_scope" docs/_index/corpus_manifest.yaml                  # 719
```

v3 §2 states *"719 claimed versus 888 measured"*. **Delta is 179, not 169.**
⚠ **Do not restate either number by hand** — regenerate with the command above. **Basis: MEASURED.**

### E-04 — ⚠ Overlapping modified files: v3 says seventeen, measured eighteen

```bash
git status --porcelain | grep -c '^ M'    # 18
git worktree list | wc -l                 # 5
```

v3 §5 Gate P0-D says *"protect the seventeen overlapping modified files"*. **Basis: MEASURED.**

### E-05 — ⛔ P0-E is scheduled after the waves it unblocks

v3 §5 correctly scopes Gate P0-E: it gates *"local covariance estimation, empirical ablation,
homeostasis threshold calibration [and] performance claims"* — which live in **CELL-DR-05, CELL-DR-06
and CELL-DR-07**.

⛔ **But v3 §10 places the "Observation" row after Wave G**, while those lanes run at **Waves D and
E**. The single binding local constraint is scheduled *after* the work it gates.

**Correction: P0-E moves to Local 0, or runs concurrently with Wave A.** It has no dependency on any
research lane. **Basis: v3 §5 read against v3 §10 — an internal inconsistency in the source.**

### E-06 — ⛔ P0-E must not depend on the documentation migration

v3 §5 opens Gate P0-E with *"After the safe migration gates permit it…"*, making it a dependent of
P0-D.

⛔ **Nothing about completing one bounded, non-dry-run agent run requires a documentation
restructure first.** The two are independent. **Correction: unbind P0-E from P0-D.**

⭐ **Severity note.** With E-05 and E-06 both applied as written, the highest-value action in the
programme — the one measurement everything empirical waits on — sits behind a docs reorganisation
*and* behind nine research lanes. **Basis: MEASURED** (10 runs, 0 PASS, 7/7 `dry_run=True`).

### E-07 — ⚠ CELL-DR-02 is written as greenfield, and the prior work is real but thin

**Corrected twice, and the second correction revises the first — see §3.** Superseded in full by
`16_CELL_DR_02_RESCOPED_SPEC.md`.

### E-08 — ⛔ "Operative Kernel" appears in no canonical source

**New, surfaced only by P0-B.** v3 §4.2 lists *"mandatory Operative Kernel and optional layers"* as a
`PROPOSED_EXTERNAL` input, and **CELL-DR-04 is built around it** (*"What is the minimum governed
architecture…"*, output *"mandatory kernel"*).

| Term | v0.1 | v0.2 | ontology | `.xlsx` | code |
|---|---:|---:|---:|---:|---:|
| **`Operative Kernel`** | **0** | **0** | **0** | **0** | **0** |
| **`CELL Kernel`** | 4 | 4 | 1 | **27** | 0 |

⭐ **The canonical term is `CELL Kernel`**, and it is well specified — v0.2 §6 gives its services and
§4.1 its control-plane rule: *"LLMs may propose plans… they must not be the final authority for
secrets, cross-tenant access, production deployment, budget ceilings, certification or hard denial
rules."*

⚠ **This is not merely a rename.** v3's `Operative Kernel` is *per-Operative*; the canonical
`CELL Kernel` is a *system-wide deterministic control plane*. **They may be different things, and
CELL-DR-04 currently asks about the one with no definition.** ⛔ **A decision is required before
CELL-DR-04 is dispatched** — recorded as TD-8. **Basis: MEASURED.**

### E-09 — ⛔ C-MESH, T-MESH and OS-MESH are defined in no canonical source

**New, surfaced only by P0-B.** v3 CELL-DR-07 scope requires research into *"C-MESH, T-MESH and
OS-MESH"* and *"Mesh Architecture, Topology and Hierarchy as distinct concepts"*.

| Term | v0.1 | v0.2 | ontology | collisions | corpus-wide |
|---|---:|---:|---:|---:|---:|
| C-MESH | 0 | 0 | 0 | 0 | 11 |
| T-MESH | 0 | 0 | 0 | **1** | 13 |
| OS-MESH | 0 | 0 | 0 | 0 | 17 |

The single `T-MESH` hit is the collision register asking whether the "MESH" sublabels should be
renamed. ⛔ **A research service asked to distinguish three concepts that no canonical document
defines will invent the distinction.** Recorded as TD-3. **Basis: MEASURED.**

⚠ **The ontology *does* define three genuinely distinct mesh concepts** — **Mesh Architecture**
(coordination pattern), **Mesh Topology** (the actual graph), **Mesh Hierarchy** (how meshes contain
meshes). **Those are the distinctions worth researching.** The C/T/OS triple is a different, undefined
axis.

### E-10 — ⚠ v3 §9 omits v2 Lane 02

v3 §9's legacy-disposition table maps repository DR01–DR08, R06B, the legacy twenty-report queue and
the RB items. **It never mentions v2 Lane 02** (*Prior Art, Novelty, **Failure Modes and Complexity
Budget***). Its prior-art half folds into CELL-DR-01; **its FMEA and complexity-budget outputs are
dropped from the programme entirely.** Recorded as missing topic MT-1. **Basis: MEASURED** (read of
both documents).

### E-11 — ⚠ The `.xlsx`/`.pdf` "no converter" premise is false

**New, from P0-B.** v3 §5 Gate P0-B says *"inspect or extract the XLSX and PDF through appropriate
read-only tooling"*; the repository's Phase 1 record carried both as *"⛔ NONE HERE — Decision D-5"*.

```bash
command -v pdftotext                            # present
python -c "import fitz"                         # present
python -c "import pdfminer"                     # present
# .xlsx needs no converter at all — stdlib zipfile + ElementTree, as scripts/docx_to_md.py already does
```

**Both were read in this pass.** Decision D-5's premise was a **tooling assumption that was never
tested**, and it had blocked two documents for as long as it stood. **Basis: MEASURED.**

### E-12 — ⚠ Five `PROPOSED_EXTERNAL` concepts are declared and assigned to no lane

v3 §4.2 declares them as approved design inputs; no lane in §7 owns them:
**Causal World Model · Temporal Executive · Operative Immune System · Cognitive Economics Engine ·
capability envelopes.** All five now measure `ZERO (MEASURED)` across all four canonical sources
(`14` §5.2).

**Recommended disposition: `DEFERRED_EXPERIMENT`** — keep them registered, open no lane until
CELL-DR-01 rules on whether the layered model needs them. **Basis: MEASURED.**

---

## 3. ⛔ A correction to this repository's own prior finding

`09_RESEARCH_MANIFEST_V3_RECONCILIATION.md` §7.2 stated that the canonical ontology *"already
supplies most of [CELL-DR-02's] Required-output list"* and described it as a **"substantial Link
specification."**

**P0-B measured it. That claim was too strong.**

| CELL-DR-02 required output | What actually exists | Measured |
|---|---|---|
| Canonical Link schema | a bulleted list headed **"*Potential* Link fields"** | 16 items, **1 document** |
| Link semantics taxonomy | a list headed **"*Candidate* Link semantics"** | 18 items, **1 document** |
| Link Contract | **one sentence**, its own definition heading | 1 occurrence total |
| Link Type Registry | **one sentence** | 1 occurrence total |
| Link Fabric | **one sentence** | 1 occurrence total |
| Inter-Mesh Link / Cell Link / Federation Link | **one sentence each** | 1 occurrence each |
| Compatibility rules · failure state machine · observability · security · tests · `contract.py` map | ⛔ **absent** | 0 |

```bash
# Link as an architectural entity across every canonical source
# v0.1: 0    v0.2: 10 (ALL non-architectural — hyperlinks, work.link, "linked Cell Image")
# ontology: 21    factory/+tests/: 0
```

**Three measured facts that change the characterisation:**

1. ⛔ **`Link` = 0 in v0.1**, the 31-page technical design. The Link vocabulary **post-dates** it.
2. ⛔ **All 10 v0.2 hits are non-architectural.** Link-as-entity exists in **exactly one document**.
3. ⚠ **That document labels its own status "design/research ontology"**, and labels the fields
   *"Potential"* and the semantics *"Candidate"*. **It is an author's candidate vocabulary, not a
   validated internal design.**

⭐ **The corrected characterisation:** the ontology is **genuine prior internal work that must be
attached and credited** — dispatching CELL-DR-02 without it would still buy back a vocabulary we
own. But it is **one author's single-document candidate list**, not a specification, and the lane's
real work is substantially larger than `09` §7.2 implied.

⚠ **And the incumbent is `CellBus`, not Link.** v0.2 §8 gives CellBus a full typed message vocabulary
with canonical effects — REQUEST · RESPONSE · CLAIM · EVIDENCE · HANDOFF · ALERT · ESCALATION ·
STATE_UPDATE. **On evidence, CellBus is the better-specified coordination concept and Link Fabric is
the newcomer.** The lane must justify Link Fabric *against* CellBus rather than assume it supersedes
it. Recorded as TD-6; specified in `16_CELL_DR_02_RESCOPED_SPEC.md`.

> ⭐ **Recorded because the mechanism matters more than the correction.** `09` §7.2 was written from
> a *reading* of the ontology, before the counting instrument had been pointed at it. It reached the
> right conclusion — rescope the lane — by an argument stronger than the evidence supported. **A
> claim that is right for a reason it cannot yet support is still a claim to correct.**

---

## 4. Corrected RB identifier mapping

`docs/research/backlog.yaml` numbers its 26 missions **`RB-00A`…`RB-00F`, then `RB-01`…`RB-20`** —
not a contiguous `RB-01`…`RB-26`.

```bash
python -c "import yaml; d=yaml.safe_load(open('docs/research/backlog.yaml',encoding='utf-8')); \
print([m['research_id'] for m in d['missions']])"
```

v3, the v3 ingest instruction and the earlier Phase 1 documents all cite the contiguous range and
reference rows **by position**, shifting every citation by six.

| Cited as | Correct ID | What the wrongly-cited ID actually names |
|---|---|---|
| RB-17 — error correlation between agent configurations | **RB-11** | a crosswalk for the six evidence vocabularies |
| RB-12 — which config parameters change outcomes | **RB-06** | credit assignment across a team |
| RB-10 — topology-task fit | **RB-04** | near-miss capture in high-reliability organisations |
| RB-09 — the store-capability question | **RB-03** | an evaluation protocol for org and team designs |
| RB-15 — ablation | **RB-09** | rank ladder versus absence table |
| RB-01…RB-06 — the six `NOT_RESEARCH` rows | **RB-00A…RB-00F** | five prior-art/foundational lanes and one comparison |
| RB-03 — complete one real agent run | **RB-00C** | what none of the existing knowledge stores can do |

⭐ **In every case the wrongly-cited row is a plausible-looking research item, so the error never
announced itself.** **Basis: MEASURED.**

---

## 5. Corrected dependency order

**v3 §10 as written**, with corrections applied:

| Wave | v3 says | Corrected |
|---|---|---|
| Local 0 | P0-A … P0-D | ⭐ **P0-A … P0-E** — P0-E moves here (E-05, E-06) |
| A | CELL-DR-01 | unchanged — ⚠ **apply TD-7, TD-8, E-01 to its prompt first** |
| B | CELL-DR-02, CELL-DR-03 | unchanged — ⛔ **CELL-DR-02 only in its rescoped form (`16`)** |
| C | CELL-DR-04 | unchanged — ⛔ **resolve TD-8 first: the lane names a term no source defines** |
| D | CELL-DR-05, CELL-DR-06 | unchanged — **research axes only**; empirical branches consume P0-E |
| E | CELL-DR-07 | unchanged — ⛔ **resolve TD-3 first: C/T/OS-MESH are undefined** |
| Local Domain | write the Domain design record | unchanged — ⛔ **a local write, not research** |
| F · G | CELL-DR-08 · CELL-DR-09 | unchanged |
| **Observation** | **P0-E, after Wave G** | ⛔ **DELETED — moved to Local 0** |
| Final | CELL-DR-10 | unchanged |

---

## 6. What this overlay does not correct

- **v3's north star, scope boundary and CELL-Q restrictions** — verified sound (`09` §9.2, three
  independent statements). No erratum.
- **v3's four-axis readiness model** — adopted wholesale; it is the most useful thing in the manifest.
- **v3's `PROPOSED_EXTERNAL` labelling** — confirmed at the strongest evidence level by P0-B (`14`
  §5.2). No erratum.
- **v3 §8's product-surface demotion to a local audit** — better than this repository's own earlier
  recommendation. No erratum.

⚠ **The errata are twelve entries against a 720-line manifest, and none of them touches its
structure.** v3 remains the accepted forward queue; this overlay is what makes it safe to use.
