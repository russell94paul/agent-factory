# Compute & Integration Fabric

## Priority

Design for it now; build integrations only when missions require them.

## Two separate concerns

### Agent communication

`Agent ↔ Agent / Team / Shared Cognition`

Handled by the communication/interaction layer.

### Software/runtime integration

`Agent Factory ↔ external runtime/tool/system`

Handled by adapters/integration contracts.

Do not merge these into one giant protocol.

## Integration contract questions

A useful adapter should expose as much as relevant of:

- identity/authentication;
- capability discovery;
- resource discovery;
- authority/permissions;
- bounded actions;
- observations/events;
- artifacts/evidence;
- health;
- cost/resource usage;
- lifecycle (deploy/pause/resume/terminate);
- rollback;
- subscriptions/wake events.

Prefer existing standards (MCP, A2A-style protocols, HTTP/SDK/CLI, OpenTelemetry/events) before inventing a proprietary protocol.

## Compute placement

Mission assembly may eventually place different workloads based on:

- capability;
- privacy;
- latency;
- cost;
- memory/GPU requirements;
- model availability;
- data locality;
- current capacity.

## NVIDIA DGX Spark

Treat DGX Spark as a future **local agent-compute node / deployment target**, not Apache Spark.

Potential use cases to research:

- persistent local inference services;
- embeddings/retrieval;
- local/private agents;
- evaluation workloads;
- local model serving;
- hybrid organizations where selected reasoning remains on external APIs.

Do not build a DGX-specific control plane until a real target exists. First define the generic compute-node/deployment capability contract and run a bounded integration experiment when hardware is available.
