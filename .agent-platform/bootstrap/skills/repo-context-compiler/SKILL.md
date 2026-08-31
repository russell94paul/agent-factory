---
name: repo-context-compiler
description: Recover the real Agent Factory repository architecture and compile mission-specific/durable project context before planning or changing code.
---

# Repo Context Compiler

## Trigger

Use at bootstrap, after major repo changes, or before a mission that spans unfamiliar domains.

## Procedure

1. Read repository-level AI instructions (`CLAUDE.md`, `AGENTS.md`, skills, contributor docs) first.
2. Record branch/commit/dirty state.
3. Map top-level directories and service/package boundaries.
4. Search for execution DAG/orchestrator/Prefect, FastAPI/control plane, agents/prompts/skills, memory, evals, events, UI, deployment, integrations and tests.
5. Read implementation files, not only design docs.
6. Identify current invariants and failure-handling semantics.
7. Build `.agent-platform/CURRENT_STATE.md` with evidence-linked paths.
8. Update `PROJECT_STATE.yaml`.
9. For the active mission, create a bounded `context-packet.md` containing only affected components, dependencies, tests, ADRs, known failures and relevant historical work.

## Do not

- redesign while scanning;
- assume a missing file means a missing capability;
- dump the entire repo into a prompt;
- overwrite established repo documentation conventions.
