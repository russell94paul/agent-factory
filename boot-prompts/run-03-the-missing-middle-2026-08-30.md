# Boot — RUN-03: make one TeamSpec actually execute

✅ **CURRENT as of 2026-08-30 05:25** — this is the live boot prompt; every other file in `boot-prompts/` is superseded or half-done. See `README.md` in this folder for the map, and `docs/findings.d/F77`/`F78` for the corrections that outlived every earlier prompt.

**Written:** 2026-08-30, 02:00. **This is the one that gets the factory running.**

Everything else open right now is tidying or infrastructure. This is the assembly line.

---

## `next:` **Wire ticket → preset → TeamSpec → one agent in a worktree → verdict → `.data/runs.jsonl`.**

**RUN-03 — "Execute a TeamSpec — the missing middle."** Already in the ledger, already carrying its
acceptance criterion and this session's pricing evidence. Do not re-scope it; execute it.

⛔ **Not the branch merges** (`branch-reconciliation-2026-08-30b.md`) — those are tidying and they
move no verdict. ⛔ **Not `factory/events.py` alone** (`phase-0-event-ledger-2026-08-30.md`) — you
cannot record events for a run that never happens. **RUN-03 subsumes Phase 0: build the runner and
have it emit the event record as it goes.** They are one vertical slice, not two tickets.

---

## 0. ⭐ Why this and nothing else — the measurement that decides it

> ⛔ **CORRECTED 2026-08-30 by `docs/findings.d/F84`. The table below is WRONG and the command
> under it is why.** That grep matches only `from factory.X import` / `from .X import`. Every
> factory module reaches its one production consumer as `from factory import X as Y` —
> `scripts/local_tracker.py`, line 46 onward — which neither alternative matches. It returned
> **0 for five modules holding 54 call sites between them.**
>
> **Actually unwired at `3e33a1a`: `presets.py` (309) + `deploy.py` (265) = 574 lines, not 2,041.**
> `dispatch`, `claims`, `runs`, `launch` and `worktrees` were all consumed by the tracker the whole
> time. Wrong by 3.5×.
>
> ⭐ **The conclusion survives and sharpens.** The two genuinely unwired modules are *exactly the
> two on the execution path* — choose a configuration, run an agent under it. Every module that
> was wired is a **reporting** surface. The estate had a complete reporting layer, no execution
> layer, and the reporting layer was reporting on work nothing here could start. That is a better
> statement of "the missing middle" than the inflated figure was: it makes the problem a shape
> rather than neglect.
>
> The rule this broke is already written in §5 of this same file — *"a code-search zero without a
> positive control is NOT-VISIBLE, not ABSENT"* — recorded four hours earlier against
> `gh api search/code`, and then repeated in a local grep. F84 carries the corrected table and the
> one-line positive control that catches it.

Measured 2026-08-30 02:00, consumers counted by import, excluding each module's own file and `demo`:

| module | lines | consumers |
|---|---|---|
| `factory/dispatch.py` | 441 | **0** |
| `factory/claims.py` | 390 | **0** |
| `factory/presets.py` | 309 | **0** |
| `factory/runs.py` | 289 | **0** |
| `factory/deploy.py` | 265 | **0** |
| `factory/launch.py` | 217 | **0** |
| `factory/worktrees.py` | 130 | **0** |
| `factory/blueprint.py` | 90 | 1 |
| `factory/contract.py` | 115 | 5 |

```bash
# regenerate:
for f in dispatch claims presets runs deploy launch worktrees blueprint contract; do
  printf "%-10s %4s ln  consumers: " $f $(wc -l < factory/$f.py)
  grep -rln "from factory.$f import\|from .$f import" --include=*.py factory/ scripts/ \
    | grep -v "factory/$f.py" | grep -v demo | wc -l
done
```

> ⭐ **Just over 2,000 lines of working, tested machinery that nothing calls.** The factory has a
> complete set of parts and no assembly line. That is the single fact that should decide what gets
> built next, and it is why RUN-03 is called *the missing middle* rather than a feature.

**This is also this estate's signature defect at its largest scale.** Five individual instances are
already filed — `blocked_by`, `RepoDeployer`, the tracker's `/finish` button, `EvalSuite`,
`live_probes` (F79) — and **every one was found by grepping for callers, never by a gate.** RUN-03 is
the systemic version. Wiring it retires most of the list at once.

