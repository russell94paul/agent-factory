# F80 — RUN-01/02's work is already built, on a branch the readiness board never looks at

**Extends F77 and F78.** Those two established *which repository* the bounding gates measure. This
is about *which revision of it* — a distinction neither of them draws, and the one that decides
whether the work exists.

- **BELIEVED** — `boot-prompts/run-the-loop-2026-08-30.md`, and `python -m factory.launch` on every
  run since: *"May I LEAVE it running, unattended? UNATTENDED-BLOCKED — cap FAIL · reaper FAIL ·
  ceiling FAIL · concurrency FAIL · bounded FAIL."* Read, reasonably, as *the bounding controls do
  not exist and RUN-01…02 must build them.*

- **ACTUALLY** — most of that work exists. `prefect-connectors` branch **`lane/control-plane`**
  carries **21 commits, 4,077 insertions across 11 files**, unmerged, including:

  ```
  0a5c393 feat(cap,bounded,concurrency,reaper,from-history): build the control primitives
          a bespoke engine does not get for free
  84b8b85 test(cap,concurrency,reaper,from-history,truthful): 39 negative controls, and a
          mutation harness that proves each one is load-bearing
  9dda05b fix(reaper,cap): the budget deferred nothing, and the order guard was order-blind
  ```

  ```
  orchestrator/engine/cloud_reaper.py                 200 ++++      (new; 8 functions)
  orchestrator/pipelines.py                          1119 ++++
  tests/orchestrator/mutate_control_plane.py          358 ++++      (new)
  tests/orchestrator/test_cloud_reaper.py             965 ++++      (new)
  tests/orchestrator/test_control_plane.py            627 ++++      (new)
  tests/orchestrator/test_control_refusal_status.py   431 ++++      (new)
  ```

  The board cannot see any of it. `readiness.CONNECTORS` resolves to
  `repos/prefect-connectors`, whose checkout is on **`chore/artefact-homes`** — a different
  session's connector work, with `orchestrator/` untouched. **The gates have been measuring a
  branch the control-plane work was never on.**

  ⭐ **And the 21 failing tests here are a symptom of the same thing.** They fail on
  `tests/orchestrator/mutate_control_plane.py` being absent. That file is not missing — it is on
  `lane/control-plane`, 358 lines of it. `boot-prompts/execution-plane-2026-08-30.md` correctly
  observed the file was absent and correctly told sessions not to treat the suite as a regression
  signal; what nobody did was ask *where the file went*.

- **MEASURED BY** — discriminating test, prediction stated before it ran. Predicted: pointing
  `$PREFECT_CONNECTORS` at `lane/control-plane` moves the five bounding gates off FAIL.

  ```bash
  git -C ../prefect-connectors worktree add --detach <tmp> lane/control-plane
  PREFECT_CONNECTORS=<tmp> python -c "from factory.readiness import measure; ..."
  ```

  Observed — **the prediction was partly wrong, and the way it was wrong is the second finding:**

  | gate | on `chore/artefact-homes` | on `lane/control-plane` |
  |---|---|---|
  | `cap` | FAIL | **PASS** — "the restarting path is capped" |
  | `from-history` | FAIL | **PASS** — "the verdict is derived from the event log" |
  | `reaper` | FAIL | FAIL at the time — **the probe could not pass; see F81** |
  | `concurrency` | FAIL | FAIL at the time — **the probe could not see it; see F81** |
  | `ceiling` | FAIL | FAIL — this one is real |
  | `bounded` | FAIL | UNMEASURABLE at the time — probe could not pass either |

  ⭐ **RE-MEASURED 2026-08-30, after the F81 probe defects were fixed.** The probes now drive the
  controls instead of grepping for them, and the picture is decisive — both columns revision-stamped
  by `readiness.revision()`, which did not exist when the first table was taken:

  | gate | `chore/artefact-homes@8b7c68d` | `lane/control-plane@7f10752` |
  |---|---|---|
  | `cap` | FAIL | **PASS** |
  | `bounded` | UNMEASURABLE | **PASS** |
  | `concurrency` | FAIL | **PASS** |
  | `reaper` | FAIL | **PASS** |
  | `from-history` | UNMEASURABLE | **PASS** |
  | `ceiling` | FAIL | FAIL |

  **Five of the six.** `ceiling` fails on both because no spend control exists on any branch — the
  only budget symbol in the engine is `TERMINATION_BUDGET_SEC`, a *time* budget for the reap sweep.
  That is RUN-01's genuine remainder and F77 describes its shape.

  Non-destructive throughout: a detached worktree, removed afterwards; `prefect-connectors` was on
  `chore/artefact-homes` with 29 dirty files before and after.

- **AFFECTS** — the whole RUN-01…04 sequence, and any session that reads `factory.launch` as a
  statement about what has been built.

  1. **The next action is a merge and a re-measure, not a build.** Two gates go green on work that
     is already written, reviewed and tested. Building RUN-02 from scratch would be rebuilding
     4,077 lines that exist.
  2. ⛔ **A readiness board must state which revision it measured.** `readiness` hashes
     `CONNECTORS` into its identity (`readiness.py:408`) — the *path*, not the *revision*. Two
     boards taken an hour apart, either side of a `git checkout` in a sibling repo, are
     incomparable and say nothing about it. Same family as F72 ("the board number depends on where
     you run it"), one level up: it also depends on *when*, and on a branch nobody named.
  3. `agent-factory/.worktrees/prefect-connectors` **is already checked out at `lane/control-plane`
     (7f10752)**. The work has been sitting inside this repo's own worktree directory while the
     board measured its sibling. Pointing `$PREFECT_CONNECTORS` there is a one-line change.
  4. The estate's measured weakness is absorption — *19 conclusions reached a mechanism and never
     reached the decision record*. This is that failure in code rather than in prose: work that
     reached a branch and never reached the instrument.
