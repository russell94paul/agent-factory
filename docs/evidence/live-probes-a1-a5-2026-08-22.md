# A1/A5 wired to a real instrument — evidence, 2026-08-22

**Claim:** `factory/live_probes.py::WindsorAiGepProbes` is a real (non-refusing) `Probes`
subclass for two of the twelve GreenContract assertions, reachable from the `prefect-connectors`
checkout on disk with **no credential and no network call**. Every other assertion still
refuses. This file is the "watched refusing" / "watched succeeding" pair the lane brief asked
for, plus the one wrong premise found and fixed along the way.

## 1. Watched succeeding — A1, real construction

```
$ python -c "
from factory.live_probes import WindsorAiGepProbes
print(WindsorAiGepProbes().config({}))
"
{'constructed': ['WindsorAIConnection', 'WindsorAIOptions'], 'accounts': ['389-957-4788', '842-825-0313', '126-436-3882', '524-661-7349', '703-152-5903', '232-341-9629']}
```

Both classes come from `connector.connectors.windsorai` in the real `prefect-connectors`
checkout, imported live (not mocked); the account ids come from
`connector/accounts/GEP/deployments/windsorai.py::_GOOGLE_ADS_ACCOUNT_IDS`, the module the real
flow actually uses. `WindsorAIConnection(api_key=...)` is constructed with a placeholder string
— this proves the class *accepts* the shape the blueprint declares, nothing about whether that
key would authenticate. That remains A2, and A2 is still unwired.

## 2. Watched refusing — no checkout

```
$ python -c "
from factory.live_probes import WindsorAiGepProbes
WindsorAiGepProbes(connectors_root='Z:/nowhere/prefect-connectors')
"
Traceback (most recent call last):
  ...
factory.contract.Unmeasurable: no prefect-connectors checkout at Z:\nowhere\prefect-connectors — set $PREFECT_CONNECTORS
```

And through `probes_for()`, the same absence degrades to the base refusing `Probes()` rather than
raising out of `factory.certify` entirely — see `test_probes_for_falls_back_to_base_probes_when_checkout_absent`.

## 3. Watched refusing — unparseable suite output

`test_suite_reports_unmeasurable_when_pytest_prints_no_summary` feeds `suite()` a fake
subprocess result with no `passed`/`failed` line; it raises `Unmeasurable`, not a fabricated
zero.

## 4. The full contract, live, against the real checkout

```
$ python -m factory.certify blueprints/windsorai_gep.yaml
connector-e2e/windsorai@GEP: FAIL (PASS=1, FAIL=1, UNMEASURABLE=10)
  [PASS] A1-config-satisfiable: constructed 2 classes, 6 account(s)
  [UNMEASURABLE] A2-credential-authenticates: no instrument configured for credential
  [UNMEASURABLE] A3-exact-image-resolves: no instrument configured for image
  [UNMEASURABLE] A4-deployment-binding: no instrument configured for deployment
  [FAIL] A5-regression-suite: 1 failing test(s)
  [UNMEASURABLE] A6 .. A12: no instrument configured for ...
```

**A5 is a real FAIL, not a fabricated one.** The full `prefect-connectors` suite currently has
one pre-existing, unrelated failure:

```
FAILED tests/orchestrator/test_logbook.py::TestResolution::test_recurrence_after_resolution_is_marked_regressed
  - AssertionError: assert 'RESOLVED' == 'REGRESSED'
1 failed, 825 passed, 1809 warnings in 57.60s
```

