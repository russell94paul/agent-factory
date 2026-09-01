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
from factory import switchboard_render as sbr
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
    assert "nudge, not durable evidence" in got[0]["basis"], (
        "peer traffic rendered without the caveat that it is not evidence")
    # The text itself lives in the digest now — see the compaction tests below for why.
    dg = sb.upstream_digest(["me"])
    assert dg["total"] == 1 and "grain" in dg["events"][0]["text"]


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


# ==================================================================== SLICE B: start synced


def _st(tmp_path, monkeypatch, store, man, **over):
    monkeypatch.setattr(sb, "manifests", lambda: [dict(man, _id="m1", _mtime=0)])
    monkeypatch.setattr(sb, "store_path", lambda: store.path)
    monkeypatch.setattr(sb._sessions, "inventory", lambda: over.get("sessions", []))
    monkeypatch.setattr(sb._sessions, "blocked", lambda: over.get("blocked", []))
    monkeypatch.setattr(sb, "upstream", lambda *a, **k: over.get("upstream", []))
    monkeypatch.setattr(sb, "worktrees", lambda: over.get("worktrees", [
        {"path": "C:/repo", "branch": "main", "head": "aaaaaaa", "primary": True, "dirty": 0}]))
    return sb.state()


def test_the_startup_packet_derives_current_state_not_remembered_state(tmp_path, monkeypatch):
    """Every load-bearing value in the packet comes from the measurement taken at write time."""
    store, man, ids = _mission(tmp_path)
    store.claim(ids["C"], actor="agent-1")
    st = _st(tmp_path, monkeypatch, store, man)
    md, bnd, events = sb.startup_packet("C", st=st)

    assert ids["C"] in md, "the packet does not carry the task id it is about"
    assert "aaaaaaa" in md and "main" in md, "HEAD/branch missing — a session cannot verify itself"
    assert "shared" in md, "the declared resource claim is missing"
    assert "`A`" in md, "the dependency is not stated"
    assert "SESSION START" in md and "REGROUND REQUIRED" in md
    assert bnd["tasks"]["C"] == "claimed" and bnd["heads"]["main"] == "aaaaaaa"


def test_a_moved_state_boundary_produces_a_reground_not_a_shrug(tmp_path, monkeypatch):
    """⭐ The markdown is a rendered artefact; the boundary is the authority.

    A handoff written twenty minutes ago reads exactly as confidently as one written now. So a
    packet carries the boundary it was built at, and the difference is computed rather than felt.
    """
    store, man, ids = _mission(tmp_path)
    st = _st(tmp_path, monkeypatch, store, man)
    _md, bnd, _e = sb.startup_packet("C", st=st)
    assert sb.reground(bnd, st) == [], "an unchanged boundary reported drift"

    store.claim(ids["C"], actor="someone-else")
    moved = _st(tmp_path, monkeypatch, store, man, worktrees=[
        {"path": "C:/repo", "branch": "main", "head": "bbbbbbb", "primary": True, "dirty": 0}])
    out = sb.reground(bnd, moved)
    assert any("task C moved blocked -> claimed" in x for x in out), out
    assert any("main moved aaaaaaa -> bbbbbbb" in x for x in out), out


def test_reground_notices_a_worktree_that_disappeared(tmp_path, monkeypatch):
    store, man, ids = _mission(tmp_path)
    st = _st(tmp_path, monkeypatch, store, man)
    _md, bnd, _e = sb.startup_packet("C", st=st)
    gone = _st(tmp_path, monkeypatch, store, man, worktrees=[])
    assert any("no longer exists" in x for x in sb.reground(bnd, gone))


def test_the_reground_command_exits_nonzero_when_state_moved(tmp_path, monkeypatch, capsys):
    """The handshake tells a session to run this. An instrument that always exits 0 is not a gate."""
    store, man, ids = _mission(tmp_path)
    st = _st(tmp_path, monkeypatch, store, man)
    _md, bnd, _e = sb.startup_packet("C", st=st)
    b = tmp_path / "b.json"
    b.write_text(json.dumps(bnd), encoding="utf-8")

    assert sb.main(["--reground", str(b)]) == 0
    assert "READY" in capsys.readouterr().out

    store.claim(ids["C"], actor="x")
    _st(tmp_path, monkeypatch, store, man)
    assert sb.main(["--reground", str(b)]) == 1
    assert "REGROUND REQUIRED" in capsys.readouterr().out


