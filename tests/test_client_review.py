"""Tests for the Client Review read model.

The important tests here are the **negative controls**: a filter that has never been shown to
drop anything, and a grounding gate that has never been shown to refuse anything, are the blind
instruments this repo keeps finding. So each guard is tested by making it fire, not only by
watching it pass something through.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from factory import client_review as cr
from factory import evidence as ev
from factory import tasks as T


# --------------------------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------------------------

@pytest.fixture()
def root(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "real.md").write_text("evidence body", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def store(tmp_path):
    s = T.TaskStore(tmp_path / "tasks.jsonl")
    mid = s.create("mission", actor="test")
    a = s.create("A", actor="test", parent=mid)
    s.add_evidence(a, kind="analysis", ref="docs/real.md", actor="test",
                   basis="MEASURED", evidence_class=ev.TARGET)
    s.close(a, actor="test")
    b = s.create("B", actor="test", parent=mid)
    s.add_evidence(b, kind="note", ref="docs/assumed.md", actor="test", basis="ASSUMED")
    return s, mid, a, b


def _write(tmp_path, doc) -> pathlib.Path:
    p = tmp_path / "review.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    # assemble() loads yaml; give it a .yaml that yaml can read (json is valid yaml).
    y = tmp_path / "review.yaml"
    y.write_text(json.dumps(doc), encoding="utf-8")
    return y


# --------------------------------------------------------------------------------------------
# 1. The client boundary is an allow-list — and it drops what nobody named
# --------------------------------------------------------------------------------------------

def test_allow_list_drops_an_unnamed_field():
    """The control that matters: a field nobody added to CLIENT_SAFE does not reach the client.

    This is the 2026-08-31 credential lesson as a test. A deny-list would pass an unknown field;
    the allow-list must drop it without anyone having thought of it in advance.
    """
    row = {"id": "x", "title": "ok", "internal_prompt": "SYSTEM: you are...",
           "operator_note": "client is difficult"}
    out = cr.client_safe("delivered", row)
    assert out == {"id": "x", "title": "ok"}
    assert "internal_prompt" not in out
    assert "operator_note" not in out


def test_diagnostics_has_no_allow_list_at_all():
    """`diagnostics` is operator-only by having no entry, not by being deleted somewhere."""
    assert "diagnostics" not in cr.CLIENT_SAFE
    with pytest.raises(cr.ReviewError):
        cr.client_safe("diagnostics", {"root": "/secret/path"})


def test_to_client_dict_never_emits_diagnostics(root, store, tmp_path):
    s, mid, a, b = store
    y = _write(tmp_path, {"project": {"id": "p", "name": "P"}})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    assert review.diagnostics                      # it is populated for the operator
    assert "diagnostics" not in review.to_client_dict()


def test_backstop_denylist_raises_rather_than_redacting():
    """The second gate is loud. A silent redaction would hide that the allow-list is wrong."""
    with pytest.raises(cr.LeakError):
        cr.client_safe("risks", {"id": "r", "title": "conn string",
                                 "impact": "uses azure-kv:vault/thing"})


# --------------------------------------------------------------------------------------------
# 2. Grounding — the guard must be shown to refuse, not only to permit
# --------------------------------------------------------------------------------------------

def test_guarded_word_is_refused_when_the_file_is_missing(root, store, tmp_path):
    s, *_ = store
    y = _write(tmp_path, {"delivered": [
        {"id": "1", "title": "T", "status": "Complete",
         "evidence_refs": ["docs/does-not-exist.md"]}]})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    assert review.delivered[0].grounding == cr.CLAIMED
    assert review.delivered[0].status == cr.UNSUBSTANTIATED


def test_guarded_word_is_refused_when_the_basis_is_only_assumed(root, store, tmp_path):
    """The file existing is not enough. An ASSUMED row is a claim, not a proof."""
    (root / "docs" / "assumed.md").write_text("x", encoding="utf-8")
    s, *_ = store
    y = _write(tmp_path, {"delivered": [
        {"id": "1", "title": "T", "status": "Verified",
         "evidence_refs": ["docs/assumed.md"]}]})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    assert review.delivered[0].grounding == cr.CLAIMED
    assert review.delivered[0].status == cr.UNSUBSTANTIATED


def test_guarded_word_survives_when_both_halves_hold(root, store, tmp_path):
    s, *_ = store
    y = _write(tmp_path, {"delivered": [
        {"id": "1", "title": "T", "status": "Complete", "evidence_refs": ["docs/real.md"]}]})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    assert review.delivered[0].grounding == cr.GROUNDED
    assert review.delivered[0].status == "Complete"


def test_unguarded_status_passes_through_untouched():
    """"In progress" describes an intention, not a verified outcome — it needs no evidence."""
    assert cr.enforce("In progress", cr.UNGROUNDED) == "In progress"
    assert cr.enforce("Blocked", cr.UNGROUNDED) == "Blocked"


@pytest.mark.parametrize("word", ["Complete", "VERIFIED", "on track", "Deployed", "Accepted"])
def test_every_guarded_word_is_actually_recognised(word):
    """Negative control on the guard list itself: a word in the list that `is_guarded` does not
    match would be a rule that exists on paper and never fires."""
    assert cr.is_guarded(word)


def test_no_evidence_refs_is_ungrounded_not_claimed(root):
    assert cr.ground([], [], root) == cr.UNGROUNDED


# --------------------------------------------------------------------------------------------
# 3. Freshness — four states that never collapse
# --------------------------------------------------------------------------------------------

def test_unreadable_source_is_unavailable_not_stale():
    """An instrument that could not look has not reported that the state is old."""
    assert cr.freshness(1000.0, now=1000.0, source_readable=False) == cr.UNAVAILABLE


def test_missing_timestamp_is_unavailable_not_live():
    assert cr.freshness(None, now=1000.0) == cr.UNAVAILABLE


@pytest.mark.parametrize("age,expected", [
    (60, cr.LIVE),
    (cr.LIVE_WINDOW_SEC + 1, cr.LAST_VERIFIED),
    (cr.STALE_AFTER_SEC + 1, cr.STALE),
])
def test_freshness_boundaries(age, expected):
    now = 1_000_000.0
    assert cr.freshness(now - age, now=now) == expected


# --------------------------------------------------------------------------------------------
# 4. Missing and partial data must degrade, never explode
# --------------------------------------------------------------------------------------------

def test_a_review_with_no_task_store_still_assembles(root, tmp_path):
    y = _write(tmp_path, {"project": {"name": "P"}, "delivered": [
        {"id": "1", "title": "T", "status": "Complete", "evidence_refs": ["docs/real.md"]}]})
    review = cr.assemble(y, tasks_path=tmp_path / "nope.jsonl", root=root)
    assert review.review["freshness_state"] == cr.UNAVAILABLE
    assert review.progress["completion_basis"] == "UNAVAILABLE"
    # The file exists but no task row backs it, so the claim is not promoted.
    assert review.delivered[0].status == cr.UNSUBSTANTIATED


def test_an_empty_narrative_renders_rather_than_raising(root, tmp_path):
    y = _write(tmp_path, {})
    review = cr.assemble(y, root=root)
    payload = review.to_client_dict()
    assert payload["delivered"] == []
    assert payload["risks"] == []
    from factory.client_review_render import render_html
    html = render_html(review)
    assert "Nothing currently requires a decision from you" in html
    assert "<title>" in html


def test_optional_fields_absent_do_not_break_the_render(root, store, tmp_path):
    s, *_ = store
    y = _write(tmp_path, {"delivered": [{"id": "1", "title": "Bare"}]})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    from factory.client_review_render import render_html
    assert "Bare" in render_html(review)


def test_a_missing_narrative_raises_loudly(tmp_path):
    with pytest.raises(cr.ReviewError):
        cr.assemble(tmp_path / "absent.yaml")


# --------------------------------------------------------------------------------------------
# 5. Origin — a factory suggestion may never read as a client requirement
# --------------------------------------------------------------------------------------------

def test_an_unknown_origin_is_rejected(root, store, tmp_path):
    s, *_ = store
    y = _write(tmp_path, {"delivered": [{"id": "1", "title": "T", "origin": "CLIENT_ISH"}]})
    with pytest.raises(cr.ReviewError):
        cr.assemble(y, tasks_path=s.path, root=root)


def test_origin_reaches_the_rendered_page(root, store, tmp_path):
    s, *_ = store
    y = _write(tmp_path, {"delivered": [
        {"id": "1", "title": "Ours", "origin": cr.FACTORY_PROPOSED},
        {"id": "2", "title": "Theirs", "origin": cr.CLIENT}]})
    from factory.client_review_render import render_html
    html = render_html(cr.assemble(y, tasks_path=s.path, root=root))
    assert "We proposed this" in html
    assert "You asked for this" in html


# --------------------------------------------------------------------------------------------
# 6. Acceptance is computed, and refuses an unsupported declaration
# --------------------------------------------------------------------------------------------

def test_declared_acceptance_is_downgraded_when_state_does_not_support_it(root, store, tmp_path):
    s, *_ = store
    y = _write(tmp_path, {
        "acceptance": {"status": "ACCEPTED"},
        "delivered": [{"id": "1", "title": "T", "evidence_refs": ["docs/missing.md"]}]})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    assert review.acceptance["status"] != cr.ACCEPTED
    assert any("not supported by state" in u for u in review.acceptance["unmet"])


def test_a_blocking_open_decision_blocks_acceptance(root, store, tmp_path):
    s, *_ = store
    y = _write(tmp_path, {
        "delivered": [{"id": "1", "title": "T", "evidence_refs": ["docs/real.md"]}],
        "decisions": [{"id": "d", "question": "?", "blocking": True, "status": "OPEN"}]})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    assert review.acceptance["status"] in (cr.NOT_READY, cr.READY_FOR_REVIEW)
    assert any("blocking decision" in u for u in review.acceptance["unmet"])


def test_clean_state_reaches_ready_for_acceptance(root, store, tmp_path):
    s, *_ = store
    y = _write(tmp_path, {
        "delivered": [{"id": "1", "title": "T", "evidence_refs": ["docs/real.md"]}],
        "next": [{"id": "n", "title": "done thing", "status": "DONE"}]})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    assert review.acceptance["unmet"] == []
    assert review.acceptance["status"] == cr.READY_FOR_ACCEPTANCE


def test_acceptance_reasons_are_client_readable_english(root, store, tmp_path):
    """No "decision(s)". The count and the noun must agree in a client-facing surface."""
    s, *_ = store
    y = _write(tmp_path, {
        "delivered": [{"id": "1", "title": "T", "evidence_refs": ["docs/real.md"]}],
        "decisions": [{"id": "d", "question": "?", "blocking": True, "status": "OPEN"}]})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    for u in review.acceptance["unmet"]:
        assert "(s)" not in u
    assert "1 blocking decision awaiting your input" in review.acceptance["unmet"]


# --------------------------------------------------------------------------------------------
# 7. Evidence mapping
# --------------------------------------------------------------------------------------------

def test_evidence_not_on_disk_is_not_found_never_verified(root, store, tmp_path):
    s, *_ = store
    y = _write(tmp_path, {"evidence": [
        {"id": "e", "label": "L", "source": "docs/gone.md"}]})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    assert review.evidence[0].status == "NOT_FOUND"
    assert review.evidence[0].verified_at is None


def test_evidence_inherits_basis_from_the_task_row_not_the_narrative(root, store, tmp_path):
    """The narrative may claim any basis it likes; the task store is the authority."""
    s, *_ = store
    y = _write(tmp_path, {"evidence": [
        {"id": "e", "label": "L", "source": "docs/real.md", "basis": "ASSUMED"}]})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    assert review.evidence[0].basis == "MEASURED"
    assert review.evidence[0].status == "VERIFIED"


def test_missing_evidence_files_are_reported_to_the_operator(root, store, tmp_path):
    s, *_ = store
    y = _write(tmp_path, {"evidence": [{"id": "e", "label": "L", "source": "docs/gone.md"}]})
    review = cr.assemble(y, tasks_path=s.path, root=root)
    assert review.diagnostics["missing_evidence_files"] == ["docs/gone.md"]


# --------------------------------------------------------------------------------------------
# 8. Progress is derived, and says so
# --------------------------------------------------------------------------------------------

def test_completion_is_derived_from_closed_children(root, store, tmp_path):
    """With no labels declared, the basis falls back to the mission task's children."""
    s, mid, a, b = store
    mission = tmp_path / "m.json"
    mission.write_text(json.dumps({"mission_task": mid, "labels": {}}), encoding="utf-8")
    y = _write(tmp_path, {})
    review = cr.assemble(y, tasks_path=s.path, mission_path=mission, root=root)
    assert review.progress["completion_percent"] == 50      # one of two children closed
    assert review.progress["completion_basis"] == "DERIVED"


