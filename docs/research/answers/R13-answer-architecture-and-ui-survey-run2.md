# R13 run 2 — the four questions run 1 left open

**Executive summary.** The migration is *subtractive*: four live surfaces exist and the correct next
build adds none. The `platform/master` postmortem says the extension dies of having a **live
sibling**, not of scope or stack — so it must not start until it can *replace* the tracker's
rendering. The latency question is over: the cache took the page to sub-second and **the honest
answer is stop**. The remaining work is not milliseconds, it is that the cache is keyed on a set
that provably misses two live suite inputs, and that the page now carries **four strings asserting it
caches nothing**. The approval contradiction dissolves — APPROVE leaves the building and becomes a
GitHub PR, so the extension never has to serve a non-engineer. On switchboard: **R12 is right, R15 is
wrong, and both are imprecise about the consequence.**

---

## 1. The migration, against the five real surfaces

Source: `docs/research/ui-surface-inventory.md` §3 (the attachment run 1 did not read).

| # | Surface | Verdict | When |
|---|---|---|---|
| 1 | Orchestrator UI `:8765` | **KEEP, untouched** | never absorb — it is the only surface with a run plane behind it, and §7 forbids removing instruments |
| 2 | Readiness tracker (`scripts/local_tracker.py`) | **KEEP the engine, ABSORB the emitter — last** | its value is `factory.readiness` / `board` / `lanes` as *functions*; the 1,894-line HTML writer is the replaceable half |
| 3 | `docs/artifacts/agent-factory.html` | **KEEP — it is already pinned** | `tests/test_tracker_is_current.py:33,40` reads it and asserts it matches `len(GATES)`. It cannot drift silently. **OBSERVED** |
| 4 | `docs/artifacts/orchestration-bench.html` | **RETIRE** | nothing in `tests/`, `scripts/` or `factory/` references it (grep, **OBSERVED**). It is the one artifact with no anti-drift pin — i.e. the `platform/master` shape in miniature |
| 5 | `platform/master/` | already dead; extract the lesson only | below |

**Parallel:** nothing. The only work with an independent file set is the notification (§3), and it
touches no file above. The two tracker fixes (§2 iii) both edit `scripts/local_tracker.py` and must
be serial.

**Must NOT be built yet: the extension itself.** Option E (provenance UI) is blocked on its own
prerequisite — the version hash covers **0 of 15** dimensions (`factory/readiness.py:757–777`,
**OBSERVED**). Building a container before it has content is the whole `platform/master` failure.

### ⭐ What the dead one predicts

Supplied outside the pack: `aldc-launchpad/CLAUDE.md`, a first-hand postmortem. It agrees with the
pack's §3 row. Three mechanisms, and only the third is the interesting one.

1. **It ran on hand-fed data** — `state.json`, `client-registry.json`, `credentials.json`, one file
   each, last touched May 2026, "never adopted; nothing reads it". A surface on hand-maintained data
   is wrong the first week nobody feeds it, and a wrong surface gets deleted rather than repaired.
   `factory/board.py:5–13` already states this rule for the task list. **Condition: the extension
   calls `readiness.measure()` / `board.board()`; never a serialized snapshot of them.**
2. **It sat off the critical path.** The ops half carried every ticket; the platform half carried
   none. The tracker survives because you cannot start a lane without it claiming first
   (`local_tracker.py` `/start-all` → `claimlib.claim`, inventory §4). **Condition: the extension
   owns a write nothing else can perform, on day one.**
3. **⭐ It was killed by a sibling with live data.** The CLAUDE.md names the successor exactly: the
   orchestrator UI, "same idea, live data". `platform/master` did not die of Electron, of Windows,
   or of scope — it died because a second surface rendered the same idea from a source that could
   not go stale. **The extension's sibling is the tracker.** An extension rendering the same 30
   gates beside a tracker that also renders them *is* `platform/master`'s configuration, and history
   says the one that dies is the newer, prettier one. **Condition: the extension is admissible only
   when it can subtract surface 2's emitter, not sit beside it.**

