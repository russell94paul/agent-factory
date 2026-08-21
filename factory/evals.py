"""The eval harness — and the negative control that makes it mean something.

An eval nobody has proved can fail is decoration. ``mutate_and_expect_failure`` exists so a green
suite is evidence rather than a claim: it deliberately breaks the world and asserts the contract
notices.

The eval corpus lives on disk **outside any agent-writable directory**. An agent that can edit
its own fitness function will reach 100%.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List

from .contract import ContractResult, GreenContract, Verdict


@dataclass
class EvalCase:
    """One scenario: a world state, and the contract that should judge it."""
    name: str
    setup: Callable[[], dict]
    expect: Verdict = Verdict.PASS
    tags: List[str] = field(default_factory=list)


@dataclass
class EvalReport:
    case: str
    expected: Verdict
    actual: Verdict
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.expected is self.actual


class EvalSuite:
    def __init__(self, contract: GreenContract, corpus_dir: Path | None = None):
        self.contract = contract
        self.cases: List[EvalCase] = []
        self.corpus_dir = corpus_dir

    def add(self, case: EvalCase) -> "EvalSuite":
        self.cases.append(case)
        return self

    def run(self) -> List[EvalReport]:
        out = []
        for c in self.cases:
            res: ContractResult = self.contract.run(c.setup())
            out.append(EvalReport(c.name, c.expect, res.verdict, res.summary()))
        return out

    def certify(self) -> bool:
        """Every case must land on its expected verdict — including the ones expected to FAIL."""
        return all(r.ok for r in self.run())


def mutate_and_expect_failure(contract: GreenContract, base_ctx: dict,
                              mutations: Dict[str, Any]) -> List[EvalReport]:
    """⭐ The negative control.

    For each mutation, break one thing in the world and assert the contract stops being green.
    A mutation that leaves the contract GREEN is a hole in the contract, and is reported as a
    failing report so CI goes red.
    """
    reports: List[EvalReport] = []
    baseline = contract.run(base_ctx)
    reports.append(EvalReport("baseline-must-be-green", Verdict.PASS,
                              baseline.verdict, baseline.summary()))
    for key, bad_value in mutations.items():
        ctx = dict(base_ctx)
        ctx[key] = bad_value
        res = contract.run(ctx)
        # we expect NOT-green; encode that as: actual must not be PASS
        actual = Verdict.FAIL if res.verdict is not Verdict.PASS else Verdict.PASS
        reports.append(EvalReport(f"mutation:{key}", Verdict.FAIL, actual, res.summary()))
    return reports


def write_report(reports: List[EvalReport], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(
        [{"case": r.case, "expected": r.expected.value,
          "actual": r.actual.value, "ok": r.ok, "detail": r.detail} for r in reports],
        indent=2), encoding="utf-8")