def test_completion_counts_declared_tasks_not_duplicated_children(root, tmp_path):
    """The regression test for the 40%-vs-25% defect found on the real mission.

    A duplicate child that repeats a declared workstream must not inflate the client-facing
    percentage. The declared population is the mission record's labels.
    """
    s = T.TaskStore(tmp_path / "dup.jsonl")
    mid = s.create("mission", actor="t")
    r1 = s.create("R1", actor="t", parent=mid)
    r2 = s.create("R2", actor="t", parent=mid)
    r3 = s.create("R3", actor="t", parent=mid)
    r4 = s.create("R4", actor="t", parent=mid)
    for t in (r1, r2):
        s.add_evidence(t, kind="k", ref="docs/real.md", actor="t", basis="MEASURED")
        s.close(t, actor="t")
    # The duplicate: same work, closed, but NOT declared by the mission record.
    dup = s.create("R1 (again)", actor="t", parent=mid)
    s.add_evidence(dup, kind="k", ref="docs/real.md", actor="t", basis="MEASURED")
    s.close(dup, actor="t")

    mission = tmp_path / "m.json"
    mission.write_text(json.dumps({"mission_task": mid,
                                   "labels": {"R1": r1, "R2": r2, "R3": r3, "R4": r4}}),
                       encoding="utf-8")
    review = cr.assemble(_write(tmp_path, {}), tasks_path=s.path,
                         mission_path=mission, root=root)
    # 2 of 4 declared, not 3 of 5 children.
    assert review.progress["completion_percent"] == 50


