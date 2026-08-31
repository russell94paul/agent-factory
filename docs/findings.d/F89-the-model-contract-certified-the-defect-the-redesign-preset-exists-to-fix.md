### F89 — The Power BI contract scored PASS=12 on the exact defect `model-redesign` exists to find, and could never have passed a redesign anyway

Two measurements, taken before wiring `model-redesign`, and either one alone would have made
reusing `verifiers.pbi_model_change` for it dishonest. Recording them together because the pair is
the finding: the contract was **simultaneously too strict to certify a redesign and too blind to
catch the thing a redesign is for**.

## The rule worth keeping

⭐ **Before reusing a contract for a second ticket type, run its own named defect through it and
watch it fail.** The M-contract is the most careful artefact in this repository — it opens by
explaining that a check can pass while every visual is broken, and it keeps two assertions no
instrument can currently make rather than quietly dropping them. It was still wrong for this
ticket type in two directions at once, and **both were invisible from reading it.** Ten minutes of
pointing the existing check at the new problem is worth more than any amount of reading it.

⚠ **This is the fifth blind instrument in eleven days** (F80 wrong branch, F81 probes that cannot
fail, F84 a grep that cannot see, F86 a ledger that cannot parse) — and the first where the blind
instrument was our own newest and most careful one. The others were old, thin, or hand-written.
This one is 460 lines of well-argued assertions that warn, in their own docstrings, about
certifying the wrong layer. **Care is not coverage.**

- **BELIEVED** — `model-redesign` is a larger `add-measure`: both are Power BI model changes, both
  are exactly what `factory/pbi_contract.py`'s M1-M12 was written to certify, so wiring it means
  adding one row to `verifiers.REGISTRY`. The preset's own prose — *"pre/post assertion battery —
  capture live state before overwriting, replay after"* — reads like a description of M1 and M7.

- **ACTUALLY** — two independent falsifications.

  **1. A redesign is permanently UNMEASURABLE under M1-M12.** `M4-additive-manifest` opens with
  `if not target.additive_only: raise Unmeasurable("target does not declare additive_only —
  blast radius uncertified")`. A redesign renames and deletes by definition, so it must declare
  `additive_only=False`, so M4 refuses, so the whole contract returns UNMEASURABLE **however
  perfect the work is**. Registering the preset against that verifier would have wired a gate
  that cannot pass — a verifier the agent cannot satisfy, which is the trap [[F87]] was recorded
  about, reached from the other direction.

  ⭐ M4's refusal was *correct*. It says the mechanism to certify a non-additive change does not
  exist. The answer is to build that mechanism, not to relax the assertion — `R2` requires every
  rename and deletion to carry its dependents, **enumerated and rewritten**, because a TOM rename
  does not rewrite the DAX that references the old name.

  **2. ⛔ M1-M12 scores PASS=12 on this preset's signature defect.** The preset names it in its
  own `model_why`: *"a slice that returns the grand total on every member — it neither errors nor
  blanks, so it looks healthy."* Evidence in which the Brand slicer responds, all 14 visuals
  paint, every anchor holds, the warehouse agrees, and `ME Spend` returns **2,890,054.50 — the
  grand total — for every single brand** is scored:

  ```
  pbi-model-change/ds-66151728: PASS (PASS=12)
  ```

  `M11-controls-respond` is satisfied by `responded: True`, and a repainting visual reports
  exactly that whether or not the number changed. **`interact` asks whether the control
  responded; nothing asked whether the numbers moved.** The contract had no field in which the
  fact could even be written down, which is why reading it does not reveal the gap: there is
  nothing there to look wrong.

- **MEASURED BY** — both against the committed contract, each predicted before it ran.

  ```python
  # 1. a redesign, declared honestly
  ev["target"]["additive_only"] = False
  ev["observations"]["writes"]["renamed"] = ["GASP -> Gross Ad Spend"]
  verifiers.pbi_model_change({"worktree": tmp})
  # -> Unmeasurable: [UNMEASURABLE] M4-additive-manifest: target does not declare
  #    additive_only — blast radius uncertified                        (predicted, got)

  # 2. the inert axis, with every other fact perfect
  ev["observations"]["interact"]["controls"][1] = {"name": "Brand filter", "responded": True}
  # ME Spend returns the grand total for Acme, Borealis and Cinder alike
  verifiers.pbi_model_change({"worktree": tmp})
  # -> (True, 'pbi-model-change/ds-66151728: PASS (PASS=12)')          (predicted, got)
  ```

  Both are now pinned as tests, the second as
  `test_the_m_contract_certifies_the_defect_this_preset_exists_to_fix`, which asserts the
  M-contract still says PASS on that evidence **and** the redesign contract says FAIL. It fails
  if either half stops being true, so it cannot rot into a tautology.

  Negative controls, confirmed red before green: making R3 accept identical members turns two
  tests red including the load-bearing one; dropping R3 from the assembly turns six red.

- **AFFECTS** — the `judgement` lane and its `honest` gate directly: a contract that returns PASS
  over an inert axis is the precise failure `honest` exists to refuse, and this is the first
  measured instance inside our own certification path rather than in a client deliverable. Also
  `factory/pbi_contract.py`, `factory/presets.py` and `factory/verifiers.py`, and the
  `control-plane` lane insofar as it owns which checks a dispatched agent is held to.

- **KIND** — INSTRUMENT

- **CHANGES** — landed with this finding. `factory/redesign_contract.py` builds M1-M12 with M4
  replaced by **R2** (renames carry enumerated, rewritten dependents) and adds **R1** (the
  pre-state captured *before* the overwrite, across an enumerated population — GP-318 audited 356
  measures, and a redesign checked against a sample is not checked), **R3** (⭐ no declared axis
  is inert), and **R4** (every captured measure was actually replayed — a coverage assertion, not
  a value one). `pbi_contract` gains two probes (`pre_state`, `slices`) and two optional target
  fields; `build_contract` still returns exactly its twelve assertions, asserted by a regression
  test, so `add-measure` is untouched. The substitution of M4 is *verified* at build time and
  raises rather than silently shipping one fewer check.

  ⚠ **R3 is only as wide as `must_slice_by`.** Declaring no axes is UNMEASURABLE, not PASS — the
  cheapest route to a green redesign must not be declaring nothing — but the contract still
  cannot know which axes *should* have been declared. That is a real limit, not a defect, and it
  is the same shape as M10's dependence on `bound_reports`: **enumeration is the agent's
  obligation, and the contract's job is to refuse to pass without it.**

- **STATUS** — ADOPTED
