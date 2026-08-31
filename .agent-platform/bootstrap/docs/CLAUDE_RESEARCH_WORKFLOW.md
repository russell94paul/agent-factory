# Claude Research Workflow — Subscription-First, No API Billing

## Purpose

This is the active research path for the bootstrap.

The project deliberately does **not** require OpenAI API or Anthropic API usage for research. Claude Research still consumes the normal usage allowance of the operator's Claude plan, so the queue should prioritize only questions that justify deep research. The default is to use the **Claude subscription surfaces** already available to the operator:

1. repository inspection in Claude Code;
2. Claude Code web search for narrow/current questions when available;
3. **Claude Research** for deep, multi-step research;
4. Claude Code synthesis back into project artifacts.

The goal is to minimize both cost and human error without pretending that Claude Code can programmatically press the Research button in the Claude app.

## Current automation boundary

Claude Research is a Claude app feature. Treat the launch of a Research run as a **human-triggered external execution step** unless a supported Anthropic integration becomes available and is explicitly configured later.

Everything around that trigger should be automated:

```text
Claude Code identifies evidence gap
        ↓
research job compiler
        ↓
versioned PROMPT.md + RETURN_CONTRACT.md
        ↓
prioritized RESEARCH_QUEUE.md
        ↓
HUMAN TRIGGER: run prompt in Claude Research
        ↓
raw report saved/pasted to designated inbox path
        ↓
research ingest checker
        ↓
Claude research synthesizer
        ↓
claims / contradictions / architecture impact
        ↓
experiment / ADR / build-DAG update
```

The operator should never have to rewrite a research prompt, remember its expected output format, or manually reconcile multiple reports.

## Research escalation policy

Use the cheapest/highest-confidence source first:

### Tier 0 — Repository evidence

Use the actual Agent Factory repository, tests, production traces, docs, and historical failures. If the repo can answer the question, do not research externally.

### Tier 1 — Claude Code web search

Use for bounded questions that can be answered with a small number of searches, such as:

- current API or library behavior;
- whether a reference project implements a specific primitive;
- current protocol/version/status checks;
- confirming a product capability.

Persist useful sources/claims into the research artifact when they materially affect architecture.

### Tier 2 — Claude Research

Escalate when the task needs:

- multi-source literature or prior-art review;
- competing architectural approaches;
- historical + contemporary evidence;
- contradiction reconciliation;
- market/monetization research;
- broad implementation comparison;
- an evidence-heavy recommendation.

Do not use Research for a question the repo or a few web searches can settle.

## Research job directory

Prepared jobs live under:

```text
.agent-platform/research/queue/<research-id>/
├── JOB.json
├── PROMPT.md
├── RETURN_CONTRACT.md
├── RAW_REPORT.md              # filled after Claude Research completes
└── INGEST_STATUS.json         # created by ingest checker
```

Completed/synthesized work can move or copy to:

```text
.agent-platform/research/runs/<research-id>/
```

## Exact operator loop

When the Bootstrap Commander says research is ready:

1. Open `.agent-platform/research/RESEARCH_QUEUE.md`.
2. Pick the highest-priority `READY_FOR_CLAUDE_RESEARCH` job.
3. Open Claude on web/desktop/mobile.
4. Enable **Research** (web search must also be enabled for Research to work).
5. Paste the job's `PROMPT.md` exactly; do not edit it unless the prompt itself is wrong.
6. When the report finishes, save/copy it verbatim into that job's `RAW_REPORT.md`, or return it to the Claude Code coordinator and ask it to save it there.
7. Tell the coordinator: `research returned <research-id>`.
8. The coordinator runs the ingest checker and `research-synthesizer`.

This is the only unavoidable manual bridge in v0.

## Output contract for every Claude Research prompt

Every generated prompt must ask for these sections:

1. Executive findings
2. Evidence table
3. Relevant prior art / existing implementations
4. What worked / failed and why
5. Contradictions and unresolved questions
6. Measured evidence vs practice vs inference vs speculation
7. Implications for current Agent Factory
8. Simplest viable architecture
9. What **not** to build
10. Experiments that would falsify the recommendation
11. Sources with titles, publishers/authors, dates, and links/citations
12. Machine-readable conclusion block containing the research ID

The research must challenge the preferred architecture and explicitly ask whether the proposed subsystem is unnecessary complexity.

## Parallelism

Claude Code may prepare many research jobs at once. The operator can run several Claude Research chats in parallel subject to subscription usage limits.

Dependencies are respected at the queue level:

- independent jobs may be marked `READY_FOR_CLAUDE_RESEARCH` together;
- jobs depending on unresolved research stay `BLOCKED_BY_RESEARCH`;
- synthesis jobs run only after required reports have been ingested.

## Failure behavior

If a Research run is incomplete, loses citations, or does not follow the output contract:

- do not silently treat it as evidence;
- mark it `NEEDS_REPAIR`;
- generate a short correction/follow-up prompt rather than rerunning the entire research track when possible.

## Future automation seam

Keep the research-job schema provider-neutral. If Anthropic later exposes a supported way for Claude Code/Cowork to launch and retrieve Claude Research runs automatically, implement it as an adapter behind the same job/inbox/synthesis contracts.

Do not redesign the research system around undocumented browser automation.
