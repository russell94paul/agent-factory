"""CLI: judge one connector against its blueprint and emit a machine-readable verdict.

This is the shape the orchestrator's `verify-qa-success` stage should call. That stage today
requires a parallel `smoke-test-<connector>` deployment; exactly one exists across 37, so the
gate is structurally incapable of validating 36 of them — and it reports that inability as
`failed`, collapsing "this is broken" into "I could not check".

Run with no live probes and every assertion reports UNMEASURABLE. That is the honest answer for
an unwired harness, and it is deliberately not exit code 0.

    python -m factory.certify blueprints/windsorai_gep.yaml
    python -m factory.certify blueprints/windsorai_gep.yaml --calibrate   # known-good world
"""
from __future__ import annotations

import argparse
import json
import sys

from .connector_contract import CtxProbes, Probes, build_contract
from .contract import Verdict
from .targets import load_target


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="factory.certify")
    ap.add_argument("blueprint")
    ap.add_argument("--calibrate", action="store_true",
                    help="run against the recorded known-good world instead of live instruments")
    ap.add_argument("--json", action="store_true", help="emit JSON only")
    args = ap.parse_args(argv)

    target = load_target(args.blueprint)
    if args.calibrate:
        from .calibration import known_good_world
        result = build_contract(target, CtxProbes()).run(known_good_world())
    else:
        result = build_contract(target, Probes()).run({})

    payload = {
        "contract": result.contract,
        "verdict": result.verdict.value,
        "promotable": result.verdict is Verdict.PASS,
        "assertions": [{"name": r.name, "verdict": r.verdict.value, "detail": r.detail}
                       for r in result.results],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())
        for r in result.results:
            print(f"  {r}")
        if result.verdict is Verdict.UNMEASURABLE:
            print("\nUNMEASURABLE is not a pass. Wire the probes, or say so on the ticket.")
    # 0 only for a real pass: UNMEASURABLE and FAIL must both stop a promotion.
    return 0 if result.verdict is Verdict.PASS else 1


if __name__ == "__main__":
    sys.exit(main())
