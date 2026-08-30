# Divergence pass — the plan and the boot prompt, checked against the code

**Run:** 2026-08-29, in-repo, on `feat/readiness-generator` @ `4a8418f`.
⚠ **The store moved under this pass.** A parallel session committed `8509a37` mid-run, adding the
**OBS/X0 lane** (9 tickets). Counts below marked *(at `4a8418f`)* were true when measured and are
superseded by §"The store is live" at the end. Regenerate with `python scripts/export_board.py`
before quoting any of them.
**Method:** every load-bearing claim in the boot prompt and `docs/CLIENT-INTAKE-PLATFORM-PLAN.md`
re-derived from the filesystem or from a command, never from another document.
**Checked:** 22 claims. **Verdicts:** 13 CONFIRMED · 5 OUR DOC STALE · 2 REVIEWER STALE · 2 BASIS DEFECT.
**One open question closed:** the factory track is **unmodelled**, not independent (D-6).

Direction is reported for every miss, because the point of the pass is not "who was wrong" but
**which side to believe next time**.

---

## The four that change what we do

### D-1 · The dependency graph is authored, not derived — and the store's own field is dead
**BASIS DEFECT · highest impact in this pass**

| | |
|---|---|
| **CLAIM** | Boot: *"the Dependencies tab draws the DAG from the 18 real edges **in the ticket store**"*; *"the waves and critical path below are **computed, not assigned**"* |
| **SOURCE** | `boot-prompts/intake-platform-design-lock-2026-08-30.md` §3, §Parallelism |
| **REALITY** | The 18 edges are real and the waves ARE computed from them — but the edges live in `docs/board/ticket-detail.json` under `"dep"`, which that file's own header calls **"authored prose per ticket"**. The task store's `blocked_by` field is `[]` for **all 33 CIP tickets**, and `scripts/build_board_artifact.py:86` reads `d.get("dep", [])` from the authored file. `t["blocked_by"]` is **never read**. |
| **VERIFIED_AT** | `scripts/build_board_artifact.py:86`; `docs/board/ticket-detail.json`; `python scripts/export_board.py` → 55 tasks, every CIP `blocked_by: []` |
| **VERDICT** | **OUR DOC STALE — in the direction that matters.** Not "computed from the store"; hand-authored beside it. |
| **IMPACT** | Three things follow. (1) The constraint *"the board mirrors, never owns"* is **violated by the roadmap itself** — the DAG is the one thing the board owns outright, and it is the thing the whole schedule rests on. (2) `blocked_by` is a supported, populated, never-read field: **this estate's signature defect — written and unwired — found a fourth time, in the board pipeline built to track the other three.** (3) The boot's framing that only the *factory* track lacks edges is wrong; **no** track has edges in the store. |

**Action:** either write the 18 edges into the store and have the builder read `blocked_by` (making
"computed" true), or delete the "computed, not assigned" language and label the DAG **ASSUMED**.
Do not leave it claiming a provenance it does not have.

---

### D-2 · D5 was delivered. The boot says twice that it was not.
**OUR DOC STALE**

| | |
|---|---|
| **CLAIM** | Boot: *"D0–D4 delivered; **D5 (what it could not judge) missing**"* and, in Status, *"❌ **D5 was never delivered** — nobody has said what the review could not judge."* |
| **REALITY** | `docs/reviews/external/deepseek.md:528` — `# D5 — What I Could Not Judge`, a **7-row table** (Question / Why / What would settle it) plus a closing "single file that would most improve my answer" note. It runs to the file's last line, 541. |
| **VERIFIED_AT** | `docs/reviews/external/deepseek.md:528-541` |
| **VERDICT** | **OUR DOC STALE.** The reviewer did the work; our handoff denies it. |
| **IMPACT** | A whole deliverable was about to be re-commissioned. Worse, D5 is the section that names **CIP-24** (`CLAUDE_CODE_SESSION_NAME` never asserted) and the **suite-fingerprint instability** behind the 10/9/10 flapping — open questions we would have paid to rediscover. Two of D5's seven rows are already tickets; the other five are not. |

**Action:** strike both D5 lines from the boot; triage D5's five unticketed rows.

---

### D-3 · The external reviewer read 422 lines of a 2,422-line decision record
**REVIEWER STALE — and this is the mechanism behind the one known bad call**

