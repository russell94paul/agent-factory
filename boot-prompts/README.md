# Boot prompts — read this first, then read exactly one

Nine prompts accumulated here in about fifty hours (`ls boot-prompts/*.md | grep -v README | wc -l`). Each was correct when written; most describe a
plan that a later measurement retired. **A boot prompt carrying a retired plan is worse than none,
because it is confidently wrong and sits further from the reader's eye than the correction.**

So: this file is the router. It is the only file here that is maintained. Everything else is dated
and frozen at its moment.

**Measured 2026-08-31 05:40**, at `ec488bb` on `fix/fifth-verdict-apparatus-error`;
**prefect-connectors `main` at `0195e59`**. RUN-03 has landed — see below.

⚠ **Every count in this file is regenerable, and none of it is hand-maintained.** Two sessions
committed here within one hour and three numbers below rotted in that window — including
*"2 of 5 presets"*, written by one session and made false by the other adding a sixth. If you are
about to type a number here, put its command beside it or leave it out.

---

## ⭐ Read this one

### Two threads are live. Pick the one you are here for.

⚠ **Corrected 2026-08-31.** This heading read *"There is no CURRENT prompt"* — true when written,
false within the hour. A second session had a workstream open the whole time.

| thread | prompt | `next:` |
|---|---|---|
| **execution plane** (this section) | none — RUN-03 executed, nothing scoped to replace it | **write one before you start** |
| **workflow library / client delivery** | [`workflow-library-2026-08-31.md`](workflow-library-2026-08-31.md) | run `keel` on the GEP marketing model **as an instrumented experiment** — §3a's five setup steps come before any agent spawns |

They do not conflict: one owns *what the factory can execute*, the other owns *which workflow a
ticket routes to* and the client-facing delivery. ⛔ **Both sessions were committing to this repo at
once.** Run `git log --oneline -5` before assuming anything about HEAD — `presets.py` verifier states
moved mid-session for one of them.

**Write the next one before you start work, not after.** The honest state, measured:

| | |
|---|---|
| `factory/control.py` · `events.py` · `provider.py` | landed `31f3527`, 1,137 lines + 442 of tests |
| `factory/verifiers.py` | the verifier registry — `add-measure` → `pbi_contract` M1–M12, `model-redesign` → `redesign_contract` M+R |
| presets with a runnable verifier | **2 of 6** — `add-measure`, `model-redesign`. The other four name a check nobody has built, `model-design` among them. `python -c "from factory.presets import PRESETS; from factory import verifiers as v; print(len(v.REGISTRY), 'of', len(PRESETS))"` |
| the tracker | routed through the controller — `local_tracker.run_ticket`, POST `/run-ticket` |
| `.data/runs.jsonl` | 10 rows |
| findings ledger | **19 visible → 31** (`f8679b7`, then F87/F88) |

⛔ **Do not re-run RUN-03's plan.** `run-03-the-missing-middle-2026-08-30.md` is now a
**superseded** file kept for its reasoning; its `next:` is executed. Its §0 headline measurement
was already wrong when written (F84) and its `breadth` acceptance claim was already retired in its
own margin.

⭐ **What RUN-03 proved, and what came next.** It proved the vertical slice runs and that
`GreenContract` assigns the verdict. It produced no PASS, and should not have: no preset had a
verifier the controller could actually run — the one that *claimed* WIRED had nothing behind it
(**F87**), so the run contract's only assertion about the client's problem could not be satisfied
by any ticket type.

**That is now wired for one preset.** `factory/verifiers.py` joins `presets` to
`factory/pbi_contract.py` — 12 assertions, ~460 lines, complete and importer-less since the day it
was written — and `add-measure` reaches a real PASS, a real FAIL and UNMEASURABLE, each with a
mutation control. `RunController` resolves a verifier from the registry, so the CLI and the tracker
get one without being handed it, and the agent's prompt now states where to leave its evidence and
to **omit rather than invent** an observation.

