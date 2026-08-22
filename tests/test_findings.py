"""The findings ledger has to stay a ledger, not become a notes file.

Four mandatory fields is the whole discipline: without MEASURED BY a finding is an opinion, and
without AFFECTS nobody downstream is shown it. Both failure modes are silent — the file still
looks full — so they are asserted rather than trusted.
"""
from __future__ import annotations

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
