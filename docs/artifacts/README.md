# Published artifacts — source files

These HTML files are the **source** for live Claude artifacts. The published pages persist
independently of any session; these files exist so a future session can edit them instead of
rebuilding from scratch.

⚠️ **This directory is read by code.** `factory/readiness.py` yields
`docs/artifacts/agent-factory.html` into the suite fingerprint by name, and `factory/lanes.py` and
`factory/schedule.py` also reference this path. Per
`wiki/concepts/patterns/session-contention-and-artefact-homes` (2026-08-23) that makes this a
**"with the code"** home — moving these files breaks the readiness gate. They do not move to the
memory layer, however much they look like documents.

| Source file | Live artifact | Favicon |
|---|---|---|
| `agent-factory.html` | https://claude.ai/code/artifact/50d3ca62-3e9c-46dd-8867-7e1c794aff75 | ⚙️ |
| `orchestration-bench.html` | https://claude.ai/code/artifact/839fd517-5305-46e1-8325-74f18b1a45b0 | ⚖️ |

Both confirmed 2026-08-29 by exact `<title>` match; `agent-factory.html` is corroborated by
`aldc-launchpad/boot-prompts/agent-factory-phase-a-2026-08-21.md`, which cites the same id, and by
its last commit (2026-08-23) matching that artifact's updated date.

⚠️ **A second, newer artifact is also called "Agent Factory"** —
`https://claude.ai/code/artifact/0fdcb1cd-2a15-4d97-93af-ba6f6c66a365`, published 2026-08-29. **Its
source is not in this repo or any other**, so it cannot be rebuilt. Do not assume it is this file.

Registered in `aldc-launchpad/docs/artifacts/REGISTRY.md`.
