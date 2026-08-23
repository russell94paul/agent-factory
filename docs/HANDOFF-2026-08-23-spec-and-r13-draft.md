# Context for the next session — the technical/business spec, three findings, and a blocked R13 repair

**Paste this whole file to that session before it starts.** Written 2026-08-23 by the session that
produced `docs/specs/agent-factory-technical-and-business-spec.md`.

---

## ⚠ First: this work is on a branch, and it was based on a stale one. Check before you build.

Everything below is on **`claude/agent-factory-architecture-doc-by7il6`**, head **`5945849`**,
pushed. Four commits ahead of `origin/feat/readiness-generator` @ `8010676`, which it is based on.

⚠ **That branch started life pointing at `main` — the 87-commit-stale skeleton.** It was reset onto
`feat/readiness-generator` at the start of the session, because a spec written against the skeleton
would have described a repo that no longer exists. If you branch from `main` you will repeat that.

## ⛔ The blocker. Read this before planning anything about R13.

**A large amount of work exists only on the operator's machine and has never been pushed.** This
session was handed context describing it and could reach none of it. Verified, not assumed:

```
git cat-file -t 74af1ae                     -> fatal: Not a valid object name
git rev-parse origin/feat/readiness-generator -> 8010676   (unchanged)

MISSING  docs/research/R13-architecture-and-ui-survey.md
MISSING  docs/research/answers/R13-answer-architecture-and-ui-survey.md
MISSING  docs/research/R14*.md   R15*.md   scripts/build_r13_pack.py
SYNTHESIS.md ends at §12 — there is no §13 or §14
```

**Do not attempt the R13 repair until `feat/readiness-generator` is pushed.** A repair cannot be
written against a prompt and an answer nobody can read, and the likeliest failure is re-deriving
conclusions that already exist in `SYNTHESIS.md` §14 and paying for them twice.

## What was delivered, and what it is for

**`docs/specs/agent-factory-technical-and-business-spec.md`** (626 lines) — the technical and
business baseline, written to be attached to a deep-research prompt. Frozen-baseline discipline,
same as `agent-factory-concept-inventory.md` and `ui-surface-inventory.md`: our own position stated
in full *before* looking outward, so an answer comes back as a diff rather than a survey. Every
figure carries `[M]`/`[D]`/`[R]`/`[A]` and names its instrument.

Measured fresh for it, from the repos rather than from prose: 24 client directories, 139 connection
configs, 739 extraction templates, 186 warehouse views, 104 reporting views; `core_api` 140 files /
30,460 LOC / 21 routers; `eclipse` 239 files / 22,715 LOC / 18 coreAPI domains.

⚠ **739 templates is the surface, not 739 units of work.** How many are live is unmeasured. The
spec says so; do not let it travel without the caveat.

## ⛔ There are now two R13s. One of them is this session's, and it is parked.

This session wrote a research prompt as "R13", not knowing the number was taken. **The collision is
not cosmetic**, and it was measured rather than reasoned about:

```
files present : ['R13-architecture-and-ui-survey.md', 'R13-platform-and-manufacturing.md']
dispatch sees : {'R13': 'R13-architecture-and-ui-survey.md'}
DROPPED       : ['R13-platform-and-manufacturing.md']
```

`dispatch.prompts()` keys by R-number over a **sorted** glob with `setdefault`, so the alphabetically
earlier file wins and the other vanishes — no status, no answer, never listed as unsent. ⭐ **That is
the failure `dispatch.py` exists to catch, occurring inside the instrument built to catch it.**

**Now parked at `docs/research/DRAFT-platform-and-manufacturing-UNNUMBERED.md`** — renamed out of
the `R[0-9]*` glob, where it is inert and visible rather than live and invisible. Deliberately **not
renumbered** (R14 and R15 are taken and this session could not see what else is) and **not deleted**.

**Before reusing any of it, diff it against R13 run 1 and its answer.** Most of its Part 5 (E1–E8)
is UI territory run 1 already answered. Its Part 4 (D1–D5 — versioned agent spec, content-addressed
prompts, a registry, cross-repo targeting) **may** be genuinely uncovered; nobody has checked.

## Three findings. Two fixed, one deliberately not.

| | State |
|---|---|
| **[[F76]]** version gate | **FIXED** in `factory/readiness.py` |
| **[[F77]]** latency baseline | **OPEN** — design change, named in CHANGES |
| **[[F75]]** corpus hash | **OPEN, deliberately** — see below |

