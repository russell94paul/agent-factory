# Source Map for this Synthesis

This pack intentionally does not copy sensitive evidence bodies. It records the main internal sources used to make decisions.

## Agent Factory review pack

- `REVIEW_CONTEXT.md` — corpus limits and measured facts.
- `docs/agent-army/CURRENT_STATE.md` — code-grounded state, highest authority in the pack for what is built.
- `.agent-platform/RECONCILIATION.md` — category/prior-art reconciliation.
- `docs/_index/current_vs_proposed.md` — 112+ capability maturity map.
- `docs/_index/contradictions.md` — architecture disagreements.
- `docs/_index/high_leverage_concepts.md` — candidate mechanisms.
- `docs/_index/research_gap_candidates.md` — actual gaps vs research-looking gaps.
- `docs/research/dependency_graph.md` — research/measurement ordering.
- `code-inventory/module-docstrings.md` — design intent for current runtime modules.
- `docs/design/switchboard-redesign-2026-09-01/SOURCE-switchboard_p1.py` — validated P1 UI source snapshot.
- `docs/case-studies/delivery-001-marketing-model.md` — real delivery case study.
- `docs/specs/marketing-model-reconstruction-v1.md` — Marketing reconstruction mission specification.
- `boot-prompts/switchboard-p1-and-finalization-2026-09-01.md` — latest Switchboard/Marketing handoff in the review pack.
- `boot-prompts/first-real-dispatch-2026-08-31.md` — F90 and first-real-run blocker detail.

## Architecture supplement

- `SUPPLEMENT_README.md` — closed DOCX gap and Agent Army Wave 0 summary.
- `docs/_index/agent_army_wave0_supplement.md` — traced findings from sibling repo.
- converted frontier architecture documents — used as proposal catalogs, not independent evidence.
- amended `current_vs_proposed.md`, `contradictions.md`, `research_gap_candidates.md`, `high_leverage_concepts.md`.

## Direct Agent Army source check

The review also directly checked the sibling repository's current `main`:

- `architecture/00-target-architecture.md` — target layers and "do first/do later" ordering.
- `architecture/06-knowledge-evidence-model.md` — explicit separation of Observation / Claim / Evidence / KnowledgeObject and source-root provenance.

## Key synthesis implications

- Organization-compiler **mechanisms** may be useful; do not adopt the novelty/category framing.
- Existing Agent Factory runtime primitives are more mature than several research roadmaps assume.
- The immediate autonomy gap is wiring/actuation, not another scheduler design.
- One real run is more valuable than another broad research pass.
- Model binding must be treated as part of any future optimized organization/config version.
