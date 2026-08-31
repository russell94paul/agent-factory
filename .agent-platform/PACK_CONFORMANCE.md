# Pack conformance — every instruction in `START_CLAUDE_HERE.md`, and what was actually done

**Measured 2026-08-31.** The pack was read in full from
`.agent-platform/bootstrap/START_CLAUDE_HERE.md`, sha256 `c8d11f3d39d574e8` — **identical** to both
extracted copies in `~/Downloads`, which are also identical to each other. 109/109 manifest files
installed, no differing file; the only gaps are five empty directories git cannot track.

## Why this file exists

`RECONCILIATION.md` says what each pack *concept* maps to in this estate. It does **not** say which
pack *instructions* were followed. Four were deliberately not, and until now that lived in a
session transcript and two boot prompts — which is exactly the state this repo has a document about
(`docs/agent-army/README.md`: speculative architecture mistaken for the running system, one layer up).

⭐ **Read the `DEVIATED` rows as decisions awaiting your review, not as settled.** Each is a
judgement made by a session, against a pack the operator supplied. The reason is stated so it can be
overruled cheaply.

Regenerate the file list this is checked against:

```bash
grep -nE "^(### Phase|## |[0-9]+\. |- )" .agent-platform/bootstrap/START_CLAUDE_HERE.md
```

---

## Legend

`FOLLOWED` — done as written · `SUBSTANCE` — the outcome was produced by a different mechanism than
the pack names · `DEVIATED` — deliberately not done, reason stated · `NOT YET` — not done, no
decision taken against it.

---

## Phase 0 — Recover context before changing architecture

| # | Instruction | State | Evidence / reason |
|---|---|---|---|
| 0.1 | Read `README.md`, `VISION.md`, `BUILD_START_TO_FINISH.md`, `AUTONOMY_LADDER`, `WEB_REMOTE_SESSION_RUNBOOK`, `EXECUTION_SURFACE_POLICY`, `RESEARCH_PROGRAM`, `PATTERN_EXTRACTION_POLICY`, `REFERENCE_IMPLEMENTATIONS` | **FOLLOWED** | All read, plus all 19 `docs/`, 8 schemas, 6 scripts, 13 skills |
| 0.2 | Invoke / follow `repo-context-compiler` | **SUBSTANCE** | The skill was never installed (`.claude/skills` does not exist). Its *procedure* was followed by four parallel `Explore` agents over orchestration, evaluation, docs/history and UI/memory |
| 0.3 | Create/update `.agent-platform/PROJECT_STATE.yaml` from the template | ⛔ **DEVIATED** | **Not created.** That state already exists and is *read by code*: `boot-prompts/README.md` (the maintained router), `.data/tasks.jsonl` (189 events), `factory/roadmap.py` — which refuses to hold a task list **on principle**, because a derived board cannot drift from the gates it reports. A second file would be a hand-maintained mirror |
| 0.4 | Build `.agent-platform/CURRENT_STATE.md` with evidence-linked paths | **SUBSTANCE** | `docs/agent-army/CURRENT_STATE.md` already existed, measured 2026-08-30, every row citing `file:line`. `RECONCILIATION.md` points at it rather than duplicating it |
| 0.5 | Recover Prefect/DAG, control plane, UI, agents, skills, memory, evals, gates, observability, git/worktree, deployment, tests, failure history | **FOLLOWED** | All thirteen. Headline: no DAG engine, no Prefect, no queue; execution is synchronous Python + `subprocess`. No memory/vector/RAG of any kind — sole runtime dep is `pyyaml` |

## Phase 1 — Reconcile current Factory vs north star

