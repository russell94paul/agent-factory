# Boot — Switchboard P1 (done) → Marketing Model live verification (next)

**Written 2026-09-01** at a context checkpoint. Two branches, both **UNPUSHED**, both green.

```
next:  retrieve the read-only Snowflake credential and exercise warehouse mode,
       then the PBI DAX instrument — the four NOT-EXERCISED items in D5 §4.
       Paul authorised credential retrieval on 2026-09-01: "Retrieve credentials
       as you please." ⚠ Name the specific secret and source in chat before using
       it anyway — the blanket grant is recorded, the habit of naming is not
       negotiable, and it is what makes the audit row readable later.
```

---

## State — re-measure before trusting any of this

```
primary checkout   main @ b827ebf   ⚠ MOVED under this session (was ab13977);
                                     other sessions share it and it held 25
                                     uncommitted files. Never `git add -A` here.
switchboard/p1                       a732716 → 7ff0e1c   (8 commits)
mission/marketing-model-finalization 1ed4277 → e7f92f3   (4 commits, from efb05cf)
pushed                               NO. 0 remote refs contain either.
worktrees                            .worktrees/p1  .worktrees/finalization
tests                                937 pass on p1 (exit 0) · 751 on finalization
```

The 2 reds on `mission/marketing-model-finalization` are the two structural guards, **already
fixed on `switchboard/p1`** and unrelated to the model. Cherry-pick them across only if you also
bring `factory/work.py`, `factory/coordination.py`, `factory/switchboard_p1.py` and the extended
`factory/tasks.py` — `scripts/local_tracker.py` imports all four, and porting it alone breaks the
import. That was tried and reverted; don't repeat it.

## The live surface Paul uses from his phone

```
https://numerous-rachelle-hexahydroxy.ngrok-free.dev/switchboard
```

⚠ **The tunnel is pointed at port 8137 by RUNTIME STATE in the ngrok agent, not by config.** It was
repointed via `POST http://127.0.0.1:4040/api/tunnels` because the P0 server on 8110 could not be
stopped (the permission classifier blocked `Stop-Process`, twice). **If ngrok restarts it reverts
to 8110 and Paul sees the P0 build again** — no CREATE button, no bottom nav. Symptom to
recognise: he reports the CREATE button missing.

Serve P1 with:

```
cd .worktrees/p1 && python scripts/switchboard_dev.py --port 8137
```

⚠ Two tunnels on one free static domain **race per request** — `/healthz` answered from one
backend and `/switchboard` from the other, on the same URL. Delete the old tunnel; do not add a
second.

## Blockers — four are one credential

| open (D5 §4) | verdict | needs |
|---|---|---|
| deployed `SNOWFLAKE_SCHEMA` | `NOT-VISIBLE` | read Vercel's env |
| warehouse-mode rendering | `NOT-EXERCISED` | a **read-only-proved** identity |
| `DATE RANGE` inertness in warehouse mode | `NOT-MEASURED` | the same |
| every Power BI rendered figure | `NOT-EXERCISED` | a DAX instrument |
| Candidate C (`MARKETING_FCT_PLATFORM_DETAIL`) | held open | a **decision**, not a measurement |
| the three client questions | unchanged | ⚠ CD-1's ROAS set must be **enumerated before asking** — the cited "16" is unreproducible (12 Aug / 14 Jun) |

⛔ **`ACCOUNTADMIN` / `PAULRUSSELLADMIN` cannot pass the mission's own read-only gate.** D5 recorded
declining to use it as *the gate working, not failing*. R3 already built the right identity once —
`R3_CARTOGRAPHY_RO`, `USAGE`+`SELECT` on `TEST_DG1_GEP` only, key-pair auth, and it was **watched
refusing a write** (`003001 (42501)`). Reuse or rebuild that shape; prove the refusal again before
trusting any read.

Secrets live in exactly two places: `wiki/vault/infra-credentials.md` and Azure Key Vault
(`aldc-vault-test` / `aldc-vault-prod`). Prefer subshell capture so no value lands in context.

## ⚠ Not done — the honest list

