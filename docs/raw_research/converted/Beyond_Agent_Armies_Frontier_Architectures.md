# Beyond Agent Armies
## Frontier organizational hierarchies, multi-layer architectures, and experiments for an Agentic Organization OS
*Research architecture document • 1 September 2026*

| **Core thesis —** The next frontier is not merely adding more command levels above an army. The highest-leverage designs combine hierarchy with orthogonal cognition, governance, economic, temporal, and evolutionary structures. The system should be able to compile, evaluate, reconfigure, and eventually discover organizational forms rather than hard-code one universal topology. |
| --- |

![image]
Figure 1 — A useful hierarchy above Agent → Team → Army, plus the meta-substrate that makes the hierarchy programmable.

# 1. Baseline: what the current concept already implies
The current Agent Factory vision already extends beyond a simple agent orchestrator. It frames Agent Factory as a subsystem of a broader Agentic Organization OS, with Collective Cognition, Mission Control, simulation/evaluation, an Evolution Chamber, Org-IR, self-maintenance, and a Research Army. It also proposes organizational presets that compile to Org-IR and can themselves evolve.
Current execution hierarchy: Agent → Agent Team → Agent Army.
Factory role: construct/version organizations rather than manually wire one-off agent graphs.
Collective Cognition: shared, provenance-aware organizational memory and knowledge transfer.
Evolution Chamber: compare candidate agents/workflows/topologies under measurable KPIs before promotion.
Organizational Compiler / Org-IR: a typed intermediate representation for roles, topology, tools, gates, budgets, memory, and metrics.
Self-maintenance loop: observe → diagnose → plan → evaluate → gate → canary → deploy → learn.
Research Army: continuously discovers techniques and converts credible findings into experiments rather than production changes.

| **Extension principle —** Everything in this document should be treated as an extension of that architecture, not a replacement. The question is: what new coordination mechanisms become possible once organizations themselves are first-class, versioned, executable artifacts? |
| --- |

# 2. First answer: what can exist above an Agent Army?
A taller hierarchy is useful up to a point. Past an army, the more interesting abstractions represent autonomy boundaries, governance, resource exchange, and civilization-scale knowledge/evolution rather than simply 'a larger manager'.

| **Level** | **Name** | **Primary purpose** | **What becomes possible** |
| --- | --- | --- | --- |
| **L1** | **Agent** | **Bounded specialist** | **One role/tool context, one local objective.** |
| **L2** | **Agent Team** | **Mission unit** | **Several agents with a shared outcome and coordination pattern.** |
| **L3** | **Agent Army** | **Portfolio / domain force** | **Multiple teams pursuing related missions with shared resources.** |
| **L4** | **Mission Command / Theater** | **Cross-army campaign command** | **Coordinates dependencies and strategic objectives across armies.** |
| **L5** | **Federation** | **Sovereign multi-command network** | **Independent commands cooperate through protocols, contracts, and shared standards.** |
| **L6** | **Institution / Constitution** | **Rule-making and legitimacy layer** | **Defines rights, permissions, norms, budgets, identity, arbitration, and change control.** |
| **L7** | **Ecosystem / Economy** | **Dynamic allocation and specialization** | **Organizations bid, trade capability, specialize, merge, split, and compete for missions.** |
| **L8** | **Agentic Civilization** | **Multi-institution discovery system** | **Many institutions, economies, research labs, archives, and evolutionary niches coexist.** |
| **Meta** | **Self-hosting organizational substrate** | **Makes all levels programmable** | **Org-IR, Factory, knowledge, evaluation, simulation, governance, replay, and evolution.** |

Important: L4–L8 should not all be mandatory runtime layers. They are optional organizational forms. The platform should compile only the minimum structure required by the mission, risk, scale, and uncertainty.
![image]
Figure 2 — The system should be thought of as multiple interacting planes, not a single command ladder.
# 3. Prior-art boundary: the ideas we should deliberately stand on
Several older fields already contain sophisticated ideas about organization. The research opportunity is not to rename them; it is to combine their strongest mechanisms with LLM-era capabilities: language-native role formation, programmable tools, rich traces, learned routing, continuous evaluation, code generation, and automated search over organizational designs.

