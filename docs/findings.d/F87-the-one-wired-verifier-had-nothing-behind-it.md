### F87 — The one preset that claimed a WIRED verifier had nothing behind it, and the contract said so on every run

`factory/presets.py` marked `ui-control` `verifier_state=WIRED` from the day the table was
written. `WIRED` is defined in that same file as *"the check exists and has been run"*, and
`control.ticket_verifier` treats it as permission to trust a verdict. No code in this repository
performed the check, and nothing ever handed the controller a callable.

## The rule worth keeping

**A state field that describes the world, on a value the code will act on, must be checked against
the mechanism — not maintained beside it.** `verifier_state=WIRED` is a claim; a `REGISTRY` entry
is a mechanism. They now disagree loudly in `tests/test_verifiers.py`, in both directions: a
preset may not claim WIRED without a callable, and a callable may not exist for a preset that
denies it.

⭐ **The interesting part is that the code was already honest.** `ticket_verifier` had a dedicated
branch for exactly this case, with a good message — *"the declaration and the wiring disagree"* —
written by whoever built the controller, anticipating it. It fired on every single run and nobody
read it, because a run that ends UNMEASURABLE for six other reasons as well does not draw the eye
to the seventh. **An honest diagnostic nobody reads is worth about as much as a silent one**, and
this is the second time that has cost this estate real work — F74 recorded an invisible refusal
reading as a broken feature.

- **BELIEVED** — `factory/presets.py`: `ui-control` carries `verifier_state=WIRED`, and
  `boot-prompts/run-03` §7 states *"5 presets, **one** with a `WIRED` verifier"*. So one ticket
  type could reach a real PASS and four could not.

- **ACTUALLY** — **none could.** `WIRED` was a claim about a procedure a human once followed on
  GP-327, not about anything in this repository. `control.RunController` takes `verifier` as a
  constructor argument, and neither the CLI (`python -m factory.control`) nor the tracker's
  `run_ticket` ever passed one, so `self.verifier` was always `None`. Every run of the one
  "wired" preset ended:

  ```
  [UNMEASURABLE] ticket_verifier  preset 'ui-control' declares a WIRED verifier but the
                                  controller was given no callable to run. The declaration
                                  and the wiring disagree.
  ```

  ⛔ **So the run contract's only assertion about the client's problem could not pass for any
  ticket type at all.** `control.assertions` says so itself: *"every assertion above it is about
  the harness; only `ticket_verifier` is about the client's problem."* The other six were
  measuring that the factory works, and nothing was measuring that the ticket was done.

  ⚠ **And the mechanism it should have used already existed.** `factory/pbi_contract.py` — 12
  assertions, ~460 lines, complete — had **no importer**, and `factory/roadmap.py` still carries
  the line *"`grep -rln pbi_contract tests/ factory/ scripts/` returns nothing"*. It is precisely
  the check the `add-measure` preset described in prose. Two halves of one mechanism sat in the
  same package, neither knowing about the other. Same shape as F79 and F84: **the missing piece
  was never the code, it was the call.**

- **MEASURED BY** — the controller's own output, before and after. Before, on the preset that
  claimed WIRED, the line above. After wiring `add-measure` through `factory/verifiers.py`:

  ```
  $ python -m factory.control GP-401 --type add-measure --dry-run
  [UNMEASURABLE] ticket_verifier  the agent left no verification evidence at
                                  .factory/verification.json — nothing observed the ticket's
                                  actual work, so this is not a pass and not a failure
  ```

  Still UNMEASURABLE, and that is the point: it moved from *a promise the code could not keep* to
  *a measurement that has not been taken yet*, which names what to do next. With a complete
  evidence file the same path reaches **PASS=12** and, with one anchor altered, **FAIL naming
  M6-anchors-hold** — both asserted in `tests/test_verifiers.py`, and the FAIL path is asserted
  because a verifier never observed to fail is a gate that cannot fail.

  Negative controls, each confirmed red before green: deleting the registry fallback in
  `control.run` turns the two runner tests red and nothing else notices; making `ApparatusError`
  a subclass of `Unmeasurable` turns the ERROR tests red.

- **AFFECTS** — the `judgement` lane and its `honest` gate: the ticket verifier is the assertion
  that decides whether output can be trusted, and it could not be satisfied by any ticket type.
  Also the `control-plane` lane, `factory/presets.py`, `factory/control.py` and every preset row
  — `ui-control` is corrected to `AVAILABLE` in the same change, because WIRED must mean *the
  controller can run it*, which is the only sense in which the field moves a verdict.

- **KIND** — CORRECTION

- **CHANGES** — landed with this finding. `factory/verifiers.py` is the registry, joining
  `presets` to `pbi_contract`; `add-measure` is genuinely WIRED and `ui-control` drops to
  AVAILABLE; `RunController` resolves `self.verifier or verifiers.for_type(preset.type_id)`, so
  the CLI and the tracker get one without being handed it; the agent's own prompt now states
  where to leave evidence and — the load-bearing sentence — to **omit** rather than invent an
  observation. `tests/test_control_run.py` stopped naming `ui-control` as "the wired one" and
  derives it from the table instead.

  ⚠ **Still true and deliberately not papered over:** four of five presets name a check nobody
  has built, and `add-measure` cannot go green on model-layer evidence alone — M10 *every visual
  paints* and M11 *each control responds* are assertions XMLA and DAX cannot make, so a run
  without a renderer is UNMEASURABLE by design. `model-redesign` is the next candidate and needs
  that renderer; `ui-control` needs a Cosmos probe.

- **STATUS** — ADOPTED
