# Contradictions — meaningful disagreements, presented with the evidence on each side

**Generated 2026-09-02** against `agent-factory` @ `fc78074`.

⛔ **NOTHING HERE IS RESOLVED.** Where the corpus has already recorded a resolution, that resolution
is quoted and attributed; where it has not, both sides are stated and the entry ends with what would
settle it. Resolving these is the job of the architecture synthesis that follows this pass, not of
this pass.

The corpus's own rule governs the format: *"where a new answer disagrees with an earlier one, or
with something already built, record the disagreement and which evidence is stronger. **Do not
average them.**"* — `docs/research/README.md` §3.

**29 contradictions are recorded.** They are ordered by how much they would change a design
decision, not by area.

> ⓘ **Amended 2026-09-02** by a narrow supplementary coverage pass. **CN-29 was added**; **CN-01 was
> amended with a dated note explaining why its balance did NOT change** despite two newly-read
> documents arguing its Side A. **No entry was resolved, split, merged or removed**, and no other
> entry was edited. Everything below the CN-01 amendment is as generated on 2026-09-02 by the
> original pass.

---

## Severity key

| | Means |
|---|---|
| ⛔ **BLOCKING** | A design decision cannot be taken correctly until this is settled |
| ⚠ **MATERIAL** | Would change what gets built, or in what order |
| ○ **RECORDED** | Real disagreement, low immediate consequence |

---

# Part 1 — Architecture and hierarchy

## CN-01 ⛔ Is the organizational-compiler category open, and should this estate build in it?

**Side A — build it.** `.agent-platform/bootstrap/VISION.md`, the six copies of
`Agent Factory Vision.txt`, `docs/research/sources/chatgpt-five-primitives-and-the-organization-compiler.md`,
and `docs/raw_research/agent-factory-bootstrap-pack/` all propose an Organization Factory / Org-IR /
Collective Cognition Fabric / Evolution Chamber as the north star. The vision document is explicit
that Agent Factory is *"one subsystem"* of *"an operating system for synthetic organizations."*

**Side B — the category is occupied and the novelty claim is refuted.**
`.agent-platform/RECONCILIATION.md` §1.1, citing the sibling repository's Wave 0 synthesis
(dated 2026-08-30, one day before the pack was installed):

> Artificial Organization Engineering **is** organisation-oriented MAS, which has a metamodel
> (Moise+), a runtime (JaCaMo) and a textbook; the category name is taken twice in 2026
> (`arXiv:2602.13275` Waites; **`arXiv:2607.25446` IMACS, which *is* the organizational-compiler
> thesis**, published five weeks before); and the surviving novelty claim is refuted on all four
> components. **Disposition on that category: `RESEARCH ONLY` / `DO NOT BUILD`.**

**Evidence weight:** Side B is a completed research wave citing primary sources and was verified
against them. Side A is a model-generated vision document with no prior-art check. **Side B is
stronger, and the corpus already acts on it.**

**But note what Side B does NOT say.** It refutes the *category framing* and the *novelty claim*, not
the *mechanism*. `RECONCILIATION.md`'s own conclusion: *"the pack's category framing is dead and its
engineering patterns are live. Mine it for mechanisms; do not adopt its programme."*

**What would settle the remainder:** a prior-art read of Moise+/JaCaMo and IMACS asking not
*"is this novel"* but *"what does the existing art already give us, and what is genuinely missing
for OUR workload."* No pass has done this. → `research_gap_candidates.md` GAP-02.

---

#### ⓘ AMENDED 2026-09-02 — CN-01's balance is UNCHANGED, and here is exactly why

The supplementary pass converted and read the two `.docx` that GAP-01 named, both of which argue
Side A at length. **They do not move CN-01, and the reason is worth stating precisely rather than
leaving the reader to assume the new documents were simply ignored.**

1. **They add volume to Side A, not evidence.** `Beyond_Agent_Armies_Frontier_Architectures.docx`
   and `Agent_Factory_Frontier_Architecture_Prioritization_Pack.docx` (both dated 2026-09-01) cite
   **one** internal input between them: `Agent Factory Vision.txt` — the file `duplicate_clusters.md`
   measures at **six byte-identical copies**. Neither cites the sibling repository, the Wave 0
   synthesis, or `RECONCILIATION.md`. **They develop the premise Wave 0 refuted, two days after the
   refutation, without knowledge of it.** `C-RS-06` governs: repeated AI claims are not independent
   evidence, and a more elaborate statement of an unevidenced position is still unevidenced.