| **Prior concept** | **What it already contributes** | **High-value extension to research** |
| --- | --- | --- |
| **MOISE+ / organization-oriented MAS** | **Roles, groups, missions, plans, norms; structural, functional and deontic dimensions.** | **A direct ancestor of Org-IR. Your extension: versioned executable organization specs, model/tool/budget/eval bindings, and automatic compilation/search.** |
| **Electronic institutions / normative MAS** | **Explicit rules and institutions constrain and guide agents; higher-level institutional governance has been studied.** | **A direct ancestor of a constitutional/policy plane. Your extension: machine-enforced change control, provenance, policy-as-code, and agent-generated but human-governed amendments.** |
| **Contract Net / market coordination** | **Decentralized negotiation and task allocation through calls, bids, and awards.** | **A strong base for capability markets. Your extension: bids include uncertainty, expected eval score, cost, latency, context fit, and blast radius.** |
| **Blackboard / Global Workspace** | **Specialists contribute to a shared workspace; a limited global surface helps coordinate otherwise distributed processors.** | **A strong base for Collective Cognition and attention routing. Your extension: provenance-aware broadcasts, contradiction handling, token-budgeted attention, and mission-conditioned visibility.** |
| **Stigmergy** | **Indirect coordination through traces left in a shared medium, without centralized planning or direct communication.** | **A base for organizational fields and self-assembly. Your extension: typed digital traces whose intensity/TTL/confidence attract or repel agents and teams.** |
| **Viable System Model** | **Recursive viability functions: operations, coordination, control, intelligence, policy; viable units recursively contain viable units.** | **A strong base for recursive agent organizations. Your extension: these functions become executable agent/service roles with evals and auto-reconfiguration.** |
| **Erlang/OTP supervision** | **Workers and supervisors arranged in fault-tolerant supervision trees with restart strategies.** | **A base for agent reliability hierarchies. Your extension: semantic restart/replan/escalate policies based on failure class rather than process death alone.** |
| **Kubernetes reconciliation** | **Controllers continuously reconcile observed state toward declared desired state.** | **A base for self-maintaining organizations. Your extension: desired organizational state + measured capability/readiness + safe reorganization.** |
| **Quality-Diversity / MAP-Elites** | **Maintain many diverse high-performing solutions instead of a single global winner.** | **A base for an organizational species archive: preserve different elite organizations for different mission niches.** |
| **AgentSquare / AFlow / ADAS / EvoAgent** | **Modern work searches or evolves agent modules, workflows, agent code, or multi-agent compositions automatically.** | **A base for automated organizational R&D. Your extension: search over multi-level institutions, topology, norms, memory, budgets, gates, and inter-organization protocols.** |

