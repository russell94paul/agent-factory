<!-- session: 2026-08-22 · boot pre-flight + three-lane launch -->

### F73 — A claim is an intent, not a process, and finish() released one out from under a live session

- **KIND** — AGENT-DESIGN
- **STATUS** — ADOPTED
- **BELIEVED** — "the claim protects a lane. While it is held nobody else can work that lane, and
  releasing it means the lane is free."
- **ACTUALLY** — the claim says someone *intends* to work the lane. It says nothing about whether a
  process is running, and `factory/finish.py` released one while the session was still alive —
  idle, but alive. A relaunch then saw a free lane and started a second agent in the same worktree.
  For a period on 2026-08-22 there were **three control-plane sessions and two artifact sessions
  sharing one worktree and one branch each** — the shared-checkout arrangement the entire lane
  model exists to avoid, recreated from the inside by the tool written to close lanes safely.
  Nothing collided, because two of the three were idle. **That was luck, not a control.**
- **MEASURED BY** — `python -c "from factory import sessions; print(sessions.duplicates())"` →
  `{'artifact': 2, 'control-plane': 3}`, cross-checked against the process table with
  `Get-CimInstance Win32_Process -Filter "Name='claude.exe'"` — all six pids alive. Worktrees were
  clean at the time (`git status --short` empty in both), which is why the damage was zero.
- **CHANGES** — liveness is now checked against the **process table**, not the registry file, in
  `factory/sessions.py`; the file outlives the process, so testing existence would report every
  historical session as live and refuse every launch. `finish()` refuses while any session in the
  lane is alive, and `launch()` refuses **before** claiming. "Could not read the process table"
  returns a distinct `unverified` verdict rather than being collapsed into "nothing is running" —
  a guard that cannot see must not silently pass. **Built.**
- **AFFECTS** — every lane, `factory/finish.py`, `factory/claims.py` and the tracker's launch path.
  The general rule, which is worth more than the fix: **a lock guards a resource, not a worker.**
  Anything that releases a lock must first establish that the thing holding it has actually stopped.