**`model-redesign` is wired too**, and it needed its own contract rather than a second registry
row — two things measured first, either of which alone would have made reuse dishonest (**F89**).
A redesign is not additive, so `M4` refuses and the M-contract can *never* pass one. And evidence
carrying that preset's own named defect — a slicer that responds while every member returns the
grand total — scored **PASS=12** under M1–M12. `factory/redesign_contract.py` replaces M4 with R2
(renames carry enumerated, rewritten dependents) and adds R1/R3/R4, of which **R3 — no declared
axis is inert** is the one nothing else could make.

⚠ **I said last commit that `model-redesign` "needs that renderer wired". That was wrong**, and
worth correcting rather than quietly dropping: it needed a **slicing** harness, which is a
different instrument. A renderer answers *did the visual paint*; `interact` answers *did the
control respond*; only `slices` answers *did the numbers differ across the members*. The first two
were both green on the defect.

⚠ **Still open, and deliberately not papered over.** Three of five presets name a check nobody has
built — `ui-control` needs a Cosmos probe, `dimension-gap` and `wrong-number` need theirs. Neither
wired verifier can go green on model-layer evidence alone: M10/M11 are assertions XMLA and DAX
cannot make, and R3 needs per-member values, so a run without those harnesses is UNMEASURABLE **by
design**, not by neglect. **R3 is also only as wide as the agent's `must_slice_by` declaration** —
declaring no axes is UNMEASURABLE rather than PASS, but the contract cannot know which axes should
have been declared. Enumeration is the agent's obligation; the contract's job is refusing to pass
without it.

⚠ **Seven findings, every one from running or wiring the thing** — F83 (two defects, two
invocations), F85 (a plan-only run spending the attempt cap that stops a real one), F86 (the ledger
that could not show you any of them), F87 (the verifier that was never wired), F88 (the reload
button that never reloaded the verdict enum), F89 (the contract that certified the defect it was
pointed at). **Not one came from a gate.** That is the whole argument for what to do next: **wire
something, then run it.** It has not failed to pay yet.

⭐ F89 is the sharpest of them, and the one to read if you read one: the blind instrument was our
**newest and most careful** file, not an old thin one. Care is not coverage. Before reusing a
contract for a second ticket type, run that type's own named defect through it and watch it fail.

---

### `workflow-library-2026-08-31.md` — **CURRENT for the workflow/client-delivery thread**

`next:` **run `keel` on the GEP/Navira marketing model when Paul's artifacts land.**

Runs *alongside* RUN-03 rather than superseding it — different thread. Establishes that the estate
already had three disconnected workflow layers (`MEASURED`: zero cross-references from `factory/` to
the councils), keys the library on **shape × layer** with client as a context pack, and ships the
`design` shape as the new `keel` council plus `factory/registry.py` to join the two halves.

Carries three corrected premises worth more than the build: R19 already did the taxonomy (re-measured
exact), the Job object **exists** in `clients/GEP/tickets/*/artifact.yaml` rather than being missing,
and **Agent Army's founding premise was falsified by its own Wave 0** — stop investing there.

⚠ Also the record of a five-lens wiki council that **refuted its own commission**: do not sort the
wiki, write four pages and ship one instrument. And of three instruments that returned plausible
wrong numbers in one session.

---

## Closed 2026-08-30 06:10

### `branch-reconciliation-2026-08-30b.md` — **DONE, and one half went the other way**

- ✅ **`lane/control-plane-renamed` landed** — `6bd12f3`.
- ⛔ **`lane/certify` was DECLINED, not merged. Its branch and `.worktrees/certify` are deleted.**
  This README said *"do not delete that worktree or branch until this merges"*; that instruction is
  retired. Merging it would have **re-added the un-redacted `blueprints/windsorai_gep.yaml`** to a
  public repo, **reverted the corpus re-pin** from `485ad12` along with the `HISTORY IS LOAD-BEARING`
  warning (F82), and **downgraded `live_probes.py`** — main defines every function the lane did, plus
  `8dc4eac`'s `probes_for` fix. Its findings F30/F31 and its evidence file are already on main. The
  branch was stale, not pending. Full reasoning in the file's own banner.

**No `lane/*` branches remain in either repo** except `trial/wave0-rescue`, already merged and left
only because another session has it checked out.

