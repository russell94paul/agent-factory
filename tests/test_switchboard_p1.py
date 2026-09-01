"""P1 acceptance — canonical work, derived readiness, and a target that must resolve.

⭐ **The negative controls are the point of this file.** Every gate here is one that would look
identical whether it worked or not: a target check that never refuses, a readiness rule that
always says READY, a visibility field that renders PRIVATE work as unmarked. So each is paired
with a fixture that MUST fail, and several assert on the failure first.

The store is a `tmp_path` file in every test that writes. Nothing here touches the live
`.data/tasks.jsonl` — a test that appends to the estate's canonical ledger is a test that
permanently changes the thing it is measuring.
"""
from __future__ import annotations

import pathlib

import pytest

from factory import coordination as coord
from factory import switchboard as sb
from factory import switchboard_p1 as p1
from factory import tasks as T
from factory import work as W
from factory.tasks import TaskStore


@pytest.fixture()
def store(tmp_path) -> TaskStore:
    return TaskStore(tmp_path / "tasks.jsonl")


def _mk(store, wid, **kw):
    kw.setdefault("repo", "agent-factory")
    kw.setdefault("resource_claim", f"res-{wid.lower()}")
    return W.create(kw.pop("title", wid), work_id=wid, store=store, **kw)


# ============================================================ 1. arbitrary work, no manifest


def test_arbitrary_work_can_be_created_without_a_manifest(store):
    """⭐ MISSION_MANIFEST_REQUIRED / MANIFEST_CREATION_TOOL_MISSING, closed.

    No `.data/missions/<id>.json` exists anywhere in this test and none is written. Before P1 this
    piece of work would have been invisible to the Switchboard entirely.
    """
    w = _mk(store, "ARBITRARY-WORK-01", title="Something a human just thought of",
            objective="prove work needs no manifest")
    assert w.id == "ARBITRARY-WORK-01"
    rows = W.project(store=store, manifests=None)
    assert [r.id for r in rows] == ["ARBITRARY-WORK-01"]
    assert rows[0].objective == "prove work needs no manifest"
    assert not (pathlib.Path(store.path).parent / "missions").exists(), (
        "a manifest was written — the whole point is that none is needed")


def test_the_work_appears_in_the_switchboard_projection(store, monkeypatch):
    """It is not enough that the store holds it; the page's projection must carry it."""
    _mk(store, "VISIBLE-WORK-01")
    monkeypatch.setattr(sb, "store_path", lambda: store.path)
    monkeypatch.setattr(W, "store_path", lambda: store.path)
    monkeypatch.setattr(sb, "manifests", lambda: [])
    st = sb.state(cheap=True)
    assert "VISIBLE-WORK-01" in [w["id"] for w in st["work"]]


def test_an_explicit_id_is_required_to_be_addressable_and_unique(store):
    store.create("first", tid="DUPE-01")
    with pytest.raises(ValueError, match="already exists"):
        store.create("second", tid="DUPE-01")
    with pytest.raises(ValueError, match="must be 1-64 chars"):
        store.create("bad", tid="has spaces and /slashes")


# ============================================================ 2. dependencies are durable


def test_a_dependency_survives_being_satisfied(store):
    """⛔ The defect `block`/`unblock` has: a satisfied dependency must still be an edge.

    With `block`, `unblock` deletes the edge and a finished mission renders as unrelated tasks.
    """
    a = _mk(store, "DEP-UPSTREAM")
    b = _mk(store, "DEP-DOWNSTREAM", depends_on=["DEP-UPSTREAM"])
    assert b.depends_on == ["DEP-UPSTREAM"]

    store.add_evidence(a.id, "proof", "docs/x.md", actor="t", basis="MEASURED")
    store.close(a.id, actor="t")

    after = {w.id: w for w in W.project(store=store)}
    assert after["DEP-DOWNSTREAM"].depends_on == ["DEP-UPSTREAM"], (
        "the edge vanished once it was satisfied — the graph forgot its own shape")
    assert after["DEP-DOWNSTREAM"].state == W.READY


