---
name: research-synthesizer
description: Reconcile multiple research reports with repository evidence into claims, contradictions, decisions, experiments and architecture impact without treating any report as automatically authoritative.
---

# Research Synthesizer

## Inputs

- one or more completed research run directories;
- current repo context;
- existing decisions/ADRs;
- north-star hypotheses.

## Outputs

For each topic create:

- `SYNTHESIS.md`
- `CLAIMS.jsonl`
- `CONTRADICTIONS.md`
- `ARCHITECTURE_IMPACT.md`
- `EXPERIMENTS.md`
- `DECISION_CANDIDATES.md`

## Rules

- Cite source/report locations.
- Separate empirical evidence from inference.
- Surface disagreements rather than averaging them away.
- Include simpler alternatives.
- No architecture decision is final solely because one research model recommended it.
- Tag decisions `ADOPT | ADAPT | RESEARCH | REJECT`.
