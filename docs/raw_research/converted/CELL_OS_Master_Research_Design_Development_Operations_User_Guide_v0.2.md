***CELL OS***
***Operating System for Synthetic Organizations***
***Master Research, Product Design, Development, Operations and User Guide***
***Including native agentic WorkGraph / Mission Board, Linear integration strategy, Paperclip pattern analysis, delivery phases, acceptance gates and a 200-ticket implementation plan.***
***Version 0.2 | September 2026***
North-star thesis: CELL OS is a programmable and experimentally optimizable substrate for synthetic organizations. The Cell is the executable organizational primitive. CELL OS compiles mission intent into bounded Cells, mediates capabilities through a deterministic Kernel, allocates context and resources, records evidence, supports replay and shadow evaluation, and learns without granting unchecked self-modification.
## Document status

| **Field** | **Definition** |
| --- | --- |
| **Purpose** | **A buildable research/design/operate baseline and working handbook for CELL OS.** |
| **Audience** | **Founder/operator, product designer, systems architect, AI researcher, platform engineer, SRE, security engineer and future Cell builder.** |
| **Truth discipline** | **Planned, Prototype, Implemented and Certified must remain distinct. This guide does not claim that research-stage features already exist.** |
| **Source basis** | **CELL_OS_Product_Technical_Design_v0.1.docx; CELL_OS_Roadmap_Tasks_Milestones_v0.1.xlsx; Agent Factory / ORCA research artifacts; current Linear and Paperclip product documentation.** |
| **Companion artifact** | **CELL_OS_Delivery_Backlog_v0.2.xlsx contains the proposed phase, gate and 200-ticket breakdown.** |

## Executive decision on project tracking
***Use both a native CELL OS work substrate and Linear, but give them different jobs.***
CELL OS WorkGraph is the canonical execution and evidence model. It understands Missions, Cells, Operatives, runs, gates, evidence, authority, resource envelopes, shadow runs and assurance. These concepts do not fit cleanly into a conventional issue tracker.
Mission Board is a human-facing projection over WorkGraph: board, list, graph, timeline, critical path, approval queue and evidence view.
Linear should be an optional synchronization surface for human planning, roadmap communication and teams that already live in Linear. Use its API/webhooks rather than coupling the runtime to Linear data structures.
Borrow Paperclip patterns that are genuinely agent-native: task hierarchy, agent lifecycle, budgets, approvals, heartbeats and atomic work claiming - but generalize beyond a strict manager hierarchy to pipelines, swarms, councils, elastic Cells and deterministic/agentic hybrids.
Recommendation: build WorkGraph early, use Linear during the transition, and ship the first native Mission Board only after the WorkGraph contracts are stable. External trackers become projections/adapters, not the CELL OS source of truth.
## Static table of contents
Part I - Research and product doctrine
Part II - System architecture and product design
Part III - Native WorkGraph / Mission Board
Part IV - Development guide
Part V - Operating guide
Part VI - User guide
Part VII - Research and evaluation program
Part VIII - Delivery plan, phases, gates and ticketing
Appendix A - Core schemas and state machines
Appendix B - Linear and Paperclip comparison
Appendix C - Sources and evidence basis

**PART I**
Research and product doctrine

# 1. Product thesis and design doctrine
***CELL OS should be designed as an operating system for synthetic organizations, not as a graphical wrapper around multi-agent chat. The user expresses an outcome, constraints and authority boundary. CELL OS compiles an organizational response, launches it as one or more Cells, exposes only authorized capabilities and knowledge, observes execution, proves accepted outcomes, and uses replay/shadow evidence to improve future configurations.***
## 1.1 Five non-negotiable product promises
Build organizations, not prompt collections. Reusable Cells are versioned organizational software.
Run safely. The deterministic Kernel owns identity, permissions, budgets, privileged capability calls and hard policy.
Remember structurally. HyperMESH separates authoritative evidence from derived retrieval projections and preserves provenance.
Prove outcomes. Consequential missions emit typed evidence and a Mission Assurance Receipt; agent assertions are not sufficient.
Improve empirically. Shadow Cells, replays and the Evolution Chamber compare configurations against explicit KPIs before promotion.
## 1.2 OS mapping that should remain architecturally useful

| **Traditional OS concept** | **CELL OS primitive** | **Design consequence** |
| --- | --- | --- |
| **Process** | **Operative Cell** | **A Cell has identity, lifecycle, resources, memory mounts, permissions, threads and state.** |
| **Thread** | **AI Operative** | **Concurrent cognitive worker inside a Cell; may block, wait, call capabilities and emit evidence.** |
| **Executable / image** | **Cell Image** | **Immutable, versioned and certifiable resolved organization definition.** |
| **Compiler** | **Organizational Compiler** | **Mission/blueprint -> Org-IR -> linked Cell Image.** |
| **RAM / virtual memory** | **Active Context / Context VM** | **Finite model context is managed as a scarce runtime resource.** |
| **Filesystem / storage** | **HyperMESH** | **Permissioned organizational knowledge, episodes, claims, procedures, artifacts and evidence.** |
| **System call** | **Capability Call** | **Operatives request side effects through Kernel policy rather than holding unrestricted credentials.** |
| **Driver** | **Capability Adapter** | **GitHub, browser, data warehouse, code runner, messaging, cloud and other integrations.** |
| **IPC** | **CellBus** | **Typed communication between Operatives, Cells and services.** |
| **Scheduler** | **Mission / Epistemic Scheduler** | **Allocates execution and cognitive effort according to dependency, risk, cost and uncertainty.** |
| **Debugger/profiler** | **Replay / Cell Profiler** | **Reconstruct and analyze execution, bottlenecks, resource use and evidence.** |
| **fork()** | **Shadow Twin** | **Counterfactual Cell from a controlled snapshot with contained side effects.** |

## 1.3 Implementation-truth discipline
***Every product surface and document should display maturity explicitly. Recommended states:***

| **State** | **Meaning** | **Allowed product language** |
| --- | --- | --- |
| **PLANNED** | **Approved design intent; no repository evidence yet.** | **Planned, designed, proposed.** |
| **PROTOTYPE** | **Partial path exists; not trusted for production claims.** | **Prototype, experimental, alpha.** |
| **IMPLEMENTED** | **Repository/runtime evidence confirms behavior in the stated environment.** | **Implemented, available in environment X.** |
| **CERTIFIED** | **Pinned version passed defined evals/gates and has an attestation record.** | **Certified for mission class / environment Y.** |
| **FRONTIER** | **Research hypothesis; prerequisites or evidence incomplete.** | **Research hypothesis, experiment, frontier.** |