This has nothing to do with windsorai — it is orchestrator logbook-state logic. Reporting it as
`FAIL` rather than silently passing is the whole point of A5: the assertion is "the pinned suite
is green", and today it is not, for a reason A5 correctly surfaces. `target.pinned_test_revision`
is still empty (nobody has pinned one yet — see the blueprint's own ASSUMED note), so this FAIL
is about the failing test existing, not about a revision mismatch.

**Ten assertions remain `UNMEASURABLE`.** No credential was requested or used to reach this
state; `Probes._refuse` is doing exactly what it is designed to do for A2–A4 and A6–A12.

## 5. A premise corrected along the way

`blueprints/windsorai_gep.yaml` declared `connection_class: WindsorAiConnection` /
`options_class: WindsorAiOptions` (mixed-case "Ai"), commented **"DERIVED ... not yet read from
source."** Reading `connector/connectors/windsorai.py` directly shows the real classes are
`WindsorAIConnection` / `WindsorAIOptions` (all-caps "AI"). Left uncorrected, A1 would have
FAILed on every live run for a blueprint typo, not a connector defect — indistinguishable from a
real regression unless someone read the source. Fixed in the same commit as the probe, along
with `evals/corpus/windsorai-2026-08-20.json`'s `config.constructed` list, which encoded the same
typo (self-consistent with the old blueprint value, not independently measured) — re-pinned via
`scripts/pin_corpus.py`.

## 6. A trap this session walked into and backed out of

`live_probes.py`'s first draft of `_default_connectors_root()` preferred
`.worktrees/prefect-connectors` — a path that did not exist when this module was started, but
was created mid-session by the `control-plane` lane doing its own unrelated work in
`prefect-connectors`. Because the search picked "first path that exists," this probe silently
started reading a different lane's concurrently mutating checkout on a different branch instead
of the canonical `repos/prefect-connectors`. Caught by comparing `WindsorAiGepProbes().root`
against what it should have been, not by any test (there wasn't one for this yet, since the
existence of that path was itself the failure mode). Fixed to always prefer the canonical
checkout; `$PREFECT_CONNECTORS` still overrides explicitly. See `docs/findings.md`.

## 7. Opus review, and what it found

An adversarial opus review ran over the diff before this lane closed. It found six real defects
in `factory/live_probes.py` (none in the direction UNMEASURABLE→PASS via the fallback path — it
confirmed that direction was safe) and one test that couldn't fail. All were fixed in the same
session, verified against real (not just mocked) behavior where the review's own reproduction
made that possible:

1. **A5 could read a suite with a real error as a clean PASS.** `suite()` only parsed
   `passed`/`failed`; pytest's separate `error` bucket (fixture/setup failures) matched neither.
   Reproduced live: `1 passed, 1 error` (exit 1) reported `{"failed": 0}`. Fixed — `error` is
   parsed and folded into `failed`, and the parsed counts are now cross-checked against the
   process's own exit code (0 vs 1 vs anything else), raising `Unmeasurable` on any of the three
   disagreeing rather than trusting text parsing alone.
2. **The revision was a proxy that could pass blank, and never checked for a dirty tree.** A
   failed `git rev-parse HEAD` fell through to an empty string rather than `Unmeasurable`, and a
   dirty working tree (the real prefect-connectors checkout has one right now — untracked files
   from unrelated work) was reported under a clean-looking sha even though `suite()` runs the
   working tree, not the commit. Fixed — `_revision()` raises on a failed lookup and appends
   `-dirty` when `git status --porcelain` is non-empty.
3. **The one test tying A5's detail to a real number was a no-op.** `"15 passed" in detail or
   "passed at" in detail` — the second clause is a substring of every possible PASS detail, so
   the assertion could not fail regardless of the count. Fixed to assert `"15 passed"` alone.
4. **The default connectors-root path was depth-dependent, not anchored.** `here.parent.parent.parent`
   is only correct when this file sits inside `.worktrees/<lane>/factory/`; one level shallower
   (the main clone, which is what this lane merges into) it silently pointed one directory too
   high, and the affected tests would silently *skip* rather than fail, so the loss would not
   show up as red. Fixed — the default now resolves via `git rev-parse --git-common-dir` (always
   the main clone's `.git`, worktree or not), independent of nesting depth; a new test verifies
   this against a fresh, independent git call rather than a hardcoded expected path.
5. **`probes_for()`'s fallback discarded which refusal happened.** A missing checkout and "nobody
   has wired A1/A5 at all" both produced the identical `Probes()` message, `no instrument
   configured for config` — hiding a real regression (checkout vanished, env var unset) behind
   text byte-for-byte identical to the pre-wiring baseline. Fixed — a new `_BlindWindsorAiProbes`
   carries and re-raises the specific reason on A1/A5 only; everything else still uses the
   generic base-class refusal.
6. **A moved probe hook could make A1 accuse the connector instead of the probe.** `config()`
   read `_GOOGLE_ADS_ACCOUNT_IDS`/`_GOOGLE_ADS_FIELDS` (private constants in the deployment
   module) via `getattr(..., default)`, so if either disappeared upstream, A1 would report "did
   not construct" / "no accounts resolved" — a FAIL, blaming the connector for this probe's own
   hook breaking. Fixed — absence of either constant now raises `Unmeasurable` naming the missing
   hook; construction failures are now caught narrowly (`pydantic.ValidationError` only), so any
   other exception propagates and is converted to `UNMEASURABLE` by the contract harness instead
   of being silently swallowed.

A seventh finding — the blueprint's `primary_key` is still missing a field (`source`) present in
the connector's own declared merge key — was **not** fixed here; see `docs/findings.md` F32. That
field belongs to the `grain` lane by file locality, and is flagged rather than edited to avoid
racing that lane's live measurement.

## Command log

```
python -m pytest tests/test_windsorai.py --no-header --tb=short -q         # 15 passed, no secret
python -m pytest --no-header --tb=no -q -p no:cacheprovider                # 1 failed, 825 passed
python -m factory.certify blueprints/windsorai_gep.yaml                    # FAIL, as above
python -m pytest tests/test_live_probes.py -v                              # 15 passed, ~34s
python -m pytest (agent-factory, full)                                     # 103 passed, ~33s
```

No vault, no Key Vault, no credential of any kind was read or requested to produce any line
above.
