"""Show a run the failure its own history already recorded — before it repeats it.

⭐ **The hypothesis this module exists to test, and nothing wider:**

    A run should not unknowingly repeat a failure whose evidence already exists in its own history.

Measured, on the only population there is (`.data/events.jsonl`, 2026-08-31): **seven of eight
recorded runs are one ticket.** GP-327 ran seven times; six of those seven ended with the same
assertion reporting the same thing —

    UNMEASURABLE ticket_verifier  preset 'ui-control' declares a WIRED verifier but the
                                  controller was given no callable to run.

— and the seventh was aborted because those six had exhausted the attempt cap. Every attempt after
the first had its predecessor's verdict on disk. Nothing read it.

⛔ **WARN-ONLY IN V0. This module never refuses a run, and no caller may make it refuse one.**
`would_refuse` is computed, recorded and **not acted on**. There are eight replayable runs, a
first-pass GREEN rate of zero, and a taxonomy written this week; a hard refusal built on that
would be a policy derived from a population too small to have seen a false positive yet. The
promotion to refusal is a later, evidence-backed decision — see `docs/protocol/ROLLOUT.md` for the
five measurements it is gated on. `would_refuse` is the shadow of that policy, so the evidence can
accumulate before the control does.

⚠ **Not a duplicate of `deploy.AttemptLedger`, and the difference is the whole point.** That class
already counts attempts and already injects prior failures into the next prompt — and it was
**live, correct by its own lights, and silent** through all seven GP-327 runs. `.data/attempts.json.pre-F85.bak`
records why:

    "ui-control-agent:gp-327": {"count": 2, "attempts": [
        {"n": 1, "outcome": "ok", "detail": "dry run", "limit": "none"},
        {"n": 2, "outcome": "ok", "detail": "dry run", "limit": "none"}]}

Both attempts are `outcome: "ok"`, because the **provider** exited zero. `failures()` filters on
`outcome != "ok"`, so `context()` returned the empty string on every retry. The ledger reads what
the provider observed; a verdict is what a `GreenContract` assigned, and those are different
questions. This module reads the second. They are complements, not rivals:

    AttemptLedger   keyed agent:worktree · provider outcome · enforces the cap · injects a prompt
    preflight       keyed ticket         · contract verdict  · refuses nothing  · records an event

⚠ **`UNCLASSIFIED` is not `NOT-RECORDED`.** UNCLASSIFIED means the failure was observed and
recorded and does not confidently map onto the nine families. NOT-RECORDED means the field was
never captured — every terminal event written before this module existed. Collapsing them would
make a taxonomy gap look like a measurement gap, which is the same shape as reporting UNMEASURABLE
as FAIL. Nothing here maps a failure to the nearest-looking family; the classifier fires on
structural signals or it says UNCLASSIFIED.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .contract import Verdict

# --------------------------------------------------------------------------------- the families

#: The nine families, clustered from the ~95 entries in `docs/findings.d/` + `docs/findings.md`,
#: plus the tenth state that keeps the other nine honest. A closed set: an unknown value is a typo
#: that would otherwise sit in the stream looking like a classification.
#:
#: ⛔ Do not add a family because a failure "sort of fits" one. Add it when two recorded failures
#: share a mechanism and a repair. Until then `UNCLASSIFIED` is the correct answer and
#: `unclassified_share()` is how we find out the taxonomy is too narrow.
BLIND_INSTRUMENT = "BLIND_INSTRUMENT"
DECLARATION_WITHOUT_MECHANISM = "DECLARATION_WITHOUT_MECHANISM"
WRONG_POPULATION = "WRONG_POPULATION"
COLLAPSED_STATE = "COLLAPSED_STATE"
SHARED_MUTABLE_STATE = "SHARED_MUTABLE_STATE"
CHANNEL_WITH_NO_READER = "CHANNEL_WITH_NO_READER"
UNBOUNDED_RETRY = "UNBOUNDED_RETRY"
STALE_ARTEFACT = "STALE_ARTEFACT"
HARNESS_FAULT = "HARNESS_FAULT"
UNCLASSIFIED = "UNCLASSIFIED"

FAMILIES = (
    BLIND_INSTRUMENT,
    DECLARATION_WITHOUT_MECHANISM,
    WRONG_POPULATION,
    COLLAPSED_STATE,
    SHARED_MUTABLE_STATE,
    CHANNEL_WITH_NO_READER,
    UNBOUNDED_RETRY,
    STALE_ARTEFACT,
    HARNESS_FAULT,
    UNCLASSIFIED,
)

#: ⚠ Distinct from UNCLASSIFIED, and the distinction is load-bearing. See the module docstring.
NOT_RECORDED = "NOT-RECORDED"


class FamilyError(ValueError):
    """A failure family outside the closed set, or attached to a verdict that cannot carry one."""


def check_family(family: Optional[str], verdict: Verdict) -> Optional[str]:
    """Validate a family against the closed set and against the verdict it is attached to.

    A PASS carries no family: a run that succeeded has no failure to classify, and allowing one
    would let a green run be filed under a defect. Every non-PASS terminal event carries one, and
    when nothing could be established that value is `UNCLASSIFIED` — never an absent key, which is
    what NOT-RECORDED means.
    """
    if verdict is Verdict.PASS:
        if family is not None:
            raise FamilyError(
                f"a PASS cannot carry a failure_family (got {family!r}). Nothing failed, so there "
                "is nothing to classify.")
        return None
    if family is None:
        return UNCLASSIFIED
    if family not in FAMILIES:
        raise FamilyError(
            f"{family!r} is not a known failure family. Known: {list(FAMILIES)}. If this failure "
            "genuinely does not fit, use UNCLASSIFIED — do not map it to the nearest-looking "
            "family, and do not widen the set for one occurrence.")
    return family


# ----------------------------------------------------------------------------- classification

#: The situations the controller can name structurally, without reading any message text. Each is
#: a place in `factory.control` where the code already knows what happened.
SITUATION_REPO_MISMATCH = "repo_mismatch"
SITUATION_HARNESS_EXCEPTION = "harness_exception"
SITUATION_PROVIDER_REFUSED = "provider_refused"
SITUATION_CONTRACT = "contract"


@dataclass(frozen=True)
class Classification:
    """A family, and the named rule that produced it. The rule name is what makes it auditable.

    A bare family says what we think happened. `classified_by` says *why we think so*, which is
    the difference between a classification somebody can argue with and one they must accept.
    """
    family: str
    classified_by: str

    def as_dict(self) -> dict:
        return {"failure_family": self.family, "classified_by": self.classified_by}


#: The literal `deploy.RepoDeployer.run_agent` raises when the cap is exhausted. Matching text is
#: normally the F19 defect — a guard that never matches the line it was written to catch — so this
#: is the ONLY text rule here and `tests/test_recurrence_preflight.py` asserts the live message
#: still starts with it. If that test fails, the rule has rotted; fix the rule, not the test.
_CAP_PREFIX = "attempt cap reached"


def classify(situation: str, *,
             verdict: Verdict,
             results: Optional[List[dict]] = None,
             verifier_declared_wired: Optional[bool] = None,
             verifier_callable_present: Optional[bool] = None,
             why: str = "") -> Classification:
    """Name the family for one non-PASS outcome, from structural signals only.

    Every rule below fires on something the caller already knows as a fact — a verdict enum, a
    preset field, the presence of a callable — except `provider_cap`, which is guarded by a test.
    Anything else is `UNCLASSIFIED`, deliberately and without apology: an unclassified failure is
    a visible gap in the taxonomy, and a misclassified one is a gap that looks filled.
    """
    if verdict is Verdict.PASS:
        raise FamilyError("classify() is for non-PASS outcomes; a PASS has no family")

    # TTCN-3 `error` is definitional, not inferred: contract.py sets ERROR only when our own
    # apparatus raised. That IS the harness-fault family, by construction.
    if verdict is Verdict.ERROR:
        return Classification(HARNESS_FAULT, "verdict_is_error")

    if situation == SITUATION_HARNESS_EXCEPTION:
        return Classification(HARNESS_FAULT, "harness_exception")

    # F90 — the controller would have put an agent in a repository the ticket is not about. The
    # run would have measured the wrong population, which is the family, and it is known from a
    # field comparison rather than from any message.
    if situation == SITUATION_REPO_MISMATCH:
        return Classification(WRONG_POPULATION, "repo_mismatch")

    if situation == SITUATION_PROVIDER_REFUSED:
        if (why or "").strip().startswith(_CAP_PREFIX):
            return Classification(UNBOUNDED_RETRY, "provider_cap")
        # ⚠ Every other provider refusal is UNCLASSIFIED, and that is a known gap rather than a
        # judgement: `ProviderError` is raised from a bare `RuntimeError`, so a cap-exhausted
        # refusal and a terminal that would not open are indistinguishable to a caller. The fix is
        # a typed exception in provider.py — NEXT tier, not this patch.
        return Classification(UNCLASSIFIED, "provider_refused_untyped")

    if situation == SITUATION_CONTRACT:
        named = {r.get("name"): r.get("verdict") for r in (results or [])}
        # F87 — the preset names a check and nothing performs it. Established from the preset's
        # own field and from whether a callable was resolved, never from the assertion's prose.
        if named.get("ticket_verifier") == Verdict.UNMEASURABLE.value and (
                verifier_declared_wired is False or verifier_callable_present is False):
            return Classification(DECLARATION_WITHOUT_MECHANISM, "verifier_declared_not_wired")
        return Classification(UNCLASSIFIED, "contract_unmapped")

    return Classification(UNCLASSIFIED, "no_rule")


def classify_recorded(fold: dict) -> Classification:
    """Classify a run already in the stream — the replay path.

    ⚠ Weaker than `classify()` by construction, and the weakness is named rather than hidden: a
    recorded run no longer has the preset object or the resolved callable, so
    `verifier_declared_not_wired` cannot be established the same way. What the stream *does* hold
    is which assertion reported what, and the six GP-327 runs are separable on that alone. A run
    this cannot place is UNCLASSIFIED, exactly as a live one would be.
    """
    raw = fold.get("verdict")
    if raw is None:
        return Classification(UNCLASSIFIED, "no_terminal_verdict")
    verdict = Verdict(raw)
    if verdict is Verdict.PASS:
        raise FamilyError("classify_recorded() is for non-PASS runs; a PASS has no family")
    if fold.get("terminal") == "run_aborted":
        return classify(SITUATION_PROVIDER_REFUSED if verdict is Verdict.NOT_RUN
                        else SITUATION_HARNESS_EXCEPTION,
                        verdict=verdict, why=str(fold.get("why") or ""))
    results = fold.get("results") or []
    named = {r.get("name"): r.get("verdict") for r in results}
    if named.get("ticket_verifier") == Verdict.UNMEASURABLE.value:
        # The stream cannot see the preset field, so the discriminator is narrower: an
        # UNMEASURABLE ticket_verifier on a preset whose verifier the registry still cannot supply
        # is the declaration-without-mechanism case. Resolved live, against the current registry.
        from . import presets as _presets
        from . import verifiers as _verifiers
        from .presets import WIRED
        chosen = fold.get("chosen")
        p = _presets.by_id(chosen) if chosen else None
        if p is not None and (p.verifier_state != WIRED or _verifiers.for_type(p.type_id) is None):
            return Classification(DECLARATION_WITHOUT_MECHANISM, "verifier_declared_not_wired")
    return Classification(UNCLASSIFIED, "contract_unmapped")


# ------------------------------------------------------------------------- prevention checks

@dataclass(frozen=True)
class Prevention:
    """Whether the thing that broke the last attempt is still broken.

    ⭐ **This is the field that separates a legitimate retry from a repeat**, and it is the reason
    the packet is worth an agent's attention rather than being a nag. "You failed this way before"
    is nearly useless on its own — the operator may have just fixed it. "You failed this way
    before, and the specific blocker is still present" is actionable.

    `available=False` is honest and common: most families have no cheap deterministic check yet,
    and inventing one that returns True would be a probe that hands itself the state it wants to
    see (F18).
    """
    available: bool
    passed: Optional[bool] = None
    detail: str = ""
    #: ⚠ Set when a check EXISTED and RAISED. Distinct from `available=False`, which means no check
    #: has been written for this family. The first version returned NOT-RECORDED for both, which is
    #: the COLLAPSED_STATE family reproduced inside the module that names it: a broken instrument
    #: and a missing one need different remedies (fix the check, versus write one) and only the
    #: first says the taxonomy's coverage number is a lie.
    error: str = ""

    @property
    def result(self) -> str:
        if self.error:
            return "CHECK_ERROR"
        if not self.available:
            return NOT_RECORDED
        return "CLEARED" if self.passed else "STILL_PRESENT"


def _prevent_declaration_without_mechanism(ctx: dict) -> Prevention:
    """Is a runnable verifier resolvable for this ticket's preset *now*?

    Deterministic, in-process, no subprocess, no network — the whole check is a registry lookup
    and a field read, which is what keeps the preflight inside its 200 ms budget.
    """
    from . import verifiers as _verifiers
    from .presets import WIRED
    preset = ctx.get("preset")
    if preset is None:
        return Prevention(False, detail="no preset in the preflight context")
    wired = preset.verifier_state == WIRED
    callable_present = _verifiers.for_type(preset.type_id) is not None
    ok = wired and callable_present
    return Prevention(
        True, ok,
        f"preset '{preset.type_id}' verifier_state={preset.verifier_state}, "
        f"registry callable={'yes' if callable_present else 'no'}")


#: family -> a deterministic check answering "is the blocker still there?". Absent means no check
#: exists yet, which reports NOT-RECORDED rather than a guess.
PREVENTION: Dict[str, Any] = {
    DECLARATION_WITHOUT_MECHANISM: _prevent_declaration_without_mechanism,
}


def prevention_for(family: str, ctx: dict) -> Prevention:
    fn = PREVENTION.get(family)
    if fn is None:
        return Prevention(False, detail=f"no prevention check exists for {family}")
    try:
        return fn(ctx)
    except Exception as exc:                                       # noqa: BLE001
        # A check that crashed has not cleared anything and has not found anything. Reporting it
        # as STILL_PRESENT would be a failure invented by our own instrument; reporting it as
        # NOT-RECORDED would hide a broken check behind a missing one.
        return Prevention(False, detail=f"prevention check for {family} raised",
                          error=f"{type(exc).__name__}: {exc}")


# ------------------------------------------------------------------------------ prior history

@dataclass
class Attempt:
    """One prior run of this ticket, folded from the event stream."""
    run: str
    at: str
    verdict: str
    terminal: str
    family: str
    classified_by: str
    reason: str

    def as_dict(self) -> dict:
        return dict(self.__dict__)


#: rule name -> the assertion that rule fired on. ⭐ **The reason must name the same assertion the
#: family was derived from.** Without this map `_reason` returned the FIRST non-passing assertion,
#: which on all six GP-327 contract runs was `outcome_observable` ("headless-cli cannot observe
#: this run's outcome — dry run"). So the packet said DECLARATION_WITHOUT_MECHANISM in one line
#: and gave a dry-run symptom as the reason in the next: a family and an explanation that
#: contradict each other, which is worse than no packet. Caught by replaying the real stream, not
#: by any test — the tests asserted the family and never read the prose beside it.
RULE_ASSERTION = {"verifier_declared_not_wired": "ticket_verifier"}

#: The one assertion that is about the client's problem rather than about the harness — see
#: `control.assertions`. When no rule names an assertion, this is a better default than "first
#: non-passing", because the harness assertions above it fail together and say the same thing.
_PRIMARY_ASSERTION = "ticket_verifier"


_KEY_BAD = re.compile(r"[^a-z0-9]+")


def ticket_key(raw: str) -> str:
    """Normalise a ticket id the way the rest of the estate already does.

    ⚠ **Identity loss this closes.** The event stream records `ticket=ticket.id` verbatim, so
    `GP-327` and `gp-327` are two tickets to a raw string match — while `worktrees.path_for` and
    `claims._task_path` both take `Ticket.key`, which lowercases and collapses punctuation. The
    two ids therefore share a worktree, a claim and an attempt-cap key, and were *the same work
    item* to every mechanism except this one. A recurrence check that missed a repeat because an
    operator typed the ticket in a different case would fail silently and look healthy.

    ⛔ This is a **false-negative** fix, not a widening. It cannot introduce a match between ids
    that the claim system already treats as distinct, because it is the claim system's own rule —
    `tests/test_recurrence_preflight.py::test_the_ticket_key_agrees_with_the_controllers` asserts
    the two definitions agree rather than trusting that they do. They are separate definitions
    only because `control` imports `preflight`, so `preflight` cannot import `control` back.
    """
    # ⚠ The `[:64]` and the fallback are not cosmetic — they are `Ticket.key`'s, and a normaliser
    # that agreed on ordinary ids while diverging on a long one or an empty one would be a guard
    # that works until the day it matters. The anchor test exercises both edges.
    k = _KEY_BAD.sub("-", (raw or "").lower()).strip("-")[:64]
    return k or "unnamed-ticket"


def _reason(fold: dict, classified_by: str = "") -> str:
    """The shortest true statement of why the last attempt did not pass.

    Prefers the assertion the classification was derived from, then the ticket's own verifier,
    then any failing assertion. The detail beats the contract summary either way: "preset
    'ui-control' declares a WIRED verifier but the controller was given no callable" tells the
    next run what to do; "UNMEASURABLE (PASS=1, UNMEASURABLE=6)" tells it only that something went
    wrong.
    """
    if fold.get("terminal") == "run_aborted":
        return str(fold.get("why") or "aborted with no reason recorded")
    results = fold.get("results") or []
    bad = [r for r in results
           if r.get("verdict") in (Verdict.FAIL.value, Verdict.UNMEASURABLE.value,
                                   Verdict.ERROR.value)]
    if not bad:
        return "no failing assertion was recorded"
    rule = (classified_by or "").split(" ")[0]
    for want in (RULE_ASSERTION.get(rule), _PRIMARY_ASSERTION):
        if want:
            hit = next((r for r in bad if r.get("name") == want), None)
            if hit is not None:
                return f"{hit.get('name')}: {hit.get('detail') or 'no detail recorded'}"
    return f"{bad[0].get('name')}: {bad[0].get('detail') or 'no detail recorded'}"


def prior_attempts(ticket: str, before: Optional[str] = None) -> List[Attempt]:
    """Every recorded non-PASS run of this ticket that happened BEFORE `before`, oldest first.

    ⚠ `before` truncates the history; it does not merely drop one row. A run must not find itself
    in its own history — the same rule `deploy.run_agent` follows when it reads prior failures
    before recording the current dispatch — and it must not find runs that came *after* it either.
    The first version of this only skipped the matching id, so replaying attempt 1 handed it the
    six attempts that had not happened yet: a preflight that reads the future is not a preflight,
    and every replayed attempt would have looked equally well-informed.

    Order is file order, which `events.py` states is the authority across runs. Timestamps are not
    used: three of the seven GP-327 runs are within two seconds of each other.
    """
    from . import events as _events
    out: List[Attempt] = []
    want = ticket_key(ticket)
    # ⚠ ONE pass. `runs()` + `fold()` per id re-read the whole stream per run — 3.7 s at 500 runs
    # against a 200 ms budget. `fold_all()` returns the same reduction in first-appearance order,
    # which is the ordering authority `events.py` states across runs.
    for run_id, fold in _events.fold_all().items():
        if before is not None and run_id == before:
            break
        if ticket_key(fold.get("ticket") or "") != want or not fold.get("terminal"):
            continue
        raw = fold.get("verdict")
        if raw is None or raw == Verdict.PASS.value:
            continue
        # A row written before this module existed carries no family key. That is NOT-RECORDED,
        # and re-deriving it here is a reading of the stream, never a rewrite of it.
        recorded = fold.get("failure_family")
        if recorded:
            c = Classification(recorded, str(fold.get("classified_by") or "recorded"))
        else:
            c = classify_recorded(fold)
            c = Classification(c.family, c.classified_by + " (re-derived; field NOT-RECORDED)")
        out.append(Attempt(run=run_id, at=str(fold.get("at") or fold.get("started_at") or ""),
                           verdict=raw, terminal=str(fold.get("terminal")),
                           family=c.family, classified_by=c.classified_by,
                           reason=_reason(fold, c.classified_by)))
    return out


# ------------------------------------------------------------------------------- the packet

#: ⚠ A hard cap, not a target. Three packets of 200 words each is the §M budget; one ticket's own
#: history is a single packet, so this is the whole of it. Over the cap is a bug — a preflight
#: that dumps history into every context is the failure it exists to prevent.
MAX_PACKET_WORDS = 200


@dataclass
class Match:
    """What the preflight found, rendered and recorded. Never a refusal."""
    ticket: str
    attempt_number: int
    prior: List[Attempt] = field(default_factory=list)
    prevention: Prevention = field(default_factory=lambda: Prevention(False))
    packet: str = ""

    @property
    def matched(self) -> bool:
        return bool(self.prior)

    @property
    def last(self) -> Optional[Attempt]:
        return self.prior[-1] if self.prior else None

    @property
    def same_family_as_prior(self) -> Optional[bool]:
        """Do the two most recent prior attempts share a family?

        None when there are fewer than two — with one prior attempt there is nothing to compare,
        and reporting False would claim the families differ.
        """
        if len(self.prior) < 2:
            return None
        return self.prior[-1].family == self.prior[-2].family

    @property
    def would_refuse(self) -> bool:
        """The shadow policy. ⛔ COMPUTED AND RECORDED; NEVER ACTED ON IN V0.

        Deliberately narrow: it fires only when a prior attempt of a known family exists **and** a
        deterministic check confirms the blocker is still present. A policy that refused on
        recurrence alone would refuse every legitimate retry-after-a-fix, and we have not yet
        observed a single false positive because we have not yet observed anything.
        """
        last = self.last
        if last is None or last.family == UNCLASSIFIED:
            return False
        return self.prevention.available and self.prevention.passed is False

    def as_event(self) -> dict:
        """The fields recorded on the `preflight_checked` event. See §6 of the approval.

        `run_started`, `eventual_verdict` and `eventual_failure_family` are **not** here: they are
        derived at read time from this run's own later events by `invocations()`. Storing them
        would mean writing a value before it is known, or writing the same fact twice.
        """
        last = self.last
        return {
            "attempt_number": self.attempt_number,
            "prior_attempt_count": len(self.prior),
            "prior_terminal_verdict": last.verdict if last else NOT_RECORDED,
            "prior_failure_family": last.family if last else NOT_RECORDED,
            "same_family_as_prior": self.same_family_as_prior,
            "prevention_check_available": self.prevention.available,
            "prevention_check_result": self.prevention.result,
            "prevention_detail": self.prevention.detail,
            "prevention_error": self.prevention.error,
            "context_packet_words": len(self.packet.split()),
            "warning_emitted": self.matched,
            "would_refuse": self.would_refuse,
            "policy": "WARN_ONLY_V0",
        }


def render(match: Match) -> str:
    """The packet an agent actually sees. Empty string when there is nothing to say.

    ⚠ An empty string, not a "no prior failures" block. A preflight that speaks on every run
    trains people to skim it, and the run with something to say is then the one nobody reads.
    """
    last = match.last
    if last is None:
        return ""
    lines = [
        "KNOWN_FAILURE_MATCH",
        f"previous_attempt: {last.run} at {last.at} (attempt {len(match.prior)} of this ticket)",
        f"failure_family: {last.family}"
        + (f" [{last.classified_by}]" if last.classified_by else ""),
        f"previous_verdict: {last.verdict}",
        f"previous_reason: {last.reason}",
        f"required_prevention: {match.prevention.detail or 'none known for this family'}"
        + f" -> {match.prevention.result}",
        f"would_refuse_under_policy: {str(match.would_refuse).lower()}",
        "",
        "This is a WARNING, not a refusal — this run has started. It is here because this ticket "
        "has failed before and the record survived. Verify it rather than assuming it: a family "
        "of UNCLASSIFIED means the previous failure was recorded but not understood.",
    ]
    text = "\n".join(lines)
    words = text.split()
    if len(words) > MAX_PACKET_WORDS:
        text = " ".join(words[:MAX_PACKET_WORDS]) + " …[truncated at the packet budget]"
    return text


def unavailable(ticket: str, exc: BaseException) -> Match:
    """The preflight itself could not run. ⚠ Not the same as having nothing to say.

    Returned by `control.RunController._preflight` when `check()` raises. The packet is empty — an
    instrument that fell over has no warning to give — but `prevention_check_result` is
    `CHECK_ERROR` and `prevention_error` names the exception, so `invocations()` can separate
    *"the preflight ran and found nothing"* from *"the preflight is broken"*.

    Reporting a crashed preflight as a clean silent one would mean the day it stops working is the
    day it looks healthiest, which is the failure this whole module exists to make visible.
    """
    m = Match(ticket=ticket, attempt_number=0,
              prevention=Prevention(False, detail="the preflight raised before it could look",
                                    error=f"{type(exc).__name__}: {exc}"))
    m.packet = ""
    return m


def check(ticket: str, ctx: Optional[dict] = None,
          before: Optional[str] = None) -> Match:
    """Run the preflight. ⛔ Returns a Match; refuses nothing, raises nothing on a match.

    `ctx` carries whatever the prevention checks need — today just `preset`.
    """
    prior = prior_attempts(ticket, before=before)
    family = prior[-1].family if prior else UNCLASSIFIED
    prev = prevention_for(family, ctx or {}) if prior else Prevention(False, detail="no prior attempts")
    m = Match(ticket=ticket, attempt_number=len(prior) + 1, prior=prior, prevention=prev)
    m.packet = render(m)
    return m


# ------------------------------------------------------------------------------- reading back

def invocations() -> List[dict]:
    """Every preflight, joined to what its run went on to do.

    ⭐ **This is the table that answers the only question worth asking:** did showing a run its
    previous failure change the outcome? Without the join we would be measuring that warnings were
    emitted, which is an activity metric with no outcome anchor — exactly what `factory.metrics`
    raises `GoodhartViolation` to prevent.
    """
    from . import events as _events
    out: List[dict] = []
    by_run: Dict[str, List[dict]] = {}
    for rec in _events.read():                       # one pass; see events.fold_all
        by_run.setdefault(rec.get("run"), []).append(rec)
    folds = _events.fold_all()
    for run_id, evs in by_run.items():
        pre = next((e for e in evs if e.get("kind") == "preflight_checked"), None)
        if pre is None:
            continue
        fold = folds.get(run_id, {})
        started = any(e.get("kind") == "agent_dispatched" for e in evs)
        verdict = fold.get("verdict")
        row = {k: v for k, v in pre.items() if k not in ("kind", "seq", "run")}
        row.update({
            "run": run_id,
            "ticket": fold.get("ticket"),
            "run_started": started,
            "eventual_verdict": verdict or NOT_RECORDED,
            "eventual_failure_family": (
                fold.get("failure_family")
                or (NOT_RECORDED if verdict in (None, Verdict.PASS.value) else UNCLASSIFIED)),
        })
        out.append(row)
    return out


def unclassified_share() -> dict:
    """How much of the failure record the taxonomy cannot place.

    ⚠ Three states, never two. `not_recorded` counts terminal events written before the field
    existed; `unclassified` counts failures we captured and could not map. A rising `unclassified`
    means the taxonomy is too narrow; a static `not_recorded` is just history.
    """
    from . import events as _events
    total = classified = unclassified = not_recorded = 0
    for fold in _events.fold_all().values():
        v = fold.get("verdict")
        if v is None or v == Verdict.PASS.value:
            continue
        total += 1
        fam = fold.get("failure_family")
        if not fam:
            not_recorded += 1
        elif fam == UNCLASSIFIED:
            unclassified += 1
        else:
            classified += 1
    return {"failures": total, "classified": classified, "unclassified": unclassified,
            "not_recorded": not_recorded,
            "unclassified_share": (unclassified / (classified + unclassified))
            if (classified + unclassified) else None,
            "basis": "MEASURED" if (classified + unclassified) else NOT_RECORDED}


def render_invocations() -> str:
    """The shadow-mode table, as text. Same content a UI would show, so the two cannot drift."""
    rows = invocations()
    if not rows:
        return ("no preflight has run.\nThat is NOT-RECORDED, not zero: the preflight was added "
                "on 2026-08-31 and every run in the stream predates it.")
    head = ("run", "ticket", "att", "prior", "same_fam", "prevention", "warn", "would_refuse",
            "words", "eventual")
    lines = ["  ".join(f"{h:<12}" for h in head)]
    for r in rows:
        lines.append("  ".join(f"{str(v):<12}" for v in (
            r["run"][-8:], r["ticket"], r["attempt_number"], r["prior_attempt_count"],
            r["same_family_as_prior"], r["prevention_check_result"], r["warning_emitted"],
            r["would_refuse"], r["context_packet_words"], r["eventual_verdict"])))
    return "\n".join(lines)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Known-failure preflight (WARN-ONLY).")
    ap.add_argument("ticket", nargs="?", help="show what this ticket's next run would be told")
    args = ap.parse_args(argv)
    if args.ticket:
        m = check(args.ticket)
        print(f"{args.ticket}: attempt {m.attempt_number}, {len(m.prior)} prior failure(s)\n")
        print(m.packet or "(nothing to say — no prior recorded failure)")
        print(f"\n{m.as_event()}")
        return 0
    print(render_invocations())
    print()
    print(unclassified_share())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
