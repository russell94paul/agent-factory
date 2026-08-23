# UI surface inventory — what the factory is for, what it already shows, and what is missing

**Written 2026-08-23, deliberately BEFORE looking at any external product.** Same discipline as
`agent-factory-concept-inventory.md`: state our own position first so an outside answer returns a
*diff* rather than a survey, and so a research pass cannot answer a question we did not ask.

⚠ **This exists because that already happened.** R12 was dispatched without one of our standing
constraints in its brief and duly recommended adopting a tool the constraint had ruled out
(`SYNTHESIS.md` §12.2). Every constraint in §7 below is written down so the next pass carries it.

Every figure was measured on 2026-08-23 and names its instrument.

---

## 1. What the factory is for — and it is not a terminal manager

From `README.md`, unchanged since the repo was founded:

> A team of agents did the work, and we can prove it — or we can prove we could not tell.

**That is an evidence product, not a process product.** It matters more than anything else in this
document, because it decides what the UI is *for*.

The repo exists because two prior mechanisms acted without anything measuring whether the action
helped: a retired agent produced **233 diagnoses, 234 escalations and 0 fixes over 81 days**, and a
loop ran **965 times, recorded its own 1.6% success rate, and never adjusted**. Both were capable.
Neither was measurable. The entire ordering of the codebase — contract before evals before tasks
before deploy — is a response to that.

⭐ **So the question "what UI would make this cutting edge" has a sharper form: every session
manager on the market manages _processes_. None of them can answer _who did this work, under what
configuration, and what proves it was correct._** That is the axis this repo is already on, and it
is the only one where it is not starting from behind.

## 2. The four planes, and who belongs in each

From `docs/specs/architecture-v0.md`. This is the load-bearing structure for any UI:

```
APPROVE   humans only. merge · per-secret grant · promote to prod   ← never automated
PROVE     readiness gates · GreenContract · findings.d · run audits
RUN       isolation ladder — T0 worktree · T1 container · T2 clone schema
DECIDE    conflict graph · claims · scheduling · caps · budgets     ← the :8765 build plane
```

⭐ **Each plane implies a different user, and only one of them is a plane a non-engineer belongs
in.** This is the answer to "maybe normal users":

| Plane | Who | What they need to see | Exists today? |
|---|---|---|---|
| DECIDE | operator | what can start, what conflicts, what it will cost | partly — Lanes tab |
| RUN | nobody, ideally | only the exceptions: stalled, orphaned, over-budget | new Sessions tab |
| PROVE | reviewer | the verdict **and what it was measured with** | partly — Gates tab |
| **APPROVE** | **anyone, including a non-engineer** | **what was delivered, what proves it, approve or reject** | **nothing** |

**The APPROVE plane has no surface at all, and it is also where delivery is measurably stuck**: two
PRs in `prefect-connectors` are fully green and have waited **6 and 9 days** for a human, and one
agent has been sitting on a written question nobody read. The "normal user" surface and the
delivery bottleneck are **the same surface**. That coincidence is the most useful finding here.

## 3. What surfaces already exist — measured

| Surface | Where | Size / state | Live? |
|---|---|---|---|
| Orchestrator UI `:8765` | `prefect-connectors/orchestrator/static/` | `index.html` **161 KB**, `flow.js` 58 KB, last touched 08-20 | yes |
| Readiness tracker | `agent-factory/scripts/local_tracker.py` → `tracker.html` | 5 tabs, re-measures per request, **~10–19 s a page** | yes |
| `agent-factory.html` | `agent-factory/docs/artifacts/` | published readout | static |
| `orchestration-bench.html` | `agent-factory/docs/artifacts/` | published readout | static |
| `platform/master/` | `aldc-launchpad` | **superseded, dead since June 2026** per its own CLAUDE.md | no |

**Four live surfaces, and a fifth that died.** Any new UI is the sixth thing built to look at this
work. `platform/master` is the cautionary case: a monorepo founded as a delivery *platform* whose
platform half stopped moving in June while the ops half carried every ticket.

## 4. What the tracker already does that a session manager does not

Not to defend it — to stop a research pass recommending we rebuild it:

- **Every number re-measures on refresh.** There is no cache. A page that can quietly show
  yesterday's state is the drift this project exists to remove.
- **Verdicts are four-valued** — `PASS` / `FAIL` / `UNMEASURABLE` / `NOT_RUN`. Not a checkbox grid.
- **The board is generated from the gates**, so a task list cannot drift from what is measured.
- **`recommend()` ranks lanes** from gate verdicts + the dependency graph + file conflicts, and says
  in writing which part is judgement.
- **Launching a lane claims it first**, refuses on conflict, and refuses if a live session already
  occupies the worktree.

## 5. The measured state, 2026-08-23

```
readiness            10 of 30 gates pass
lanes                5 defined · max 3 concurrent (file-conflict graph, DERIVED from lanes.py)
                     judgement and grain have NEVER been launched
per-lane cost        control-plane 1.23M out · 322M cache-read · 22.8h · opus-5 · 25 commits
                     artifact        227k out ·  55M cache-read · 19.4h · sonnet-5 ·  5 commits
                     certify         236k out ·  55M cache-read ·  1.7h · sonnet-5 ·  4 commits
sessions             12 running · 1 blocked on an unread question
                     2 directories hold >1 running session (one is a lane worktree — F73)
autonomy             3 of 14 recorded runs finished with no human
gate refusals        0 of 22 gate events were ever a refusal
delivery             prefect-connectors: 2 PRs green and waiting 6–9 days for a human
```