# 4. Frontier architecture catalog
The following architectures are intentionally different. Each should become a first-class experimentable topology in the Factory, with a small reference implementation, a mission family, and an evaluation harness.
## A. Recursive Holarchy / Viable Command
**Best for: very large systems that must remain locally autonomous but globally coherent.**
Every operational unit is simultaneously a whole and a part: a team can be a viable organization, an army can contain viable teams, and a command can contain viable armies. Each recursion carries explicit functions for operations, coordination, internal control, future intelligence, and policy.
### When to use it
Multi-repo estates where each repo/domain needs local autonomy.
Long-running organizations with changing membership or workload.
Systems where failures must be contained rather than escalated centrally.
### Capabilities unlocked
Scale without one omniscient master agent.
Give each level its own sensing, coordination, strategy, and policy capacity.
Move decisions to the lowest level that has enough context.
Diagnose missing organizational functions (for example: execution is strong but future intelligence is absent).
### Main failure mode
Recursive overhead, duplicated coordination, and policy drift between levels.
### Smallest useful experiment
Implement one Army as a five-function viable unit: Operations, Coordination, Control, Intelligence, Policy/Audit. Compare against the current manager-only hierarchy on throughput, escalation rate, recovery time, and context volume.
**Prior-art anchors:** Viable System Model; holonic/holarchy literature; recursive organizational design.
![image]
Figure 3 — Recursive holarchy: the same viability functions recur at multiple organizational scales.
## B. Polycentric Federation
**Best for: multiple autonomous armies, domains, clients, or security boundaries.**
Several commands are sovereign within their domain but share a constitution, common protocols, cross-domain contracts, and arbitration. There is no single master agent that must understand all operational detail.
### When to use it
Separate engineering domains with distinct policies.
Client or tenant boundaries.
Cross-product programs where local teams should not surrender autonomy.
### Capabilities unlocked
Fault and policy isolation.
Cross-army collaboration without global prompt/context coupling.
Federated knowledge sharing with permissions.
Graceful operation if one command or service is unavailable.
### Main failure mode
Protocol complexity, inconsistent local policies, slow cross-domain decisions.
### Smallest useful experiment
Run two armies with separate memory and managers; permit collaboration only through typed federation messages and a shared claims registry. Measure coordination quality versus direct shared-context collaboration.
**Prior-art anchors:** Polycentric governance; federated systems; electronic institutions.
![image]
Figure 4 — Polycentric federation: autonomous commands share policy, cognition, markets, and arbitration.
## C. Constitutional Institution Stack
**Best for: high-risk autonomy, multi-tenant systems, or agent-generated changes.**
A separate institutional layer defines what organizations may do, how they are formed, who may change policy, what evidence is required, how disputes are resolved, and how emergency powers expire. The institution governs armies rather than participating in their ordinary work.
### When to use it
Production code changes, deployments, credentials, customer data, or expensive actions.
Self-modifying or self-reorganizing agent systems.
Cases where 'manager says yes' is too weak an assurance model.
### Capabilities unlocked
Stable identity and doctrine independent of individual agent prompts.
Machine-checkable permissions and obligations.
Appeals/arbitration when agents disagree.
Constitutional amendments with versioning and recertification.
### Main failure mode
Policy ossification, rule explosion, agents optimizing to formal rules while missing intent.
### Smallest useful experiment
Add a Constitutional Type Checker to Org-IR: refuse to compile organizations that violate segregation-of-duty, budget, evidence, or gate constraints.
**Prior-art anchors:** Normative MAS, electronic institutions, MOISE+ deontic dimension, policy-as-code.
## D. Capability Economy / Internal Market
**Best for: dynamic task allocation when many agents/teams could perform a mission.**
Missions publish requirements; agents, teams, or armies bid based on predicted success, cost, latency, confidence, context locality, and current load. The allocator awards work using a policy-defined objective rather than static routing.
### When to use it
Large heterogeneous fleets.
Bursty workloads.
Cases where the best team depends on domain, context, model availability, or budget.
### Capabilities unlocked
Self-balancing workload.
Empirical price/performance discovery.
Specialization emerges from repeated success.
Can make capacity constraints visible rather than hidden in prompts.
### Main failure mode
Gaming bids, local optimization, unstable markets, unfair starvation of exploratory teams.
### Smallest useful experiment
Use a shadow-only market to route historical missions; compare market allocation against current static routing using accepted-change rate, cost, and latency.
**Prior-art anchors:** Contract Net Protocol, auction-based MAS, market-based control.
## E. Collective Cognition / Global Workspace
**Best for: complex missions where many specialists hold partial but relevant knowledge.**
Most cognition remains local. Only high-value facts, hypotheses, contradictions, commitments, and blockers compete for promotion into a limited global workspace that can be broadcast to relevant organizations.
### When to use it
Cross-team debugging.
Research synthesis.
Long missions with dangerous context fragmentation.
Situations where 'share everything' causes token/context overload.
### Capabilities unlocked
Selective global awareness without globally shared transcripts.
Cross-team surprise detection.
Fast propagation of decisive evidence.
A natural surface for attention, provenance, and contradiction resolution.
### Main failure mode
Attention bottlenecks, popularity bias, stale broadcasts, malicious or low-quality claims gaining salience.
### Smallest useful experiment
Implement a 20-item bounded global workspace. Promotion score = relevance × confidence × urgency × dependency centrality; evaluate whether teams require fewer direct handoffs.
**Prior-art anchors:** Blackboard systems, Global Workspace Theory, shared workspaces.
![image]
Figure 5 — Global workspace: only selected high-value state becomes organization-wide broadcast context.
## F. Morphogenetic / Stigmergic Organization
**Best for: missions whose correct team shape is unknown at the start.**
Tasks, failures, dependencies, and knowledge gaps emit typed signals into a shared field. Agents and teams self-assemble around strong attractors, split when work diverges, and dissolve when gradients disappear. Organization becomes an emergent response to the work graph.
### When to use it
Incident response.
Large unknown codebases.
Exploratory refactors and research.
Fast-changing dependency graphs.
### Capabilities unlocked
Dynamic team formation without a central planner enumerating every topology.
Work can recruit capability as evidence emerges.
Natural support for temporary swarms and task-local specialists.
### Main failure mode
Thrashing, overcrowding around salient tasks, weak global prioritization, difficult reproducibility.
### Smallest useful experiment
Represent blockers as digital pheromones with type, intensity, owner, TTL, confidence, and required capability. Compare self-assembly against a fixed team on unknown-unknown debugging missions.
**Prior-art anchors:** Stigmergy, swarm intelligence, holonic reorganization.
## G. Evolutionary Ecology / Organizational Species
**Best for: discovering architectures rather than hand-designing them.**
Organizations are encoded as genomes: role set, communication graph, memory policy, toolset, budgets, gates, retry rules, evaluator, and doctrine. Populations mutate/recombine in sandbox missions. Instead of selecting one winner, a quality-diversity archive preserves high-performing organizational species for different niches.
### When to use it
R&D laboratory.
Repeated mission families with stable evals.
Model/tool landscape changes where old designs may become obsolete.
### Capabilities unlocked
Discover non-obvious topologies.
Maintain niche specialists instead of converging on one generic organization.
Empirically test whether more agents/levels actually help.
Produce transferable organizational design insights.
### Main failure mode
Eval gaming, enormous search cost, benchmark overfitting, unsafe auto-promotion.
### Smallest useful experiment
Start with 6–10 hand-designed org genomes and mutate only topology + role prompts. Use a MAP-Elites archive indexed by cost and coordination density, with quality = mission success + regression safety.
**Prior-art anchors:** Quality-Diversity, organizational ecology, AgentSquare, AFlow, ADAS, EvoAgent.
![image]
Figure 6 — Evolutionary ecology: search over organization genomes and retain diverse niche elites.
## H. Temporal Echelons / Multi-Timescale Organization
**Best for: systems that must act now while learning and planning over days or months.**
Different organizations operate at different time horizons: reflex agents handle seconds/minutes, tactical teams handle hours, operational commands handle sprints, strategic research organizations handle months. They exchange compressed commitments and forecasts rather than full context.
### When to use it
Production operations + roadmap planning.
Trading/monitoring-like streams of events.
Any system where immediate execution and long-horizon optimization conflict.
### Capabilities unlocked
Avoid strategic agents blocking urgent work.
Allow slow deep research to influence future doctrine without touching live execution.
Detect when local optimization harms long-term goals.
### Main failure mode
Horizon mismatch, delayed feedback, strategy becoming detached from operational reality.
### Smallest useful experiment
Split one maintenance organization into immediate incident, daily reliability, and weekly architecture echelons. Measure repeated incident rate and recommendation adoption.
**Prior-art anchors:** VSM time-horizon separation; hierarchical control; organizational planning.
## I. Shadow Twin / Counterfactual Organization
**Best for: high-stakes decisions where you want autonomy without blind trust.**
A live organization executes. A side-effect-free shadow organization receives the same intent and evidence but may use a different topology/model/doctrine. A judge compares their plans, confidence, predicted outcomes, and disagreements before sensitive gates.
### When to use it
Deployment, migration, schema changes, security-sensitive modifications.
Evaluating new agent architectures in production-like traffic.
Detecting correlated reasoning failure.
### Capabilities unlocked
Continuous A/B of organizational designs.
Counterfactual evidence before irreversible action.
Early warning when the live organization is overconfident.
Safe collection of data about experimental organizations.
### Main failure mode
Cost doubles, shared evidence can still create correlated failures, judge becomes another single point of failure.
### Smallest useful experiment
Shadow the existing implementation team with a minimal independent reviewer organization on 20 real tickets; gate only on material disagreement.
**Prior-art anchors:** N-version programming, shadow traffic, red teams, ensemble disagreement.
![image]
Figure 7 — Shadow organization: counterfactual execution without side effects, followed by disagreement-aware gating.
## J. Bicameral / Adversarial Governance
**Best for: decisions where proposal quality and opposition quality both matter.**
One chamber proposes or optimizes; another is explicitly rewarded for finding invalid assumptions, missing evidence, unsafe actions, or simpler alternatives. Neither chamber can unilaterally execute high-risk changes.
### When to use it
Architecture decisions.
Novel self-improvement proposals.
Research claims and product doctrine changes.
### Capabilities unlocked
Institutionalizes skepticism instead of relying on one reviewer prompt.
Can calibrate confidence by measuring how proposals survive attack.
Creates richer training/eval traces about failure modes.
### Main failure mode
Permanent gridlock, theatrical disagreement, duplicated cost.
### Smallest useful experiment
For architecture ADRs, require a Builder Council and Skeptic Council. Score final outcome, decision latency, and defects caught pre-merge.
**Prior-art anchors:** Debate, red teaming, checks and balances, adversarial review.
## K. Mission Hypergraph / Mesh Organization
**Best for: complex work where dependencies matter more than reporting lines.**
The primary structure is a dynamic graph of objectives, claims, artifacts, risks, dependencies, and capabilities. Agents and teams attach to graph regions. Leadership is task-local rather than permanently top-down.
### When to use it
Cross-cutting refactors.
Data lineage/migration programs.
Research programs with many dependent hypotheses.
### Capabilities unlocked
Makes real dependency structure visible.
Enables local parallelism while preserving global constraints.
Supports automatic critical-path and bottleneck detection.
### Main failure mode
Graph complexity, difficult human comprehension, hidden cycles, weak accountability if ownership is too fluid.
### Smallest useful experiment
Compile one existing 18-stage DAG plus agent handoffs into a mission hypergraph; allow capability-based routing only at ambiguous nodes.
**Prior-art anchors:** Workflow/DAG systems, graph-based planning, actor/blackboard coordination.
## L. Self-Hosting Autonomic Organization
**Best for: making Agent Factory itself maintainable and eventually partially self-improving.**
The platform declares desired organizational state, continuously observes actual performance/readiness, and runs bounded reconcilers. Supervisors contain failures; repair organizations are spawned from typed diagnoses; candidates are simulated and canaried before promotion.
### When to use it
Agent Factory runtime and configuration health.
Agent prompt/model/tool drift.
Broken integrations, stale knowledge, eval degradation.
### Capabilities unlocked
Closed-loop maintenance.
Versioned recovery policy.
Automatic rollback/restart/replan based on failure class.
The Factory becomes its own first customer.
### Main failure mode
Recursive failure, repair loops causing more damage, self-certification bias.
### Smallest useful experiment
Start with one narrow reconciler: if an agent/team version loses certified eval status, automatically quarantine it and route work to the last certified version; no auto-editing yet.
**Prior-art anchors:** MAPE-K, Kubernetes reconciliation, Erlang supervision trees, self-healing systems.
![image]
Figure 8 — Self-hosting organizational reconciliation loop.
# 5. High-value novelty hypotheses to actively test
The items below are not claims of novelty. They are deliberately framed as research hypotheses that should be subjected to prior-art attack. Each is potentially valuable because it combines mechanisms that are usually studied separately.
## 1. Organizational Genome + Morphogenesis
Treat Org-IR as a genotype rather than only a config file. A mission/environment phenotype can trigger developmental rules: add a verifier when uncertainty rises, split a team when dependency entropy grows, collapse parallel scouts when evidence converges. Research question: can an organization 'grow' the right structure from mission signals instead of selecting from a fixed preset catalog?
## 2. Constitutional Type System
Compile organizational legality before execution. Roles, tools, data scopes, budgets, evidence requirements, and segregation-of-duty become types/constraints. Invalid organizations fail to compile. Research question: can a type system catch entire classes of unsafe multi-agent organizations before runtime?
## 3. Organizational Fields
Represent work pressure as typed fields: urgency, uncertainty, contradiction, dependency, risk, and knowledge deficit. Agents/teams react to field gradients, producing self-assembly and dissolution. Research question: can stigmergic fields outperform centralized routing on high-uncertainty work while remaining replayable?
## 4. Knowledge Metabolism
Move beyond memory retrieval. Claims have provenance, confidence, decay, contradiction load, usage history, and maintenance cost. Organizations digest, merge, challenge, archive, or forget knowledge. Research question: does active forgetting/curation improve multi-agent accuracy and context efficiency more than simply growing memory?
## 5. Counterfactual Organizational Twins
Continuously run one or more shadow organizations with different topology, doctrine, or models. Use disagreement as a risk sensor and source of training data. Research question: can organizational disagreement predict live failures earlier than agent-level confidence?
## 6. Temporal Polyphony
Let different echelons optimize different horizons, then exchange compressed 'commitment objects' rather than raw transcripts. Research question: can multi-horizon organizational memory reduce short-term firefighting and long-term strategy drift simultaneously?
## 7. Organizational Immune System
Maintain detectors for recurring failure signatures, provenance anomalies, permission violations, eval drift, and coordination pathologies. The response can quarantine an agent/team version and recruit a repair organization. Research question: can immune-style memory detect organizational failure classes earlier without producing alert fatigue?
## 8. Doctrine Compiler
Translate human policy and architecture doctrine into executable Org-IR constraints, eval obligations, gate rules, and observability requirements. Research question: how much organizational intent can be compiled without making policy brittle or encouraging literalist optimization?
## 9. Capability Credit Graph
Attribute accepted outcomes across agents, tools, memories, supervisors, and organizational structures rather than assigning success to the final agent. Research question: can causal/credit graphs support reliable organizational selection and prevent rewarding visible but low-value agents?
## 10. Quality-Diversity Organization Archive
Preserve multiple certified organizations for different niches rather than one 'best' team. Research question: are diverse organizational species more robust to model/tool/task drift than a globally optimized universal architecture?
## 11. Institution-Governed Institution Evolution
Allow agent institutions to propose changes to lower-level institutions, while a higher constitutional layer enforces amendment rules and recertification. Research question: can governance itself evolve safely without an uncontrolled recursive self-modification loop?
## 12. Organizational Compiler as a Search Space
Instead of searching only prompts, agents, or workflow code, search across roles, authority, topology, memory visibility, norms, budget, temporal horizon, tool access, and evaluation structure. Research question: which organizational dimensions explain the most variance in success after controlling for model quality?
# 6. Which architecture should the Factory choose?
A mission classifier should not merely select agents. It should select or synthesize an organizational topology. The first version can be rules-based and auditable; later versions can learn from outcomes.

