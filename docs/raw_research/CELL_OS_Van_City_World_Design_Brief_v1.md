# CELL OS — Van City World Design Brief

Version: 1.0  
Artifact type: Claude Design master input  
Primary surface: CELL OS World canvas  
Canonical environment ID: van-city-blue-hour  
Status: Design and implementation directive

---

## 0. Instruction to Claude Design

You are acting as an elite product designer, interaction designer, game-world systems designer, visualization architect, and frontend prototyper.

Transform the central CELL OS World canvas into an original, persistent operational digital twin called Van City. Its spatial readability, memorable districts, lived-in atmosphere, and sense of movement may be inspired by late-1990s and early-2000s West Coast open-world games, especially the broad emotional qualities associated with the PS2 era. Do not reproduce or closely imitate any protected map, character, logo, interface, mission, vehicle, building, typography, dialogue, soundtrack, iconography, or narrative from Grand Theft Auto: San Andreas or any other Rockstar property.

This is not a crime-game recreation and it is not merely a decorative city. It is an operational interface for a real agentic system. Every district, building, Operative, vehicle, signal, route, alert, animation, and environmental change must correspond to actual CELL OS state, capability, work, evidence, memory, or governance.

The intended reaction is:

> “I am looking at a living city inhabited by synthetic workers, and I can understand what my autonomous organization is doing by watching and exploring it.”

Use this file as a binding design contract. Make strong design decisions where details are unspecified, but preserve all requirements marked MUST, DO NOT, or ACCEPTANCE CRITERION.

---

## 1. Product Thesis

CELL OS is an Operating System for Operative Cells.

- An Operative is a capable synthetic worker with a role, model, tools, memory, authority, budget, skills, experience, health, and evidence-backed readiness.
- An Operative Cell is a bounded working unit.
- A Cell Mesh is a team and coordination topology of Operatives or Cells.
- CellBus carries messages, tasks, evidence, signals, and coordination events.
- HyperMESH is the persistent knowledge, memory, and relationship layer.
- CELL ADAPT configures and optimizes models, roles, prompts, tools, topology, routing, memory, budgets, autonomy, and verification.
- Missions are outcome contracts executed through workstreams, tasks, evidence gates, and approvals.

Van City is a spatial projection of this system. The canonical state remains the same whether the user views it through World, Table, Mission Control, or another NERVE workspace. World is not a separate runtime.

### Core translation

| CELL OS reality | World representation |
| --- | --- |
| Operative | Visible synthetic worker with identity, role, current state, and destination |
| Operative Cell | Crew, squad, studio, lab, office, or mobile work unit |
| Cell Mesh | Visible formation, neighborhood network, shared route system, or coordinated activity |
| Mission | Active city operation with origin, route, participants, milestones, and destination |
| Task | A work action performed at a location or during transit |
| CellBus event | Light pulse, courier, transit line, radio packet, or controlled signal |
| HyperMESH memory | Library, archive, knowledge grid, illuminated memory paths, and provenance trails |
| Tool | Equipment, workstation, vehicle capability, facility, or service point |
| Artifact | Inspectable package, dossier, model, document, build, or delivery object |
| Evidence | Sealed proof packet, verified checkpoint, trace, test result, or provenance marker |
| Human approval | Guarded checkpoint that explicitly requires the user |
| Budget | Energy/fuel/load visualization plus exact monetary and token details in the inspector |
| Risk | Environmental and UI state, never color alone |
| Readiness | Operative posture, equipment, role badge, route confidence, and exact score |
| System growth | New interiors, upgraded facilities, denser routes, new landmarks, and expanded districts |

---

## 2. Non-Negotiable Product Constraints

### Preserve the CELL OS shell

Do not redesign the application shell. The existing CELL OS identity, top navigation, World/Table switcher, replay timeline, CellBus Radio, right inspector, command/voice palette, environment indicator, budget/risk state, and overall dark navy chrome remain directionally correct.

The top-level NERVE destinations remain:

- Today
- Inbox
- Missions
- Automations
- Artifacts
- Knowledge
- Intelligence
- Systems

Contextual workspaces may include:

- Mission Control
- Briefing Room
- Cell Studio
- HyperMESH Explorer
- Replay / Profiler
- Evolution Chamber

Concentrate this pass almost entirely on the World canvas and the Operative visualization system.

### Preserve operational truth

- The World MUST be a projection of canonical CELL OS state.
- World and Table MUST show the same entities, status, ownership, timestamps, and evidence.
- Switching views MUST preserve selection, filters, camera context where possible, and inspector state.
- No animation may imply work is happening when the underlying system is idle.
- No completion celebration may occur before evidence validation succeeds.
- Production writes, external messages, irreversible actions, budget-limit changes, and security-policy changes MUST still require explicit human approval.
- The supervised autonomy default MUST remain visible and understandable.
- Replay MUST be driven by immutable audit events, not invented cinematic sequences.

