"""A research pass must not be startable on a guess, and a recorded dispatch must be visible.

The two properties worth a test here are the two that fail silently:

1. **An undeclared prompt gets no button.** `pass_type()` returning a guess would configure a run
   with the wrong lane count and search modality — named in the deep-research skill as "the main
   way a run wastes a day".
2. ⭐ **`record()` must move `dispatch.state()`.** The ledger and the status line answer different
   questions, and only the status line is what `dispatch` reads — so a dispatch that wrote only the
   ledger would be a recorded event nothing can see, which is the exact gap this module exists to
   close. The round-trip is asserted, not the write.
"""
from __future__ import annotations

import pathlib

import pytest

from factory import dispatch as disp
from factory import research_run as rr


HEADER = """# {rid} — a test prompt

**Status: NOT DISPATCHED.** Written 2026-08-23.
{decls}

## Run log

| Run | Date | Outcome |
|---|---|---|
| — | — | not yet dispatched |

## Body
"""


@pytest.fixture()
def estate(tmp_path, monkeypatch):
    """A throwaway repo root. Real prompts are never written to by a test."""
    (tmp_path / "docs" / "research" / "answers").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    monkeypatch.setattr(rr, "_root", lambda: tmp_path)
    return tmp_path


def write(root: pathlib.Path, rid: str, decls: str = "") -> pathlib.Path:
    p = root / "docs" / "research" / f"{rid}-topic.md"
    p.write_text(HEADER.format(rid=rid, decls=decls), encoding="utf-8")
    return p


def test_pass_type_is_declared_never_inferred(estate):
    write(estate, "R90", "**Pass type:** STRUCTURE_CRITIQUE")
    write(estate, "R91")
    # A prompt whose prose is full of "Claude Code" but declares nothing must still be UNDECLARED.
    write(estate, "R92", "This is an external survey of the field, obviously.")
    assert rr.pass_type("R90") == rr.STRUCTURE_CRITIQUE
    assert rr.pass_type("R91") == rr.UNDECLARED
    assert rr.pass_type("R92") == rr.UNDECLARED


def test_an_unrecognised_pass_type_is_not_a_licence_to_guess(estate):
    write(estate, "R90", "**Pass type:** VIBES_BASED")
    assert rr.pass_type("R90") == rr.UNDECLARED
    pl = rr.plan("R90", {"R90": disp.UNDISPATCHED})
    assert pl["eligible"] == rr.NOT_ELIGIBLE
    assert pl["action"] == ""


def test_undeclared_prompt_gets_no_action(estate):
    write(estate, "R91")
    pl = rr.plan("R91", {"R91": disp.UNDISPATCHED})
    assert pl["eligible"] == rr.NOT_ELIGIBLE
    assert "Pass type" in pl["why"]
    assert pl["action"] == ""


def test_dependency_gates_the_button(estate):
    write(estate, "R90", "**Pass type:** EXTERNAL_SURVEY\n**Depends on:** none")
    write(estate, "R91", "**Pass type:** STRUCTURE_CRITIQUE\n**Depends on:** R90")
    state = {"R90": disp.UNDISPATCHED, "R91": disp.UNDISPATCHED}

    assert rr.plan("R90", state)["eligible"] == rr.READY
    blocked = rr.plan("R91", state)
    assert blocked["eligible"] == rr.WAITING
    assert "R90" in blocked["why"], "the blocker must be NAMED, not merely counted"

    # Only ANSWERED clears it. A dependency that was merely *sent* has not produced anything to
    # audit, so IN_FLIGHT must still block.
    state["R90"] = disp.IN_FLIGHT
    assert rr.plan("R91", state)["eligible"] == rr.WAITING
    state["R90"] = disp.ANSWERED
    assert rr.plan("R91", state)["eligible"] == rr.READY


def test_every_declared_pass_is_runnable_and_carries_its_shape(estate):
    """⛔ The inverse of what this file first asserted. The original test enforced that only a
    CLAUDE_CODE pass could start, which encoded a wrong belief: the deep-research skill replaces
    the paste loop, so every pass runs here. What differs between them is not WHETHER they run but
    HOW -- lane count and independence risk -- so that is what is asserted now."""
    write(estate, "R90", "**Pass type:** EXTERNAL_SURVEY")
    write(estate, "R91", "**Pass type:** DECISION_REVIEW")
    state = {"R90": disp.UNDISPATCHED, "R91": disp.UNDISPATCHED}

    for r in ("R90", "R91"):
        assert rr.plan(r, state)["action"] == "run it here"

    survey, review = rr.plan("R90", state), rr.plan("R91", state)
    assert survey["risk"] == "LOW" and review["risk"] == "SEVERE", (
        "a pass reading our own conclusions must not be marked as independent as a web survey")
    assert survey["shape"] != review["shape"]