| **Mission signature** | **Preferred architecture** | **Why** |
| --- | --- | --- |
| **Low uncertainty + repeatable + low risk** | **Pipeline / deterministic DAG with specialist insertion** | **Minimize coordination overhead.** |
| **High uncertainty + urgent** | **Morphogenetic swarm + Mission Command** | **Recruit expertise as evidence changes.** |
| **High risk + reversible only with difficulty** | **Shadow Twin + Constitutional Institution** | **Require independent counterfactual evidence and hard policy gates.** |
| **Many candidate teams + variable load** | **Capability Economy** | **Allocate based on predicted cost/quality/latency.** |
| **Cross-domain + strong autonomy boundaries** | **Polycentric Federation** | **Avoid giant shared context and central bottlenecks.** |
| **Long-lived operational system** | **Recursive Holarchy + Autonomic Reconciliation** | **Local autonomy plus recursive health functions.** |
| **Research / unknown best design** | **Evolutionary Ecology + Quality-Diversity Archive** | **Search topology and retain multiple niche elites.** |
| **Many partial knowledge sources** | **Global Workspace** | **Broadcast only decisive information.** |
| **Short-term operations + long-term strategy** | **Temporal Echelons** | **Separate time horizons and couple via commitments.** |

# 7. Experimental roadmap: push the limits without losing the production path
The fastest way to make this research real is to build a small 'Organization Lab' beside the production Factory. The lab replays recorded missions, compiles candidate Org-IR, and produces comparable traces. Nothing reaches production merely because it is interesting.

