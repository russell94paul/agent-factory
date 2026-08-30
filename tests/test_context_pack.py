"""Context is structure — with the two refusals that make that claim mean something.

The important test here is `test_lane_prompt_is_byte_identical`: the seam was allowed in on the
promise that it changes nothing an agent reads. A promise nobody tests is a comment.
"""
from __future__ import annotations

import pytest

from factory import context as ctx
from factory.lanes import LANES, PREAMBLE, POSTAMBLE


def test_a_ref_without_a_source_is_refused():
    """The load-bearing rule: a projection that cannot point back at its origin is a fork."""
    with pytest.raises(ctx.ContextError) as exc:
        ctx.ContextRef(kind=ctx.CLIENT, id="acme", source="  ", body="…")
    assert "source" in str(exc.value)


def test_current_without_a_checked_date_is_refused():
    """Freshness is a measurement. CURRENT with no date is an assertion wearing its label."""
    with pytest.raises(ctx.ContextError):
        ctx.ContextRef(kind=ctx.CLIENT, id="acme", source="wiki/x.md",
                       body="…", status=ctx.CURRENT)
    ok = ctx.ContextRef(kind=ctx.CLIENT, id="acme", source="wiki/x.md", body="…",
                        status=ctx.CURRENT, checked="2026-08-29")
    assert ok.status == ctx.CURRENT


def test_unknown_kind_status_and_confidence_are_all_refused():
    for kw in ({"kind": "ClientContexts"},
               {"status": "FRESH"},
               {"confidence": "PROBABLY"}):
        base = {"kind": ctx.CLIENT, "id": "a", "source": "wiki/x.md", "body": "b"}
        base.update(kw)
        with pytest.raises(ctx.ContextError):
            ctx.ContextRef(**base)


def test_unverified_is_the_default_not_current():
    r = ctx.ContextRef(kind=ctx.REPO, id="clients", source="repo:clients", body="…")
    assert r.status == ctx.UNVERIFIED


def test_stale_and_unverified_are_different_questions():
    p = ctx.ContextPack("p")
    p.add(ctx.ContextRef(kind=ctx.METRIC, id="acos", source="wiki/m.md", body="…",
                         status=ctx.STALE, checked="2026-01-01"))
    p.add(ctx.ContextRef(kind=ctx.METRIC, id="mer", source="wiki/m.md", body="…"))
    assert [r.id for r in p.stale()] == ["acos"]
    assert [r.id for r in p.unverified()] == ["mer"]
    assert "STALE" in p.summary() and "UNVERIFIED" in p.summary()


def test_a_pack_can_be_selected_by_kind_and_can_name_its_sources():
    """Selection and provenance are the two things a concatenated string cannot do."""
    p = ctx.pack("job:1", [
        ctx.ContextRef(kind=ctx.CLIENT, id="acme", source="wiki/clients/acme.md", body="a"),
        ctx.ContextRef(kind=ctx.METRIC, id="acos", source="wiki/metrics.md", body="b"),
        ctx.ContextRef(kind=ctx.METRIC, id="mer", source="wiki/metrics.md", body="c"),
    ])
    assert [r.id for r in p.of_kind(ctx.METRIC)] == ["acos", "mer"]
    assert p.sources() == ["wiki/clients/acme.md", "wiki/metrics.md"]   # deduped, ordered


def test_headers_carry_kind_source_and_freshness():
    r = ctx.ContextRef(kind=ctx.SOURCE, id="windsorai", source="wiki/tools/windsor.md",
                       body="x", status=ctx.CURRENT, checked="2026-08-29",
                       confidence=ctx.MEASURED)
    h = r.header()
    for expected in (ctx.SOURCE, "windsorai", ctx.CURRENT, ctx.MEASURED,
                     "2026-08-29", "wiki/tools/windsor.md"):
        assert expected in h


# ------------------------------------------------------------------- the promise the seam made

def test_lane_prompt_is_byte_identical_to_the_concatenation_it_replaced():
    """The seam was allowed in because it changes nothing an agent reads. Prove it.

    Recomputes the old expression directly rather than trusting `full_prompt()` to agree with
    itself — a test that called the new code twice would pass no matter what it produced.
    """
    from factory.operator import block
    for lane in LANES:
        expected = PREAMBLE + lane.prompt + POSTAMBLE + block(lane)
        assert lane.full_prompt == expected, lane.id      # a property, as its callers use it


def test_every_lane_pack_carries_a_source_for_every_ref():
    for lane in LANES:
        p = lane.context()
        assert p.refs, lane.id
        assert all(r.source.strip() for r in p.refs), lane.id
        assert p.of_kind(ctx.TASK), lane.id       # the lane's own instruction is addressable
