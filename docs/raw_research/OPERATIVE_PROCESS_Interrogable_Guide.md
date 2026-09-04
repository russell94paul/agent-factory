# THE OPERATIVE PROCESS — An Interrogable Guide to CELL//OS / QUANTA//OS
### Workflow · Reasoning · Models · Evaluation · Self-Improvement · Weighting

*Version 1.0 — 4 September 2026. Written to be read by a model whose job is to interrogate it, find the seams, and propose new concepts, frameworks, hybrids, and weighting models. Every section ends with the tensions it leaves unresolved. Nothing here is final; the "Open Problems" and "Seed Hybrids" sections are the starting line, not the finish.*

---

## 0. How to read this (instructions for the interrogating model)

You are not being asked to summarize. You are being asked to **attack, recombine, and extend**.

Working rules:
1. Every component below has a stated **job**, **inputs/outputs**, **owner**, and **failure mode**. Whenever two failure modes could cancel each other out, that is a candidate hybrid — name it.
2. Every gate, weight, and score in this system is a *choice*. For each one ask: what would a different choice cost, what would it buy, and under what regime would it dominate?
3. Prefer proposals that are **mechanisms, not metaphors**. A proposal must say what is computed, from what data, and what decision it changes.
4. Use the **Concept Card** schema in §12 for every proposal. Cards without a falsification test are rejected.
5. Anything marked ⚠ is a known weakness. Anything marked ◆ is a deliberate design bet that could be wrong. Anything marked ∅ is an empty slot nobody has filled. Target ∅ first, ◆ second, ⚠ third.

Vocabulary: **Operative** = agent. **Cell** = role + tools + memory + budget + success criteria. **Mesh** = a topology of Cells. **Mission** = a scoped objective with evidence requirements. **Crucible** = adversarial evaluation. **Blackbox** = evolutionary discovery. **Domain Pane** = the vertical instantiation of every layer for one domain (here: futures quant, "QUANTA//OS").

---

## 1. First principles (the physics of the system)

These are the axioms everything else is derived from. If a proposal violates one, it must say why the axiom is wrong.

**A1 — Survival is the benchmark.** The only utility that cannot be reward-hacked is one scored by reality with a delay. In the trading pane that utility is live PnL under prop-firm rules. Everything upstream (backtests, judges, simulations) is a *proxy* and every proxy is gameable.

**A2 — Every search is a multiple-comparisons problem.** Trying N ideas and keeping the best is a statistical operation with a known false-discovery rate. The system must account for N explicitly (a *budget*) and deflate every reported score by it. Corollary: the Evolution Engine is an overfitting machine unless its acceptance rule is deflated.

**A3 — Statistical control and structural control are complementary, not substitutes.** A planted look-ahead leak survives Deflated Sharpe with a perfect score (Gençay 2026, arXiv 2608.27734). Deflation catches *luck*; sealing catches *leakage*. You need both.

**A4 — Evaluators must co-evolve with the things they evaluate, but only against an anchor they cannot influence.** A fixed judge saturates and is gamed; a free-floating judge drifts. The Red Queen Gödel Machine (arXiv 2606.26294) resolves this with frozen-evaluator epochs and anchor-gated replacement. Our anchor is live-vs-backtest divergence.

**A5 — No probabilistic reasoner in the order path.** Operatives decide *what* runs and at *what size*; a compiled, deterministic runtime places orders behind a fail-closed rule gate. Latency, non-determinism, and prompt-injection risk make LLMs disqualifying in the hot path.

**A6 — Information barriers are enforced by permissions, not prompts.** Hypothesis generators cannot see holdout data or detailed Crucible verdicts. If the barrier is a sentence in a system prompt, it does not exist.

