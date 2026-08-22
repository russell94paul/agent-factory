# Spec — terminal configuration for agent factories

**Written 2026-08-22, after the first day three lanes ran for real.** Every number here was
measured, not estimated; every defect named actually happened. Scope: how lane terminals are laid
out, launched, coloured, tuned and rehearsed. Non-goal: what the lanes *do*.

---

## 0. The requirement hits a wall immediately

**Asked for: four terminals. Maximum simultaneous lanes today: three.**

```
lanes       control-plane · certify · judgement · artifact · grain
conflicts   control-plane <-> judgement   (both edit orchestrator/pipelines.py)
            certify       <-> grain       (both edit factory/connector_contract.py)
max set     3   — {control-plane, certify, artifact}, and three other triples
```

Computed from `factory/lanes.py`, not assumed. Conflicts are by **file locality, not the
dependency graph**: the graph would allow control-plane and judgement together; the filesystem
would not, and two sessions editing one file is the 41.7% cross-agent conflict rate R5 measured.

A fourth terminal is therefore one of:

| Option | The 4th pane is | Cost | Verdict |
|---|---|---|---|
| **A** | a **conductor** — board, bus, finish; not a lane | none | **adopt now** |
| **B** | a 4th lane, after splitting `pipelines.py` gate definitions into their own module | one refactor | the real unlock |
| **C** | a 4th lane accepting the conflict, merged later | a guaranteed merge conflict | rejected — this is F70 |

⭐ **A is not a consolation prize.** Everything that closed the loop on 2026-08-22 — releasing
claims, pushing branches, reading the board, relaying corrections between lanes — was done from a
shell that had to be found or opened first. The conductor pane is where the human actually works.

---

## 1. Layout

```
┌────────────────────────────┬────────────────────────────┐
│  lane 1                    │  lane 2                    │
│  control-plane · opus      │  certify · sonnet          │
├────────────────────────────┼────────────────────────────┤
│  lane 3                    │  CONDUCTOR                 │
│  artifact · sonnet         │  board · bus · finish      │
└────────────────────────────┴────────────────────────────┘
```

Two-by-two, not a four-way vertical split: a Claude session wants vertical room, and four slivers
is what `start_all_command`'s alternating `-V`/`-H` degrades into past three panes.

**Both modes stay offered, neither imposed** (already true in `start_all_command(panes=…)`): panes
for watching, tabs for working *inside* one. The conductor exists in both — it is the pane you
return to.

### The conductor pane

Not a Claude session. A plain shell holding one live view:

```
readiness headline · claims held · per-lane commits-ahead + dirty · unread bus traffic
```

Refreshed on demand, never on a timer — see §2, where a refresh costs ~19 seconds.

---

## 2. Fast — the latency budget

Measured today, on this machine:

| Operation | Now | Target | Where it goes |
|---|---|---|---|
| Tracker page load | **19s** | < 2s | re-runs all 30 probes every request |
| `python -m factory.readiness` | ~19s | < 3s | the same probes, serially |
| Lane launch (claim → window) | ~1–2s | keep | fine |
| Two concurrent tracker requests | **returns empty** | serialise | `socketserver.TCPServer` is single-threaded |

**Rules.**

1. **Never cache a measurement silently.** The tracker's whole argument is that every refresh
   re-measures; a page that can quietly show yesterday's state is the drift this project exists to
   remove. Speed comes from making probes cheap, **not** from remembering their answers.
2. **Parallelise the probes.** They are independent and mostly I/O — thirty serial file-and-git
   walks *are* the 19 seconds. A thread pool is the single biggest win available.
3. **Cache only what is provably immutable within one request**: the audit file set,
   `git worktree list`, the findings parse. Keyed by mtime, dropped when the request ends.
4. **A stale number may only be shown if it is labelled stale**, with its age, *in the same string
   as the number* — the F72 rule: the basis travels with the figure or the figure means nothing.
5. **Fix the single-threaded server.** Two concurrent requests today return empty, which reads as a
   crash and cost real debugging time. `ThreadingHTTPServer` — but then rule 1 needs a lock, or two
   refreshes both run thirty probes.

**Launch fast path.** A lane's first thirty seconds are pure cost. Keep the generated `.ps1` (a
`-Command` payload is F10, where `wt` ate the semicolons) and keep the prompt on disk —
interpolating it into a command line is how quoting silently truncates it.

---

## 3. Optimizing — model, effort, and what a lane costs

Each lane already declares a model, and until today **not one of them used it**: `--model` was
built into a variable nothing read, so the banner announced opus while the session ran the
default. The rule that governs this whole section is the one that defect proves:

> **A declared setting that nothing reads is worse than no setting, because it reports as
> configured.** Every field in §6 must have a test asserting it reaches the process.

| Lane | Model | Why |
|---|---|---|
| control-plane | **opus** | designing controls for a bespoke engine, each needing a negative control. Pair with `/effort high` |
| certify · judgement · artifact | sonnet | execution after a decided design |
| grain | haiku | one query and one dataclass field |