def test_a_dependency_cycle_is_refused(store):
    _mk(store, "CYC-A")
    _mk(store, "CYC-B", depends_on=["CYC-A"])
    with pytest.raises(ValueError, match="cycle"):
        store.depend("CYC-A", "CYC-B", actor="t")


def test_an_artifact_dependency_is_measured_against_the_disk(store, tmp_path):
    """⭐ So historical work never needs a fabricated predecessor task."""
    present = tmp_path / "real.md"
    present.write_text("x", encoding="utf-8")
    _mk(store, "ART-OK", artifacts=[{"ref": str(present), "kind": "evidence"}])
    _mk(store, "ART-MISSING", artifacts=[{"ref": str(tmp_path / "nope.md"), "kind": "evidence"}])
    rows = {w.id: w for w in W.project(store=store)}
    assert rows["ART-OK"].state == W.READY
    assert rows["ART-MISSING"].state == W.BLOCKED
    assert "does not exist" in rows["ART-MISSING"].blocked_reason


# ============================================================ 3. readiness is DERIVED


def test_readiness_cannot_be_chosen_only_derived(store):
    """There is no writer that sets READY, and the projection recomputes it every call."""
    assert not hasattr(store, "set_ready")
    assert not hasattr(store, "set_state")
    w = _mk(store, "DERIVED-01")
    assert w.state == W.READY
    store.depend("DERIVED-01", _mk(store, "DERIVED-BLOCKER").id, actor="t")
    assert {x.id: x for x in W.project(store=store)}["DERIVED-01"].state == W.BLOCKED


def test_an_unmeasured_check_is_never_a_pass(store):
    """⛔ UNKNOWN != PASS. Work with no declared repo is DRAFT — not READY, and not FAILED."""
    W.create("no repo declared", work_id="UNMEASURED-01", store=store,
             repo="", resource_claim="res-x")
    w = {x.id: x for x in W.project(store=store)}["UNMEASURED-01"]
    assert w.state == W.DRAFT, f"unmeasured readiness rendered as {w.state}"
    repo_check = next(c for c in w.checks if c.name == "repo")
    assert repo_check.verdict == W.UNMEASURED
    assert not repo_check.ok


def test_an_undeclared_resource_claim_is_unmeasured_not_conflict_free(store):
    """Absence of a declaration is not evidence of isolation, and must not read as one."""
    W.create("no claim", work_id="NOCLAIM-01", store=store, repo="agent-factory")
    w = {x.id: x for x in W.project(store=store)}["NOCLAIM-01"]
    c = next(x for x in w.checks if x.name == "contract")
    assert c.verdict == W.UNMEASURED
    assert w.state == W.DRAFT


def test_a_live_conflicting_writer_blocks_even_with_every_dependency_met(store):
    _mk(store, "CLASH-A", resource_claim="res-shared", access="WRITE")
    _mk(store, "CLASH-B", resource_claim="res-shared", access="WRITE")
    store.claim("CLASH-A", actor="agent")
    rows = {w.id: w for w in W.project(store=store)}
    assert rows["CLASH-A"].state == W.RUNNING
    assert rows["CLASH-B"].state == W.BLOCKED
    assert "res-shared" in rows["CLASH-B"].blocked_reason


def test_two_readers_of_one_resource_are_not_a_conflict(store):
    _mk(store, "READ-A", resource_claim="res-ro", access="READ")
    _mk(store, "READ-B", resource_claim="res-ro", access="READ")
    store.claim("READ-A", actor="agent")
    rows = {w.id: w for w in W.project(store=store)}
    assert rows["READ-B"].state == W.READY, "over-reporting a conflict is its own failure"


# ============================================================ 4. NEGATIVE CONTROL: targets