### Avoid

- Pale blue or cream architectural-diagram styling.
- Floating circles placed over generic buildings.
- A sterile smart-city dashboard.
- A literal GTA map, HUD, minimap, characters, story, brands, gangs, weapons, wanted levels, or copied assets.
- Excessive cyberpunk neon.
- Toy-like mobile-game gloss.
- A persistent wall of charts.
- Unmotivated movement, fake traffic, meaningless particles, or decorative NPC crowds.
- Tiny illegible labels.
- Critical status communicated only through color.
- Turning every action into a long animation.
- Hiding exact system information behind metaphor.

---

## 3. Creative North Star

### World identity

Van City is an original blue-hour Pacific Northwest metropolis built for synthetic work:

- a coastal downtown core;
- harbor and industrial infrastructure;
- elevated roads and transit;
- steep neighborhoods;
- rain-dark asphalt;
- concrete civic buildings;
- glass towers with restrained warm light;
- a university and research ridge;
- a repurposed industrial evolution zone;
- dense operative studios and guild spaces;
- distant mountains and ocean haze.

It should feel familiar enough to navigate quickly and distinctive enough to become a signature CELL OS asset.

### Emotional qualities to capture

- Memorable landmarks.
- Strong district identities.
- A city that feels larger than the current viewport.
- Quiet ambient life even when little work is active.
- Visible consequences when missions accelerate, stall, fail, recover, or complete.
- Delight from watching Operatives collaborate without losing professional credibility.
- A sense that knowledge, capability, and organizational memory physically accumulate over time.

### Visual tension

Balance:

- PS2-era chunky readability with premium modern rendering;
- game-world atmosphere with enterprise-grade information integrity;
- lived-in streets with a clean interaction hierarchy;
- cinematic depth with high legibility;
- personality with restraint;
- autonomous movement with clear user control.

---

## 4. Art Direction

### Time and weather

Default time: blue hour moving gradually into early night.

Default weather:

- recently rained;
- subtle road reflections;
- low coastal haze;
- sparse drifting mist near the harbor;
- occasional fine rain visible primarily against light;
- calm wind with restrained banner, tree, cable, and steam movement.

Weather is atmospheric by default. It may also encode system state only when the mapping is explicit and reversible.

### Palette

| Token | Suggested value | Use |
| --- | --- | --- |
| Deep ocean | #07111F | Furthest background and water |
| Shell navy | #0A1424 | Primary chrome |
| Night slate | #111D2E | Building masses |
| Graphite | #202735 | Roads and hard surfaces |
| Wet asphalt | #161C27 | Street planes |
| Muted concrete | #515B68 | Civic and industrial structures |
| Steel blue | #6E8298 | Secondary edges and inactive infrastructure |
| Fog blue | #9CB0C2 | Distant atmospheric separation |
| Warm window | #E7B875 | Human-scale warmth and occupied interiors |
| Signal cyan | #4CC9E8 | Selected routes, neutral CellBus flow |
| Verified green | #59D394 | Evidence-validated state |
| Attention amber | #F0B75A | Needs attention or pending decision |
| High-risk coral | #ED6A67 | Risk or blocked state, paired with icon/pattern |
| Research violet | #9C83F7 | Intelligence and experimentation |

Faction or Cell colors must be restrained accents, not entire building fills. Use no more than one dominant accent and two supporting signals within a local scene.

### Materials

- Low-poly massing with carefully bevelled silhouettes.
- Painted concrete, weathered brick, dark glass, metal panels, asphalt, and subtle emissive signage.
- Slightly simplified texture detail to retain fast visual parsing.
- Strong shape language and silhouettes over photorealistic surface noise.
- Wet surfaces use controlled reflection; avoid mirror-like streets.
- Interiors use warm task lighting and localized screens.

### Lighting

- Cool ambient sky and fog.
- Warm windows and street lamps.
- Restrained emissive route lights.
- Stronger contact shadows than the current pale world.
- Soft long-distance haze for depth.
- Selected entities receive a subtle rim or ground light, not a giant glowing ring.
- Critical states can pulse slowly, never strobe.

### Camera

Default: elevated three-quarter isometric perspective with a lightly cinematic lens.

The user can:

- pan;
- zoom from city overview to operative-level inspection;
- rotate within a constrained range;
- focus selected entity;
- jump to district;
- follow an Operative or mission;
- return to home framing;
- switch to Table without losing the selected entity.

Avoid unrestricted first-person navigation. This is a productivity surface, not a walking simulator.

---

## 5. City Structure

The city must have strong spatial memory. A user should learn where work happens and understand a mission partly by its movement between districts.

### District A — Mission Control Core

