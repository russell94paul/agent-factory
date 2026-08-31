### F77 — RUN-01's acceptance criterion measures a different repository from RUN-01's work

- **BELIEVED** — `boot-prompts/run-the-loop-2026-08-30.md`: *"RUN-01: wire `deploy.py`'s spend
  ceiling into the path the launcher actually takes. Done when `python -m factory.launch` stops
  reporting gate `ceiling` as FAIL."* Stated as a WIRE ticket, not a build ticket, on the grounds
  that `deploy.py` already implements the ceiling and `RepoDeployer` has zero callers.

- **ACTUALLY** — the two halves of that sentence are about two different repositories, and no
  amount of work on the first can move the second.
  * The **work** is in `agent-factory`: `deploy.RepoDeployer.run_agent` passes
    `--max-budget-usd` per launch, and the path that actually runs is
    `scripts/local_tracker.launch(lane_id)`.
  * The **gate** is in `prefect-connectors`. `readiness.g_spend_ceiling_survives_restart` calls
    `_src("orchestrator/pipelines.py")`, and `_src` resolves every path against
    `CONNECTORS = C:\Users\PaulRussell\repos\prefect-connectors` (`readiness.py:723-727`). It
    greps that file for `cost_usd … (>=|>) … budget`.

  Wiring agent-factory's launcher to its own budget changes nothing the probe reads. The ticket as
  written cannot be completed by doing the thing it says to do.

- **MEASURED BY** — discriminating check, result predicted before it ran:

  ```python
  from factory.readiness import CONNECTORS       # C:\Users\PaulRussell\repos\prefect-connectors
  # readiness.py:724 →  f = CONNECTORS / rel
  ```

  and the probe body itself, which searches `_src("orchestrator/pipelines.py")` and nothing else.
  Predicted: the constant points at the sibling repo. Observed: it does.

- **AFFECTS** — the next session, and the RUN-01…04 sequence the whole current plan rests on.
  Three consequences, in order:

  1. **RUN-01 is really two tickets.** One in `prefect-connectors` (make `pipelines.py` compare
     accrued spend to a budget before dispatch) and one in `agent-factory` (give the launcher the
     ceiling `RepoDeployer` already has). Only the first moves the gate. Only the second is the
     "wire, not build" ticket the brief describes.
  2. ⛔ **Do not satisfy the probe without fixing the accounting under it.** The gate's own
     evidence line says *"cost is recorded only on `stage_completed`, so the accrued figure a
     ceiling would read is itself blind to every failure."* Adding a comparison that reads a
     failure-blind number would turn the gate green over a ceiling that cannot hold — gaming the
     instrument, which is the worst available outcome in this repo.
  3. **The negative control is currently unavailable.** `prefect-connectors/tests/orchestrator/
     mutate_control_plane.py` does not exist in that checkout (measured 2026-08-29; it is why 21
     tests fail here). Until it is back, a gate turned green cannot be shown still able to refuse,
     and this repo's standing rule is that a mechanism nobody has watched refuse is not a control.

  Same class as the three action→gate edges R16 killed in `roadmap.py`: an edge that *resolves* to
  a live gate id, and still points at a gate whose question is about something else. `_validate()`
  can only prove the id exists.
