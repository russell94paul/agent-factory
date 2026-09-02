# Agent Army — Wave 0 supplement, the two frontier documents, and the adaptive-orchestration prior art

**Generated 2026-09-02** by a narrow continuation pass, against:

| Repository | HEAD | Branch |
|---|---|---|
| `agent-factory` | `fc78074` | `main` |
| `agent-army-research` (sibling) | `11c5b3d` | `main` |

This file closes **`research_gap_candidates.md` GAP-01 in full** and the **architecture-relevant
portion of GAP-03**. It does **not** index the whole sibling repository, and it resolves nothing:
every conclusion below is attributed and tagged, and where two sources disagree the disagreement is
recorded rather than averaged.

---

## Epistemic tags used throughout

Every numbered statement in Parts 2–4 carries exactly one tag. This is the supplement's contract
with the reader, and it is the same discipline `contradictions.md` and `concept_index.yaml` follow.

| Tag | Means |
|---|---|
| `SOURCE FACT` | Verified in a primary artefact — a file in one of the two repositories, or a standard/paper the cited pass says it opened. Traceable to `file:line`. |
| `PRIOR SYNTHESIS` | A conclusion a previous pass reached from sources. It may be right; it is **not** itself a source. Cited to the synthesising document. |
| `PROPOSAL` | Something a document argues *should* be built or adopted. No evidence is claimed for it. |
| `SPECULATION` | An idea offered without mechanism, metric or evidence, and labelled as such by its own author or by this pass. |
| `UNRESOLVED` | A question the corpus poses and no pass has answered. |

⛔ **Nothing below is tagged `MEASURED` unless this pass ran the command and shows it.**

---

# Part 0 — What was inspected, and what was not

## 0.1 The two `.docx` — now converted (`SOURCE FACT`)

Both originals are **preserved byte-for-byte**. Converted renderings were written beside them:

```
docs/raw_research/Beyond_Agent_Armies_Frontier_Architectures.docx                430,863 bytes  (untouched)
docs/raw_research/Agent_Factory_Frontier_Architecture_Prioritization_Pack.docx   203,671 bytes  (untouched)

docs/raw_research/converted/Beyond_Agent_Armies_Frontier_Architectures.md         46,047 chars, 513 lines
docs/raw_research/converted/Agent_Factory_Frontier_Architecture_Prioritization_Pack.md
                                                                                  42,261 chars, 421 lines
```

Converter: `scripts/docx_to_md.py` (written this pass; `python-docx` is **not installed** in this
environment, so it parses `word/document.xml` directly and preserves heading level, list nesting,
tables and hyperlink targets).

**Extraction was verified rather than assumed.** The raw `<w:t>` character count was compared with
the markdown output stripped of syntax characters:

```
Beyond_Agent_Armies…            raw 38,548  →  md-stripped 38,251   (coverage 100.1%)
Agent_Factory_Frontier…         raw 32,732  →  md-stripped 32,519   (coverage 100.1%)
```

Coverage slightly exceeds 100% because hyperlink *targets* are added to the markdown and are not
`<w:t>` text. **The gap between 430,863 bytes and 46,047 characters is images**, not lost text:
`word/media/` holds 8 PNGs in the first document. ⚠ **Eight figures were NOT extracted** — they are
captioned in the text (`Figure 1 … Figure 8`) and the captions are preserved, but the diagrams
themselves are unread. That is a residual, narrower GAP-01.

## 0.2 The sibling repository — what was opened (`MEASURED`)

⚠ **First, a correction to `GAP-03`'s own figure.** GAP-03 and the boot prompt both state
*"155 markdown files, 3.6 MB"*. The file count is right; **the byte figure is not reproducible**:

```bash
cd ../agent-army-research && python -c "
import pathlib
fs=[p for p in pathlib.Path('.').rglob('*') if p.is_file() and '.git' not in p.parts]
md=[p for p in fs if p.suffix=='.md']
print('working tree', len(fs), sum(p.stat().st_size for p in fs))
print('markdown    ', len(md), sum(p.stat().st_size for p in md))"
# working tree 184 1,882,122
# markdown     155   880,781
```

Including `.git` the total is 2,467,147 bytes. **No basis yields 3.6 MB.** The markdown corpus is
**881 KB — about a quarter of the stated size.** This matters only because it was used to argue the
sibling was too large to index; on the true figure, indexing it is a much smaller job than believed.
*(This is `C-VD-04` — a count stated without its regeneration command, re-rotting exactly as
predicted.)*

**Read in full this pass** (7 files, 49,322 bytes):

| File | Why |
|---|---|
| `research/synthesis/W0-foundations.md` | ⭐ the Wave 0 synthesis — the document CN-01 rests on |
| `research/HYPOTHESIS_LEDGER.md` | H01–H10 with current status |
| `research/RESEARCH-MANIFEST.yaml` | wave plan, and which of R00–R45 have run |
| `ontology/00-core-ontology.md` | the 24-term draft ontology W0 proposes cutting to 13 |
| `foundations/FOUNDATIONAL_LAWS_DRAFT.md` | the 15 draft laws |
| `repo-boundary/PRODUCT-BOUNDARY.md` | the factory/runtime split and the 14-component ecosystem tally |
| `research/prompts/R31-frontier-organizational-primitives.md` | the unrun prompt closest to the frontier documents |

**⚠ Also read, and stated precisely because the first draft of this line overstated it:**
`architecture/` holds **13** files totalling **19,544 bytes** — they are *stubs*, not designs; the
largest is 4,849 bytes. **Eight were read in full** (13,614 bytes): `00` target architecture, `01`
intent-contract schema, `02` staff mesh, `03` cognitive logistics, `05` temporal echelons, `08`
organization-compiler pipeline, `10` federation protocol, `11` evolution chamber.
⛔ **Five were NOT read** (5,930 bytes): `04` event-and-world-state model, `06` knowledge-evidence
model, `07` skill-capability-doctrine model, `09` organizational-debugger model, `12` performance
reference architecture. ⚠ **`06` is the one that matters**: `PRODUCT-BOUNDARY.md` names it as the
**highest-priority convergence risk** — *"two evidence schemas… if these diverge, the field record
cannot be diffed against the capability record and the feedback loop silently stops working"* — and
this pass did not open it.

**Read by targeted extraction, not in full** — the three Wave 0 answers total **377,558 bytes** and
were not read end to end:

| File | Bytes | What was extracted |
|---|---|---|
| `research/answers/R01-answer-prior-art-and-novelty-boundary.md` | 121,598 | Deliverable 4 (the 15-concept novelty-risk map, lines 900–975) and Deliverable 5 (recommended terminology) |
| `research/answers/R00-answer-foundations-of-aoe.md` | 118,355 | the `StaffFunction` / PROSA verdicts only |
| `research/answers/R02-answer-canonical-ontology-and-vocabulary.md` | 137,605 | the ontology dispositions only |
| `research/sources/agent-factory-vocabulary-crawl.md` | 89,803 | **not read** |
| `research/sources/W0-audit-prior-art-citations.md` | 39,778 | Claim 5 (PROSA) only |
| `research/sources/W0-adversarial-refutation-novelty-claim.md` | 29,830 | **not read directly** — its conclusions reached this pass through `W0-foundations.md` |

⛔ **This is a real coverage limit and the reviewer must weight it.** Roughly **595 KB of the
sibling's 881 KB of markdown was not read.** What *was* read is the layer that carries conclusions;
what was not is the layer that carries the evidence behind them.

## 0.3 Independence of the sibling's sources (`MEASURED`)

The override requires that repeated copies not be counted as independent evidence. Measured:

```bash
cd ../agent-army-research && python -c "
import pathlib,hashlib,collections
s=collections.defaultdict(list)
for p in pathlib.Path('.').rglob('*'):
    if p.is_file() and '.git' not in p.parts and '.obsidian' not in p.parts:
        s[hashlib.sha256(p.read_bytes()).hexdigest()].append(p.as_posix())
print(sum(1 for v in s.values() if len(v)>1))"
# 4
```

**Four byte-identical groups, all benign:** ten empty `.gitkeep` files, and three template pairs
(`research/ANSWER_TEMPLATE.md` == `templates/research-answer.md`, and the same for the synthesis and
handoff templates). `legacy/research-pack-v2/` and `legacy/research-pack-v3/` hold **13 files,
62,611 bytes** — earlier *editions* of R00 and of prompts R28–R31 that all **differ** from the live
versions (checked with `diff`; every pair reported DIFFERS). So they are **superseded drafts, not
duplicates**, and no conclusion here rests on more than one copy of anything.

⚠ **Contrast with `agent-factory`, where the duplication problem is real:** `duplicate_clusters.md`
records `Agent Factory Vision.txt` at **six byte-identical copies** across the inbound packs. The
sibling repository does **not** have that pathology.

---

# Part 1 — What the two frontier documents actually contain

## 1.1 Provenance, and the thing to notice first (`SOURCE FACT`)

Both documents are dated **1 September 2026** and both name their input explicitly:

> *"Grounded in the current Agent Factory Vision + Beyond Agent Armies frontier architecture
> catalog"* — Prioritization Pack, subtitle
>
> *"The current Agent Factory vision already extends beyond a simple agent orchestrator."*
> — Beyond Agent Armies §1

⭐ **Neither document cites the sibling repository, the Wave 0 synthesis, `RECONCILIATION.md`, or any
finding in `agent-factory`.** Their sole internal input is `Agent Factory Vision.txt` — **the same
file that exists in six byte-identical copies** and whose category framing Wave 0 refuted two days
earlier (2026-08-30). The Prioritization Pack's own §2 claims grounding in *"the current project
inventory established in prior Agent Factory work"*, but every row in that section restates the
Vision's direction; none cites a `file:line`, a ledger, or a measurement.

**This is the single most important fact about both documents, and it is the frame for everything
in Parts 2 and 3.** They are not a second opinion on Wave 0. They are a *more elaborate development
of the premise Wave 0 falsified*, produced without knowledge of the falsification.

## 1.2 What is genuinely new in them (`PROPOSAL`)

Setting the provenance aside, the two documents contribute four things the `agent-factory` corpus
did not previously hold in any form:

**(a) An eight-level organizational ladder with an explicit refusal to make it mandatory.**

| | Level | Purpose |
|---|---|---|
| L1 | Agent | bounded specialist |
| L2 | Agent Team | mission unit |
| L3 | Agent Army | portfolio / domain force |
| **L4** | **Mission Command / Theater** | cross-army campaign command |
| **L5** | **Federation** | sovereign multi-command network |
| **L6** | **Institution / Constitution** | rule-making and legitimacy |
| **L7** | **Ecosystem / Economy** | dynamic allocation, specialization, bidding |
| **L8** | **Agentic Civilization** | multi-institution discovery system |
| Meta | self-hosting organizational substrate | makes all levels programmable |

> *"L4–L8 should not all be mandatory runtime layers. They are optional organizational forms. The
> platform should compile only the minimum structure required by the mission, risk, scale, and
> uncertainty."* — Beyond Agent Armies §2

⭐ **That caveat is the document's best sentence and it agrees exactly with `C-OR-01` (topology as
data).** L4–L8 are new *names* in this corpus; the *discipline* is already `C-OR-01`'s.

**(b) Twelve architecture cards (A–L), each with a stated failure mode and a smallest useful
experiment.** This is the shape `C-OR-04` was a placeholder for. Cards: Recursive Holarchy,
Polycentric Federation, Constitutional Institution Stack, Capability Economy, Collective Cognition /
Global Workspace, Morphogenetic / Stigmergic, Evolutionary Ecology, Temporal Echelons, Shadow Twin,
Bicameral Governance, Mission Hypergraph / Mesh, Self-Hosting Autonomic Organization.

⭐ **The "main failure mode" and "smallest useful experiment" fields are the valuable part.** They
are what `C-OR-04` lacked and what a topology tournament (`GAP-14` / `RB-04`) would need.

**(c) A prioritisation with a stated method (Prioritization Pack §4–5).** Seven weighted dimensions
summing to 100, effort scored separately 1–5, evidence maturity Low/Medium/High. Result:

| Priority | Architectures |
|---|---|
| **P0** | Mission Hypergraph, Constitutional Type System, Shadow Twin, Global Workspace, Bounded Self-Hosting Reconciliation |
| **P1** | Recursive Holarchy, Temporal Echelons, Polycentric Federation, Bicameral Governance |
| **P2** | Capability Economy, Evolutionary Ecology |
| **P3 Lab** | Morphogenetic / Stigmergic |

⚠ **The scores are declared non-measurements by their own author** — *"directional planning
judgments, not measured ROI"* (§4). Treat the **ordering argument** as the contribution and the
decimals (`4.75/5`, `2.90/5`) as decoration. Under `C-VD-03` these figures have basis `ASSUMED`;
they are rendered to two significant figures, which overstates them.