def test_an_invalid_target_is_refused(store):
    _mk(store, "REAL-TARGET-01")
    rows = W.project(store=store)
    with pytest.raises(W.TargetRefused, match="does not name any canonical work"):
        W.resolve("TYPO-TARGET-01", rows)
    with pytest.raises(W.TargetRefused, match="no target given"):
        W.resolve("", rows)
    assert W.resolve("REAL-TARGET-01", rows).id == "REAL-TARGET-01"
    assert W.resolve("real-target-01", rows).id == "REAL-TARGET-01", "case should still resolve"


def test_an_invalid_target_opens_nothing_and_compiles_no_context(monkeypatch, store):
    """⭐ THE safety-critical negative control.

    The measured P0 defect: an unresolved target fell through to a whole-mission packet still
    TITLED with the bogus target, so a session opened believing it was grounded in work that does
    not exist. This asserts the refusal happens before ANY of that — no packet built, no file
    written, no terminal spawned.
    """
    from scripts import local_tracker as lt

    spawned, packets = [], []
    monkeypatch.setattr(lt, "_spawn", lambda cmd, cwd: spawned.append(cmd))
    monkeypatch.setattr(sb, "startup_packet",
                        lambda **kw: packets.append(kw) or ("md", {}, []))
    monkeypatch.setattr(W, "store_path", lambda: store.path)
    _mk(store, "GOOD-TARGET-01")

    ok, msg = lt.start_synced(target="DEFINITELY-NOT-A-TARGET")
    assert ok is False
    assert "REFUSED" in msg
    assert spawned == [], "a terminal was opened for an unresolved target"
    assert packets == [], "context was compiled for an unresolved target"
    assert "no context was compiled" in msg


def test_work_that_is_not_ready_is_refused_by_start_synced(monkeypatch, store):
    from scripts import local_tracker as lt

    spawned = []
    monkeypatch.setattr(lt, "_spawn", lambda cmd, cwd: spawned.append(cmd))
    monkeypatch.setattr(W, "store_path", lambda: store.path)
    _mk(store, "BLOCKER-01")
    _mk(store, "NOT-READY-01", depends_on=["BLOCKER-01"])

    ok, msg = lt.start_synced(target="NOT-READY-01")
    assert ok is False and "not READY" in msg
    assert spawned == [], "a terminal was opened for work that is not READY"


def test_an_ambiguous_target_is_refused_rather_than_guessed(store):
    """Picking the closest match is the wrong-session dispatch this estate already refuses."""
    _mk(store, "AMBIG-ONE")
    _mk(store, "AMBIG-TWO")
    with pytest.raises(W.TargetRefused, match="Did you mean"):
        W.resolve("AMBIG", W.project(store=store))


# ============================================================ 5. NEGATIVE CONTROL: visibility


def test_private_work_never_renders_as_public(store):
    """⛔ Visibility must survive the whole lifecycle and default CLOSED."""
    _mk(store, "PRIV-01", visibility=T.PRIVATE)
    rows = {w.id: w for w in W.project(store=store)}
    assert rows["PRIV-01"].visibility == T.PRIVATE
    d = rows["PRIV-01"].to_dict()
    assert d["visibility_label"] == "PRIVATE"

    html = p1.work_card(d)
    assert "PRIVATE" in html
    assert "PUBLIC" not in html, "PRIVATE work rendered a PUBLIC mark"


def test_visibility_defaults_closed_for_rows_written_before_the_field_existed(store):
    """A legacy row must not become publishable because a field was added."""
    store.create("legacy row", tid="LEGACY-01")          # no visibility argument at all
    assert store.get("LEGACY-01").visibility == T.PRIVATE
    assert T.DEFAULT_VISIBILITY == T.PRIVATE

    store._emit({"ts": 0, "actor": "t", "kind": "create", "task": "LEGACY-02",
                 "data": {"title": "explicit null", "visibility": None}})
    assert store.get("LEGACY-02").visibility == T.PRIVATE, "an explicit null did not fall closed"


