"""The three safeguards added after 2026-08-23, and proof each can fire.

Every one of them exists because something got past the checks that were already there:

  1. **`unreconciled()`** — R8's answer was filed while `SYNTHESIS.md` said, three times, that R8
     was *still outstanding*. `unsynthesised()` asks whether the id is *mentioned*, so a document
     discussing an answer in the future tense satisfies it, and the gate stayed green over an
     answer nobody had read.
  2. **`run_log()`** — nobody could say which prompts had been uploaded, because dispatch state was
     a status line a human edits and nothing recorded the moment of sending.
  3. **`order()`** — with four prompts in four states there was no answer to "what do I do next",
     and the tempting answer (send the next one) is the wrong one while an answer sits unread.

Synthetic throughout: each condition is constructed on disk rather than waiting for the repo to
drift into it, so the failing case is watched rather than assumed.
"""

from __future__ import annotations

import pathlib

import pytest

from factory import dispatch, synthesis


# --------------------------------------------------------------------------- unreconciled


def _synth_and_answer(tmp_path, monkeypatch, banked: bool, prose="mentions R7 everywhere"):
    """A synthesis and one answer, with the answer banked or not.

    ⛔ This fixture used to set MODIFICATION TIMES, because `unreconciled()` compared them. That
    was F93: `git worktree add` writes every file at once, so in any fresh checkout all eighteen
    real answers read as "filed after" on write-ordering alone — measured at five milliseconds
    apart. The check is now over CONTENT, so the fixture banks a hash or does not.
    """
    research = tmp_path / "research"
    answers = research / "answers"
    answers.mkdir(parents=True)
    syn = research / "SYNTHESIS.md"
    syn.write_text(prose, encoding="utf-8")
    ans = answers / "R7-answer-thing.md"
    ans.write_text("the answer", encoding="utf-8")

    monkeypatch.setattr(synthesis, "SYNTHESIS", syn)
    monkeypatch.setattr(synthesis, "ANSWERS", answers)
    if banked:
        synthesis.bank()
    return research


def test_unreconciled_fires_when_an_answer_has_never_been_banked(tmp_path, monkeypatch):
    """The negative control. Without this the check is decoration."""
    _synth_and_answer(tmp_path, monkeypatch, banked=False)
    assert synthesis.unreconciled() == ["R7"]


def test_unreconciled_is_quiet_once_the_answer_is_banked(tmp_path, monkeypatch):
    _synth_and_answer(tmp_path, monkeypatch, banked=True)
    assert synthesis.unreconciled() == []


def test_unreconciled_fires_again_when_a_banked_answer_changes(tmp_path, monkeypatch):
    """⭐ The property mtime could not give per answer.

    A modification time is one number for the whole synthesis, so ANY write cleared the check for
    EVERY id — a partial reconciliation marked the answers it never opened as banked. The
    2026-08-29 correction recorded that and could only answer it with a rule. Per-answer hashes
    make it a property.
    """
    research = _synth_and_answer(tmp_path, monkeypatch, banked=True)
    ans = research / "answers" / "R7-answer-thing.md"
    ans.write_text("the answer, substantially revised", encoding="utf-8")
    assert synthesis.unreconciled() == ["R7"]


def test_rewriting_the_synthesis_does_not_bank_an_answer_nobody_read(tmp_path, monkeypatch):
    """⛔ The regression this whole change exists to make impossible.

    Under mtime, touching SYNTHESIS.md cleared the check for every id at once. Here the prose is
    rewritten — at length, mentioning R7 — and R7 stays outstanding, because nothing banked it.
    """
    research = _synth_and_answer(tmp_path, monkeypatch, banked=False)
    (research / "SYNTHESIS.md").write_text(
        "A long and careful reconciliation that discusses R7 at length.", encoding="utf-8")
    assert synthesis.unreconciled() == ["R7"], (
        "writing the synthesis must not bank an answer that was never stamped")


def test_a_future_tense_mention_does_not_satisfy_unreconciled(tmp_path, monkeypatch):
    """The exact R8 case: the id IS mentioned, and the answer is still unread.

    `unsynthesised()` passes here — that is the weakness. `unreconciled()` must not.
    """
    _synth_and_answer(tmp_path, monkeypatch, banked=False,
                      prose="R7 is still outstanding. Read them together when R7 lands.")
    assert synthesis.unsynthesised() == [], "the id IS mentioned — this is the weak check passing"
    assert "R7" in synthesis.unreconciled(), (
        "an answer whose synthesis only promises to read it is NOT reconciled")


def test_a_stamped_but_unmentioned_answer_is_reported(tmp_path, monkeypatch):
    """⭐ The gap content-hashing opens, and the cross-check that closes it.

    mtime was blunt on purpose: it could not be satisfied by writing the id anywhere, only by
    editing the file after the answer landed. A hash CAN be stamped by something that never read
    the answer — so a banked id the prose never names is reported rather than trusted.
    """
    _synth_and_answer(tmp_path, monkeypatch, banked=True, prose="this prose names no ids at all")
    o = synthesis.outstanding()
    assert o["never_banked"] == [] and o["stale"] == []
    assert o["banked_but_unmentioned"] == ["R7"]


# --------------------------------------------------------------------------- run_log


def test_run_log_reads_the_rows_and_skips_the_table_furniture(tmp_path):
    f = tmp_path / "R99-thing.md"
    f.write_text(
        "# R99\n\n**Status: DISPATCHED.**\n\n## Run log\n\n"
        "| Run | Dispatched | Outcome |\n|---|---|---|\n"
        "| 1 | 2026-08-23 | Recorded as dispatched, but it never ran. |\n"
        "| 2 | pending | queued |\n\n> a note\n",
        encoding="utf-8")
    rows = dispatch.run_log(f)
    assert len(rows) == 2, rows
    assert rows[0]["run"] == "1" and rows[0]["dispatched"] == "2026-08-23"
    assert "never ran" in rows[0]["outcome"]


