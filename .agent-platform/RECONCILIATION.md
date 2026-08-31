# Reconciliation — the bootstrap pack against what this estate actually has

**Measured 2026-08-31** against `agent-factory` @ `6d9e94a` (branch `main`) and
`agent-army-research` @ `11c5b3d`. Every `EXISTS` row cites a path, and most cite a line. Open the
file before relying on the row.

This document exists because the pack was written without access to the repository. Its value is
its research scaffolding and its prior-art pointers. Its risk is that it names, as things to build,
nine subsystems this estate already has under different names — and one whole programme this
estate has already **falsified on evidence**.

---

## 1. The three findings that should change what happens next

### ⛔ 1.1 The pack's founding premise was refuted here, a day before it was installed

`agent-army-research/research/synthesis/W0-foundations.md` (dated 2026-08-30) is a completed
research wave whose executive line is:

> **Wave 0 falsified the programme's founding premise. That is a success, and it cost one morning
> instead of one build cycle.**

Specifically, and each verified against primary sources in that document: Artificial Organization
Engineering is organisation-oriented MAS, which has a metamodel (Moise+), a runtime (JaCaMo) and a
textbook; the category name is taken twice in 2026 (Waites `arXiv:2602.13275`; **IMACS**
`arXiv:2607.25446`, which *is* the organizational-compiler thesis, published five weeks ago); and
the surviving novelty claim is refuted on all four components.

The pack's `VISION.md` proposes an "Organization Factory / Compiler", "Org-IR", a "Collective
Cognition Fabric" and an "Evolution Chamber" as things to build. **Wave 0's disposition on that
category is `RESEARCH ONLY` / `DO NOT BUILD`.** The prior session's call, recorded at
`boot-prompts/workflow-library-2026-08-31.md:44-48`, is *"stop investing there — 27 of 30 prompts
`NOT_RUN`; leave them."*

This does **not** mean the pack is worthless. It means the pack's *category framing* is dead and its
*engineering patterns* are live. Wave 0 itself paid for the fifth verdict (below). Mine it for
mechanisms; do not adopt its programme.

### ⭐ 1.2 The estate's own gate says Agent Army is locked, and the precondition is unmet

`README.md:94-104` lists what is deliberately absent, each with a named precondition:

| Not here | Unlocked by |
|---|---|
| Optimizer | A working eval — the fitness function *is* the eval score |
| Agent Army / supervisor tiers | **One certified team**, plus evidence a tier helps |
| More than one comms topology | A second team that actually needs to talk to the first |
| Gym | The eval corpus plus a scoreboard |
| Platform UI | Numbers worth looking at |

**No team is certified.** `.data/runs.jsonl` holds 10 rows, 0 `PASS`; `.data/events.jsonl` holds 8
runs with `PASS=0`; all 7 `agent_returned` events carry `dry_run=True`. **No agent has ever been
dispatched for real by this system.** Regenerate:

```bash
python -c "import json;rows=[json.loads(l) for l in open('.data/runs.jsonl')];print(len(rows),[r.get('outcome') for r in rows])"
```

Every pack proposal at Rank 4 and above (Communication Mesh, Collective Cognition, Mission
Assembly, Venture Loop) sits behind that unmet gate. The pack's roadmap would have us start at
Rank 4. The estate's own rule says finish Rank 2 first.

### 1.3 The first real run is blocked by one open design defect

`docs/findings.d/F90` (OPEN, DESIGN, **untracked as of this writing**): `TeamSpec.repo` is inside
the version hash and **nothing reads it**. `worktrees.REPO` is a module constant bound to this
checkout. Both presets with a runnable verifier (`add-measure`, `model-redesign`) are `pbi_model`
work living in `~/repos/clients`, so every ticket the controller can reach a verdict on is one it
would run in the **wrong repository**.

