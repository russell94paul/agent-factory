# Agent Factory — the operations UI, and the ledger it has to stand on

**Written 2026-08-29.** Supersedes the 58-section "MOTION-FIRST VISUAL OPERATIONS UI" brief, whose
vision this keeps and whose premise it corrects. That brief specified a telemetry-rich command
centre for a system that emits almost no telemetry, and its own §53 escape hatch ("simulate the
events if they don't exist") made a beautiful mock the guaranteed outcome. This version builds the
missing half first.

---

## 0. ⛔ Kill condition — read before writing any code

**Inspect the repository first. If the normalized event stream in §3 does not exist, do not proceed
to a simulated one. Stop, say so, and build §3.**

A UI that renders invented events is indistinguishable from one rendering real events, and this repo
exists to make exactly that distinction impossible to fudge. A demo that passes the acceptance test
on simulated data has not passed it.

**The honest state, measured 2026-08-29 at `17a6a5a` — verify before trusting, these will drift:**

| Fact | Command |
|---|---|
| **No JS frontend exists.** No `package.json`, `tsconfig.json` or `next.config.*` anywhere in the repo | `find . -name package.json -not -path "*/node_modules/*"` |
| The entire UI is **2,575 lines of Python** serving **213 inline HTML tags** from a `socketserver` | `wc -l scripts/local_tracker.py` · `grep -c "<div\|<span\|<table" scripts/local_tracker.py` |
| **`.data/runs.jsonl` holds 3 rows.** Ever | `wc -l .data/runs.jsonl` |
| The certification verdict is `NOT_RUN` — **12 assertions have no instrument wired** | `python -m factory.launch` |
| The eval corpus is **1 case, 0 strata — below any calibration threshold** | `python -m factory.launch` |
| The live launch path is `local_tracker._launch_script()` → a generated `.ps1` → bare `claude`, with **no cap, no budget, no transcript parsing and no run record** | read `scripts/local_tracker.py` §`_launch_script` |
| `deploy.py` — which *does* have the retry ledger and cost caps — has **zero production callers** | `grep -rn "RepoDeployer" --include=*.py . \| grep -v deploy.py` |
| Ticket ledger: **76 tickets, 2 done, 18 blocked** | `python -c "from factory.tasks import TaskStore; ..."` |

**So: there is no agent event stream, no per-agent cost telemetry on the path that actually runs, and
one certified connector's worth of history — which is zero.** Ninety percent of the original brief
described views over data that does not exist.

⚠ **Check `docs/design/session-ui-and-intake.html` ("Control Room & Intake", created 2026-08-29)
before starting.** A parallel session is designing this surface. Reconcile or you will ship two
command centres.

---

## 1. What this product is actually for

Not "show that agents are busy." The one sentence:

> **Make it visually unavoidable whether work is progressing toward a *verified* outcome — and make
> "we could not measure this" as loud as failure.**

Activity is not success. A finished ticket is not necessarily correct. A green light from an
instrument that cannot produce a red is worthless. The UI's job is to carry those three facts into
pixels, and everything else is secondary.

**The chain the UI represents:**

```
Intent → Work → Team → Agent → Action → Tool → Resource → Observation → Evidence → Verification → Outcome
```

---

## 2. ⭐ The rule that governs every number on screen

This repo has four verdicts, not two:

```
PASS   FAIL   UNMEASURABLE (no instrument could be established — NOT a pass)   NOT_RUN
```

Research completed 2026-08-29 (`docs/reviews/build-vs-adopt-2026-08-29.md`) established that six
mature tools and standards already carry an equivalent state — and **every one of them destroys it at
the aggregate**: OpenSSF Scorecard drops inconclusive checks from the denominator (10 of 18
inconclusive still scores 10.0/10); OHDSI computes `countPassed = countTotal - countOverallFailed`,
rounding it up to passed; XCCDF and Great Expectations score it as failure; Grafana ships a "Set
Normal state" switch; pytest greens `skipped` by default.

> **The representation problem is solved everywhere. The aggregation problem is solved nowhere.
> That is this product's entire differentiator, and it lives or dies in the metric bar.**

**Therefore, binding on every view:**

1. **No single-number percentage may stand for a set containing an UNMEASURABLE.** `PASS RATE 81%` is
   forbidden. Render a four-part proportional bar where unmeasurable has its own visible mass and its
   own non-colour treatment (hatching, a distinct glyph), never a shade of red or green.
2. **A mission with missing evidence must never render as healthy** — not at estate zoom, not in a
   sparkline, not in a rollup, not when aggregated with 40 healthy siblings.
3. **`NOT_RUN` and `UNMEASURABLE` are visually distinct from each other.** One means nobody looked;
   the other means we looked and could not see.
4. **Every displayed figure carries its basis** — `MEASURED | DERIVED | ASSUMED | REPLAYED`. A
   replayed score prints as replayed. The repo already does this: `factory/certify.py` emits
   `"REPLAYED, not a live measurement"`. The UI must not launder it.
5. **A cached number carries its own age in the same string as its value.**

If you build one thing well, build this. It is the part no incumbent has.

---

## 3. ⭐ PHASE 0 — build the event ledger. No UI. This is the real work.

**Do this before any pixel.** Justification, from the repo's own briefs: the append-only event record
is *the only piece that cannot be reconstructed later*. Providers can be abstracted whenever a second
provider appears; a run that executed without recording what it did is simply gone. And R19's
load-bearing claim: **the eligible set — every configuration that passed the filter and was not
chosen — costs nothing to write and cannot be recovered afterwards.**

Create `factory/events.py`: an append-only JSONL event log with a fold into current state.

```
event_id · ts · mission_id · team_id · agent_id · parent_agent_id · lane_id
event_type · status · tool_id · resource_id · artifact_id
duration_ms · tokens_in · tokens_out · cost_usd · basis · metadata
```

**Event types — implement only what the system can actually emit today, and mark the rest `PLANNED`
in code rather than faking them:**

```
mission.created / started / completed / failed
team.created / changed
agent.spawned / started / blocked / resumed / completed / failed / cancelled
tool.started / completed / failed
resource.read / write / created
test.started / passed / failed
evidence.created / updated / invalidated
verification.started / assertion / completed
human.required / responded
retry.started / completed
context.added / removed / compacted
```

**Three requirements that are not negotiable:**

- **`RunStarted` carries the eligible set** — every configuration that passed the filter, which was
  chosen, and under what rule. Backfill everything else; never this.
- **Every terminal event carries one of the four verdicts**, and `GreenContract` assigns it — never
  the agent, never the provider, never the UI.
- **Fold two existing ledgers in or keep them apart with the reason recorded — do not create a
  third.** `.data/runs.jsonl` (`factory/runs.py`, 3 rows) and `prefect-connectors/.sessions` (14
  runs, read by `g_work_is_attributable`) count different populations and neither records a
  configuration.

**Then wire the emitter to the path that actually runs.** Today that is
`local_tracker._launch_script()`, not `deploy.py`. An event model wired to the unwired code produces
an empty log and a green demo — the exact failure this document exists to prevent.

**Phase 0 is done when:** a real supervised lane run produces a real event log, and `python -m
factory.launch` moves `breadth` off *"1 case, 0 strata"*. Until then the UI has nothing true to say.

---

## 4. Scale — design for what exists

**Three lanes on one Windows workstation. It is a *file* ceiling, not a compute one.** Realistic
targets: **~3 concurrent missions, ~10 agents, hundreds of events per run, thousands in history.**

- **Do not** build aggregation machinery for 100 agents. Do not reach for WebGL or Three.js. Do not
  optimise for 50 simultaneous missions that cannot physically occur.
- **Do** virtualise the event list, batch updates, and memoise graph nodes — cheap, and correct at
  any scale.
- The interesting performance problem here is **history**, not concurrency: replaying a long run's
  events smoothly. Optimise that.

A UI that is beautiful with 40 fake missions and awkward with 3 real ones is a failure.

---

## 5. Stack — decided, not left to the implementer

The original brief said "reuse the existing application" *and* listed React/Next/TypeScript. There is
no JS app to reuse. Resolve it explicitly:

**Extend `scripts/local_tracker.py`'s server-rendered surface. Do not introduce a Next.js app.**

Reasons: it is the surface Paul actually uses; it already re-measures on every request (its docstring:
*"A tracker that can quietly show yesterday's state is the drift this whole project exists to
remove"*); and a second UI would immediately drift from the first. The repo has **one runtime
dependency** (`pyyaml`) and **no lockfile and no CI** — adding a node toolchain is a large, ungated
new surface.

**Permitted:** a single vanilla-JS + SVG/Canvas module served by the tracker, talking to one SSE
endpoint over the Phase-0 event log. Inline CSS/JS, no build step, no bundler.
**If you believe a framework is genuinely required, say so and stop** — that is a decision for Paul,
not a side effect of implementation.

⚠ Before adding *any* dependency, note that nothing gates them: `dependencies = ["pyyaml>=6.0"]`, no
lockfile, no `.github/`, and none of the 27 readiness gates measures a dependency. Ticket `BVA-01`
covers this and should land first.

---

## 6. The Factory Floor — what to actually build

One continuously-updating spatial view, with **semantic zoom** rather than separate pages:

```
LEVEL 0  Estate    all missions
LEVEL 1  Mission   one ticket and its team
LEVEL 2  Team      agents, responsibilities, dependencies
LEVEL 3  Agent     execution history, context, tools, metrics
LEVEL 4  Action    one tool invocation / command / edit / probe
LEVEL 5  Evidence  the artifact proving it worked
```

**Layout:** the visualisation gets 60–70% of the screen. Navigation chrome does not. Global metric
strip across the top, mission navigator left, inspector right, event timeline along the bottom.

**Motion carries information or it is deleted.** Pulse frequency tracks event velocity, not a
`setInterval`. A directional packet along an edge means a real tool call with a real duration. If a
motion cannot be traced to an event in the Phase-0 log, remove it.

Respect `prefers-reduced-motion`, and **no meaning may depend on animation alone** — every state has
a textual and non-colour form.

### The five things worth building first

1. **Evidence accumulating visibly around a mission.** Confidence should be watchable. This is the
   product's thesis in motion.
2. **The verification ring — A1…A12 as clickable segments**, each showing verdict, the evidence
   behind it, observed vs expected, and the responsible lane and agent. `UNMEASURABLE` segments must
   look materially unlike `PASS`. Today, honestly rendered, **this ring is almost entirely
   `NOT_RUN`** — 12 assertions, 2 instruments. **Render that truthfully.** A ring that looks bad
   right now is the single most valuable screen in the product.
3. **Loop detection.** Same command, same file re-read, same failing test, plan regenerated. Draw a
   literal loop with `7 repetitions · $1.82 consumed · 4m 13s · no new evidence`. This is the most
   distinctive alert in the system and directly measurable from the event log.
4. **Failure traces persist.** Solid = successful branch, ghosted = abandoned, broken = failed,
   looped = retried, marked = human-corrected. Never erase failed reasoning; the convergence story is
   the debugging tool.
5. **"Why?" on every autonomous action** — why spawned, why blocked, why this tool, why retried, why
   unmeasurable — answered by citing events from the log, not by generating prose.

### Defer until Phase 0 has produced real data

Execution replay · trace waterfall · critical path · cost heatmaps · resource map · collision
detection · context stack · knowledge graph · agent/team performance analytics · the constellation
and city metaphors.

Every one is good. Every one needs an event history that does not yet exist. **Design the component
and event architecture now so they slot in without a rebuild — but do not build them against
invented data.**

---

## 7. Simulated data — permitted, fenced

You will want a fixture to develop against. Allowed, under four rules:

1. It lives in a clearly separate module and **cannot be enabled in the same process as live data**.
2. Every simulated view carries a **persistent, non-dismissable banner**: `SIMULATED — not a
   measurement`. Same discipline as `certify.py`'s `"REPLAYED, not a live measurement"`.
3. It emits the **same schema** as Phase 0, so the UI cannot tell the difference and never needs a
   second code path.
4. **It may not be used to satisfy the acceptance test in §9.**

Include one deliberate retry loop and one recoverable failure so abnormal states are developable.

---

## 8. Visual language

Serious infrastructure with beautiful motion. Deep charcoal ground, soft layered panels, bright data,
high-contrast type, subtle depth, minimal borders, a precision grid.

**Not:** cyberpunk neon, heavy gradients, glassmorphism everywhere, everything glowing, giant rounded
cards, cartoon robots, holographic effects.

Optimise, in this order: **clarity → hierarchy → situational awareness → trust → speed → delight.**

When nothing is happening the factory should feel calm, not dead. When work starts it comes alive.
When verification succeeds it should **settle into completion because the evidence proves it** — not
celebrate because an agent said "done".

---

## 9. ⭐ Acceptance test — written so a simulator cannot pass it

The original acceptance test was a list of activity questions, all answerable by a convincing mock.
This one is not.

**Open the UI against the live system and answer, in five seconds:**

1. How many missions are running, and **how many of their assertions are `NOT_RUN`?**
2. Which numbers on this screen are **`UNMEASURABLE` rather than passing** — and is that visually
   unmistakable without reading a legend?
3. Which displayed figures are `MEASURED`, which `DERIVED`, which `REPLAYED`?
4. What is blocked, and what is looping?

**Then, in one click on any agent:** its purpose, current action, parent, tools, resources, timeline,
cost, tokens, retries, evidence produced — **each labelled with its basis, and `NOT-RECORDED` where
the instrument does not exist.**

**Then, in two clicks, the question the whole product is for:**

> **Is this mission's claimed success actually supported by evidence — and if not, is that because it
> failed, or because nothing measured it?**

**And the negative control, which is the real test:** point the UI at the factory **as it stands
today** — 3 recorded runs, 1 corpus case, 12 uninstrumented assertions, a launch path that records
nothing. **It must look conspicuously unfinished.** Sparse, honest, mostly `NOT_RUN`.

**If today's factory renders as a healthy, busy command centre, the UI is lying and the
implementation has failed** — however good it looks. That is the whole acceptance test; the rest is
detail.

---

## 10. What to produce

1. **Current-state assessment** — what actually exists, measured, with the commands. Correct anything
   in §0 that has drifted; that correction is a deliverable, not an aside.
2. **Phase 0: `factory/events.py`** — schema, append-only writer, fold, wired to the path that
   actually runs, with tests. **This is the deliverable that matters most.** Ship it even if no UI
   follows.
3. **A wireframe** before implementation.
4. **The vertical slice** — factory shell, mission graph from real events, agent nodes, the
   verification ring rendered honestly, event stream, agent inspector, and only motion that carries
   information.
5. **A negative control** — a test proving the UI renders `UNMEASURABLE` distinctly from `PASS` and
   from `FAIL`, that **fails if the distinction is removed**. Every gate in this repo ships with a
   demonstration that it can fail; a UI gate is no different. This is not optional: a `bash-guard.sh`
   in this estate exited 127 and blocked nothing for months while reporting success.

**Do not stop at a design document unless genuinely blocked** — and if you are blocked, name the
blocker and the access that would clear it rather than routing around it with simulated data.
