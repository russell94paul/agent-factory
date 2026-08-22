<!-- session: 2026-08-22 · boot pre-flight + three-lane launch -->

### F74 — The research upload had no diagnostic anyone could reach, so a refusal read as "it does not persist"

- **KIND** — INSTRUMENT
- **STATUS** — ADOPTED
- **BELIEVED** — "research answer uploads are broken — nothing persists."
- **ACTUALLY** — the upload path works. Driven directly it accepts both a pasted body and a
  multipart file, writes the file, git tracks it, and the `/research` page lists it — all four
  verified. But **no R7, R8 or R9 answer exists anywhere on disk**, including in the three lane
  worktrees, so the attempts never reached `save_answer`. The reason that was indistinguishable
  from a broken feature: the only diagnostic on the path was `print("  answer: …")` to stdout, and
  the tracker is normally started with `-WindowStyle Hidden`. A refusal — a mismatched stem, an
  empty body, a file already filed — produced **no file, no visible message, and no record**. The
  honest report from outside is "it does not persist".
- **MEASURED BY** — `curl -X POST .../answer` with a urlencoded body, then again with
  `-F file=@…` multipart: both returned 303 and both wrote the file, confirmed with `ls` and
  `git status`. Then `find . -name 'R*-answer*.md'` across the repo **and every worktree** →
  only R1–R6, none newer.
- **CHANGES** — every attempt is now appended to `.data/answer-log.jsonl` with timestamp, stem,
  content type, byte count, outcome and the exact refusal message, before the redirect. Logging is
  wrapped so it can never itself fail an upload. **Built** — verified by logging one success and
  one deliberate failure (`no research prompt with stem 'R99-does-not-exist'`).
- **AFFECTS** — every lane, and every future "X is broken" report about this tracker. The general
  rule: **a path whose only diagnostic is stdout has no diagnostic at all when the process runs
  detached.** Anything that can refuse must record the refusal somewhere the user can reach it —
  otherwise the failure and the absence of the feature look identical, and the user is right to
  call it broken.
