### F98 — the DAG field was surveyed as "exists and is unused", and now carries 25 block edges holding the mission's critical path

Filed 2026-09-01. The superseded statement was **true when it was written**; this file exists so
the retirement is recorded rather than the history rewritten.

## The claim and its retirement

`docs/specs/client-review-loop-v0.md:36`, in the capability-leads table:

> ⚠ ticket-level `blocked_by` is `[]` in all 189 events — the DAG field exists and is unused

At the time of that survey the store held 189 events and every one carried an empty `blocked_by`.
The observation was correct. What it could not see is that the field was **unused, not unusable** —
and the very next piece of work used it.

```bash
python -c "
import json
ev=[json.loads(l) for l in open('.data/tasks.jsonl',encoding='utf-8') if l.strip()]
print('total events', len(ev)); print('block events', sum(1 for e in ev if e['kind']=='block'))"
total events 217
block events 25
```

The 25 edges were written by `marketing-model-reconstruction-v1`
(`scripts/mission_marketing_model.py`), which uses `create(parent=…)` + `block()` as the house
pattern rather than adding a `depends_on` field. They currently hold the live shape

```
R1 2b9aae3b ─┐
R2 3d053975 ─┼─▶ D1 1785f5a9 ─▶ D2 933e6c33 ─▶ D3 387780b5 ─▶ D4 b1f38c1c ─▶ D5 91088e54
R3 e397be46 ─┘
```

— which is to say the field the spec called unused is the only thing currently expressing the
mission's critical path.

⭐ **A survey of an empty field measures adoption, not capability**, and the two decay on different
clocks. The row was 28 events away from being wrong on the day it was written, and nothing in its
phrasing carried an expiry.

## Remediation status — already applied elsewhere, deliberately not duplicated here

Session 2 (Rapid Reliability) has **already corrected line 36** in its worktree at
`.worktrees/reliability/docs/specs/client-review-loop-v0.md`, uncommitted, marking the row
`CORRECTED 2026-08-31` with the superseded text preserved and a regeneration command attached.
This session did **not** edit the copy on `main`: the same line is in flight on another branch and
a second edit would manufacture a merge conflict over an identical fix. The correction reaches
`main` when Session 2's branch does.

- **BELIEVED** — ticket-level `blocked_by` is dead weight; a DAG primitive would have to be built
  from scratch, because the existing field is populated nowhere.

- **ACTUALLY** — `blocked_by` is live and load-bearing. 25 `block` events express the eight-task
  mission DAG, and `D1` is `blocked` on exactly `['2b9aae3b','3d053975','e397be46']` right now.
  The original survey was accurate at 189 events and false by 217.

- **MEASURED BY** — the regeneration command above (217 total / 25 block), plus a direct read of
  the blocked task:
  ```bash
  python -c "
  from factory.tasks import TaskStore; from factory import repo
  print(TaskStore(repo.data()/'tasks.jsonl').get('1785f5a9').blocked_by)"
  ['2b9aae3b', '3d053975', 'e397be46']
  ```

- **AFFECTS** — **every lane**, through the general form rather than the specific one: every lane
  writes surveys of the codebase into specs, and a count typed from a survey has no expiry stamped
  on it. The rule this instantiates is the repo's own — *a count in a document carries the command
  that regenerates it, or it is not written* — and none of the counts in that leads table did.
  Specifically: `docs/specs/client-review-loop-v0.md:36` (corrected on Session 2's branch, not yet
  on `main`), and any design that proposed building a DAG primitive on the premise that none
  exists.

- **KIND** — CORRECTION

- **STATUS** — SUPERSEDED
