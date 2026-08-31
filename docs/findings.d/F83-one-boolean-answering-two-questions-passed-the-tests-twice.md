# F83 — the controller's two verdict defects were the same defect: one boolean answering two questions

Both were found by **running** the newly-wired controller, not by the 24 tests that already passed
against it. Both were a single field standing in for two independent facts. Recording them together
because the pair is the finding — one of them is a bug, two of them is a shape.

## What happened

`factory/provider.AgentResult` carried a field `observable` — *can this provider see how the run
ended.* `factory/control` then leaned on it for two further questions it does not answer.

### 1. An unchanged worktree was reported as an agent that did nothing

- **BELIEVED** — the run contract's assertions all gate on `observable`, so an unobserved run
  yields UNMEASURABLE across the board.

- **ACTUALLY** — six of seven did. `work_landed` did not, and it is the only one that can return
  **FAIL**. So the very first real run through the controller —
  `python -m factory.control GP-327 --type ui-control --dry-run`, in which by definition **no agent
  executes** — came back:

  ```
  GP-327  FAIL  preset=ui-control
    [FAIL] work_landed   the worktree is unchanged — the agent altered nothing
  ```

  It had not. No agent existed. The remedy for *"the agent did no work"* and *"no agent ran"* are
  entirely different, and the contract published the first while the second was true.

  ⭐ **Every supervised launch would have read the same way.** `SupervisedProvider` returns the
  instant the terminal opens, with the human yet to type a character; the worktree is necessarily
  unchanged at that moment. The path that actually runs would have reported FAIL on every single
  dispatch — and, being the path that actually runs, would have done so in front of an operator.

- **FIX** — `work_landed` raises `Unmeasurable` when the run was not observable. An unchanged
  worktree is evidence about an agent only if an agent ran *and somebody watched it*.

### 2. A dry run held a lane claim against nothing

- **BELIEVED** — the claim must outlive the controller when work is still in flight, so
  `in_flight = result.dispatched and not result.observable`.

- **ACTUALLY** — that derivation is false for half the cases:

  | | observable | still running |
  |---|---|---|
  | supervised terminal | no | **yes** |
  | dry run | no | **no** |
  | headless run | yes | no |

  A dry run is unobservable *and finished*. So it retained `task--gp-327.json`, which
  `claims.task_holder` reads as `HELD_UNVERIFIED` (no pid), which correctly refuses the next launch
  with *"not being able to look is not proof that nothing is there"*. **A deadlock caused by
  nothing at all** — held open by a run that never started, against a ticket nobody was working.
  Found by listing `.data/claims/` after the run, not by any check.

- **FIX** — `in_flight` is its own field on `AgentResult`, set by each provider. Two questions,
  two fields.

## Why the tests did not catch either

They were both written *and passing* before the first real invocation. 24 tests, including a
positive control, three negative controls and a mutation test that verifiably went red when the
observability mapping was removed. None of them ran the actual `HeadlessProvider`, and none looked
at `.data/claims/` afterwards.

⭐ **A test suite written by whoever wrote the code shares the code's model of the world.** The
mutation test proved the assertions were load-bearing; it could not notice that one assertion had
been left out of the set, because the author's list of assertions-that-gate-on-observability was
the same list in both files. That is the same shape as the three hand-maintained allow-lists this
estate has already lost to — `TeamSpec.version`'s hash keys, `local_tracker._HOT`,
`synthesis.session_prompt`'s fallback — and it is why
`tests/test_hot_reload_covers_every_import.py` exists to derive its list rather than assert one.

**Both defects were found within two invocations of running the thing.** That is the same yield
`F79` recorded when `live_probes.py` gained its first caller: one line in `certify.py` turned A1
from UNMEASURABLE into a real verdict and exposed two defects standing since 2026-08-21. Wiring
existing code keeps being the highest-yield work in this repository, and the reason is visible
here — **an unwired module's tests only ever test the author's model of it.**

## Also corrected in passing

Several boot prompts and design notes say *"the four verdicts"*. There are **five**:
`factory/contract.py` added `ERROR` (TTCN-3's `none < pass < inconc < fail < error`, ITU-T Z.140
§24.2) where `error` is set by the test system rather than the test case and dominates `fail`.
`factory/events.py` takes the enum rather than a list of names, so it cannot fall behind again;
`tests/test_control_run.py::test_the_stream_can_express_all_five_verdicts` iterates `Verdict` for
the same reason.

## The rule worth keeping

**Before a boolean gates a decision, say the question it answers as a sentence. If two different
sentences fit, it is two fields.** `observable` answers *"can I see how it ended"*. It does not
answer *"is it still running"* and it does not answer *"is the worktree's state evidence about the
agent"* — and it was quietly asked all three.
