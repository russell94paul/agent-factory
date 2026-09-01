# Client Review — Canonical Read Model

## Principle

The Client Review should be a **projection/read model** over Agent Factory delivery state.

It should not become a competing system of record.

Internal Agent Factory primitives should map into one stable client-facing contract.

## Proposed model

```yaml
client_review:
  project:
    id:
    name:
    client:

  review:
    status:
    freshness_state:        # LIVE | LAST_VERIFIED | STALE | UNAVAILABLE
    last_updated:
    last_verified_at:
    last_review_at:

  intent:
    objective:
    requested_outcome:
    requirements: []
    assumptions: []
    exclusions: []
    acceptance_criteria: []
    unresolved_ambiguities: []

  progress:
    completion_percent:
    current_stage:
    milestones: []

  delivered:
    - id:
      title:
      summary:
      business_impact:
      status:
      evidence_refs: []

  evidence:
    - id:
      type:
      label:
      status:
      source:
      verified_at:
      summary:
      technical_detail_ref:

  decisions:
    - id:
      question:
      context:
      blocking:
      recommendation:
      options: []
      status:
      delivery_impact:

  risks:
    - id:
      title:
      severity:
      impact:
      mitigation:
      owner:
      client_action_required:

  next:
    - id:
      title:
      status:
      dependency:

  acceptance:
    status:                 # NOT_READY | READY_FOR_REVIEW | READY_FOR_ACCEPTANCE | ACCEPTED | CHANGES_REQUESTED
    accepted_at:
    accepted_by:
    notes:
```

## Transformation boundary

```text
Agent Factory internal state
           ↓
Client Review assembler
           ↓
visibility / confidentiality filtering
           ↓
claim grounding
           ↓
client_review read model
           ↓
UI
```

## Requirements

- Avoid duplicating existing mission state.
- Preserve provenance where available.
- Each client-visible success claim should be traceable to evidence.
- Missing optional fields must not break the UI.
- Stale or unavailable state must be represented honestly.
- Do not expose credentials, secrets, prompts, raw reasoning, or internal-only incident information.
