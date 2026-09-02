# Agent Factory — Chat Design Consolidation Pack

**Purpose:** Convert the concepts developed in this chat into a reusable design/research pack for the Agent Factory.

## Current direction

1. **Primary UI:** a serious Agentic IDE / Mission Command Console.
2. **Alternative UI:** a highly gamified Army Command World driven by the exact same real system state.
3. **Core design rule:** the world must not be a decorative game skin. Spatial position, formations, logistics, radio, fog, front lines, threats, ranks, AARs, and war games should encode actual operational state or accelerate real operator actions.
4. **Organization model:** arbitrarily nested, configurable service designations rather than a fixed Agent → Team → Army hierarchy.
5. **Learning metric:** Recurring Failure Rate and related recurrence/learning metrics are first-class measures of whether the organization actually learns.
6. **Autonomous improvement organization:** Advanced Projects Command / “Black Site” continuously mines organizational experience for high-leverage changes, researches them, war-games them, prototypes them, and proposes promotion.

## Pack structure

- `00_MASTER_CONCEPT_MAP.md` — all major concept families and current status.
- `01_PRIMARY_AGENTIC_IDE.md` — the serious UI that should be built first.
- `02_ARMY_COMMAND_WORLD.md` — the alternate animated spatial operating world.
- `03_ARMY_INTERACTION_LANGUAGE.md` — military metaphors mapped to real engineering semantics.
- `04_GAMIFICATION_SOCIAL_WORLD.md` — social, witty, remote-company gamification.
- `05_ADVANCED_PROJECTS_COMMAND.md` — autonomous cross-team improvement / research lab.
- `06_ORGANIZATION_HIERARCHY_AND_SERVICE_DESIGNATIONS.md` — configurable nested organizational grammar.
- `07_METRICS_FAILURE_RECURRENCE_AND_HEALTH.md` — RFR, preventable recurrence, learning-chain diagnostics, health.
- `08_EXPERIMENTAL_RESEARCH_CONCEPTS.md` — 10 extreme research concepts.
- `09_BUSINESS_VALUE_FEATURES.md` — 10 value-first concepts.
- `10_AGENTIC_RESEARCH_PROGRAM.md` — research program for validating the paradigm.
- `11_IMPLEMENTATION_AND_INTEGRATION_GUIDE.md` — how to reconcile this with Agent Factory later.
- `12_NAMING_AND_DESIGN_HISTORY.md` — Zeus exploration vs current Army direction.
- `13_RESEARCH_PROMPTS.md` — ready-to-run research prompts.
- `concept_catalog.json` — machine-readable concept registry.
- `agent_org_schema_example.yaml` — illustrative configurable hierarchy.
- `failure_recurrence_schema.yaml` — illustrative recurrence ledger.
- `pack_manifest.json` — file manifest.
- `legacy_reference/` — prior ZEUS research pack and original Agent Factory vision source.

## Status vocabulary

- **CORE** — foundational design principle; should shape platform architecture.
- **CURRENT** — current preferred product/UI direction.
- **SUPPORTING** — useful concept, not itself a top-level product decision.
- **EXPERIMENTAL** — deliberately speculative; validate before implementation.
- **RESEARCH** — research question/program, not an implementation commitment.
- **SUPERSEDED** — retained as design history but replaced by a newer direction.

## Recommended use

Feed this pack plus the current Agent Factory repository/spec into a design-reconciliation agent and ask it to produce:
1. ontology changes,
2. schema changes,
3. UI state model,
4. event model,
5. component boundaries,
6. migration plan,
7. eval plan,
8. phased implementation roadmap.

Do **not** implement the fully animated world before the primary Mission Command Console and underlying typed state/event model are strong.
