# Structured idea portfolio

Complexity uses `S / M / L / XL`. Time saved is a hypothesis to validate, not a measured claim.

| Idea | Description | Improvement type | Complexity | User value | Business value | Potential optimization | Current process | Future process | Estimated time saved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Agents-as-Configuration | Version every meaningful agent behavior, tool, budget, skill, policy and memory choice | Architecture, DB, New functionality | L | Reuse reliable agents instead of rebuilding prompts | Sellable presets, faster onboarding, reproducible delivery | Layered presets, inheritance, lockfiles, schema-driven UI | Hand-authored prompt/session | Select or generate certified config | 20–60 min per launch |
| Prompt-to-Config Constructor | Convert plain intent into a proposed validated configuration with rationale | AI, UI/UX | L | Lets non-experts create agents | Broadens platform audience | Retrieval from proven presets; diff before approval | Manually edit YAML | Describe role; review generated diff | 15–45 min per config |
| Mission Matcher | Scores agents and formations against mission requirements and evidence | Performance, AI | XL | Faster, explainable staffing | Better success/cost ratio; future marketplace | Constraint filter then multi-objective ranking | Operator chooses by intuition | Ranked candidates with gaps and confidence | 10–30 min plus avoided reruns |
| Readiness Uplift Planner | Last-minute pre-deployment micro-evals, knowledge injection, tool checks and substitutions | Reliability, Performance | L | Catches weak readiness before costly work | Fewer failed missions and client delays | Pick highest expected uplift per minute/cost | Launch or manually inspect | Compare baseline and optimal readiness; apply approved actions | 15–90 min per avoided failure |
| Adaptive Communication Doctrine | Adjust scans, updates, alerts and handoffs to risk, novelty, coupling and struggle | Performance, New functionality | L | Less noise without missing critical facts | Lower token cost and coordination defects | Event-triggered policies; learn optimal intensity | Fixed/prompt-requested updates | Mission policy dynamically selects communication events | 10–25% coordination overhead hypothesis |
| Team Communication Effectiveness | Measures correct receipt, consumption, actionability, latency, noise and contradiction resolution | Metrics, Performance | M | Shows whether more communication actually helps | Enables doctrine optimization | Pair activity with accepted outcomes | Count messages or rely on impressions | Score evidence-linked communication effects | Avoids unproductive communication loops |
| MESH Knowledge Router | Mission-scoped discovery, packaging, delivery and promotion of permissioned knowledge | Knowledge, DB, Performance | XL | Agents receive relevant context without reading everything | Cross-repo learning and differentiated IP | Requirement graph, provenance, freshness, access and value ranking | Full wiki scan/manual copy | Typed knowledge packet delivered at decision points | 10–40 min/session plus fewer errors |
| Sentinel Observer | Long-running, read-only event consumer that identifies risk, drift, stale state and coordination gaps | Observability, Security | L | One place to catch struggling teams and blind monitors | Reliability offering and lower support cost | Rules first; agent synthesis only for novel patterns | Operator checks dashboards | Sentinel creates evidence-linked alerts/tickets | 30–120 min/day at scale |
| Agent Family / Lineage | Persistent specialization cluster with generations, bonded knowledge policies and growth evidence | UI/UX, Knowledge, R&D | L | Memorable way to understand agent evolution | Engagement, preset marketplace, explainability | Model lineage and bonds; avoid decorative simulation | Flat agent list | Family tree shows inheritance, certifications and complementary skills | Primarily comprehension value |
| Cognitive Bonds | Pre-authorized agent-to-agent context and rescue relationship | Communication, Reliability | M | Faster help with less handoff reconstruction | Better recovery time | Optimize partner complementarity and intervention threshold | Broadcast or manual handoff | Bonded helper receives typed minimum context on trigger | 5–20 min per intervention |
| Surplus Capacity Queue | Uses expiring provider capacity only for bounded positive-value tasks | Cost, Performance | M | Converts unused allowance into useful maintenance/research | Better subscription utilization | Expected value per token/minute; strict caps and stop conditions | Capacity expires unused | Queue selects safe, reversible work above value threshold | Variable; must measure net value |
| Capability Growth / Titles | Updates evidence-backed capability confidence, certifications and titles after evals | Knowledge, UI/UX | M | Shows what agents have actually learned | Trust, marketplace credibility | Time decay, minimum sample, unseen evals | Static role names | Evidence events trigger review, not automatic promotion | Faster staffing and fewer poor matches |
| Team Config Studio | UI for presets, diffs, inheritance, policies, validation and certification state | UI/UX | XL | Makes deep configuration understandable | Core commercial product surface | Schema-generated forms plus expert raw view | Edit files and prompts | Visual compose → diff → validate → certify | 20–60 min per team change |
| Platform Operations Overview | Fleet view for SEVs, struggling teams, deadlines, budgets, gates and successes | UI/UX, Observability | XL | Operator can answer “what needs me now?” | Enables multi-product operations | Attention ranking and causal drill-down | Visit separate sessions/logs | One derived projection over canonical events | 1–3 hr/day at larger scale |
| Product Portfolio Autopilot | Connect product revenue/usage/reliability to audits and engineering missions | Business operations, AI | XL | Finds underperforming products and routes improvements | Direct revenue and portfolio optimization | Causal guardrails, experiment design, human investment gates | Manual analytics and ticket creation | Underperformance triggers evidence audit, then candidate mission | Days per portfolio review |
| Configuration Optimizer | Champion/challenger search over bounded parameters in sandboxed evals | R&D, Performance | XL | Finds better configurations systematically | Creates defensible performance advantage | Bayesian/evolutionary search, multi-objective Pareto frontier | Tune prompts by intuition | Search → replay → certify → gradual rollout | Avoided weeks of manual tuning |

