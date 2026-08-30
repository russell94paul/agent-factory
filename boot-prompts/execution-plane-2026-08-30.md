# Boot — split the execution plane, AFTER the loop is bounded

**Written:** 2026-08-29, late. **Corrected:** 2026-08-29 ~21:40, after F78.
**For:** a session that comes after `run-the-loop-2026-08-30.md`. **Does NOT supersede it.**

⛔ **CORRECTED — this file said "that brief leads with RUN-01…04 and it is still right" and set
`next:` to "still RUN-01". Both are now wrong.** `docs/findings.d/F78-*.md` measured which
repository each gate probes: **`cap`, `ceiling`, `concurrency` and `reaper` all grep
`prefect-connectors`**, so no agent-factory work moves them, and RUN-01/02 were chosen for verdicts
they cannot shift. `run-the-loop` has been re-led accordingly.

`next:` **read `run-the-loop-2026-08-30.md` and do what its `next:` line says** — currently: run one
supervised lane and put the run in the corpus, to move gate `breadth` off *"1 case, 0 strata"*.

⚠ **Do not use the check that used to be here.** It read
`python -m factory.launch   # cap / reaper / ceiling / concurrency still FAIL?` — those four staying
red says nothing about work done in this repo, which is exactly the trap F77 and F78 describe.
`factory.launch` also takes ~9 minutes and prints nothing until it finishes.

---

## ⛔ Read this before touching the architecture

The brief this file was generated from asks to separate the control plane from the execution plane
behind `AgentProvider` / `SandboxProvider` / `RunController`. **That is the right direction and the
wrong order today**, for three reasons that are measured, not stylistic:

1. **`RepoDeployer` has zero callers.** `git grep "RepoDeployer"` outside `deploy.py` and its test
   returns nothing. Putting a provider interface in front of it abstracts code that nothing runs —
   which the source brief's own DO-NOT list forbids: *"create speculative abstractions with no
   working implementation."* One agent provider plus one sandbox backend **is** that.
2. **"Execution remains bounded" is not something to preserve — it is not true yet.** Measured
   2026-08-29: `cap`, `ceiling`, `concurrency`, `reaper` and `bounded` all **FAIL**. The brief lists
   bounding under things to keep. There is nothing there to keep.
3. **RUN-01…04 and the RunController refactor touch the same lines of `deploy.py`.** Doing both at
   once means the bounding work lands inside a refactor that is rewriting the code being bounded,
   and neither can be verified independently. Bound first — each ticket is done when a **verdict
   moves**, which is falsifiable — then abstract.

⭐ **The honest sequencing** (revised after F78): **one supervised run → RUN-03** (a `TeamSpec`
actually executes) → **then** this brief. By RUN-03 there is a live execution path with real callers,
and the provider boundary stops being speculative because there is something on both sides of it.

⛔ This line previously read *"RUN-01 → RUN-02 → RUN-03 → then this brief"*. RUN-01 and RUN-02 are
still worth doing — `RepoDeployer` has zero callers, so the launcher genuinely is unbounded — but
they no longer gate this brief, because **the argument for putting them first was that a verdict
would move, and F78 shows none will.** RUN-03 is unaffected: its acceptance is a real run, not a
sibling-repo probe.

**If you start here anyway**, say why in one sentence and record it — do not silently reorder.

---

## First: inspect reality, but not with the test suite

Read `factory/contract.py`, `factory/tasks.py`, `factory/blueprint.py`, `factory/deploy.py`,
`factory/evals.py`, `factory/metrics.py`, and `git status`. Then state current vs partial vs missing.

⚠ **Do NOT use `pytest -q` as your baseline measurement.** Measured 2026-08-29, the failure count
moved **8 → 12 → 15 → 18 → 21 within one session with no code change in between.** Cause: roughly
twenty tests read the **`prefect-connectors` checkout live**, and other sessions move it. That day it
sat on branch `chore/artefact-homes` with 29 dirty files and **no `tests/orchestrator/
mutate_control_plane.py` at all**, which alone fails `test_mutation_anchors_still_match` and
`test_live_probes`.

`run-the-loop-2026-08-30.md` says *"304 tests green"*. That was true under a sibling-repo state it
does not name. **Before quoting any suite number, record the condition it holds under:**

```bash
git -C ../prefect-connectors branch --show-current
git -C ../prefect-connectors status --porcelain | wc -l
python -c "from factory.readiness import CONNECTORS; print((CONNECTORS/'tests'/'orchestrator'/'mutate_control_plane.py').is_file())"
```