# 2. Core product object model

| **Entity** | **Definition** | **Lifecycle** | **Key configuration** |
| --- | --- | --- | --- |
| **Objective** | **North-star outcome for a person/organization.** | **Long-lived** | **Owner, target, health, evidence.** |
| **Initiative** | **Strategic grouping of projects/missions.** | **Medium/long** | **Priority, target window, health, projects.** |
| **Mission** | **Desired executable outcome plus constraints, risk and evidence contract.** | **Ephemeral or recurring** | **Mission Contract, budget, authority, Cell Image.** |
| **AI Operative** | **Versioned cognitive worker inside a Cell.** | **Ephemeral/persistent seat** | **Model/runtime, tools, memory, communication, authority.** |
| **Worker** | **Deterministic execution unit.** | **Task/daemon** | **Code, typed I/O, retry, resources.** |
| **Cell** | **Bounded executable organization containing Operatives, Workers, mounts and policy.** | **Spawn/pause/resume/terminate** | **Cell Genome, topology, resources, authority, assurance.** |
| **Cell Image** | **Immutable resolved executable packaging of Cell configuration and dependencies.** | **Build/certify/deploy/deprecate** | **Hashes, versions, capabilities, evals, policies.** |
| **Organism** | **Persistent adaptive organization composed of Cells.** | **Long-lived** | **Strategy, topology, homeostasis, governance.** |
| **Federation** | **Cooperating CELL OS nodes under explicit trust/policy.** | **Long-lived optional** | **Identity, policy, knowledge/resource exchange.** |

# 3. Competitive and adjacent product research
## 3.1 Linear - what to borrow
***Linear remains valuable as a polished human project-management surface. Current Linear documentation describes Initiatives for strategic objectives, Projects for deliverables, issues/sub-issues, dependency relations, estimates, cycles, project health updates, a GraphQL API and webhooks. Linear also supports agent integrations: issues can be delegated to agents while a human assignee remains responsible. These are strong patterns for human accountability and integration ergonomics.***
Fast issue creation, keyboard-first workflows and low-friction editing.
Initiative -> Project -> Issue/Sub-issue planning hierarchy.
Blocking/blocked relations, milestones, estimates, cycles and project health updates.
API/webhook integration model with scoped credentials and real-time updates.
Human accountability remains visible even when an agent performs delegated work.
## 3.2 Paperclip - what to borrow
***Paperclip is explicitly designed around AI-agent organizations. Its public documentation models companies, agents, tasks, budgets, approvals, role hierarchy, agent lifecycle states, heartbeats and task checkout. Its task hierarchy traces work back to a company goal, and agent assignment can wake an agent to work. These are important agent-native patterns, but CELL OS should generalize beyond a strict employee/org-chart metaphor.***
Task hierarchy tied to the top-level goal.
Agent lifecycle and event-driven wake/heartbeat concepts.
Per-agent and organization budget limits.
Approval queues for consequential organizational changes.
Atomic task checkout to reduce duplicate work.
Auditability of agent runs and task updates.
## 3.3 Where CELL OS should deliberately differ
Treat Cell, not individual agent, as the primary executable/certifiable organizational primitive.
Support multiple topologies: hierarchy, pipeline, swarm, council, blackboard, deterministic spine and elastic phase-specific forms.
Separate task/work status from runtime attempt status.
Make evidence and assurance first-class objects; comments and agent claims do not determine success.
Put privileged side effects behind Kernel capability calls with scope, resource and policy checks.
Treat context allocation and memory mounting as runtime concerns.
Support counterfactual/shadow execution and empirical topology evaluation.
Allow external trackers to synchronize while preserving a richer canonical mission graph.
Important positioning note: Paperclip currently uses an "operating system for your AI company" framing. CELL OS therefore needs technical differentiation, not just category wording. The strongest differentiators are Cell Image + Kernel-mediated capabilities + Context Virtual Memory + evidence-backed mission completion + Shadow/Evolution + multi-formation compilation.

**PART II**
System architecture and product design

# 4. Reference architecture
USER SPACE
  Mission Control | Mission Board | Cell Studio | Briefing Room | Evolution | Replay

SYSTEM SERVICES
  WorkGraph | HyperMESH | Context Manager | Evidence | Evaluation | Registry | Observability | Supervisor

CELL KERNEL
  Identity | Lifecycle | Scheduler | Policy | Resources | Isolation | Capability API | Audit | Recovery

CAPABILITY DRIVERS
  GitHub | Browser | Files | Code Runner | Data | Prefect | Messaging | Cloud | External SaaS

COMPUTE / MODEL PLANE
  LLM providers | local models | sandboxes | containers | embeddings | specialized solvers
## 4.1 Control-plane rule
***Keep Kernel authority deterministic. LLMs may propose plans, request capabilities, estimate uncertainty or recommend policy changes; they must not be the final authority for secrets, cross-tenant access, production deployment, budget ceilings, certification or hard denial rules.***
# 5. Organizational Compiler and Cell Images
## 5.1 Compile pipeline
Mission intent
   -> Mission Contract
   -> Capability/readiness analysis
   -> Formation selection / blueprint
   -> Org-IR
   -> resolve models + skills + tools + policies + mounts + evals
   -> Cell Image
   -> preflight
   -> load / boot
   -> running Cell process
## 5.2 Cell Image minimum manifest

| **Category** | **Required contents** |
| --- | --- |
| **Identity** | **Cell name, semantic version, digest, parent lineage.** |
| **Mission compatibility** | **Supported mission classes, required inputs, risk ceiling.** |
| **Topology** | **Operatives, Workers, relations, phases, communication rules.** |
| **Runtime** | **Model/provider bindings, deterministic adapters, timeouts, retries.** |
| **Capabilities** | **Descriptors/scopes, parameter constraints, secret references.** |
| **Memory** | **HyperMESH mounts, read/write mode, retrieval policy, retention.** |
| **Resources** | **Token, cost, wall-clock, concurrency, tool-call and child-Cell ceilings.** |
| **Assurance** | **Evidence requirements, evaluators, human/policy gates, rollback.** |
| **Certification** | **Pinned eval set, threshold, approver, date, environment.** |

# 6. CELL Kernel
## 6.1 Kernel services