def test_run_log_is_empty_rather_than_fatal_when_there_is_none(tmp_path):
    f = tmp_path / "R98-thing.md"
    f.write_text("# R98\n\nno run log here\n", encoding="utf-8")
    assert dispatch.run_log(f) == []
    assert dispatch.run_log(tmp_path / "does-not-exist.md") == []


# --------------------------------------------------------------------------- order


def test_reconciling_outranks_dispatching(tmp_path):
    """The judgement this module encodes, asserted rather than left in a comment.

    An unread answer is work already paid for and not yet banked. Sending another prompt while one
    sits unreconciled spends money to widen a backlog.
    """
    research = tmp_path / "research"
    answers = research / "answers"
    answers.mkdir(parents=True)
    (research / "R1-answered.md").write_text("**Status: DISPATCHED.**\n", encoding="utf-8")
    (answers / "R1-answer-x.md").write_text("a", encoding="utf-8")
    (research / "R2-waiting.md").write_text("**Status: NOT DISPATCHED.**\n", encoding="utf-8")

    rows = dispatch.order(research, answers, syn_unreconciled={"R1"})
    assert rows[0]["id"] == "R1" and "reconcile" in rows[0]["action"]
    assert rows[1]["id"] == "R2" and rows[1]["action"] == "send it"


def test_a_prompt_contradicting_itself_outranks_everything(tmp_path):
    """STALE_STATUS first: the document and the disk disagree and one of them is wrong."""
    research = tmp_path / "research"
    answers = research / "answers"
    answers.mkdir(parents=True)
    (research / "R1-stale.md").write_text("**Status: NOT DISPATCHED.**\n", encoding="utf-8")
    (answers / "R1-answer-x.md").write_text("a", encoding="utf-8")
    (research / "R2-waiting.md").write_text("**Status: NOT DISPATCHED.**\n", encoding="utf-8")

    rows = dispatch.order(research, answers, syn_unreconciled=set())
    assert rows[0]["id"] == "R1"
    assert rows[0]["state"] == dispatch.STALE_STATUS


def test_order_covers_every_prompt_exactly_once(tmp_path):
    research = tmp_path / "research"
    answers = research / "answers"
    answers.mkdir(parents=True)
    for n in (1, 2, 3):
        (research / f"R{n}-x.md").write_text("**Status: NOT DISPATCHED.**\n", encoding="utf-8")
    ids = [r["id"] for r in dispatch.order(research, answers, syn_unreconciled=set())]
    assert sorted(ids) == ["R1", "R2", "R3"]
    assert len(ids) == len(set(ids))


# --------------------------------------------------------------------------- dependencies


def test_the_dependency_map_refuses_a_dangling_edge(tmp_path, monkeypatch):
    """`_validate()` is the whole point: an edge naming a prompt that does not exist is a silent
    lie about ordering, and it must break the import rather than be quietly skipped."""
    research = tmp_path / "research"
    research.mkdir()
    (research / "R1-x.md").write_text("**Status: NOT DISPATCHED.**\n", encoding="utf-8")
    monkeypatch.setitem(dispatch.DEPENDS, "R1", ["R99"])
    with pytest.raises(ValueError, match="not a prompt"):
        dispatch._validate(research)


def test_the_real_dependency_map_is_not_stale():
    """Live gate. Every edge in DEPENDS names a prompt that exists right now."""
    dispatch._validate()


def test_a_dependency_answered_once_but_owing_a_run_is_NOT_satisfied(tmp_path):
    """The flaw the graph caught in its own first version.

    R13 was ANSWERED from run 1 while run 2 was rewritten and pending, and the first `blocked_by`
    cleared R16 on the strength of the stale run. A dep is met only when it is answered AND owes
    no further run.
    """
    research = tmp_path / "research"
    answers = research / "answers"
    answers.mkdir(parents=True)
    (research / "R1-dep.md").write_text(
        "**Status: ANSWERED.**\n\n## Run log\n\n| Run | Dispatched | Outcome |\n|---|---|---|\n"
        "| 2 | pending | rewritten |\n| 1 | 2026-08-23 | filed |\n", encoding="utf-8")
    (answers / "R1-answer-dep.md").write_text("a", encoding="utf-8")
    (research / "R2-waiter.md").write_text("**Status: NOT DISPATCHED.**\n", encoding="utf-8")

    import factory.dispatch as D
    D.DEPENDS["R2"] = ["R1"]
    try:
        assert D.state(research, answers)["R1"] == D.ANSWERED, "R1 is answered..."
        assert D.blocked_by("R2", research, answers) == ["R1"], (
            "...and still owes run 2, so it does NOT satisfy the dependency")
    finally:
        D.DEPENDS.pop("R2", None)


def test_a_fully_settled_dependency_is_satisfied(tmp_path):
    research = tmp_path / "research"
    answers = research / "answers"
    answers.mkdir(parents=True)
    (research / "R1-dep.md").write_text(
        "**Status: ANSWERED.**\n\n## Run log\n\n| Run | Dispatched | Outcome |\n|---|---|---|\n"
        "| 1 | 2026-08-23 | filed |\n", encoding="utf-8")
    (answers / "R1-answer-dep.md").write_text("a", encoding="utf-8")
    (research / "R2-waiter.md").write_text("**Status: NOT DISPATCHED.**\n", encoding="utf-8")

    import factory.dispatch as D
    D.DEPENDS["R2"] = ["R1"]
    try:
        assert D.blocked_by("R2", research, answers) == []
    finally:
        D.DEPENDS.pop("R2", None)