| | |
|---|---|
| **CLAIM** | Reviewer: *"`docs/research/SYNTHESIS.md` (already read — **422 lines**) is the decision record."* |
| **REALITY** | `wc -l docs/research/SYNTHESIS.md` → **2,422**. The reviewer read, or was served, roughly **17%** of it — and reported the figure as if complete. |
| **VERIFIED_AT** | `wc -l docs/research/SYNTHESIS.md`; `docs/reviews/external/deepseek.md:541` |
| **VERDICT** | **REVIEWER TRUNCATED**, undisclosed. |
| **IMPACT** | This is the **root cause of the one known-bad finding**, not a second unrelated slip. The boot already records that the reviewer called `g_version_hash_is_complete` a live defect six days after `13e746e` fixed it, and blamed "it had read SYNTHESIS.md, which describes the pre-fix state". Both are the same defect: **it read a truncated SYNTHESIS and did not know it had.** That upgrades the lesson from "check which side is stale" into a rule with teeth: **an external pass must state the line count of every file it read, and we must check those counts before believing a word of it.** A reviewer that silently reads 17% of the decision record and reports confidently is indistinguishable from one that read all of it. |

**Action:** add "state the line count of every file you read" to `docs/EXTERNAL-REVIEW-PROMPT.md`;
re-check any deepseek finding that leans on SYNTHESIS beyond line 422.

---

### D-4 · The plan's centrepiece number is an unsourced projection from another domain, carrying no basis label
**BASIS DEFECT**

| | |
|---|---|
| **CLAIM** | Plan: *"A well-designed questionnaire … will yield **70–80%** of the ontology automatically; a generic … questionnaire will yield **30–40%**"* — called *"a 2× difference in spec completeness"* and *"the single highest-leverage claim across all four corpora"*. Boot escalates it: *"the single highest-leverage number in the whole plan … **spend disproportionate care there and hurry elsewhere**."* |
| **SOURCE** | `docs/CLIENT-INTAKE-PLATFORM-PLAN.md:58-59`, repeated at `:161`, `:192`, `:270` |
| **REALITY** | The quote is **verbatim accurate** — `ALDC Ontology AutoGeneration Assessment.md:18`. But at source it sits in the **Executive Summary of a forward-looking feasibility assessment** (*"Is feasible in 8–12 weeks for a 1.0 (beta) release"*), carries **no citation, no study, no dataset**, and describes **ontology extraction from stakeholder interviews for a food-waste / circular-economy domain** (FoodMesh, Food Banks Canada, CPMA) — not connector intake specs. It is a projection the document makes, not a result it reports. |
| **VERIFIED_AT** | source `:18`, `:111`, `:215`; provenance `:1-20`. Plan cites the path at `:269` — the real path **doubles the directory** (`26-05 Ontology Research/26-05 Ontology Research/`). |
| **VERDICT** | **BASIS DEFECT.** Quote accurate; **basis absent**. True basis: `EXTERNAL / ASSUMED — unsourced projection, different domain`. |
| **IMPACT** | The plan labels its basis honestly in §10 for three *other* claims (form completion `ASSUMED`, RMRR transfer `DERIVED`, effort `NOT-SUPPLIED`) — and leaves **the one number it calls highest-leverage** unlabelled. That breaks the plan's own §285 rule (*"A vendor claim is never a design premise"*) and the global rule *"Every published figure carries its basis"*. The scheduling consequence is live: the boot spends the critical path on CIP-07→08→10 **because of this number**. |

**This is an unapplied convention, not a missing one.** `docs/specs/control-room.md` §8 is a
seven-row **basis register** — every claim carrying `MEASURED` / `OBSERVED` / `BET` / `REASONED` /
`DERIVED` **plus a "how it dies" column** naming the observation that would kill it. It even labels
its own centrepiece honestly (*"A UI makes the operator faster — `BET`"*). So the estate already
practises exactly the discipline D-4 asks for, at a higher standard than the global rule requires,
one directory away from the plan that omitted it — and the plan cites neither that file nor its
format (D-6). **Adopt §8's table wholesale for the plan, including the "how it dies" column**; for
the 70–80% figure the answer to *how it dies* is already written as CIP-19.

**What survives:** the *design guidance* is sound independent of the figure — targeting entity
types, relationships, roles and decision gates beats "tell us about your work", and each question
mapping to a check (CIP-08) is right on its own merits. **Keep the questionnaire work; drop the 2×.**
Do not quote 70–80% to a client, and do not let it order the roadmap by itself.

---

### D-5 · A branch of real work exists that the handoff never mentions — and it is the only place an instrument is actually wired
**OUR DOC STALE · found because Paul asked whether we were on the newest branch**

