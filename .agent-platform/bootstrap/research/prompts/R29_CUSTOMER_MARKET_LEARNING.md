# R29 — Customer & Market Learning Fabric

## Objective

Design an evidence-producing feedback system that lets autonomous or low-human software products learn from real usage without confusing telemetry with customer value.

## Primary questions

1. Which customer/product signals should become first-class evidence objects?
2. How should product telemetry, support messages, interviews, churn reasons, conversion experiments, sales objections and cost-to-serve be normalized?
3. How should privacy, consent, tenant isolation, provenance and temporal validity be represented?
4. What belongs in Collective Cognition versus product-specific stores?
5. How should role-specific agents receive synthesized customer context without unnecessary raw-data exposure?
6. How should the system distinguish correlation, customer statement, experiment result and causal evidence?
7. How does the learning fabric emit bounded product-improvement missions?
8. Which decisions must remain human/policy-gated?

## Required prior art

Research product analytics, experimentation platforms, continuous discovery, CRM/customer-success systems, feature flags, event sourcing, process mining, causal inference, feedback-loop design and autonomous product-agent systems.

## Falsification

Assume a sophisticated learning fabric may be unnecessary. Compare it with a much simpler event warehouse + scheduled synthesis pipeline.

## Required output

- signal taxonomy;
- evidence schema;
- privacy/permission model;
- customer-to-mission flow;
- minimum viable implementation using existing Agent Factory services;
- experiments proving whether synthesized customer context improves product decisions;
- risks and rejected complexity.
