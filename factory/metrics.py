"""Metrics — every activity metric paired with an outcome metric.

The retired agent's dashboard would have shown 234 escalations and 233 diagnoses climbing steadily.
A self-improving loop pointed at those numbers would have optimised for *escalating faster* and
called it progress. So this module refuses to register an activity metric that has no paired
outcome metric: the pairing is enforced, not documented.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class GoodhartViolation(Exception):
    """Raised when an activity metric is registered with no outcome metric to anchor it."""


@dataclass
class Metric:
    name: str
    kind: str              # "activity" | "outcome"
    value: float = 0.0
    paired_with: Optional[str] = None
    basis: str = "MEASURED"

    def bump(self, by: float = 1.0) -> None:
        self.value += by


class MetricSet:
    def __init__(self, name: str):
        self.name = name
        self._m: Dict[str, Metric] = {}

    def outcome(self, name: str, basis: str = "MEASURED") -> Metric:
        m = Metric(name, "outcome", basis=basis)
        self._m[name] = m
        return m

    def activity(self, name: str, paired_with: str, basis: str = "MEASURED") -> Metric:
        """An activity metric MUST name an outcome metric that already exists."""
        target = self._m.get(paired_with)
        if target is None or target.kind != "outcome":
            raise GoodhartViolation(
                f"activity metric {name!r} must be paired with a registered outcome metric; "
                f"{paired_with!r} is {'missing' if target is None else target.kind}. "
                "An activity metric with no outcome anchor is how 234 escalations looked like progress.")
        m = Metric(name, "activity", paired_with=paired_with, basis=basis)
        self._m[name] = m
        return m

    def get(self, name: str) -> Metric:
        return self._m[name]

    def report(self) -> List[dict]:
        out = []
        for m in self._m.values():
            row = {"name": m.name, "kind": m.kind, "value": m.value, "basis": m.basis}
            if m.paired_with:
                anchor = self._m[m.paired_with]
                row["paired_with"] = m.paired_with
                row["anchor_value"] = anchor.value
                # the ratio that would have exposed the retired agent immediately
                row["ratio"] = (anchor.value / m.value) if m.value else 0.0
            out.append(row)
        return out

    def suspicious(self) -> List[str]:
        """Activity climbing while its outcome stays at zero — the 234/0 signature."""
        bad = []
        for m in self._m.values():
            if m.kind == "activity" and m.value > 0:
                if self._m[m.paired_with].value == 0:
                    bad.append(f"{m.name}={m.value:.0f} but {m.paired_with}=0")
        return bad
