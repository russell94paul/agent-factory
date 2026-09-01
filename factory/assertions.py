"""Grounding, freshness, evidence basis, and counterfactual honesty — shared by every artifact.

Extracted 2026-09-01 from :mod:`factory.client_review` (grounding + freshness, unchanged in
behaviour) and extended with the two contracts Delivery #001 proved were missing.

⛔ **What this module deliberately does NOT define: a temporal assertion type.**

The first draft of the Artifact Generator proposal invented one. :mod:`factory.context` already had
it — ``CURRENT / STALE / UNVERIFIED``, a ``confidence`` vocabulary, a required ``source``, a
``checked`` date, and a constructor that *refuses* to call a ref ``CURRENT`` without one
(``context.py:109``). Inventing a parallel vocabulary would have been the largest failure family in
the case study this module exists to render — ``KNOWLEDGE_AVAILABLE_BUT_NOT_CONSUMED``, 8 of 37
issues — committed inside the tooling built to expose it.

So temporal state lives in :mod:`factory.context`, extended additively. This module holds only what
had no home: the evidence-basis display vocabulary, and the counterfactual contract.
"""
from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

from . import evidence as _evidence

# --------------------------------------------------------------------------------------------
# Grounding — extracted verbatim from client_review.py:190-233
# --------------------------------------------------------------------------------------------

GROUNDED = _evidence.SATISFIED    #: evidence resolves and carries a usable basis
CLAIMED = _evidence.ASSERTED      #: someone asserted it; nothing usable backs it
UNGROUNDED = _evidence.ABSENT     #: nobody attached anything

#: Words that assert something about the world rather than describe an intention. None of these
#: may render as fact without resolved evidence. Compared case-insensitively against the whole
#: status string, so "ON TRACK" and "on track" are the same guarded claim.
GUARDED_WORDS: frozenset = frozenset({
    "success", "successful", "verified", "validated", "deployed", "accepted",
    "healthy", "on track", "ready", "complete", "completed", "passed", "passing",
    "confirmed", "proven", "live", "green",
})

#: What a guarded word degrades to when its evidence does not resolve. Deliberately not "FAILED" —
#: we did not measure a failure, we failed to measure.
UNSUBSTANTIATED = "UNSUBSTANTIATED"


class AssertionError_(ValueError):
    """A claim was made in a shape the contract does not permit."""


def is_guarded(status: str) -> bool:
    """True when `status` asserts something that needs evidence behind it."""
    low = (status or "").strip().lower()
    if low in GUARDED_WORDS:
        return True
    return any(w in low.split() for w in GUARDED_WORDS if " " not in w) or \
        any(w in low for w in GUARDED_WORDS if " " in w)


def ground(refs: Sequence[str], rows: Iterable[dict], root: pathlib.Path) -> str:
    """Return GROUNDED / CLAIMED / UNGROUNDED for a set of evidence references.

    ``GROUNDED`` requires **both** halves, and the two halves answer different questions:

    * every ref resolves to a file that exists under `root` — *the artefact is really there*;
    * at least one task-evidence row whose ``ref`` matches carries a basis in
      :data:`evidence.USABLE` — *somebody measured or derived it, rather than assuming it*.

    A file that exists but is backed only by an ``ASSUMED`` row is ``CLAIMED``. A ref naming a file
    that is not on disk is ``CLAIMED`` too, never ``GROUNDED`` — the claim survives, its promotion
    does not.

    ⭐ Added 2026-09-01: a ref may carry an anchor (``path#anchor``). The anchor is stripped for the
    existence check here — whether the anchor *resolves* is the boundary validator's job
    (:mod:`factory.forensic_source`), because that is a different question with a different failure
    mode, and answering both here would let a dangling anchor pass as a present file.
    """
    refs = [r for r in (refs or []) if r]
    if not refs:
        return UNGROUNDED
    by_ref = {r.get("ref"): r for r in rows if isinstance(r, dict)}
    paths = [r.split("#", 1)[0] for r in refs]
    all_present = all((root / p).exists() for p in paths)
    any_usable = any(
        (by_ref.get(r) or by_ref.get(p) or {}).get("basis") in _evidence.USABLE
        for r, p in zip(refs, paths))
    if all_present and any_usable:
        return GROUNDED
    return CLAIMED