# --------------------------------------------------------------------------------------------
# 9. The page is genuinely standalone
# --------------------------------------------------------------------------------------------

def test_the_generated_page_makes_no_external_requests(root, store, tmp_path):
    """The control behind the no-webfont decision.

    A live meeting on a shared screen must not depend on a font host resolving. Any absolute URL
    in the output is a request that can hang or reflow the page mid-sentence, so the page is
    asserted to contain none at all — not "no font links", none.
    """
    import re as _re
    s, *_ = store
    y = _write(tmp_path, {"project": {"name": "P"},
                          "delivered": [{"id": "1", "title": "T",
                                         "evidence_refs": ["docs/real.md"]}]})
    from factory.client_review_render import render_html
    html_out = render_html(cr.assemble(y, tasks_path=s.path, root=root))

    for pattern in (r'https?://', r'src\s*=\s*["\']//', r'@import', r'url\(\s*["\']?https?:'):
        assert not _re.search(pattern, html_out), f"external reference matched {pattern!r}"
    assert "fonts.googleapis" not in html_out
    assert "<link" not in html_out


def test_every_font_role_resolves_through_a_token(root, store, tmp_path):
    """No rule may name a family directly — a literal stack is how one role drifts from the rest."""
    from factory.client_review_render import _CSS
    for token in ("--display:", "--body:", "--mono:"):
        assert token in _CSS
    for gone in ("Zilla Slab", "IBM Plex Mono", "Source Sans 3"):
        assert gone not in _CSS


