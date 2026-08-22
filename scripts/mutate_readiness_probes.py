"""Do the control-plane gates change their answer when the control is removed?

`tests/test_readiness_probes_can_pass.py` proves a PASS verdict is *written* in each
probe. That is a static check and it cannot see whether the PASS is reachable, or whether
the probe would notice the control disappearing. This does.

For each control it copies the connectors checkout's `orchestrator/` into a scratch tree,
deletes the control there, points `$PREFECT_CONNECTORS` at the copy, and re-runs the gate.
The gate must go from PASS to FAIL. A gate that stays green over a system with the control
removed is measuring something other than the control.

    python scripts/mutate_readiness_probes.py

Exit code 0 means every control-plane gate is load-bearing.

⚠ Nothing under the real checkout is ever written. The whole point of a probe mutation is
that it must not require breaking the thing being measured, and a harness that mutated the
live tree would be one crash away from leaving a control removed —
`prefect-connectors/tests/orchestrator/mutate_control_plane.py` did exactly that until
2026-08-22, and a tool timeout killed it mid-mutation once. It now copies too.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

FACTORY = pathlib.Path(__file__).resolve().parent.parent
CONNECTORS = pathlib.Path(os.environ.get("PREFECT_CONNECTORS",
                                         FACTORY.parent / "prefect-connectors"))

#: (gate id, [(anchor, replacement)], what the mutation removes[, target file])
MUTATIONS = [
    ("cap",
     [("""    used = attempts(stage)
    if used < MAX_ATTEMPTS_PER_STAGE:
        return""",
       """    used = attempts(stage)
    if True:
        return"""),
      ('        if attempts(stage) >= MAX_ATTEMPTS_PER_STAGE and not stage.pop("_cap_grant", None):',
       "        if False:")],
     "both cap checks — the entry points and the choke point"),

    ("bounded",
     [('        if attempts(stage) >= MAX_ATTEMPTS_PER_STAGE and not stage.pop("_cap_grant", None):',
       "        if False:")],
     "the ceiling at the choke point, so a watchdog can dispatch forever"),

    ("concurrency",
     [('        if _holds_a_dispatch_slot({**stage, "status": "dispatched"}) and free <= 0:',
       "        if False:")],
     "the dispatch ceiling branch"),

    ("reaper",
     [("""    now = datetime.now(timezone.utc)
    reaped: List[Dict[str, Any]] = []
    unmeasurable: List[Dict[str, Any]] = []""",
       """    return []
    now = datetime.now(timezone.utc)
    reaped: List[Dict[str, Any]] = []
    unmeasurable: List[Dict[str, Any]] = []""")],
     "reap_expired_leases, which now reaps nothing"),

    ("from-history",
     [("""    if not path.exists():
        raise HistoryUnreadable(f"no audit log at {path}")""",
       """    if not path.exists():
        return {}""")],
     "the refusal to treat a missing log as an empty one"),

    # The mutation this harness did not have, and the reason the gate needed rewriting a
    # second time: reverting ONLY `any_failed` to the original last-write-wins expression
    # left the gate reading PASS over a system with the defect it is named for.
    ("from-history",
     [("""    any_failed = any(o["last_terminal"] == "failed" and not o["tolerated"]
                     for o in event_outcomes)""",
       """    any_failed = any(s["status"] == "failed" and not s.get("continue_on_failure")
                     for s in stage_records)""")],
     "the verdict's history replay ALONE — the defect the gate is named for"),

    # Likewise for `cap`: the probe builds a stage with _attempts already at the ceiling,
    # so it never established that the production path INCREMENTS the counter.
    ("cap",
     [('        stage["_attempts"] = attempts(stage) + 1',
       '        stage["_attempts"] = attempts(stage)')],
     "the only write to _attempts — the cap can now never fire"),

    ("reaper",
     [('            stage["status"] = "failed"\n            stage["error"] = error',
       '            stage["status"] = "pending"\n            stage["error"] = error')],
     "the terminal kill — the reaper now recovers instead, so the orphan runs again"),

    # The half the gate was blind to until 2026-08-22. Removing the call leaves a reaper
    # that closes the record perfectly and leaves the container burning a shared core —
    # which is what the gate said PASS to for its whole life before this mutation existed.
    ("reaper",
     [("            termination = _terminate_external_work(pipeline[\"id\"], stage, _deadline)",
       "            termination = []")],
     "the call that kills the cloud work behind a reaped stage"),

    # And the recorder, separately: a terminator nothing can hand a handle to is a
    # terminator that is never reached. Two halves, two mutations, because a compound one
    # reports a kill and lets you credit it to the wrong half (finding F18).
    ("reaper",
     [("        handles.append({\"kind\": kind, \"id\": handle_id, \"name\": handle_name,\n"
       "                        \"recorded_at\": _now_iso()})",
       "        pass")],
     "the durable handle — nothing is left for the reaper to kill"),

    # The two an independent review used to satisfy this gate while the production
    # path was dead. Both edits leave the IMPORT in place, which is precisely how the
    # old substring checks survived them: `"cloud_reaper" in src` was true of a module
    # that registered nothing, and `_report_run(ctx,` counted CALL SITES while the
    # function they all called did nothing at all.
    ("reaper",
     [("        _cloud_reaper.register(engine)\n        return True",
       "        return True")],
     "the registration call — the terminator is never wired, though the import remains",
     "orchestrator/server.py"),

    ("reaper",
     [('        rid = (run or {}).get("id") or ""\n        if rid:\n            ctx.report_external_handle("prefect_flow_run", rid, (run or {}).get("name", ""))',
       "        pass")],
     "the BODY of _report_run — every launch site still calls it and it records nothing",
     "orchestrator/stage_scripts/prefect_ops.py"),
]


def _gate_verdict(gate_id: str, connectors: pathlib.Path) -> str:
    """Run ONE gate in a subprocess against a given checkout, and return its verdict.

    A subprocess because the probes import the build plane and cache the module; a second
    verdict in the same process would be answered by the first checkout's code.
    """
    code = (
        "import json, sys;"
        "from factory import readiness as r;"
        f"g = next(g for g in r.GATES if g.id == {gate_id!r});"
        "\ntry:\n    res = g.probe()\n    print(res.verdict)\n"
        "except r.Unmeasurable as e:\n    print('UNMEASURABLE')\n"
        "except Exception as e:\n    print('ERROR:' + type(e).__name__ + ':' + str(e)[:120])\n"
    )
    env = dict(os.environ, PREFECT_CONNECTORS=str(connectors), PYTHONPATH=str(FACTORY))
    r = subprocess.run([sys.executable, "-c", code], cwd=FACTORY, env=env,
                       capture_output=True, text=True)
    out = [ln for ln in r.stdout.splitlines() if ln.strip()]
    return out[-1] if out else f"NO OUTPUT (rc={r.returncode}) {r.stderr.strip()[-160:]}"


def main() -> int:
    if not (CONNECTORS / "orchestrator" / "pipelines.py").is_file():
        print(f"no orchestrator/pipelines.py at {CONNECTORS}")
        return 2

    print(f"connectors  {CONNECTORS}\n")
    results = []
    for mutation in MUTATIONS:
        gate_id, edits, removes = mutation[:3]
        target_rel = mutation[3] if len(mutation) > 3 else 'orchestrator/pipelines.py'
        scratch = pathlib.Path(tempfile.mkdtemp(prefix="probe-mutation-"))
        try:
            shutil.copytree(CONNECTORS / "orchestrator", scratch / "orchestrator",
                            ignore=shutil.ignore_patterns("__pycache__", "data", "data-pr",
                                                          "sessions", "health"))
            # `prefect_ops` inserts ACTIVATION_API_DIR on sys.path and imports
            # PrefectService from it, so a scratch tree holding only `orchestrator/`
            # cannot import it — and the reaper gate would then report NOT-IMPORTABLE
            # and FAIL for a reason that has nothing to do with the mutation. A kill
            # credited to the wrong half is the tail of finding F18, so the copy
            # carries `.deploy` too.
            src_deploy = CONNECTORS / '.deploy'
            if src_deploy.is_dir():
                shutil.copytree(src_deploy, scratch / '.deploy',
                                ignore=shutil.ignore_patterns('__pycache__'))
            # The history-measured gates need the audit files; they are small.
            src_audits = CONNECTORS / "orchestrator" / "data" / "audits"
            if src_audits.is_dir():
                shutil.copytree(src_audits, scratch / "orchestrator" / "data" / "audits")
            pj = CONNECTORS / "orchestrator" / "data" / "pipelines.json"
            if pj.is_file():
                shutil.copy2(pj, scratch / "orchestrator" / "data" / "pipelines.json")

            target = scratch / target_rel
            body = target.read_text(encoding="utf-8")
            missing = [a for a, _ in edits if body.count(a) != 1]
            if missing:
                print(f"  !!  {gate_id}: an anchor is not present exactly once — the "
                      f"mutation could not be applied, so this gate is UNTESTED")
                results.append((gate_id, "ANCHOR-MISSING", removes))
                continue
            for anchor, replacement in edits:
                body = body.replace(anchor, replacement, 1)
            target.write_text(body, encoding="utf-8")
            compile(body, str(target), "exec")

            before = _gate_verdict(gate_id, CONNECTORS)
            after = _gate_verdict(gate_id, scratch)
            # after == "FAIL" specifically. `!= "PASS"` also accepted UNMEASURABLE and
            # ERROR, so a mutation that merely broke the scratch tree's import would have
            # reported LOAD-BEARING — the gate noticing nothing except that it could not
            # look. A control-plane gate must REFUSE, not merely fail to measure.
            ok = before == "PASS" and after == "FAIL"
            results.append((gate_id, "LOAD-BEARING" if ok else "NOT MEASURING", removes))
            print(f"  {'ok ' if ok else '!! '} {gate_id}")
            print(f"       removed: {removes}")
            print(f"       intact -> {before}   mutated -> {after}")
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    print()
    bad = [r for r in results if r[1] != "LOAD-BEARING"]
    for gate_id, verdict, removes in results:
        print(f"  {verdict:14s} {gate_id:14s} {removes}")
    if bad:
        print(f"\n{len(bad)} gate(s) that do not notice their own control disappearing.")
        return 1
    print(f"\nAll {len(results)} mutations flipped their gate off PASS: every "
          f"control-plane gate is measuring the control it names.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