| **Phase** | **Experiment** | **Scope** | **Success criterion** |
| --- | --- | --- | --- |
| **R0** | **Org-IR enrichment** | **Add topology, authority, memory visibility, constitutional constraints, evaluator binding, and version lineage.** | **Can represent current Factory and every experiment without special-case code.** |
| **R1** | **Shadow organizations** | **Run alternative organizations side-effect-free against real or replayed missions.** | **Disagreement and outcome metrics are captured reproducibly.** |
| **R2** | **Global workspace** | **Add bounded promoted-context layer across teams.** | **Lower handoff/context volume without reducing accepted outcome rate.** |
| **R3** | **Federation protocol** | **Two independent armies exchange only typed contracts/claims.** | **Cross-domain mission succeeds without transcript sharing.** |
| **R4** | **Constitutional compiler** | **Static checks for permissions, gates, evidence, cost, and SoD.** | **Invalid organizations fail preflight.** |
| **R5** | **Capability market** | **Shadow routing auction over historical missions.** | **Allocation improves one of cost/latency/success without harming the others beyond threshold.** |
| **R6** | **Org genome search** | **Mutate limited dimensions in sandbox.** | **Search finds at least one topology that beats seeded designs on held-out missions.** |
| **R7** | **Quality-diversity archive** | **Keep multiple niche elites.** | **Archive shows distinct high-performing organizations for distinct mission classes.** |
| **R8** | **Self-reconciliation** | **Quarantine/rollback certified organization versions based on eval drift.** | **Recovery works without autonomous code mutation.** |
| **R9** | **Morphogenetic field experiment** | **Agents self-assemble based on typed work signals.** | **Comparable or better outcomes with fewer manual routing decisions.** |