| **Kernel service** | **Responsibility** |
| --- | --- |
| **Lifecycle Controller** | **Load, boot, pause, resume, terminate, checkpoint and recover Cells.** |
| **Identity / Namespace** | **Actor identity, tenant/project/mission boundaries and scoped resource names.** |
| **Policy Decision Point** | **Hard allow/deny for capability requests and state transitions.** |
| **Resource Manager** | **Cost, token, time, concurrency, tool calls, model quota and child-Cell budgets.** |
| **Capability Router** | **Standard syscall-like interface to drivers; prevents direct broad external authority.** |
| **Mission Scheduler** | **Dependency-aware allocation of runnable work and execution slots.** |
| **Audit / Provenance** | **Append actor, policy decision, config and result to the event/evidence substrate.** |
| **Recovery Manager** | **Retry, quarantine, restore, suspend, last-certified fallback and escalation.** |

## 6.2 Capability call flow
Operative request: repo.merge_pull_request(...)
        |
        v
CELL Kernel
  identity?
  capability scope?
  parameter boundary?
  namespace?
  budget?
  policy?
  evidence prerequisite?
  human authorization?
        |
        +-- DENY / REQUEST GATE
        |
        v
Capability Driver -> external system -> result -> audit/evidence
# 7. HyperMESH and Context Virtual Memory
***HyperMESH should be hybrid. Write authoritative evidence/history once; project it into query-optimized forms such as temporal graph, semantic/vector indexes, episodic summaries, procedure stores and capability relationships. Derived indexes are not allowed to silently become the authority.***

| **Memory layer** | **Responsibility** | **Example representation** |
| --- | --- | --- |
| **Working** | **Temporary Operative reasoning state** | **In-memory / short TTL** |
| **Mission** | **Live shared state, dependencies, claims and evidence** | **WorkGraph / mission hypergraph** |
| **Episodic** | **What happened in prior missions** | **Event/evidence store + retrieval indexes** |
| **Semantic** | **Validated claims/relations with provenance/time validity** | **Temporal knowledge graph** |
| **Procedural** | **How-to knowledge, skills and repeatable routines** | **Versioned artifacts / deterministic tools** |
| **Capability/relationship** | **Who/what works for which mission contexts** | **Graph projections + registries** |
| **Artifacts** | **Files, code, images, reports, datasets and receipts** | **Immutable object/content-addressed store** |

## 7.1 Context Virtual Memory
***The Context Manager gives each Operative a logical knowledge address space larger than the model context window. It retrieves, authorizes, ranks, compresses, maps, refreshes and evicts Context Pages according to the current reasoning step.***
Potential knowledge space (HyperMESH)
        |
   Context fault / prefetch
        |
   authorization + ranking
        |
   compression with provenance
        v
+-------------------------+
| ACTIVE OPERATIVE CONTEXT|
| mission + objective     |
| relevant evidence       |
| current code/data       |
| pinned policy           |
+-------------------------+
# 8. CellBus and typed coordination
***Do not make chat transcripts the canonical coordination structure. CellBus should carry typed messages that can be routed, filtered, audited and converted into state/evidence where appropriate.***

| **Message type** | **Purpose** | **Canonical effect** |
| --- | --- | --- |
| **REQUEST** | **Ask another Operative/Cell/service for bounded work or information.** | **Creates dependency or service call.** |
| **RESPONSE** | **Return requested result.** | **May satisfy dependency; not automatically evidence.** |
| **CLAIM** | **Statement believed to be true.** | **Stored with provenance and uncertainty; requires validation for consequential use.** |
| **EVIDENCE** | **Typed proof object.** | **Appended to Evidence Ledger and linked to assertion.** |
| **HANDOFF** | **Transfer ownership/context.** | **Updates WorkGraph ownership and context package.** |
| **ALERT** | **Health/risk signal.** | **May create incident/decision/gate.** |
| **ESCALATION** | **Request stronger cognition or human decision.** | **Routes to Governor / approval queue.** |
| **STATE_UPDATE** | **Runtime/object state update.** | **Validated by owning deterministic service.** |

# 9. Assurance, replay, certification and Shadow Twin
## 9.1 Evidence-backed mission completion
***The core anti-false-green rule is that an execution status cannot by itself complete a mission. The Success/Assurance Contract defines positive assertions and acceptable Evidence Object types before launch where practical.***
Mission -> WorkGraph nodes -> outputs -> Evidence Objects -> evaluators/gates
                                                    |
                                                    +--> VERIFIED_SUCCESS
                                                    +--> FAILED
                                                    +--> HUMAN_DECISION_REQUIRED
## 9.2 Mission Assurance Receipt
Mission identity and Mission Contract version.
Cell Image digest and versions of Operatives, models, tools, prompts/skills and policy.
Evidence objects, tests/evals, approvals and policy decisions.
Cost/resource totals and runtime timeline.
Shadow/replay disagreement and residual uncertainty where applicable.
Rollback/checkpoint state and final verified outcome.
## 9.3 Shadow Twin
***A Shadow Twin is a counterfactual execution path forked from a controlled mission state. It should default to no production side effects. Use it for adversarial review, alternate topology/model/context tests, regression discovery and pre-promotion evidence.***
# 10. Product surfaces

| **Surface** | **Primary question** | **Core widgets** |
| --- | --- | --- |
| **Organization Home** | **What is my synthetic organization doing and is it healthy?** | **Goals, mission queue, Cells, cost, health, decisions, experiments.** |
| **Mission Board** | **What work exists, what is blocked, and what should act next?** | **Board/list/timeline/graph, dependencies, owners, evidence, gates.** |
| **Mission Control** | **What is happening right now?** | **Live topology, runs, events, resources, syscalls, gates, rollback.** |
| **Briefing Room** | **What is unknown and what decision is needed?** | **Questions, options, evidence, assumptions, approvals.** |
| **Cell Studio** | **How is this Cell built?** | **Topology, genome, capabilities, mounts, budgets, versions, diff, evals.** |
| **HyperMESH Explorer** | **What does the organization know and why?** | **Graph, episodes, provenance, contradictions, retrieval trace.** |
| **Evolution Chamber** | **Which configuration performs better?** | **Experiments, shadows, distributions, Pareto frontier, promotion.** |
| **Replay / Profiler** | **Why did this mission behave this way?** | **Timeline, calls, context, waits, costs, evidence and critical path.** |

**PART III**
Native WorkGraph and Mission Board

# 11. Why CELL OS needs a native board
***A conventional issue tracker is optimized for people coordinating planned work. CELL OS must additionally represent machine execution, authority, evidence, Cell Images, resource envelopes, multiple attempts, shadow runs, context/capability dependencies and certification. Forcing all of that into labels/comments would create an untestable second control plane.***
## 11.1 Canonical hierarchy
Objective
  -> Initiative
      -> Project
          -> Mission
              -> Work Package
                  -> Ticket
                      -> Mission Node / Run
                          -> Evidence / Gate / Decision
