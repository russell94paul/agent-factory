# 14 — Gate P0-B: extraction record and canonical terminology reconciliation

**Phase 1, Gate P0-B only.** Measured 2026-09-03 against `agent-factory` @ `827f871` (`main`).
⛔ **No external research dispatched. No Phase 2 migration started. No tracked file moved, renamed
or deleted. No source archive or original binary modified.**

**Authoritative location for:** the P0-B provenance record, the canonical terminology reconciliation,
and the terminology decisions awaiting user approval. Other Phase 1 documents cite this one rather
than restating it.

---

## 1. Verdict

> ## `P0-B COMPLETE`

| P0-B task (from `10_PROPOSED_research_registry.yaml`) | Result |
|---|---|
| Surface `CELL_OS_Canonical_Terminology_vNext.md` | ✅ **DONE** — three-way hash match |
| Surface `KNOWN_TERMINOLOGY_COLLISIONS.md` | ✅ **DONE** — three-way hash match |
| Convert `CELL_OS_Product_Technical_Design_v0.1.docx` | ✅ **DONE** — 100% body coverage, measured |
| Convert `…User_Guide_v0.2.docx` | ✅ **DONE** — 100% body coverage, measured |
| Inspect `CELL_OS_Delivery_Backlog_v0.2.xlsx` | ✅ **DONE** — ⛔ **took three readers**; §4.2 |
| Inspect `CELL OS Design Master Brief.pdf` | ✅ **DONE** — ⛔ **Decision D-5 was wrong**; §4.3 |
| Revise all `NOT_VISIBLE` findings | ✅ **DONE** — §5. **All resolved, none merely bounded** |
| Surface NERVE / Switchboard design research | ⚠ **NOT ATTEMPTED — out of this pass's authorised scope.** §8 |

⭐ **v3 §13's activation condition "binary-document visibility gaps are resolved *or explicitly
bounded*" is met at the stronger reading: resolved.** All four CELL OS binaries were read, each by an
instrument proved live by positive control.

---

## 2. Source resolution — the `.docx` was determined from the record, not guessed

The instruction required that the `.docx` identity come from the repository's Phase 1 records, with a
`BLOCKED-AMBIGUOUS-SOURCE` verdict if they did not name it unambiguously.

```bash
python -c "import yaml; d=yaml.safe_load(open('docs/restructure/10_PROPOSED_research_registry.yaml',encoding='utf-8')); \
g=[x for x in d['local_gates'] if x['id']=='P0-B'][0]; \
print([t['task'] for t in g['tasks']])"
```

The record names **two** `.docx`, by exact filename, with expected sizes — and v3 §5 line 130 says
*"convert and inspect the **two** CELL OS DOCX files."* Two independent records agree on identity and
cardinality.

> **Verdict: `SOURCE-RESOLVED`, not `BLOCKED-AMBIGUOUS-SOURCE`.** The requirement is plural, not
> ambiguous. ⚠ The other three `.docx` in the tree (`Agent_Factory_Frontier_Architecture_
> Prioritization_Pack.docx`, `Beyond_Agent_Armies_Frontier_Architectures.docx`) are **already
> converted** and present in `docs/raw_research/converted/`; they are not P0-B candidates.

---

## 3. Provenance record

### 3.1 Surfacing location — ⛔ a correction to `12_NEXT_RESEARCH_RUN.md`

`12_NEXT_RESEARCH_RUN.md` and `DESIGN_DELTA…` §8 both proposed extracting the ontology to
`docs/architecture/canonical/terminology/`. **That was wrong on two counts, and the extraction did
not use it:**

1. ⛔ **`docs/architecture/` does not exist.** It is a *proposed Phase 2 target*
   (`04_PROPOSED_TARGET_STRUCTURE.md` §83–86). Creating it would have started Phase 2.
2. ⛔ **`04_PROPOSED_TARGET_STRUCTURE.md` §4 rule 4 forbids the promotion anyway:** *"Promotion to
   `architecture/canonical/` requires implementation evidence or a passing test, and an explicit
   written rationale. A research report never becomes canonical automatically."* The ontology's own
   header reads **"Status: design/research ontology"**. It does not qualify.

