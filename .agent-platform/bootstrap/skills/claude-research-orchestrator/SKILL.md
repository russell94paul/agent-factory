---
name: claude-research-orchestrator
description: Compile evidence gaps into exact Claude Research prompts and a prioritized queue, then ingest returned reports for deterministic synthesis. Uses Claude subscription Research, not an API.
---

# Claude Research Orchestrator

Use this skill when external deep research is genuinely required after repository evidence and narrow web search are insufficient.

## Rules

1. Do not request or use an API key.
2. Do not claim Claude Code can automatically launch Claude Research unless a supported integration is actually present.
3. Minimize the human step to **launching the prepared prompt and returning the raw report**.
4. Generate exact, versioned prompts and deterministic return contracts.
5. Prefer fewer, higher-value research runs over large speculative batches.
6. Run independent research tracks in parallel only when their results do not depend on one another.
7. Preserve raw reports unchanged; synthesis is a separate artifact.

## Procedure

1. Inspect repo/project state and existing research first.
2. State the unresolved evidence gap.
3. Decide `repo_only | claude_code_web_search | claude_research`.
4. For `claude_research`, create/update a job in the research manifest.
5. Run:

```bash
python <pack>/scripts/prepare_claude_research_wave.py <manifest> --out .agent-platform/research
```

6. Present the operator with the generated `RESEARCH_QUEUE.md`, not a wall of prompts in chat.
7. After the operator returns a report, verify it with:

```bash
python <pack>/scripts/ingest_claude_research.py \
  --job-dir .agent-platform/research/queue/<research-id>
```

8. Invoke `research-synthesizer` over all completed jobs required by the current decision.
9. Update architecture decisions, experiments, roadmap, and project state.

## Human interaction

Only ask the operator to do this:

> Run Research job `<id>` using the exact generated PROMPT.md and return/save the raw report to the designated path.

Do not ask them to rewrite, summarize, reconcile, or manually merge research outputs.