def test_an_unreadable_boundary_is_a_reground_not_a_pass(tmp_path, monkeypatch):
    """A gate that cannot read its own input must fail closed. Exiting 0 on a missing boundary
    would let a session print READY having verified nothing."""
    assert sb.main(["--reground", str(tmp_path / "does-not-exist.json")]) == 1


def test_the_packet_carries_unread_traffic_without_marking_it_read(tmp_path, monkeypatch):
    """⛔ The cursor rule, at the packet boundary. `startup_packet` RETURNS the events instead of
    marking them, so 'never advance a cursor before delivery' is a property of the shape rather
    than a rule the caller has to remember."""
    monkeypatch.setattr(buslib, "ROOT", tmp_path / "bus")
    buslib.post("peer", "correction", "the grain moved")
    store, man, ids = _mission(tmp_path)
    st = _st(tmp_path, monkeypatch, store, man)

    md, _b, events = sb.startup_packet("C", reader="me", st=st)
    assert len(events) == 1 and "the grain moved" in md
    assert "nudge, not durable evidence" in md, "traffic rendered without its caveat"
    assert not buslib._cursor_path("me").exists(), "building a packet advanced the cursor"
    assert len(buslib.unread("me")) == 1


def test_the_cursor_advances_only_when_deliver_is_called(tmp_path, monkeypatch):
    monkeypatch.setattr(buslib, "ROOT", tmp_path / "bus")
    buslib.post("peer", "correction", "one")
    evs = buslib.unread("me")
    assert sb.deliver("me", []) is None, "an empty delivery advanced a cursor"
    assert sb.deliver("", evs) is None, "a delivery with no reader advanced a cursor"
    assert not buslib._cursor_path("me").exists()
    assert sb.deliver("me", evs)
    assert buslib.unread("me") == []


def test_a_dry_start_writes_the_packet_opens_nothing_and_marks_nothing(tmp_path, monkeypatch):
    """The dry-run lesson `start_research_pass` already paid for: `dry` is checked before the
    spawn, and a dry run that dispatched would be worse than none at all. Here it must also leave
    the bus cursor exactly where it was."""
    from scripts import local_tracker as lt
    monkeypatch.setattr(buslib, "ROOT", tmp_path / "bus")
    # ⚠ Point the packet directory at tmp. `.data/handoffs` is SHARED estate state that other live
    # sessions read; a test suite that drops probe files into it is mutating the thing it observes.
    monkeypatch.setattr(lt, "FACTORY", tmp_path)
    buslib.post("peer", "correction", "one")
    opened = []
    # ⚠ `lt._spawn`, NOT `subprocess.Popen`. Patching Popen module-wide also breaks
    # `subprocess.run`, which the projection uses for every git and process-table read — the
    # assertion then fails for a reason unrelated to what it asserts.
    monkeypatch.setattr(lt, "_spawn", lambda *a, **k: opened.append(a))

    ok, msg = lt.start_synced(target="", note="probe", reader="me", dry=True)
    assert ok, msg
    assert "DRY RUN" in msg
    written = sorted(p.name for p in (tmp_path / ".data" / "handoffs").iterdir())
    assert len(written) == 2, f"expected the packet and its boundary, got {written}"
    assert not opened, "a dry run opened a terminal"
    assert not buslib._cursor_path("me").exists(), "a dry run advanced a bus cursor"
    assert len(buslib.unread("me")) == 1


def test_the_gate_handoff_is_off_by_default(tmp_path, monkeypatch):
    """⛔ `handoff.session_handoff()` runs `readiness.measure()` — the path timed at 413.8 s for
    `board.board()` and 801.0 s for `session.brief()` on 2026-09-01. If it ever becomes the
    default, START SYNCED becomes a button nobody presses."""
    store, man, ids = _mission(tmp_path)
    st = _st(tmp_path, monkeypatch, store, man)
    called = []

    import factory.handoff as h
    monkeypatch.setattr(h, "session_handoff", lambda note="": called.append(1) or "SLOW")
    md, _b, _e = sb.startup_packet("C", st=st)
    assert not called, "the default packet ran the readiness measure"
    md2, _b2, _e2 = sb.startup_packet("C", st=st, include_gate_handoff=True)
    assert called and "SLOW" in md2, "the opt-in did not reach handoff.session_handoff"


