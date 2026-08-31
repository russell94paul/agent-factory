# R06B — Collective Cognition, Mission-Shaped Knowledge Graphs & Context Routing


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

Determine how agents/teams should publish, retrieve, challenge, synthesize and reuse historical knowledge and experience without relying on giant shared transcripts.

## Questions

- Knowledge graph vs event store vs vector retrieval vs relational/provenance store combinations?
- How to represent claims, evidence, decisions, temporal validity, contradictions and provenance?
- Mission similarity and prior-expert discovery?
- What is a mission-shaped knowledge/context graph and when is it worth materializing?
- How should role-specific context packets be compiled?
- Push vs pull knowledge routing and cross-agent notifications?
- How to prevent stale/poisoned knowledge and eval leakage?
- How to measure retrieval utility, cost, freshness and contradiction handling?
- How should successful missions write reusable learning back?
