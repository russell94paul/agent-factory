# Research gap candidates

**Generated 2026-09-02** against `agent-factory` @ `fc78074`.
**Amended 2026-09-02** @ `7b19baf` by the `.agent-platform` delta pass — Part 9, `GAP-44` and
`GAP-45`. Nothing existing was rewritten. See
[`agent_platform_delta_synthesis.md`](agent_platform_delta_synthesis.md).

⛔ **NO RESEARCH IS RUN HERE.** This file identifies where the corpus lacks the evidence it would
need, and nothing more. The candidate missions themselves are in
[`docs/research/backlog.yaml`](../research/backlog.yaml); their ordering is in
[`docs/research/dependency_graph.md`](../research/dependency_graph.md).

**A gap is only listed if the corpus does not already answer it.** Two filters were applied, and
both come from the corpus's own rules:

1. **The `DEFERRED` filter.** `docs/research/agent-factory-concept-inventory.md` §1 makes `DEFERRED`
   a first-class verdict precisely so a survey cannot report a deliberate deferral as a gap:
   > *"A survey run without that list in hand will report all ten as gaps, and be wrong ten times."*
   Nothing on `README.md`'s absence table is listed here **as a gap**. Where its *unlock condition*
   has never been tested, that is listed — which is a different thing.
2. **The do-not-re-ask filter.** `concept-inventory` §3 lists what R1–R9 already settled. Re-asking
   *"buys the same answer at full price."*

**42 gaps** — 37 numbered candidates plus 5 poorly-understood dependencies. Priority is `CRITICAL` (a decision is blocked now) / `HIGH` (changes what gets built) /
`MEDIUM` / `EXPLORATORY`.

---

## Part 1 — Gaps in the corpus itself

*Not questions about the world. Things this corpus cannot currently see about its own contents.*

### GAP-01 · ✅ `CLOSED 2026-09-02` (text) · ⚠ `LOW` residual (figures)

~~Two source documents have never been read.~~ **Both were converted and read in full on
2026-09-02** by the supplementary coverage pass.

```
docs/raw_research/Beyond_Agent_Armies_Frontier_Architectures.docx                 430,863 bytes  → converted/…md  46,047 chars
docs/raw_research/Agent_Factory_Frontier_Architecture_Prioritization_Pack.docx    203,671 bytes  → converted/…md  42,261 chars
```

Converter `scripts/docx_to_md.py`; originals preserved byte-for-byte. **Extraction verified, not
assumed** — raw `<w:t>` characters vs markdown stripped of syntax: 38,548 → 38,251 and
32,732 → 32,519, i.e. **100.1% coverage** (the excess is hyperlink targets the markdown adds).

**What it produced:** six new concepts (`C-OR-06`, `C-OR-07`, `C-OR-08`, `C-KN-07`, `C-GV-06`,
`C-TM-06`), one new contradiction (**CN-29**, `BLOCKING`), one amendment to CN-01 explaining why its
balance did **not** change, and one new high-leverage candidate (`HL-15`). Full analysis:
[`agent_army_wave0_supplement.md`](agent_army_wave0_supplement.md) Parts 1 and 3.

⚠ **RESIDUAL, and it is real: twelve embedded figures were not extracted.** `word/media/` holds
**8 PNGs** in the first document and **4** in the second. All twelve captions survive in the
converted text (`Figure 1 — A useful hierarchy above Agent → Team → Army…`, `Figure 8 — Self-hosting
organizational reconciliation loop.`, and so on), so the *subject* of each figure is known and the
*content* is not. Priority `LOW`: the surrounding prose describes each figure's subject, and no
claim in either document appears to rest on a diagram alone. **Anyone consolidating the architecture
should open the two `.docx` in Word and look at the eight figures in the first one** — that is
minutes of work and it is the only part of GAP-01 still open.

---

### GAP-02 · `CRITICAL` · The prior art was used to refute, never to harvest

`.agent-platform/RECONCILIATION.md` §1.1 establishes that organisation-oriented MAS has a metamodel
(**Moise+**), a runtime (**JaCaMo**), a textbook, and that `arXiv:2607.25446` (**IMACS**) *is* the
organizational-compiler thesis. That work refuted the novelty claim and stopped.

