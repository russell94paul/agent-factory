# Absorption backlog — the conclusions eighteen passes reached and nobody actioned

**Created 2026-08-29.** Source: `docs/research/SYNTHESIS.md` §17.9, *"What no section has ever
touched"* — a table this repo's own reconciliation pass produced on 2026-08-23 and which has sat
unconverted since. Every row below is a conclusion that reaches a mechanism or names a control, and
appears nowhere in the decision record.

**Why this file exists.** §17 measured the problem precisely: *"Seven sentences say an answer has not
landed. All seven are false."* The research is done. What was missing is anything standing between
"we concluded X" and "X got done". These are tasks in `.data/tasks.jsonl`; this file is their body,
because the task store carries a title and evidence refs but no description field.

## Schema, and why it is not the findings ledger's

`docs/findings.md` uses **BELIEVED / ACTUALLY / MEASURED BY / AFFECTS**. That schema is for a
*corrected premise* — something another lane would otherwise get wrong. These rows are not
corrections; they are conclusions that were never taken up. Forcing the ledger schema here would
produce four fields of which two are empty, so each entry carries:

| Field | Meaning |
|---|---|
| **SOURCE** | the answer document and section, so the reader can go to the original |
| **SAYS** | the conclusion, in the source's own words where possible |
| **WHY IT ISN'T FILLER** | what breaks, or stays broken, if this stays unabsorbed |
| **ACTION** | the smallest thing that would close it — including "reject it in writing" |

**A written rejection closes a row.** Silence does not. That distinction is the whole point: an
unabsorbed conclusion and a rejected one look identical in the record today.

---

## A · Controls the build order has no step for

### AB-01 — R3's expected-work manifest and `scope_hash`
- **SOURCE** R3, executive verdict; unabsorbed per §17.9.
- **SAYS** scope/evidence closure is *"the biggest missing control"*, because the six prescriptions
  *"can still report success over work they never knew existed"*. R3 derives `SUCCEEDED` from it.
- **WHY IT ISN'T FILLER** every gate we have measures the work it was told about. Nothing measures
  work that was never declared, so a team can pass by doing less than the task required.
  `SYNTHESIS.md` §5's nine-step build order has **no such step**.
- **ACTION** add the manifest + `scope_hash` as an explicit step in §5, or record in §5 why it was
  refused.

### AB-02 — R3's FACPR (first-attempt contract pass rate)
- **SOURCE** R3; unabsorbed per §17.9.
- **SAYS** report the pass rate of the *first* attempt, not the eventual one.
- **WHY IT ISN'T FILLER** without it, attempt 352 and attempt 1 score identically. Every efficiency
  claim the factory makes is currently unfalsifiable.
- **ACTION** add FACPR to `factory/metrics.py` beside the existing activity/outcome pairing.

### AB-03 — R3's budget proxy that owns the provider credential
- **SOURCE** R3; independently re-derived as §16.8's recommendation two days later.
- **SAYS** a token cap is advisory unless something that holds the credential enforces it.
- **WHY IT ISN'T FILLER** build-order step 1 is *"hard external attempt / spend / concurrency
  budget — non-negotiable"*. Today it is a number in a config an agent can exceed.
- **ACTION** design the proxy, or downgrade step 1's "hard" to "advisory" and say so.

### AB-04 — R3's corpus gate: 40 fixtures, 30 development + 10 held-out
- **SOURCE** R3; echoed by R1 (≥29), R8, and R10 (as a precondition of its own recommendation).
- **SAYS** the eval corpus needs 30 development and 10 held-out whole connectors.
- **WHY IT ISN'T FILLER** ⭐ the corpus is **one file, 6,747 bytes** (R16 audit §3.1). Four passes
  asked for this and *"no action among the eighteen names it."*
- ⚠ **RESTATED 2026-08-29 — this is a breadth task, not a sensitivity task. See F76.** The premise
  that the one-file corpus means *"the instrument has not been shown able to fail"* is **false** and
  was inherited by this very file when it was written. The contract is calibrated: all twelve
  assertions have a known-bad, enforced by
  `tests/test_connector_contract.py::test_every_assertion_has_been_proved_able_to_fail`, and
  `certify --calibrate` now returns `PASS (PASS=12)` — not the `UNMEASURABLE (PASS=11)` the README
  claimed until today. What one fixture cannot show is that the contract **generalises**: it has
  been replayed against one connector, and 48 have never been scored.
