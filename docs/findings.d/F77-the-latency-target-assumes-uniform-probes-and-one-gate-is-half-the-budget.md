<!-- session: 2026-08-23 · R13 rewrite handoff, blocked -->

### F77 — The tracker latency target assumes 30 uniform probes; one gate is roughly half the budget and cannot be split

- **KIND** — DESIGN
- **STATUS** — OPEN
- **BELIEVED** — from the R13 run-2 handoff: *"`factory.readiness.measure()` runs 30 gates serially
  in 9.3 s; the loop is `for g in GATES: g.probe()` over independent I/O-bound probes; the server is
  `socketserver.TCPServer`, so two concurrent requests return empty. **An 8-wide pool puts a page
  near 1.2 s.** Ask what each technique buys in milliseconds against that."*
- **ACTUALLY** — the first three facts are confirmed. **The projection is not**, because the probes
  are not uniform and one of them is not I/O.

  `g_contract_suite_green` (gate `suite`) shells out to a **full `python -m pytest` subprocess**,
  `timeout=300`. It is one indivisible unit of work that no pool can subdivide. Measured in a Linux
  container at `8010676`:

      per-gate timing, all 30 gates        total 0.53 s
        suite                              0.43 s   = 81.8% of total
        certified                          0.09 s   = 16.3%
        the other 28 gates combined        0.01 s   =  1.9%

  ⚠ **That 0.43 s flatters it badly** — pytest aborts at *collection* here because of [[F75]], so
  the gate is timing a crash. With collection working (105 tests, `--ignore` the F75-blocked
  module) the same subprocess takes **4.68 s, reproducible over two runs**. The operator's machine
  runs 135 tests, on Windows process-spawn, with a corpus that loads — so `suite` is plausibly
  **half or more of the reported 9.3 s**.

  ⭐ **Parallel speedup floors at the slowest single task, not at total÷width.** Against a ~4.7 s
  `suite`:

      handoff model   30 uniform independent probes, 8-wide   -> 9.3/8  = 1.16 s
      actual shape    one ~4.7 s subprocess + the rest        -> floor  = 4.7 s at ANY width

  **The 1.2 s target is roughly 4× out and is not reachable by concurrency at all.** Widening the
  pool past 2 buys almost nothing, because 28 of the 30 gates already sum to under 2% of the work.

  ⭐ **The consequence for the research pass is the point of filing this.** Run 2 is to be asked
  *"what does each technique buy in milliseconds against that baseline."* Handing a researcher a
  baseline of *30 uniform I/O-bound probes* guarantees answers about thread pools, async I/O and
  connection reuse — every one of which is correct in general and worth **near zero here**. The
  question that matters is not *how do we parallelise 30 probes*, it is **why is a full test suite
  running inside a page load at all.**

- **MEASURED BY** — `factory/readiness.py:1007` for the serial loop;
  `scripts/local_tracker.py:1395` for `socketserver.TCPServer` (single-threaded, confirming the
  two-concurrent-requests observation). Then per-gate timing:

      python -c "import time; from factory import readiness
                 [ (time.perf_counter(), g.probe()) for g in readiness.GATES ]"   # timed per gate

  and the subprocess cost on its own:

      python -c "import subprocess,time; t=time.perf_counter();
                 subprocess.run(['python3','-m','pytest','--no-header','--tb=no',
                 '-p','no:cacheprovider','--ignore=tests/test_connector_contract.py'],
                 capture_output=True); print(time.perf_counter()-t)"
      -> 4.69, 4.67

  ⚠ **Re-measure on the operator's machine before quoting a ratio.** Per [[F72]] the gate mix
  differs by cwd and by platform, and the 9.3 s figure is from there while these are from here.
  What is platform-independent is the *shape*: one subprocess that cannot be divided dominates a
  pool of trivial file reads.

- **CHANGES** — two, and they are different kinds of change.

  1. **Do not run the suite inside the request.** Cache its result against the git SHA of `tests/`
     and `factory/`, or run it out of band and read the last result with its age attached. The
     estate's rule is *"a cached figure carries its age in the same string"*, which is exactly the
     escape hatch needed: `suite: 105 passed (as of 4 min ago, at a1b2c3d)` is honest and costs
     nothing. **This is an architecture change, not a concurrency change**, and it is the only one
     that reaches 1.2 s.
  2. **State the real baseline in the R13 run-2 prompt** — one ~4.7 s indivisible subprocess plus
     ~28 trivial file reads — and ask what each technique buys against *that*. Ask specifically
     what the state of the art does about **an expensive verification inside an interactive
     surface**, which is the actual problem, rather than about pool width.

  ⚠ A pool is still worth building for the other 29 gates once `suite` is out of the request path;
  the objection is to the projection, not to concurrency.

- **AFFECTS** — **every lane**, since the readiness board is how each reads its own state; the R13
  run-2 prompt (its item 2 would otherwise dispatch on a wrong baseline and buy irrelevant answers);
  `scripts/local_tracker.py` and the `10–19 s page` figure quoted in
  `docs/research/ui-surface-inventory.md` §5 and §6 item 7, and in
  `docs/specs/agent-factory-technical-and-business-spec.md` §8.4, all of which describe the symptom
  without naming this cause. Compounds [[F75]]: while the corpus hash is unfixed, `suite` on any
  non-Windows checkout times a crashing pytest and the gate looks four times cheaper than it is.