| | |
|---|---|
| **CLAIM** | Boot: all work is on `feat/readiness-generator`; *"❌ **No ticket has been started.** Every one is `todo`."* The boot names no other branch. |
| **REALITY** | `trial/wave0-rescue` @ `6872aee` (2026-08-29 12:59) carries **1,151 insertions across 6 new files** that are **not** on `feat/readiness-generator`: `factory/live_probes.py` (256), `scripts/mutate_readiness_probes.py` (240), and three test files (492). Its message: *"A1/A5 wired to a real instrument, plus three RED gates … Rescued from an uncommitted scratchpad worktree before it was cleaned up."* |
| **VERIFIED_AT** | `git rev-list --count feat/readiness-generator..trial/wave0-rescue` → **1**; reverse → **22**. `git show --stat 6872aee`. Both refs fetched and current. |
| **VERDICT** | **OUR DOC STALE.** `feat/readiness-generator` *is* the newest branch and the right one to work on — it is 22 commits ahead — but it is **not a superset**. One commit of substantive work sits outside it, unmentioned. |
| **IMPACT** | Three reasons this is not a footnote. (1) **It is the estate's only counter-example to its own signature defect.** Everything in D-1 and rows 8–11 below is *written and unwired*; `live_probes.py` is the one thing that actually **wires** an assertion to a real instrument — A1 constructs the real connector classes, A5 shells out to the real pytest — with every other verb left inheriting `Probes._refuse` **on purpose, so `UNMEASURABLE` cannot quietly become `PASS`**. That is precisely the discipline the plan's gates are supposed to encode. (2) **It is deliberately RED — 21 failures, all inside its three new test files**, because the author made the mutation anchors *fail* rather than `skip` (*"A pytest.skip reads as green"*). Merging it therefore **breaks the clean `304 passed`** that row 6 confirms, by design. That is a real decision, and nobody has been asked to make it. (3) It was *"rescued from an uncommitted scratchpad worktree before it was cleaned up"* — this work has **already come within one cleanup of being lost once**, and it is currently preserved only by a branch no handoff names. |

**Action:** decide explicitly — merge it and accept a RED suite with a written reason, or leave it
parked and **name it in the boot prompt** so the next session cannot lose it. Do not let it stay
invisible. → this is a decision for §2 (Lock the design), not a cleanup.

---

### D-6 · Six specs, 91 KB, referenced by neither the plan nor the boot — and they contain the acceptance gates for the 13 tickets that have none
**BASIS DEFECT · closes the boot's own open question**

*Surfaced by a relayed note from a parallel session, not by this pass. Worth recording how it
arrived: without it this session would have re-specified a UI whose shape was decided days ago.*

| | |
|---|---|
| **CLAIM** | Boot §3: *"the **factory track has no dependency edges at all** (all 13 are wave 0), which is **either true or unmodelled**. Decide which."* |
| **REALITY** | **Unmodelled — decisively.** The 13 factory tickets have no edges because they have **no `detail` entry at all**: `CIP-21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35` are absent from `ticket-detail.json`. They carry no `why`, no acceptance criterion, no effort and no `dep`, and render on the board under the builder's fallback string *"No acceptance criterion recorded."* The 20 platform tickets all have entries; the 13 factory ones have none. The wave-0 flatness was never a finding about independence — it is the shadow of an empty file section. |
| **AND** | The detail is not missing from the estate — only from the tickets. `docs/specs/control-room.md` §5 already specifies **Slice 0 = CIP-24** (*"Assert `CLAUDE_CODE_SESSION_NAME` reaches the spawned process"*) **with its gate** (*"a test that spawns through the real launcher and reads the name back out of the registry"*), and **Slice 1 = CIP-23** (*"surface every `blocked` job's `needs` in one merged queue"*) **with a fire-drill gate and the only measured before-number in the spec** (*"4 sat all day"* → target under a minute). §5's governing rule is *"**A slice with no gate is not a slice**"* — and these tickets shipped as exactly that. |
| **VERIFIED_AT** | `ticket-detail.json` → 20 entries, all `CIP-01…20`; `build_board_artifact.py` fallback string; `docs/specs/control-room.md:293-312`, `:289`. Reference check: `architecture-v0`, `client-intake-portal`, `control-room`, `product-end-state`, `ui-future-features`, `terminal-configuration` → **0 references** from `CLIENT-INTAKE-PLATFORM-PLAN.md` or any boot prompt. `control-room.md` is cited only by prompt scaffolding and R13/R14/R15 evidence packs. |
| **VERDICT** | **BASIS DEFECT.** Not absent knowledge — **unwired knowledge**, the fifth instance. D-1 found a dead field; this finds six dead documents. |
| **IMPACT** | (1) The boot's open question is closed: **do not schedule the factory track as genuinely parallel** — it is unscheduled, which looks identical on a DAG and is not. (2) The fix is **harvest, not authorship**: at least CIP-23 and CIP-24 already have acceptance gates written, one directory away. (3) `control-room.md` §7 (*What we refuse to build* — seven refusals, including *no batch approval of secrets*, *no cache that can show yesterday's state*, *no live-terminal grid before §6 passes*) is a **finished refusal list for the design lock**, and §2.4 is titled *"Declared but not executed — the gap the vision turns on"*, i.e. this estate had already named its own signature defect before the external review rediscovered it. |