**(d) The Mission Assurance Receipt (Prioritization Pack §9).** A per-mission client-facing artefact
with nine sections — identity, organization+version, execution graph, evidence, independent
challenge, governance, recovery, provenance, outcome.

⭐ **This is the most immediately actionable idea in either document, and it is the one with the
least prior art risk**, because it is a *packaging* of evidence this repository already produces.
See §3.3 below.

## 1.3 What in them is already in `concept_index.yaml`

| Frontier document idea | Existing concept | Relationship |
|---|---|---|
| Org-IR / organizational compiler | `C-OR-02` | identical; the documents add nothing and repeat the refuted framing |
| Organization presets, compile-to-Org-IR | `C-OR-03` | identical |
| Topology chosen per mission signature (§6 table) | `C-OR-01` | the documents give the *selection table* `C-OR-01` lacked |
| Higher-order structures beyond the army | `C-OR-04` | ⭐ **this is C-OR-04's missing content** |
| Stigmergic fields / organizational fields | `C-OR-05` | identical mechanism, richer failure-mode description |
| Collective Cognition / Global Workspace | `C-KN-03` | the documents add the **bounded 20–50 item** constraint and a promotion score |
| Capability Economy / bidding | `C-CM-06` | identical |
| Evolution Chamber / genome search | `C-OP-01`, `C-SM-01`, `C-AG-05` | identical; adds the MAP-Elites / quality-diversity framing |
| Self-hosting reconciliation | `C-SI-01` | identical; adds the **bounded-actions-only** constraint |
| Intent Contract / definition of green | `C-EV-01` | ⚠ the documents call it new substrate; it is **BUILT** here (`factory/contract.py`) |
| Versioned Org-IR + lockfile | `C-AG-04` | identical shape, organization-scale instead of agent-scale |
| Replay / organization debugger | `C-UI-01`, `C-KN-06` | overlapping |
| Provenance + evidence model | `C-EV-06`, `C-KN-01` | ⚠ **BUILT** here (`factory/evidence.py`) |
| Bicameral / adversarial governance | `C-RS-04`, `C-EV-03` | ⭐ `C-EV-03` (grader separation) is the *enforced* version of the same idea |
| Quality-diversity archive | — | **new to this corpus** |
| Temporal echelons / multi-timescale | `C-OR-04` (alias only) | the documents give it a card; the sibling gives it a schema |
| Mission Hypergraph / typed mission graph | — | **new as a named architecture**; but see §4.2 — the mechanism is partly built |
| Shadow Twin / counterfactual organization | `C-EV-10` (`Counterfactual`) | ⚠ related but **not** the same: `C-EV-10`'s `Counterfactual` is a *documentation* object with no `status` field, deliberately un-renderable beside a real outcome. The Shadow Twin is a *runtime* organization. |
| Mission Assurance Receipt | — | **new to this corpus** |
| Constitutional type system / compile-time org legality | — | **new as a mechanism** (`C-GV-02` is the nearest, and is about autonomy surface, not compilation) |
| Organizational immune system | `C-AG-15` (predictive cognitive immunity) | agent-scale exists; organization-scale is new |
| Capability credit graph | `C-KN-05`, and `RB-12` | the documents name it; `RB-12` already exists as a mission |
| Knowledge metabolism / active forgetting | `C-KN-03`, `C-KN-04` | the **decay / forgetting / maintenance-cost** framing is new |
| Eight-level L1–L8 ladder | `C-OR-04` | **new content for an existing concept** |

**Net: five genuinely new concepts** — quality-diversity organization archive, mission hypergraph as
a named architecture, the constitutional type system, the Mission Assurance Receipt, and knowledge
metabolism. These are added to `concept_index.yaml` as `C-OR-06` … `C-OR-08`, `C-KN-07`, `C-GV-06`.

---

# Part 2 — Wave 0, recovered and tagged

Everything in this Part is traced to the sibling repository. Where a claim originates in a source
the sibling itself did not open, that is stated.

## 2.1 The conclusions CN-01 rests on

**W0-1 `PRIOR SYNTHESIS`** — *Artificial Organization Engineering is organisation-oriented MAS,
not a new discipline.* Source: `research/synthesis/W0-foundations.md:31-35`, from `R00` and `R01`.
Named prior art: Moise+ (metamodel), JaCaMo/ORA4MAS (runtime), Gaia/Tropos/INGENIAS (methodology),
a normative layer, a textbook. **Disposition recorded: `RESEARCH ONLY`.**

**W0-2 `SOURCE FACT`** — *The category name is occupied twice in 2026.* `W0-foundations.md:36-39`:
Waites, `arXiv:2602.13275` (Feb 2026); **IMACS**, Chen et al., `arXiv:2607.25446` (28 Jul 2026),
described as *"the organizational-compiler thesis, published"*. Disposition: **`DO NOT BUILD`** the
public category. ⚠ These arXiv ids were verified by the sibling's own citation-audit pass
(`research/sources/W0-audit-prior-art-citations.md`), **not by this pass.**

**W0-3 `SOURCE FACT`** — *`UNMEASURABLE` is TTCN-3's `inconc`, standardised since ISO/IEC 9646
(1991).* `W0-foundations.md:44-46`. The synthesizer states it fetched **ITU-T Z.140 (07/2001) §24.2
and Table 20** directly, after `R02` reported the ETSI edition paywalled. This is the strongest
citation in the wave — a primary standard, opened.

**W0-4 `SOURCE FACT`, and it found a live defect** — *TTCN-3 has a fifth verdict, `error`, for
failure of the test apparatus, which nothing can override.* `W0-foundations.md:47-51` located
`agent-factory/factory/contract.py:57` folding instrument-crash into `UNMEASURABLE`.
⭐ **This has since been fixed** — `concept_index.yaml` `C-VD-01` records commit `ba57f66`
(2026-08-31) adding `ERROR`, and `factory/contract.py:32` now carries it with ERROR dominating FAIL.
**Wave 0 changed this repository's code.** It is the clearest evidence that the sibling's output is
load-bearing and not decorative.

**W0-5 `SOURCE FACT`** — *The most-quoted number in the estate lost its uncertainty in transit.*
`W0-foundations.md:52-55`: −3.5% carries a 95% CI of **[−18.6%, +25.7%]**, **σ = 45.2%**, and the
peer-reviewed title is *"Capable language models can outgrow the benefits of collaboration"* —
capability saturation, not multi-agent inferiority. ⚠ `contradictions.md` **CN-20** is this
disagreement and `RB-04` already owns it.

