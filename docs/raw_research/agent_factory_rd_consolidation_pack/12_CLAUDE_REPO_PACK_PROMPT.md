# Claude Prompt — Create an External Architecture Review Pack

Run this inside the current Agent Factory repository.

## Mission

Create a complete, self-contained review package of the current `agent-factory` repository so an external
AI research/architecture session can understand exactly what exists, distinguish implementation from research,
review all architecture/Agent/UI/optimization work, and reconstruct one canonical design.

Do NOT redesign the system in this session.

Do NOT modify production behavior.

## Create

```text
external-review-pack/
├── 00_README.md
├── 01_EXECUTIVE_CONTEXT.md
├── 02_REPO_INVENTORY.md
├── 03_CURRENT_IMPLEMENTATION.md
├── 04_CURRENT_ARCHITECTURE.md
├── 05_RESEARCH_INDEX.md
├── 06_SPEC_INDEX.md
├── 07_UI_UX_INDEX.md
├── 08_AGENT_RESEARCH_INDEX.md
├── 09_KNOWLEDGE_COMMUNICATION_INDEX.md
├── 10_OPTIMIZATION_EVALUATION_INDEX.md
├── 11_OPEN_DECISIONS.md
├── 12_CONTRADICTIONS.md
├── 13_IMPLEMENTATION_GAPS.md
├── 14_TEST_AND_EVIDENCE_STATE.md
├── 15_GLOSSARY.md
├── 16_FILE_MANIFEST.csv
├── source-docs/
├── current-code/
├── schemas/
├── blueprints/
├── evals/
├── tests/
├── diagrams/
└── metadata/
```

Then create:

```text
agent-factory-external-review-pack.zip
```

## Record repo identity

Include:

- repo name
- active branch
- HEAD
- git status
- dirty/untracked state
- current date
- project metadata
- top-level tree

Do not silently clean or modify the worktree.

Do not include secrets, tokens, `.env` files, credential stores or keys.

## Systematically inspect

At minimum:

```text
README.md
BRAIN-DUMP.md
docs/
docs/agent-army/
docs/design/
docs/artifacts/
docs/evidence/
docs/findings.d/
boot-prompts/
blueprints/
factory/
evaluator_service/
evals/
tests/
scripts/
```

Discover anything else relevant.

## Include material related to

- Agents
- Agent config
- blueprints
- Teams
- Army
- organization design
- communication
- memory
- knowledge / MESH
- evaluation
- simulation
- optimization
- reliability
- capability readiness
- monitoring
- missions
- tickets
- workflows
- UI/UX / Agent IDE
- dashboards
- autonomy
- self-maintenance
- research
- prior art
- security
- permissions
- provenance
- versioning
- certification
- implementation handoffs

## Research index

For every major document record:

```text
document
path
date
topic
status
source
research/design/spec/implementation/evidence
still-current / possibly-stale / superseded / unknown
major concepts
dependencies
contradictions
implementation relevance
```

Do not delete stale or duplicate material.

## Separate evidence from aspiration

For every major concept classify:

```text
IMPLEMENTED
PARTIAL
PLANNED
RESEARCHED
PROPOSED
REJECTED
UNKNOWN
```

Never mark implemented because a document describes it.

For implemented/partial claims cite actual code/tests.

## Diagrams

Create CURRENT implemented diagrams for:

1. module architecture
2. blueprint/config flow
3. evaluation/certification flow
4. lane/session/worktree flow
5. evidence-gated task lifecycle
6. current UI/status generation
7. current storage/data surfaces

Create separate proposed/research diagrams.

Clearly mark status on every node.

## Contradictions

Record:

- stale critical paths
- later-rejected concepts
- name collisions
- different definitions of Agent/Team/Army
- versioning conflicts
- evaluator conflicts
- stale implementation status
- research vocabulary that does not match code
- UI concepts ahead of backend contracts
- research concepts duplicating implemented mechanisms

Do not resolve them.

## Implementation gap matrix

Include at minimum:

- Agent Registry
- Agent Genome
- Mission Contract
- Mission lifecycle
- skill registry
- Agent health
- mission readiness
- training
- HyperMESH
- communication protocol
- Agent Architect
- Team Composer
- simulation
- Organization Lab
- optimizer
- meta-optimizer
- monitoring
- Mission Control UI
- Army
- federation
- self-maintenance

Fields:

```text
subsystem
current capability
missing capability
reusable primitives
dependencies
known research
tests/evidence
risk
implementation maturity
```

## Tests/evidence

Summarize:

- test layout
- corpus
- certification
- negative controls
- current guarantees
- unproved areas
- known limitations

## Representative code

Copy relevant source into `current-code/`.

Prioritize:

```text
factory/
evaluator_service/
scripts/
```

Include tests separately.

Exclude environments, caches, build output and secrets.

## Manifest

`16_FILE_MANIFEST.csv`:

```text
relative_path
category
size
sha256
included_reason
```

## Final response

Report:

```text
pack path
zip path
HEAD
branch
dirty/clean
number of source docs
number of code files
number of tests
major omissions
intentional exclusions
warnings
```

Then stop.
