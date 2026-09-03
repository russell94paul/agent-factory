"""Mission preset acceptance — a preset must compile to work that can actually START.

⭐ **The negative controls are the point of this file.** A preset that compiles cleanly and
produces work nobody can start looks *identical* on the page to one that works: the rows exist,
the DAG renders, the mission appears. The failure only shows up as "the pump started nothing",
which reads as the pump being broken.

Both traps below were MEASURED on the live checkout on 2026-09-02, not reasoned about:

  - 54 of 91 live rows sit in DRAFT because they declare no `repo` and no `resource_claim`.
    `work._state_for` makes an UNMEASURED check DRAFT, deliberately and permanently.
  - `work.guarded_start` refuses on a **declared** resource conflict whether or not the other
    side is live, so two stages sharing one WRITE claim are both permanently ineligible.

So each is paired with a fixture that MUST be refused, and the assertion is on the refusal.

The store is a `tmp_path` file in every test. Nothing here touches the live `.data/tasks.jsonl`.
"""
from __future__ import annotations

import pytest

from factory import missions as M
from factory import tasks as T
from factory import work as W
from factory.tasks import TaskStore

yaml = pytest.importorskip("yaml")


@pytest.fixture()
def store(tmp_path) -> TaskStore:
    return TaskStore(tmp_path / "tasks.jsonl")


def _preset(tmp_path, monkeypatch, body: dict, pid: str = "fixture-v1") -> M.Preset:
    d = tmp_path / "presets"
    d.mkdir(exist_ok=True)
    (d / f"{pid}.yaml").write_text(yaml.safe_dump(body, sort_keys=False), encoding="utf-8")
    monkeypatch.setattr(M, "PRESETS_DIR", d)
    return M.load(pid)


def _ok_body(**over) -> dict:
    body = {
        "version": 1,
        "id": "fixture-v1",
        "title": "Fixture",
        "repo": "agent-factory",
        "target": "S2",
        "stages": [
            {"id": "S1", "title": "one", "kind": "deterministic", "autonomy": "GUARDED",
             "resource_claim": "res-one", "access": "READ"},
            {"id": "S2", "title": "two", "kind": "deterministic", "autonomy": "GUARDED",
             "resource_claim": "res-two", "access": "WRITE", "depends_on": ["S1"]},
        ],
    }
    body.update(over)
    return body


# ============================================================ 1. the shipped preset

def test_the_shipped_marketing_preset_loads_and_validates():
    """If this fails, `--create` would refuse and the whole run is unavailable."""
    p = M.load("marketing-meeting-v1")
    assert p.stages, "the preset compiled to no stages"
    assert M.validate(p) == []
    assert p.target in {s.id for s in p.stages}


def test_the_shipped_preset_has_a_human_gate_before_the_client_artifact():
    """The artifact is client-facing; a regeneration must not be reachable without a decision."""
    p = M.load("marketing-meeting-v1")
    art = next(s for s in p.stages if s.access == "WRITE")
    gates = {s.id for s in p.stages if s.kind == M.HUMAN_GATE}
    assert gates & set(art.depends_on), (
        f"{art.id} writes the client artifact but no human gate is upstream of it")


def test_every_shipped_stage_declares_both_fields_that_gate_readiness():
    p = M.load("marketing-meeting-v1")
    for s in p.stages:
        assert s.repo, f"{s.id} declares no repo — it could never leave DRAFT"
        assert s.resource_claim, f"{s.id} declares no resource_claim — it could never leave DRAFT"


# ============================================================ 2. F-2: the DRAFT trap

def test_a_created_stage_reaches_READY_rather_than_DRAFT(tmp_path, monkeypatch, store):
    """⭐ The whole point of the preset. A stage the pump cannot start is not startable work."""
    p = _preset(tmp_path, monkeypatch, _ok_body())
    M.create(p, store=store)
    rows = {w.id: w for w in W.project(store=store)}
    assert rows["S1"].state == W.READY, (
        f"S1 is {rows['S1'].state}, not READY — {rows['S1'].blocked_reason}")
    assert rows["S2"].state == W.BLOCKED, "S2 must wait on S1"


def test_a_stage_with_no_repo_is_REFUSED_not_created(tmp_path, monkeypatch):
    """NEGATIVE CONTROL. Without this refusal the stage is created and sits in DRAFT forever."""
    body = _ok_body(repo="")
    with pytest.raises(M.PresetRefused, match="no repo declared"):
        _preset(tmp_path, monkeypatch, body)


