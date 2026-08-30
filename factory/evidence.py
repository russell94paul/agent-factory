"""The four classes of evidence a delivery must carry — typed, so "missing" is sayable.

`tasks.py` already refuses to close a task with no MEASURED or DERIVED evidence. That is one
control and it is not enough for a delivery that crosses systems: **four pieces of evidence that
are all the same class look identical to four that cover four different questions.** A job can
satisfy the existing rule with four screenshots and still never have proved which object the
consumer reads.

So the classes are named here, and the standing rule they encode is Paul's evidence gate:

    TARGET      which object/system does the consumer ACTUALLY read
                — proved by a discriminating test, never inferred from matching values, and
                  never inherited from a ticket, a boot prompt or a handoff
    CONSUMER    is it correct at the layer the consumer reads — the rendered surface for a
                dashboard, DAX for a semantic model, the response body for an API
    REGRESSION  did only the intended thing change — out-of-scope rows byte-identical,
                before/after delta equal to expectation
    ROLLBACK    can this be reversed — captured BEFORE the mutation, not after

⭐ **Three states, never two.** A class with no row at all and a class whose only rows are
ASSUMED are different situations, and collapsing them is the same defect as collapsing
UNMEASURABLE into FAIL. `ABSENT` means nobody looked. `ASSERTED` means somebody claimed it
without measuring. Only `SATISFIED` is a pass.

⛔ **What this module cannot check, stated so nobody believes otherwise.**

  * **It cannot verify ordering.** `ROLLBACK` is only worth anything if it was captured before the
    mutation, and a task store holds no mutation event to compare a timestamp against. The
    Power BI contract asserts that ordering properly (`pbi_contract` M1) because it can see both.
    Here, a rollback row proves a rollback was *recorded*, not that it was recorded *first*.
  * **It cannot judge the evidence.** A `TARGET` row pointing at a file that says "looks right"
    counts. The class is a slot, not a referee — the referee is a `GreenContract`.

Both limits are the reason this is a small module and not a framework.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

#: The four classes. Ordered as the evidence gate runs them: you cannot validate at the consumer's
#: layer until you know which object the consumer reads.
TARGET = "TARGET"
CONSUMER = "CONSUMER"
REGRESSION = "REGRESSION"
ROLLBACK = "ROLLBACK"

CLASSES: tuple = (TARGET, CONSUMER, REGRESSION, ROLLBACK)

#: What each class must answer, in a sentence an operator can hold a piece of evidence against.
MEANS: Dict[str, str] = {
    TARGET: "which object the consumer actually reads, proved by a discriminating test",
    CONSUMER: "correct at the layer the consumer reads, not only at the layer that changed",
    REGRESSION: "only the intended rows changed; out-of-scope unchanged, delta as expected",
    ROLLBACK: "a captured way back, recorded before the mutation",
}

#: The default requirement for work that mutates something a consumer reads. Named rather than
#: inlined so a caller that requires fewer classes has to say so and say why.
DELIVERY: tuple = CLASSES

#: Analysis produces a number rather than a mutation: nothing to roll back, nothing to regress.
#: It still has to prove which instrument produced the figure and that the figure is right where
#: it is read. Present so that "we only need two" is a declared policy, not an omission.
ANALYSIS: tuple = (TARGET, CONSUMER)

#: Per-class state. Three, never two — see the module docstring.
SATISFIED = "SATISFIED"   #: at least one MEASURED or DERIVED row
ASSERTED = "ASSERTED"     #: rows exist, all ASSUMED — a claim, not a proof
ABSENT = "ABSENT"         #: nobody looked

#: The bases `tasks.py` accepts. Only the first two can satisfy a class.
USABLE = ("MEASURED", "DERIVED")


class UnknownClass(ValueError):
    """An evidence class that is not one of the four.

    Deliberately loud. A typo'd class silently creates a fifth bucket nothing requires, which is
    how a mandatory artifact becomes optional without anyone deciding it should be.
    """


def check(evidence_class: str) -> str:
    """Validate and return one class name, or raise."""
    if evidence_class not in CLASSES:
        raise UnknownClass(
            f"{evidence_class!r} is not an evidence class. Known: {list(CLASSES)}. "
            "Add a class only if a delivery genuinely has a fifth question to answer.")
    return evidence_class


@dataclass(frozen=True)
class Coverage:
    """What a set of evidence rows covers, and what it does not."""

    required: tuple
    state: Dict[str, str]

    @property
    def missing(self) -> List[str]:
        """Required classes with no usable row — ABSENT and ASSERTED alike.

        Both are returned because both block, but `state` keeps them distinguishable: the fix for
        ABSENT is to go and measure, and the fix for ASSERTED is to stop calling a claim a proof.
        """
        return [c for c in self.required if self.state.get(c, ABSENT) != SATISFIED]

    @property
    def complete(self) -> bool:
        return not self.missing

    def summary(self) -> str:
        parts = [f"{c}={self.state.get(c, ABSENT)}" for c in self.required]
        head = "COMPLETE" if self.complete else f"INCOMPLETE ({len(self.missing)} of " \
                                                f"{len(self.required)} unsatisfied)"
        return f"{head}: {', '.join(parts)}"


def coverage(rows: Iterable[dict], required: Sequence[str] = DELIVERY) -> Coverage:
    """Fold evidence rows into per-class state.

    `rows` are the dicts `tasks.TaskStore` appends: `{kind, ref, basis, evidence_class?}`. A row
    with no `evidence_class` counts toward nothing — it is unclassified, not universal. That is
    the point of typing the field, and it is why existing rows do not retroactively satisfy
    anything.
    """
    req = tuple(required)
    for c in req:
        check(c)
    state = {c: ABSENT for c in req}
    for row in rows:
        cls = row.get("evidence_class")
        if cls not in state:
            continue
        if row.get("basis") in USABLE:
            state[cls] = SATISFIED
        elif state[cls] == ABSENT:
            state[cls] = ASSERTED
    return Coverage(required=req, state=state)


def render(cov: Coverage) -> str:
    """Multi-line, one class per line, with what each class was supposed to answer.

    The `MEANS` line is included on purpose: somebody reading "TARGET=ABSENT" needs to know what
    would satisfy it, and a bare state name sends them looking for a convention instead.
    """
    out = [cov.summary()]
    for c in cov.required:
        out.append(f"  [{cov.state.get(c, ABSENT):9}] {c:10} — {MEANS[c]}")
    return "\n".join(out)