**Action:** for §2 (Lock the design), harvest `docs/specs/` rather than authoring — §7 becomes the
refusal register, §5's gates become the acceptance criteria for CIP-23/24, §8 becomes the basis
register's format. Then make the plan **cite** the specs, so the next pass cannot miss them.

---

## Confirmed — build on these, do not re-verify

| # | Claim | Verified by | Verdict |
|---|---|---|---|
| 1 | 55 tasks, 33 CIP (20 platform + 13 factory) | `python scripts/export_board.py` → `55 tasks`; families CIP 33 / AB 19 / other 3 | CONFIRMED |
| 2 | 18 dependency edges | counted from `ticket-detail.json` `dep` | CONFIRMED *(source wrong — D-1)* |
| 3 | Waves 0–9 exactly as the boot lists | recomputed longest-path independently; matched row for row | CONFIRMED |
| 4 | Critical path 10 deep, CIP-03→04→07→08→10→11→15→18→19→20 | recomputed | CONFIRMED |
| 5 | All 13 factory tickets wave 0, none on critical path | no `detail` entry exists for CIP-21…35, so no edges | CONFIRMED *(unmodelled, not measured — D-1)* |
| 6 | 304 tests pass | `python -m pytest` → `304 passed in 62.51s` | CONFIRMED |
| 7 | certify A1–A12 PASS, labelled REPLAYED | `python -m factory.certify blueprints/windsorai_client_a.yaml --calibrate` → `PASS (PASS=12)` + `REPLAYED, not a live measurement` | CONFIRMED |
| 8 | `RepoDeployer` has no caller outside its file | `grep -rn RepoDeployer` → `factory/deploy.py:188` + `tests/test_retry_context.py` only | CONFIRMED |
| 9 | `deploy.py` imported only by a test | `tests/test_retry_context.py:15,155` only | CONFIRMED |
| 10 | `metrics.py`, `evals.py` reach production only via `demo.py`; nothing imports `demo.py` | importers are `demo.py` + own tests; `demo` has **zero** importers | CONFIRMED |
| 11 | `blueprint.py` `TeamSpec`/`AgentSpec` unexecuted | only non-test importer is `deploy.py:21` — itself unwired, so transitively dead | CONFIRMED |
| 12 | CIP-22 rightly rejected — `claim()` already atomic | `factory/claims.py` — check and write share one `with _exclusive():` | CONFIRMED |
| 13 | CIP-33 rightly rejected — `ABANDONED` already declared | `factory/runs.py:41`; `factory/tasks.py:20-21` (`_TERMINAL`) | CONFIRMED |
| 14 | `main` is a skeleton | `git ls-tree -r --name-only main \| wc -l` → **18**; `git rev-list --count main..HEAD` → **165** | CONFIRMED |
| 15 | Isolation weakness still described on the public repo | `blueprints/windsorai_client_a.yaml:54-57` — *"One ALDC Windsor key returns EVERY client's accounts — 45 of them"* | CONFIRMED |
| 16 | 18 research passes, 19 unabsorbed conclusions | 18 distinct `R*` (R9 absent); AB-01…AB-19 | CONFIRMED |
| 17 | `g_version_hash_is_complete` fixed before the review called it broken | `13e746e`, 2026-08-23; reviewer's pass later | CONFIRMED *(cause now known — D-3)* |

---

## Also stale, minor

- **`tasks.py` is no longer unwired.** The boot inherits the review's *"`tasks.py`, `metrics.py` and
  `evals.py` are imported only by `demo.py`"*. `tasks.py` now has a real non-test caller —
  `scripts/export_board.py:16` — added by `d79cef8`. **Our doc stale in the good direction**: the
  board work wired it. `metrics.py` and `evals.py` remain unwired.
