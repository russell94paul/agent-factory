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

| Source file | Live artifact | Favicon | Audience |
|---|---|---|---|
| `agent-factory.html` | https://claude.ai/code/artifact/50d3ca62-3e9c-46dd-8867-7e1c794aff75 | ⚙️ | engineering — status, gates, build order |
| `orchestration-bench.html` | https://claude.ai/code/artifact/839fd517-5305-46e1-8325-74f18b1a45b0 | ⚖️ | engineering — ⚠ R13 run 2 recommends retiring this (AB-12) |

⚠ **`agent-factory.html` is stale as of 2026-08-29.** It reflects the `UNMEASURABLE (PASS=11)` era and
a "9 of 30 gates" count; `certify --calibrate` now returns `PASS (PASS=12)`. See
[`F76`](../findings.d/F76-the-eval-can-fail-what-it-cannot-do-is-generalise.md). It has not been
republished, so the live page carries the old numbers too.

### Filed elsewhere on purpose

**"The Fourth Verdict"** — the internal vision / USP / taxonomy orientation, published 2026-08-29 —
lives in **`aldc-launchpad/docs/readouts/the-fourth-verdict.html`**, not here. Its URL is
deliberately **not** repeated on this page: `aldc-launchpad/docs/artifacts/registry/build.py` locates
an artifact's source by `git grep`-ing every repo for its URL, so a second repo mentioning it makes
the measurement ambiguous — and on the first run it mis-attributed this page to `agent-factory`
because of exactly that. **The link lives in the canonical registry**,
`aldc-launchpad/docs/artifacts/REGISTRY.md`, which is generated and is the place to look.

It is not read by any code in this package, and it spans agent-factory, prefect-connectors,
aldc-launchpad, neurospect-learn, the CLIENT-B tickets, `ccx` and the skills library. By the test in
`wiki/concepts/patterns/session-contention-and-artefact-homes` — *"it spans repos, so it has no
single code home"* — that makes it memory-layer, alongside `zeus-foundry-brief.html`. The two files
in the table above stay here because `factory/readiness.py` yields `agent-factory.html` into the
suite fingerprint **by name**; moving those breaks the gate.

Both confirmed 2026-08-29 by exact `<title>` match; `agent-factory.html` is corroborated by
`aldc-launchpad/boot-prompts/agent-factory-phase-a-2026-08-21.md`, which cites the same id, and by
its last commit (2026-08-23) matching that artifact's updated date.

⚠️ **A second, newer artifact is also called "Agent Factory"** —
`https://claude.ai/code/artifact/0fdcb1cd-2a15-4d97-93af-ba6f6c66a365`, published 2026-08-29. **Its
source is not in this repo or any other**, so it cannot be rebuilt. Do not assume it is this file.

Registered in `aldc-launchpad/docs/artifacts/REGISTRY.md`.
