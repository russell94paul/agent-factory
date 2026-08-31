# RDGX — NVIDIA DGX Spark as an Agent Compute Target


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

Evaluate NVIDIA DGX Spark as a local/private agent-compute node in a hybrid Agent Factory compute fabric.

## Questions

- Current hardware/software/runtime capabilities and constraints?
- Best use cases: local inference, embeddings/retrieval, evaluation, persistent local agents, model serving?
- What should remain on external APIs?
- Container/runtime management and remote deployment options?
- Monitoring/health/capacity interfaces?
- Multi-node possibilities and limitations?
- Security/secrets/isolation considerations?
- What generic compute-node contract would support DGX Spark without coupling the platform to NVIDIA?
- What smallest deployment experiment is worth running once hardware is available?

## Priority

Lower priority unless there is an immediate deployment use case. Design the generic compute abstraction first.
