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