def test_visibility_persists_across_the_lifecycle(store):
    _mk(store, "VIS-LIFE-01", visibility=T.REVIEW_REQUIRED)
    store.claim("VIS-LIFE-01", actor="agent")
    store.add_evidence("VIS-LIFE-01", "proof", "docs/x.md", actor="t", basis="MEASURED")
    store.close("VIS-LIFE-01", actor="t")
    w = {x.id: x for x in W.project(store=store)}["VIS-LIFE-01"]
    assert w.state == W.DONE
    assert w.visibility == T.REVIEW_REQUIRED, "visibility was lost somewhere in the lifecycle"


def test_an_invalid_visibility_is_refused(store):
    with pytest.raises(ValueError):
        store.create("bad", tid="BADVIS-01", visibility="EVERYONE")


# ============================================================ 6. session association


def test_a_spawn_that_dies_immediately_does_not_move_work_to_running(monkeypatch, store):
    """⚠ `Popen` returning is evidence a process was CREATED, not that a session is live."""
    from scripts import local_tracker as lt

    class _Dead:
        def poll(self):
            return 1                                   # exited instantly

    monkeypatch.setattr(lt, "_SPAWN_CONFIRM_S", 0.01)
    assert lt._confirm_spawn(_Dead()) is False

    class _Alive:
        def poll(self):
            return None

    assert lt._confirm_spawn(_Alive()) is True


def test_session_association_is_recorded_only_when_known(store):
    _mk(store, "ASSOC-01")
    store.claim("ASSOC-01", actor="switchboard")
    assert {w.id: w for w in W.project(store=store)}["ASSOC-01"].session_id is None
    store.attach_session("ASSOC-01", "sess-abc123", actor="switchboard")
    w = {x.id: x for x in W.project(store=store)}["ASSOC-01"]
    assert w.session_id == "sess-abc123"
    assert w.state == W.RUNNING


# ============================================================ 7. old mission work still works


def test_manifested_mission_work_still_projects(store):
    """⛔ The legacy mission's opaque ids and manifest-only contracts must keep working."""
    tid = store.create("D5 · Recommendation", actor="t")        # opaque uuid, as before P1
    manifest = {"_id": "legacy-mission", "mission": "Legacy mission",
                "labels": {"D5": tid},
                "contracts": {tid: {"resource_claim": "res-legacy", "access": "READ"}}}
    rows = {w.id: w for w in W.project(store=store, manifests=[manifest])}
    assert rows[tid].from_manifest is True
    assert rows[tid].mission == "Legacy mission"
    assert rows[tid].contract["resource_claim"] == "res-legacy"


def test_legacy_block_events_still_produce_edges(store):
    """Rows predating `depend` recover their graph from the append-only block log."""
    a = store.create("upstream", actor="t")
    b = store.create("downstream", actor="t")
    store.block(b, by=a, actor="t")
    store.unblock(b, by=a, actor="t")                  # the edge is deleted from blocked_by
    assert store.get(b).blocked_by == []
    rows = {w.id: w for w in W.project(store=store)}
    assert rows[b].depends_on == [a], "the legacy edge was lost when it was satisfied"


# ============================================================ 8. autonomy


def test_autonomy_defaults_manual_and_guarded_denies_by_default(store):
    w = _mk(store, "AUTON-01")
    assert w.autonomy == T.MANUAL
    allowed, why = W.guarded_start(w)
    assert allowed is False
    assert any("MANUAL" in r for r in why)


def test_guarded_refuses_on_an_unmeasured_condition(store):
    """⭐ The rule that makes GUARDED safe rather than optimistic."""
    W.create("no repo", work_id="AUTON-UNMEAS", store=store, repo="", resource_claim="res-a")
    store.set_autonomy("AUTON-UNMEAS", T.GUARDED, actor="t")
    w = {x.id: x for x in W.project(store=store)}["AUTON-UNMEAS"]
    allowed, why = W.guarded_start(w)
    assert allowed is False
    assert any("UNMEASURED" in r for r in why), why


