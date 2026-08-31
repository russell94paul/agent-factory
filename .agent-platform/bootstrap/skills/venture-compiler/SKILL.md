---
name: venture-compiler
description: Turn an approved opportunity hypothesis into a bounded, stage-gated product/venture mission graph using existing Agent Factory teams, skills, evals and policies.
---

# Venture Compiler

## Inputs

- approved OpportunityHypothesis;
- repository/product context;
- capability registry;
- team/skill blueprints;
- budget and commercial autonomy policy;
- deployment/integration availability;
- evidence/evaluation requirements.

## Procedure

1. Determine current commercial evidence level.
2. Choose the smallest next experiment capable of changing the decision.
3. Reuse existing team blueprints before inventing a new team.
4. Ask Mission Assembly to resolve participants, tools, context routes and communication topology.
5. Emit a DAG whose deterministic stages own known checks and lifecycle transitions.
6. Add human/policy gates for consequential commercial actions.
7. Define success, failure and kill criteria before execution.
8. Define telemetry/customer evidence required after release.
9. Persist a `VenturePlan` and update durable project/venture state.

## Never

- jump directly from an unvalidated idea to a large build because agents are cheap;
- let a growth agent redefine the business success criteria after seeing results;
- allow the same agent configuration to both generate and certify its own improvement without external/frozen evaluation;
- assume zero-human operation is required or optimal.
