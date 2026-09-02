# Advanced Projects Command / Black Site

## Purpose

A persistent autonomous cross-company improvement organization that asks:

> Given everything the company and its agents have learned, what is the highest-leverage change we should test next against the current success criterion?

## Inputs

- engineering failures and friction
- agent traces
- recurring interventions
- product usage
- support cases
- customer requests
- sales objections
- cost anomalies
- architecture bottlenecks
- external research
- new models/tools
- competitor/market signals
- doctrine performance
- recurrence metrics

## Success criteria

The lab should always optimize against an explicit, frozen objective such as:

- revenue
- delivery speed
- quality
- feature adoption
- cost
- client satisfaction
- reliability

It must not self-rewrite the success criterion during an experiment.

## Loop

```text
OBSERVE
  ↓
CONNECT SIGNALS
  ↓
OPPORTUNITY DETECTION
  ↓
HYPOTHESIS
  ↓
SKEPTIC / RED CELL
  ↓
EXPERIMENT DESIGN
  ↓
SANDBOX BUILD
  ↓
EVALUATE
  ↓
WAR GAME / CHAMPION-CHALLENGER
  ↓
CANARY
  ↓
PROMOTE / MODIFY / KILL
  ↓
LEARN
  ↺
```

## Internal roles

- Research Commander
- Evidence Scouts
- Synthesis Officer
- Skeptic / Red Cell
- Experiment Designer
- Builder
- Evaluator
- Architecture Mapper
- Doctrine Officer

## Opportunity / leverage model

Do not rely on one fake-precision score. Use a Pareto view over:

- expected outcome delta
- evidence strength
- reach/frequency
- confidence
- cost
- risk
- time
- reversibility
- strategic fit

## Cross-team convergence

A candidate becomes stronger when independent signals converge, e.g.:

Support + Engineering + Sales + Telemetry + Agents
→ same customer pain
→ feature / automation candidate

## What the lab may change

- agent configuration
- prompts/models/tools
- memory/retrieval
- team composition
- communication topology
- workflow
- deterministic automation
- product feature
- UX
- architecture
- documentation
- commercial process
- repetitive human work
- deletion of low-value process

## Autonomy boundaries

Early maturity:

`discover → research → propose → human approval → experiment`

Later bounded maturity:

`discover → research → sandbox prototype → evaluate → automatically kill/continue`

Production, spend, external communication, security and strategic decisions can remain gated.
