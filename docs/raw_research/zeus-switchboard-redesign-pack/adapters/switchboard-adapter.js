/**
 * Switchboard data boundary.
 *
 * Replace DemoSwitchboardAdapter with an implementation backed by the tracker
 * REST/SSE/WebSocket APIs. UI components should never depend on transport.
 */
export class SwitchboardAdapter {
  async getSnapshot() { throw new Error('getSnapshot() not implemented'); }
  async listMissions(_filters = {}) { throw new Error('listMissions() not implemented'); }
  async getMission(_missionId) { throw new Error('getMission() not implemented'); }
  async sendCommand(_envelope) { throw new Error('sendCommand() not implemented'); }
  async decideApproval(_approvalId, _decision) { throw new Error('decideApproval() not implemented'); }
  async createMission(_spec) { throw new Error('createMission() not implemented'); }
  async controlRun(_runId, _action) { throw new Error('controlRun() not implemented'); }
  subscribe(_listener) { throw new Error('subscribe() not implemented'); }
}

export const eventTypes = Object.freeze([
  'SIM_START', 'NODE_ENTER', 'INPUT_REVEAL', 'EDGE_TRANSFER',
  'NODE_PROCESS', 'OUTPUT_REVEAL', 'METRIC_UPDATE', 'LOG_APPEND',
  'BRANCH', 'RETRY', 'FAILURE', 'RECOVERY', 'NODE_EXIT', 'SIM_COMPLETE',
  'MESSAGE_POSTED', 'HANDOFF_CREATED', 'APPROVAL_REQUESTED',
  'APPROVAL_DECIDED', 'ARTIFACT_CREATED', 'RUN_CHECKPOINTED'
]);

export function commandEnvelope({ missionId, target, body, contextRefs = [] }) {
  return {
    schemaVersion: 1,
    idempotencyKey: crypto.randomUUID(),
    missionId,
    target, // { type: 'agent'|'team'|'mission'|'human'|'broadcast', id: string }
    body,
    contextRefs, // typed IDs, never silently copied transcript blobs
    requestedAt: new Date().toISOString()
  };
}

