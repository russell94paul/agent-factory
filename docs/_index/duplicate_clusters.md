# Duplicate clusters — documents covering substantially the same subject

**Generated 2026-09-02** against `agent-factory` @ `fc78074`.

⛔ **NOTHING HERE IS DELETED, MERGED OR MOVED.** This file records where the corpus says the same
thing more than once and classifies *what kind* of repetition it is, because the kinds have
completely different consequences:

| Kind | What it means | What to do with it |
|---|---|---|
| **Direct duplicate** | Byte-identical, or identical in substance | Read one. Know the others exist so a "third independent source" is not counted. |
| **Revision** | A later treatment supersedes an earlier one | Read the later. The earlier is history, and several are kept on purpose. |
| **Complementary** | Same subject, different halves | Read both. Neither is redundant. |
| **Contradictory** | Same subject, incompatible conclusions | See [`contradictions.md`](contradictions.md). Recorded there, not resolved here. |
| **Independent treatment** | Same idea reached separately | ⭐ **The most valuable kind.** Independent arrival is evidence — but only if the sources really were independent. |

**Exact duplicates were MEASURED**, not eyeballed:

```bash
python - <<'PY'
import pathlib, hashlib, collections
seen = collections.defaultdict(list)
for r in ('docs', '.agent-platform', 'blueprints', 'missions', 'evals', 'boot-prompts'):
    for p in pathlib.Path(r).rglob('*'):
        if p.is_file():
            seen[hashlib.sha256(p.read_bytes()).hexdigest()].append(p.as_posix())
for h, v in seen.items():
    if len(v) > 1:
        print(len(v), v)
PY
```

That returns **22 groups** of byte-identical files. They are clusters DC-01, DC-06, DC-07, DC-08
and DC-10 below.

---

## DC-01 — `Agent Factory Vision.txt` · **DIRECT DUPLICATE, ×6**

**MEASURED: six byte-identical copies, 21,179 bytes each, sha256 identical.**

```
.agent-platform/bootstrap/source/Agent Factory Vision.txt
docs/raw_research/agent-factory-bootstrap-pack/docs/01-research-corpus/raw/source-snapshots/Agent Factory Vision.txt
docs/raw_research/agent_factory_agent_genome_research_pack/source/Agent Factory Vision.txt
docs/raw_research/agent_factory_agents_as_configuration_research_pack/06_SOURCE_MATERIAL/Agent Factory Vision.txt
docs/raw_research/agent_factory_army_ui_concept_pack/sources/Agent Factory Vision.txt
docs/raw_research/agent_factory_chat_design_pack/legacy_reference/Agent Factory Vision.txt
```

**Classification: direct duplicate.** Each pack shipped its own copy of the same source
conversation.

⛔ **This is the single most consequential duplication in the corpus, and it is not a tidiness
problem.** Five separate research packs propose Org-IR, a Collective Cognition Fabric, an Evolution
Chamber and organization presets. That reads as five sources converging. It is **one source,
reformatted five times.** The bootstrap pack's own manifest states the rule that this violates:
`repeated_ai_claims_are_not_independent_evidence`.

**Disposition:** keep all six — each pack is preserved as it arrived. Cite
`.agent-platform/bootstrap/source/` as the reference copy. Never count two packs that derive from
this file as independent corroboration of anything.

---

## DC-02 — Two different "bootstrap packs" · **COMPLEMENTARY, with a name collision**

| | `.agent-platform/bootstrap/` | `docs/raw_research/agent-factory-bootstrap-pack/` |
|---|---|---|
| Files | 110 | 44 |
| Installed | 2026-08-31, verbatim, 109/109 manifest files | 2026-09-01, as raw research |
| Purpose | An **autonomous build** pack: vision, rank roadmap, skills, research waves, venture material | A **corpus-preparation** pack: manifest/registry/evidence/decision/implementation scaffolding |
| Entry point | `START_CLAUDE_HERE.md` | `docs/08-research-backlog/prompts/CLAUDE_CORPUS_PREPARATION_PROMPT.md` |
| Reconciled | ✅ `.agent-platform/RECONCILIATION.md` + `PACK_CONFORMANCE.md` | ⛔ **never reconciled** |

**Classification: complementary, sharing a name and a concept vocabulary.** Both propose Org-IR,
Collective Cognition, an Evolution Chamber and organization presets; both derive from DC-01. But
one is asking the repository to *build* and the other to *index*, and only the first was audited.

⚠ **The asymmetry is the finding.** The `.agent-platform` pack was subjected to an
instruction-by-instruction conformance audit with four recorded deviations. The `raw_research`
bootstrap pack was extracted and left. Its templates are still empty (`artifacts: []`,
`concepts: []`, a 0-byte `claims.jsonl`) — this `docs/_index/` directory is the work they asked for,
done in a different shape.