# --------------------------------------------------------------------------------------------
# 10. Mission integrity — the defect the client-facing figure steps around must stay visible
# --------------------------------------------------------------------------------------------

def test_mission_integrity_warns_on_an_undeclared_duplicate(root, tmp_path):
    """The declared-set basis is correct AND defensive. This proves it does not hide the fault."""
    s = T.TaskStore(tmp_path / "dup.jsonl")
    mid = s.create("mission", actor="t")
    r1 = s.create("R1", actor="t", parent=mid)
    r2 = s.create("R2", actor="t", parent=mid)
    dup = s.create("R1 (again)", actor="t", parent=mid)
    s.add_evidence(dup, kind="k", ref="docs/real.md", actor="t", basis="MEASURED")
    s.close(dup, actor="t")

    mission = tmp_path / "m.json"
    mission.write_text(json.dumps({"mission_task": mid, "labels": {"R1": r1, "R2": r2}}),
                       encoding="utf-8")
    review = cr.assemble(_write(tmp_path, {}), tasks_path=s.path,
                         mission_path=mission, root=root)
    mi = review.diagnostics["mission_integrity"]
    assert mi["status"] == "WARNING"
    assert mi["declared_task_count"] == 2
    assert mi["observed_child_count"] == 3
    assert [t["id"] for t in mi["duplicate_or_unexpected_tasks"]] == [dup]
    assert "declared logical task set" in mi["client_progress_basis"]