2. **Side A is now better characterised, which is a real gain.** Before this pass, Side A was a
   vision document. It is now a vision document *plus* a twelve-card architecture catalog with
   stated failure modes and smallest-useful-experiments, *plus* a prioritisation with a declared
   method. That does not make Side A stronger, but it makes Side A **arguable**, and an architecture
   synthesis can now engage with a specific proposal rather than a direction.
3. ⭐ **The genuinely new fact is that the two sides AGREE on what to do next.** Wave 0's conclusion
   is that *"every surviving column entry is about evidence, verification or governance — not one is
   about organizational structure"* (`R01:934`). **Four of the Prioritization Pack's five P0 items
   are exactly that**: constitutional type system (governance), shadow twin (verification), bounded
   reconciliation (governance), global workspace (evidence propagation). Only the mission hypergraph
   is structural. The two documents also, independently, produce **the same promotion-gate chain**
   (Pack §12 G0–G7; sibling `architecture/11`). See `agent_army_wave0_supplement.md` §3.3–§3.4.
4. ⚠ **Do not upgrade that agreement to corroboration.** Both were produced by language models over
   overlapping training distributions. What is independent is the *input corpus*, not the reasoner.
   Basis: `DERIVED`, medium confidence.

**Net effect on CN-01: still OPEN, Side B still stronger, and the remainder still needs GAP-02.**
What changed is that the practical disagreement has narrowed to almost nothing — **both sides now
say build the mechanism and do not claim the category** — while the *evidential* disagreement is
untouched. The Prioritization Pack §11 even asks for the work Wave 0 already did: *"client-facing
novelty claims around holarchies, markets, stigmergy or evolution [should wait] until prior-art
research has classified what is actually new."*

---

## CN-02 ⛔ Where should this estate start — Rank 2 or Rank 4?

**Side A — start at Rank 4.** `.agent-platform/bootstrap/ROADMAP_TO_VISION.md` and
`BUILD_START_TO_FINISH.md` sequence the work so that the Communication Mesh, Collective Cognition,
Mission Assembly and the Venture Loop come next.

**Side B — finish Rank 2 first.** `README.md`'s absence table gates each of those behind a named
precondition, and `.agent-platform/RECONCILIATION.md` §1.2 measures the precondition as **unmet**:

> `.data/runs.jsonl` holds 10 rows, 0 `PASS`; `.data/events.jsonl` holds 8 runs with `PASS=0`; all 7
> `agent_returned` events carry `dry_run=True`. **No agent has ever been dispatched for real by this
> system.**

**RE-MEASURED for this pass, 2026-09-02 — unchanged:** `runs.jsonl` 10 rows
(`FINISHED`×3, `FAIL`×1, `UNMEASURABLE`×6, **zero `PASS`**); `events.jsonl` 61 events, verdicts
`FAIL`×2, `UNMEASURABLE`×12, `NOT_RUN`×1; 7 `agent_returned`, all `dry_run=True`.

**Evidence weight:** Side B is measured from this repository's own ledgers with a stated command.
Side A is an imported roadmap written without access to the repository. **Side B is stronger.**

**Open:** the pack's rank ladder and README's absence table encode the *same discipline* in
different shapes. Neither cites the other and no document compares them. Which representation is
better is a real open question.

---

## CN-03 ⛔ Build a knowledge fabric, or retire a store first?

**Side A — build the fabric.** Five sources propose shared organizational memory:
`.agent-platform/bootstrap/docs/COLLECTIVE_COGNITION.md`,
`agent_factory_rd_consolidation_pack/03_HYPERMESH_ARCHITECTURE.md`,
`agent-factory-bootstrap-pack/…/FEATURE_INTEGRATION_SEEDS.md` §5,
`agent_factory_army_ui_concept_pack/09_INTELLIGENCE_KNOWLEDGE_MEMORY.md`,
`agent2_sihre_consolidation_pack` (Agent KG Mesh).

**Side B — there are already too many stores.** `docs/research/answers/R10-…` §7:

> *"We already have **six** overlapping stores… adding a seventh would be a mistake… retire or merge
> at least one."*

`docs/absorption-backlog.md` AB-13 makes it an action: enumerate the six, retire or merge one,
**before any new store lands** — and observes that *"we have since been designing new stores against
a recommendation to reduce them."*

**Side C — ask a different question first.** `docs/research/R06B-…` (written 2026-08-31, **never
dispatched**) measures **nine** stores and asks what, specifically and measurably, **none of them
can do** — requiring every candidate view to *beat the null*.