**A7 — Lineage is the unit of credit.** A weak idea that spawns strong descendants is valuable (Huxley-Gödel Machine's *clade metaproductivity*). Score nodes by their subtree, not their own result.

**A8 — Commitment is deferred to the last responsible moment.** Belief states stay as distributions (over regimes, strategies, hypotheses) until a decision must be made; collapse happens at the gate, not in the planner.

> Tensions: A1 vs A2 — the real utility arrives slowly, so most search is done against proxies, which A2 says are gameable at scale. A4 vs A6 — co-evolution needs the evaluator to see agent outputs; the barrier says the agent must not see evaluator internals. Where exactly does the one-way mirror sit? ∅

---

## 2. The end-to-end workflow

### 2.1 The Evolution Loop, expanded
```
MISSION → HYPOTHESIZE → BUILD → SEAL → TEST → DEFLATE → SIMULATE → SHADOW → PROMOTE → OPERATE → MONITOR → POST-MORTEM → MUTATE → (loop)
```

| Stage | Job | Inputs | Outputs / artifact | Owner Cell | Gate to pass | Failure mode ⚠ |
|---|---|---|---|---|---|---|
| Mission | Scope the objective and evidence needed | Human intent, capital, firm rules | Mission spec, budget allocation | CIO + Human | Budget assigned | Vague objective → ungated search |
| Hypothesize | Pre-register an edge claim | Research memory (RECALL), regime state, literature | Hypothesis record: edge source, expected decay, capacity, kill criterion, **backtest budget N** | Research Cell | Registered before any data touch | Post-hoc hypotheses (HARKing) |
| Build | Features, labels, model | Point-in-time feature store | Strategy spec (compiled, deterministic) | Research Cell | Compiles; passes unit tests | Lookahead in feature construction |
| Seal | Structural leakage control | Strategy spec | Sealed sandbox run manifest | Evaluation Cell | Sandbox has no access to future data, holdout, or evaluator internals | Leak through timestamps, symbol maps, revised macro data |
| Test | Time-respecting CV | Sealed run | Purged/CPCV fold results, IC/ICIR, feature stability | Evaluation Cell | ICIR > 0.3, stable in ≥70% folds | Ordinary K-fold; no embargo |
| Deflate | Multiple-testing correction | Fold results + budget N | DSR, PBO, SPA p-value, min track-record length | DEFLATOR | DSR > 0.95, PBO < 0.2 | Undercounted N (trials hidden in "tuning") |
| Simulate | Survival under firm rules | Trade distribution | P(pass), P(survive 120d), E[payout], CVaR5, distance-to-breach curve | PROPSIM (Risk Cell) | P(pass) ≥ 40%, P(survive) ≥ 70% at chosen size | Sim ignores payout-cushion dynamics |
| Shadow | Real-time, no capital | Live feed | Live-vs-backtest tracking error, slippage attribution | Execution Cell | ≥30 sessions; slippage ≤ 1.5× modeled | Too-short window; regime not sampled |
| Promote | Allocate capital | All above + red-team verdict | Lifecycle state change; account assignment | CIO + Risk + Human | Three sign-offs | Promotion by narrative, not numbers |
| Operate | Run | Compiled strategy in DISPATCH behind WARDEN | Fills, LEDGER exhaust | Execution Cell | WARDEN passes every order | Any LLM in path (A5) |
| Monitor | Detect decay | LEDGER, PULSE, DISTANCE | CUSUM alarms, drift scores, degradation ladder actions | PULSE / JUDGE | No alarm | Alarm without automatic action |
| Post-mortem | Extract knowledge | Everything | Structured post-mortem → RECALL, lineage update | Post-mortem Analyst | Written within 1 session of retirement | Post-mortems as prose no one reads |
| Mutate | Propose next generation | Lineage graph, CMP scores, post-mortems | New hypotheses (charged to budget) | EVOLVE (Blackbox) | Under budget; anchored | Mutation toward proxies |

### 2.2 Strategy lifecycle states
`incubating → paper → shadow → live-probation → live → probation → quarantined → retired`
Transitions only forward except on alarm. Each state has its own WARDEN rule-set and size cap. ◆ Bet: separate rule-sets for eval-stage and funded-stage accounts (two-regime sizing). Simulation showed eval-optimal size ≠ survival-optimal size.

### 2.3 Data flows that feed the loop
- **TAPE → BARSMITH → FEATUREVAULT** (market data → bars → point-in-time features)
- **ROLLKEEPER, CALENDAR, SPECBOOK** (futures-specific reference data with change history)
- **LEDGER** (own fills, slippage, latency — the only non-hackable dataset the system generates itself)
- **LINEAGE** (Neo4j: hypothesis → feature → model → backtest → deployment → outcome)
- **RECALL** (vector/document memory of post-mortems, regime notes)
- **Agent telemetry** (prompts, tool calls, reasoning traces, cost, disagreement)

> Tensions: the loop is linear on paper but real research is iterative within stages; where iteration is allowed, the budget must be decremented. ∅ No formal accounting yet for *within-stage* iterations (e.g., feature tweaks before Test) — these are hidden trials.

---

## 3. Reasoning architecture (how an Operative thinks)

### 3.1 The cognitive stack per Operative
```
Intent → Context (point-in-time assembly) → Belief state (distribution) → Plan → Act (tool calls, sandboxed) → Evidence → Update belief → Emit
```
Every Operative maintains an explicit **belief state**: a distribution over hypotheses/regimes/strategy fitness, not a single answer (A8). The Context Engine assembles only what the Operative is *permitted* to see (A6).

### 3.2 Meta-agent / task-agent split
Following HyperAgents (arXiv 2603.19461): each Cell has a *task agent* (does the work) and a *meta-agent* (edits the task agent's tools, prompts, workflow). Only the meta-agent participates in self-improvement; the task agent is what gets evaluated. ◆ Bet: meta-agents may edit shared infrastructure, because RQGM found 59–90% of accepted patches modified shared surfaces rather than role-specific code.

### 3.3 Reasoning modes by Cell
| Cell | Dominant mode | Sees | Must not see | Model tier (Model Gateway) |
|---|---|---|---|---|
| Hypothesis Generator | divergent, generative | RECALL, regime state, literature, *own* train-split results | holdout, Crucible verdict detail, live PnL by strategy | frontier reasoning |
| Feature Scientist | constructive | feature store, train split | holdout | frontier |
| Model Developer | constructive | train/val | test/holdout | frontier or fast |
| Backtest Engineer | procedural, deterministic | everything sealed | — | fast/cheap (mostly code) |
| Red-Team Reviewer | adversarial | strategy spec, backtest, **live divergence anchor** | — | frontier; co-evolved |
| Risk Officer / WARDEN | deterministic rules | positions, rules, DISTANCE | — | no LLM (compiled) |
| Execution Trader | deterministic | orders, fills | — | no LLM |
| CIO / Allocator | portfolio reasoning | all aggregates | individual research drafts | frontier |
| Post-mortem Analyst | reflective | everything after retirement | — | frontier |
| JUDGE | evaluative | agent traces, outcomes | — | frontier; calibrated |

### 3.4 Deferred collapse in practice
- REGIMEWATCH publishes a *distribution* (e.g., trend 0.6 / chop 0.3 / event 0.1), never a label.
- ALLOCATOR consumes distributions and outputs weights (§7).
- Collapse happens at WARDEN → DISPATCH: one order or none.

### 3.5 Debate, critique, verification
Research Cell outputs are critiqued by the Red-Team before entering the Crucible. ◆ Bet: adversarial pairs are more reliable than committee voting for trading (committees converge on consensus and consensus is where alpha is not).

> Tensions: ∅ No formal model of *disagreement* between Operatives as a signal (RQGM uses evaluator disagreement implicitly; we do not use it at all). ⚠ Belief states are stored as text today, not as calibrated distributions — calibration is unmeasured.

---

## 4. Models (what is learned, where, and by whom)

### 4.1 Model taxonomy by role
| Model class | Examples | Lives in | Trained on | Evaluated by |
|---|---|---|---|---|
| **World models** (regime, volatility, liquidity) | HMM, clustering, Hawkes, state-space | REGIMEWATCH | market data | forecast log-score, regime persistence |
| **Signal models** (predict returns / labels) | LightGBM/CatBoost on microstructure features, meta-labeling, TFT/PatchTST | TRAINYARD | point-in-time features + triple-barrier labels | CPCV IC/ICIR, DSR |
| **Execution models** (slippage, queue position) | empirical from LEDGER, Almgren-Chriss | DISPATCH | own fills | live vs modeled slippage |
| **Sizing / survival models** | drawdown-constrained Kelly, PROPSIM Monte Carlo | Risk Cell | trade distributions + firm rules | live breach rate vs predicted |
| **Allocation models** | HRP, Bayesian model averaging, bandits | ALLOCATOR | strategy PnL streams | portfolio DSR, CVaR, P(all-dead) |
| **Evaluator models** | co-evolved red-team judge, JUDGE | Crucible | strategy specs + live divergence anchor | anchor accuracy (ε-best-belief) |
| **Meta-models** | which model class works in which regime; which Operative topology works | EVOLVE / LINEAGE | lineage outcomes | clade metaproductivity |
| **Language models** | frontier / fast / local via Model Gateway | all reasoning Cells | — | JUDGE evals; never by PnL directly |

### 4.2 Where LLMs are and are not
- **Are**: hypothesis generation, feature proposal, code generation, news/event parsing, post-mortems, red-team critique, judge.
- **Are not**: signal generation on ticks, sizing, order routing, rule enforcement.
- ◆ Bet on time-series foundation models (Chronos/TimesFM class): treat as *feature generators* subject to the same deflation as any feature, not as strategies.

### 4.3 Model development pipeline
`hypothesis → PIT features → labels → purged/CPCV → train → hyper-search (charged to budget) → deflate → simulate → shadow → registry (MLflow) → live → monitor → retire`
Every hyperparameter trial is a trial. ⚠ Optuna/Ray Tune runs are the most common hidden-N in the industry.

> Tensions: ∅ No model yet for **model-class selection as a function of regime** beyond mixture-of-experts by hand. ∅ No formal *capacity* model (how much capital an edge can absorb) — prop accounts hide this problem until live scale.

---

## 5. Evaluation (the gate stack)

Think of evaluation as five stacked filters, each catching what the previous one cannot.

### 5.1 The five gates
| Gate | Catches | Cannot catch | Formal criterion |
|---|---|---|---|
| **G1 Structural sealing** (sandbox, PIT joins, embargo, split-metric selection — AQuA-style) | leakage | luck | manifest proves no future data reachable |
| **G2 Statistical deflation** (DSR, PBO via CSCV, SPA, min-TRL) | luck / selection | leakage | DSR = Z[(SR − SR₀)·√(T−1) / √(1 − γ₃SR + (γ₄−1)/4·SR²)], with SR₀ = expected max SR of N trials |
| **G3 Simulation / survival** (PROPSIM, stress, crisis replay) | rule-breach risk, sizing error | model error | P(pass), P(survive), CVaR5, distance-to-breach |
| **G4 Live anchor** (shadow/probation) | proxy-reality divergence | slow decay | tracking error, slippage drift, live DSR |
| **G5 Co-evolved judge** (red-team anchored to live divergence) | overfit *patterns* humans and statistics miss | anchor-invisible failures | ε-best-belief accuracy vs anchor; adversarial regularization |

### 5.2 Key formulas the interrogator should know
- **Expected max Sharpe of N null trials**: E[max SR] ≈ √(2 ln N) × (σ_SR). Our sim: 200 trials → best null Sharpe ≈ 2.0 over 2 years.
- **PBO**: fraction of CSCV splits where the in-sample best is below median out-of-sample.
- **Clade metaproductivity** (HGM): CMP(a) = successes over clade(a) / (successes + failures over clade(a)).
- **ε-best-belief** (RQGM): BB_ε = ε-quantile of Beta(1+S, 1+F) — a conservative lower bound on true accuracy.
- **Distance-to-breach**: DISTANCE = (balance − floor) / drawdown allowance; size ∝ clip(DISTANCE/0.5, 0.2, 1).

### 5.3 Anytime-valid alternatives ◆
PACE (arXiv 2606.08106) and SEA (arXiv 2607.00871) replace fixed-N deflation with e-process / FWER-ledger gates that remain valid under continuous peeking. Bet: finance needs *both* — DSR for the backtest ledger, e-process for the live/shadow stream where we peek daily.

### 5.4 Evaluator co-evolution protocol (RQGM adapted)
1. Freeze the red-team evaluator for an epoch (e.g., one month of shadow trading).
2. During the epoch, task agents evolve against the frozen evaluator + G1–G3.
3. At epoch boundary, challenger evaluators compete on the **anchor** (live-vs-backtest divergence of everything traded that epoch).
4. Replace only if challenger's ε-best-belief on the anchor beats incumbent; **selectively erase** utility records scored by the displaced evaluator.
5. Adversarial regularization: strategies the old evaluator passed that then diverged live become the adversarial pool the new evaluator must reject.

> Tensions: ⚠ G2 assumes returns are roughly IID within the ledger; futures intraday returns are not. ⚠ G4 is slow — an epoch of one month gives ~20 sessions of anchor evidence. ∅ **No gate weighting model**: today the gates are AND-ed. Is there a better combination rule (§7.5)? ∅ No treatment of *evaluator disagreement* as evidence.

---

## 6. Self-improvement (what evolves, how, and under what rule)

### 6.1 What can evolve
| Level | Object | Search method | Acceptance rule (current) | Frontier reference |
|---|---|---|---|---|
| L0 | Strategy parameters/features | Optuna, genetic programming (Blackbox) | G1–G3 | formulaic alpha mining |
| L1 | Strategy *code* | LLM-proposed mutation | G1–G4 | AlphaEvolve, RD-Agent(Q) |
| L2 | Operative tools/prompts/workflow (task agent) | meta-agent edits, archive search | JUDGE evals + clade CMP | DGM, HGM, HyperAgents |
| L3 | Evaluators | co-evolution under epochs | anchor ε-best-belief | RQGM |
| L4 | Organization (Cells, Mesh topology, barriers, vetoes) | ∅ not yet | ∅ | ADAS, MaAS, GPTSwarm, AFlow (none constraint-aware) |
| L5 | The acceptance rules themselves | ∅ | ∅ (dangerous; see §9) | — |

### 6.2 Archive search (how Blackbox explores)
- Maintain an **archive** of agents/strategies as a tree (parent → child mutations), never a single champion.
- Select parents by **Thompson sampling over clade metaproductivity** (HGM) — a lineage that keeps producing survivors gets more budget.
- Expansion vs evaluation controlled by a UCB-Air style gate (grow archive as N^α).
- ◆ Bet: quality-diversity (MAP-Elites) with a *regime* behavior descriptor keeps specialists alive that a single objective would kill.

### 6.3 The acceptance rule is the whole game
Current rule for L0–L1: pass G1–G3 (+G4 for live). Proposed **Deflated Gödel Machine** rule: a mutation is committed only if
  (i) its CPCV out-of-sample DSR, computed against the hypothesis's *pre-registered budget N*, exceeds threshold,
  (ii) PBO < 0.2,
  (iii) it survives an embargoed shadow window, and
  (iv) the co-evolved red-team does not veto.
This is white space in the literature: PACE/SEA gate general agents with anytime-valid tests; Gençay applies DSR *post-hoc*; AQuA uses sealing without deflation. Nobody has the recursive loop + deflated commit gate + delayed real anchor together.

### 6.4 Budgets
- Each hypothesis carries a **backtest budget** N (default 50 trials). Every fold-evaluation, hyperparameter trial, and feature variant decrements it. Exhausted ⇒ hypothesis closed, recorded in LINEAGE.
- Each Cell carries a **token/compute budget**; JUDGE tracks cost per validated hypothesis (FinOps-aware evolution).
- ⚠ Budgets are the easiest thing to game: an Operative that splits one hypothesis into ten "new" ones resets N. ∅ No similarity-based budget inheritance yet (AlphaAgent uses AST similarity for originality — a candidate).

### 6.5 Epochs and non-stationarity
Search is organized in epochs (RQGM). Within an epoch the evaluator and rule-set are frozen so per-epoch guarantees hold; across epochs the utility may drift (regime change, firm rule change, evaluator replacement). Selective erasure keeps stale utility from mixing.

### 6.6 Safety inside the loop
- WARDEN and the information barrier are **outside** the evolvable surface (L5 is forbidden to the meta-agent).
- Human sign-off required at Promote and at any evaluator replacement.
- Full lineage auditability in Neo4j; every accepted mutation stores its diff, its trial count, and its gate scores.

> Tensions: ⚠ Clade metaproductivity assumes repeatable trials; live epochs are not repeatable. ∅ L4 (organizational evolution) has no search space defined. ◆ Forbidding L5 may prevent the system from discovering better gates; allowing it invites reward hacking. ∅ No *similarity-aware* budget accounting.

---

## 7. Weighting models (where the interrogator is most likely to find something)

Weights appear at six places. Today each is solved separately with an off-the-shelf method. The open question is whether they should be *one* model.

### 7.1 Signal → strategy weights (inside a strategy)
Stacking / meta-labeling. Signed continuous signals combined so that agreement amplifies and disagreement cancels (interference). ⚠ Learned combiners are themselves a trial.

### 7.2 Strategy → portfolio weights (ALLOCATOR)
Current: HRP for risk budget × EW-Sharpe softmax with 30% equal-weight floor and correlation caps.
  w_i ∝ exp(κ · SR̂_i), SR̂ from EWMA (λ = 0.93), then w = 0.7·softmax + 0.3/K.
Sim: Sharpe 0.50 → 0.72 across a regime shift vs equal weight. ◆ κ and λ are hand-set. ∅ Regime-conditional weights (weights as a function of REGIMEWATCH's distribution) are not implemented.

### 7.3 Strategy × account × firm allocation
Constrained problem: maximize E[payout] s.t. P(all accounts dead in 120d) ≤ 20%, per-firm share ≤ 35%, per-account DISTANCE ≥ 30%. Solved greedily. ∅ Candidate: QUBO / annealing solver as an ARENA competitor.

### 7.4 Lineage credit weights (EVOLVE)
Clade metaproductivity pools binary outcomes over subtrees. ∅ Outcomes in trading are continuous and delayed; CMP over *deflated Sharpe buckets* or over *survival time* is unexplored.

### 7.5 Gate weights (Crucible) ∅
Gates are AND-ed. Options nobody has tested here: (a) weighted log-odds combination with weights learned from live divergence; (b) sequential gates ordered by cost-of-evaluation × discriminative power; (c) treat gates as an ensemble of judges with RQGM-style co-evolution of *the combination rule* (dangerous: L5).

### 7.6 Evaluator weights (JUDGE panel)
Multiple judges (statistical, red-team, human) — currently any veto wins. ∅ Calibrated weighting by each judge's historical anchor accuracy is the obvious next step.

### 7.7 Candidate unified view ◆
All six are instances of one problem: *given noisy, delayed evidence about a set of units (signals, strategies, accounts, lineages, gates, judges), allocate a scarce resource (capital, budget, trust) to maximize a survival-weighted objective under correlation and rule constraints.* A single **Bayesian survival-weighted allocator** with unit-specific priors might replace six hand-built weighting schemes. Whether that is elegant or a disaster is exactly what the interrogator should decide.

---

## 8. Monitoring and decoherence

Three levels, one ladder.
| Level | Signals | Detector | Automatic action ladder |
|---|---|---|---|
| Strategy | rolling Sharpe CUSUM, DD vs Monte Carlo envelope, slippage drift, PSI on top features | PULSE | size −50% → pause → quarantine → flatten |
| Portfolio | correlation spikes, concentration, aggregate DISTANCE | PULSE/CIO | de-risk book; block promotions |
| Operative | eval-score drift, tool-error rate, cost creep, disagreement rate, reasoning-trace anomalies | JUDGE | route to stronger model → freeze mutations → roll back version |

Literature: "Agent Drift" (arXiv 2601.04170) proposes an Agent Stability Index; "How Fast Do Agents Rot?" (arXiv 2609.01660) shows per-step reliability compounds geometrically to guaranteed long-horizon collapse. ∅ No one has an agent-drift metric anchored to a *financial* ground truth; JUDGE could provide the first.

> Tensions: ⚠ CUSUM thresholds are hand-set; ∅ no joint model of strategy decay and Operative decay (does a degrading researcher produce strategies that decay faster?).

---

## 9. Open problems (targets, ranked by emptiness)

1. **∅ Constraint-aware organizational evolution (L4).** Search over Cell roles, Mesh topology, information barriers, and veto rights, scored by clade-level outcomes, where barriers are *rewarded* dimensions not just constraints. No published system does this.
2. **∅ The one-way mirror.** A formal spec for what the co-evolving evaluator may see of agents and what agents may see of it, that satisfies both A4 and A6.
3. **∅ Similarity-aware budget accounting.** Trials charged to a hypothesis *family* by semantic/AST similarity so splitting does not reset N.
4. **∅ Gate combination rule.** Replace AND with a learned, anchor-calibrated combination; prove it does not become gameable.
5. **∅ Continuous, delayed clade credit.** CMP over deflated, delayed outcomes.
6. **∅ Regime-conditional everything.** Weights, model-class selection, evaluator strictness, and budgets as functions of REGIMEWATCH's distribution.
7. **∅ Financially-anchored agent decoherence metric.**
8. **◆ Whether L5 (evolving the acceptance rules) can ever be made safe** — e.g., only under a frozen meta-anchor with human veto.
9. **⚠ Non-IID deflation.** DSR variants for autocorrelated, fat-tailed intraday futures returns.
10. **⚠ Capacity.** An edge's capital capacity is invisible in prop accounts until it is not.

---

## 10. Seed hybrids (starting points, deliberately unfinished)

These are sketches the interrogator should improve, merge, or kill.

**H1 — Deflated Gödel Machine.** Archive search (HGM) + deflated commit gate (DSR/PBO on pre-registered N) + anytime-valid live gate (e-process) + delayed anchor (shadow PnL). *Test:* accepted mutations' live DSR vs a keep-if-Sharpe-up baseline, with a planted-leakage oracle to expose the gate's blind spot.

**H2 — Red Queen Risk.** RQGM evaluator co-evolution where the evaluator is a red-team judge and the anchor is live-vs-backtest divergence. *Test:* co-evolved judge's calibration on out-of-sample divergence vs frozen DSR/PBO and a generic LLM judge.

**H3 — Barrier-Rewarded Org Search.** MaAS/GPTSwarm-style topology search where the objective includes a leakage/contamination penalty and clade-level survival, with barrier and veto edges in the search space. *Test:* does the searched org outperform the same search without barriers *on live-anchored outcomes*, not on backtests?

**H4 — Survival-Weighted Universal Allocator.** One Bayesian allocator across signals, strategies, accounts, lineages (§7.7). *Test:* replace ALLOCATOR + EVOLVE budget allocation with it; compare portfolio DSR and P(all-dead) in PROPSIM and shadow.

**H5 — Regime-Indexed Quality-Diversity Archive.** MAP-Elites over strategies with behavior descriptors = (regime, holding period, turnover); elites per cell; ALLOCATOR draws from the archive by REGIMEWATCH distribution. *Test:* diversity-adjusted portfolio Sharpe vs single-objective evolution across a regime shift.

**H6 — Disagreement as Signal.** Treat Operative/judge disagreement as a feature: high disagreement ⇒ smaller size, more budget to that hypothesis's clade. *Test:* does disagreement predict live divergence?

**H7 — Decoherence-Coupled Decay.** Joint model where Operative drift (JUDGE) is a leading indicator of strategy decay (PULSE). *Test:* Granger-style: does researcher eval drift lead strategy Sharpe CUSUM alarms?

**H8 — Similarity Ledger.** Trials charged by AST/embedding similarity to a hypothesis family (AlphaAgent-style originality). *Test:* does it reduce PBO of promoted strategies at equal budget?

---

## 11. Interrogation prompts (run these against this document)

1. For each ⚠, propose a mechanism that removes it and state what new ⚠ it introduces.
2. For each ∅, propose at least two designs and a decisive experiment that would pick between them.
3. Find every place two components use the same statistic differently (e.g., Sharpe in G2 vs §7.2). Should they be unified? What breaks?
4. Which of the eight axioms is most likely false? Design the experiment that would falsify it.
5. Which two of the seed hybrids H1–H8 conflict? Which two compose into something stronger than either?
6. Where is the system *most* reward-hackable by a meta-agent? Write the exploit, then the patch.
7. If you could make exactly one thing evolvable that is currently frozen, what is it and what anchor protects it?
8. Propose a **new weighting model** that no section above contains. It must specify units, evidence, prior, update rule, constraint set, and the decision it changes.
9. Propose a **new framework** (a named, reusable pattern) that generalizes beyond trading to any Domain Pane.
10. Rank all your proposals by (novelty, defensibility, cost, fit). Be harsh: 2026 papers already claim acceptance-gate-as-multiple-testing (PACE, SEA), post-hoc DSR on agentic search (Gençay), sealed recursive quant research (AQuA), and evaluator co-evolution (RQGM).

---

## 12. Concept Card (required output schema)

```
CONCEPT: <name>
TYPE: mechanism | framework | hybrid | weighting-model
TARGET: <which ∅ / ◆ / ⚠ it addresses>
COMPUTES: <what, from what data>
CHANGES: <which decision or gate>
PRIOR ART: <closest 1–3 works and the delta>
FALSIFICATION: <the experiment, baseline, metric, threshold that would kill it>
COST: <data, compute, time; which epochs>
RISKS: <reward hacking, leakage, statistics, engineering>
CELL//OS MAPPING: <layers / engines / Operatives that implement it>
SCORE: novelty /10, defensibility /10, cost /10, fit /10
```

---

## 13. Glossary (compact)
**CPCV** combinatorial purged cross-validation · **DSR** deflated Sharpe ratio · **PBO** probability of backtest overfitting · **SPA** superior predictive ability test · **CMP** clade metaproductivity · **ε-best-belief** conservative Beta-quantile utility · **e-process** anytime-valid test statistic · **HRP** hierarchical risk parity · **PIT** point-in-time · **DISTANCE** distance-to-breach · **WARDEN** fail-closed pre-trade rule gate · **DEFLATOR** statistical deflation gate · **PROPSIM** prop-rule survival Monte Carlo · **ARENA** strategy tournament · **JUDGE** Operative evaluator · **PULSE** strategy/portfolio health · **RECALL** research memory · **LINEAGE** Neo4j hypothesis graph.

---

*End of guide. The measure of a good interrogation is not agreement — it is a Concept Card that survives its own falsification test.*
