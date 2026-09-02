# 03 — Army Interaction Language

The Army vocabulary should be a semantic compression layer, not decoration.

| Army concept | Real system meaning |
|---|---|
| Campaign | strategic initiative / multi-mission program |
| Operation | mission |
| Objective | desired measurable state |
| Theatre | domain / business / technical operating area |
| Front Line | highest-priority active work |
| Task Force | dynamically assembled cross-specialty team |
| Squad | bounded working team |
| Formation | execution topology |
| Recon | uncertainty reduction / investigation |
| Intelligence | context, evidence, memory, knowledge |
| Signals | communication and handoffs |
| Logistics / Supply | context, tools, credentials, compute, budget |
| Readiness | ability to execute mission now |
| Threat | failure/risk class |
| Known Threat | recurring failure family |
| Rules of Engagement | autonomy and governance |
| Command Authorization | human/policy gate |
| Surveillance | observability |
| War Game | controlled simulation / experiment / evaluation |
| Doctrine | validated reusable workflow/team pattern |
| Candidate Doctrine | not-yet-certified workflow/team pattern |
| After-Action Report | structured learning from completed mission |
| Tactical Withdrawal | cancel / rollback |
| Hold Position | pause consequential action while preserving state |
| Redeploy | move team/agent with structured handoff |
| Reinforcement | additional agent or team capability |
| Distress Signal | intelligent help request |
| Hot Drop | rapidly add specialist with prepared context |
| Breach | investigate and remove blocker |
| Target Lock | set current focus/context |
| Satellite / Surveillance Mode | anomaly-only organizational view |

## Design requirement

Every metaphor must map to typed state.

Examples:

- “building on fire” → deployment or mission failure state.
- “broken supply line” → context, credential, environment, compute, or dependency unavailable.
- “fog” → unsupported/unknown/low-confidence information.
- “unit pinned” → agent/team blocked.
- “front line” → priority derived from objective/risk/dependency/value.
- “returning threat” → recurring failure family.

Never generate fake urgency or military drama with no operational meaning when the visual is used for actual work.
