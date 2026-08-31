### F86 — The findings ledger could not see its own last eight findings, including every correction the boot README calls load-bearing

The mechanism this repository uses to stop a lane paying twice for the same mistake had silently
dropped its **eight most recent entries** — every finding written since 2026-08-30 — because of a
heading level. `test_findings.py` passed throughout.

## The rule worth keeping

**A validator that only inspects what it managed to parse cannot report what it failed to parse.**
`malformed()` answers *"which findings are missing fields"*. Nobody was asking *"which findings
are missing"*. A file that fails to parse is not malformed — it is **absent**, and absence was the
one state the suite had no assertion for.

This is the fourth blind instrument in ten days ([[F80]] wrong branch, [[F81]] probes that cannot
fail, [[F84]] a grep that cannot see the only consumer) and the third where the instrument
returned a **plausible number instead of an error**. The countermeasure is the same one every
time and it is already the house style — `tests/test_hot_reload_covers_every_import.py` derives
its list rather than asserting one. **Enumerate the population from the directory, not from the
parser's output.**

⭐ The irony is load-bearing, not decorative: **[[F84]] is a finding about a blind instrument that
was itself invisible to a blind instrument**, and it sat that way for a day while being cited as
the correction that should decide what gets built next.

- **BELIEVED** — findings written as one file per entry in `docs/findings.d/` are in the ledger.
  `docs/findings.d/README.md` states the four mandatory fields, the id blocks, the filename
  convention and the optional fields, and `ls docs/findings.d/` is described as "the index".

- **ACTUALLY** — `factory/findings.py` splits on
  `_HEADING = re.compile(r"^###\s+(F\d+)\s*[—-]\s*(.+?)\s*$", re.M)`. **A fragment whose title is
  `#` rather than `###` parses to nothing at all.** F20, F21 and F70–F76 used `###`. Starting at
  F77 the convention drifted to `#`, and every finding after it inherited the drift:

  | | heading | in the ledger |
  |---|---|---|
  | F20, F21, F70–F76 | `###` | ✅ 9 findings |
  | **F77–F84** | `#` | ⛔ **8 findings, invisible** |

  The lost eight are not marginal. They are F77 (RUN-01 measures the wrong repository), F78 (the
  unattended verdict is about the other repo), F80 (the board was reading the wrong branch), F81
  (three probes that could not see) — **the four the boot-prompts README titles "the corrections
  that outlived every prompt above"** — plus F79, F82, F83 and F84.

  ⛔ **The consequence is exactly what the ledger exists to prevent.** `by_lane()` feeds the
  per-lane findings a new lane agent is shown. None of these eight reached a lane. A session
  starting `control-plane` was shown nothing about F80 or F81, both of which are about
  `control-plane`'s own gates.

  ⚠ **And nothing failed.** `test_every_finding_carries_all_four_mandatory_fields` calls
  `malformed()`, which iterates `load()`; `test_every_finding_reaches_at_least_one_lane` calls
  `unattached()`, which iterates `load()`. Both were green over a ledger missing a third of
  itself, because both asked their question only of the findings that had already parsed.

  ⭐ **The README is the root cause, and it is a documentation defect rather than an author's
  slip.** It specifies every other part of the format in detail and never once states the heading
  level. Eight consecutive authors read it and got the same thing wrong, which is what a missing
  spec looks like from the outside.

- **MEASURED BY** — enumerate the population from the directory and compare it with the parser's
  output, which is the positive control that was never run:

  ```bash
  python -c "
  import pathlib, re
  from factory.findings import load
  seen = {f.id for f in load()}
  files = {re.match(r'(F\d+)', p.name).group(1)
           for p in pathlib.Path('docs/findings.d').glob('F*.md')}
  print('on disk:', len(files), '| in ledger:', len(files & seen), '| INVISIBLE:', sorted(files - seen))"
  ```

  Before: `on disk: 17 | in ledger: 9 | INVISIBLE: ['F77','F78','F79','F80','F81','F82','F83','F84']`.
  After: `INVISIBLE: []`. The totals reconcile independently — `load()` returned **19** before
  (10 legacy entries in `docs/findings.md` + 9 visible fragments) and **28** after (+8 recovered,
  +F85), which is the arithmetic the count should show if nothing else moved.

- **AFFECTS** — every lane, and the lane-briefing path specifically: `by_lane()` is what shows a
  finding to the session that needs it, and it could not show these. `control-plane` is worst hit
  (F80 and F81 are about its own `cap`, `reaper` and `concurrency` gates); `certify` loses F79
  about `certified`/`breadth`/`corpus`. Also `docs/findings.d/README.md`, which specifies the
  format and omitted the one rule that decides whether a file is read at all.

- **KIND** — INSTRUMENT

- **CHANGES** — all three landed in the commit that files this. (1) F77–F84 promoted to `###`;
  no body text altered. (2) F83 and F84 given the mandatory field blocks they never had — they
  were written as prose essays, so heading promotion alone would have made them load as
  malformed. (3) `tests/test_findings.py::test_every_findings_file_is_visible_to_the_ledger`
  derives the expected id set from `ls docs/findings.d/` and fails on any file the parser cannot
  see, and the heading rule is now stated in `docs/findings.d/README.md`.

- **STATUS** — ADOPTED
