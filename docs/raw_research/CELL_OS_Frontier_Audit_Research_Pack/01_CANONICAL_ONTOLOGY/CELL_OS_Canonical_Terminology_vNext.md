# CELL OS — Canonical Terminology Draft vNext

> Status: design/research ontology. This document distinguishes current conceptual intent from older terminology that may need retirement or renaming.

## Product thesis

CELL OS is being explored as an **operating system for synthetic organizations**: users express objectives and constraints; CELL OS assembles governed organizations of AI Operatives and deterministic workers, coordinates them through configurable organizational architectures, equips them with permissioned capabilities and structured memory, verifies consequential outcomes with evidence, and improves configurations through replay and contained experimentation.

## Core hierarchy

```text
Model
  ↓
Operative Runtime
  ↓
Operative
  ↓
Cell Mesh
  ↓
Cell
  ↓
Organization
  ↓
CELL OS
```

### Model
Foundation intelligence (e.g., frontier or specialized models).

### Operative Runtime
The governed runtime machinery that turns model intelligence into an operational entity: instructions, identity, state, memory access, capabilities, policy, budgets, observability, evaluation, recovery and lifecycle controls.

### Operative
The individual intelligent computational worker. A CELL OS Operative is intended to be more than a conventional "model + prompt + tools" agent: it is versioned, mission-aware, permissioned, observable and evaluated inside a bounded runtime.

### Deterministic Worker
A non-LLM execution component: script, service, function, workflow step, policy engine, verifier, scheduler, API adapter or other deterministic machinery.

### Cell Mesh
A coordinated **team/topology of Operatives**. A Cell Mesh is not OS federation. It may be flat, hierarchical, nested, recursive, dynamic, elastic or hybrid.

### Mesh Architecture
The coordination pattern and control logic governing a Cell Mesh. Candidate patterns include solo, sequential, pipeline, parallel, hierarchy, council, debate, swarm, blackboard, hub-and-spoke, graph, market, adversarial, recursive, temporal, elastic, deterministic-spine and hybrids.

### Mesh Topology
The actual graph of participants and links in a given Mesh instance.

### Mesh Hierarchy
How Meshes supervise, contain, invoke or coordinate subordinate Meshes. A hierarchical Mesh can contain sub-Meshes that use completely different architectures.

### Cell
A bounded mission-execution system containing one or more Cell Meshes plus the infrastructure, memory, capabilities, deterministic workers, policies, budgets, gates, lifecycle, evaluation and evidence mechanisms required to perform an objective reliably.

### Cell Blueprint / Cell Genome
The declarative, versioned source specification describing how a Cell should be constructed: roles, Operatives, topology, links, capabilities, memory, authority, resource policy, assurance, lifecycle and adaptation policy.

### Cell Image
A resolved, immutable, versioned deployment artifact representing exactly what will run: resolved Operatives, model policies, prompts/skills, deterministic code, capabilities, memory policies, contracts, digests and configuration.

### Mission
A desired outcome, not merely a task string. It may specify objective, risk, priority, temporal horizon, constraints, authority, resources, artifacts, success assertions and evidence requirements.

### Intent Contract / Mission Contract
A machine-readable agreement between human intent and execution: objective, bounds, permissions, budget, risk, success criteria, evidence and required human gates.

### Org-IR / Cell-IR
A machine-readable intermediate representation between human intent and runtime artifacts. It supports compilation from natural-language intent into topology, roles, links, dependencies, capabilities, resources, gates and contracts.

### Organizational Compiler
The system that transforms a mission and constraints into a suitable Cell/organization configuration, ideally using prior architecture outcomes, risk, cost, latency and capability availability.

## Connectivity and coordination

### Link
A first-class, typed, governed, measurable relationship between two CELL OS entities.

A Link can connect Operatives, Meshes, Cells, humans, services, tools, knowledge domains, external systems or CELL OS instances.

Potential Link fields:
- source / destination
- relationship type
- direction
- protocol / schema
- authority
- trust
- context filter
- bandwidth / rate
- latency class
- cost ceiling
- privacy / security policy
- verification requirements
- activation conditions
- fallback
- lifetime
- evidence requirements

### Candidate Link semantics
- communication
- delegation
- authority
- knowledge
- capability
- consultation
- escalation
- event
- synchronization
- consensus
- competition
- adversarial challenge
- supervision
- resource allocation
- temporal handoff
- subscription
- trust
- federation

### Link Contract
A typed specification defining what a Link carries, who may use it, what permissions flow through it, how it is validated, and how it behaves under failure or policy changes.

### Link Type Registry
An extensible registry of semantic link classes. Prefer this to hundreds of hard-coded enums.

### Link Fabric
The connective tissue of CELL OS: runtime infrastructure for creating, enforcing, observing and optimizing Links across Operatives, Meshes, Cells and external systems.

### Inter-Mesh Link
A Link connecting two Cell Meshes while allowing each Mesh to remain a separate coordination unit.

### Cell Link
A Link connecting Cells into a larger organization.

### CELL OS Federation Link
A governed relationship between independent CELL OS environments. **Do not call this Cell Mesh.** Candidate names for the federation layer include CELL Federation, CELL Fabric, InterCELL, CELL Network or Inter-OS Fabric.

