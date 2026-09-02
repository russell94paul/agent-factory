# Installation into the existing `agent-factory` repository

## Recommended approach

This pack is an overlay. Merge it into the existing repository root.

### Safe manual install

From outside the repository:

```bash
cp -R agent-factory-bootstrap-pack/* /path/to/agent-factory/
```

Review conflicts before overwriting anything. The included installer defaults to dry-run behavior and refuses to overwrite existing files unless explicitly requested.

### Research ingestion

Put original generated research in:

```text
docs/01-research-corpus/raw/
├── chatgpt/
├── claude/
├── deep-research/
├── papers/
├── external/
├── ui-ux/
├── agent-config/
├── agent-army/
├── ontology/
├── compounding/
├── sihre/
└── unknown/
```

Keep original names where useful. Exact and semantic duplicates should be recorded, not deleted during the first pass.

## What stays outside the monorepo

Client repositories, connector repositories, customer-specific workloads and other strongly isolated estates may remain separate repositories managed by Agent Factory.

Conceptually:

```text
agent-factory platform repo
        |
        +--> manages external connector repo A
        +--> manages external connector repo B
        +--> manages client repo X
        +--> manages app Y
```

This yields a **platform monorepo + federated workload estate**.

## Repository rename

Do not rename the repository merely to match the broader vision. A later synthesis may conclude that a name such as `agent-platform` is more accurate, but that should be an explicit architecture/product decision after current-state reconciliation.