**Disposition:** keep both. A reviewer comparing them learns more from the *pair* than from either.

---

## DC-03 — The two "agents-as-configuration" packs · **COMPLEMENTARY, and one is far stronger**

| | `agent-config-research-pack/` (21 files) | `agent_factory_agents_as_configuration_research_pack/` (16 files) |
|---|---|---|
| Read the repository? | ✅ **Yes** — cites `blueprint.py`, `presets.py`, `metrics.py`, `registry.py`, `readiness.py`, `handoff.py`, `bus.py` and the `.agent-platform` schemas by path | ❌ No |
| Integrity | ✅ ships `SHA256SUMS.txt` | ❌ none |
| Has a "do not implement literally" section | ✅ **Yes**, five entries | ❌ No |
| Central move | *"Extend those seams. Do not create a parallel configuration product."* | Concept-first: health vectors, READY-UP, phenotypes, resident agents |

**Classification: complementary — same thesis, incompatible epistemic standards.**

⚠ **They also contradict each other.** The concept-first pack proposes READY-UP (raising readiness
before deployment); the repository-grounded pack lists *"artificially increasing all health scores
before deployment"* under ideas that must not be implemented literally, because *"this corrupts the
instrument."* See [`contradictions.md`](contradictions.md) **CN-04**.

**Disposition:** keep both. Weight `agent-config-research-pack` higher on every question where they
differ — it is the only inbound pack that measured before proposing.

---

## DC-04 — "Agent Genome" in two packs · **COMPLEMENTARY, different depth**

- `agent_factory_agent_genome_research_pack/` (22 files) — the deep treatment: the four-layer model,
  the five field classes, the agent registry and lockfile, relationship edges, communication
  phenotypes, a 25-item experiment backlog.
- `agent_factory_rd_consolidation_pack/02_AGENT_GENOME.md` (2.8 KB) — a summary within a broader R&D
  pack that also covers HyperMESH, optimization and self-hosting.

**Classification: complementary.** The genome pack is the depth; the R&D pack is the breadth and
places the genome in a wider architecture. No contradiction found between them.

**Disposition:** keep both. Read the genome pack for the mechanism, the R&D pack for the context.

---

## DC-05 — Research passes run twice · **COMPLEMENTARY, and deliberately so**

| Pass | Files | Relationship |
|---|---|---|
| R4 | `R4-answer-agnostic-optimizer.md` (52 KB) + `-run2.md` (57 KB) | **Corroboration.** SYNTHESIS §7.4: two independent runs, same verdict from different framings, no material contradiction; run 2 is longer on cost and isolation. |
| R13 | `R13-answer-architecture-and-ui-survey.md` (27 KB) + `-run2.md` (17 KB) | **Revision-by-extension.** Run 2 answers the four questions run 1 left open; it does not replace run 1. |
| R16 | `R16-answer-decision-review-and-order.md` (30 KB) + `R16-outside-evidence-lane.md` (40 KB) | **Complementary halves.** One attacks the decisions from inside, one from external evidence — and the outside lane **attacks the action three passes had agreed on.** |

**Classification: complementary.** The house rule is explicit — *"file the raw answer, do not
summarise it; the disagreements between passes are the most useful part."*

**Disposition:** keep all six. Merging any pair would destroy the comparison that makes them
worth having.

⚠ **One caution on R4:** two runs of the same prompt against the same literature are *not*
independent in the sense that matters. Treating their agreement as corroboration is exactly the
move SYNTHESIS §15.5 later had to retract in a different case.

---

## DC-06 — The ZEUS / Army-world UI material · **DIRECT DUPLICATE ×3 plus REVISION**

**MEASURED: 13 files exist byte-identically at three paths each**, plus the 56 KB single-file
consolidation, also at three paths:

```
docs/raw_research/zeus_world_ui_research_pack/                              ← the reference copy
docs/raw_research/agent_factory_army_ui_concept_pack/prior_research/…       ← identical
docs/raw_research/agent_factory_chat_design_pack/legacy_reference/…         ← identical
```

Plus an **internal** duplicate: `agent_factory_chat_design_pack/CHAT_CONSOLIDATED_SPEC.md` (46 KB)
is that pack's own 15 documents concatenated into one file.

And a **revision relationship** between the two UI packs:

| | `agent_factory_army_ui_concept_pack/` | `agent_factory_chat_design_pack/` |
|---|---|---|
| Carries | schemas (4), a 20-track research backlog, an artifact catalog | a per-concept **status vocabulary**, a **design history** (7 named stages), `concept_catalog.json` |
| Zeus theme | carried as `prior_research/` | **explicitly marked SUPERSEDED** in §I, with what to retain it for |

**Classification: direct duplicate (the triplication) + revision (Zeus → Army theme) + complementary
(the two UI packs carry different halves).**

