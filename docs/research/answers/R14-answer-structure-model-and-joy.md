# R14 — Structure, the object model, and what this should feel like to open

**Answered 2026-08-23, from the repository, not from a summary.** Every structural claim below cites
a file and a line. Where I could not see something I have written `NOT-SUPPLIED` and named it.

**Tiers, per §8.** `OBSERVED` — I read the source or ran it · `REPORTED` — a credible postmortem or
write-up · `MARKETED` — a vendor says so · `INFERRED` — my reasoning. No `MARKETED` claim is used as
a design premise anywhere in this document.

**What I did not re-open.** Platform (VS Code extension), topology (seven patterns, none raises the
cap), and the embedded-terminal question are settled per §0 and I have taken them as given. The
one place I touch the terminal is §7.4, and it is a consequence of the constraint, not an argument
against it.

**Measurement note.** I did not execute `measure()`. Another session is working in this checkout
concurrently, and `g_contract_suite_green` writes a cache file (`readiness.py:427-431`) and shells a
full pytest run — running it would have been a write and a race. Every count below is therefore
static: read from source, `wc -l`, `grep`, and `git`. Where a claim needed execution to be
`OBSERVED` and I did not execute it, it is labelled `INFERRED` with the discriminating test stated.

---

## 0. Executive summary

Six things, in the order I would act on them.

1. **Your god-object is not `local_tracker.py` and it is not `readiness.py`. It is
   `local_tracker.render()` — one function, lines 530–1431, 902 lines, 54% of the file**, holding
   seven tabs in one local namespace with `blocked`, `rows` and `w` reused across them. The module
   is fine. The function is the problem, and the seam is obvious and cheap.

2. **The threading change is a live correctness defect, and the module-level globals are the
   decoy.** `ThreadingTCPServer` (`local_tracker.py:1663`, and it is **uncommitted** — `git show
   HEAD:scripts/local_tracker.py | grep -c ThreadingTCPServer` → 0) removed the accidental
   serialisation that was the only thing making `claims.claim()` atomic. `claims.claim()` is
   check-then-write (`claims.py:111` reads, `claims.py:124` writes) with nothing between. Two
   concurrent requests to `/start/<lane>` — a GET, so a double-click or a browser prefetch is
   enough — both pass the check and both write. **That is F73 re-opened at the HTTP layer**: two
   agents, one worktree, one branch. The four `_*_MSG` globals are a cosmetic bug by comparison.

3. **The missing object that fixes the most at once is a measurement scope — call it `Snapshot`.**
   `measure()` is a free function with no scope, so every consumer re-runs all thirty probes.
   The Flow tab runs `measure()` **five times per page load** (`local_tracker.py:533, 1083, 1084`,
   and twice more inside `flow.svg()` at `flow.py:103,107`). Four of the six measuring tabs never
   read the result of the first one. `Snapshot` is simultaneously the latency fix, the freshness
   design primitive, and the object that makes "how old is this number" a type rather than a
   convention.

4. **`lane` is four objects wearing one string**, and that — not the topology — is why the
   concurrency cap will not move. A lane id is at once a work package, a file-conflict key, a git
   branch name, a directory name, a claim key and a ledger key. You cannot run two agents on one
   work package because the work package *is* the branch.

5. **The state-root fork is not a tidiness problem, it is two latent false-greens.** Both
   `claims.py:35` and `worktrees.py:31-32` resolve through `__file__.parent.parent`, so inside a
   lane worktree `worktrees.existing()` returns `{}` — which makes `worktrees.is_dirty()` return
   `False` for a dirty tree, which makes `finish.checks()` (`finish.py:73`) pass a lane that has
   uncommitted work. `runs.py:46-61` already wrote the correct resolver and kept it private.

6. **The design answer is that the first screen is a queue of things waiting on a human, and it is
   usually empty.** Your own measurement says the bottleneck is human latency — two green PRs at
   6–9 days, an agent question unread for days (`ui-surface-inventory.md:100-101, 120`) — not agent
   throughput. Twelve sessions running is the resting state, not news. And the no-cache rule is
   currently producing *staler* information than a labelled cache would, because a 19-second page
   is a page you refresh less often (§6.4).

---

## 1. The three structural changes I would make first

### 1.1 First: give measurement a scope object

**The finding.** `readiness.measure()` (`readiness.py:1052-1063`) takes no arguments, returns a
list, and caches nothing. Every consumer that needs a verdict calls it again. Static call sites:

| Caller | Line |
|---|---|
| `board.board()` | `board.py:81` |
| `goals.progress()` | `goals.py:64` |
| `handoff.lane_state()` | `handoff.py:87` |
| `handoff.session_handoff()` | `handoff.py:154` |
| `local_tracker.render()` | `local_tracker.py:533` |
| `readiness.main()` | `readiness.py:1067` |
| `build_tracker.py` | `scripts/build_tracker.py:40` |

