# Deep review, architecture, phase plan, ticket set and board design — Agent Factory

**You are receiving a ZIP pack.** Everything you are allowed to cite is inside it. Read this whole
brief before opening a file, because the first section changes how you are permitted to write every
sentence that follows.

---

## 0 · What you have, and what you do not have

You have **files**. You do **not** have: a shell, a filesystem outside the pack, `git`, `python`,
`pytest`, the internet-facing state of this system, or any ability to run the code you are reading.

That single fact governs the whole pass, because the estate this pack comes from has a house rule it
has already been burned by:

> ⭐ **A zero from an instrument you have not proved can still see is not a measurement.**

So you must separate four verdicts everywhere and never collapse them:

| Verdict | Means |
|---|---|
| `MEASURED-IN-PACK` | a file in the pack states this figure, and you cite the file and section |
| `DERIVED` | you computed it from something `MEASURED-IN-PACK`, and you show the arithmetic |
| `NOT-VISIBLE` | the pack does not contain what would answer this. **This is a finding, not a gap in you** |
| `ASSUMED` | you are proceeding on a guess, and you say so in the same sentence |

⛔ **Never write a `path:line` citation.** You cannot verify line numbers from a pack, and this
estate has already rejected one research answer for exactly that — it cited a repo it could not see.
Cite `filename § heading` instead. A bare filename is not a citation either.

⛔ **Never state a count you did not read in the pack.** If you need a number the pack does not
give, write `NOT-VISIBLE — would be measured by <the command that would produce it>`. That phrasing
is not a hedge; it is the deliverable, because it tells the next session exactly what to run.

⚠ **Expect the pack to contradict itself, and treat every contradiction as a first-class finding.**
It is a snapshot of a live repo whose own documents disagree with each other in at least three
places the authors already know about, and probably more they do not. Finding those is D0 and it is
worth more than anything else you produce.

### Where external research is allowed, and where it is not

Permitted, and useful: **board/UI patterns, dependency-graph modelling, scheduling and phase-gating
practice, and architecture patterns** for D2–D4.

⛔ Not permitted: re-surveying agent frameworks, orchestration topologies, sandboxes, eval harnesses
or desktop stacks. Four prior passes already did that (`R11` vendor taxonomy, `R13` option space,
`R15` what people actually built read repo-by-repo, `R17` the data-engineering field). If you want to
raise one of those, you must first name **which of those four failed to cover it, and in which
section**. An unattributed re-survey will be discarded.