# --------------------------------------------------------------- resume safety


def _cards(monkeypatch, *rows):
    from scripts import local_tracker as lt
    monkeypatch.setattr(lt.sblib, "session_cards", lambda *a, **k: list(rows))
    return lt


def test_direct_resume_cannot_create_a_second_process_on_a_live_session(monkeypatch):
    """⛔ The divergent-duplicate failure, refused at the action rather than hidden in the page.

    The rendered page is NOT the authority: a page rendered thirty seconds ago can still be
    offering RESUME for a session that has since been reattached. So liveness is re-measured inside
    the action, and a live session is refused there.
    """
    lt = _cards(monkeypatch, sb.session_cards([_session(
        session_id="abc123", state=sesslib.RUNNING_ATTACHED)])[0])
    opened = []
    monkeypatch.setattr(lt, "_spawn", lambda *a, **k: opened.append(a))
    ok, msg = lt.resume_session("abc123")
    assert not ok and not opened, "a live session was resumed — two processes, one transcript"
    assert "RUNNING-ATTACHED" in msg and "second process" in msg


def test_direct_resume_refuses_an_orphaned_session_too(monkeypatch):
    lt = _cards(monkeypatch, sb.session_cards([_session(
        session_id="abc123", state=sesslib.RUNNING_ORPHANED, kind="bg")])[0])
    opened = []
    monkeypatch.setattr(lt, "_spawn", lambda *a, **k: opened.append(a))
    ok, msg = lt.resume_session("abc123")
    assert not ok and not opened and "Attach to it instead" in msg


def test_direct_resume_refuses_when_liveness_is_unknown(monkeypatch):
    """UNKNOWN is not EXITED. Resuming on an unread process table claims a measurement nobody made."""
    lt = _cards(monkeypatch, sb.session_cards([_session(
        session_id="abc123", state=sesslib.UNKNOWN)])[0])
    opened = []
    monkeypatch.setattr(lt, "_spawn", lambda *a, **k: opened.append(a))
    ok, msg = lt.resume_session("abc123")
    assert not ok and not opened and "not established" in msg


def test_a_stale_resume_link_for_a_vanished_session_is_refused(monkeypatch):
    lt = _cards(monkeypatch)
    opened = []
    monkeypatch.setattr(lt, "_spawn", lambda *a, **k: opened.append(a))
    ok, msg = lt.resume_session("gone9999")
    assert not ok and not opened and "the page was stale" in msg


def test_an_exited_resumable_session_is_actually_resumable(monkeypatch):
    """The control has to work, or the refusals above are just a broken button."""
    lt = _cards(monkeypatch, sb.session_cards([_session(
        session_id="abc123", state=sesslib.EXITED_RESUMABLE, cwd="C:/repo")])[0])
    ok, msg = lt.resume_session("abc123", dry=True)
    assert ok and "DRY RUN" in msg and "abc123" in msg


def test_the_start_synced_control_is_on_the_page():
    import datetime

    from scripts import local_tracker as lt
    page = lt.render(datetime.datetime(2026, 9, 1, 12, 0), "switchboard")
    assert 'action="/switchboard/start"' in page
    assert "START SYNCED" in page and "PACKET ONLY" in page
    for field in ('name="target"', 'name="worktree"', 'name="reader"', 'name="note"'):
        assert field in page, f"the dispatch form is missing {field}"
    assert "413.8" in page, "the slow opt-in does not state its measured cost"


# ============================================================ the upstream digest (compaction)


def test_the_digest_renders_one_event_once_no_matter_how_many_readers_are_behind(monkeypatch, tmp_path):
    """⛔ The defect that made the Upstream panel 211,485 bytes on 2026-09-01.

    The bus is ONE channel that several readers have not caught up on. Rendering per reader
    duplicated every message once per reader — sixteen copies of a message is not sixteen
    messages. The digest deduplicates and records who is behind instead.
    """
    monkeypatch.setattr(buslib, "ROOT", tmp_path)
    buslib.post("peer", "correction", "the grain moved")
    readers = [f"r{i}" for i in range(16)]

    per_reader = sb.upstream(readers)
    assert len(per_reader) == 16, "every behind reader should still be counted"
    assert all("rendered" not in r for r in per_reader), (
        "upstream() is carrying message text again — that is the 211 KB panel returning")

    dg = sb.upstream_digest(readers)
    assert dg["total"] == 1, f"one post rendered as {dg['total']} events"
    assert dg["events"][0]["text"] == "the grain moved"
    assert len(dg["events"][0]["unread_by"]) == 16