A session that treats a fluctuating suite as a regression signal will "fix" phantom breakage. Use
`python -m factory.launch` and `python -m factory.readiness` as the baseline instead — they state
their own basis.

## You are not alone in this checkout

Three interactive sessions were live in `agent-factory` on 2026-08-29
(`python -c "from factory import sessions; print(sessions.collisions())"`).

- **Stage by path. Never `git add -A`, never `git commit -a`.** Two sessions edited the same two
  files that day and both survived by luck.
- **`git status` shows other people's work.** On 2026-08-29 `docs/research/SYNTHESIS.md` was dirty
  because a reconciliation session was mid-write, and `docs/research/R19-*.md` were untracked from a
  third. Committing either would have swept another session's work under your message.
- **Ask before committing.** Paul approves commits.

---

## What to build, and the one interface that is not speculative

### Build the event model FIRST — it is the only piece that is time-sensitive

Of everything the source brief asks for, **only the append-only event record cannot be
reconstructed later.** Providers can be abstracted whenever a second provider appears. A run that
executed without recording what it was doing is gone.

⭐ **Reconcile it with `docs/research/answers/R19-answer-work-taxonomy-and-team-selection.md` §5
before writing a line.** R19 designs a *dispatch record* for the selection side; this brief asks for
an *event stream* for the execution side. They are the same ledger seen from two ends, and building
them separately guarantees they disagree. R19's load-bearing claim:

> the **eligible set** — every configuration that passed the filter and was *not* chosen — costs
> nothing to write and cannot be reconstructed afterwards. Every other field can be backfilled.

So `RunStarted` must carry: ticket, `type_id`, declared difficulty and novelty (**before** the run),
the eligible configurations, which was chosen, and under what rule. Then the execution events
(`AgentText`, `CommandStarted/Finished`, `UsageObserved`, `CommitCreated`) and the verification
events (`AssertionEvaluated`, `RunCertified`).

Two existing ledgers must be folded in or explicitly kept apart, with the reason recorded — do not
make a third: `.data/runs.jsonl` (`factory/runs.py`, **3 rows, all `FINISHED`**) and
`prefect-connectors/.sessions` (**14 runs**, read by `g_work_is_attributable`). They count different
populations and neither records a configuration.

### The four verdicts survive the event model

`RunFailed` and `RunBlocked` are not enough. An event stream that cannot express **`UNMEASURABLE`**
has collapsed the distinction this repo exists to protect. Every terminal event carries one of
`PASS` / `FAIL` / `UNMEASURABLE` / `NOT_RUN`, and `GreenContract` — never the agent, never the
provider — assigns it.

### Team selection is constrained by R2, which already ran

`blueprints/orchestrator_team.yaml` opens with **⛔ SUPERSEDED BY EVIDENCE — DO NOT BUILD THIS
TEAM**, rejecting planner → implementer → tester with a 180-configuration study and our own
seam-failure history. The source brief's *"Planner / team selection"* step must not resurrect it.
R2's unlock threshold is stated in that file; clear it or stay single-worker. `factory/presets.py`
is the selector that exists — five presets, **one** with a `WIRED` verifier — and **nothing consumes
its decision.** Wiring that (RUN-03/04) beats designing a new planner.

### ⛔ CORRECTED 2026-08-29 — "adopt before you abstract" was FALSIFIED. Build the runner.

**This section previously argued that because `RepoDeployer` has zero callers, adopting a maintained
runner "gets the interface *and* the implementation." That was wrong.** The question has now been
run — six lenses, `/prospect`, output at `docs/reviews/build-vs-adopt-2026-08-29.md` (491 lines) —
and the verdict on agent orchestration is **BUILD**, adopting only the Claude Agent SDK as transport.

The measurements that killed it:

- **The frameworks cover 3 of 8 requirements.** Worktree isolation, lane claiming, the persisted
  retry ledger, the event ledger and the verdict model are **ABSENT from all six**. You build those
  either way, so adoption buys an interface and *most of* the implementation is still yours.
- **~370–510 new lines hand-rolled** (~310–420 with the SDK), on top of **1,682 lines that already
  exist and work**. LangGraph alone costs **150–300 lines of event-model adaptation** *plus* the
  framework, *plus* `langsmith` — a hosted telemetry client — as the first entry of `langchain-core`'s
  **mandatory** `dependencies`.
