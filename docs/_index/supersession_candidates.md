# Supersession candidates — advisory only

**Generated 2026-09-02** against `agent-factory` @ `fc78074`.

⛔ **NOTHING IS MARKED OBSOLETE HERE.** This file lists documents that *may* have been replaced,
with the evidence for and against in each case. A document is only called superseded when the
corpus itself says so, in writing, and names the replacement — and those cases are listed first,
separately, because they are findings rather than candidates.

**Why this distinction is enforced.** `docs/agent-army/README.md` names the failure mode this whole
estate guards against: *"someone reads a well-written speculative architecture document, sees
vocabulary they recognise, and builds on it as though it described the running system."* The inverse
is just as expensive — retiring a document because a newer one *looks* like its replacement. Several
documents in this corpus are kept deliberately *because* they are wrong:
`blueprints/orchestrator_team.yaml` carries the instruction **"THIS FILE IS KEPT, NOT DELETED"** in
its own header.

**Verdict vocabulary**

| | Means |
|---|---|
| **DECLARED** | The corpus states the supersession in writing and names the replacement. Not a candidate — a fact. |
| **STRONG** | A later document covers the same scope with better evidence, and no reason to keep the earlier one was found |
| **PARTIAL** | Superseded on some claims, still authoritative on others. **Do not retire.** |
| **APPARENT-ONLY** | Looks superseded and is not — the earlier document is load-bearing, deliberately kept, or read by code |
| **STALE, NOT SUPERSEDED** | Wrong, with no replacement. Needs correcting, not retiring — a different action |

---

# Part 1 — DECLARED supersessions (facts, not candidates)

## SP-01 `R3-optimizer-sandbox-SUPERSEDED.md` → `R3-control-plane-and-optimizer.md`

**Verdict: DECLARED.** The corpus's only file that carries its own supersession *in its filename*.
Kept, not deleted.

| | |
|---|---|
| Superseded | `docs/research/R3-optimizer-sandbox-SUPERSEDED.md` (10,024 bytes, added 2026-08-21) |
| Replacement | `docs/research/R3-control-plane-and-optimizer.md` (15,166 bytes, same day) |
| Action | **None.** The filename is the record. |

---

## SP-02 The Zeus/Olympus UI theme → the Army/Mission Command theme

**Verdict: DECLARED, and partial by the replacement's own instruction.**

`docs/raw_research/agent_factory_chat_design_pack/00_MASTER_CONCEPT_MAP.md` §I:

> **Zeus/Olympus World — SUPERSEDED FOR UI THEME.** The Zeus mythology exploration produced useful
> architectural naming patterns, but the user selected a **full Army/Mission Command theme** for the
> world. Retain Zeus artifacts only as reference for: service-to-world mapping, role identity, world
> vocabulary design, consistent thematic semantics. **Do not treat Zeus naming as current UI
> direction.**