- **ACTION** score a **second** real connector end to end and add it to the corpus. That single step
  converts n=1 into evidence of generality and will find the assumptions baked into the windsorai
  fixture faster than manufacturing 38 more. Then work toward R3's 30 + 10.
- **DOES NOT BLOCK** the README's team/optimizer/UI precondition, which is met.

### AB-05 — R4's Fitness Qualification Gate
- **SOURCE** R4; unabsorbed per §17.9.
- **SAYS** five named pre-search tests — repeatability, known-bad sensitivity, known-good invariance,
  discrimination, holdout validity — each with an abort condition.
- **WHY IT ISN'T FILLER** §11.4 rejects gates-as-fitness and §16.6 corroborates, but **neither cites
  the gate design already written**. We argued a question that had a designed answer on file.
- **ACTION** read R4's design, then either adopt it or record why the rejection stands *against the
  actual design* rather than against a paraphrase.

## B · Assurance gaps

### AB-06 — R1's unintended-side-effect and reconciliation checks
- **SOURCE** R1, graded **High** among damaging omissions. ⭐ Rediscovered independently by R17 §4.7
  as *"none of these receipts describes what the agent did to a shared warehouse — the single biggest
  gap in the field's tooling for your use case."* Same gap, two arrivals, unconnected.
- **SAYS** correct landed rows are not enough if the agent also leaves duplicate loads, orphaned
  deployments, unintended tables or stale containers.
- **WHY IT ISN'T FILLER** two independent passes reached the same conclusion and neither is in the
  record. This is the check that would have caught the estate's own 4.86×-duplication near-miss.
- **ACTION** specify the side-effect check; add to the GreenContract assertion set.

### AB-07 — R1's `pass@k` vs `pass^k` reporting set
- **SOURCE** R1; unabsorbed.
- **SAYS** report both; they answer different questions about reliability.
- **ACTION** add to `factory/metrics.py`, or reject in writing.

### AB-08 — R2's build/run manifest schema and permission topology
- **SOURCE** R2; §17.4.
- **SAYS** the nine dimensions in §3.4 are R2's *list* — but the manifest that carries them, and
  **keeping the run record separate from the build record**, are not in the document.
- **WHY IT ISN'T FILLER** *"the build plane never runs a connector; the run plane never builds one"*
  is called the single most useful thing to understand about the system, and the record has no schema
  enforcing the separation. Also bears on the 0-of-15 version hash.
- **ACTION** write the manifest schema; state which plane owns each field.

### AB-09 — R16 outside: a container does nothing about prompt injection
- **SOURCE** R16 outside-evidence lane, §3.
- **SAYS** an allowlist without network isolation is not isolation, and **a container does nothing
  about prompt injection — the lethal trifecta survives it intact**.
- **WHY IT ISN'T FILLER** §13.7 adopted a sandbox move partly on isolation grounds. If the sandbox
  does not address the actual threat, the justification is wrong even if the move is right.
- **ACTION** narrow the sandbox claim to what it does defend, and name what still is not defended.

## C · Instruments and testing

### AB-10 — R5's property-based and differential testing
- **SOURCE** R5 §3; §10 took items 1, 2 and 5 only.
- **SAYS** property-based and differential testing are the answer to brittle instruments.
- **WHY IT ISN'T FILLER** F5 records **three confident false results from this repo's own instruments
  in a single session**. The instruments are the known weak point and the proposed fix is on file,
  unread.
- **ACTION** apply to the render/tracker probes first — the ones that produced the false results.

### AB-11 — R5's one canonical readout model, regenerated and diffed in CI
- **SOURCE** R5 §4.
- **SAYS** keep one canonical readout model; regenerate and diff it in CI.
- **WHY IT ISN'T FILLER** exactly the problem R13 run 2 later found shipping — **four page strings
  each asserting the page caches nothing**, while it caches.
- **ACTION** single source for readout strings; CI diff.

### AB-12 — R13 run 2: five of its six findings, untaken
- **SOURCE** R13 run 2; §13.6 took the switchboard settlement, §15.1 quotes it once.
- **SAYS** untaken: the four false *"nothing on this page is cached"* strings; the cache fingerprint's
  live stale-green holes (`scripts/` is not in it though the suite imports it; the environment is not
  in it, which **reintroduces F72 verbatim**); the duplicate `measure()` per render; *"the extension is
  admissible only when it can subtract the tracker's emitter"*; ⭐ **APPROVE leaves the building and
  becomes a GitHub PR**; and retire `orchestration-bench.html`.
