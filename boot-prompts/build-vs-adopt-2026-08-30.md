# Boot — the adopt question is answered; go bound the loop

**Written:** 2026-08-29, late, after a six-lens `/prospect` pass on `docs/BUILD-VS-ADOPT-PROMPT.md`.
**Companion to** `run-the-loop-2026-08-30.md` (still right) and `execution-plane-2026-08-30.md`
(⚠ **its starred "adopt before you abstract" section is now falsified — see §1**).

---

## `next:` **Run one supervised lane and put the run in the corpus** — defer to `run-the-loop-2026-08-30.md`.

⛔ **CORRECTED 2026-08-29 ~21:40, after F78.** An earlier version of this file said `next:` was
*"RUN-01, agent-factory half"*. **That is now retired.** Do not do it.

`docs/findings.d/F78-the-unattended-verdict-is-about-the-other-repo.md` extends F77 from one gate to
four: **`cap`, `ceiling`, `concurrency` and `reaper` all grep `prefect-connectors`** — `_src`/`_grep`
resolve every path against `CONNECTORS` (`readiness.py:723-727`). **No agent-factory work moves any
of them**, so RUN-01 *and* RUN-02 were both accepted on verdicts they cannot shift.

**The live `next:` lives in `run-the-loop-2026-08-30.md` and currently reads:**

> **Run one supervised lane, and put the run in the corpus.**
> `python scripts/local_tracker.py --serve --port 8099`, launch the `certify` lane, watch it, answer
> it if it blocks. Done when gate `breadth` reads **2 cases** instead of *"1 case, 0 strata"*.

⭐ **This converges with §0 of the build-vs-adopt review rather than replacing it.** That review's
sequencing constraint was already *"nothing should be adopted before one connector is certified end
to end"* — `breadth FAIL — 1 case(s), 0 strata` and `certified NOT_RUN` are the same hole seen from
two sides. The re-led ticket is the cheapest move against it, and it is in this repo.

### What the build-vs-adopt pass settles, whatever you pick up

⛔ **Do NOT adopt LangGraph / CrewAI / AutoGen / OpenHands / SWE-agent / Aider.** Retired on
evidence, not taste. They cover **3 of 8** of our requirements; worktree isolation, lane claiming,
the persisted retry ledger, the event ledger and the verdict model are absent from every one, so you
build those either way. Two are disqualified outright:

- **AutoGen** README, verbatim: *"AutoGen is now in maintenance mode. It will not receive new
  features or enhancements and is community managed going forward."*
- **CrewAI**'s core abstraction *is* the topology R2 rejected — `role`/`goal`/`backstory`, and a
  hierarchical process that *"automatically assigns a manager to the defined crew."*
  `blueprints/orchestrator_team.yaml` opens `⛔ SUPERSEDED BY EVIDENCE` on a 180-configuration study.

⛔ **Do NOT start with an adoption ticket of any kind.** `CIP-05` (certify one connector) and
`BVA-01` (the dependency gate) gate all of them — both are in the ledger.

⚠ **And do not use gate movement as your definition of done in this repo without checking which
repository the gate reads first.** That is the whole lesson of F77/F78, and it is the second time in
two days that a plan was aimed at a verdict it could not move.

**Read first:** `docs/findings.d/F77-*.md` and `F78-*.md` (they rewrite the RUN sequence), then
`run-the-loop-2026-08-30.md`, then `docs/reviews/build-vs-adopt-2026-08-29.md` (491 lines) —
§0, §1, §4, §5.

---

## 1. ⚠ The correction this session produced — re-inherit it, do not re-derive it

`execution-plane-2026-08-30.md` contains a ⭐-starred section headed **"Adopt before you abstract"**
which argues that because `RepoDeployer` has zero callers, adopting a maintained runner *"gets the
interface AND the implementation."* **That sentence is false and has been corrected in place in that
file.** If you are reading an older copy, this supersedes it.

The reasoning that killed it, all measured:

| | |
|---|---|
| Frameworks cover | **3 of 8** requirements |
| Hand-rolled runner | **~370–510 new lines**, on top of **1,682 lines that already exist and work** |
| With the Claude Agent SDK | **~310–420 new lines** |
| LangGraph adaptation alone | **150–300 lines**, *plus* the framework, *plus* `langsmith` (a hosted telemetry client) as a **mandatory** transitive dep — it is the first entry of `langchain-core`'s `dependencies` array |

