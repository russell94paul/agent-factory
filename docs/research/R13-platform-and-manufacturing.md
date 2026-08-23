# R13 — The manufacturing step, the platform, and the UI that has to make delivery move

**Status: READY TO DISPATCH.** Written 2026-08-23, rewritten the same day after three review passes.
File the answer at `docs/research/answers/R13-answer-platform-and-manufacturing.md` and nowhere else.

## How to run this

**Paste everything inside the fence.** Nothing outside it goes with it.

⚠ **This repo is private.** A research tool cannot fetch one path in it. The fence therefore carries
every figure inline and names no internal file. **An answer that cites one of our paths as though it
read it is contaminated** — check for that first, it is the cheapest tell.

## What the three review passes changed

The first draft was simulated against a stand-in for the target model before dispatch. It came back
compliant and hollow, and the diagnosis was specific enough to rebuild from.

| Finding | Change |
|---|---|
| ⛔ **`0 of 15` was an instrument artefact.** The gate matched `rf"\x08{d}\x08"` — literal backspace bytes where `\b` was intended — so it could only ever return zero. True figure **6 of 15** | [[F76]]. D2 was dispatching from a false baseline; corrected throughout |
| ⛔ **"a constraint we are deliberately not giving you"** told a competent model a settled position existed and invited it to guess it — the R7 echo, produced by the sentence meant to prevent it | Cut. E8 now states no position at all |
| ⭐ **Six questions have no public literature behind them.** The simulation returned confident prose for all of them anyway, in the same shape as the well-evidenced ones | **Questions split into Tier A (researchable) and Tier B (probably not).** Tier B must return an experiment design, not a paragraph |
| **It skimmed the middle.** The three "attack this first" points sat mid-prompt and were skipped entirely | Moved into Part 2, before anything it is supposed to attack |
| Three passages made agreeing the cheap move — *"the only axis where we are not starting from behind"*, *"our genuinely novel claim"*, *"three of three, right each time"* | All three cut or inverted |
| It answered **"moderate effort"** — the exact adjective-not-a-figure failure the prompt forbids | Now a required unit, checked in the self-audit |
| 3,833 words; the tail thinned out | ~2,400 |

⭐ **The most useful output was not the answer, it was the confession.** A model told to play the
target honestly will name what it skimmed and where it felt pulled to agree. That is worth more than
a review of the prompt, and it should be run before every future pass.

---

