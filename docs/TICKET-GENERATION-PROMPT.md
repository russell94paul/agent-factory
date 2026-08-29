# Ticket-generation prompt — corrected 2026-08-29

Run in a Claude Code session with cwd `C:\Users\PaulRussell\repos\agent-factory`.

**What changed from the draft, and why.** Four corrections, each verified against the repo:

1. The draft said *"the build order is fixed by SYNTHESIS.md §5"* and then gave a P0–P8 list that
   **appears nowhere in `SYNTHESIS.md` or the external review**. §5 exists at line 196 and states a
   *different* nine-step order. The list is authored; it is now labelled as such, and reconciling
   the two is task zero.
2. The draft said CIP-21…CIP-35 exist. **Thirteen do.** CIP-22 and CIP-33 were rejected as
   already-implemented.
3. The draft said AB-05 was already rejected. **The review marks it `DO`.**
4. Nothing stopped the model proposing already-built work — which is how CIP-22 and CIP-33 got
   through. A grep-first rule is now mandatory.

---

## The prompt

Copy everything below the line.

---

You are a principal engineer turning a completed research programme into executable tickets. The
research is done. **Do not open a new research question.** If you believe one is unavoidable, you
may only propose it, and the proposal must name which existing answer failed to cover it, by file
and section.

### Read first

```
docs/research/SYNTHESIS.md            the decision record — 17 passes reconciled, 2,422 lines
docs/absorption-backlog.md            AB-01..AB-19, concluded and never actioned
docs/specs/architecture-v0.md         the strawman architecture
docs/specs/control-room.md            the UI spec with slices
docs/reviews/external/verification.md what survived checking the external pass — READ THIS
docs/board/tickets.json               the 33 tickets that already exist
factory/                              39 modules, the GreenContract, the board
```

### ⛔ Task zero — reconcile the build order before writing any ticket

Two orderings are in play and **they disagree**.

**A · `SYNTHESIS.md` §5 (line 196) — the decision record:**

```
1  hard external attempt / spend / concurrency budget      ← non-negotiable
2  cloud timeout + cancellation + orphan reaping + restart reconciliation
3  terminal verdict computed from append-only history, not current state
4  refusal-capable gates, with negative drills
5  tenant capability isolation at every persistence/promotion boundary
6  complete attempt/cost telemetry, including failures
7  external evaluator trust boundary (a service, not a directory)
8  expand and freeze the evaluation corpus
9  ── only here ── configuration experiments
```

§5: steps 1–4 non-negotiable per R3; 5–7 must precede optimisation *"because otherwise the
optimisation score itself is not safe to trust."*
§11.5: *"R7's build order does not supersede §5… §5 stands unchanged. R7 slots in after it."*

**B · A proposed order, AUTHORED 2026-08-29 — not from any document in this repo:**

```
P0 Decouple from aldc-launchpad          P5 Snowflake grant envelope (WHERE FALSE probe first)
P1 Fix instrument failures               P6 Run supervised migration
P2 Fix finish button                     P7 Application layers (Decision, Snapshot, UI)
P3 Budget on live launch path            P8 Optimisation — deferred until corpus breadth ≥ 29
P4 Atomic claims
```

**They conflict substantively.** §5 makes the hard budget step 1 and calls it non-negotiable; B
demotes it to P3. §5 never mentions decoupling; B makes it P0.

**Your first output is the reconciliation:** which order governs, with the reason, and what changes
in B if §5 governs. Do not write tickets against B until you have done this. If you conclude B
governs, you are overturning a decision record — say so explicitly and justify it.

### The two ticket tracks — do not merge them

`CIP-` and the phase labels are already overloaded. Keep these separate:

| Track | Prefix | Phases | Scope |
|---|---|---|---|
| Client Intake Platform | `CIP-01..20` | P0–P5 | questionnaire → contract → portal → learning loop |
| agent-factory hardening | **`AF-`** | **F0–F8** | the build order above; making the factory itself trustworthy |

**CIP-21…CIP-35 are mis-prefixed** — they are factory hardening, not intake platform, and they
currently sit under P0–P5 labels meaning something different from CIP-01…20's. Your ticket set
should (a) start new work at **`AF-01`**, and (b) include a `retire` ticket to rename CIP-21…35 to
the `AF-` track. They are hours old; the rename is cheap now and expensive later.