# 8. Evaluation framework for organizational research
Outcome: accepted mission success, specific RED→GREEN evidence, no regressions.
Cost: total model/tool spend, human attention minutes, opportunity cost.
Speed: time-to-first-useful-evidence and time-to-green.
Coordination: messages, context bytes/tokens, handoffs, blocked time, dependency waits.
Reliability: retry rate, rollback rate, recovery time, policy violations, non-deterministic variance.
Cognition: contradiction detection, important-evidence propagation latency, stale-knowledge usage.
Adaptation: performance after model/tool/task shift, not just on the training/eval distribution.
Diversity: number of distinct certified organizational niches retained.
Governance: gate rejection rate, unsafe proposal catch rate, amendment/re-certification burden.
Human leverage: engineer minutes saved per accepted outcome, and percentage of interventions that were truly necessary.

| **Critical experimental rule —** Do not compare architectures only on benchmark accuracy. An architecture that adds three agents and 5× coordination cost for a 1% gain may be worse. Always report a Pareto view: quality, cost, latency, reliability, human effort, and risk. |
| --- |

# 9. Frontier research prompt — prior art attack + concept discovery
The following prompt is designed for a deep-research agent. It explicitly prevents novelty-by-renaming, asks the agent to search adjacent disciplines, and requires concrete experiments instead of speculative architecture diagrams.

| ROLE
You are the lead researcher for an Agentic Organization OS. Your task is not to praise the architecture. Your job is to find the strongest prior art, expose rediscovery, identify missing mechanisms, and propose experimentally testable organizational designs that become possible in the LLM era.

CURRENT BASELINE
We already have the conceptual stack:
Agent → Agent Team → Agent Army
plus Agent Factory / Organizational Compiler / Org-IR, Collective Cognition, Mission Control, evaluation, simulation, Evolution Chamber, organizational debugger/replay, executable doctrine, capability readiness, temporal echelons, knowledge transfer, and self-maintenance.

RESEARCH QUESTION
What organizational levels, topologies, institutions, coordination mechanisms, or meta-systems exist beyond or orthogonal to Agent → Team → Army that could materially increase capability, resilience, safety, scalability, learning, or discovery?

DO NOT ASSUME A TALLER HIERARCHY IS THE ANSWER.
Search for recursive, federated, market-based, stigmergic, institutional, cybernetic, cognitive, evolutionary, ecological, temporal, adversarial, and self-organizing designs.

PRIOR-ART DOMAINS — SEARCH ALL OF THEM
1. Distributed AI and classical multi-agent systems.
2. Organization-oriented MAS and agent-oriented software engineering.
3. Electronic institutions, normative MAS, computational governance.
4. Contract Net, auctions, mechanism design, computational economies.
5. Blackboard systems, global workspace, cognitive architectures, society-of-mind approaches.
6. Stigmergy, swarm intelligence, morphogenesis, collective intelligence.
7. Holons, holarchies, holonic manufacturing, recursive organizations.
8. Cybernetics: MAPE-K, Viable System Model, requisite variety, homeostasis.
9. Actor systems and fault-tolerance: Erlang/OTP supervision, distributed systems, reconciliation/control loops.
10. Workflow/DAG systems, process mining, adaptive workflows.
11. Evolutionary computation, open-ended evolution, coevolution, quality-diversity/MAP-Elites, organizational ecology.
12. Team science, organizational design, incident command, staff systems, federations, polycentric governance.
13. Modern LLM agent architecture search: ADAS, AgentSquare, AFlow/A²Flow, EvoAgent, graph/topology optimization, multi-agent debate, automated prompt/workflow search.
14. Safety engineering: N-version programming, independent verification, shadow traffic, canarying, runtime assurance, policy-as-code.