def test_the_digest_truncates_a_long_message_and_says_by_how_much(monkeypatch, tmp_path):
    """The bus caps a message at 2000 chars, which is right for delivery into a session and much
    too generous for a command page. Truncation must be visible, never silent."""
    monkeypatch.setattr(buslib, "ROOT", tmp_path)
    buslib.post("peer", "note", "x" * 1500)
    e = sb.upstream_digest(["me"])["events"][0]
    assert len(e["text"]) == sb.DIGEST_CHARS
    assert e["clipped"] == 1500 - sb.DIGEST_CHARS
    page = sbr._upstream({"upstream": sb.upstream(["me"]),
                          "upstream_digest": sb.upstream_digest(["me"])})
    assert "more chars" in page, "the panel truncated without saying so"


def test_the_digest_still_advances_no_cursor(monkeypatch, tmp_path):
    monkeypatch.setattr(buslib, "ROOT", tmp_path)
    buslib.post("peer", "correction", "one")
    sb.upstream_digest(["me"])
    sb.upstream_digest(["me"])
    assert not buslib._cursor_path("me").exists()
    assert len(buslib.unread("me")) == 1


# ==================================================================== SLICE C: quick dispatch


def _live(sid, state_, topic, cwd="C:/repo", **kw):
    return sb.session_cards([_session(session_id=sid, state=state_, topic=topic, cwd=cwd, **kw)])[0]


def _plan(prompt, cards, target=""):
    return sb.dispatch_plan(prompt, target_session_id=target,
                            st={"sessions": cards, "tasks": []})


# ---------------------------------------------------------------- deterministic routing


def test_an_explicit_header_routes_deterministically():
    """No LLM router. The header either matches a declared alias as a whole phrase, or it does not."""
    cards = [_live("s1", sesslib.RUNNING_ATTACHED, "# MAIN T — resume the mission")]
    p = _plan("# MAIN T\nplease continue at D5", cards)
    assert p["header"] == "MAIN T" and p["decision"] == "READY"
    assert p["chosen"]["session_id"] == "s1"


def test_every_declared_header_is_recognised():
    for hdr, aliases in sb.TARGET_ALIASES.items():
        for a in aliases:
            got = sb.header_of(f"# {a}\nbody")
            assert got["header"] == hdr, f"{a!r} did not route to {hdr}"


def test_a_header_is_not_matched_inside_a_longer_word():
    """`maint` must not fire inside `maintenance`, or a maintenance note dispatches to MAIN T."""
    assert sb.header_of("# maintenance window tonight")["header"] is None
    assert sb.header_of("# switchboarding is not a word")["header"] is None


def test_a_header_only_counts_in_the_first_lines():
    """A prompt that MENTIONS client review in its body is not addressed to it. Treating a mention
    as an address is the wrong-session dispatch this slice exists to stop."""
    body = "# some other thing\n" + ("filler\n" * 20) + "later we should tell CLIENT REVIEW\n"
    assert sb.header_of(body)["header"] is None


def test_two_headers_is_a_refusal_not_a_tie_to_break():
    cards = [_live("s1", sesslib.RUNNING_ATTACHED, "# MAIN T"),
             _live("s2", sesslib.RUNNING_ATTACHED, "# CLIENT REVIEW")]
    p = _plan("# MAIN T and CLIENT REVIEW\nboth of you", cards)
    assert p["decision"] == "REQUIRE_SELECTION"
    assert p["chosen"] is None and "two addresses" in p["why"]


def test_no_header_requires_an_explicit_target():
    p = _plan("just some text with no header", [_live("s1", sesslib.RUNNING_ATTACHED, "# MAIN T")])
    assert p["decision"] == "REQUIRE_SELECTION" and p["chosen"] is None


