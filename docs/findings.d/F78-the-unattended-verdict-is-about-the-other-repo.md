# F78 — UNATTENDED-BLOCKED is a verdict about `prefect-connectors`, not about agent-factory

**Extends F77.** F77 established this for one gate (`ceiling` / RUN-01). It is four of five, and it
therefore takes RUN-02 with it.

- **BELIEVED** — `boot-prompts/run-the-loop-2026-08-30.md`, and the RUN-01…04 sequence the current
  plan leads with: *"Four tickets buy those three back, and each one is done when a verdict moves."*
  RUN-01 is accepted on gate `ceiling`; **RUN-02 on gates `cap` AND `reaper`**. Both were written as
  agent-factory work — wire `deploy.py`'s controls into `scripts/local_tracker.launch()`.

- **ACTUALLY** — four of the five `UNATTENDED_GATES` probe files in the **sibling repository**.
  `_src`/`_grep` resolve every path against
  `CONNECTORS = C:\Users\PaulRussell\repos\prefect-connectors` (`readiness.py:723-727`):

  | gate | probe | reads |
  |---|---|---|
  | `cap` | `g_attempt_cap_on_the_live_path` | `orchestrator/engine/pipeline_agent.py`, `orchestrator/pipelines.py`, `orchestrator/server.py` |
  | `reaper` | `g_orphans_are_reaped` | `orchestrator/engine/work_guard.py` |
  | `ceiling` | `g_spend_ceiling_survives_restart` | `orchestrator/pipelines.py` |
  | `concurrency` | `g_concurrency_is_reserved_outside_the_agent` | `orchestrator/pipelines.py` |
  | `bounded` | `g_failure_is_bounded` | not a `_src` probe — the one exception |

  No amount of work in `agent-factory` moves any of the first four.

- **MEASURED BY** — discriminating check, outcome predicted before running. For each gate id in
  `UNATTENDED_GATES`, resolve its probe function and read its body for `_src(` / `_grep(` (sibling)
  versus local path construction:

  ```
  cap          g_attempt_cap_on_the_live_path              prefect-connectors (SIBLING)
  ceiling      g_spend_ceiling_survives_restart            prefect-connectors (SIBLING)
  concurrency  g_concurrency_is_reserved_outside_the_agent  prefect-connectors (SIBLING)
  reaper       g_orphans_are_reaped                        prefect-connectors (SIBLING)
  bounded      g_failure_is_bounded                        neither
  ```

  Predicted: `ceiling` sibling (from F77), others unknown. Observed: four sibling. Confirmed by
  reading each body directly rather than trusting the classifier.

- **AFFECTS** — the framing of the whole current plan, in three steps:

  1. **RUN-02 has F77's defect and has not been corrected for it.** The other session rewrote the
     `next:` block for RUN-01 only. RUN-02 is accepted on `cap` AND `reaper`; both are sibling
     probes. It splits the same way RUN-01 does — an agent-factory half that is real bounding work
     and moves no gate, and a `prefect-connectors` half that moves the gate.

  2. ⭐ **`UNATTENDED-BLOCKED` does not mean what the plan reads it as meaning.** The verdict is
     currently a true statement about the **connector orchestrator's** control plane. The plan reads
     it as *"agent-factory's launcher is unbounded"* — which is **also true**, and is why the error
     survived: two different claims, both correct, one instrument, and the instrument measures the
     one the plan is not working on. Nothing in the board says which.

  3. **This is the lane defect again, one layer down.** `factory/lanes.py` describes today's work in
     the earlier project's vocabulary; `factory/readiness.py` measures the earlier project's
     repository and is read as measuring this one. Same shape: **an instrument inherited from a
     previous project, still correct about that project, silently re-pointed at this one by the
     reader rather than by the code.**

- ⭐ **THE CONSTRUCTIVE HALF — the other verdict is entirely ours.** The same discriminating check,
  run against `TRUST_GATES` instead of `UNATTENDED_GATES`:

  ```
  suite      g_contract_suite_green        LOCAL (agent-factory)
  certified  g_output_is_certified         LOCAL (agent-factory)
  corpus     g_corpus_is_tamper_evident    LOCAL (agent-factory)
  version    g_version_hash_is_complete    LOCAL (agent-factory)
  breadth    g_corpus_has_breadth          LOCAL (agent-factory)
  ```

  **Five of five.** So the board offers two verdicts, and the plan has spent its effort on the one
  that agent-factory work cannot move:

  | verdict | gates | movable from this repo |
  |---|---|---|
  | `UNATTENDED-BLOCKED` | cap · ceiling · concurrency · reaper | **no** — 4 of 5 are sibling probes |
  | `OUTPUT-UNCERTIFIED` | suite · certified · corpus · version · breadth | **yes** — 5 of 5 local |

  The cheapest movement available is `breadth`, which fails with *"1 case, 0 strata"*. **A single
  supervised lane run produces case #2.** That is the only gate in the set whose remedy is to run
  the thing rather than to write more of it — and `launch.py` already argues for exactly that:
  a supervised run is *"the only way to measure the loop at all"*.

  This does not retire RUN-01a/02a as engineering — the launcher genuinely is unbounded. It retires
  them as **the lead**, because they were chosen for a verdict they cannot move.

- **WHAT THIS DOES NOT SAY.** The gates are not wrong, the probes are not broken, and
  `prefect-connectors` genuinely is unbounded. `launch.py`'s own sentence — *"You are the cap, the
  reaper and the spend ceiling"* — remains true of agent-factory on its own merits, because
  `RepoDeployer` has zero callers. What is wrong is only the claim that **doing RUN-01/02 in this
  repo moves these gates.** It does not.

- **SUGGESTED REPAIR** — do not "fix" this by re-pointing `CONNECTORS`. That would silently change
  what every existing verdict in the corpus meant. Either:
  * **label the gate's subject** — each gate states the repo it measures, and `launch.py` renders
    two verdicts rather than one; or
  * **add agent-factory-local twins** for `cap`/`ceiling`/`reaper`/`concurrency` and accept RUN-01/02
    against the twins, leaving the sibling gates as the connector migration's own business.

  The first is cheaper and is the honest one: it makes the board say what it has always meant.
  ⛔ Either way, F77's warning stands — a gate turned green over a failure-blind accrued figure is
  gaming the instrument, and `prefect-connectors/tests/orchestrator/mutate_control_plane.py` is
  absent from that checkout, so no negative control is available to prove a newly-green gate can
  still refuse.
