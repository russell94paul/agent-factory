"""The Switchboard join, tested where it can be wrong.

Everything here targets `factory/switchboard.py` rather than the rendered page. The HTML is a
projection of a projection; what can silently lie is the join — a dependency that stops blocking
because its edge was deleted, a dead process shown as resumable, a bus cursor advanced by looking.

Two page-level tests are included and only two: that the route renders at all, and that it does not
pay for a readiness measure. Both are properties the HTML is the only place to observe.
"""
from __future__ import annotations

import json

import pytest

from factory import bus as buslib
from factory import sessions as sesslib
from factory import switchboard as sb
from factory.tasks import TaskStore


# --------------------------------------------------------------------- fixtures


def _mission(tmp_path):
    """A four-task mission whose shape exercises every classification branch.

    A -> B, A -> C, C -> D.  B and C both WRITE `shared`, so they conflict; D reads it, so it does
    not conflict with anything. That single graph is enough to test dependency blocking,
    conflict blocking, parallel-safety and the critical path together.
    """
    store = TaskStore(tmp_path / "tasks.jsonl")
    mid = store.create("MISSION", actor="test")
    ids = {}
    for lbl in ("A", "B", "C", "D"):
        ids[lbl] = store.create(f"{lbl} · task {lbl}", actor="test", parent=mid)
    for child, parent in (("B", "A"), ("C", "A"), ("D", "C")):
        store.block(ids[child], by=ids[parent], actor="test")
    man = {
        "_id": "m1", "mission": "MISSION", "mission_task": mid,
        "labels": dict(ids),
        "contracts": {
            ids["A"]: {"label": "A", "resource_claim": "src", "access": "READ"},
            ids["B"]: {"label": "B", "resource_claim": "shared", "access": "WRITE"},
            ids["C"]: {"label": "C", "resource_claim": "shared", "access": "WRITE"},
            ids["D"]: {"label": "D", "resource_claim": "shared", "access": "READ"},
        },
    }
    return store, man, ids


def _rows(store, man, critical=()):
    return sb.classify(sb._task_rows(store, man), list(critical))


def _by(rows):
    return {r["label"]: r for r in rows}


def _session(**kw):
    base = {"pid": 1, "session_id": "s" * 8, "cwd": "C:/repo", "state": sesslib.RUNNING_ATTACHED,
            "name": "n", "status": "busy", "kind": "interactive", "agent": None, "job_id": None,
            "repo": "repo", "lane": None, "where": "repo", "topic": "t", "job_state": None,
            "tempo": None, "tokens": None, "detail": "", "needs": "", "in_flight": None}
    base.update(kw)
    return base


# ------------------------------------------------------------- the dependency graph


def test_the_dag_survives_its_dependencies_being_satisfied(tmp_path):
    """⛔ The defect this module was written around.

    `TaskStore.unblock()` DELETES the edge from `Task.blocked_by`, so a mission whose dependencies
    have all been met renders as a set of unrelated tasks with no critical path. Measured on the
    live marketing-model mission on 2026-09-01: D5 showed `blocked_by = []` with a `block` event
    naming D4. The edges must come from the append-only event log.
    """
    store, man, ids = _mission(tmp_path)
    store.unblock(ids["B"], by=ids["A"], actor="test")
    store.unblock(ids["C"], by=ids["A"], actor="test")

    assert store.get(ids["C"]).blocked_by == [], "precondition: unblock cleared the live field"
    rows = _by(_rows(store, man))
    assert rows["C"]["depends_on"] == ["A"], (
        "a satisfied dependency vanished from the DAG — the graph was read from blocked_by")
    assert sb._longest_chain(sb._edges(store, list(ids.values()))), "critical path collapsed"


def test_the_critical_path_is_the_longest_dependency_chain(tmp_path):
    store, man, ids = _mission(tmp_path)
    edges = sb._edges(store, list(ids.values()))
    by_id = {v: k for k, v in ids.items()}
    chain = [by_id[t] for t in sb._longest_chain(edges)]
    assert chain == ["A", "C", "D"], chain
    assert sb.CRITICAL_PATH_BASIS == "DEPENDENCY", (
        "the page labels the path from this constant; a duration basis would be an ETA built on "
        "estimates the manifest itself marks ASSUMED")


