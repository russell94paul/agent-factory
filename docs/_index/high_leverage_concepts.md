# High-leverage concepts — candidates, not winners

**Generated 2026-09-02** against `agent-factory` @ `fc78074`.
**Amended 2026-09-02** @ `7b19baf` by the `.agent-platform` delta pass — `HL-16` and `HL-17`. See
[`agent_platform_delta_synthesis.md`](agent_platform_delta_synthesis.md).

⛔ **NOTHING IS SELECTED HERE.** This file identifies ideas whose *value-to-cost ratio looks
unusually favourable* and states, for each, exactly what is known and what is not. It does not rank
them against each other, does not recommend a build order, and does not eliminate anything.
Selecting is the job of the architecture synthesis that follows this pass.

**How a concept got onto this list.** One or more of:

- it is **cheap to test against evidence this repository already holds** — the strongest reason;
- it would **unblock several other concepts at once**;
- it is **already half-built under a different name**, so the marginal cost is low;
- two independent parts of the corpus **arrived at it separately** (a genuine signal, unlike the
  agreement between packs that share a source file);
- refusing it would **cost something specific and named**.

**How a concept did NOT get on.** Being interesting, being ambitious, or being repeated by five
packs that share one source file. Also excluded: anything on `README.md`'s absence table whose
unlock condition is not met — those are not leverage, they are deferrals, and reporting them here
would be the error `concept-inventory` §1 exists to prevent.

⚠ **One constraint governs every entry.** No agent has completed a real run
(`runs.jsonl`: 10 rows, zero `PASS`; 7 `agent_returned`, all `dry_run=True`). Several entries below
become dramatically cheaper to evaluate after that changes, and each says so.

---

## HL-01 · The expected-work manifest and `scope_hash`

| | |
|---|---|
| **Concept** | Declare the work a run is expected to do, hash it, and derive `SUCCEEDED` from scope closure — so a team cannot pass by doing less than the task required |
| **Source** | `docs/research/answers/R3-answer-control-plane.md`, executive verdict · `docs/absorption-backlog.md` AB-01 |
| **Potential value** | ⭐ **It closes the one hole every existing gate shares.** Every gate in this repository measures the work it was *told about*. R3: the six prescriptions *"can still report success over work they never knew existed."* |
| **Affected layer** | Contract / gates / task store — `factory/contract.py`, `factory/tasks.py`, `factory/evidence.py` |
| **Evidence available** | R3's design, filed and read. ⛔ Nothing else. It has been unabsorbed since 2026-08-21 and `SYNTHESIS` §5's nine-step build order **has no step for it**. |
| **Uncertainty** | How scope is declared without becoming a second hand-maintained list — the defect `board.py` refuses on principle. Unresolved in the source. |
| **Research required** | **None to start.** The design exists. What is missing is a decision: adopt it into §5, or record in §5 why it was refused. |
| **Likely experiment** | Add a declared-scope field to one mission (`marketing-model-reconstruction-v1` has five tasks with per-task contracts) and check whether any task closed having done less than declared. Retrospective, cheap, uses data already on disk. |
| **Difficulty** | **Medium.** The mechanism is small; getting the declaration to be derived rather than typed is the hard half. |

---

## HL-02 · Score a second connector

| | |
|---|---|
| **Concept** | Take one more real connector end to end through the twelve-assertion contract and add it to the eval corpus |
| **Source** | `docs/absorption-backlog.md` AB-04, restated after `docs/findings.d/F76` |
| **Potential value** | ⭐ **It converts n=1 into evidence of generality**, and is the precondition for the optimizer, the gym and every claim that the contract means anything beyond one fixture. AB-04: it *"will find the assumptions baked into the windsorai fixture faster than manufacturing 38 more."* |
| **Affected layer** | Eval corpus · `evals/`, `factory/corpus.py`, `factory/targets.py`, `blueprints/` |
| **Evidence available** | MEASURED — the corpus is one file, 6,762 bytes, one connector; **48 have never been scored**. All twelve assertions are calibrated with a known-bad. The machinery to score a second one already exists. |
| **Uncertainty** | ⛔ **`docs/research/README.md` §4 question 3 may invalidate the existing fixture**: *"20 rows across 18 campaigns on one date cannot be unique on `(account_id, campaign_id, date)`. If it is one account, the declared primary key is wrong and the calibration world is built on a mistake."* Settle that first or the second connector inherits the error. |
| **Research required** | **None.** Two questions for a human (GAP-30), then run it. |
| **Likely experiment** | This *is* the experiment. |
| **Difficulty** | **Low-medium** — mostly access and data, not code. |