⭐ **What is NOT superseded, and this is the important half.** The Zeus pack's
`05_EVALUATION_PROTOCOL.md` (core metrics, a baseline task suite, target thresholds a concept must
beat, a prototype ladder) and `09_IMPLEMENTATION_READINESS.md` (ten gates, including *"no Goodhart
reward loop"* and *"three world interactions must beat baseline"*) are **theme-independent**. They
survive the supersession entirely and are the most valuable material in the whole UI corpus.

**Action: none.** Keep all three copies (see `duplicate_clusters.md` DC-06). Read the evaluation
protocol and the readiness gates as current.

---

## SP-03 `R8` → `R17` (external half) + `R18` (internal half)

**Verdict: DECLARED, and only half.**

`docs/research/README.md`:

> ⚠ **R8 reads `ANSWERED` and its internal half is not evidence.** The filed answer carries zero file
> paths and zero line references against a pack whose own rule demanded both. `dispatch` has no state
> for *dispatched, answered, answer half-rejected* — so the split into R17/R18 is the record, and
> R8's own header carries the ⛔. **Read the external half; do not cite the internal half.**

| | |
|---|---|
| Superseded | The **internal half** of `docs/research/answers/R8-answer-data-engineering-agent-factory.md` |
| Still standing | The **external half** of the same file |
| Replacements | `R17-answer-data-engineering-external-survey.md` · `R18-answer-our-factory-internal-audit.md` |

**Action: none.** The half-supersession is recorded in three places and is the reason R17 and R18
exist. ⚠ Note it also produced an unclosed contradiction — see `contradictions.md` CN-11.

---

## SP-04 `docs/findings.md` → `docs/findings.d/`

**Verdict: DECLARED for new writing, NOT for reading.**

`docs/findings.d/README.md`: *"**Write new findings here, as a new file. Do not append to
`docs/findings.md`.** `load()` reads this directory *and* `../findings.md`, so the existing entries
still count and nothing already on a lane branch breaks."*

**Action: none. `findings.md` is still read by `factory/findings.py`.** Retiring it would silently
drop F1–F19 from every lane's correction feed.

---

## SP-05 `docs/research/R06B-…` supersedes the pack's `R06B_COLLECTIVE_COGNITION.md`

**Verdict: DECLARED by the successor, in its own header.**

`docs/research/R06B-collective-cognition-and-knowledge-architecture.md`:

> Supersedes the draft prompt at `.agent-platform/bootstrap/research/prompts/R06B_COLLECTIVE_COGNITION.md`,
> which is `priority: critical` in `WAVE_0.yaml` and which **no instrument in `factory/` can see** —
> `grep -rn "R06\|WAVE_0" factory/*.py` returns nothing, so `python -m factory.dispatch` has never
> listed it as outstanding. **That blindness is itself a finding; file it.**

⭐ This is the corpus's clearest single example of the intended relationship between an inbound pack
and this repository: the pack's prompt asks *how to build a Collective Cognition Fabric*; the
superseding prompt first **measures the nine stores that already exist** and asks what a fabric would
add that none of them can do.

**Action: none on the documents.** The finding about `dispatch`'s blindness is **not filed** —
carried into `research_gap_candidates.md` GAP-06.

---

# Part 2 — STRONG candidates

## SP-06 `docs/artifacts/agent-factory.html` — the numbers it renders are dead

**Verdict: STRONG for its *content*, APPARENT-ONLY for the *file*.**

Its own `README.md` says so:

> ⚠ **`agent-factory.html` is stale as of 2026-08-29.** It reflects the `UNMEASURABLE (PASS=11)` era
> and a "9 of 30 gates" count; `certify --calibrate` now returns `PASS (PASS=12)`. **It has not been
> republished, so the live page carries the old numbers too.**

⛔ **Do not delete or move the file.** `factory/readiness.py` yields it into the suite fingerprint
**by name**; `factory/lanes.py` and `factory/schedule.py` also reference the path. Moving it breaks
the readiness gate.

**Action: regenerate and republish.** The *file* stays where it is. ⚠ The **published artifact** is
the more serious half — a live page carries numbers the repository has corrected.

---

## SP-07 `docs/specs/client-review-loop-v0.md` — the code overtook the spec

**Verdict: STRONG. The spec is behind the implementation.**

| Spec says | Code says |
|---|---|
| *"queued capability, **not started**"* | `factory/client_review.py` 1,191 lines · `client_review_render.py` 704 lines · two test modules · a rendered-confirmed evidence pass on 2026-09-01 |

Per `docs/agent-army/RESEARCH_REPO.md`'s hierarchy — **code beats specification** — the code is
right.

**Action: update the spec's status line, or mark it HISTORICAL.** Not a deletion; the eleven
contracts it specifies are still the design. Also `contradictions.md` CN-28.

---

## SP-08 `docs/research/agent-factory-concept-inventory.md` §3 — the do-not-re-ask table

**Verdict: PARTIAL, tending to STRONG on one section only.**

§3 was written 2026-08-22 and records R8 and R9 as *"written, NOT DISPATCHED"* and R10–R19 as not
yet existing. **Measured 2026-09-02: `python -m factory.dispatch` reports R1–R8 and R10–R19 all
`ANSWERED`.** R9 was withdrawn 2026-08-23.

⭐ **§2 and §4 are NOT superseded and are the most valuable parts of the corpus for a gap analysis:**
§2 is the 26-concept surface measured from code, §4 is the seven `NOT-SEARCHED` axes.

**Action: none, or refresh §3's status column.** ⚠ The rest of the document is load-bearing.

---

## SP-09 `docs/CORPUS-AND-DESIGN-PROMPT.md` — superseded by the pass that actually ran

**Verdict: STRONG as an instruction, PARTIAL as a specification of deliverables.**

It asks for `docs/corpus/OBJECTIVE.md`, a design artifact and `docs/corpus/GAPS.md`.
**MEASURED: `docs/corpus/` does not exist.** The corpus-preparation work was eventually done into
`docs/_index/` under a different prompt (`CLAUDE_CORPUS_PREPARATION_PROMPT.md`) with a different
deliverable shape.

⚠ **But it also asks for D3, a Detailed Technical Design Artifact — which `docs/_index/` deliberately
does NOT produce**, because the corpus-preparation prompt's stop condition forbids proposing an
architecture in the same pass.

**Action: none.** Keep it as the specification of a deliverable that has not been produced. See
`duplicate_clusters.md` DC-09.

---

## SP-10 `docs/artifacts/orchestration-bench.html` — recommended for retirement, unactioned

**Verdict: STRONG on a recommendation nobody has acted on.**

R13 run 2 recommends retiring it; `absorption-backlog.md` AB-12 carries the recommendation as one of
five findings never taken; `docs/artifacts/README.md` carries it as a ⚠ note. The file is still
present and still listed as published.

**Action: decide.** Per the absorption-backlog rule, **a written rejection closes the row just as
well as retirement does.** What is not acceptable is the current state, where the recommendation is
recorded three times and nothing has happened.

---

# Part 3 — PARTIAL

## SP-11 `docs/specs/architecture-v0.md` — corrected twice, still the current architecture

**Verdict: PARTIAL. Two specific claims superseded; the document is not.**

| Corrected | By |
|---|---|
| §2's cost row, which read *"nothing records tokens or wall clock"* while carrying a `MEASURED` label | R18, then re-measured and corrected in place 2026-08-23 |
| §5's *"0 of 15 version dimensions"* and a gate id (`hash`) that never existed | R18 found the number; re-measurement found the wrong id. Now **6 of 15**, gate `version` |

Both corrections were written **into** the document beside the original claims.

**Action: none.** §4's isolation ladder is the highest-leverage unbuilt idea originating in this
repository, and §7's five self-attacks are still open questions.

---

## SP-12 `docs/research/answers/R8-…` §2's record/channel answer

**Verdict: PARTIAL on one section, and the supersession is UNATTRIBUTED.**

R8 §2 answered the record/channel question with *"event sourcing… like CQRS"*. `SYNTHESIS.md` §16.10
refutes it as **"neither"** — but presents the question as one *"asked in session"*, never recording
that a pass had already answered it wrongly.

**Action:** file the refutation against R8 explicitly (`absorption-backlog.md` AB-14). Until then,
the record does not show that a research pass got this wrong, **so the same wrong answer can arrive
again from the same source.**

---

## SP-13 `docs/protocol/prompts/` — the ten agent roles

**Verdict: PARTIAL. Superseded in *approach*, not in *content*.**

Ten LLM agent roles including a mandatory skeptical reviewer sit against `R2`'s verdict (one worker
+ a non-LLM verifier + a human) and `README.md`'s deferral of extra LLM roles behind quantified
unlocks. The pack's own README concedes the framing: they are written *"so they are not re-derived,
**not so they are built now**."*

