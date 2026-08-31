# RREF3 — Inkwell / Factory-in-a-Box: Sandbox, Delegation and Out-of-the-Loop Pattern Mining

## Objective
Study `https://github.com/disler/inkwell-agent-sandboxes-and-software-factory` as a working proof-of-concept for isolated agentic software construction. Extract architectural patterns for sandboxing, nested orchestration, credential boundaries, fan-out experiments, observability, artifact harvesting, and operator-out-of-the-loop execution. Do **not** copy the application, UI, branding, or implementation wholesale.

## Why it matters
This reference combines a small application, a software factory, and disposable remote sandboxes. It may contain useful patterns for Agent Factory's future execution isolation, parallel workstreams, experiment chamber, session console, remote compute fabric, and safe autonomy progression.

## Required questions
1. What are the exact orchestration tiers and why are they separated?
2. What responsibilities stay outside the sandbox vs inside it?
3. How does the credential boundary prevent recursive sandbox creation or privilege escalation?
4. How are per-run credentials scoped/capped/revoked?
5. How is a sandbox mounted, filled, executed, observed, harvested, and torn down?
6. Which state is durable enough to recover from host/orchestrator failure?
7. How does the design keep the coding agent physically/logically close to the code while preserving operator control?
8. How are multiple sandboxes fanned out for best-of-N experiments?
9. How are results harvested without automatic destructive merge?
10. How does outside-only observability work, and what should inform our Session Console / Mission Control?
11. Which patterns could generalize to DGX Spark, local GPU nodes, Kubernetes, cloud sandboxes, or customer environments?
12. Which patterns should influence the Evolution Chamber's isolation and champion/challenger experiments?
13. What are the limitations of one-level nested orchestration for our longer-term multi-organization vision?
14. Which concepts should be `ADOPT CONCEPT | ADAPT | EXPERIMENT | REJECT`?

## Special comparison targets
Compare against:
- current Agent Factory execution and deployment paths;
- Prefect orchestration;
- future compute/integration fabric;
- session/task console;
- evaluation and canary gates;
- self-maintenance;
- organization simulation / Evolution Chamber.

## Required falsification
Identify where disposable sandboxes add unnecessary operational cost or latency, where worktrees/containers are enough, and where remote-agent isolation is materially safer. Challenge the assumption that every autonomous mission needs a VM.

## Do not copy
- Inkwell product design;
- UI layouts or styling;
- prompt text;
- code wholesale;
- naming/branding.

Mine invariants, protocols, control boundaries and failure semantics.

## Required outputs
- `SUMMARY.md`
- `SANDBOX_LIFECYCLE.md`
- `CREDENTIAL_BOUNDARY.md`
- `ORCHESTRATION_TIERS.md`
- `EXPERIMENT_CHAMBER_IMPLICATIONS.md`
- `COMPUTE_FABRIC_IMPLICATIONS.md`
- `PATTERN_MATRIX.md`
