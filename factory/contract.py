"""GreenContract — what "done" means, and what "I could not tell" means.

The root success object. Every team, every optimizer run and every certification reads its
verdict from here, so this module is deliberately dependency-free and boring.

**Four verdicts, never collapsed.** The distinction between FAIL and UNMEASURABLE is the entire
reason this file exists: a check whose instrument could not run has not passed, and reporting it
as a pass is how a measurement gap becomes a claim about the system.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Optional


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNMEASURABLE = "UNMEASURABLE"   # instrument could not run — NOT a pass
    NOT_RUN = "NOT_RUN"

    @property
    def is_pass(self) -> bool:
        return self is Verdict.PASS


@dataclass
class AssertionResult:
    name: str
    verdict: Verdict
    detail: str = ""
    observed: Any = None
    expected: Any = None

    def __str__(self) -> str:
        return f"[{self.verdict.value}] {self.name}: {self.detail}"


@dataclass
class Assertion:
    """One falsifiable claim.

    ``check`` returns (bool, detail). Raising ``Unmeasurable`` inside it yields UNMEASURABLE
    rather than FAIL — the caller must be able to tell "it is broken" from "I could not look".
    """
    name: str
    check: Callable[[dict], tuple]
    required: bool = True
    description: str = ""

    def run(self, ctx: dict) -> AssertionResult:
        try:
            ok, detail = self.check(ctx)
        except Unmeasurable as exc:
            return AssertionResult(self.name, Verdict.UNMEASURABLE, str(exc))
        except Exception as exc:                       # noqa: BLE001 - a crash is not a pass
            return AssertionResult(self.name, Verdict.UNMEASURABLE,
                                   f"instrument raised {type(exc).__name__}: {exc}")
        return AssertionResult(self.name, Verdict.PASS if ok else Verdict.FAIL, detail)


class Unmeasurable(Exception):
    """Raise inside a check when the instrument cannot run at all."""


@dataclass
class ContractResult:
    contract: str
    results: List[AssertionResult] = field(default_factory=list)

    @property
    def verdict(self) -> Verdict:
        """GREEN only when every required assertion PASSed.

        An UNMEASURABLE required assertion yields UNMEASURABLE for the whole contract — not FAIL,
        because we did not observe a failure, and emphatically not PASS.
        """
        if not self.results:
            return Verdict.NOT_RUN
        if any(r.verdict is Verdict.FAIL for r in self.results):
            return Verdict.FAIL
        if any(r.verdict is Verdict.UNMEASURABLE for r in self.results):
            return Verdict.UNMEASURABLE
        return Verdict.PASS

    @property
    def is_green(self) -> bool:
        return self.verdict is Verdict.PASS

    def failures(self) -> List[AssertionResult]:
        return [r for r in self.results if r.verdict is not Verdict.PASS]

    def summary(self) -> str:
        counts = {v: 0 for v in Verdict}
        for r in self.results:
            counts[r.verdict] += 1
        parts = [f"{v.value}={counts[v]}" for v in Verdict if counts[v]]
        return f"{self.contract}: {self.verdict.value} ({', '.join(parts)})"


@dataclass
class GreenContract:
    """A named set of assertions defining "this worked" for one unit of work."""
    name: str
    assertions: List[Assertion] = field(default_factory=list)

    def add(self, name: str, check: Callable[[dict], tuple],
            required: bool = True, description: str = "") -> "GreenContract":
        self.assertions.append(Assertion(name, check, required, description))
        return self

    def run(self, ctx: Optional[dict] = None) -> ContractResult:
        ctx = ctx or {}
        return ContractResult(self.name, [a.run(ctx) for a in self.assertions])