***This hierarchy is not mandatory at every level. A personal user may jump directly from Objective to Mission. A large enterprise can use Initiative and Project rollups. Runtime nodes and runs are always separate from human planning objects.***
# 12. WorkGraph data model

| **Object** | **Required fields** | **Special rules** |
| --- | --- | --- |
| **WorkItem** | **id, kind, parent, title, intent, owner, priority, status, namespace, timestamps** | **Every mutation is evented/provenanced.** |
| **Mission** | **MissionContract, risk, budget, authority, selected Cell Image** | **Completion derives from assurance, not comment/status.** |
| **Relation** | **from, to, type, strength, reason** | **Types include blocks, depends, related, duplicate, spawned-from, evidence-for.** |
| **Assignment** | **owner, executor(s), approver(s), lease** | **Human ownership and machine execution are distinct.** |
| **Run** | **Cell Image, attempt, state, start/end, resources, result** | **Many runs can exist for one ticket/mission.** |
| **Gate** | **policy/eval/human requirement, prerequisites, state, expiry** | **Only authorized actors/services may resolve.** |
| **EvidenceRequirement** | **assertion, acceptable types, evaluator, threshold** | **Prefer defined before execution.** |
| **EvidenceObject** | **type, artifact/hash, assertion, producer, provenance, validity** | **Append-only; may later be superseded/invalidated.** |

# 13. State machines
## 13.1 Work state
BACKLOG -> READY -> IN_PROGRESS -> IN_REVIEW -> DONE
                  |             |
                  v             v
               BLOCKED      NEEDS_CHANGES
                  |             |
                  +----> READY / IN_PROGRESS

DONE does not imply VERIFIED_SUCCESS for a mission.
## 13.2 Runtime attempt state
NEW -> QUEUED -> READY -> RUNNING -> WAITING -> VERIFYING -> TERMINAL
                         |          |          |
                         |          |          +-> HUMAN_GATE
                         |          +-> BLOCKED
                         +-> FAULTED / SUSPENDED / QUARANTINED

Terminal runtime states: SUCCESS, FAILED, TERMINATED, ROLLED_BACK.
## 13.3 Mission assurance state
UNPROVEN -> EVIDENCE_PENDING -> VERIFYING -> VERIFIED_SUCCESS
                               |
                               +-> REJECTED / HUMAN_DECISION_REQUIRED
# 14. Agent-native board operations
***Cells should be able to manage work, but only through explicit WorkGraph capabilities. Recommended capabilities:***
work.read - retrieve authorized work items and graph relations.
work.create - create child work only within the caller mission/namespace and creation budget.
work.update - update allowed fields; scope may exclude priority, owner, due date or external commitment.
work.claim - obtain an atomic lease for exclusive execution.
work.assign - delegate under explicit hierarchy/capability constraints.
work.link - add dependency/related/evidence relations.
work.comment - add narrative context; comments do not directly alter assurance.
work.request_gate - request policy/human decision.
work.propose_close - declare readiness for evidence verification.
work.close - reserved for deterministic assurance service or authorized human for specific work types.
## 14.1 Rules for Cell-created tickets
Child tickets must inherit mission/namespace and trace to the parent objective.
A Cell has a ticket-creation budget and optionally a maximum decomposition depth.
Duplicates are checked before creation using exact/semantic similarity plus parent context.
High-risk or scope-expanding tasks become proposals requiring approval rather than silent creation.
Agent-created tickets carry creator Cell, run, reasoning summary and provenance.
The Kernel can freeze board mutation while a mission is in a critical gate/recovery state.
# 15. Mission Board UX
## 15.1 Views
Board: human-friendly status lanes with Cell/human ownership and evidence badges.
List: dense planning and bulk edit.
Mission graph: dependency topology, critical path, gates, evidence, Cell topology overlay.
Timeline: target windows, milestones, cycles and mission/runtime overlays.
Decision queue: human/policy gates sorted by risk/urgency.
Evidence view: what claims are proven, pending, contested or stale.
Cell view: all work owned/executed by a Cell Image/version.
Replay view: timeline of ticket and run state changes for audit/debugging.
## 15.2 Ticket card should expose more than status

| **Card field** | **Why it matters** |
| --- | --- |
| **Outcome / acceptance** | **Prevents task-title completion theater.** |
| **Owner vs executor** | **Keeps human accountability distinct from Cell execution.** |
| **Cell Image / formation** | **Makes the organizational configuration inspectable.** |
| **Evidence status** | **Shows UNPROVEN, PENDING, VERIFIED or CONTESTED.** |
| **Run state** | **Shows current attempt separately from work status.** |
| **Dependencies / blocker reason** | **Supports critical path and automated unblock.** |
| **Resource envelope** | **Shows cost/time/tool limits and pressure.** |
| **Authority/gate** | **Explains why a Cell is waiting for a person/policy.** |
| **Provenance** | **Who/what created or modified the ticket and why.** |

# 16. Linear integration strategy
## 16.1 Architecture
Human planning / stakeholder communication
                 LINEAR
                   ^  |
          webhooks |  | API mutations
                   |  v
             Linear Bridge
                   ^  |
                   |  v
         CELL OS WorkGraph  <-- canonical execution/evidence model
                   |
         Kernel / Cells / Evidence / Runs
## 16.2 Field ownership
***Do not use naive last-writer-wins for everything. Assign canonical ownership by field. Example:***

| **Field** | **Recommended owner** | **Sync behavior** |
| --- | --- | --- |
| **Human narrative / project update** | **Linear** | **Import as context/update; not evidence.** |
| **Mission Contract / authority / evidence requirements** | **CELL OS** | **Expose link/summary to Linear.** |
| **Issue title/priority/estimate** | **Shared with conflict policy** | **Bi-directional and evented.** |
| **Runtime state / attempts / Cell Image** | **CELL OS** | **Optional summarized comment/status only.** |
| **Evidence / assurance receipt** | **CELL OS** | **Publish pointer/link, not duplicate authority.** |
| **Human assignee** | **Linear/human source** | **Preserve accountability while Cell executes.** |
| **Shadow experiment state** | **CELL OS only** | **Never alters canonical Linear work status.** |

## 16.3 Rollout sequence
Stage A - use Linear now for visible project/ticket tracking; create issue templates for Mission Contract link, acceptance evidence and Cell assignment.
Stage B - implement WorkGraph contracts/API and import/sync Linear issues into authorized namespaces.
Stage C - ship native Mission Board for agent-specific state/evidence while Linear remains a stakeholder projection.
Stage D - add field-level bi-directional synchronization, reconciliation dashboard and dead-letter handling.
Stage E - allow organizations to choose native-only, Linear-linked or other tracker adapters.