def test_mission_integrity_is_ok_when_the_record_matches(root, tmp_path):
    """Negative control: the warning must be capable of NOT firing, or it says nothing."""
    s = T.TaskStore(tmp_path / "clean.jsonl")
    mid = s.create("mission", actor="t")
    r1 = s.create("R1", actor="t", parent=mid)
    mission = tmp_path / "m.json"
    mission.write_text(json.dumps({"mission_task": mid, "labels": {"R1": r1}}), encoding="utf-8")
    review = cr.assemble(_write(tmp_path, {}), tasks_path=s.path,
                         mission_path=mission, root=root)
    mi = review.diagnostics["mission_integrity"]
    assert mi["status"] == "OK"
    assert mi["duplicate_or_unexpected_tasks"] == []
    assert mi["declared_not_observed"] == []


def test_mission_integrity_flags_a_declared_task_that_does_not_exist(root, tmp_path):
    s = T.TaskStore(tmp_path / "ghost.jsonl")
    mid = s.create("mission", actor="t")
    r1 = s.create("R1", actor="t", parent=mid)
    mission = tmp_path / "m.json"
    mission.write_text(json.dumps({"mission_task": mid,
                                   "labels": {"R1": r1, "R9": "deadbeef"}}), encoding="utf-8")
    review = cr.assemble(_write(tmp_path, {}), tasks_path=s.path,
                         mission_path=mission, root=root)
    mi = review.diagnostics["mission_integrity"]
    assert mi["status"] == "WARNING"
    assert mi["declared_not_observed"] == [{"label": "R9", "id": "deadbeef"}]


def test_mission_integrity_never_crosses_the_client_boundary(root, tmp_path):
    """It names internal task ids and titles. It must have no allow-list, and reach no client."""
    assert "mission_integrity" not in cr.CLIENT_SAFE
    s = T.TaskStore(tmp_path / "dup2.jsonl")
    mid = s.create("mission", actor="t")
    r1 = s.create("R1", actor="t", parent=mid)
    s.create("SECRET-INTERNAL-DUPLICATE", actor="t", parent=mid)
    mission = tmp_path / "m.json"
    mission.write_text(json.dumps({"mission_task": mid, "labels": {"R1": r1}}), encoding="utf-8")
    review = cr.assemble(_write(tmp_path, {}), tasks_path=s.path,
                         mission_path=mission, root=root)
    assert review.diagnostics["mission_integrity"]["status"] == "WARNING"
    payload = review.to_client_dict()
    assert "mission_integrity" not in payload
    from factory.client_review_render import render_html
    assert "SECRET-INTERNAL-DUPLICATE" not in render_html(review)


def test_mission_integrity_is_unavailable_without_a_mission_record(root, store, tmp_path):
    """No record to compare against is not the same as a clean record."""
    s, *_ = store
    review = cr.assemble(_write(tmp_path, {}), tasks_path=s.path, root=root)
    assert review.diagnostics["mission_integrity"]["status"] == "UNAVAILABLE"


# --------------------------------------------------------------------------------------------
# 11. The real review renders end to end
# --------------------------------------------------------------------------------------------