**The established, existing convention was used instead** — extract under `docs/raw_research/`
mirroring the archive's internal path, byte-identical, no header inserted. Verified against a prior
extraction:

```bash
# an existing pack extract is byte-identical to its archive member — the convention this follows
python -c "import zipfile,hashlib;z=zipfile.ZipFile('docs/raw_research/agent2_sihre_consolidation_pack.zip');\
n='agent2_sihre_consolidation_pack/research_prompts/DR01_PRIOR_ART_AND_NOVELTY.md';\
print(hashlib.sha256(z.read(n)).hexdigest());\
print(hashlib.sha256(open('docs/raw_research/'+n,'rb').read()).hexdigest())"
# a7dfd4d1…  a7dfd4d1…   -> identical
```

⚠ **`docs/_incoming/` was also not used — it does not exist either** (proposed only). No second
intake structure was invented.

### 3.2 The archive

```bash
sha256sum docs/raw_research/CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip
# 6cc48dc65fa3a922dc0273f18b5ac5b7cb36bd50e5d6c3be7844deb5f096b815      15,503,568 bytes, 35 members
```

Member listing was inspected **before** anything was extracted; only the two required members were
read and written.

### 3.3 ⭐ Three-way hash verification

The pack ships its own `00_START_HERE/FILE_MANIFEST_SHA256.csv`. That is a **second, independent
instrument** for provenance, and it was reconciled rather than trusted.

| File | in-archive | on-disk | pack's own CSV | Match |
|---|---|---|---|---|
| `CELL_OS_Canonical_Terminology_vNext.md` (12,055 B) | `dfebc108…3222a95` | `dfebc108…3222a95` | `dfebc108…3222a95` | ✅ **3/3** |
| `KNOWN_TERMINOLOGY_COLLISIONS.md` (1,174 B) | `e0a81e3c…0622380b` | `e0a81e3c…0622380b` | `e0a81e3c…0622380b` | ✅ **3/3** |

**Extracted to** `docs/raw_research/CELL_OS_Frontier_Audit_Research_Pack/01_CANONICAL_ONTOLOGY/`.
**Archive unmodified.** The extraction script refuses to overwrite an existing path.

### 3.4 The two `.docx` — originals fingerprinted before and after

| Original (immutable) | SHA-256 | Bytes | Converted to |
|---|---|---:|---|
| `docs/design/CELL_OS_Product_Technical_Design_v0.1.docx` | `30131d25…40ee3713` | 311,438 | `docs/raw_research/converted/CELL_OS_Product_Technical_Design_v0.1.md` (547 lines) |
| `docs/raw_research/CELL_OS_Master_Research_Design_Development_Operations_User_Guide_v0.2.docx` | `724cb7db…0ab071f0` | 66,022 | `docs/raw_research/converted/…_v0.2.md` (886 lines) |

**Converter — the repository's existing one, not a new tool:**

```bash
python scripts/docx_to_md.py "docs/design/CELL_OS_Product_Technical_Design_v0.1.docx" \
       "docs/raw_research/converted/CELL_OS_Product_Technical_Design_v0.1.md"
python scripts/docx_to_md.py "docs/raw_research/CELL_OS_Master_Research_Design_Development_Operations_User_Guide_v0.2.docx" \
       "docs/raw_research/converted/CELL_OS_Master_Research_Design_Development_Operations_User_Guide_v0.2.md"
```

**Both originals re-hashed after conversion: unchanged.** Output directory
`docs/raw_research/converted/` is the existing convention (it already held two converted `.docx`).

---

## 4. ⭐ Conversion coverage — measured, not asserted, and it corrected a claim

### 4.1 The `.docx` conversions

The Phase 1 record carried the converter as *"exists, verified 100.1% coverage"*. **That figure was
inherited, not re-measured.** A discriminating test was run instead: extract every `<w:t>` text run
from every `word/*.xml` part and check whether its whitespace-normalised text survives into the
Markdown.