`flow.py` never calls `measure()` directly and its docstring says so proudly ("DERIVED from the same
`measure()` call", `flow.py:87`) — but it calls `board()` four times: `layout()` at `flow.py:51`,
`counts()` at `flow.py:88`, and `svg()` calls both again at `flow.py:103` and `flow.py:107`.

So, per page load (all `OBSERVED` by reading the call graph; `INFERRED` only in that I did not
instrument a live run):

| Tab | `measure()` calls | Does the tab use the result of line 533? |
|---|---|---|
| `/flow` | **5** | **no** — the flow block (`1078-1143`) never references `results` |
| `/goals` | 2–3 | **no** — the goals block (`1009-1076`) never references `results` |
| `/handoff` | 2 | **no** — the handoff block (`1357-1393`) never references `results` |
| `/sessions` | 1 | **no** — the sessions block (`908-1007`) never references `results` |
| `/` (gates) | 2 | yes |
| `/lanes` | 1 | yes (`local_tracker.py:659`) |
| `/research` | 0 | n/a — correctly excluded at line 533, and tested (`test_tracker_routes.py:31`) |

**Four of six measuring tabs pay a full thirty-probe measurement they then discard.** The research
tab was carved out of this cost and given a test; the same carve-out was never applied to the four
tabs that needed it just as much.

The cost of one `measure()` is not uniform. `g_contract_suite_green` (`readiness.py:388`) shells a
full pytest run unless a content hash matches; `g_output_is_certified` (`readiness.py:439`) shells
`python -m factory.certify`; `_audits()` (`readiness.py:121-140`) parses every file in
`orchestrator/data/audits/`; `_suite_fingerprint()` (`readiness.py:359-375`) sha256s the *bytes* of
every `.py` under `tests/` and `factory/` — on the Flow tab, five times.

**Why this is the first change and not merely an optimisation.** A `Snapshot` is not a cache. It is
the object the whole freshness constraint needs:

```python
@dataclass(frozen=True)
class Snapshot:
    taken_at: datetime
    results: dict[str, Result]       # gate id -> Result
    connectors: Path                 # the basis F72 says must travel with the number
    since: str                       # MEASURED_SINCE
    @property
    def age(self) -> timedelta: ...
```

Seam: `measure()` stays exactly as it is and gains one wrapper, `snapshot() -> Snapshot`. Every
consumer changes signature to take one: `board(snap)`, `flow.layout(snap)`, `goals.progress(snap)`,
`handoff.session_handoff(snap)`. The tracker builds exactly one per request and hands it down.
That is roughly 15 call-site edits and it is mechanical.

The payoff is not only that Flow goes 5 → 1. It is that **a renderer can no longer receive a bare
integer.** Today `local_tracker.py:586` writes `<b>{n}</b><span>of {total} gates pass</span>` where
`n` is an `int` with no provenance attached; the page then prints a separate timestamp string at
line 565 and *hopes* they correspond. With a `Snapshot`, the age is a property of the thing being
rendered and the correspondence is structural. §6 builds the entire design on this.

`INFERRED`, with a discriminating test you can run in a minute: time `curl -s -o /dev/null -w '%{time_total}' localhost:8099/flow`
against `localhost:8099/lanes`. If the scope object is the right diagnosis, `/flow` is roughly 3–5×
`/lanes` despite rendering less. If they are within 20% of each other, I am wrong and the cost is
elsewhere.

### 1.2 Second: make the claim a lock, and stop mutating state on GET

**This is the live defect the brief asked me to rule on, and it is real.**

`claims.claim()` (`claims.py:106-125`):

```python
found = blockers(lane)          # line 111 — reads the directory
if found and not force:
    raise ClaimError(...)
ROOT.mkdir(parents=True, exist_ok=True)
...
_path(lane).write_text(...)     # line 124 — writes
```

Read, decide, write, with nothing making the three one operation. Under the previous
single-threaded `TCPServer` this was safe *by accident*: requests were serialised, so no second
thread could interleave. `ThreadingTCPServer` (`local_tracker.py:1663-1665`) removes that. The
comment above it is accurate about why threading was needed and silent about what it took away.

The window is not theoretical, for three compounding reasons, all `OBSERVED`:

1. **The launch routes are GETs.** `/start/<lane>` (`local_tracker.py:1571`), `/start-all`
   (`1522`), `/claim/<lane>` and `/release/<lane>` (`1581`), `/unanswer/<lane>` (`1516`), `/reload`
   (`1607`) and `/sync` (`1599`) all mutate state on GET. A double-click, a middle-click that opens
   in a background tab, a browser prerender, or the favicon-and-link prefetch the threading comment
   itself mentions, issues two of these concurrently.
2. **`/start-all` claims in a loop** (`local_tracker.py:1535-1539`), so one request holds the window
   open across several lanes while another request is inside it.
3. **`launch()` widens the window further.** It checks `sessions.live(lane_id)` (line 259), then
   claims (line 268), then builds the command (line 272), then `Popen`s (line 280). The gap between
   the liveness check and the spawn spans a `git worktree add` (`worktrees.ensure`, called at line
   114) and a file write.

**Severity.** The failure mode is exactly the one already recorded: `sessions.py:1-11` documents
three control-plane sessions sharing one worktree and one branch on 2026-08-22, and notes that
nothing collided "because two of the three were idle. That is luck, not a control." Today's change
makes that reachable again through the button that was written to prevent it.

**What is *not* racy, so the fix is not scattered.** `worktrees.ensure()` is protected by git's own
index lock — a concurrent `git worktree add` for the same path fails cleanly (`worktrees.py:85-87`
surfaces the error). Assignments to the `_*_MSG` globals are atomic under the GIL, so there is no
torn write. Two threads writing `_SUITE_CACHE` (`readiness.py:428`) is last-write-wins over two
valid documents.

**Two secondary threading defects, both `OBSERVED`.**

- `start_session_from_handoff()` writes its PowerShell to a **fixed path**:
  `_launch_script("handoff session", ...)` → `.data/launch/handoff session.ps1`
  (`local_tracker.py:148`, `180-182`). The handoff *markdown* is uniquely stamped
  (`session-%Y%m%d-%H%M%S.md`, line 143) but the script that references it is not. Two concurrent
  `/new-session` POSTs: thread A writes the script pointing at handoff A, thread B overwrites it
  pointing at handoff B, thread A's `Popen` (line 159) runs B's script. Two terminals open on the
  same handoff and one is silently lost. Lane launches do not have this bug — they are keyed per
  lane (line 119) — which is what makes it easy to miss.
- `hot_reload()` (`local_tracker.py:409-445`) calls `importlib.reload()` on four modules and then
  rewrites this module's `globals()` (lines 427-441) **while other threads may be inside
  `render()`**. `importlib.reload` re-executes module code into the live module dict. Worst
  realistic outcome is an exception in one in-flight request rather than data corruption — but
  `/reload` is a GET, so a prefetcher can trigger it.

**And one route that is worse than any of them.** `/sync` is a GET (`local_tracker.py:1599`) that
runs three subprocesses (`_GENERATORS`, lines 375-379) which **rewrite
`docs/artifacts/agent-factory.html`, a committed file**. A link prefetch can rewrite a tracked
artifact. GET must be safe; this is the least safe route on the server.

**The fix, and it is small.**

1. Make the claim atomic at the filesystem, which is the only shared medium the lanes agree on:
   ```python
   fd = os.open(_path(lane), os.O_CREAT | os.O_EXCL | os.O_WRONLY)   # fails if it exists
   ```
   `O_EXCL` is honoured on Windows via the CRT. The conflict check stays where it is; what changes
   is that the *self*-claim becomes a create-or-fail, so the last writer cannot win.
2. **Put the pid in the claim.** `Claim` currently carries `lane, since, who, note` (`claims.py:49-53`)
   and infers staleness from a four-hour timer (`STALE_AFTER`, line 39). The docstring is honest
   that this is "a convention with a staleness warning, not a lock" — but `sessions._running_pids()`
   (`sessions.py:29-49`) already knows how to answer the question the timer is guessing at. A claim
   carrying the pid of the session it belongs to can report `HELD` / `HELD-BY-A-DEAD-PROCESS` /
   `HELD-BUT-INSTRUMENT-BLIND`, which is the same four-valued discipline the contract already
   enforces everywhere else. The timer is the one place in this repo where a "could not tell" is
   collapsed into a guess.
3. **Move every mutating route to POST**, and give `Handler` a small dispatch table instead of the
   current if-ladder (`local_tracker.py:1516-1618`, 103 lines of sequential `if self.path...`).
4. **Serialise the whole mutating path behind one `threading.Lock`.** Reads stay concurrent — that
   is what threading was for. Writes are rare and human-paced; a lock costs nothing and removes the
   entire class.

### 1.3 Third: split `render()`, and put the flash message in the response

**The god-object, precisely located.** `local_tracker.py` is 1,682 lines. `render()` is lines
530–1431 — **902 lines, 54% of the file, one function, one local namespace**. Inside it:

- `if tab == "gates"` appears **twice** (lines 562 and 614) with a different block each time.
- `blocked` is bound four times to four different types: a list of 3-tuples (line 619), a list of
  session dicts (915), a list of `Claim` (852, inside a `for lane` loop), and an `int` (1087).
- `rows` is rebound at lines 592, 616, 671, 707 and 727.
- `w` is `o.append` (line 547) — 400-odd calls to a one-letter closure over a list.

That is the god-object. It wears a tidy docstring at the module level (lines 1-16, and the docstring
is genuinely good) and the tidiness has nothing to do with the function.

**The globals are the decoy — but they carry one real finding.** `_RELOAD_MSG`, `_SYNC_MSG`,
`_ANSWER_MSG`, `_CLAIM_MSG` are initialised to `None` at lines 92-95, assigned in the handlers, read
in `render()` at lines 549-560 — **and never reset to `None` anywhere**. I grepped every
occurrence; there is no clear. So:

> The page whose entire thesis is that no number may be silently stale renders four
> permanently-stale strings at the top of every tab.

A banner reading "claimed control-plane — copy its prompt and start a session" from three hours ago
sits above a header that says "measured 2026-08-23 14:02:11 local · refresh this page to
re-measure". Under threading it also leaks across viewers. And `sync_artifact()` declares
`global _SYNC_MSG` (line 389) without ever assigning it — dead, and a tell that this state was
moved once and not finished.

**The seam.** One module per zone, each `render(snap, ctx) -> str`, where `ctx` is a per-request
object carrying the flash message and the `Snapshot`. `Handler` keeps routing and nothing else.
`factory/ui/gates.py`, `ui/lanes.py`, `ui/sessions.py`, `ui/research.py`, `ui/handoff.py`,
`ui/flow.py`, `ui/goals.py` — each 80–200 lines, each with the tab-local names it actually needs,
and the four globals die of natural causes because there is a request object to put them on.

Do this **third**, not first. It is the largest diff and the lowest risk; the two above it are
correctness.

---

## 2. Verdict on the three structural facts you asked me to judge (§2.1)

### 2.1 Is `readiness.py` a god-module?

**No — but it is two files wearing one name, and the seam is not where you would guess.**

The instinct is to split thirty gates into five phase files. That would be the wrong cut and it
would break the one property that makes the board correct. `board._validate()` (`board.py:61-73`)
and `goals._validate()` (`goals.py:43-56`) both check their authored maps against
`{g.id for g in GATES}` **at import**, so a renamed gate breaks the build rather than silently
dropping out. One list is one denominator. Five lists are five denominators and a merge conflict
every time a gate moves phase. Keep `GATES` as one registry in one file. `OBSERVED`: the validation
pattern is duplicated in exactly the two modules that consume the list, which is the correct shape.

The real seam is **instruments vs. gates**. `readiness.py:80-198` is a shared-instrument layer —
`_started`, `_since`, `_basis`, `_audits`, `_events`, `_counts`, `_template`, `_blueprint` — plus
`_src`, `_grep` (`621-636`), `_suite_fingerprint` and `_age` (`359-386`). These are reusable
measurement primitives with their own failure semantics (`_audits` raises `Unmeasurable` rather than
returning `[]`, lines 126-135 — that is a policy, not a helper). They belong in
`factory/instruments.py` and should be independently tested, which today they are not.

That split is roughly 250 lines out of 1,092 and it buys something specific: **the instruments are
where UNMEASURABLE is decided**, and right now the decision to raise rather than return empty is
made in eight places with no test asserting it. That is the highest-value 250 lines in the file to
put behind a boundary.

**One instrument defect I found while reading it, which the brief did not list.**
`readiness.py:410` shells `["python", "-m", "pytest", ...]` and `readiness.py:439` shells
`["python", "-m", "factory.certify", ...]` — **bare `python`, resolved from `PATH`**. `handoff.py:52`
shells `[sys.executable, "-m", "pytest", "-q"]`. So the suite gate and the preflight can measure
**two different Python environments**, and the suite gate can measure a different environment from
the one the server is running in. On a machine with a `.venv` this is not hypothetical.
`OBSERVED` in the source; `INFERRED` as to whether it bites here, and the discriminating test is one
line: add `sys.executable` to the evidence list and compare.

**A candidate cause for the 10 / 9 / 10 instability you say you have not found.** I am not claiming
this *is* the cause — you asked me not to build an argument on that number and I have not — but it
is the only mechanism in the source that produces a time-varying verdict inside a twenty-minute
window, and it has a clean discriminating test.

`_suite_fingerprint()` (`readiness.py:359-375`) hashes the bytes of **every `.py` under `factory/`
and `tests/`**. That includes `readiness.py` itself. So:

- Any concurrent session saving any `.py` in this repo invalidates the cache.
- On a miss, pytest runs **against the tree as it is at that instant** — which, mid-save, can be a
  file with a syntax error or a half-written import. Collection error → `returncode != 0` →
  `_fail(...)` (line 425) → 9. Next request, file saved → PASS → 10.
- The result is then written back into the cache keyed on the *broken* fingerprint (lines 427-431),
  so it is sticky until the next edit.

The window is twenty minutes, the repo has another session in it (`git status` shows
`M factory/readiness.py` and `M scripts/local_tracker.py` right now), and the mechanism produces
exactly a flip-and-flip-back. **Discriminating test:** add the fingerprint's first 12 hex to the
gate's evidence — it already prints there on a *hit* (line 405) but not on a *miss*. If the 9 and
the 10 carry different fingerprints, this is it. If they carry the same one, it is not and you
should look at `_since()` windowing instead.

There is also a designed-in conflict worth naming: **the hot-reload button and the suite cache are
in opposition.** `/reload` exists so you can edit `readiness.py` without restarting
(`local_tracker.py:409-417`); editing `readiness.py` is guaranteed to miss the suite cache, which is
the single most expensive probe. The feature makes the optimisation useless exactly when it is used.

### 2.2 What does the test gap tell you about where confidence comes from?

You named eight untested modules — `board`, `claims`, `demo`, `deploy`, `handoff`, `operator`,
`schedule`, `worktrees` — and observed that two are the concurrency-safety primitives. The pattern
is sharper than that, and it is a boundary, not an oversight.

`OBSERVED`, from the test directory and the imports of each module:

| Tested (18 files, 143 tests) | What it is |
|---|---|
| `contract`, `connector_contract`, `findings`, `dispatch`, `synthesis`, `corpus`, `tasks`, `metrics`, `blueprint`, `runs`, `measurement_window`, `eval_can_fail`, `evaluator_isolation`, `research_safeguards` | **parsers and pure functions over files** |

| Untested | What it is |
|---|---|
| `claims`, `worktrees`, `sessions`, `schedule`, `operator`, `deploy`, `board`, `handoff` | **every one of them shells out to git, the process table, or a subprocess** |

The line is not "important vs. unimportant". It is **"reasons about data" vs. "acts on the world"**.
The suite certifies the reasoning perfectly and certifies none of the acting. That is the ordinary
gravity of testing — the pure half is easy — and here it has landed precisely on the safety
primitives because the safety primitives are the ones that must touch git and the OS.

Two consequences worth stating plainly.

**First, the gate that would have caught this is itself at zero.** `refuses` — "Has any gate ever
refused a run?", `readiness.py:1002-1004`, "A gate never observed refusing is decoration. Same rule
as an eval." — is at `0 of 22`. The repo has an articulated principle that a control unwatched
refusing is not a control, and its two most important controls (`claims`, `worktrees`) have never
been watched refusing. The principle is stated in the right place and applied to the wrong half of
the codebase.

**Second, the fix is not "write tests for the eight".** It is one seam: make each world-touching
module take its effect as an injectable. `worktrees._git()` (`worktrees.py:41-44`) and
`finish._git()` (`finish.py:33-36`) and `runs`'s three inline `subprocess.run` calls
(`runs.py:54, 182, 209-218`) and `schedule._git()` (`schedule.py:70-72`) are **four separate
hand-rolled git wrappers with four different timeout policies** (none, 120s, 30/60s, none). Unify
them into one `factory/git.py` with one fake, and six of the eight untested modules become testable
in an afternoon. That is a better use of the effort than eight bespoke fixtures.

`ASSUMED`, and flagged as such: I have not measured how long that would take.

### 2.3 The five state roots — single store, declared boundary, or something else?

**Declared boundary per concern. But the current arrangement is not a "fork of conventions" — it is
two different concerns sharing one resolver, and it has already produced two false greens.**

`OBSERVED`, the resolvers:

| Module | Root | Line |
|---|---|---|
| `bus` | `__file__.parent.parent / ".data" / "bus"` | `bus.py:35` |
| `claims` | `__file__.parent.parent / ".data" / "claims"` | `claims.py:35` |
| `operator` | `__file__.parent.parent / ".data" / "operator"` | `operator.py:22` |
| `worktrees` | `__file__.parent.parent / ".worktrees"` | `worktrees.py:31-32` |
| `findings` | `__file__.parent.parent / "docs" / "findings.md"` + `findings.d/` | `findings.py:24-29` |
| `runs` | **the primary worktree**, via `git worktree list` | `runs.py:46-65` |
| `handoff` | `__file__.parent.parent.parent / "aldc-launchpad" / "boot-prompts"` | `handoff.py:33` |
| `sessions` | `~/.claude/sessions`, `~/.claude/jobs`, `~/.claude/projects` | `sessions.py:26, 116, 117` |

There are **three legitimate scopes** here and they are all real:

- **LANE-LOCAL** — dies with the worktree, and *should*: the bus (correctly, and `bus.py:10-16`
  argues for it well), launch scripts, generated lane prompts.
- **MACHINE-LOCAL** — one per machine, all lanes must agree: claims, the run ledger, operator
  answers, the suite cache.
- **DURABLE** — in git, reviewed, merges with the branch: `findings.d/`, evidence, research.

The defect is that **`claims` and `operator` are machine-local concerns using the lane-local
resolver.** That is not a convention fork; it is a miscategorisation. `runs.py` already noticed and
already wrote the fix — `_primary()` at `runs.py:46-61`, with a docstring
(`runs.py:11-16`) that names F70/F71 and explains exactly this — and then kept it private to one
module.

**Two live consequences, both `OBSERVED` from the source and both worse than untidiness.**

1. **`worktrees` is blind inside a worktree, and `finish` believes it.**
   `worktrees.ROOT = REPO / ".worktrees"` where `REPO = __file__.parent.parent`
   (`worktrees.py:31-32`). Run from inside `.worktrees/certify/`, `REPO` is the *worktree*, so
   `ROOT` is `.worktrees/certify/.worktrees` — which does not exist. `existing()`
   (`worktrees.py:53-71`) resolves every path git reports against that `ROOT` and matches none, so
   it returns `{}`. Therefore:
   - `is_dirty(lane)` returns `False` for a lane with uncommitted work (line 92-93: `if p is None: return False`),
   - so `finish.checks()` (`finish.py:73`) omits "the worktree is dirty",
   - and `handoff.lane_state()` (`handoff.py:88`) gets `{}`, so the generated handoff writes
     *"no worktree; this lane was worked in the main checkout or not started"* (`handoff.py:128`)
     for a lane that has one with uncommitted work in it.

   A safety check that returns clean for a dirty tree, and a handoff that records the opposite of
   the truth. It does not bite today only because the tracker runs in the primary worktree — which
   is a property of how it happens to be launched, not a control.

2. **`claims` written from inside a worktree is invisible to the tracker.** Same mechanism: an agent
   running `python -m factory.finish` or `factory.claims` inside its own worktree writes to
   `.worktrees/<lane>/.data/claims/`, which the tracker (in the primary) never reads. The claim
   system is invisible to exactly the processes it governs.

**The change.** Promote `runs._primary()` into `factory/state.py`:

```python
def lane_local() -> Path      # this worktree's .data — the bus, launch scripts, prompts
def machine() -> Path         # the primary worktree's .data — claims, runs, operator, caches
def durable() -> Path         # the repo — findings.d, evidence, research
def registry() -> Path        # ~/.claude — sessions, jobs, transcripts
```

Every module asks for a *scope* instead of computing a path. Five one-line changes
(`bus.py:35`, `claims.py:35`, `operator.py:22`, `worktrees.py:31`, `readiness.py:_SUITE_CACHE`),
and the whole F70/F71 class stops being reachable. **And add a gate that measures it**, because
today nothing does: assert that `claims.ROOT` and `worktrees.ROOT` resolve identically from the
primary and from every lane worktree. That is a probe that can refuse, on a control that has never
been watched refusing.

**`handoff.BOOT` deserves its own line.** `REPO.parent / "aldc-launchpad" / "boot-prompts"`
(`handoff.py:33`) is a hard-coded sibling-directory path, with no existence check, no environment
override, and no gate. `write_lane_handoff` does `BOOT.mkdir(parents=True, exist_ok=True)`
(`handoff.py:107`) — so on a machine where the sibling is absent or renamed, it **silently creates
the wrong directory** and writes the handoff into it. The entire cross-repo memory mechanism depends
on a directory layout that nothing verifies. See §4.3.

---

## 3. The object model

You have: *agents, agent teams, sessions, lanes, worktrees, claims, tasks, gates, findings, runs,
research prompts, blueprints, contracts.* Here is my verdict on each, then the two that are missing.

### 3.1 Genuinely first-class, and correctly modelled

- **`Gate`** (`readiness.py:47-54`) — a falsifiable question bound to its own instrument. This is
  the best object in the repo. `question` is always a question about the *system*, `why` is always
  the consequence of not knowing, and `probe` is the instrument. Nothing else in this estate has
  that shape and it is the thing worth protecting in every refactor.
- **`Verdict` / `Result`** (`contract.py:17-25`, `readiness.py:56-65`) — four-valued, never
  collapsed, with `ContractResult.verdict` (`contract.py:73-85`) implementing the correct precedence
  (any FAIL → FAIL; else any UNMEASURABLE → UNMEASURABLE; else PASS). `Assertion.run`
  (`contract.py:52-60`) turning an unexpected exception into UNMEASURABLE rather than FAIL is
  precisely right and is the line most codebases get wrong.
- **`Finding`** (`findings.py:49-80`) — a correction as data, with four mandatory fields and a
  *conditional* fifth (`missing`, lines 65-76: a DESIGN finding must name what CHANGES). That
  conditional is a genuinely sophisticated bit of modelling and I have not seen it elsewhere.
- **`Claim`**, **`Worktree`**, **`Run`** — real, distinct, and each earning its place.

### 3.2 One name hiding two — `lane`

This is the important one, and it is why the concurrency ceiling will not move.

`Lane` (`lanes.py:70-92`) carries, in one frozen dataclass:

| Field | What it really is |
|---|---|
| `gates` | a **work definition** |
| `touches` | a **conflict key** (file locality) |
| `repo` | a **location** |
| `size` | an **estimate** |
| `model`, `model_why` | an **execution policy** |
| `prompt`, `needs_paul` | a **brief** |
| `full_prompt` (property, line 87-92) | a brief **spliced with an operator answer at read time** |

And the *id* is used, as a string, as:

- a claim key (`claims.py:71` → `ROOT / f"{lane}.json"`),
- a git branch name (`worktrees.py:80` → `lane/{lane_id}`),
- a directory name (`worktrees.py:50` → `ROOT / lane_id`),
- a session identity (`sessions._identity`, `sessions.py:143-146`, derives it from the path),
- a ledger key (`runs.report()`, `runs.py:232` — `for lane in LANES`),
- a bus channel (`bus.py:78` → `ROOT / f"{lane}.jsonl"`),
- a terminal tab title (`local_tracker.py:124`).

**Therefore two agents cannot work one lane, because the lane *is* the branch.** R8's containerisation
recommendation raises the ceiling only if the branch identity is separable from the work identity;
today it is not, and no amount of isolation changes that. This is a modelling constraint wearing a
resource constraint's clothes.

**Split it:**

- **`Workstream`** — what to do. Gates, brief, model policy, conflict set. Durable, in git,
  reviewed. Roughly today's `Lane` minus the runtime.
- **`Attempt`** — one agent's go at a Workstream. Owns a branch, a worktree, a claim, a session, a
  transcript, a cost, an outcome. Ephemeral, machine-local, and **there can be more than one per
  Workstream** — sequentially today, concurrently once containers land.

The code has already discovered this and is fighting it. `runs.history(lane)` returns a **list**
(`runs.py:163-176`) — plural, correct — and then `runs.report()` (`runs.py:228-245`) collapses it to
one row per *lane*, taking `runs[0]` and discarding the rest (line 238). The ledger knows a lane can
run more than once; the report cannot say so. And `runs.reconstruct()` (`runs.py:197-225`) has to
guess an Attempt's cost from a *directory*, because an Attempt has no identity of its own.

Give `Attempt` an id and `report()` stops lying, `reconstruct()` becomes a fallback rather than the
default path, and cost-per-outcome (which `ui-surface-inventory.md:170-172` correctly identifies as
your differentiator) becomes a division you can actually perform.

### 3.3 One name hiding two — `session`, and this one is a safety hole

`sessions.py` contains **two implementations of the same join**, written at different times, and the
safety-critical callers use the weaker one.

| | narrow | broad |
|---|---|---|
| inventory | `live_by_lane()` — `sessions.py:52-79` | `inventory()` — `sessions.py:214-262` |
| collision | `duplicates()` — `sessions.py:82-84` | `collisions()` — `sessions.py:270-280` |
| scope | **only paths containing `.worktrees`** (line 65-66) | every registered session |

`collisions()`'s own docstring says it: *"Broader than `duplicates()`, which only sees lane
worktrees. This catches any shared cwd, including the case that actually happened."*
(`sessions.py:271-274`).

**And then the guards use the narrow one.** `OBSERVED`:

- `finish.checks()` → `_sessions.live(lane)` (`finish.py:67`), and `live()` is
  `live_by_lane().get(lane, [])` (`sessions.py:78-79`).
- `local_tracker.launch()` → `_sess.live(lane_id)` (`local_tracker.py:259`).

So the pre-launch guard and the pre-finish guard **cannot see a session whose cwd does not contain
`.worktrees`** — while the Sessions tab, which is display-only, uses `collisions()` and can
(`local_tracker.py:916`).

Your own measurement is that **six sessions were sharing one directory, and it was the launchpad
repo root** (`ui-surface-inventory.md:111`, `sessions.py:105-107`). That is precisely the case the
guard is blind to and the display can see. **The instrument that decides is weaker than the
instrument that reports**, which is a specific and correctable inversion.

Collapse to one: `inventory()` is the right implementation. `live(lane)` becomes a filter over it,
`duplicates()` is deleted, `collisions()` is the only collision answer, and both guards get the
broad view. `INFERRED` cost: about 30 lines removed.

The five liveness states (`sessions.py:119-129`) are excellent and should not be touched.
`RUNNING-ATTACHED` / `RUNNING-ORPHANED` / `EXITED-RESUMABLE` / `EXITED-GONE` /
`UNKNOWN-INSTRUMENT-BLIND` is the four-valued contract applied to processes, and the note that
`--resume` on an orphan starts a *second* process on one session id (`sessions.py:122-123`) is the
kind of thing nobody writes down until it has cost them.

### 3.4 Two names for one thing — `task` and `gate`

`board.py:5-13` settles this in its own docstring: there is no task list; a gate that is not passing
*is* a task. That is correct and it is one of the best decisions in the repo.

But `factory/tasks.py` still exists — 144 lines, 5 tests, a full append-only `TaskStore` with
`OPEN / CLAIMED / BLOCKED / DONE / ABANDONED` and evidence-gated closure (`tasks.py:20-24`). I
checked its importers. **The only module that imports `tasks` is `demo.py`, and nothing imports
`demo.py`.** Same for `metrics` and `evals`: importers are `demo.py` only. `demo.py` has a `main()`
and a `__main__` guard (`demo.py:42, 84`).

So `tasks` + `metrics` + `evals` + `demo` is a **closed island of ~394 lines reachable only from a
demo entry point**. "Tasks" is on your object list because a demo uses it, not because the system
does.

That matters beyond dead code, because it means you are carrying **three status vocabularies with
no shared word**:

- `board`: `DONE / READY / BLOCKED` (`board.py:29`)
- `runs`: `FINISHED / REFUSED / ABANDONED` (`runs.py:39`)
- `tasks`: `open / claimed / blocked / done / abandoned` (`tasks.py:20`)

Three enums, two of them live, `BLOCKED` meaning "dependency unmet" in one and "agent is stuck" in
the other. Pick one vocabulary and delete the third.

### 3.5 The right primary object

Not the agent, the session, the task, or the lane. **The artefact-with-its-evidence — and the
`Decision` a human makes about it.**

The argument is your own README, quoted at `ui-surface-inventory.md:19`: *"A team of agents did the
work, and we can prove it — or we can prove we could not tell."* That is a sentence about an
**artefact** and a **proof**, not about a process. Every session manager on the market makes the
session primary because their product is process; yours is evidence, and making the session primary
would put you on their axis, where you are behind (`ui-surface-inventory.md:157`).

The practical test: what does the operator at 2am actually need to *act on*? Not "session 7 is
running". They need "this branch is green and has waited nine days for you". Session, lane, worktree
and claim are all **machinery in service of producing an artefact you can decide about**. They
belong on the screen; they are not the subject of it.

### 3.6 What is missing

**(a) `Snapshot` — the measurement scope.** §1.1. This is the biggest omission because it is three
problems in one object: latency, freshness-as-a-type, and the reason four tabs measure and discard.

**(b) `Decision` — and the APPROVE plane has no data type at all.**

Your own table (`ui-surface-inventory.md:49-54`) says APPROVE exists for "anyone, including a
non-engineer" and that what exists today is **nothing**. Every other plane has objects: DECIDE has
`Lane`/`Claim`, RUN has `Worktree`/`Session`, PROVE has `Gate`/`Finding`/`Run`. The one plane where
a human is *mandatory* has no type, no store, no ledger, and no age.

And the measured bottleneck is exactly there: two green PRs at 6 and 9 days, one agent question
unread for days (`ui-surface-inventory.md:100-101, 115-117`). **The absent object and the measured
bottleneck are the same thing.** That is not a coincidence, it is the ordinary consequence — what
has no type has no instrument, and what has no instrument has no age, and what has no age waits nine
days without anything noticing.

```python
@dataclass(frozen=True)
class Decision:
    id: str
    subject: str          # branch · PR · secret · promotion · an agent's question
    kind: str             # MERGE | GRANT | PROMOTE | ANSWER
    evidence: str         # snapshot id + contract result + cost — never a summary
    requested_at: datetime
    requested_by: str     # a lane, an attempt, or a person
    state: str            # AWAITING | GRANTED | REFUSED | EXPIRED
    decided_at: datetime | None
    decided_by: str | None
    reason: str           # required on REFUSED; optional on GRANTED
```

**Do not start this from scratch.** `operator.py` is already a one-field prototype of it: an answer
to a declared blocker, on disk, with a timestamp, with a length bound that refuses a conversation
(`operator.py:55-57`), and with `block()` (`operator.py:72-80`) rendering it into the prompt with an
instruction to *stop rather than improvise* if the answer does not actually resolve the blocker.
That last touch is better than most approval systems manage. Generalise `operator.py`; do not
replace it.

Note also that `bus.KINDS` already contains `"blocked"` — *"I need a human; other lanes should not
wait on me"* (`bus.py:46`) — so the *event* exists and there is nowhere for it to go.

**(c) Teams — no, and here is what you actually want instead.**

You asked whether a team should be first-class with composition, roles, a shared budget and a
lifecycle. **Not yet, and probably not ever in that shape.**

Against: it would be the fourth thing to keep in sync (§3.4 already shows three status vocabularies
drifting), it needs a lifecycle nobody has asked for, and the measured concurrency is three. A team
object with roles would be a taxonomy imported from org charts, and R11 already covered the vendor
version of that question.

But there *is* a missing object that people reach for the word "team" to describe, and it falls out
of the two above without a new lifecycle:

> **A `Campaign`: the set of `Attempt`s that share one `Snapshot`, one budget, and one `Decision` at
> the end.**

That is what "prove a team did the work" actually needs. It is a **provenance** grouping, not an
org-chart grouping. Composition is emergent — you learn which attempts belonged to it by reading the
ledger, not by declaring membership up front. Roles are already carried by `Workstream.gates`.
Budget is a sum over `Attempt.cost`, which `runs.cost()` (`runs.py:88-136`) can already compute from
transcripts. And the lifecycle is the `Decision`'s: a Campaign is over when someone decides.

This is also the honest reading of your own domain: sessions here are ephemeral and are identified
by their **opening prompt** rather than by a name (`sessions.py:169-175`, and the finding at
`sessions.py:96-99` that five live sessions shared one name). Nothing durable about a "team" exists
to be modelled. What is durable is the set of attempts that produced a given artefact.

---

## 4. Repo structure

### 4.1 One package, 29 flat modules, 8.7k lines — right at this size, and the seam is not by plane

**Keep it flat for now.** Your own measurement says internal coupling is almost flat, and I verified
the shape: `finish.py` is the only hub (imports bus, claims, findings, runs, sessions, worktrees —
`finish.py:21-26`), and `board`/`lanes`/`flow`/`goals`/`handoff` all depend on `readiness`. Splitting
a flat graph buys nothing and costs every import path.

At 30k, the seam I would cut on is **not** by plane. Splitting decide/run/prove/approve would put
`claims` (DECIDE) and `worktrees` (RUN) in different packages when they are two halves of one
transaction, and it would leave `readiness` straddling all four with nowhere to live.

Cut on **"does this touch the world"**, because §2.2 shows that is already the line your test
coverage found:

```
factory/
  model/        pure, fully testable with no fixtures
                contract  findings  dispatch  synthesis  goals  board  lanes
                flow  blueprint  metrics  connector_contract  corpus
  instruments/  the measurement primitives lifted out of readiness.py (§2.1)
  adapters/     git · process table · subprocess · filesystem — one fake each
                worktrees  claims  sessions  runs  schedule  operator  bus  deploy
  gates/        readiness.py — the registry, one file, one denominator
  ui/           the seven tab renderers + the request object (§1.3)
```

Under that split, the eight untested modules are exactly `adapters/`, and the remedy is one fake per
adapter rather than eight bespoke fixtures. The boundary and the coverage gap become the same line,
which is what makes a package boundary worth having.

### 4.2 Library / CLI / service — `scripts/` is not a boundary, it is a second package

`OBSERVED`:

- `scripts/local_tracker.py` is **100,352 bytes**, imports **17** modules from `factory`
  (`local_tracker.py:31-48`), and is imported *by the test suite*
  (`tests/test_tracker_routes.py:16`: `from scripts import local_tracker as lt`).
- `scripts/` has an `__init__.py` (empty, `scripts/__init__.py`), so it already *is* a package,
  just one that is named as though it were a bin directory.
- `local_tracker.py:29` does `sys.path.insert(0, ...)` to reach `factory` — the tell that the
  boundary is fictional.
- It imports `factory.dispatch` **twice under two names**: `as dispatchlib` at line 43 and `as disp`
  at line 48, both used (line 1152 and line 1220). Small, but it is what a file looks like when two
  people extended it without either reading the top.

**The boundary that is real, and worth keeping:** `evaluator_service/` as a separate top-level
package. That separation is *load-bearing*, not stylistic — the `isolated` gate
(`readiness.py:990-992`: "Is the evaluator a principal the agent cannot impersonate? Tamper-evidence
is not a trust boundary; a separate directory is not either") is about exactly this. Do not fold it
in. If anything it should move further out.

**The boundary that is fictional:** `scripts/`. Fix:

- `local_tracker.py` → `factory/ui/` (a package inside the library, split per §1.3), served by
  `python -m factory.ui`.
- `scripts/` keeps only genuine one-shot generators: `build_figure_lastwrite.py`, `build_plan.py`,
  `build_tracker.py`, `build_r*_pack.py`, `render_pass.py`, `check_svg_text.py`, `file_answers.py`,
  `pin_corpus.py`.
- The CLI surface is already `python -m factory.X` — nearly every module has a `main()`. Keep that
  and stop treating `scripts/` as a home for anything long-lived.

Note that five `build_r*_pack.py` scripts exist (`build_r8`, `build_r13`, `build_r14`, `build_r16`,
plus `build_plan`/`build_tracker`/`build_figure`). Four near-identical evidence-pack builders is a
parameter, not four scripts.

### 4.3 Monorepo — the split is sound, and it is doing harm in exactly one checkable place

Splitting code (`agent-factory`) from evidence and session memory (`aldc-launchpad`) is defensible:
the evidence genuinely is cross-repo — `aldc-launchpad/boot-prompts/` carries handoffs for
`clients`, `client-a`, `core_api` and `prefect-connectors` too, and duplicating it per repo would be
worse.

But the *mechanism* joining them is a hard-coded relative path with no verification:

```python
BOOT = REPO.parent / "aldc-launchpad" / "boot-prompts"     # handoff.py:33
...
BOOT.mkdir(parents=True, exist_ok=True)                    # handoff.py:107
```

`OBSERVED`: no existence check, no environment override, no gate. `mkdir(parents=True)` means that
on a machine where the sibling is missing or named differently, the handoff is written into a
**newly created wrong directory** and reports success. Compare `readiness.py:35-37`, where the
cross-repo dependency on `prefect-connectors` *is* overridable (`$PREFECT_CONNECTORS`) and *is*
checked (`_audits()` raises `Unmeasurable` naming the env var, `readiness.py:126`).

The same treatment applied to two cross-repo paths, one done right and one not. So the answer to
"is that separation why nothing can see everything" is: **the separation is fine; the join is
unmeasured.** Make `BOOT` overridable, make it raise rather than `mkdir` when the target's parent is
absent, and add a gate that measures whether the boot-prompt directory a handoff would be written to
is the one that actually holds the boot prompts. That is one probe and it closes a silent-loss path.

### 4.4 Documentation that code depends on — right, and the best idea in the repo

`docs/research/` is globbed by `dispatch.prompts()` (`dispatch.py:78`) and `synthesis.filed()`, and
`tests/test_synthesis_current.py` fails when the record drifts. **This is correct and I would
defend it.** A record that nothing reads is the failure mode this repo exists to fight; making the
record load-bearing is the only reliable way to keep it current. `dispatch.py`'s five-state model
(`ANSWERED / UNDISPATCHED / IN_FLIGHT / STALE_STATUS / UNKNOWN`, `dispatch.py:61-65`) is the
four-valued contract applied to paperwork, and the reasoning at `dispatch.py:27-32` — report queue
depth, gate only self-contradiction — is exactly the right line.

**The flaw is that the *directory* is untyped and the *filename* is doing the typing.** Generated
evidence packs live in `docs/research/` and match the prompt glob, so both consumers special-case
them:

- `dispatch.py:84`: `if f.stem.upper().endswith("-EVIDENCE-PACK"): continue`
- `local_tracker.py:1205-1206`: the same string test, again

And `dispatch.py:82-83` admits the guard is fragile: *"Today the real prompt wins only because
`R13-architecture-…` sorts before `R13-evidence-pack` and this loop uses setdefault — rename either
file and the pack becomes the prompt, silently."*

**Fix:** move generated packs to `docs/research/.packs/` (they are already gitignored individually —
four separate `.gitignore` entries, one per pack, which is itself a smell) and delete both
special cases. Documentation-as-data works; it needs the *location* to carry the type, not the name.
One directory, one rule, no string-suffix guards.

`docs/` at 11 MB / 83 files is not a problem. It is 8.6 MB of artifacts and evidence, and evidence
is the product.

---

## 5. The AMT proposal (§4b) — which ideas survive contact with the code

You asked which of the five survive. **Two, one of them not in the form proposed. Three do not.**

### Survives, and is the highest-value thing on the list — the Interrupt Inbox

It survives because **its data already exists and its absence is already measured.**
`jobs/<id>/state.json` carries a `needs` field in plain English; `sessions.py:252` reads it; the
comment beside it says *"the question nobody was reading"*; `inventory()` sorts blocked-first
unconditionally (`sessions.py:258-261`); and `sessions.py:111-113` records that four agents were
blocked on written questions with no surface showing them — *"Not alarm fatigue, it is alarm
absence."*

That is the strongest possible case for a feature: the event is emitted, the reader exists, the cost
of not having it is measured in days.

But it should not be built as an "inbox". Build it as the **`Decision` queue** (§3.6b), with an
agent's question as one `kind` alongside merge, grant and promote. A separate inbox for agent
questions would be the sixth surface (`ui-surface-inventory.md:71`) and would split the operator's
attention across two lists that are answering the same question: *what is waiting on me.*

### Survives in a different form — Collision Detection

Half-built and pointed the wrong way. `sessions.collisions()` (`sessions.py:270-280`) already
detects it and the Sessions tab already renders it (`local_tracker.py:944-955`). What is missing is
not detection — it is **making detection load-bearing**, per §3.3: the guards use the narrow
instrument and the display uses the broad one.

So the deliverable is not a feature called Collision Detection. It is three lines: `finish.py:67`
and `local_tracker.py:259` switch to the broad instrument, and `duplicates()` is deleted. A feature
name here would obscure that the work is a one-line correction to an existing control.

### Does not survive — Terminal Genome

It is the version hash under a better name, and the version hash covers **0 of 15 dimensions**
(`readiness.py:987-989`, `ui-surface-inventory.md:167-169`). Giving an unbuilt thing a second, more
evocative name makes it *harder* to notice it is unbuilt — which is the exact failure class this
repo was founded on ("a gate that reported PASS while measuring nothing", §8 of the brief). Build
the fifteen dimensions; do not rename the zero.

### Does not survive — Resurrection Capsules

`claude --resume` already exists, the tracker already surfaces it with the right command and the
right cwd (`local_tracker.py:994-997`), and `sessions.py:122-123` records the thing a "capsule"
would hide: *"`claude --resume` will refuse, and forcing it starts a SECOND process on one session
id."* A capsule abstraction over a mechanism whose main hazard is *starting a duplicate* is a
footgun with a friendly name — and starting a duplicate is the defect you already hit (F73).

### Does not survive — Agent Radar

A radar encodes **distance and bearing**. There is no distance here. Twelve sessions have no
spatial relation to one another; what they have is an **age** and a **state**, and both are ordinal.
A sorted list carries ordinal data better than any position on a circle, and `inventory()` already
sorts blocked-first (`sessions.py:260-261`) — which is more information than a radar can show,
because a radar has no way to say "this one first".

This is the general test I would apply to the whole document: **a visualisation must encode a real
dimension of the data.** Radar encodes position; you have none.

### The meta-point

The document proposes five features and two of them are things you have already built and not
wired up. That is the signal worth keeping: it was written without measuring against the repo, and
it duly re-proposed the repo. Treating it as a vision to argue with was the right call. The argument
is: *the interesting work here is not new surfaces, it is making three existing instruments
load-bearing.*

---

## 6. ⭐ The design

### 6.1 The thesis: the screen answers "what is waiting on me", not "what is happening"

At 2am with twelve sessions across four repos, "twelve sessions are running" is not information.
**It is the resting state.** A screen that leads with it has spent its most valuable real estate on
a constant.

What is *not* constant, and what your own measurement says is the actual failure:

- two green PRs waiting **6 and 9 days** for a human (`ui-surface-inventory.md:101, 120`),
- an agent blocked on a written question nobody read (`sessions.py:111-113`),
- and the observation that items 1–5 in that inventory were legibility problems now mostly fixed,
  while **item 6 is a throughput problem no surface touches** (`ui-surface-inventory.md:125-126`).

So the design brief is not "make twelve agents legible". It is **"make the human the fastest
component"**. Everything below follows from that, and it is also why the primary object is the
`Decision` (§3.5) and not the session.

### 6.2 Information architecture

**Three zones, one column, in this order. No tabs.**

```
┌──────────────────────────────────────────────────────────────────┐
│  2 waiting on you · 1 blocked 41m · 9 running · 1 unmeasured     │  ← one line
├──────────────────────────────────────────────────────────────────┤
│  WAITING ON YOU                                                  │
│  ▸ merge   prefect-connectors #128  green · 9d        [Review]   │
│  ▸ answer  control-plane            "…?"    · 41m     [Answer]   │
├──────────────────────────────────────────────────────────────────┤
│  RUNNING                                          9 sessions     │
│  ● control-plane  af/.worktrees/control-plane  ▁▃▅▇▅▃▁▁    3m    │
│  ● R14-answer     agent-factory                ▇▇▇▇▇▇▇▇   12s    │
│  ◌ grain          client-a                       ▁▁▁▁▁▁▁▁   47m    │
│  … 6 more                                                        │
├──────────────────────────────────────────────────────────────────┤
│  EVIDENCE                        10 of 30 gates · measured 4s    │
│  (collapsed by default)                                          │
└──────────────────────────────────────────────────────────────────┘
```

**The first line is a sentence with numbers in it, not a chart.** Three seconds of orientation is
one fixation, and one fixation is one line of text. Not four tiles, not a donut. You said it
yourself: *"We would rather read one number than four charts."* This is that, taken literally.

**Zone 1 — WAITING ON YOU.** Zero to n rows. A merge, a secret grant, an agent's question, a
promotion. Each row: what it is · what it's for · how long it has waited · one primary action.
**Sorted by age, descending, always.** No other sort. The scan you actually perform at 2am is down
the age column, and any other sort order defeats it.

**Zone 2 — RUNNING.** One row per session. A table, not cards. Twelve rows at 32px is 384px — above
the fold on a laptop. Twelve cards is three times that and you are scrolling to count.

**Zone 3 — EVIDENCE.** The gate board, the flow graph, the ledger, cost. Collapsed. This is what you
open when someone asks *"prove it"*, and that is not a 2am activity. It is not less important — it
is the product — but it is not the thing that decides what to do next.

**What should never be shown unless it is wrong.** Every one of these is on the first screen today:

| Currently first-screen | Where it should live |
|---|---|
| cost totals, token counts (`local_tracker.py:753-758`) | EVIDENCE, or a row when over budget |
| velocity / schedule report (`local_tracker.py:1050-1058`) | EVIDENCE |
| worktree cleanliness (`local_tracker.py:705-715`) | a row, only when dirty **and** the lane is closing |
| the parallel set (`local_tracker.py:685-719`) | on the start action, not standing |
| "Past runs — 0 of 5 lanes have a history" (`local_tracker.py:730-735`) | EVIDENCE |
| the gate progress bar (`local_tracker.py:467, 587`) | delete — see §6.5 |

**The resting state.** Most of the time everything is fine, and a dashboard that looks alarming at
rest teaches people to ignore it. So the resting state is:

```
Nothing waiting on you. You cleared the last one 3h ago.
9 running · all measured · 10 of 30 gates
```

Same typography, same position, same shape as the busy state — just different numbers. **No green
banner, no checkmark, no celebration graphic.** The reward for an empty queue is that the page is
short. That is a reward that still works on the two-hundredth viewing.

### 6.3 Hierarchy and rhythm

The existing CSS (`local_tracker.py:451-510`) is honestly good: 15px/1.6 body, a monospace subline,
a 2px ink rule under the header, restrained colour. What breaks it is that **everything is a `.par`
box with an `<h3>`**. The Lanes tab renders six-plus bordered boxes at identical visual weight
(lines 677, 685, 730, 784, 811), so nothing is primary and the eye has no entry point.

**Type scale — four steps, and one of them is a rule about meaning:**

| Step | Size | Use |
|---|---|---|
| display | 28px / 1.15 / -0.02em | the one-line summary, and zone headers |
| body | 17px / 1.5 | a row's human-readable subject |
| meta | 15px / 1.5 | supporting prose |
| **machine** | **12.5px mono** | **ids, paths, ages, verdicts, hashes — and nothing else** |

That last row is the highest-leverage rule on this page: **if it is monospace, it came from an
instrument.** A reader can then tell measurement from authorship pre-attentively, which is a
distinction this whole project is about and which the current page carries only in prose.

**Density and alignment.** One left rail, four fixed columns:

```
x=0     x=28        x=140                            right
│       │           │                                    │
●   control-plane   what it is doing                   41m
```

- status glyph at x=0 — so "everything normal" is a **straight vertical line of identical marks**
  and any deviation breaks the line without being read. This is the glass-cockpit technique (§6.7)
  and it is worth more than colour at 2am.
- **age right-aligned against the rule.** The single highest-value alignment decision here, because
  the ages are the sort key and right-alignment makes the digits stack.

**Rule weight carries hierarchy; boxes do not.** 2px ink under a zone header, 1px hairline between
rows, **no border on anything else**. Reserve a border for the one thing that is wrong. Today
`--rule` borders everything (`.phase`, `.g`, `.t`, `.par`, `.chip`, `.count`, `.sz`, `code`), so a
border carries no information at all.

**Whitespace.** 34px between zones, 0 between rows. Zones separate; rows fuse into one block you
read as a shape rather than as twelve things.

**Twelve rows staying scannable** comes from this and nothing else: fixed columns, no wrapping (the
subject truncates with the full text on hover — `sessions._topic` already caps at 90 chars,
`sessions.py:169`), one glyph column, one age column. No zebra striping — the hairline is enough and
striping adds a second visual rhythm competing with the glyph column.

### 6.4 Colour with a job — and the UNMEASURABLE problem

**The mistake every palette makes is putting UNMEASURABLE on the green → amber → red axis**, where
it reads as "somewhere between pass and fail". It is not on that axis at all. `PASS` and `FAIL` are
claims about the **subject**. `UNMEASURABLE` is a claim about the **instrument**. Amber says
"nearly bad". The true statement is "there is nothing here to read".

**So: two channels, not one.**

- **Hue encodes the subject's verdict.** Two hues. Green, red. That is the whole hue budget.
- **Treatment encodes the instrument's state.** Measured → saturated and filled. Not measured →
  achromatic, hollow, hatched.

`UNMEASURABLE` therefore renders **colourless**: a hollow mark with a 45° hatch, in a neutral that
sits at the same lightness as body text. It cannot be mistaken for a warning because it has no
warning hue. `NOT_RUN` gets the same neutral at lower opacity with a dotted outline — *nothing has
looked yet* versus *something looked and could not see*.

And **the glyph is never optional.** `flow.py:41-46` already does this correctly — `● ■ ◆ ○`, with
the comment that `◆` is "deliberately not a warning shape". Extend it: the glyph must appear
everywhere, not only in the SVG. Today `.chip` (`local_tracker.py:478-481`) is colour-only, so the
one place the four verdicts appear most often is the one place a colour-blind reader cannot
distinguish them.

**Tokens, both themes, contrast against the stated ground:**

```
                       light  #faf9f7            dark  #12120f
pass                   #1a6b45   5.9:1           #6ecf9a   8.4:1     ● filled
fail                   #a52e1a   6.4:1           #ff8a6b   8.0:1     ■ filled
unmeasurable           #6b6759   5.1:1           #9a9587   6.6:1     ◆ hollow + 45° hatch
not_run                #a19c8c   2.9:1 *         #5f5c52   3.1:1 *   ○ dotted
accent                 #2b4c9b   7.2:1           #8fb0f5   8.9:1
ink / ink2 / ink3      unchanged — the existing values are well chosen

* non-text use only. The label beside a NOT_RUN mark is set in ink3, which meets 4.5:1 in both.
```

Every text-bearing token clears 4.5:1 in both themes; pass/fail/accent clear 4.5:1 as *graphical*
marks too, so the glyph works without its label.

**The one token I would change is `--unmeas`.** It is currently `#a06a12` in light and `#e0aa4a` in
dark (`local_tracker.py:453, 455`) — amber, in both. That is a semantic error, not a taste
preference: the page's own footer says *"UNMEASURABLE is not a pass"* and its flow legend says it
is *"not a worse FAIL"* (`local_tracker.py:1107-1110`), and then the colour says warning.

**And spend the accent on exactly one thing per screen:** the primary action in WAITING. Nowhere
else. Today `--accent` is used for `.st.ready` chips and `.par` borders (`local_tracker.py:498, 506`),
which spends the only attention-grabbing colour on ambient state.

### 6.5 Motion that encodes something

Four places motion earns its keep here. Each one is a **measurement**, not a transition.

**(1) Age — the only continuously-changing true value on the page.** A question blocked at 41
minutes is a *different fact* at 42, so a static render is stale the moment it paints. The age
column increments live on a 60-second tick (not `requestAnimationFrame` — nothing here moves faster
than a minute). And the row carries a **time-proportional hairline** across its left rail, growing
against a stated threshold: a question is expected answered within an hour, so the hairline crosses
the row over that hour and, on completing, the row gains its border.

Nothing pulses. Nothing blinks. **The bar's geometry *is* the number**, so if you disagree with the
threshold you can see what you are disagreeing with. This passes the "would look identical if the
numbers were different" test literally — the same test `flow.py:6-9` already applies to its diagram
and passes.

**(2) Re-measurement — the old value stays.** When a value is being re-derived, the existing value
**remains on screen** and its mark thins to a 1px outline for the duration. No skeleton, no spinner,
no dimming. You keep reading the old number and you can see it is being replaced.

When the new value lands: **no animation if it is the same, a 400ms crossfade if it changed.** That
one rule turns the page's motion into a diff. Over a long night, what moves is exactly what changed,
and you learn to trust stillness.

**(3) Going quiet — the absence is the shape.** A session's activity is already measurable:
`runs.cost()` reads `timestamp` off every transcript record (`runs.py:109-112`). So each running row
carries a 24-cell sparkline of the last two hours. When the cells stop, the line flattens. **No
colour change, no alert** — a flat line at the right-hand end of a sparkline is unmistakable at a
glance and costs no attention when it is not there.

This is also how "quietly burning tokens on a loop" becomes visible **without inventing a loop
detector**: a loop looks like perfectly regular activity with a flat commit count, and both figures
are already measured (`runs.cost()` tokens versus `git rev-list --count`, `runs.py:212-216`). Two
sparklines, one over tokens and one over commits, diverging. Nothing needs to classify anything.

**(4) Arrival — 200ms of height, and nothing else.** A new WAITING item expands into place. No
slide, no highlight-fade, no toast. The list got longer; that is the entire message.

**Where motion is noise here, specifically:**

- **The gate progress bar** (`local_tracker.py:467, 587`). A bar for "10 of 30" implies a
  trajectory, and `schedule.py:20-24` **explicitly refuses to project one** because the denominator
  is still growing (13 → 30 while passes went 1 → 9). The bar contradicts the module's most
  carefully argued refusal. Delete it; the words already say it.
- **Any animated "measuring…" state.** The entire latency budget exists so that state does not
  happen. Animating it makes it feel designed-in.
- **Tab transitions** — there are no tabs in this IA.
- **Hover animation of any kind.** Twelve rows means twelve accidental hovers per scan.

### 6.6 Delight that survives the tenth viewing

**Earns its place:**

- **The empty state names the last decision.** *"Nothing waiting. You cleared the last one 3h ago."*
  You get the small reward of having cleared it, in the same shape and position as the busy state,
  without a graphic you will resent by Thursday. And it is *informative*: knowing the queue has been
  empty three hours is different from knowing it is empty.
- **The age is copyable as a sentence.** Click a row's age and the clipboard holds
  *"control-plane has been blocked 41m on: <the question>"*. At 2am that goes straight into Slack.
  This is a flourish that gets **more** useful with repetition, which is the test. The pattern is
  already proven in this codebase — `data-copy` (`local_tracker.py:1411-1429`) is used seven times
  and the "copied" label reverting after 1200ms (line 1417) is exactly the right amount of feedback.
- **Every number's tooltip is its provenance, not its definition.** Hovering `10 of 30` gives
  `readiness.measure() · 4.1s ago · connectors C:\…\prefect-connectors · suite cached 2m`. That is
  the repo's entire thesis rendered as a hover, and it costs nothing at rest. `_basis()`
  (`readiness.py:114-118`) already composes exactly this string; it currently goes into an evidence
  bullet where nobody looks.

**Becomes friction:**

- **A confirm dialog on a reversible action.** `/release` is reversible (`claims.release` returns
  `False` rather than raising when there is nothing to drop — `claims.py:128-135`, and the docstring
  is right about why). A confirm is a tax paid a hundred times to prevent an event that costs five
  seconds.
- **Toasts.** They are `_CLAIM_MSG` in disguise: a message appearing somewhere other than where the
  change happened. And the measured outcome of that design here is that it **never leaves**
  (§1.3). Put the result *in the row that changed*, where it is self-evidently about that row and
  disappears when the row re-renders.
- **A "last updated: just now" ticker in a corner.** Decoration pretending to be freshness. Freshness
  belongs on each value (§6.8), not on the page.
- **Sound.** At 2am with twelve sessions, any sound is a sound you disable on night two — and then
  the one that mattered does not play. If you want an out-of-band channel, it should be OS-level and
  should fire on exactly one event: a `Decision` crossing its threshold.
- **Sparkline animation on load.** Draw them instantly. They are data, not an entrance.

### 6.7 The emotional shape of failure

Three principles, each following from something you have already measured.

**(1) Failure is stated about the system, never about the person.** *"The cap did not refuse"* —
not *"you have not implemented the cap"*. Your gates already do this: every `Gate.question` is a
question about the system (`readiness.py:945-1041`), and every `why` is a consequence rather than an
accusation. The design job is not to undo that in the UI. It is easy to undo — a "0 of 30 complete"
progress bar reads as a report card, which is one more reason to delete it (§6.5).

**(2) The first real refusal must be unmistakable exactly once, and then become ordinary.**
`0 of 22` gate events were ever a refusal, so the first one has **no precedent to be graded
against** — and a first-ever event rendered as an ordinary red row will read as a bug in the tool
rather than as the tool working.

So a refusal does not join the WAITING list. It takes the full width above it, once, with its own
negative control stated:

> **The cap refused run 23 after 3 attempts.**
> This is the first refusal ever recorded — 22 prior gate events, 0 refusals.
> The control worked. Nothing is wrong.

That framing turns the first refusal into **evidence the control works**, which is exactly what it
is, and the opposite of an incident. On the second refusal it becomes an ordinary row and the banner
never returns. Designing the transition from "novel" to "normal" explicitly is the thing that stops
this from becoming crying wolf: the loud treatment is spent once, deliberately, on the event it was
reserved for.

**(3) Never cry wolf about the instrument.** `UNMEASURABLE` must never use the failure treatment
(§6.4), and its caption must be the **instrument's** words, not the subject's.
`readiness.py:126` already produces exactly the right sentence — *"no audit directory at …, set
`$PREFECT_CONNECTORS`"* — a statement about a missing instrument with the remedy attached. It just
needs not to be coloured like a problem with the work.

The general rule: **red is reserved for a thing that is measurably wrong with the subject.** Nothing
about the instrument, the environment, the config or the queue ever gets it. If red appears more
than about twice a week it has stopped meaning anything, and with 30 gates at 10 passing that is a
live risk today.

### 6.8 Freshness that is instant and never lying

**The tension dissolves the moment freshness stops being a property of the *page* and becomes a
property of each *value*.** A page-level "last updated" forces the choice between instant and honest,
because one timestamp has to describe thirty numbers of thirty different ages. A value-level age does
not.

Three rules.

**(1) Every rendered number is a `(value, measured_at, basis)` triple — as a type, not a
convention.** This is `Snapshot` from §1.1: the design requirement and the performance fix are the
same object. **A renderer that receives a bare `int` cannot render it.** That is what makes the
constraint enforceable rather than aspirational — today the rule is upheld by a comment
(`local_tracker.py:64-70`, and it is a good comment) and by everyone remembering.

**(2) Age is expressed by decay of the mark, not by a printed timestamp.** A value measured within
the last five seconds is set in full ink. As it ages, **the number itself does not change at all**
and a hairline beneath it recedes. Nothing greys out — greying implies invalid, and a two-minute-old
number is not invalid. Nothing re-flows — re-flow at 2am is the enemy. No timestamp string competes
for the 12.5px row. The printed basis appears on hover and on focus.

**(3) A value never measured renders as its instrument's sentence, never as a dash.** `—` is the
collapse this project exists to stop. `runs.py:40, 223` already gets this exactly right —
`NOT-RECORDED` is a distinct basis from zero, and `local_tracker.py:734-735` renders it as a
sentence. **The design rule is that there is no code path anywhere that turns a basis into a blank.**

**And the system-level resolution: serve stale, re-measure behind, mark the difference.**

The page paints from the last `Snapshot` in about 50ms, with every mark carrying its true age. A new
`Snapshot` is taken concurrently. When it lands, only the values that changed animate (§6.5 rule 2).

This is legitimate **here and only here**, because the age is visible on every mark, so a stale value
is never *presented* as fresh. And I want to put the strongest version of this argument on the
record, because it cuts against a rule you hold hard:

> **The no-cache rule is currently producing staler information than a labelled cache would.**
>
> A page that takes 10–19 seconds is a page you refresh less often. The operator opens it, waits,
> reads, and does not re-open it for twenty minutes — so the numbers they act on are, in practice,
> minutes old and *unlabelled*, because the header timestamp describes when the render started, not
> how old any individual value is now. A page that paints in 50ms from a 4-second-old snapshot,
> with the age on every mark, is showing them **fresher** data and **labelled** data.
>
> The rule you actually want is not "never cache". It is **"no unlabelled stale numbers"** — which
> is what §7 of your own constraints says, and what the suite-cache gate already implements
> correctly by putting the age *inside the headline string* (`readiness.py:392-406`). Generalise
> that; do not forbid it.

That resolves the tension without dropping either half: instant, because you paint from a snapshot;
never lying, because the snapshot is an object that knows its own age and every mark derived from it
inherits it.

### 6.9 Interfaces that get this right, and the technique — not the vibe

- **Linear — optimistic local mutation with a server-reconciled log.** The row changes *before* the
  round-trip; if the server disagrees, the row reverts **in place** with the reason attached to that
  row. It is not that Linear is fast; it is that the feedback and the failure both land where the
  action was. Directly applicable: `/claim` today is a 303 → full 10-second re-render → global
  banner (`local_tracker.py:1586-1597`). One `fetch` and an in-row revert would change how this page
  feels more than any other single change.
- **Linear — the command palette as the only navigation.** No nav bar to keep in sync. With seven
  tabs, a `TABS` constant (`local_tracker.py:81-84`) and a test asserting the nav has not lost one
  (`test_tracker_routes.py:24-28`), that is a maintenance surface you can simply delete.
- **GitHub checks — neutral is a *fourth* state solved with glyph and neutrality, not a third
  colour.** A neutral check is a grey circle; a skipped one is a grey circle with a slash; neither
  blocks the merge button and both stay visible. That is a two-valued system that discovered it
  needed four and solved it without adding hue. Direct precedent for the `UNMEASURABLE` treatment in
  §6.4, and it has been load-bearing at enormous scale.
- **`gh pr status` — your queue first, everything else after, in twelve lines.** It prints what is
  waiting on *you* before what exists, and it fits on one screen. That is Zone 1, proven at exactly
  this scale, in a tool you already have.
- **Datadog / Grafana — take the sparkline-in-the-row, refuse the tile grid.** Twelve tiles at equal
  weight is the same failure as twelve `.par` boxes. The sparkline-inside-a-table-row is their good
  idea and it is the one I have used in §6.5(3).
- **A glass-cockpit primary flight display — the resting state is a memorised *shape*.** Horizon
  level, needles at twelve o'clock: deviation is detected pre-attentively, before any value is read.
  That is the argument for the fixed glyph column in §6.3 — twelve identical marks form a straight
  vertical line, and a break in the line is seen before it is read. At the fourteenth hour that is
  worth more than colour, because colour discrimination degrades with fatigue and edge detection
  does not.

`REPORTED` for the Linear and GitHub behaviours (widely documented, and I have used both, but I have
not read their source). `OBSERVED` for `gh pr status` output shape. `INFERRED` for the flight-display
analogy — the perceptual claim about pre-attentive edge detection is well established, the
application to this table is mine.

### 6.10 What the design implies about the launcher

One consequence of the settled no-terminal constraint, stated because it changes the design rather
than the constraint.

If the terminal is an escape hatch launched on demand, then **the launcher is a first-class surface
even though the terminal is not** — and yours is already good. `_launch_script`
(`local_tracker.py:172-217`) writes a `.ps1` rather than a `-Command` string because `wt` splits on
semicolons (line 176-178); it clears `CLAUDE_CODE_CHILD_SESSION` so the spawned lane keeps its
transcript (lines 198-203); it passes `--model` so the banner cannot advertise a model the process
is not running (lines 185-190); and it sets a per-session name so twelve terminals are not all
called the same thing (lines 191-196). Every one of those is a lesson that cost something.

The design implication: **give the launch action the same treatment as a `Decision`.** A row, an
explicit primary action, and the resulting terminal's identity echoed back into the RUNNING zone
within one tick — so the operator sees the thing they launched appear in the list rather than
having to go and look. That closes the loop the escape-hatch model otherwise leaves open, and it
does it without putting a terminal on the page.

---

## 7. What I would refuse to build, and what to delete

### 7.1 Refuse

| | Why |
|---|---|
| **A terminal grid** | §0 settles it, and `ui-surface-inventory.md:153` is right: it competes on a commodity axis and would be the sixth surface. |
| **Terminal Genome / Resurrection Capsules / Agent Radar** | §5. Two rename unbuilt things, one encodes a dimension the data does not have. |
| **A team object with roles, composition and a lifecycle** | §3.6c. It is a fourth thing to keep in sync when three are already drifting. `Campaign` instead. |
| **A "synthesize" button** | Already refused, correctly, and the reasoning at `local_tracker.py:1268-1274` is better than anything I would write: *"synthesis is judgement, and a button that cannot exercise it would either fake it or do nothing."* |
| **An ETA or a burndown chart** | `schedule.py:20-24` refuses to project because the denominator is growing. Any chart implying a trajectory contradicts the module's most careful reasoning. |
| **Batch approval of anything** | Hard rule in §7 of the brief. Worth restating because a `Decision` queue is precisely the shape that invites a "select all". Do not build the checkbox. |
| **Alerting before the `Decision` object exists** | An alert on an object with no age, no state and no store is the 233-diagnoses/0-fixes shape again. Model it, then watch it. |

### 7.2 Delete

| | Evidence |
|---|---|
| `factory/tasks.py` · `metrics.py` · `evals.py` · `demo.py` | ~394 lines reachable only from `demo.py`, which nothing imports (§3.4). `tasks` is also the third status vocabulary. |
| `factory/deploy.py` | No importers. Imports `blueprint`, which then also becomes orphaned. |
| `duplicates()` — `sessions.py:82-84` | Superseded by `collisions()`, and keeping it is what lets a guard use the weaker instrument (§3.3). |
| The duplicate dispatch import — `local_tracker.py:43` **and** `:48` | Same module, two names, both used. |
| `global _SYNC_MSG` — `local_tracker.py:389` | Declared, never assigned. Dead. |
| The gate progress bar — `local_tracker.py:467, 587` | §6.5. It asserts a trajectory `schedule.py` refuses to assert. |
| `tracker.html` at the repo root | Gitignored but present on disk, and its existence invites reading a stale snapshot as current state — which is the failure the module docstring opens by warning about. |
| The two `-EVIDENCE-PACK` string guards — `dispatch.py:84`, `local_tracker.py:1205` | §4.4. Move the packs to a typed directory instead. |

### 7.3 Fix, in this order

1. `claims.claim()` → `O_EXCL`, plus one lock over the mutating path, plus every mutating route → POST. **(§1.2 — live defect, reachable today.)**
2. `finish.py:67` and `local_tracker.py:259` → the broad session instrument. **(§3.3 — three lines.)**
3. `local_tracker.py:1445` — the `/finish` handler releases the claim **before** examining whether the preflight failed, and never calls `factory.finish` at all: no push, no bus announce, no `runs.record()`. See §7.5.
4. `factory/state.py` with three named scopes; five one-line changes. **(§2.3 — closes two false greens.)**
5. `Snapshot`; ~15 call sites. **(§1.1.)**
6. `readiness.py:410, 439` → `sys.executable`. **(§2.1 — one word each.)**
7. Split `render()`. **(§1.3 — largest diff, lowest risk.)**

### 7.4 On the terminal — no dissent

I do not dissent. Everything I read supports it: the launcher already treats the terminal as an
on-demand escape hatch and does it well (§6.10), building one into the page would be a PTY bridge
plus a multiplexer to arrive somewhere worse than `wt` already is (`local_tracker.py:222-224`, and
that reasoning is sound), and the measured bottleneck is human decision latency, which a terminal
does not touch. The only thing I would add is the point in §6.10 — the *launcher* deserves
first-class design attention precisely because the terminal does not.

### 7.5 One thing I found that is not in your known-flaws list, and belongs at the top

The tracker's **"run preflight & finish"** button does not call `factory.finish`.

`local_tracker.py:1438-1454`:

```python
path, checks = ho.write_lane_handoff(lane_id, note)
fails = [c["check"] for c in checks if not c["ok"]]
claimlib.release(lane_id)                              # line 1445 — unconditional
_CLAIM_MSG = (not fails, f"finished {lane_id} — …" + (f"; ⚠ {len(fails)} preflight check(s) failed…"))
```

The claim is released on **line 1445**, before `fails` is used on line 1446. So:

- **The claim is released even when the preflight failed** — which is precisely what `finish.py`
  exists to prevent. Its docstring, `finish.py:12-14`: *"It ASSERTS before it releases. A lane that
  'finished' with a dirty tree, or with no commits, or with nothing written to the ledger, has not
  finished — it has stopped, and releasing its claim would advertise a lie to the next session."*
- **The branch is never pushed.** `finish.finish()` pushes and explicitly refuses to release on a
  failed push (`finish.py:112-120`, *"Losing the branch is the thing this whole step exists to
  prevent"*). The UI path skips it entirely.
- **The bus is never told.** `finish.py:122-127`.
- **`runs.record()` never fires**, because it is only called from `finish._record()`
  (`finish.py:143-159`). Which is why the Lanes tab renders *"Nothing recorded yet. That is
  NOT-RECORDED, not zero"* (`local_tracker.py:734-735`) — the ledger is honest about being empty,
  and it is empty because **the only button that would fill it does not call the thing that fills
  it.**

`handoff.preflight()` is also a *report, not a gate*, and says so deliberately
(`handoff.py:16-19`) — that choice is defensible on its own. But combined with the unconditional
release, the result is that the safest-looking button in the interface performs the least safe
version of the operation, and the run ledger's emptiness is not a measurement of inactivity. It is a
measurement of a disconnected wire.

This one is worth fixing before the threading race, because the threading race needs concurrency and
this one fires every time.

---

## 8. Summary of tiers

`OBSERVED` — every line reference in this document; the module map; the call graph for `measure()`
and `board()`; the `_*_MSG` never-cleared finding; the two `sessions.py` implementations and which
callers use which; `claims`/`worktrees` root resolution; the `/finish` handler's ordering; the
importer graph for `tasks`/`metrics`/`evals`/`demo`/`deploy`; `ThreadingTCPServer` being present in
the working tree and absent from `HEAD`; bare `python` at `readiness.py:410, 439` versus
`sys.executable` at `handoff.py:52`; the fixed-path handoff launch script.

`INFERRED` — that `/flow` is 3–5× the cost of `/lanes` (discriminating test in §1.1); that the
suite-cache fingerprint is the most likely cause of the 10/9/10 flip (discriminating test in §2.1,
and I have not claimed it *is* the cause); the cost estimate for unifying the git wrappers; the
whole of §6, which is design judgement built on observed facts.

`REPORTED` — the Linear and GitHub interaction techniques in §6.9.

`MARKETED` — nothing in this document rests on a vendor claim, and no design premise here comes from
one.

`NOT-SUPPLIED` — I did not read `docs/research/R14-evidence-pack.md` (469 KB), because I had the
repository itself and the pack is by its own `.gitignore` entry a concatenation of files already
present here; reading a copy when the original is on disk is the failure this pass exists to avoid.
I also did not read the AMT proposal's full 62 KB text — §5 answers the five ideas as summarised in
§4b of the brief, and if any of them has substance beyond that summary, my verdicts on them should
be re-checked. I did not execute `measure()` or the tracker (reasons stated at the top), so no
timing figure in this document is `OBSERVED`.
