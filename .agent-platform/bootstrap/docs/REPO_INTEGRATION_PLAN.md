# Repository Integration Plan

## Initial rule

Do not immediately reorganize the existing repo into the north-star structure.

First:

1. inspect current boundaries;
2. map imports/contracts/runtime ownership;
3. identify genuine shared packages;
4. identify research-only vs production dependencies;
5. write ADR for any monorepo migration.

## Likely end-state hypothesis

A **platform monorepo + federated workload repositories** is a strong candidate:

```text
Agent Platform Monorepo
├── control-plane/apps/packages/skills/evals/research
└── manages → connector/client/application repositories
```

External estates retain independent access/lifecycle boundaries.

Promote code to shared packages only when multiple domains actually consume it.
