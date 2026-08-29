# Client Intake Platform — corpus synthesis, design, phases and tickets

**Written 2026-08-29.** Scope: turn client kickoff → spec → build → acceptance into one instrumented
loop, and make the loop improve itself.

---

## 0. ⛔ Read this before adding anything

Four things are already true, and each one kills a plausible plan:

1. **`docs/CORPUS-AND-DESIGN-PROMPT.md` already exists** (460 lines, written today). It covers
   corpus consolidation, the objective report, a technical-design artifact, and a gaps register for
   *this repo's* research. **Do not write a second version of it.** This plan is the layer it does
   not reach: the client-facing intake surface and the learning loop around it.
2. **The gap is absorption, not knowledge.** `SYNTHESIS.md` §17: *"Seven sentences say an answer has
   not landed. All seven are false."* `docs/absorption-backlog.md` lists **AB-01 … AB-19** —
   conclusions that reached a mechanism and appear nowhere in the decision record. Any new research
   lane must first name which existing answer failed to cover it, by file and section.
3. **The Engineering Tracker (Part A) is approved but not built.** Plan approved 2026-05-14
   (`~/.claude/plans/indexed-puzzling-shannon.md`); `data/tracker/` holds one PBI-EVAL results file
   and nothing else — no `tracker.json`, no `pages/tracker/`. So "put it on the tracker" currently
   means `.data/tasks.jsonl` in this repo, which is live (31 events) and append-only.
4. **The 7-stage pipeline B1…B7 already names the shape** — B1 Requirements → B2 Approach →
   B3 Implementation → B4 Testing → B5 PR → B6 CR → B7 Deploy+Rollback. **The client portal is a
   front end on B1 and B2, which today have no client-facing surface at all.** It is not a new
   pipeline.

---

## 1. The goal, in one sentence

> A client answers a structured questionnaire once; that answer becomes the machine-checkable
> contract every later stage is judged against; and every correction the client makes afterwards
> improves the next client's questionnaire.

The failure it exists to end, in Paul's words: *"I got a high-level idea, but no detailed spec, or
validation each new API connector had the data they expected"* — discovering a missing field in
week six rather than at kickoff.

---

## 2. The four corpora, and what each actually contributes

| Corpus | Contributes | Load-bearing artefact |
|---|---|---|
| **agent-factory** — 80 docs, R1–R18, findings F20–F76 | the contract, certification, and the negative-control discipline | `factory/contract.py`, `evals.py`, `certify.py` |
| **Ontology research** (26-05) | **how to elicit a domain model from a stakeholder** | `ALDC Ontology AutoGeneration Assessment.md` |
| **Compounding research** (26-05, Vlad/John) | **how to know the system is actually learning** | `AOR_RMRR_explainer_note_final.md` |
| **workflow-kit** (2026-08-29) | the four gates that make the above fire | `check_intake.py`, `guard.py`, `verify.py`, `measure.py` |

### What the ontology work actually says — and why it is the centrepiece

Its finding is not about food waste. It is about **elicitation quality**:

> *"Success depends entirely on questionnaire quality. A well-designed questionnaire (20–30
> structured questions targeting **entity types, relationships, roles, decision gates**) will yield
> **70–80%** of the ontology automatically; a generic 'tell us about your work' questionnaire will
> yield **30–40%** and require extensive manual curation."*

That is a **2× difference in spec completeness**, decided entirely by how the form is written. It is
the single highest-leverage claim across all four corpora, and it applies directly to a client
kickoff form. The four target dimensions — entity types, relationships, roles, decision gates — are
the schema for the questionnaire.

It also states the extraction pipeline is feasible in 8–12 weeks for a domain-scale ontology, and
that relationship-heavy domains suit graph extraction. A single client's connector spec is far
smaller than a domain ontology, so the method transfers with a much shorter timeline.

### What the compounding work actually says — and the trap it already caught

