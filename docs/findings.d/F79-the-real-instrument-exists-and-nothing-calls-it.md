# F79 — the connector contract's real instrument exists, works, and nothing calls it

**Extends F77/F78.** Those found the *plan* aimed at gates it could not move. This is the inverse:
work that is **already done**, already correct, and wired to nothing — so the board reports it as
missing and a lane exists to rebuild it.

- **BELIEVED** — `factory/lanes.py`, the `certify` lane, presented by the tracker as runnable:

  > *"All 12 assertions return UNMEASURABLE against a live target because **no probe is wired to
  > anything**."*
  > *"**START with A1** (config satisfiable) **and A5** (regression suite) — both may be reachable
  > from the prefect-connectors checkout alone, with no secret at all. **Prove that** before asking
  > for a credential."*

  And `python -m factory.launch`: `certified  NOT_RUN  12 assertions have no instrument wired`.

- **ACTUALLY** — A1 and A5 were wired on 2026-08-29 in `6872aee` *"feat(probes): A1/A5 wired to a
  real instrument, plus three RED gates"*. `factory/live_probes.py` defines
  `WindsorAiGepProbes`, and **it works today, with no credential**:

  ```
  config      -> OK  constructed ['WindsorAIConnection', 'WindsorAIOptions']      (A1)
  suite       -> OK  {'passed': 825, 'failed': 1, 'revision': '8b7c68d5...'}      (A5)
  credential  -> Unmeasurable: no instrument configured for credential
  run         -> Unmeasurable: no instrument configured for flow run
  landed      -> Unmeasurable: no instrument configured for landed rows
  ```

  **`factory/certify.py` never constructs it.** It imports and instantiates only
  `CtxProbes` (a recorded world) and `Probes` (refuses everything) — `certify.py:29,102,105`. The
  sole importer of `live_probes` anywhere in the repo is `tests/test_live_probes.py`.

  So the lane's premise is false in both directions: the probes exist, *and* the thing the lane would
  "prove" was proven and committed. A session launched on that prompt spends itself rebuilding
  `live_probes.py`.

- **MEASURED BY** — discriminating test, result predicted before it ran. Predicted: if the probe
  class is genuinely functional, constructing it and calling `config`/`suite` returns data while the
  unimplemented verbs raise `Unmeasurable`. Observed: exactly that (above).

  ```bash
  grep -rn "live_probes\|LiveProbes" --include=*.py . | grep -v "^./factory/live_probes.py" \
                                                       | grep -v "^./.worktrees"
  #   -> tests/test_live_probes.py only
  grep -n "Probes" factory/certify.py
  #   -> CtxProbes, Probes.  Never WindsorAiGepProbes.
  git log -1 --format="%ad %h %s" --date=short -- factory/live_probes.py
  #   -> 2026-08-29 6872aee feat(probes): A1/A5 wired to a real instrument, plus three RED gates
  ```

- **AFFECTS** — the `certify` lane, the `certified`/`breadth`/`corpus` gates, and the
  build-vs-adopt review's §0, which states that every migration cost in it is priced against
  interfaces that have never carried traffic. Two are now closer to carrying traffic than the board
  admits.

  1. ⭐ **The cheapest verdict move on the board is a wiring change, not a lane.** Constructing
     `WindsorAiGepProbes` in `certify.py`'s live path should move A1 and A5 off `NOT_RUN` today, with
     no credential and no vault approval. Everything needed already exists and is under test.
  2. ⛔ **Do not launch the `certify` lane as written.** Its prompt instructs an agent to build what
     `6872aee` already built and to prove what `6872aee` already proved.
  3. **`lanes.py` is a hand-maintained allow-list that drifted from the code it describes** — the
     fourth instance of that pattern recorded in this repo (`TeamSpec.version`,
     `synthesis.session_prompt`, `local_tracker._HOT`, now `lanes.LANES`). A lane's premise should be
     derived from, or tested against, the state it claims. **A lane whose `why` cannot fail is
     decoration.**
  4. **This is the estate's signature defect — written and unwired — for the fifth time**
     (`blocked_by`, `RepoDeployer`, the tracker `/finish` button, `EvalSuite`, now `live_probes`).
     Every previous instance was found by grepping for callers, never by a gate. Nothing in the
     readiness battery asks *"does anything import this?"*, and that is the gate worth adding.

- **NOT MEASURED** — whether wiring it actually moves `certified` end to end. `certify.py`'s live
  path needs a target loaded via `load_target`, and A2/A3/A4/A6–A12 remain genuinely uninstrumented,
  so the contract will still refuse overall. **The claim here is narrow: A1 and A5 have a real
  instrument and the certification path does not call it.** Whether the aggregate verdict moves is
  the next session's discriminating test, and it must be predicted before it is run.