def test_a_stage_with_no_resource_claim_is_REFUSED_not_created(tmp_path, monkeypatch):
    """NEGATIVE CONTROL. Same DRAFT trap, via `contract UNMEASURED`."""
    body = _ok_body()
    body["stages"][0]["resource_claim"] = ""
    with pytest.raises(M.PresetRefused, match="no resource_claim declared"):
        _preset(tmp_path, monkeypatch, body)


def test_the_draft_trap_is_real_and_not_a_theory(store):
    """The refusals above are only worth having if the trap they name actually exists."""
    st = store
    st.create(title="no repo, no claim", tid="TRAP-01", actor="t")
    w = {x.id: x for x in W.project(store=st)}["TRAP-01"]
    assert w.state == W.DRAFT
    verdicts = {c.name: c.verdict for c in w.checks}
    assert verdicts["repo"] == W.UNMEASURED
    assert verdicts["contract"] == W.UNMEASURED


# ============================================================ 3. F-5: the shared WRITE claim

def test_two_stages_sharing_a_WRITE_claim_are_REFUSED(tmp_path, monkeypatch):
    """NEGATIVE CONTROL. Both stages would reach READY and never be allowed to start."""
    body = _ok_body()
    body["stages"][1]["resource_claim"] = "res-one"        # same claim as S1, and S2 is WRITE
    with pytest.raises(M.PresetRefused, match="DECLARED conflict"):
        _preset(tmp_path, monkeypatch, body)


def test_two_READERS_of_one_claim_are_allowed(tmp_path, monkeypatch, store):
    """The refusal must be about writers, not about sharing — over-refusing is also a defect."""
    body = _ok_body()
    body["stages"][1]["resource_claim"] = "res-one"
    body["stages"][1]["access"] = "READ"
    p = _preset(tmp_path, monkeypatch, body)
    assert M.validate(p) == []
    M.create(p, store=store)
    rows = {w.id: w for w in W.project(store=store)}
    assert rows["S1"].conflicts_with == [], "two readers were reported as a conflict"


def test_the_shared_write_trap_is_real_and_not_a_theory(store):
    """A declared, non-live conflict refuses a guarded start — measured, not assumed."""
    W.create("writer", work_id="A", repo="agent-factory", resource_claim="res-x",
             access="WRITE", store=store)
    W.create("reader", work_id="B", repo="agent-factory", resource_claim="res-x",
             access="READ", store=store)
    store.set_autonomy("A", T.GUARDED, actor="t")
    a = {w.id: w for w in W.project(store=store)}["A"]
    assert a.state == W.READY, "the trap only bites work that is otherwise startable"
    allowed, why = W.guarded_start(a)
    assert not allowed
    assert any("resource conflict" in r for r in why)


def test_the_shipped_preset_has_no_shared_write_claim():
    p = M.load("marketing-meeting-v1")
    writers = [s.resource_claim for s in p.stages if s.access == "WRITE"]
    assert len(writers) == len(set(writers))
    for w in writers:
        shared = [s.id for s in p.stages if s.resource_claim == w]
        assert len(shared) == 1, f"{w} is shared by {shared} and one of them writes"


# ============================================================ 4. append-only safety

def test_a_second_create_is_REFUSED_rather_than_duplicating(tmp_path, monkeypatch, store):
    """⛔ The store is append-only, so a repeated create resets fields folded after the first."""
    p = _preset(tmp_path, monkeypatch, _ok_body())
    M.create(p, store=store)
    with pytest.raises(M.PresetRefused, match="already exist"):
        M.create(p, store=store)


def test_the_refused_second_create_wrote_nothing(tmp_path, monkeypatch, store):
    p = _preset(tmp_path, monkeypatch, _ok_body())
    M.create(p, store=store)
    before = len(store.all())
    with pytest.raises(M.PresetRefused):
        M.create(p, store=store)
    assert len(TaskStore(store.path).all()) == before


def test_plan_writes_nothing(tmp_path, monkeypatch, store):
    p = _preset(tmp_path, monkeypatch, _ok_body())
    txt = M.plan_report(p)
    assert "S1" in txt and "S2" in txt
    assert store.all() == [], "plan_report wrote to the store"


# ============================================================ 5. structure and gates

def test_edges_are_durable_depend_edges_not_block_status(tmp_path, monkeypatch, store):
    """⛔ A `block` is erased by its `unblock`; the graph must outlive its own satisfaction."""
    p = _preset(tmp_path, monkeypatch, _ok_body())
    M.create(p, store=store)
    assert store.get("S2").depends_on == ["S1"]


