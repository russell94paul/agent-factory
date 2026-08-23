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


def prompt() -> str:
    """The paste text for actually doing the reconciling. Generated so it always names the real
    gap rather than whatever was outstanding when someone last wrote instructions down."""
    gap = unsynthesised()
    if not gap:
        return ("SYNTHESIS.md mentions every filed answer. Nothing to reconcile — but note that "
                "this only checks mentions, not engagement.")
    listing = "\n".join(f"  - {rid}: docs/research/answers/{filed()[rid].name} "
                        f"({filed()[rid].stat().st_size:,} bytes)" for rid in gap)
    return f"""Update docs/research/SYNTHESIS.md, which is the decision record for this programme's
research. It currently does not mention {', '.join(gap)} at all.

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
    the id anywhere, only by editing the synthesis after the answer landed. It over-reports (a
    whitespace edit clears it) rather than under-reports, which is the correct direction for a
    check — a false alarm costs a glance, a false pass costs the record.
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
