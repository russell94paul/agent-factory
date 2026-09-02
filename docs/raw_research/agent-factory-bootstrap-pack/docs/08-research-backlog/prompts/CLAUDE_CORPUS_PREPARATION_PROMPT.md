# Claude Code Prompt — Prepare the Agent Factory Research Corpus

You are operating **at the root of my existing `agent-factory` repository**. Do not create an `agent-platform/` subfolder.

I am adding a large corpus of research generated across ChatGPT, Claude, Deep Research, architecture work, UI/UX work, agent configuration research, organizational science, evaluation/monitoring research and implementation planning.

The later goal is to derive a new consolidated north-star design and implementation pack from:

1. the actual current repository,
2. the full research corpus,
3. previous proposed designs,
4. experiments and measured outcomes,
5. external evidence and prior art.

Your task **now** is evidence preservation, indexing, normalization, provenance and current-state grounding — not platform redesign.

## Non-negotiable rules

- Do not redesign the platform yet.
- Do not select a winning architecture.
- Do not delete source research.
- Do not silently resolve conflicts.
- Do not turn hypotheses into facts.
- Do not treat repeated AI-generated claims as independent evidence.
- Do not infer implementation from design documents.
- Code, tests and runtime evidence outrank old docs when determining current implementation.
- Product vision expresses intent; research expresses ideas/evidence; designs express proposals; decisions express selected direction; code/tests express current software reality.

## 1. Preserve source artifacts

Keep original research under `docs/01-research-corpus/raw/` using practical source/domain folders. Preserve filenames where useful. Calculate SHA-256 where feasible. Record duplicates rather than deleting them.

## 2. Inventory the real repository

Inspect the codebase and identify applications, services, packages, agents, workflows/DAGs, memory/knowledge systems, configuration, evals, observability, health, simulations, UI, APIs, storage, schemas, infra, integrations, tests, CI/CD, feature flags, experiments and stale/dead code where reasonably detectable.

Populate `docs/00-source-of-truth/CURRENT_SYSTEM_SNAPSHOT.md` using statuses:

- IMPLEMENTED
- PARTIAL
- STUB
- EXPERIMENTAL
- DOCUMENTED_ONLY
- PLANNED
- UNKNOWN

Include concrete repository paths as evidence.

Also populate `CURRENT_REPO_MAP.md`, `CURRENT_PRIORITIES.md`, `CURRENT_CONSTRAINTS.md` where the evidence supports them. Put owner-dependent ambiguity in `OWNER_INPUT_REQUIRED.md` rather than guessing.

## 3. Build the corpus manifest

Populate `docs/01-research-corpus/manifests/corpus-manifest.yaml` using stable artifact IDs and the schema already supplied in this bootstrap pack.

Use `unknown`/null instead of fabricated metadata.

## 4. Build the Concept Registry

Populate `docs/02-concepts/concept-registry.yaml` with significant architecture/product/research concepts, not every heading.

Capture themes including agent architecture/config/skills/health/lifecycle, team/army/higher-order organizations, topology, communication, memory, collective cognition, self-maintenance, evolution, simulation, evals, research automation, governance, context engineering, deterministic-agentic boundaries, mission planning, UI/Agentic IDE and hybrid cross-domain ideas.

Never label something novel without prior-art evidence.

## 5. Build claims and evidence maps

Populate `docs/04-evidence/claims.jsonl` with strategically significant claims and distinguish:

- external_evidence
- internal_measurement
- hypothesis
- design_claim
- opinion

Populate `evidence-map.yaml` for major concepts with source count, independent-source estimate, external evidence, internal measurement, implementation evidence, benchmark evidence, contradictions and research gaps.

## 6. Detect contradictions

Populate `docs/05-decisions/contradictions.md` with incompatible hierarchies, stale assumptions, autonomy-vs-determinism conflicts, terminology conflicts, UI/runtime mismatches, or recommendations that disagree.

Do not resolve them unless an explicit decision already exists.

## 7. Build the decision ledger

Populate `decision-ledger.yaml` using statuses:

- DECIDED
- PROVISIONAL
- PROPOSED
- REJECTED
- SUPERSEDED
- UNKNOWN

Repeated ideas are not decisions.

## 8. Map research to implementation

Populate `docs/07-implementation/implementation-map.yaml` and `capability-matrix.yaml`.

For major capabilities include code paths, tests, config, UI, runtime use and gaps. Use statuses such as production, implemented, partial, prototype, stub, planned, research_only, absent and unknown.

## 9. Detect doc/code drift

Populate `doc-code-drift.md` with material cases where documentation and implementation have diverged. Do not rewrite historical research to hide drift.

## 10. Research gaps and queue

Replace the seed `RESEARCH_GAPS.md` and `RESEARCH_QUEUE.yaml` with gaps that actually block decisions. Prioritize CRITICAL / HIGH / MEDIUM / EXPLORATORY.

Preserve all standalone research prompts under `docs/08-research-backlog/prompts/`.

## 11. Owner questions

Populate `OWNER_INPUT_REQUIRED.md` only with questions whose answers materially affect future architecture. Do not block the automated corpus preparation pass on these questions.

## 12. AI handoff

Update `AGENT_RESEARCH_HANDOFF.yaml` with the exact branch, commit SHA and generated timestamp once the corpus pass is complete. Update `docs/START_HERE_RESEARCH_SYNTHESIS.md` if repository-specific guidance is needed.

## 13. Final report

Create `docs/CORPUS_PREPARATION_REPORT.md` with counts and findings: files discovered/classified, duplicates, concepts, decisions, contradictions, implementation mappings, documentation drift, research gaps, unclassified artifacts, owner questions and processing limitations.

End with one readiness classification:

- READY
- READY_WITH_GAPS
- NOT_READY

and explain why.

## Stop condition

Once corpus preparation is complete, stop. Do **not** propose the new north-star architecture in the same pass.