**PART IV**
Development guide

# 17. Repository and service architecture
agent-platform/
  apps/
    mission-control/
    cell-studio/
    briefing-room/
    avatar-world/              # optional
  services/
    workgraph/
    cell-runtime/
    cell-kernel/
    org-compiler/
    hypermesh/
    context-manager/
    evidence/
    evaluation/
    registry/
    evolution/
    observability/
    integrations/
  packages/
    contracts/
    org-ir/
    workgraph-sdk/
    capability-sdk/
    evidence-sdk/
    events/
  cells/
    blueprints/
    operatives/
    system-cells/
  evals/
  research/
  docs/
  infra/

External client/repository estates remain federated rather than forcibly moved into the platform monorepo.
## 17.1 Dependency rule
UI -> application/domain APIs -> services -> shared contracts
Operatives -> Kernel capability API / WorkGraph API
Operatives X direct infrastructure internals
Client namespace A X client namespace B
Research artifacts X production runtime dependency unless promoted/versioned
# 18. Contract-first development
Version schemas before implementing distributed services.
Every service boundary gets explicit request/response/event contracts and backward compatibility policy.
Use contract tests and replay fixtures for integrations.
Store behavior/config digests for Cell Images and capability drivers.
Separate declarative desired configuration from measured evidence.
Avoid hidden prompt/session state that cannot be diffed or replayed.
# 19. Event and data design
## 19.1 Canonical event envelope
event_id
event_type
schema_version
occurred_at
recorded_at
actor {human|cell|operative|worker|service}
namespace
objective_id?
mission_id?
work_item_id?
cell_id?
run_id?
correlation_id
idempotency_key?
causation_id?
source
payload
provenance
behavior_digest?
## 19.2 Storage responsibilities

| **Store** | **Canonical data** | **Avoid** |
| --- | --- | --- |
| **Relational transactional DB** | **Current object state, contracts, permissions, mappings, indexes** | **Huge immutable artifacts.** |
| **Event/evidence store** | **Append-only mission/work/runtime/policy/evidence events** | **Treating derived summaries as authority.** |
| **Object/content store** | **Files, reports, code snapshots, receipts, datasets** | **Mutable overwrite without lineage.** |
| **Temporal graph** | **Validated relations, mission/knowledge projections** | **Being the only source of truth for raw events.** |
| **Vector index** | **Semantic retrieval projection** | **Directly promoting vector-nearest text to doctrine.** |

# 20. Testing strategy

| **Test layer** | **Purpose** | **Examples** |
| --- | --- | --- |
| **Schema/contract** | **Prevent incompatible state/protocol drift** | **Round-trip, version, invalid-field tests.** |
| **Unit** | **Deterministic logic** | **State machines, policy, budget math, evidence evaluator.** |
| **Integration** | **Service and adapter correctness** | **WorkGraph + Kernel; Linear webhook replay; capability driver.** |
| **Replay** | **Reproduce historical mission behavior** | **Recorded failure -> known expected evidence.** |
| **Adversarial/security** | **Verify denials and isolation** | **Cross-tenant read, capability escalation, shadow side effect.** |
| **Agent eval** | **Measure cognitive output** | **Held-out missions, uncertainty, evidence quality, cost.** |
| **Organization eval** | **Measure formation outcomes** | **Solo vs pipeline vs swarm under matched contracts.** |
| **Resilience** | **Recovery under failure** | **Duplicate events, crash/restart, stale locks, unavailable dependencies.** |

# 21. CI/CD and release
PR: lint/contracts/unit tests/forbidden-dependency checks/security scans.
Preview: ephemeral environment runs contract and end-to-end fixtures.
Candidate Cell Image: built immutably and evaluated against pinned suite.
Certification: pass thresholds, policy and human approval where required.
Canary: limited environment/namespace/traffic/resource exposure.
Promotion: registry moves candidate -> certified with receipt.
Rollback: last-certified image and checkpoint are always available for protected mission classes.

**PART V**
Operating guide

# 22. Operating model
***CELL OS operations should be organized around three planes: platform health, mission health and cognitive/evidence health. A green infrastructure dashboard is insufficient if missions are unproven; a successful agent run is insufficient if policy/evidence is missing.***

| **Plane** | **Core signals** | **Operator action** |
| --- | --- | --- |
| **Platform** | **service health, queues, latency, storage, driver health, error rate** | **Restore service, throttle, fail over, quarantine.** |
| **Mission** | **blocked path, run state, Cell health, deadlines, approvals, resource pressure** | **Reassign, extend resources, gate, suspend, rollback.** |
| **Cognition** | **context faults, disagreement, uncertainty, retrieval provenance, model errors** | **Refresh context, escalate reasoning, invoke shadow/human review.** |
| **Assurance** | **missing evidence, failed eval, stale/superseded proof, policy violations** | **Keep unverified, request proof, reject, rerun.** |

# 23. Daily operator routine
Review system brief: critical faults, blocked missions, approvals and budget pressure.
Review mission queue and critical path; ensure high-priority work has owners and acceptable Cell Images.
Resolve human/policy gates; inspect evidence/diff rather than approving from narrative alone.
Inspect anomalies: repeated failures, context faults, capability denials, stale knowledge, unexpected cost.
Review completed mission receipts and any contested/invalidated evidence.
Review experimental candidates separately from production-certified configurations.
# 24. Incident response
## 24.1 Recovery ladder
DETECT
 -> classify retryable vs non-retryable
 -> stop unsafe side effects
 -> retry bounded transient failure
 -> suspend/quarantine unhealthy Cell
 -> restore checkpoint / last-certified image
 -> spawn diagnostic Cell if useful
 -> human escalation for unresolved/high-risk state
 -> create incident evidence + postmortem
 -> promote only validated lesson/tool/config change
## 24.2 Never do automatically in early releases
Unbounded self-edit of Kernel/policy/security code.
Silent production topology mutation.
Credential rotation or privilege expansion solely on agent recommendation.
Promotion of a Cell Image based only on proxy metrics or self-reported success.
Knowledge/doctrine promotion without provenance/evidence review.
# 25. SLO and operational metrics

| **Domain** | **Suggested metric** |
| --- | --- |
| **Runtime** | **Cell start latency, run success by mission class, stuck-run rate, supervisor detection time.** |
| **WorkGraph** | **event lag, claim conflicts, blocked minutes, orphan work, sync reconciliation backlog.** |
| **Kernel** | **capability denial rate, policy latency, budget enforcement errors, namespace violations.** |
| **Assurance** | **false-green rate, evidence completeness, replay success, certification regression.** |
| **HyperMESH** | **retrieval precision, provenance coverage, stale/contradicted context rate, context token cost.** |
| **Human load** | **approvals per accepted mission, intervention minutes, clarification loops.** |
| **Business value** | **time-to-green, cost/accepted outcome, rework/rollback, throughput per operator.** |

