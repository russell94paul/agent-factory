### F90 — `TeamSpec.repo` is inside the version hash and the controller ignores it, so a certified team runs in the wrong repository

Found while choosing a target for RUN-03's first supervised run. Both presets that now have a
runnable verifier are `pbi_model` work, which lives in `~/repos/clients` — and the controller can
only ever create a worktree inside `agent-factory`.

## Why this is the sharp version of a defect this repo already paid for

`blueprint.TeamSpec.version` was changed on 2026-08-29 for exactly this reason, and its docstring
says so:

> *"A team certified against `prefect-connectors` under 'must not deploy to production' kept the
> **identical** version when repointed at another repo with the prohibition deleted. Those are
> precisely the two edits that change blast radius."*

The fix made `repo` part of the team's identity. **It is now faithfully hashing a field that
nothing downstream honours.** The certification records which repository the team was certified
against; the executor puts the agent somewhere else and never mentions it. That is worse than the
original bug, because the hash now carries an assurance the run cannot keep — the version says
*certified against `clients`* about a run that happened in `agent-factory`.

## The rule worth keeping

**A field that is part of an identity must be read by whatever acts on that identity.** If it is
hashed but never obeyed, the hash is not recording a fact about the run — it is recording an
intention that the run is free to ignore, which is the shape of every certification that
transfers silently. Before adding a field to a version hash, name the code that reads it.

- **BELIEVED** — `Ticket.repo` selects the repository the agent works in. It is carried into
  `TeamSpec.repo` (`control.py:206`, `repo=ticket.repo or str(_repo.primary())`), written to the
  `run_started` event, and included in `TeamSpec.version`, so a run against a different repo gets
  a different team version.

- **ACTUALLY** — nothing reads it. `RunController._make_worktree` calls
  `worktrees.ensure(ticket.key)`, and `worktrees.REPO` is `_repo.primary()` — a module constant
  bound at import to *this* checkout. There is no parameter by which another repository can be
  named, and `control.main()` compounds it by hard-coding `repo_root=_repo.primary()` for the
  headless provider too. `ticket.repo` is recorded and discarded.

- **MEASURED BY** — a discriminating test, result predicted before it ran:

  ```python
  t = control.Ticket(id='GP-329', title='add ad-spend measures',
                     type_id='add-measure', repo=r'C:\Users\PaulRussell\repos\clients')
  team = control.team_for(t, presets.by_id('add-measure'))
  ```
  ```
  TeamSpec.repo        C:\Users\PaulRussell\repos\clients     <- in run_started AND the version hash
  worktree would be    C:\Users\PaulRussell\repos\agent-factory\.worktrees\gp-329
  Do they agree?       False
  ```

  Corroborated structurally: `grep -n "REPO = " factory/worktrees.py` gives
  `REPO = _repo.primary()` at module scope, and `factory/worktrees.py` exposes no function taking
  a repository argument. No test in `tests/test_control_run.py` mentions `repo=` at all — the
  field was never asserted on, which is why 26 passing tests did not see it.

- **AFFECTS** — the `control-plane` lane and `factory/control.py`, `factory/worktrees.py`,
  `factory/blueprint.py`. Operationally it blocks the first supervised run: **the only two presets
  with a runnable verifier — `add-measure` and `model-redesign` — are both `pbi_model` work**, so
  every ticket the controller can actually reach a verdict on is a ticket it would run in the
  wrong repository. `python -c "from factory import verifiers as v; print(sorted(v.REGISTRY))"`
  and `python -c "from factory.presets import by_id; print(by_id('add-measure').layers)"`.

  ⚠ It also means the run ledger's attribution — the join RUN-03 exists to provide — is
  misleading rather than absent for any run whose ticket named a repo. `NOT-RECORDED` would have
  been safer than a value nothing enforced.

- **KIND** — DESIGN

- **CHANGES** — none yet; recorded before choosing a remedy, because there are two and they are
  not equivalent. **(a)** Make the repository real: thread it through `worktrees.ensure` and the
  providers so a run can genuinely happen in `clients`. That is what the presets imply and it is
  the larger job — cross-repo worktrees, claims resolving to the right primary (F70/F71 again,
  one repo further out), and `runs.path()` deciding which estate a run belongs to. **(b)** Make
  the controller refuse: reject a `Ticket` whose `repo` is not this checkout, so the record can
  never claim something the executor did not do. (b) is a few lines and is honest immediately;
  (a) is the feature. **They should land in that order** — the refusal first, so nothing can ship
  a false attribution while the feature is built.

- **STATUS** — OPEN
