"""Is the synthesis still current with the answers on disk?

`docs/research/SYNTHESIS.md` is the decision record — where the research passes agree, disagree,
and contradict something already built. It is written by hand, because reconciling six documents
is judgement and a script that concatenated them would be producing a *collation* while calling
itself a synthesis.

What is NOT judgement is whether it has fallen behind. It had: written 2026-08-21 covering R1–R4,
it did not mention R5 or R6 at all, and nothing said so. That is the same shape as the readiness
table advertising 25 gates against a set of 30 — a generated-from-reality document quietly
describing an earlier reality.

So there is no "synthesize" button. There is a measurement of the gap, a test that fails on it,
and a generated prompt for a human-or-session to do the actual reconciling.

⚠ **What this cannot check.** That the synthesis is *correct*, or that it engaged with an answer
rather than name-dropping it. Mentioning `R6` once satisfies this module. It catches the failure
that actually happened — an answer landing and the record never being touched — and nothing
subtler. Do not read a pass here as "the synthesis is good".
"""
from __future__ import annotations

import pathlib
import re
from typing import Dict, List

RESEARCH = pathlib.Path(__file__).resolve().parent.parent / "docs" / "research"
SYNTHESIS = RESEARCH / "SYNTHESIS.md"
ANSWERS = RESEARCH / "answers"

#: R5-answer-build-velocity.md -> "R5"
_STEM = re.compile(r"^(R\d+)-answer", re.I)


def filed() -> Dict[str, pathlib.Path]:
    """Research id -> its filed answer. Follow-up answers count as their own id's answer."""
    out: Dict[str, pathlib.Path] = {}
    if not ANSWERS.is_dir():
        return out
    for f in sorted(ANSWERS.glob("R[0-9]*.md")):
        m = _STEM.match(f.name)
        if m:
            out.setdefault(m.group(1).upper(), f)
    return out


def synthesised() -> List[str]:
    """Research ids the synthesis mentions at all. Deliberately a low bar — see the module note."""
    if not SYNTHESIS.is_file():
        return []
    text = SYNTHESIS.read_text(encoding="utf-8")
    return sorted({m.upper() for m in re.findall(r"\bR\d+\b", text)})


def unsynthesised() -> List[str]:
    """Answers on disk the synthesis has never mentioned. Empty is the healthy state."""
    seen = set(synthesised())
    return sorted(rid for rid in filed() if rid not in seen)


def _num(rid: str) -> int:
    return int(rid[1:])


def outstanding() -> Dict[str, List[str]]:
    """The two reasons an answer is unbanked, kept apart because they are different claims.

    ⛔ **Both must drive the prompt, and until 2026-08-29 only the first did.** `prompt()` used
    `unsynthesised()` alone and `session_prompt()` used ``unsynthesised() or unreconciled()`` —
    an `or`, so the *stronger* check was consulted only when the weaker one was already satisfied.
    On 2026-08-29 that produced a reconciliation session told to fold in R19 while the page beside
    it reported R14, R18 and R19 outstanding.

    That is worse than merely incomplete, because `unreconciled()` is a modification-time check:
    **any** write to SYNTHESIS.md clears it for **every** id, so a partial reconciliation marks
    the answers it never read as banked. R14 and R18 would have gone green having been read by
    nobody — the exact vacuous-verification failure `unreconciled()` was added to prevent, one
    level up and in the same file.

    The two lists are disjoint by construction: an id that was never mentioned is reported once,
    under the stronger reason.
    """
    never = sorted(unsynthesised(), key=_num)
    late = sorted((r for r in unreconciled() if r not in never), key=_num)
    return {"never_mentioned": never, "filed_after": late}


def prompt() -> str:
    """The paste text for actually doing the reconciling. Generated so it always names the real
    gap rather than whatever was outstanding when someone last wrote instructions down."""
    o = outstanding()
    never, late = o["never_mentioned"], o["filed_after"]
    gap = never + late
    if not gap:
        return ("SYNTHESIS.md mentions every filed answer, and none was filed after it was last "
                "written. Nothing to reconcile — but note that this only checks mentions and "
                "timestamps, not engagement.")

    def _row(rid: str, why: str) -> str:
        f = filed().get(rid)
        if f is None:
            return f"  - {rid}: (answer file not found under docs/research/answers/) — {why}"
        return (f"  - {rid}: docs/research/answers/{f.name} "
                f"({f.stat().st_size:,} bytes) — {why}")

    listing = "\n".join(
        [_row(r, "NEVER MENTIONED in the synthesis") for r in never]
        + [_row(r, "mentioned, but FILED AFTER the synthesis was last written — whatever the "
                   "record says about it predates the answer") for r in late])

    if never and late:
        why = (f"It has never mentioned {', '.join(never)}, and it was last written before "
               f"{', '.join(late)} landed.")
    elif never:
        why = f"It does not mention {', '.join(never)} at all."
    else:
        why = (f"It was last written before {', '.join(late)} landed, so anything it says about "
               "them predates the answers.")

    return f"""Update docs/research/SYNTHESIS.md, which is the decision record for this programme's
research. {why}

⛔ Fold in ALL of them in one pass. Writing this file updates its modification time, which clears
the "filed after" check for every id at once — so an answer left out of this pass is not merely
skipped, it is marked reconciled without having been read.

Answers to fold in:
{listing}

SYNTHESIS.md already has a structure — convergence, what we got right, what we got wrong,
corrections to things said in session, build order, what not to build, where the answers disagree,
what changes in this repo. Extend those sections rather than bolting on a new one per answer.

Hold to what the existing document does well, which is refusing to smooth:

  - Where a new answer DISAGREES with an earlier one, or with something already built or already
    said, record the disagreement and which evidence is stronger. Do not average them.
  - Label every recommendation by the basis its source gave it — OBSERVED in a comparable setting
    versus EXTRAPOLATED from human teams. R6 labelled its own; R5 partly did.
  - ⚠ Read docs/findings.md F7 first. One of these answers was produced under a FALSE CONSTRAINT
    that I wrote into its prompt, and it demonstrably changed the ranking. The synthesis has to
    say so, or it will carry the distortion forward as a finding.
  - Say what the answers could NOT settle. Both declared their own gaps; those belong in the
    record as much as the conclusions.

Then re-run `python -m pytest tests/test_synthesis_current.py` — it fails while any filed answer
goes unmentioned."""


