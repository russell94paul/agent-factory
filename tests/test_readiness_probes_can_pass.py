"""No readiness gate may be unreachable.

`test_eval_can_fail.py` holds the contract's half of this rule: an assertion nobody has
shown able to fail is not an assertion. This is the other half, for the readiness gates:
**a gate nobody could satisfy is not a gate.**

It is not hypothetical. On 2026-08-22 two of the thirty probes —
`g_failure_is_bounded` (gate `bounded`) and `g_orphans_are_reaped` (gate `reaper`) —
had exactly one return path each, `_fail`. They were constants wearing an instrument's
clothes. No amount of work on the build plane could ever have moved them, and both sat
in the readiness table for a day being read as measurements of an unbounded, unreaped
system. Nothing in the suite noticed, because nothing was looking at the probes.

⚠ **What this can and cannot see.** It is a static reachability check: it proves a PASS
verdict is *written* in the probe, not that any input reaches it. A probe whose PASS
branch is guarded by `if False` would satisfy this test. That is a weaker guarantee than
the mutation harness in `scripts/mutate_readiness_probes.py`, which removes the control
and requires the probe to change its answer — and the two are complementary rather than
alternatives. This one is cheap enough to run on every commit; that one is not.
"""
from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from factory import readiness
from factory.readiness import GATES

_SRC = ast.parse(pathlib.Path(inspect.getfile(readiness)).read_text(encoding="utf-8"))
_FUNCS = {n.name: n for n in ast.walk(_SRC) if isinstance(n, ast.FunctionDef)}

#: Gates whose probe has no PASS path, and whose fix belongs to another lane. Entries are
#: `xfail`, never `skip`: a known defect must stay visible in the report and must flip to
#: XPASS the moment somebody fixes it. Anything added here needs an argument and an owner,
#: because "this gate can never pass" is a claim someone has to defend in writing.
KNOWN_UNREACHABLE: dict[str, str] = {
    "corpus": (
        "g_corpus_is_tamper_evident returns _fail on every branch, including the one where "
        "all four of its sub-checks passed. Its closing line — 'NOT ENFORCED: the corpus "
        "still lives in a repo this agent can write to' — is written as an unconditional "
        "verdict, so moving the corpus out via $AGENT_FACTORY_EVALS would change nothing "
        "the gate reports. Same class as `bounded` and `reaper` were. Owner: the certify "
        "lane, which owns `corpus`; recorded in docs/findings.md 2026-08-22."
    ),
}


#: Gates whose probe has no way of REFUSING, same rules as above.
KNOWN_CANNOT_REFUSE: dict[str, str] = {
    "tenancy": (
        "g_tenancy_declared passes when allowed_tenants is non-empty and raises "
        "Unmeasurable when it is empty. But an empty list IS a measurement — the "
        "blueprint was read successfully and the answer was 'none declared'. Reporting "
        "that as UNMEASURABLE ('no instrument could be established') rather than FAIL "
        "('blast radius is not declared') collapses two of the contract's four verdicts "
        "in the direction the contract exists to prevent. Owner: the certify lane, which "
        "owns `tenancy`; recorded in docs/findings.md 2026-08-22."
    ),
}

_HELPERS = ("_pass", "_fail", "_notrun")