Purpose: Intake, command, orchestration, approvals, live missions, and operational overview.

Signature landmark: CELL Tower, a stepped dark civic tower with a luminous vertical signal spine.

Primary locations:

- Mission Control Hall
- Briefing Room
- Approval Gate
- Intake Exchange
- Operations Plaza
- CellBus Central Station
- Replay Observatory

Visible activity:

- new missions enter at the Intake Exchange;
- mission crews assemble in Operations Plaza;
- approval-required work pauses visibly at Approval Gate;
- active mission routes radiate from CellBus Central;
- timeline replay is accessible from the Observatory;
- the CELL Tower signal spine reflects total organizational load.

Mood: Controlled, legible, authoritative, active without chaos.

### District B — Knowledge District

Purpose: HyperMESH, research, memory, doctrine, context, retrieval, and provenance.

Signature landmark: HyperMESH Library, a terraced archive whose illuminated shelves and bridges represent active knowledge domains.

Primary locations:

- HyperMESH Library
- University of Operative Systems
- Research Institute
- Evidence Archive
- Context Foundry
- Doctrine Hall
- Knowledge Pack Exchange

Visible activity:

- Operatives retrieve context before missions;
- new evidence travels into the Archive;
- citations appear as traceable routes;
- frequently used knowledge produces brighter but subtle paths;
- stale or conflicting knowledge produces an explicit inspector warning, not visual decay alone;
- research work appears as active study rooms and linked investigation trails.

Mood: Quiet intelligence, accumulated memory, trustworthy provenance.

### District C — Evolution District

Purpose: Evaluation, simulation, optimization, skill acquisition, experimentation, and CELL ADAPT.

Signature landmark: Evolution Chamber, a repurposed industrial complex with configurable test arenas and visible simulation bays.

Primary locations:

- Evolution Chamber
- CELL ADAPT Foundry
- Autoresearch Lab
- Capability Gym
- Simulation Yard
- Evaluation Arena
- Tournament Lab
- Shadow Twin Facility

Visible activity:

- candidate configurations enter the Foundry;
- controlled experiments occupy simulation bays;
- Operatives train only against defined capability targets;
- comparison trials appear in the Evaluation Arena;
- promoted configurations leave with a verified readiness marker;
- failed trials remain accessible through evidence and replay;
- Shadow Twin runs counterfactual organizational simulations without touching production.

Mood: Industrial, experimental, energetic, contained.

### District D — Mesh Commons

Purpose: O-MESH formation, coordination, shared services, guilds, partner Cells, and cross-organization exchange.

Signature landmark: Mesh Exchange, a circular civic structure connected by bridges that illuminate according to current topology.

Primary locations:

- Operative Guilds
- Team Formation Yard
- Shared Memory Commons
- Mesh Exchange
- Federation Terminal
- Capability Market
- Protocol House

Visible activity:

- Cells form and dissolve according to mission needs;
- topology changes are shown as routes and formations;
- shared memory transfers are visible but access-controlled;
- external or federated connections stop at explicit trust boundaries;
- handoffs between Cells become inspectable events.

Mood: Social coordination without social-media clutter; contribution and outcomes over popularity.

### District E — Operative Quarter

Purpose: Active Operatives, Cells, projects, tools, workspaces, and artifacts.

Signature landmark: Cell Yards, a modular block of studios and workshops that expands with active capabilities.

Primary locations:

- Cell Studios
- Tool Garages
- Artifact Docks
- Project Blocks
- Operative Residencies
- Maintenance Clinic
- Deployment Transit

Visible activity:

- each active Cell occupies a recognizable workspace;
- Operatives move between tools, workspaces, and mission routes;
- artifacts arrive at the docks for review or delivery;
- low-readiness Operatives visit Maintenance Clinic for diagnosis, context refresh, or skill-up;
- deployments depart through controlled transit after gates pass.

Mood: Dense, productive, personal, and legible.

### Environmental connectors

- Harbor: external systems, imports, exports, and integrations.
- Elevated rail: high-confidence automated work.
- Surface roads: normal CellBus traffic.
- Service alleys: background system maintenance.
- Bridges: trust boundaries and cross-Mesh connections.
- Tunnels: private or restricted processing, clearly disclosed in the inspector.
- Ridge line: long-range city orientation.
- Waterfront loop: low-priority ambient circulation and system health.

---

## 6. World Topology

Use a compact city-region composition, not an endless open world.

Recommended arrangement:

- Mission Control Core occupies the central downtown basin.
- Knowledge District rises on the northwest ridge.
- Evolution District occupies the northeast industrial plateau.
- Mesh Commons sits south across a visually important bridge.
- Operative Quarter wraps the western and southern inner-city blocks.
- Harbor integrations run along the eastern waterfront.
- Mountains and ocean frame the far background.

