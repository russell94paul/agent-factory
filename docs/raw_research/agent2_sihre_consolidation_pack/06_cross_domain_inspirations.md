# Cross-Domain Concepts to Transfer into Agent 2.0

## Research map

| Real-world domain | Transferable mechanism | Agent 2.0 interpretation |
|---|---|---|
| Biology / Physiology | Homeostasis | Maintain cognitive/tool/memory/workload variables within viable ranges |
| Immunology | Recognition, quarantine, immune memory | Predictive cognitive immunity |
| Nervous systems | Reflex vs deliberation vs metacognition | Three-speed cognitive control |
| Human metacognition | Knowing what you know/don't know | Calibration and self-competence prediction |
| Digital twins | Model, predict, simulate, optimize | Agent Self Model / Counterfactual Self |
| Human organizations | Transactive memory | Know who knows what and who performs well where |
| Social networks | Relationship strength and complementarity | Dyadic capability / collaboration graph |
| Careers / education | Apprenticeship, certification, promotion | Developmental agents with evidence-backed experience |
| Evolution | Genome, phenotype, mutation, selection | Evolvable agent configuration |
| Ecology | Niches, biodiversity, specialization | Capability biodiversity and emergent specialist roles |
| Swarms / insects | Stigmergy | Digital traces in KG/environment alter future behavior |
| Economics | Markets and bids | Agent task bidding and scarce-resource allocation |
| Military mission command | Intent + decentralized execution | Objectives and boundaries without micromanaging HOW |
| Emergency response / ICS | Modular command structure | Teams dynamically expand/contract with mission complexity |
| High Reliability Organizations | Near misses and weak signals | Learn from almost-failures, not only failures |
| Aviation CRM | Structured brief, challenge, read-back, handoff | Explicit communication protocols |
| SRE | Error budgets | Reliability-linked autonomy and innovation budgets |
| Zero Trust | Continuous verification, least privilege | Dynamic earned authority |
| Resilience engineering | Graceful degradation | Normal -> degraded -> supervised -> safe -> quarantined |
| Organizational cybernetics | Viable System Model | Recursive viable intelligence at Agent/Team/Army levels |
| Quant portfolio theory | Return vs covariance vs risk | Cognitive portfolio optimization |
| Information theory | Entropy and information gain | Value of information and epistemic metabolism |
| Control theory | State estimation + feedback | Agent physiology/homeostasis |
| Risk management | CVaR / tail loss | Tail-risk-aware autonomy |
| Cooperative game theory | Shapley values | Contribution attribution |
| Causal inference | Intervention and mechanism | Transferable diagnosis and strategy selection |

## Human behavior -> computational countermeasure

| Human behavior | Agent analogue | Proposed mechanism |
|---|---|---|
| Confirmation bias | Early hypothesis dominates later interpretation | Independent hypotheses + falsification |
| Groupthink | Agents converge because they see each other's outputs | Preserve initial independence and diversity |
| Overconfidence | Confidence exceeds observed reliability | Calibration and contextual trust |
| Authority bias | Leader dominates stronger specialist evidence | Evidence-weighted expertise |
| Availability bias | Recent cases dominate decisions | Explicit temporal weighting |
| Anchoring | Initial diagnosis constrains later search | Parallel hypotheses and reset policies |
| Escalation of commitment | Agent persists with failing plan | Expected-value replanning |
| Cognitive overload | Too much context degrades reasoning | Health-driven context control |
| Fatigue | Long missions reduce quality | Performance-state monitoring and handoff |
| Curiosity | Seeking useful missing information | Value-of-information |
| Expertise | Fast recognition in familiar contexts | Contextual competence model |
| Wisdom | Knowing when not to act | Abstention, delegation, escalation |

## Design rule

Anthropomorphic concepts should only survive if they map to measurable computational behavior.

Bad:

```yaml
agent:
  mood: tired
```

Better:

```yaml
agent_health:
  context_saturation: 0.91
  recent_error_rate: 0.14
  calibration_delta: -0.11
  tool_latency_p95: 4.2
```

and a policy that changes behavior because of those values.