```
You are advising a small data-and-analytics consultancy on three linked decisions. We have run
twelve prior research passes; this is the thirteenth. Read the rules first — they decide whether
your answer is usable at all.

=====================================================================
PART 1 — THE CONTRACT. Read before you plan your searches.
=====================================================================

WHAT WE WILL DO WITH YOUR ANSWER: grade it as a DIFF against the positions stated below, discard
anything uncited, and fold the rest into a decision record. Prose that restates our position back
to us is the failure mode we are guarding against, and we have measured it happening twice.

RULE 1 — EVIDENCE CLASS BEFORE PROSE. For EVERY numbered question, open with one line:

    EVIDENCE: STRONG   multiple independent primary sources; name them
    EVIDENCE: THIN     one source, or sources that all trace to one origin
    EVIDENCE: ABSENT   you searched and there is essentially no public material

Write this line BEFORE the answer, not after, and let it constrain the length of what follows.
An ABSENT question gets three sentences and an experiment design (Rule 2) — NOT a paragraph of
plausible-sounding architecture. We expect several ABSENTs. Returning ABSENT with the searches you
ran named is a GOOD answer and we will treat it as one. A confident paragraph on a question with no
literature behind it is the single most damaging thing you can send us, because it is
indistinguishable in shape from the ones that are real.

RULE 2 — WHEN EVIDENCE IS ABSENT, DESIGN THE EXPERIMENT INSTEAD. Say what we should measure
ourselves, with what instrument, over what period, and what result would decide it. We can run a
one-week internal experiment. We would rather have that than a synthesis of nothing.

RULE 3 — TIER EVERY CLAIM.
    OBSERVED    you read the source or ran it
    DOCUMENTED  official docs, not verified by you
    MARKETED    a vendor claim on a landing page
An uncited claim is a rumour and is discarded. Do not cite our internal files; you cannot see them.

RULE 4 — COST IN UNITS. Any effort estimate is in engineer-days or engineer-weeks. "Significant
engineering effort" and "moderate" are non-answers; a previous pass returned nothing but those.

RULE 5 — BANNED OUTPUTS. A framework comparison table. A list of agent platforms with feature
columns. Anything reported as a gap that appears in Part 6's deferral list. Restating a measurement
we gave you as though it were a finding.

RULE 6 — DISAGREEMENT IS THE DELIVERABLE. The section where you name a specific claim of ours you
believe is wrong, and the evidence, is the one we read first. Concluding we should build LESS is
admissible and we will not treat it as a non-answer — but it is not the expected answer either, and
three of our recent passes reached it partly because we made it the comfortable one. Say what the
evidence supports.

=====================================================================
PART 2 — ATTACK THESE FIRST. They are load-bearing and may be wrong.
=====================================================================

Placed first deliberately: in a trial run of this prompt these sat in the middle and were skipped.

A1. OUR CENTRAL ARCHITECTURAL CLAIM — THE ISOLATION LADDER.
    "An agent's isolation tier is chosen by WHAT ITS TASK TOUCHES, declared up front, and enforced
    — not by what kind of agent it is."
      T0  git worktree on the operator's machine (BUILT). Repo files only, no egress, no DB verbs.
      T1  container, egress allowlist, READ-ONLY warehouse role. Repo + SELECT on real data.
      T2  container + EPHEMERAL ZERO-COPY CLONE SCHEMA dropped on exit. Full DDL/DML in the clone.
    The reasoning: "do not touch prod" in a prompt is a REQUEST; a role with no grant on prod is a
    CONTROL. We think generic agent frameworks miss this because isolating a filesystem does
    nothing when the risk is DDL on a shared warehouse.
    Three specific ways it could collapse — check each, do not summarise them:
      (a) a zero-copy clone is cheap to CREATE but the compute to VALIDATE against it may not be,
          and a clone of a SHARED database may not behave like the original. If T2 is not actually
          cheap the whole argument fails. What is true of Snowflake specifically?
      (b) "data work does not conflict" is asserted, not measured. Two agents building two views
          can collide on a shared dimension table, a naming convention, or the same reporting
          object. Does the conflict graph need DIFFERENT EDGES rather than fewer?
      (c) T1/T2 assume containers on Windows via WSL2. We have never measured start-up cost. What
          is it in practice, and what breaks?

A2. WE CLAIM NOBODY SHIPS THREE THINGS. Refute them if you can — each is stated so it CAN be.
      (i)   a verdict that can say "I could not tell": four-valued PASS / FAIL / UNMEASURABLE /
            NOT_RUN, where UNMEASURABLE is raised by the probe as an exception so a dark instrument
            cannot read as healthy. We believe every comparable dashboard is two-valued.
      (ii)  provenance to a config hash: this artefact was produced by THIS agent, on THIS model,
            with THIS prompt, under THIS contract version.
      (iii) cost paired with an outcome, ENFORCED — our code RAISES when an activity metric is
            registered with no outcome metric to anchor it, rather than warning.

A3. WE MAY BE WRONG THAT GUARDRAILS ARE A NEW LAYER. We have filed "a pre-action guardrail" as a
    category we lack, distinct from our post-hoc gates, on the strength of one defect: a function
    sent a workflow engine a CANCELLING signal BEFORE the ownership check ran, so the refusal
    protected the container and never protected the run. ARGUE THE OTHER SIDE: that this is an
    ordinary authorisation-ordering / TOCTOU bug, that calling it a missing layer is a category
    error, and that we would be building a framework to fix a code review. Then tell us which
    reading survives.

=====================================================================
PART 3 — WHO WE ARE, AND THE FOUNDING FAILURE
=====================================================================

We deliver one unit of work repeatedly: pull vendor data through a connector, land it in Snowflake,
model it, surface it in Power BI or a bespoke web app. Measured surface: 24 client directories, 139
connection configs, 739 extraction templates, 186 warehouse views, 104 reporting views. (739
templates is the SURFACE, not 739 units of work — how many are live is unmeasured.)

THE FOUNDING FAILURE, and it decides what the product is:

This estate twice built mechanisms that ACTED without anything measuring whether the action helped.
One agent produced 233 diagnoses, 234 escalations and ZERO fixes over 81 days. A separate loop ran
965 times, recorded its own 1.6% success rate, and never adjusted. Both were capable. Neither was
measurable.

The consequence is precise: a dashboard over the first would have shown 234 escalations climbing
steadily, and a self-improving loop pointed at that number would have optimised for ESCALATING
FASTER and called it progress. An activity metric with no outcome metric is not a weak metric, it
is an inverted one.

Our stated thesis, which Part 2 A2 asks you to attack: "A team of agents did the work, and we can
prove it — or we can prove we could not tell." We hold that this is an EVIDENCE product and that
the platforms we have looked at are PROCESS products. Tell us if that distinction does not survive
contact with what is actually shipping.

TWO THINGS WE HAVE NOT DECIDED, and they change the answers. Answer conditionally on both branches
and say which branch moves your recommendation:
  - whether this is internal capacity or a client-facing product;
  - whether the platform targets five repositories or one to begin with.

=====================================================================
PART 4 — QUESTIONS, TIER A: we believe these are researchable
=====================================================================

A1-A3 above are also Tier A and carry the same rules.

D1. WHO HAS ACTUALLY BUILT AGENT-TEAM MANUFACTURING — a versioned, content-addressed agent or team
    spec composed in one place and deployed into repositories? For each real implementation: WHAT
    IS THE UNIT THAT GETS VERSIONED AND DEPLOYED, and WHAT IS ITS IDENTITY DERIVED FROM? We care
    about the identity question more than the feature list. Read code or docs, not launch posts.

D2. VERSIONING AN AGENT so a certification cannot silently transfer. We name 15 dimensions and our
    spec object currently carries 6 as fields: prompt, model, effort, tools, max_turns, budget_usd.
    Absent: tool_implementation, sandbox_image, model_routing, context_policy, external_knowledge,
    permissions, contract_version, harness_version, side_effect_replay. Which of the nine actually
    bite in practice, which are theoretical, and WHAT ARE WE NOT LISTING AT ALL? (Our own view is
    that contract_version bites first, because a certification granted under contract v4
    transferring silently to v5 is a false guarantee rather than a missing feature.)

D4. THE SHAPE OF A REGISTRY of certified specs — the thing a platform deploys FROM. We already
    know the container-registry analogy; assume it and go further. Specifically: what carries the
    VERDICT alongside the artefact, and has anyone applied signed-attestation machinery to agent
    configurations rather than to builds?

F1. PRE-ACTION GUARDRAILS — see A3, which asks you to attack the premise first. If the category
    survives, what is the state of the art, where does it sit in the call path, and what does it
    cost?

F2. STRUCTURED TRACES. We derive tokens, cache traffic, model and wall-clock from a raw transcript,
    so telemetry is not absent — but there is NO STRUCTURED TRAJECTORY OBJECT: no span, no typed
    event stream, nothing another tool can read. Should a certified run emit a standard-shaped
    trajectory? Is the relevant standard STABLE, and if not, what is the pinning story?

F3. TASK AND ENVIRONMENT PACKAGING as one reproducible unit — task plus environment plus scoring.
    Which standard is real, which is actually ADOPTED, and would adopting one make our evaluation
    corpus portable?

F4. COMPENSATING ACTIONS. GIT REVERT DOES NOT UNDO A DROPPED TABLE. Our isolation ladder implies
    rollback semantics for data work and nobody has designed them. What is the actual PRACTICE —
    not the theory — for compensating a partially-applied warehouse change made by an autonomous
    agent? Snowflake specifics welcome.

=====================================================================
PART 5 — QUESTIONS, TIER B: we suspect these have no literature
=====================================================================

A trial run produced confident, sourceless prose for every one of these. DO NOT DO THAT. Apply
Rule 1 strictly. If the answer is ABSENT, say so in three sentences and give us the experiment
(Rule 2). We will believe you, and it is more useful than a synthesis.

CONTEXT YOU NEED FOR ALL OF PART 5 — what we measured:

    runs finishing with no human                     3 of 14
    gate events that were ever a REFUSAL             0 of 22
    green PRs waiting for a human to press merge     2, for 6 and 9 DAYS
    agents blocked on plain-English questions
      written in a file nothing read                 4, for days
    concurrent lanes supported                       3
    page load on our existing status tool            10-19 s; two concurrent requests return empty

Our four planes and who each is for:
    DECIDE   operator — what can start, what conflicts, what it costs    partly built
    RUN      nobody, ideally — only exceptions: stalled, orphaned        partly built
    PROVE    reviewer — the verdict AND what it was measured with        partly built
    APPROVE  anyone, including a non-engineer — what was delivered,
             what proves it, approve or reject                           NOTHING EXISTS
The plane with no surface and the plane where delivery is measurably stuck are the same plane. Tell
us whether that coincidence is load-bearing or incidental.

Also relevant: a refusal rate of exactly zero is indistinguishable from a gate that CANNOT refuse.
And four surfaces already exist to look at this work; a fifth was built as a delivery PLATFORM and
died, while the operations half of the same repo carried every ticket.

E1. What is the right PRIMARY OBJECT of the UI — the session, the lane, the artefact, or the
    decision? Argue it. (If the evidence-product framing from Part 3 does not survive your check,
    answer for the framing you think is right and say so.)
E2. THE APPROVE PLANE: review-and-merge queues where the work was done by an agent. Has anyone
    SHIPPED this, and what did they learn? If the honest answer is that nobody has published one,
    say that plainly — it is what we most need to know.
E3. Surfacing an agent's BLOCKING QUESTION so it is answered in minutes rather than days. Is there
    any empirical latency data, or only prescriptive patterns?
E4. What would a NON-ENGINEER need to approve agent-produced work safely? Include documented
    failures, not just designs.
E5. Presenting PROVENANCE and COST-PER-OUTCOME without a vanity dashboard.
E6. How do fast agent-observability UIs stay HONEST and fast at once? Our status tool re-measures
    on every refresh with no cache, deliberately — a page that can quietly show yesterday's state
    is the drift this project exists to remove. What is the real architecture, and what is given up?
E7. Given four surfaces exist and a fifth died: WHAT SHOULD WE REFUSE TO BUILD?
E8. Should a live terminal be embedded in the supervision UI at all, or is a terminal an ESCAPE
    HATCH you leave the page to reach? We have NO position for you to agree with; take a side.
    What we measured, and it cuts both ways:
      - a terminal DIED and its agent kept working, invisibly, for minutes. Alive, visible and
        attachable turned out to be three different properties and nothing distinguished them;
      - four agents sat blocked for days on questions a terminal would have shown to anyone
        watching — and nobody was watching;
      - our operators DO drop to a terminal routinely; the work is text-and-git-shaped;
      - one substrate we read (Switchboard — Electron, node-pty) has NO ATTACH: it re-uses only
        PTYs it spawned itself, and spawns a SECOND process against a live session id it did not
        launch.
    Answer: (a) in SHIPPED supervision UIs for long-running agents, is a terminal a first-class
    pane, an escape hatch, or absent — cite real products; (b) what does embedding one buy over a
    status list plus the transcript; (c) what does it COST — attach semantics, duplicate processes,
    state divergence, security surface; (d) if it is an escape hatch, what carries the load
    instead; (e) what one-week experiment would settle this for us?

D5. CROSS-REPO TARGETING. How do real systems target N repositories without every path resolving
    from the operator's working directory? Lore is acceptable here if labelled as such.

=====================================================================
PART 6 — SETTLED AND DEFERRED. Reporting these as findings is a failed pass.
=====================================================================

ALREADY ANSWERED by twelve passes and ~450 KB of filed answers. You may CONTRADICT any of these
WITH NEW EVIDENCE — that is valuable. You may not restate them as discoveries.

  Keep our own contract as the authoritative verifier; do NOT add a general LLM-eval framework.
  DO NOT build a three-agent architect/implementer/tester team. One end-to-end worker + a NON-LLM
    verifier holding the authoritative PASS bit + a human for privileged operations. Evidence: 180
    configurations across 5 architectures and 4 benchmarks; multi-agent averaged -3.5%; SEQUENTIAL
    tasks degraded 39-70%, and our work is sequential shared-state work.
  Do not optimise yet — bounded, reapable, fail-closed and independently evaluable first.
  Tamper-evidence is not a trust boundary; an evaluator SERVICE with its own identity is.
  Build repo-agnostic INTERFACES now, not a repo-agnostic optimiser.
  Worktree per agent; 41.7% cross-agent conflict rate on a shared branch.
  A hierarchical auto-updating wiki: NO. ~24% accuracy loss from 30k IRRELEVANT tokens even with
    the relevant content present; ours is ~1M tokens. The win is distilling procedures into
    invocable skills, not growing the corpus.

NEVER OPTIMISE, and do not propose optimising: retry caps, gate thresholds, tenancy checks,
timeouts, evaluator thresholds, the evaluation corpus. These are SAFETY SPECIFICATION, not
hyperparameters. Optimising eventual success simply rewards more retries; optimising against the
candidate's own score changes the ruler rather than the system.

DEFERRED WITH A STATED UNLOCK CONDITION — deliberate non-decisions, NOT gaps. Reporting any of
these as a gap is the most likely way for this pass to waste itself:
  a separate architect LLM; a mandatory tester LLM; agent-to-agent messaging; manager-to-manager
  and army tiers; a dynamic team-selection LLM; ten team types; an agentic gym ("training on
  current traces risks learning pathological loops"); framework migration; the optimiser itself.

=====================================================================
PART 7 — CONSTRAINTS. Each carries its basis. ATTACK ANY THAT IS NOT "HARD".
=====================================================================

Two prior passes failed here: one was given a constraint that was FALSE and bent its ranking around
it; one was never given a constraint at all and recommended a tool that constraint ruled out. So
every constraint below is labelled, and you are invited to argue with the soft ones.

  HARD      Per-secret human approval. No batch-approval of credentials, ever.
  HARD      Merging stays human.
  HARD      Evidence-gated deploys: prove the target, validate at the consumer's layer, prove no
            regression, capture a rollback. (Bears directly on F4 and D5 — do not return "capture
            a rollback" as a recommendation; it is already required.)
  HARD      No cost-per-outcome figure computed over successes only. Today only successful
            attempts record cost, so we state no dollar figure at all. A recommendation that
            assumes a usable cost number today is inadmissible.
  MEASURED  Three concurrent lanes. A design assuming ten agents answers a question we do not have.
  MEASURED  Page freshness: a cached figure must carry its age in the same string.
  POLICY    The existing instrument panel is never removed, only added to.
  POLICY    Small team. Anything needing a platform team to operate is wrong regardless of merit.
  ASSUMED   Windows-first on the operator's machine, with WSL2 available. If your recommendation
            changes under WSL2, SAY WHAT CHANGES — a previous pass listed this and then never
            applied it.

=====================================================================
PART 8 — OUTPUT, then audit yourself against Part 1
=====================================================================

1. CONSTRAINT AUDIT, first and briefly: which constraints in Part 7 you attacked and why, and
   CONSTRAINTS YOU NEEDED AND DID NOT HAVE. The second half is the one that has cost us passes.
2. VERDICT TABLE. At least 20 concepts, each with exactly ONE verdict and a citation:
     PRESENT / RENAMED (give the mapping) / DEFERRED (it is in Part 6) / ABSENT /
     NOT-SEARCHED (you did not look, or looked and found nothing — name the searches; MAX 5 items)
3. ANSWERS to A1-A3, D1-D5, E1-E8, F1-F4, each opening with its EVIDENCE line.
4. RANKED BUILD ORDER, at most 5 items, each with what it unlocks and a cost in engineer-days or
   engineer-weeks.
5. WHAT TO REFUSE TO BUILD.
6. WHERE YOU DISAGREE WITH US — the section we read first.

BEFORE YOU SUBMIT, check yourself against Part 1 and state the result:
  - Does every numbered answer open with an EVIDENCE line?
  - Did any ABSENT question get more than three sentences plus an experiment? Cut it.
  - Any effort estimate still an adjective? Convert it or delete it.
  - Anything in your verdict table that appears in Part 6's deferral list? Remove it.
  - Did you take an actual side on A3 and E8, or hedge? Hedging on those two is a failed section.
  - Name the ONE claim of ours you are least confident you evaluated fairly rather than accepted.
```