FOR EACH CANDIDATE CONCEPT
Return:
- canonical name and original domain;
- earliest/strongest sources;
- what the mechanism actually is;
- what problem it solved;
- concrete implementation examples;
- known failure modes;
- what is already directly equivalent to our current architecture;
- what changes because LLM agents can reason in language, write code, use tools, inspect traces, and be evaluated;
- novelty risk: HIGH / MEDIUM / LOW;
- a falsifiable experiment we can run in Agent Factory.

NOVELTY ATTACK
For every proposed “new” idea:
1. Search exact conceptual synonyms and older terminology.
2. Search pre-LLM literature.
3. Search adjacent disciplines where the same mechanism may have a different name.
4. Search recent LLM-agent papers and open-source implementations.
5. State explicitly whether the idea is:
   A. known and directly implemented;
   B. known but not applied to LLM agent organizations;
   C. a new combination of known mechanisms;
   D. potentially novel mechanism;
   E. too vague to evaluate.
Never call category C or D groundbreaking without evidence.

FRONTIER SYNTHESIS
After prior-art mapping, deliberately synthesize 15–25 new candidate architectures. At least:
- 3 recursive/holarchic;
- 3 federated/institutional;
- 3 evolutionary/ecological;
- 3 cognition/knowledge architectures;
- 3 safety/adversarial/self-healing architectures;
- 3 architectures that do not resemble human companies or militaries.

For each candidate specify:
- topology diagram;
- layers and authority;
- information flows;
- memory boundaries;
- how teams form/dissolve;
- failure containment;
- evaluation and credit assignment;
- when it is better than Agent → Team → Army;
- when it is worse;
- minimum viable experiment;
- expected measurable advantage;
- likely bottleneck;
- prior-art overlap.

HIGH-VALUE HYPOTHESES TO ATTACK
Test, do not assume, the following:
- Org-IR as an organizational genome with developmental/morphogenetic rules.
- A Constitutional Type System that makes invalid organizations fail to compile.
- Stigmergic “organizational fields” that cause agents/teams to self-assemble around uncertainty, urgency, contradiction, or dependency gradients.
- Knowledge metabolism: active curation, decay, contradiction resolution, and forgetting.
- Counterfactual shadow organizations as a runtime risk sensor.
- Multi-timescale temporal echelons exchanging compressed commitments.
- An organizational immune system for drift, failure signatures, provenance anomalies, and unsafe behavior.
- A quality-diversity archive of multiple elite organizational species.
- Institutions that govern the evolution of lower-level institutions.
- Causal capability-credit graphs across agents, tools, memory, managers, and topology.
- Search over organization design dimensions, not just prompts/workflows.

EXPERIMENTAL DISCIPLINE
Every architecture must be encoded as a versioned Org-IR candidate and evaluated on replayable missions.
Report a Pareto frontier across:
outcome quality, cost, latency, reliability, human attention, coordination overhead, adaptability, safety, and knowledge reuse.
Prefer small experiments that can falsify an idea quickly.

DELIVERABLES
1. Prior-art map.
2. Terminology / synonym graph.
3. Architecture comparison matrix.
4. 15–25 frontier architecture cards.
5. Five strongest “new combination” hypotheses.
6. Five strongest potentially novel hypotheses.
7. Five ideas we should explicitly stop calling novel.
8. Experiment backlog ranked by information gain / implementation effort.
9. Proposed Org-IR extensions required by the experiments.
10. A final section titled: “What would surprise us if it worked?” |
| --- |

# 10. Research questions worth turning into separate deep-research tickets
RQ1 — Is a recursive Viable System / holarchy a better top-level model than a fixed five-level Agent → Team → Manager → Master → Army hierarchy?
RQ2 — Can Org-IR be made expressive enough to encode structure, function, norms, markets, cognition, temporal horizon, and evolution without becoming an untestable universal language?
RQ3 — What organizational features explain performance after model capability is controlled for?
RQ4 — Can bounded global-workspace broadcasting outperform all-to-all/shared-transcript approaches on cross-team tasks?
RQ5 — Can typed stigmergic signals self-assemble effective teams while remaining deterministic enough to replay and debug?
RQ6 — Can a capability market allocate work better than a learned central router under changing load and tool/model availability?
RQ7 — Which constitutional constraints should be compile-time versus runtime versus human approval?
RQ8 — Does a shadow organization’s disagreement predict production failure better than agent self-confidence or evaluator scores?
RQ9 — Can Quality-Diversity preserve robust organizational species through model/tool drift better than selecting one best workflow?
RQ10 — What is the safest useful form of organizational self-maintenance before allowing self-modification?
RQ11 — How should causal credit be assigned across multi-stage agent organizations so evolution does not reward visible but non-causal contributors?
RQ12 — What knowledge should cross federation boundaries, at what abstraction level, and under what provenance/permission model?
RQ13 — When should an agent be replaced by deterministic code or a mined meta-tool, and how does that alter the organization topology?
RQ14 — How do we measure organizational complexity debt: the point where extra hierarchy/agents create more coordination cost than capability?
RQ15 — Can an institution safely govern changes to its own lower-level policies through amendment, recertification, and rollback rules?
# 11. Recommended near-term direction
The most promising research path is not to immediately build L8 'civilization'. Build the substrate that makes higher-order forms cheap to express and compare. That means expanding Org-IR, adding shadow execution, and creating a replayable Organization Lab.
Keep Agent → Team → Army as the operator-friendly default mental model.
Add Mission Command, Federation, and Institution as optional higher-order entities rather than mandatory parents.
Treat cognition, governance, temporal horizon, and evolution as orthogonal planes.
Implement Shadow Organization + bounded Global Workspace first; both generate immediate operational value and research data.
Make Constitutional constraints and evaluation bindings first-class in Org-IR before attempting autonomous self-reorganization.
Use Quality-Diversity later to maintain multiple certified organizational species; do not optimize toward one universal super-team.
Make Agent Factory itself the first target of the self-hosting reconciler, but begin with quarantine/rollback—not self-editing.