def test_the_navira_review_assembles_and_renders():
    """End to end against the real narrative, at the root the artifact is actually built from.

    ⭐ **The root is not this checkout, and that is a decision rather than an accident.**
    `mission/marketing-model-v1` carries client-identifying evidence and is deliberately not
    merged (operator decision, 2026-09-01), so the mission's evidence is only ever read read-only
    from its worktree. Asserting grounding against `repo` asserted a state that the approved
    architecture guarantees will never hold — and it duly broke the moment the write-ups landed.
    See `missions/client-review-v1/06-D5-REFRESH-CONTRACT.md`.

    ⭐ **And the second half, which is a different root for a different reason (F105).** Two kinds
    of path meet in this call and they resolve oppositely:

        root         GIT-TRACKED evidence  -> checkout/worktree relative. Correct above.
        tasks_path   ESTATE-WIDE state     -> `factory.repo`, shared by every worktree.
        mission_path         ""                        ""

    As `repo / ".data"` the latter two pointed at the WORKTREE's own `.data/`, which holds no task
    store and no mission manifest — so `assemble()` received zero tasks, all four delivered
    outcomes fell back to ASSERTED, and this assertion failed. RED in every worktree, GREEN only
    in the primary checkout: the test was detecting its own broken input and reporting it as a
    grounding regression.

    Both fixes are required and neither subsumes the other. They were made independently on two
    branches, each correct about its own half.
    """
    repo = pathlib.Path(__file__).resolve().parent.parent
    y = repo / "missions" / "client-review-v1" / "reviews" / "navira-marketing-model.yaml"
    if not y.exists():                                      # pragma: no cover
        pytest.skip("narrative not present")
    mission_root = repo / ".worktrees" / "mission"
    root = mission_root if mission_root.exists() else repo

    from factory import repo as _repo
    review = cr.assemble(y, tasks_path=_repo.data() / "tasks.jsonl",
                         mission_path=_repo.data() / "missions"
                         / "marketing-model-reconstruction-v1.json", root=root)
    from factory.client_review_render import render_html
    html = render_html(review)
    assert "Navira" in html

    authored = [o for o in review.delivered if o.writeup == "AUTHORED"]
    assert authored, "the narrative should carry authored outcomes"

    if root == mission_root:
        # The evidence is readable, so every authored outcome must actually be backed by it.
        ungrounded = [(o.id, o.evidence_refs) for o in authored
                      if o.grounding != cr.GROUNDED]
        assert not ungrounded, f"authored outcomes with unresolved evidence: {ungrounded}"
    else:                                                   # pragma: no cover
        # No mission worktree here. The point is then the *degrade*, not the grounding: an
        # outcome whose artefact cannot be read must never quietly keep a guarded word.
        for o in authored:
            if o.grounding != cr.GROUNDED:
                assert o.status == cr.UNSUBSTANTIATED or not cr.is_guarded(o.status)

    # An unwritten outcome never renders as a finished one, at either root.
    for o in review.delivered:
        if o.writeup == "PENDING":
            assert o.summary == "" and o.business_impact == ""
    # And nothing operator-only leaked into the page.
    for needle in ("diagnostics", "tasks_readable", str(repo)):
        assert needle not in html


# --------------------------------------------------------------------------------------------
# 12. A blind instrument must not quietly downgrade a client-facing claim
# --------------------------------------------------------------------------------------------

def test_the_cli_default_task_store_is_the_shared_root_not_the_cwd(tmp_path, monkeypatch):
    """⭐ Delivery-critical, and the defect lives at the CLI boundary.

    Measured 2026-09-01, same narrative and same code, differing only in the directory the build
    ran from:

        --tasks .data/tasks.jsonl  (the old CWD-relative default, from a worktree)
            grounding 4x ASSERTED   status 4x UNSUBSTANTIATED   freshness UNAVAILABLE
        resolved via factory.repo
            grounding 4x SATISFIED  status 4x Complete          freshness LAST_VERIFIED

    The degradation is visible rather than hidden -- the page says UNSUBSTANTIATED -- so this was
    never an overclaim. It is the opposite and still delivery-critical: the client receives a
    document reporting fully evidenced outcomes as unsubstantiated, from the command the runbook
    prescribes at the moment it prescribes it.

    ⚠ Asserted against what `main()` PASSES, not against a grounding outcome. `assemble()`'s
    `tasks_path=None` means "there is no store" and the readiness gate depends on that sentinel,
    so the default cannot live in `assemble()`. An earlier version of this test called `assemble`
    twice with the same argument and compared the results -- a check that could not fail.
    """
    from factory import client_review as _cr
    from factory import repo as _repo

    root = pathlib.Path(__file__).resolve().parent.parent
    y = root / "missions" / "client-review-v1" / "reviews" / "navira-marketing-model.yaml"
    if not y.exists():                                      # pragma: no cover
        pytest.skip("narrative not present")

    seen = {}

    def _spy(narrative, **kw):
        seen.update(kw)
        raise SystemExit(0)                 # stop before rendering; the argument is the assertion

    monkeypatch.setattr(_cr, "assemble", _spy)
    monkeypatch.chdir(tmp_path)             # a directory with no .data/ at all
    with pytest.raises(SystemExit):
        _cr.main([str(y)])

    got = pathlib.Path(seen["tasks_path"])
    assert got == _repo.data() / "tasks.jsonl", (
        f"the CLI default resolved to {got}, not the shared root — the evidence strength of a "
        f"client document would depend on the working directory")
    assert got.is_absolute(), "a relative default is the whole defect"