---

## 2. The latency budget

⚠ **The brief and the pack are both stale here, and rule 2 says report it:** the pack's
"single-threaded socketserver.TCPServer" is contradicted by
`scripts/local_tracker.py:1875–1876` — `ThreadingTCPServer` with `daemon_threads = True`
(**OBSERVED**). The 9.39 s serial figure is likewise superseded by the cache at
`factory/readiness.py:388–434`.

### (i) Critique of the choice made

**Content hash over git SHA is right, and for a reason stronger than the one in the docstring.** A
SHA-keyed cache is stale exactly while you iterate (`readiness.py:359–365`) — correct — but the
sharper point is that a git SHA is *not an input to the suite at all*. The suite reads bytes. Keying
a cache on something that is not an input is the same defect class as
`g_evaluator_is_a_service`'s self-matching probe (`readiness.py:781–789`): a green derived from a
signal that cannot see the thing it claims to cover.

**The age-in-the-headline rule is satisfied at the gate and broken everywhere downstream.**
`readiness.py:401–406` puts the age *inside* the headline string — the rule as written is met. But
every aggregate computed from that string carries no age:

- `readiness.py:1074` — "readiness: N of 30 gates pass". N now contains a cached component.
- `board.py:81` — `board()` derives DONE/READY/BLOCKED and the critical path from it.
- `local_tracker.py:567` — "**measured** {timestamp} local · refresh this page to re-measure".
- `local_tracker.py:1337` — "**Nothing on this page is cached; it re-ran when you loaded it.**"
- `local_tracker.py:10` and `:1882` — same claim in the docstring and the serve banner.

So the page simultaneously says "cached, last run 3h ago" and "nothing on this page is cached."
**A missing label is a gap; a false label is a defect**, and there are four of them. This is the
highest-value item in this section: it is four one-line edits and it is the exact drift the repo
exists to remove, reproduced inside the instrument.

### (ii) What the remaining latency work is worth

Warm render 0.84 s (**REPORTED** by the operator; I did not re-time it). Of that, gates are 0.23 s,
so **≈0.6 s is not gates at all.** Against the named techniques:

Dependency-tracked invalidation is **already built** — the fingerprint is it. Virtualisation buys
**0 ms** (30 rows, not 30,000). Event-sourcing buys **0 ms** — it is a correctness idea, not a
latency one. Optimistic rendering hides ≤840 ms behind a new state machine. Push buys **0 ms on
load**; it changes *when you learn*, which is §3's problem, not this one.

**De-duplicating `measure()` is the only remaining item with a number: ≈230 ms plus one consistency
class.** `render()` calls `measure()`
(`local_tracker.py:535`) and then `board()` (`:618`), which calls `measure()` again
(`board.py:81`) — **two full measurements per gates render, OBSERVED.** Pre-cache that meant the
9.16 s suite ran *twice* per page, which is most of the 27.3 s cold figure. Post-cache it is nearly
free, and that is the problem: **the cache masked a structural defect instead of fixing it.** Every
edit to `tests/` or `factory/` now pays 2 × 9.16 s, not 1. And the header count and the task board
come from two different measurements of a moving repo.

**The honest answer the brief asked for: stop.** Fix the duplicate `measure()` because it is a
consistency bug that happens to be fast, fix the four false labels, and do no further latency work.

### (iii) ⭐ What the cache can now silently get wrong

I enumerated the fingerprint's file set live: **50 files, in `.`, `factory/`, `tests/` only**
(`readiness.py:366–374`, **OBSERVED**).

1. **`scripts/` is not in the fingerprint, and the suite imports it.**
   `tests/test_tracker_routes.py:16` — `from scripts import local_tracker as lt`. So a change to
   the 1,894-line UI — *the file being edited today* — cannot invalidate the cache, while the suite's
   verdict depends on it. **This is a live stale-green hole, not a theoretical one.**
