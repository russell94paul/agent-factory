# Claude prompt — create the Agents-as-Configuration context pack

Paste this into a fresh Claude Code session at the root of `agent-factory`.

---

You are preparing a **read-only, sanitized architecture context pack** for an external research and
design review of Agents-as-Configuration, agent/team metrics, mission matching, readiness uplift,
MESH knowledge routing, cognitive bonds/lineage, configuration optimization and future portfolio
operations.

Do not redesign or implement anything. Do not commit, push, modify tracked files, expose secrets,
or copy credentials. Create the pack under a temporary/export directory only.

## 1. Record the repository basis

Include:

- repository name and current absolute path;
- current branch and exact commit SHA;
- clean/dirty state without copying secret values;
- complete tracked tree excluding binaries, caches, generated screenshots and sensitive material;
- current test command and directly reported result counts if run safely.

## 2. Copy the load-bearing files

Include, preserving paths:

- README, brain dump, current roadmap and architecture/design docs;
- `factory/blueprint.py`, `presets.py`, `registry.py`, `metrics.py`, `readiness.py`, `contract.py`,
  `events.py`, `tasks.py`, `handoff.py`, `bus.py`, `context.py`, `control.py`, `calibration.py`,
  `certify.py`, `evaluator.py`, `teamplan.py`, `workplan.py` and associated tests;
- all current blueprint YAML and bootstrap JSON Schemas;
- Agent Army current-state, approved-concepts, research answers, synthesis, ADRs and handoffs;
- UI source for tracker/switchboard/config-related pages;
- docs describing knowledge, memory, communication, RBAC, tenancy, provenance and secret handling;
- eval manifests and a minimal representative set of sanitized eval inputs/results.

If a requested path does not exist, record `NOT PRESENT` in the manifest. Do not invent it.

## 3. Generate derived inventories

Create:

- `inventory/config-seams.md`: config classes, fields, hashes, parsers, presets and registries;
- `inventory/metric-seams.md`: every metric/event, unit, source, consumer and outcome pairing;
- `inventory/storage-seams.md`: files, databases, event stores, caches, knowledge and secrets;
- `inventory/identity-versioning.md`: what changes hashes/certification and what does not;
- `inventory/ui-seams.md`: routes/components/data contracts relevant to configuration and operations;
- `inventory/research-status.md`: MEASURED/PARTIAL/PLANNED/ABSENT concepts with code evidence;
- `inventory/open-conflicts.md`: contradictory docs, stale claims, overlapping sources of truth;
- `inventory/security-redactions.md`: what was excluded and why, without revealing values.

## 4. Manifest

For every included file record:

```yaml
path:
source_commit:
size_bytes:
sha256:
category:
basis: MEASURED | DERIVED | STATED | ASSUMED
sensitivity: public | internal | restricted
last_checked:
notes:
```

Fail closed: do not include `.env`, vault exports, tokens, passwords, private keys, cloud connection
strings, raw customer data, production payloads or files likely to contain them. Detect secret-like
content before packaging and report excluded paths only.

## 5. Output

Produce:

```text
agent-config-context-pack/
  MANIFEST.yaml
  BASIS.md
  MISSING.md
  source/...
  inventory/...
```

Validate that every manifest SHA matches, scan the pack for obvious secret patterns, then create
`agent-config-context-pack.zip`. Report the archive path, byte size, SHA-256, included file count,
excluded count and any limitations. Do not stage or commit the export.

---