⚠ And every external recommendation must clear §6's PoC constraints or be marked `DEFER — fails
constraint N`. A recommendation that cannot be built here is not a recommendation.

---

## 1 · The system, in the terms its authors use

Read this as the position to **attack**, not as ground truth. The authors wrote it as a strawman and
say so.

**The founding claim:**

> A team of agents did the work, and we can prove it — or we can prove we could not tell.

**Why the estate is shaped this way.** It twice built mechanisms that *acted* with nothing measuring
whether the action helped: one agent produced **233 diagnoses, 234 escalations and 0 fixes over 81
days**; a separate loop ran **965 times, recorded its own 1.6% success rate, and never adjusted**.
Both were capable. Neither was measurable. Everything in the ordering below descends from that.

**The four planes:**

```
agent-factory        builds + certifies the agents        ← blueprints, GreenContract, gates
prefect-connectors   Foundry — the 18-stage build plane   ← the procedure the agents execute
Prefect 3 on Azure   the run plane                        ← where connectors actually execute
aldc-launchpad       evidence, boot prompts, ops SQL      ← the memory layer
```

**The build plane never runs a connector; the run plane never builds one.** A fix to one is
invisible in the other. If your architecture blurs that line, say explicitly why it is safe to.

**The four verdicts, never collapsed** — `PASS` · `FAIL` · `UNMEASURABLE` · `NOT_RUN`.
`UNMEASURABLE` is **not** a pass. Collapsing *"I could not look"* into *"I looked and it was fine"*
is the failure the whole system exists to prevent. Your deliverables must preserve this distinction
in their own data models, not merely describe it.

**The number every recommendation must move:**

> A proven migration was **21.6 minutes of active stage time inside 8 h 20 m of wall clock — 4.3%**.
> The pipeline is not the bottleneck. **Waiting for a human to review and merge is.** Two PRs were
> fully green and had waited 6 and 9 days. Four agents sat blocked on questions written in plain
> English that no surface displays.

⭐ **Rank everything you propose by its effect on that 4.3%.** An architecture that renders agents
more beautifully while the merge queue stays at nine days has optimised the wrong end — say so by
name if any existing plan in the pack does this.

**The commercial argument is not time saved.** It is **five faults that every green light missed**:
a connector that ran ~24 times reporting COMPLETED with zero tables; a migration judged on 22% of
itself; a correct connector scored 30.2% because the check compared 14,517 distinct rows against
4,381 business keys (on the key itself both sides measured 4,381 exactly); a false certification
reproduced before it shipped, over a production baseline that is itself 4.86× duplicated; and ten
containers against one quota turning 30 uploads into 465 with three invisible hours and no error
text. Any design that would not have caught these has missed the point of the product.

**The scale:** 49 connector modules · 7 live on Prefect v3 · 13 importable but not migrated · 29 do
not import at all (20 of the 29 fail on the **same** missing file) · **1 proven end to end**. 48 have
never been scored.

---

## 2 · What already exists — read this before designing anything

⚠ **This is the section most likely to save you from producing a plan to rebuild working code.**
A large amount of what a first reading would propose is already built. The pack contains the source.

| Already built | Where | What it means for you |
|---|---|---|
| **A dependency-aware task board** | `factory/board.py` | Gate not passing → a task. `DEPENDS` is the authored edge map, validated at import so a renamed gate breaks the build rather than dangling. `DONE / READY / BLOCKED`. Everything `READY` is parallelisable by definition. |
| **An append-only, evidence-gated task store** | `factory/tasks.py`, `.data/tasks.jsonl` | Append never overwrite; current state is a fold over events. `status=done` with empty evidence is **rejected by the store, not by convention**. |
| **A wave/roadmap view** | `factory/roadmap.py` | `TEAMS`, `ACTIONS` (18 research decisions), `waves()`. Marks every row `MEASURED` or `AUTHORED` — and records that the honest count is **0 MEASURED, 18 AUTHORED**. |
| **Per-team sequences with dependency closure** | `factory/teamplan.py` | A team declaring 7 gates actually needs 10; the closure is taken and the pulled-in steps are marked as belonging to another team. |
| **Parallel lane allocation by file locality** | `factory/lanes.py` | Explicitly `ASSUMED`, and says so. Lanes are git worktrees. |
| **Live session detection** | `factory/sessions.py` | Reads `~/.claude/sessions/<pid>.json` and checks liveness **against the process table**, because the file outlives the process. Returns `None` — not an empty set — when it cannot see the process table. |
| **A served local UI with three routes** | `scripts/local_tracker.py` (`/`, `/lanes`, `/research`), `tracker.html` | Self-contained: no network, no fonts, no dependencies. |
| **A generated tracker section** | `scripts/build_tracker.py` | Regenerates the artifact's tracker from measured state. `--check` exits non-zero if the page no longer matches the repo. Replaced a checkbox grid with no storage behind it. |
| **A written UI spec that already answers "should we build a session UI now?"** | `docs/specs/control-room.md` (443 lines) | Answers **"No — but the UI is not the part that makes you faster"**, and proposes slices 0–3 with slice 3 held behind a real connector migration. |

### The three costs the control-room spec measured, and which are actually UI problems

| # | Cost | UI problem? |
|---|---|---|
| 1 | 4 agents blocked on plain-English questions no surface shows | **No.** The signal exists at `~/.claude/jobs/<id>/state.json` in a `needs` field. **No line of code reads it.** Alarm *absence*, not alarm fatigue. |
| 2 | 5 of 12 live sessions share one name; only a hand-looked-up `cwd` distinguishes them | **No.** One env var and a test. `CLAUDE_CODE_SESSION_NAME` is already set per lane by `local_tracker.py` — **no live session demonstrates it and no test asserts it reaches the process.** |
| 3 | A page load re-runs 30 probes serially on a single-threaded server: **~19 s**, and two concurrent requests return empty | **Yes** — and it is why the instrument that already exists goes unused. |

⭐ **So the board you are asked to design is not a greenfield build.** Your D4 must state, per
component, whether it is `EXISTS-AS-IS`, `EXTEND`, `REPLACE — because`, or `NEW`. A design that
silently reinvents `board.py` will be rejected.

### ⚠ The real design tension you must resolve — do not paper over it

There are **two task models in this repo and they are not reconciled**:

- **`board.py` refuses to hold a task list.** Its docstring records why: an earlier version had
  twenty-five hand-typed tasks whose *status* was derived from gates while the *list itself* was
  not. Add a gate and no task appeared; delete one and an orphan lingered. *"A hand-maintained board
  wearing a computed status."* So now **every gate that is not passing is a task**, and drift is
  *structurally impossible* rather than merely discouraged.
- **`tasks.py` holds an authored task list** — titles, owners, parents, evidence — in an append-only
  event log.

Paul is asking for a **ticket board with dependent tickets**. Tickets are authored. The board module
refuses authored lists on principle, and has a scar to show for it.

⛔ **You must resolve this explicitly in D4, not choose one silently.** Acceptable resolutions
include: two clearly separated planes (derived *gates* vs authored *tickets*) joined by a declared
link where a ticket cites the gate that closes it; or authored tickets that **cannot reach `done`
without a gate or evidence ref**, which is the `tasks.py` discipline applied to tickets. What is not
acceptable is a hand-maintained list wearing a computed status — that is the exact defect already
paid for once.

⭐ The precedent to follow is already in the code: `roadmap.py` renders authored rows as `AUTHORED`
and measured rows as `MEASURED`, **and makes `AUTHORED` deliberately weaker-looking**, so the
hand-maintained part cannot borrow the credibility of the measured part. Carry that asymmetry into
the ticket board.

---

## 3 · The six deliverables

Produce them in this order. Each later one depends on the earlier ones.

### D0 · Contradiction register — *do this first, and do it ruthlessly*

Before designing anything, read the pack for **claims that disagree with each other**. One row each:
the claim, both sources (`file § heading`), which is better evidenced and why, and what breaks if the
wrong one is believed.

Seeds — the authors already know about these, so finding only these means you did not look:

- The published artifact `docs/artifacts/agent-factory.html` shows `UNMEASURABLE (PASS=11)` and
  "9 of 30 gates". `README.md` says `certify --calibrate` now returns `PASS (PASS=12)`. **Two live
  pages disagree about the same number.**
- `docs/absorption-backlog.md` AB-04 was **written on a premise its own file now marks false** — that
  a one-file corpus meant the instrument had not been shown able to fail. `docs/findings.d/F76`
  corrects it: all twelve assertions have a known-bad, enforced by
  `tests/test_connector_contract.py::test_every_assertion_has_been_proved_able_to_fail`. What one
  fixture cannot show is **generality**. Sensitivity is not coverage.
- `README.md` names `tests/test_eval_can_fail.py` as the gate that proves the instrument can fail,
  then says that test **never loads the corpus** and proves only that the mutation harness works.
  The gate and its reputation are different things.
- `docs/research/README.md` marks R8 `ANSWERED` while its internal half was **rejected** for citing
  nothing — `dispatch` has no state for *"answered, answer half-rejected"*.
- `roadmap.py` says **0 MEASURED / 18 AUTHORED**: *no gate currently decides any of the eighteen
  decisions the research produced.*

⭐ **An inherited premise is a hypothesis, not a finding — including every premise in this brief.**
If something here is contradicted by the pack, say so. Correcting this document is a deliverable.

### D1 · The system as it actually is

A from-scratch statement of the objective, the architecture, and the current state — built from the
pack's **primary sources** (code and specs), not from its summaries. Where a summary and the code
disagree, the code wins and the disagreement goes in D0.

Must include: the four planes and what crosses each boundary; the internal architecture of
`agent-factory` itself (39 modules — group them by role, do not list them); the data stores and their
formats; the gate model and how `readiness` / `board` / `roadmap` / `teamplan` / `lanes` / `goals`
compose; and **what has never been run**, distinguished from what has been run and failed.

### D2 · The phase plan

Phases `P0…Pn`, each with: the question it answers · **entry gate** (what must be true to start) ·
**exit gate** (the *measurement* that closes it, not a feeling) · what is explicitly out of scope ·
and the risk that it is the wrong phase.

Constraints you must respect or argue down in writing:

- `README.md` states an ordering it calls **non-negotiable**: `contract → evals → tasks → blueprint
  → deploy → metrics`, and *"do not add a team, an optimizer or a UI until the eval gate passes."*
  It also records that this gate **passes today and is weaker than its reputation** (see D0).
- `SYNTHESIS.md` §5 holds a **nine-step build order that four independent passes agree on.** It wins
  over any new ordering you invent unless you defeat it with pack evidence. Reproduce it, then say
  where you differ and why.
- `README.md` "What is deliberately absent" pairs each missing thing with **the precondition that
  unlocks it** (optimizer ← a working eval; agent army ← one certified team; second topology ← a
  second team that needs to talk; gym ← the corpus; platform UI ← numbers worth looking at). Each is
  *"cheap to add after its precondition and expensive to unwind before it."*
- `control-room.md` §6 holds slice 3 behind a real connector migration.

⚠ The phase plan must state where **the board work itself** sits, and defend it. There is a live
argument that a control room becomes the project — *"a nicer window onto an unproven machine."*

### D3 · The ticket set — machine-readable, dependency-aware

The core deliverable. Every ticket in **both** prose and one JSON array, so the board in D4 can eat
it without transcription.

```json
{
  "id": "AF-012",
  "title": "imperative, one line",
  "phase": "P1",
  "kind": "build | measure | decide | fix | retire",
  "depends_on": ["AF-004", "AF-009"],
  "blocks": ["AF-021"],
  "gate": "breadth | null",
  "acceptance": "the MEASUREMENT that closes it — a command and its expected output",
  "evidence_kind": "test | command-output | artifact | written-decision",
  "size": "S | M | L",
  "basis": "MEASURED-IN-PACK | DERIVED | ASSUMED",
  "source": "file § heading, or NEW",
  "risk": "what makes this ticket wrong",
  "poc_doable": true
}
```

Hard rules:

1. **`depends_on` must form a DAG.** State that you checked, and name any cycle you had to break.
2. **Every id in `depends_on` and `blocks` must exist in the set.** `board.py` validates its edges at
   import for exactly this reason; a dangling edge must break loudly, never dangle quietly.
3. **`acceptance` is a measurement, not a description.** *"Board renders dependencies"* is not
   acceptance. *"`python -m factory.board` prints AF-012 as BLOCKED until AF-004 is DONE, asserted by
   `tests/test_board_tickets.py`"* is.
4. **A ticket that cannot state its acceptance is a `decide` ticket, not a `build` ticket.** Say who
   decides and what the options are. Do not invent an acceptance to make a ticket look actionable.
5. **Include `retire` tickets.** The pack records at least one candidate: R13 run 2 recommends
   retiring `orchestration-bench.html` (backlog row AB-12). A plan with no deletions in it has not
   been honest about a corpus this size.
6. **Start from the nineteen that already exist.** `docs/absorption-backlog.md` holds AB-01…AB-19 —
   conclusions that named a control and were never actioned, each with `SOURCE / SAYS / WHY IT ISN'T
   FILLER / ACTION`. For each, emit a ticket, **or** a written rejection with a reason. *A written
   rejection closes a row; silence does not.* Do not restate them — restatement is what made them a
   backlog.
7. **Two whole answers were never absorbed at all** — R14 (1,389 lines, cited seven times, zero
   conclusions taken, AB-16) and R18 (referenced entirely in the future tense, AB-17). Both are in
   the pack. Read them and convert them, or reject them in writing.

### D4 · The board — design and PoC spec

**Purpose:** track tickets, their dependencies, and their readiness. Sessions are a **stretch goal**,
gated behind tickets working, per Paul: *"tickets at least (if not sessions)"*.

Deliver:

1. **A per-component disposition table** — `EXISTS-AS-IS` / `EXTEND` / `REPLACE — because` / `NEW`
   against the inventory in §2. Anything marked `NEW` that duplicates a listed module will be read
   as not having read §2.
2. **The resolution of the two-task-model tension** (§2), argued, with the losing option stated.
3. **The data model** — ticket store format, where it lives, how it is written, and how a ticket
   relates to a gate. It must be compatible with the append-only, evidence-gated discipline in
   `tasks.py`: *a ticket cannot close without evidence, enforced by the store, not by convention.*
4. **The views**, each earning its place: the DAG (what blocks what) · READY (everything with no
   unmet dependency — parallelisable by definition) · phases · and the blocked-question channel.
   ⭐ Surfacing the `needs` field from `~/.claude/jobs/<id>/state.json` is the **cheapest measured
   win in the pack** — four agents idle, one waiting on a yes/no that takes a human four seconds. If
   your design does not include it, justify the omission.
5. **The render-performance answer.** The existing tracker re-runs 30 probes serially per page load
   (~19 s) on a single-threaded server, and two concurrent requests return empty. Say concretely how
   the board avoids inheriting this. A cache needs a stated invalidation rule, and a stale board that
   looks live is worse than a slow one.
6. **A DAG layout that stays legible.** Say what happens at 20, 100 and 400 tickets, and what the
   degradation strategy is. A graph view that becomes hairball at the size this will actually reach
   is not a design.
7. **The build sequence** — smallest useful slice first, each slice independently shippable, with the
   measurement that says the slice worked.

### D5 · The artifact — the app, drawn

A single self-contained HTML page, heavily visual, that a reader can understand the whole system
from without reading the code.

**Figures, not prose. Every figure's geometry computed from the pack's own numbers** — a figure that
could carry any numbers is decoration. Required:

1. **The four planes**, with the boundary drawn so *"the build plane never runs a connector"* is
   visible rather than captioned.
2. ⭐ **The time-proportional strip: 21.6 minutes inside 8 h 20 m — 4.3%.** Draw the 95.7% wait. This
   is the single most important figure on the page and the product's whole argument.
3. **The four verdicts**, with `UNMEASURABLE` visually *not* a pass — a figure showing the collapse,
   not a four-row table.
4. **The estate as a proportion plate** — 49 / 7 / 13 / 29 (20 of them on one missing file) / **1**.
5. **The five faults every green light missed** — the commercial argument. The best figure on the
   page after #2.
6. **The 18-stage pipeline**, with the three agent stages that are **71.4% of active time** drawn
   proportionally.
7. **The phase plan and ticket DAG** from D2 and D3, with `READY` visually distinct from `BLOCKED`.
8. **The corpus and its absorption state** — 18 passes, 23 answers, 19 unactioned conclusions,
   0 MEASURED / 18 AUTHORED. Absorbed and unabsorbed must be visually distinct.

**Truth-marking is mandatory.** ⭐ **A planned component must never look built.** Four distinct
treatments for built / partial / planned / rejected, with the key where the reader hits it first.
Every headline number carries its basis on the page, not in a footnote. `PASS (PASS=12)` must read as
**a replay against one recorded connector** — not a live measurement, not a second subject. If the
page lets a reader think twelve passing assertions means the contract generalises, it has lied, and
`findings.d/F76` exists because that exact claim was already mis-stated once.

Technical: single file, no build step, no external JS/CSS beyond an inline `<style>`/`<script>`,
inline SVG for figures, legible in light and dark, wide content scrolls inside its own container
rather than the page.

### D6 · Gaps, optimisations, and the questions only Paul can answer

- **Gaps** — with the evidence each one is real. Distinguish `ZERO` (didn't happen, instrument live)
  from `NOT-RECORDED` from `NOT-VISIBLE` from `NOT-RETAINED`. Candidate seams: instrument blind
  spots (`dispatch` *"cannot see whether a prompt was ever actually pasted anywhere"*;
  `filed()` globs exactly one directory; finding F75 records that **both reconciliation checks passed
  over three unabsorbed answers**); the nine findings in `docs/findings.d/` (a shared ledger cannot
  survive parallel lanes; lanes cannot see each other live; the board number depends on where you run
  it; an invisible refusal reads as a broken feature) — are any *fixed*, or only *recorded*?
- **Optimisations** — each with cost, saving, and **the measurement that would show it worked**.
  An optimisation with no number attached is an opinion. Rank by effect on the 4.3%.
- **Questions only Paul can answer** — one block at the end. Do not resolve these yourself and do not
  block on them; do everything independent of them first. They are, at minimum:

  1. **Is this productised and sold, or internal tooling that makes one agency faster?**
  2. **Who is the buyer, and do they ever open the UI?** If a non-engineer client ever opens a
     surface, the approval plane becomes a *product* surface — and it is currently the plane with no
     interface at all.
  3. **One estate or many?** If the end state is N client estates, multi-tenancy stops being a
     backlog item and becomes an architectural premise.
  4. **What is the timeline?** No date has been stated anywhere, so no design can currently be judged
     too slow.
  5. ⛔ **The embedded terminal question** — the pack marks this *the blocking one*. It has been
     answered by accident twice: once by a pass restating the estate's own position back to it, once
     by a pass never told the rule existed. **Do not settle it by taking whichever answer arrives
     first.** Lay out the options and their consequences and stop.

  For every recommendation you make, state **which way it changes under each reading of 1–4.**

---

## 4 · PoC constraints — the accuracy gate

⭐ **A design that cannot be built here is not a design.** Every D3 ticket carries `poc_doable`, and
every D4 component must clear these or be explicitly marked `DEFER — fails constraint N`:

1. **Python 3 standard library only.** The existing tracker is *"self-contained: no network, no
   fonts, no dependencies."* Any proposed dependency must be argued for by name, with what it
   replaces and what it costs.
2. **No database.** State lives in append-only JSONL under `.data/` (gitignored) plus files in the
   repo. If you need a database, say what specifically fails without one.
3. **Windows is the primary platform.** `sessions.py` already shells to `tasklist` for this reason.
   Anything POSIX-only is disqualified unless it degrades cleanly.
4. **Single developer, sessions of hours not weeks.** Size everything `S` (under an hour) / `M` (a
   session) / `L` (more than a session), matching `lanes.py`. An `L` ticket must be justified or
   split.
5. **The existing test suite must stay green.** Note especially that
   `factory/readiness.py` yields `docs/artifacts/agent-factory.html` **by name** into the suite
   fingerprint, and `factory/lanes.py` and `factory/schedule.py` reference that path — so adding a
   file there is safe, but **moving or renaming one breaks the readiness gate.**
6. ⛔ **Do not propose moving anything out of `docs/research/` or `docs/research/answers/`.**
   `factory/synthesis.py` defines the research record by two globs over exactly those directories,
   and `tests/test_synthesis_current.py` goes red while any matching file goes unmentioned in
   `SYNTHESIS.md`. A file moved out becomes permanently invisible to the only instrument watching the
   record. This already happened once, with R10, and had to be undone.
7. **No new always-on service** without saying who starts it, what happens when it is not running,
   and how the user finds out.
8. ⛔ **No new dependency on a sibling repo.** See §4b — this is a stated direction, not a
   preference.

---

## 4b · ⛔ Decoupling from `aldc-launchpad` — a stated direction, and a design constraint

**Paul's direction, 2026-08-29: `agent-factory` should stand alone.** It must be clonable and
measurable on its own, without any sibling repo checked out beside it.

⚠ **This contradicts a document in your pack, deliberately.** `docs/specs/product-end-state.md` §2
declares `aldc-launchpad` as one of the four planes — *"the memory layer"* — and
`factory/handoff.py` states that boot prompts *"are cross-repo session memory and live in
aldc-launchpad by long-standing convention."* Read as written, the pack argues **for** the coupling.
That argument is now superseded on direction, but **not** dismissed: you must still address its cost
(below) rather than route around it.

### The coupling as measured, so you are not designing against a guess

Four places in code resolve a path **outside this repo**, off the parent directory:

| Where | Resolves to | Escape hatch? |
|---|---|---|
| `factory/handoff.py` — `BOOT` | `<parent>/aldc-launchpad/boot-prompts` | **None** |
| `factory/readiness.py` — `g_work_has_a_ticket` | `<parent>/aldc-launchpad/boot-prompts/drafts` | **None** — and this is a **gate** |
| `factory/readiness.py` — `CONNECTORS` | `<parent>/prefect-connectors` | ✅ `$PREFECT_CONNECTORS` |
| `scripts/build_figure_lastwrite.py` — `CONNECTORS` | `<parent>/prefect-connectors` | ✅ `$PREFECT_CONNECTORS` |

⭐ **The pattern for the fix already exists in the codebase and was applied to one sibling and not
the other.** `prefect-connectors` is overridable by environment variable; `aldc-launchpad` is not.
That asymmetry is the finding, and it makes the remedy small rather than architectural.

⚠ **`tests/test_repo_root.py` asserts `handoff.BOOT.parent.name == "aldc-launchpad"`** — the suite
actively locks the coupling in. Decoupling therefore *must* change a test, and a plan that reports
"tests still green" without saying which assertion it rewrote has not done the work.

⭐ **Why this is not cosmetic: a readiness gate reads another repo, so this system's own headline
number is not reproducible by anyone who clones only this repo.** For a project whose entire thesis
is *"we can prove it — or we can prove we could not tell"*, a score that depends on what else is
checked out next to it is a defect in the instrument, not a packaging inconvenience.

**Finding `F72` in your pack already records the symptom** — the same commit measured **9 of 30**
from the main checkout and **10 of 30** from a lane worktree, because sibling paths resolve
differently from each location; the launchpad gate goes `UNMEASURABLE` from a worktree while the
connectors path lands on an unmerged branch. F72 frames this as a *cwd* problem. **Consider whether
the deeper cause is the sibling-repo coupling itself**, and say so in D0 if you agree.

⚠ Note also that F72 cites the ticket gate at `readiness.py:811` and it is no longer there — the
line moved. That is a live demonstration of why §0 forbids you to cite line numbers.

### What you must deliver on this

1. **A D0 row** recording the contradiction between Paul's direction and `product-end-state.md` §2.
2. **In D1**, state the architecture **as it is** (four planes, coupled) and **as directed**
   (standalone), and name precisely what crosses the boundary today.
3. **In D3, a decoupling ticket group**, sequenced, each with a measurable acceptance. The obvious
   shape — argue with it if you disagree — is: an env-var override mirroring `$PREFECT_CONNECTORS`;
   a gate that reports `UNMEASURABLE` **with a reason naming the absent repo**, never `FAIL`, when
   the sibling is not present; the `test_repo_root` assertion rewritten to assert *configurability*
   rather than a hard-coded repo name; and an acceptance test that **clones or copies this repo
   alone into an empty directory and runs the suite plus `python -m factory.readiness`**. That last
   one is the real gate — everything else is a proxy for it.
4. **Name the cost honestly.** `handoff.py` warns that relocating boot prompts here would create
   *"the fifth artefact home CLAUDE.md warns of"* — a real problem this estate has already paid for.
   Decoupling the *code path* from the *artefact convention* are two different tasks and may have
   different answers: the code can stop **requiring** the sibling while boot prompts still **live**
   there when it is present. Say whether you think that split is sound.
5. **In D4**, the board must store its own state inside this repo. No board component may read a
   sibling repo, and any view that would benefit from one must degrade to a stated
   `NOT-VISIBLE` rather than an error or a blank.

⛔ **Do not treat the launchpad files in `launchpad-context/` as a live dependency.** They are
included as *history* — the research programme began there and `product-end-state.md` cites the
brief. Read them; do not design anything that reads them at runtime.

---

## 5 · Rules this pass runs under

1. Every load-bearing figure carries `MEASURED-IN-PACK` · `DERIVED` · `NOT-VISIBLE` · `ASSUMED`.
2. Cite `file § heading`. Never a line number. Never a bare filename.
3. **Never collapse the four verdicts**, in your prose or in any data model you design.
4. **Do not average disagreeing sources.** Record the disagreement and which evidence is stronger.
5. **A written rejection closes a row; silence does not.**
6. **A planned thing must never be rendered as a built thing** — in the artifact, the tickets, or the
   board.
7. **Do not resolve Paul's five questions.** State how each recommendation changes under each answer.
8. **Correcting this brief is a deliverable.** It was written by a session that had the repo but not
   your reading time; where the pack contradicts it, the pack wins and it goes in D0.
9. If you run out of budget, deliver **D0, D1, D2 and D3** completely rather than all six thinly.
   The ticket set with honest dependencies is the point; the artifact is the part that most rewards
   being done last.

---

## 6 · Definition of done

- **D0** — contradiction register with more rows than the five seeded here, each with both sources
  and which is better evidenced.
- **D1** — architecture and current state from primary sources, with what has never been run stated
  separately from what ran and failed.
- **D2** — phases with entry gate, exit **measurement**, out-of-scope, and risk; reconciled against
  `SYNTHESIS.md` §5's nine-step order and `README.md`'s precondition table, with differences argued.
- **D3** — the ticket JSON array: a valid DAG, no dangling edges, every ticket with a measurable
  acceptance, all nineteen AB rows converted or rejected in writing, `retire` tickets included.
- **D4** — board design with the component disposition table, the two-task-model tension resolved
  and the losing option named, the data model, the views, the render-performance answer, the DAG
  legibility answer at 400 tickets, and a slice sequence.
- **D5** — the single-file HTML artifact with all eight figures, geometry from real numbers, four
  truth treatments, and every headline number carrying its basis.
- **D6** — gaps with evidence, optimisations ranked by effect on 4.3% with a measurement each, and
  Paul's five questions in one block with per-recommendation sensitivity.

---

## Appendix · What is in the pack

```
README.md                        the founding claim, the ordering, the four verdicts,
                                 what is deliberately absent — read FIRST
