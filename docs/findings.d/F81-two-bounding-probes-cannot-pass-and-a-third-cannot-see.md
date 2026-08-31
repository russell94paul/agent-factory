### F81 — two of the five bounding probes cannot pass, and a third cannot see the control it judges

Found while checking F80. Both are in `factory/readiness.py`, both concern gates on the critical
path, and both report a confident FAIL about a control that exists.

- **BELIEVED** — `reaper` FAIL *"no lease, timeout or reaper for dispatched work"* and
  `concurrency` FAIL *"concurrency is bounded per wave, not per stage dispatch"*. Read as
  measurements of the orchestrator.

- **ACTUALLY** — neither sentence is a measurement of the branch that holds the work.

  **1. `g_orphans_are_reaped` has exactly one return statement, and it is `_fail`.**
  The probe greps `work_guard.py` for heartbeats, appends three canned evidence lines — including
  *"4 of 14 runs sit at stage_started"*, a figure from an old audit — and returns `_fail`
  unconditionally. There is no input to this function that produces PASS. It is the mirror image
  of this repo's founding sin: a gate that cannot fail proves nothing, and a gate that cannot pass
  proves nothing either, while looking exactly like a finding.

  Meanwhile `lane/control-plane` ships `orchestrator/engine/cloud_reaper.py` — **10,240 bytes, 8
  functions** — with `tests/orchestrator/test_cloud_reaper.py`, **965 lines**.

  **2. `g_concurrency_is_reserved_outside_the_agent` greps case-sensitively for a lowercase name
  the code spells in uppercase.**

  ```python
  stage_level = re.search(r"max_parallel", _src("orchestrator/pipelines.py"))
  ```

  On `lane/control-plane`, `pipelines.py` defines `MAX_PARALLEL_STAGE_DISPATCH = 4` guarded by
  `_DISPATCH_LOCK`, computes `free = MAX_PARALLEL_STAGE_DISPATCH - dispatched_slots_in_use()`, and
  emits a refusal event `{"control": "dispatch_ceiling", "ceiling": MAX_PARALLEL_STAGE_DISPATCH}` —
  stage-level dispatch concurrency, which is exactly what the gate says does not exist.

- **MEASURED BY** — run against `lane/control-plane`:

  ```
  probe regex  max_parallel  (case-sensitive): False
  case-insensitive                          : True
  occurrences of MAX_PARALLEL_STAGE_DISPATCH: 6

  reaper probe return statements: ['_fail']
  ```

  The reaper result is from `ast.walk` over the probe's own source, not from reading it — the
  return set is `{_fail}` with no branch.

- **AFFECTS** — anyone reading `python -m factory.launch`, and the RUN-02 ticket specifically.

  1. ⛔ **A case-sensitive grep is a zero from an instrument nobody proved could see.** Identical
     to review finding **D-2**, where D5 was reported missing and existed at `deepseek.md:528-541`
     for the same reason. That one was corrected in prose and the *class* of defect was not swept
     for. This is the second instance, in the readiness probes themselves.
  2. **`tests/test_readiness_probes_can_pass.py::test_every_gate_can_report_pass[reaper]` is
     already red** and has been read as sibling-repo noise. It is not noise — it is that test
     doing its job, on a gate that genuinely cannot report PASS. The suite knew.
  3. **Fix the probes before merging `lane/control-plane`, not after.** A merge that turns
     `concurrency` green by accident, via a probe that was reading the wrong case all along, would
     record a pass nobody can attribute. Fix the instrument, re-measure the *current* branch to
     confirm it still FAILs for the right reason, then merge, then re-measure.
  4. **The sweep was run, and it found a third.** `bounded` — `g_failure_is_bounded` — has the
     identical shape: it reads the audits, computes the worst restart count, and returns
     `_fail("no attempt cap on restart")` **whatever it found**, including when it found no
     restarts at all. `test_every_gate_can_report_pass[bounded]` is red for that reason, and
     `bounded` is one of the five gates in `launch.UNATTENDED_GATES`. So **two** of the five
     bounding gates carry a probe that cannot pass, not one.

     ```python
     # every gate whose probe has no return path other than _fail
     reaper   g_orphans_are_reaped      ← defect; a reaper exists on lane/control-plane
     bounded  g_failure_is_bounded      ← defect; returns _fail whatever the audits say
     corpus   g_corpus_is_tamper_evident ← NOT a defect, see below
     ```

     ⭐ **`corpus` is exonerated, and the difference is the useful part.** It also has no `_pass`
     path, and its docstring says why in advance: separation of the grader from the graded *is
     not enforced*, and the gate refuses *"rather than passing on the strength of the other
     three"*. It reaches four distinct `_fail` reasons depending on what it observes, and it will
     become passable when the corpus moves to a repo this agent cannot write to. That is a
     **declared** cannot-pass-yet with the condition written down. `reaper` and `bounded` are
     **undeclared** ones that read as findings about the orchestrator. Same AST shape, opposite
     honesty — which is why the sweep is a starting point and not a verdict.

  5. **Still to sweep: case-sensitive identifier searches across the other probes.** Only the
     `_fail`-shape sweep has been run.


---

## Addendum, 2026-08-30 — fixed, plus a fourth instance in the checker itself

All three probes now **drive the control and watch it refuse** through a new `readiness._engine()`,
which imports `orchestrator.pipelines` from `$PREFECT_CONNECTORS` with its audit writes muted. Each
was calibrated in both directions against both checkouts:

```
cap          refused at 6 attempts, allowed at 0
bounded      refused; an override bought exactly one; the replay refused again
concurrency  0 slots empty, 6 in use over a ceiling of 4, manual gate = 0 slots
reaper       killed the 6h-expired lease (status -> failed), spared the live one
from-history all stages 'completed' + unreadable log -> failed/UNMEASURABLE, not succeeded
```

Against `chore/artefact-homes@8b7c68d`, which carries none of the controls, all five decline. The
instrument now separates *the control is missing* from *the control is here and works*, which is
the whole thing it could not do before.

⭐ **And a fourth instance, in the test that catches these.** `test_every_gate_can_report_pass`
reported `suite` as *"a constant, not a measurement"*. It is not — `g_contract_suite_green` does
`res = _pass(...)`, caches it, then `return res`. `_verdicts_reachable` only inspected the
*immediate* call in a `return`, so one level of indirection made a working probe look unreachable,
and that red was read for days as sibling-repo noise. The checker was fixed to follow a name back
to the helper it was assigned from, not the probe.

**The pattern across all four: an instrument that cannot see reports absence with total
confidence.** It is the same sentence as the `ZERO` vs `NOT-RECORDED` rule and the same sentence as
D-2's case-sensitive grep. It keeps arriving in new clothes.
