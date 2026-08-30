# Boot — Phase 0: the event ledger, and the wiring change that comes first

**Written:** 2026-08-29, late. **For:** the session that builds `factory/events.py`.
**Companions:** `build-vs-adopt-2026-08-30.md` (the decision record), `run-the-loop-2026-08-30.md`
(the live `next:` for the wider board), `docs/FACTORY-UI-PROMPT.md` (what Phase 0 eventually feeds).

---

## `next:` **Construct `WindsorAiGepProbes` in `certify.py`'s live path. It is a wiring change, not a lane.**

⛔ **Do NOT launch the `certify` lane from the tracker.** Its prompt is falsified — see
`docs/findings.d/F79-the-real-instrument-exists-and-nothing-calls-it.md`. It instructs an agent to
build A1/A5 probes that shipped on 2026-08-29 in `6872aee`, and to "prove" reachability that was
already proven. A session launched on it rebuilds `factory/live_probes.py`.

**The measured situation.** `WindsorAiGepProbes` works today, with no credential:

```
config      -> OK  constructed ['WindsorAIConnection', 'WindsorAIOptions']      (A1)
suite       -> OK  {'passed': 825, 'failed': 1, 'revision': '8b7c68d5...'}      (A5)
credential  -> Unmeasurable: no instrument configured for credential
run         -> Unmeasurable: no instrument configured for flow run
landed      -> Unmeasurable: no instrument configured for landed rows
```

And `factory/certify.py` never constructs it — `certify.py:29,102,105` instantiate only `CtxProbes`
(a recorded world) and `Probes` (refuses everything). The only importer of `live_probes` in the whole
repo is `tests/test_live_probes.py`.

**Do this first because it is small, reversible, needs no vault approval, and is the cheapest
verdict move available.** ⚠ **Predict the result before you run it** — that is the house rule and
this is exactly the case it exists for. My prediction, recorded so it can be wrong:

> A1 and A5 move off `NOT_RUN` to real verdicts. **The aggregate `certified` verdict does NOT move
> to PASS**, because A2/A3/A4/A6–A12 remain uninstrumented and `ContractResult.verdict` returns
> `UNMEASURABLE` when any required assertion is unmeasurable. **`UNMEASURABLE` is the correct and
> desirable outcome here.** If the aggregate reports `PASS`, something is rounding up and that is a
> defect, not a success.

⛔ **`UNMEASURABLE` must never become `PASS` just because a probe now exists but cannot reach its
instrument.** That sentence is in the lane prompt and is the one part of it still true.

---

## Then: Phase 0 — the append-only event ledger

**Build `factory/events.py`. No UI.**

**Why this and not the UI:** the append-only event record is *the only piece that cannot be
reconstructed later*. Providers can be abstracted whenever a second provider appears; a run that
executed without recording what it did is gone. R19's load-bearing claim: **the eligible set — every
configuration that passed the filter and was *not* chosen — costs nothing to write and cannot be
recovered afterwards.** Everything else can be backfilled.

### Schema

```
event_id · ts · mission_id · team_id · agent_id · parent_agent_id · lane_id
event_type · status · tool_id · resource_id · artifact_id
duration_ms · tokens_in · tokens_out · cost_usd · basis · metadata
```

### Three requirements that are not negotiable

1. **`RunStarted` carries the eligible set** — every configuration that passed the filter, which was
   chosen, and under what rule. Backfill everything else; never this.
2. **Every terminal event carries one of `PASS / FAIL / UNMEASURABLE / NOT_RUN`, and `GreenContract`
   assigns it** — never the agent, never the provider, never the UI. An event stream that cannot
   express UNMEASURABLE has collapsed the distinction this repo exists to protect.
3. **Fold the two existing ledgers in, or keep them apart with the reason recorded. Do not make a
   third.** `.data/runs.jsonl` (`factory/runs.py`, **3 rows**) and `prefect-connectors/.sessions`
   (**14 runs**, read by `g_work_is_attributable`) count different populations and neither records a
   configuration.

### ⭐ Wire the emitter to the path that actually runs

That is **`scripts/local_tracker.py::_launch_script()`** → a generated `.ps1` → bare `claude`.
It is **not** `deploy.py`. `RepoDeployer` has zero production callers (`tests/test_retry_context.py`
is its only importer), so an emitter wired there produces an empty log and a green demo — the exact
failure this whole line of work exists to prevent.