docs/specs/product-end-state.md  what it is FOR — read SECOND, always
docs/specs/                      architecture-v0 · control-room (443 lines, the UI spec)
                                 client-intake-portal · ui-future-features · terminal-configuration
docs/absorption-backlog.md       AB-01…AB-19, the unactioned conclusions — the seed of D3
docs/findings.md + findings.d/   corrected premises, incl. F76 (sensitivity ≠ coverage)
                                 and F70/F71 (a shared ledger cannot survive parallel lanes)
docs/research/README.md          the run order, each pass's border, and what each must refuse
docs/research/SYNTHESIS.md       2,422 lines. §5 the build order · §7 where answers disagree ·
                                 §17 the reconciliation — read §17 in full
docs/research/R*.md              18 prompts
docs/research/answers/           23 filed answers, incl. R14 (1,389 lines, unabsorbed)
                                 and R18 (937 lines, unabsorbed)
factory/*.py                     39 modules — the system itself
tests/*.py                       26 test files — what is actually asserted
scripts/local_tracker.py         the served UI, three routes
scripts/build_tracker.py         the generated tracker section
blueprints/*.yaml                2 blueprints
evals/                           the sha256-pinned corpus — ONE fixture
.data/tasks.jsonl                31 task events, the append-only store in use
tracker.html                     the rendered UI as it stands today — read it for D4
docs/artifacts/                   agent-factory.html (STALE — see D0) · orchestration-bench.html
                                 (a retire candidate) · README.md
docs/evidence/                    per-run evidence notes, incl. phase-a-windsorai
BRAIN-DUMP.md                     the original unstructured intent, before any of this was built

launchpad-context/               a SECOND repo (aldc-launchpad), included because the research
                                 programme started there and product-end-state.md cites it:
  agent-team-factory-report.md      1,210 lines — audit, certification stack, pilot path
  agent-fleet-architecture-spec.md    606 lines — 2026-08-19, "migrate 29 connectors fast"
  deep-research-prompt-agent-team-constructor.md   400 lines
  deep-research-prompt-connector-e2e.md            263 lines
  agent-sandboxes-simulation-and-bi-exit-2026.md   494 lines
  army-graph-engineering-research-prompt.md        155 lines
  narration-and-voice-system.md                    816 lines
  zeus-foundry-brief.html           the 18 Aug 2026 product brief — the source of
                                    product-end-state.md §1
```

⚠ **`launchpad-context/` predates `agent-factory` and is not governed by its rules.** Where it
disagrees with the `agent-factory` files, the newer repo wins and the disagreement is a D0 row.

⛔ **Not in the pack, on purpose:** the four `*-evidence-pack.md` files (~4 MB of generated
concatenation — they are views of files you already have), `.git/`, `.worktrees/`, `.venv/`, and the
rest of `.data/`. If you find yourself needing one, that is a `NOT-VISIBLE` finding — name it.