| Source part | Runs | Testable (≥8 chars) | **Missing** |
|---|---:|---:|---:|
| v0.1 `word/document.xml` | 894 | 776 | ⭐ **0** |
| v0.1 `word/header1.xml` | 1 | 1 | ⛔ **1** |
| v0.1 `word/footer1.xml` | 1 | 1 | ⛔ **1** |
| v0.2 `word/document.xml` | 1,212 | 1,038 | ⭐ **0** |
| v0.2 `word/header1.xml` | 1 | 1 | ⛔ **1** |
| v0.2 `word/footer1.xml` | 1 | 1 | ⛔ **1** |

⭐ **Body coverage is 100% — 776/776 and 1038/1038.** ⚠ **The converter reads `word/document.xml`
only**, so headers and footers are dropped. All four dropped runs are page furniture:

- *"CELL OS | PRODUCT + TECHNICAL DESIGN | v0.1"*
- *"Design baseline — September 2026 | Research / architecture working specification"*
- *"CELL OS | MASTER RESEARCH + DESIGN + DEVELOPMENT + OPERATIONS + USER GUIDE | v0.2"*
- *"Research / architecture working specification - September 2026"*

**No body content was lost.** 📝 **Skill gap:** `scripts/docx_to_md.py` silently ignores
`word/header*.xml` and `word/footer*.xml`. Harmless here; it would not be for a document whose
version or classification lives only in the header.

⭐ **And the dropped furniture is itself evidence:** both documents describe themselves in their own
running footer as a **"Research / architecture working specification"**. That is the documents
agreeing, in their own page furniture, with the rule that they are not implementation records.

### 4.2 ⛔ The `.xlsx` took three readers. The first two were blind and returned zeroes.

| Attempt | Method | Result | Verdict |
|---|---|---|---|
| 1 | `xl/sharedStrings.xml` → `<si>/<t>` | **0 strings** | ⛔ **BLIND** — the file's shared-string table is empty (115 bytes, self-closing) |
| 2 | worksheets → `<t>` nodes (inline strings) | **0 nodes** | ⛔ **BLIND** — this workbook uses neither |
| 3 | worksheets → cells with `t="str"`, text in `<x:v>` | ⭐ **3,288 text cells, 62,323 chars** | ✅ **LIVE** |

```bash
# the encoding that defeated readers 1 and 2
python -c "import zipfile,re;d=zipfile.ZipFile('docs/raw_research/CELL_OS_Delivery_Backlog_v0.2.xlsx')\
.read('xl/worksheets/sheet3.xml').decode();print(len(re.findall('t=\"str\"',d)))"   # 2815
```

⭐ **Had reader 1 been trusted, this pass would have published a 20-row table of zeroes from an
instrument that could not see, and called the binary-visibility gap closed.** The positive control —
*does the reader return any content at all?* — is the only thing that caught it. Sheets are
`Dashboard · Phases · Tickets · WorkGraph · Linear Bridge · Research · Gates`; sheet 3 (`Tickets`)
holds 2,616 of the 3,288 cells. **SHA-256 `3b216ea6…3ba9b6`; file unmodified, nothing extracted.**

### 4.3 ⛔ The `.pdf` — Decision D-5 is wrong as measured today

The Phase 1 record carried `.xlsx` and `.pdf` as *"⛔ NONE HERE — Decision D-5"* (no converter).
**Measured:**

```bash
command -v pdftotext            # present
python -c "import fitz"         # present  (PyMuPDF)
python -c "import pdfminer"     # present
```

Three PDF text extractors are available. **The gap was a tooling assumption, not a tooling absence.**

```bash
pdftotext -layout "docs/raw_research/CELL OS Design Master Brief.pdf" \
          "docs/raw_research/converted/CELL_OS_Design_Master_Brief.txt"
# 576 lines, 16,759 chars.  Original sha256 83aa65ed…716a68bf — unchanged before and after.
```

⚠ **Content note, and it matters for classification:** the PDF is **not an architecture
specification**. It is a *design brief prompt* — *"You are the Principal Product Design & Interaction
Intelligence Lead for CELL OS… Your job is not to make the existing UI prettier."* It is an input to
a design exercise. **It carries no entity definitions**, which is why its census (§5) is almost
entirely zero for architecture terms while returning `NERVE` 11, `Cell Studio` 6, `Switchboard` 4.

---

## 5. ⭐ Revised `NOT-VISIBLE` findings — all thirteen resolve to `ZERO (MEASURED)`