def unreconciled() -> List[str]:
    """Answers filed AFTER the synthesis was last written — the check `unsynthesised()` cannot do.

    ⚠ `unsynthesised()` asks whether the synthesis *mentions* an id, and that is weaker than it
    looks. On 2026-08-23 R8's answer was filed while `SYNTHESIS.md` said, in three places, *"R8 is
    still outstanding"* and *"read them together when R8 lands"* — so the id was mentioned, in the
    future tense, and the gate went green over an answer nobody had read. A check that passes
    because a document talks about the thing it has not done is the vacuous-verification failure
    this repo exists to prevent.

    Modification time is a blunt instrument and deliberately so: it cannot be satisfied by writing
    the id anywhere, only by editing the synthesis after the answer landed.

    ⛔ **CORRECTION 2026-08-29.** This docstring claimed the check "over-reports (a whitespace edit
    clears it) rather than under-reports, which is the correct direction for a check — a false
    alarm costs a glance, a false pass costs the record." **That was true only while the sole
    actor was a human making an edit by hand, and the button 60 lines below falsifies it.** A
    dispatched reconciliation writes this file as part of a PARTIAL pass, which clears the check
    for every id including the ones it never opened. In the presence of that button the check
    under-reports systematically, in exactly the direction the docstring called unacceptable.

    It is not the timestamp that was wrong — it is that a partial write must never happen. So the
    guard now lives in `outstanding()`, which forces every unbanked id into the same pass. Read
    this check as "nothing landed after the last write", never as "each of these was read".
    """
    syn = SYNTHESIS if isinstance(SYNTHESIS, pathlib.Path) else pathlib.Path(SYNTHESIS)
    if not syn.is_file() or not ANSWERS.is_dir():
        return []
    when = syn.stat().st_mtime
    late = set()
    for f in ANSWERS.glob("R[0-9]*-answer*.md"):
        try:
            if f.stat().st_mtime > when:
                late.add(f.name.split("-")[0].upper())
        except OSError:
            continue
    return sorted(late, key=lambda r: int(r[1:]))


# ---------------------------------------------------------------------------------------------
# Launching the reconciliation, rather than only describing it.
#
# ⛔ The Research tab used to carry a comment saying there is deliberately NO synthesize button,
# "because synthesis is judgement, and a button that cannot exercise it would either fake it or
# do nothing". That reasoning was correct WHEN THE ONLY MECHANISM WAS A PASTE LOOP — and it is
# superseded by the same thing that superseded the paste loop for research passes: a button can
# now open a Claude Code session in this repo that actually does the work.
#
# The objection is answered rather than ignored. The button does not exercise judgement; it
# DISPATCHES judgement to an agent and records that it did, exactly as `/research/start` does. A
# reconciliation run locally is less independent than a human reading the answers cold, and the
# run note says so, because that is what tells the next reader how to weigh the record.
#
# ⚠ What it still cannot do is make the reconciliation GOOD. `unsynthesised()` checks mention and
# `unreconciled()` checks modification time; neither checks engagement, and a session that writes
# one sentence per answer clears both. That gap is unchanged by this button and is stated on the
# page rather than papered over.


def session_prompt() -> str:
    """What the launched reconciling session is told.

    Wraps :func:`prompt` — which already names the real gap — with the three rules a session
    working in a shared checkout needs, and the run-provenance stamp.
    """
    o = outstanding()
    gap = o["never_mentioned"] + o["filed_after"]
    return f"""Reconcile the research record.

{prompt()}

⛔ You may write EXACTLY ONE file: docs/research/SYNTHESIS.md. Do NOT `git add`, commit, stage, or
edit any other file — other sessions are working in this checkout right now, and the answers you
are reading are inputs, not drafts to tidy.

⛔ READ THE ANSWERS IN FULL before writing anything. The failure this reconciliation exists to end
is a record that talks about an answer nobody read: on 2026-08-23 SYNTHESIS.md said three times
that R8 was "still outstanding" while its answer sat filed on disk, and the mention-check went
green over it. Writing the id into a sentence is what a broken run looks like.

⛔ Do NOT smooth a disagreement. Where an answer contradicts an earlier one, or something already
built, record both and say which evidence is stronger and why. Averaging two findings produces a
third that nobody measured.

When you finish, append one line to the end of SYNTHESIS.md recording HOW this pass ran:
reconciled locally by an agent with repo access — stronger on file-and-line claims, less
independent than a reader coming to the answers cold. Both halves.

Outstanding when this session started: {', '.join(gap) if gap else 'nothing'}.
"""
