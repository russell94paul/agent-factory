# Proposed Bootstrap Pack Structure

```text
bootstrap_pack/
├── README.md
│
├── schemas/
│   ├── agent.schema.json
│   ├── team.schema.json
│   ├── mission.schema.json
│   ├── hypermesh.schema.json
│   ├── knowledge-object.schema.json
│   ├── knowledge-request.schema.json
│   ├── context-pack.schema.json
│   ├── curriculum.schema.json
│   ├── optimization-run.schema.json
│   └── optimization-postmortem.schema.json
│
├── presets/
│   ├── agents/
│   │   ├── factory-architect.yaml
│   │   ├── agent-architect.yaml
│   │   ├── triage-investigator.yaml
│   │   ├── verifier.yaml
│   │   ├── sentinel.yaml
│   │   └── knowledge-cartographer.yaml
│   │
│   ├── teams/
│   │   ├── factory-development.yaml
│   │   ├── rapid-triage.yaml
│   │   ├── deep-research.yaml
│   │   └── knowledge-intelligence.yaml
│   │
│   ├── hypermesh/
│   │   ├── rapid-recall.yaml
│   │   ├── deep-root-cause.yaml
│   │   ├── research-brain.yaml
│   │   └── audit-brain.yaml
│   │
│   ├── retrieval/
│   │   ├── low-latency.yaml
│   │   ├── relational.yaml
│   │   ├── historical.yaml
│   │   └── adaptive.yaml
│   │
│   └── optimizers/
│       ├── rapid.yaml
│       ├── deep.yaml
│       ├── exploratory.yaml
│       ├── conservative.yaml
│       └── root-cause.yaml
│
├── protocols/
│   ├── mission-contract.yaml
│   ├── knowledge-request.yaml
│   ├── knowledge-response.yaml
│   ├── knowledge-change-request.yaml
│   ├── agent-handoff.yaml
│   ├── conflict-report.yaml
│   ├── promotion-decision.yaml
│   └── optimization-postmortem.yaml
│
├── evals/
│   ├── agent-builder/
│   ├── retrieval/
│   ├── context-quality/
│   ├── access-control/
│   ├── knowledge-promotion/
│   └── optimizer/
│
├── diagrams/
├── research-prompts/
├── glossary/
└── adr/
```