def test_waves_place_independent_tasks_together(tmp_path):
    store, man, ids = _mission(tmp_path)
    by_id = {v: k for k, v in ids.items()}
    lv = [sorted(by_id[t] for t in w) for w in sb.waves(sb._edges(store, list(ids.values())))]
    assert lv == [["A"], ["B", "C"], ["D"]]


# ------------------------------------------------------------------ classification


def test_dependency_blocked_work_is_never_ready(tmp_path):
    store, man, ids = _mission(tmp_path)
    rows = _by(_rows(store, man))
    for lbl in ("B", "C", "D"):
        assert rows[lbl]["state"] == sb.BLOCKED, f"{lbl} is startable with A not done"
        assert "waits on" in rows[lbl]["blocked_reason"]
    assert rows["A"]["state"] in (sb.READY, sb.READY_IN_PARALLEL)


def test_a_live_conflicting_writer_blocks_a_dependency_satisfied_task(tmp_path):
    """The rule a dependency-only scheduler gets wrong.

    A is done, so B and C are both dependency-clear. They both WRITE `shared`. With C claimed,
    B must NOT be offered as parallel-safe — two agents writing one resource is the collision the
    DAG cannot see.
    """
    store, man, ids = _mission(tmp_path)
    store.add_evidence(ids["A"], kind="analysis", ref="x", actor="test")
    store.close(ids["A"], actor="test")
    store.claim(ids["C"], actor="agent-1")

    rows = _by(_rows(store, man))
    assert rows["C"]["state"] == sb.RUNNING
    assert rows["B"]["state"] == sb.BLOCKED, (
        "B was offered while a live writer holds the same resource claim")
    assert "live writer" in rows["B"]["blocked_reason"]
    assert "shared" in rows["B"]["blocked_reason"]


def test_a_read_only_task_does_not_conflict_with_another_reader(tmp_path):
    """Over-reporting a conflict ends the same way as under-reporting it: nobody believes it."""
    store, man, ids = _mission(tmp_path)
    for c in man["contracts"].values():
        c["access"] = "READ"
    rows = _by(_rows(store, man))
    assert rows["B"]["conflicts_with"] == [] and rows["C"]["conflicts_with"] == []


def test_parallel_safe_is_off_the_critical_path_and_ready_is_on_it(tmp_path):
    store, man, ids = _mission(tmp_path)
    store.add_evidence(ids["A"], kind="analysis", ref="x", actor="test")
    store.close(ids["A"], actor="test")
    for c in man["contracts"].values():
        c["access"] = "READ"                       # remove the conflict, isolate the path rule
    rows = _by(_rows(store, man, critical=["A", "C", "D"]))
    assert rows["C"]["state"] == sb.READY, "a critical-path task is the work, not a spare seat"
    assert rows["B"]["state"] == sb.READY_IN_PARALLEL


def test_a_written_question_outranks_a_running_process(tmp_path):
    """The operator's next action on a blocked task is the answer, not the observation."""
    store, man, ids = _mission(tmp_path)
    store.claim(ids["A"], actor="agent-1")
    plain = _by(sb.classify(sb._task_rows(store, man), []))
    assert plain["A"]["state"] == sb.RUNNING
    withq = _by(sb.classify(sb._task_rows(store, man), [], {"A": [{"needs": "ok to read key?"}]}))
    assert withq["A"]["state"] == sb.NEEDS_HUMAN


# ---------------------------------------------------------------------- sessions


def test_a_live_attached_session_is_open_not_resume():
    c = sb.session_cards([_session(state=sesslib.RUNNING_ATTACHED)])[0]
    assert c["can_open"] and not c["can_resume"] and c["is_live"]
    assert c["action"] == "OPEN"


def test_an_orphaned_session_is_never_offered_a_resume():
    """⛔ Resuming a live session spawns a second process against one transcript — the
    divergent-duplicate failure recorded in control-room.md §5. ORPHANED is alive; it is only
    detached."""
    c = sb.session_cards([_session(state=sesslib.RUNNING_ORPHANED, kind="bg")])[0]
    assert not c["can_resume"], "an orphaned (live) session was offered a resume"
    assert c["is_live"] and "DO NOT DUPLICATE" in c["action"]


def test_an_exited_session_with_a_transcript_is_resumable():
    c = sb.session_cards([_session(state=sesslib.EXITED_RESUMABLE)])[0]
    assert c["can_resume"] and not c["is_live"] and c["action"] == "RESUME"


