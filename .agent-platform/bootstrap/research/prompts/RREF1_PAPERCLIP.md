# RREF1 — Paperclip Reference Implementation Mining


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


## Target

https://github.com/paperclipai/paperclip

## Objective

Mine Paperclip for proven control-plane concepts that could save Agent Factory from redesigning mundane infrastructure, without making Agent Factory a carbon copy.

## Inspect specifically

- task/session persistence;
- heartbeats/wake semantics;
- atomic checkout/locks;
- worktree isolation;
- agent adapters;
- runtime skills;
- budgets/costs;
- approvals/governance;
- artifact/work-product model;
- task dependencies/routines;
- operator UI information hierarchy;
- AGENTS.md / AI-contributor repository conventions;
- failure/recovery semantics.

## Compare against our north star

Explicitly identify where Paperclip's strict org tree, task/comment communication, single-assignee execution model, knowledge scope, dynamic assembly, shared cognition, Org-IR, evolution or self-maintenance are insufficient or simply different.

Produce a file-level adoption matrix with license/provenance implications for any code reuse.