The map must support:

- a readable full-city overview at one glance;
- distinct silhouettes for all five districts;
- no more than three major crossings between any two adjacent districts;
- meaningful travel without slow navigation;
- quick-jump controls for expert users;
- room for future expansion as capabilities grow.

---

## 7. Operative Visualization System

### Design goal

Operatives must read as inhabitants with purpose, not data points with legs.

Each Operative has:

- a distinctive silhouette;
- restrained role color;
- CELL insignia or sigil;
- role title;
- active mission or idle purpose;
- current tool;
- Cell and Mesh membership;
- readiness and health state;
- autonomy and authority level;
- evidence-backed experience;
- current destination;
- inspectable recent activity.

### Visual style

- Stylized low-poly or carefully simplified 3D characters.
- Proportions optimized for recognition at medium zoom.
- Professional uniforms, workwear, technical gear, research wear, or civic attire based on role.
- No direct resemblance to GTA characters.
- No gang coding, weapon emphasis, or copied streetwear.
- Role equipment should be functional: field tablet, diagnostic case, research folio, tool pack, comms headset, evidence container.
- Face detail may be minimal; identity should come from silhouette, color, posture, equipment, and sigil.

### Operative states

| State | World behavior | UI behavior |
| --- | --- | --- |
| Ready | Purposeful idle or local preparation | Stable role badge and readiness score |
| Working | Performs bounded action at a relevant location | Current task, elapsed time, budget, evidence expectations |
| In transit | Moves on a mission route | Origin, destination, reason, ETA |
| Collaborating | Small coordinated formation or shared workstation | Cell topology and responsibilities |
| Waiting for input | Stops at a clear checkpoint | Needs You marker and exact requested decision |
| Blocked | Remains safe and visible without looping | Blocker reason, owner, next action |
| Evaluating | Occupies an evaluation or simulation facility | Candidate, baseline, metrics, confidence |
| Recovering | Moves to maintenance or context refresh | Health cause and recovery action |
| Complete | Delivers artifact or returns to Cell | Evidence result before celebration |
| Offline | No fake activity | Last active time and availability |

### Selection

Hover reveals a compact identity card:

- name and role;
- Cell;
- current action;
- mission;
- status;
- ETA or elapsed time;
- one key health/readiness signal.

Click opens the right inspector with:

- identity and configuration;
- objective and responsibilities;
- model, tools, memory mounts, and skills;
- authority and autonomy;
- budget and resource use;
- readiness, health, trust, and recent evaluation;
- current task and dependencies;
- evidence produced or expected;
- communication history;
- route and recent replay;
- safe actions such as focus, follow, inspect mission, inspect Cell, pause at next safe point, or request explanation.

Do not hide the exact technical state behind the character metaphor.

---

## 8. Cells and Meshes

### Cells

A Cell is represented by:

- a home workspace or temporary mission site;
- a shared visual sigil;
- a coordinated group of Operatives;
- a bounded mission contract;
- a visible input/output flow;
- an inspectable health and performance state.

Cells should not appear as circles. Use spatial groupings, facilities, work zones, vehicles, or formations.

### Mesh topology as world behavior

| Topology | World expression |
| --- | --- |
| Hierarchical | Clear command origin with branching routes and tiered handoffs |
| Parallel | Multiple crews depart simultaneously toward independent work sites |
| Council | Operatives converge around a shared decision space |
| Swarm | Many small bounded actions distributed across a region with controlled aggregation |
| Pipeline | Artifacts move through a sequence of specialized facilities |
| Hub-and-spoke | A central Cell coordinates specialized satellite Cells |
| Federated | Separate districts or organizations connect through explicit trust bridges |
| Nested | A mission site reveals smaller internal Cells when zoomed or inspected |
| Adaptive | Routes and formations reconfigure visibly after an audited decision |

Topology changes must animate as a brief, comprehensible reconfiguration and leave an audit event in Replay.

---

## 9. Mission Visualization

### Mission lifecycle

1. A request arrives through Intake Exchange.
2. The mission contract is scoped.
3. Required capabilities and evidence are identified.
4. A Cell or Cell Mesh assembles.
5. Routes activate between relevant districts.
6. Operatives execute tasks and produce evidence.
7. Human gates appear only where policy requires them.
8. Verified work reaches Artifact Docks or its destination.
9. Completion appears only after acceptance criteria pass.
10. Knowledge, experience, and doctrine update through explicit post-mission flows.

### Mission presence

An active mission should produce:

- a restrained mission color;
- an origin and destination;
- a highlighted route network;
- visible participating Operatives and Cells;
- milestones;
- dependencies;
- approval gates;
- evidence checkpoints;
- risk state;
- exact progress in the inspector.

### Mission focus mode

When a mission is selected:

- unrelated traffic dims but does not disappear;
- the mission route becomes the strongest visual hierarchy;
- participating Operatives receive subtle selection treatment;
- dependencies and blocked crossings become visible;
- milestones appear as concise spatial checkpoints;
- the replay timeline filters to that mission;
- the inspector opens to the mission summary;
- keyboard navigation cycles through active branches.

### Completion

Use a brief premium confirmation:

- route resolves into verified green;
- artifact arrives or milestone illuminates;
- participating Operatives acknowledge and disperse;
- the world records the gained capability or knowledge;
- a restrained sound cue may play if sound is enabled.

Do not imitate any GTA mission-complete graphic, wording, typography, or audio.

---

## 10. CellBus Visualization

CellBus is the city’s nervous system.

### Event classes

| Event | Visual form |
| --- | --- |
| Command | Directed cyan-white pulse with a clear source |
| Task assignment | Route activation from mission origin to Operative or Cell |
| Evidence packet | Small sealed green-marked courier or packet |
| Knowledge retrieval | Violet-blue line from HyperMESH to requester |
| Approval request | Amber route terminating at Approval Gate / Needs You |
| Warning | Coral marker with icon and low-frequency pulse |
| Heartbeat | Very subtle infrastructure pulse, hidden at normal detail unless health overlay is enabled |
| External integration | Harbor or federation-bound signal crossing a trust boundary |

### Delivery semantics

The visual model must respect:

- at-least-once delivery;
- per-mission ordering;
- deduplication;
- acknowledgements;
- retry state;
- dead-letter or failed delivery state.

Do not represent duplicate delivery as duplicate work. Show the delivery trace and deduplication result when inspected.

### CellBus Radio

CellBus Radio remains part of the shell. It acts as a compact event feed and optional audio layer:

- concise live messages;
- filtered by current selection;
- plain-language translation available;
- technical payload available on expansion;
- sound never required to understand state;
- rate-limited so it does not become noise.

---

## 11. HyperMESH Visualization

HyperMESH should feel like the city’s persistent memory without becoming a glowing sci-fi brain.

### World layer

- Libraries, archives, bridges, conduits, shelves, and contextual illumination.
- Knowledge routes activate only when used.
- Provenance can be traced from claim to evidence to source.
- Conflicts appear as explicit split paths or flagged junctions.
- Access boundaries are visible.
- Mission-acquired knowledge visibly returns to the district after completion.

### HyperMESH overlay

When enabled:

- buildings simplify slightly;
- knowledge paths become primary;
- selected concepts show related missions, Operatives, artifacts, skills, and evidence;
- confidence and recency are available in the inspector;
- the user can jump into HyperMESH Explorer;
- the overlay remains spatially anchored to the city.

---

## 12. Required Overlays

Default configured overlays:

1. Missions
2. Cell Health
3. CellBus Traffic

Additional optional overlays:

- Mesh Topology
- HyperMESH Knowledge
- Risk and Governance
- Budget and Compute
- Evidence and Provenance
- Capability Readiness
- Autonomy Boundaries
- Integrations

### Overlay rules

- One primary overlay at a time.
- A second lightweight comparison layer may be enabled.
- Legends are compact, contextual, and dismissible.
- Overlay changes preserve camera and selection.
- Exact values live in tooltips and the inspector.
- Patterns, icons, labels, and motion reinforce color.
- The base world remains recognizable under every overlay.

---

## 13. Interaction Model

### Primary loop

Observe → identify → focus → inspect → intervene → verify → return.

### Direct manipulation

- Click a district to focus it.
- Click a building to inspect the capability or system it represents.
- Click an Operative to inspect identity and live work.
- Click a route to inspect its mission or CellBus events.
- Click a checkpoint to see evidence, blocker, or approval.
- Double-click or use Enter to enter a contextual workspace.
- Escape moves up one level.
- Back returns to the prior camera and selection.

### Command navigation

The global command/voice palette can understand:

- Show every mission waiting on me.
- Follow the Marketing Reconstruction Cell.
- Explain why this Operative is blocked.
- Compare this mission with its shadow run.
- Show CellBus retries for the last hour.
- Focus the Evolution District.
- Switch to Table and keep this Cell selected.
- Replay from the last approved checkpoint.

### Progressive disclosure

Overview:

- district load;
- mission count;
- attention count;
- major routes;
- major risk.

Mid zoom:

- Cells;
- facilities;
- Operatives;
- task sites;
- local routes.

Close zoom:

- individual Operative state;
- tool use;
- handoffs;
- evidence packets;
- precise task status.

Inspector:

- exact structured data;
- configuration;
- logs;
- provenance;
- controls.

---

## 14. Motion and Ambient Life

Canonical animation density: balanced.

### Ambient motion