def enforce(status: str, grounding: str) -> str:
    """Return the status a reader may see, given its grounding.

    A guarded word with anything less than :data:`GROUNDED` becomes :data:`UNSUBSTANTIATED`.
    Unguarded statuses ("In progress", "Blocked") pass through untouched — they describe an
    intention or an observable state, not a verified outcome.
    """
    if not is_guarded(status):
        return status
    return status if grounding == GROUNDED else UNSUBSTANTIATED


# --------------------------------------------------------------------------------------------
# Freshness — extracted verbatim from client_review.py:239-258
# --------------------------------------------------------------------------------------------

LIVE = "LIVE"
LAST_VERIFIED = "LAST_VERIFIED"
STALE = "STALE"
UNAVAILABLE = "UNAVAILABLE"

LIVE_WINDOW_SEC = 15 * 60
STALE_AFTER_SEC = 24 * 60 * 60


def freshness(last_verified: Optional[float], now: Optional[float] = None,
              source_readable: bool = True) -> str:
    """Classify how much the projection can be trusted as current.

    `source_readable=False` yields ``UNAVAILABLE`` regardless of timestamps: an unreadable source
    has not told us the state is old, it has told us nothing. Collapsing those is exactly the
    failure :mod:`factory.contract` keeps ``UNMEASURABLE`` separate to prevent.
    """
    import datetime as _dt
    if not source_readable:
        return UNAVAILABLE
    if last_verified is None:
        return UNAVAILABLE
    now = _dt.datetime.now(_dt.timezone.utc).timestamp() if now is None else now
    age = now - last_verified
    if age <= LIVE_WINDOW_SEC:
        return LIVE
    if age <= STALE_AFTER_SEC:
        return LAST_VERIFIED
    return STALE


# --------------------------------------------------------------------------------------------
# Evidence basis — the DISPLAY vocabulary
# --------------------------------------------------------------------------------------------

#: ⛔ This is display vocabulary. It is deliberately NOT `evidence.USABLE`, and must never be
#: merged into it.
#:
#: `evidence.USABLE = ("MEASURED", "DERIVED")` is the *promotion gate*: it decides whether a
#: guarded word may render as fact. `DOCUMENTED` is one hop from measurement and is honest for a
#: forensic case study — but if it entered `USABLE`, every claim read out of a document would
#: promote itself to VERIFIED. That is the single most dangerous edit anyone could make to this
#: file, so the separation is stated here and asserted in `tests/test_assertions.py`.
MEASURED = "MEASURED"          #: a command was run against real state and its output read
DERIVED = "DERIVED"            #: computed from measured/documented values; the computation is shown
DOCUMENTED = "DOCUMENTED"      #: stated in a cited file. ONE HOP, and the hop is the point
INFERRED = "INFERRED"          #: reasoning. stated nowhere
ESTIMATED = "ESTIMATED"        #: a figure with a stated method and no measurement
SIMULATED = "SIMULATED"        #: counterfactual. never observed
NOT_RECORDED = "NOT_RECORDED"  #: the record does not hold it. NOT zero
CONTRADICTORY = "CONTRADICTORY"  #: two sources disagree and neither has won yet

BASES: tuple = (MEASURED, DERIVED, DOCUMENTED, INFERRED, ESTIMATED,
                SIMULATED, NOT_RECORDED, CONTRADICTORY)

#: Bases that may back a guarded word. Identical to `evidence.USABLE`, restated so that a change
#: to one and not the other is a visible inconsistency rather than a silent widening.
PROMOTABLE: tuple = tuple(_evidence.USABLE)


def check_basis(basis: str) -> str:
    if basis not in BASES:
        raise AssertionError_(f"{basis!r} is not an evidence basis. Known: {list(BASES)}")
    return basis


# --------------------------------------------------------------------------------------------
# Counterfactual honesty
# --------------------------------------------------------------------------------------------

WOULD_BLOCK = "WOULD_BLOCK"
WOULD_INTERCEPT = "WOULD_INTERCEPT"
WOULD_WARN = "WOULD_WARN"
WOULD_PROVIDE_CONTEXT = "WOULD_PROVIDE_CONTEXT"
MAY_REDUCE_LIKELIHOOD = "MAY_REDUCE_LIKELIHOOD"
NO_MATERIAL_EFFECT = "NO_MATERIAL_EFFECT"

STRENGTHS: tuple = (WOULD_BLOCK, WOULD_INTERCEPT, WOULD_WARN, WOULD_PROVIDE_CONTEXT,
                    MAY_REDUCE_LIKELIHOOD, NO_MATERIAL_EFFECT)

