# R06A — Agent Communication, Coordination & Swarming


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

Design the minimum communication/interaction substrate needed for non-siloed agent organizations: shared information, availability, help requests, expert consultation, typed evidence, handoffs, warnings, subscriptions and bounded swarm formation.

## Research domains

Agent communication languages, actor systems, blackboards, tuple spaces, stigmergy, pub/sub, event sourcing, workflow/event buses, distributed systems, multi-agent coordination, A2A/MCP-style standards, incident command, market/task allocation.

## Questions

- Which message/event primitives are actually necessary?
- Centralized manager vs decentralized coordination tradeoffs?
- How to avoid everyone-to-everyone chat and manager bottlenecks?
- Sync vs async semantics?
- Ack/delivery/dedup/TTL/priority/correlation semantics?
- How should capability/availability be announced and discovered?
- When should the system form/dissolve a swarm?
- How should communication be observed/replayed/debugged?
- Can existing protocols be adapted, or is a custom semantic layer justified?