---

## HL-03 · The five field classes: `TUNABLE` / `DECLARED` / `MEASURED` / `DERIVED` / `POLICY`

| | |
|---|---|
| **Concept** | Every configuration field carries exactly one class. `POLICY` fields are human-governed and may never be mutated by a search; `MEASURED` fields are append-only observations and never live in the config file |
| **Source** | `agent_genome_research_pack/01_CURRENT_DESIGN_SYNTHESIS.md` + `schemas/field_classification.yaml` |
| **Potential value** | ⭐ **Two independent parts of the corpus arrived at this, and neither cites the other.** `SYNTHESIS` §6's never-optimise list — retry caps, gate thresholds, tenancy checks, timeouts, evaluator thresholds, corpus, *"safety specification, not hyperparameters"* — **is the `POLICY` class**. That convergence is the strongest single argument in the concept index, because the two sources genuinely are independent. |
| **Affected layer** | Agent configuration · `factory/blueprint.py`, `factory/presets.py`; and the future optimizer's legal search space |
| **Evidence available** | The pack's design; §6's list; and two measured defects it would have prevented — `F90` (a field inside the version hash that nothing reads) and `architecture-v0` §5 (*"a spec field that nothing reads is worse than no field"*). |
| **Uncertainty** | Who assigns a class, and what happens when a field's class should change. Unaddressed in the source. |
| **Research required** | **None.** It is a schema decision. |
| **Likely experiment** | Classify the existing `AgentSpec`/`TeamSpec` fields. If any field cannot be classified, that is a finding about the field. If `TeamSpec.repo` classifies as `DECLARED` while nothing reads it, `F90` becomes structurally visible instead of being discovered by accident. |
| **Difficulty** | **Low.** Annotation plus one test. |

---

## HL-04 · Extend the counterfactual maturity ladder beyond the case study

| | |
|---|---|
| **Concept** | `EXERCISED` / `IMPLEMENTED_NOT_EXERCISED` / `SIMULATED` / `PROPOSED`, enforced by a type that **raises** — a maturity claiming code must name `module:line`; a maturity claiming it *ran* must cite the evidence of it running; anything below `EXERCISED` has its basis forced to `SIMULATED` *"whatever the authored file said"* |
| **Source** | `factory/assertions.py` — already built, scoped to one artifact type |
| **Potential value** | ⭐ **It is the corpus's own answer to its own biggest recurring failure**, and it is enforced by a dataclass rather than by vigilance. `concept_index.yaml` C-GV-04 records four separate findings (F79, F87, F90, F98) that are all the same defect: a declaration mistaken for a mechanism. This ladder makes that defect *unconstructible* in the places it is applied. |
| **Affected layer** | Currently `factory/case_study.py` only. Candidates: `factory/readiness.py` (30 gates), `factory/presets.py` (verifier state), `factory/registry.py` (proven/declared/unbuilt) |
| **Evidence available** | Running, tested, and rendered — `case_study_render.py:490` publishes the exercised-vs-claimed ratio in the artifact itself. |
| **Uncertainty** | Whether `exercised_proof` can be produced automatically for a gate, or whether it becomes a field someone fills in — in which case it is the defect it exists to prevent. |
| **Research required** | **None.** |
| **Likely experiment** | Apply it to `factory/registry.py`, which already distinguishes proven / declared / unbuilt workflows in prose. If the ladder's three rules can be enforced there, it generalises. |
| **Difficulty** | **Low per site; medium to generalise.** |

---

## HL-05 · Repetition → deterministic meta-tools

