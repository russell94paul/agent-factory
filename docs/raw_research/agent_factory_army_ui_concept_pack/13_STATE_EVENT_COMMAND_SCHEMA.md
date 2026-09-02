# Shared State, Events & Commands

## Architectural requirement

Do not create separate operational state for the gamified world.

The world should project typed domain state and events.

## Suggested domain entities

- OrganizationNode
- Agent
- Capability
- TeamBlueprint
- Formation
- Campaign
- Operation
- Objective
- Decision
- Evidence
- Artifact
- Handoff
- CommunicationEvent
- Approval
- EvaluationRun
- Doctrine
- FailureIncident
- FailureFamily
- Resource / SupplyDependency
- Environment
- Budget

## Example events

- `operation.created`
- `operation.started`
- `operation.blocked`
- `operation.completed`
- `agent.assigned`
- `agent.needs_help`
- `handoff.created`
- `decision.made`
- `evidence.published`
- `context.missing`
- `credential.unavailable`
- `environment.unready`
- `collision.detected`
- `approval.requested`
- `approval.granted`
- `failure.classified`
- `failure.recurred`
- `doctrine.promoted`

## Example world projections

| Event/state | World projection |
|---|---|
| operation.blocked | unit pinned / objective flashing |
| context.missing | severed intelligence supply |
| credential.unavailable | logistics blockade |
| collision.detected | units converging / conflict marker |
| approval.requested | Command Authorization marker |
| failure.recurred | Known Threat returns |
| doctrine.promoted | new doctrine / certification celebration |

## Typed world commands

- `target.lock`
- `operation.pause`
- `operation.abort`
- `unit.redeploy`
- `reinforcement.request`
- `specialist.deploy`
- `recon.launch`
- `context.attach`
- `formation.change`
- `handoff.execute`
- `evaluation.launch`
- `replay.fork`

All commands must route through the same RBAC, autonomy, budget and audit layer as the Command Console.