## Three example scenarios per major theme

### Readiness Uplift Planner

1. **Python/Azure migration:** detects outdated Azure SDK knowledge and a failing credential probe;
   injects current repo context, runs a symbol-resolution micro-eval and recommends a specialist.
2. **Client artifact:** detects low evidence coverage but adequate implementation readiness; assigns
   a short evidence pass rather than changing the main builder.
3. **Long-running agent:** detects context saturation and repeated file scans; checkpoints, compacts
   context and resumes with a verified handoff packet.

### Agent Family / Lineage

1. **Cloud family:** AWS, Azure and Snowflake descendants share data-platform foundations while
   carrying separate tool permissions and certifications.
2. **Quality family:** tester, evidence reviewer and reliability observer inherit the same verdict
   semantics but specialize in different evidence classes.
3. **Research family:** researcher, synthesizer and adversarial reviewer share sources through typed
   objects while maintaining different prompts and evaluation contracts.

### Surplus Capacity Queue

1. Generate missing unit tests for a low-risk module, stopping before any repository mutation.
2. Re-index already-approved documentation and report stale links without rewriting content.
3. Run cached evaluation replays for challenger presets; do not deploy or modify graders.

## Priority and honest score

| Concept | Strategic value / 10 | Evidence readiness / 10 | Build now? | Reason |
| --- | ---: | ---: | --- | --- |
| Config compiler + lockfile | 10 | 8 | Yes | Extends existing blueprint identity directly |
| Team/agent metrics contracts | 10 | 7 | Yes | Required before optimization or UI claims |
| Capability matcher | 9 | 5 | Prototype | Needs enough evaluated runs to rank credibly |
| Readiness uplift | 9 | 6 | Recommend-only prototype | Can reuse readiness/eval seams without falsifying scores |
| MESH router | 9 | 4 | Research/spec | Powerful but permissions/provenance are substantial |
| Adaptive communication | 8 | 5 | Instrument first | Current repo explicitly lacks a real dialogue requirement |
| Sentinel observer | 8 | 6 | Rules-first prototype | Good fit for existing events/readiness projections |
| Family/lineage | 7 | 3 | Design only | Valuable UX, but depends on capability history |
| Surplus capacity queue | 6 | 4 | Later | Easy to optimize usage instead of value |
| Portfolio autopilot | 9 | 2 | Future | Requires trustworthy execution and business telemetry |