- **Open decision 1 is already decided.** The boot asks *"Push the redaction? It is committed
  locally and unpushed."* `git rev-list --count personal/feat/readiness-generator..HEAD` → **0**.
  Nothing is unpushed, and the boot's own status block already says "Redaction pushed". The decision
  block contradicts the status block in the same file. **Drop it.**
- **Corpus path wrong in the plan** (`:269`) — the real directory is doubled. One-line fix.

---

## What this pass could not judge

Stated explicitly, because D-2 is what happens when this section is skipped.

| Question | Why | What would settle it |
|---|---|---|
| Whether the 18 authored edges are the *right* edges | I verified they exist and that the waves follow from them. I did not re-derive whether CIP-15 truly needs CIP-11, etc. | A read of each ticket's `why` against its `dep`, by whoever will do the work |
| ~~Whether the 13 factory tickets are genuinely independent~~ | **CLOSED by D-6** — they have no `detail` entry at all, so no edges, no gate, no `why`. Unmodelled, not independent. | *Answered.* Harvest gates from `docs/specs/`, starting with control-room §5 for CIP-23/24 |
| Whether 70–80% is *directionally* right for intake specs | No ALDC measurement exists, in this repo or the corpus | CIP-19's pre/post test — which is exactly what it is for |
| Whether the remaining deepseek findings survive the truncation in D-3 | I checked the load-bearing ones named in the boot, not all 15 | Re-run the citations against full SYNTHESIS |

---

## The store is live — and this pass closes two of its newest tickets

`8509a37` ("a third lane for what gets noticed in flight") landed **while this pass was running**,
adding the **OBS / X0 lane**. Regenerated: **64 tasks** — CIP 33 · AB 19 · **OBS 9** · other 3
(`python scripts/export_board.py`). Every count in this document written before that commit said 55.
That is not an error in either document; it is the cost of a live store and a long pass, and it is
the reason every figure here names the command that regenerates it.

**Two OBS tickets are answered by the work above. Both should be closed in writing, the way CIP-22
and CIP-33 were — a written reject is as terminal as a build.**

| Ticket | Its question | This pass |
|---|---|---|
| **OBS-04** — *"The factory track has no dependency edges at all — true, or unmodelled?"* | the boot's open question, promoted to a ticket | **ANSWERED: unmodelled** (D-6). The 13 have no `detail` entry at all — no `why`, no gate, no effort, no `dep`. Not independence; an empty file section. |
| **OBS-05** — *"D5 was never delivered — nobody has said what the external review could not judge"* | assumes D5 is missing | **REFUTED (D-2).** D5 is delivered: `deepseek.md:528-541`, a 7-row table. **The ticket rests on a false premise and should be rejected, not worked.** Replace it with the real remainder: five of D5's seven rows are not yet tickets. |

**A third needs re-basing, not closing:**

- **OBS-08** — *"`main` is **157+** commits behind"*. Measured now: **166**
  (`git rev-list --count main..HEAD`), and it moved 165 → 166 *during this session*. A hardcoded
  count in a ticket title re-rots on every commit, invisibly, because the number still looks
  authoritative. **Retitle it without the figure** and let the ticket body carry the command.

**And one this pass can retire as already-built:**

- **OBS-03** — *"UI tickets must be wire, not build — control-room.md already specs the slices."*
  Independently reached as D-6 here, and it is stronger than "the spec exists": **the UI also
  already runs.** `python scripts/local_tracker.py --serve` is a working
  `http.server` surface whose handler **re-measures on every request** — `local_tracker.py:2321`,
  *"Re-measure per request. Slower than serving a file, and the entire reason to serve."* Its
  docstring states the discipline directly: *"A tracker that can quietly show yesterday's state is
  the drift this whole project exists to remove."* `OBSERVED` in source; the serve path was
  exercised by a parallel session, not by me — I read the handler, I did not bind the port.
  **This is the estate's second counter-example to its own signature defect** (the first being
  `live_probes.py`, D-5) — and it is more than wired, it is a **refusal enforced in code**:
  control-room §7 refuses *"a cache that can quietly show yesterday's state"*, and the one cache
  the tracker permits (the `suite` gate, 97.6% of page load) is admitted only under the rule
  *"its headline carries its own age in the same string as its number"* — `"147 passed (cached,
  last run 4m ago)"`. A refusal that is actually implemented, not just declared.

  **Consequence for step 6:** the board artifact is *not* the only surface, and it is the weaker
  one — it replays a build-time snapshot where the tracker re-measures. Do not spec a second UI.
  The open question is not *what to build* but **which surface owns which claim**, and that is a
  §2 decision.
