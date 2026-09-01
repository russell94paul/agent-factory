"""Context as structure, so it can be selected, sourced and dated — not one prompt-shaped blob.

⭐ **This module exists to stop one decision being made by accident.** `Lane.full_prompt()` was
``PREAMBLE + prompt + POSTAMBLE + operator_block`` — four strings concatenated. Text that has
already been concatenated cannot be filtered per lane, cannot say where it came from, and cannot
carry a date. Every further call site that concatenates is a decision to keep context
unstructured, and by the time there are twenty of them the decision is unrecoverable. So the seam
goes in now, with a real caller, while it is four lines.

⛔ **What this is NOT, and must not become.** It is not a knowledge base, an extraction pipeline,
or a second source of truth. `~/repos/wiki` holds the company's engineering, client, architecture,
metric and incident knowledge and stays canonical. The intended `factory-wiki` is a **derived,
task-oriented projection** of it — which imposes exactly one hard schema rule:

    Every ref names the artefact it was derived FROM, and when that was last checked.

A projection that cannot point back at its source is a copy, and a copy silently becomes a second
truth the moment the original moves. `factory/corpus.py` already solved this shape for eval data
and its three properties are the ones wanted here too — EVIDENT, ATTRIBUTED, SEPARABLE.

⚠ **`UNVERIFIED` is the default status, not `CURRENT`.** Nothing has checked a ref against its
source at construction time, and defaulting to CURRENT would let every ref claim a freshness
nobody established — the same collapse as reporting UNMEASURABLE as PASS. A ref becomes CURRENT
by someone recording that they checked it, on a date.

**Nothing here extracts anything.** Building the wiki→pack pipeline is deliberately deferred until
one real client workflow has validated that these kinds are the right kinds. See
`docs/specs/golden-workflow-fit.md` §5.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence

# --------------------------------------------------------------------------------------- kinds
#: What a piece of context IS. An agent asks for the kinds its lane needs rather than for
#: everything, which is the whole reason the field exists.
COMPANY = "CompanyContext"      #: standards, release procedure, environment and approval rules
REPO = "RepoContext"            #: purpose, paths, commands, dangerous operations, known traps
CLIENT = "ClientContext"        #: business model, channels, regions, terminology, DQ history
SOURCE = "SourceContract"       #: an API: auth, endpoints, paging, limits, grain, late arrival
DATASET = "DatasetContract"     #: a table/view: grain, keys, dedup rule, incremental strategy
METRIC = "MetricContract"       #: numerator, denominator, scope, currency, valid dimensions
TASK = "TaskContext"            #: the instruction for this specific piece of work
OPERATOR = "OperatorAnswer"     #: a decision a human recorded in response to a declared blocker

CASE_STUDY = "CaseStudyClaim"   #: one forensic claim about a past delivery, with its as-of

KINDS: tuple = (COMPANY, REPO, CLIENT, SOURCE, DATASET, METRIC, TASK, OPERATOR, CASE_STUDY)

# ---------------------------------------------------------------------------------- freshness
#: Six states. `UNVERIFIED` is not a weak `CURRENT` — it means nobody has looked.
CURRENT = "CURRENT"          #: checked against its source, and it agreed
STALE = "STALE"              #: checked, and the source has moved since
UNVERIFIED = "UNVERIFIED"    #: never checked against its source

#: ⭐ The three added 2026-09-01 for the forensic case study, and why each is NOT one of the above.
#:
#: A ref that has been overtaken is not `STALE`. `STALE` says *the source moved and this copy did
#: not*; these three say *the claim itself was answered*. Collapsing them would lose which of the
#: three happened, and Delivery #001 contains one of each:
#:
#: * `SUPERSEDED`   — a later claim replaced it. (R1/R2 duplicate tasks, annotated not deleted.)
#: * `REFUTED`      — measurement showed it false. (The inherited metric hierarchy.)
#: * `CONTRADICTED` — two sources disagree and neither has won. (MER, written both ways.)
#:
#: `CONTRADICTED` in particular must never degrade to `STALE`: staleness implies a correct value
#: exists elsewhere, and the whole point of the MER finding is that it does not, yet.
SUPERSEDED = "SUPERSEDED"        #: a later claim replaced it; `superseded_by` names which
REFUTED = "REFUTED"              #: measured against its source and found false
CONTRADICTED = "CONTRADICTED"    #: sources disagree; no side has won. NOT a weak STALE

STATUSES: tuple = (CURRENT, STALE, UNVERIFIED, SUPERSEDED, REFUTED, CONTRADICTED)

#: The statuses that mean "this claim has been answered", as opposed to merely aged.
ANSWERED: tuple = (SUPERSEDED, REFUTED, CONTRADICTED)

#: How much the content is to be trusted, separate from whether it is fresh. A ref can be
#: perfectly current and still be somebody's guess; a ref can be a hard measurement taken a year
#: ago. Collapsing the two loses whichever one matters.
MEASURED = "MEASURED"
DERIVED = "DERIVED"
STATED = "STATED"            #: a human said so; true by assertion, not by measurement
ASSUMED = "ASSUMED"
CONFIDENCE: tuple = (MEASURED, DERIVED, STATED, ASSUMED)


class ContextError(ValueError):
    """A ref that cannot be trusted to be a projection. Loud, because a silent one becomes truth."""


@dataclass(frozen=True)
class ContextRef:
    """One addressable piece of context, with where it came from and how fresh that is.

    `source` is **required and non-empty**. That is the load-bearing constraint of the whole
    module: a ref with no source cannot be re-derived, cannot be invalidated when the wiki page
    behind it changes, and is therefore not a projection but a fork. In-repo prose is not exempt —
    its source is the file and symbol that holds it (`factory/lanes.py:PREAMBLE`), which is also
    how a reader finds the thing to edit.
    """

    kind: str
    id: str
    #: Where this was derived FROM — a wiki path, a repo path:symbol, a ticket id, a URL.
    source: str
    #: The projected content. Text today; a caller may hold a structured payload in `data`.
    body: str = ""
    status: str = UNVERIFIED
    confidence: str = STATED
    #: ISO date the ref was last checked against `source`. Empty means never.
    checked: str = ""
    #: ⭐ ISO date the claim was FIRST established. Distinct from `checked`, and the distinction is
    #: the whole point: Delivery #001's "ticket-level `blocked_by` is unused" was TRUE when
    #: observed (189 events, all empty) and FALSE when re-used (25 block events existed by then).
    #: One date cannot express that. `observed` without `checked` renders as "true as of X, not
    #: re-checked" — never as "true".
    observed: str = ""
    #: Which ref replaced this one. Required when `status` is SUPERSEDED.
    superseded_by: str = ""
    #: Structured payload for kinds that have one (a MetricContract's numerator/denominator/scope).
    #: Deliberately untyped for now — the schema is validated against one real client workflow
    #: before it is fixed in code. See the module docstring.
    data: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ContextError(f"{self.kind!r} is not a context kind. Known: {list(KINDS)}")
        if self.status not in STATUSES:
            raise ContextError(f"{self.status!r} is not a status. Known: {list(STATUSES)}")
        if self.confidence not in CONFIDENCE:
            raise ContextError(
                f"{self.confidence!r} is not a confidence. Known: {list(CONFIDENCE)}")
        if not (self.source or "").strip():
            raise ContextError(
                f"context ref {self.id!r} has no source. Every ref must name what it was derived "
                "from — a projection that cannot point back at its origin is a second source of "
                "truth, which is the one thing the factory-wiki must not become.")
        if self.status == CURRENT and not self.checked:
            raise ContextError(
                f"context ref {self.id!r} claims CURRENT with no `checked` date. Freshness is a "
                "measurement; without the date it is an assertion wearing a measurement's label.")
        if self.status == SUPERSEDED and not self.superseded_by:
            raise ContextError(
                f"context ref {self.id!r} claims SUPERSEDED but names nothing that superseded it. "
                "The same rule as CURRENT-needs-a-date: a status that asserts something happened "
                "must carry the evidence of what happened, or it is an opinion with a label.")

    def header(self) -> str:
        """The one line that precedes this ref's body when it is rendered into a prompt."""
        when = f", checked {self.checked}" if self.checked else ""
        return f"[{self.kind} · {self.id} · {self.status} · {self.confidence}{when}] {self.source}"


