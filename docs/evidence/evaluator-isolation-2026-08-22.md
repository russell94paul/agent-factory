# Evaluator isolation — the evaluator is now a principal, and the boundary has been watched refusing

**Measured 2026-08-22** against `agent-factory` @ branch `feat/readiness-generator`.
Gate `isolated` moved `NOTRUN → PASS`; readiness moved **3 of 30 → 4 of 30**; the board moved
**3 done / 20 ready / 7 blocked → 4 done / 21 ready / 5 blocked**, and `certified` — the only thing
queued behind `isolated` — is now startable.

> ⚠ **Read the deployment rank before quoting the gate.** The *design* is R3's rank 1. The
> *deployment* is a loopback process under the same uid, which R3 ranks 5 and calls "mostly
> theatre". Those are not the same claim and this document does not merge them. See
> [What this does not buy](#what-this-does-not-buy).

---

## What was built

| | |
|---|---|
| `factory/evaluator.py` | `EvaluatorClient` — the agent's only route to a verdict. Three verbs, no writer. |
| `evaluator_service/` | The separate principal: `service.py` (scoring), `store.py` (write-once verdicts), `app.py` (stdlib HTTP), `__main__.py` (runner). |
| `tests/test_evaluator_isolation.py` | 16 tests, every refusal exercised against a real socket. |
| `factory/certify.py --remote` | The certification path, routed through the service instead of scoring in-process. |
| `factory/readiness.py::g_evaluator_is_a_service` | Reports measured liveness, identity, bundle hash and **deployment rank**. |

**The design, in one sentence, and it is a statement about `factory/evaluator.py`:** the agent
supplies `{artifact_uri, artifact_sha256, run_id}` and nothing else — not the corpus, not the
manifest, not the assertion set, not the evaluator. Those are resolved by the service from its own
configuration on every request.

⛔ **Not done by moving `evals/`.** `$AGENT_FACTORY_EVALS` is untouched by this change and was the
red herring R3 named: *"Moving only the files to another directory changes nothing; moving
ownership/credentials out of the agent's capability set does."*

---

## Evidence

### 1. The positive control — the known-good world still scores green, through the service

```
$ python -m factory.certify blueprints/windsorai_client_a.yaml --remote --run-id evidence-2026-08-22-green
PASS for evidence-2026-08-22-green - by local-process, bundle 41caa5d8326b
  [PASS] A1-config-satisfiable … through … [PASS] A12-tenancy-scope        (12/12)

  scored against corpus windsorai-2026-08-20 (c3fbfed83308, recorded 2026-08-20)
      — REPLAYED, not a live measurement
  recorded to C:\Users\PaulRussell\.agent-factory\verdicts\evidence-2026-08-22-green.json
exit 0
```

Without this control every refusal below would also be satisfied by a service that says no to
everything.

### 2. The four refusals, each watched happening

| # | Attack an agent with shell + repo write could actually mount | Result |
|---|---|---|
| A | **Weaken the target.** Submit a blueprint with `expect_rows: false`, empty `primary_key`, empty `non_null_positive`, no `tenant_column` | `REFUSED` — *"weaker than this evaluator's floor … A target the graded party can soften is a contract the graded party can pass."* |
| B | **Name your own corpus.** POST a body carrying a fourth field, `corpus_path` | HTTP 400 — *"not part of the submission vocabulary … The graded party supplies the artefact and nothing else."* Refused, not silently filtered. |
| C | **Swap the artefact.** Claim the real blueprint's sha256, present a different file | `REFUSED` — *"artifact sha256 mismatch — claimed fee9bbc6…, read 61386b87…"*. Not a FAIL: nothing was scored. |
| D | **Replace an unkind verdict.** Resubmit under an existing run id | Scored, **not recorded** — `recorded to NOWHERE — see store_error`; the original verdict is intact. |

### 3. Exit codes — nothing that is not a PASS exits 0

```
REFUSED           exit 1
no endpoint       exit 1      ($AGENT_FACTORY_EVALUATOR unset — not a licence to score locally)
unreachable       exit 1      UNMEASURABLE — "not a pass, and not a licence to score locally"
```

### 4. The controls were mutation-tested — they can fail

A control nobody has watched reject something is a diagram. Three mutants were introduced and
every one was caught, then reverted:

| Mutant | Caught by |
|---|---|
| Delete the corpus tenant override, letting the submission govern A12 | 3 tests, incl. `test_the_service_supplies_the_tenants_not_the_submission` |
| Make the target floor advisory (`if False:`) | `test_a_weakened_blueprint_is_refused` |
| Let the verdict store overwrite (`"x"` → `"w"`) | `test_a_verdict_cannot_be_replaced_by_a_kinder_one` |

`test_the_service_supplies_the_tenants_not_the_submission` is discriminating by construction: the
shipped blueprint's six dash-formatted account ids do **not** appear in the corpus, whose tenants
are two ten-digit ids. If the submission governed tenancy, A12 would FAIL. It passes, which is only
possible if the service overrode it.

### 5. Suite

```
$ python -m pytest
72 passed          (56 before, + 16 isolation tests)
```

---

## What this does not buy

Stated plainly, because a gate reading PASS is exactly when this list stops being read.

1. **The deployment is rank 5, not rank 1.** `http://127.0.0.1:8787` under the same uid as the
   agent. Same user can restart the evaluator, edit its source, and write the verdict store
   directly. R3: *"mostly theatre."* The gate says `loopback` in its evidence for this reason. The
   remaining gap is a managed identity the agent sandbox does not hold — **a deployment change,
   not a code change.** Nothing in `evaluator_service/` changes when it moves.
2. **⚠ The contract is parameterised by a blueprint the graded party writes.** This is the real
   hole and it survives the process boundary. Two partial answers are implemented and neither
   closes it: the artefact hash travels with every verdict (so a weakened blueprint is
   *attributable*, not silent), and `_enforce_target_floor` holds four expectations the submitter
   may not drop below. The fix is a per-connector target pinned by the evaluator. **Nobody has
   written one.**
3. **The bundle hash is not a signature** and is not claimed to be one — a signing key inside the
   agent sandbox is theatre, per R3. It buys the weaker, useful property: two verdicts can be
   checked for whether the same grader produced them.
4. **The verdict store's "one writer" is a convention on one machine**, not an enforcement.
   Anything that can run this Python can write those files. It lives outside the repo
   (`~/.agent-factory/verdicts`) so it neither sits in the tree the agent edits all day nor
   evaporates on a fresh clone — but that is hygiene, not a credential boundary.
5. **All 12 assertions are still UNMEASURABLE against a live target.** This changes *who grades*,
   not *whether the instruments are wired*. Wiring them needs credentials and explicit per-secret
   approval, which has still never been requested.
6. **The gate does not require liveness.** It asks whether the evaluator *is* a separate principal,
   which is an architectural fact, and reports liveness as evidence. A cold session with the
   service stopped will read `health check: NO ANSWER (URLError) — configured is not running` and
   still PASS. That is deliberate; if you disagree, the pass condition is three lines.

## Two words that were being asserted without measurement

Both fixed in this change, same species as the self-matching probe that once returned a false PASS:

- `g_evaluator_is_a_service` claimed **"configured and reachable"** while testing neither
  reachability nor who answered. It now calls `/health` with a 1.5s timeout and reports the
  identity, bundle hash, corpus and verdict count it got back — or says it got nothing.
- `_followup_gate` reported **"answered: R2-followup.md"** for a file that contains a *question*.
  It now says `dispatched:`, because the gate's own NOTRUN text is "not asked yet" — it tracks
  asking, and should not be readable as tracking answering.

## Reproducing

```bash
python -m evaluator_service --port 8787          # the separate principal
export AGENT_FACTORY_EVALUATOR=http://127.0.0.1:8787
python -m factory.certify blueprints/windsorai_client_a.yaml --remote --run-id <id>
python -m factory.readiness                      # 4 of 30
python -m pytest                                 # 72 passed
```

`$AGENT_FACTORY_EVALUATOR` was set durably for this user on 2026-08-22 to
`http://127.0.0.1:8787` (verified in `HKCU\Environment`: 21 characters, no quotes). Undo with
`setx AGENT_FACTORY_EVALUATOR ""`.

> ⚠ **`setx` from bash embeds the quotes.** `setx VAR "http://..."` stored the value *including*
> the `"` characters, which parses to a hostname of nothing and would have made every fresh shell
> fail to reach the evaluator while the gate still read PASS. Caught by reading the value back
> rather than trusting `SUCCESS: Specified value was saved.` Set it with
> `[Environment]::SetEnvironmentVariable('AGENT_FACTORY_EVALUATOR','http://127.0.0.1:8787','User')`
> and read it back.
