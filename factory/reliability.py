"""The two reliability metrics that need no new field — measured before anything is added.

⭐ **These two exist to prove the instrument can see a non-zero before we trust it to report a
zero.** Eight of the ten metrics in `docs/protocol/METRICS.md` are NOT-RECORDED today because the
fields they need did not exist. These two do not need them: metric 7 folds the task store's
`block` edges, which are live (25 events), and metric 9 folds the event stream's verdicts, which
have been written since 2026-08-30. Shipping them first means the baseline is measured under the
*old* behaviour, so any later movement is attributable.

⚠ **Both are registered through `factory.metrics`**, so every activity metric names an outcome
anchor or `GoodhartViolation` refuses it at registration. That is not ceremony: a "warnings
emitted" counter with nothing to anchor it is exactly the 234-escalations dashboard that module
was written about, and this patch's whole risk is producing one.

⛔ **Three verdicts, never one number.** A rate over an empty population is not zero — it is
NOT-MEASURABLE, and `Rate.basis` says which. `first_pass_green()` today returns 0.0 with basis
MEASURED and `instrument_live=True`, and that combination is the interesting one: the stream
*would* have registered a PASS, and none occurred, because no preset could produce one (F87).
A zero from an instrument nobody has proved can see is not a measurement.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional

from .contract import Verdict
from .metrics import MetricSet

MEASURED = "MEASURED"
NOT_MEASURABLE = "NOT-MEASURABLE"
NOT_RECORDED = "NOT-RECORDED"


@dataclass
class Rate:
    """A ratio that refuses to be quoted without its population and its basis."""
    name: str
    numerator: int
    denominator: int
    basis: str
    detail: str = ""
    instrument_live: Optional[bool] = None

    @property
    def value(self) -> Optional[float]:
        return (self.numerator / self.denominator) if self.denominator else None

    def __str__(self) -> str:
        if self.value is None:
            return f"{self.name}: {NOT_MEASURABLE} (population is empty) — {self.detail}"
        live = ""
        if self.instrument_live is not None:
            live = ("  [instrument proven live]" if self.instrument_live
                    else "  ⚠ [instrument NEVER seen to register a non-zero]")
        return (f"{self.name}: {self.numerator}/{self.denominator} = {self.value:.3f} "
                f"[{self.basis}]{live}" + (f" — {self.detail}" if self.detail else ""))


# ------------------------------------------------------------------------------- metric 7

def dependency_violations(path=None) -> Rate:
    """Metric 7 — tasks claimed while a declared blocker was still open.

    Replays the task store in file order rather than reading the folded state: the question is
    *"was this task blocked at the moment somebody took it"*, and the fold only knows what is true
    now. A task blocked after it was claimed is not a violation, and a task unblocked before it
    was claimed is not one either; only the ordered replay can tell them apart.
    """
    from . import repo as _repo
    p = path or (_repo.data() / "tasks.jsonl")
    if not p.is_file():
        return Rate("dependency_violation_rate", 0, 0, NOT_RECORDED,
                    detail=f"no task store at {p}")
    blocked: Dict[str, set] = {}
    started = violations = 0
    offenders: List[str] = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue                      # a torn append must not lose the rest — bus.py's rule
        tid, kind = ev.get("task"), ev.get("kind")
        if kind == "block":
            blocked.setdefault(tid, set()).add(ev.get("data", {}).get("by"))
        elif kind == "unblock":
            blocked.get(tid, set()).discard(ev.get("data", {}).get("by"))
        elif kind == "claim":
            started += 1
            if blocked.get(tid):
                violations += 1
                offenders.append(tid)
    return Rate("dependency_violation_rate", violations, started, MEASURED,
                detail=(f"offending task(s): {offenders}" if offenders
                        else "every claim had its declared blockers cleared"),
                # The instrument has been shown able to see a block edge; whether it has ever seen
                # a violation is a different claim, and this is the honest one.
                instrument_live=bool(blocked))


# ------------------------------------------------------------------------------- metric 9

def first_pass_green() -> Rate:
    """Metric 9 — runs that reached PASS with no earlier attempt at the same ticket.

    ⚠ The denominator is runs that reached a terminal verdict, not runs that started. A run whose
    process died before a verdict was assigned has an outcome nobody observed; counting it as a
    non-green would report our own crash as the ticket's failure.
    """
    from . import events as _events
    seen: Dict[str, int] = {}
    completed = green = 0
    for run_id in _events.runs():
        fold = _events.fold(run_id)
        ticket, verdict = fold.get("ticket"), fold.get("verdict")
        if verdict is None:
            continue
        completed += 1
        prior = seen.get(ticket, 0)
        seen[ticket] = prior + 1
        if verdict == Verdict.PASS.value and prior == 0:
            green += 1
    return Rate("first_pass_green_rate", green, completed, MEASURED if completed else NOT_RECORDED,
                detail=(f"{len(seen)} distinct ticket(s) across {completed} completed run(s)"
                        if completed else "nothing has executed through factory.control"),
                # ⛔ FALSE today, and that is the point. The stream can express PASS — the enum and
                # the contract both do — but no run has ever produced one, so a zero here has not
                # yet been shown to be a measurement rather than a blind instrument. It becomes
                # True the first time any run passes. Do not quote this rate without this flag.
                instrument_live=green > 0)


# ------------------------------------------------------------------------------- the pairing

def metric_set() -> MetricSet:
    """Both rates, registered so the Goodhart pairing is enforced rather than remembered.

    ⭐ The pairing that matters for this patch: `known_failure_warnings` is an ACTIVITY metric —
    how many times the preflight spoke — and it is anchored to `first_pass_green_rate`. If
    warnings climb while green stays at zero, `suspicious()` says so in one line. That is the
    234/0 signature, and this patch is exactly the kind of work that could produce it.
    """
    from . import preflight as _preflight
    ms = MetricSet("reliability")
    dep = dependency_violations()
    fpg = first_pass_green()
    ms.outcome("first_pass_green_rate", basis=fpg.basis)
    ms.get("first_pass_green_rate").value = fpg.value or 0.0
    ms.outcome("dependency_violation_rate", basis=dep.basis)
    ms.get("dependency_violation_rate").value = dep.value or 0.0
    ms.activity("known_failure_warnings", paired_with="first_pass_green_rate", basis=MEASURED)
    ms.get("known_failure_warnings").value = sum(
        1 for r in _preflight.invocations() if r.get("warning_emitted"))
    return ms


def report() -> str:
    dep, fpg = dependency_violations(), first_pass_green()
    from . import preflight as _preflight
    lines = ["reliability metrics — measured now, nothing remembered", "",
             f"  7. {dep}", f"  9. {fpg}", "",
             f"  failure classification: {_preflight.unclassified_share()}", ""]
    sus = metric_set().suspicious()
    lines += ["  ⚠ " + s for s in sus] if sus else ["  no activity metric is climbing over a zero outcome"]
    return "\n".join(lines)


def main(argv=None) -> int:
    print(report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