def test_a_dead_registry_entry_is_not_treated_as_live():
    """A registry file outlives its process. `EXITED-GONE` has no transcript either, so the only
    honest action is a new session."""
    c = sb.session_cards([_session(state=sesslib.EXITED_GONE)])[0]
    assert not c["is_live"] and not c["can_resume"] and c["action"] == "NEW SESSION"


def test_unknown_liveness_is_not_a_safe_resume():
    """UNKNOWN means the process table could not be read. 'It exited' is then not a measurement,
    it is the absence of one — so resume must be refused and the page must say why."""
    c = sb.session_cards([_session(state=sesslib.UNKNOWN)])[0]
    assert not c["can_resume"] and not c["liveness_trusted"]
    assert "do not resume" in c["action"].lower()


def test_a_blocked_question_survives_the_process_that_asked_it(monkeypatch, tmp_path):
    """⭐ The 2026-08-23 defect, guarded at the Switchboard's own boundary.

    A session-keyed inbox systematically hides the questions that have waited LONGEST, because the
    longer a question waits the more likely its session has exited. Every one of the five questions
    on this machine on 2026-09-01 was `NO-SESSION`. So `needs_you` must be sourced from
    `sessions.blocked()` (jobs) and must never be filtered by the session inventory.
    """
    monkeypatch.setattr(sb._sessions, "inventory", lambda: [])          # not one live session
    monkeypatch.setattr(sb._sessions, "blocked",
                        lambda: [{"needs": "okay to read the key?", "state": "NO-SESSION",
                                  "job_id": "j1", "waiting_since": 0}])
    monkeypatch.setattr(sb, "manifests", lambda: [])
    monkeypatch.setattr(sb, "store_path", lambda: tmp_path / "nope.jsonl")
    monkeypatch.setattr(sb, "upstream", lambda *a, **k: [])
    st = sb.state(cheap=True)
    assert st["needs_you_count"] == 1, "a question was dropped because its session had exited"
    assert st["sessions"] == []


# -------------------------------------------------------------------------- bus


def test_an_unread_bus_event_is_surfaced(monkeypatch, tmp_path):
    monkeypatch.setattr(buslib, "ROOT", tmp_path)
    buslib.post("peer", "correction", "the grain is not what D3 assumed")
    got = sb.upstream(["me"])
    assert len(got) == 1 and got[0]["unread"] == 1
    assert "grain" in got[0]["rendered"]
    assert "nudge, not durable evidence" in got[0]["basis"], (
        "peer traffic rendered without the caveat that it is not evidence")


def test_reading_the_switchboard_does_not_advance_a_bus_cursor(monkeypatch, tmp_path):
    """⛔ `mark_read` is called AFTER delivery, by the thing that delivered it — the lane-bus hook
    injecting traffic into a session's context. If opening this page counted as delivery, a
    correction would be marked seen by a session that never saw it."""
    monkeypatch.setattr(buslib, "ROOT", tmp_path)
    buslib.post("peer", "correction", "one")
    cursor = buslib._cursor_path("me")
    assert not cursor.exists()
    sb.upstream(["me"])
    sb.upstream(["me"])
    assert not cursor.exists(), "rendering the Switchboard advanced a reader's cursor"
    assert len(buslib.unread("me")) == 1, "the event stopped being unread without being delivered"


def test_a_lane_never_reads_its_own_traffic_back(monkeypatch, tmp_path):
    monkeypatch.setattr(buslib, "ROOT", tmp_path)
    buslib.post("me", "note", "mine")
    assert sb.upstream(["me"]) == []


def test_bus_readers_include_read_only_and_write_only_lanes(monkeypatch, tmp_path):
    """A lane that has only written has a file and no cursor; one that has only read has a cursor
    and no file. Taking either source alone lists half the estate."""
    monkeypatch.setattr(buslib, "ROOT", tmp_path)
    buslib.post("writer", "note", "x")
    buslib.mark_read("reader")
    assert sb.bus_readers() == ["reader", "writer"]


# ------------------------------------------------------------------- honest gaps