**Nobody has asked the useful question:** what do Moise+, JaCaMo and IMACS *already provide*, and
what is genuinely missing for a workload that deploys containers and writes to a warehouse?

⭐ **A refutation that stops at "this is not novel" leaves the strongest available asset unused.**
The prior art is now a resource, not a threat, and no pass has treated it as one.

**Would unblock:** CN-01's remainder; whether `Org-IR` should be designed or adopted; C-OR-02.

---

### GAP-03 · ⚠ `MEDIUM` (was `HIGH`) · The sibling repository is now partly indexed

`agent-army-research` @ `11c5b3d` is the authoritative home of Agent Army research since 2026-08-30
and holds the Wave 0 synthesis that drives CN-01, plus 26 unrun prompts (R20–R45) and 7 research
ADRs. The original pass indexed only this repository.

**⚠ First, a correction to this gap's own figure.** It said *"155 markdown files, 3.6 MB"*. The file
count is right; **the byte figure is not reproducible from any basis**:

```bash
cd ../agent-army-research && python -c "
import pathlib
fs=[p for p in pathlib.Path('.').rglob('*') if p.is_file() and '.git' not in p.parts]
md=[p for p in fs if p.suffix=='.md']
print('working tree', len(fs), sum(p.stat().st_size for p in fs))
print('markdown    ', len(md), sum(p.stat().st_size for p in md))"
# working tree 184 1,882,122
# markdown     155   880,781      ← plus .git = 2,467,147 total. Nothing yields 3.6 MB.
```

**The markdown corpus is 881 KB — about a quarter of the stated size.** That matters because the
figure was used to argue the sibling was too large to index. It is not. *(`C-VD-04`: a count without
its regeneration command, re-rotting exactly as predicted.)*

**✅ Closed 2026-09-02, the architecture-relevant portion.** The supplementary pass read in full the
Wave 0 synthesis, the hypothesis ledger, the research manifest, the core ontology, the foundational
laws, the product boundary, `R31`, and all twelve `architecture/*.md` stubs — and extracted `R01`'s
15-concept novelty-risk map and terminology table. Output:
[`agent_army_wave0_supplement.md`](agent_army_wave0_supplement.md) Part 2, 24 tagged findings
(`W0-1` … `W0-24`) traced to `file:line`. **Independence was checked**: only 4 byte-identical groups
exist in the sibling (`.gitkeep`s and three template pairs), and `legacy/` holds *differing* earlier
editions, not duplicates — so unlike this repository, no conclusion there rests on a reformatted copy.

**⛔ What remains open, and it is 595 KB.** Read by targeted extraction only, not end to end:

| File | Bytes | Read? |
|---|---|---|
| `research/answers/R02-answer-canonical-ontology-and-vocabulary.md` | 137,605 | dispositions only |
| `research/answers/R01-answer-prior-art-and-novelty-boundary.md` | 121,598 | Deliverables 4 and 5 only |
| `research/answers/R00-answer-foundations-of-aoe.md` | 118,355 | PROSA / `StaffFunction` verdicts only |
| `research/sources/agent-factory-vocabulary-crawl.md` | 89,803 | **not read** |
| `research/sources/W0-audit-prior-art-citations.md` | 39,778 | one claim only |
| `research/sources/W0-adversarial-refutation-novelty-claim.md` | 29,830 | **not read** — reached this pass only through the synthesis that quotes it |

⭐ **The layer that carries conclusions was read; the layer that carries the evidence behind them was
not.** Every Wave 0 citation in the supplement is therefore tagged `PRIOR SYNTHESIS`, never
`SOURCE FACT`-verified-here — and `W0-24` (two WebFetch summaries in that wave were wrong, in
opposite directions) is the reason that distinction is worth keeping.

**What is still needed:** read the vocabulary crawl and the adversarial-refutation source. The
crawl is the derivation of the three-axis model (standing / basis / window) that would settle
`GAP-05` / `CN-06` / `RB-17`, and **the `agent-factory` indexes do not currently know that model
exists.** That is now the highest-value unread thing in either repository.

---

### GAP-04 · `HIGH` · Nine (or six) knowledge stores have never been enumerated