| | |
|---|---|
| **Concept** | Mine successful traces for repeated stable tool-call sequences and promote one, after tests and a human approval, into a single deterministic composite tool |
| **Source** | `Agent Factory Vision.txt` §8 (citing Microsoft Research, *Optimizing Agentic Workflows Using Meta-Tools*) · `FEATURE_INTEGRATION_SEEDS.md` §9 · `RESEARCH_QUEUE.yaml` R-META-01 |
| **Potential value** | ⭐ **It moves the deterministic/agentic boundary in the direction this repository already believes in, with evidence rather than by decree.** `QUALITY_GATES.md`: six of seven gates are deterministic *by design*. This is a mechanism for making the seventh deterministic once it is understood — a compounding loop that makes the system *more* checkable over time. |
| **Affected layer** | Tool registry / provider seam / trace store — `factory/provider.py`, `factory/deploy.py` |
| **Evidence available** | External, cited, **not verified here**. Zero internal evidence: there are no traces to mine. |
| **Uncertainty** | ⛔ **It needs a structured trajectory object and there is none.** `deploy.py` streams a transcript; `concept-inventory` §4.2 records the absence explicitly. And with 7 dry-run dispatches there is no corpus of successful traces. |
| **Research required** | GAP-33 (observability and trace standards) is the real prerequisite — and it is a `NOT-SEARCHED` axis the corpus already named. |
| **Likely experiment** | Not yet runnable. The cheap precursor is to emit a structured trajectory alongside the transcript and see whether repeated sequences appear at all in whatever real runs eventually occur. |
| **Difficulty** | **High**, and gated behind HL-08. |

---

## HL-06 · Expected Verification Value

| | |
|---|---|
| **Concept** | Decide whether an additional verifier or test is worth running, as `error probability × impact × detection probability`. Selective assurance rather than uniform |
| **Source** | `agent2_sihre_consolidation_pack/05_quantitative_agent2_features.md` |
| **Potential value** | ⭐ **Directly testable against data this repository already holds, unlike the rest of its pack.** Twelve assertions, each with a calibrated known-bad, each with recorded verdicts. Detection probability per assertion is *obtainable from disk*. It would also give `factory/verifiers.py` a principled answer to "which check should this preset own", currently a judgement. |
| **Affected layer** | Contract / verifier registry / gates |
| **Evidence available** | The calibration data. ⛔ No impact model — nothing scores the cost of a defect escaping. |
| **Uncertainty** | Impact is the hard term and the corpus has one source for it: `delivery-001`'s **defect escape distance** analysis. Whether that generalises from one delivery is unknown. |
| **Research required** | Low. The formula is standard decision theory; the work is instantiating it. |
| **Likely experiment** | Compute detection probability per assertion from the existing calibration runs. If assertions differ sharply, that alone is a finding about where assurance is concentrated. |
| **Difficulty** | **Medium.** The measurement is easy; the impact model is not. |

---

## HL-07 · Cognitive error correlation

| | |
|---|---|
| **Concept** | Measure **which agents fail together**, and select teams by error *covariance* rather than by individual accuracy — so diversity provably reduces correlated failure instead of merely adding members |
| **Source** | `agent2_sihre_consolidation_pack/03_agent2_concept_registry.md` + `05` + `DR02` |
| **Potential value** | ⭐ **It is the only proposal in the entire corpus that offers a MECHANISM for why a team might beat a single agent.** R2's evidence is that the naive version does not: a mean effect of −3.5% with an interval spanning zero, and −70% on sequential planning. If multi-agent structure ever helps here, correlated-failure reduction is the most plausible reason, and it is measurable. |
| **Affected layer** | Team composition / evaluation |
| **Evidence available** | ⛔ **None internal.** Requires several agents scored on the same tasks; the estate has one connector scored and no multi-agent runs. |
| **Uncertainty** | High. It is also the strongest available answer to the question `README.md` defers behind *"evidence a tier helps"*. |
| **Research required** | Prior art on ensemble error correlation transferred to LLM agents (`DR02`, unrun). |
| **Likely experiment** | ⭐ **Cheap version available now:** run the *same* ticket under two different presets (they already differ in model, effort and caps) and record whether the failures coincide. That needs two real runs, not an organizational architecture — so it is gated behind GAP-09, not behind the Agent Army. |
| **Difficulty** | **Medium**, and it becomes the natural *first* multi-agent experiment rather than a downstream one. |

---

## HL-08 · A structured trajectory object

