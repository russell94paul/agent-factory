"""The dispatch check, and proof it can fire.

Two kinds of test here, and the split is deliberate.

The **live** test gates exactly one condition — a prompt whose answer has landed while it still
declares NOT DISPATCHED. That is a document contradicting the disk, and one of them is wrong.

It does **not** gate queue depth. Undispatched prompts are the intended workflow: R8, R9 and R10
were written in one session ahead of being sent. A test that failed on "3 prompts unsent" would
force a dispatch or a delete, and both are worse than simply knowing. So the queue is reported by
``python -m factory.dispatch`` and asserted nowhere.

The **synthetic** tests are the negative control. A check nobody has watched fire is decoration —
so each of the five states is constructed on disk and asserted, including the two failing ones.
"""

from __future__ import annotations

import pathlib

import pytest

from factory.dispatch import (
    ANSWERED,
    IN_FLIGHT,
    STALE_STATUS,
    UNDISPATCHED,
    UNKNOWN,
    prompts,
    render,
    stale_status,
    state,
    undispatched,
)


# --------------------------------------------------------------------------- live


def test_no_prompt_contradicts_its_own_answer():
    """An answer is filed but the prompt still says NOT DISPATCHED — fix the status line."""
    bad = stale_status()
    assert not bad, (
        f"{bad} have filed answers but still declare '**Status: NOT DISPATCHED.**'. "
        "The prompt is contradicting the disk. Update the status line in each prompt."
    )


def test_the_series_is_discovered_and_superseded_drafts_are_not_prompts():
    found = prompts()
    assert "R1" in found and "R10" in found, f"series not discovered: {sorted(found)}"
    # R3 has both a live prompt and R3-optimizer-sandbox-SUPERSEDED.md; it must resolve to one.
    assert "SUPERSEDED" not in found["R3"].stem.upper()


# ----------------------------------------------------------------- negative control


def _mk(tmp: pathlib.Path, name: str, status: str | None) -> None:
    body = f"# {name}\n\n"
    if status is not None:
        body += f"**Status: {status}** Written for a test.\n"
    (tmp / name).write_text(body, encoding="utf-8")


@pytest.fixture()
def world(tmp_path: pathlib.Path):
    research = tmp_path / "research"
    answers = research / "answers"
    answers.mkdir(parents=True)
    return research, answers


def test_every_state_can_be_produced(world):
    research, answers = world
    _mk(research, "R1-answered.md", "DISPATCHED 2026-01-01.")
    _mk(research, "R2-stale.md", "NOT DISPATCHED.")
    _mk(research, "R3-waiting.md", "NOT DISPATCHED.")
    _mk(research, "R4-inflight.md", "DISPATCHED 2026-01-02.")
    _mk(research, "R5-silent.md", None)
    (answers / "R1-answer-answered.md").write_text("x", encoding="utf-8")
    (answers / "R2-answer-stale.md").write_text("x", encoding="utf-8")

    got = state(research, answers)
    assert got == {
        "R1": ANSWERED,
        "R2": STALE_STATUS,
        "R3": UNDISPATCHED,
        "R4": IN_FLIGHT,
        "R5": UNKNOWN,
    }, got


def test_the_gated_condition_actually_fails(world):
    """⭐ The negative control. Manufacture the defect and assert the check catches it."""
    research, answers = world
    _mk(research, "R9-lying.md", "NOT DISPATCHED.")
    assert stale_status(research, answers) == []          # clean while no answer exists

    (answers / "R9-answer-lying.md").write_text("x", encoding="utf-8")
    assert stale_status(research, answers) == ["R9"], (
        "filing an answer beside a NOT DISPATCHED prompt did not trip the check — "
        "the instrument cannot fail, so a pass from it means nothing"
    )


def test_undispatched_is_reported_not_gated(world):
    research, answers = world
    _mk(research, "R8-unsent.md", "NOT DISPATCHED.")
    _mk(research, "R9-unsent.md", "NOT DISPATCHED.")
    assert undispatched(research, answers) == ["R8", "R9"]
    # Reported, and no assertion anywhere forbids it.
    assert "waiting on Paul" in render(research, answers)


def test_ids_sort_numerically_not_lexically(world):
    """R10 after R9, not between R1 and R2 — a lexical sort would misreport the queue."""
    research, answers = world
    for n in (1, 2, 9, 10):
        _mk(research, f"R{n}-x.md", "NOT DISPATCHED.")
    assert undispatched(research, answers) == ["R1", "R2", "R9", "R10"]


def test_an_empty_research_dir_is_empty_not_an_error(tmp_path):
    assert state(tmp_path, tmp_path) == {}
    assert "No research prompts found." in render(tmp_path, tmp_path)