def test_a_pass_that_reads_our_own_material_is_told_to_go_blind_first(estate):
    """The independence instruction is not decoration -- it is the only thing a local run has that
    the paste loop did not, and it applies exactly to the two high-risk types."""
    write(estate, "R90", "**Pass type:** EXTERNAL_SURVEY")
    write(estate, "R91", "**Pass type:** STRUCTURE_CRITIQUE")
    state = {"R90": disp.UNDISPATCHED, "R91": disp.UNDISPATCHED}

    outside = rr.session_prompt(rr.plan("R90", state), estate / "x.txt")
    inside = rr.session_prompt(rr.plan("R91", state), estate / "x.txt")
    assert "BLIND-FIRST" not in outside
    assert "BLIND-FIRST" in inside


def test_the_session_prompt_never_paraphrases_the_brief(estate):
    """The brief is a file and the skill's rule is 'read the real file, not a summary'. A prompt
    that restated the question would be a second source of truth, and the two would drift."""
    p = write(estate, "R90", "**Pass type:** EXTERNAL_SURVEY")
    payload = rr.payload("R90")
    sp = rr.session_prompt(rr.plan("R90", {"R90": disp.UNDISPATCHED}), payload)
    assert str(payload) in sp, "it must point at the brief"
    assert "## Body" not in sp, "it must not inline the brief's content"
    assert "git add" in sp, "other sessions share this checkout; the ban must be stated"
    assert "exactly one file" in sp.lower()


def test_record_moves_dispatch_state(estate):
    """The round-trip. A ledger-only write would pass a weaker test and change nothing visible."""
    p = write(estate, "R90", "**Pass type:** EXTERNAL_SURVEY")
    research, answers = p.parent, p.parent / "answers"

    assert disp.state(research, answers)["R90"] == disp.UNDISPATCHED
    rr.record("R90", "EXTERNAL_SURVEY run in-repo", when="2026-08-23")
    assert disp.state(research, answers)["R90"] == disp.IN_FLIGHT, (
        "record() wrote the ledger but dispatch still cannot see the send")

    body = p.read_text(encoding="utf-8")
    assert "**Status: DISPATCHED 2026-08-23.**" in body
    assert "not yet dispatched" not in body, "the placeholder run-log row should be consumed"
    assert "| 1 | 2026-08-23 |" in body
    assert rr.ledger().is_file()


def test_a_second_record_appends_rather_than_overwriting(estate):
    p = write(estate, "R90", "**Pass type:** DECISION_REVIEW")
    rr.record("R90", "first", when="2026-08-23")
    rr.record("R90", "second", when="2026-08-24")
    body = p.read_text(encoding="utf-8")
    assert "| 1 | 2026-08-23 |" in body and "| 2 | 2026-08-24 |" in body
    assert body.count("**Status:") == 1, "the status line must be replaced, not duplicated"


def test_record_refuses_a_prompt_with_no_status_line(estate):
    p = estate / "docs" / "research" / "R90-topic.md"
    p.write_text("# R90\n\n## Run log\n\n| Run | Date | Outcome |\n|---|---|---|\n",
                 encoding="utf-8")
    with pytest.raises(rr.ResearchError, match="Status"):
        rr.record("R90", "x")


def test_start_refuses_when_not_ready(estate):
    write(estate, "R90", "**Pass type:** STRUCTURE_CRITIQUE\n**Depends on:** R91")
    write(estate, "R91", "**Pass type:** EXTERNAL_SURVEY")
    state = {"R90": disp.UNDISPATCHED, "R91": disp.UNDISPATCHED}
    with pytest.raises(rr.ResearchError, match="R91"):
        rr.start("R90", state)
    # and nothing was prepared or recorded on the way to refusing
    assert not (estate / ".data" / "research-prompts").exists()
    assert "NOT DISPATCHED" in (estate / "docs" / "research" / "R90-topic.md").read_text(
        encoding="utf-8")


def test_start_prepares_then_records(estate):
    write(estate, "R90", "**Pass type:** EXTERNAL_SURVEY")
    res = rr.start("R90", {"R90": disp.UNDISPATCHED})
    assert res["prompt_path"].is_file()
    assert "deep-research" in res["session_prompt"], "the session must be told to invoke the skill"
    assert res["prompt_path"].read_text(encoding="utf-8").startswith("# R90")
    assert "DISPATCHED" in (estate / "docs" / "research" / "R90-topic.md").read_text(
        encoding="utf-8")


def test_already_dispatched_is_not_re_offered(estate):
    write(estate, "R90", "**Pass type:** EXTERNAL_SURVEY")
    pl = rr.plan("R90", {"R90": disp.IN_FLIGHT})
    assert pl["eligible"] == rr.ALREADY
    with pytest.raises(rr.ResearchError):
        rr.start("R90", {"R90": disp.IN_FLIGHT})


def test_the_live_board_declares_every_unanswered_pass():
    """Against the REAL repo: an unanswered prompt with no declaration is a button we cannot draw.

    Not a style rule — `plan()` fails closed, so an undeclared pass silently loses its control and
    nobody finds out until they go looking for a button that was never there.
    """
    rows = [r for r in rr.board() if r["state"] != disp.ANSWERED]
    undeclared = [r["id"] for r in rows if r["pass_type"] == rr.UNDECLARED]
    assert not undeclared, f"unanswered prompts with no **Pass type:** declaration: {undeclared}"
