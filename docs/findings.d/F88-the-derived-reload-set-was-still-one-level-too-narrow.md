### F88 — The reload button's derived module list was still one level too narrow, and never reloaded the verdict enum

`scripts/local_tracker.py` replaced two hand-written reload lists with a derivation, because both
had under-covered. The derivation was over **this file's own imports**. `importlib.reload` does
not recurse, so every module reached only *through* another one was still never reloaded — and
the button still reported success.

## The rule worth keeping

⭐ **A derived list is only as wide as the relation it derives over.** Deriving over *"what this
file imports"* is not the same as deriving over *"what this process runs"*, and the reload button
claims the second. Getting from a hand-written list to a derived one is the easy half; choosing
the relation is where the coverage actually comes from.

This is the fourth time in this estate that a list which was supposed to mirror something has
silently missed entries — after `TeamSpec.version`'s hash keys, `synthesis.session_prompt`'s
fallback, and `_HOT` itself. The first three were hand-maintained. **This one had already been
fixed once**, and the fix was correct and insufficient at the same time, which is the part worth
remembering: *the previous repair is not evidence that the defect is gone.*

- **BELIEVED** — `scripts/local_tracker.py`, in the comment above `_HOT`: the reload set is
  *"DERIVED from this file's own imports, never typed out"*, and
  `tests/test_hot_reload_covers_every_import.py` asserts *"no factory import may sit outside the
  reload set"*. Pressing **↻ reload code & re-measure** therefore serves the code on disk.

- **ACTUALLY** — it served the code on disk for the **24** modules the script imports by name,
  and the process-start code for everything those modules import in turn. `importlib.reload`
  re-executes one module; it does not walk its dependencies. The closure is **31** modules, so
  **7 were being reported as reloaded and were not**:

  | recovered by the closure | what it is |
  |---|---|
  | `contract` | ⛔ **the five verdicts themselves** — PASS/FAIL/UNMEASURABLE/ERROR/NOT_RUN |
  | `deploy` | ⛔ **the attempt cap and the retry ledger** (see F85) |
  | `verifiers` | the registry that decides which check owns a ticket's verdict (F87) |
  | `pbi_contract` | the 12 assertions that check a Power BI model change |
  | `blueprint` | `AgentSpec` / `TeamSpec`, and the version hash |
  | `repo` | primary-worktree resolution — where `.data` is |
  | `evidence` | the evidence classes |

  ⚠ **The four most consequential files in a verdict were all in the blind spot.** An operator
  editing `factory/contract.py` — the module whose entire job is refusing to collapse
  UNMEASURABLE into PASS — and pressing reload got a message saying *"reloaded 24 modules"* and
  the old verdict logic. The test that was written to stop exactly this passed the whole time,
  because it asked about direct imports, which is the set the derivation already covered.

  ⭐ **Found by adding a module, not by the test.** `factory/verifiers.py` was written, wired into
  `control`, and then checked for reloadability out of habit — it was absent, and pulling that
  thread produced the other six. Nothing in the suite was going to raise it.

- **MEASURED BY** — the two sets, compared directly:

  ```bash
  python -c "
  import importlib.util
  s = importlib.util.spec_from_file_location('lt', 'scripts/local_tracker.py')
  m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
  direct = set(m._imported_factory_modules())
  hot    = {n.split('.', 1)[1] for n in m._HOT}
  print('direct:', len(direct), '| reload set:', len(hot))
  print('reachable but never reloaded:', sorted(hot - direct))"
  ```

  Before the fix: `direct: 24 | reload set: 24`, difference empty — the reload set *was* the
  direct imports. After: `direct: 24 | reload set: 31`, recovering the seven above. Reload order
  still holds across the wider set (`contract` before `verifiers` before `control`), which
  matters because an importer reloaded first keeps references to the pre-reload objects.

  Negative control: restoring `_HOT` to the direct-import derivation turns
  `test_the_reload_set_is_the_transitive_closure_not_just_direct_imports` and
  `test_the_modules_that_decide_a_verdict_are_reloadable` red, and nothing else in the suite
  notices — which is the same blindness, demonstrated.

- **AFFECTS** — every lane, since anyone editing `factory/*` while the tracker runs inherits it,
  and the `control-plane` lane specifically: `factory/deploy.py` holds the attempt cap that the
  `cap` gate is about, and it was among the modules never reloaded. Also
  `tests/test_hot_reload_covers_every_import.py`, whose stated regression it did not actually
  cover.

- **KIND** — INSTRUMENT

- **CHANGES** — landed with this finding. `_factory_module_closure()` walks the factory import
  graph from the tracker's own imports and `_HOT` is derived from the closure;
  `_sibling_imports()` parses all four import spellings we actually use, including the
  `from . import x as y` alias form the tracker itself is written in. Three tests added: the
  closure equals `_HOT`, the four verdict-deciding modules are in it by name, and a dependency
  still precedes its importer across the wider set.

- **STATUS** — ADOPTED