**Already rejected — do not recreate:** CIP-22 (*make `claim()` atomic* — already done,
`claims.py:219` and `:252`) and CIP-33 (*add ABANDONED* — already declared, `runs.py:41`,
`tasks.py:20-21`). See `verification.md`.

### Measure before you write

You have a filesystem; the previous external pass did not. Run these and **report what they
actually say** before any ticket:

```bash
python -m pytest -q
python -m factory.certify blueprints/windsorai_client_a.yaml --calibrate
python -m factory.board
python scripts/export_board.py       # after you load tickets, not before
```

⚠ **Where `SYNTHESIS.md` and the code disagree, say which is stale.** The external pass reported
`g_version_hash_is_complete` as a live defect; it was real and had been **fixed six days earlier**
by `13e746e`. It had read the decision record, which describes the pre-fix state. A stale verdict
pointing the wrong way is the characteristic failure of this method.

### Hard rules

1. **Grep before you propose.** No `build` ticket without first searching for the symbol, flag or
   behaviour. If it exists, the ticket is `wire` or `retire` — never `build`. **Cite the grep.**
   Two tickets in the last pass proposed things already implemented.
2. **Acceptance is a measurement, not a description.** *"Board renders dependencies"* is not
   acceptance. *"`python -m factory.board` prints AF-012 as BLOCKED until AF-004 is DONE, asserted
   by `tests/test_board_tickets.py`"* is.
3. **State what would falsify each acceptance criterion.** A gate that cannot fail is decoration.
4. **A ticket that cannot state its acceptance is a `decide` ticket**, not a `build` ticket. Label
   it so.
5. **Include `retire` tickets.** A plan with no deletions in it has not been thought about.
6. **Cite every source** as `filename § section`. If you cannot, mark the ticket `ASSUMED` and say
   why.
7. **The dependency graph must be a DAG.** Name any cycle you break and how.
8. **Rejection is a first-class outcome.** The external pass returned **18 DO and 1 REJECT** across
   nineteen AB items — a backlog that has been endorsed, not triaged. Expect to reject more than
   one of nineteen, and write the reason.

### Where tickets go

```python
from factory.tasks import TaskStore
store = TaskStore(pathlib.Path(".data/tasks.jsonl"))
tid = store.create("AF-01 - F1 <title>", actor="human")
store.add_evidence(tid, "citation", "<source> | acceptance: <criterion>", actor="claude")
```

Then `python scripts/export_board.py` to refresh `docs/board/tickets.json`.
`.data/` is gitignored — the export is the tracked, recoverable copy. **Do not invent a new record
file**; three ticket-record systems already disagree in this estate.

### The pattern to look for

Three independent findings, same shape:

- `deploy.py` implements budget caps and a retry ledger — **`RepoDeployer` has zero callers**.
- `blueprint.py` has `TeamSpec`/`AgentSpec` with a version hash — **§11.5: "nothing executes them.
  `grep` finds one caller, a test."**
- `clients/.claude/hooks/bash-guard.sh` was the estate's only blocking guard — **it depended on a
  binary that is not installed and exited 127, blocking nothing for months.**

**Written and unwired is this estate's signature defect.** It is invisible to tests, invisible to
review, and only a caller-grep finds it. Weight tickets that *wire existing code* above tickets
that write new code, and say so when you do.

### Output, in this order

1. **The build-order reconciliation** — which governs, why, what changes.
2. **A table: AB-01 … AB-19 → ticket id or REJECTED**, with the reason for each rejection.
3. **A JSON array of tickets** starting at `AF-01`, each with:
   `id, track, phase, type (build|wire|retire|decide), title, why, depends_on, acceptance,
   falsified_by, evidence, effort (S|M|L), tier (OBSERVED|DERIVED|ASSUMED), source`
4. **The dependency graph** as a list of edges, plus the critical path.
5. **The first five tickets**, in order, with what each unblocks.
6. **What you could not judge** from the materials, and the one file that would most improve your
   answer. Be specific — *"more context"* is not an answer.

---

## After it runs

- Check a sample of `OBSERVED` claims against the code before loading anything.
- Load with `TaskStore.create()`, then export.
- Any AB item it rejects gets that rejection written into `docs/absorption-backlog.md` — a rejected
  row is closed, not deleted.