**The one thing worth adopting is the Claude Agent SDK** (MIT, `v0.2.148`, 2026-08-28, `windows-latest`
CI), and its cost is *negative*: `factory/deploy.py:230-234` already hard-codes `--max-turns`,
`--max-budget-usd`, `--output-format stream-json`, `--model` against an **undocumented, unversioned,
unpinned argv surface**. The SDK does not add a vendor coupling — it makes an existing invisible one
typed and pinnable. It has no verdict model, so it sits cleanly *below* `GreenContract`.

**Also corrected:** the zero-callers grep is right but its conclusion was wrong. Of `deploy.py`'s 265
lines, **140 are `AttemptLedger`** — a cap that survives restart. Every framework's budget control is
per-invocation and resets on the next call, **which is exactly the bug `AttemptLedger` was written to
fix.** "Unwired code is cheap to replace" is true of 86 lines and false of 140.

---

## 2. State, measured 2026-08-29 late — not remembered

```
$ python -m factory.launch
May I LEAVE it running, unattended?
  UNATTENDED-BLOCKED
    - cap          FAIL         a cap exists on a path that did not run
    - reaper       FAIL         no lease, timeout or reaper for dispatched work
    - ceiling      FAIL         no spend ceiling enforced before dispatch
    - concurrency  FAIL         concurrency is bounded per wave, not per stage dispatch
    - bounded      FAIL         no attempt cap on restart

May I TRUST what it produced?
  OUTPUT-UNCERTIFIED
    - suite        FAIL         21 failed, 409 passed, 2 xfailed (0:02:11)
    - certified    NOT_RUN      12 assertions have no instrument wired
    - corpus       FAIL         tamper-evident, but separation is not enforced
    - version      FAIL         9 dimensions absent from the version
    - breadth      FAIL         1 case(s), 0 strata — below any calibration threshold
```

**None of the five bounding gates has moved — and per F78, four of them cannot be moved from this
repo at all** (`cap`, `ceiling`, `concurrency`, `reaper` all grep `prefect-connectors`). Their
staying red says nothing about work done here. Use `breadth` and `certified` as the movable
verdicts instead; both are about this repo, and both are the same hole §3 of the review names.

**⭐ The 21 failures are NOT a regression — they are the sibling checkout.** Measured at the same
moment:

```
$ git -C ../prefect-connectors branch --show-current   → chore/artefact-homes
$ git -C ../prefect-connectors status --porcelain | wc -l   → 29
$ python -c "from factory.readiness import CONNECTORS; print((CONNECTORS/'tests'/'orchestrator'/'mutate_control_plane.py').is_file())"   → False
```

That missing file alone fails `test_mutation_anchors_still_match` and `test_live_probes`. **Do not
"fix" these.** Re-measure and quote the condition, or use `factory.launch` / `factory.readiness`,
which state their own basis.

**⚠ And the passing count moved inside one hour: 388 → 409, with no action of mine.** Another
session was adding tests in this checkout throughout. **Never quote a suite number without the
command and the sibling-repo condition beside it.**

**Ledger:** `.data/tasks.jsonl`, **185 events / 76 tickets — 53 open, 18 blocked, 3 abandoned, 2 done**
(after this pass added 5; measured 2026-08-29 late — it moved twice during this session as a
concurrent session worked, so re-measure rather than quote). The binding constraint on this project is finishing things, not choosing
components.

---

## 3. ⭐ The finding most likely to be lost

**The headline thesis was refuted at the level of representation and survives only at the level of
aggregation.** If nobody writes this down it will be re-derived wrongly, or worse, published wrongly.

`docs/BUILD-VS-ADOPT-PROMPT.md` closes by claiming UNMEASURABLE-as-first-class-verdict is not seen
"in any scorecard or data-quality product." **Six counter-examples, all verified at source:**

| Tool | The state |
|---|---|
| OpenSSF Scorecard | `InconclusiveResultScore = -1` — *"returned when no reliable information can be retrieved by a check"* |
| Soda Core | `CheckOutcome.NOT_EVALUATED` **and** `EXCLUDED` — two states for two different claims |
| datacontract-cli | `ResultEnum` = `passed, warning, failed, error, info, skipped, unknown` |
| Dagster | `EXECUTION_FAILED  # hit some exception` · `SKIPPED  # the check didn't execute` |
| W3C EARL 1.0 | `earl:CannotTell` — *"an undetermined outcome"* · `earl:NotTested` |
| XCCDF / NIST IR 7275 | `ERROR`, `UNKNOWN`, `NOT_CHECKED`, `NOT_APPLICABLE`, `NOT_SELECTED` |

