"""CLI: judge one connector against its blueprint and emit a machine-readable verdict.

This is the shape the orchestrator's `verify-qa-success` stage should call. That stage today
requires a parallel `smoke-test-<connector>` deployment; exactly one exists across 37, so the
gate is structurally incapable of validating 36 of them — and it reports that inability as
`failed`, collapsing "this is broken" into "I could not check".

Run with no live probes and every assertion reports UNMEASURABLE. That is the honest answer for
an unwired harness, and it is deliberately not exit code 0.

    python -m factory.certify blueprints/windsorai_client_a.yaml
    python -m factory.certify blueprints/windsorai_client_a.yaml --calibrate   # known-good world
    python -m factory.certify blueprints/windsorai_client_a.yaml --remote --run-id r1   # not us

**`--calibrate` and `--remote` are not two flavours of the same thing.** `--calibrate` scores
in-process, with the same identity as whoever ran it — fine for developing the contract, worthless
as evidence that an agent did not grade itself. `--remote` submits the blueprint to the evaluator
service and takes back a verdict it did not compute; see `factory/evaluator.py` for why the
submission carries three fields and cannot carry a fourth.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

from .connector_contract import CtxProbes, Probes, build_contract
from .contract import Verdict
from .targets import load_target


def _remote(args) -> int:
    """Submit to the evaluator and report what it said. Compute nothing.

    There is no local-scoring fallback here on purpose. An unreachable evaluator yields
    UNMEASURABLE and a non-zero exit — the alternative is a promotion gate that quietly grades
    itself on the day the grader is down, which is the whole defect in one line.
    """
    from .evaluator import EvaluatorClient, EvaluatorError, Submission

    path = pathlib.Path(args.blueprint).resolve()
    if not path.is_file():
        print(f"no blueprint at {path}", file=sys.stderr)
        return 1
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    run_id = args.run_id or f"certify-{path.stem}-{sha[:12]}"

    try:
        client = EvaluatorClient()
        verdict = client.submit(Submission(path.as_uri(), sha, run_id))
    except EvaluatorError as exc:
        print(json.dumps({"verdict": Verdict.UNMEASURABLE.value, "promotable": False,
                          "detail": str(exc)}, indent=2) if args.json else
              f"UNMEASURABLE — {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(verdict.raw, indent=2, sort_keys=True))
    else:
        print(verdict.summary())
        for a in verdict.assertions:
            print(f"  [{a['verdict']}] {a['name']}: {a['detail']}")
        if verdict.raw.get("detail"):
            print(f"\n  {verdict.raw['detail']}")
        sa = verdict.scored_against
        if sa:
            print(f"\n  scored against corpus {sa['corpus']} ({sa['sha256'][:12]}, recorded "
                  f"{sa['recorded']}) — REPLAYED, not a live measurement")
        print(f"  recorded to {verdict.raw.get('recorded_to') or 'NOWHERE — see store_error'}")
    return 0 if verdict.is_pass else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="factory.certify")
    ap.add_argument("blueprint")
    ap.add_argument("--calibrate", action="store_true",
                    help="run against the recorded known-good world instead of live instruments")
    ap.add_argument("--json", action="store_true", help="emit JSON only")
    ap.add_argument("--remote", action="store_true",
                    help="submit to the evaluator at $AGENT_FACTORY_EVALUATOR rather than "
                         "scoring in-process")
    ap.add_argument("--run-id", default=None, help="run id for a --remote submission")
    args = ap.parse_args(argv)

    if args.remote:
        return _remote(args)

    scored_against = None
    if args.calibrate:
        from .calibration import calibration_target, known_good_world, provenance
        # Read the stamp BEFORE scoring: if the corpus does not verify, this raises here rather
        # than producing a verdict nobody can tie to a world.
        scored_against = provenance()
        # Calibration scores the CORPUS world against the CORPUS's own declared scope, not
        # against the shipped blueprint's. It has to: the corpus is a closed world whose rows and
        # tenants must agree with each other, while the blueprint's tenants describe live runs.
        # Mixing them made A12 fail the moment the real account ids were filled in — the contract
        # correctly rejecting a placeholder world, but reported as a broken calibration.
        target = calibration_target()
        result = build_contract(target, CtxProbes()).run(known_good_world())
    else:
        target = load_target(args.blueprint)
        result = build_contract(target, Probes()).run({})

    payload = {
        "contract": result.contract,
        "verdict": result.verdict.value,
        "promotable": result.verdict is Verdict.PASS,
        # A verdict with no corpus is a live run; a verdict WITH one was replayed and must say so.
        # Without this a calibration result and a production result are indistinguishable.
        "scored_against": scored_against,
        "assertions": [{"name": r.name, "verdict": r.verdict.value, "detail": r.detail}
                       for r in result.results],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())
        for r in result.results:
            print(f"  {r}")
        if scored_against:
            print(f"\n  scored against corpus {scored_against['corpus']} "
                  f"({scored_against['sha256'][:12]}…, recorded {scored_against['recorded']}) "
                  f"— REPLAYED, not a live measurement")
        if result.verdict is Verdict.UNMEASURABLE:
            print("\nUNMEASURABLE is not a pass. Wire the probes, or say so on the ticket.")
    # 0 only for a real pass: UNMEASURABLE and FAIL must both stop a promotion.
    return 0 if result.verdict is Verdict.PASS else 1


if __name__ == "__main__":
    sys.exit(main())