**Side D — the one thing actually built refuses the mechanism.** `factory/preflight.py` and
`docs/protocol/KNOWN_FAILURE_PREFLIGHT.md`: *"matching is deterministic key lookup — ⛔ no retrieval,
no similarity."* `docs/protocol/README.md` forbids the pack becoming *"a knowledge store, embedding
index or retrieval layer."*

**Evidence weight:** Side A is five non-independent AI documents (see `duplicate_clusters.md`
DC-01). Side B is measured, though R10's own numbers are flagged unverified. Side D is running code.
**Sides B and D are stronger. Side C is the pass that would settle it and it has never been sent.**

⚠ **Note the store count disagrees with itself: R10 says six, R06B says nine, eight days later.**
Neither enumerates them in a form the other can be checked against.

**What would settle it:** dispatch R06B. → `research/backlog.yaml` RB-03.

---

## CN-04 ⚠ Should readiness be raised before deployment?

**Side A — yes, READY-UP.**
`agent_factory_agents_as_configuration_research_pack/02_CONCEPTS/MISSION_READINESS_AND_READY_UP.md`
proposes mission conditioning: bounded interventions that raise an agent's readiness for a specific
mission before it starts. `agent-factory-bootstrap-pack/…/FEATURE_INTEGRATION_SEEDS.md` §3 agrees,
adding that a *mission-specific delta* is preferable to blind maximisation.

**Side B — no, that corrupts the instrument.**
`agent-config-research-pack/00-executive-assessment.md`, under *"Ideas that should not be implemented
literally"*:

> **Artificially increasing all health scores before deployment.** This corrupts the instrument. The
> system may improve readiness and forecast uplift, but **health moves only after measurement.**

**Evidence weight:** Side B is the only inbound pack that read the repository, and its objection is
the same principle `factory/metrics.py` enforces in code (`GoodhartViolation`). Side A's own sources
partly agree — the "bounded" and "mission-specific delta" framing is a narrower claim than "raise the
scores".

**These may be reconcilable.** *Recommending* an uplift and *forecasting* its effect is compatible
with health only moving on measurement. Side B's own six-step sequence includes *"pre-deployment
readiness uplift in **recommend-only** mode."* Nothing in the corpus states this reconciliation.

---

## CN-05 ⚠ Is the isolation ladder the right control?

**Side A — yes, and it is the load-bearing idea.** `docs/specs/architecture-v0.md` §4: an agent's
isolation tier is chosen by what its task touches. *"'Do not touch prod' in a prompt is a request; a
role with no grant on prod is a control."*

**Side B — a container does not defend against the actual threat.**
`docs/research/answers/R16-outside-evidence-lane.md` §3: an allowlist without network isolation is
not isolation, and **a container does nothing about prompt injection — the lethal trifecta survives
it intact.** `absorption-backlog.md` AB-09: SYNTHESIS §13.7 adopted a sandbox move *partly on
isolation grounds*; if the sandbox does not address the actual threat, the justification is wrong
even if the move is right.

**Side C — the clone is a compromised oracle.**
`docs/research/answers/R17-…` §16.3: the ephemeral clone sits *"at exactly the layer our evidence
rule exists to protect"* — validating against a clone is not validating at the consumer's layer.

**Side D — architecture-v0 says so itself.** Its §7.1 lists this as the first way it may be wrong:
if a zero-copy clone is not actually cheap to validate against, *"§4 collapses and the ceiling stays
at 3."* §7.2 adds that *"data work does not conflict"* is **asserted, not measured**.

**Evidence weight:** Sides B and C are external evidence and an internal audit. Side D is the
proposal conceding the point in advance. **The tier idea survives; the specific claims about what a
container buys and what a clone can certify do not.**

**What would settle it:** a T1 container on Windows/WSL with a measured start-up cost, and a T2
clone with a measured validation cost. Neither exists. → `research/backlog.yaml` RB-06.

---

# Part 2 — Terminology

## CN-06 ⚠ Four incompatible basis vocabularies

| Vocabulary | Where | Used for |
|---|---|---|
| `MEASURED` / `DERIVED` / `ASSUMED` | `factory/tasks.py:137` | evidence rows |
| `MEASURED` / `DERIVED` / `REASONED` / `BET` | `docs/specs/architecture-v0.md` | design claims |
| `OBSERVED` / `DOCUMENTED` / `MARKETED` | `R8` §7, `R17` §3 | external claims |
| `RECORDED` / `RECONSTRUCTED` / `NOT-RECORDED` | `factory/runs.py:42` | run provenance |

Plus a fifth family in the evidence documents: `CONTRADICTORY` / `NOT_RECORDED` /
`REQUIRES_CLIENT_DECISION` / `REQUIRES_TECHNICAL_VERIFICATION`
(`docs/evidence/marketing-model-v1/D1-…`).