**But every one throws it away at the aggregate.** Scorecard drops it from the denominator (10 of 18
inconclusive can still score 10.0/10). OHDSI computes `countPassed <- countTotal -
countOverallFailed`, so `notApplicable` and `isError` **round up to passed**. XCCDF scores `ERROR`
and `UNKNOWN` as 0.0 — identical to fail. Great Expectations computes
`unsuccessful = evaluated - successful` with `successful = sum(exp.success or False ...)`, so a
crashed instrument counts as a *failing* expectation and `None` coerces into that bucket. Grafana
ships a **"Set Normal state"** handler for No-Data. pytest greens `skipped`/`xfailed` by default.

> **The claim that survives, and it is the one to publish:** the representation problem is solved
> everywhere; **the aggregation problem is solved nowhere.** UNMEASURABLE must *survive aggregation
> as a refusal* — not dropped from the denominator, not counted as passed, not scored as failed, with
> no configuration path to defeat it. `factory/readiness.py:1176` keeps it in the denominator;
> `factory/contract.py:73-85` ranks `FAIL > UNMEASURABLE > PASS`.

**Corroboration, not competition:** Scorecard and `readiness.py` converged *independently* on the
same two sources of unmeasurability — an explicit "could not establish an instrument"
(`CreateInconclusiveResult` / `raise Unmeasurable`) and a caught runtime exception
(`CreateRuntimeErrorResult` / `except Exception → UNMEASURABLE`). Both refuse to read the second as a
failure. Cite that.

**Second finding, equally easy to lose — thesis 4 is TRIED-AND-FAILED prior art.**
"Spec-and-test as one artefact elicited from a non-technical stakeholder" **is BDD**, and Cucumber's
own creator published in 2014 that adopters *"completely missed out on the underlying practices"* and
used it *"uniquely as a testing tool. No collaboration."* Concordion's last release was 2023-07-16.
**BDD did not fail on format — it failed because the stakeholder does not fill it in**, an engineer
does it afterwards, and the artefact becomes a config file the client never read. **If CIP-07 fails,
that is how.** The only differentiator is already in the plan — *pre-fill from a live schema probe so
the client confirms rather than authors* — and it belongs on the critical path, not in the nice-to-have
column.

---

## 3b. Second thread, opened late: the operations UI

`docs/FACTORY-UI-PROMPT.md` (324 lines) replaces a 58-section UI brief. **Paul is testing it against
Claude Design as of 2026-08-29 late** — treat any output from that as a draft to assess, not a
decision taken.

⭐ **Why it matters to the `next:` line above: the UI's Phase 0 and the supervised-lane run are the
same work seen from two ends.** Phase 0 is `factory/events.py`, an append-only event ledger wired to
the path that actually launches agents (`local_tracker._launch_script()`, **not** `deploy.py`, which
has zero production callers). It has nothing to record until a real lane runs. So the one action in
`next:` unblocks three things at once: gate `breadth`, the first real certification, and the UI's
only honest data source.

**The three rules in that prompt that must survive contact with any design tool:**

1. **No single-number percentage may stand for a set containing an UNMEASURABLE.** The original brief
   specified `PASS RATE 81%` on the front page — that is the aggregation collapse §3 documents, in
   the one product whose thesis forbids it.
2. **Simulated data may never satisfy the acceptance test.** The test ends: *pointed at the factory
   as it stands today — 3 runs, 1 corpus case, 12 uninstrumented assertions — the UI must look
   conspicuously unfinished. If it renders as a healthy busy command centre, it is lying.*
3. **Stack is decided, not delegated:** extend `local_tracker.py` with vanilla JS over one SSE
   endpoint. There is no `package.json` anywhere in this repo; a node toolchain is a large ungated
   new surface while `BVA-01` is open.

⚠ **Collision:** `docs/design/session-ui-and-intake.html` ("Control Room & Intake", 35 KB) was
written by a concurrent session the same evening. **Read it before building either surface** or the
estate gets two command centres.

⛔ **My own recommendation, recorded so it is not silently lost:** Phase 0 is worth doing now and the
UI probably is not. Three recorded runs and one certified connector do not need a command centre;
they need a second certified connector. Build the event ledger and stop — it captures the only thing
that is unrecoverable, and the UI gets better the more history sits behind it.

---

## 4. NOT done — read this before believing anything is ready