def test_guarded_refuses_a_publication_gate_and_non_private_visibility(store):
    _mk(store, "AUTON-GATE")
    store.set_autonomy("AUTON-GATE", T.GUARDED, actor="t")
    store.set_meta("AUTON-GATE", actor="t", contract={"publication_gate": "CLIENT_SAFE"})
    w = {x.id: x for x in W.project(store=store)}["AUTON-GATE"]
    allowed, why = W.guarded_start(w)
    assert allowed is False and any("publication_gate" in r for r in why)

    _mk(store, "AUTON-PUBLIC", visibility=T.PUBLIC)
    store.set_autonomy("AUTON-PUBLIC", T.GUARDED, actor="t")
    w2 = {x.id: x for x in W.project(store=store)}["AUTON-PUBLIC"]
    ok2, why2 = W.guarded_start(w2)
    assert ok2 is False and any("publication boundary" in r for r in why2)


def test_a_guarded_item_with_every_condition_met_is_allowed(store):
    """The permissive case must exist, or the deny-by-default rule proves nothing."""
    _mk(store, "AUTON-OK")
    store.set_autonomy("AUTON-OK", T.GUARDED, actor="t")
    w = {x.id: x for x in W.project(store=store)}["AUTON-OK"]
    allowed, why = W.guarded_start(w)
    assert allowed is True, why


def test_pause_outranks_the_policy_at_all_times(store):
    _mk(store, "AUTON-PAUSE")
    store.set_autonomy("AUTON-PAUSE", T.GUARDED, actor="t")
    store.pause_autonomy("AUTON-PAUSE", True, actor="operator")
    w = {x.id: x for x in W.project(store=store)}["AUTON-PAUSE"]
    allowed, why = W.guarded_start(w)
    assert allowed is False and any("PAUSED" in r for r in why)


def test_p1_ships_no_autonomous_executor(store):
    """⛔ The brief forbids uncontrolled recursive autonomous execution.

    `guarded_start` DECIDES; nothing calls it on a timer. This asserts the absence, because an
    absence is exactly the kind of property that quietly stops being true.
    """
    import inspect

    from scripts import local_tracker as lt
    src = inspect.getsource(lt) + inspect.getsource(W)
    for banned in ("threading.Timer", "sched.scheduler", "while True:\n        start_synced"):
        assert banned not in src, f"an autonomous execution loop appeared: {banned}"
    # `guarded_start` must exist and be reachable, but nothing may CALL it to spawn.
    assert "record_start" in inspect.getsource(lt), "the start mode is not recorded at all"
    assert "def guarded_start" in inspect.getsource(W), "the decision function is gone"
    assert "guarded_start" not in inspect.getsource(lt.start_synced), (
        "start_synced consults the autonomy policy — that is the trigger this must not have; "
        "a guarded item still requires an operator to press START SYNCED")


def test_the_start_mode_is_recorded(store):
    _mk(store, "MODE-01")
    store.record_start("MODE-01", T.MANUAL_START, actor="t")
    assert {x.id: x for x in W.project(store=store)}["MODE-01"].start_mode == T.MANUAL_START
    with pytest.raises(ValueError):
        store.record_start("MODE-01", "SOMEHOW_ELSE", actor="t")


# ============================================================ 9. coordination


def test_coordination_publishes_no_aggregate_percentage(store):
    """⛔ No headline coordination-tax number until its denominator is defined."""
    _mk(store, "COORD-01")
    st = {"work": [w.to_dict() for w in W.project(store=store)],
          "now": {"needs_you": []}}
    sig = coord.signals(st, store)
    assert sig, "no signals at all"
    for g in sig:
        assert g.basis in ("MEASURED", "DERIVED", "NOT-RECORDED", "NOT-VISIBLE")
        assert "%" not in str(g.value), f"{g.name} published a percentage"
    names = {g.name for g in sig}
    assert not any("tax" in n.lower() or "score" in n.lower() for n in names)