def test_a_header_matching_two_sessions_refuses_rather_than_guessing():
    """⭐ The measured problem this guards: 5 of 12 live sessions once shared one name. A router
    that picks the first of two identically-named sessions is a coin toss with a confident UI."""
    cards = [_live("s1", sesslib.RUNNING_ATTACHED, "# MAIN T one"),
             _live("s2", sesslib.RUNNING_ATTACHED, "# MAIN T two")]
    p = _plan("# MAIN T\ngo", cards)
    assert p["decision"] == "REQUIRE_SELECTION"
    assert "more than one session" in p["why"] and len(p["candidates"]) == 2


def test_an_explicit_target_overrides_the_header_entirely():
    """The operator is the authority. A chosen target is used even when the header says otherwise —
    and it is the header that is advisory, not the choice."""
    cards = [_live("s1", sesslib.RUNNING_ATTACHED, "# MAIN T"),
             _live("s2", sesslib.EXITED_GONE, "# CLIENT REVIEW")]
    p = _plan("# MAIN T\ngo", cards, target="s2")
    assert p["chosen"]["session_id"] == "s2" and p["decision"] == "READY"


def test_an_empty_prompt_is_never_dispatchable():
    p = _plan("   \n  ", [_live("s1", sesslib.RUNNING_ATTACHED, "# MAIN T")])
    assert p["decision"] == "REQUIRE_SELECTION" and "no prompt" in p["why"]


def test_the_alias_table_cannot_be_ambiguous():
    """Two headers claiming one alias would make routing non-deterministic while still looking
    declarative — worse than no table. Guarded at import."""
    import importlib
    bad = dict(sb.TARGET_ALIASES, DECOY=("main t",))
    orig = sb.TARGET_ALIASES
    try:
        sb.TARGET_ALIASES = bad
        with pytest.raises(ImportError):
            sb._validate_aliases()
    finally:
        sb.TARGET_ALIASES = orig
    sb._validate_aliases()
    importlib.reload  # noqa: B018  - referenced so the intent is obvious


# ------------------------------------------------------------------ the route matrix


def test_send_is_offered_only_where_the_channel_is_owned():
    """⛔ SEND appears for a session that does not exist yet, and for nothing else.

    Measured 2026-09-01: all 8 live claude.exe processes report MainWindowHandle 0, so a running
    session's terminal tab cannot be raised from here; and the per-session `messagingSocketPath`
    named pipe has no reader or writer anywhere in this estate and an unverified protocol. What IS
    proven is the channel every lane already launches on: a session we spawn takes its prompt as an
    argument.
    """
    assert sb.route_for(sesslib.EXITED_GONE)[0] == sb.SEND
    assert sb.route_for(None)[0] == sb.SEND
    for st_ in (sesslib.RUNNING_ATTACHED, sesslib.RUNNING_ORPHANED, sesslib.EXITED_RESUMABLE):
        assert sb.route_for(st_)[0] != sb.SEND, f"{st_} was offered a direct SEND"


def test_an_unknown_liveness_target_is_refused_outright():
    assert sb.route_for(sesslib.UNKNOWN)[0] == sb.REFUSE
    cards = [_live("s1", sesslib.UNKNOWN, "# MAIN T")]
    p = _plan("# MAIN T\ngo", cards)
    assert p["decision"] == "REFUSE"


def test_an_orphaned_target_is_pointed_at_the_attach_path_not_a_spawn():
    route, why = sb.route_for(sesslib.RUNNING_ORPHANED)
    assert route == sb.COPY_OPEN
    assert "attach" in why and "never started here" in why


# ----------------------------------------------------------- the action refuses safely


def test_dispatch_refuses_without_resolving_and_spawns_nothing(monkeypatch):
    from scripts import local_tracker as lt
    opened = []
    monkeypatch.setattr(lt, "_spawn", lambda *a, **k: opened.append(a))
    ok, msg = lt.quick_dispatch("no header anywhere in this prompt")
    assert not ok and not opened and "REQUIRE_SELECTION" in msg