- **The factory has never certified a connector.** `certified NOT_RUN — 12 assertions have no
  instrument wired`. `factory/live_probes.py` wires **A1 and A5 only**, and its docstring notes both
  are reachable *"with no credential and no network call."* A2, A3, A4, A6, A7, A8, A9, A10, A11, A12
  have never run against a live target. **Every migration cost in the review is priced against
  interfaces that have never carried traffic.** Nothing should be adopted before this changes.
- ✅ **Tickets ARE loaded** (corrected 2026-08-29 — an earlier draft of this prompt said they were
  not). `.data/tasks.jsonl` went 165 → 185 events. **Created:** `BVA-01` `771630bd` (dependency gate)
  · `BVA-02` `377b70f0` (filelock) · `BVA-04` `56546789` (ODCS) · `BVA-06` `c295ce8e` (adapter
  contract) · `BVA-07` `cd2a7aa5` (retitle the claim). **Three drafts were duplicates and became
  evidence on existing tickets instead:** `CIP-05` (certify a connector — now the gate on all
  adoption), `RUN-03` (the BUILD verdict + the runner pricing), `CIP-09`/`CIP-10` (already built
  upstream). **Check `CIP-05` and `BVA-01` before actioning any adoption.**
- ✅ **Everything from this session is committed and pushed** across `agent-factory` (`f32c69b`),
  `wiki` and `aldc-launchpad`. Nothing of mine is outstanding.
- ⛔ **No UI code was written.** `docs/FACTORY-UI-PROMPT.md` is a prompt, not an implementation,
  and its Phase 0 (`factory/events.py`) **does not exist**. Nothing in it has been built.
- ⛔ **No connector has been certified**, so the UI has no honest data source and the review's
  migration costs remain priced against interfaces that have never carried traffic.
- **No candidate was executed.** Every verdict rests on reading source, packaging metadata, CI
  matrices and release APIs. Two cheap executions would upgrade DOCUMENTED → OBSERVED and are named
  in §6.
- **The review's own weakest link:** `datacontract-cli` silently drops uncompilable rules
  (`create_checks.py`, 673 lines, **seven** `logger.warning(...) → return []` paths, and the file
  never imports `Run`). I verified this by reading source, **not by running it.** A 30-minute
  negative control settles it: declare a `type: text` rule and a model-level `nullValues` rule
  against an empty table, then read the JSON result.
- **The conceptual-literature lane is ~half searched** — metrology/GUM, MCAR-MAR-MNAR missing-data
  theory and medical "indeterminate" results were *refused rather than asserted* after IUPAC returned
  403. If the write-up goes public, that lane needs finishing.

---

## 5. Blocked on a human

| Item | What unblocks it |
|---|---|
| ~~Append the BVA tickets~~ | ✅ **Done 2026-08-29.** 5 created, 4 existing tickets given evidence. |
| Commit `docs/reviews/build-vs-adopt-2026-08-29.md` | Paul approves commits. **Stage by exact path.** |
| Wiki page for the aggregation finding | Paul's word; update an existing page rather than create. |
| Cortex / Port / Soundcheck result-state enums | A trial account each. ABSENT from public source, not from the product. |
| Whether `soda-core` v4 runs fully keyless | A Soda Cloud account. Matters — keyless Soda at 0.2 MB with a five-member `CheckOutcome` would be the most interesting adopt in the field. |
| Power BI Scanner API returning populated `datasetExpressions` | Fabric admin or service principal with `Tenant.Read.All`, **plus tenant metadata scanning confirmed ON**. |

---

## 6. Gotchas earned — each is an hour you do not have to lose

- **⛔ `gh api search/code` and `gh search code` are BLIND on this workstation.** Positive control:
  searching `InconclusiveResultScore repo:ossf/scorecard` — a string verified to exist — returned
  **0**, with no error. The token is a `gho_` OAuth token without code-search scope. **Every
  code-search zero is NOT-VISIBLE, not ABSENT.** Use `gh api repos/OWNER/REPO/contents/PATH` (proven
  working: 39 entries) or fetch raw files.
- **`WebFetch` is a DOCUMENTED-tier instrument even when pointed at source** — it returns a small
  model's *summary*. It gave a materially incomplete read of OHDSI's `summarizeResults.R` that `curl`
  + `cat` settled as fact. **Use `curl`/`gh` for any claim that will carry a verdict.**
- **`WebSearch` is near-useless here.** One probe confused "Great Expectations" the data-quality
  library with **a dating service** and reported its complaints. Lead generation only.
