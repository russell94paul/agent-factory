# R22A — Agent Software Integration, Runtime Interoperability & Deployment Targets


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

Determine the minimum integration abstraction needed for Agent Factory to operate across runtimes/tools/software without inventing unnecessary proprietary protocols.

## Compare

MCP, A2A-style protocols, HTTP/REST, gRPC, event buses, OpenTelemetry, container/Kubernetes APIs, workflow systems, CLI/SDK adapters, identity/delegation standards.

## Required capabilities to test

identity, capability discovery, authority, resource discovery, bounded actions, observations/events, artifacts/evidence, health, cost, lifecycle, rollback, subscriptions/asynchronous wakes.

## Output

Recommend where Agent Factory should `ADOPT`, `WRAP`, `EXTEND`, or introduce a new semantic layer. Provide concrete missing use cases and limitations before proposing custom protocol work.
