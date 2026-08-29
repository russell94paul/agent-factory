<!-- session: 2026-08-29 · absorption backlog import + AB-04 -->

### F76 — The eval has been proved able to fail. What is unproven is that it generalises past one connector

- **KIND** — INSTRUMENT
- **STATUS** — ADOPTED
- **BELIEVED** — "the corpus is one file, 6,747 bytes, so the instrument has not been shown able to
  register a failure; the README's precondition therefore still blocks a team, an optimizer and a
  UI." Stated in `SYNTHESIS.md` §17.9 (R16 audit §3.1 — *"and no action among the eighteen names
  it"*), carried into `docs/absorption-backlog.md` AB-04 and into the 2026-08-29 session plan as
  "Phase 3 — prove the instrument can fail".
- **ACTUALLY** — the contract is calibrated and **has** been proved able to fail. Three separate
  facts, none of which the corpus-size claim distinguishes between:
  1. `tests/test_connector_contract.py` holds **17 tests** whose stated purpose is exactly this —
     *"The point of this file is not that the contract passes. It is that each assertion has been
     shown to FAIL when the thing it claims to measure is broken."* It includes a meta-test,
     `test_every_assertion_has_been_proved_able_to_fail`, so the property is enforced rather than
     asserted, and it separates `UNMEASURABLE` from `FAIL` in three further tests (unconfigured
     probes, a crashing instrument, a missing session id).
  2. ⚠ `tests/test_eval_can_fail.py` — the file the README names as **the** gate — **does not touch
     the corpus at all.** It builds a synthetic three-assertion contract inline over a hardcoded
     three-key dict. It proves the *mutation harness* works. It proves nothing about the real
     connector contract, and passing it was never evidence about the corpus either way.
  3. The README's own status block is stale: it reports
     `UNMEASURABLE (PASS=11, UNMEASURABLE=1)` with A12 blocking on an undeclared tenant scope. The
     real current output is **`PASS (PASS=12)`** — A12 passes, *"every row within the 2 declared
     tenant(s)"*.

  **What is genuinely missing is breadth, not sensitivity.** The contract has been replayed against
  exactly **one** real recorded run. Its failure modes have been demonstrated by *mutating that one
  world*, which shows each assertion is wired to its subject — it does not show the contract holds
  on a second connector, and 48 connectors remain.
- **MEASURED BY** — all four, 2026-08-29 at `00f9620`:
  - `python -m factory.certify blueprints/windsorai_gep.yaml --calibrate` → `PASS (PASS=12)`, every
    assertion listed, footer *"REPLAYED, not a live measurement"*.
  - `python -m pytest tests/test_eval_can_fail.py tests/test_corpus.py -q` → **10 passed**.
  - `grep -n "corpus" tests/test_eval_can_fail.py` → **no hits** (the only `corpus` references in
    that grep were in `factory/evals.py`).
  - `grep -c "^def test_" tests/test_connector_contract.py` → **17**; `factory.corpus.available()`
    → **1** fixture, `c3fbfed83308…`.
- **CHANGES** — README status block corrected to `PASS (PASS=12)`. `AB-04` in
  `docs/absorption-backlog.md` restated: it is a **breadth** task (replay against a second and third
  real connector), not a sensitivity task. No test or contract code was altered.
- **AFFECTS** — AB-04; build-order step 8 (*"expand and freeze the evaluation corpus"*); and most
  importantly **the README's blocking precondition, which is met**: *"Do not add a team, an
  optimizer or a UI until `pytest tests/test_eval_can_fail.py` passes"* — it passes, and the real
  contract is calibrated besides. Anyone treating the one-file corpus as the reason nothing
  downstream may start has inherited a premise that conflates *"the instrument cannot fail"* with
  *"the instrument has only seen one subject"*. Those need different work and only the second is
  outstanding.

  ⭐ The general rule: **a corpus-size number answers a coverage question and is silent on a
  sensitivity question.** Quoting it as evidence for either is how one measurement gets asked to do
  two jobs.
