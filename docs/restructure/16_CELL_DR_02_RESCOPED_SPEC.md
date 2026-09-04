# 16 — CELL-DR-02, rescoped

# Canonical Link Architecture Validation, Gap Analysis and Advancement

**Identifier:** `CELL-DR-02` — **retained.** File identifier `CELL-DR-02-LINK-FABRIC` retained.
The governing registry (`10_PROPOSED_research_registry.yaml`) requires no new versioned identifier;
this is a scope revision of the same lane, recorded as such.

**Supersedes:** the CELL-DR-02 scope in
`docs/raw_research/CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack/CELL_OS_Deep_Research_Manifest_v3.md`
§7. ⛔ **That source is immutable and unmodified** (`bef3b644…6cb826a5`). This document is the
version to dispatch.

**Phase 1, post-P0-B.** Measured 2026-09-03 against `827f871`.
⛔ **NOT DISPATCHED. Nothing here has been sent to any research service.**

---

## 1. Why the original scope must not be dispatched

v3 §7 asks: *"What formal semantics should govern every connection between Operatives, Cells, Meshes,
tools, memory, domains and organizations?"* — and lists as **required outputs** a canonical Link
schema, a Link Contract schema, and a Link Type Registry.

**A candidate version of all three already exists inside this repository**, surfaced by Gate P0-B:
`docs/raw_research/CELL_OS_Frontier_Audit_Research_Pack/01_CANONICAL_ONTOLOGY/CELL_OS_Canonical_Terminology_vNext.md`
(SHA-256 `dfebc108…3222a95`).

⭐ **Dispatching the original scope would buy back a vocabulary this repository already owns** —
the failure `docs/research/backlog.yaml` names as *"this corpus's characteristic failure… paid for at
least twice"*, and the same failure the DR08 finding identified.

⚠ **But the prior work is thinner than first reported, and the correction runs the other way too.**
`09` §7.2 called it a *"substantial Link specification"*. Measured, it is **one document, with each
Link entity mentioned exactly once**, its fields labelled *"Potential"* and its semantics labelled
*"Candidate"*, in a file whose own status line reads *"design/research ontology"*.

> **Both errors are avoidable in the same way: attach the prior work, and scope the lane to what is
> genuinely missing.**

---

## 2. Measured baseline — what the lane inherits

### 2.1 Link across every canonical source

```bash
# regeneration: see docs/restructure/14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md §6
```

| Term | v0.1 (31pp design) | v0.2 (Master Guide) | ontology vNext | collisions | `factory/`+`tests/` |
|---|---:|---:|---:|---:|---:|
| `Link` (as an architectural entity) | **0** | **0** | **21** | 0 | **0** |
| `Link Contract` | 0 | 0 | **1** | 0 | 0 |
| `Link Type` / `Link Type Registry` | 0 | 0 | **1** each | 0 | 0 |
| `Link Fabric` | 0 | 0 | **1** | 0 | 0 |
| `Inter-Mesh Link` / `Cell Link` / `Federation Link` | 0 | 0 | **1** each | 0 | 0 |
| **`Inter-Cell Link`** | 0 | 0 | **0** | 0 | 0 |
| **`CellBus`** | **4** | **3** | 1 | 0 | **0** |
| `Mesh Synapse` | **1** | 0 | 0 | 0 | 0 |

**Three facts the lane must be told:**

1. ⛔ **`Link` is 0 in v0.1.** The Link vocabulary **post-dates** the 31-page technical design.
2. ⛔ **v0.2's 10 `Link` hits are all non-architectural** — hyperlinks, `work.link` board operations,
   *"linked Cell Image"*. **Link-as-entity exists in exactly one document.**
3. ⚠ **`Inter-Cell Link` does not exist.** The ontology's term for that role is **`Cell Link`**.

### 2.2 ⭐ The incumbent is CellBus, and it is better specified

v0.2 §8 — *"CellBus and typed coordination"* — carries a complete typed message vocabulary with
canonical effects, and a design rule: *"Do not make chat transcripts the canonical coordination
structure."*

| Message type | Purpose | Canonical effect |
|---|---|---|
| `REQUEST` | ask another Operative/Cell/service for bounded work or information | creates dependency or service call |
| `RESPONSE` | return requested result | may satisfy dependency; **not automatically evidence** |
| `CLAIM` | statement believed true | stored with provenance and uncertainty; requires validation for consequential use |
| `EVIDENCE` | typed proof object | appended to Evidence Ledger and linked to assertion |
| `HANDOFF` | transfer ownership/context | updates WorkGraph ownership and context package |
| `ALERT` | health/risk signal | may create incident/decision/gate |
| `ESCALATION` | request stronger cognition or human decision | routes to Governor / approval queue |
| `STATE_UPDATE` | runtime/object state update | validated by owning deterministic service |

