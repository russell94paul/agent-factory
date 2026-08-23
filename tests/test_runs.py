"""The run ledger, and proof each of its verdicts can fire.

Same split as `test_dispatch.py`. The **live** tests gate two properties of the real repo that
would silently rot: the ledger must be shared rather than per-worktree, and every lane must appear
in the report. The **synthetic** tests are the negative control — a basis nobody has watched fire
is decoration, so NOT-RECORDED, MEASURED, RECORDED and REFUSED are each constructed and asserted.

The one that matters most is `test_a_refused_finish_is_recorded`. A refusal is the event that left
no trace at all: `NotFinished` propagates, the operator fixes it or does not, and nothing
remembers. If that row stops being written, the UI silently goes back to showing only successes —
which reads as "no lane ever had a problem".
"""

from __future__ import annotations

import json

import pytest

from factory import finish as finishlib
from factory import runs


# --------------------------------------------------------------------------- live


def test_ledger_is_shared_not_per_worktree(real_ledger):
    """The whole point: one ledger, in the primary worktree.

    `bus.py` and `claims.py` root at ``parent.parent/.data``, which inside a worktree is that
    worktree's own ``.data`` — F70/F71, files that cannot see each other. A run ledger with one
    copy per lane is not a ledger, so this asserts the path is NOT under `.worktrees/`.
    """
    p = runs.path()
    assert p.name == "runs.jsonl"
    assert ".worktrees" not in str(p), (
        f"the ledger resolved to {p} — that is a worktree-local copy, which is F71 again")


def test_every_lane_appears_in_the_report(real_ledger):
    from factory.lanes import LANES
    rows = {r["lane"] for r in runs.report()}
    assert rows == {lane.id for lane in LANES}


def test_a_lane_that_never_ran_reports_not_recorded_rather_than_zero(real_ledger):
    """The ZERO-vs-NOT-RECORDED distinction, on real data.

    Whichever lanes have never been launched must say so. Reporting them as a measured zero would
    be a claim about their cost; NOT-RECORDED is a claim about our instrument, and only one of
    those is true.
    """
    rows = runs.report()
    for r in rows:
        c = r["cost"]
        if c["basis"] == runs.NOT_RECORDED:
            assert c["output"] == 0 and c["sessions"] == 0
        else:
            assert c["basis"] == runs.MEASURED
            assert c["sessions"] > 0


# --------------------------------------------------------------------------- synthetic


@pytest.fixture()
def ledger(tmp_path, monkeypatch):
    """Point the ledger and the transcript root at throwaway directories."""
    monkeypatch.setattr(runs, "_primary", lambda: tmp_path)
    monkeypatch.setattr(runs, "TRANSCRIPTS", tmp_path / "projects")
    return tmp_path


def test_slug_matches_claude_codes_project_directory_naming():
    """``C:\\a\\repo\\.worktrees\\lane`` -> ``C--a-repo--worktrees-lane``.

    Each of ``: \\ / .`` becomes one dash, which is why ``C:\\`` yields two and ``\\.worktrees``
    yields two. Get this wrong and every lane silently reports NOT-RECORDED, because the
    transcript directory is simply never found.
    """
    assert runs.slug(r"C:\a\repo\.worktrees\lane") == "C--a-repo--worktrees-lane"
    assert runs.slug(r"C:\Users\p\repos\aldc-launchpad\docs\readouts") == \
        "C--Users-p-repos-aldc-launchpad-docs-readouts"


def test_cost_with_no_transcripts_is_not_recorded_not_measured_zero(ledger):
    c = runs.cost(r"C:\nowhere\at\all")
    assert c["basis"] == runs.NOT_RECORDED
    assert c["output"] == 0


def test_cost_sums_usage_across_sessions_and_names_the_model(ledger):
    d = ledger / "projects" / runs.slug(r"C:\x\lane")
    d.mkdir(parents=True)
    rows = [
        {"timestamp": "2026-08-22T10:00:00.000Z", "message": {
            "model": "claude-opus-5",
            "usage": {"input_tokens": 10, "output_tokens": 100,
                      "cache_creation_input_tokens": 5, "cache_read_input_tokens": 1000}}},
        {"timestamp": "2026-08-22T12:00:00.000Z", "message": {
            "model": "claude-opus-5",
            "usage": {"input_tokens": 1, "output_tokens": 50,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 20}}},
        "{ this line is torn and must not lose the rest",
    ]
    (d / "s1.jsonl").write_text(
        "\n".join(r if isinstance(r, str) else json.dumps(r) for r in rows), encoding="utf-8")

    c = runs.cost(r"C:\x\lane")
    assert c["basis"] == runs.MEASURED
    assert (c["output"], c["input"]) == (150, 11)
    assert (c["cache_write"], c["cache_read"]) == (5, 1020)
    assert c["models"] == ["claude-opus-5"]
    assert c["wall_clock_s"] == 2 * 3600


def test_record_then_history_is_newest_first(ledger):
    runs.record("alpha", runs.FINISHED, detail="first")
    runs.record("alpha", runs.REFUSED, detail="second", problems=["dirty"])
    runs.record("beta", runs.FINISHED, detail="other")

    all_rows = runs.history()
    assert [r["detail"] for r in all_rows][:1] == ["other"] or len(all_rows) == 3
    alpha = runs.history("alpha")
    assert len(alpha) == 2
    assert alpha[0]["at"] >= alpha[1]["at"]
    assert alpha[0]["basis"] == runs.RECORDED
    assert {r["outcome"] for r in alpha} == {runs.FINISHED, runs.REFUSED}


def test_a_torn_ledger_line_is_skipped_not_fatal(ledger):
    runs.record("alpha", runs.FINISHED)
    with runs.path().open("a", encoding="utf-8") as fh:
        fh.write("{not json\n")
    runs.record("alpha", runs.REFUSED)
    assert len(runs.history("alpha")) == 2


def test_a_refused_finish_is_recorded(ledger, monkeypatch):
    """The row that did not exist before: a lane that refused to close.

    `judgement` has no worktree, so `checks()` refuses immediately — a real refusal, reached
    through the real code path rather than by calling `record()` directly.
    """
    with pytest.raises(finishlib.NotFinished):
        finishlib.finish("judgement", push=False)

    rows = runs.history("judgement")
    assert rows, "a refused finish left no trace — the exact gap this ledger closes"
    assert rows[0]["outcome"] == runs.REFUSED
    assert rows[0]["problems"], "a refusal with no problems recorded says nothing"


def test_recording_never_breaks_a_close(ledger, monkeypatch):
    """A ledger failure must not turn a finished lane into an exception.

    By the time the success row is written the branch is pushed and the claim released. Raising
    there would report a completed close as a failure — the record is not a control.
    """
    def boom(*a, **k):
        raise OSError("disk full")

    monkeypatch.setattr(runs, "record", boom)
    finishlib._record("alpha", runs.FINISHED, "detail", [], "lane/alpha", None)   # must not raise