| # | Instruction | State | Evidence / reason |
|---|---|---|---|
| 1.1 | Classify every subsystem `KEEP\|EXTEND\|REFACTOR\|MOVE\|DELETE\|RESEARCH` | **FOLLOWED** | `RECONCILIATION.md` §3, ~22 concepts |
| 1.2 | Test: agents synthesize, deterministic code enforces | **FOLLOWED** | Confirmed — no LLM judge anywhere; every verdict is deterministic Python. `provider.py:11-13`: *"a provider never names its own verdict"* |
| 1.3 | Test: success is a positive assertion, not absence of exceptions | ⭐ **FOLLOWED, and it failed** | Six gates returned PASS over an absence, four with an empty evidence list. Fixed — `F94`, 15 tests |
| 1.4 | Test: `UNMEASURED != GREEN` | **FOLLOWED** | Holds in `contract.py`; the violations were at the *population* level, not the verdict level — see 1.3 |
| 1.5 | Test: version/lock behaviour for reproducibility | **FOLLOWED** | `TeamSpec.version` hashes config — and `F90` found it hashing a `repo` field nothing read |
| 1.6 | Test: higher autonomy needs evaluation/isolation/recovery first | **FOLLOWED** | This is the basis of the Rank-4+ deviation below |

## Phase 2 — Mine reference implementations

| # | Instruction | State | Evidence / reason |
|---|---|---|---|
| 2.1 | Read `REFERENCE_MINING.yaml` + `research/reference-implementations/` | **FOLLOWED** | |
| 2.2 | Mine Paperclip, SSSF, Inkwell | **FOLLOWED** | Three agents read **source**, not READMEs. Paperclip shallow-cloned (6,169 files); SSSF 21 files; Inkwell 24 |
| 2.3 | Invoke `reference-implementation-miner` | **SUBSTANCE** | Skill not installed; its procedure (license → architecture → per-feature → classify → provenance) was given to the agents directly |
| 2.4 | Classify `ADOPT_CONCEPT\|ADAPT\|EXPERIMENT\|REJECT` | **FOLLOWED** | All three; written up as `wiki/concepts/patterns/agent-control-plane-prior-art.md`, the one artefact with no in-repo home |
| 2.5 | Do not copy product identity, UI, branding, prompts, code | **FOLLOWED** | No code taken. All three MIT; obligations recorded |

## Phase 3 — Subscription-first research

| # | Instruction | State | Evidence / reason |
|---|---|---|---|
| 3.1 | No metered OpenAI/Anthropic research API | **FOLLOWED** | None used. Verified the pack requires none |
| 3.2 | Escalate repo evidence → web search → Claude Research | **FOLLOWED** | Everything was answerable at tiers 0–1 |
| 3.3 | Compile jobs into versioned prompts + `RESEARCH_QUEUE.md` | ⛔ **DEVIATED** | **No queue generated.** `agent-army-research/` already has 26 prompts, an A–E evidence-tier protocol, a hypothesis ledger and a graduation rule. A second queue competes with stronger machinery |
| 3.4 | Run Wave 0 (R25, R06A, R06B, R16A, RREF1) | ⛔ **DEVIATED** | **None run.** R06A ≈ `factory/bus.py` + `docs/agent-communication.md`; R06B ≈ `findings.d/` + `findings.py`; R07 ≈ `contract.py`; R25 ≈ `boot-prompts/`. RREF1 was mined directly. R16A is gated on *"numbers worth looking at"* |
| 3.5 | Do not claim programmatic Research launching | **FOLLOWED** | Stated as a human-triggered step throughout |

## Phase 4 — Execution surfaces

| # | Instruction | State | Evidence / reason |
|---|---|---|---|
| 4.1 | Choose `remote_control\|cloud_web\|either` per task | **NOT YET** | All work ran on one local surface |
| 4.2 | Attach the `execution:` metadata block to DAG tasks | **NOT YET** | No task carries it. Candidate for the session-router work |
| 4.3 | Collision rule — read-only, separate worktrees, or proven locking | ⭐ **FOLLOWED** | Every write task ran in its own worktree; `claims.py` provides `O_EXCL` locking. ⚠ The rule is *honoured by discipline, not enforced* — nothing allocates the worktree, which is the branch-conflict problem |

## Phase 5–7 — DAG, build order, design questions

