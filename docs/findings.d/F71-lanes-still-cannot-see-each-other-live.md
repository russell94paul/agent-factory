<!-- session: 2026-08-22 · boot pre-flight + three-lane launch -->

### F71 — Fragments fix the merge, not the blindness: lanes still cannot see each other live

- **KIND** — AGENT-DESIGN
- **STATUS** — OPEN
- **BELIEVED** — "[[F70]] fixed cross-lane findings, so a lane will now see what another lane
  learned."
- **ACTUALLY** — it fixed the *collision*, not the *latency*. A fragment written on
  `lane/certify` is invisible to `lane/artifact` until both merge, which is typically after both
  lanes have finished — i.e. after the point where knowing would have helped. On 2026-08-22 every
  cross-lane correction that actually arrived in time arrived over `SendMessage`, by a human
  noticing and relaying it; none arrived through the ledger. The ledger is a durable record, not
  a channel, and it was being asked to be both.
- **MEASURED BY** — after certify committed F30/F31, `grep -c 'F30' .worktrees/artifact/docs/findings.md`
  → 0, with both sessions live. Nothing in either lane's tooling reads the other's worktree.
- **CHANGES** — undecided, and deliberately so. Three options, in increasing cost: (a) accept it
  and keep `SendMessage` as the live channel, treating the ledger as the durable record only —
  which is what actually worked; (b) a shared append-only file **outside** the worktree boundary,
  rejected for now because `.data/` is gitignored and would be machine-local, the same defect as
  [[F53]]; (c) a properly threaded broker process that outlives the tracker. The tracker itself is
  **not** a candidate: `scripts/local_tracker.py:1181` is a plain `socketserver.TCPServer`, single
  threaded, and it was restarted four times in one session. Do not build (c) before the loop it
  would coordinate is bounded.
- **AFFECTS** — every lane, and anyone reading [[F70]] as though cross-lane knowledge is now
  solved. Until this is decided, **assume another lane will not read what you write in time** —
  if it blocks them, message them.

<!-- correction: 2026-08-23 · R18 internal audit -->

- **CORRECTED 2026-08-23** — ⛔ **two premises in CHANGES above are stale, and one of the three
  options has since been built.** The finding stays **OPEN**; it was never closed. What is wrong is
  the *reasoning*, which is worse than a wrong status because it reads as settled.

  1. **"The tracker itself is not a candidate: `local_tracker.py:1181` is a plain
     `socketserver.TCPServer`, single threaded."** It is not, since 2026-08-23:
     `scripts/local_tracker.py:2357-2362` is a `ThreadingTCPServer` with `daemon_threads = True`.
     Found by R18; **line numbers verified here against the file, not taken on trust.** The
     rejection of option (c) therefore rests on a fact that is no longer true. That does not make
     (c) right — it makes the recorded argument against it void, and it must be re-argued on
     current grounds if anyone wants to close this.

     ⚠ Note what threading actually cost: it silently deleted an atomicity property nothing had
     declared. `claims.claim()` was check-then-write, atomic *only* because `TCPServer` served one
     request at a time. Removing that serialisation let **17 of 20 concurrent threads claim one
     lane** until `_exclusive()` was added. A threaded broker inherits that whole class of problem;
     "the tracker is threaded now" is an argument for re-opening the question, not for answering it
     yes.

  2. **"(b) ... rejected for now because `.data/` is gitignored and would be machine-local, the
     same defect as [[F53]]."** Option (b) **was built** — `factory/bus.py`, writing to `.data/bus/`,
     one append-only file per writer so the F70 collision cannot recur. Its docstring argues the
     machine-local property is **correct rather than a compromise**: the lanes are processes on one
     machine, the channel dies with them, and anything worth keeping is promoted to a finding by
     the lane that learned it.

     ⭐ **That is a real disagreement with this finding, and it is left standing rather than
     smoothed.** F71 called machine-local a defect; `bus.py` calls it the point. Both arguments are
     on the record; whoever closes this must say which is right and why.

- **STILL TRUE** — the thing this finding is actually about is unchanged: **a fragment written on
  one lane is invisible to another until both merge.** `bus.py` addresses the *channel*, not the
  ledger's latency, and R18 §7 flags the channel as a shared writable store injected into every
  lane's context by a hook — the exact shape R17 warns against. The mitigation is one sentence in
  the render preamble.

- **AFFECTS (unchanged)** — assume another lane will not read what you write in time. If it blocks
  them, message them.