## 6. What is actually confusing — enumerated, not guessed

Every item observed today, not imagined:

1. **Five live sessions shared one name** (`boot pre-flight verification`), inherited from the boot
   prompt that spawned them. `CLAUDE_CODE_SESSION_NAME` is read once at startup, so a running
   session cannot be renamed. *(Addressed: identity is now derived from the opening prompt.)*
2. **Six sessions shared one working directory**, so cwd does not disambiguate either.
3. **A terminal died and its agent kept working**, invisibly, for minutes. Alive, visible and
   attachable are three different properties and nothing distinguished them. *(Addressed: four
   liveness states.)*
4. **Four agents were blocked on questions written in plain English** in `jobs/<id>/state.json`,
   which nothing read. Not alarm fatigue — **alarm absence**. *(Partly addressed: shown, not yet
   answerable.)*
5. **A finished lane left no trace at all** — `finish()` deleted the claim and that was the record.
   *(Addressed: `factory/runs.py`.)*
6. **Two green PRs waited 6–9 days** for a human to press merge. **Not addressed.**
7. **A page load takes 10–19 s** and two concurrent requests return empty (single-threaded server).
   **Not addressed.**
8. **Two servers can hold one port** and you verify against the stale one (F8). **Not addressed.**

⭐ Items 1–5 were *legibility* problems and are mostly fixed. **Item 6 is a throughput problem and
no UI built so far touches it.** That is the distinction a research pass must not blur.

## 7. Constraints any recommendation must respect — state these in the prompt

The R12 failure was a missing constraint. These are the ones:

- **Windows-first** on the operator's machine. WSL exists; say what changes.
- **Three concurrent lanes** today. A design assuming ten agents answers a question we do not have.
- **Small team.** Anything needing a platform team to operate is wrong regardless of merit.
- **Per-secret human approval is a hard rule.** No batch-approval of credentials, ever.
- **No unlabelled stale numbers.** A cached figure must carry its age *in the same string*.
- **The existing instrument panel is never removed**, only added to.
- ⚠ **The no-in-page-terminal constraint is UNDER REVIEW.** It has never been tested — R7 handed
  our own position back rather than challenging it (§11.1), and R12 was never told about it
  (§12.2). Paul's position on 2026-08-23 is *"terminal mode needs to exit"*, which points at
  **retiring** it. **Before any pass is dispatched this must be settled and stated as a decision**,
  because it is the single fact that decides whether adopting an Electron terminal grid is
  admissible. Do not let a third pass answer it by accident.

## 8. The options, as options

Not a recommendation — the shape of the decision, so an outside answer can be graded against it.

| # | Option | What it wins | What it costs | Killed by |
|---|---|---|---|---|
| A | **Extend the tracker** (status quo+) | zero new surfaces; every number already re-measures | still a 19 s page; still an engineer's tool | nothing yet — it is the default |
| B | **Adopt an external session manager** (switchboard et al.) | months of UI work skipped | R12 OBSERVED: no true attach, spawns a **duplicate against a live session id**, cannot see `needs`; no plugin API | the duplicate-spawn behaviour *is* the bug we hit |
| C | **Build a terminal grid ourselves** | full control | competing on a commodity axis with Warp, VS Code, tmux, switchboard | §3 — it would be the sixth surface |
| D | **Build the APPROVE surface** — a decision queue | targets the *measured* bottleneck; the only plane a non-engineer can use | does not make agents more visible | nothing yet |
| E | **Provenance UI** — every artefact traceable to agent, config hash, evidence, verdict | the one axis where this repo is ahead of every product | needs the version hash fixed (**0 of 15 dimensions covered today**) | its own prerequisite |

⭐ **B and C are the same bet on someone else's axis. D and E are the axes this repo already owns.**
D is the smaller and targets a measured problem; E is the differentiator and has a prerequisite.

## 9. What "cutting edge" would actually mean here

A terminal grid is table stakes and several products already ship it. Three things nobody ships,
all of which this repo is closer to than any of them:

1. **A verdict that can say "I could not tell."** Four-valued, with `UNMEASURABLE` as a first-class
   outcome rather than a silent pass. Every dashboard on the market is two-valued.
2. **Provenance to a config hash.** "This artefact was produced by *this* agent, on *this* model,
   with *this* prompt and *this* contract version." The hash exists and covers **0 of 15
   dimensions** — so this is a gap, not a feature, but it is a gap with a name.
3. **Cost paired with an outcome, enforced.** `metrics.py` *refuses* an activity metric with no
   outcome metric. R12 reached the same rule independently. Now that per-lane cost is measured,
   tokens-per-commit is computable — and nothing else shows it.

## 10. Questions the research pass should answer

1. Given §1 — an evidence product, not a process product — **what is the right primary object of the
   UI**: the session, the lane, the artefact, or the decision?
2. What does the state of the art do for **the APPROVE plane** — review-and-merge queues where the
   work was done by an agent? Who has shipped this, and what did they learn?
3. **Is a terminal visible at all in the best designs**, or is it an escape hatch? (Ask *only* after
   §7's constraint is settled.)
4. What is the evidence on **surfacing an agent's question to a human** so it is answered in minutes
   rather than days — interrupt, queue, inbox, push? Our measured latency is *days*.
5. What would a **non-engineer** need to approve agent-produced work safely, and what has been
   tried?
6. How do teams present **provenance and cost-per-outcome** without it becoming a vanity dashboard?
7. What should we **refuse to build**, given four surfaces already exist and a fifth is dead?
