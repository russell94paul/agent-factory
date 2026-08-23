"""A research pass must not be startable on a guess, and a recorded dispatch must be visible.

The two properties worth a test here are the two that fail silently:

1. **An undeclared prompt gets no button.** `runner()` returning a guess would put a "launch a
   session" control on a pass that runs in somebody else's product.
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


def test_runner_is_declared_never_inferred(estate):
    write(estate, "R90", "**Runs on:** CLAUDE_CODE")
    write(estate, "R91")
    # A prompt whose prose is full of "Claude Code" but declares nothing must still be UNDECLARED.
    write(estate, "R92", "This pass runs in a Claude Code session in this repo, obviously.")
    assert rr.runner("R90") == rr.CLAUDE_CODE
    assert rr.runner("R91") == rr.UNDECLARED
    assert rr.runner("R92") == rr.UNDECLARED


def test_an_unrecognised_runner_is_not_a_licence_to_guess(estate):
    write(estate, "R90", "**Runs on:** GEMINI_DEEP_RESEARCH")
    assert rr.runner("R90") == rr.UNDECLARED
    pl = rr.plan("R90", {"R90": disp.UNDISPATCHED})
    assert pl["eligible"] == rr.NOT_ELIGIBLE
    assert pl["action"] == ""


def test_undeclared_prompt_gets_no_action(estate):
    write(estate, "R91")
    pl = rr.plan("R91", {"R91": disp.UNDISPATCHED})
    assert pl["eligible"] == rr.NOT_ELIGIBLE
    assert "Runs on" in pl["why"]
    assert pl["action"] == ""


def test_dependency_gates_the_button(estate):
    write(estate, "R90", "**Runs on:** CLAUDE_RESEARCH\n**Depends on:** none")
    write(estate, "R91", "**Runs on:** CLAUDE_CODE\n**Depends on:** R90")
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


def test_only_claude_code_is_launchable(estate):
    write(estate, "R90", "**Runs on:** CLAUDE_CODE")
    write(estate, "R91", "**Runs on:** CLAUDE_RESEARCH")
    write(estate, "R92", "**Runs on:** DEEP_RESEARCH")
    state = {r: disp.UNDISPATCHED for r in ("R90", "R91", "R92")}
    assert rr.plan("R90", state)["launchable"] is True
    assert rr.plan("R91", state)["launchable"] is False
    assert rr.plan("R92", state)["launchable"] is False
    # And the labels must differ, or the button lies about two of the three.
    labels = {rr.plan(r, state)["action"] for r in ("R90", "R91")}
    assert len(labels) == 2


def test_record_moves_dispatch_state(estate):
    """The round-trip. A ledger-only write would pass a weaker test and change nothing visible."""
    p = write(estate, "R90", "**Runs on:** CLAUDE_RESEARCH")
    research, answers = p.parent, p.parent / "answers"

    assert disp.state(research, answers)["R90"] == disp.UNDISPATCHED
    rr.record("R90", "prepared for claude.ai Research", when="2026-08-23")
    assert disp.state(research, answers)["R90"] == disp.IN_FLIGHT, (
        "record() wrote the ledger but dispatch still cannot see the send")

    body = p.read_text(encoding="utf-8")
    assert "**Status: DISPATCHED 2026-08-23.**" in body
    assert "not yet dispatched" not in body, "the placeholder run-log row should be consumed"
    assert "| 1 | 2026-08-23 |" in body
    assert rr.ledger().is_file()


def test_a_second_record_appends_rather_than_overwriting(estate):
    p = write(estate, "R90", "**Runs on:** DEEP_RESEARCH")
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
    write(estate, "R90", "**Runs on:** CLAUDE_CODE\n**Depends on:** R91")
    write(estate, "R91", "**Runs on:** CLAUDE_RESEARCH")
    state = {"R90": disp.UNDISPATCHED, "R91": disp.UNDISPATCHED}
    with pytest.raises(rr.ResearchError, match="R91"):
        rr.start("R90", state)
    # and nothing was prepared or recorded on the way to refusing
    assert not (estate / ".data" / "research-prompts").exists()
    assert "NOT DISPATCHED" in (estate / "docs" / "research" / "R90-topic.md").read_text(
        encoding="utf-8")


def test_start_prepares_then_records(estate):
    write(estate, "R90", "**Runs on:** CLAUDE_RESEARCH")
    res = rr.start("R90", {"R90": disp.UNDISPATCHED})
    assert res["launchable"] is False
    assert res["prompt_path"].is_file()
    assert res["prompt_path"].read_text(encoding="utf-8").startswith("# R90")
    assert "DISPATCHED" in (estate / "docs" / "research" / "R90-topic.md").read_text(
        encoding="utf-8")


def test_already_dispatched_is_not_re_offered(estate):
    write(estate, "R90", "**Runs on:** CLAUDE_RESEARCH")
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
    undeclared = [r["id"] for r in rows if r["runner"] == rr.UNDECLARED]
    assert not undeclared, f"unanswered prompts with no **Runs on:** declaration: {undeclared}"