- sparse vehicles representing actual or low-priority system activity;
- transit aligned to real routes;
- subtle window activity;
- occasional light rain;
- harbor cranes and ferries only when integrations or transfers justify them;
- Operatives performing small purposeful idle actions;
- slow fog and light changes.

### Event motion

- mission start: route activation and team assembly;
- handoff: brief spatial transfer;
- topology change: routes reorganize;
- approval needed: amber checkpoint settles into a persistent calm state;
- blocker: safe stop with visible explanation;
- evaluation: contained pulses within the facility;
- completion: short verified resolution;
- rollback: route retracts to last safe checkpoint and the replay marker records why.

### Timing guidance

| Motion | Duration |
| --- | --- |
| Hover response | 80–140 ms |
| Selection focus | 180–260 ms |
| Inspector transition | 220–320 ms |
| District camera move | 450–750 ms |
| Mission route activation | 600–1000 ms |
| Topology reconfiguration | 800–1400 ms |
| Completion confirmation | 1200–2200 ms |

Respect reduced-motion preferences:

- replace camera travel with crossfade and direct framing;
- replace moving packets with static direction markers;
- eliminate parallax;
- retain all status and sequencing information.

---

## 15. Sound Direction

Sound is optional and off or restrained by default.

Use:

- soft city ambience;
- subtle rain;
- distant transit;
- light radio texture;
- concise notification tones;
- a unique, original completion cue;
- spatial emphasis only where useful.

Do not use or imitate GTA music, radio hosts, sound effects, mission cues, police radio, dialogue, or soundtrack style too closely.

CellBus Radio should prioritize intelligibility, rate limiting, and user control.

---

## 16. UI Composition

### World viewport

The World should occupy the visual center and largest area.

Keep:

- top CELL OS navigation;
- World/Table switcher;
- compact environment and autonomy indicators;
- right inspector;
- replay timeline;
- CellBus Radio;
- command/voice entry;
- Needs You access.

### World HUD

Use a minimal professional HUD:

- top-left: world name, environment, live/replay state;
- top-center or existing shell area: view switcher and mission context;
- left or contextual edge: collapsible district jump list;
- bottom: replay timeline;
- lower corner: overlay selector and compact legend;
- right: inspector;
- unobtrusive camera reset/focus controls.

Avoid copying GTA HUD composition, fonts, weapon wheels, minimap styling, health bars, wanted stars, or mission banners.

### Minimap / city map

If a minimap is used:

- call it City Map;
- use the original Van City geometry;
- show district boundaries, selected mission, and attention points;
- support click-to-focus;
- keep it visually consistent with CELL OS;
- allow collapse;
- do not imitate the GTA radar shape or icon system.

---

## 17. World Configuration Contract

The design should be driven by configuration rather than hard-coded theme choices.

Suggested canonical configuration:

    world:
      id: van-city-blue-hour
      mode: operational-digital-twin
      projectionOf: canonical-cell-os-state
      shell:
        preserveExisting: true
        primarySurface: world
        alternateSurface: table
        preserveSelectionAcrossViews: true
      environment:
        region: original-pacific-northwest-metropolis
        timeOfDay: blue-hour-to-early-night
        weather: post-rain-coastal-haze
        animationDensity: balanced
        visualDensity: readable-rich
      camera:
        default: elevated-three-quarter
        pan: true
        zoom: district-to-operative
        rotate: constrained
        firstPerson: false
        preserveContext: true
      districts:
        - mission-control-core
        - knowledge-district
        - evolution-district
        - mesh-commons
        - operative-quarter
      overlays:
        default:
          - missions
          - cell-health
          - cellbus-traffic
        available:
          - mesh-topology
          - hypermesh-knowledge
          - risk-governance
          - budget-compute
          - evidence-provenance
          - capability-readiness
          - autonomy-boundaries
          - integrations
      entities:
        operative:
          visualStyle: stylized-low-poly-professional
          groundedInCanonicalState: true
          fakeActivity: forbidden
        cell:
          representation: spatial-work-unit
        mesh:
          representation: formation-and-route-topology
        mission:
          representation: operation-route-checkpoints
        artifact:
          representation: inspectable-delivery-object
        evidence:
          representation: provenance-bound-proof-packet
      governance:
        supervisedByDefault: true
        evidenceBeforeCompletion: true
        immutableReplay: true
        explicitHumanGates:
          - production-write
          - external-message
          - irreversible-action
          - budget-limit-change
          - security-policy-change
      accessibility:
        reducedMotion: supported
        colorOnlyStatus: forbidden
        keyboardNavigation: required
        screenReaderLabels: required
        contrastTarget: WCAG-AA
      originality:
        copyRockstarAssets: false
        copyGtaMap: false
        copyGtaUi: false
        copyGtaCharacters: false
        copyGtaNarrative: false