| **Most important conceptual shift —** The long-term product is not an 'army of agents'. It is a programmable ecology of synthetic organizations: organizations can be created, federated, governed, observed, compared, evolved, dissolved, and recomposed—while preserving explicit contracts, evidence, and human control. |
| --- |

# 12. Source map and research anchors
This document combines the current Agent Factory Vision with established research and engineering precedents. The references below are anchors for deeper review; they do not establish novelty of the proposed combinations.

| **Source** | **Why it matters** | **Link** |
| --- | --- | --- |
| **Current Agent Factory Vision (project source)** | **Defines the current Organizational OS direction: Agent Factory, Collective Cognition, Org-IR, organizational presets, Evolution Chamber, self-maintenance, and Research Army.** | **local project source** |
| **MOISE / MOISE+** | **Organization-oriented MAS using explicit roles, groups, missions; MOISE+ separates structural, functional, and normative/deontic dimensions.** | **https://moise-lang.github.io/** |
| **Contract Net Protocol — Reid G. Smith (1980)** | **Negotiation-based task distribution in decentralized distributed problem solving.** | **https://doi.org/10.1109/TC.1980.1675516** |
| **Hayes-Roth — A blackboard architecture for control (1985)** | **Shared blackboard plus control knowledge for adaptive multi-source problem solving.** | **https://doi.org/10.1016/0004-3702(85)90063-3** |
| **Baars / Global Workspace literature** | **Distributed specialist processors with limited global broadcast/workspace for difficult or novel cognition.** | **https://doi.org/10.1016/S0079-6123(05)50004-9** |
| **Stigmergy as a universal coordination mechanism** | **Indirect coordination through action traces in a shared medium.** | **https://doi.org/10.1016/j.cogsys.2015.12.002** |
| **Stafford Beer — Viable System Model** | **Recursive viable systems with operations, coordination, control, intelligence, and policy functions.** | **https://viable-systems.github.io/vsm-docs/overview/what-is-vsm/** |
| **Electronic Institutions / HarmonIA** | **Explicit norms, rules, procedures, governance and institutional regulation for open multi-agent environments.** | **https://doi.org/10.1007/978-3-0348-7955-2** |
| **Erlang/OTP supervision trees** | **Workers, supervisors, restart strategies, and hierarchical fault containment.** | **https://www.erlang.org/docs/27/system/design_principles.html** |
| **Kubernetes controllers** | **Desired-state reconciliation loops that continuously move actual state toward declared state.** | **https://kubernetes.io/docs/concepts/architecture/controller/** |
| **Quality-Diversity / MAP-Elites** | **Maintain a repertoire of diverse high-performing solutions across behavioral niches.** | **https://quality-diversity.github.io/** |
| **Hannan & Freeman — Population Ecology of Organizations (1977)** | **Competition and selection across populations of organizations as an alternative to assuming organizations only adapt internally.** | **https://doi.org/10.1086/226424** |
| **AgentSquare (ICLR 2025)** | **Search over modular LLM agent design components using evolution/recombination and performance prediction.** | **https://proceedings.iclr.cc/paper_files/paper/2025/hash/0ae94013da7cd459402fd77874e09ee3-Abstract-Conference.html** |
| **AFlow (ICLR 2025)** | **Automated search over code-represented agentic workflows using execution feedback and tree search.** | **https://proceedings.iclr.cc/paper_files/paper/2025/hash/5492ecbce4439401798dcd2c90be94cd-Abstract-Conference.html** |
| **Automated Design of Agentic Systems (ADAS)** | **Meta-agent search that programs and discovers new agentic systems.** | **https://arxiv.org/abs/2408.08435** |
| **EvoAgent** | **Evolutionary extension of expert agents into multi-agent systems using mutation/crossover/selection.** | **https://aclanthology.org/2025.naacl-long.315/** |
