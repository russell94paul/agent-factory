# Repository Architecture Seed — Not Yet a Migration Plan

The expected current topology is an existing `agent-factory` platform repository plus federated external workload/client repositories.

Potential future platform root domains, subject to synthesis:

```text
agent-factory/
├── apps/                # UI / mission control / briefing surfaces
├── services/            # orchestration, context, memory, eval, simulation, etc.
├── packages/            # shared contracts / schemas / SDK
├── agents/              # roles / managers / maintenance agents
├── organizations/       # blueprints / presets / doctrine / schemas
├── skills/              # reusable skills
├── evals/               # agent / team / organization / regression
├── docs/                # source-of-truth + corpus + design + decisions
├── infra/
└── tools/
```

Do not force existing code into this tree during corpus preparation. The synthesis phase must first map actual current paths and determine which moves produce enough value to justify migration cost.