| # | Instruction | State | Evidence / reason |
|---|---|---|---|
| 5.1 | Compile evidence + gaps into a DAG; parallelise independent work | **FOLLOWED** | SITREP's DAG; T1–T3 ran in parallel worktrees |
| 5.2 | Each task carries objective/inputs/surface/isolation/artifacts/checks/gate/edges/rollback | **PARTIAL** | Objective, artifacts, checks and gate yes; surface and rollback no |
| 6.1 | Build order: bootstrap → harden → console → comms → cognition → assembly → … | **FOLLOWED to item 2** | Items 1–2 (durable state, hardened evaluation) done. Item 3 (Console) deliberately not started — see below |
| 7.1 | Preserve the ten core design questions | **FOLLOWED** | Carried in `RECONCILIATION.md` and the boot prompts |
| 7A.1 | Maintain evidence-gated rank via `roadmap-rank-tracker` → `PROGRESS.yaml` | ⛔ **DEVIATED** | **No `PROGRESS.yaml`.** `factory/roadmap.py` + `board.py` already derive rank state from gate verdicts; a parallel YAML would be the hand-maintained twin |
| 7A.2 | Open a bounded commercial lane once Stage 1–2 are done | **DEVIATED** | Gated behind *one certified team*; the ledger is `0 PASS` |
| 7B.1 | Treat R06A communication as a priority experiment | **DEVIATED (for now)** | `README.md:96` — a second comms topology is unlocked by *a second team that needs to talk to the first*. There is not yet a first |
| 8.1 | Accumulate non-urgent questions in `HUMAN_QUESTIONS.md` | **NOT YET** | Not created. Questions were asked inline instead |

## Working rules

| Rule | State |
|---|---|
| No greenfield rewrite | **FOLLOWED** — nothing existing was replaced |
| Do not inflate agent count | **FOLLOWED** — 7 recon/mining agents, sized to independent areas |
| No recursive LLM management hierarchy | **FOLLOWED** |
| Do not equate activity with success | ⭐ **FOLLOWED** — stated repeatedly that 0 PASS is the headline |
| No optimizer may define its own promotion test | **FOLLOWED** — and found two paths where a graded party influences its own metric |
| Do not treat transcripts as the knowledge architecture | **FOLLOWED** — findings, boot prompts and the wiki all written |
| Prefer deterministic phases for known operations | **FOLLOWED** |
| Store durable state in the repo | **FOLLOWED** |
| Install skills per `INSTALL_SKILLS.md` | ⛔ **NOT DONE** — `.claude/skills` does not exist. The 13 pack skills were read and followed by hand, never installed |

## First-pass output contract (12 items)

All twelve were delivered in the SITREP. Items 5 and 7 (research jobs to prepare, exact queue plan)
were answered **"zero justified"** rather than with a queue — the deviation at 3.3/3.4.

---

## ⛔ The four deviations, in one place

1. **No `PROJECT_STATE.yaml`** — the state exists and is code-read; a second file rots.
2. **No research queue, no Wave 0 run** — `agent-army-research` already holds it with stronger epistemics.
3. **No `PROGRESS.yaml`** — `roadmap.py`/`board.py` derive rank from gate verdicts.
4. **Nothing built above Rank 3** — `README.md:96` gates it on one certified team; ledger is `0 PASS`.

## ⭐ And the one you should weigh yourself

The pack's `VISION.md` proposes an Organization Compiler, Org-IR, a Collective Cognition Fabric and
an Evolution Chamber. `agent-army-research/research/synthesis/W0-foundations.md` — **your own
research, dated the day before the pack was installed** — concludes that AOE *is* organisation-
oriented MAS, that the category name is taken twice in 2026, that **IMACS (`arXiv:2607.25446`) is
the organizational-compiler thesis, already published**, and that the novelty claim is *"refuted on
all four components"*. Its recommendation was to stop investing there.

**This session followed that evidence over the pack's plan.** That is a judgement, not a fact. If
you want the pack's programme built as written, say so and it will be — but it should be a decision
you make with the refutation in front of you, not a default.

## Not-yet items worth scheduling

- `HUMAN_QUESTIONS.md` (8.1) — cheap, and the right home for questions like the one above.
- Execution-surface metadata (4.1/4.2) — belongs with the session router.
- Installing the pack skills (`INSTALL_SKILLS.md`) — only worth doing for the ones that will
  actually be invoked; `registry.py` should decide which.