**Precedent that it pays off immediately:** on 2026-08-29 `factory/live_probes.py` had no importer
but its own test. One line in `certify.py` — `Probes()` → `probes_for(target)` — turned A1 from
`UNMEASURABLE` into a real verdict **and exposed two genuine defects within seconds** (a wrong class
name that had stood since 2026-08-21, and a redaction that had silently unplugged the instrument).
Wiring existing code is the highest-yield work in this repo, by a distance.

---

## 1. What you are building

```
ticket id
   ↓  presets.by_id / for_layers          five presets exist, ONE has a WIRED verifier
TeamSpec { agents[], topology, contract, repo, prohibition }
   ↓  worktrees                            isolated checkout per lane
   ↓  claims                               atomic lane claim, Windows EACCES handled
   ↓  deploy.RepoDeployer.run_agent(spec, task, wt)
        AgentSpec { name role model effort prompt tools max_turns budget_usd prohibition }
   ↓  events                               ⭐ NEW — the only unreconstructable piece
   ↓  GreenContract                        assigns PASS / FAIL / UNMEASURABLE / NOT_RUN
   ↓  runs.jsonl                           durable record + MEASURED cost
```

**Everything above except `events` already exists and is tested.** You are writing the controller
that calls them in order, plus the event record.

### The three requirements that are not negotiable

1. **`RunStarted` carries the eligible set** — every configuration that passed the filter, which was
   chosen, and under what rule. R19: *the eligible set costs nothing to write and cannot be
   reconstructed afterwards.* Every other field can be backfilled. **This is the only
   time-sensitive thing in the whole ticket.**
2. **Every terminal event carries one of the four verdicts, and `GreenContract` assigns it** — never
   the agent, never the provider, never the UI. An event stream that cannot express `UNMEASURABLE`
   has collapsed the distinction this repo exists to protect.
3. **Fold the existing ledgers in or keep them apart with the reason recorded — do not create a
   third.** `.data/runs.jsonl` (`factory/runs.py`, **3 rows**) and `prefect-connectors/.sessions`
   (**14 runs**, read by `g_work_is_attributable`) count different populations and neither records a
   configuration.

### ⭐ Wire it to the path that actually runs

The live launch path today is **`scripts/local_tracker.py::_launch_script()`** → a generated `.ps1`
→ bare `claude`, with **no cap, no budget, no transcript parsing and no run record.**
`RepoDeployer.run_agent` (`factory/deploy.py:211`) already passes `--max-turns`, `--max-budget-usd`
and `--model` — and has **zero production callers.**

⛔ **A controller wired to `deploy.py` while the tracker still shells out to a `.ps1` produces an
empty event log and a green demo.** Route the tracker's launch through the controller, or accept
that you have built a second unwired thing. That is the whole lesson of the 2,041 lines above.

⚠ **The `.ps1` path is not a mistake to delete.** `launch.py`'s three-question model
(*May I RUN / LEAVE / TRUST*) says the supervised path is legitimate — a human wants to watch and
type. **The headless runner is a second path, not a replacement.**

### Adopt exactly one thing

**The Claude Agent SDK** (`claude-agent-sdk-python`, MIT, `v0.2.148` 2026-08-28, `windows-latest` CI,
5 runtime deps) — as **transport only**, below `GreenContract`, never as the thing that decides an
outcome. Its cost is *negative*: `deploy.py:230-234` already hard-codes `--max-turns`,
`--max-budget-usd`, `--output-format stream-json`, `--model` against an **undocumented, unversioned,
unpinned argv surface.** The SDK makes an existing invisible coupling typed and pinnable.

⛔ **Do not adopt an orchestration framework.** Retired on evidence in
`docs/reviews/build-vs-adopt-2026-08-29.md`: the six candidates cover **3 of 8** requirements —
worktree isolation, lane claiming, the retry ledger, the event ledger and the verdict model are
absent from all of them. AutoGen is in maintenance mode by its own README. CrewAI's core abstraction
*is* the topology R2 rejected on a 180-configuration study.

⚠ **Pin it exactly, and keep the seam.** `v0.2.148` is pre-1.0 with 148 patch releases. The SDK goes
behind our own ~15-line provider call, not an architecture. **`BVA-01` (a lockfile + a dependency
gate) should land first** — today `dependencies = ["pyyaml>=6.0"]` with no lockfile, no CI, and none
of the readiness gates measures a dependency.