`09` §5.2 recorded thirteen concepts as **`ABSENT (corroborated)`** — agreed by a text census and by
a 525-line cross-reference audit, but **not proved**, because the binaries were unread.

**All four binaries have now been read. Every instrument was proved live by positive control before
its zeroes were accepted.**

### 5.1 Positive controls — proving each instrument could see

| Instrument | Control terms | Result |
|---|---|---|
| v0.1 `.md` | `Cell` 173 · `Cell Image` 18 · `Cell Genome` 10 · `HyperMESH` 16 · `CellBus` 4 | ✅ LIVE |
| v0.2 `.md` | `Cell` 157 · `Cell Image` 23 · `Kernel` 24 · `HyperMESH` 14 | ✅ LIVE |
| ontology | `Cell` 53 · `Link` 21 · `Mesh` 32 | ✅ LIVE |
| `.xlsx` reader 3 | 3,288 cells; first cell = *"CELL OS — Research, Build & Operating Roadmap v0.2"* | ✅ LIVE |
| `.pdf` | 576 lines; `NERVE` 11 · `Cell Studio` 6 | ✅ LIVE |

### 5.2 The revised verdicts

| Concept | v0.1 | v0.2 | ontology | `.xlsx` | `.pdf` | **Verdict was** | **Verdict now** |
|---|---:|---:|---:|---:|---:|---|---|
| Domain Plane | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Domain Genome | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Domain Compiler | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Domain Fabric | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Domain Data Plane | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| CELL-Q | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| MESA | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Causal World Model | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Temporal Executive | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Earned Authority | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Capability Graph | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Operative Immune System | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Cognitive Economics | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Recursive Operative Genesis | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| capability envelope | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Claims–Evidence Graph | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Experience-to-Doctrine | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Operative Canonical Layered Model | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| **Operative Kernel** | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** ⚠ but `CELL Kernel` = 4/4/1/27/0 — §7 TD-8 |
| Mission Compiler | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Shadow Execution Twin | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** ⚠ but `Shadow Twin` = 0/7/1 and `Shadow Cell` = 6/1/1 |
| Regime-Adaptive | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| Capability Lab | 0 | 0 | 0 | 0 | 0 | ABSENT (corroborated) | ⭐ **ZERO (MEASURED)** |
| **C-MESH / T-MESH / OS-MESH** | 0 | 0 | 0 | 0 | 0 | *not previously assessed* | ⛔ **ZERO (MEASURED)** — §7 TD-3 |

⭐ **Not one of the v3 `PROPOSED_EXTERNAL` concepts appears in any CELL OS design document, at any
maturity, anywhere.** The classification `PROPOSED_EXTERNAL` is confirmed at the strongest available
evidence level. **This does not reject them** — repository absence is not refutation — but it settles
that they are external design inputs and not undocumented internal history.

---

## 6. Canonical terminology reconciliation

**Sources (all now surfaced):** `v0.1` = converted Product + Technical Design; `v0.2` = converted
Master Guide; `onto` = `CELL_OS_Canonical_Terminology_vNext.md`; `coll` =
`KNOWN_TERMINOLOGY_COLLISIONS.md`; `code` = occurrences in `factory/` + `tests/`.

⛔ **Rule applied throughout: implementation is never inferred from documentation presence.** A term
is `IMPLEMENTED CODE ENTITY` only where it appears in `factory/` or `tests/`.

