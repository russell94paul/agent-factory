# Agents-as-Configuration Research Pack

Repository-grounded design pack for evolving `russell94paul/agent-factory` from its current
`AgentSpec` / `TeamSpec` blueprint skeleton into a versioned configuration compiler, capability
registry, mission matcher and measurable team-operations platform.

## Start here

1. `00-executive-assessment.md` — honest recommendation and repository impact.
2. `01-idea-portfolio.md` — every idea structured by value, complexity, process change and time saved.
3. `02-configuration-and-storage.md` — what belongs in YAML, schemas, databases and event stores.
4. `03-parameter-catalog.md` — the v0 parameter taxonomy for agents and teams.
5. `04-team-metrics-and-formulas.md` — health, struggle, communication and outcome metrics.
6. `05-research-and-build-sequence.md` — sequenced deep-research waves and implementation gates.
7. `06-claude-context-pack-prompt.md` — prompt for Claude to produce the missing repo context pack.
8. `07-repository-change-map.md` — code, database, security and UI integration seams.
9. `SOURCES.md` — repository evidence and external primary/official references.
10. `configs/` — illustrative agent, team, mission, metric and policy configurations.
11. `schemas/` — draft JSON Schemas for validating the agent and team examples.

## Central decision

Use **YAML as the authoring format**, **JSON Schema 2020-12 as the interchange validation
contract**, Python dataclasses/Pydantic-style models as runtime types, and a **resolved JSON
lockfile** as the immutable identity that is hashed, certified and executed.

Do not store runtime metrics in YAML. Store timestamped events, measurements, evidence and
capability observations in append-only/queryable runtime stores.

## Repository status respected by this pack

The current repository deliberately gates optimizer, Army and platform work on a certified team
and evidence that added structure helps. This pack is therefore a research and contract proposal,
not authorization to merge Army functionality into production.

The original additional document mentioned in the request was not attached. It should be added to
the Claude context pack and reviewed before any architecture decision is accepted.

## Suggested next action

Run `06-claude-context-pack-prompt.md` in Claude Code from the repository root. Return the produced
ZIP together with the missing document. Then run research Wave 0 before approving schema changes.

## Validation status

- All JSON files parse as JSON.
- All YAML files parse with a safe YAML loader.
- The agent and team examples are paired with draft JSON Schema 2020-12 contracts.
- These contracts are proposals and have not been run through the repository's own test suite.
