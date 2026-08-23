# R6 — What should be automated, and what should raise an alarm, across parallel agent sessions?

**Status: ANSWERED 2026-08-22.** Written 2026-08-22 for a Deep Research pass. Paste the whole file. The answer is filed at `docs/research/answers/R6-answer-automation-and-alerting.md`.

Companion to [`R5-build-velocity.md`](R5-build-velocity.md), which asks how to go faster. This one
asks what should notice when going faster breaks something. Read R5 first if you have not; the
build process it describes is the system under discussion here.


## Run log

| Run | Dispatched | Outcome |
|---|---|---|
| 1 | *not recorded* | Answer filed **2026-08-22** (measured: the answer file's mtime). This prompt predates the run log, so when it was sent is **NOT-RECORDED** — which is not the same as never. |

> Kept because `factory.dispatch` reads a status line and the presence of an answer file, and by its own account cannot see whether a prompt was ever actually pasted anywhere. Without this table "which did I send, and when?" is not answerable from disk. **Add a row every time this prompt is dispatched.**

---

## The situation, measured

A programme is about to move from **one session at a time** to **three or four in parallel**, each
a separate Claude Code session working the same two repositories in different files.

Progress is measured by 30 readiness gates, each a probe reading a fact from a file at the moment
it runs. `9 of 30` pass today. Work is grouped into five lanes by *file locality* rather than
dependency order, because 16 of 30 gates have no unmet dependency but two sessions editing
`orchestrator/pipelines.py` simply conflict.

**What exists to notice a problem:**

- 80 tests, run by typing `pytest`
- generator `--check` modes that detect a published surface drifting from measured state, wired
  into the test suite
- an append-only findings ledger (`docs/findings.md`) where a lane records corrected premises for
  other lanes, with four mandatory fields and a parser that fails the suite on a malformed entry
- git history, which carries a dated `n of N gates pass` headline in every commit that touched the
  readout, so velocity is derivable

**What does not exist, verified rather than assumed:**

- ⛔ **No CI whatsoever in this repository.** `.github/workflows` does not exist and there are no
  git hooks. Nothing runs on push. The sibling repo has three workflows; this one has none. So the
  80 tests run only when a human types the command.
- ⛔ **Nothing detects a gate going PASS → FAIL.** Verified by grep: every match for "regress" is
  the word inside an assertion name. Gate verdicts are read fresh each time and never compared to
  a previous reading, so a lane that breaks another lane's gate lowers the total silently — the
  board shows a smaller number and says nothing about *which* gate moved, or when, or in which
  commit.
- ⛔ **No liveness signal from a session.** A Claude Code session that stalls, loops, or exits
  half-done is indistinguishable from one thinking hard. The programme has already been bitten by
  this shape one level down: 4 of 14 recorded pipeline runs sit at `stage_started` with no terminal
  event and nothing timed them out.
- ⛔ **No claim mechanism.** Two sessions can start the same lane. The conflict map says which
  lanes *cannot* run together; nothing records which one *is* running.

**Relevant history.** This estate's signature failure is a mechanism that reports success over an
unseen population: a pipeline whose stored status keeps only the last attempt, so a stage that
failed 100 times and succeeded once closes the run as `succeeded`. Any alerting design that can be
satisfied by an absence of signal will reproduce that failure at the session layer.

## The questions

**1. What is the minimum automation that would actually catch a parallel-session regression?**
Candidates: CI on push; a pre-push hook; a scheduled re-measure that diffs gate verdicts against
the last recorded reading; a bot that comments on divergence. **Which of these earn their keep,
and in what order?** We would rather add one thing that fires than four that are ignored. Note the
constraint: work happens on a Windows workstation, repos are private, and there is currently no
runner budget or appetite for one.

**2. How should a gate regression be attributed, not just detected?**
Detecting `truthful: PASS → FAIL` is easy once verdicts are stored. Saying *which lane's commit
did it* is the useful part, and with several sessions pushing to the same branch the last commit is
not necessarily the culprit. **What attribution technique is worth the complexity here** — bisect,
per-commit measurement, per-lane branches with measurement at merge?

**3. What is the right liveness signal for an agent session, and what should its absence mean?**
A session is not a process we control; it is a conversation that may be paused, thinking, or dead.
**Is heartbeat-style monitoring even the right model**, or should the signal be work-shaped —
commits, findings entries, gate movement — with silence over a threshold treated as a question
rather than a failure? Critically: what stops "no signal" being read as "fine", which is the exact
failure this programme exists to stop?

**4. How much should be alerted versus surfaced?**
There is a readout the human refreshes. There is no notification channel to a session, deliberately
— a button that claims to notify one would do nothing while looking like it did. **When is a push
alert justified for solo/small-team agent work, and when is a well-designed dashboard strictly
better?** We are wary of building an alerting system nobody has watched fire.

**5. Does prior art cover this, or is it genuinely new?**
Parallel *human* development on one repo is a solved problem: CI, branch protection, code owners,
merge queues. **How much of that transfers to parallel agent sessions**, and where does it break
down? Specifically: agents can produce large correct-looking diffs quickly, do not reliably read
each other's work, and can confidently report a false finding — we recorded three such in a single
session. Are there published practices for multi-agent work on one codebase, and are they
*observed* or *proposed*?

**6. What should a session be forced to do before it closes?**
Today the lane prompt *asks* for five things (tests, render check, generator checks, an independent
review, a findings entry). A prompt asking is a convention; we are considering a `close_lane`
command that runs them and refuses. **Is a preflight command the right control, or does it just
move the convention?** What makes such a gate hard to skip without making it hated?

## What a useful answer looks like

An ordered shortlist — what to build first, what to build only if the first thing proves
insufficient, and what to deliberately not build. For each: what it catches, what it cannot catch,
and **how you would make it fire on purpose to prove it works.** A control nobody has watched
refuse something is treated here as decoration, so a recommendation without a way to test it is
incomplete.

Label each recommendation **observed** (seen working in a comparable setting — LLM agents, multiple
concurrent sessions, one repository) or **extrapolated** (from human teams or single-agent work).
Those are different claims and will be weighted differently.

Say explicitly which questions you could **not** find good evidence for. Four solid answers and two
honest gaps beat six confident ones.

## Method note

The estate's rule, applied to its own research: *an object named by a ticket, boot prompt or
handoff is a hypothesis, not a finding — walk the route yourself before adopting it.* An earlier
pass here named the wrong component as the cause of a defect, the claim was carried into a second
research question before anyone checked, and verifying took one grep. Assume the same about
anything in this document you can check.