**F76 — the version gate could only ever report zero.** `g_version_hash_is_complete` matched
`rf"\x08{d}\x08"` — two literal BACKSPACE bytes, where `\b` word-boundaries were intended. In an
f-string `\b` *is* the backspace escape. The pattern could never match, so the gate returned
`0 of 15` unconditionally. True figure is **6 of 15**: `prompt, model, effort, tools, max_turns,
budget_usd` are present; nine are absent *as fields*. The verdict does not move — it FAILs either
way — only the number becomes honest.

⭐ **It is the self-matching evaluator probe with the sign flipped.** That one could only ever pass;
this one could only ever fail. **A gate that cannot pass has stopped measuring just as completely**,
and it is harder to catch, because a red gate on unfinished work looks like the truth — nobody
re-derives a number that already agrees with them. The `0 of 15` had travelled into the specs, two
research prompts and the wiki as `[M]`.

Corrected in the **living** documents only (`architecture-v0.md`, `ui-surface-inventory.md`, the new
spec). **`R8` and `R10` still say `0 of 15` on purpose** — they are dispatched prompts and are the
record of what was actually asked; editing them would falsify it. F76's AFFECTS carries the list.

⚠ **The `version` gate belongs to no lane at all.** It appears in none of the five lanes' gate lists
in `lanes.py`, so nobody was assigned to look at it and nobody did. That is why F76 survived.

**F75 — the corpus hash was pinned against Windows line endings, and it is left broken on purpose.**
`MANIFEST.sha256` pins `c3fbfed8…`; the bytes git stores hash to `c5eb1cb9…`. The manifest was
pinned from a Windows working tree after autocrlf expanded LF to CRLF. Both files landed in one
commit and neither has moved since, so **the tamper-evidence mechanism has never verified
successfully off Windows.**

Not merely a red gate — `tests/test_connector_contract.py` imports a module calling `corpus.load()`
at **module scope**, so pytest **aborts at collection**:

```
as committed                                1 collection error,  7 failed,  98 passed
manifest re-pinned to the bytes git stores                       1 failed, 134 passed
```

**36 tests fail or never run because of a line-ending conversion.** ⛔ **Left unfixed deliberately** —
the repo's own error message says a re-pin is a deliberate act that states its reason, so it is the
operator's call, not a tidy-up. The discriminating test is in the finding.

⭐ **The consequence is architectural.** T1/T2 in `architecture-v0.md` put agents in containers. A
containerised agent reads the corpus as tampered and refuses to certify — correctly, by its own
rules, for a reason that is not about the corpus. **The trust boundary certification rests on does
not survive the move to the environment we propose running agents in**, and CI on `ubuntu-latest`
could never have run this suite.

**F77 — the tracker latency target is built on the wrong model of the workload.** The handoff's
first three facts check out: the loop is serial (`readiness.py:1007`), probes are per-gate, the
server is `socketserver.TCPServer` (`local_tracker.py:1395`, single-threaded — hence two concurrent
requests returning empty). **The `8-wide pool → 1.2 s` projection does not.**

Gate `suite` shells out to a **full `python -m pytest` subprocess** (`timeout=300`). It is not an
I/O-bound probe; it is one indivisible unit no pool can subdivide.

```
per-gate timing, all 30 gates       total 0.53 s
  suite                             0.43 s  = 81.8% of total
  the other 28 gates combined       0.01 s  =  1.9%
```

⚠ **That 0.43 s flatters it** — pytest aborts at collection here under F75, so the gate is timing a
crash. With collection working: **4.68 s, reproducible over two runs.**

```
handoff model   30 uniform independent probes, 8-wide  -> 9.3/8 = 1.16 s
actual shape    one ~4.7 s subprocess + the rest       -> floor = 4.7 s at ANY width
```

⭐ **Parallel speedup floors at the slowest single task, not total÷width.** ~4× out, and unreachable
by concurrency at any pool width. **The fix is architectural, not concurrency**: take the suite out
of the request path, cache it against the git SHA of `tests/` and `factory/`, and render it with its
age attached — which the estate's own *"a cached figure carries its age in the same string"* rule
already permits.

⚠ **Re-measure on the operator's machine before quoting a ratio.** 9.3 s is from there; these are
from a Linux container, and per [[F72]] the gate mix differs by cwd and platform. What is
platform-independent is the *shape*.

