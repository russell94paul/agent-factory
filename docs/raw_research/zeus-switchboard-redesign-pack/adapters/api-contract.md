# Switchboard integration contract

The redesign is transport-independent. Connect the current tracker by implementing
`SwitchboardAdapter`; keep UI state derived from one snapshot plus one ordered event
stream.

## Snapshot

`GET /api/switchboard/snapshot?campaign_id=...`

```json
{
  "schema_version": 1,
  "cursor": "opaque-event-cursor",
  "campaign": { "id": "factory", "name": "Agent Factory" },
  "objective": {
    "id": "OBJ-42",
    "title": "Ship marketing model for client review",
    "priority": "alpha",
    "readiness": 0.82,
    "eta_seconds": 6120,
    "cost": 34.82,
    "budget_cap": 60,
    "confidence": "high"
  },
  "missions": [],
  "formation": { "nodes": [], "edges": [] },
  "messages": [],
  "approvals": [],
  "artifacts": [],
  "activity": []
}
```

## Ordered live stream

Use SSE for server-to-client telemetry unless the existing product already requires
bidirectional WebSockets. Reconnect with the last cursor and deduplicate by event ID.

`GET /api/switchboard/events?after={cursor}`

```text
id: evt_01
event: NODE_PROCESS
data: {"mission_id":"CLIENT-REV-042","node_id":"builder","progress":0.68}
```

Required execution events are listed in `switchboard-adapter.js`. Communications,
approvals, artifacts, and checkpoints use the same stream so the thread and execution
graph cannot drift.

## Commands

`POST /api/switchboard/commands`

Targets are typed: `human`, `agent`, `team`, `mission`, or `broadcast`. Each command
contains explicit `context_refs` and an idempotency key. Do not infer or silently attach
private context.

## Safety boundaries

- Pause is reversible and may execute immediately.
- Abort, publish, merge, deploy, and destructive actions require a confirmation policy.
- Approval decisions record operator ID, mission ID, evidence refs, timestamp, and reason.
- Secrets are represented only as safe metadata such as vault reference and health state.
- Demo values in the standalone build are labeled illustrative and must be replaced.

