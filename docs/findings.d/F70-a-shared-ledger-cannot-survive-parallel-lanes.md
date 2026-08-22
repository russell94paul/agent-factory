<!-- session: 2026-08-22 · boot pre-flight + three-lane launch -->

### F70 — A shared ledger file cannot survive parallel lanes, and ours did not

- **KIND** — AGENT-DESIGN
- **STATUS** — ADOPTED
- **BELIEVED** — "`docs/findings.md` is how one lane tells another something. Append your entry
  and the next lane reads it."
- **ACTUALLY** — lanes run in isolated git worktrees, so no lane can observe another's append
  until merge. On 2026-08-22 three sessions each read F10 as the last id and appended their own
  **F11 and F12** — every one of them correct by sequence, and mutually incompatible. Three F11s,
  three F12s, and a merge that would have silently dropped two of each, in the one file whose
  purpose is stopping a lane from paying twice for the same mistake. The ledger had the exact
  shape the lanes are being asked to find defects in over in the orchestrator: shared mutable
  state written concurrently by processes that cannot see each other.
- **MEASURED BY** — `grep -n '^### F1[0-9]' docs/findings.md` in each of the three lane
  worktrees, which returns a different F11 and F12 in each. Then
  `git merge-tree --write-tree HEAD lane/certify` → `CONFLICT (content) in docs/findings.md`.
- **CHANGES** — entries move to `docs/findings.d/<id>-<slug>.md`, one file each; `load()` unions
  the directory with the old ledger so nothing in flight breaks. Ids stay, because `[[F20]]` has
  to resolve, but they become a naming convention rather than a lock on a shared file, allocated
  in per-lane blocks. **Built.**
- **AFFECTS** — every lane, and any future artefact written concurrently by lanes. The general
  rule: if parallel sessions must both write it, it cannot be one file. Prefer a directory of
  fragments, or a broker — never an append target.
