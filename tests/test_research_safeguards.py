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


def _synth_and_answer(tmp_path, monkeypatch, answer_is_newer: bool):
    research = tmp_path / "research"
    answers = research / "answers"
    answers.mkdir(parents=True)
    syn = research / "SYNTHESIS.md"
    syn.write_text("mentions R7 everywhere", encoding="utf-8")
    ans = answers / "R7-answer-thing.md"
    ans.write_text("the answer", encoding="utf-8")

    import os
    base = syn.stat().st_mtime
    os.utime(ans, (base + 60, base + 60) if answer_is_newer else (base - 60, base - 60))

    monkeypatch.setattr(synthesis, "SYNTHESIS", syn)
    monkeypatch.setattr(synthesis, "ANSWERS", answers)
    return research


def test_unreconciled_fires_when_an_answer_lands_after_the_synthesis(tmp_path, monkeypatch):
    """The negative control. Without this the check is decoration."""
    _synth_and_answer(tmp_path, monkeypatch, answer_is_newer=True)
    assert synthesis.unreconciled() == ["R7"]


def test_unreconciled_is_quiet_once_the_synthesis_is_rewritten(tmp_path, monkeypatch):
    _synth_and_answer(tmp_path, monkeypatch, answer_is_newer=False)
    assert synthesis.unreconciled() == []


def test_a_future_tense_mention_does_not_satisfy_unreconciled(tmp_path, monkeypatch):
    """The exact R8 case: the id IS mentioned, and the answer is still unread.

    `unsynthesised()` passes here — that is the weakness. `unreconciled()` must not.
    """
    research = _synth_and_answer(tmp_path, monkeypatch, answer_is_newer=True)
    (research / "SYNTHESIS.md").write_text(
        "R7 is still outstanding. Read them together when R7 lands.", encoding="utf-8")
    import os
    ans = research / "answers" / "R7-answer-thing.md"
    syn = research / "SYNTHESIS.md"
    os.utime(ans, (syn.stat().st_mtime + 60,) * 2)

    monkeypatch.setattr(synthesis, "RESEARCH", research)
    assert "R7" in synthesis.unreconciled(), (
        "an answer filed after a synthesis that only promises to read it is NOT reconciled")


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