R10 says **six** overlapping stores. R06B, eight days later, says **nine**. Neither enumerates them
in a form the other can be checked against, and `absorption-backlog.md` AB-13 — *"enumerate the six,
pick one to retire or merge, and do it before any new store lands"* — is unactioned.

⭐ **This is a measurement, not a research mission**, and it blocks the largest design question in
the corpus (CN-03: build a knowledge fabric, or retire a store first).

---

### GAP-05 · `HIGH` · No crosswalk exists between six evidence vocabularies

`contradictions.md` CN-06 lists six incompatible basis vocabularies in active use. Only one
crosswalk exists anywhere (`SYNTHESIS` §16.12, mapping R17's tiers onto the estate's).

**Consequence:** a claim labelled `DERIVED` in one document and `DOCUMENTED` in another cannot be
compared, and no automated audit can roll them up. ⭐ `factory/assertions.py`'s eight-value set is a
superset of three of the six and is the obvious candidate — but nothing declares it as canonical.

---

### GAP-06 · `MEDIUM` · The dispatch instrument cannot see two of its own prompts

`docs/research/R06B-…` records it in its own header:

> `grep -rn "R06\|WAVE_0" factory/*.py` returns nothing, so `python -m factory.dispatch` **has never
> listed it as outstanding. That blindness is itself a finding; file it.**

`docs/research/warehouse-framework-brief.md` has the same problem. **The finding has not been filed**
— an instance of `concept_index.yaml` C-VD-02 sitting in the instrument that measures research
coverage. Related: `F93` (mtime comparison), `F75` (both reconciliation checks passed over three
unabsorbed answers).

---

### GAP-07 · `MEDIUM` · 19 absorption rows and 2 whole answers have no disposition

`absorption-backlog.md`: **0 of 19 rows closed.** AB-16 and AB-17 are entire research answers — R14
(87 KB) and R18 (105 KB) — each carrying *"absorb it or reject it in writing."* Neither has happened.

**This is a reading-and-deciding job, not research**, but 191 KB of paid-for analysis currently has
no standing in the record either way.

---

## Part 2 — Claims that lack evidence

### GAP-08 · `CRITICAL` · Nothing has been shown to generalise past one connector

`F76` corrected the premise: the instrument **can** fail (12/12 assertions calibrated). What is
unproven is **coverage**. The corpus is one file, one connector, 6,762 bytes; **48 connectors have
never been scored**.

⭐ **`absorption-backlog.md` AB-04 names the cheapest decisive step: score a SECOND real connector
end to end.** That converts n=1 into evidence of generality, and *"will find the assumptions baked
into the windsorai fixture faster than manufacturing 38 more."*

**This is an experiment, not a research mission.** It is the highest-value single action in the
corpus and it does not require a research pass to authorise it.

---

### GAP-09 · `CRITICAL` · No agent has ever completed a real run

MEASURED: `.data/runs.jsonl` 10 rows, zero `PASS`; 7 `agent_returned` events, **all
`dry_run=True`**. Every metric with a denominator of runs is therefore over an empty population, and
`METRICS.md` reports First-Pass GREEN Rate as `0/8` with `instrument_live = False`.

⚠ **This is not a research gap and must not be converted into one.** It is a build-and-run gap.
`F90` (OPEN) names the specific blocker: `TeamSpec.repo` is inside the version hash, nothing reads
it, and both presets with a runnable verifier target a *different repository*.

**Listed here only because it invalidates the evidentiary basis of almost every other gap below.**

---

### GAP-10 · `HIGH` · The 41.7% conflict figure and the 9–13pp model figure

R5's 41.7% cross-agent PR conflict rate was flagged by R17 as *"a citation wearing a measurement's
clothes"*; a discriminating test was run (`SYNTHESIS` §16.1). `SYNTHESIS` §6's *"9–13pp differences
between backends"* — the top item in the search screening order — is `EXTERNAL_CITED` and has
**never been checked back to source here**.