### Organizational Connectivity Optimization
A research problem: optimize who should be connected to whom, through what protocol, with what authority, under what conditions and for what objective, given success, cost, latency, privacy, trust, resilience and human-burden constraints.

## Knowledge, context and cognition

### HyperMESH
The structured organizational cognition/memory substrate combining evidence/event history, semantic retrieval, artifacts, graph/relational structure, temporal context, contradiction awareness, provenance and knowledge promotion.

**Terminology audit required:** older HyperMESH sublabels using "MESH" may collide semantically with Cell Mesh as the precise team/topology concept.

### Context Virtual Memory / Context Compiler
Treats context as a scarce computational resource. Mission, role, state and retrieval policy are compiled into role-specific context pages rather than dumping all available information into prompts.

### Cognitive Governor
A meta-cognitive controller deciding when to use deterministic code, one Operative, a specialist, a larger Mesh, verification, human escalation, abstention or additional reasoning.

### Reasoning IR
A structured representation of operational conclusions (not hidden chain of thought): claims, evidence, uncertainty, assumptions, contradictions, verification requests and decisions.

### Contextual Trust / Capability Model
Trust is contextual rather than a single global score: operative × capability × mission type × environment × time. Routing can use this context.

## Execution, security and assurance

### CELL Kernel
The deterministic control plane that owns identity, authority, privileged execution, lifecycle, resource controls, capability enforcement, budgets, retries/quarantine, policy and audit.

### Capability Fabric
The permissioned substrate through which Operatives and Cells access tools, APIs, data, services, deterministic functions and specialist Cells.

### Capability Descriptor / Capability Ticket
A machine-verifiable representation of what an entity may do, where, for how long, with what approvals, and whether delegation is permitted.

### CellBus
Typed internal event/communication fabric for claims, requests, evidence, decisions, escalations, artifacts and state changes. Not every interaction should be free-form natural-language chat.

### WorkGraph / Mission DAG
The structured execution graph for deterministic and agentic work, including dependencies, gates, retries and state transitions.

### Proof-Carrying Mission DAG
A workflow in which nodes cannot claim success merely because a process returned "SUCCESS"; they must emit the required positive evidence.

### Evidence Ledger
Canonical record of consequential activity and proof: artifacts, assertions, tests, tool calls, decisions, approvals, costs, provenance, diffs, evaluator output, failures and rollbacks.

### Assurance Receipt
Human- and machine-readable explanation of why a mission should be trusted as successful: required outcome, evidence, tests, regressions, policies, gates, versions and artifacts.

## Experimentation and evolution

### Shadow Cell / Shadow Twin
A contained candidate configuration that runs against the same or replayed mission for comparison without silently becoming production authority.

### Evolution Chamber / Crucible
The experimental environment for comparing models, prompts, tools, Mesh architectures, Links, context strategies, budgets, routing, Operative combinations and workflows.

### Organizational Architecture Search
Search over combinations of Operatives, models, prompts, tools, topology, Links, context, workflows, resources and authority to discover better organizations for mission classes.

### Trace → Meta-Tool Distillation / Agentic Crystallization
Repeated successful agentic sequences can be proposed as deterministic composite capabilities, reducing cost and variance after testing and certification.

### AutoResearcher / Research Army
Research subsystem that produces hypotheses, evidence and experiments. Findings must pass gates and contained evaluation before affecting production behavior.

### Reliability Corps / Self-Maintenance
A bounded organization that observes CELL OS itself, diagnoses failures/drift, proposes repairs, evaluates them, canaries them and learns from outcomes under explicit authority constraints.

## Product surfaces

### NERVE
High-frequency human operating surface. Current expansion: **Navigation, Execution, Routing, Verification & Escalation**. Candidate primary sections: Today, Inbox, Missions, Automations, Artifacts, Knowledge, Intelligence and Systems.

### Mission Control
Expert operational cockpit: what is happening right now, where work is blocked, what is at risk, and what requires action.

### Briefing Room
Structured decision environment: objective, known facts, unknowns, assumptions, evidence, options, risks, questions and decisions required.

### Cell Studio
Advanced builder for Mesh architecture, Operatives, capabilities, communication, memory, authority, resources, evaluation and versioning.

### Replay / Profiler
Mission debugger for causal analysis of latency, costs, waits, tool calls, failures, escalations and evidence.

### Organization / Organism
Potential term for a persistent collection of Cells pursuing larger objectives. **Terminology audit required:** determine whether both terms are needed or should be merged.

## Known terminology collisions to resolve

1. **Cell Mesh vs OS federation** — Cell Mesh should mean Operative team/topology; rename OS-to-OS federation.
2. **Cell vs Operative Cell** — determine whether Operative Cell adds a necessary technical distinction or should be retired/merged into Cell.
3. **Organization vs Organism** — keep both only if they denote different runtime concepts.
4. **HyperMESH sublabels** — audit use of "MESH" to avoid confusing cognition/memory layers with Cell Mesh organizational topology.

## Canonical short statement

> **The Operative is the intelligent worker. The Cell Mesh is the team and coordination topology. The Cell is the bounded operating unit. Links define relationships. Organizations coordinate Cells. CELL OS creates, governs, observes and improves the whole system.**