- **WHY IT ISN'T FILLER** the APPROVE finding removes the very plane §14.2's platform argument was
  justifying. A settled platform question may rest on a premise a later pass refuted.
- **ACTION** take each of the five separately; the APPROVE one first, because a decision depends on it.

## D · State, memory and the record

### AB-13 — R10: retire or merge at least one of the six overlapping stores
- **SOURCE** R10 §7. R16 §3.4 flags that a5 took *"skills over corpus"* and dropped the
  recommendation it sat inside.
- **SAYS** *"We already have **six** overlapping stores… adding a seventh would be a mistake…
  retire or merge at least one."*
- **WHY IT ISN'T FILLER** bears directly on §16.10's ledger split and on R18's enumeration of shared
  state. We have since been designing new stores against a recommendation to reduce them.
  ⚠ Separately, R10 attributes its strongest figure (32% → 55%) to two different authors in one
  source list — treat R10's numbers as unverified.
- **ACTION** enumerate the six, pick one to retire or merge, and do it before any new store lands.

### AB-14 — R8's record/channel answer was wrong and the refutation is unattributed
- **SOURCE** R8 §2; refuted by §16.10.
- **SAYS** R8 answered the record/channel question with *"event sourcing… like CQRS"*. §16.10 refutes
  it as **"neither"** — but presents the question as one *"asked in session"*, never recording that a
  pass had already answered it wrongly.
- **WHY IT ISN'T FILLER** the record does not show that a research pass got this wrong, so the same
  wrong answer can arrive again from the same source.
- **ACTION** file the refutation against R8 explicitly.

### AB-15 — R12's productivity list
- **SOURCE** R12 §4.4; unabsorbed.
- **SAYS** prompt templates, session forking and its token cost, cross-session search, checkpoints, a
  prepared prompt queue — each tiered.
- **WHY IT ISN'T FILLER** this is the closest thing on file to the session-consolidation problem that
  prompted this backlog.
- **ACTION** tier them against current pain; cross-session search looks highest-value.

## E · Whole answers never absorbed

### AB-16 — R14, in its entirety
- **SOURCE** §17.2 — *"1,389 lines, seven mentions, and not one conclusion taken."*
- **ACTION** read it and either absorb its conclusions or **reject it in writing**. Either closes
  this; neither has happened.

### AB-17 — R18, in its entirety
- **SOURCE** §17.3 — it exists, and every reference to it in the synthesis is in the future tense.
- **ACTION** as AB-16.

### AB-18 — R16 audit's nine findings are bare pointers
- **SOURCE** §15.3 lists nine findings **with no content**.
- **SAYS** the substance is missing: a14 merged with a3 into a `Decision`, a1's honest state, a4's
  real evidence, a6's disconnected producer, a13 as a ranking-with-a-precondition rather than a
  decision, and the whole of §4's ordering.
- **ACTION** fill in the nine, or delete the pointers so the record stops implying they were handled.

## F · The argument the record only heard one side of

### AB-19 — Settle the alerting question honestly
- **SOURCE** §17.9's closing paragraph.
- **SAYS** five positions exist across five answers: **R6 §4** (fatigue is real; alert only on the
  actionable) → **R12 §4.2 / R13 §6** (absence, not fatigue; must interrupt) → **R13 run 2 §3**
  (measure whether it fired at all, first) → **R16 outside §2** (the inverted-U: *"escalating
  everything is strictly worse than the optimum"*) → **R17** (same paper, independently).
- **WHY IT ISN'T FILLER** §14.3 records the middle pair as *"three passes and one measurement agree —
  stop asking and build it"*; §15.5 then retracts the independence. **R6's position — filed first, and
  on the same side as the strongest external finding — is nowhere.** Two sources agreed and were
  counted; the two agreeing with the inverted-U were not.
- **ACTION** re-decide with all five positions on the table, and record the decision with its dissent.

---

## Closing rule

A row closes when its **ACTION** is done *or* when a written rejection exists naming the row. Both
outcomes are progress. What is not progress — and what produced this file — is a row that is
mentioned in a synthesis and mistaken for one that was handled.