@dataclass
class ContextPack:
    """The ordered set of refs assembled for ONE lane or task.

    An agent receives a pack, not the corpus. That is the point of the whole design: selection
    happens here, where it can be inspected and argued with, rather than inside a prompt string
    nobody can query.
    """

    name: str
    refs: List[ContextRef] = field(default_factory=list)

    def add(self, ref: ContextRef) -> "ContextPack":
        self.refs.append(ref)
        return self

    def of_kind(self, *kinds: str) -> List[ContextRef]:
        return [r for r in self.refs if r.kind in kinds]

    def stale(self) -> List[ContextRef]:
        """Refs known to have drifted. Distinct from `unverified()` — see the module docstring."""
        return [r for r in self.refs if r.status == STALE]

    def unverified(self) -> List[ContextRef]:
        return [r for r in self.refs if r.status == UNVERIFIED]

    def answered(self) -> List[ContextRef]:
        """Refs a later measurement settled — superseded, refuted or contradicted.

        Deliberately NOT folded into `stale()`. Staleness implies a correct value exists
        elsewhere; `CONTRADICTED` means it does not, yet.
        """
        return [r for r in self.refs if r.status in ANSWERED]

    def not_rechecked(self) -> List[ContextRef]:
        """Refs established once and never re-established. The `blocked_by` failure mode."""
        return [r for r in self.refs if r.observed and not r.checked]

    def sources(self) -> List[str]:
        """Every artefact this pack was derived from — the audit answer to "where did that come
        from", available without parsing the rendered text."""
        seen, out = set(), []
        for r in self.refs:
            if r.source not in seen:
                seen.add(r.source)
                out.append(r.source)
        return out

    def render(self, headers: bool = False) -> str:
        """The text an agent actually receives.

        `headers=False` by default so this is a **byte-identical** replacement for the string
        concatenation it supersedes — the seam lands without changing what any agent reads, which
        is what makes it safe to put in before there is anything to select from. Turning headers
        on marks each block with its kind, source and freshness, and is what a pack assembled from
        the factory-wiki will want.
        """
        parts = []
        for r in self.refs:
            if headers and r.body:
                parts.append(f"--- {r.header()}\n{r.body}")
            else:
                parts.append(r.body)
        return "".join(parts) if not headers else "\n\n".join(parts)

    def summary(self) -> str:
        counts = {}
        for r in self.refs:
            counts[r.kind] = counts.get(r.kind, 0) + 1
        bits = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        warn = ""
        if self.stale():
            warn += f" · {len(self.stale())} STALE"
        if self.unverified():
            warn += f" · {len(self.unverified())} UNVERIFIED"
        return f"{self.name}: {len(self.refs)} ref(s) [{bits}]{warn}"


def pack(name: str, refs: Iterable[ContextRef]) -> ContextPack:
    return ContextPack(name=name, refs=list(refs))


def literal(kind: str, id: str, source: str, body: str, **kw) -> ContextRef:
    """A ref whose body is authored in this repo rather than projected from the wiki.

    Exists so in-repo prose goes through the same object as everything else and carries the same
    source field. It is NOT an exemption — `source` still has to name the file and symbol.
    """
    return ContextRef(kind=kind, id=id, source=source, body=body, **kw)
