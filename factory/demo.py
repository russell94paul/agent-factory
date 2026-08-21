"""End-to-end demo: contract -> negative control -> task -> metrics.

Run: python -m factory.demo
Deploys nothing and touches no network. Proves the foundation holds together.
"""
from __future__ import annotations

from pathlib import Path

from .contract import GreenContract, Unmeasurable, Verdict
from .evals import mutate_and_expect_failure
from .metrics import MetricSet
from .tasks import EvidenceRequired, TaskStore

DATA = Path(".data")


def build_contract() -> GreenContract:
    c = GreenContract("connector-green")

    def rows_landed(ctx):
        n = ctx.get("rows")
        if n is None:
            raise Unmeasurable("row count unavailable - warehouse not reachable")
        return n > 0, f"{n} rows"

    def run_marker(ctx):
        sid = ctx.get("session_id")
        return bool(sid), f"session_id={sid!r}"

    def source_agrees(ctx):
        src, dst = ctx.get("source_rows"), ctx.get("rows")
        if src is None:
            raise Unmeasurable("source count unavailable - vendor API not reachable")
        return src == dst, f"source={src} warehouse={dst}"

    return (c.add("rows-landed", rows_landed)
             .add("run-marker-present", run_marker)
             .add("source-agrees", source_agrees))


def main() -> None:
    contract = build_contract()
    good = {"rows": 1200, "session_id": "ses_abc123", "source_rows": 1200}

    print("=" * 66)
    print("1. Baseline")
    print("  ", contract.run(good).summary())

    print("\n2. Negative control - the contract must NOTICE each break")
    reports = mutate_and_expect_failure(contract, good, {
        "rows": 0,                # nothing landed
        "session_id": None,       # run cannot be identified
        "source_rows": 999,       # silent data loss
    })
    for r in reports:
        print(f"   {'ok ' if r.ok else 'HOLE'}  {r.case:<28} {r.detail}")

    print("\n3. UNMEASURABLE is not a pass")
    dark = contract.run({"session_id": "ses_x"})          # no warehouse, no source
    print("  ", dark.summary(), "->  is_green =", dark.is_green)

    print("\n4. A task cannot close without evidence")
    store = TaskStore(DATA / "tasks.jsonl")
    tid = store.create("Migrate exchangeratesapi", actor="human")
    store.claim(tid, actor="implementer")
    try:
        store.close(tid, actor="implementer")
    except EvidenceRequired as exc:
        print("   refused:", exc)
    store.add_evidence(tid, "contract", "connector-green=PASS", actor="tester", basis="MEASURED")
    store.close(tid, actor="implementer")
    print("   closed with evidence ->", store.get(tid).status)

    print("\n5. Goodhart guard")
    m = MetricSet("pipeline-agent")
    m.outcome("fixes_applied")
    m.activity("escalations", paired_with="fixes_applied")
    m.get("escalations").bump(234)
    print("   suspicious:", m.suspicious())
    print("=" * 66)


if __name__ == "__main__":
    main()
