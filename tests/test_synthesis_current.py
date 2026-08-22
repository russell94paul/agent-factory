"""The decision record cannot silently fall behind the answers it is supposed to reconcile.

SYNTHESIS.md was written on 2026-08-21 covering R1-R4. R5 and R6 were answered the next day and
it did not mention either — same shape as the readiness table advertising 25 gates against a set
of 30. A record that describes an earlier reality, with nothing saying so.

⚠ This asserts MENTION, not engagement. Name-dropping R6 once satisfies it. It catches the failure
that actually happened and nothing subtler; a green here is not "the synthesis is good".
"""
from __future__ import annotations

from factory.synthesis import SYNTHESIS, filed, prompt, unsynthesised


def test_the_synthesis_exists():
    assert SYNTHESIS.is_file(), f"no decision record at {SYNTHESIS}"


def test_every_filed_answer_is_mentioned_in_the_synthesis():
    gap = unsynthesised()
    assert not gap, (
        f"SYNTHESIS.md does not mention {gap}, which have filed answers. "
        f"Run `python -c \"from factory.synthesis import prompt; print(prompt())\"` for the "
        "reconciling prompt.")


def test_the_prompt_names_the_actual_gap():
    """Generated, not written down once and left to rot — the failure it exists to catch."""
    gap = unsynthesised()
    text = prompt()
    for rid in gap:
        assert rid in text, f"the generated prompt does not name {rid}"
    if not gap:
        assert "Nothing to reconcile" in text