| Concept | v0.1 | v0.2 | onto | code | Classification |
|---|---:|---:|---:|---:|---|
| **Operative** | 26 | 27 | 21 | **0** | **Canonical definition** (onto: *"the individual intelligent computational worker"*). v0.1/v0.2 call it **AI Operative** in their object models — an **alias**. ⛔ Documentation-only design |
| **Operative Cell** | 0 | 2 | 2 | **0** | ⛔ **Unresolved decision.** Defined nowhere. Its only appearances are the collision entries asking whether it should exist (`onto` §"Known terminology collisions" 2; `coll` row 2) |
| **Cell** | 173 | 157 | 53 | **0** | **Canonical definition** — and the three definitions agree: a bounded executable organizational unit. Documentation-only design |
| **Cell Image** | 18 | 23 | 1 | **0** | ⭐ **Canonical definition** — the resolved, immutable, attested deployment artifact. **Promoted to a first-class entity in v0.2's object model.** Documentation-only design. ⛔ **v3 omits this term entirely** |
| **Cell Blueprint** | 1 | 0 | 1 | **0** | ⚠ **Never independently defined.** The `onto` hit is the compound heading *"Cell Blueprint / Cell Genome"*; the v0.1 hit is lowercase prose (*"One Cell blueprint compiler…"*). **Alias of Cell Genome at best** |
| **Cell Genome** | 10 | 1 | 1 | **0** | ⭐ **Canonical definition, and the winner on evidence** — v0.1 §2 gives it a full seven-facet specification (topology, cognition, memory, communication, authority, resources, adaptation). Documentation-only design |
| **Configuration Genome** | 0 | 0 | 0 | **0** | ⛔ **Deprecated / colliding.** Zero occurrences in **every** canonical source. It exists only in the external v2/v3 manifests. **Retire** |
| **`TeamSpec`** | 0 | 0 | 0 | ⭐ **32** | ⭐ **Implemented code entity** — `factory/blueprint.py`, covered by `tests/test_blueprint.py`. **Invisible to every design document** |
| **`AgentSpec`** | 0 | 0 | 0 | ⭐ **38** | ⭐ **Implemented code entity.** Same |
| **Cell Mesh** | 11 | 1 | 12 | **0** | ⛔ **DIRECT CONTRADICTION — §7 TD-1.** `onto`: *"a coordinated team/topology of Operatives. **A Cell Mesh is not OS federation.**"* v0.1 §5 heading: *"**CELL Mesh — Federation of CELL OS Nodes**"* |
| **C-MESH** | 0 | 0 | 0 | **0** | ⛔ **ZERO in every canonical source.** Undefined |
| **T-MESH** | 0 | 0 | 0 (1 in `coll`) | **0** | ⛔ Undefined; named once, only as a collision to audit |
| **OS-MESH** | 0 | 0 | 0 | **0** | ⛔ **ZERO in every canonical source.** Undefined |
| **Federation** | 17 | 3 | 7 | **0** | **Canonical definition** — v0.1/v0.2 object models both carry `Federation` as the cooperating-nodes entity. `onto` names it **CELL OS Federation Link** and offers alternatives (CELL Federation, CELL Fabric, InterCELL, CELL Network, Inter-OS Fabric) — **unresolved naming** |
| **Organism** | 11 | 3 | 2 | **0** | ⚠ **Alias or distinct? Unresolved.** v0.1 **and** v0.2 object models both use **Organism** for the persistent adaptive organization |
| **Organization** | 42 | 27 | 16 | **0** | **Canonical in `onto`'s core hierarchy**, which flags *"Organization / Organism — determine whether both terms are needed"*. ⭐ **Two documents say Organism; the ontology hierarchy says Organization** |
| **Link** | **0** | 10 | 21 | **0** | ⛔ **See §7 TD-6 and `16_CELL_DR_02_RESCOPED_SPEC.md`.** Zero in v0.1. **All 10 v0.2 hits are non-architectural** — hyperlinks, `work.link` board ops, "linked Cell Image". **Link-as-entity exists in exactly one document** |
| **Link Contract** | 0 | 0 | **1** | **0** | ⚠ **Proposed, single-source, single-mention** — its own definition heading and nothing else |
| **Link Type / Link Type Registry** | 0 | 0 | **1** each | **0** | ⚠ Same |
| **Link Fabric** | 0 | 0 | **1** | **0** | ⚠ Same |
| **Inter-Mesh Link** | 0 | 0 | **1** | **0** | ⚠ Same |
| **Inter-Cell Link** | 0 | 0 | **0** | **0** | ⛔ **Does not exist.** `onto` defines **Cell Link** (1) for this role — ⚠ *the addendum instruction's own term is not the canonical one* |
| **Federation Link** | 0 | 0 | **1** | **0** | ⚠ Proposed, single-mention |
| **CellBus** | 4 | 3 | 1 | **0** | ⭐ **Canonical definition, and the strongest coordination concept on evidence** — v0.2 §8 gives it a full typed message vocabulary (REQUEST · RESPONSE · CLAIM · EVIDENCE · HANDOFF · ALERT · ESCALATION · STATE_UPDATE) with canonical effects. Documentation-only design |
| **Mesh Synapse** | **1** | 0 | 0 | **0** | ⚠ **Link-adjacent prior art inside our own corpus** — v0.1 §5: *"policy-controlled recurring pathway between two Cells/nodes"*. Predates the Link vocabulary |
| **Domain Plane / Domain Genome** | 0 | 0 | 0 | **0** | **Proposed external concept.** §5.2 |
| **HyperMESH** | 16 | 14 | 3 | **0** | **Canonical definition** — the memory/context/evidence substrate. ⚠ `onto` flags that "MESH" sublabels may collide with Cell Mesh. Documentation-only design |
| **SIHRE** | 3 | 0 | **0** | **0** | ⚠ **Never expanded in any canonical source.** v0.1 §7 heading uses it (*"SIHRE-Derived Governance"*). Expansion is `SOURCED` to external v2 Lane 05 — §7 TD-4 |
| **CELL ADAPT** | 0 | 0 | 0 | **0** | ⛔ **ZERO in every canonical source.** Documentation-only, external. Nearest internal concept: **Evolution Chamber** (9/3/1/18) |
| **MESA** | 0 | 0 | 0 | **0** | **Proposed external concept** |
| **NERVE** | 0 | 0 | **1** | **0** | ⚠ **Defined only in `onto`** (*"Navigation, Execution, Routing, Verification & Escalation"*). 11 hits in the PDF brief, which uses but does not define it. §8 |
| **Organizational Compiler / Org-IR** | 1 / 0 | 2 / 4 | 1 / 1 | **0** | **Canonical definition** — v0.2 §5 gives the compile pipeline. ⛔ **Novelty already refuted** (`arXiv:2607.25446`) |
| **CELL Kernel** | 4 | 4 | 1 | **0** | ⭐ **Canonical definition** — the deterministic control plane. v0.2 §4.1: *"LLMs… must not be the final authority for secrets, cross-tenant access, production deployment, budget ceilings, certification or hard denial rules."* Documentation-only design |
| **Evolution Chamber** | 9 | 3 | 1 | **0** | **Canonical definition** — and 101 occurrences corpus-wide. ⛔ **In no v3 lane** (`09` §10.1) |
| **Shadow Twin / Shadow Cell** | 0 / 6 | 7 / 1 | 1 / 1 | **0** | **Canonical definition, two names.** `onto` merges them: *"Shadow Cell / Shadow Twin"* |