⭐ **And a sixth, which is the most developed of them and is enforced in code:**
`factory/assertions.py` defines eight bases — `MEASURED` / `DERIVED` / `DOCUMENTED` / `INFERRED` /
`ESTIMATED` / `SIMULATED` / `NOT_RECORDED` / `CONTRADICTORY` — where `DOCUMENTED` is explicitly
*one hop, and the hop is the point*, and `NOT_RECORDED` is explicitly *"NOT zero"*. It is a superset
of three of the five above and could plausibly serve as the crosswalk, but nothing declares it as
one, and it is scoped to one artifact type.

**No document maps any of these onto any other**, except `SYNTHESIS.md` §16.12, which maps R17's
tiers onto the estate's — the only crosswalk that exists.

**Consequence:** a claim labelled `DERIVED` in one document and `DOCUMENTED` in another cannot be
compared, and an automated audit cannot roll them up. **Recorded, not resolved.**

---

## CN-07 ⚠ "Handoff" names three different things

| Meaning | Where |
|---|---|
| A prose lane/session note generated from measured state | `factory/handoff.py` |
| A typed message contract with an envelope and ACK states | `docs/protocol/HANDOFF_CONTRACT.schema.json` |
| A research-to-implementation graduation | `docs/agent-army/IMPLEMENTATION_HANDOFFS.md` |

`docs/protocol/README.md` recognises the collision and forbids one merger explicitly:

> ⛔ A `HandoffContract` class inside `factory/handoff.py` — that module generates prose lane and
> session notes and is **a different concept wearing the same word**.

**The prohibition is a mitigation, not a resolution.** Nothing renames anything, and a fourth usage
(`handoff.preflight()`) already exists.

⚠ A parallel collision was actually merged and cost real time: **`sessions`**. `factory/sessions.py`
(live CLI processes) and `factory/workplan.py`'s work-sessions *"were written independently on
separate lanes and both were called `sessions`; git reported the collision only as an add/add
conflict."*

---

## CN-08 ⚠ Five verdicts in the enum, six in effective use, and `Unmeasurable` defined three times

`docs/agent-army/CURRENT_STATE.md`, verbatim:

> ⚠ **Five in the enum, six in effective use:** `REFUSED` (`evaluator_service/service.py:62`) is a
> verdict to the client — `UNSCORED_VERDICTS` (`factory/evaluator.py:65`) — but is not a `Verdict`
> member; it is the *service* refusing to score, not an assertion outcome, so the separation may be
> correct. And **`Unmeasurable` is still defined three separate times, with three different
> docstrings**, at `contract.py`, `readiness.py:42` and `schedule.py:54` — **unresolved.**

This one matters more than an ordinary naming collision, because the whole system's founding claim is
that two kinds of not-knowing must never be collapsed — and the exception class expressing that is
defined three times with three different meanings.

---

## CN-09 ○ "Mission" is used for four different things

Mission as a scoped delivery unit (`missions/client-review-v1/`, `docs/specs/marketing-model-reconstruction-v1.md`);
mission as an operation in the army vocabulary (`agent_factory_army_ui_concept_pack`); mission as the
compilation input to Org-IR (`FEATURE_INTEGRATION_SEEDS.md` §1); mission as a research pass
(`research missions RUX-01..13`).

`docs/agent-army/CURRENT_STATE.md` measures the product meaning as **NOT IMPLEMENTED**: *"No mission
object, schema or lifecycle anywhere. The word appears in this codebase only inside `submission` and
`PermissionError`."* Meanwhile `missions/` exists on disk as a directory of documents. **Both are
true**, and the ambiguity is between "a directory of mission documents" and "a mission object".

---

# Part 3 — Protocols and schemas

## CN-10 ⚠ Five message kinds (built) versus six message types (designed)

`docs/agent-communication.md` + `factory/bus.py`: five kinds — `correction`, `claimed`, `blocked`,
`finished`, `note` — rejected at `bus.py:74` if not in the set. **Running.**

`docs/protocol/AGENT_COMMUNICATION_PROTOCOL.md`: six message types, four boundary moments, six ACK
states. **⛔ "Nothing here is built."**

Nothing maps the five onto the six. The design was written for the *deferred* agent-to-agent case,
while the built five serve lane-to-lane nudges between human-launched sessions. **They are for
different layers and share a vocabulary space.**

---

## CN-11 ⚠ Was the record/channel question answered, and by whom?

`docs/absorption-backlog.md` AB-14:

> R8 §2 answered the record/channel question with *"event sourcing… like CQRS"*. §16.10 refutes it as
> **"neither"** — but presents the question as one *"asked in session"*, **never recording that a
> pass had already answered it wrongly.**
>
> **Consequence:** the record does not show that a research pass got this wrong, so the same wrong
> answer can arrive again from the same source.

**Unresolved.** The action — file the refutation against R8 explicitly — has not been taken.

---

## CN-12 ○ Does `Task` need a `depends_on` field?

`docs/protocol/README.md`: ⛔ *"A `depends_on` field on `Task`. `block()` is the edge, and it is live
(25 events)."*
`docs/findings.d/F98`: the DAG field was surveyed as *"exists and is unused"* and **now carries 25
block edges** — status `SUPERSEDED`.

**Effectively resolved** by measurement, and recorded here because the survey that called it unused
is still in the corpus.

---

# Part 4 — Implementation plans and priorities

## CN-13 ⛔ The alerting question has five positions and was decided on two

`docs/absorption-backlog.md` AB-19, verbatim:

| Position | Source |
|---|---|
| Fatigue is real; alert only on the actionable | **R6 §4** |
| Absence, not fatigue; it must interrupt | R12 §4.2 / R13 §6 |
| Measure whether it fired at all, first | R13 run 2 §3 |
| The inverted-U: *"escalating everything is strictly worse than the optimum"* | R16 outside §2 |
| The same paper, independently | R17 |

> §14.3 records the middle pair as *"three passes and one measurement agree — stop asking and build
> it"*; §15.5 then **retracts the independence**. **R6's position — filed first, and on the same side
> as the strongest external finding — is nowhere.** Two sources agreed and were counted; the two
> agreeing with the inverted-U were not.

**Action recorded and not taken:** re-decide with all five positions on the table, and record the
decision **with its dissent**.

---

## CN-14 ⛔ A settled platform decision may rest on a refuted premise

`docs/research/answers/R13-answer-architecture-and-ui-survey-run2.md` found that **APPROVE leaves the
building and becomes a GitHub PR**.

`docs/absorption-backlog.md` AB-12: *"the APPROVE finding removes the very plane §14.2's platform
argument was justifying. A settled platform question may rest on a premise a later pass refuted."*

**Five of R13 run 2's six findings were never taken.** The APPROVE one is named as the first to
action, *"because a decision depends on it."* **Not done.**

---

## CN-15 ⚠ Two whole research answers were never absorbed or rejected

`SYNTHESIS.md` §17.2 on R14: *"1,389 lines, seven mentions, and not one conclusion taken."*
§17.3 on R18: *"it exists, and every reference to it here is in the future tense."*

`absorption-backlog.md` AB-16/AB-17: read it and either absorb its conclusions **or reject it in
writing**. Either closes it; **neither has happened.**

**191 KB of research** — including the only internal audit with `path:line` citations — is in the
corpus with no disposition. This is a contradiction between the corpus's own rule (*a written
rejection closes a row; silence does not*) and its state.

---

## CN-16 ⚠ Is the eval corpus a sensitivity problem or a breadth problem?

**Earlier position:** four passes (R1 ≥29, R3 30+10, R8, R10) asked for a much larger corpus, and
`absorption-backlog.md` AB-04 originally inherited the premise that one file meant *"the instrument
has not been shown able to fail."*

**Correction:** `docs/findings.d/F76` — **that premise is false.** All twelve assertions are
calibrated with a known-bad, enforced by
`test_every_assertion_has_been_proved_able_to_fail`, and `certify --calibrate` returns `PASS
(PASS=12)`. AB-04 was restated in place: *"this is a breadth task, not a sensitivity task."*

**What remains:** the contract has been replayed against **one** connector; **48 have never been
scored**. Sensitivity is not coverage.

**Recorded as a contradiction because the corrected and uncorrected forms both still circulate** —
`README.md` carries the correction, `docs/artifacts/agent-factory.html` still renders the
`UNMEASURABLE (PASS=11)` era, and the *published* artifact carries the old numbers too.

---

## CN-17 ⚠ Does this repository stay separate, or become one platform monorepo?

**Side A — one platform monorepo.** `Agent Factory Vision.txt` §1: *"one platform monorepo for the
Agent Factory/Army operating system + federated external repositories that the Factory manages"*,
with Agent Factory absorbed as a subsystem.

