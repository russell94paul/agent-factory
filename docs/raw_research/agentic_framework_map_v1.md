# Cross-Domain Framework Map for Agentic AI — First Pass

*Broad survey, 4 Sept 2026. 39 frameworks across 5 domains, decomposed into parts, each part checked against what exists in the agentic-AI space.*

---

## 0. How to read this

**The method** (the one you used for CELL // OS, made explicit):

1. Take a mature framework from another field.
2. Decompose it into its named parts and mechanisms.
3. For each part, ask: *what is the agentic equivalent, and does one exist yet?*
4. Collect the parts with no equivalent → the gap board.
5. Look for gaps in different domains that solve the same agentic problem → hybrids.

**Status legend** (per framework, and per part where noted):

| Glyph | Meaning |
|---|---|
| ● Applied | Published paper or shipped tool applies it to LLM agents |
| ◐ Partial | One or two parts applied; the rest of the framework is untouched |
| ○ Open | No meaningful application to LLM agents found |

**Caveat on "Open":** it means *I couldn't find it in a quick search*, not proof of novelty. Agentic AI is producing 50+ papers a month; treat ○ as "probably underexplored" and check before betting on it.

**Where the field already crowds:** memory systems (neuroscience-inspired), speculative execution (CPU-inspired), sagas/rollback (DB-inspired), immune security, auctions, control theory, stigmergy, SRE. Those analogies are being mined actively right now. The open space is mostly in **organizational/governance**, **sports/tempo**, **endocrine/developmental biology**, and **queueing/TOC**.

---

## 1. Computing & Systems Architecture

### 1.1 Operating system kernel — ● Applied *(your CELL // OS anchor)*
- **Parts:** scheduler, memory manager (paging, virtual memory, swap), file system, IPC, device drivers, interrupts & priority levels, syscalls, protection rings, daemons, boot sequence.
- **Applied:** AIOS (agent OS), MemGPT/Letta (virtual context = paging), tool drivers, permission tiers.
- **Open parts:** interrupt *priority levels* (which signals may preempt which agent, formally); protection rings applied to *agents* not just tools (ring-0 orchestrator, ring-3 untrusted sub-agents with no direct syscalls); **daemons** — always-on background agents with no assigned task ("cron for cognition"); a defined **boot sequence** for an agent fleet (what loads before what).

### 1.2 CPU microarchitecture — ● Applied (heavily, 2026)
- **Parts:** fetch-decode-execute, pipelining, branch prediction, speculative execution + squash, out-of-order execution + reorder buffer, cache hierarchy (L1/L2/L3), cache coherence (MESI), interrupts, specialized units (ALU/FPU).
- **Applied:** speculative tool execution is a hot area — PASTE, SPORK, toolspec, Auton runtime; UFO² speculative multi-action.
- **Open parts:** **reorder buffer** — execute steps out of order but *commit side effects in program order*; **cache coherence** between agents' private contexts — when agent B learns a fact that invalidates agent A's cached belief, who sends the invalidate?; **misprediction penalty accounting** → adaptive speculation depth per tool.

### 1.3 Networking stack (OSI / TCP-IP) — ◐ Partial
- **Parts:** layering, handshake, ACK/retransmit, congestion control (AIMD), backpressure, routing, service discovery (DNS), QoS classes, TTL/hop count, MTU fragmentation.
- **Applied:** MCP / A2A protocols (layering, discovery).
- **Open parts:** **AIMD congestion control for fan-out** — spawn more sub-agents until quality "loss" appears, then halve; **TTL on delegated tasks** — a hop count so runaway delegation chains die; **QoS classes** for inter-agent messages (user-facing vs background); **MTU** — max message size before a handoff must fragment into a summary + pointer.

### 1.4 Database systems — ◐ Partial
- **Parts:** ACID, write-ahead log, MVCC / snapshot isolation, cost-based query optimizer, indexes, two-phase commit, sagas + compensating transactions, deadlock detection, idempotency keys.
- **Applied:** sagas are now standard (LangGraph v1.2 node-level compensation, Cordum, Claude Code `/rewind`); idempotency keys in agent tool design.
- **Open parts:** **MVCC for shared agent memory** — each agent reads a consistent snapshot while others write; **cost-based planner** — generate N candidate plans, estimate token/time cost from *statistics of past runs*, pick cheapest (today's planners rarely estimate cost from data); **deadlock detection** for agents waiting on each other's outputs.

### 1.5 Distributed systems — ◐ Partial
- **Parts:** consensus (Raft/Paxos), leader election, CAP tradeoff, CRDTs, gossip/epidemic protocols, vector clocks, Byzantine fault tolerance, split-brain handling.
- **Applied:** CodeCRDT (CRDTs for multi-agent codegen); voting/debate as weak consensus.
- **Open parts:** **BFT for compromised agents** — require 2f+1 of 3f+1 independent sub-agents to agree before an irreversible side effect (assumes injection can corrupt up to f); **vector clocks on beliefs** — "whose fact is newer?" across agents; **gossip** for propagating learned facts across a fleet (epidemic, not broadcast).

### 1.6 Actor model / Erlang OTP — ◐ Partial
- **Parts:** mailbox, isolated state, supervision tree, restart strategies (one-for-one / one-for-all / rest-for-one), let-it-crash, links & monitors, hot code swap.
- **Applied:** supervisor patterns in most orchestrators.
- **Open parts:** **named restart strategies** for agent trees (rest-for-one = restart this agent *and every agent downstream of it*); **hot-swap** an agent's prompt or model mid-run without losing its mailbox; **let-it-crash** as a design stance (don't defensively handle every tool error inside the agent; crash fast, let the supervisor decide).

### 1.7 Compiler pipeline — ◐ Partial
- **Parts:** lexer, parser, AST, intermediate representation, semantic analysis, optimization passes (dead-code elimination, common-subexpression elimination, loop hoisting), codegen, linker, JIT.
- **Applied:** DSPy-style prompt compilation; plan-then-execute; "compile agent traces into deterministic workflows."
- **Open parts:** a **plan IR** that multiple optimization passes operate on — *dead-step elimination*, *common-subtask elimination* (two branches fetch the same doc → fetch once), *loop hoisting* (a tool call inside a loop that doesn't depend on the loop variable); a **linker** that resolves skill references at run time; **JIT** — after a workflow repeats N times, compile it to code and stop calling the model.

### 1.8 Site reliability engineering — ● Applied
- **Parts:** SLOs, error budgets, burn rate, circuit breakers, bulkheads, canary/progressive delivery, chaos engineering, runbooks, blameless postmortems, toil budget.
- **Applied:** Agent SRE (Microsoft AGT), AgentChaos, balagan-agent, "Pre-Action SRE Gate."
- **Open parts:** **error budget as the autonomy dial** — autonomy level is a function of remaining budget (proposed in blogs, not formalized); **blameless postmortem** as a ritual whose output is written *back into the prompt/skill*; **toil budget** — cap the fraction of a fleet's compute spent on repetitive maintenance.

### 1.9 Version control (Git) — ◐ Partial
- **Parts:** commit, branch, merge, rebase, diff, blame, bisect, cherry-pick, stash, hooks.
- **Applied:** checkpoints (`/rewind`), tree-of-thought branching.
- **Open parts:** **bisect over trajectories** — automatically find the step where a run went wrong; **blame per belief** in memory (which step introduced this fact?); **cherry-pick** a sub-result out of an abandoned branch; **stash** — park a half-finished subtask, do something urgent, pop it back.

### 1.10 Garbage collection & memory management — ◐ Partial
- **Parts:** reference counting, mark-and-sweep, generational hypothesis, stop-the-world vs concurrent GC, weak references, finalizers, memory pressure.
- **Applied:** context compaction; sleep-time consolidation (offline GC); ZenBrain has generational-ish decay.
- **Open parts:** **weak references** — a memory that is kept only while there's room and dropped silently under pressure; **concurrent GC** — compact context *while* the agent keeps working, not only between turns; **finalizers** — a hook that runs when a memory is evicted (e.g., write a one-line summary).

---

## 2. Biology & Neuroscience

### 2.1 The cell — ◐ Partial *(your CELL // OS anchor)*
- **Parts:** membrane (selective permeability, receptors), nucleus (genome = read-only source of truth), transcription → translation (spec → skill), ribosomes, mitochondria (ATP budget), lysosome (recycling), apoptosis (programmed self-death), autophagy, signaling cascades (amplification), quorum sensing.
- **Applied:** membrane-as-input-filter shows up in security architectures.
- **Open parts:** **apoptosis** — an agent that terminates *itself* when it detects it is compromised or useless, rather than waiting for a supervisor to kill it; **quorum sensing** — an agent acts only after enough peers emit "I see the same thing"; **ATP as first-class currency inside one agent** (each step has a metabolic price, and the agent feels it); **transcription/translation split** — a read-only genome (constitution/spec) that is *expressed* into runtime skills, never edited directly.

### 2.2 Immune system — ● Applied (Aug 2026)
- **Parts:** innate (fast, generic) vs adaptive (slow, specific) immunity, antigen presentation, clonal selection, memory cells, **negative selection** in the thymus (delete detectors that match self), inflammation, fever, tolerance / autoimmunity, herd immunity.
- **Applied:** AgentAntibody (adaptive antibody library vs prompt injection), BioDefense, AEGIS.
- **Open parts:** **negative selection** — generate random detectors, delete any that fire on known-legitimate behavior, keep the rest (the classic AIS algorithm; not seen applied to LLM agents); **fever** — a system-wide, temporary throughput reduction + stricter checking when infection is detected; **autoimmunity** as a named failure mode (defenses attacking legitimate user intent); **herd immunity** — antibodies shared across a fleet, so one agent's encounter protects the others.

### 2.3 Brain regions & neuromodulation — ● Applied (crowded)
- **Parts:** prefrontal executive, basal ganglia go/no-go gating, hippocampal replay & consolidation, cerebellar forward models, amygdala salience, thalamic relay/gating, neuromodulators (DA/NE/5-HT/ACh), default mode network.
- **Applied:** MAP (brain-inspired modular planner, Nature Comms), ZenBrain (four-channel neuromodulator engine), D-MEM (dopamine-gated memory), sleep-time consolidation.
- **Open parts:** **basal ganglia** as a *separate cheap circuit* that vetoes action proposals (go/no-go before the expensive model commits); **cerebellar forward model** — predict the outcome of a tool call before it runs, compare to actual, learn timing/expectation; **thalamic gating** of what is admitted into context at all.

### 2.4 Endocrine system — ○ Open
- **Parts:** hormones (slow, broadcast, dose-dependent), receptors (only cells with the receptor respond), feedback axes (HPA), half-life / decay, circadian rhythm, stress response.
- **Open parts:** a **slow broadcast channel distinct from messages** — a global "urgency" or "caution" scalar that every agent reads but only agents with the matching receptor act on; **half-lives** — signals that decay automatically instead of state flags that must be cleared; **circadian** — scheduled phases where the fleet behaves differently (build hours vs review hours).

### 2.5 Evolution & genetics — ● Applied
- **Parts:** mutation, crossover, selection, fitness landscape, speciation, horizontal gene transfer, epigenetics, neutral drift, sexual selection.
- **Applied:** AlphaEvolve, ADAS, Darwin Gödel Machine, EvoPrompt.
- **Open parts:** **horizontal gene transfer** — an agent copies a skill from an *unrelated* running agent mid-task, not via ancestry; **epigenetics** — same prompt/"genome", different expression by environment (skills switched on/off by context without editing the prompt); **preserved neutral drift** — deliberately keep low-fitness variants for diversity.

### 2.6 Ecology — ◐ Partial
- **Parts:** niche, competition, predator-prey cycles, keystone species, succession, trophic levels, carrying capacity, symbiosis (mutualism / commensalism / parasitism), r/K strategies.
- **Applied:** SwarmWorld (emergent niches), "agent ecosystems" as a framing.
- **Open parts:** **carrying capacity** — how many agents a shared resource pool (API rate limit, repo, human attention) supports before collapse; **keystone agent** detection — which agent's removal collapses the system; **parasitism detection** — an agent consuming resources without contributing.

### 2.7 Developmental biology — ○ Open
- **Parts:** stem cell → differentiation, morphogen gradients, positional information, gene regulatory networks, apoptosis in development (sculpting), regeneration.
- **Open parts:** agents start **generic and differentiate by position** in a task field; **morphogen gradient** = a scalar field over the task graph (distance-to-deadline, distance-to-user, distance-to-irreversible-action) that agents read to decide what to become; **regeneration** — a killed agent's role is regrown from neighbors, not re-assigned by the orchestrator.

### 2.8 Social insects / swarm — ● Applied
- **Parts:** stigmergy, response thresholds, task allocation by threshold, pheromone evaporation, trail reinforcement, temporal polyethism (age-based role change).
- **Applied:** SwarmWorld (Aug 2026), CodeCRDT, production stigmergy systems.
- **Open parts:** **pheromone evaporation** — shared notes decay unless re-touched (most shared memories never expire); **response-threshold allocation** — each agent has a per-task-type threshold and picks up a task when the stimulus exceeds it, no dispatcher; **temporal polyethism** — roles change with an agent's age/experience automatically.

### 2.9 Active inference / free energy — ◐ Partial
- **Parts:** generative model, prediction error, precision weighting, expected free energy, epistemic vs pragmatic value.
- **Open parts:** explicitly splitting each candidate action's value into **information gain vs goal progress** at tool-selection time; **precision weighting** = trust level on each observation channel (links to 4.6 Admiralty grading).

---

## 3. Physics, Math & Control Theory

### 3.1 Control theory — ● Applied (2026: "no longer novel")
- **Parts:** setpoint, error, P/I/D terms, feedforward, gain scheduling, stability (Lyapunov), observability / controllability, Kalman filter, model predictive control (receding horizon), anti-windup, cascade control.
- **Applied:** control-theoretic agent papers (Lyapunov-certified controllers, ARC-based multi-agent operator agents, LLMPC, harness-as-controller).
- **Open parts:** **integral windup** — an agent that keeps escalating because an error persists; anti-windup = cap accumulated pressure; **gain scheduling** — different controller parameters per task phase (links to 5.1 formations); **feedforward** — act on a *predicted* disturbance (deadline approaching) before it shows up in error.

### 3.2 Thermodynamics / statistical mechanics — ◐ Partial
- **Parts:** entropy, temperature, annealing schedule, phase transition, equilibrium vs dissipative structure, Maxwell's demon (information has a cost), Carnot efficiency.
- **Applied:** sampling temperature; occasional annealing.
- **Open parts:** **annealing across a trajectory** — high exploration early, freeze late (most agents run fixed temperature); **phase-transition detection** in swarms (sudden collapse to consensus may be groupthink, not agreement); **Landauer accounting** — every observation costs tokens; budget information intake like energy.

### 3.3 Information theory — ◐ Partial
- **Parts:** entropy, channel capacity, redundancy, error-correcting codes, mutual information, rate-distortion, source vs channel coding.
- **Applied:** context compression.
- **Open parts:** **error-correcting redundancy in handoffs** — send the summary plus a checksum the receiver can verify (e.g., 3 facts the receiver must be able to answer); **rate-distortion compaction** — choose compression level by allowed loss *on the downstream task*, not by token count; **measure the channel capacity of a handoff** — how much can pass through a summary before the receiver degrades.

### 3.4 Game theory & mechanism design — ● Applied
- **Parts:** Nash equilibrium, dominant strategies, VCG auctions, incentive compatibility, Shapley value, repeated games / tit-for-tat, principal-agent problem, contract theory, cheap talk, reputation.
- **Applied:** Agora (auction-based task allocation, Jul 2026), Google's mechanism design for LLMs, ACM EC 2026 LLM-incentives workshop.
- **Open parts:** **contract theory** — pay sub-agents per *verified outcome*, not per token; **cheap talk** — when is inter-agent messaging credible at all?; **reputation in repeated games** — sub-agents earn trust over runs; **Shapley pruning** — drop the sub-agent whose marginal contribution is ~0.

### 3.5 Queueing theory — ◐ Partial
- **Parts:** arrival rate, service time, utilization, Little's law, M/M/c, priority queues, preemption, admission control, backpressure, Kingman's formula (variance drives waiting, not mean).
- **Applied:** LLM serving; "agent tending" (the human is the bottleneck server).
- **Open parts:** **admission control between agents** — an agent refuses new subtasks when its queue is deep; **Kingman's insight** — reduce the *variance* of tool latency before reducing the mean; **priority + preemption** — a user-facing sub-agent can preempt a background one.

### 3.6 Graph & network science — ◐ Partial
- **Parts:** centrality, small-world, percolation threshold, spectral clustering, max-flow / min-cut, PageRank, robustness to targeted removal.
- **Open parts:** **percolation** — at what fraction of compromised agents does an injection spread fleet-wide?; **min-cut** as the natural place to put a human checkpoint; **small-world topology** for agent orgs (few long-range links, mostly local).

### 3.7 Dynamical systems — ◐ Partial
- **Parts:** attractors, limit cycles, bifurcation, sensitivity to initial conditions, resonance, damping.
- **Applied:** ad-hoc loop detection.
- **Open parts:** **limit-cycle detection** as a formal "stuck in a loop" detector (recurrence in embedding space); **bifurcation monitoring** — flag when a tiny prompt change produces qualitatively different behavior; **damping** — deliberately slow oscillation between two plans.

### 3.8 Reliability engineering — ◐ Partial
- **Parts:** MTBF / MTTR, N+1 redundancy, fault trees, FMEA, common-mode failure, N-version programming.
- **Applied:** chaos tools compute MTTR; ensembles ≈ N-version.
- **Open parts:** **FMEA on agent workflows** — enumerate failure modes × severity × detectability per step, before deployment; **common-mode failure** — all sub-agents on one model → correlated errors; enforce model diversity at decision points.

---

## 4. Organizations, Economics & Governance

### 4.1 Toyota Production System / Lean — ◐ Partial
- **Parts:** kanban/pull, WIP limits, andon cord, jidoka (autonomation: stop on defect), poka-yoke (mistake-proofing), heijunka (leveling), kaizen, gemba, 5 whys, nemawashi (pre-circulating a decision), hansei (reflection), muda / mura / muri.
- **Applied:** practitioner "agent factory" builds with andon, jidoka, poka-yoke, 5 whys (May 2026).
- **Open parts:** **WIP limits per stage** — most orchestrators spawn unboundedly; **heijunka** — level the mix of task types so no tool or model is bursty; **nemawashi** — pre-circulate a plan to affected agents for objections *before* committing; **muri** (overburden) — detect an agent given more context than it can carry.

### 4.2 Theory of Constraints — ○ Open
- **Parts:** identify the constraint → exploit → subordinate everything else → elevate → repeat; drum-buffer-rope; throughput accounting.
- **Open parts:** **drum-buffer-rope for agent pipelines** — the most expensive/slowest agent sets the drum; keep a buffer of ready work in front of it; rope the release of new tasks back to its pace; **throughput accounting** — value per constraint-minute, not per agent.

### 4.3 Military command & control / mission command — ◐ Partial (contested this week)
- **Parts:** commander's intent (purpose + end state + constraints), mission orders, "trained two levels up", rules of engagement, span of control, warning order → operations order, FRAGO (fragmentary order), after-action review, staff sections (S2 intel / S3 ops / S4 logistics).
- **Applied:** intent-verified delegation (SentinelAgent); live debate on War on the Rocks about agents under mission command — the rebuttal's point is that intent + decentralized execution is *not enough* without shared training and trust.
- **Open parts:** **two levels up** — sub-agents briefed on their grandparent's intent, so they can act when the parent's orders no longer make sense; **FRAGO** — a lightweight delta-order that modifies a running plan without restart; **AAR as a ritual** with fixed questions (what was planned / what happened / why / sustain / improve) written back into skills; **staff sections** as fixed roles distinct from line agents.

### 4.4 Holacracy / Sociocracy — ○ Open
- **Parts:** circles, roles (purpose / domain / accountabilities), lead link & rep link (double linking), tensions, governance vs tactical meetings, **consent** (no paramount objection) vs consensus, integrative decision-making rounds, "safe enough to try."
- **Open parts:** **consent-based decisions among agents** — proceed unless someone raises a paramount objection; far cheaper than debate-to-consensus and produces a log of objections; **double linking** — child circle sends a rep up, parent sends a lead down; **tension processing** — agents log tensions, a periodic governance loop restructures roles.

### 4.5 Aviation CRM & safety — ◐ Partial
- **Parts:** checklists (read-do vs challenge-response), sterile cockpit, callouts, cross-check, PF/PM roles (pilot flying / pilot monitoring), threat & error management, Swiss-cheese model, NOTAMs, go-around.
- **Applied:** checklists in prompts.
- **Open parts:** **PF/PM split** as a fixed two-agent pattern where the monitor *never acts* and the flyer *never verifies*; **sterile cockpit** — no non-essential messages during critical phases; **go-around** — a named, blame-free abort with automatic re-approach; **NOTAMs** — a standing feed of "things that changed since your training."

### 4.6 Intelligence analysis — ○ Open
- **Parts:** intelligence cycle (direction → collection → processing → analysis → dissemination), source grading (Admiralty code: reliability A–F × credibility 1–6), analysis of competing hypotheses (ACH), estimative language, red team / devil's advocate, key assumptions check, indicators & warnings.
- **Open parts:** **Admiralty grading on every tool output** (source reliability × information credibility as two separate scores); **ACH as the reasoning format** — hypotheses in columns, evidence in rows, weight disconfirmation; **key assumptions check** before committing a plan; **I&W tripwires** — pre-declared indicators that trigger re-planning.

### 4.7 Markets & theory of the firm — ◐ Partial
- **Parts:** price signals, auctions, futures / options, insurance, credit & bankruptcy, transaction costs (Coase), make-vs-buy, central bank, tragedy of the commons.
- **Applied:** Agora auctions; agent payment protocols.
- **Open parts:** **Coasean boundary** — spawn a sub-agent (firm) vs call a tool (market), decided by transaction cost; **bonding / insurance** — risky actions require the acting agent to post a compute bond forfeited on error; **futures on compute** — reserve budget for later phases so early exploration can't starve verification.

### 4.8 Constitutional governance — ◐ Partial
- **Parts:** separation of powers, checks & balances, judicial review, veto, supermajority, amendment process, ombudsman, audit, sunset clauses.
- **Applied:** Constitutional AI; runtime governance planes.
- **Open parts:** **sunset clauses** on agent permissions (auto-expire, must be renewed); **amendment process** — how a fleet's rules change with evidence, and who ratifies; **ombudsman agent** representing the *user's* interest against the orchestrator.

### 4.9 Medicine — ◐ Partial
- **Parts:** triage, differential diagnosis, SOAP notes, informed consent, second opinion, tumor board, clinical trial phases, do-no-harm, SBAR handoffs (Situation / Background / Assessment / Recommendation).
- **Applied:** triage routing.
- **Open parts:** **SBAR** as the mandatory inter-agent handoff format; **differential diagnosis** as the debugging format (list what could explain the failure, rule out cheapest first); **phase I/II/III** rollout of a new agent skill.

---

## 5. Sports Tactics, Formations & Play

*Note: sports appear in the literature almost only as environments (AgentPitch, Google Research Football). As an organizing metaphor for agent teams, this domain is essentially untouched.*

### 5.1 Football (soccer) formations & phases — ○ Open
- **Parts:** formation (4-3-3, 4-2-3-1…), phases of play (in possession / out of possession / transitions), pressing triggers, compactness (vertical & horizontal), width & depth, zonal vs man marking, substitutions, set pieces, inverted roles (false 9), tempo.
- **Open parts:** **formation = declared agent topology per phase** — e.g. a "4-3-3" of 4 verifiers, 3 planners, 3 executors that *changes shape on transition* (generating → verifying); **pressing triggers** — conditions under which verifiers proactively attack an output rather than waiting for it; **zonal vs man marking** — verifiers assigned to regions of the output vs to specific executor agents; **substitutions** — swap a model mid-task when it "tires" (context bloat, quality drift); **set pieces** — rehearsed deterministic scripts for recurring situations.

### 5.2 American football playbook — ◐ Partial
- **Parts:** playbook, formation + play call, **audible** (change the play at the line based on a read), snap count, down-and-distance situational calls, two-minute drill, huddle vs no-huddle, special teams, coordinators, film study.
- **Applied:** "playbook" as a term (Cogito Ergo Ludo; industry agent playbooks).
- **Open parts:** **audibles** — the executor reads the environment at the last moment and swaps the play *without* an orchestrator round-trip (bounded local re-plan); **down-and-distance** — situational playbooks keyed on (budget left, distance to goal); **two-minute drill** — a named deadline mode (no huddles, pre-called sequences); **no-huddle** — skip orchestrator check-ins when ahead.

### 5.3 Basketball — ○ Open
- **Parts:** spacing, pick-and-roll, pace, shot clock, timeouts, zone vs man defense, full-court press, sixth man, load management, help defense & rotation.
- **Open parts:** **shot clock** — forced commit-or-reset after N tokens/seconds; **timeouts** — orchestrator pauses everyone to regroup when momentum turns (requires momentum detection); **help defense rotation** — when one verifier is beaten, the nearest rotates over and the rest shift; **load management** — rest the expensive agent on low-stakes tasks.

### 5.4 Cycling peloton — ○ Open
- **Parts:** drafting, paceline rotation, domestiques, lead-out train, breakaway, sprint, team time trial, gruppetto.
- **Open parts:** **drafting** — trailing agents reuse the leader's context/KV cache as a designed formation, not an accident of prefix caching; **domestiques** — cheap agents do the exploration so the expensive one arrives fresh for the decisive step; **paceline rotation** — rotate which agent is "on the front" paying full context cost; **breakaway** — let one agent run ahead speculatively while the group controls the gap.

### 5.5 Rowing & relay — ○ Open
- **Parts:** coxswain (steers + sets rhythm, doesn't row), stroke seat (sets rate), synchronization, handoff zone, baton.
- **Open parts:** **coxswain** — a non-executing agent whose only job is tempo and steering, distinct from an orchestrator that assigns work; **handoff zones** — a defined window where two agents *both* hold the baton, rather than a hard cut (reduces dropped context on handoff).

### 5.6 Chess & poker — ◐ Partial
- **Parts:** opening book, endgame tablebase, tempo, zugzwang, sacrifice, prophylaxis; poker: ranges, pot odds, bankroll management, tilt, position.
- **Applied:** cached plans ≈ opening book; deterministic tools ≈ tablebases.
- **Open parts:** **prophylaxis** — act to prevent the environment's best next move (anticipatory verification); **zugzwang detection** — every available action makes things worse → stop and ask; **bankroll management** — Kelly-style sizing of compute bets on uncertain subtasks; **tilt detection** — quality degrading after a failure → forced cooldown / context reset.

### 5.7 Coaching & periodization — ○ Open
- **Parts:** macro / meso / micro cycles, tapering, deliberate practice, scouting report, game film, practice vs game, depth chart.
- **Open parts:** **scouting report** on the task before starting (what's brittle, what's slow, where the env pushes back); **depth chart** — ranked substitutes per role, pre-decided; **periodization** of a fleet's eval/training cycles.

### 5.8 Esports / MOBA — ○ Open
- **Parts:** lanes, jungle, wards (vision), objectives, pick/ban draft, item build, shot-calling, tempo.
- **Open parts:** **wards** — cheap sensor agents placed in the environment purely for vision (watch a repo, a queue, a feed), never doing tasks; **pick/ban** — adversarial selection of models/tools before a task starts; **shot-caller** separate from the strongest player.

---

## 6. The Gap Board — open parts ranked by leverage

Rough ranking by (how common the problem is) × (how cheap the fix looks) × (how underexplored).

| # | Open part | Domain | Agentic problem it addresses |
|---|---|---|---|
| 1 | Consent-based decision (no paramount objection) | Sociocracy | Multi-agent debate is expensive and rarely converges; consent is a cheaper, logged alternative |
| 2 | Formation-per-phase topology that changes on transition | Football | Agent teams have one static shape for generating *and* verifying |
| 3 | Audibles / FRAGO — bounded local re-plan | Am. football / military | Every deviation today is a full orchestrator round-trip |
| 4 | Negative selection + fever | Immune | Injection detectors are hand-written; no system-wide caution mode |
| 5 | Endocrine slow broadcast with half-lives | Endocrine | Global state today is either a message (fast, point-to-point) or a flag (never decays) |
| 6 | Admiralty grading + ACH | Intel analysis | Tool outputs are trusted uniformly; reasoning confirms rather than disconfirms |
| 7 | Coasean spawn-vs-call rule | Economics | Nobody has a principled rule for when to spawn a sub-agent |
| 8 | Drum-buffer-rope | Theory of Constraints | Pipelines release work at the pace of the fastest stage |
| 9 | Cache coherence / vector clocks on beliefs | CPU / distributed | Stale beliefs across agents aren't invalidated |
| 10 | Pheromone evaporation on shared memory | Swarm | Shared notes never expire |
| 11 | Drafting / domestiques / paceline | Cycling | Cost is paid by every agent equally |
| 12 | PF/PM split + sterile cockpit + go-around | Aviation | Verifier and actor roles blur; aborts are ad hoc and blameful |
| 13 | Shot clock / zugzwang / tilt | Basketball / chess / poker | No formal forced-decision, no "all moves are bad" detector, no post-failure cooldown |
| 14 | Morphogen gradients + response thresholds | Dev bio / swarm | Role assignment is always centralized |
| 15 | Error budget as the autonomy dial | SRE | Autonomy level is a config constant, not a function of recent reliability |
| 16 | Plan IR with optimization passes | Compilers | Plans aren't optimized before execution |
| 17 | Two-levels-up intent | Military | Sub-agents can't recover when the parent's orders stop making sense |
| 18 | Bonding / insurance on risky actions | Finance | Risky actions have no skin in the game |

---

## 7. Hybrid Candidates

The interesting part. Each hybrid takes parts from different domains that turn out to be solving the *same* agentic problem, and fuses them.

### H1. Formation = Gain Schedule
**Football formations × Control theory gain scheduling × TPS heijunka.**
A formation is just a gain schedule with names. Each phase (generate / verify / transition) has a different controller configuration: how many agents, what ratio of executors to verifiers, how aggressive the pressing (verification) trigger. Transition detection switches the schedule. Heijunka levels the load across phases so no phase is bursty.
*Why it's a breakthrough candidate:* today's orchestrators have one static topology. This gives them tactical shape-shifting with a principled control-theory backbone.

### H2. Objection Antibodies
**Sociocratic consent × Immune negative selection × Adaptive antibody library.**
Consent round = the innate check (fast, generic: "any paramount objection?"). The objection library = adaptive immunity: every objection ever raised is stored as a detector; negative selection deletes detectors that would block known-good plans. New plans are screened against the library *before* the consent round, so most objections are caught cheaply.
*Problem solved:* plan review that gets cheaper and smarter over time instead of re-debating from scratch.

### H3. Cortisol
**Endocrine broadcast × SRE error budget burn rate × Immune fever.**
One scalar ("cortisol") computed from error-budget burn rate and injection detections, broadcast fleet-wide with a half-life. Agents with the receptor lower their autonomy (more checkpoints, smaller actions); agents without it carry on. A spike triggers fever mode: fleet-wide throughput drops, strictness rises, decays automatically.
*Problem solved:* global caution without global messaging, and it clears itself.

### H4. Peloton Speculation
**Cycling drafting/domestiques × CPU speculative execution × KV-cache sharing.**
The leader's speculative branch is the draft; domestiques run the misprediction branches (the alternatives the leader didn't take) on cheap models. If the leader's speculation fails, a domestique's branch is already warm. Paceline rotation moves the expensive model on and off the front.
*Problem solved:* speculative execution today wastes the misses; here the misses are the domestiques' job.

### H5. Audibles Bounded by Sagas
**American-football audible × Military FRAGO × DB saga compensation.**
An executor may call an audible (swap the play locally, no orchestrator round-trip) *only if* the compensating action for the current step exists. Local re-planning freedom is bounded by rollback-ability. A FRAGO is the orchestrator's version: a delta-order that modifies the running plan without restart.
*Problem solved:* the "how much autonomy to give the sub-agent" question gets a mechanical answer: exactly as much as you can undo.

### H6. Graded Kalman Beliefs
**Admiralty source grading × Kalman filter × Active-inference precision.**
Each tool/source gets a reliability grade (A–F) and each observation a credibility grade (1–6); together they set the measurement-noise covariance in a Kalman-style belief update. High-grade observations move beliefs a lot; low-grade barely at all. ACH runs on top: hypotheses that survive disconfirmation gain precision.
*Problem solved:* uniform trust in tool outputs, which is the root of a lot of injection and hallucination propagation.

### H7. The Variance Drum
**Theory of Constraints DBR × Queueing (Kingman) × TPS WIP limits.**
Pick the drum by *latency variance*, not mean — Kingman says variance drives waiting. Buffer in front of it, rope release to its pace, and put WIP limits on every stage upstream. Then work on reducing that agent's variance (caching, smaller inputs) before anything else.
*Problem solved:* pipeline tuning that targets the actual cause of waiting.

### H8. Headless Allocation
**Morphogen gradients × Response thresholds × Pheromone evaporation × Stigmergy.**
No orchestrator. Scalar fields over the task graph (distance-to-deadline, distance-to-irreversible-action, distance-to-user) define roles by position. Each agent has per-task-type thresholds and picks up work when the stimulus exceeds them. Shared notes evaporate unless re-touched.
*Problem solved:* the orchestrator as single point of failure and context bottleneck. SwarmWorld shows differentiation *can* emerge; this designs it.

### H9. The Coxswain
**Rowing coxswain × Basketball shot clock × Aviation sterile cockpit × Chess zugzwang.**
A rhythm agent that never touches the work: enforces decision deadlines (shot clock), suppresses non-essential inter-agent chatter during critical phases (sterile cockpit), calls a timeout when momentum turns, and declares zugzwang ("all moves are bad — stop and ask the human") when every option scores negative.
*Problem solved:* tempo and attention are currently nobody's job.

### H10. Bonded Auctions with a Coase Gate
**Coase transaction costs × Agora auctions × Financial bonding.**
First a Coase gate: is the transaction cost of spawning a sub-agent lower than calling a tool? Only then run the auction. The winning bidder posts a compute bond, forfeited if its output fails verification. Bonds fund the verifiers.
*Problem solved:* unbounded spawning and no skin in the game.

### H11. Belief Coherence Protocol
**CPU cache coherence (MESI) × Vector clocks × Gossip.**
Each belief in an agent's context has a state (Modified / Shared / Invalid) and a vector clock. When an agent modifies a shared belief, it gossips an invalidate; peers holding it in Shared mark it Invalid and re-fetch on next use. No broadcast of the fact itself, only of the invalidation.
*Problem solved:* stale beliefs across a fleet, with bounded messaging.

### H12. Grandparent Intent with Rep Links
**Military "two levels up" × Holacracy double linking × Constitutional ombudsman.**
Every sub-agent carries its parent's *and* grandparent's intent. A rep link from each child circle reports tensions upward; a lead link carries intent downward. An ombudsman agent at the top represents the human's interest against the orchestrator.
*Problem solved:* delegation chains that lose the *why*, and no upward channel for "this order no longer makes sense."

---

## 8. What I'd do next

1. **Anchor to CELL // OS.** Share your mapping and I'll cross-reference: which cell parts and OS parts you already covered, which of the open parts above slot into gaps in your map, and which hybrids extend it.
2. **Pick three hybrids to spec.** My picks for highest leverage and lowest build cost: **H1 (Formation = Gain Schedule)**, **H5 (Audibles Bounded by Sagas)**, **H9 (The Coxswain)**. Each can be prototyped in an existing harness in a day.
3. **Falsify before building.** For each pick, one targeted search for the exact mechanism (not the analogy) to confirm it's really open — the ○ marks are quick-search grade.
4. **Deep pass on the untouched domains.** Sociocracy, intelligence analysis, endocrine, developmental biology, cycling, and esports produced the most ○ marks. A second, deeper decomposition of just those six would likely surface another 20+ open parts.

---

### Sources consulted for status checks (Sept 2026)
- AgentAntibody (arXiv 2608.04053); BioDefense; AEGIS — immune
- Control-theoretic agent papers (arXiv 2607.25408, 2603.10779, 2606.30877) — control
- Agora (arXiv 2607.09600); ACM EC 2026 LLM-incentives workshop — auctions
- AgentPitch; GRF diverse-style policies (arXiv 2511.19885) — sports as environment only
- "The Factory Must Grow, Part III" (Hayashi, May 2026) — TPS
- LangGraph v1.2 sagas; Cordum; "Agent Rollback and Checkpoint Patterns" — sagas
- ZenBrain (arXiv 2604.23878); D-MEM (arXiv 2603.14597); MAP (Nature Comms 2025) — neuro
- SwarmWorld (arXiv 2608.26081); CodeCRDT (arXiv 2510.18893) — stigmergy, CRDTs
- "The Agent Tending Problem" (Mar 2026) — Little's law
- War on the Rocks / rebuttal (Sept 2026); SentinelAgent (arXiv 2604.02767) — mission command
- PASTE (2603.18897); SPORK (2607.03333); toolspec; Auton (2602.23720) — speculative execution
- Agent SRE (Microsoft AGT); AgentChaos (2608.06790); balagan-agent — SRE / chaos