# 26. Cost and resource operations
Budget at mission, Cell and Operative levels; organization budget is the roll-up, not the only control.
Track cost per accepted outcome, not only cost per token/call.
Use uncertainty-driven cognitive scaling: cheap deterministic/cached paths first; expensive parallel/deep reasoning only when justified.
Resource extensions are explicit gate requests with expected value/risk, not silent overrun.
Detect repeated reasoning traces that can be converted into deterministic capabilities/meta-tools.
# 27. Knowledge operations
Review contradiction queue and superseded claims.
Monitor provenance coverage and source freshness.
Separate raw observations, candidate claims, verified knowledge and promoted doctrine.
Invalidate/refresh active Context Pages when critical knowledge changes.
Periodically evaluate retrieval on held-out mission questions rather than trusting nearest-neighbor quality.

**PART VI**
User guide

# 28. First run
Create a workspace and choose deployment/trust mode.
Describe a north-star objective in plain language.
Review the generated Mission Contract: outcome, evidence, budget, authority and risk.
Choose a starter formation or accept the compiler recommendation.
Review capabilities, data mounts, resource limits and human gates.
Run simulation/preflight when the Cell will have consequential side effects.
Launch the first Cell and watch Mission Board/Mission Control for blockers/evidence.
Review the Assurance Receipt; save useful Cell Image as a candidate/certified blueprint only after evaluation.
# 29. Building a Cell in Cell Studio
## 29.1 Start from mission shape, not agent count

| **Mission shape** | **Recommended starting formation** | **Why** |
| --- | --- | --- |
| **Simple bounded transformation** | **Solo Operative or deterministic Worker** | **Coordination overhead is not justified.** |
| **Predictable multi-stage process** | **Specialist pipeline / deterministic spine** | **Clear handoffs and evidence points.** |
| **High diagnostic uncertainty** | **Parallel hypothesis swarm + synthesis** | **Independent search can reduce time-to-root-cause.** |
| **High assurance / contested claims** | **Adversarial pair/diamond + independent verifier** | **Creates intentional challenge and proof.** |
| **Large decomposable mission** | **Command tree / federated Cells** | **Local ownership with explicit coordination.** |
| **Mission changes by phase** | **Elastic Cell** | **Expand/collapse specialists according to uncertainty and work shape.** |

## 29.2 Configure each Operative
Role and objective - what unique function does this Operative perform?
Model/runtime - why does this role need this reasoning capability?
Context mounts - what should it know, and what should it deliberately not see?
Capabilities - exact operations, parameter bounds and environments.
Communication policy - when should it emit claim, request, handoff or escalation?
Resource envelope - budget, time, tool/model use and concurrency.
Evaluation - how will you know the role is useful rather than decorative?
# 30. Using Mission Board
Create work manually or allow a scoped planning Cell to propose child tickets.
Inspect dependency and critical-path views before increasing agent count.
Assign execution to a Cell while preserving a human owner for consequential work.
Use claim/lease for exclusive tasks; use collaborative work mode when multiple Cells intentionally contribute.
Treat BLOCKED as a reasoned state: every blocked item needs blocker relation/reason.
Use the evidence badge to distinguish finished-looking work from verified outcomes.
Review agent-created scope expansions before they affect budget/dates/external commitments.
# 31. Common Cell operations

| **Operation** | **When to use** | **Operator expectation** |
| --- | --- | --- |
| **Boot** | **Start a Cell from an approved image** | **Preflight passes; capabilities/mounts/resources are visible.** |
| **Suspend** | **Pause without discarding recoverable state** | **No new side effects; lease/locks handled safely.** |
| **Terminate** | **End a Cell/run** | **Terminal event and cleanup evidence recorded.** |
| **Fork Shadow** | **Test alternate plan/configuration** | **No production side effects; result compared, not auto-promoted.** |
| **Checkpoint** | **Capture recoverable state** | **Checkpoint identifies config/context/artifact references.** |
| **Restore** | **Recover from a known checkpoint/image** | **Restore is audited and mission state reconciled.** |
| **Expand Cell** | **Add temporary/permanent specialist** | **Temporary role or new image version is explicit.** |
| **Split Cell** | **Decompose oversized responsibility into bounded Cells** | **New interfaces, namespaces and coordination contract defined.** |

# 32. Example: building an elastic engineering Cell
Mission: repair an unfamiliar integration failure

Phase 1 - Solo investigator
  ATLAS

Uncertainty remains high -> expand

