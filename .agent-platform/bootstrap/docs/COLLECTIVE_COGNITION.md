# Collective Cognition Fabric

## Goal

Make the organization cumulative rather than episodic: new missions should benefit from prior missions, prior experts, proven fixes, failures, evidence, and doctrine without copying entire transcripts into every agent.

## Knowledge object candidates

- observations;
- claims;
- evidence;
- facts;
- hypotheses;
- decisions;
- artifacts;
- failures/successes;
- procedures/skills;
- capabilities;
- entities/relationships;
- system topology;
- mission history;
- evaluation outcomes;
- confidence;
- contradictions;
- temporal validity;
- provenance.

## Mission-shaped knowledge/context graph

For each mission, compile a temporary graph/view containing only the most relevant:

```text
mission intent
├── affected repositories/systems
├── dependencies
├── current runtime state
├── policies / gates
├── previous similar missions
├── prior failures / known-good fixes
├── relevant agents/teams/experts
├── evidence / uncertainty
└── active mission participants
```

This graph can evolve as the mission produces new evidence.

## Context compiler

The graph is not the prompt. A context compiler creates role-specific packets:

```text
Mission Graph
   ├── builder packet
   ├── tester packet
   ├── reviewer packet
   ├── incident commander packet
   └── human briefing packet
```

Each packet should have:

- source/provenance links;
- freshness/validity;
- trust/confidence;
- token/size budget;
- explicit omissions/unknowns where important.

## Cross-agent experience transfer

When a mission starts:

1. classify task family and affected systems;
2. search prior missions and capability evidence;
3. identify experienced agents/teams;
4. retrieve or generate experience summaries;
5. synthesize conflicting lessons;
6. include the minimum relevant guidance in mission context;
7. notify an expert only when active consultation is worth the cost.

## Storage hypothesis

Do not prematurely choose one database. Likely needs a combination of:

- relational/event metadata;
- immutable evidence/artifacts;
- semantic/vector retrieval;
- graph relationships;
- temporal/provenance metadata.

The first vertical slice should reuse current memory/wiki/event stores where possible and prove the retrieval/context behavior before a new knowledge infrastructure rewrite.