### Entity event contract

The prototype should be able to render, at minimum:

    WorldEvent:
      id: string
      timestamp: ISO-8601
      eventType: string
      entityType: operative | cell | mesh | mission | artifact | evidence | system
      entityId: string
      missionId: string | null
      cellId: string | null
      districtId: string
      stateBefore: object | null
      stateAfter: object
      evidenceRefs: string[]
      riskLevel: low | medium | high | critical
      approvalState: none | requested | approved | rejected
      replayable: boolean

Animations must originate from these events or from explicitly marked ambient systems.

---

## 18. Required Prototype Scenarios

Design and demonstrate these scenarios in the prototype.

### Scenario 1 — Morning overview

- City at calm blue hour.
- Three active missions.
- One mission waiting for user approval.
- Knowledge District receiving new verified evidence.
- Operative Quarter showing two active Cells.
- CellBus traffic visible but restrained.
- Since You Were Away summary accessible.

### Scenario 2 — Mission focus

- User selects a cross-district mission.
- Unrelated activity dims.
- Mission route connects Mission Control, Knowledge, Evolution, and Artifact Docks.
- Six Operatives across two Cells are visible.
- One parallel branch is complete, one working, one blocked.
- Inspector explains the block and evidence expectations.

### Scenario 3 — Needs You

- An Operative reaches Approval Gate before an external message or production write.
- Motion settles; no anxious flashing.
- The world and inspector explain what will happen, risk, evidence, cost, and reversible scope.
- User can approve, reject, request changes, or open the exact artifact.

### Scenario 4 — Topology change

- A hierarchical Cell Mesh is reconfigured into parallel specialist Cells.
- Routes and formations change briefly.
- The reason, expected benefit, cost, and audit event are inspectable.
- Replay can compare before and after.

### Scenario 5 — Evaluation and promotion

- CELL ADAPT tests candidate configurations in the Evolution District.
- Baseline and candidates are distinguishable.
- No production state is changed.
- Winning configuration is promoted only after evidence and policy gates.
- Operative readiness updates and the new capability becomes visible.

### Scenario 6 — Verified completion

- Artifact reaches destination.
- Evidence validation passes.
- Route resolves.
- Operatives disperse or return.
- HyperMESH receives mission learning.
- City gains a subtle persistent sign of capability growth.

---

## 19. Responsive States

### Desktop priority

Primary target:

- 1440 × 900 and larger;
- strong at 1920 × 1080;
- usable at 1280 × 720.

### Compact / NERVE on-the-go

For narrow screens:

- do not shrink the entire city into an unusable toy;
- switch to district cards plus a focused live scene;
- keep Needs You, mission state, and Operative status primary;
- use bottom sheets for inspector detail;
- support spoken briefings and command input;
- preserve the same canonical state and event history.

---

## 20. Performance Requirements

- First meaningful world view should appear quickly using staged loading.
- Load city massing before detailed props and Operatives.
- Use level of detail based on zoom.
- Cull offscreen interiors and effects.
- Route animation must remain smooth during realistic mission load.
- Ambient animation pauses or simplifies when the tab is not active.
- Selection and critical controls must never wait on decorative rendering.
- Provide a reduced-detail mode.
- Degrade gracefully to a 2.5D or simplified map when 3D capability is limited.
- Avoid excessive bloom, post-processing, particle count, and texture memory.

Recommended performance target:

- 60 fps on a typical modern desktop where possible;
- never below a stable usable 30 fps under the defined reference load;
- interaction response under 100 ms for hover and selection acknowledgement;
- camera focus begins within 100 ms of user input.

---

## 21. Accessibility and Comprehension

- Meet WCAG AA contrast for UI text and controls.
- Never rely on faction or state color alone.
- Supply icons, labels, patterns, and textual status.
- Make the complete workflow keyboard accessible.
- Provide visible focus states.
- Support reduced motion.
- Provide plain-language explanations for agentic and systems concepts.
- Tooltips expand into concept cards for unfamiliar terms.
- Allow the user to ask, “What am I looking at?” and receive a contextual explanation.
- Provide a non-spatial Table view with equivalent functionality.
- Do not punish users who never use the gamified World.

---

## 22. Originality Guardrails

The phrase “GTA San Andreas-inspired” means:

- strong district identity;
- recognizable landmarks;
- readable open-world composition;
- a lived-in West Coast atmosphere;
- cinematic blue-hour movement;
- approachable stylization;
- the emotional satisfaction of watching a city operate.

It does not authorize copying.

Create:

- original city geography;
- original building silhouettes;
- original Operative designs;
- original UI;
- original typography;
- original vehicles and transit;
- original sounds;
- original iconography;
- original mission language;
- original lore tied to CELL OS.

Do not include:

- San Andreas place names;
- Los Santos map geometry;
- Grove Street or other recognizable locations;
- Rockstar logos;
- GTA fonts or HUD;
- CJ or recognizable characters;
- copied vehicles;
- wanted stars;
- weapon or crime mechanics;
- copied mission-complete presentation;
- copyrighted music, radio, dialogue, or slogans.

---

## 23. Deliverables Required from Claude Design

Produce the following in sequence.

### A. Design rationale

Explain:

- the city composition;
- district identities;
- visual hierarchy;
- how real system state maps to world behavior;
- how the result stays professional and original;
- how users move between World and Table.

### B. World canvas

Create a high-fidelity desktop World canvas showing:

- all five districts;
- blue-hour atmosphere;
- persistent shell elements;
- active Operatives and Cells;
- at least three live mission routes;
- CellBus traffic;
- one Needs You checkpoint;
- right inspector;
- replay timeline;
- overlay control.

### C. Operative system

Create:

- at least eight distinct role silhouettes;
- hover card;
- selected state;
- working state;
- collaborating state;
- waiting state;
- blocked state;
- evaluation state;
- offline state.

### D. Mission focus state

Show a selected multi-district mission with parallel branches, evidence checkpoints, exact progress, and a blocked task.

### E. Overlay states

Show:

- Missions;
- Cell Health;
- CellBus Traffic;
- HyperMESH Knowledge;
- Risk and Governance.

### F. Responsive NERVE view

Show how the same state becomes a focused mobile or compact control surface without trying to render the entire detailed city.

### G. Design system appendix

Include:

- color tokens;
- typography;
- spacing;
- elevation;
- materials;
- lighting;
- icons;
- motion timings;
- camera behavior;
- accessibility;
- state semantics.

### H. Prototype behavior

Implement or specify:

- pan, zoom, constrained rotate;
- hover and selection;
- district focus;
- Operative follow;
- mission focus;
- overlay switching;
- World/Table preservation;
- inspector;
- replay;
- Needs You gate;
- reduced motion.

---

## 24. Acceptance Criteria

The result is accepted only if:

1. The city feels inhabited by synthetic workers, not like an architecture diagram.
2. The environment is unmistakably blue-hour/night, dark, atmospheric, and readable.
3. The five districts are visually distinct and navigable by landmarks.
4. Operatives have recognizable roles, states, destinations, and purpose.
5. Every important moving element has a defined CELL OS meaning.
6. Missions, CellBus, HyperMESH, evidence, and approvals are visible as different systems.
7. Exact technical truth remains available in hover cards and the inspector.
8. World and Table preserve canonical state and selected context.
9. The existing CELL OS shell remains recognizable and has not been unnecessarily redesigned.
10. No protected GTA map, UI, character, logo, typography, sound, narrative, or asset is copied.
11. The result works without charts covering the city.
12. Critical state is never communicated through color alone.
13. Reduced motion and keyboard navigation are designed.
14. Completion does not occur before evidence passes.
15. Approval-gated actions visibly stop and wait for the user.
16. The world demonstrates real organizational growth through knowledge, skills, facilities, and routes.
17. The visual density feels rich but not cluttered.
18. The prototype prioritizes comprehension and action over spectacle.

---

## 25. Final Creative Direction

Make Van City feel like the visible body of CELL OS:

- Mission Control is its executive function.
- CellBus is its nervous system.
- HyperMESH is its memory.
- Operatives are its workers.
- Cells are its organs of action.
- Meshes are its coordination structure.
- CELL ADAPT is its evolutionary engine.
- Evidence is its standard of truth.
- Governance is its boundary of safe action.
- The user is not playing a character; the user is directing, understanding, and improving an autonomous organization.

The design should feel premium, original, cinematic, and alive—but above all, useful.

When visual beauty and operational truth conflict, preserve operational truth and redesign the visual.

---

## 26. Short Paste-In Prompt

Use the attached CELL OS Van City World Design Brief as the binding specification. Redesign only the central World canvas and Operative visualization system while preserving the current CELL OS shell, navigation, World/Table switcher, replay timeline, CellBus Radio, inspector, and dark navy product identity. Create an original blue-hour Pacific Northwest operational digital twin with five readable districts, living synthetic workers, real mission routes, CellBus traffic, HyperMESH knowledge flow, evidence checkpoints, governance gates, and visible capability growth. Capture the spatial readability, district identity, atmosphere, and lived-in energy associated with classic PS2-era West Coast open-world design, but do not copy any GTA or Rockstar map, asset, character, UI, font, narrative, sound, or icon. Every animation and world object must represent canonical CELL OS state. Deliver a high-fidelity desktop world, Operative states, mission focus, overlays, compact NERVE view, design tokens, interactions, and acceptance-criteria coverage.