**Side B — it stays separate, for stated reasons.** `docs/specs/product-end-state.md` §2 explains why
`agent-factory` exists separately from the delivery estate. `docs/DEEP-REVIEW-PROMPT.md` §4b records
*a stated direction to decouple from `aldc-launchpad`*, treated as a design constraint — i.e.
movement in the opposite direction. `docs/agent-army/RESEARCH_REPO.md` rule 5: *"never
auto-synchronise the two directories — they have different truth semantics."*

**Evidence weight:** Side B is a set of decisions with reasons attached. Side A is a proposal with no
prior-art or cost analysis. **Unresolved**, and it is a real architecture question a synthesis must
take.

---

# Part 5 — Metrics

## CN-18 ⚠ Composite health scores: build them or refuse them?

**Side A.** `agent-config-research-pack/04-team-metrics-and-formulas.md` (agent health, team health,
struggle score, communication effectiveness), `army_ui_concept_pack/12_…` (army health with
hierarchical aggregation), `agents_as_configuration_research_pack` (Agent Health Vector).

**Side B.** `docs/protocol/METRICS.md` reports **eight of its ten metrics NOT-RECORDED or
NOT-MEASURABLE**, refuses to publish a rate over an empty population, and flags any zero from an
unproven instrument. `FEATURE_INTEGRATION_SEEDS.md` §2 — from Side A's own family — agrees:
*"Health must not become a single opaque score without decomposition."*

**Partially self-resolving:** every source that proposes composite health also warns against
collapsing it. The real disagreement is about **sequencing**: build the metric set now, or wait until
there is data.

---

## CN-19 ⛔ MER is defined as the reciprocal of what the code computes

`docs/findings.d/F97` (**OPEN**, `KIND: DESIGN`): *"the document that locks MER defines it as the
reciprocal of what three code layers compute"*, and *"the document also disagrees with itself."*

A locked metric definition contradicting three code layers is the sharpest terminology contradiction
in the corpus, because both the document and the code are live.

---

## CN-20 ○ Which figure supports the multi-agent decision?

`blueprints/orchestrator_team.yaml:18` states the **−3.5% mean without its interval**.
`docs/research/answers/R2-…:15` carries the interval: **−18.6% to +25.7%** — spanning zero.

`docs/agent-army/CURRENT_STATE.md` states the resolution plainly:

> A mean whose confidence interval spans zero is **not** evidence that multi-agent coordination hurts
> on average. **The decision to reject the three-agent blueprint still stands, but not on the
> −3.5%.** It stands on the sequential-task degradation and on our own measured failures, which were
> all at seams.

⛔ **The blueprint header was deliberately NOT edited** — it is a product artefact and a historical
record — so the uncorrected figure is still in the repository and still quotable.

---

# Part 6 — Autonomy boundaries

## CN-21 ⚠ `needs_paul` — a gate or a label?

`docs/protocol/QUALITY_GATES.md`: *"`needs_paul` on `Lane` and `Preset` is **display-only** today: it
renders, it does not refuse. A gate built on it would be a declaration without a mechanism — the
family this estate has recorded three times."*

Meanwhile `docs/specs/architecture-v0.md` §5 lists `needs_human: [credential-grant, merge, promote]`
as a field of the `AgentSpec`, and `factory/operator.py` treats declared blockers as real.

**The contradiction is between the field's intent and its enforcement**, and the corpus names it as
an instance of a recurring class (see `concept_index.yaml` C-GV-04, four findings).

---

## CN-22 ⚠ Who has solved non-engineer approval?

`SYNTHESIS.md` §14.4: *"The non-engineer approval question — answered, and the answer is 'nobody
has'."*

Against: `agent_factory_army_ui_concept_pack` (Command Authorization, Rules of Engagement),
`.agent-platform/bootstrap/docs/COMMERCIAL_AUTONOMY_POLICY.md`, and
`docs/protocol/CLIENT_WOW_FEATURES.md` all design client- or non-engineer-facing approval surfaces.

**Not a direct contradiction** — the packs design a surface, the synthesis reports that nobody has
*solved* it — but a reader could easily take the pack material as a solved pattern. **Recorded so
they cannot.**

---

## CN-23 ○ Is autonomy a ladder or a set of switches?

Ladder: `.agent-platform/bootstrap/docs/AUTONOMY_LADDER.md`, `ROADMAP_TO_VISION.md` — ordered ranks
with promotion rules.
Switches: `docs/research/answers/R7-…` — five named auto-actions, each refuse-by-default,
individually enabled.

A ladder implies a single ordering of trust; switches imply independent grants. The corpus never
compares them.

---

# Part 7 — UI

## CN-24 ⚠ Build the UI now, or wait for numbers worth looking at?