⛔ **On evidence, CellBus is the incumbent coordination mechanism and Link Fabric is the newcomer.**
The lane must justify Link Fabric **against** CellBus. It must not assume Link supersedes it, and it
must not produce a design in which both exist without a stated boundary.

### 2.3 What the ontology already supplies — attach, do not re-derive

- **Link** — *"a first-class, typed, governed, measurable relationship between two CELL OS entities"*;
  may connect Operatives, Meshes, Cells, humans, services, tools, knowledge domains, external systems
  or CELL OS instances.
- **16 "Potential Link fields"** — source/destination · relationship type · direction · protocol/schema
  · authority · trust · context filter · bandwidth/rate · latency class · cost ceiling ·
  privacy/security policy · verification requirements · activation conditions · fallback · lifetime ·
  evidence requirements.
- **18 "Candidate Link semantics"** — communication · delegation · authority · knowledge · capability ·
  consultation · escalation · event · synchronization · consensus · competition · adversarial
  challenge · supervision · resource allocation · temporal handoff · subscription · trust · federation.
- **Link Contract**, **Link Type Registry** (with the rule *"prefer this to hundreds of hard-coded
  enums"*), **Link Fabric**, **Inter-Mesh Link**, **Cell Link**, **CELL OS Federation Link** — one
  sentence each.
- **A naming ruling:** *"**Do not call this Cell Mesh**"* for the federation layer.
- **A figure:** `05_VISUALS/Link_Fabric.mmd`.
- **An open research problem, already named:** *"Organizational Connectivity Optimization — optimize
  who should be connected to whom, through what protocol, with what authority, under what conditions
  and for what objective."*

### 2.4 ⚠ Link-adjacent prior art inside our own corpus

v0.1 §5 proposes **Mesh Synapse** — *"a policy-controlled recurring pathway between two Cells/nodes
that repeatedly exchange useful context"* — plus **Epistemic Routing Table**, **Context Proximity
Index**, **Capability Lease** and **Context Relay Cell**. These predate the Link vocabulary and cover
overlapping ground. **The lane must reconcile them rather than discover them again.**

---

## 3. Rescoped decision question

> **Given the existing CELL OS Link ontology and the better-specified CellBus coordination model
> (both attached), what formal semantics, contracts, compatibility rules and failure behaviour must
> be added to make Links implementable and testable — and where exactly is the boundary between the
> Link Fabric and CellBus?**

⛔ **This lane may not restate the ontology's definitions as findings.** Its first required output is
an inventory proving it read them.

---

## 4. Required work

### 4.1 Enumerate what already exists — before any external search

1. Inventory every Link concept already defined, with its source and its exact status label
   (*"Potential"*, *"Candidate"*, defined, undefined).
2. Reconcile `Mesh Synapse`, `Epistemic Routing Table`, `Context Proximity Index`, `Capability Lease`
   and `Context Relay Cell` (v0.1 §5) against the Link vocabulary. **State which are Links, which are
   Link policies, and which are something else.**
3. Reconcile `CellBus` (v0.2 §8) against `Link Fabric`. ⛔ **A design in which both exist without a
   stated boundary is a failed output.**

### 4.2 Test the inherited candidates rather than adopting them

4. **Test whether all 16 candidate Link fields are necessary.** For each: is it load-bearing, derivable
   from another field, or policy that belongs on the Link *Contract* rather than the Link? **Propose
   a minimal required set and an optional set**, with the reason for each demotion.
5. **Reconcile the 18 candidate semantics.** ⚠ Several appear to be the same relationship at different
   authority levels (`delegation` / `authority` / `supervision`) or the same transport with different
   intent (`communication` / `event` / `subscription`). **Produce a smaller orthogonal set plus a
   mapping showing where each of the 18 lands** — and justify any that survive as distinct.
6. Determine whether the **Link Type Registry** is the right extensibility mechanism, or whether a
   closed core set with typed extension is safer.

### 4.3 Specify what is genuinely absent

7. **Formal semantics** — reliability, ordering, idempotency, delivery guarantees, at-least-once vs
   exactly-once, and what a Link promises under partition.
8. **Failure and recovery state machine** — degraded, suspended, revoked, expired, renegotiated;
   what happens to in-flight evidence.
9. **Lifecycle and negotiation** — creation, capability/trust negotiation, activation conditions,
   renewal, revocation, retirement. ⚠ **Absent from the ontology entirely.**
10. **Authority and trust flow** — what permissions traverse a Link, whether authority is delegable
    through one, and how this composes with the `CELL Kernel`'s deterministic control-plane rule
    (v0.2 §4.1: LLMs *"must not be the final authority for secrets, cross-tenant access, production
    deployment, budget ceilings, certification or hard denial rules"*).
11. **Evidence and provenance flow** — how the `EVIDENCE` message type and the Evidence Ledger relate
    to Link-carried provenance.
12. **Observability** — what a Link must emit for health, degradation and cost to be measurable.
13. **Versioning and compatibility** — what makes two Link versions compatible; how a Contract change
    is rolled out without breaking live Links.

### 4.4 Topology coverage — enumerate the gaps

14. Analyse coverage across every connection class, and **state which are the same Link type and which
    are genuinely different**:

| Class | Meaning | Ontology term today |
|---|---|---|
| **C↔C** | Cell to Cell | `Cell Link` |
| **T↔T** | Mesh (team) to Mesh | `Inter-Mesh Link` |
| **C↔OS** | Cell to the CELL OS control plane | ⛔ **undefined** |
| **T↔OS** | Mesh to the control plane | ⛔ **undefined** |
| **OS↔OS** | federation between CELL OS instances | `CELL OS Federation Link` |
| **Hierarchical** | parent Mesh to sub-Mesh (`Mesh Hierarchy`) | ⛔ **undefined** |
| **Shared** | one Mesh participating in two parents | ⛔ **undefined** |

⚠ **Four of seven classes have no term.** ⛔ **And the `T` classes depend on TD-3**: `C-MESH`,
`T-MESH` and `OS-MESH` are defined in **no canonical source**. **The lane must be told to use the
ontology's `Mesh Architecture` / `Mesh Topology` / `Mesh Hierarchy` distinction instead, and must not
invent definitions for the C/T/OS triple.**

### 4.5 External prior art — comparison, not adoption

15. Compare against protocol, actor, workflow, graph, service-mesh and multi-agent contract
    approaches. **Distinguish novelty of a primitive from novelty of a combination, implementation
    differentiation and practical utility.**
16. ⛔ **Do not claim CELL-DR-02 is novel before §4.1 is complete.** A novelty claim made before the
    internal inventory is a claim about a corpus the lane has not read.
17. ⚠ Note for the lane: the organizational-compiler novelty claim in this estate was already
    **refuted** on primary sources (`arXiv:2607.25446`, IMACS). Treat that as an input.

### 4.6 Propose only what is missing

18. Every proposal must state which of: `ALREADY_DEFINED` · `REFINEMENT_OF_EXISTING` ·
    `GENUINELY_NEW` · `REJECTED_AS_UNNECESSARY`.
19. ⛔ **A proposal that restates an ontology definition and labels it `GENUINELY_NEW` fails the
    lane's acceptance criteria.**

### 4.7 Falsifiable questions and acceptance criteria

20. For each recommendation, state the **falsifiable research question**, what evidence would
    **disconfirm** it, and the **acceptance criterion** that would let it be promoted.
21. Report the **four readiness axes separately** for every recommendation.

---

## 5. Required outputs

1. **Inventory of existing Link work** — every concept, source and status label. *(Precondition for
   everything below.)*
2. **CellBus ↔ Link Fabric boundary** — with a recommendation on TD-6.
3. **Minimal Link schema** — required fields, optional fields, and the justification for every one of
   the 16 candidates demoted or dropped.
4. **Orthogonal Link semantics set** — with a mapping showing where each of the 18 candidates lands.
5. **Link Contract schema.**
6. **Link Type Registry design** — or a reasoned rejection in favour of a closed core set.
7. **Lifecycle and negotiation model.**
8. **Failure and recovery state machine.**
9. **Compatibility and versioning rules.**
10. **Authority, trust and evidence flow**, composed with the `CELL Kernel` control-plane rule.
11. **Observability requirements.**
12. **Topology coverage matrix** across the seven classes in §4.4, with the four undefined classes
    resolved.
13. **Tests for invalid, degraded and adversarial Links.**
14. **Minimal implementation interface**, compatible with the current flat Python package
    (68 modules, PyYAML the only runtime dependency).
15. **Integration map for `factory/contract.py`** — ⚠ the dependency centre; changes there have the
    widest blast radius in the codebase.
16. **Prior-art comparison matrix** and a defensible differentiation statement.
17. **Decision register** — `KEEP` · `MODIFY` · `MERGE` · `RESEARCH` · `DEFER` · `REJECT`.
18. **Claim-to-source ledger**, separating sourced fact, measured repository fact, inference, design
    proposal and speculative R&D.

---

## 6. Readiness — reported on four independent axes

| Axis | Verdict | Basis |
|---|---|---|
| **RESEARCH_READINESS** | ⭐ **READY** | Gate P0-B is complete; the ontology and both `.docx` are surfaced and greppable; the attachment set (§7) exists in full. ⚠ **Ready on this rescoped spec only** — the v3 original is not ready and must not be sent |
| **EXPERIMENT_READINESS** | ⛔ **BLOCKED** | No two-component test harness exists. `Link*` = 0 occurrences in `factory/` and `tests/`. Nothing can exercise a Link today |
| **IMPLEMENTATION_READINESS** | ⛔ **NOT_READY** | TD-6 (Link vs CellBus) is undecided; `contract.py`'s integration surface is unanalysed. ⚠ **`contract.py` is the dependency centre — implementation must not begin on an undecided boundary** |
| **PROMOTION_READINESS** | ⛔ **NOT_READY** | Nothing implemented, nothing exercised. Per `factory/assertions.py`, even fully built code that no mission invoked is `IMPLEMENTED_NOT_EXERCISED`, never `EXERCISED` |

⛔ **Research readiness does not imply the other three.** Recorded separately and never collapsed.

---

## 7. Attachment set

### Canonical sources — surfaced by Gate P0-B, hashes verified
- `docs/raw_research/CELL_OS_Frontier_Audit_Research_Pack/01_CANONICAL_ONTOLOGY/CELL_OS_Canonical_Terminology_vNext.md` — `dfebc108…3222a95` ⭐ **the prior work; read it first**
- `docs/raw_research/CELL_OS_Frontier_Audit_Research_Pack/01_CANONICAL_ONTOLOGY/KNOWN_TERMINOLOGY_COLLISIONS.md` — `e0a81e3c…0622380b`
- `docs/raw_research/converted/CELL_OS_Product_Technical_Design_v0.1.md` — ⭐ **§5 Mesh Synapse and mesh-native concepts**
- `docs/raw_research/converted/CELL_OS_Master_Research_Design_Development_Operations_User_Guide_v0.2.md` — ⭐ **§8 CellBus, §4.1 control-plane rule**

### Phase 1 measurements
- `docs/restructure/14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md` — the reconciliation and the terminology decisions
- `docs/restructure/15_V3_ERRATA_OVERLAY.md` — ⚠ **E-07, E-09 and §3 apply directly to this lane**
- `docs/restructure/09_RESEARCH_MANIFEST_V3_RECONCILIATION.md` — ⚠ **§7.2 is superseded by `15` §3**

### Code anchors
- `factory/contract.py` — ⭐ the dependency centre and the integration target
- `factory/blueprint.py` — `TeamSpec` / `AgentSpec`, the only implemented entities in the family

### Prior art already settled here
- `.agent-platform/RECONCILIATION.md` §1.1 — the organizational-compiler novelty refutation, **as an
  input, not an open question**

### Diagram
- `05_VISUALS/Link_Fabric.mmd`, inside `CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip`
  (⚠ **not yet surfaced** — surface it with the lane if the diagram is needed)

---

## 8. Prohibitions carried into the prompt

1. ⛔ Do not restate an ontology definition as a finding.
2. ⛔ Do not claim novelty before the internal inventory (§4.1) is complete.
3. ⛔ Do not invent definitions for `C-MESH`, `T-MESH` or `OS-MESH` — they are defined in no canonical
   source (TD-3). Use `Mesh Architecture` / `Mesh Topology` / `Mesh Hierarchy`.
4. ⛔ Do not use `Inter-Cell Link` — the canonical term is `Cell Link`.
5. ⛔ Do not assume Link Fabric supersedes CellBus. CellBus is better specified today.
6. ⛔ Do not infer implementation from documentation. **Every CELL OS concept in this lane measures
   zero in `factory/` and `tests/`.**
7. ⛔ Do not introduce a new synonym into the Blueprint/Genome/Image family (TD-7).
8. ⛔ Do not propose a design requiring runtime dependencies beyond PyYAML without stating the cost
   explicitly.

---

## 9. Dispatch status

    NOT DISPATCHED
    RESEARCH_READY on this rescoped spec — pending user approval of the rescope itself
    ⛔ The v3 original scope must not be sent.
