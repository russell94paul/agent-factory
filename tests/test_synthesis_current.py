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
    never, late = o["never_banked"], o["stale"]

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
    gap = o["never_banked"] + o["stale"]
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
    if not o["stale"]:
        return
    text = prompt()
    for rid in o["stale"]:
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
    """A synthesis record and answer set with known mention/banking relationships.

    `mentioned` — ids the synthesis names in its prose.
    `answers` — {id: banked}. A banked id is stamped with its hash and then LEFT ALONE; an
    unbanked one never was.

    ⛔ This fixture used to set modification times, because the check compared them. That was
    F93: a fresh checkout writes every file at once, so all eighteen real answers read as
    "filed after" on write-ordering alone.
    """
    from factory import synthesis as S

    ans = tmp_path / "answers"
    ans.mkdir()
    syn = tmp_path / "SYNTHESIS.md"
    syn.write_text("Synthesis. " + " ".join(mentioned), encoding="utf-8")

    for rid in answers:
        (ans / f"{rid}-answer-topic.md").write_text("x", encoding="utf-8")

    monkeypatch.setattr(S, "SYNTHESIS", syn)
    monkeypatch.setattr(S, "ANSWERS", ans)
    to_bank = [rid for rid, is_banked in answers.items() if is_banked]
    if to_bank:
        S.bank(to_bank)
    return S


def test_union_is_proved_on_a_synthetic_record(tmp_path, monkeypatch):
    """R18 banked-then-changed, R19 never banked — the exact 2026-08-29 shape.

    The old logic returned only R19 here. Both must reach the prompt.
    """
    S = _fixture(tmp_path, monkeypatch,
                 mentioned=["R18"],
                 answers={"R18": True, "R19": False})
    # R18 was banked, then its answer changed — the record now describes an earlier version.
    (tmp_path / "answers" / "R18-answer-topic.md").write_text("x, revised", encoding="utf-8")

    assert S.unsynthesised() == ["R19"], "only R19 is unmentioned"
    assert S.unreconciled() == ["R18", "R19"], "R18 changed after banking; R19 never banked"

    o = S.outstanding()
    assert o["never_banked"] == ["R19"]
    assert o["stale"] == ["R18"], "R18 is banked-but-changed and must not be dropped"

    text = S.prompt()
    assert "R18" in text and "R19" in text, "the prompt must name both or R18 is silently banked"
    assert "never banked R18" not in text, "R18 WAS banked — say that it changed"


def test_a_fully_current_record_is_reported_clean(tmp_path, monkeypatch):
    """The negative control: the check must be able to say 'nothing outstanding' AND mean it."""
    S = _fixture(tmp_path, monkeypatch, mentioned=["R1"], answers={"R1": True})
    assert S.unsynthesised() == [] and S.unreconciled() == []
    assert S.outstanding() == {"never_banked": [], "stale": [], "banked_but_unmentioned": []}
    assert "Nothing to reconcile" in S.prompt()


def test_a_fresh_checkout_does_not_invent_a_backlog(tmp_path, monkeypatch):
    """⭐ F93 itself, pinned so it cannot come back.

    `git worktree add` wrote SYNTHESIS.md and all eighteen answers five milliseconds apart, so
    every answer read as "filed after" and any fresh clone — including a first CI run — opened
    with eighteen phantom outstanding items. Here every mtime is moved AHEAD of the synthesis and
    the record must stay clean, because content is what was banked.
    """
    import os, time
    S = _fixture(tmp_path, monkeypatch, mentioned=["R1", "R2"],
                 answers={"R1": True, "R2": True})
    now = time.time()
    os.utime(S.SYNTHESIS, (now, now))
    for i, f in enumerate(sorted(S.ANSWERS.glob("R*.md"))):
        os.utime(f, (now + 0.005 + i * 0.001,) * 2)

    assert S.unreconciled() == [], "a checkout's write order must not create a backlog"
    assert S.outstanding()["stale"] == []


def test_the_hash_survives_a_line_ending_rewrite(tmp_path, monkeypatch):
    """⛔ Without this, the fix for F93 reproduces F93.

    `core.autocrlf` is `true` on this machine, so git rewrites line endings at checkout and the
    same committed answer has different BYTES in different working trees. Measured 2026-08-31 on
    R1-answer-eval-harness.md — 60,313 bytes / 0 CRLF in the primary, 61,186 / 873 in a worktree.
    A byte hash therefore made the verdict depend on which checkout you stood in, which is exactly
    what F93 says must not happen. It was caught by banking in a worktree and reading in the
    primary: 14 answers reported stale that had not changed.

    Only CRLF is collapsed, because that is the transformation git performs. A hash that ignored
    more than that would start missing real edits, which is the worse failure.
    """
    from factory import synthesis as S

    lf = tmp_path / "lf.md"
    crlf = tmp_path / "crlf.md"
    lf.write_bytes(b"line one\nline two\nline three\n")
    crlf.write_bytes(b"line one\r\nline two\r\nline three\r\n")

    assert lf.read_bytes() != crlf.read_bytes(), "the fixture must actually differ in bytes"
    assert S.answer_hash(lf) == S.answer_hash(crlf), (
        "the same content checked out with different line endings must bank identically, or the "
        "check is checkout-dependent — which is the defect it replaces")

    changed = tmp_path / "changed.md"
    changed.write_bytes(b"line one\nline two CHANGED\nline three\n")
    assert S.answer_hash(changed) != S.answer_hash(lf), (
        "normalising must not blind the hash to a real edit")