| | |
|---|---|
| **Concept** | Emit a structured, standard-shaped record of what an agent did — tool calls, decisions, verdicts — alongside the transcript |
| **Source** | `concept-inventory` §4.2 (a `NOT-SEARCHED` axis) · R13's OpenTelemetry GenAI recommendation · `agent_genome_research_pack/schemas/agent_runtime_event.schema.yaml` |
| **Potential value** | ⭐ **It is the common prerequisite of at least five other concepts** — meta-tool extraction (HL-05), phenotype measurement, communication-defect attribution, credit assignment, and replay. Each is currently blocked on the same missing artifact, and none of the five says so. |
| **Affected layer** | Execution / observability — `factory/deploy.py`, `factory/events.py`, `factory/provider.py` |
| **Evidence available** | `factory/events.py` already exists and holds 61 events; `docs/FACTORY-UI-PROMPT.md` §3 argues *"Phase 0 — build the event ledger. No UI. This is the real work."* The half that exists is the *run* event stream; the *within-run* trajectory does not. |
| **Uncertainty** | Whether to adopt the OpenTelemetry GenAI semantic conventions or define a local shape. **This is the actual open question and it has never been researched** (GAP-33). |
| **Research required** | GAP-33 — one prior-art pass. It is the best-scoped research mission the corpus offers, because the answer is a standard to adopt or reject rather than an architecture to invent. |
| **Likely experiment** | Emit one run's trajectory in the candidate shape and check whether the five downstream concepts can each read what they need from it. |
| **Difficulty** | **Medium.** ⭐ **Highest fan-out of any concept in this file.** |

---

## HL-09 · Topology as data — arbitrarily nested service designations

| | |
|---|---|
| **Concept** | Do not hard-code Army → Command → Corps → … → Agent. That is *one possible preset*. An organization is a tree of parent/child nodes whose grammar is data |
| **Source** | `army_ui_concept_pack/05` · `chat_design_pack/06` · `FEATURE_INTEGRATION_SEEDS.md` §11 |
| **Potential value** | ⭐ **It is the only organizational proposal in the corpus that is a REFUSAL TO COMMIT rather than a commitment.** Councils, guilds, federations, markets, meshes, blackboards, swarms and temporal echelons all become expressible without a schema change — which is exactly what a topology tournament (GAP-14) would need, and exactly what a fixed hierarchy would foreclose. |
| **Affected layer** | Organization model — nothing exists yet, so this is a decision about a future schema |
| **Evidence available** | ⛔ None that any nesting depth beyond one team is useful. The estate has never run two teams. |
| **Uncertainty** | Whether *any* of this is needed. The honest state is that the shape is unknown, which is precisely why not committing has value. |
| **Research required** | GAP-14 (topology tournament) and GAP-02 (what Moise+ and IMACS already provide — organisation-oriented MAS **has a metamodel**, and adopting it may be cheaper than designing one). |
| **Likely experiment** | None yet. This is a constraint on a future design, not a build. |
| **Difficulty** | **Low as a constraint, high as an implementation.** ⚠ Its leverage is entirely in the constraint. Building the general nested-topology machinery now would be the error `README.md`'s absence table exists to prevent. |

---

## HL-10 · The evaluation protocol and readiness gates from the ZEUS pack

| | |
|---|---|
| **Concept** | Before a concept may be implemented: core metrics, a baseline task suite, **target thresholds it must beat**, a prototype ladder, and ten readiness gates including *"three world interactions beat baseline"* and *"no Goodhart reward loop"* |
| **Source** | `zeus_world_ui_research_pack/05_EVALUATION_PROTOCOL.md` + `09_IMPLEMENTATION_READINESS.md` |
| **Potential value** | ⭐ **It is theme-independent and survives the supersession of everything around it.** The Zeus *branding* is explicitly superseded (`chat_design_pack` §I); the protocol is not. It is also the only artifact in the entire inbound corpus that supplies a **graduation rule** — a way for a proposed concept to earn implementation. `C-OR-03` says organizational design should become empirical and gives no method; this is the method, written for a different subject. |
| **Affected layer** | Governance / process. Composable with `README.md`'s absence table and `SYNTHESIS` §6's unlock conditions |
| **Evidence available** | The protocol itself. Never applied to anything. |
| **Uncertainty** | It was written for UI concepts. Whether the thresholds transfer to organizational or agent concepts is untested — but the *shape* clearly does. |
| **Research required** | **None.** |
| **Likely experiment** | Apply it to one deferred concept from the absence table and see whether its unlock condition can be restated as a graduation rule with a baseline suite. If it can, the absence table gains a method it currently lacks. |
| **Difficulty** | **Low.** ⭐ Possibly the highest value-to-cost ratio in this file. |

---

## HL-11 · The neighbours discipline, generalised