2. **`docs/artifacts/agent-factory.html` is not in the fingerprint, and the suite reads it.**
   `tests/test_tracker_is_current.py:33,40`. Editing the published readout — which is what a render
   pass does — can turn the suite red under an unchanged fingerprint.
3. **The environment is not in the fingerprint, and the suite depends on it.**
   `tests/test_measurement_window.py:105` asserts `str(R.CONNECTORS)` appears in gate evidence, and
   `CONNECTORS` comes from `$PREFECT_CONNECTORS` (`readiness.py:35–37`). This **reintroduces F72
   verbatim** — the defect `readiness.py:1070` already records, "this board reads 9 or 10 at the
   SAME COMMIT depending only on the cwd". The cache now serves a verdict measured under one
   checkout to a reader pointed at another.
4. **The negative control is now replayed from JSON.** The cached evidence line is literally
   `"includes test_every_assertion_has_been_proved_able_to_fail"` (`readiness.py:422–423`, and it is
   in `.data/suite-cache.json` today). A project whose thesis is "green is worthless unless every
   assertion has been shown able to fail" is now asserting that from a cache with **no TTL**. It is
   defensible, but it is the one claim that should be re-earned on a clock — a forced daily re-run
   costs 9 s a day.
5. **Stale *red* is also possible, and it is the F20/F21 shape.** The verdict is cached both ways
   (`readiness.py:428–431`). Fix a missing dependency — an environment change, no bytes changed — and
   the board keeps showing a cached FAIL. `readiness.py:88–97` already names "a gate that cannot
   pass" as a defect equal to one that cannot refuse.
6. **No single-flight, and the write is not atomic.** Threaded server × two `measure()` calls means
   a cold page from two viewers can run up to four `pytest` subprocesses. `-p no:cacheprovider`
   (`:410–411`) correctly avoids the `.pytest_cache` collision, but `write_text` (`:428`) has no
   tmp+`os.replace` and no lock; interleaved writes yield invalid JSON, which the reader swallows
   (`:397–399`) and re-runs. Self-healing, so low severity — but it converts a miss into a herd, in
   an estate whose signature incident is "ten containers took the whole 10-core quota".
7. Two small ones: `_age` has no day bucket, so a five-day cache reads `120h 0m ago`; and
   `time.time() - cached["at"]` is unclamped, so a backward clock correction renders a negative age.

**Not holes, checked:** `evals/` is absent from the fingerprint but `tests/test_corpus.py:26` uses a
sandbox copy, so it is not a suite input. A missing `at` key raises `KeyError` → `measure()`'s
handler → `UNMEASURABLE`, which fails loud. Both correct.

---

## 3. The approval surface — the contradiction dissolves

Run 1's two recommendations only conflict if you assume **one surface must hold all four planes**.
Run 1 never checked that assumption, and it is false.

The measured bottleneck is *two PRs green and waiting 6–9 days* (inventory §5, §6 item 6) — already
a GitHub object. GitHub is an APPROVE surface a non-engineer can use, with per-item approval,
identity, an audit trail, a mobile client and notifications — and **we do not maintain it.** The
cost of "maintaining two surfaces" is therefore zero, because the second is not ours.

Run 1's own finding — *no off-the-shelf tool targets business users reviewing code changes* — is
right and does not bite, because **the non-engineer does not approve the diff. They approve the
claim.** The PROVE plane's output is "the verdict *and what it was measured with*" (inventory §2):
text, not a diff, and therefore a generated PR description.

**So APPROVE leaves the building, and the platform decision stops needing to cover it at all.** The
extension serves DECIDE, RUN and PROVE — three engineer planes, all in VS Code.

One carve-out: **per-secret approval cannot be a PR** — a secret grant is not a diff. It stays
engineer-only in the tracker/extension, which is correct, since only an engineer grants a secret.

⚠ **And the fix is probably not a UI at all.** Nobody has established whether those 6–9 days were
*no notification sent* or *notification sent and ignored*. That is `NOT-SUPPLIED` by the pack, and
it decides the entire remedy. Building a bespoke queue to fix an unmeasured notification failure is
the wrong-layer deploy this estate has a standing rule against. **Measure first: was the reviewer
subscribed?** A ZERO and a NOT-VISIBLE are different verdicts.