**AOR** asked "is the corpus helping or just accumulating?" It found an 18-point gap between
successes and failures — then six honest tests were run against 4,518 real memories, and **the
decisive one killed it**: comparing successes vs failures *within the same topic*, the gap fell to
~0. Successful work repeats (near-identical memories, high cosine similarity); failed work scatters.
**The gap measured the shape of the work, not learning.**

Two things follow, and both are directly reusable here:

- **The fair test is within-topic.** Any claim that our loop improves must compare like with like,
  or it will measure repetition. This is the same class of error as the CLIENT-A wrong-layer deploy.
- **Retooled AOR = coverage:** `coverage = (real questions with a relevant answer) / (all real
  questions)`, judged by **relevance** — not cosine similarity (reintroduces the flaw), not outcome
  (that is RMRR's job). Output is a **ranked gap list**, which is a roadmap.

**RMRR** is the online outcome metric: when stored knowledge is used, did a correction follow? Its
honest status is *"right instrument, no readings."*

**The ranking fix matters most for us.** Today rank scales with `retrieval_count` alone, so a
memory that is **wrong but popular keeps climbing and spreads its mistake**. The guarded fix:

```
boost      ∝ retrieval_count × helpfulness
helpfulness = max(0, (uses − corrections + k) / (uses + 2k))          k ≈ 2
```

The guards are the point: `max(0,…)` floors it; `+k/+2k` stops one correction blacklisting a new
memory; `× retrieval_count` keeps volume meaningful. The naive `(uses − corrections)/uses` is
defective and must not be quoted as the fix.

Two mechanisms are named as **missing**: a **write gate** (rejects low-grounding writes; we
currently accept ~100%) and a **causal test** (A/B or pre/post — correlation is not proof).

---

## 3. The convergence — one loop, and we already own every piece but the front end

```
CLIENT ANSWERS            →  CONTRACT              →  EXECUTION        →  ASSURANCE        →  LEARNING
structured questionnaire     blueprint.yaml           connector runs      certify A1–A12      coverage + helpfulness
(ontology method)            (factory blueprint)      (existing)          (existing)          (AOR retooled + RMRR)
        ▲                                                                       │
        └───────────────── ranked gap list improves the next questionnaire ─────┘
```

**The insight worth defending:** the questionnaire and the acceptance test are *the same artefact*.
A field the client declares becomes an A9 semantic invariant. A field they do not declare cannot
silently appear in week six, because an undeclared field fails the contract on the first run.

Mapping, concretely:

| Client is asked | Becomes | Checked by |
|---|---|---|
| "What is one row of this feed?" (grain) | business key | **A10 source-agreement** |
| "Which fields must never be null?" | semantic invariant | **A9 semantic invariants** |
| "How fresh must it be?" | freshness bound | freshness tripwire |
| "How many rows do you expect per day?" | volume range | volume/variance tripwire |
| "Which report will you judge this on?" | consumer surface | **consumer-layer validation** (gate 2) |
| "What must be true for this to be done?" | acceptance assertion | `check_intake.py` acceptance block |

The last row already exists — a peer session added `check_intake.py` and `templates/intake.md`
today, with `acceptance: [{id, assert, check, fails_before, verdict}]`. **The portal is a rich UI
over that frontmatter.** That is the cheapest possible v1 and it does not invent a data model.

---

## 4. Architecture — five layers, and the diagram each one needs

| Layer | What it is | Diagram to draw |
|---|---|---|
| **L1 Elicitation** | the questionnaire; adaptive, schema-probing | **Form-to-contract flow** — question → frontmatter field → assertion id. One claim: nothing is asked that does not become checkable. |
| **L2 Contract** | `intake.md` frontmatter + `blueprint.yaml` | **Entity-relationship of the contract itself** — ticket → consumer → acceptance → check. Plus a **state machine**: DRAFT → AGREED → CERTIFIED → SUPERSEDED, with the transition conditions on the edges. |
| **L3 Execution** | connector → storage → warehouse → model | **Boundary-crossing flow** — what may and may not cross the client boundary; RLS drawn as a real line. |
| **L4 Assurance** | certify A1–A12, the four gates, CI | **Inverted-check chain** — where a gate can be bypassed, drawn as the path it actually takes. This is the diagram that finds the next `jq` bug. |
| **L5 Learning** | coverage, helpfulness, write gate, causal test | **The loop with the evaluator OUTSIDE it** — already drawn in Council Room. Add the write gate as the valve on the Store step. |

**Cross-cutting: one status vocabulary, everywhere.** Reuse the proven set —
`Live / Partial / Awaiting / Pending / Not-in-scope` (the CLIENT-A Delivery & Coverage report shipped
34/8/5/2/2). Do not invent a second one for the portal.

---

## 5. Pitfalls — each one already has evidence behind it

| # | Pitfall | Evidence it is real | Guard |
|---|---|---|---|
| P1 | **The portal becomes a fourth record system** | three ticket-record systems already disagree (wiki/tickets, docs/evidence, boot-prompts) | Portal **mirrors**; the record stays `docs/evidence/<TICKET>.md` in git |
| P2 | **A learning metric that measures repetition** | AOR's 18-point gap collapsed to ~0 within-topic | Every improvement claim uses the **within-topic fair test**; publish the reconciliation |
| P3 | **Popular-but-wrong knowledge gets amplified** | current rank ∝ `retrieval_count` alone | ship the **guarded helpfulness** formula before any ranking boost |
| P4 | **A gate that cannot fail** | `bash-guard.sh` exited 127, blocked nothing for months | every gate ships with a negative control; `install.sh` refuses to pass without it |
| P5 | **A generic questionnaire** | ontology assessment: 70–80% vs **30–40%** | questions must target entity types, relationships, roles, decision gates — and each must map to a check |
| P6 | **Research that never lands** | AB-01…AB-19 unabsorbed; R14 cited 7×, zero conclusions taken | no new lane without naming the answer that failed to cover it |
| P7 | **Client fatigue kills the form** | 20–30 questions is the stated design point | probe the live schema and ask them to **confirm**, not type; never ask what we can measure |
| P8 | **Correlation sold as improvement** | compounding note §9: needs A/B or pre/post | a causal test is a **phase exit criterion**, not a nice-to-have |
| P9 | **Building on an unbuilt tracker** | `data/tracker/` is empty but for PBI-EVAL | tickets live in `.data/tasks.jsonl` until Part A ships |
| P10 | **Concurrent sessions clobbering each other** | 5 sessions in one repo; a peer pushed my commits mid-session | worktree per lane before this scales |

---

## 6. Alternatives and trade-offs — the four real decisions

**D1 · Where the spec lives**

| Option | For | Against | Verdict |
|---|---|---|---|
| Git markdown + frontmatter *(recommended)* | already built, diffable, CI-checkable, no new store | not pretty for clients on its own | **take it** — the portal renders it |
| Database-backed portal | rich queries, workflow states | fourth record system (P1); needs migrations | later, if ever |
| Jira custom fields | client already sees Jira | schema rigid; no CI hook; wiki links banned | no |

**D2 · How the questionnaire is delivered**

| Option | For | Against | Verdict |
|---|---|---|---|
| Static form → git PR *(v1)* | trivial, auditable, zero infra | clunky for non-technical clients | **PoC** |
| Superset/portal page on existing auth | RLS + per-client auth already provisioned | some build | **v2 — the target** |
| Conversational intake (Zeus chat) | highest completion; adapts | free text must still land in frontmatter; hallucination risk | v3, behind a write gate |

**D3 · How much to auto-derive vs ask**

| Option | For | Against | Verdict |
|---|---|---|---|
| Ask everything | complete | P7 fatigue; 30–40% yield | no |
| **Probe schema, ask to confirm** | fastest, highest quality | needs source access at kickoff | **take it** |
| Derive from transcripts only | zero client effort | ontology work says needs curation | supplement, not source |

**D4 · The learning signal**

| Option | For | Against | Verdict |
|---|---|---|---|
| RMRR only | true outcome axis | no data yet; blind to gaps never retrieved | primary, once instrumented |
| Retooled AOR only | finds gaps; offline and cheap | availability ≠ helpfulness | secondary |
| **Both, on separate axes** *(as the note designs)* | complementary by construction | two pipelines | **take it** |
| Original AOR | already built | measures repetition (P2) | **rejected, in writing** |

---

## 7. Phases — each with an exit criterion that can fail

| Phase | Goal | Exit criterion |
|---|---|---|
| **P0 · Absorb** | close the gap between concluded and done | AB-01…AB-19 each **actioned or rejected in writing**; `docs/corpus/GAPS.md` exists |
| **P1 · Contract v1** | one client, one connector, end to end | a real `docs/evidence/<TICKET>.md` passes `check_intake.py --stage deploy`, and `certify` scores that connector A1–A12 |
| **P2 · Questionnaire** | 20–30 questions, every one mapped to a check | a filled form emits valid frontmatter **with no manual editing**; unmapped question count = 0 |
| **P3 · Portal v1** | client-facing render + submit | a client completes intake unaided; output lands as a PR; status renders in the five-term vocabulary |
| **P4 · Learning instrumented** | coverage + helpfulness live | write gate rejects a low-grounding write in a test; helpfulness formula ships **with** its guards |
| **P5 · Causal test** | prove improvement, don't assert it | pre/post or A/B on spec-completeness, reported **with** the within-topic control |

**Sequence rule:** P4 must not start before P1 and P2, or the loop optimises a spec that was never
mechanically checked — the same error as pointing an optimiser at prose gates.

---

## 8. Tickets

Created in `.data/tasks.jsonl` (append-only; this file is their body, matching the
`absorption-backlog.md` convention). Prefix `CIP-`.

| ID | Phase | Title | Depends on |
|---|---|---|---|
| CIP-01 | P0 | Action or reject AB-01…AB-19, each in writing | — |
| CIP-02 | P0 | Publish `docs/corpus/GAPS.md` from the existing corpus | CIP-01 |
| CIP-03 | P1 | Pick the pilot client + connector; record why | — |
| CIP-04 | P1 | Author the first real intake record end to end | CIP-03 |
| CIP-05 | P1 | Certify that connector A1–A12 against a recorded run | CIP-04 |
| CIP-06 | P1 | Add the recorded run to `evals/corpus/` + MANIFEST | CIP-05 |
| CIP-07 | P2 | Draft 20–30 questions on the four ontology dimensions | CIP-04 |
| CIP-08 | P2 | Map every question → frontmatter field → check; unmapped = 0 | CIP-07 |
| CIP-09 | P2 | Schema-probe so clients confirm rather than type | CIP-08 |
| CIP-10 | P2 | Form → frontmatter emitter, no manual editing | CIP-08 |
| CIP-11 | P3 | Portal render of intake + per-field status (5-term vocabulary) | CIP-10 |
| CIP-12 | P3 | Submit → PR → Jira, portal mirrors and owns nothing | CIP-11 |
| CIP-13 | P3 | Reuse `portal_provision.py` auth + RLS; no new auth model | CIP-11 |
| CIP-14 | P4 | Write gate: reject low-grounding writes; prove it rejects | CIP-05 |
| CIP-15 | P4 | Coverage metric (retooled AOR): question vs corpus, relevance-judged | CIP-11 |
| CIP-16 | P4 | Guarded helpfulness ranking; ship the guards, not the naive ratio | CIP-14 |
| CIP-17 | P4 | Negative control for every new gate in this plan | CIP-14 |
| CIP-18 | P5 | Within-topic fair test harness | CIP-15 |
| CIP-19 | P5 | Causal test: pre/post or A/B on spec completeness | CIP-18 |
| CIP-20 | P5 | Publish the reconciliation, including what did not replicate | CIP-19 |

---

## 9. The prompt

Run in a Claude Code session with cwd `C:\Users\PaulRussell\repos\agent-factory`.

```text
You are designing the Client Intake Platform. Read, in this order, before writing anything:

  docs/CLIENT-INTAKE-PLATFORM-PLAN.md      this file — the plan you are executing
  docs/CORPUS-AND-DESIGN-PROMPT.md         the sibling pass; do NOT duplicate its deliverables
  docs/absorption-backlog.md               AB-01..AB-19, the conclusions nobody actioned
  docs/research/SYNTHESIS.md §17           why absorption, not research, is the gap
  docs/findings.md                         F20..F76, corrected premises other lanes would repeat
  ../aldc-launchpad/workflow-kit/README.md the four gates, and the jq failure that motivated them
  ../aldc-launchpad/workflow-kit/templates/intake.md   the contract schema you are building a UI over

External corpora (read, do not re-research):
  ~/Downloads/26-05 Ontology Research/ALDC Ontology AutoGeneration Assessment.md
      → §"Source 2: Questionnaire" is the elicitation method. 70-80% vs 30-40% turns on
        question quality. Four dimensions: entity types, relationships, roles, decision gates.
  ~/Downloads/26-05 Compounding Research/.../AOR_RMRR_explainer_note_final.md
      → §3 the repetition confound and the within-topic fair test; §4 retooled AOR as coverage;
        §5 the GUARDED helpfulness formula. Never quote the naive ratio.

RULES, non-negotiable:
1. No new external research lane. If you believe one is needed, PROPOSE it and name which
   existing answer failed to cover it, by file and section. "We should research X" without
   that citation is the failure this pass exists to end.
2. Every gate you design ships with a negative control that proves it can fail AND proves it
   lets legitimate work through. A guard that blocks everything is as broken as one that
   blocks nothing.
3. Every number carries the command that regenerates it. Do not type a count you did not
   just measure. `workflow-kit/measure.py` is the pattern.
4. Label every claim OBSERVED / DERIVED / ASSUMED / MARKETED. A vendor claim is never a
   design premise.
5. Distinguish BUILT from RECOMMENDED from REJECTED in every diagram, and legend it. A plan
   drawn like a product convinces its own author.
6. The portal MIRRORS state. It never owns it. Three record systems already disagree.
7. Where you are uncertain, say NOT-SUPPLIED and name what was missing. Do not infer it.

DELIVERABLES, in order:
  1. A design doc per layer L1-L5 (§4), each with the named diagram, drawn as inline SVG with
     geometry computed from real numbers — not eyeballed.
  2. For each of P1-P5, the smallest thing that could prove the phase works, and what would
     falsify it.
  3. A revision of §5 pitfalls: which are now closed, which are newly visible, what evidence.
  4. Optimisations THIS plan misses — with the trade-off stated, not just the upside.
  5. Ticket bodies for CIP-01..CIP-20: acceptance criteria, evidence required, and the check
     that settles each one.

Begin by running `python workflow-kit/verify.py` and `python -m factory.certify
blueprints/windsorai_client_a.yaml --calibrate` in ../aldc-launchpad and here respectively, and
report what they actually say. Do not trust this file's claims about them.
```

---

## 10. What this plan does not know

- **Whether the client will complete a 20–30 question form.** ASSUMED from the ontology
  assessment's design point; never tested on an ALDC client. P3's exit criterion is the test.
- **Whether RMRR-style instrumentation transfers** from chat memory to delivery specs. The axis is
  the same (was a correction needed?), the unit is not. DERIVED, not observed.
- **Effort.** The ontology assessment's 8–12 weeks is for a full domain ontology with 10–30
  stakeholder interviews. A single connector spec is far smaller, but no ALDC figure exists.
  NOT-SUPPLIED — do not quote a timeline until P1 has produced one real record.