EXERCISED = "EXERCISED"                              #: it ran, against this delivery, and we saw it
IMPLEMENTED_NOT_EXERCISED = "IMPLEMENTED_NOT_EXERCISED"  #: the code exists; nothing has run it here
SIMULATED_ONLY = "SIMULATED"                         #: designed, not built
PROPOSED = "PROPOSED"                                #: named, not designed

MATURITIES: tuple = (EXERCISED, IMPLEMENTED_NOT_EXERCISED, SIMULATED_ONLY, PROPOSED)


@dataclass
class Counterfactual:
    """What a capability WOULD have done — and how much of that is observation.

    ⭐ **This dataclass has no ``status`` field and no ``grounding`` field, and that is the design.**

    An artifact renders delivered outcomes through a component that reads ``status`` and
    ``grounding``. Because a Counterfactual has neither, it is not duck-type-compatible with an
    outcome and *cannot* be passed to that component. The rule "a SIMULATED capability must not be
    rendered in the same visual register as an observed one" is therefore enforced by the type
    rather than by a convention a future contributor has to remember.

    ``basis`` is forced to ``SIMULATED`` for anything below ``EXERCISED`` in
    :meth:`__post_init__`, whatever the authored file said.
    """
    capability: str
    strength: str
    maturity: str
    expected_effect: str = ""
    remaining_human: str = ""
    confidence: str = ""
    #: module:line for anything claimed IMPLEMENTED or EXERCISED. Empty is legal only below those.
    mechanism_refs: List[str] = field(default_factory=list)
    basis: str = SIMULATED
    #: ⭐ A reference to evidence that this capability ACTUALLY RAN on this delivery. Required when
    #: maturity is EXERCISED, and validated to resolve like any other reference.
    #:
    #: It is a second, independent half from `mechanism_refs`, and the two answer different
    #: questions: mechanism_refs says *the code exists*, exercised_proof says *it ran here*. A
    #: capability can trivially satisfy the first and fail the second — Source Cartography is
    #: implemented nowhere and Intent Contract does not exist, but even a fully built capability
    #: that no mission invoked is IMPLEMENTED_NOT_EXERCISED, not EXERCISED.
    exercised_proof: str = ""

    def __post_init__(self) -> None:
        if self.strength not in STRENGTHS:
            raise AssertionError_(
                f"{self.capability}: {self.strength!r} is not an interception strength. "
                f"Known: {list(STRENGTHS)}")
        if self.maturity not in MATURITIES:
            raise AssertionError_(
                f"{self.capability}: {self.maturity!r} is not a maturity. Known: {list(MATURITIES)}")
        if self.maturity in (EXERCISED, IMPLEMENTED_NOT_EXERCISED) and not self.mechanism_refs:
            raise AssertionError_(
                f"{self.capability}: maturity {self.maturity} claims code exists but names none. "
                "Give mechanism_refs (module:line), or drop the maturity to PROPOSED. A capability "
                "that cannot point at its own implementation is a proposal wearing a build's label.")
        if self.maturity == EXERCISED and not self.exercised_proof:
            raise AssertionError_(
                f"{self.capability}: maturity EXERCISED with no exercised_proof. Naming the code "
                "shows it exists; it does not show it RAN on this delivery. Supply a reference to "
                "the evidence of it running, or the honest maturity is IMPLEMENTED_NOT_EXERCISED.")
        # ⛔ The authored file does not get to decide this.
        if self.maturity != EXERCISED:
            self.basis = SIMULATED
        check_basis(self.basis)

    @property
    def is_observed(self) -> bool:
        return self.maturity == EXERCISED and self.basis != SIMULATED


# --------------------------------------------------------------------------------------------
# Anchored references
# --------------------------------------------------------------------------------------------

_REF = re.compile(r"^(?P<path>[^#]+)(?:#(?P<anchor>[A-Za-z0-9][A-Za-z0-9._-]*))?$")


def split_ref(ref: str) -> tuple:
    """``docs/x.md#h1-phantom-ask`` -> ``('docs/x.md', 'h1-phantom-ask')``.

    Returns ``(path, None)`` when there is no anchor. Raises on a malformed ref rather than
    silently treating the whole string as a path — a ref that looks anchored and is not is exactly
    the class of thing that resolves to a file and points at nothing.
    """
    m = _REF.match((ref or "").strip())
    if not m:
        raise AssertionError_(
            f"{ref!r} is not a valid evidence reference. Expected 'path' or 'path#anchor'.")
    return m.group("path"), m.group("anchor")
