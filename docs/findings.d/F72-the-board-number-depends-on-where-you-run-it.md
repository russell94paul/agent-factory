<!-- session: 2026-08-22 · boot pre-flight + three-lane launch -->

### F72 — The board's own number depends on which directory you run it from

- **KIND** — INSTRUMENT
- **STATUS** — OPEN
- **BELIEVED** — "`python -m factory.readiness` prints the readiness of the system. Quote the
  number; compare it before and after."
- **ACTUALLY** — it prints the readiness of *whatever the paths resolve to from your cwd*, and
  that differs by several gates. Measured within minutes of each other, same commit:

    from repos/agent-factory (main checkout)      -> 9 of 30
    from .worktrees/artifact (a lane worktree)    -> 10 of 30

  Both are correct and they answer different questions. `CONNECTORS` is
  `FACTORY.parent / "prefect-connectors"` (`readiness.py:33`), so from a worktree it lands on
  `.worktrees/prefect-connectors` — control-plane's branch, carrying unmerged control primitives —
  while from the main checkout it lands on the canonical repo without them. The `ticket` gate
  moves the opposite way: it reads `FACTORY.parent / "aldc-launchpad" / ...`, which from a
  worktree becomes `.worktrees/aldc-launchpad/` and does not exist, so the gate reports
  UNMEASURABLE rather than reading the real drafts folder. One gate gains, another is lost, and
  the totals differ without either run being wrong.
- **MEASURED BY** — run `python -m factory.readiness | head -3` from `repos/agent-factory` and
  again from `repos/agent-factory/.worktrees/artifact`. Compare the headline AND the two paths the
  header prints — the header already tells you, which is the only reason this was caught. Then
  `readiness.py:33` and `readiness.py:811` for the two resolutions.
- **CHANGES** — a before/after claim must state the cwd it was measured from, and comparisons must
  hold it fixed. The header prints `factory` and `connectors` paths already; the **headline should
  carry the same basis**, so a number quoted out of context cannot be read as global. Longer term
  `$PREFECT_CONNECTORS` should be set explicitly by whatever runs the measurement rather than
  inferred from cwd. Related to [[F30]], which found the shadowing from the other direction.
- **AFFECTS** — every lane, and every before/after number on this board, including the "7 → 10"
  improvement claimed for control-plane's primitives on 2026-08-22 — that comparison happens to be
  like-for-like (both from worktrees) but nothing recorded said so at the time, which is the
  defect. `judgement` and `control-plane` gates are the ones whose resolution actually moves.