**W0-6 `SOURCE FACT`** — *There was never a resolvable citation to walk back to.*
`W0-foundations.md:56-58`: `agent-factory/docs/research/` cites via **1,388 opaque ChatGPT tokens
across 7 files**; `R2-answer-topology.md` contains **no arXiv id, DOI or URL at all**.

**W0-7 `PRIOR SYNTHESIS`** — *The nine "different names for the same thing" are nine different
collapses of three orthogonal axes:* **standing** (did the instrument see?), **basis** (how strongly
believed?), **window** (over what period?). `W0-foundations.md:59-62`, from `R02`. Promoted by the
wave as *"the most substantive original contribution of W0"*, and explicitly *descriptive of code
that already exists*. ⚠ This is the sibling's answer to `GAP-05` / `CN-06` / `RB-17` — **and the
`agent-factory` indexes do not currently know it exists.**

**W0-8 `SOURCE FACT`** — *IMACS splits the ontology in two.* Nine terms are **structural**
(binding-independent); four are **configurational** and must carry a model `binding`, because
*"the winning placement flips across model families."* `W0-foundations.md:63-65`.
⭐ **This is the strongest single constraint Wave 0 places on the frontier documents**, and neither
document knows it. See §3.2.

**W0-9 `PRIOR SYNTHESIS`** — *The compiler and debugger are the weakest analogies; version-control
and test-framework are the strongest — and the strongest two are already built.*
`W0-foundations.md:86` (consensus finding C9). Disposition: `RESEARCH ONLY`, and *"stop leading the
vision with the compiler"*.

## 2.2 The Agent → Team → Army hierarchy conclusions

**W0-10 `PRIOR SYNTHESIS`** — *Every surviving novelty claim is about evidence, verification or
governance. Not one is about organizational structure.*
`research/answers/R01-answer-prior-art-and-novelty-boundary.md:934-936`, stated as *"arrived at
from the map rather than asserted"*. The map behind it (R01 Deliverable 4) scores 15 concepts:

| Risk | Concepts |
|---|---|
| **CRITICAL** | Organizational Compiler, Org-IR, Organizational OS, Stigmergic Fields, Morphogenetic Teams, Organizational Debugger, Staff Mesh |
| **HIGH** | Intent Contract, Collective Cognition Fabric, Executable Doctrine, Capability Readiness, Federated Agent Armies |
| **MEDIUM** | Evolution Chamber, Cognitive Logistics |
| **LOW** | **Temporal Echelons** |

⭐ **`Temporal Echelons` is the only `LOW` row in the map** — and what survives as ours is
*"organizational speculative preparation with budget/expiry/relevance/cancellation, measured"*.
That matters for Part 4.

**W0-11 `SOURCE FACT`** — *PROSA (Van Brussel et al., 1998) contains "staff holons"* — the Staff Mesh
under the same word, and PROSA's are **centralised**, which independently establishes that
*"Staff Mesh" names the opposite of its own design*. `W0-foundations.md:40-43`;
`R01:86-87, 599-601`. ⚠ The sibling's own audit pass rates this claim `B (DERIVED)` —
*"I did not read the paper"* (`R01:1287`). **A characterisation, not a verified quotation.**

**W0-12 `PRIOR SYNTHESIS`** — *Supervisor tiers are `DO NOT BUILD`.* `W0-foundations.md:220-221`:
*"still gated on one certified team, unmet, and the peer-reviewed title now argues the gain shrinks
as models improve."* ⭐ **This is the sibling's direct verdict on adding levels above the team**, and
it is the sharpest available counter to the frontier documents' L4–L8 ladder.

## 2.3 Non-hierarchical topology