def test_a_missing_store_still_degrades_visibly_rather_than_pretending(root, tmp_path):
    """The fail-closed path is preserved: an explicit path that is not there must still announce
    itself, in freshness, in completion basis and in every outcome's status. A weaker claim that
    does not say why is the thing that cannot be told apart from an honest absence."""
    y = _write(tmp_path, {"project": {"name": "P"}, "delivered": [
        {"id": "1", "title": "T", "status": "Complete", "evidence_refs": ["docs/real.md"]}]})
    review = cr.assemble(y, tasks_path=tmp_path / "nope.jsonl", root=root)
    assert review.review["freshness_state"] == cr.UNAVAILABLE
    assert review.progress["completion_basis"] == "UNAVAILABLE"
    assert review.delivered[0].status == cr.UNSUBSTANTIATED


def test_the_runbook_command_produces_a_grounded_artifact_from_any_checkout(tmp_path):
    """⭐ The documented regeneration command, verbatim, must be correct from a worktree.

    `05-CLIENT-REVIEW-DEMO-RUNBOOK.md` passes `--tasks .data/tasks.jsonl` and
    `--mission .data/missions/<id>.json`, both CWD-relative, and tells the operator to regenerate
    "shortly before the meeting". Run from a worktree those resolve to a `.data/` holding neither
    file, and the client artefact reported all four delivered outcomes as UNSUBSTANTIATED. The
    failure landed exactly when nobody had time to notice it.
    """
    from factory import repo as _repo
    root = pathlib.Path(__file__).resolve().parent.parent
    y = root / "missions" / "client-review-v1" / "reviews" / "navira-marketing-model.yaml"
    if not y.exists() or not (_repo.data() / "tasks.jsonl").exists():   # pragma: no cover
        pytest.skip("narrative or shared store not present")

    # ⛔ The mission worktree, not this checkout. D2-D5 evidence is deliberately isolated there
    # (operator decision 2026-09-01), so grounding asserted against this checkout asserts a state
    # the approved architecture guarantees will never hold. That is the exact mistake the
    # docstring on test_the_navira_review_assembles_and_renders already records -- made again
    # here, independently, on another branch, and inherited on merge.
    mission_root = root / ".worktrees" / "mission"
    if not mission_root.exists():                           # pragma: no cover
        pytest.skip("mission worktree absent - evidence cannot resolve from main by design")
    review = cr.assemble(y, tasks_path=pathlib.Path(".data/tasks.jsonl"),
                         mission_path=pathlib.Path(
                             ".data/missions/marketing-model-reconstruction-v1.json"),
                         root=mission_root)
    assert cr.publication_block(review) == [], (
        "the runbook's own command produces an artefact that understates its evidence")
    assert all(o.grounding == cr.GROUNDED for o in review.delivered)


def test_publication_is_blocked_when_the_document_understates_itself(root, tmp_path):
    """⭐ Negative control for the gate. It checks the OUTPUT, not the inputs — a path that
    resolved by luck still passes, and one that looked right but produced a degraded document
    still fails."""
    y = _write(tmp_path, {"project": {"name": "P"}, "delivered": [
        {"id": "1", "title": "T", "status": "Complete", "evidence_refs": ["docs/real.md"]}]})
    degraded = cr.assemble(y, tasks_path=tmp_path / "definitely-absent.jsonl", root=root)
    blocks = cr.publication_block(degraded)
    assert blocks, "a review with an unreadable store was cleared for publication"
    assert any("freshness" in b for b in blocks)