⭐ **The supersession is documented, which is unusual and worth noticing.** `chat_design_pack`
§I states: *"The Zeus mythology exploration produced useful architectural naming patterns, but the
user selected a full Army/Mission Command theme… Do not treat Zeus naming as current UI direction."*
It then names four things to retain it for.

**Disposition:** keep everything. Read `zeus_world_ui_research_pack/` at its top-level path only.
⭐ Its **evaluation protocol** (`05_EVALUATION_PROTOCOL.md`) and **ten readiness gates**
(`09_IMPLEMENTATION_READINESS.md`) are theme-independent and survive the supersession entirely —
they are the most valuable part of the whole UI corpus.

---

## DC-07 — `rollback/` and `rollback-main/` · **DIRECT DUPLICATE ×2**

```
docs/evidence/control-plane-2026-08-22/rollback/pipelines.json       ┐ byte-identical
docs/evidence/control-plane-2026-08-22/rollback-main/pipelines.json  ┘ (32,794 bytes)
docs/evidence/control-plane-2026-08-22/rollback/pipe_29b8edf6.json       ┐ byte-identical
docs/evidence/control-plane-2026-08-22/rollback-main/pipe_29b8edf6.json  ┘ (9,431 bytes)
```

**Classification: direct duplicate — and the identity may itself be the evidence.** A rollback
capture taken from a branch and from `main` being byte-identical is a meaningful measurement
(nothing diverged), not an accident. The evidence README should say so and does not.

**Disposition:** keep both. **Recorded as a small documentation gap**, not a cleanup task.

---

## DC-08 — Identical render captures · **DIRECT DUPLICATE ×2, and the identity IS the proof**

```
docs/evidence/client-review-readiness-2026-09-01/client-review-nojs-1100.png
docs/evidence/client-review-readiness-2026-09-01/client-review-standard-light-1100.png
```
plus four more pairs across `artifact-generator-2026-09-01/`, `manual-2026-09-01/` and
`render-2026-08-22/`.

**Classification: intentional. Not a duplicate to remove — a NEGATIVE CONTROL that passed.**

A no-JS capture that is byte-identical to its JavaScript-enabled sibling is the strongest possible
demonstration that the page's static rendering is complete and JavaScript adds only enhancement.
Deleting either half destroys the evidence.

**Disposition:** keep every one. ⚠ **Any future de-duplication script must exclude
`docs/evidence/`** or it will delete proofs.

---

## DC-09 — Three prompts asking for a corpus preparation · **INDEPENDENT TREATMENTS**

| Document | Asks for | Ran? |
|---|---|---|
| `docs/CORPUS-AND-DESIGN-PROMPT.md` (28 KB) | D1 consolidate · D2 `docs/corpus/OBJECTIVE.md` · D3 a technical design artifact · D4 `docs/corpus/GAPS.md` | ❌ **No** — `docs/corpus/` does not exist |
| `docs/raw_research/agent-factory-bootstrap-pack/…/CLAUDE_CORPUS_PREPARATION_PROMPT.md` (6 KB) | 13 numbered steps into a `00-`…`09-` numbered tree, with a **stop condition** | ❌ No — the templates are still empty |
| `docs/raw_research/agent_factory_rd_consolidation_pack/12_CLAUDE_REPO_PACK_PROMPT.md` (5 KB) | "an external architecture review pack", separating **evidence from aspiration** | ❌ No |

**Classification: independent treatments of the same task**, all three unexecuted, all three
specifying a different deliverable shape.

⭐ **This cluster is itself a finding about the corpus:** the instruction to index it was issued at
least three times before it was carried out. The pack that asked most precisely
(`CLAUDE_CORPUS_PREPARATION_PROMPT.md`) is also the one whose non-negotiable rules this pass
followed most closely.

**Disposition:** keep all three. Together they define what a corpus-preparation deliverable was
expected to contain, and `docs/_index/` can be checked against all three.

---

## DC-10 — `06-claude-context-pack-prompt.md` · **DIRECT DUPLICATE ×2**

```
docs/raw_research/06-claude-context-pack-prompt.md                      ┐ byte-identical
docs/raw_research/agent-config-research-pack/06-claude-context-pack-prompt.md  ┘ (3,583 bytes)
```

**Classification: direct duplicate.** A pack member also dropped loose at the `raw_research/` root,
probably during extraction.

**Disposition:** keep both. The loose copy is harmless; note that it is a pack member so it is not
mistaken for a separate source.

---

## DC-11 — Agent-communication protocol, built vs designed · **CONTRADICTORY-ADJACENT**

