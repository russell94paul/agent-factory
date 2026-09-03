"""Autonomy planner acceptance — the refusals are the product.

⭐ **This file exists to make the pump's refusals falsifiable.** A planner that starts everything
looks identical to a correct one on a store where everything happens to be eligible. So almost
every test here builds work that *is* startable, then adds exactly one condition, and asserts the
START becomes a refusal. Where a rule could be satisfied vacuously, its negative control sits
directly beside it.

⛔ The planner is PURE by contract, and one test asserts that structurally: it must not be able
to reach the start mechanism at all. A planner that can spawn is a planner whose refusals cannot
be tested without spawning.

The store is a `tmp_path` file and `runs_dir` is redirected in every test. Nothing here touches
the live `.data/tasks.jsonl` or `.data/runs/`.
"""
from __future__ import annotations

import pytest

from factory import autonomy as A
from factory import tasks as T
from factory import work as W
from factory.tasks import TaskStore

MISSION = "M1"


@pytest.fixture()
def store(tmp_path) -> TaskStore:
    return TaskStore(tmp_path / "tasks.jsonl")


@pytest.fixture(autouse=True)
def _isolate_runs(tmp_path, monkeypatch):
    """Mandates are shared state under `.data/runs`; a test must never write the real one."""
    monkeypatch.setattr(A, "runs_dir", lambda: tmp_path / "runs")


def _mission(store) -> None:
    store.create(title="mission", tid=MISSION, actor="t", contract={"kind": "mission"})


def _stage(store, wid, *, deps=(), autonomy=T.GUARDED, claim=None, access="READ",
           repo="agent-factory", visibility=T.PRIVATE, contract=None, parent=MISSION):
    c = {"resource_claim": claim if claim is not None else f"res-{wid.lower()}",
         "access": access}
    c.update(contract or {})
    store.create(title=wid, tid=wid, actor="t", parent=parent, repo=repo,
                 visibility=visibility, contract=c)
    for d in deps:
        store.depend(wid, d, actor="t")
    if autonomy != T.DEFAULT_AUTONOMY:
        store.set_autonomy(wid, autonomy, actor="t")
    return wid


def _done(store, wid: str) -> None:
    """Close as DONE the way the store insists on — with real evidence.

    ⛔ `TaskStore.close` refuses a DONE with no MEASURED or DERIVED evidence attached, so a test
    helper that bypassed it would be exercising a lifecycle the product does not have.
    """
    store.add_evidence(wid, kind="test", ref=f"{wid}.md", actor="t", basis="MEASURED")
    store.close(wid, actor="t", status=T.DONE)


def _rows(store):
    return {w.id: w for w in W.project(store=store)}


def _mandate(**kw) -> A.Mandate:
    kw.setdefault("run_id", "run-1")
    kw.setdefault("mission", MISSION)
    kw.setdefault("mode", T.GUARDED)
    return A.Mandate(**kw)


# ============================================================ 1. the planner is pure

