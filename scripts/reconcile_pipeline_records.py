"""Run the build plane's status reconciler against a real orchestrator data directory.

`reconcile_status_with_history()` runs at every `configure()`, so from the next time the
orchestrator starts this happens on its own. This script exists for the record that is
already wrong: `pipe_29b8edf6` has read "running" since 2026-05-28 over a log that ends
`stage_failed`, and nothing will start that process tonight.

It is deliberately two-step. `--dry-run` (the default) reports what the reconciler WOULD
correct without writing anything; `--apply` writes, after taking a rollback copy of every
file it is about to touch. The estate's rule is that a non-destructive validation comes
before any mutation and a rollback is captured before it, so that is the shape.

    python scripts/reconcile_pipeline_records.py --data <dir>
    python scripts/reconcile_pipeline_records.py --data <dir> --apply --rollback <dir>

⚠ This CORRECTS a record; it does not rewrite history. Every correction writes a
`status_reconciled` event carrying the old value, so the record's history of having been
wrong survives being made right.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys


def _load_engine(connectors: pathlib.Path):
    if not (connectors / "orchestrator" / "pipelines.py").is_file():
        sys.exit(f"no orchestrator/pipelines.py at {connectors}")
    sys.path.insert(0, str(connectors))
    from orchestrator import pipelines as engine
    from orchestrator.engine import audit as audit_trail
    return engine, audit_trail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, type=pathlib.Path,
                    help="orchestrator data directory holding pipelines.json and audits/")
    ap.add_argument("--connectors", type=pathlib.Path,
                    default=pathlib.Path(__file__).resolve().parents[2] / "prefect-connectors",
                    help="prefect-connectors checkout to take the engine from")
    ap.add_argument("--apply", action="store_true",
                    help="write the corrections; without it nothing is modified")
    ap.add_argument("--rollback", type=pathlib.Path,
                    help="directory to copy every touched file into before writing")
    args = ap.parse_args()

    if args.apply and not args.rollback:
        sys.exit("--apply requires --rollback: capture a rollback before mutating a record")

    engine, audit_trail = _load_engine(args.connectors)

    # Read-only pass first, against a scratch copy, so the report is produced without the
    # data directory ever being opened for writing.
    import tempfile
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="reconcile-dry-"))
    shutil.copytree(args.data / "audits", scratch / "audits")
    shutil.copy2(args.data / "pipelines.json", scratch / "pipelines.json")
    audit_trail.configure(scratch, scratch / "sessions")
    engine._pipelines.clear()
    engine._DATA_DIR = None          # _load() is driven manually below, not via configure
    engine.configure(scratch)        # configure() reconciles, on the COPY

    listed = json.loads((args.data / "pipelines.json").read_text(encoding="utf-8"))["pipelines"]
    before = {p["id"]: p.get("status") for p in listed}
    after = {pid: p.get("status") for pid, p in engine._pipelines.items()}
    changes = [(pid, before.get(pid), after.get(pid))
               for pid in before if before.get(pid) != after.get(pid)]

    print(f"data       {args.data}")
    print(f"engine     {args.connectors}")
    print(f"pipelines  {len(before)} recorded\n")
    if not changes:
        print("Nothing to reconcile: every recorded status already agrees with its log.")
        return 0
    for pid, was, now in changes:
        p = engine._pipelines[pid]
        v = p.get("verdict", {})
        print(f"  {pid}   {was}  ->  {now}")
        print(f"      basis            {v.get('basis')}")
        print(f"      clean            {v.get('clean')}")
        print(f"      failures in log  {v.get('failures_in_log')}")
        print(f"      closed because nothing further can ever run: "
              f"{v.get('unreachable_close')}")

    if not args.apply:
        print(f"\nDRY RUN — {len(changes)} correction(s) computed on a scratch copy at")
        print(f"{scratch}\nNothing under {args.data} was modified. Re-run with --apply "
              f"--rollback <dir> to write.")
        return 0

    args.rollback.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.data / "pipelines.json", args.rollback / "pipelines.json")
    for pid, _, _ in changes:
        f = args.data / "audits" / f"{pid}.json"
        if f.exists():
            shutil.copy2(f, args.rollback / f.name)
    print(f"\nrollback captured in {args.rollback}: "
          f"{', '.join(sorted(p.name for p in args.rollback.iterdir()))}")

    engine._pipelines.clear()
    engine._DATA_DIR = None
    audit_trail.configure(args.data, args.data / "sessions")
    engine.configure(args.data)      # configure() reconciles, and _flush()es
    applied = json.loads((args.data / "pipelines.json").read_text(encoding="utf-8"))["pipelines"]
    now = {p["id"]: p.get("status") for p in applied}
    print("\nAPPLIED:")
    for pid, was, expected in changes:
        got = now.get(pid)
        print(f"  {pid}   {was} -> {got}   "
              f"{'as predicted' if got == expected else f'UNEXPECTED (predicted {expected})'}")
    return 0 if all(now.get(p) == e for p, _, e in changes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
