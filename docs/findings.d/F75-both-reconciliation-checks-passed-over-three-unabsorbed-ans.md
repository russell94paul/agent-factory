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