**Pattern:** the corpus has a citation-verification discipline (R17 §8's verification ledger) and it
has been applied to exactly one pass.

---

### GAP-11 · `HIGH` · Nobody has measured what an isolation tier costs

`architecture-v0.md` §7 names this as the first way it may be wrong: if a zero-copy clone is not
cheap to validate against, *"§4 collapses and the ceiling stays at 3."* T1/T2 assume containers on
Windows via WSL, **unmeasured**, and start-up cost is *"a guess."*

**Needed:** a measured T1 container start-up cost on this machine, and a measured T2 clone creation +
validation cost against a real warehouse. Both are experiments.

---

### GAP-12 · `HIGH` · "Data work does not conflict" is asserted, not measured

`architecture-v0.md` §7.2 concedes it: two agents building two views can conflict on a shared
dimension table, a naming convention, or the same `REPORT_COMMON` object. *"The conflict graph may
just need different edges, not fewer."*

The whole argument that the 3-lane ceiling does not generalise to data work rests on this.

---

### GAP-13 · `MEDIUM` · R10's numbers are unverified and self-inconsistent

`absorption-backlog.md` AB-13: R10 *"attributes its strongest figure (32% → 55%) to two different
authors in one source list — treat R10's numbers as unverified."* R10 is the primary evidence for
the store-consolidation position in CN-03.

---

## Part 3 — Architectures that lack research

### GAP-14 · `CRITICAL` · No topology tournament has been run

The bootstrap pack's own `R-TOPO-01` asks: under what task characteristics do hierarchy, swarm,
mesh, blackboard, market, council and hybrid topologies outperform one another? **Unrun.**

R2 answered a narrower question (one agent or three) with 180 configurations of external evidence,
and `CURRENT_STATE.md` records that the source's v3 abstract now leads with *"architecture-task
alignment determines collaborative success"* — a range from **+80.8%** to **−70.0%**.

⭐ **The interesting question is no longer "does multi-agent help" but "which task shapes does which
architecture suit", and that question has never been asked here.**

---

### GAP-15 · `HIGH` · Nothing evaluates an organizational structure

`C-OR-03` proposes that organization presets are *versioned candidates*, so organizational design
becomes empirical. `zeus_world_ui_research_pack/05_EVALUATION_PROTOCOL.md` supplies a graduation
rule for UI concepts. **Nothing connects them**: there is no method for scoring one organizational
shape against another.

**Without it, every preset in the corpus is unfalsifiable.**

---

### GAP-16 · `HIGH` · No evaluation methodology exists for the memory layer

Five packs propose a knowledge fabric. `R06B` demands that *every candidate view must beat the null*
and asks for a benchmark *"against our corpus, or admit we cannot."*

**Nobody has defined what beating the null means for a retrieval or projection layer**, so CN-03
cannot be settled by evidence even if R06B were dispatched today.

---

### GAP-17 · `HIGH` · Agent health metrics have never been tested against outcomes

Four packs specify health vectors, struggle scores and readiness composites. `R-HEALTH-01` asks
which metrics **actually predict mission success** and how composite scores avoid hiding failure
modes. **Unrun**, and with zero completed runs there is no outcome variable to correlate against.

---

### GAP-18 · `MEDIUM` · Simulation-to-production transfer validity

The bootstrap pack lists this as a `HIGH` unvalidated gap in its own `RESEARCH_GAPS.md`.

⭐ **And a prior question nobody has asked:** *what is being simulated?* No document says whether the
simulator models the **world** (a warehouse, a connector, a failing API) or only the **agent loop**.
Those are very different builds with very different costs, and the corpus's simulation material
never distinguishes them.

---

### GAP-19 · `MEDIUM` · Credit assignment across a team

Named in `monitoring_benchmarking_spec.md`, in the bootstrap `RESEARCH_GAPS.md`, and as Shapley
Cognitive Credit in `agent2_sihre`. **No pass has looked at it**, and `METRICS.md` §H's attribution
rules cover *communication* defects only.

---

### GAP-20 · `EXPLORATORY` · SIHRE transfer validity

`agent2_sihre_consolidation_pack/08_NOVELTY_CLAIMS` states its own requirement: the transfer from
quantitative research to agent organizations is *a hypothesis requiring agent-specific evaluation*.
`DR01` asks the prior-art question. **Unrun.**

---

## Part 4 — Competing designs that need comparison

### GAP-21 · `HIGH` · Rank ladder versus absence table

Two encodings of the same discipline — an ordered autonomy ladder with promotion rules
(`ROADMAP_TO_VISION.md`) and a table of independent gates each with a quantified unlock
(`README.md` + `SYNTHESIS` §6). **Neither cites the other; no document compares them.**

Which representation is better is a real design question: the ladder communicates, the table is
harder to game.

---

### GAP-22 · `HIGH` · Four planes versus five layers

`architecture-v0.md` decomposes into DECIDE / RUN / PROVE / APPROVE. `docs/reviews/external/deepseek.md`
decomposes into L1 elicitation / L2 contract state machine / L3 execution / L4 assurance / L5
learning. Both are on file; **no document compares them**, and architecture-v0 §7.3 independently
wonders whether *"four planes may be three."*

---

### GAP-23 · `HIGH` · Autonomy as a ladder or as independent switches

`AUTONOMY_LADDER.md` implies a single ordering of trust. `R7`'s five auto-actions, each
refuse-by-default, imply independent grants. `contradictions.md` CN-23. Uncompared.

---

### GAP-24 · `MEDIUM` · Five message kinds versus six message types

The built vocabulary (`bus.py`: correction/claimed/blocked/finished/note) and the designed one
(`AGENT_COMMUNICATION_PROTOCOL.md`: six types, four moments, six ACK states) have **no mapping**
between them. CN-10.

---

### GAP-25 · `MEDIUM` · Four metric families with no crosswalk

`duplicate_clusters.md` DC-12. Recurring Failure Rate appears in all four and is the only metric
that crossed from a pack into code. **Nothing maps the other three sets onto `METRICS.md`.**

---

## Part 5 — Unresolved implementation choices

### GAP-26 · `CRITICAL` · The embedded terminal

⛔ **The corpus's own blocking open decision.** `docs/research/README.md` §4 lists it first, and it
is stated as an explicit open question in R8, R13, R14 **and** R15 *"precisely so none of them
resolves it silently."*

> **Do not settle the terminal question by taking whichever answer arrives first.** It has been
> answered by accident twice.

⚠ **This is a decision for a human, not a research mission.** Listed because a synthesis that
proposes an operator surface without settling it will re-open it by accident a third time.

---

### GAP-27 · `CRITICAL` · Does APPROVE leave the building?

R13 run 2 found that APPROVE becomes a GitHub PR — *"which removes the very plane §14.2's platform
argument was justifying."* AB-12 names it the first of five findings to action, *"because a decision
depends on it."* **Not done.** CN-14.

---

### GAP-28 · `HIGH` · One monorepo or federated repositories

`Agent Factory Vision.txt` §1 proposes a platform monorepo absorbing the Factory.
`product-end-state.md` §2 and `DEEP-REVIEW-PROMPT.md` §4b move the opposite way. CN-17. **No cost
analysis exists on either side.**

---

### GAP-29 · `HIGH` · Where does the evaluator actually run?

R3 ranks a separate *local* process **5 of 5, "mostly theatre"**. `evaluator_service/` is designed to
be lifted out — *"a packaging change, not a refactor"* — and **nothing records that it has been**.
`corpus.py`: separation is *evident and attributed, not yet enforced*.

---

### GAP-30 · `HIGH` · Which CLIENT-A account ids are in scope; is the landing table one account or two?

`docs/research/README.md` §4, questions 2 and 3. The first **blocks the tenancy assertion and
therefore blocks certification of the one green connector**. The second is sharper:

> 20 rows across 18 campaigns on one date cannot be unique on `(account_id, campaign_id, date)`. If
> it is one account, the declared primary key is wrong and **the calibration world is built on a
> mistake.**

⛔ **If the second is true, GAP-08's fixture is wrong**, and so is everything replayed against it.

---

### GAP-31 · `MEDIUM` · Retire `orchestration-bench.html`?

Recommended by R13 run 2, recorded three times, unactioned. Per the absorption rule, **a written
rejection closes it as well as retirement does.** SP-10.

---

### GAP-32 · `MEDIUM` · Is `REFUSED` a sixth verdict, and why is `Unmeasurable` defined three times?

`CURRENT_STATE.md` leaves the first open (*"the separation may be correct"*) and marks the second
**unresolved**. The system's founding claim is that two kinds of not-knowing must never be collapsed,
and the exception class expressing that has three definitions.

---

## Part 6 — Concepts needing prior-art research

### GAP-33 · `HIGH` · Observability and trace standards

`concept-inventory` §4.2 — a `NOT-SEARCHED` axis. R1 was scoped to *eval frameworks* and concluded
"don't add one"; **that verdict does not cover tracing.** OpenTelemetry GenAI semantic conventions,
Langfuse / LangSmith / W&B Weave, and whether a certified run should emit a standard-shaped
trajectory are untouched. `deploy.py` streams a transcript; **there is no structured trajectory
object** — which also blocks C-OP-06 (meta-tool extraction).

### GAP-34 · `MEDIUM` · Task and environment packaging standards

`concept-inventory` §4.3 — METR's task standard, Inspect's task format, SWE-Gym-style environment
packaging. Relevant because the deferred gym is partly a packaging question and a standard format
would make the corpus portable.

### GAP-35 · `MEDIUM` · Interop as a factory primitive

`concept-inventory` §4.4 — MCP is used across the estate but is not a factory *concept* here; A2A
and AGNTCY were deferred as *messaging topology* (correctly) but never examined as an **interface
standard**, which is a different question.

### GAP-36 · `MEDIUM` · Mid-run human approval and escalation

`concept-inventory` §4.6 — `operator.py` handles blockers declared *before* the session. R5 calls for
a human approval step before any container launch and it is unbuilt. R9 asked what the operator
*sees*, not what the approval **workflow** is. **The gap between those two is unexamined.**

### GAP-37 · `HIGH` · Compensation and rollback semantics

`concept-inventory` §4.7 and R8 §0's sharp version: **`git revert` does not undo a dropped table.**
"Side-effect replay semantics" is listed as a missing version dimension. **Nobody has designed the
compensating action**, and `evidence.py:27` states its own related limit: it cannot verify that
ROLLBACK was captured *before* the mutation.

---

## Part 7 — Dependencies that are poorly understood

| # | Dependency | Why it is poorly understood |
|---|---|---|
| GAP-38 | **Claude Code's own surfaces** | `deploy.py:230` hard-codes `--max-turns`, `--max-budget-usd`, `--output-format stream-json`, `--model` against *"an argv surface that is undocumented, unversioned and unpinned"*. `factory/provider.py` exists to contain the blast radius. Nothing measures whether the surface has changed. |
| GAP-39 | **Machine-local state** | `docs/evidence/machine-local-state-2026-08-22.md` — state living outside every repository is invisible to every gate that reads the repository. `factory/runtime_deps.py` partially addresses it. |
| GAP-40 | **`prefect-connectors`** | `F91`: `readiness.py` resolved the sibling checkout from its own file, so every gate reading it **went blind in a lane**. `F78`: the UNATTENDED verdict is about *that* repo, not this one. The dependency is load-bearing and was silently mis-resolved once. |
| GAP-41 | **The Windows/WSL container path** | Assumed by T1 and T2. Never measured. GAP-11. |
| GAP-42 | **Snowflake zero-copy clone semantics** | `architecture-v0` §7.1 calls it *"the single highest-value thing for R8 §2.3 to check"*. R17 §16.3 then argues the clone is a compromised oracle. Unresolved either way. |

---

## Part 8 — Added 2026-09-02 by the supplementary coverage pass

### GAP-43 · `MEDIUM` · Nothing in either repository trades scope for time under a deadline

Recorded because an operator-proposed direction — **Goal-Aware Adaptive/Dynamic Orchestration**
(`concept_index.yaml` `C-TM-06`) — was checked against the corpus, and thirteen of its fourteen
component ideas turned out to have prior art here or in the sibling. **One did not.**

```bash
grep -rniE "scope degrad" . ../agent-army-research     # zero occurrences, both repositories
```

⭐ **The adjacent mechanisms all degrade on the wrong trigger.**

| Mechanism | Where | Degrades on |
|---|---|---|
| `admit() → DEGRADED(missing)` | `agent-army-research/repo-boundary/PRODUCT-BOUNDARY.md` | **missing capability**, never elapsed time. Its author is explicit that this is a *demand signal*, not a failure: *"`staffing.unstaffable` is the runtime telling the factory what to build next."* |
| `HorizonWorkItem.expiry` | `agent-army-research/architecture/05-temporal-echelons.md` | speculative work **times out**; nothing reduces the goal |
| `factory/schedule.py` | built here | ⛔ **refuses to name a deadline at all.** `schedule.py:26`: *"'Ahead or behind schedule' needs a target, and there isn't one. No deadline has been stated anywhere in the programme."* |

**Why `MEDIUM` and not higher.** Two reasons, and both are arguments for doing something cheaper
first:

1. ⛔ **There is no deadline in this estate for anything to be aware of.** `schedule.py` already
   accepts `--target YYYY-MM-DD` and becomes measurable the moment one is supplied. **Stating a
   target is a one-line action, not a research mission**, and it is the precondition for every part
   of this gap. Doing the research before the target exists would measure nothing.
2. ⭐ **The scheduling half is already bounded by a proof this corpus holds.**
   `docs/research/SYNTHESIS.md:1389` — *"every topology is a scheduler, schedulers redistribute
   `T₁/P`, **none touch the critical path `T∞`**"* (Blumofe & Leiserson [E-1]). Reordering fixed work
   cannot beat `T∞`. **So the only version of this idea that is not already known to be bounded is
   one that mutates the graph** — changes scope, evidence requirements or gates. A design that does
   not say which side of that line it sits on cannot be evaluated, and researching the bounded side
   would buy a known answer at full price.

**⚠ And Wave 0 forbids the obvious object.** `W0-foundations.md:99`: authority, budget and deadline
are `Mandate`, not `Contract` — *"a `GreenContract`'s fold is meaningful only because every member is
falsifiable; adding permissions breaks the property the object exists for."* A "goal contract"
carrying a deadline must be the three-way split `Contract` / `Mandate` / `Task`, and `Mandate` is
itself behind an unmet enforcement gate (the sibling's own unresolved question 1).

**What is genuinely missing, stated narrowly:** *a rule for what may be dropped when time runs out,
and who may authorise dropping it.* That is a governance question, not a scheduling one — which puts
it in the same family as `GAP-27` (does APPROVE leave the building) and `GAP-36` (mid-run human
approval and escalation), and it should probably be answered with them rather than alone.

⛔ **NOT dispatched. Not designed. No novelty claimed.** See
[`agent_army_wave0_supplement.md`](agent_army_wave0_supplement.md) Part 4.

---

## Part 9 — Added 2026-09-02 by the `.agent-platform` delta pass

Two gaps, both of the *"claim with no instrument"* family. Reconciliation:
[`agent_platform_delta_synthesis.md`](agent_platform_delta_synthesis.md).

### GAP-44 · `MEDIUM` · Nothing counts the friction that execution-surface routing claims to remove

`C-GV-07` is promoted on a stated benefit — fewer operator interventions and fewer branch
conflicts across many parallel sessions. ⛔ **Neither quantity is counted anywhere in this estate.**

`factory/coordination.py` publishes coordination *ingredients* — and refuses to sum them, for a
good reason it states in its own docstring: *"a single headline percentage would need a denominator
nobody has defined"*. But none of the ingredients it does publish is **"a task ran on a surface that
could not reach what it needed"** or **"two lanes touched the same file"**. The nearest instrument
is `factory/claims.py`, which prevents a collision rather than recording that one was attempted.

⭐ **This is `C-VD-02` pointed at a proposal instead of at a result.** Without a before-number,
`RB-22`'s experiment can only report a prediction. And the failure it would measure is one this
repo has already met by hand: two sessions committed within one hour on 2026-08-31 and three
numbers in `boot-prompts/README.md` rotted in that window.

**Why `MEDIUM` and not higher.** The fix is a measurement, not a research pass — count operator
interventions, branch conflicts and surface-caused re-runs for one week **before** anything is
built. That is the same shape as `GAP-01`, which paid, and it is a precondition for `RB-22` rather
than an argument against it.

```bash
# the instrument that would have to exist first — MEASURED 2026-09-02, it does not
grep -rniE "collision|conflict_count|wrong_surface" factory/coordination.py factory/claims.py
```

---

### GAP-45 · `MEDIUM` · A mined conclusion that lives outside the repository is invisible to every gate

`C-PR-08` records the 2026-08-31 prior-art mining as **validated** — three MIT repositories read
from source, five patterns that would let this estate delete rather than add, one defect inverted
rather than inherited. ⛔ **Its durable artefact has no in-repo home.**
`.agent-platform/RECONCILIATION.md` §4 says so in its own words: the write-up is
`wiki/concepts/patterns/agent-control-plane-prior-art.md`, *"the one artefact with no in-repo
home"*.

Every gate in `factory/readiness.py` reads this repository. A conclusion in the wiki is therefore
outside all thirty of them — the same structural problem as **`GAP-39`** (machine-local state
invisible to every gate that reads the repo), and it has already cost once: **`F91`**, where
`readiness.py` resolved a sibling checkout from its own file and every gate reading it *went blind
in a lane*.

**What makes this cheap.** It is not a research question and it is not a wiki-versus-repo argument.
It is one decision — does a mined pattern land in `docs/findings.d/` (addressable, reviewed, merges
with the branch, and already read as data by `factory/findings.py`), or does the wiki stay its home
and something in the repo point at it? Either answer closes the gap; leaving it open means the next
mining pass produces another artefact nothing can see.

---

## Summary

| Priority | Count | IDs |
|---|---:|---|
| ✅ `CLOSED` | 1 | **GAP-01** (text; `LOW` residual on twelve un-extracted figures) |
| `CRITICAL` | 7 | GAP-02, GAP-08, GAP-09, GAP-14, GAP-26, GAP-27, GAP-30 |
| `HIGH` | 15 | GAP-04, GAP-05, GAP-10, GAP-11, GAP-12, GAP-15, GAP-16, GAP-17, GAP-21, GAP-22, GAP-23, GAP-28, GAP-29, GAP-33, GAP-37 |
| `MEDIUM` | 16 | **GAP-03** (↓ from `HIGH`), GAP-06, GAP-07, GAP-13, GAP-18, GAP-19, GAP-24, GAP-25, GAP-31, GAP-32, GAP-34, GAP-35, GAP-36, **GAP-43**, **GAP-44**, **GAP-45** |
| `EXPLORATORY` | 1 | GAP-20 |
| Dependencies | 5 | GAP-38 … GAP-42 |
| **Total** | **45** | ⓘ was 43. **GAP-44 and GAP-45 added 2026-09-02** by the `.agent-platform` delta pass; no existing gap was touched. Earlier that day: GAP-43 added, GAP-01 closed, GAP-03 downgraded. |

> ⓘ **Both new gaps are `MEDIUM` and both are measurements, not research** — which makes the count
> of *"gaps that are not research at all"* rise from six to eight. That ratio is observation 1
> below, and the delta pass made it worse rather than better. Neither is dispatched.

⭐ **Three observations that matter more than the list.**

**1. Six of the eight `CRITICAL` gaps were not research at all — and one of them has now been
done.** ✅ **GAP-01 was a file conversion and it took under an hour**, exactly as this section
predicted; it produced six concepts, a `BLOCKING` contradiction and an amendment to CN-01, which is a
better return than most of the remaining `CRITICAL` gaps will give. Of the seven left: GAP-08 is
scoring a second connector, GAP-09 is fixing one open finding and running the loop, GAP-26 and GAP-27
are decisions for a human, GAP-30 is asking a client two questions. ⭐ **Dispatching research against
them would be the corpus's characteristic failure — buying an answer to a question that measurement
would settle more cheaply.** Only GAP-02 and GAP-14 genuinely need a research pass.
⭐ **The completed one is the evidence for the rule.**

**2. The corpus's own unrun queue already names several of these.** `R-TOPO-01`, `R-HEALTH-01`,
`R-SELF-01`, `R-ORGIR-01`, `R-META-01` and `R-UI-01` sit in
`agent-factory-bootstrap-pack/docs/08-research-backlog/RESEARCH_QUEUE.yaml` marked `status: seed_only`,
and `R06B` is written and never dispatched. **The gap is not that the questions were never asked. It
is that they were asked and left.**

**3. Almost every gap becomes cheaper after GAP-09.** With zero completed real runs, every metric is
over an empty population, every health model has no outcome variable, and every topology comparison
has no baseline. **One real run converts perhaps a dozen of these from research questions into
measurements.**
