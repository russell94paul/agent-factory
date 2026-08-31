"""The findings ledger has to stay a ledger, not become a notes file.

Four mandatory fields is the whole discipline: without MEASURED BY a finding is an opinion, and
without AFFECTS nobody downstream is shown it. Both failure modes are silent — the file still
looks full — so they are asserted rather than trusted.
"""
from __future__ import annotations

import re

from factory.findings import REQUIRED, by_lane, load, malformed, unattached
from factory.lanes import LANES


def test_the_ledger_has_entries():
    fs = load()
    assert fs, "docs/findings.md parsed to zero findings — the format changed under the parser"


def test_every_finding_carries_all_four_mandatory_fields():
    bad = malformed()
    assert not bad, (
        f"findings missing mandatory fields: {bad}. Required: {list(REQUIRED)}. "
        "An entry without MEASURED BY is an opinion; without AFFECTS nobody is shown it.")


def test_every_finding_reaches_at_least_one_lane():
    """A correction nobody will be shown is a correction that will be paid for twice.

    The likeliest cause of an orphan is an AFFECTS field written in prose that names no lane, no
    gate, and not 'every lane' — which is exactly how F5 was orphaned when this first ran.
    """
    orphans = unattached()
    assert not orphans, (
        f"findings attached to no lane: {orphans}. Name a lane id, a gate id, or 'every lane' "
        "in AFFECTS.")


def test_attachment_is_by_declared_id_not_by_keyword():
    """Guards the matcher against being loosened into fuzzy text search.

    A false attachment is worse than none — it trains people to skim the section — so a finding
    must only reach a lane it actually names.
    """
    mapping = by_lane()
    assert set(mapping) == {l.id for l in LANES}
    for lane in LANES:
        for f in mapping[lane.id]:
            text = f.affects.lower()
            named = (lane.id.lower() in text
                     or any(g in text for g in lane.gates)
                     or "every lane" in text or "all lanes" in text)
            assert named, f"{f.id} attached to {lane.id} without naming it: {f.affects[:80]!r}"


def test_a_design_finding_must_name_the_change_it_implies():
    """KIND=DESIGN with no CHANGES is an observation wearing a decision's clothes.

    A correction is spent once it has been read. A design consequence is not spent until it is
    built or deliberately refused, and the ledger could not tell those apart — so they were filed,
    admired, and never acted on. This is the rule that makes design_debt() a real list.
    """
    from factory.findings import _split
    bad = _split("### F999 — a design claim with no change\n\n"
                 "- **KIND** — DESIGN\n- **BELIEVED** — x\n- **ACTUALLY** — y\n"
                 "- **MEASURED BY** — z\n- **AFFECTS** — every lane\n")[0]
    assert "CHANGES" in bad.missing, (
        "a DESIGN finding without CHANGES must be rejected, or the field is decoration")

    good = _split("### F999 — a design claim that names its change\n\n"
                  "- **KIND** — DESIGN\n- **BELIEVED** — x\n- **ACTUALLY** — y\n"
                  "- **MEASURED BY** — z\n- **CHANGES** — build the thing\n"
                  "- **AFFECTS** — every lane\n")[0]
    assert not good.missing, f"a complete DESIGN finding must pass, got {good.missing}"


def test_an_unknown_kind_or_status_is_rejected():
    """A controlled vocabulary nobody enforces is a free-text field with extra steps."""
    from factory.findings import _split
    f = _split("### F998 — typo'd kind\n\n- **KIND** — DESIGNN\n- **STATUS** — MAYBE\n"
               "- **BELIEVED** — x\n- **ACTUALLY** — y\n- **MEASURED BY** — z\n"
               "- **AFFECTS** — every lane\n")[0]
    assert any("KIND=DESIGNN" in m for m in f.missing), f.missing
    assert any("STATUS=MAYBE" in m for m in f.missing), f.missing


# --------------------------------------------------------------------- ⭐ F86: the population
def test_every_findings_file_is_visible_to_the_ledger():
    """⛔ A file the parser cannot read is ABSENT, not malformed — and nothing else asks about it.

    `malformed()` and `unattached()` both iterate `load()`, so both answer their question only of
    the findings that already parsed. That left one state unasserted: a fragment the splitter
    drops entirely. F77-F84 sat in that state for a day — eight consecutive findings, including
    the four the boot-prompts README calls "the corrections that outlived every prompt above" —
    because their titles used `#` where `_HEADING` requires `###`. Both tests above stayed green
    over a ledger missing a third of itself.

    The population is derived from `ls docs/findings.d/` rather than listed here, for the same
    reason `test_hot_reload_covers_every_import` derives its own: a hand-maintained expectation
    drifts silently, which is the failure being guarded against.
    """
    from factory.findings import FRAGMENTS

    on_disk = {}
    for p in sorted(FRAGMENTS.glob("F*.md")):
        m = re.match(r"(F\d+)", p.name)
        if m:
            on_disk[m.group(1)] = p.name

    assert on_disk, f"no finding fragments found under {FRAGMENTS} — the layout moved"

    seen = {f.id for f in load()}
    invisible = sorted(on_disk[i] for i in set(on_disk) - seen)
    assert not invisible, (
        f"{len(invisible)} finding file(s) exist but do not reach the ledger: {invisible}. "
        "A fragment's title must be `### F<n> — <title>` (three hashes); `_HEADING` in "
        "factory/findings.py matches nothing else, and a file it cannot split is invisible to "
        "load(), by_lane(), malformed() and unattached() alike.")