| | `docs/agent-communication.md` | `docs/protocol/AGENT_COMMUNICATION_PROTOCOL.md` |
|---|---|---|
| Status | ✅ **BUILT** (`factory/bus.py`) | ⛔ **DESIGN. "Nothing here is built."** |
| Message kinds | **five**: correction, claimed, blocked, finished, note | **six** typed messages |
| Model | one append-only file per writer; a lane never writes another's | a typed envelope with six ACK states |
| Scope | lane-to-lane nudges between human-launched sessions | agent-to-agent, at four defined moments |

**Classification: complementary in intent, unreconciled in vocabulary.** They describe different
layers — but nothing maps the five built kinds onto the six designed types, and `docs/protocol/`
explicitly forbids a `HandoffContract` class inside `factory/handoff.py` because *"that module
generates prose lane and session notes and is a different concept wearing the same word."*

⚠ Three things in this corpus are called a **handoff**: a lane/session note (`factory/handoff.py`),
a typed message contract (`HANDOFF_CONTRACT.schema.json`), and a research-to-implementation
graduation (`docs/agent-army/IMPLEMENTATION_HANDOFFS.md`). See
[`contradictions.md`](contradictions.md) **CN-07**.

**Disposition:** keep both. Record that the vocabularies are unmapped.

---

## DC-12 — The metrics families · **COMPLEMENTARY, four vocabularies, no crosswalk**

| Source | Metric set |
|---|---|
| `docs/protocol/METRICS.md` | 10 reliability metrics, 2 built, each with its gaming route and counter-metric |
| `docs/raw_research/agent-config-research-pack/04-team-metrics-and-formulas.md` | team metric families, agent health, team health, struggle score, communication effectiveness, feature output |
| `docs/raw_research/agent_factory_army_ui_concept_pack/12_METRICS_HEALTH_AND_RECURRENCE.md` | RFR suite, failure fingerprint, army health, hierarchical aggregation |
| `docs/raw_research/agent_factory_agent_genome_research_pack/evaluation/monitoring_benchmarking_spec.md` | observability levels, metric catalog, mission readiness, benchmark vault, credit assignment |

**Classification: complementary — and one of them measures what actually exists.**

⭐ Only `METRICS.md` is scoped to data this estate holds, and it reports that **eight of its ten
metrics are NOT-RECORDED or NOT-MEASURABLE**. The three pack documents specify much larger metric
sets against no data at all. Recurring Failure Rate appears in all four and is the only metric that
crossed from a pack into code.

**Disposition:** keep all four. **No crosswalk exists between the four vocabularies, and building
one is a real piece of work** — carried into
[`research_gap_candidates.md`](research_gap_candidates.md).

---

## DC-13 — Six documents describe "what already exists" · **REVISION CHAIN**

| Document | Date | Scope | Basis |
|---|---|---|---|
| `docs/research/agent-factory-concept-inventory.md` §2 | 2026-08-23 | 26 concepts as built | measured from code |
| `docs/research/answers/R18-…` | 2026-08-23 | full internal audit | `path:line` citations |
| `docs/reviews/divergence-2026-08-29.md` | 2026-08-29 | plan and boot prompt vs code | measured |
| `docs/reviews/external/deepseek.md` D0 | 2026-08-29 | doc/code divergence | external, unverified |
| `docs/agent-army/CURRENT_STATE.md` | 2026-08-30 | Agent Army vocabulary vs code | `file:line` per row |
| `.agent-platform/RECONCILIATION.md` | 2026-08-31 | pack concepts vs estate | measured, both repos |

**Classification: revision chain — each supersedes the previous *for its own scope*, and the scopes
differ.** None fully replaces another.

**Reading order for currency:** `RECONCILIATION.md` → `CURRENT_STATE.md` → `concept-inventory` §2.
The last is the oldest and the most complete on the *built* concept surface; the first two are
newer and scoped to specific vocabularies.

**Disposition:** keep all six. ⚠ Only `CURRENT_STATE.md` and `RECONCILIATION.md` carry a
regeneration command; the others will rot silently. See
[`supersession_candidates.md`](supersession_candidates.md).

---

## What is NOT duplicated, and is worth noticing

Some things a reader might expect to find twice appear exactly once. Each single point of failure is
worth knowing about:

| Unique document | Why the uniqueness matters |
|---|---|
| `docs/case-studies/delivery-001-marketing-model.md` | The **only** test of the design against real, already-made mistakes. Nothing corroborates it. |
| `blueprints/orchestrator_team.yaml` | The **only** multi-agent architecture that was actually built and refused. |
| `evals/corpus/windsorai-2026-08-20.json` | The **only** fixture the contract has ever been scored against. |
| `docs/findings.d/` | The **only** durable corrected-premise ledger; no pack proposes anything like it. |
| `docs/research/README.md` §2 | The **only** statement of the neighbours discipline. |
| `docs/release-gate/AF-RELEASE-GATE-01-2026-09-01.md` | The **only** publication-boundary measurement, and it is **untracked**. |
