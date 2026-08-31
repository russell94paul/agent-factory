# Reference Implementation Pattern-Extraction Policy

Reference repositories exist to reduce accidental reinvention, not to define the Agent Factory product.

## Allowed extraction
- architectural invariants;
- control-plane boundaries;
- state machines;
- failure and recovery semantics;
- isolation patterns;
- lifecycle patterns;
- observability concepts;
- interface contracts;
- operator questions / information hierarchy;
- testing and evaluation strategies;
- deployment and credential-boundary concepts;
- reusable abstractions that can be independently designed for Agent Factory.

## Not allowed by default
- copying UI layouts or visual identity;
- copying product naming/branding;
- copying prompts verbatim;
- wholesale source-code copying;
- cargo-culting their data model or hierarchy;
- changing Agent Factory architecture simply to resemble the reference.

## Classification
Every extracted pattern must be classified:

- `ADOPT_CONCEPT` — the underlying invariant is clearly useful; implement independently in our architecture.
- `ADAPT` — useful but must be changed for Agent Factory constraints.
- `EXPERIMENT` — plausible but needs measurement before adoption.
- `REJECT` — does not fit, duplicates a better existing mechanism, or creates unjustified complexity.

## Required comparison
Before adoption, answer:
1. What problem does this pattern solve?
2. Do we already solve it?
3. What evidence shows the pattern works?
4. What are its constraints/failure modes?
5. Is a simpler mechanism sufficient?
6. How does it fit our deterministic-control and external-evaluation principles?
7. What would be uniquely ours after adaptation?

The goal is convergence on strong engineering patterns while preserving a distinct product and architecture.
