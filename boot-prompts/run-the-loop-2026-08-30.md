# Boot — bound the loop, then run a ticket through it

**Written:** 2026-08-29, late. **For:** the next session.
**Supersedes** `intake-platform-design-lock-2026-08-30.md` for sequencing. That brief's job — the
divergence pass — is **done**; read its outputs, do not re-run it.

`next:` **RUN-01.** Wire `deploy.py`'s spend ceiling into the path the launcher actually takes.
Done when `python -m factory.launch` stops reporting gate `ceiling` as FAIL.

---

## Stop designing. The instrument already chose the direction.

Run this first, before reading anything else:

```bash
python -m factory.launch
```

Measured 2026-08-29:

```
May I RUN an agent, with me watching?     SUPERVISED-OK
May I LEAVE it running, unattended?       UNATTENDED-BLOCKED
    cap FAIL · reaper FAIL · ceiling FAIL · concurrency FAIL · bounded FAIL
May I TRUST what it produced?             OUTPUT-UNCERTIFIED
    certified NOT_RUN · corpus FAIL · version FAIL · breadth FAIL
```

`launch.py` also states what the current position costs, in its own words:

> *"You are the cap, the reaper and the spend ceiling."*

**That is the whole brief.** Four tickets buy those three back, and each one is done when a verdict
moves — not when someone decides it is.

| | | done when |
|---|---|---|
| **RUN-01** | spend ceiling before dispatch | gate `ceiling` not FAIL |
| **RUN-02** | turn cap + reaper **on the path that runs** | gates `cap` AND `reaper` not FAIL |
| **RUN-03** | execute a TeamSpec | one preset runs one real ticket, ledger row appended, still SUPERVISED-OK |
| **RUN-04** | ticket → team entry point, then the UI button | one command takes a ticket id and produces a claimed lane running the matched preset |

**RUN-01 and RUN-02 are SYNTHESIS §5 steps 1–2**, which R3 calls non-negotiable. RUN-03 comes after
because an executor built before its bounds is an unbounded executor — the thing that
*"staged a fresh budget and re-dispatched all night"*. RUN-04's button is last because until RUN-03
exists it has nothing to call.

⭐ **RUN-01 is a WIRE ticket, not a build ticket.** `deploy.py` already implements the ceiling and
the `AttemptLedger`. `RepoDeployer` has **zero callers**. And read RUN-02's gate text closely —
*"a cap exists on a path that did not run"* — that sentence is the finding.

---

## What is already true — do not rediscover it

- **The configurator exists and is good.** `python -m factory.presets` — five baseline presets
  grounded in real tickets, each with model, effort, turn and dollar caps, an escalation trigger and
  an explicit refusal. It decides which team a ticket type gets. **Nothing consumes that decision.**
- **The certifier exists.** A1–A12 pass; `certify` labels its own basis (`REPLAYED`, not measured).
- **Nothing executes a `TeamSpec`** — `git grep "TeamSpec\|load_team"` outside `blueprint.py`
  returns nothing. SYNTHESIS §11.5 found this independently.
- **304 tests green.** 39 modules, 26 test files, 24 research answers, 71 tickets, **1** corpus run.
- **Five lanes are launchable today** (`control-plane`, `certify`, `judgement`, `artifact`, `grain`)
  via `local_tracker.launch(lane_id)` — one agent, one prompt, one worktree, claimed atomically.
  A lane is not a team; that is the gap RUN-03 closes.

## Read these — they were produced by a parallel session and are not to be redone

- `docs/reviews/divergence-2026-08-29.md` — 22 claims: **13 CONFIRMED · 5 our doc stale · 2 reviewer
  stale · 2 basis defect**
- `docs/reviews/ticket-repo-crossref-2026-08-29.md` — **9 of 33 tickets are wrong about the repo**
  (base rate 13% → 27%)
- `docs/reviews/external/verification.md` — what survived checking the external pass

⚠ **Three of their findings correct earlier work. Two are still open:**

| | |
|---|---|
| **D-2** | D5 was reported missing; it exists at `deepseek.md:528-541`. **Fixed.** The cause was a case-sensitive grep — a zero from an instrument nobody proved could see. **Five of D5's seven rows are still unticketed.** |
| **D-4** | The 70–80% vs 30–40% questionnaire figure is **verbatim accurate but basis-absent** — an unsourced projection from a food-waste ontology feasibility study, in a different domain. **OPEN.** Apply `control-room.md` §8's basis register, including its *"how it dies"* column. |
| **D-1** | The dependency graph is **authored, not derived** — the store's own `blocked_by` field is dead and the edges were hand-written in `ticket-detail.json`. **OPEN.** |

**D-4 matters because the intake-platform critical path was built on that number.** If it does not
survive its basis label, that path is not the priority the earlier brief said it was — which is part
of why this brief leads with RUN-01 instead.

---

## Working rules

- **Grep before proposing.** `9 of 33` tickets were wrong about the repo, two proposed things
  already built. If the symbol exists, the ticket is `wire` or `retire`, never `build`. Cite the grep.
- **Every gate ships with a negative control** — it must block bad input *and* let good work through.
- **Numbers carry their command.** `scripts/export_board.py`, `workflow-kit/measure.py`,
  `python -m pytest -q`. Do not type a count you did not just measure.
- **The board is generated.** Edit `docs/board/template.html` or `ticket-detail.json`, then
  `export_board.py && build_board_artifact.py`. **Never edit `docs/board/index.html`.**
- **Republish to the same artifact URL** — https://claude.ai/code/artifact/11564c9c-0aa2-4369-9911-2e2ad82cfbaf
  A new one loses Paul's saved ticket states.
- **Stage by path, never `git add -A`.** Sessions run concurrently in this repo; on 2026-08-29 two
  edited the same two files and both survived by luck. Check `git status` and commit only your own.
- **Ask before committing.** Paul approves commits.

## Surfaces

| | |
|---|---|
| `python scripts/local_tracker.py --serve --port 8099` | lands on **Tickets**; `/gates` is the readiness verdict |
| board artifact `11564c9c` | 68 tickets, THE PATH lane first |
| showcase artifact `f95b50b4` | what this project is, for showing people |

## Status — honest

- ✅ 15 commits pushed on `feat/readiness-generator`; 304 tests green; working tree clean of my work.
- ✅ RUN-01…04 exist, each with a `launch.py` gate as acceptance.
- ❌ **No ticket has been started.** 5 of 71 closed, and those five predate today.
- ❌ D-1 and D-4 are open; five D5 rows unticketed.
- ❌ `main` is 157+ commits behind; nothing merged.
- ❌ Git history still carries client names (working tree is redacted).
- ❌ The corpus holds **one** recorded run — sensitivity is proved, breadth is not.