Phase 2 - Parallel diagnosis
  ATLAS
   |-- AUTH specialist
   |-- runtime/code investigator
   `-- historical evidence specialist

Root cause converges -> collapse/reform

Phase 3 - Build + independent verify
  Lead -> Builder -> Verifier

High-risk promotion -> fork Shadow reviewer

Evidence converges -> human production gate -> Assurance Receipt
***Reasoning: team size follows mission uncertainty. Specialists receive different Context Pages. The verifier is independent of the builder. The Shadow does not gain production authority. The final outcome is accepted because evidence satisfies the Mission Contract, not because the lead says it is complete.***
# 33. External tracker usage
***If your team lives in Linear, create projects/issues there and let the Bridge synchronize them into WorkGraph. Delegate execution to Cells from the issue or Mission Board. Keep deep runtime/evidence details in CELL OS and publish concise links/updates back to Linear. Avoid manually mirroring every Cell event as a comment - that creates noise and weakens the canonical audit model.***

**PART VII**
Research and evaluation program

# 34. Research program principles
Every research claim becomes a falsifiable question, experiment and measurable outcome.
Use held-out mission evidence; do not evaluate a Cell only on the missions used to tune it.
Track cost, latency, rework, human burden and evidence quality alongside success.
Negative results and disproven preferred ideas are valuable organizational knowledge.
Production promotion requires mission-level evidence and regression constraints, not proxy activity metrics.
New topology/cognition/memory mechanisms begin in replay/shadow unless the risk is trivial and bounded.
# 35. Priority experiments

| **ID** | **Question** | **Experiment** | **Primary metrics** | **Decision** |
| --- | --- | --- | --- | --- |
| **R1** | **Does typed WorkGraph improve planning/runtime truth?** | **Replay real missions using stage list vs graph model.** | **Blocked minutes, status accuracy, critical path, time-to-green.** | **Ship if truth/coordination improves without excessive complexity.** |
| **R2** | **Does evidence gating reduce false-green?** | **Inject known false-green cases.** | **False-green, rework, escaped defects.** | **Core if materially improved.** |
| **R3** | **Can Cells safely create work?** | **Multi-Cell planning with creation limits/duplicate detection.** | **Duplicate/orphan tickets, scope creep, audit completeness.** | **Enable progressively by scope.** |
| **R4** | **Does Context VM beat static prompts?** | **Long-history held-out missions.** | **Success, token cost, stale-context errors.** | **Tune retrieval/mount strategy.** |
| **R5** | **Can formation routing predict team shape?** | **Solo/pipeline/swarm/council on matched mission classes.** | **Outcome, cost, latency, coordination overhead.** | **Use rules first, learned router later.** |
| **R6** | **Does Shadow Twin improve assurance enough to justify cost?** | **Primary vs primary+shadow.** | **Regression discovery, evidence quality, cost.** | **Use selectively by risk class.** |
| **R7** | **Can trace distillation reduce LLM usage?** | **Mine repeated successful traces into candidate deterministic tools.** | **Cost, latency, correctness, drift.** | **Promote only after deterministic tests.** |

# 36. Agent/team evaluation dimensions

| **Dimension** | **Measure** |
| --- | --- |
| **Outcome** | **Verified mission success, not message/task activity.** |
| **Quality** | **Regression, escaped defect, evidence completeness, contradiction handling.** |
| **Efficiency** | **Cost/accepted outcome, time-to-green, model/tool calls, context volume.** |
| **Human burden** | **Approval count, intervention minutes, clarification/rework loops.** |
| **Reliability** | **Retryability classification, recurrence, rollback, stuck rate.** |
| **Coordination** | **Idle/wait time, handoff loss, duplicate work, communication overhead.** |
| **Trust** | **Policy compliance, provenance, version pinning, replayability, uncertainty visibility.** |

**PART VIII**
Delivery plan, phases, gates and ticketing

# 37. Recommended build order
***The guiding dependency is simple: trust and measurement before autonomous organizational evolution. The existing CELL OS v0.1 roadmap already follows this principle. v0.2 adds WorkGraph/Mission Board and external tracker integration as first-class build tracks rather than leaving project coordination outside the architecture.***

| **Phase** | **Name** | **Window** | **Gate** | **Primary exit** |
| --- | --- | --- | --- | --- |
| **P0** | **Foundation & Architecture** | **W1-4** | **G0** | **Glossary, ADRs, trust boundaries, events, implementation truth.** |
| **P1** | **WorkGraph & Mission Contracts** | **W3-8** | **G0** | **Mission/evidence/work contracts and agent-native board API.** |
| **P2** | **Cell Runtime MVP** | **W6-14** | **G1** | **One immutable Cell Image executes end to end.** |
| **P3** | **CELL Kernel & Capability Security** | **W9-18** | **G1** | **Identity, capabilities, policy, resources, isolation, audit.** |
| **P4** | **Mission Control & Mission Board** | **W12-22** | **G2** | **Operator + Cell planning/execution UI.** |
| **P5** | **Assurance, Replay & Certification** | **W16-27** | **G3** | **Evidence, replay, receipt, lockfile, registry promotion.** |
| **P6** | **HyperMESH & Context VM** | **W20-34** | **G4** | **Hybrid knowledge + permissioned context paging.** |
| **P7** | **Cognitive Governor & Formation Router** | **W24-37** | **G4** | **Uncertainty/risk routing, readiness, elastic formations.** |
| **P8** | **Shadow Twin & Evolution Chamber** | **W28-42** | **G5** | **Contained experiments, comparisons, Pareto, promotion.** |
| **P9** | **External Work Integrations** | **W30-43** | **G5** | **Linear/GitHub bridge; WorkGraph remains canonical.** |
| **P10** | **Avatar / Social / Blueprint Network** | **W34-48** | **G6** | **Optional spatial/social shell and blueprint ecosystem.** |
| **P11** | **CELL Mesh Federation** | **W40-55** | **G7** | **Two-node safe federation.** |
| **P12** | **Organism & Self-Hosting** | **W48-59** | **G8** | **Persistent orgs and bounded maintenance.** |
| **P13** | **Security Hardening & v1** | **W54-60** | **V1** | **SLO/security/perf/recovery/docs/beta release gates.** |

# 38. Ticket taxonomy

| **Level** | **Example** | **Purpose** |
| --- | --- | --- |
| **Objective** | **Ship CELL OS v1 with evidence-backed Cells** | **North-star outcome.** |
| **Initiative** | **Assurance substrate** | **Strategic grouping of multiple projects.** |
| **Project/Epic** | **Mission Assurance + Replay** | **Deliverable workstream.** |
| **Ticket** | **Implement EvidenceObject ingestion** | **Actionable change with acceptance/evidence.** |
| **Sub-ticket** | **Add artifact hash validator** | **Small implementation unit.** |
| **Mission Node** | **Run contract test / deploy fixture** | **Runtime execution node, not planning object.** |

## 38.1 Ticket template
TITLE
Short outcome-oriented statement.

WHY
Parent objective / problem / evidence.

SCOPE
In / out.

ACCEPTANCE CONTRACT
Machine-checkable where possible.

EVIDENCE REQUIRED
Tests / artifact / screenshot / diff / benchmark / approval.

RISK + AUTHORITY
What a Cell may change; gates.

DEPENDENCIES
Blocking relations.

OWNER / EXECUTOR
Human owner; Cell/Operative/Worker executor.

RESOURCE ENVELOPE
Estimate, budget, time, external calls.

TRACEABILITY
Mission / Cell Image / run / source issue links.
# 39. 90-day execution focus
Weeks 1-4: canonical terminology, trust boundaries, Mission Contract, WorkGraph, Evidence and event envelopes.
Weeks 3-8: agent-native WorkGraph API, permissions, claim leases, first Linear mapping/reconciliation design.
Weeks 6-12: compile and run one existing real workflow as Cell v0; do not redesign everything before proving the runtime boundary.
Weeks 9-13: Kernel capability router, resource accounting, secrets indirection and human gates.
Weeks 11-13: Mission Board thin slice showing real WorkGraph state, Cell assignment, blocker and evidence status.
By day 90: demonstrate one real mission created from contract, executed by a Cell, reflected in Board/Linear, controlled by Kernel and closed by positive evidence.
# 40. Release gates

| **Gate** | **Must be true** |
| --- | --- |
| **G0 Architecture** | **Core schemas versioned; WorkGraph and implementation-truth rules active.** |
| **G1 Cell Runtime** | **One real mission executes from immutable image; privileged calls/resources are Kernel-controlled.** |
| **G2 Operator UX** | **Normal create/inspect/start/stop/plan flow needs no direct DB/manual runtime edits.** |
| **G3 Assurance** | **Positive assertions, replay fixture and Mission Assurance Receipt prove what ran and why accepted.** |
| **G4 Knowledge/Cognition** | **Authoritative evidence remains distinct from projections; retrieval is provenance-aware; Governor cannot bypass policy.** |
| **G5 Evolution/Integrations** | **Shadows cannot mutate production; external trackers remain projections; promotion is gated.** |
| **G6 Experience** | **Spatial/social modes are state-equivalent and accessible; reputation is evidence-weighted.** |
| **G7 Mesh** | **Two nodes federate identity/policy/knowledge/capability without private-default violations.** |
| **G8 Organism** | **Structural changes are shadow-evaluated before production mutation.** |
| **V1 Release** | **Security/performance/recovery/docs/beta/support readiness checklist passes.** |

Companion delivery workbook: CELL_OS_Delivery_Backlog_v0.2.xlsx contains 14 phases, 10 gates, 200 proposed tickets, WorkGraph object mapping, Linear/Paperclip pattern mapping and the research matrix. Treat dates/estimates as planning hypotheses until reconciled with the current repository and available team capacity.

**APPENDIX A**
Core schemas and state machines

# A1. Mission Contract sketch
mission_id
objective
mission_class
namespace
risk_class
priority
constraints[]
authority_envelope
resource_envelope
success_assertions[]
evidence_requirements[]
required_capabilities[]
knowledge_mount_policy
human_gates[]
rollback_policy
temporal_horizon
created_by
version
# A2. Cell Image sketch
cell_image_id
name
version
digest
org_ir_digest
operatives[]
workers[]
topology
models[]
capabilities[]
knowledge_mounts[]
communication_policy
resource_envelope
authority_policy
evaluators[]
evidence_contract
recovery_policy
certification_record
lineage
# A3. WorkItem sketch
work_item_id
kind
namespace
objective_id?
initiative_id?
project_id?
mission_id?
parent_id?
title
intent
status
priority
owner_actor
executor_actor?
approver_actor?
claim_lease?
relations[]
acceptance_contract
evidence_requirements[]
resource_envelope?
due_window?
labels[]
created_by
updated_by
created_at
updated_at
source_system
source_external_id?

**APPENDIX B**
Linear and Paperclip comparison

# B1. Decision matrix

| **Capability** | **Linear** | **Paperclip** | **CELL OS target** |
| --- | --- | --- | --- |
| **Human project UX** | **Excellent** | **Good agent-centric** | **Mission Board should approach Linear usability over time.** |
| **Initiative/project hierarchy** | **Strong** | **Goal/project/task hierarchy** | **Objective/Initiative/Project/Mission/WorkGraph.** |
| **Agent-native task execution** | **Integrations/agent sessions** | **Core concept** | **Core, but executable unit is Cell.** |
| **Agent lifecycle** | **Integration-specific** | **Explicit states/heartbeats** | **Cell + Operative runtime lifecycle.** |
| **Budgets** | **Not core agent budget primitive** | **Per-agent/company budget** | **Mission/Cell/Operative resource envelopes.** |
| **Approvals** | **Workflow/product features** | **Agent hiring/governance approvals** | **Kernel gates for side effects/topology/promotion.** |
| **Task checkout** | **Conventional assignment** | **Atomic checkout** | **Claim lease + collaboration mode.** |
| **Evidence/assurance** | **Links/comments/integrations** | **Audit/task history** | **Typed evidence ledger + receipt + certification.** |
| **Team topology** | **Human teams** | **Strict org hierarchy orientation** | **Hierarchy + pipeline + swarm + council + elastic + hybrid.** |
| **Context/memory** | **External to tracker** | **Agent/runtime dependent** | **HyperMESH + Context VM.** |
| **Shadow/evolution** | **Not core** | **Not core task primitive** | **First-class counterfactual/evolution path.** |

# B2. Final tracking recommendation
Do not choose Linear OR a native agent board. Use Linear as an optional human planning and stakeholder bridge while CELL OS owns the canonical WorkGraph, evidence and runtime semantics. This avoids rebuilding Linear before CELL OS can execute a trusted Cell, while preventing the long-term architecture from being trapped inside a generic issue schema.

**APPENDIX C**
Sources and evidence basis

# C1. Project sources
CELL_OS_Product_Technical_Design_v0.1.docx - north-star product/runtime, object model, HyperMESH, Kernel, UX and gates.
CELL_OS_Roadmap_Tasks_Milestones_v0.1.xlsx - 60-week roadmap baseline, milestones, gates and 140-task plan.
Agent_Factory_Frontier_Architecture_Prioritization_Pack.docx - build assurance/evidence/measurement before frontier autonomy.
ORCA / Operative Cell framework artifacts - Mission Contract, Org-IR, HyperMESH, Shadow Twin, Evidence, certification and presets.
# C2. Current external references used for tracker research

| **Reference** | **URL** |
| --- | --- |
| **Linear API and Webhooks** | **https://linear.app/docs/api-and-webhooks** |
| **Linear Agents** | **https://linear.app/docs/agents-in-linear** |
| **Linear Agent Developer Guide** | **https://linear.app/developers/agents** |
| **Linear Initiatives** | **https://linear.app/docs/initiatives** |
| **Linear Projects** | **https://linear.app/docs/projects** |
| **Linear Issue Relations** | **https://linear.app/docs/issue-relations** |
| **Linear Parent/Sub-issues** | **https://linear.app/docs/parent-and-sub-issues** |
| **Linear Cycles** | **https://linear.app/docs/use-cycles** |
| **Paperclip - What is Paperclip?** | **https://docs.paperclip.ing/guides/welcome/what-is-paperclip/** |
| **Paperclip - Key Concepts** | **https://docs.paperclip.ing/guides/welcome/key-concepts/** |
| **Paperclip - Agents** | **https://docs.paperclip.ing/guides/org/agents/** |
| **Paperclip - Managing AI Agents** | **https://paperclip.inc/docs/guides/board-operator/managing-agents** |
| **Paperclip GitHub** | **https://github.com/PaperclipAI/paperclip** |

# C3. Research caution
***External product features change quickly. The comparison in this guide reflects documentation retrieved in September 2026 and should be refreshed before final implementation or procurement decisions. The proposed CELL OS architecture is a synthesis and design recommendation; repository inspection is required to label any component Implemented or Certified.***