---

## Superseded — kept for their reasoning, not their instructions

| file | why it is here | what retired it |
|---|---|---|
| `run-03-the-missing-middle-2026-08-30.md` | the pricing table, the three non-negotiable requirements, and the adopt-exactly-one-thing verdict on the Agent SDK — none of which is spent | **its `next:` is DONE** — landed `31f3527`, and the two defects that came out of running it are F83/F85 |
| `run-the-loop-2026-08-30.md` | the F77/F78 correction and the gate-ownership table are still the clearest statement of that finding | its `next:` (run one supervised lane) is now RUN-03's first step |
| `build-vs-adopt-2026-08-30.md` | **the adopt-vs-build decision record** — still load-bearing, and it falsifies `execution-plane`'s "adopt before you abstract" section | its `next:` only deferred to `run-the-loop` |
| `execution-plane-2026-08-30.md` | the provider-boundary reasoning, and why it comes *after* a real execution path | corrected twice: F78, then RUN-03 |
| `phase-0-event-ledger-2026-08-30.md` | the event-model design, especially the eligible-set argument | **subsumed by RUN-03** — you cannot record events for a run that never happens |
| `branch-reconciliation-2026-08-30.md` | reasoning behind the merge order | self-marked superseded by `…-30b` at 01:40 |
| `intake-platform-design-lock-2026-08-30.md` | the divergence pass it commissioned, which is done | superseded for sequencing by `run-the-loop` |

---

## The corrections that outlived every prompt above

If you read nothing else here, read these. Every one was expensive, and every one is the kind of
thing a fresh session re-derives wrongly. Regenerate the list with
`grep -l 'AFFECTS' docs/findings.d/F7*.md docs/findings.d/F8*.md`; do not maintain a count by hand.

- **`docs/findings.d/F77`** — RUN-01's acceptance criterion measures a different repository from
  RUN-01's work.
- **`docs/findings.d/F80`** — the board was measuring the wrong **branch**. The bounding controls
  existed the whole time on `lane/control-plane`; `CONNECTORS` pointed at a checkout that did not
  have them. Now merged, and `readiness.revision()` stamps every board with `branch@sha` so this
  cannot recur silently.
- **`docs/findings.d/F81`** — three probes that could not see (two with a single `_fail` return path
  since 2026-08-22, one case-sensitive grep), plus a fourth blind spot in the checker that catches
  them. All fixed; the probes now drive the controls.
- ⭐ **`docs/findings.d/F86`** — **the findings ledger could not see F77–F84.** Every correction in
  this list was invisible to `load()`, `by_lane()` and both of `test_findings.py`'s checks for a
  day, because the fragments were titled `#` where the parser requires `###`. Fixed at `f8679b7`,
  and a test now derives the population from `ls docs/findings.d/` rather than trusting the
  parser's own output. **If you write a finding, `### F<n> — title` or it does not exist.**
- **`docs/findings.d/F85`** — two `--dry-run` invocations spent the whole attempt cap and made a
  ticket unrunnable. The suite missed it because it reached the cap the same way.
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
- ⚠ **`python -m factory.launch` will still report the five bounding gates FAIL** until someone moves
  `repos/prefect-connectors` off `chore/artefact-homes` (29 dirty files, another session's) onto
  `main`. That is truthful about the revision it reads, and wrong about the estate. Point
  `$PREFECT_CONNECTORS` at a checkout on `main` and five of six pass. `readiness.revision()` prints
  which revision was measured — read it before quoting any gate.
- **Gate `ceiling` is the only real red, and must not be faked.** The engine's only budget symbol is
  `TERMINATION_BUDGET_SEC`, a *time* budget for the reap sweep. Cost is recorded only on
  `stage_completed`, so an accrued figure is blind to every failure — **fix the accounting before
  adding the comparison**, or the gate goes green over a ceiling that cannot hold.

## When you add a prompt here

Refresh the existing one for a workstream instead, and if you must add one: put its row in this
table, mark what it supersedes **in the superseded file itself**, and grep that file's body for the
claim you are retiring — editing only its `next:` line leaves the stale half reading as authoritative.