**Escalation is per-subagent, not per-session.** A sonnet lane should still spend opus on its
closing review and haiku on greps — that pattern is what produced the six real defects certify's
reviewer found in certify's own diff. Do not run a whole session on opus because one step in it is
hard.

**Instrument the cost.** Nothing currently records what a lane spent. Minimum viable: tokens and
wall-clock per lane, posted to the bus on `finished`, so "grain is the cheap lane" becomes a
measurement instead of an intention.

**Concurrency ceiling.** Three lanes plus a conductor is four panes, and the machine also runs the
tracker, the evaluator service and Docker. Cap simultaneous lanes at 3 until measured otherwise,
and let the conductor be the thing that says when a fourth would be safe.

---

## 4. UI options

**Identity was the running problem of the day.** Three lanes were all named `boot pre-flight
verification`, indistinguishable in every listing, so a question from one lane could only be
answered by messaging all three and letting two ignore it. Fixed via `CLAUDE_CODE_SESSION_NAME`.
What remains is colour:

- **Per-lane tab colour** (`wt --tabColor`), matching each lane's existing banner accent:
  control-plane blue · certify teal · judgement violet · artifact green · grain amber · conductor
  grey. One frame, five instances: differently-coloured *windows* would read as noise, a coloured
  *tab stripe* reads as identity.
- **One scheme for the system** — `Agent Factory Blue` is already defined and is currently the only
  scheme. It is applied per-tab today; setting `profiles.defaults.colorScheme` makes every terminal
  match, including the conductor.
- **Title format** `<lane> · <what it is doing>` — already shipped. Keep it; it is what makes
  alt-tab usable.

**Attention.** A waiting lane already bells, flashes the taskbar and marks its tab `(!)`. Extend to
**state colour**: a lane that has gone quiet without committing is the stalled-lane signal R6
prefers over a heartbeat, and the tab is the honest place to show it.

**Status line**, per pane, one line: `lane · model · commits-ahead · dirty? · claim age`.

**Explicitly not wanted:** background images, acrylic, retro effects. This is an instrument panel,
not a desktop.

---

## 5. Simulation — rehearse the harness without spending a token

The entire launcher was debugged today **by launching real lanes and reading what broke**. That is
how three defects were found, and it is far too expensive to be the method.

**Two modes, both required.**

### 5.1 `--dry` — exists, keep, extend

Prints the command, the worktree and the prompt path, creating nothing. ⚠ Today it proves nothing
about the thing that will *parse* the command — that is exactly F10, where a dry run looked perfect
and `wt` split the invocation on a semicolon. Extend it to render the **exact final `.ps1`** and
assert on its content: model flag present, transcript marker cleared, session name set, and no
semicolon in any `wt` argument.

### 5.2 `--simulate` — new

Launch the full layout with a **fake agent** in every pane: a script that reads the real lane
prompt, prints the real banner, posts a plausible sequence to the bus (`claimed` → `note` →
`finished`), makes one empty commit, sleeps, and exits. No model call, no tokens.

That exercises everything that actually broke today — window layout, colours, titles, the claim
lifecycle, the attention hook, bus delivery, `finish()`'s assertions and the conductor's view — for
free, repeatably, and in CI.

### 5.3 What simulation must never do

It must be **visibly** a simulation: a `SIM` badge in every banner and window title, a flag on every
bus event, and a hard refusal to push. A rehearsal that could be mistaken for a real run is simply a
new way to lie about state, and this project already has enough of those.

---

## 6. Config surface

One declarative block, not five call sites:

```python
TERMINAL = {
    "layout":      "grid-2x2",        # grid-2x2 | tabs | single
    "panes":       3,                 # lanes; the conductor is added, not counted
    "conductor":   True,
    "scheme":      "Agent Factory Blue",
    "tab_colour":  "per-lane",        # per-lane | uniform | off
    "attention":   "bell+flash+title",
    "status_line": True,
    "mode":        "live",            # live | dry | simulate
}
```

Every field must be **read** by the launcher, and a test must assert that it reaches the spawned
process — see §3.

---

## 7. What must never be automated here

- **Merging a lane branch.** `finish()` refuses it deliberately; layout changes nothing about that.
- **Releasing a claim on a lane that stopped rather than finished.** The assertions in
  `factory/finish.py` are the guard, and a prettier terminal must not become a reason to skip them.
- **A simulated run reporting as a real one.**

---

## 8. Open

- **Option B — splitting `pipelines.py` gate definitions — is the only route to a genuine fourth
  lane.** Until it is done the fourth pane is the conductor, and this spec says so plainly rather
  than implying four lanes are available.
- Per-lane cost is unmeasured, so §3's model table is reasoning, not evidence. It should be
  re-derived once `finished` events carry tokens and wall-clock.
- ~~`wt --tabColor` is assumed available.~~ **Closed 2026-08-22: Windows Terminal is 1.24.11911.0
  and `--tabColor` has existed since 1.7, so §4's per-lane colour is buildable.** Recorded because
  the check itself is instructive — `wt --help` opens a GUI tab instead of printing, so grepping it
  returns nothing, and that nothing is NOT-VISIBLE rather than absent. The version came from
  `Get-AppxPackage`, an instrument that can actually see.