---

## 4. The switchboard reading — settled

Read from source: `doctly/switchboard` `main.js`, default branch `main`, at commit
`4c5a6da4ee23818584a53094e85989d7143da0c4` (2026-08-04). **OBSERVED.**

```js
// --- IPC: open-terminal ---
ipcMain.handle('open-terminal', async (_event, sessionId, projectPath, isNew, sessionOptions) => {
  if (!mainWindow) return { ok: false, error: 'no window' };

  // Reattach to existing session
  if (activeSessions.has(sessionId)) {
    ...
    return { ok: true, reattached: true, mcpActive: !!session.mcpServer };
  }

  // Spawn new PTY
  ...
      } else {
        claudeArgs.push('--resume', String(sessionId));
      }
```

**R12 is right. R15 is wrong.** R15's *"it can attach to any running session… not just those it
spawned"* is contradicted by the branch above: `activeSessions` is an in-process `Map` (`main.js:88`)
written only after this handler spawns (`:1158`). A grep for `pid`, `kill(0`, `tasklist`, `lockfile`
or any process-table probe returns **zero hits** across the file — there is no OS-level liveness
check anywhere.

**⭐ The third reading both passes missed.** Neither described the actual consequence. Switchboard
does not "spawn a duplicate": it **unconditionally issues `claude --resume <sessionId>` and never
checks whether anything else holds that id.** Whether a second live process results is decided
entirely by the Claude CLI — a program switchboard does not consult, does not control, and whose
refusal (if any) it never surfaces. The correct verdict is not "it duplicates" but **"it has no
guard, and delegates the guard to something it cannot see"** — worse than a duplicate, because it is
unobservable: the UI reports the same "not running" for *exited*, *running-outside-switchboard*, and
*running-and-refused*.

Two scope corrections to R12: it is **not only** sessions started outside switchboard. A crash
leaves the map empty while PTYs may survive (the tidy kills at `:207–211` and `:1502–1506` run only
on `closed`/`will-quit`), and the fork path re-keys a live session under a `realSessionId`
(`:1257–1269`), so `has(sessionId)` can miss a PTY switchboard **does** own. The decision is
unchanged; the reason sharpens — this is not a patchable bug but the absence of a liveness concept,
exactly the one `ui-surface-inventory.md` §6 item 3 says we had to invent ourselves.

---

## 5. What I would refuse to build, and what to delete

**Refuse:** (1) a terminal grid — settled; (2) a second web surface for approval — §3 makes it
unnecessary and §1's lesson makes it fatal; (3) any bespoke notification daemon before measuring
whether GitHub's own notification fired; (4) any surface with a hand-maintained data file — that is
`platform/master`'s cause of death; (5) parallelising `measure()` — the brief is right, it buys
0.23 s; (6) **the VS Code extension, for now**, until it can subtract the tracker's emitter rather
than sit beside it.

**Delete:** `docs/artifacts/orchestration-bench.html` (nothing pins it). And delete the four false
claims — `local_tracker.py:10`, `:567`, `:1337`, `:1882` — before anything else on this list. A
surface that asserts it never caches, while caching, is the only defect here that makes every other
number on the page unreliable.

---

## NOT-SUPPLIED

- Whether the 6–9 day PR wait was an unsent notification or an ignored one. **This decides §3's
  remedy and nothing in the pack measures it.**
- Any measurement of our operators' behaviour — no user studies exist and none are cited here.
- What fraction of agent deliverables are code-shaped (PR-able). The *measured* bottleneck is
  entirely PR-shaped, so §3 covers what we can see; it may not cover Snowflake/PBI deliverables.
- The 0.84 s warm / 27.3 s cold figures are **REPORTED** by the operator, not re-measured by me.
  I did independently time `factory.certify` at **0.13 s** (rc=1), which makes the 0.23 s
  twenty-nine-gate figure plausible rather than suspect.