- **AutoGen is in maintenance mode.** Its README, verbatim: *"AutoGen is now in maintenance mode. It
  will not receive new features or enhancements and is community managed going forward."*
- **CrewAI's core abstraction is the topology R2 rejected** — `role`/`goal`/`backstory`, hierarchical
  process that *"automatically assigns a manager to the defined crew."* It cannot be layered below
  `GreenContract` because it owns the control flow.
- **SWE-agent** (v1.1.0, 2025-05-22) and **Aider** (v0.86.0, 2025-08-09) fail on release staleness.
  **OpenHands** is now a web application with a server, not an embeddable library.

**And the zero-callers premise itself drew the wrong conclusion.** Of `deploy.py`'s 265 lines,
**140 are `AttemptLedger`** — a cap that survives restart. Every framework's budget control is
per-invocation and resets on the next call, **which is precisely the bug `AttemptLedger` was written
to fix.** "Unwired code is cheap to replace" is true of 86 lines and false of 140.

**What IS worth adopting:** the **Claude Agent SDK** (MIT, `v0.2.148` 2026-08-28, `windows-latest`
CI, 5 runtime deps). Its cost is *negative* — `deploy.py:230-234` already hard-codes `--max-turns`,
`--max-budget-usd`, `--output-format stream-json`, `--model` against an **undocumented, unversioned,
unpinned argv surface**. The SDK does not add a vendor coupling; it makes an existing invisible one
typed and pinnable. It has no verdict model, so it sits cleanly below `GreenContract`.

⚠ Part 4 of `BUILD-VS-ADOPT-PROMPT.md` is labelled `RECALLED / UNVERIFIED` in its own text — *"my
prior knowledge, not a search result"* — and **six of its rows are now corrected** (see the review's
§6). Its "cheapest place to adopt" line, quoted approvingly above before this correction, was one of
them. The actual cheapest adopt is **`filelock`** in `claims.py`, a category Part 4 has no row for.
Sandcastle remains unread and therefore still `MARKETED`.

The two components its author judged strongest to **build**, not adopt, are the ones to protect in
any adoption: **`UNMEASURABLE` as a first-class verdict, and evidence-basis enforced in code.** If a
candidate framework cannot represent a fourth verdict, it may still be adopted — but only *below*
`GreenContract`, never as the thing that decides an outcome.

### Sandcastle is UNVERIFIED

`mattpocock/sandcastle` is named in the source brief as an execution-plane reference. **Nobody in
this estate has read it.** Treat every concept attributed to it — warm sandboxes, lifecycle hooks,
normalized agent events, commit collection — as `MARKETED` until exercised. Before designing an
adapter, fetch the repo and record what its API *actually* exposes, with a citation. A named
artifact from a brief is a hypothesis, not a finding; that rule has cost this estate a wrong-layer
deploy before.

### ⭐ Derive registries; do not enumerate them

`AgentProvider` and `SandboxProvider` both want a registry, and a registry is an allow-list.
**Three hand-maintained allow-lists under-covered in a single session on 2026-08-29:**

| | what it missed |
|---|---|
| `TeamSpec.version` | `repo` and `prohibition` — a certification survived both |
| `synthesis.session_prompt` | `unreconciled()` behind an `or` — banked two unread answers |
| `local_tracker._HOT` | `flow`, `runs`, `sessions` — reload reported success and re-served old code |

All three looked correct. All three silently omitted something. **If a list can be derived from the
thing it tracks, derive it** — and pair it with a test that fails when an entry goes missing, not
one that asserts the list's contents.

---

## Definition of done

A vertical slice: task → `RunController` → one agent provider → one workspace/sandbox → **recorded
structured events including the eligible set** → result → evidence → `GreenContract` verdict — with
tests, and with a second provider addable without touching `GreenContract` or task semantics.

Prove substitution with a **fake provider in a test**, not by adding a second real one. A fake that
the RunController drives identically is the evidence the boundary is real; a second real provider is
scope.

## Before finishing

1. Files changed.
2. Architecture before vs after.
3. What now works end-to-end — and what its verdict is, including any `UNMEASURABLE`.
4. Remaining production gaps.
5. Next 3 tasks in strict priority order.
6. Decisions deliberately deferred, and why.
7. **Which gates moved.** `python -m factory.launch` before and after. If none moved, say so plainly
   — a refactor that changes no verdict is not progress, it is rearrangement.