| | |
|---|---|
| **Concept** | Every research pass carries a table naming what it **owns** and what it must **NOT answer**, and is told: if a question belongs to a neighbour, say so and stop rather than answering it thinly |
| **Source** | `docs/research/README.md` §2 — this repository's own invention. **No inbound pack contains anything like it** |
| **Potential value** | Prevents duplicate research *at the prompt* rather than detecting it *at the answer*. `README.md` §2: *"The expensive failure in this programme is two passes answering the same question differently, which costs a run and then costs a reconciliation."* Directly applicable to agent task decomposition, not just to research. |
| **Affected layer** | Research process; and potentially any future team decomposition |
| **Evidence available** | Every prompt from R12 onward carries one. ⛔ **And a measured failure:** it did **not** prevent the alerting question being answered five different ways across five passes (AB-19). |
| **Uncertainty** | ⭐ That failure is the interesting part: the neighbours table scopes **subjects**, and the alerting question **cut across subjects**. A cross-cutting-question register would be the missing half. |
| **Research required** | None. |
| **Likely experiment** | Enumerate the questions answered by more than one pass (AB-19 gives one; there are probably others) and check whether a cross-cutting register would have caught them. |
| **Difficulty** | **Low.** |

---

## HL-12 · Near-miss memory

| | |
|---|---|
| **Concept** | A **successful** mission can still carry a safety lesson. Capture it |
| **Source** | `agent2_sihre_consolidation_pack/03_agent2_concept_registry.md` |
| **Potential value** | ⭐ **Genuinely absent, and the absence is structural.** `factory/preflight.py` shows a run its recorded *failures*; `docs/findings.d/` records *corrected premises*. **A success with a lesson currently leaves no trace anywhere.** This estate has already produced at least one: `docs/evidence/live-probes-a1-a5` §6 records *"a trap this session walked into and backed out of"* — a near miss, captured only because someone chose to write a prose section about it. |
| **Affected layer** | Memory — `factory/preflight.py`, `docs/findings.d/`, `factory/tasks.py` |
| **Evidence available** | ⚠ At least three near misses are recorded in prose across the evidence documents. None is in any ledger, so none is retrievable. |
| **Uncertainty** | What triggers capture. An agent asked *"did anything nearly go wrong?"* will answer no — the same reason `QUALITY_GATES.md` makes six of seven gates deterministic. |
| **Research required** | Prior art on near-miss reporting in high-reliability organisations (aviation, healthcare). Well-established outside; never surveyed here. |
| **Likely experiment** | Retrospective: sweep the evidence documents for near misses already written in prose and see how many exist. If it is more than a handful, the capture rate through prose is the finding. |
| **Difficulty** | **Low to try, high to make reliable.** |

---

## HL-13 · A written rejection closes a row

| | |
|---|---|
| **Concept** | An unabsorbed conclusion and a rejected one look identical in the record. So a row closes when its action is done **or** when a written rejection exists naming it. Both are progress; silence is not |
| **Source** | `docs/absorption-backlog.md`, closing rule |
| **Potential value** | ⭐ **It is the cheapest possible fix for the corpus's largest measured waste.** 19 rows open, **0 closed**; two whole research answers (191 KB) with no disposition; five of R13 run 2's six findings untaken, one of which refutes a premise a settled decision rests on. |
| **Affected layer** | Process. Composable with `factory/synthesis.py`'s currency gate |
| **Evidence available** | MEASURED — the counts above. And a worked example that it functions: `docs/reviews/external/verification.md` **rejected two proposed tickets in writing**, and those two are closed. |
| **Uncertainty** | Whether a rejection can be enforced mechanically. `F75` shows the existing instruments detect *unmentioned*, not *unabsorbed* — mentioning an answer satisfies them. |
| **Research required** | **None.** |
| **Likely experiment** | Extend `factory/synthesis.py` to require a disposition marker per filed answer, not merely a mention. That single change would have caught R14 and R18 on the day they landed. |
| **Difficulty** | **Low.** ⭐ The clearest small mechanism in this file. |

---

## HL-14 · The isolation ladder