⭐ **The four-section structure is not superseded and may be the most reusable thing in the pack:**
every role prompt carries `INPUT CONTRACT` / `OUTPUT CONTRACT` / `STOP CONDITIONS` /
`EVIDENCE REQUIREMENTS`.

**Action: none.** Keep as a design record with its status marker intact.

---

## SP-14 `BRAIN-DUMP.md` — superseded as a plan, irreplaceable as a baseline

**Verdict: APPARENT-ONLY.** Every idea in it has been researched, deferred or refused since. But it
is the only record of what was asked for **before** any evidence existed, and reading the corpus
against it is the fastest way to see what the evidence actually did to each idea.

**Action: none, ever.** `docs/agent-army/README.md` explicitly records that it did not move during
the research migration: *"the verbatim recovered origin record… the original is intact."*

---

## SP-15 The frontier documents' VOCABULARY is superseded by Wave 0; their CONTENT is not

*Added 2026-09-02 by the supplementary coverage pass.*

**Verdict: PARTIAL — terminology superseded, substance preserved. Advisory only; nothing was edited.**

The two newly-converted `.docx` (`docs/raw_research/converted/`) use, as headline terms, **seven
names the sibling repository's Wave 0 explicitly ruled against** — and they do so because they were
written on 2026-09-01 without having read the 2026-08-30 verdict (see `contradictions.md`, the CN-01
amendment). `agent-army-research/research/answers/R01-…md` Deliverable 5:

| The documents say | Wave 0 recommends | Reason recorded |
|---|---|---|
| Organizational Compiler | **Organization Synthesiser** | *"compiler over-promises determinism we do not have; synthesis is the honest word and the literature's"* |
| Org-IR | **Organization Specification** (structural / functional / deontic, after Moise+) | *"the three-way split is a design improvement, not just a rename"* |
| Collective Cognition (Fabric) | **Knowledge and Evidence Store** | our usage **inverts** the industry senses of *fabric* and *mesh* |
| Stigmergic / Organizational Fields | **Coordination Fields** (cite Co-Fields/TOTA, Parunak) | keeps the mechanism, drops the implied invention |
| Morphogenetic Teams | **Adaptive Team Formation** | plain, searchable, honest about lineage |
| Evolution Chamber | **Organization Design Lab** | removes the StarCraft collision; *"lab" correctly implies offline* |
| Temporal Echelons | **Planning Horizons** (NOW / NEXT / LATER) | ⛔ *"echelon means command level, not time horizon. The literature wins."* |

Also recorded as outright collisions: **"Organizational OS"** (trademarked **EOS®**), **"Executable
Doctrine"** (Doctrine PHP ORM), **"Cognitive Logistics"** (EU H2020 project), and — rated
**BLOCKING** — **"Organizational Digital Twin"**, because *"we would be entering a defined analyst
category (Gartner DTO Magic Quadrant), against funded incumbents, with no differentiator stated."*

**What is superseded:** the *names*, for any external or client-facing use.
**What is NOT superseded:** the twelve architecture cards, the failure modes, the smallest-useful-
experiments, the prioritisation argument, the promotion gates and the Mission Assurance Receipt.
⭐ **Renaming is cheap and is the whole remedy.** Nothing in either document needs to be discarded.

**Action: none in these files.** They are inbound source material and, like the nine packs in Part 4
below, are preserved verbatim so the reconciliation remains checkable. ⚠ **The action belongs to any
document written FROM them** — an architecture synthesis that adopts "Temporal Echelons" or
"Organizational OS" as a heading is re-importing a collision the corpus has already priced.

---

# Part 4 — APPARENT-ONLY (looks superseded, is not)

