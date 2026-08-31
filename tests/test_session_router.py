"""The session brief must be derived, must refuse rather than guess, and must not hand two
sessions the same files.

⭐ Every fact this module reports already existed — in `roadmap`, `lanes`, `claims`, `board`,
`registry` — and reached nobody. These tests pin the three properties that make the join worth
having rather than being a fifth place for the same numbers to rot.
"""
from __future__ import annotations

import pytest

from factory import lanes as _lanes
from factory import registry as _registry
from factory import session as S


# --------------------------------------------------------------------- the authored edge

def test_the_lane_shape_map_covers_every_lane_and_only_real_shapes():
    """`registry` routes on a shape and nothing else in the estate carries one, so this map is the
    missing edge. It is AUTHORED, and an authored map that drifts is worse than none — it still
    looks authoritative. `_validate()` runs at import; this proves it is not vacuous."""
    assert set(S.LANE_SHAPE) == {l.id for l in _lanes.LANES}
    assert set(S.LANE_SHAPE.values()) <= set(_registry.SHAPES)


def test_the_import_guard_actually_refuses_drift(monkeypatch):
    """The negative control. A guard nobody has watched fail is decoration."""
    monkeypatch.setitem(S.LANE_SHAPE, "a-lane-that-does-not-exist", "build")
    with pytest.raises(ImportError):
        S._validate()

    monkeypatch.delitem(S.LANE_SHAPE, "a-lane-that-does-not-exist")
    monkeypatch.setitem(S.LANE_SHAPE, next(iter(S.LANE_SHAPE)), "not-a-real-shape")
    with pytest.raises(ImportError):
        S._validate()


# --------------------------------------------------------------- refuse rather than guess

def test_routing_refuses_when_every_workflow_for_the_shape_declares_a_layer():
    """⛔ The bug this file was written after, caught on its first run.

    `build` has exactly two workflows and both are client-layer stage machines — `gep-feature`
    (warehouse/semantic_model/app) and `prefect-connector` (connector). A `Lane` carries a `repo`
    and a `touches` set but **no layer**, so there is nothing to match against. The first version
    preferred the layer-specific workflow and routed `control-plane` — agent-factory's own
    execution path — into a GEP warehouse machine.

    A resemblance is not a route. None is the honest answer, and the brief says why.
    """
    assert S.workflow_for("control-plane") is None

    text = S.render()
    assert "NO WORKFLOW" in text
    assert "army" in text, "the honest fallback must be named as a fallback, not offered as a route"


def test_routing_still_reaches_a_council_when_one_is_layer_agnostic():
    """Positive control. A router that returns None for everything has been disabled, not fixed."""
    w = S.workflow_for("judgement")
    assert w is not None and w.id == "conclave"
    assert not w.layers, "the match must be the layer-agnostic council"


def test_an_unmapped_lane_routes_to_nothing_rather_than_to_anything(monkeypatch):
    monkeypatch.delitem(S.LANE_SHAPE, "judgement")
    assert S.workflow_for("judgement") is None


# ------------------------------------------------------------------- derived, not stored

def test_the_brief_reflects_the_dependency_graph_rather_than_a_stored_copy(monkeypatch):
    """⭐ The property that stops this becoming a tenth boot prompt.

    A stored plan is correct when written and confidently wrong a day later — which is what the
    nine dated files in `boot-prompts/` became. The brief must read the graph on every call.

    ⚠ **This is asserted by SUBSTITUTING a graph, not by varying the passing set, and the reason
    is a finding.** Measured 2026-08-31: `lanes.waits_on()` returns `[]` for **every** lane and
    `runnable_now()` returns all five, whatever gates are passing — there are no recorded
    inter-lane dependencies at all. So varying `passing` cannot change the output, and a test that
    tried would be pinning the emptiness of today's data rather than the behaviour of the code.
    """
    monkeypatch.setattr(_lanes, "waits_on",
                        lambda passing=None: {"judgement": ["some-gate", "another"]})
    monkeypatch.setattr(_lanes, "runnable_now", lambda passing=None: ["artifact"])

    b = S.brief(passing=set())
    row = next(r for r in b["lanes"] if r["lane"] == "judgement")
    assert row["waits_on"] == ["some-gate", "another"], "the brief did not read the graph"
    assert not row["runnable"], "a lane that waits on something is not runnable"
    assert next(r for r in b["lanes"] if r["lane"] == "artifact")["runnable"]


def test_the_lane_dependency_graph_is_currently_empty_and_that_is_recorded():
    """⛔ Not a test of the router — a standing record of the gap it exposed.

    The estate has dependency machinery (`lanes.waits_on`, `unblocks`, `runnable_now`) and, at the
    ticket level, a `blocked_by` field. Measured: `waits_on()` is `[]` for every lane, and all 189
    task events carry an empty `blocked_by`. **The machinery is real and the data is absent.**

    This test passes today by asserting the emptiness out loud. When dependencies are finally
    recorded it will fail, and whoever it fails on should delete it — that is the point. A gap
    nobody has written down is one everybody re-discovers.
    """
    graph = _lanes.waits_on(set())
    assert all(not v for v in graph.values()), (
        "inter-lane dependencies now exist — good. Delete this test and let the router report "
        "them; it already reads the graph (see the test above).")


def test_the_brief_reports_the_things_the_operator_asked_for():
    """phases, dependencies, parallelism, ownership, routing — the four complaints, in one call."""
    b = S.brief()
    assert b["waves"], "phases"
    assert all("waits_on" in r for r in b["lanes"]), "dependencies"
    assert all("conflicts_with" in r for r in b["lanes"]), "parallelism"
    assert all("held_by" in r for r in b["lanes"]), "ownership"
    assert all("workflow" in r for r in b["lanes"]), "routing"


# --------------------------------------------------------------------- the collision rule

def test_start_refuses_a_lane_that_conflicts_with_a_live_claim(monkeypatch):
    """⛔ The branch-conflict problem, and the reason a session does not name its own branch.

    `claims` takes an `O_EXCL` lock, but a lock cannot see that two DIFFERENT lanes write the same
    files. That is what `lanes.conflicts()` knows and what the 2026-08-23 incident was: one session
    `git add`-ing across a directory another was mid-edit in, shipping a HEAD that did not import.
    """
    class _Held:
        who = "another session"

    monkeypatch.setattr(S._claims, "active", lambda: {"judgement": _Held()})
    took = []
    monkeypatch.setattr(S._claims, "claim", lambda *a, **k: took.append(a) or _Held())
    monkeypatch.setattr(S._worktrees, "ensure", lambda k: ("/nowhere", "not created"))

    with pytest.raises(SystemExit) as e:
        S.start("control-plane")
    assert "judgement" in str(e.value)
    assert not took, "it must refuse BEFORE taking a lock"


def test_start_names_the_alternatives_it_could_have_taken(monkeypatch):
    """A refusal that leaves the reader with nothing to do is a dead end, not a control."""
    class _Held:
        who = "another session"

    monkeypatch.setattr(S._claims, "active", lambda: {"judgement": _Held()})
    with pytest.raises(SystemExit) as e:
        S.start("control-plane")
    msg = str(e.value)
    assert any(other in msg for other in ("certify", "artifact", "grain")), msg


def test_start_refuses_an_unknown_lane_and_lists_the_real_ones():
    with pytest.raises(SystemExit) as e:
        S.start("no-such-lane")
    assert "judgement" in str(e.value)