`README.md`: Platform UI is deliberately absent, unlocked by *"numbers worth looking at."*
`docs/FACTORY-UI-PROMPT.md` §3 agrees and goes further: **"PHASE 0 — build the event ledger. No UI.
This is the real work."**

Against: three inbound packs design the UI in full
(`army_ui_concept_pack`, `chat_design_pack`, `zeus_world_ui_research_pack`), and one arrived as
working code (`zeus-switchboard-redesign-pack`).

**Partially resolved in practice** — the Switchboard shipped (P0 then P1), rendered-validated, as a
projection over existing state. That is neither "no UI" nor the animated world. **Nothing records
that as the decision**, so both sides are still live in the documents.

---

## CN-25 ○ Retire `orchestration-bench.html`?

`R13 run 2` recommends retiring it (`absorption-backlog.md` AB-12). `docs/artifacts/README.md`
carries the recommendation as a ⚠ note. **The file is still there and still listed as published.**

---

# Part 8 — Contradictions the corpus has with itself

## CN-26 ⚠ SYNTHESIS contradicts itself in three places

`SYNTHESIS.md` §17.8: *"Three places this document contradicts itself, and one count that drifted."*
Left visible rather than smoothed — which is the right handling, and is recorded here so a reader
does not treat the document as internally consistent.

## CN-27 ⚠ Seven sentences say an answer has not landed. All seven are false.

`SYNTHESIS.md` §17.1. The decision record was wrong about its own coverage in seven places, found by
auditing itself against `answers/`. **The instruments that were supposed to catch this
(`unsynthesised()`, `dispatch`) both passed** — see `docs/findings.d/F75`: they detect *unmentioned*,
not *unabsorbed*, and mentioning an answer satisfies them.

## CN-28 ⚠ `docs/specs/client-review-loop-v0.md` says NOT STARTED; the code is built and tested

The spec's title is *"Client Review Loop V0 — queued capability, not started"*.
`factory/client_review.py` (1,191 lines), `factory/client_review_render.py` (704 lines),
`tests/test_client_review.py` and `tests/test_client_review_readiness.py` all exist, and
`docs/evidence/client-review-readiness-2026-09-01/` records a rendered-confirmed gate pass.

**The spec is behind the code.** Per `docs/agent-army/RESEARCH_REPO.md`'s hierarchy — *code beats
specification* — the code is right and the spec needs updating. Recorded, not edited.

---

# Part 9 — Opened 2026-09-02 by the supplementary coverage pass

*One new contradiction, and it is the only one this pass opened. It could not have been found
before, because it needs both a document that was unreadable and a repository that was unindexed.*

## CN-29 ⛔ Is an organizational design a durable asset, or does it expire with the model binding?

**Side A — organizational designs are assets you accumulate.**
`docs/raw_research/converted/Agent_Factory_Frontier_Architecture_Prioritization_Pack.md` §5 assigns
each of twelve architectures **one** planning-value score (`4.75/5`, `4.20/5`, `2.90/5`, …) with no
model dimension anywhere in its seven weighted criteria. §6.11 and Phase F then propose org-genome
search whose output is *"certified versions"* clients consume, and §8 calls the result a
*"potential long-term moat: the Factory learns which organization is best for each mission family
instead of shipping static handcrafted teams."* `C-OR-08` (quality-diversity archive) is the same
premise: elites accumulate.