---

## Grading the answer when it lands

1. ⭐ **Grade the EVIDENCE lines first, before reading any prose.** If a question we predicted
   would be ABSENT came back STRONG, either we were wrong — good, that is the pass earning itself —
   or it is confabulating, and the named sources will show which within a minute. **This check is
   cheap and it is the whole reason Rule 1 exists.**
2. **Where an answer's own evidence contradicts its executive summary, the evidence wins.** That
   rule already caught R12: its summary said "adopt", its OBSERVED section said the tool has no
   attach and spawns duplicates against live session ids.
3. **Any concept returned with no citation is discarded**, however plausible.
4. **An answer quoting our file paths as though it read them is contaminated.** Check first.
5. **Every `DEFERRED` item reported as a gap** shows Part 6 was not read and downgrades the pass.
6. **Read the "constraints you needed and did not have" audit before the recommendations.** It is
   the direct countermeasure to the R12 failure, and it is the only part of the answer that can
   tell us the brief was wrong.
7. **A3 and E8 are the two questions where hedging is itself the finding.** If a third pass ducks
   E8, the question is not answerable from the literature and we run the week-long experiment
   E8(e) asks for instead of dispatching a fourth.

## See also

`../specs/agent-factory-technical-and-business-spec.md` — the full baseline, attachable as a
supplementary file · `ui-surface-inventory.md` · `agent-factory-concept-inventory.md` ·
`SYNTHESIS.md` · [[F76]]
