<!-- session: 2026-08-23 · tracker stabilisation + R17/R18 -->

### F75 — Both reconciliation checks passed while three answers sat unabsorbed, and only an agent reading them found out

- **KIND** — INSTRUMENT
- **STATUS** — OPEN
- **BELIEVED** — "`unsynthesised()` and `unreconciled()` together tell us whether the decision
  record has kept up. When both are empty, the only outstanding work is whatever they name."
- **ACTUALLY** — they measure **mention** and **modification time**, and the gap between those and
  *absorption* is roughly 3× wider than either can see. Immediately before the R18 reconcile ran,
  the instruments read:

  ```
  unsynthesised: []          every filed answer is MENTIONED somewhere
  unreconciled: ['R18']      only R18 postdates the last SYNTHESIS.md edit
  ```

  The session that then read the answers found **R13 run 2 substantially unabsorbed, R14
  unabsorbed, and R18 entirely unabsorbed** — and `SYNTHESIS.md` stating **twice** that R14 *has
  not run*, while R14's answer has been `ANSWERED` and on disk since 2026-08-23.

  ⭐ **That is [[F-the-R8-case]] repeating exactly, in the same document, after the check written
  to catch it.** A sentence saying *"R14 has not run"* **mentions R14**, so the mention check is
  satisfied by a claim that is the opposite of absorption. `unreconciled()` was added precisely
  because mention was known to be weak — but mtime is cleared by *any* edit, including the edit
  that absorbs one answer while three others stay untouched. Reconciling R17 cleared the mtime
  signal for R13, R14 and R18 as a side effect.

  ⚠ Neither check is wrong about what it measures. The failure is that **both were read as a
  verdict on the record's health**, and their combined blind spot is unbounded: a document can
  discuss every filed id, in any tense, and be edited daily, while absorbing nothing.

- ⛔ **RECURRED 2026-08-29, on the same two answers, and this time it was predicted before it
  happened.** The R19 reconciliation was dispatched from the tracker. Measured at 19:05, before it
  wrote:

  ```
  unsynthesised: ['R19']                 unreconciled: ['R14', 'R18', 'R19']
  gap the launched session was given:    ['R19']          <- R14 and R18 never named to it
  ```

  **Cause, now located** — `session_prompt()` computed `gap = unsynthesised() or unreconciled()`.
  An `or`, so the stronger check was consulted only when the weaker one was already clean; and
  `prompt()` read `unsynthesised()` alone. The session was therefore *instructed* to write a
  partial reconciliation, and the write at 19:24:08 (+12 lines) cleared `unreconciled()` for all
  three. Post-write both checks read `[]`.

  ⭐ **R14 and R18 have now been swept twice — once by the R17 reconcile on 2026-08-23, once by the
  R19 reconcile on 2026-08-29 — and remain unabsorbed.** Their answer files' **mtimes** were
  2026-08-29 14:32 (mtime is last-written, not first-filed — but mtime is exactly what
  `unreconciled()` compares, so it is the right clock for this claim); every one of the 33 `R14`
  and 25 `R18` mentions in `SYNTHESIS.md` predates that. The instrument can no longer report this:
  it is recorded here because after the write there is nowhere else it survives.

  ✅ **Corroborated independently.** The R19 session went on to write ~425 lines and reached the
  same conclusion from the other direction, unprompted: *"the newest answer now has a section while
  R14 and R18 still do not"*, and *"R14 (1,389 lines, filed 08-23) and R18 (614 lines, filed 08-23)
  still have no section."* Two instruments, one mechanical and one an agent reading the documents,
  agreeing that the two swept answers are unabsorbed — which is as close to confirmation as this
  finding's subject allows, since F75's whole point is that absorption is not mechanically
  detectable.

  **Partial fix applied 2026-08-29** — `factory/synthesis.py::outstanding()` now returns the union
  of both checks and both prompts name every outstanding id, with a stated refusal to fold in a
  subset. That closes the *dispatch* mechanism: a session can no longer be told to write partially.
  ⚠ **It does not close this finding.** The blind spot F75 is actually about — mention and mtime
  are not absorption — is untouched, and a session that reads all three and writes one sentence
  each still clears both checks. This is not option (a), (b) or (c) below; it removes one way the
  gap gets *created*, not the gap. Regression: `tests/test_synthesis_current.py
  ::test_union_is_proved_on_a_synthetic_record`, proved against a synthetic record because the live
  one closed to empty mid-fix — which is itself the reason the earlier live-state tests were
  vacuous.

- **MEASURED BY** — `python -c "from factory import synthesis as s; print(s.unsynthesised(),
  s.unreconciled())"` → `[] ['R18']` at 18:04 on 2026-08-23, with `test_synthesis_current` green.
  The contradicting evidence is the reconcile session's own reading of `docs/research/answers/`
  minutes later, plus `grep -n "R14" docs/research/SYNTHESIS.md` returning two future-tense claims
  that R14 had not run. The three unabsorbed answers were invisible to both checks and to the
  suite.

- **CHANGES** — undecided, and the honest options are all worse than they sound:

  (a) **Accept and label.** The `/research` panel already says in print that neither check can tell
  a real reconciliation from one sentence per answer. Cheapest, changes nothing, and this finding
  is the evidence that the label is not enough on its own — the checks were still read as a verdict.

  (b) **A per-answer absorption marker** — the reconciling session records which answer ids it
  actually read and folded in, and the check compares that list against `filed()`. Turns a
  document-level heuristic into a claim the worker makes. ⚠ It is then only as honest as the
  worker, which is the same trust boundary as every other agent self-report here.

  (c) **Tense/negation detection** on the mention check — reject a mention that appears inside
  *"has not run"*, *"still outstanding"*, *"when X lands"*. Cheap, and **it is a refuse-list, so it
  is wrong by omission** — the exact defect shape recorded for the DAX answerability guards.

  ⛔ **Do not simply tighten `unreconciled()` to per-answer mtime comparison.** It would have caught
  this instance and still cannot distinguish absorption from an edit that touched the file. A
  stricter proxy for the same unmeasured thing reads as a fix and is not one.

- **AFFECTS** — anyone reading `unsynthesised()`/`unreconciled()`/`test_synthesis_current` as
  evidence that the decision record is current; the `/research` Decision-record panel; and any
  future gate tempted to certify "the record is up to date". Until this is decided, **treat both
  checks as detecting a record nobody touched, and nothing subtler** — the only instrument that has
  ever found an unabsorbed answer here is an agent that read the answers.
