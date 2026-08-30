# Boot prompts — read this first, then read exactly one

Eight prompts accumulated here in about thirty hours. Each was correct when written; most describe a
plan that a later measurement retired. **A boot prompt carrying a retired plan is worse than none,
because it is confidently wrong and sits further from the reader's eye than the correction.**

So: this file is the router. It is the only file here that is maintained. Everything else is dated
and frozen at its moment.

**Measured 2026-08-30 05:25.** `main` at `6bd12f3`.

---

## ⭐ Read this one

### `run-03-the-missing-middle-2026-08-30.md` — **CURRENT**

`next:` **wire ticket → preset → TeamSpec → one agent in a worktree → verdict → `.data/runs.jsonl`.**

Argues from a consumer count: `dispatch.py` (441 lines), `claims.py` (390), `presets.py` (309),
`runs.py` (289) — **2,041 lines, zero consumers.** It explicitly subsumes `phase-0-event-ledger`
(build the runner and have it emit the event record as it goes — one vertical slice, not two
tickets) and explicitly rules out the branch merges as tidying that moves no verdict.

---

## Still live, but narrower than it says

### `branch-reconciliation-2026-08-30b.md` — **HALF DONE**

Scope was two merges into `main`: `lane/control-plane-renamed` (31 commits) and `lane/certify` (4).

- ✅ **`lane/control-plane-renamed` landed** — `6bd12f3`, 2026-08-30 05:22.
- ❌ **`lane/certify` is still out** — 4 commits, oldest 2026-08-22, including *"fix six real defects
  an opus review found in the probe."* Its worktree is at `.worktrees/certify`. **Do not delete that
  worktree or branch until this merges.**

Read it only for the `lane/certify` half. Its `lane/control-plane-renamed` figures are spent.

---

## Superseded — kept for their reasoning, not their instructions

| file | why it is here | what retired it |
|---|---|---|
| `run-the-loop-2026-08-30.md` | the F77/F78 correction and the gate-ownership table are still the clearest statement of that finding | its `next:` (run one supervised lane) is now RUN-03's first step |
| `build-vs-adopt-2026-08-30.md` | **the adopt-vs-build decision record** — still load-bearing, and it falsifies `execution-plane`'s "adopt before you abstract" section | its `next:` only deferred to `run-the-loop` |
| `execution-plane-2026-08-30.md` | the provider-boundary reasoning, and why it comes *after* a real execution path | corrected twice: F78, then RUN-03 |
| `phase-0-event-ledger-2026-08-30.md` | the event-model design, especially the eligible-set argument | **subsumed by RUN-03** — you cannot record events for a run that never happens |
| `branch-reconciliation-2026-08-30.md` | reasoning behind the merge order | self-marked superseded by `…-30b` at 01:40 |
| `intake-platform-design-lock-2026-08-30.md` | the divergence pass it commissioned, which is done | superseded for sequencing by `run-the-loop` |

---

## The corrections that outlived every prompt above

If you read nothing else here, read these two findings. Both were expensive and both are the kind of
thing a fresh session re-derives wrongly:

- **`docs/findings.d/F77`** — RUN-01's acceptance criterion measures a different repository from
  RUN-01's work.
- **`docs/findings.d/F78`** — it is four gates, not one. `cap`, `ceiling`, `concurrency` and `reaper`
  all grep `prefect-connectors`, so **no agent-factory work moves them**; and all five
  `OUTPUT-UNCERTIFIED` gates are local, so that is the verdict this repo can actually move.

## Gotchas that cost real time

- **`python -m factory.launch` takes ~9 minutes and prints nothing until it finishes.** Use
  `python -u`. It is not hung; one of its gates runs the whole pytest suite.
- **Never use `pytest -q` as a baseline.** ~20 tests read the `prefect-connectors` checkout live;
  the failure count moved 8 → 21 in one session with no code change here.
- **The git index is shared between concurrent sessions.** Staging by path does *not* protect you —
  another session's `git commit` takes whatever you have staged. Proven 2026-08-29 21:00.
- **`main` may be checked out in another session's worktree.** `git worktree list` before assuming.

## When you add a prompt here

Refresh the existing one for a workstream instead, and if you must add one: put its row in this
table, mark what it supersedes **in the superseded file itself**, and grep that file's body for the
claim you are retiring — editing only its `next:` line leaves the stale half reading as authoritative.