def test_a_task_with_no_declared_resource_claim_is_reported_as_a_warning(tmp_path, monkeypatch):
    """Absence of a declaration is not evidence of isolation, and the page must not let it read
    like one."""
    store, man, ids = _mission(tmp_path)
    man["contracts"][ids["B"]].pop("resource_claim")
    monkeypatch.setattr(sb, "manifests", lambda: [dict(man, _id="m1", _mtime=0)])
    monkeypatch.setattr(sb, "store_path", lambda: store.path)
    monkeypatch.setattr(sb._sessions, "inventory", lambda: [])
    monkeypatch.setattr(sb._sessions, "blocked", lambda: [])
    monkeypatch.setattr(sb, "upstream", lambda *a, **k: [])
    st = sb.state(cheap=True)
    assert any("no resource claim declared for B" in w for w in st["warnings"])
    assert any("not evidence of isolation" in w for w in st["warnings"])


def test_a_mission_child_outside_the_manifest_is_warned_about_not_hidden(tmp_path, monkeypatch):
    """Two such tasks exist on this machine from an earlier `--create`. The store is append-only,
    so they cannot be removed — only reported."""
    store, man, ids = _mission(tmp_path)
    store.create("a stray earlier attempt", actor="test", parent=man["mission_task"])
    monkeypatch.setattr(sb, "manifests", lambda: [dict(man, _id="m1", _mtime=0)])
    monkeypatch.setattr(sb, "store_path", lambda: store.path)
    monkeypatch.setattr(sb._sessions, "inventory", lambda: [])
    monkeypatch.setattr(sb._sessions, "blocked", lambda: [])
    monkeypatch.setattr(sb, "upstream", lambda *a, **k: [])
    st = sb.state(cheap=True)
    assert any("not in the manifest" in w for w in st["warnings"])


def test_the_projection_is_never_written_to_disk(tmp_path, monkeypatch):
    """`state()` is derived per call. A stored projection is what the boot prompts kept becoming:
    correct when written, confidently wrong an hour later."""
    monkeypatch.setattr(sb, "manifests", lambda: [])
    monkeypatch.setattr(sb, "store_path", lambda: tmp_path / "nope.jsonl")
    monkeypatch.setattr(sb._sessions, "inventory", lambda: [])
    monkeypatch.setattr(sb._sessions, "blocked", lambda: [])
    monkeypatch.setattr(sb, "upstream", lambda *a, **k: [])
    before = sorted(p.name for p in tmp_path.iterdir())
    sb.state(cheap=True)
    assert sorted(p.name for p in tmp_path.iterdir()) == before


# ------------------------------------------------------------------------- page


def test_the_switchboard_route_renders_and_carries_the_needs_you_count():
    import datetime

    from scripts import local_tracker as lt
    page = lt.render(datetime.datetime(2026, 9, 1, 12, 0), "switchboard")
    assert "SWITCHBOARD" in page and "NEEDS YOU" in page
    assert 'href="/switchboard"' in page, "the tab is unreachable from the nav"
    assert "Critical path" in page and "Sessions" in page and "Upstream" in page


def test_the_switchboard_does_not_pay_for_a_readiness_measure(monkeypatch):
    """⛔ `measure()` reaches `board.board()`, which did not return inside 120 s when timed on
    2026-09-01. A live command page that pays that per refresh is a page nobody opens — the exact
    failure control-room.md §3 records against this tracker at ~19 s."""
    import datetime

    from scripts import local_tracker as lt
    called = []
    monkeypatch.setattr(lt, "measure", lambda *a, **k: called.append(1) or [])
    lt.render(datetime.datetime(2026, 9, 1, 12, 0), "switchboard")
    assert not called, "the switchboard tab called measure()"


def test_a_tied_critical_path_head_is_reported_as_tied(tmp_path):
    """⛔ Printing one chain over a graph with parallel roots implies a linearity that is not there.

    A -> B and A -> C and C -> D gives ONE longest chain (A→C→D), so ties == 1. Add a second root
    feeding C and there are two, and the page must say so — the first version of this counter
    counted endpoints at maximum depth, returned 1 for the live mission's three parallel roots, and
    so reported no ambiguity in the one place the ambiguity lives.
    """
    store, man, ids = _mission(tmp_path)
    assert sb._chain_ties(sb._edges(store, list(ids.values()))) == 1

    e2 = store.create("E · a second root", actor="test", parent=man["mission_task"])
    man["labels"]["E"] = e2
    man["contracts"][e2] = {"label": "E", "resource_claim": "src", "access": "READ"}
    store.block(ids["C"], by=e2, actor="test")
    assert sb._chain_ties(sb._edges(store, list(man["labels"].values()))) == 2

