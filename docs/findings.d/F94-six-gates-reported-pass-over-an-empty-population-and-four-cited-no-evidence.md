### F94 — six gates reported PASS over an absence rather than a measurement, and four of them cited no evidence at all

One defect in six places, found by an inventory of the evaluation system and then confirmed here
with a discriminating test per gate, each prediction written from the source **before** the run.
All six predictions were correct.

## The shape

Every one of these answers a question of the form *"is anything wrong in this population?"* and
none of them checked that the population existed. `if not bad: return _pass(...)` is correct
arithmetic and a false measurement: **an empty population produces no bad rows.**

⭐ This is the rule the estate already holds every *verdict* to, unapplied one level down to the
*population*. `contract.py` exists so *"I could not look"* never reads as *"I looked and it was
fine"*. These gates looked at nothing and reported fine.

⚠ **Four of the six returned an empty evidence list**, and that is the cheap tell. A pass that
cites nothing usually counted nothing. The sibling gate `g_status_matches_reality` already reports
*"N listed, M with an event log, K actually compared"* and carries a comment saying it *"used to
report only the first"* — the discipline existed, in the same file, and had not spread.

## The six, each with the test that confirmed it

| Gate | The absence that passed | Was |
|---|---|---|
| `readiness.py` `g_success_means_correct` | one run that only ever **failed**; nothing completed | `PASS`, evidence `[]` |
| `readiness.py` `g_gates_have_checks` | pipeline defs with **every gate deleted** — `0 == 0` | `PASS`, *"every gate has a check"* |
| `readiness.py` `g_qa_gate_is_general` | `promotion_ops.py` present but **emptied** | `PASS`, evidence `[]` |
| `readiness.py` `g_repo_is_durable` | a remote **named** by a `git remote` that exited **128** | `PASS`, *"pushed to origin"*, evidence `[]` |
| `readiness.py` `g_evaluator_is_a_service` | `AGENT_FACTORY_EVALUATOR=totally-not-a-service` | `PASS`, *"a separate principal"* |
| `redesign_contract.py` `R2` | evidence file that **never mentions renames** | `PASS`, *"additive after all"* |

- **BELIEVED** — a green readiness board means the gates looked and found nothing wrong.

- **ACTUALLY** — for these six it could equally mean there was nothing to look at. Two are worse
  than that: `g_repo_is_durable` **asserted a word it never tested** — the headline says *pushed*
  while the only command run was `git remote`, whose exit code was never inspected, so a
  repository 200 commits ahead of an unreachable remote reported itself durable. And
  `g_evaluator_is_a_service` printed *"the evaluator is a separate principal (remote deployment)"*
  **directly above its own evidence line** reading *"health check: NO ANSWER — configured is not
  running"* — a headline and its evidence contradicting each other inside one result object, over
  an environment variable **the graded party sets itself.**

  ⭐ `g_evaluator_is_a_service`'s own docstring states the rule it went on to break, about an
  earlier version of itself: *"a gate that asserts a word it never tested is the same species of
  defect as a probe matching its own source."*

- **MEASURED BY** — six discriminating tests, predictions recorded before running. Verbatim:

  ```
  1 g_success_means_correct   PREDICTED PASS  OBSERVED PASS  evidence (EMPTY)
  2 g_gates_have_checks       PREDICTED PASS  OBSERVED PASS  ['0 of 0 gates ... have a gate_check']
  3 g_qa_gate_is_general      PREDICTED PASS  OBSERVED PASS  evidence (EMPTY)
  4 g_repo_is_durable         PREDICTED PASS  OBSERVED PASS  'pushed to origin'   (git exit 128)
  5 g_evaluator_is_a_service  PREDICTED PASS  OBSERVED PASS  'separate principal' (health: NO ANSWER)
  6 redesign_contract R2      PREDICTED PASS  OBSERVED PASS  {} and {"renamed":[]} INDISTINGUISHABLE
  ```

  R2's pair is the sharpest: `{}` and `{"renamed": [], "deleted": []}` returned the **same** verdict
  and the **same** detail string. The agent that never reported and the agent that reported nothing
  could not be told apart.

- **AFFECTS** — **every lane.** `factory/readiness.py` and `factory/redesign_contract.py`, and
  through them everything derived from `readiness.GATES`: `factory/board.py`, `roadmap.py`,
  `flow.py`, `goals.py` and the tracker, which renders the board an operator reads. `R2` sits in
  the contract the `model-redesign` preset is certified against — one of only two presets with a
  runnable verifier.

## ⭐ Why all six survived, which is the part worth keeping

**25 of 30 readiness gates have never been mutation-tested.** `scripts/mutate_readiness_probes.py`
covers exactly five — `cap`, `bounded`, `concurrency`, `reaper`, `from-history` — and every one of
them measures the *connectors* repo. **Every gate that measures agent-factory itself is outside the
negative control.** That is not a coincidence with these six; it is the reason for them.
`tests/test_readiness_probes_can_pass.py` says as much about its own limits at `:14-19`: it is a
static AST check proving a PASS branch is *written*, and *"a probe guarded by `if False:` would
satisfy this test."*

- **KIND** — INSTRUMENT

- **CHANGES** — each gate now separates *measured and clean* from *nothing to measure*, using the
  verdict the estate already has for it:

  - `g_success_means_correct` — counts completed runs; `NOT_RUN` when none, and the PASS now cites
    how many it examined.
  - `g_gates_have_checks` — `NOT_RUN` on an empty gate set, because zero of zero is not coverage.
  - `g_qa_gate_is_general` — a **positive control** before believing an absence: the file must
    carry at least one `def` and one mention of `deployment`, else `Unmeasurable`. Anchors
    calibrated against the real file (`prefect-connectors@main`: 241 lines, 7 defs, 48 mentions),
    not guessed.
  - `g_repo_is_durable` — inspects the exit code, then **measures the word in its own headline**
    with `git log --branches --not --remotes`. FAILs while any commit exists only on this disk.
  - `g_evaluator_is_a_service` — the endpoint must parse as an `http(s)` URL. ⚠ Reachability
    stays **deliberately out** of the pass condition, per the author's stated reasoning: the gate
    asks whether the evaluator *is* a separate principal, not whether it is up this second, and a
    service that is merely down is still a principal. A string that is not an endpoint names no
    principal at all — a different claim, and the one that was going green.
  - `R2` — distinguishes an absent key from an empty list, applying the sentence already written
    twelve lines below it for the dependents list: *"An absent list is NOT-VISIBLE, not 'nothing
    depends on it' — enumerate, never assume."*

  15 tests in `tests/test_gates_refuse_an_empty_population.py`. ⭐ **Every refusal is paired with a
  positive control** — the same gate, given a real population, must still reach both PASS and FAIL
  — because a gate that refuses everything would satisfy the refusal tests and has been disabled
  rather than fixed.

  ⚠ **Measured: the board did not move.** All five readiness gates return the identical verdict in
  the real estate before and after, because the real populations are non-empty and the real
  endpoint is well-formed. Only `g_repo_is_durable`'s headline changed — from *"pushed to
  personal"*, asserted, to *"every commit has reached personal"*, measured. **The fixes bite only
  in the degenerate cases that were silently green.** Full suite: 16 failures before, 16 after, the
  same 16 — no regression.

  ⛔ **Not done, and it is the larger half:** the 25 uncovered gates still have no negative control.
  Six were found by inventory; nobody has shown the other 19 can fail.

- **STATUS** — ADOPTED