def test_unrecorded_starts_are_neither_manual_nor_autonomous(store):
    """Folding them into MANUAL would invent an operator decision nobody made."""
    _mk(store, "COORD-OLD")
    store.claim("COORD-OLD", actor="agent")             # claimed, but no `start` event
    sig = {g.name: g for g in coord.signals(
        {"work": [w.to_dict() for w in W.project(store=store)], "now": {"needs_you": []}}, store)}
    assert sig["manual launches"].value == 0
    assert sig["autonomous launches"].value == 0
    assert sig["starts with no recorded mode"].value == 1
    assert sig["starts with no recorded mode"].basis == "NOT-RECORDED"


def test_intervention_priority_is_explainable_and_banded(store):
    """⛔ A band plus its factors, never a decimal score presented as precision."""
    _mk(store, "PRI-ROOT")
    _mk(store, "PRI-CHILD-A", depends_on=["PRI-ROOT"])
    _mk(store, "PRI-CHILD-B", depends_on=["PRI-CHILD-A"])
    works = [w.to_dict() for w in W.project(store=store)]

    assert coord.downstream_blocked("PRI-ROOT", works) == ["PRI-CHILD-A", "PRI-CHILD-B"], (
        "downstream blocking must be transitive — one item blocking one that blocks four is not "
        "a low-priority intervention")

    rows = coord.prioritise(
        [{"kind": "WORK", "live": True, "work": next(w for w in works if w["id"] == "PRI-ROOT"),
          "questions": [{}]},
         {"kind": "QUESTION", "live": False, "work": None, "questions": [{}], "orphan": True}],
        works, critical=["PRI-ROOT"])
    assert rows[0]["priority"] == coord.HIGH
    assert rows[0]["why"], "a priority with no stated reason is unusable"
    assert any("Blocks 2 downstream" in x for x in rows[0]["why"])
    assert rows[-1]["priority"] == coord.LOW
    for r in rows:
        assert isinstance(r["priority"], str) and r["priority"] in (
            coord.HIGH, coord.MEDIUM, coord.LOW)


def test_an_unattributed_question_is_never_dropped(store):
    """The inbox exists because a question must not be filtered by the thing that produced it."""
    works = [w.to_dict() for w in W.project(store=store)]
    buckets = sb.now_buckets(works, [{"name": "some session", "needs": "is this ok?"}])
    assert buckets["needs_you_count"] == 1
    assert buckets["needs_you"][0]["orphan"] is True


# ============================================================ 10. the rendered surface


@pytest.fixture()
def live_state():
    return sb.state(cheap=True)


def test_every_p1_view_renders(live_state):
    for view in [v for v, _ in p1.VIEWS] + [v for v, _ in p1.MORE_VIEWS] + ["create"]:
        html = p1.page(live_state, view=view, token="tok", runtime="rt")
        assert len(html) > 500, f"view {view} rendered almost nothing"
        assert "AGENT FACTORY" in html


def test_the_now_page_leads_with_the_three_questions(live_state):
    html = p1.page(live_state, view="now", token="tok", runtime="rt")
    for panel in ("NEEDS YOU", "NEXT", "RUNNING", "RECENT"):
        assert panel in html.upper(), f"the NOW page does not carry {panel}"
    assert html.upper().index("NEEDS YOU") < html.upper().index("RECENT")


def test_the_p0_panels_are_retained_behind_disclosure(live_state):
    """Retained, not removed — and not dominant."""
    html = p1.page(live_state, view="now", token="tok", runtime="rt")
    assert 'action="/switchboard/start"' in html
    assert 'action="/switchboard/dispatch"' in html
    assert "<details class=\"p0\"" in html
    assert html.index("Needs you") < html.index('<details class="p0"')