| | |
|---|---|
| **Concept** | An agent's isolation tier is chosen by **what its task touches**, declared up front and enforced. An agent asking for a verb its tier does not carry is refused, and the refusal is an audit event |
| **Source** | `docs/specs/architecture-v0.md` §4 — the highest-leverage unbuilt idea originating in this repository rather than in a pack |
| **Potential value** | *"'Do not touch prod' in a prompt is a **request**; a role with no grant on prod is a **control**."* It also claims to remove the 3-lane concurrency cap for data work, and to make the promotion evidence (clone→real diff) **mechanically producible**. |
| **Affected layer** | Execution / isolation / approval — `factory/deploy.py`, `factory/worktrees.py`, `factory/blueprint.py` |
| **Evidence available** | T0 is built and measured (3 lanes, 20 commits, zero conflicts). ⛔ T1 and T2 are unmeasured on every axis. |
| **Uncertainty** | **Three named objections, all on file.** A container does nothing about prompt injection (R16-outside §3). The clone is a compromised oracle at exactly the layer the evidence rule protects (R17 §16.3). *"Data work does not conflict"* is asserted, not measured (architecture-v0 §7.2 — its own concession). |
| **Research required** | None on the *idea*. GAP-11 and GAP-12 are **measurements**: a T1 container start-up cost on Windows/WSL, and a T2 clone creation + validation cost. |
| **Likely experiment** | Build T1 only, with an egress allowlist, and measure start-up. It is the smallest step that tests the whole ladder's premise, and `architecture-v0` §8 already sequences it fourth for exactly that reason. |
| **Difficulty** | **Medium for T1, high for T2.** ⚠ Note the leverage is asymmetric: T1 is where the cost is measured, T2 is where the value is claimed. |

---

## HL-15 · The Mission Assurance Receipt — trust as a product surface

*Added 2026-09-02 by the supplementary coverage pass, from a source the original pass could not read.*

| | |
|---|---|
| **Concept** | A concise machine-generated per-mission artifact, emitted from **the same evidence the runtime already uses**, with nine sections: identity · organization (preset + version, model/tool versions, knowledge snapshot) · execution (mission graph, blocked nodes, deterministic vs agentic) · evidence (evals, RED→GREEN proof, parity checks, diff summary, artifact hashes) · **independent challenge** (shadow agreement/disagreement, unresolved uncertainty) · governance (policies, gates, approvals, budget actual vs limit) · recovery (rollback/canary, last-certified fallback) · provenance · outcome |
| **Source** | `docs/raw_research/converted/Agent_Factory_Frontier_Architecture_Prioritization_Pack.md` §9. Independently, `agent-army-research/repo-boundary/PRODUCT-BOUNDARY.md` specifies the same object as the *capability record* crossing the factory/runtime boundary |
| **Potential value** | ⭐ **The best value-to-new-machinery ratio recovered by this pass, and the only recovered idea that is client-facing.** The argument is commercial and it is a good one: *"more autonomous"* does not persuade a client; *"controlled autonomy with proof"* does. The receipt turns the estate's actual strength — Part 1 of `current_vs_proposed.md`, the part **no inbound research pack describes** — into something a client can hold |
| **Affected layer** | Operator/client surface. ⚠ Governed by `C-UI-04`: *nothing on the surface is a new source of truth.* It must be a projection, never a place a number is first stated |
| **Evidence available** | ⭐ **Every section already has a producer.** `contract.py:17-21` (verdict) · `corpus.py` (corpus hash) · `evidence.py:48,68-70` (evidence classes and states) · `runs.py:42` (cost basis) · `board.py:108` (the mission graph and critical path) · `assertions.py` (maturity of every claim). The sibling states the consequence plainly: **"the record is a join, not a new subsystem."** |
| **Uncertainty** | Two, and both are answerable by reading rather than research. (1) ⛔ **§9's specification omits a `limits.unmeasured` section**, which the sibling calls *load-bearing* — *"a capability record that does not say what the corpus failed to exercise invites the runtime to use it outside the envelope it was graded in."* A receipt without it is a marketing document. (2) The *"independent challenge"* section has nothing to populate it: no shadow organization exists, and `C-EV-10`'s `Counterfactual` is deliberately un-renderable beside a real outcome |
| **Research required** | ⛔ **None, and that is the point.** One prior-art check is worth doing before publishing the term — SLSA/in-toto attestations, SBOMs, assurance cases and NIST AI RMF (which the source document itself cites) are the obvious neighbours, and `C-RS-06` plus Wave 0's terminology record are the reason to look before naming |
| **Likely experiment** | Emit a receipt for **one already-completed piece of work** — the client-review readiness gate pass at `docs/evidence/client-review-readiness-2026-09-01/` is the obvious candidate, because its evidence already exists and was rendered-confirmed. Show it to one person who did not do the work and ask what they cannot tell from it |
| **Difficulty** | **Low.** It is a join and a renderer over existing objects. ⚠ The discipline is the hard part, not the code: the receipt must refuse to render a section it cannot populate, exactly as `C-EV-06` makes *"missing"* sayable and `C-GV-03` makes a gate refuse rather than render |

