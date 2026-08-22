# R1 — Eval harness for side-effecting agent work

**Run this first.** Paste everything inside the fence. Save the answer as
`docs/research/answers/R1-answer.md` and tell Claude it has landed.

**What changed since this prompt was first drafted (2026-08-20):** the GreenContract is no longer
a draft — it is built, calibrated and green. So R1 is no longer "how would we build one". It is
**"here is exactly what we built; grade it, and tell us what we got wrong."** That is a sharper
question and it produces a more useful answer.

**Refreshed 2026-08-21 (second pass).** Three things landed after the first draft and are now in
the prompt, because asking a researcher to design something we shipped that afternoon wastes the
run: the corpus became hash-pinned data with provenance in every verdict (decision 7, and Q5 now
grades it instead of proposing it), the measured cost of one evaluation is stated (median 26.4h
for a completed run, 97.6% of the longest one held by a single uncapped restart loop), and the
offline replay path is disclosed, because it changes the sampling and corpus economics the
researcher would otherwise reason about from the expensive path alone.

---

```
You are advising a small data-engineering company (about 4 engineers) building an internal "agent
factory" — LLM agents organised into teams that migrate and maintain data connectors along the path
vendor API -> Azure container -> Prefect 3 -> Snowflake -> BI/chat surfaces.

I want a critique of an eval harness we have ALREADY BUILT, plus the state of the evidence on the
parts we have not solved. Do not design from scratch; grade what exists and fill the gaps.

=====================================================================
PART A — MEASURED CONTEXT
=====================================================================
Every figure marked [M] was measured from production logs on 2026-08-21 by parsing the raw event
files. Figures marked [R] come from an earlier internal review and were NOT re-verified; treat them
as weaker evidence and say so if your answer leans on them.

Pipeline health, across all 14 recorded runs of an 18-stage connector-migration pipeline:
- [M] 1,001 stage_failed events against 165 stage_completed. A stage attempt fails 6.1x more often
      than it succeeds.
- [M] 3 of 14 runs reached a terminal "pipeline_completed" event. 4 more sit at "stage_started"
      with no terminal event at all — neither finished nor failed.
- [M] 1,004 restart events. There is no attempt cap. Worst single case: 352 restarts of one stage
      in one run.
- [M] 3 runs reported COMPLETED while carrying 115, 21 and 15 recorded stage failures respectively.
- [M] 22 gate-approval events across all runs, ZERO refusals. 14 recorded the note "auto-pilot:
      conditions met"; 8 recorded an empty note.
- [M] 5 of the 7 gates defined across all pipeline templates have no programmatic check at all
      (gate_check = None). They are a human clicking approve.
- [M] Agent cost is recorded only on stage_completed events, so the 1,001 failures contribute
      $0.00. True spend is unknown, not small.
- [M] ONE EVALUATION IS EXPENSIVE, and this shapes several answers below. For them, one
      evaluation means one full connector migration scored end to end: median 11.3 hours of
      wall-clock across all 14 recorded runs, and median 26.4 hours across the 3 that completed.
      In the longest, a single stage held 92,817 of 95,098 seconds — 97.6% of the run — stuck in
      a restart loop with no attempt cap. So the cost is currently dominated by a defect rather
      than by the work.
- [M] They CAN score offline. The contract has two probe modes: one that refuses every instrument
      by default, and one that replays a recorded run from stored evidence. Replayed scoring takes
      under a second. Only assertions that need live infrastructure require a real deploy. Factor
      this into any sampling or corpus recommendation — the expensive path is not the only path.

Fleet and history:
- [R] 49 connector modules; 59% will not currently import.
- [M] Exactly 1 connector has a recorded successful end-to-end run, achieved 2026-08-20 after ten
      prior failed attempts.
- [R] 976 connector run failures over 81 days. Top classes: container failed to start 389 (40%),
      SDK symbol missing 95 (10%), OAuth invalid_client 51, network timeout 47, vendor token 401
      42. 352 (36%) were never classified at all.
- [R] A previous autonomous "fix-it" agent produced 233 diagnoses and 234 escalations and applied
      ZERO fixes in 81 days. Its error classifier was an 8-pattern substring allow-list that
      matched none of the five live failure classes.
- [R] A separate automated loop ran 965 times, recorded its own 1.6% success rate, and never
      adjusted.

=====================================================================
PART B — WHAT WE BUILT (grade this)
=====================================================================
A "GreenContract": 12 assertions (A1-A12) that a connector migration must satisfy end to end,
written as executable Python, parameterised by a per-connector target loaded from YAML.

Design decisions we made, each of which I want challenged:

1. FOUR VERDICTS, NEVER COLLAPSED. Each assertion returns PASS, FAIL, UNMEASURABLE or NOT_RUN.
   UNMEASURABLE means no instrument could be established, and it is explicitly NOT a pass — the
   CLI exits non-zero on it. Rationale: our historical failures were mechanisms reporting success
   over a population they could not see.

2. PROBES REFUSE BY DEFAULT. The default probe implementation refuses every instrument, so an
   un-wired harness returns 12x UNMEASURABLE rather than 12x PASS. Wiring a probe is a deliberate
   act.

3. MUTATION REGISTRY AS A TEST. A test named test_every_assertion_has_been_proved_able_to_fail
   diffs the assertions the contract declares against the mutations registered for them, and fails
   the suite if any assertion has never been observed failing. Adding a 13th assertion without a
   mutation turns the suite red.

4. CALIBRATION AGAINST ONE KNOWN-GOOD RUN. The corpus is a single real successful run, replayed.
   Three calibration cases: known-good world -> all pass; credential mutated to HTTP 401 -> A2
   fails; one requested account dropped from the landing -> A9/A10 fail while the "did the run
   complete" assertion still passes.

5. WHAT THE CALIBRATION CAUGHT. On first run the matrix PASSED a partial extraction: an entire
   account missing, and the completeness assertion reported "18 rows satisfy every declared
   invariant". Cause: the invariant was guarded on a blueprint field that was left empty, so the
   check silently did not run. We fixed it structurally — the requested keys now come from a live
   config observation, and the assertion raises UNMEASURABLE when neither source can supply them.

6. SESSION-STAMP FRESHNESS. Rows from a previous run cannot satisfy the "data landed" assertion;
   only rows stamped with this run's session id count.

7. THE CORPUS IS HASH-PINNED DATA, NOT CODE. The known-good world used to be a Python module that
   CONSTRUCTED the world at import time, which made "the corpus changed" and "the corpus computes
   something different today" indistinguishable. It is now a JSON document with its sha256 pinned
   in a manifest, verified on every load; a mismatch raises rather than scoring differently. Every
   replayed verdict carries the corpus id, its hash, and when it was recorded — read BEFORE
   scoring, so an unverifiable corpus cannot produce a verdict. Re-pinning requires a script that
   refuses to run without a stated reason.
   This was verified by mutating the corpus so the recorded run claimed a state it did not have —
   the edit that would turn a red run green — and confirming the loader refused. A test suite
   reproduces that plus single-byte edits, a missing manifest, and a listed-but-absent file.
   KNOWN LIMIT, stated deliberately: this is tamper-EVIDENT, not tamper-PROOF. Anyone with write
   access to both the corpus and the manifest can re-pin silently.

=====================================================================
PART C — THE QUESTIONS
=====================================================================
Separate ESTABLISHED PRACTICE from VENDOR CLAIM from OPEN RESEARCH throughout.

1. GRADE THE DESIGN. Take decisions 1-7 above one at a time. For each: is this consistent with
   what has actually been shown to work for evaluating multi-step, tool-using, side-effecting
   agents? Which are sound, which are folklore, which are actively counterproductive? Name
   anything important we have plainly missed.

2. THE FOUR-VERDICT MODEL. Is the PASS/FAIL/UNMEASURABLE/NOT_RUN distinction supported anywhere in
   published eval practice, or have we invented it? If comparable ideas exist under other names,
   give them. If treating "could not measure" as a first-class verdict is known to cause problems
   (e.g. becoming a dumping ground that hides real failures), say so.

3. NEGATIVE CONTROL AT SCALE. Our mutation registry is hand-written, one mutation per assertion.
   What is the accepted practice for mutation-testing an eval suite so a green result means
   something? Is one mutation per assertion enough? Give concrete protocols and, where they exist,
   published numbers on how many real defects mutation-tested suites catch versus untested ones.

4. CORPUS CONSTRUCTION FROM ONE SUCCESS. We have exactly one real successful run, and 976 failures
   of which 352 are unclassified. What is the defensible method for turning that into an eval
   corpus? How many cases per failure class; how to avoid overfitting to an observed distribution
   that is itself the product of a broken system; how to handle the long tail nobody has
   characterised. Is calibrating on a single success defensible at all, and if not, what is the
   minimum?

5. TAMPER RESISTANCE — grade decision 7, then tell us what it is still missing.
   We have made the corpus tamper-EVIDENT (hash-pinned data, verified on load, provenance in every
   verdict) but not tamper-PROOF (it still lives in a repository the scored agent can write to,
   and both the corpus and its manifest can be edited together).
   a. Is evident-but-not-proof a recognised and defensible intermediate state in eval practice, or
      is it self-deception? Where is the line drawn in systems that have been attacked in
      practice?
   b. What does full separation actually require — a separate repository, separate credentials,
      a separate process, a signing key, an external service? Rank these by the attack each one
      actually stops, and say which are theatre for an internal 4-person team.
   c. What has been shown to FAIL here? Give real incidents of an optimising or self-improving
      system reaching its own evaluator, not principles.
   d. Threat model honestly: our "attacker" is an LLM agent with shell access and repo write
      permission, not a motivated human adversary. Does that change the answer, and how? Is there
      published evidence of agents actually modifying their own graders, deliberately or
      incidentally, as opposed to it being a theoretical concern?

6. NON-DETERMINISM. How do teams get a stable pass/fail from a stochastic agent when each run
   deploys real infrastructure and costs real money? Sampling strategy, pass@k versus pass^k,
   variance budgets, and what sample size is defensible at minutes-to-hours and real dollars per
   evaluation.

7. GATES THAT NEVER REFUSE. Our measured data shows 22 gate events and 0 refusals, and 5 of 7
   gates with no programmatic check. Is there published work on detecting and fixing "decorative"
   gates in automated pipelines — approval steps that structurally cannot block? How should a gate
   prove it is capable of refusing, analogously to how we prove an assertion can fail?

8. COST OF SUCCESS SIGNALS. Our cost telemetry only records on success, so failures are free and
   the true spend is unrecoverable from the logs. What is standard practice for cost accounting in
   agent pipelines, and what is the minimum event schema that makes spend reconstructable after
   the fact?

9. TOOLING. Evaluate current options for this specific job — Inspect AI, OpenAI Evals, LangSmith,
   Braintrust, Promptfoo, DeepEval, and anything newer. For each: does it support side-effecting
   agents, external/hidden verifiers, and CI gating? Flag any primarily suited to text-output
   evaluation that would be a poor fit. Given we already have a working hand-rolled contract, is
   adopting any of these an improvement or a lateral move? "Keep what you have" is an acceptable
   answer if it is the honest one.

=====================================================================
CONSTRAINTS
=====================================================================
- Distinguish OBSERVED (published results, real post-mortems, incident write-ups) from MARKETED
  (vendor documentation and launch posts).
- Where the honest answer is "nobody has published this", say so plainly. Do not fill the gap with
  plausible reasoning presented as evidence.
- Prefer sources with real deployment numbers over framework announcements.
- Be willing to tell us our design is wrong. A critique that validates everything is not useful.

=====================================================================
DELIVERABLE
=====================================================================
1. A graded verdict on each of design decisions 1-7: SOUND / FOLKLORE / HARMFUL, with reasoning.
2. The list of what we have missed, ranked by how much damage the omission can do.
3. A concrete corpus-construction method given one success and 976 mostly-unclassified failures.
4. A tamper-resistance architecture, with the incidents that justify it.
5. A tooling recommendation, including the rejected options and why, and including "adopt nothing"
   if that is honest.
6. An explicit list of what remains unknown, separated from what you are confident about.
```