### 6.1 ⭐ The three findings this table produces

**⭐ 6.1.1 — Zero. Not one CELL OS architectural concept exists in `factory/` or `tests/`.** The only
implemented entities in the entire family are **`TeamSpec` (32)** and **`AgentSpec` (38)**, and they
appear in **none** of the four design documents. The code and the canon have no shared vocabulary at
all. That is the terminology problem, stated as a measurement.

**⛔ 6.1.2 — Three object models, none identical, all authoritative-sounding.**

| | v0.1 §2 | v0.2 §2 | ontology core hierarchy |
|---|---|---|---|
| | Mission · AI Operative · Worker · **Cell** · **Organism** · Federation | Objective · Initiative · Mission · AI Operative · Worker · **Cell** · **Cell Image** · **Organism** · Federation | Model → Operative Runtime → Operative → **Cell Mesh** → Cell → **Organization** → CELL OS |
| Cell Mesh in the model? | ⛔ no — used for *federation* in §5 | ⛔ no — `Federation` carries that role | ✅ yes — as the *team topology* |
| Persistent org called | **Organism** | **Organism** | **Organization** |
| Cell Image first-class? | ⚠ defined, not in the entity table | ✅ **yes** | ⚠ mentioned once |

⭐ **v0.2 silently resolves the Cell Mesh contradiction in the ontology's favour** — it drops Cell
Mesh from the object model and uses `Federation` for federation. **But it never says it is doing
so**, and v0.1 remains in the corpus asserting the opposite.

