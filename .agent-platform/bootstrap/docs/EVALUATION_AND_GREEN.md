# Evaluation, Certification & GREEN

## Semantic rule

```text
GREEN = conjunction(required positive assertions)
UNMEASURED != GREEN
NO EXCEPTION != GREEN
```

## Evaluate at multiple levels

- seat/agent;
- team;
- organization;
- capability;
- skill;
- workflow;
- knowledge/context policy;
- integration/runtime;
- platform.

## Evidence sources

Prefer deterministic evidence where possible:

- unit/integration/property tests;
- known failure reproduction;
- RED-before / GREEN-after proof;
- regression suites;
- environment outcomes;
- invariants;
- hidden/frozen tests;
- independent graders;
- human review;
- canaries;
- production outcomes.

## Organizational seam attribution

Capture:

```text
introduced_by
escaped_by
detected_by
repaired_by
verified_by
```

The purpose is to improve boundaries and organization design, not blame the last agent.
