# Agent Factory Research + Architecture Bootstrap Pack

This pack is designed to be copied into the **root of the existing `agent-factory` repository** as a non-destructive research and architecture overlay.

It is **not** a new `agent-platform/` subfolder and it does **not** rename the current repository. The existing Agent Factory implementation remains the production proving ground while the wider Agentic Organization Platform is researched and synthesized.

## What this pack is for

The immediate objective is to consolidate GPT, Claude, Deep Research, external papers, UI/UX research, architecture proposals, implementation notes, experiments and current code reality into a form that an advanced coding/research agent can reliably analyze.

The target traceability chain is:

```text
IDEA
  -> SOURCE
  -> CLAIM / EVIDENCE
  -> DECISION
  -> DESIGN
  -> IMPLEMENTATION
  -> TEST / EVAL
  -> RESULT
```

The later synthesis should answer four different questions without mixing them:

1. **What exists now?** — code, tests and runtime evidence.
2. **What have we researched?** — preserved source documents and claims.
3. **What have we decided?** — explicit decision ledger / ADRs.
4. **What should we build next?** — derived only after reconciliation and architecture comparison.

## Install location

Copy the **contents** of this pack into the existing repository root:

```text
agent-factory/
├── apps/                  # existing, if present
├── services/              # existing, if present
├── agents/                # existing, if present
├── ...                    # existing runtime code
├── docs/                  # bootstrap research layer merges here
├── schemas/
├── organizations/
├── tools/bootstrap/
├── AGENT_RESEARCH_HANDOFF.yaml
└── BOOTSTRAP_MANIFEST.yaml
```

Do **not** create this shape:

```text
agent-factory/
└── agent-platform/        # NOT RECOMMENDED
```

## First-use workflow

1. Commit or checkpoint the current `agent-factory` repo.
2. Copy this pack into the repo root.
3. Add all original GPT/Claude research under `docs/01-research-corpus/raw/` without rewriting it.
4. Give Claude Code `docs/08-research-backlog/prompts/CLAUDE_CORPUS_PREPARATION_PROMPT.md`.
5. Claude inventories the real repo and creates manifests, concept registry, evidence map, decision ledger and implementation map.
6. Review `OWNER_INPUT_REQUIRED.md` only after the automated pass.
7. Freeze a commit SHA for Research Corpus v1.
8. Run `docs/09-synthesis/MASTER_SYNTHESIS_PROMPT.md` against that exact commit.
9. Compare candidate architectures using `ARCHITECTURE_TOURNAMENT_PROMPT.md` before selecting the north star.
10. Convert the winning architecture into an implementation DAG with explicit eval and migration gates.

## Core design principle

**Preserve raw research; normalize around it.** Do not edit historical artifacts to make them agree with the new architecture.

The source corpus is evidence. The indexes are interpretation. The codebase is implementation reality.