## The standing recommendation on "should we write a new research prompt"

**No — a follow-up in the existing R13 thread, scoped to one item.** Of the three "go deeper" items
in the R13 run-2 handoff:

1. **Migration against the four real surfaces** — the only genuine research need, and not a new
   question: it is run 1's question re-asked with the attachment actually read. Use the R8 pattern —
   ship the generated pack, state *"where the pack and the prompt disagree, the pack wins."*
2. **Latency** — ⛔ **closed by measurement, remove from scope.** See F77. Dispatching it would buy
   thread-pool and async-I/O advice that is correct in general and worth near zero here.
3. **Non-engineer vs VS Code** — ⛔ **a decision, not a research question.** No external literature
   resolves whether *our* approver has VS Code open, and the approval-plane question was already
   established to have essentially no public literature (below).

**A new numbered prompt is justified only if** the D1–D5 manufacturing material turns out to be
uncovered by run 1. That is checkable, not arguable — run the diff first.

## ⭐ The most transferable thing this session learned: simulate the responder before dispatching

Three subagents reviewed the prompt — an independent writer working blind from the spec, an
adversarial reviewer, and one **simulating the target model answering the fence**. The simulation
was worth more than both reviews, and the mechanism is reusable for every future pass.

Told to play the target honestly (*it skims; it weights beginning and end; it drifts toward
validating the asker*) and then to break character, it reported what it had skimmed, which passages
pulled it toward agreeing, and — the valuable part — **which questions it had bluffed**:

> **Six of fourteen questions have essentially no public literature**, and it returned confident,
> sourceless prose for every one, *in the same shape as the well-evidenced ones.*

Absent: the approval plane, non-engineer approval, cost-per-outcome, fast-and-honest consoles, the
embedded terminal, cross-repo targeting. Present: agent identity/versioning, guardrails, OTel GenAI
status, task packaging, warehouse rollback.

Three derived rules, all now in the draft prompt and worth keeping in any successor:

- **Demand an evidence class before the prose** — `EVIDENCE: STRONG / THIN / ABSENT` opening every
  answer, with ABSENT capped at three sentences plus an experiment design. Grade those lines
  *first*, before reading anything: a question predicted ABSENT that returns STRONG is either the
  pass earning itself or confabulation, and the named sources settle it in a minute.
- **Attack-this-first material must not sit mid-prompt.** Three such points were skipped entirely.
- **Any "tell us if we are wrong" framing that makes agreeing the cheap, citable move will be
  taken.** Three exact passages were identified doing this.

⚠ It also answered **"moderate effort"** — the exact adjective-instead-of-a-figure failure the
prompt explicitly forbids. Effort must be demanded in engineer-days and checked in a closing
self-audit.

## Gotchas found the hard way

- **`git mv` out of a glob is a real containment tool.** Renaming the duplicate prompt out of
  `R[0-9]*` made it inert without deleting it or guessing a free number.
- **A subagent's factual claims need checking.** The reviewer reported *"`AgentSpec` is referenced
  only from `tests/test_blueprint.py`"*. It is not — `deploy.py` takes one. It is `load_team` and
  `TeamSpec` that nothing outside the tests reads, which is a **sharper** fact: the team object is
  manufactured by no one. Verified before it went into the spec.
- **`findings.unattached()` will reject a finding whose AFFECTS names an unowned gate.** F76 names
  the `version` gate, which belongs to no lane, and orphaned until AFFECTS said *"every lane"* with
  the reason. Do not satisfy that test by naming a lane the finding does not really affect.
- **Test baseline in this container is `7 failed, 98 passed`**, all pre-existing and all F75-related
  except one test that feeds `lane_from_cwd` a hard-coded `C:\repos\...` path. **Diff against that
  baseline, not against green**, or you will attribute someone else's platform failure to yourself.

## What to do first

1. **Push `feat/readiness-generator`.** Nothing about R13 can proceed until then.
2. Diff `DRAFT-platform-and-manufacturing-UNNUMBERED.md` §D1–D5 against R13 run 1's answer. Settle
   whether a new number is warranted; if not, delete the draft and say so.
3. Decide F75 — re-pin to the bytes git stores plus a `.gitattributes` marking
   `evals/corpus/*.json` as `-text`, or accept that CI and every container tier stay red.
4. F77's change 1 — take the suite out of the request path — before any UI performance work.
