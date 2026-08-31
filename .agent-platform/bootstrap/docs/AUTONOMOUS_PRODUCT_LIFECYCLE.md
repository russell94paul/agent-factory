# Autonomous Product Lifecycle — Design Target

## Goal

Provide one reproducible path from an evidence-backed opportunity to an operated software product, while letting Agent Factory dynamically assemble different organizations at each stage.

## Lifecycle

| Stage | Primary question | Typical organization | Required output |
|---|---|---|---|
| Discover | Is there a plausible valuable problem? | Opportunity Intelligence Council | OpportunityHypothesis |
| Validate | What evidence would falsify/confirm it? | Research + customer-discovery organization | Validation report + evidence matrix |
| Design | What is the smallest product test? | Product/UI Studio + architect | Product contract + experiment spec |
| Build | Can we produce it reliably? | Venture Build Pod | Tested deployable artifact |
| Launch | Can intended users reach/understand it? | Launch/Growth Pod | Bounded release + acquisition experiment |
| Learn | What happened externally? | Customer/Market Learning Pod | MarketSignal set + experiment result |
| Operate | Can it run at acceptable reliability/cost? | Reliability Corps | Operational health + support state |
| Improve | What next change is justified? | Evolution/Product organization | Ranked candidate changes |
| Decide | Scale, hold, pivot or kill? | Portfolio Allocator + human/policy gate | VentureDecision |

## Dynamic workflow rule

Claude/Factory should not instantiate every role for every product. It should compile the smallest organization sufficient for the stage and risk level.

For example, an internal developer tool may need no pricing strategist at build time. A public subscription product may require pricing, privacy, support and distribution work before launch.

## Product state must be durable

A venture should have a durable machine-readable state record containing at least:

- opportunity and target segment;
- evidence and uncertainty;
- product/version;
- current lifecycle stage;
- active mission graph;
- deployed environments;
- customer/market signals;
- commercial metrics;
- costs;
- risks;
- active experiments;
- decisions and rationale;
- responsible human/policy authority;
- next review/gate.

## Relationship to self-improvement

Never let product growth metrics directly rewrite the Factory's safety/evaluation rules. Product optimization and platform self-improvement share infrastructure but must retain separate evaluator authority and audit trails.
