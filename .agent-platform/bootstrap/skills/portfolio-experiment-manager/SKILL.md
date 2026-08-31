---
name: portfolio-experiment-manager
description: Compare bounded product/feature experiments under fixed budgets and evidence gates, then recommend kill, hold, improve, scale, or gather-more-evidence decisions.
---

# Portfolio Experiment Manager

## Objective

Allocate limited Factory attention/compute/budget toward the experiments with the strongest expected learning or value, while preserving hard constraints.

## Inputs

- active OpportunityHypotheses/VenturePlans;
- experiment results;
- commercial evidence;
- cost/reliability/support data;
- strategic constraints;
- fixed decision criteria.

## Output

For each candidate:

`KILL | HOLD | IMPROVE | SCALE | MORE_EVIDENCE`

with:

- evidence summary;
- uncertainty;
- cost consumed;
- next marginal experiment;
- opportunity cost;
- hard-constraint status;
- human gate if needed.

Use multi-objective comparison rather than reducing every decision to raw revenue.