def test_dispatch_to_a_live_session_starts_no_second_process(monkeypatch, tmp_path):
    """⛔ The core P0 safety property: a live externally controlled session is never duplicated."""
    from scripts import local_tracker as lt
    monkeypatch.setattr(lt, "FACTORY", tmp_path)
    card = _live("s1", sesslib.RUNNING_ATTACHED, "# MAIN T mission", cwd=str(tmp_path))
    monkeypatch.setattr(lt.sblib, "state",
                        lambda *a, **k: {"sessions": [card], "tasks": []})
    opened = []
    monkeypatch.setattr(lt, "_spawn", lambda *a, **k: opened.append(a))

    ok, msg = lt.quick_dispatch("# MAIN T\ndo the thing")
    assert ok, msg
    assert not opened, "a live session was dispatched to by starting a second process"
    assert "COPY+OPEN" in msg and "No second process was started" in msg
    assert "MainWindowHandle 0" in msg, "the reason it cannot open the tab is not stated"
    saved = list((tmp_path / ".data" / "dispatch").iterdir())
    assert len(saved) == 1 and saved[0].read_text(encoding="utf-8").startswith("# MAIN T")


def test_dispatch_to_a_dead_target_sends_by_spawning_one_session(monkeypatch, tmp_path):
    from scripts import local_tracker as lt
    monkeypatch.setattr(lt, "FACTORY", tmp_path)
    card = _live("s1", sesslib.EXITED_GONE, "# CLIENT REVIEW", cwd=str(tmp_path))
    monkeypatch.setattr(lt.sblib, "state", lambda *a, **k: {"sessions": [card], "tasks": []})
    opened = []
    monkeypatch.setattr(lt, "_spawn", lambda *a, **k: opened.append(a))

    ok, msg = lt.quick_dispatch("# CLIENT REVIEW\nrefresh please")
    assert ok and "SENT" in msg
    assert len(opened) == 1, "SEND did not open exactly one session"


def test_a_dry_dispatch_resolves_the_target_and_opens_nothing(monkeypatch, tmp_path):
    from scripts import local_tracker as lt
    monkeypatch.setattr(lt, "FACTORY", tmp_path)
    card = _live("s1", sesslib.EXITED_GONE, "# CLIENT REVIEW", cwd=str(tmp_path))
    monkeypatch.setattr(lt.sblib, "state", lambda *a, **k: {"sessions": [card], "tasks": []})
    opened = []
    monkeypatch.setattr(lt, "_spawn", lambda *a, **k: opened.append(a))
    ok, msg = lt.quick_dispatch("# CLIENT REVIEW\ngo", dry=True)
    assert ok and "DRY RUN" in msg and not opened


def test_dispatching_to_an_unknown_liveness_target_opens_nothing(monkeypatch, tmp_path):
    from scripts import local_tracker as lt
    monkeypatch.setattr(lt, "FACTORY", tmp_path)
    card = _live("s1", sesslib.UNKNOWN, "# MAIN T", cwd=str(tmp_path))
    monkeypatch.setattr(lt.sblib, "state", lambda *a, **k: {"sessions": [card], "tasks": []})
    opened = []
    monkeypatch.setattr(lt, "_spawn", lambda *a, **k: opened.append(a))
    ok, msg = lt.quick_dispatch("# MAIN T\ngo")
    assert not ok and not opened and "REFUSE" in msg


def test_the_dispatch_panel_shows_identity_before_the_act():
    """SECURITY: target, state, worktree/cwd and session id must be visible beside the button."""
    card = _live("s1", sesslib.RUNNING_ATTACHED, "# MAIN T mission", cwd="C:/repo/wt")
    plan = _plan("# MAIN T\ngo", [card])
    html = sbr._plan_readout(plan)
    for needle in ("TARGET", "RUNNING-ATTACHED", "C:/repo/wt", "s1", "COPY+OPEN"):
        assert needle in html, f"the pre-dispatch identity block is missing {needle!r}"


def test_the_dispatch_control_is_on_the_page():
    import datetime

    from scripts import local_tracker as lt
    page = lt.render(datetime.datetime(2026, 9, 1, 12, 0), "switchboard")
    assert 'action="/switchboard/dispatch"' in page
    assert "COPY + DISPATCH" in page and "PREVIEW (resolve only)" in page
    assert 'id="qd-prompt"' in page
    for hdr in sb.TARGET_ALIASES:
        assert hdr in page, f"the recognised header {hdr} is not advertised to the operator"