F90 proposes two remedies and an order: **(b) make the controller refuse** a ticket whose `repo` is
not this checkout — a few lines, honest immediately — then **(a)** thread the repository through
for real. That ordering is correct and should be honoured.

---

## 2. Where the pack's "durable project state" already lives

The pack ships `PROJECT_STATE.template.yaml` with fields for `known_gaps`, `decisions`,
`human_questions`, `current_autonomy_rank`. **Do not fill it in.** Each field already has a home
that is *read by code*, not maintained by convention:

| Pack artifact | Existing home | Read by |
|---|---|---|
| `PROJECT_STATE` | `boot-prompts/README.md` — the only maintained boot file, says so at line 7 | humans; it is a router |
| `CURRENT_ARCHITECTURE` | `docs/agent-army/CURRENT_STATE.md` — every row cites `file:line` | humans |
| `ROADMAP` | `factory/roadmap.py` (377 ln) — **has no task list by design**; `board.board()` derives it from gate verdicts | `factory/board.py`, tracker |
| `TASKS` | `.data/tasks.jsonl` (185 events), `factory/tasks.py` — append-only, evidence-gated close | `factory/tasks.py:148` raises `EvidenceRequired` |
| `DECISIONS` | `docs/research/SYNTHESIS.md` (18 passes reconciled); `docs/absorption-backlog.md` for unactioned conclusions | humans |
| `RESEARCH` | sibling repo `agent-army-research/` — protocol, evidence tiers A–E, hypothesis ledger | `scripts/validate_repo.py` |
| `EVALS` | `evals/` + `evals/MANIFEST.sha256`, loaded via `factory/corpus.py` (hash-verified on load) | `factory/certify.py` |
| `CAPABILITIES` | `factory/registry.py` — `(shape, layer) → workflow`, versioned by `SKILL.md` content hash; `unproven()` reports coverage honestly | tests |
| `RUNS` | `.data/runs.jsonl` + `.data/events.jsonl`, `factory/runs.py` / `factory/events.py` | `factory/control.py:550` |
| `HANDOFF` | `factory/handoff.py` (210 ln), `.data/handoffs/` | — |

⛔ **There is no tracked `ROADMAP.md`, `ADR/`, `DECISIONS.md`, `PROJECT_STATE.*`, `TASKS.md` or
`HANDOFF.md`.** The only files with those names sit inside `bootstrap/`. That is not an absence to
be filled; it is a deliberate choice — `factory/roadmap.py` refuses to keep a hand-authored task
list *on principle*, because a derived board cannot drift from the gates it reports.

---

## 3. Disposition table — every major pack concept

`KEEP` = exists and is good · `EXTEND` = exists, add to it · `REFACTOR` = exists, wrong shape ·
`RESEARCH` = genuine open question · `NOT YET JUSTIFIED` = pack proposes it, evidence does not.

