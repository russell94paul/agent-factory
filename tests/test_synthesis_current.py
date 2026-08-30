"""The decision record cannot silently fall behind the answers it is supposed to reconcile.

SYNTHESIS.md was written on 2026-08-21 covering R1-R4. R5 and R6 were answered the next day and
it did not mention either — same shape as the readiness table advertising 25 gates against a set
of 30. A record that describes an earlier reality, with nothing saying so.

⚠ This asserts MENTION, not engagement. Name-dropping R6 once satisfies it. It catches the failure
that actually happened and nothing subtler; a green here is not "the synthesis is good".
"""
from __future__ import annotations

from factory.synthesis import (
    SYNTHESIS, filed, outstanding, prompt, session_prompt, unreconciled, unsynthesised,
)


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


def test_outstanding_covers_both_checks_and_does_not_double_count():
    """The regression. Both reasons an answer is unbanked must reach the prompt.

    Before 2026-08-29 `prompt()` read `unsynthesised()` alone and `session_prompt()` read
    `unsynthesised() or unreconciled()` — an `or`, so the stronger check fired only when the
    weaker one was already clean. Measured that day: never-mentioned ['R19'], filed-after
    ['R14','R18','R19'], and the launched session was told about R19 only.
    """
    o = outstanding()
    never, late = o["never_mentioned"], o["filed_after"]

    assert not (set(never) & set(late)), (
        f"an id is reported under both reasons: {sorted(set(never) & set(late))}. They must be "
        "disjoint or the prompt lists it twice.")

    union = set(unsynthesised()) | set(unreconciled())
    assert set(never) | set(late) == union, (
        "outstanding() must cover the union of both checks; it is the only thing standing "
        "between a partial write and two answers marked banked without being read.")


def test_the_prompt_names_every_outstanding_answer():
    """⭐ The partial-write hazard, pinned.

    `unreconciled()` is a modification-time check, so ANY write to SYNTHESIS.md clears it for
    EVERY id. A prompt that omits an outstanding answer therefore does not merely skip it — the
    resulting write marks it reconciled. This test is the reason `outstanding()` exists.
    """
    o = outstanding()
    gap = o["never_mentioned"] + o["filed_after"]
    for text, label in ((prompt(), "prompt()"), (session_prompt(), "session_prompt()")):
        for rid in gap:
            assert rid in text, (
                f"{label} does not name {rid}, which is outstanding. Writing SYNTHESIS.md without "
                f"it would clear the timestamp check for {rid} anyway — banking an answer nobody "
                "read.")


def test_the_prompt_never_claims_an_id_is_unmentioned_when_it_is_merely_late():
    """Every sentence the generated prompt asserts has to be true.

    Widening the gap to the union is only safe if the wording widens with it. The old text said
    "It currently does not mention {gap} at all" — false for an id that IS mentioned and was
    merely filed afterwards, and a false statement in a generated brief is how a session gets
    sent looking for something that is already there.
    """
    o = outstanding()
    if not o["filed_after"]:
        return
    text = prompt()
    for rid in o["filed_after"]:
        assert f"does not mention {rid} at all" not in text
        assert f"never mentioned {rid}" not in text.lower()


# ---------------------------------------------------------------------------------------------
# The three tests above are LIVE-STATE tests: when nothing is outstanding they assert nothing.
# That is vacuous verification, and it bit immediately — the fix on 2026-08-29 could not be shown
# to fail against the old logic, because the reconciliation session closed the gap to empty while
# the fix was being written. A test whose ability to fail depends on the repo happening to be in
# the wrong state is not a control.
#
# So the union logic is also proved against a SYNTHETIC record, which is always in the state the
# test needs.

def _fixture(tmp_path, monkeypatch, mentioned, answers):
    """A synthesis record and answer set with known mention/mtime relationships.

    `mentioned` — ids the synthesis names. `answers` — {id: filed_before_synthesis}.
    """
    import os
    from factory import synthesis as S

    ans = tmp_path / "answers"
    ans.mkdir()
    syn = tmp_path / "SYNTHESIS.md"

    old, new = 1_000_000, 2_000_000
    for rid, before in answers.items():
        f = ans / f"{rid}-answer-topic.md"
        f.write_text("x", encoding="utf-8")
        os.utime(f, (old, old) if before else (new, new))
    syn.write_text("Synthesis. " + " ".join(mentioned), encoding="utf-8")
    os.utime(syn, ((old + new) // 2,) * 2)

    monkeypatch.setattr(S, "SYNTHESIS", syn)
    monkeypatch.setattr(S, "ANSWERS", ans)
    return S


def test_union_is_proved_on_a_synthetic_record(tmp_path, monkeypatch):
    """R18 mentioned-but-late, R19 never-mentioned — the exact 2026-08-29 shape.

    The old logic returned only R19 here. Both must reach the prompt, because the write that
    banks R19 clears the timestamp check for R18 too.
    """
    S = _fixture(tmp_path, monkeypatch,
                 mentioned=["R18"],                    # named, but named before its answer landed
                 answers={"R18": False, "R19": False})  # both filed AFTER the synthesis

    assert S.unsynthesised() == ["R19"], "only R19 is unmentioned"
    assert S.unreconciled() == ["R18", "R19"], "both were filed after the synthesis"

    o = S.outstanding()
    assert o["never_mentioned"] == ["R19"]
    assert o["filed_after"] == ["R18"], "R18 is late-but-mentioned and must not be dropped"

    text = S.prompt()
    assert "R18" in text and "R19" in text, "the prompt must name both or R18 is silently banked"
    assert "does not mention R18 at all" not in text, "R18 IS mentioned — say why it is late"


def test_a_fully_current_record_is_reported_clean(tmp_path, monkeypatch):
    """The negative control: the check must be able to say 'nothing outstanding' AND mean it."""
    S = _fixture(tmp_path, monkeypatch, mentioned=["R1"], answers={"R1": True})
    assert S.unsynthesised() == [] and S.unreconciled() == []
    assert S.outstanding() == {"never_mentioned": [], "filed_after": []}
    assert "Nothing to reconcile" in S.prompt()