⭐ **One cheap experiment worth running first, ~$1:** `deploy.py:98-110` records
`limit=UNDETERMINED` on every non-zero exit because *"the CLI gives us no documented signal
distinguishing a cap-kill from a crash."* The SDK's `ResultMessage` carries `stop_reason` and
`terminal_reason`. **One run past `max_budget_usd` settles whether adopting it converts a live
`UNDETERMINED` in our own code into a measurement.**

---

## 2. Pricing — measured, so scope does not drift

| Piece | Hand-rolled | With the SDK |
|---|---|---|
| `factory/events.py` — schema, append-only writer, fold | 120–160 | 120–160 |
| stream parser (`stream-json` → events) | 60–90 | **~10** |
| `factory/control.py` — the controller | 150–200 | 140–190 |
| provider seam + a fake for tests | 40–60 | 40–60 |
| cost attribution | 0 — reuse `runs.cost()` | 0, and live rather than scraped |
| **new non-test code** | **370–510** | **310–420** |
| tests | 200–300 | 200–300 |

**~400 lines, on top of 1,682 that already exist and are tested.** This is a session or two, not a
project. Anything much larger means scope drifted — stop and re-read this table.

---

## 3. Definition of done

A vertical slice: **task → controller → one agent → one worktree → recorded events including the
eligible set → result → evidence → `GreenContract` verdict → a row in `.data/runs.jsonl`.**

```bash
python -m factory.launch          # states its own basis; the baseline instrument
python -c "import json; print(sum(1 for _ in open('.data/runs.jsonl')))"   # was 3
```

⭐ **Prove substitution with a FAKE provider in a test, not by adding a second real one.** A fake the
controller drives identically is the evidence the boundary is real; a second real provider is scope.

⭐ **And ship the negative control**, because every gate here must demonstrate it can fail: a test
that the controller reports `UNMEASURABLE` — not `PASS`, not `FAIL` — when the agent produces no
usable result, **and that fails if that mapping is removed.** A `bash-guard.sh` in this estate exited
127 and blocked nothing for months while reporting success.

⛔ **A green run is not the goal. A run whose verdict is assigned by `GreenContract` from real
evidence is.** If the first slice reports `PASS`, check what measured it before believing it.

---

## 4. What NOT to do

- ⛔ **Do not merge `lane/certify` or `lane/control-plane-renamed` first.** Tidying. They move no
  verdict. `branch-reconciliation-2026-08-30b.md` when you want them.
- ⛔ **Do not build the UI.** `docs/FACTORY-UI-PROMPT.md` exists and its §0 kill condition says:
  *inspect first; if the event stream does not exist, stop and build it, never simulate.* **You are
  the session that builds it.** The UI gets its data from this ticket.
- ⛔ **Do not launch the `certify` lane from the tracker.** Its prompt is falsified — it asks for
  A1/A5 work that shipped in `6872aee` (F79). `lanes.py` is stale; `control-plane` and `judgement`
  both point at the *other* repo.
- ⛔ **Do not resurrect planner → implementer → tester.** `blueprints/orchestrator_team.yaml` opens
  `⛔ SUPERSEDED BY EVIDENCE` on a 180-configuration study. `TeamSpec.topology` defaults to
  `manager_to_agent`, *"the only one supported, deliberately."*

---

## 5. Rules of this checkout — all earned, all measured

- ⛔ **Never `git add` then `git commit`.** A concurrent session's `git add` landed **three of its
  files inside a commit of mine**, under my message, between my stage and my commit. Staging by path
  did not prevent it. Use `git commit -F <msg> -- <explicit paths>`. Recovery:
  `git reset --soft HEAD~1` (working tree untouched), `git restore --staged <theirs>`, re-commit.
- ⛔ **Merge in a temporary worktree; never check out `main` here.** Other sessions hold uncommitted
  work in the primary tree.
- ⛔ **`pytest -q` is not the baseline.** ~20 tests read the `prefect-connectors` checkout live; the
  count moved **388 → 409 inside one hour** with no change from the measuring session, and a full run
  takes **20+ minutes**. Use `factory.launch` / `factory.readiness` — they state their own basis.
  Quote no count without its command *and* the sibling `branch@sha`.
