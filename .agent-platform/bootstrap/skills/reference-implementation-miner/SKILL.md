---
name: reference-implementation-miner
description: Inspect a mature external implementation and extract reusable control-plane primitives, failure semantics and UI patterns without cloning the product.
---

# Reference Implementation Miner

For the target repository:

1. Read license, README, architecture/spec, AI-contributor instructions.
2. Map modules and data model.
3. Inspect implementation for each relevant feature.
4. Compare with current Agent Factory implementation.
5. Classify every candidate `REUSE | ADAPT | RESEARCH | REJECT`.
6. Record code-level provenance/license obligations if direct reuse is proposed.
7. Explicitly list product/architecture differences that must not be copied.
8. Convert accepted patterns into ADR/experiment/backlog candidates, not immediate rewrites.