⚠ **This is the fifth instance of the estate's signature defect** — written and unwired
(`blocked_by`, `RepoDeployer`, the tracker's `/finish` button, `EvalSuite`, now `live_probes`).
Every one was found by grepping for callers; **none was found by a gate.** Before you finish,
consider adding the gate nobody has: *does anything import this?*

### Definition of done

A real supervised lane run produces a real event log, containing the eligible set, with terminal
events carrying a four-verdict value assigned by `GreenContract`. **Ship this even if no UI follows.**

---

## What NOT to build

⛔ **No UI in this session.** `docs/FACTORY-UI-PROMPT.md` exists and is committed, but its §0 kill
condition says: *inspect first; if the event stream does not exist, stop and build it, never
simulate.* You are the session that builds it. The UI's Phase 0 and this are the same work.

⛔ **No simulated events**, not even to develop against, until a real run has produced a real log.
A convincing mock is indistinguishable from working telemetry and this repo exists to make that
distinction impossible to fudge.

⚠ **Collision:** `docs/design/session-ui-and-intake.html` ("Control Room & Intake", 35 KB) was
written by a concurrent session on 2026-08-29, and Paul is testing `FACTORY-UI-PROMPT.md` against
Claude Design. **Any UI output from either is a draft to assess, not a decision taken.**

---

## State, measured 2026-08-29 late

```
$ python -m factory.launch
  UNATTENDED-BLOCKED   cap · reaper · ceiling · concurrency · bounded   all FAIL
  OUTPUT-UNCERTIFIED   suite FAIL 21 failed, 409 passed, 2 xfailed
                       certified NOT_RUN — 12 assertions have no instrument wired
                       corpus FAIL · version FAIL · breadth FAIL 1 case(s), 0 strata
```

⚠ **Four of the five bounding gates cannot be moved from this repo** — `cap`, `ceiling`,
`concurrency`, `reaper` all grep `prefect-connectors` (F77, F78). Their staying red says nothing
about work done here. **The movable verdicts from this repo are `certified`, `breadth` and
`corpus`** — which is why `next:` is what it is.

⚠ **The 21 test failures are the sibling checkout, not a regression.** `prefect-connectors` is on
`chore/artefact-homes`, 29 dirty files, `tests/orchestrator/mutate_control_plane.py` **absent**.
Re-measure with the condition recorded; never quote a suite number without it. It moved 388 → 409
inside one hour on 2026-08-29 while a concurrent session added tests.

**Ledger:** `.data/tasks.jsonl` — 185 events, 76 tickets, **53 open, 18 blocked, 2 done**.

---

## ⚠ The lane board is stale — do not trust "5 can start now"

Measured 2026-08-29 from `factory/lanes.py`:

| Lane | Reality |
|---|---|
| `control-plane` | `touches=orchestrator/pipelines.py` — **prefect-connectors**, and its gates are the four F78 proved unmovable from here |
| `judgement` | same file, same other repo |
| `certify` | **premise falsified** — F79 |
| `grain` | held back on an unanswered blocker |
| `artifact` | real, and the smallest item on the board |

`lanes.py` is a hand-maintained allow-list that drifted from the code it describes — the **fourth**
such list in this repo to under-cover silently (`TeamSpec.version`, `synthesis.session_prompt`,
`local_tracker._HOT`, now `lanes.LANES`). **If a list can be derived from the thing it tracks, derive
it**, and pair it with a test that fails when an entry goes stale — not one that asserts the list's
contents.

---

## Gotchas earned

- ⛔ **`gh api search/code` / `gh search code` are BLIND here** — they returned **0** for a string
  verified to exist, with no error (a `gho_` OAuth token without code-search scope). **A code-search
  zero without a positive control is NOT-VISIBLE, not ABSENT.** Use
  `gh api repos/OWNER/REPO/contents/PATH` (proven working) or fetch raw files.
- ⚠ **`WebFetch` returns a small model's *summary*, even of raw source** — `DOCUMENTED`-tier, not
  `OBSERVED`. Use `curl` / `gh api` for any claim that will carry a verdict.
- ⛔ **`git add` then `git commit` is NOT safe in this checkout.** A concurrent session's `git add`
  between your stage and your commit put three of its files into a commit of mine on 2026-08-29,
  under my message. **Use `git commit -F msg -- <explicit paths>`** — it bypasses the index and
  commits only those paths. Recovery that time was `git reset --soft HEAD~1`, working tree untouched.
- **Never quote a count without the command that produced it.** `docs/BUILD-VS-ADOPT-PROMPT.md`'s
  four size figures were stale the day they were written, and "304 tests" is three different numbers.
- **Ask before any secret.** No session has ever requested one; name the exact secret and source and
  get an explicit yes.

---

## Where things live

| Path | What |
|---|---|
| `factory/live_probes.py` | `WindsorAiGepProbes` — the real A1/A5 instrument. **Works. Uncalled.** |
| `factory/certify.py` | `:29,102,105` — instantiates `CtxProbes`/`Probes`, never the live one. **The wiring site.** |
| `factory/connector_contract.py` (311 ln) | A1–A12. A7–A10 bodies are `:189-264` = 76 lines |
| `factory/contract.py` (115 ln) | The four verdicts; `FAIL > UNMEASURABLE > PASS`; any instrument exception → UNMEASURABLE |
| `scripts/local_tracker.py` (2,575 ln) | The live launch path, and the only UI. `_launch_script()` is where the emitter goes |
| `factory/runs.py` / `.data/runs.jsonl` | 3 rows; `cost()` scrapes `~/.claude/projects/*.jsonl` |
| `docs/findings.d/F77, F78, F79` | Which repo each gate reads; and the unwired instrument |
| `docs/reviews/build-vs-adopt-2026-08-29.md` | Why we build rather than adopt, and what UNMEASURABLE actually needs to survive |
| `docs/FACTORY-UI-PROMPT.md` | What Phase 0 eventually feeds. Not this session's job |
