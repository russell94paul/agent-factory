# Phase A — the GreenContract, calibrated on `windsorai`

**2026-08-20.** Implements `aldc-launchpad/docs/specs/green-contract-exchangeratesapi.md` as
running code, generalised to any connector, and calibrated against the one connector in this
estate with a recorded end-to-end success.

**Verdict: the contract is proved able to fail on all twelve assertions, and it refuses to
certify `windsorai` today.** The refusal is the deliverable, not a shortfall.

---

## What was built

| File | What it is |
|---|---|
| `factory/connector_contract.py` | A1-A12 as executable assertions, parameterised by target |
| `factory/targets.py` | blueprint -> `ConnectorTarget`; unknown keys raise rather than pass silently |
| `blueprints/windsorai_client_a.yaml` | the windsorai target, every field labelled MEASURED / DERIVED / ASSUMED |
| `factory/calibration.py` | the known-good world, rebuilt from the 2026-08-20 run |
| `factory/certify.py` | CLI emitting a JSON verdict — the shape `verify-qa-success` should call |
| `tests/test_connector_contract.py` | the calibration matrix, 29 cases |

`pytest -q` → **47 passed** (18 pre-existing, 29 new).

## Calibration — the three runs the spec asked for

| # | Run | Expected | Observed |
|---|---|---|---|
| 1 | Known-good world, tenancy filled | PASS | **PASS**, 12/12 — the contract does not cry wolf |
| 2 | Mutate the credential to HTTP 401 | A2 FAIL, contract not green | **FAIL** |
| 3 | Drop one requested account from the landing | A9/A10 FAIL while A6 still PASS | **FAIL on A9 and A10, A6 PASS** |

Run 3 is the one that matters: it reproduces the shape of both historical failures in this estate
— a mechanism reporting success over a population it could not see.

## Every assertion has been observed failing

`test_every_assertion_has_been_proved_able_to_fail` compares the assertions the contract declares
against the mutations registered for them, and names any that has never been shown to fail. Adding
an A13 without a mutation turns the suite red.

Two cases carry the argument on their own:

- **`test_silent_empty_is_caught_by_a7_while_a6_still_passes`** — the runtime swallows non-200
  responses and returns an empty dataframe, so the flow run reaches COMPLETED with nothing landed.
  A6 passes. A7 fails. That gap is the entire reason the contract exists.
- **`test_rows_from_a_previous_run_do_not_satisfy_a7`** — a table a prior run populated returns a
  healthy row count and proves nothing about this one. Only the session-id stamp does.

## ⭐ A hole the calibration found, that review did not

The first run of the matrix passed a **partial extraction**: an entire account dropped from the
landing, and A9 reported *"18 rows satisfy every declared invariant."* Cause: the completeness
invariant was guarded on `target.required_keys`, which the blueprint left empty, so the check
silently did not run.

Fixed structurally rather than by filling the list — the requested keys now come from the live
config observation, and when neither the blueprint nor the config can supply them, A9 raises
`Unmeasurable`. **An invariant that quietly does not run is an assertion that quietly stopped
being made**, and that is indistinguishable from a pass unless the harness says so.

## What the contract says about `windsorai` today

```
connector-e2e/windsorai@CLIENT-A: UNMEASURABLE (PASS=11, UNMEASURABLE=1)
  [UNMEASURABLE] A12-tenancy-scope: target declares no tenancy scope — cannot certify blast radius
```

Eleven assertions pass against the recorded run. The twelfth blocks, and should: one ALDC Windsor
key returns **every** client's accounts, so an unfiltered pull lands CLIENT-B rows in a CLIENT-A table
and nothing downstream can tell. `allowed_tenants` is empty because nobody has written the CLIENT-A
account ids down. Until someone does, this connector is not certifiable — which is a true
statement about the estate, not a limitation of the harness.

## Open questions this produced — for a human, not a researcher

1. **The declared primary key cannot be right, or the grain isn't what we think.** 20 rows across
   18 distinct campaigns on a single date cannot satisfy a unique `(account_id, campaign_id, date)`
   under one account. The calibration world assumes two accounts with two shared campaign ids. If
   the real table holds one account, the PK is wrong and A9 will say so on the first live run.
2. **The image digest in the evidence is truncated** to `sha256:d2d7193bc096ae149` (19 chars). A4
   matches byte-for-byte, so `expected_image_digest` is left empty rather than pinned to a prefix.
   Re-measure from the registry before pinning.
3. **No pinned test revision exists.** 721 passed on 2026-08-20, but pinning a count is wrong the
   moment a test is added. A5 needs a test-tree revision hash.
4. **Which CLIENT-A account ids are in scope?** Blocks A12, and therefore blocks certification.

## Not done

- **No live probes.** `Probes` refuses everything by design; `CtxProbes` serves the eval corpus.
  Prefect / Snowflake / registry / API implementations are the next unit of work, and each needs
  credentials — none were requested or used in this session.
- **The eval corpus still lives inside the repo the agents can write to.** The spec requires it
  outside any agent-writable directory. Structural, not cosmetic, and not yet done.
- **Nothing has been run against the live warehouse.** Every number here is replayed from the
  2026-08-20 evidence, not re-queried.