**Side B — the winning configuration flips across model families, so every learned result expires.**
The sibling repository's Wave 0 synthesis, `research/synthesis/W0-foundations.md:63-65`, from the
**IMACS** ablation (`arXiv:2607.25446`, verified by the sibling's own citation-audit pass):

> Nine ontology terms are **structural** (binding-independent); four are **configurational** and must
> carry a model `binding`, because *"the winning placement flips across model families."*
> **Organizational design cannot be hard-coded.**

`research/HYPOTHESIS_LEDGER.md` records the consequence as the sting on H07:

> H07 *Evolution discovers better topologies than manual templates* — **SUPPORTED**, but *"every
> learned result is **model-binding-specific and expires with the binding**."*
> H09 *Organizational configuration must be re-validated per model binding* — **SUPPORTED**.

**Evidence weight.** Side B cites a published ablation and is recorded as SUPPORTED in a hypothesis
ledger. Side A is a scoring table its own §4 declares *"directional planning judgments, not measured
ROI"*. ⭐ **Side B is stronger, and Side A does not know Side B exists** — the Prioritization Pack
cites no sibling-repository material (see the CN-01 amendment above).

**⛔ Why this is BLOCKING rather than MATERIAL.** It does not argue against building any of the
twelve architectures. It argues that **the output of Phase F has a shelf life nobody has measured**,
and therefore that:

- a portfolio scorecard with no binding dimension is under-specified, not merely imprecise;
- a quality-diversity archive may be curating **elites that have already expired**;
- `C-AG-01` (*the configuration IS the version*) already implies the model is part of the
  configuration — so this estate's own vocabulary is on Side B while its inbound roadmap is on Side A;
- and the sequencing changes: **re-validation cadence is a prerequisite of the archive, not a
  follow-up to it.**

**What would settle it.** ⭐ The experiment is already written and unrun — **E3** in
`research/synthesis/W0-foundations.md:231`:

> *"Configuration flips across model bindings in our estate. Baseline: one task class, one topology.
> Re-run the same team spec across ≥2 model families; does the winner flip? **Stop condition:** if it
> does not flip in 2 families, IMACS may not generalise here."*

⚠ E3 is blocked behind the same precondition as everything else: `GAP-09` / `RB-00C` — **no agent has
ever completed a real run**, so there is no winner to flip. **This contradiction cannot be settled
before one real run exists**, which is an argument for `RB-00C`'s priority, not against E3's value.

→ `concept_index.yaml` `C-OR-08`, `C-AG-01`; `research_gap_candidates.md` GAP-14, GAP-09;
`agent_army_wave0_supplement.md` §3.2.

---

## Summary

Severity was read from each entry's own heading marker.

| Severity | Count | IDs |
|---|---|---|
| ⛔ BLOCKING | 7 | CN-01, CN-02, CN-03, CN-13, CN-14, CN-19, **CN-29** |
| ⚠ MATERIAL | 17 | CN-04, CN-05, CN-06, CN-07, CN-08, CN-10, CN-11, CN-15, CN-16, CN-17, CN-18, CN-21, CN-22, CN-24, CN-26, CN-27, CN-28 |
| ○ RECORDED | 5 | CN-09, CN-12, CN-20, CN-23, CN-25 |
| **Total** | **29** | ⓘ was 28; **CN-29 added 2026-09-02**. No existing entry was resolved, split or removed. |

By what disagrees with what:

| Shape | Count | IDs |
|---|---|---|
| An **inbound research pack** against a **measurement taken in this repository** | 9 | CN-01, CN-02, CN-03, CN-04, CN-17, CN-18, CN-22, CN-24, **CN-29** |
| The corpus against **itself**, found by its own audits | 8 | CN-11, CN-13, CN-14, CN-15, CN-16, CN-26, CN-27, CN-28 |
| **Terminology** collisions — one word, several meanings | 5 | CN-06, CN-07, CN-08, CN-09, CN-19 |
| A **specification** against the **code that implements it** | 3 | CN-10, CN-12, CN-21 |
| Two **research passes** against each other | 2 | CN-05, CN-20 |
| A **recommendation** against the **state of the repository** | 2 | CN-23, CN-25 |

**The pattern worth noticing.** In all eight of the first row, the measurement is the stronger
evidence — not once does an inbound pack's claim survive contact with a number taken here. And the
second row is as large as the first: the corpus found as many contradictions **in itself** as exist
between it and the imported material, and recorded them rather than hiding them.

That ratio is the most useful single fact about this corpus's trustworthiness. It is much better at
auditing itself than the inbound material is at describing it — which is also the reason the eight
entries in row one are worth taking seriously rather than treating as a house style of scepticism.

---

## What this file does not contain

- **Resolutions.** Where the corpus has already resolved something, the resolution is quoted and
  attributed. Nothing is resolved here for the first time.
- **Ranked priorities.** Severity marks how much a decision depends on the entry, not what to do
  first.
- ~~**Contradictions inside the two unread `.docx` files.**~~ ✅ **Closed 2026-09-02.** Both were
  converted and read in full. They produced **one** new contradiction (CN-29) and one amendment
  (CN-01). ⚠ **The residual limit is narrower and should be stated:** their **twelve embedded
  figures were not extracted**, so a contradiction expressed only in a diagram would still be
  missing. See [`agent_army_wave0_supplement.md`](agent_army_wave0_supplement.md) §0.1.
- **Contradictions inside the sibling repository's unread 595 KB.** The supplementary pass read the
  Wave 0 *synthesis* and sampled the three Wave 0 *answers*. `R00`, `R02` and the 89 KB vocabulary
  crawl were not read end to end. A disagreement recorded there and not surfaced in the synthesis is
  missing from this file. See [`agent_army_wave0_supplement.md`](agent_army_wave0_supplement.md)
  §0.2 and `research_gap_candidates.md` GAP-03.
