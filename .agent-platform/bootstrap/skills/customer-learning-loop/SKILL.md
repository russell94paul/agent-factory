---
name: customer-learning-loop
description: Convert permissioned customer/product signals into structured evidence, hypotheses and bounded improvement missions.
---

# Customer Learning Loop

## Objective

Close the product loop without letting autonomous agents treat noisy telemetry as proof of customer value.

## Inputs

- product telemetry;
- support/feedback artifacts;
- experiment results;
- revenue/conversion/churn evidence where authorized;
- current product and venture goals;
- privacy/tenant policies.

## Procedure

1. Validate source provenance and permission scope.
2. Normalize each signal into an evidence record with time, source, confidence and affected customer/product scope.
3. Cluster related signals without erasing disagreement.
4. Distinguish observation, customer statement, metric movement, experiment result and hypothesis.
5. Produce a prioritized set of product hypotheses.
6. For each hypothesis, specify the cheapest falsification experiment.
7. Send only approved hypotheses into Venture Compiler / Mission Assembly.
8. Preserve negative results as reusable knowledge.

## Guardrails

- do not expose one tenant/customer's private data to another;
- do not optimize for deceptive engagement or spam;
- do not let the same agent silently redefine the metric that judges its own experiment;
- consequential customer-facing changes still obey launch/policy gates.