| Pack concept | Status here | Evidence | Disposition |
|---|---|---|---|
| Five-verdict contract | **EXISTS, stronger than the pack's** | `factory/contract.py:32-37` — `PASS/FAIL/UNMEASURABLE/ERROR/NOT_RUN`; `ERROR` dominates the fold at `:102`. Grounded in ITU-T Z.140 §24.2 | **KEEP** — pack has no equivalent |
| Positive GREEN contract | **EXISTS** | `factory/contract.py`; `evals/` corpus hash-verified; `tests/test_connector_contract.py` enforces every assertion has been proved able to fail | **KEEP** |
| Grader separation ("no self-grading") | **EXISTS, partially enforced** | `evaluator_service/` separate identity; `factory/certify.py:15-17` documents `--calibrate` as *"worthless as evidence that an agent did not grade itself"* | **EXTEND** — separation is attributed, not yet *enforced* |
| Evidence-gated task close | **EXISTS** | `factory/evidence.py` classes `TARGET/CONSUMER/REGRESSION/ROLLBACK`; refusal lives in the **store** (`tasks.py:163`), not a convention | **KEEP** |
| Worktree isolation | **EXISTS** | `factory/worktrees.py:38-39`, `factory/claims.py:200-244` (`O_CREAT\|O_EXCL`, Windows `PermissionError` race handled) | **KEEP** |
| Typed agent messages / comms fabric | **EXISTS as a channel, deliberately ephemeral** | `factory/bus.py:48` `KINDS` (5, rejected at `:74`); delivery is a **hook** (`scripts/hooks/lane-bus.py`) so a lane that never polls still receives. Design rationale: `docs/agent-communication.md` | **KEEP** — do **not** replace with the pack's 22-primitive protocol |
| Durable cross-entity event log | **PARTIAL** | `factory/events.py` — 9 closed event kinds, terminal kinds must carry a `Verdict` enum (`:225-231`). Per-run, not organizational | **EXTEND** if a second team ever needs it |
| Knowledge objects / collective cognition | **PARTIAL** | `docs/findings.d/` — 23 files, addressable, reviewed, merges with the branch; `factory/findings.py` reads them **as data** so `by_lane()` briefs an agent only with corrections that hit it | **EXTEND** — this is a working experience-transfer mechanism already |
| Capability registry | **EXISTS** | `factory/registry.py`; `unproven()` returns 4 of 9 workflows never run on real work | **EXTEND** |
| Readiness / autonomy rank | **EXISTS** | `factory/readiness.py:1394` `GATES` — 30 gates across 5 phases; `factory/goals.py` validates grouping on import; a goal with no measurable gate reports `NOT-MEASURED`, never `0%` | **KEEP** — supersedes the pack's `PROGRESS.yaml` |
| Session detection | **EXISTS** | `factory/sessions.py` — liveness checked against the **process table**, not file existence | **KEEP** |
| Cost ledger | **EXISTS, measured not estimated** | `factory/runs.py:82-130` reads Claude transcripts; basis `RECORDED/RECONSTRUCTED/NOT-RECORDED` (`:42`) | **KEEP** |
| Retry / attempt cap | **EXISTS** | `factory/deploy.py:38-177` `AttemptLedger`, max 2, counts before dispatch; dry runs excluded (fix for F85) | **KEEP** |
| Mission object / lifecycle | **ABSENT** | No mission object, schema or lifecycle. `docs/agent-army/CURRENT_STATE.md` | **NOT YET JUSTIFIED** — a lane brief + a gate cover today's need |
| Org-IR / organization compiler | **ABSENT** | — | **NOT YET JUSTIFIED** — and IMACS already published it (§1.1) |
| Mission-shaped knowledge graph | **ABSENT** | — | **RESEARCH** — but only after a second team exists |
| Dynamic team assembly / swarming | **ABSENT, tested and rejected** | `blueprints/orchestrator_team.yaml` — a 3-agent blueprint **built, tested and rejected on evidence**, kept deliberately. Unlock threshold stated in its header | **NOT YET JUSTIFIED** — the threshold is written down; meet it first |
| Evolution Chamber / optimizer | **ABSENT by decision** | `README.md:98` — unlocked by a working eval | **NOT YET JUSTIFIED** |
| Session / Mission Console | **PARTIAL** | `tracker.html` + `scripts/local_tracker.py`; `docs/specs/control-room.md` | **EXTEND** — but see §5 |
| Heartbeats | **ABSENT by decision** | `factory/claims.py:10-20` cites R6 *"alive ≠ working"*; uses commits-ahead/dirty as progress instead | **KEEP the refusal** — pack proposes heartbeats; this estate has a better argument |
| Venture / commercial track | **ABSENT** | — | **NOT YET JUSTIFIED** — gated behind a certified team |
| DGX Spark / compute fabric | **ABSENT** | — | **DEFER** |

---

## 4. Prior-art mining — what the three reference repos actually gave us

All three verified to exist; all three MIT. Full reports in this session's transcript; the
load-bearing conclusions:

### Super Simple Software Factory (`disler/super-simple-software-factory`, 773★)
⚠ **It orchestrates `pi`, not Claude Code** — `agent_cc.py` is a stub raising `NotImplementedError`
and `agents.py:61` hard-rejects non-`pi`. Prior art at the **pattern** level only; not liftable.

Five patterns that would let us **delete** rather than add:
1. **A Python function replaces the workflow engine.** `main()` is the graph, `with run.phase()` is
   the node, `if verified:` is the edge. Nothing serialises workflow state because the call stack
   holds it. — This estate already agrees (`factory/control.py` is exactly this shape).
2. **`kind="code"` phases replace agents.** There is no tester agent; running the suite is a
   subprocess. *"A known command is code, not an agent."* This is the difference between a 5-agent
   and a 15-agent factory.
3. **`as_envelope()` collapses result-type dispatch to one path.**
4. **Post-hoc git change-set diffing replaces sandboxing** — ~100 lines, and it catches what a
   write-interceptor cannot (reversion via `git checkout`). Transfers to Claude Code unchanged.
5. **SQLite + `rowid` polling replaces the entire streaming stack** — live view and history are the
   same query, so there is no replay subsystem.

🚩 **And one defect to invert if we lift it:** every quality block ships as `["echo", "PLACEHOLDER"]`,
`echo` exits 0, so a stamped repo reports `verified=True` and commits **having tested nothing**. The
authors warn about it in a 20-line banner — but a banner is not a control. This is precisely the
blind-instrument family this repo has met five times.

### Inkwell (`disler/inkwell-agent-sandboxes-and-software-factory`, 147★)
Uses **exe.dev VMs over plain SSH** — not Docker, not E2B. ⚠ A web search for this repo returns E2B
text belonging to a *different* repo (`disler/agent-sandboxes`); that must not reach any downstream
doc.

**Verdict: git worktrees suffice for this repo at its current stage.** The honest boundary:

> A worktree is sufficient while a misbehaving agent's worst outcome is **losing work you can
> regenerate**. A sandbox is warranted when its worst outcome is **reaching something you cannot** —
> production credentials, the shared git object store, or an unbounded bill.

The gap to close is **not isolation** but the two things a VM would have given incidentally:
(a) a **capped per-run credential with revocation verified against the key *list***, and (b) post-hoc
git-diff permission enforcement. Inkwell's measured trap is worth carrying: *right after a
successful DELETE, `GET /key` still returns 200 — the LIST is the authoritative view.*

Also worth adopting: **teardown is never chained** (the destroyed thing is the evidence), harvest
into `refs/sandbox/<id>` never touching a branch you own, and **a harvest failure aborts the whole
teardown**.

### Paperclip
Report outstanding at time of writing.

---

## 5. What the pack proposes that this estate should refuse

| Pack proposal | Why refuse |
|---|---|
| Fill in `PROJECT_STATE.yaml` | A hand-maintained mirror of state that code already derives. §2 |
| Generate `.agent-platform/research/` queue | Competes with `agent-army-research`, which has stronger epistemics. §1.1 |
| 22-primitive communication protocol | `README.md:96` — a second topology is unlocked by *a second team that needs to talk to the first*. There is not yet a first. |
| Rank 4+ work (mesh, cognition, assembly, venture) | Gated behind one certified team; zero teams are certified. §1.2 |
| Org-IR / organization compiler | Published prior art (IMACS), and no evidence a distinct IR earns its complexity. §1.1 |
| Heartbeats | This estate rejected them with a better argument. §3 |
| Gamified Mission Control now | `README.md:98` — Platform UI unlocked by *"numbers worth looking at"*. `.data/runs.jsonl` is 10 rows, 0 PASS. |

The pack is a **north star and a research scaffold**, exactly as the operator framed it. Treated as a
build plan it would move this estate backwards, by starting six ranks above its evidence.
