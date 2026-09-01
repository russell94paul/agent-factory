# Switchboard P1 — control UX, measured

Branch `switchboard/p1`, worktree `.worktrees/p1`, from `ab13977`. **Not pushed.**

Everything below is a number this session produced, with the command that produced it. Nothing is
carried over from the brief, and where the brief's premise did not survive measurement it is
corrected here rather than repeated.

## Tests

```
python -m pytest tests/
930 passed, 1 skipped, 2 xfailed        exit 0
```

Baseline at `ab13977` was **4 failed** (2 guards + 2 `test_case_study` — all four fixed, see below).
P1's own suite: `python -m pytest tests/test_switchboard_p1.py` → **46 passed**.

## Rendered validation — real Chromium, both schemes

```
python scripts/render_check_switchboard_p1.py --url http://127.0.0.1:8117/switchboard --shots
```

| viewport | scheme | horizontal overflow | NEEDS YOU top | console errors | failed requests |
|---|---|---|---|---|---|
| 390×844 | light | 0 px | 487 / 844 px | 0 | 0 |
| 390×844 | dark | 0 px | 487 / 844 px | 0 | 0 |
| 430×932 | light | 0 px | 487 / 932 px | 0 | 0 |
| 430×932 | dark | 0 px | 487 / 932 px | 0 | 0 |
| 1440×900 | light | 0 px | 332 / 900 px | 0 | 0 |
| 1440×900 | dark | 0 px | 332 / 900 px | 0 | 0 |

`PHONE VIEWPORT = RENDERED_CONFIRMED` · `PHYSICAL PHONE = HUMAN_CONFIRMATION_REQUIRED`
(no physical device was used).

Screenshots: `p1-{phone-390,phone-430,desktop-1440}-{light,dark}.png`.
Machine report: `render-check-switchboard-p1.json`.

### ⭐ The check earned its keep before it passed

It failed twice on real defects that were invisible in a screenshot, because the *page body*
scrolled sideways while every panel looked correct:

1. **157 px overflow at 390, 117 px at 430** — a **collapsed** `<details>` still contributes to
   `documentElement.scrollWidth` in Chromium, so the retained P0 panels widened the page while
   being invisible.
2. **The real culprit was `.btn.wide` inheriting `white-space:nowrap`** — the P0 disclosure's
   summary rendered 524 px wide inside a 344 px column. Fixed by letting full-width buttons wrap.

A screenshot of either state looks completely correct. Only the measurement found them.

### ⭐ And one the measurement could not find — reading the rendered page did

With every metric green, the 390px page still opened on **five orphaned questions**, one full card
each, pushing NEXT and its START SYNCED button several screens down. That is precisely the failure
the brief names: five old questions must not visually outrank one live delivery blocker. No
overflow check, and no unit test, can see it — it is only visible by looking.

Stale questions now collapse to one line (never deleted, never hidden), and the alarm border, the
top-bar flash and the bottom-nav badge all count **live questions only** — a permanent red dot is
one the operator stops seeing. Measured effect on the phone page:

| | before | after |
|---|---|---|
| full page height @390 | 8742 px | 5770 px |
| NEEDS YOU heading top | 539 px | 487 px |
| NEXT / START SYNCED | several screens down | second screen |

### Negative control — the check can refuse

`min-width:900px` was forced onto `.p1 .brand` and the server restarted:

```
FAIL phone-390  overflow=532px      FAIL phone-430  overflow=492px      exit 1
```

Mutation restored, re-measured: **all six PASS, exit 0**.

## Restart / refresh — three controls, three true statements

`hot_reload()` was **measured before** the supervisor was written rather than assumed away:

```
hot modules                            38
factory.work / factory.switchboard_p1  both covered (the list is DERIVED from imports)
reloaded 38 modules, rebound 20 names, 30 gates
can reload scripts/local_tracker.py    NO
```

So it is **reused** as *Re-measure*. The supervisor exists only for the module it structurally
cannot reload — the one defining the routes, the handler and `render()`.

Proof, by injecting a marker into `local_tracker.py` (`KNOWN_REPOS`) on a live server:

| action | marker visible | meaning |
|---|---|---|
| **Refresh** (re-request page) | **0** | re-measures data; does NOT reload code — and does not claim to |
| **Re-measure** (`/reload`) | **0** | reloads all 38 `factory.*` modules; correctly cannot reach `local_tracker.py` |
| **Restart Switchboard** | **1** | new process, new runtime, same port |

Runtimes observed across restarts, all on port 8117:
`e5da8e3f4c7b`(pid 31408) → `13a3b83ace24`(6796) → `1a3b9b8a01eb`(37380) → `46ec4f926d43`(3908) → …

Supervisor log: `restart requested by the UI -- exiting 97 for the supervisor`.

### Restart security — every refusal measured

