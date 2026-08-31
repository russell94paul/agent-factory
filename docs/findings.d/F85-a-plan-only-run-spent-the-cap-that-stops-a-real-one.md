### F85 — Two plan-only runs made a ticket permanently unrunnable, and the test suite reached the cap the same way

Found by running `factory.control`'s first real invocation twice, in the session that landed
RUN-03. Same shape as [[F83]] and recorded for the same reason: one mechanism was quietly asked
two different questions.

## The rule worth keeping

**Reading a cap is free; writing to one is a dispatch.** Before any code touches a counter that
bounds spending, say what it is counting as a sentence. `record()` counts *"an agent was started
under this configuration"*. A dry run starts none — so it may read the counter, report that the
cap is exhausted, and refuse. What it may never do is spend one.

- **BELIEVED** — `AttemptLedger` counts dispatches, so the cap bounds how many times an agent may
  be re-run at a task. `--dry-run` composes the command and the prompt, writes them to a
  transcript, and starts nothing, so it costs nothing.

- **ACTUALLY** — `RepoDeployer.run_agent` called `ledger.record(key)` **above** the `if dry_run:`
  branch, so a plan spent an attempt exactly like a dispatch. `max_attempts` is **2**. Two
  plan-only invocations therefore exhausted the cap, and every real dispatch afterwards was
  refused by a message that forbids the only obvious remedy:

  ```
  attempt cap reached for ui-control-agent:gp-327 (2/2).
  Escalate to a human — do not raise the cap to get past this.
  ```

  Measured live, not hypothesised: `.data/attempts.json` held exactly two entries for
  `ui-control-agent:gp-327`, both `"detail": "dry run"`, `"outcome": "ok"`, and between them they
  had made GP-327 unrunnable without a human overriding a cap that was never spent on anything.
  **The first ticket the factory could execute was blocked by the act of planning it twice.**

  ⭐ **The suite could not catch it, because the suite reached the cap the same way.**
  `test_the_cap_still_refuses_and_says_so` exhausted the cap with three `dry_run=True` calls and
  asserted the third raised. It passed for the same reason the bug existed. That is [[F83]]'s
  lesson recurring one file over — *a test suite written by whoever wrote the code shares the
  code's model of the world* — and it is why the replacement exhausts the cap with `record()`
  calls, which is what a cap actually counts.

  ⚠ **A second defect sat behind the obvious fix.** `note_outcome()` writes to `attempts[-1]`.
  Moving `record()` below the dry branch while leaving `note_outcome(key, "ok", "dry run")`
  inside it makes a dry run stamp *ok* onto the **previous real attempt** — deleting a genuine
  failure from `failures()`, and so from the retry context the next real dispatch is handed. The
  agent then repeats the approach that already failed, against a cap it cannot raise. Confirmed
  by mutation: with that one call restored, `failures()` returns `[]` where a real `exit 1` had
  been recorded.

- **MEASURED BY** — discriminating test, result predicted before it ran, against a fresh ledger:

  ```python
  led = AttemptLedger(tmp / "attempts.json")          # max_attempts=2
  dep.run_agent(spec, "a task", wt, ledger=led, dry_run=True)   # count=1
  dep.run_agent(spec, "a task", wt, ledger=led, dry_run=True)   # count=2, exhausted=True
  dep.run_agent(spec, "a task", wt, ledger=led, dry_run=False)  # RuntimeError: cap reached
  ```

  Predicted refusal, got refusal. `led.context(key)` stayed `''` throughout, which bounds the
  blast radius: dry entries record `outcome="ok"` and `failures()` filters those out, so retry
  **context** was never polluted — only the **counter**. After the fix, three consecutive
  `python -m factory.control GP-327 --type ui-control --dry-run` runs leave `attempts == 0` and
  the verdict is `UNMEASURABLE`, which is the honest answer for a run nobody watched.

  Negative controls, both confirmed red before being confirmed green:
  `test_a_dry_run_does_not_spend_an_attempt` fails with the original ordering restored;
  `test_a_dry_run_does_not_overwrite_the_previous_attempts_outcome` fails with `note_outcome()`
  restored without `record()`.

- **AFFECTS** — the `control-plane` lane and its `cap` gate directly: `cap` is the claim that
  re-dispatch is bounded, and this is the first evidence that the bound can be spent by something
  that never dispatched. Also every lane that plans before it runs, and `factory/deploy.py`,
  `factory/provider.py`, `factory/control.py` — the whole execution path RUN-03 just wired.
  The tracker's "plan only" button is **not** affected: `local_tracker.run_ticket` returns from
  `ctrl.eligible()` before a provider exists, so the supervised path never reached this code.

- **KIND** — CORRECTION

- **CHANGES** — done in the same commit. `record()` moved below the dry-run return;
  `note_outcome()` deleted from that branch with a comment saying why it must not come back; the
  transcript field renamed `attempt` -> `would_be_attempt`, because it now reports the attempt a
  dispatch *would* take rather than one it has taken. `.data/attempts.json` had its two
  fabricated entries cleared (backup at `.data/attempts.json.pre-F85.bak`), which is what
  unblocked GP-327.

- **STATUS** — ADOPTED