- **Line counts differ by ref.** Synthesiser vs lens disagreed every time — `create_checks.py` 673
  vs 996, Dagster `asset_check_execution_record.py` 334 vs 286, GE
  `expectation_validation_result.py` 846 vs 766 vs 1,087. Substance agreed every time. **Quote a line
  number only with its ref.**
- **Unauthenticated `api.github.com` rate-limits at ~60/hr** and returns HTTP 403 mid-sweep. `gh api`
  (authenticated, `russell94paul`) gives 5,000/hr.
- **`docs/BUILD-VS-ADOPT-PROMPT.md`'s size table was stale the day it was written.** All four figures.
  Measured at `17a6a5a`: `factory/` **9,227** across 40 files (not 8,886/38) · `tests/` **4,684**
  across 31 (not 3,873) · `docs/` **56,125** across 93 (not 54,232/89).
- **"304 tests passing" is three different numbers and none is reproducible without its condition** —
  301 `def test_` definitions, 388 then 409 executed within one hour, 304 from an unrecorded sibling
  state. The suite is currently **RED**.
- **`docs/reviews/external/verification.md:43` is now stale**: it records `tasks.py` as having no live
  callers. `TaskStore` is imported by `scripts/export_board.py:16` and `scripts/local_tracker.py:827`.
- **⚠ You are not alone in this checkout.** During this pass `agent-factory-25` modified five files
  and added four (`factory/context.py`, `factory/evidence.py`, `tests/test_context_pack.py`,
  `tests/test_evidence_classes.py`). **Stage by path. Never `git add -A`, never `git commit -a`.**

---

## 7. Where things live

| Path | What |
|---|---|
| `docs/reviews/build-vs-adopt-2026-08-29.md` | **This pass's output.** 491 lines. Ten verdicts, 8 draft tickets, 12 corrections, instrument log. |
| `docs/BUILD-VS-ADOPT-PROMPT.md` | The question that was run. Its Part 4 is `RECALLED/UNVERIFIED` and **six rows are now corrected** — see the review's §6. |
| `boot-prompts/execution-plane-2026-08-30.md` | Same workstream. Its ⭐ adopt section is **corrected in place**; the rest still stands. |
| `boot-prompts/run-the-loop-2026-08-30.md` | Leads with RUN-01…04. **Still right.** |
| `factory/contract.py` (115 ln) | The four verdicts. `FAIL > UNMEASURABLE > PASS`. The semantic core — nothing surveyed replaces it. |
| `factory/readiness.py` (1,200 ln, 27 gates) | Keeps UNMEASURABLE in the denominator — the surviving novelty. |
| `factory/connector_contract.py` (311 ln) | A1–A12. A7–A10 bodies are lines **189–264** = **76 lines**. |
| `factory/live_probes.py` | Wires A1 and A5 **only**, and says so. |
| `factory/deploy.py` (265 ln) | 140 ln `AttemptLedger` (keep) + 86 ln `RepoDeployer` (replaceable). Zero production callers; `tests/test_retry_context.py` uses it. |
| `factory/claims.py:200-247` | Should be `filelock` — `BVA-02`, the cleanest adopt in the repo. |
| `.data/tasks.jsonl` | 71 created / 5 closed / 18 blocked. Shared append-only — **another session may be writing.** |

---

## 8. If you do one optional thing beyond RUN-01

**`BVA-02` — replace `claims.py:200-247` with `tox-dev/filelock`.** Unlicense, **zero transitive
dependencies**, last release 3.32.4 (2026-08-23). It deletes ~48 lines whose Windows `EACCES`-vs-
`EEXIST` race the author's own comment records being bitten by — *"Twenty racing threads reproduce it
every time; two rarely do."* **A lock is not a judgement, so K2 does not apply** — it changes no
verdict semantics. `grep -rn "filelock"` returns nothing in this repo, and Part 4 has no locking row
at all, so the search never ran.

It is small, independent of RUN-01, and it is the direct answer to the source document's question 3:
*"what am I about to build that already exists and I clearly do not know about?"*

⚠ But `BVA-01` (a lockfile + a dependency gate) should land first if you are adding *any* dependency.
Measured now: `dependencies = ["pyyaml>=6.0"]`, **no lockfile of any kind, no `.github/`, no CI**, and
**none of the 27 gates measures a dependency.** The repo gates a corpus byte changing and does not
gate its grader's dependencies changing.