| attempt | result |
|---|---|
| `GET /switchboard/restart` | **HTTP 404** — there is no GET route |
| `POST` with no token | `REFUSED: missing or stale restart token` |
| `POST` with wrong token | `REFUSED: missing or stale restart token` |
| `POST` valid token, `Origin: https://evil.example.com` | `REFUSED: cross-origin restart refused` |
| `POST token=…&command=calc.exe&cmd=whoami` | HTTP 202 — restarted; **`calc.exe` processes: 0**. The extra parameters have no effect because the handler reads none: its entire effect is a fixed exit code. |
| unsupervised server | control renders as unavailable; endpoint refuses |
| **through the phone tunnel**, same origin | **HTTP 202 — restarts** (see below) |
| through the tunnel, `Origin: evil.example.com` | `REFUSED: … does not match the host this request was sent to, 'abc123.ngrok-free.app'` |
| through the tunnel, no token | `REFUSED: missing or stale restart token` |
| two restart POSTs in a row | second gets connection-refused (already exiting); **listeners on 8117: 1** — no duplicate server |

`ngrok` needs no restart: the supervisor never binds a socket. The child owns the port, so a
tunnel pointed at it survives every restart by construction.

### ⛔ The tunnel path was broken, and every test passed anyway

The first same-origin check compared `Origin` against a **loopback allow-list**. Reached through
the phone tunnel the page's own origin IS the tunnel hostname, so the browser sends
`Origin: https://<id>.ngrok-free.app` and the server refused its own button:

```
REFUSED: cross-origin restart refused (Origin: 'abc123.ngrok-free.app')
```

The button rendered, the tap would have done nothing, and the operator would have walked back to
the laptop — the exact trip this control exists to remove. **Every security test passed while this
was live**, because all of them hit `127.0.0.1` directly and sent no `Origin` header at all. The
whole matrix was measuring a path nobody uses.

Fixed by comparing `Origin` to the request's own `Host`, which is the standard same-origin check
and strictly *stronger*: a third-party page carries its own origin, which cannot match our Host,
on localhost or through any tunnel. Re-measured on both paths — table above.

### ⚠ Measured limitation — hard kill orphans the child

Stopping the supervisor with `Stop-Process -Force` (**not** Ctrl+C) left the child alive and still
LISTENING. A Windows job object with `KILL_ON_JOB_CLOSE` is attempted and **could not be
established here** — the child inherits the harness's own job, and a process already in a job
cannot be assigned to another without breakaway rights the outer job may not grant. The supervisor
therefore prints a warning at startup rather than implying a guarantee it did not get.

The Ctrl+C path itself (terminate → wait → exit 0) is implemented but was **NOT** measured in a
real console: `IMPLEMENTED-NOT-MEASURED`, which is not the same as working.

## The two guards

| guard | the brief's premise | what measurement showed |
|---|---|---|
| `test_repo_root` | self-matching on Switchboard's prose | **Correct.** It flagged a docstring instructing readers to obey it. |
| `test_suite_cache` | self-matching on Switchboard's prose | **Wrong.** It flagged rendered UI text claiming *"nothing on this page is cached"* — the exact absolute claim it exists to ban. The fix belonged to the **surface**, not the test. |

Both were also aimed at the **wrong checkout** (`repo.primary()` / `R.FACTORY`), so a suite running
in a worktree validated the *primary's* source. Fixing that and widening the scan exposed three
real pre-existing defects, all fixed:

- `scripts/local_tracker.py` read the **task store** from a `__file__`-relative path → serving from
  a worktree showed **zero** closed tickets, an empty store rendering as "no progress".
- `scripts/credential_use.py` wrote the **credential audit log** into whichever worktree invoked it.
- `tests/test_case_study.py` — `ROOT/.data` across two lines; red in every worktree, green only in
  the primary. Its two failing tests were detecting their own broken input.

The **split form** (`__file__` root on one line, `.data` join on another) trips no single-line rule.
It is now detected, proven by negative control, and **reported not gated** — 9 instances remain,
several may be correct, and promoting it to a gate is a human decision with the census in hand.

## Real dogfood — created through the operator path, neither started

```
MARKETING-MODEL-FINALIZATION-01   READY     PRIVATE  agent-factory  depends_on 91088e54
AF-CLIENT-REVIEW-P1.5             BLOCKED   PRIVATE  agent-factory  depends_on MARKETING-MODEL-FINALIZATION-01
```

`91088e54` is **D5 · Recommendation + human sign-off**, measured `done` with 5 evidence rows. A real
predecessor — no completion record was invented, and no manifest was written for either item.

FINALIZATION's seven checks all PASS. P1.5 is BLOCKED on `dependencies FAIL: waits on
MARKETING-MODEL-FINALIZATION-01` — derived, not asserted. Neither has a `start_mode`, so neither
has been started.
