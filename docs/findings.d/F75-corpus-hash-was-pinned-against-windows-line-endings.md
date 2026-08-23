<!-- session: 2026-08-23 · technical/business spec + R13 -->

### F75 — The corpus hash was pinned against Windows line endings, so the tamper check has never passed anywhere else

- **KIND** — INSTRUMENT
- **STATUS** — OPEN
- **BELIEVED** — "The corpus is hash-pinned data. `MANIFEST.sha256` is verified on load, so editing
  a recorded run so a `FAILED` reads `completed` is refused with both hashes. The `corpus` gate
  going red means the corpus was tampered with."
- **ACTUALLY** — the `corpus` gate is red on **every non-Windows checkout**, and always has been,
  for a reason that has nothing to do with the corpus contents:

      sha256(bytes as stored in git, LF)         = c5eb1cb9…   ← Linux, CI, any container
      sha256(same bytes with CRLF)               = c3fbfed8…   ← what MANIFEST.sha256 pins

  The manifest was pinned from the **Windows working tree**, where `core.autocrlf` had already
  expanded LF to CRLF. Git stores LF. `factory/corpus.py:89` and `scripts/pin_corpus.py:59` both
  hash `path.read_bytes()` — raw bytes, correctly — so the pin captured bytes that only exist on
  one platform. There is no `.gitattributes` to normalise it back.

  Both files landed in the same commit (`0f1a09b`) and neither has been touched since, so this is
  not drift and not tampering: **the mechanism has never verified successfully off Windows since
  the day it was written.** It reads as tamper-evidence and behaves as a platform check.

  ⭐ **It does not merely turn a gate red — it stops the test suite collecting.**
  `tests/test_connector_contract.py` imports `factory.calibration`, which calls `corpus.load()` at
  **module scope**, so the `CorpusError` is raised during collection and pytest aborts the whole
  run. Measured on Linux at `8010676`:

      as committed            1 collection error, 7 failed, 98 passed
      manifest re-pinned to
      the bytes git stores    1 failed, 134 passed

  **36 tests either failed or never ran because of a line-ending conversion.** The one remaining
  failure is unrelated and separate — `test_lane_is_recovered_from_a_worktree_path` feeds
  `bus.lane_from_cwd` a hard-coded `C:\repos\...` path that cannot parse on POSIX.

  ⭐ **The consequence is not cosmetic, and it is upstream of the isolation ladder.** T1 and T2 in
  `docs/specs/architecture-v0.md` put agents in **containers**. A containerised agent loads the
  corpus, gets `CorpusError`, and refuses to certify — correctly, by its own rules, for a reason
  that is not about the corpus. **The trust boundary the whole certification story rests on is not
  portable to the environment we are proposing to run agents in.**

- **MEASURED BY** — from a Linux checkout at `8010676`:

      cat evals/MANIFEST.sha256          -> c3fbfed8…  corpus/windsorai-2026-08-20.json
      sha256sum evals/corpus/*.json      -> c5eb1cb9…
      grep -c $'\r' evals/corpus/*.json  -> 0          (not a CRLF working-tree artefact)
      python -c "...sha256(b.replace(b'\n', b'\r\n'))" -> c3fbfed8…   ← reproduces the pin exactly

  Then `python -m factory.readiness` from `/home/user/agent-factory`:
  `corpus  FAIL  a pinned corpus does not match its hash`. Confirm the pin has never moved with
  `git log --oneline -- evals/MANIFEST.sha256 evals/corpus/`.

  **The discriminating test** — copy the repo to a scratch directory, re-pin the manifest to
  `sha256(path.read_bytes())` there, and run `pytest`. It goes from `1 error, 7 failed, 98 passed`
  to `1 failed, 134 passed`. Nothing but the manifest line changed, so nothing else can explain it.

- **CHANGES** — re-pin from the bytes **git stores**, not from the working tree, and add a test
  that fails if the two ever differ. The cheapest durable fix is a `.gitattributes` marking
  `evals/corpus/*.json` as `-text` (never converted) plus re-running `scripts/pin_corpus.py` on a
  checkout with conversion disabled. Whichever route, **the pinning step must hash the same bytes a
  CI or container checkout will see**, and something must assert that — a tamper check that is
  green on exactly one machine is not a trust boundary, it is a local convention.

  ⚠ Do not "fix" this by relaxing the check or by hashing normalised text. Hashing raw bytes is
  correct and is what makes a swapped artefact detectable; the defect is in **what was pinned**,
  not in **how it is verified**.

- **AFFECTS** — `tests/test_connector_contract.py` (cannot be collected at all),
  `tests/test_corpus.py`, `tests/test_evaluator_isolation.py`, the `corpus` and `breadth` gates (`breadth` raises `CorpusError` for the same
  reason), every readiness measurement taken off the operator's Windows machine (compounds [[F72]],
  which found the cwd dependence — this is the *platform* dependence, and the two are additive),
  `factory/certify.py` and any remote evaluator deployment, and **every T1/T2 tier in
  `architecture-v0.md` §4**. Also §10.3 of
  `docs/specs/agent-factory-technical-and-business-spec.md`, which records it.