def test_run_membership_is_the_parent_link(tmp_path, monkeypatch, store):
    """The pump answers "is this stage in the run?" with `parent`, so it has to be set."""
    p = _preset(tmp_path, monkeypatch, _ok_body())
    M.create(p, store=store)
    for s in p.stages:
        assert store.get(s.id).parent == p.mission_id
    assert store.get(p.mission_id).parent is None


def test_a_human_gate_is_created_held(tmp_path, monkeypatch, store):
    body = _ok_body()
    body["stages"].append({"id": "S3", "title": "gate", "kind": "human_gate",
                           "autonomy": "MANUAL", "resource_claim": "res-three",
                           "hold": "AWAITING-X", "depends_on": ["S2"]})
    p = _preset(tmp_path, monkeypatch, body)
    M.create(p, store=store)
    assert store.get("S3").blocked_by == ["AWAITING-X"]
    w = {x.id: x for x in W.project(store=store)}["S3"]
    assert w.state == W.BLOCKED
    assert any(c.name == "hold" and c.verdict == W.FAIL for c in w.checks)


def test_a_human_gate_with_no_hold_is_REFUSED(tmp_path, monkeypatch):
    """NEGATIVE CONTROL. A gate that holds nothing is a gate that cannot stop anything."""
    body = _ok_body()
    body["stages"].append({"id": "S3", "title": "gate", "kind": "human_gate",
                           "resource_claim": "res-three", "depends_on": ["S2"]})
    with pytest.raises(M.PresetRefused, match="no hold"):
        _preset(tmp_path, monkeypatch, body)


def test_requires_approval_survives_onto_the_contract(tmp_path, monkeypatch, store):
    """It is read by `work.guarded_start`, so it must land on the task, not stay in the YAML."""
    body = _ok_body()
    body["stages"].append({"id": "S3", "title": "gate", "kind": "human_gate",
                           "autonomy": "MANUAL", "resource_claim": "res-three",
                           "hold": "AWAITING-X", "requires_approval": "SIGNOFF",
                           "depends_on": ["S2"]})
    p = _preset(tmp_path, monkeypatch, body)
    M.create(p, store=store)
    assert store.get("S3").contract.get("requires_approval") == "SIGNOFF"


def test_the_model_binding_lands_on_the_contract(tmp_path, monkeypatch, store):
    """⚠ A banner naming a model the process is not running is worse than no banner."""
    body = _ok_body()
    body["stages"][0]["model"] = "claude-opus-5"
    body["stages"][0]["effort"] = "max"
    p = _preset(tmp_path, monkeypatch, body)
    M.create(p, store=store)
    c = store.get("S1").contract
    assert c["model"] == "claude-opus-5" and c["effort"] == "max"


# ============================================================ 6. refusals that fail closed

@pytest.mark.parametrize("mutate,match", [
    (lambda b: b["stages"][1].__setitem__("depends_on", ["NOPE"]), "not a stage"),
    (lambda b: b.__setitem__("target", "NOPE"), "target"),
    (lambda b: b.__setitem__("target", ""), "no target"),
    (lambda b: b["stages"][0].__setitem__("kind", "wizard"), "kind"),
    (lambda b: b["stages"][0].__setitem__("autonomy", "YOLO"), "autonomy"),
    (lambda b: b["stages"][0].__setitem__("access", "MAYBE"), "access"),
    (lambda b: b["stages"][0].__setitem__("id", "not a legal id!"), "legal task id"),
    (lambda b: b.__setitem__("stages", []), "no stages"),
])
def test_a_malformed_preset_is_refused_before_anything_is_written(tmp_path, monkeypatch,
                                                                  mutate, match):
    body = _ok_body()
    mutate(body)
    with pytest.raises(M.PresetRefused, match=match):
        _preset(tmp_path, monkeypatch, body)


def test_a_dependency_cycle_is_refused(tmp_path, monkeypatch):
    body = _ok_body()
    body["stages"][0]["depends_on"] = ["S2"]
    with pytest.raises(M.PresetRefused, match="cycle"):
        _preset(tmp_path, monkeypatch, body)


def test_an_unknown_preset_is_refused_and_names_what_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "PRESETS_DIR", tmp_path / "empty")
    with pytest.raises(M.PresetRefused, match="no preset"):
        M.load("does-not-exist")


def test_no_preset_writes_a_manifest_sidecar(tmp_path, monkeypatch, store):
    """⛔ The contract travels ON the task. A sidecar would be a second source of truth."""
    p = _preset(tmp_path, monkeypatch, _ok_body())
    M.create(p, store=store)
    assert store.get("S1").contract.get("resource_claim") == "res-one", (
        "the claim is not on the task, so the projection would need an overlay to see it")