**⛔ 6.1.3 — `C-MESH`, `T-MESH` and `OS-MESH` are defined in no canonical source.** They measure zero
across all four surfaced documents. They exist in the wider corpus (11 / 13 / 17 occurrences) and in
the external v2/v3 manifests. ⚠ **v3 CELL-DR-07 asks a research service to treat them as three
distinct concepts. There is nothing here to distinguish.** That scope line needs a decision before it
is dispatched, not a researcher's guess.

---

## 7. Terminology decisions requiring user approval

⛔ **None of these was decided by this pass.** P0-B surfaces and reconciles; it does not rule.

| # | Decision | Evidence | Recommendation (for approval) |
|---|---|---|---|
| **TD-1** | ⭐ **Cell Mesh: team topology, or OS federation?** | Direct contradiction: `onto` (12 hits) vs v0.1 §5 (11 hits). v0.2 has already moved to `Federation` | **Adopt the ontology reading** — Cell Mesh = team/topology; the federation layer gets its own name. v0.2 already behaves this way. ⚠ Requires marking v0.1 §5 superseded |
| **TD-2** | **Federation layer name** | `onto` offers five candidates and rules only *"do not call this Cell Mesh"*; v0.1/v0.2 object models say `Federation` | **Keep `Federation`** — it is the term both design documents already use. Do not adopt InterCELL / CELL Fabric |
| **TD-3** | ⛔ **C-MESH / T-MESH / OS-MESH** | **0 in every canonical source**; 11/13/17 corpus-wide | **Retire, or define before use.** ⛔ Do not send CELL-DR-07 to research a distinction no document makes |
| **TD-4** | **SIHRE expansion** | Never expanded in any canonical source; `SOURCED` to v2 Lane 05 | **Adopt *Self-Improving Heterogeneous Reasoning Ensemble*** and record its basis as `SOURCED`, not `MEASURED` |
| **TD-5** | ⛔ **OPC** | 2 occurrences, both customer-facing; absent from all four canonical sources | **Define it or remove it from the deck.** ⚠ Still a hypothesis that it abbreviates "Operative Cell" |
| **TD-6** | ⭐ **Link Fabric vs CellBus** | `CellBus` has a full typed message vocabulary in v0.2 §8; `Link Fabric` has one sentence in one document | ⭐ **CellBus is the incumbent on evidence.** The Link lane must justify Link Fabric *against* CellBus, not assume it replaces it. See `16_…RESCOPED_SPEC.md` |
| **TD-7** | **Blueprint / Genome / Image / `TeamSpec`** | `Cell Genome` 10/1/1 with a seven-facet spec · `Cell Image` 18/23/1 · `Cell Blueprint` never independently defined · `Configuration Genome` **0 everywhere** · `TeamSpec`/`AgentSpec` **70 in code** | **Adopt `Cell Genome`** (declarative spec) + **`Cell Image`** (resolved artifact). **Retire `Cell Blueprint` and `Configuration Genome`.** ⭐ **State the mapping `Cell Genome ↔ TeamSpec`/`AgentSpec`** so code and canon can name the same thing |
| **TD-8** | **Operative Kernel vs CELL Kernel** | `Operative Kernel` **0 everywhere**; `CELL Kernel` 4/4/1 + 27 in the delivery backlog | **`CELL Kernel` is the canonical term.** ⚠ v3 CELL-DR-04 is built around "Operative Kernel", a term no canonical source uses |
| **TD-9** | **Organism vs Organization** | v0.1 (11) and v0.2 (3) say **Organism**; `onto` hierarchy says **Organization** and flags the audit | **Decide.** Two design documents outweigh one ontology hierarchy on usage; the ontology outranks them on intent. ⛔ **A genuine tie that needs a human** |
| **TD-10** | **Operative Cell vs Cell** | Defined nowhere; appears only in collision entries | **Retire `Operative Cell`.** Nothing defines it, and `Cell` is fully specified in three documents |

⭐ **TD-8 and TD-3 are new — surfaced only because P0-B ran.** Both are cases where v3 builds a lane
around a term that no canonical source contains.

---

## 8. ⚠ What P0-B did NOT do