- ⛔ **`gh api search/code` is BLIND here** — returned **0** for a string verified to exist, with no
  error (a `gho_` token without code-search scope). **A code-search zero without a positive control
  is NOT-VISIBLE, not ABSENT.**
- ⚠ **`WebFetch` returns a small model's *summary*, even of raw source** — `DOCUMENTED`-tier. Use
  `curl` / `gh api` for anything carrying a verdict.
- ⚠ **`pin_corpus.py` deletes the manifest's comment history on every run** (F82). Unfixed.
- ⚠ **`tests/test_roadmap.py` hangs**, >200s, `rc=124`, pre-existing.
- ⚠ **Four of five bounding gates cannot move from this repo** — `cap`, `ceiling`, `concurrency`,
  `reaper` grep `prefect-connectors` (F77/F78/F80). **The movable verdicts are `certified`,
  `breadth`, `corpus`** — and RUN-03 is what finally moves `breadth` off *1 case, 0 strata*.

  > ⛔ **CORRECTED 2026-08-30. RUN-03 does not move `breadth`, and cannot.**
  > `readiness.g_corpus_has_breadth` reads **`evals/corpus/`** — pinned eval cases and their
  > declared strata — and passes only at `len(pinned) >= 29 and len(strata) >= 15`. It never looks
  > at `.data/runs.jsonl` or at anything a run produces. Executing a thousand TeamSpecs leaves it
  > at *1 case, 0 strata*. **Measured:** RUN-03 shipped and landed two runs; the board is
  > byte-identical before and after except the ledger row count. Moving `breadth` means writing
  > corpus cases, which is a different ticket. Same shape as F77 — an acceptance criterion
  > pointed at something the work cannot reach.
- ⚠ **`F83` is the next free finding id.** Ids have collided across branches twice.
- **Ask before any secret.** No session has ever requested one.

---

## 6. State, measured 2026-08-30 02:00

```
main                      02ffa23   local == personal/main   ✅
feat/readiness-generator  b4bac0d   fully merged into main
.data/runs.jsonl          3 rows
.data/tasks.jsonl         76 tickets — 53 open, 18 blocked, 2 done
certify (live)            A1 PASS · A5 FAIL · 10 UNMEASURABLE · aggregate FAIL · exit 1
```

main was a **one-commit skeleton from 2026-08-20** until 00:30 on 2026-08-30. It now carries the
build-vs-adopt decision, the first live instrument wired into the certification path, A1 passing
against reality, and findings F77–F82.

**Still unmerged:** `lane/certify` (4 commits, 7 conflicts, all decided) and
`lane/control-plane-renamed` (31, 4 conflicts — got harder when `508cfc3` landed).

---

## 7. Where things live

| Path | What |
|---|---|
| `factory/presets.py` (309) | 5 presets, **one** with a `WIRED` verifier. `by_id`, `for_layers`, `unwired`. **Nothing consumes it — this is the input side of RUN-03** |
| `factory/blueprint.py:19,43` | `AgentSpec` (name role model effort prompt tools max_turns budget_usd prohibition) · `TeamSpec` (agents topology contract repo prohibition) |
| `factory/deploy.py:188,211` | `RepoDeployer.run_agent(spec, task, wt)`. 140 of its 265 lines are `AttemptLedger` — a cap that survives restart, which no framework replaces |
| `factory/worktrees.py` (130) | Isolation per lane. Windows junction guard, primary-worktree resolution |
| `factory/claims.py:200-247` | Atomic claim. Windows `EACCES`-vs-`EEXIST` handled. ⭐ `BVA-02`: this should be `tox-dev/filelock` |
| `factory/contract.py` (115) | The four verdicts. `FAIL > UNMEASURABLE > PASS`. Any instrument exception → `UNMEASURABLE` |
| `factory/runs.py` (289) | The ledger + `cost()` scraping `~/.claude/projects/*.jsonl`, basis `MEASURED` vs `NOT-RECORDED` |
| `scripts/local_tracker.py::_launch_script` | **The path that actually runs today.** Wire here or the log stays empty |
| `docs/research/answers/R19-*.md` §5 | The dispatch record and the eligible-set claim |
| `docs/reviews/build-vs-adopt-2026-08-29.md` | Why build not adopt; the SDK-as-transport verdict |
| `boot-prompts/branch-reconciliation-2026-08-30b.md` | The merges, when you want them |