---

## HL-16 · Execution-surface routing — metadata plus a predicate, over machinery that exists

*Added 2026-09-02 by the `.agent-platform` delta pass. Concept id `C-GV-07`.*

| | |
|---|---|
| **Concept** | A task declares what it needs from the machine it runs on — local files, MCP servers, secrets, isolation, whether it may run beside anything, and which paths it writes — and the surface is **chosen** from that declaration. The collision rule is the load-bearing half: two tasks may run at once only if both are read-only, or they hold separate worktrees, or a deterministic lock proves their mutable resources are disjoint |
| **Source** | `.agent-platform/bootstrap/docs/EXECUTION_SURFACE_POLICY.md` (which supplies the exact `execution:` block) · `.agent-platform/PACK_CONFORMANCE.md` rows 4.1–4.3, where the prior session recorded it as **NOT YET** |
| **Potential value** | ⭐ **It is the only mechanism recovered from the pack whose unlock condition is *none*.** Everything else in the delta waits on a certified team, a second connector, or numbers worth looking at. This one schedules work rather than grading it, so the 0-PASS ledger does not gate it — and it is aimed at the operator's actual present cost, which is running many sessions by hand across one checkout |
| **Affected layer** | Scheduling / isolation — `factory/claims.py`, `factory/worktrees.py`, `factory/lanes.py`, `factory/sessions.py`, and the mission task records |
| **Evidence available** | ⭐ **Half of it is already built, and it is the harder half.** `claims.py:200-244` takes `O_CREAT\|O_EXCL` locks verified against the process table; `worktrees.py:38-39` gives each write task its own tree; `lanes.py` groups by **file locality, not the dependency graph** — which is clause 3 of the collision rule, already reasoned out here independently. ⛔ MEASURED absent: `grep -rniE "remote_control\|cloud_web\|preferred_surface\|execution_surface" factory/ scripts/ blueprints/ missions/ \| wc -l` → **0** |
| **Uncertainty** | Two. (1) ⚠ **`GAP-38`** — the Claude Code argv surface is undocumented, unversioned and unpinned (`factory/provider.py` exists to contain that blast radius); a router that hard-codes surface flags inherits it, so the installed CLI must be interrogated at runtime. (2) ⛔ **Who writes `writes:`?** A hand-typed path list that nothing checks is `C-GV-04` — a spec field nothing reads — which is the defect this estate has now recorded four times |
| **Research required** | **None to start.** `RB-22` exists as a prior-art candidate and is explicitly marked *experiment first*, because the experiment below is cheaper than the survey and could retire it |
| **Likely experiment** | Attach the `execution:` block to the **five tasks of `missions/client-review-v1`** and write one `can_run_together(a, b)` predicate over the three clauses. Run it retrospectively against the last week of parallel lanes and count the disagreements. No scheduler, no dispatch, no new module |
| **Difficulty** | **Low for the experiment; medium to make `writes:` derived rather than typed** — which is the same hard half as `HL-01`'s declared scope, and for the same reason |

---

## HL-17 · The capability record — two fields on four rows that already exist

*Added 2026-09-02 by the `.agent-platform` delta pass. Concept id `C-AG-16`.*