def test_refresh_and_restart_state_different_things(live_state):
    html = p1.page(live_state, view="now", token="tok", runtime="rt")
    assert "Refresh" in html and "Restart Switchboard" in html and "Re-measure" in html
    assert "the loaded Python is unchanged" in html, (
        "Refresh does not say it is NOT a code reload")
    assert "replaces the whole server process" in html


def test_restart_is_unavailable_without_a_supervisor(live_state):
    """A restart with nothing to restart it is a remote kill switch."""
    html = p1.page(live_state, view="now", token="", runtime="rt")
    assert 'action="/switchboard/restart"' not in html
    assert "not supervised" in html or "was not started" in html


def test_the_mobile_bottom_nav_is_present_and_small(live_state):
    html = p1.page(live_state, view="now", token="tok", runtime="rt")
    assert 'class="bnav"' in html
    assert len(p1.BOTTOM) == 5, "a bottom nav that needs a scroll is a menu"


def test_the_page_declares_a_runtime_for_the_restart_poll(live_state):
    html = p1.page(live_state, view="now", token="tok", runtime="RUNTIME-XYZ")
    assert 'data-runtime="RUNTIME-XYZ"' in html, (
        "without this the poll cannot tell a NEW process from the dying one answering 200")


def test_the_inspector_shows_readiness_reasoning_not_just_a_verdict(store, monkeypatch):
    _mk(store, "INSPECT-BLOCKED", depends_on=[_mk(store, "INSPECT-DEP").id])
    rows = [w.to_dict() for w in W.project(store=store)]
    st = {"work": rows, "now": {}, "measured_at": "now", "sessions": [], "warnings": []}
    html = p1.inspector(st, "INSPECT-BLOCKED", "now")
    assert "INSPECT-DEP" in html
    assert "UNMEASURED is not a pass" in html
    assert "Autonomy" in html and "Coordination" in html


def test_the_inspector_shows_evidence_references_never_bodies(store):
    _mk(store, "EV-01")
    store.add_evidence("EV-01", "proof", "docs/evidence/secret-analysis.md",
                       actor="t", basis="MEASURED")
    rows = [w.to_dict() for w in W.project(store=store)]
    st = {"work": rows, "now": {}, "measured_at": "n", "sessions": [], "warnings": []}
    html = p1.inspector(st, "EV-01", "now")
    assert "docs/evidence/secret-analysis.md" in html
    assert "References only" in html, "the page does not say it is showing paths, not content"


# ============================================================ 11. the real dogfood, live


LIVE = ("MARKETING-MODEL-FINALIZATION-01", "AF-CLIENT-REVIEW-P1.5")


@pytest.mark.parametrize("wid", LIVE)
def test_the_real_follow_on_work_exists_canonically(wid):
    rows = {w.id: w for w in W.project(manifests=sb.manifests())}
    if wid not in rows:
        pytest.skip(f"{wid} not in this machine's store")
    w = rows[wid]
    assert w.visibility == "PRIVATE"
    assert w.repo == "agent-factory"
    assert w.start_mode is None, "the dogfood work was STARTED — it must not be"
    assert w.status != "claimed", "the dogfood work is running"


def test_the_dependency_between_them_is_real():
    rows = {w.id: w for w in W.project(manifests=sb.manifests())}
    if not all(k in rows for k in LIVE):
        pytest.skip("dogfood work not in this machine's store")
    p15 = rows["AF-CLIENT-REVIEW-P1.5"]
    assert "MARKETING-MODEL-FINALIZATION-01" in p15.depends_on
    assert p15.state != W.READY, "P1.5 is READY while its predecessor is not done"
    fin = rows["MARKETING-MODEL-FINALIZATION-01"]
    for dep in fin.depends_on:
        assert dep in rows, f"{fin.id} depends on {dep}, which is not in the store"