**W0-13 `SOURCE FACT`** — Prior art exists at CRITICAL risk for *every* non-hierarchical mechanism
the frontier catalog proposes: digital pheromone infrastructure (2000–02) and Co-Fields/TOTA
middleware (2004–09) for stigmergic fields; Organization Self-Design (1992) and Morphogenetic
Engineering (2012) for morphogenetic teams; KB-ORG (2008) for the compiler; Grid virtual
organizations (2001) and FIPA for federation. `R01` Deliverable 4 table.
⭐ **For Stigmergic Fields, R01's "what survives as ours" column reads: `Nothing at the mechanism
level. Domain signal choice only.`**

**W0-14 `PRIOR SYNTHESIS`** — Recommended renames, from `R01` Deliverable 5. Seven of these directly
strike names the frontier documents use:

| Frontier document says | Wave 0 says use | Why |
|---|---|---|
| Organizational Compiler | **Organization Synthesiser** | *"compiler over-promises determinism we do not have"* |
| Org-IR | **Organization Specification** (structural / functional / deontic, after Moise+) | the three-way split is a design improvement, not a rename |
| Collective Cognition (Fabric) | **Knowledge and Evidence Store** | our usage inverts the industry senses of *fabric* and *mesh* |
| Stigmergic / organizational Fields | **Coordination Fields** | keeps the mechanism, drops the implied invention |
| Morphogenetic Teams | **Adaptive Team Formation** | plain, searchable, honest about lineage |
| Evolution Chamber | **Organization Design Lab** | removes the StarCraft collision; "lab" correctly implies offline |
| Temporal Echelons | **Planning Horizons** (NOW / NEXT / LATER) | *"echelon means command level, not time horizon"* |

Plus **forbidden**: `"Organizational OS"` (collides with trademarked **EOS®**), `"Executable
Doctrine"` (Doctrine PHP ORM), `"Cognitive Logistics"` (EU H2020 project), and `Organizational
Digital Twin` — rated **BLOCKING**, because *"we would be entering a defined analyst category
(Gartner DTO Magic Quadrant), against funded incumbents, with no differentiator stated."*

## 2.4 Collective cognition and shared knowledge

**W0-15 `PROPOSAL`** — the sibling's Collective Cognition Fabric is a layer of
*claims / evidence / knowledge / skills / capabilities / doctrine*
(`architecture/00-target-architecture.md`). Novelty risk **HIGH**; what survives is the
**Observation → Claim → Evidence → Knowledge promotion with `sourceRootId` independence tracking**
(`R01` Deliverable 4).

**W0-16 `SOURCE FACT`** — ⛔ **`Claim` was deprecated by Wave 0.** `W0-foundations.md:97, 126`:
the vocabulary crawl measured **four live senses in one codebase** (lane lease / task status / bus
kind / prose). The code already names the research sense `Assertion` (`factory/contract.py:41`).
⚠ **This directly contradicts the frontier documents and the sibling's own `architecture/10`
federation draft, both of which use `Claim` as a first-class crossing object.**

**W0-17 `PROPOSAL`** — `ContextPackage` → adopt **`ContextPack`/`ContextRef`** as they exist in
`agent-factory/factory/context.py:121,:71` — *"built, tested, and already carrying a mandatory
`source`, freshness state and confidence."* `W0-foundations.md:121-122`.
⭐ **The prioritization pack's "bounded global workspace" P0 has a partially-built substrate here
and does not know it.**

## 2.5 Self-improving / self-maintaining organizations

**W0-18 `SOURCE FACT`** — the sibling's own draft law: *"Simulation Precedes Evolution — self-
optimization should first occur in replay, simulation and shadow environments"*
(`foundations/FOUNDATIONAL_LAWS_DRAFT.md`, Law 9). ⚠ But `W0-foundations.md:192` records that
**Law 9 was assessed vacuous** and Law 6 **falsified** (*routine as truce* is a political settlement
between people with interests; agents have none). Laws 1/3/5 weakened; **only Law 4 holds**
("context is a resource, not a transcript" — and `context.py` already implements it).

**W0-19 `SOURCE FACT`** — ⛔ **The simulation substrate does not exist anywhere.**
`repo-boundary/PRODUCT-BOUNDARY.md`, Layer 5, measured 2026-08-30:

> *"Of roughly fourteen components, none is ecosystem-ready and seven are partial. The simulation
> substrate is the one load-bearing safety component that is entirely absent, so a roadmap putting
> the evolution chamber first still proposes to evolve an organization with no sandbox."*

**W0-20 `PROPOSAL`** — ⭐ **The product boundary generalises the grader-separation rule to
organizations:**

> *"An agent that can edit its own grader is not graded"* → *"An organization that can certify its
> own capabilities is not certified."* … *"evolution proposes, the factory disposes."*

This is `C-EV-03` scaled up, and it is the sharpest available constraint on the frontier documents'
Self-Hosting Autonomic Organization card.

**W0-21 `SOURCE FACT`, a correction worth carrying** — `PRODUCT-BOUNDARY.md` originally recorded the
policy-enforcement point as `ABSENT`; it was **corrected 2026-08-30** because the inventory *"was
taken across `agent-factory` and this repository and never opened `conductor`"*.
`conductor/engine/work_guard.py` is a real enforcement point with a declarative policy
(`conductor/config/work-guard-policy.json`: `blockedPaths`, `approvalRequiredFor`,
`highRiskRequiresApproval`, `staleLockBehavior: "require-approval"`), and its `safe_to_run(repo_path)`
is *"an `admit()`-shaped function that already exists."*
⭐ **This is `C-PR-02` (an inherited premise is a hypothesis) and `C-VD-02` (a blind instrument) in
one event — four components were reported ABSENT by an instrument that could not see them.** It is
the sibling's own commit `ecbcdb0`.

## 2.6 Evaluation and simulation

**W0-22 `SOURCE FACT`** — three experiments are specified and **none has been run**
(`W0-foundations.md:227-232`):

| ID | Hypothesis | Stop condition |
|---|---|---|
| **E1** | a harness-error verdict changes gate outcomes | if zero change across 30 gates, the distinction is real but inert here — record and stop |
| **E2** | the three axes are genuinely orthogonal | if any of the nine vocabularies needs a fourth axis, the model is wrong |
| **E3** | configuration flips across model bindings *in our estate* | if it does not flip in 2 model families, IMACS may not generalise here |

⭐ **E1 is now partly answered by events, not by the experiment**: `ERROR` was added in `ba57f66`.
Whether it changed a gate outcome was never measured. **E1 is cheap, ready, and unrun.**

**W0-23 `PROPOSAL`** — the Evolution Chamber's promotion chain
(`architecture/11-evolution-chamber-architecture.md`): `offline simulation → historical replay →
shadow → limited live → production`, with an explicit **mutation prohibition** — constitution, hard
permissions and audit rules are **not in the genome**. ⭐ Compare the Prioritization Pack's G0–G7
gates (§3.4): the two chains were written independently and **agree**.

## 2.7 Unresolved questions the sibling itself records

| | `UNRESOLVED` |
|---|---|
| U1 | **`Mandate`'s enforcement gate** — is there any boundary in the system that can actually enforce authority? If not, the term demotes to `RESEARCH ONLY`. ⚠ **`W0-21` above is the beginning of an answer and the two have never been connected.** |
| U2 | ISO 26262 / DO-178C verification vocabularies are **paywalled and unread**. A further kill on the verdict lattice could come from there. |
| U3 | **ODML must be re-sourced** — it is a predictive design model targeting Mathematica, not an IR. The Org-IR verdict survives on Moise+/OperA/AGR, not on R01's headline sentence. |
| U4 | The **ORA4MAS enforcement quote is behind a paywall** and its chapter subtitle points the other way. `NOT-ACCESSIBLE`. |
| U5 | Four primary PDFs in R00 are **scanned images** — declared, still a gap. |
| U6 | *(this pass)* **595 KB of the sibling's markdown was not read.** See §0.2. |

## 2.8 Method finding the reviewer should carry

**W0-24 `SOURCE FACT`** — `W0-foundations.md:259-269`: **two WebFetch summaries were wrong in this
wave, in opposite directions.** One reported no sample-size passage in `arXiv:2606.03034` (there is
one — reading the PDF killed a novelty component); one reported an empty arXiv `journal-ref`, from
which the synthesizer wrongly concluded `UNSUPPORTED` on a Nature paper that exists (retitled).

> *"A fetch summary is a lead, not evidence. … Both kills that mattered most in this wave came from
> opening the file."*

⭐ This is `C-RS-05` and `C-VD-02` measured in the wild, and it is the reason the citation ids in
§2.1 are tagged as verified-by-the-sibling rather than verified-here.

---

# Part 3 — Where the two documents and Wave 0 collide

This is the substance of the pass. Five collisions, each with the evidence on both sides.

## 3.1 The frontier documents restate the premise Wave 0 falsified

**They say:** *"Organizational Compiler / Org-IR: a typed intermediate representation for roles,
topology, tools, gates, budgets, memory, and metrics"* is the meta-substrate that makes everything
else programmable (Beyond Agent Armies §1, §11; Prioritization Pack Phase A).

**Wave 0 says:** the category is occupied (`W0-2`), the compiler is the *weakest* of the analogies
(`W0-9`), KB-ORG (2008) already did fully-automated knowledge-based organization design, and Org-IR
carries **CRITICAL** novelty risk against ODML / Moise+ / OperA / AGR (`W0-10`).

**Weight.** Wave 0 is stronger, and for a stated reason: it cites primary sources and its own audit
pass re-checked them; the frontier documents cite a model-generated vision file and add a source
table (Beyond Agent Armies §12) whose entries are *anchors*, explicitly *"they do not establish
novelty of the proposed combinations"*.

⛔ **But this changes CN-01 less than it looks.** Both sides of CN-01 already exist; the frontier
documents add **weight to Side A's volume and nothing to Side A's evidence.** ⭐ **The correct
reading is that CN-01's evidence balance is UNCHANGED and its Side A is now better characterised:**
`contradictions.md` should record that Side A's strongest available statement has been read and is
still un-evidenced. See §3.5 for what *does* change.

## 3.2 IMACS's model-binding result invalidates a premise of the prioritisation

**`W0-8`**: four ontology terms are **configurational** and must carry a model `binding`, because
*"the winning placement flips across model families."* `H09` is **SUPPORTED** on the IMACS ablation.

**The Prioritization Pack's ranking assumes the opposite.** Its scorecard assigns a single
`4.55/5`-style value per architecture with no binding dimension, and its Phase F proposes org-genome
search producing certified presets. **If organizational configuration is model-binding-specific,
every search result expires with the binding**, which is precisely `H07`'s recorded sting:

> *"SUPPORTED, with a sting … every learned result is model-binding-specific and expires with the
> binding."*

⭐ **This is a real, new, material conflict, and it is the strongest thing this pass found.** It does
not kill the roadmap; it means **Phase F's output has a shelf life nobody has measured**, and that
the scorecard needs a per-binding column or an explicit statement that scores are binding-agnostic
claims. Recorded as **CN-29**.

## 3.3 On the things Wave 0 says survive, the two documents *agree* — and that is the finding

`W0-10`: *"Every surviving column entry is about evidence, verification or governance. Not one is
about organizational structure."*

Now read the Prioritization Pack's P0 list on the same axis:

| P0 architecture | Structure, or evidence/verification/governance? |
|---|---|
| Constitutional Institution / Type System | **governance** |
| Shadow Twin / Counterfactual Organization | **verification** |
| Bounded Self-Hosting Reconciliation | **governance** (quarantine, rollback, certification) |
| Collective Cognition / Global Workspace | evidence propagation — **evidence** |
| Mission Hypergraph / Mesh | structure — **but see §4.2** |

⭐ **Four of five P0s are exactly what Wave 0 says survives.** Two documents written from opposite
premises, with no knowledge of each other, converge on the same near-term list. That convergence is
**the most decision-relevant fact this pass produced**, and it is much stronger evidence than either
document alone, because the two are genuinely independent (§1.1 establishes the frontier documents
did not read Wave 0; `W0-foundations.md`'s source list establishes Wave 0 did not read them).

⚠ **Do not overstate it.** Both were produced by language models from overlapping training
distributions. `C-RS-06` applies: *repeated AI claims are not independent evidence.* What is
independent here is the **input corpus**, not the reasoner. Tier this as **`DERIVED`, medium
confidence**, not as corroboration by two instruments.

## 3.4 The two promotion-gate chains agree, independently

| Prioritization Pack §12 | Sibling `architecture/11` |
|---|---|
| G0 Representable → G1 Replayable → G2 Measurable → G3 Safer than baseline → G4 Pareto useful → G5 Shadow proven → G6 Canary proven → G7 Preset/certified | offline simulation → historical replay → shadow → limited live → production, with a mutation prohibition on constitution/permissions/audit |

⭐ Same shape, same order, same refusal to let anything reach production without a shadow stage.
`W0-20`'s *"evolution proposes, the factory disposes"* is the rule both chains encode.
**This is a settled design, not an open question**, and the architecture synthesis can treat it so.

## 3.5 What the documents contribute that Wave 0 does not touch

Wave 0 attacked *novelty*. It never asked *what to build first*. The Prioritization Pack does, with
a stated method, an effort axis, an evidence-maturity axis, and — §11 — an explicit **"what I would
explicitly not build yet"** list:

> *"A literal eight-level always-on command hierarchy … a full capability marketplace before you
> have several certified substitutable teams … automatic organizational mutation in production …
> an unrestricted 'self-healing agent' … all-to-all shared memory … a flashy civilization/swarm
> visualization that is not backed by typed mission/organization state … client-facing novelty
> claims around holarchies, markets, stigmergy or evolution until prior-art research has classified
> what is actually new."*

⭐ **That last clause is the frontier document asking for exactly the work Wave 0 already did.**
It is also the cleanest possible answer to CN-01's remainder: the Prioritization Pack and Wave 0
agree on the *disposition* (don't claim it, don't launch the category) while disagreeing on whether
the underlying mechanism is worth building — and on that, **both say build the mechanism**.

---

# Part 4 — Goal-Aware Adaptive/Dynamic Orchestration: the prior art

⛔ **Nothing here designs or endorses the concept.** The override asks one question — *does prior
research already contain equivalent, overlapping, supporting or conflicting concepts?* — and the
answer is **yes, extensively, in three places, and one of them is a hard theoretical limit.**

## 4.1 The hard limit — read this before designing anything

**`SOURCE FACT`, and it is the most important item in this Part.**
`docs/research/SYNTHESIS.md:1380-1394`, clause one, upgraded from a survey to a proof:

> *"Blumofe & Leiserson close it formally: **every topology is a scheduler, schedulers redistribute
> `T₁/P`, none touch the critical path `T∞`** [E-1]."*

and, in the same passage:

> *"under a conflict graph the instantaneous ceiling is the maximum independent set α(G), scheduling
> everything into rounds is bounded graph colouring, and the scheduling literature proves the problem
> generalises graph colouring and is strongly NP-hard [A-24 ✓, A-25]. A topology is a decision
> procedure over who runs when — it cannot select more than α(G) pairwise-non-adjacent vertices
> because there aren't any. … **concurrency comes from touching disjoint data, not from a better
> scheduler** [A-27]."*

and:

> *"Contract-net answers itself — auctions solve assignment under uncertainty about capability or
> cost, and with a known static graph and homogeneous agents there is nothing to discover
> [A-58, A-59]."*

**What this does and does not say about the new concept.**

| It refutes | It does not refute |
|---|---|
| that a smarter scheduler shortens a mission whose dependency graph is fixed | that a scheduler can **change the graph** — which is exactly what *scope degradation* and *replanning* do |
| that adaptive allocation raises the parallelism ceiling | that adaptive allocation improves **which** work gets done under a deadline |
| bidding/market allocation over a known static graph with homogeneous agents | bidding under genuine uncertainty about capability or cost — the paper's own stated precondition |

⭐ **The honest framing of Goal-Aware Adaptive Orchestration is therefore not "a better scheduler".
It is "a mechanism that mutates `T∞` by changing scope, evidence requirements or gates."** Anything
that leaves the goal fixed and reorders the work is, by this result, already known to be bounded.
**A design that does not state which side of that line it sits on cannot be evaluated.**

## 4.2 What is already BUILT in this repository

⭐ **This is the surprise of the pass: four of the fourteen listed sub-concepts are implemented and
running, and the frontier documents propose the same things as new P0 substrate.**

| Sub-concept from the override | Status | Evidence |
|---|---|---|
| **dynamic critical paths** | **BUILT** | `factory/board.py:108 critical_path()` computes the longest dependency chain over the live gate set; `factory/roadmap.py:276` renders it *"with each hop's live status — the sequence parallelism cannot remove"*; `factory/flow.py:52` draws it |
| **adaptive task prioritization** | **BUILT** | `factory/coordination.py:100 prioritise()` — orders human interventions by *"what an answer would actually unblock"*, from four measured factors: transitive downstream-blocked count (`downstream_blocked()`, `:80`), critical-path membership, wait time, and whether the asking session is alive |
| **mutable DAGs** | **BUILT, and recently** | `docs/findings.d/F98…` — ticket-level `blocked_by` was surveyed as *"exists and is unused"* across 189 events and now carries **25 block edges** written by `scripts/mission_marketing_model.py` holding the live mission critical path. Regenerate: `python -c "import json; ev=[json.loads(l) for l in open('.data/tasks.jsonl',encoding='utf-8') if l.strip()]; print(len(ev), sum(1 for e in ev if e['kind']=='block'))"` |
| **deadline-aware scheduling** | **BUILT — as a refusal** | `factory/schedule.py`. ⭐ It **declines to emit a completion date** until scope velocity settles, with a stated criterion (`SETTLED_HOURS = 24.0`), because *"an ETA computed from pass-rate alone divides by a denominator that is still growing, and every such estimate flatters"*. It reports the target as `NOT-SET` rather than inventing one: *"No deadline has been stated anywhere in the programme."* `--target YYYY-MM-DD` makes it measurable immediately |
| **dynamic human gating** | **PARTIAL** | `factory/coordination.py` bands interventions HIGH/MEDIUM/LOW; `C-GV-03` (human gates that refuse rather than render) is the enforced half. `conductor/config/work-guard-policy.json` carries `approvalRequiredFor` / `highRiskRequiresApproval` (`W0-21`) |
| **automatic downstream execution** | **PARTIAL** | `downstream_blocked()` computes the transitive set; nothing acts on it automatically |

⛔ **Consequence for the review: the Prioritization Pack's P0 #1 (Mission Hypergraph / Mesh) is
scored `Effort 3/5, Evidence High` as if greenfield. Its "minimum valuable implementation" —
*"compile the existing production DAG plus agent handoffs into typed MissionNode/MissionEdge/
Artifact/Evidence objects"* — is materially already done at gate scale and partly at ticket scale.**
That does not make the card wrong; it makes its **effort estimate wrong in this estate**, and
`current_vs_proposed.md` is where that belongs.

⚠ **Counter-evidence against over-reading this.** `factory/coordination.py`'s own docstring is
explicit that these are *ingredients, not an aggregate*: *"There is no coordination-tax percentage
here, and that is the point."* And `prioritise()` bands are *"deliberately coarse"* because *"the
weighting between 'blocks four items' and 'has waited twenty minutes' is a judgement nobody has
validated."* **Nothing has measured whether the ordering it produces is better than any other.**

## 4.3 What exists as prior research

| Sub-concept | Where | Tag |
|---|---|---|
| **goal contracts** | `C-EV-01` GreenContract (**BUILT**, `factory/contract.py`) is the falsifiable half. The sibling's `architecture/01-intent-contract-schema.md` is the full object: `desiredEndState`, `invariants` (`hard`/`soft`, `block`/`warn`/`escalate`), `authorityEnvelope` with `maxAutonomyLevel: manual\|suggest\|guarded_auto\|autonomous`, `riskTolerance`, `BudgetEnvelope` (`maxCostUsd`/`maxTokens`/`maxRuntimeSeconds`/`maxAgents`), `escalationConditions` | `PROPOSAL` |
| ⛔ **and Wave 0 rejects merging them** | `W0-foundations.md:99` — *"a GreenContract's fold is meaningful only because every member is falsifiable; adding permissions breaks the property the object exists for."* Adopt the **three-way split `Contract` / `Mandate` / `Task`**, with `Mandate` behind a hard enforcement gate | `PRIOR SYNTHESIS` |
| **event-driven replanning** | `Agent Factory Vision.txt` (six copies — **one source**), `agent_factory_agent_genome_research_pack/schemas/agent_genome.schema.yaml`, `R5-answer-build-velocity.md`, `R16-evidence-pack.md`. No mechanism specified in any | `SPECULATION` |
| **elastic team composition** | `C-TM-04` adaptive team formation, `C-OR-03` presets. ⚠ Wave 0 renames this **Adaptive Team Formation** and rates the "morphogenetic" framing **CRITICAL** risk against Organization Self-Design (1992) | `PROPOSAL` |
| **resource-aware scheduling** | `architecture/03-cognitive-logistics.md` — context/knowledge/skills/tools/permissions/models/tokens/compute/sandboxes/API quotas/**human attention**/**verification capacity** as rationed supplies, with a `capability_readiness` record carrying an explicit `blocker` field. Novelty risk **MEDIUM**; what survives is *"verification capacity and human attention treated as rationed supplies with readiness blockers"* | `PROPOSAL` |
| **adaptive communication** | `agent-config-research-pack/00-executive-assessment.md`, `01-idea-portfolio.md`, `05-research-and-build-sequence.md`; `agent_factory_agent_genome_research_pack/experiments/EXPERIMENT_BACKLOG.md`. Related to `C-AG-05` communication phenotypes | `PROPOSAL` |
| **goal drift detection** | ⚠ **Only two occurrences in the whole corpus**, both the same sentence, quoted from an external survey: `R13-answer-architecture-and-ui-survey.md:11` and `R16-evidence-pack.md:5786` — *"Hierarchical (Supervisor Trees) … Failure: 'goal drift' between layers or bottlenecks at higher levels."* **It is named as a failure mode of hierarchy and never developed.** No detector, no metric, no definition | `SOURCE FACT` (that it is absent) |
| **scope degradation as deadlines approach** | ⛔ **ZERO occurrences** — `grep -riE "scope degrad"` returns nothing in either repository. The nearest thing is `admit() → DEGRADED` in `repo-boundary/PRODUCT-BOUNDARY.md`, which degrades on **missing capability**, not on **elapsed time**, and whose author is explicit: *"`DEGRADED` is not an error state. `staffing.unstaffable` is the runtime telling the factory what to build next."* | `SOURCE FACT` (absent) + `PROPOSAL` (the adjacent mechanism) |
| **deadline-aware scheduling, as a stance** | `R16-evidence-pack.md:4956` — *"you should aim to converge the backlog … a useful metric is the intake-to-throughput ratio: when it stays near 1 for a sustained period, scope is stabilizing. Freezing too early risks missing vital tasks; freezing too late means endless replanning."* ⭐ This is the same criterion `factory/schedule.py` implements as `scope_settled` | `PRIOR SYNTHESIS` |
| **temporal echelons / planning horizons** | `architecture/05-temporal-echelons.md`: `HorizonWorkItem` with `horizon: now\|next\|later`, `dependencies`, `promotionCriteria`, `expiry`; promotion `LATER→NEXT` on relevance, `NEXT→NOW` on dependency gates; guardrail requiring **budget, expiry, relevance threshold and cancellation path**; metrics *critical-path idle time, speculative waste, promotion accuracy, setup latency, **replanning frequency*** | `PROPOSAL` |
| ⭐ **and this is the lowest-prior-art-risk item in the whole map** | `R01` Deliverable 4 rates Temporal Echelons **LOW**, the only LOW row, surviving as *"organizational speculative preparation with budget/expiry/relevance/cancellation, measured"*. Precedents named: anytime algorithms + deliberation scheduling (1988), speculative execution, planning horizons | `PRIOR SYNTHESIS` |
| ⚠ **but its hypothesis was weakened** | `H04` — *"NOW/NEXT/LATER cells reduce critical-path idle time"* — is **WEAKENED**, because `Cell` was deleted from the ontology. *"Restate without `Cell` or drop."* | `PRIOR SYNTHESIS` |
| **the concept as a whole** | ⛔ Prompt **`R36-temporal-echelons-multi-horizon-agency.md`** and **`R37-cognitive-logistics-and-readiness.md`** exist in the sibling and are **`NOT_RUN`**. So is **`R31-frontier-organizational-primitives.md`**, which lists `temporal echelons`, `capability readiness` and `organizational metabolism` among its candidate primitives | `SOURCE FACT` |

## 4.4 The prior-art verdict on the new concept

**Stated in the corpus's own vocabulary, and deliberately unflattering:**

1. `SOURCE FACT` — **No term in the fourteen-item list is novel to this corpus.** Twelve have named
   prior art; four are already built here; one (`goal drift`) exists only as a quoted failure mode;
   one (`scope degradation as deadlines approach`) has **zero occurrences anywhere** and is the only
   genuinely unrepresented idea in the list.
2. `PRIOR SYNTHESIS` — **The scheduling half is bounded by a proof this corpus already holds**
   (§4.1). Reordering fixed work cannot beat `T∞`.
3. `PRIOR SYNTHESIS` — **The goal half runs into Wave 0's type argument** (`W0`, §4.3): authority,
   budget and deadline are `Mandate`, not `Contract`, and folding them into a falsifiable object
   destroys the property that object exists for.
4. `UNRESOLVED` — **the one thing the corpus does not contain**: a mechanism that *trades scope for
   time under a deadline*, with a stated basis for what may be dropped and who may authorise it.
   `admit() → DEGRADED` is capability-triggered; `schedule.py` refuses to name a deadline at all;
   `HorizonWorkItem` has an `expiry` but no scope-reduction rule.
5. ⛔ `SOURCE FACT` — **there is no deadline anywhere in the programme to be aware of.**
   `factory/schedule.py:26`: *"'Ahead or behind schedule' needs a target, and there isn't one. No
   deadline has been stated anywhere in the programme."* **A goal-aware, deadline-aware orchestrator
   has no input in this estate today.** That is a one-line fix (`--target`), and it is a precondition,
   not a detail.

**Recorded as `GAP-43` and as concept `C-TM-06` (proposed, no implementation, prior art named).
It is NOT claimed as novel and it is NOT dispatched.**

---

# Part 5 — What this supplement does NOT do

| | |
|---|---|
| ⛔ | **Resolves nothing.** CN-01 stays open. One new contradiction (CN-29) is *opened*, not settled. |
| ⛔ | **Dispatches nothing.** No mission in `docs/research/backlog.yaml` was launched. |
| ⛔ | **595 KB of the sibling's markdown is still unread** — including the entire 89 KB vocabulary crawl and the 30 KB adversarial-refutation source, whose conclusions reached this pass only through the synthesis that quotes them. |
| ⛔ | **Eight figures in `Beyond_Agent_Armies…docx` were not extracted.** Their captions are preserved; the diagrams are not read. |
| ⛔ | **No arXiv id, DOI or paper cited by Wave 0 was verified by this pass.** Every one is `PRIOR SYNTHESIS` at best, and `W0-24` is the reason that distinction is kept. |
| ⛔ | **`R00`, `R02` and the vocabulary crawl were sampled, not read.** The three-axis model (`W0-7`) is reported as the synthesis states it; its derivation was not checked. |
| ⛔ | **Five of the sibling's thirteen `architecture/*.md` stubs were not opened** (§0.2). One of them, `06-knowledge-evidence-model.md`, is named by `PRODUCT-BOUNDARY.md` as the **highest-priority convergence risk** between the two repositories — *"if these diverge, the field record cannot be diffed against the capability record and the feedback loop silently stops working."* It is 1,187 bytes and should be the next thing anyone reads. |
| ⚠ | **This pass corrected itself twice, in public, on its own numbers.** It first wrote *"12 dependency edges"* for the gate DAG (measured: **11**, and `factory/flow.py`'s own docstring is the source of the wrong figure) and *"all twelve architecture files read in full"* (measured: **13 files, 8 read**). Both are recorded rather than quietly fixed, because `C-VD-04` predicts exactly this and a supplement that made the error while documenting the rule is the useful version of the evidence. |
