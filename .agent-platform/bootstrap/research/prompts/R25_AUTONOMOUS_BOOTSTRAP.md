# R25 — Autonomous Project Bootstrap, Agentic Software Construction & Recursive Platform Development


## Required method

- Prefer primary/official/peer-reviewed sources and source code over marketing summaries.
- Separate measured evidence, documented implementation practice, architectural inference, hypothesis, and speculation.
- Find failure cases and negative results, not only success stories.
- Assume the preferred Agent Factory architecture may be unnecessarily complicated; identify simpler alternatives.
- Identify what existed before the LLM era and what materially changes now.
- Where relevant, inspect open-source implementations rather than only papers/blogs.
- Do not recommend a new service/protocol/agent layer unless a real requirement justifies it.

## Required outputs

1. Executive finding
2. Prior-art map
3. Current implementations / systems
4. What works / what fails
5. Constraints and failure modes
6. Architecture implications for Agent Factory
7. `ADOPT | ADAPT | RESEARCH | REJECT` table
8. Minimum viable experiment(s)
9. Falsification conditions
10. Open questions
11. Source list with source-quality notes


## Objective

Determine the best evidence-grounded architecture for giving Claude an existing repository, north-star specification, skills/prompts, tools and permissions, then having it safely decompose, parallelize, execute, evaluate, integrate, document and resume a long-running software program over many sessions.

## Questions

- One persistent commander vs disposable resumable sessions?
- How should project state survive context windows/reboots?
- Skills vs static prompts vs agents vs workflows?
- How should repository context be acquired cheaply and mission-specifically?
- Worktree/branch/task isolation patterns for parallel coding agents?
- How should task DAGs, gates, retries and stalled-session recovery work?
- What should remain deterministic?
- How should agents hand off context/artifacts rather than transcripts?
- How should review/test/merge authority be separated?
- How should cost/model selection be routed?
- What current Claude Code primitives, hooks, subagents, skills, managed-agent patterns or external control planes matter?
- What design enables Agent Factory to progressively take over the workflow used to build itself?

## Special requirement

Design an autonomy maturity model and identify the exact capabilities needed before increasing autonomy from manual → skilled → orchestrated → parallel → evaluated → adaptive → self-maintaining.