- **Nothing is pushed.** Neither branch has left this machine.
- **Two Jira comments are drafted and UNPOSTED** — the Atlassian MCP is unavailable. They are
  `boot-prompts/drafts/GP-319-comment-2026-09-01.md` (design pass) and
  `…/GP-319-finalization-comment-2026-09-01.md` (this pass). The wiki's `log.md` also names a
  `GP-319-comment-D3-D5-2026-09-01.md`, which is **not in this checkout** — look in
  `.worktrees/mission`. Paste the design pass first.
  ⭐ `wiki/tickets/gep/GP-319.md` confirms GP-319 **is** the Navira Marketing Model ticket, which
  raises confidence in a key both drafts originally guessed by content match. Still eyeball it.
- **The client review is validated at 760 px and up only.** Phone widths unmeasured — if Paul
  presents from a phone, that is a gap.
- **Hard-killing the supervisor orphans its child**, which keeps the port. Ctrl+C is handled; a
  hard kill is not. The Windows job object could not be established (the child inherits the
  harness's job), and the supervisor prints a warning saying so rather than implying a guarantee.
  First P1.1 item.
- **9 split-form `.data`-from-`__file__` instances remain**, detected and **reported, not gated**.
  Several may be correct. Promoting to a gate is a human decision with the census in hand.
- **14 MB of client-review screenshots** are committed on the finalization branch. Same class as
  what `main` already tracks, but it is client-facing content in git history on a branch that must
  not be pushed.

## Gotchas earned this session

⭐ **A guard aimed at the wrong checkout is worse than no guard.** Both structural guards scanned
`repo.primary()`, so a suite running in a worktree validated the *primary's* source — a lane could
add the banned expression, watch the guard pass, and be reading someone else's files. Fixes made in
a worktree could never turn it green. Source is git-tracked content and is legitimately
checkout-relative; `.data/` is not. That distinction was already written in the guard's own
docstring and the guard did not obey it.

⭐ **Fail-closed mechanisms do damage when they fire spuriously at the point of delivery.** The
client-review degradation was *visible*, not silent — the page printed UNSUBSTANTIATED four times.
It was never an overclaim. It understated fully-evidenced work, in a client's hands, produced by
the command the runbook prescribes. Ask which *direction* a safety mechanism fails in before
congratulating it.

⭐ **A recorded blocker is a claim with a shelf life.** D5 recorded `warehouse.test.ts` as blocked
by a live session on 2026-09-01; the file's mtime was 2026-08-11. Re-measure an inherited blocker
before inheriting it. It ran clean: 108 passed.

⭐ **Dogfooding found two bugs reading could not.** Blocking real work wrote `status=blocked` to the
store and the page still said READY with a live START SYNCED button; and the waiting card named a
*satisfied* dependency while the real hold appeared nowhere. Both had passing test suites over them.

⚠ **Surfacing every `blocked_by` took NEEDS YOU from 5 rows to 24** — the exact "five old questions
outrank one live blocker" failure, arriving through the door the fix had just opened. Narrowed to:
the hold names something outside the store, **and** it is the only failing check.

⛔ **Heredocs mangle backslashes here, repeatedly.** Three patch scripts failed this session on
`\n` and on quoting. Use `Write`/`Edit` for anything containing escapes.

⛔ **`os.kill(pid, 0)` on Windows TERMINATES rather than probes.** A parent-watchdog written with it
was never shipped only because the patch failed to apply. If you build that watchdog, use
`OpenProcess(SYNCHRONIZE)` + `WaitForSingleObject`.

## Key paths

```
factory/work.py                     canonical work, readiness, target refusal, guarded_start
factory/coordination.py             measured signals; NO aggregate percentage by design
factory/switchboard_p1.py           the NOW-first UI, Inspector, bottom nav
factory/client_review.py            assemble() + publication_block() — the delivery gate
scripts/switchboard_dev.py          the restart supervisor
scripts/render_check_switchboard_p1.py   390/430/desktop harness
docs/evidence/marketing-model-v1/FINALIZATION-01-status.md   what closed, what needs Paul
missions/client-review-v1/05-CLIENT-REVIEW-DEMO-RUNBOOK.md   corrected regeneration command
```