def _verdicts_reachable(fn: ast.FunctionDef) -> set[str]:
    """Every verdict this probe can return, by the helper or constant it names.

    ⚠ **This checker was itself blind until 2026-08-30, and reported a false defect for it.**
    It read only the *immediate* call in a `return`, so the extremely ordinary

        res = _pass(...)          # or _fail(...)
        _cache_write(...)         # something in between
        return res

    looked like a probe with no PASS path. `g_contract_suite_green` builds its result, writes it
    to a cache, and then returns the name — and was reported as *"a constant, not a measurement"*
    while being neither. The red was read for days as sibling-repo noise.

    That is the same family as the defects this file exists to catch, one level up: **an
    instrument that cannot see reports absence with total confidence.** So the walk now follows
    a name back to the helper it was assigned from. It is still static and still shallow — it
    does not follow a helper through a branch into a second name, and a probe that hid its
    verdict behind two hops would fool it.
    """
    assigned: dict[str, set[str]] = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign):
            f = getattr(getattr(node.value, "func", None), "id", None)
            if f in _HELPERS:
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        assigned.setdefault(t.id, set()).add(f)

    seen: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and node.value is not None:
            f = getattr(getattr(node.value, "func", None), "id", None)
            if f in _HELPERS:
                seen.add(f)
            elif isinstance(node.value, ast.Name):
                if node.value.id in ("PASS", "FAIL", "UNMEASURABLE", "NOT_RUN"):
                    seen.add(node.value.id)
                seen |= assigned.get(node.value.id, set())
    return seen


@pytest.mark.parametrize("gate", GATES, ids=lambda g: g.id)
def test_every_gate_can_report_pass(gate):
    fn = _FUNCS.get(gate.probe.__name__)
    assert fn is not None, f"{gate.id}: probe {gate.probe.__name__} not found in the source"
    reachable = _verdicts_reachable(fn)
    if gate.id in KNOWN_UNREACHABLE and not ("_pass" in reachable or "PASS" in reachable):
        pytest.xfail(KNOWN_UNREACHABLE[gate.id])
    assert "_pass" in reachable or "PASS" in reachable, (
        f"gate {gate.id!r} ({gate.probe.__name__}) has no PASS path: it can only return "
        f"{sorted(reachable) or 'nothing'}. That is a constant, not a measurement — "
        f"no work on the system it claims to measure could ever satisfy it.")


@pytest.mark.parametrize("gate", GATES, ids=lambda g: g.id)
def test_every_gate_can_refuse(gate):
    """The mirror. A probe that can only pass is decoration in the other direction.

    NOT_RUN counts as a refusal. The contract's four verdicts are never collapsed, and a
    gate that tracks whether something has been ASKED — the three research follow-ups —
    is right to answer "not asked yet" rather than "failed". What none of them may do is
    have no way of declining at all.

    An `Unmeasurable` raise deliberately does NOT count. UNMEASURABLE means no instrument
    could be established; it is not a judgement about the system, and a gate whose only
    non-pass outcome is "I could not look" has still never refused anything.
    """
    fn = _FUNCS[gate.probe.__name__]
    reachable = _verdicts_reachable(fn)
    if gate.id in KNOWN_CANNOT_REFUSE and not reachable & {"_fail", "FAIL", "_notrun", "NOT_RUN"}:
        pytest.xfail(KNOWN_CANNOT_REFUSE[gate.id])
    assert reachable & {"_fail", "FAIL", "_notrun", "NOT_RUN"}, (
        f"gate {gate.id!r} ({gate.probe.__name__}) can only report success. A gate that "
        f"cannot refuse is decoration.")


def test_the_control_plane_probes_watch_rather_than_grep():
    """The five control-plane probes must execute the build plane, not read it for a word.

    A probe satisfied by a string is satisfied by a comment mentioning that string — and
    by the lane that writes the comment. Four of these five were exactly that before
    2026-08-22: two constants, one grepping the wrong file, one matching a variable name
    the graded party chooses.
    """
    for name in ("g_attempt_cap_on_the_live_path", "g_failure_is_bounded",
                 "g_concurrency_is_reserved_outside_the_agent", "g_orphans_are_reaped",
                 "g_verdict_is_computed_from_history"):
        fn = _FUNCS[name]
        calls = {getattr(n.func, "id", None) for n in ast.walk(fn) if isinstance(n, ast.Call)}
        assert "_engine" in calls, (
            f"{name} does not drive the build plane. A control-plane gate must watch the "
            f"control refuse; reading source for a pattern is not watching.")