| Document | Why it looks superseded | Why it is not |
|---|---|---|
| `blueprints/orchestrator_team.yaml` | Its architecture was rejected | ⭐ **"THIS FILE IS KEPT, NOT DELETED. It is a hypothesis that was tested and rejected."** It also carries the quantified threshold that would unlock it — the only such threshold in the repository. |
| `docs/findings.d/F98` | Status `SUPERSEDED` | Only its *claim* is superseded (the DAG field is now used). The finding is the record of the correction and is what stops the claim returning. |
| `docs/raw_research/**` (all nine packs) | Their category framing is refuted (`contradictions.md` CN-01) | Their **engineering patterns are live**. `RECONCILIATION.md`: *"mine it for mechanisms; do not adopt its programme."* Retiring the packs would discard C-AG-03, C-OR-01, C-OP-06 and the 25-item experiment backlog with them. |
| `docs/research/answers/R4-…` (run 1) | A longer run 2 exists | SYNTHESIS §7.4 treats them as **corroboration**, not replacement. ⚠ And two runs of one prompt are not independent — see `duplicate_clusters.md` DC-05. |
| `docs/research/answers/R13-…` (run 1) | A run 2 exists | Run 2 answers only the four questions run 1 left **open**. It is an extension. |
| `docs/agent-army/APPROVED_CONCEPTS.md` | The table is empty | ⭐ **An empty table is the correct output today.** It also carries the four approval requirements and the measured state of the sibling repo's research programme. |
| `.agent-platform/bootstrap/**` | Its founding premise is refuted | Kept **verbatim and unmodified** so the reconciliation and conformance audits beside it remain checkable. `.agent-platform/README.md` declares its authority as NONE, which is a stronger control than deletion. |
| `docs/artifacts/project.html` | Zero code references | ⚠ **By design.** An audit on 2026-08-31 read the zero as orphaning and nearly cost the file. |

---

# Part 5 — STALE, NOT SUPERSEDED

These are wrong with **no replacement**. The action is to correct them, which is a different job from
retiring them — and in three cases nobody has.

| Document | What is stale | Has a replacement? |
|---|---|---|
| `docs/artifacts/agent-factory.html` **and its published page** | Gate counts and the `PASS=11` era | ⛔ No. Regeneration is the fix. |
| `docs/specs/client-review-loop-v0.md` | Its "not started" status | ⛔ No. The code is the truth; the spec needs a status line. |
| `docs/research/agent-factory-concept-inventory.md` §3 | Dispatch statuses for R8–R19 | ⛔ No. Only §3 is affected. |
| `blueprints/orchestrator_team.yaml:18` | A mean stated without its interval | ⛔ No, **deliberately.** Flagged in `CURRENT_STATE.md` rather than edited, because the blueprint is a historical record. Quote the answer file instead. |
| `docs/reviews/build-vs-adopt-2026-08-29.md` §6 | Issues corrections to `BUILD-VS-ADOPT-PROMPT.md` and says to *"publish these wherever it has been quoted"* | ⚠ Not done — the prompt still carries the uncorrected claims. |

---

# What has NO supersession risk, and why that matters

Four documents carry a **regeneration command**, so they announce their own staleness instead of
rotting quietly:

- `docs/agent-army/CURRENT_STATE.md` — a term sweep across `factory/`, `evaluator_service/`, `scripts/`
- `.agent-platform/RECONCILIATION.md` — measured against two named commits, with commands per figure
- `.agent-platform/PACK_CONFORMANCE.md` — regenerates the instruction list it audits
- `docs/evidence/recurrence-preflight-2026-08-31/README.md` — *"regenerating every number in the report"*

⭐ **This is the single cheapest improvement available to the corpus.** Six of the documents above
would not appear in Part 3 or Part 5 at all if they carried the command that produced their numbers.
The rule is already written down — `concept_index.yaml` C-VD-04 — and is followed by four documents
out of 168.

---

## Method and limits

Supersession was assessed from: (a) explicit statements in the documents themselves; (b) date order
plus scope overlap; (c) `git log --diff-filter=A` for first-commit dates; (d) direct measurement
where a document made a checkable claim (dispatch state, gate count, run ledger, file existence).

⛔ **Two limits, stated rather than hidden:**

1. **The two `.docx` files were not read** (635 KB). One is titled *"Beyond Agent Armies: Frontier
   Architectures"*. If either supersedes material in this corpus, this file cannot know. →
   `research_gap_candidates.md` GAP-01.
2. **The sibling repository `agent-army-research` was not indexed.** It is the authoritative home of
   Agent Army research and holds the Wave 0 synthesis that drives `contradictions.md` CN-01. Its
   contents may supersede documents here, and this pass would not see it.