| Item | Status | Why |
|---|---|---|
| Surface the 4 NERVE / Switchboard design-research artifacts | ⛔ **NOT ATTEMPTED** | Out of this pass's authorised scope — the instruction scoped Step 1 to the two ontology files plus the required `.docx`. **The registry's P0-B task list carries it as a seventh task; it remains open** |
| Promote anything to `architecture/canonical/` | ⛔ **REFUSED** | §3.1 — the tree does not exist and the promotion rule forbids a research ontology |
| Re-run the repo-wide concept census | ⛔ not run | Would change the published 998-file baseline. §5 uses **targeted** censuses over the newly visible sources instead, which is the discriminating test |
| Decide any terminology question | ⛔ **REFUSED** | §7 is a recommendation set awaiting approval |

⚠ **Consequence for `09` §8:** the claim *"completed NERVE research exists but reuse is NOT
EVIDENCED"* is **unchanged** by this pass. P0-B has now added one measurement to it: **`NERVE` is
defined in exactly one surfaced source** (the ontology, one line) and used-but-undefined in the PDF
brief (11 hits). It appears **zero** times in v0.1 and v0.2.

---

## 9. Commands and validation checks executed

```bash
# provenance
sha256sum docs/raw_research/CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip
python  # zipfile.infolist() -> member listing inspected BEFORE extraction
python  # per-member sha256 in-archive == on-disk == pack FILE_MANIFEST_SHA256.csv   (3-way, 2 files)
sha256sum docs/design/CELL_OS_Product_Technical_Design_v0.1.docx                     # before and after
sha256sum "docs/raw_research/CELL OS Design Master Brief.pdf"                        # before and after

# conversion (repository's existing converter)
python scripts/docx_to_md.py <in.docx> <out.md>        # x2
pdftotext -layout "docs/raw_research/CELL OS Design Master Brief.pdf" <out.txt>

# coverage — discriminating, not asserted
python  # every <w:t> run from word/{document,header*,footer*}.xml checked against the .md
        # document.xml: 776/776 and 1038/1038 survive;  header/footer: 4 runs dropped

# instrument validation — positive control before accepting any zero
python  # xlsx reader 1 (sharedStrings) -> 0     BLIND
python  # xlsx reader 2 (<t> nodes)     -> 0     BLIND
python  # xlsx reader 3 (t="str"/<x:v>) -> 3288  LIVE
command -v pdftotext ; python -c "import fitz, pdfminer"   # D-5 refuted

# census
python  # 24-term census over v0.1 + v0.2 + ontology
python  # 40-term reconciliation across v0.1 + v0.2 + ontology + collisions + factory/ + tests/
grep -rIoh -E "TeamSpec|AgentSpec|..." factory tests    # code-entity counts
```

**Integrity checks after the pass:**

```bash
git rev-parse --short HEAD                       # 827f871   — unchanged
git status --porcelain | grep -c '^ M'           # 18        — unchanged
git status --porcelain | grep -E '^( D|R |D )'   # (empty)   — nothing deleted or renamed
```

---

## 10. Method and limits

**Measured:** three-way hash agreement on both ontology files; before/after hashes on all four
binaries; per-XML-part conversion coverage; three successive `.xlsx` readers with positive controls;
PDF tooling availability; a 40-term reconciliation across four surfaced sources plus `factory/` and
`tests/`.

**Read in full:** both ontology files; the converted v0.1 §§1–2, 5, 8, 15, 20; the converted v0.2
§§2, 4, 5, 8, 11; the PDF brief's opening.

**Not read:** the v0.1 and v0.2 sections not listed above were censused but not read line by line —
⚠ **a term could be defined in a section I censused but did not read, and the census would find it
while I would not have understood its definition.** The census is exhaustive; the reading is not.

**Not attempted:** any dispatch, any external search, any Phase 2 work, any promotion to canonical,
any terminology ruling, any NERVE artifact surfacing.

⭐ **The finding most worth carrying forward is procedural, not architectural.** The `.xlsx` returned
a clean, plausible, entirely false table of zeroes **twice** before the third reader worked. Only the
positive control caught it. **Two of the three instruments this gate depended on were blind, and both
failed silently in the direction that would have confirmed what we already believed.**