def _code(mod) -> "ast.Module":
    """The module's CODE, with every docstring and comment gone.

    ⚠ Written this way after the first version of these two tests failed against the module's own
    docstring — which *names* the banned constructs in order to say it does not use them. A scan
    that a prose warning can trip is not measuring the code, and the fix is not to soften the
    prose: an assertion satisfiable by editing a comment is not a guard.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(mod))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body.pop(0)
    return tree


def _names(tree) -> set:
    """Every dotted name the code actually references."""
    import ast

    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
        elif isinstance(n, ast.alias):
            out.add(n.name.split(".")[0])
            out.add(n.name)
    return out


def test_the_planner_cannot_reach_the_start_mechanism():
    """⛔ Structural. If this fails, the refusals below can no longer be tested in isolation."""
    refs = _names(_code(A))
    for banned in ("local_tracker", "start_synced", "subprocess", "Popen", "spawn"):
        assert banned not in refs, (
            f"the planner references {banned!r} — it must decide, and the pump must act, or a "
            f"refusal cannot be tested without spawning a real session")


def test_the_planner_contains_no_timer_or_loop():
    """⛔ The brief forbids uncontrolled recursive autonomous execution."""
    import ast

    tree = _code(A)
    refs = _names(tree)
    for banned in ("Timer", "scheduler", "Thread", "sched", "threading"):
        assert banned not in refs, f"an autonomous execution mechanism appeared: {banned}"
    for n in ast.walk(tree):
        if isinstance(n, ast.While):
            assert not (isinstance(n.test, ast.Constant) and n.test.value is True), (
                f"a `while True` loop appeared at line {n.lineno}")


def test_planning_writes_nothing_to_the_store(store):
    _mission(store)
    _stage(store, "S1")
    before = len(store.all())
    A.plan(_mandate(), _rows(store))
    assert len(TaskStore(store.path).all()) == before


# ============================================================ 2. the happy path exists

def test_a_ready_guarded_stage_is_STARTed(store):
    """The positive control. Without this the refusals below could all be vacuous."""
    _mission(store)
    _stage(store, "S1")
    p = A.plan(_mandate(), _rows(store))
    assert p.starts == ["S1"], A.report(_mandate(), p)


def test_every_decision_carries_a_reason(store):
    _mission(store)
    _stage(store, "S1")
    _stage(store, "S2", deps=["S1"])
    p = A.plan(_mandate(), _rows(store))
    assert p.decisions
    for d in p.decisions:
        assert d.verdict in A.VERDICTS
        assert d.reason.strip(), f"{d.work_id} got a verdict with no reason"


# ============================================================ 3. guarded_start is never bypassed

def test_MANUAL_work_never_starts_under_any_run_mode(store):
    """⛔ Required behaviour: MANUAL never auto-starts."""
    _mission(store)
    _stage(store, "S1", autonomy=T.MANUAL)
    for mode in (T.GUARDED, T.AUTO):
        p = A.plan(_mandate(mode=mode), _rows(store))
        assert p.starts == [], f"MANUAL work started under run mode {mode}"


def test_AUTO_run_mode_does_not_bypass_guarded_start(store):
    """⭐ The deliberate deviation from the pack, asserted.

    The pack specified `AUTO: require_guarded_start_allowed: false`. If that were implemented,
    this publication-boundary refusal would evaporate under AUTO — which is precisely the failure
    the deviation exists to prevent.
    """
    _mission(store)
    _stage(store, "S1", autonomy=T.AUTO, visibility=T.PUBLIC)
    allowed, why = W.guarded_start(_rows(store)["S1"])
    assert not allowed and any("publication boundary" in r for r in why)
    p = A.plan(_mandate(mode=T.AUTO), _rows(store))
    assert p.starts == []
    assert p.by_verdict(A.HUMAN_GATE), "a publication-boundary stop must read as a human gate"


def test_an_unmeasured_condition_is_a_stop_not_a_pass(store):
    """No resource claim -> `contract UNMEASURED` -> DRAFT, never READY."""
    _mission(store)
    _stage(store, "S1", claim="")
    assert _rows(store)["S1"].state == W.DRAFT
    p = A.plan(_mandate(), _rows(store))
    assert p.starts == []
    assert p.by_verdict(A.BLOCKED)[0].verdict == A.BLOCKED


def test_a_declared_human_gate_contract_is_never_started(store):
    _mission(store)
    _stage(store, "S1", autonomy=T.AUTO, contract={"requires_approval": "SIGNOFF"})
    p = A.plan(_mandate(mode=T.AUTO), _rows(store))
    assert p.starts == []
    assert p.by_verdict(A.HUMAN_GATE)


def test_a_declared_resource_conflict_is_never_started(store):
    """Live or not — `guarded_start` refuses on the declaration itself."""
    _mission(store)
    _stage(store, "S1", claim="res-shared", access="WRITE")
    _stage(store, "S2", claim="res-shared", access="READ")
    p = A.plan(_mandate(), _rows(store))
    assert p.starts == []


def test_paused_work_outranks_its_own_policy(store):
    _mission(store)
    _stage(store, "S1", autonomy=T.AUTO)
    store.pause_autonomy("S1", True, actor="operator")
    p = A.plan(_mandate(mode=T.AUTO), _rows(store))
    assert p.starts == []


# ============================================================ 4. dependencies and gates

def test_downstream_does_not_start_while_its_dependency_is_open(store):
    _mission(store)
    _stage(store, "S1")
    _stage(store, "S2", deps=["S1"])
    p = A.plan(_mandate(), _rows(store))
    assert p.starts == ["S1"]
    assert [d.verdict for d in p.decisions if d.work_id == "S2"] == [A.BLOCKED]


def test_an_explicit_hold_reads_as_a_human_gate_not_a_block(store):
    """A hold on a PERSON is an inbox item; a hold on a task is a queue item. Different acts."""
    _mission(store)
    _stage(store, "S1", autonomy=T.MANUAL)
    store.block("S1", by="AWAITING-SIGNOFF", actor="t")
    p = A.plan(_mandate(), _rows(store))
    d = next(d for d in p.decisions if d.work_id == "S1")
    assert d.verdict == A.HUMAN_GATE
    assert "AWAITING-SIGNOFF" in d.reason


def test_releasing_the_hold_makes_downstream_startable(store):
    """⭐ Gate 5 in miniature: APPROVE is an event, not a second manual launch."""
    _mission(store)
    _stage(store, "S1")
    _stage(store, "GATE", deps=["S1"], autonomy=T.MANUAL)
    store.block("GATE", by="AWAITING-SIGNOFF", actor="t")
    _stage(store, "S3", deps=["GATE"])

    _done(store, "S1")
    assert A.plan(_mandate(), _rows(store)).starts == [], "downstream started through a held gate"

    store.unblock("GATE", by="AWAITING-SIGNOFF", actor="operator")
    _done(store, "GATE")
    assert A.plan(_mandate(), _rows(store)).starts == ["S3"]


# ============================================================ 5. concurrency

def test_concurrency_is_enforced_across_the_batch(store):
    _mission(store)
    for i in range(5):
        _stage(store, f"S{i}")
    p = A.plan(_mandate(max_parallel=2), _rows(store))
    assert len(p.starts) == 2
    assert any("concurrency limit" in d.reason for d in p.by_verdict(A.WAIT))


def test_concurrency_counts_work_already_running_anywhere(store):
    """A start opens a real terminal, so two runs cannot each have their own allowance."""
    _mission(store)
    _stage(store, "S1")
    _stage(store, "S2")
    p = A.plan(_mandate(max_parallel=2), _rows(store), running=2)
    assert p.starts == []
    assert p.capacity == 0


def test_two_writers_of_one_claim_do_not_start_in_the_same_batch(store):
    """`guarded_start` catches a DECLARED conflict; this catches a same-batch collision."""
    _mission(store)
    _stage(store, "S1", claim="res-a", access="WRITE")
    rows = _rows(store)
    # Force the batch case: two rows that each look isolated to `_conflicts` but collide on start.
    rows["S2"] = W.Work(id="S2", title="S2", repo="agent-factory", parent=MISSION,
                        autonomy=T.GUARDED, visibility=T.PRIVATE,
                        contract={"resource_claim": "res-a", "access": "WRITE"})
    rows["S2"].state = W.READY
    rows["S2"].checks = []
    p = A.plan(_mandate(max_parallel=5), rows)
    assert len(p.starts) == 1, "two writers of res-a were started together"
    assert any("same batch" in d.reason for d in p.by_verdict(A.WAIT))


# ============================================================ 6. pause and plan-only mode

def test_a_paused_run_starts_nothing(store):
    _mission(store)
    _stage(store, "S1")
    p = A.plan(_mandate(paused=True), _rows(store))
    assert p.starts == []
    assert p.by_verdict(A.PAUSED)


def test_MANUAL_run_mode_plans_but_starts_nothing(store):
    _mission(store)
    _stage(store, "S1")
    p = A.plan(_mandate(mode=T.MANUAL), _rows(store))
    assert p.starts == []
    assert "plan-only" in p.note


# ============================================================ 7. selection

def test_DAG_mode_selects_only_the_run(store):
    _mission(store)
    _stage(store, "S1")
    _stage(store, "OTHER", parent=None)
    p = A.plan(_mandate(run_mode=A.DAG), _rows(store))
    assert p.starts == ["S1"], "work outside the mission was started"


def test_the_mission_container_row_is_never_started(store):
    _mission(store)
    _stage(store, "S1")
    p = A.plan(_mandate(), _rows(store))
    assert MISSION not in p.starts
    assert all(d.work_id != MISSION for d in p.decisions)


def test_CRITICAL_PATH_selects_only_ancestors_of_the_target(store):
    _mission(store)
    _stage(store, "A1")
    _stage(store, "A2", deps=["A1"])
    _stage(store, "SIDE")                       # in the run, but not on the path to A2
    p = A.plan(_mandate(run_mode=A.CRITICAL_PATH, target="A2"), _rows(store))
    ids = {d.work_id for d in p.decisions}
    assert "SIDE" not in ids, "unrelated work was selected by RUN CRITICAL PATH"
    assert p.starts == ["A1"]


def test_CRITICAL_PATH_does_not_delete_or_alter_unselected_work(store):
    """Deprioritise, never drop. Automatic scope degradation is deliberately absent."""
    _mission(store)
    _stage(store, "A1")
    _stage(store, "SIDE")
    before = TaskStore(store.path).get("SIDE").to_dict()
    A.plan(_mandate(run_mode=A.CRITICAL_PATH, target="A1"), _rows(store))
    assert TaskStore(store.path).get("SIDE").to_dict() == before


def test_ancestors_tolerates_an_unknown_target(store):
    _mission(store)
    _stage(store, "S1")
    rows = _rows(store)
    assert A.ancestors("NOPE", rows) == set()
    p = A.plan(_mandate(run_mode=A.CRITICAL_PATH, target="NOPE"), rows)
    assert p.starts == [] and "not in the store" in p.note


def test_ancestors_walks_the_whole_chain(store):
    _mission(store)
    _stage(store, "A1")
    _stage(store, "A2", deps=["A1"])
    _stage(store, "A3", deps=["A2"])
    assert A.ancestors("A3", _rows(store)) == {"A1", "A2"}


# ============================================================ 8. no automatic retry

def test_a_recorded_start_failure_is_not_retried(store):
    """⛔ A failed start leaves the work READY, so without this the pump retries forever."""
    _mission(store)
    _stage(store, "S1")
    m = _mandate(failed={"S1": "no terminal opened"})
    p = A.plan(m, _rows(store))
    assert p.starts == []
    assert any("not retried automatically" in d.reason for d in p.by_verdict(A.WAIT))


def test_clearing_a_failure_is_a_deliberate_act(store, tmp_path):
    _mission(store)
    _stage(store, "S1")
    m = _mandate(failed={"S1": "no terminal opened"})
    m.save()
    assert A.main(["clear-failure", "--run", "run-1", "--work", "S1"]) == 0
    assert A.load_mandate("run-1").failed == {}
    assert A.main(["clear-failure", "--run", "run-1", "--work", "S1"]) == 2


# ============================================================ 9. the mandate

def test_the_mandate_round_trips(store):
    m = _mandate(target="S1", deadline="2026-09-02T12:00:00-07:00", max_parallel=2)
    m.save()
    back = A.load_mandate("run-1")
    assert back.target == "S1" and back.max_parallel == 2
    assert back.deadline == "2026-09-02T12:00:00-07:00"


def test_the_deadline_is_scheduling_context_only(store):
    """⭐ A deadline changes urgency; it must not change eligibility or what PASS means."""
    _mission(store)
    _stage(store, "S1")
    rows = _rows(store)
    overdue = A.plan(_mandate(deadline="2020-01-01T00:00:00+00:00"), rows)
    none_at_all = A.plan(_mandate(), rows)
    assert overdue.starts == none_at_all.starts
    assert [d.verdict for d in overdue.decisions] == [d.verdict for d in none_at_all.decisions]


def test_an_overdue_deadline_is_reported_not_acted_on(store):
    m = _mandate(deadline="2020-01-01T00:00:00+00:00")
    assert m.remaining().total_seconds() < 0
    txt = A.report(m, A.plan(m, {}))
    assert "OVERDUE" in txt
    assert "does not change what PASS means" in txt


def test_an_unparseable_deadline_does_not_crash_the_planner(store):
    m = _mandate(deadline="tomorrow-ish")
    assert m.deadline_at is None and m.remaining() is None
    assert "unparseable" in A.report(m, A.plan(m, {}))


def test_active_excludes_paused_and_plan_only_runs(store):
    A.Mandate(run_id="a", mission=MISSION, mode=T.GUARDED).save()
    A.Mandate(run_id="b", mission=MISSION, mode=T.GUARDED, paused=True).save()
    A.Mandate(run_id="c", mission=MISSION, mode=T.MANUAL).save()
    assert {m.run_id for m in A.active()} == {"a"}


def test_an_unknown_run_is_refused_by_the_cli(store, capsys):
    assert A.main(["plan", "--run", "nope"]) == 2


def test_pause_and_resume_persist(store):
    _mandate().save()
    assert A.main(["pause", "--run", "run-1"]) == 0
    assert A.load_mandate("run-1").paused is True
    assert A.main(["resume", "--run", "run-1"]) == 0
    assert A.load_mandate("run-1").paused is False