| | |
|---|---|
| **Concept** | A capability claim carries the envelope it was measured in — task family, conditions, evidence count and refs, success and regression history, cost, latency, and a **validity window** after which the claim expires |
| **Source** | `.agent-platform/bootstrap/schemas/capability-record.schema.json` (11 properties, 3 required) · `docs/PLATFORM_COMPLETION_FEATURES.md`. ⭐ Independently, `agent-army-research/repo-boundary/PRODUCT-BOUNDARY.md` specifies the same object as the record crossing the factory/runtime boundary — the second independent arrival, which is why `HL-15` and this entry are siblings |
| **Potential value** | ⭐ **It is the completion of an argument `registry.py` already makes.** That module states *"the version of a workflow is the hash of its text"*, because a `SKILL.md` edited between two runs is a different workflow and a certification must not silently transfer. The record generalises that from the **artifact** to the **conditions** — the part a hash cannot express |
| **Affected layer** | `factory/registry.py` (extend, never parallel), joined to `factory/certify.py` |
| **Evidence available** | `registry.py` carries `id/kind/shapes/layers/ends_at/state/evidence` plus a text-hash version, and `unproven()` already returns **4 of 9 workflows never run on real work**. ⛔ It carries none of `conditions`, `success_rate`, `evidence_count`, `cost`, `latency`, `valid_from`, `valid_until`. `grep -rniE "capability_record\|CapabilityRecord" factory/` → 0 |
| **Uncertainty** | ⚠ **Do not reinvent discovery.** A2A Agent Cards already standardise identity, skills and security requirements; the differentiated layer here is the *evidence envelope*, not the vocabulary. That question is now `RB-20`'s, and it is unanswered |
| **Research required** | `RB-20` for the A2A boundary; `RB-23` for the record itself. Neither is dispatched |
| **Likely experiment** | Add `conditions` and `valid_until` to the **four rows `unproven()` already returns**, then assert in a test that a row whose window has closed cannot be reported as coverage. The rows exist; the assertion *is* the experiment |
| **Difficulty** | **Low as an experiment.** ⛔ **But gated:** `.data/runs.jsonl` holds 10 rows and **0 PASS**, so there is nothing certified to describe. Sequence it behind `GAP-09` |

---

## Cross-cutting observations

> ⓘ **Amended again 2026-09-02** by the `.agent-platform` delta pass. `HL-16` and `HL-17` were
> added. ⭐ **`HL-16` is now the only entry in this file whose unlock condition is *none* and whose
> experiment needs no new module** — observation 4 below still holds (the highest-value action is
> a measurement, not a concept), but `HL-16` is the cheapest *concept* here and it is the first
> one that does not wait on `GAP-09`. `HL-17` is the opposite: low difficulty, hard gate, and it
> belongs behind `GAP-09` with `HL-06` and `HL-07`. Nothing below was rewritten, and the
> observations still count fourteen because they were written about fourteen.

> ⓘ **Amended 2026-09-02.** `HL-15` was added; **`HL-09` should now be read against
> `concept_index.yaml` `C-OR-04`**, whose source has been read and which supplies the twelve
> concrete topologies `HL-09`'s "councils, guilds, federations, markets" was gesturing at. Nothing
> below was rewritten, and the observations still count fourteen because they were written about
> fourteen.

**1. Six of the fourteen need no research at all.**
HL-01, HL-03, HL-04, HL-10, HL-11 and HL-13 are decisions or small mechanisms. Their sources are
already read; what is missing is a choice. Dispatching research against them would be this corpus's
characteristic failure — buying an answer to a question that reading would settle.

**2. HL-08 sits underneath five others.**
Meta-tool extraction, phenotype measurement, communication-defect attribution, credit assignment and
replay are all blocked on a structured trajectory object, and **none of the five says so**. If
anything here is a keystone, it is this — and its open question (adopt OpenTelemetry GenAI
conventions, or define a local shape) is the best-scoped research mission in the corpus, because the
answer is a standard to accept or reject rather than an architecture to invent.

**3. Two entries are cheap tests of the corpus's biggest unresolved question.**
HL-06 and HL-07 both come from its most speculative pack, and both are testable against evidence
this repository holds or could hold within one or two real runs. ⭐ **HL-07 in particular reframes
the multi-agent question usefully:** instead of *"should we build a supervisor tier"* — deferred
behind an unmet gate — it asks *"do two configurations of the same agent fail on the same things?"*,
which needs two runs rather than an organizational architecture.

**4. The highest-value single action is not on this list, because it is not a concept.**
Scoring a second connector (HL-02) and completing one real run (GAP-09) between them would convert
perhaps a dozen entries from arguments into measurements. Every uncertainty column above would
shrink.

**5. What is deliberately absent from this file.**
No ranking. No recommended order. No elimination of anything. Several concepts in
`concept_index.yaml` that are more ambitious than these — the Viable Cognitive Entity, morphological
cognition, stigmergic coordination, the spatial command language — are **not here and are not
dismissed**. They are preserved in the index with their sources intact, and their absence from this
file means only that no cheap test of them was identified, not that they are worth less.
