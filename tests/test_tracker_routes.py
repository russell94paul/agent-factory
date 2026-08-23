"""The tracker's three routes render, and each shows only its own tab.

Added when the page was split into /, /lanes and /research. A route that silently renders the
wrong tab, or throws, is invisible until someone opens it — and the whole point of the split was
that `/research` must not pay for a 30-probe measurement it does not use.

These call render() directly rather than over HTTP: the transport is stdlib and boring, the
routing table is the thing that can be wrong.
"""
from __future__ import annotations

import datetime

import pytest

from scripts import local_tracker as lt  # noqa: E402


@pytest.fixture(scope="module")
def research_page() -> str:
    return lt.render(datetime.datetime(2026, 8, 22, 12, 0), "research")


def test_every_tab_is_reachable_from_every_tab():
    """A nav that loses a tab strands it — nothing else links to /research."""
    page = lt.render(datetime.datetime(2026, 8, 22, 12, 0), "research")
    for _, href, label in lt.TABS:
        assert f'href="{href}"' in page, f"nav is missing {label} ({href})"


def test_research_renders_without_measuring(research_page, monkeypatch):
    """The reason the split exists. `measure()` shells out to pytest and factory.certify, so a
    research page that measured would cost a full test run to read a prompt."""
    called = []
    monkeypatch.setattr(lt, "measure", lambda *a, **k: called.append(1) or [])
    lt.render(datetime.datetime(2026, 8, 22, 12, 0), "research")
    assert not called, "the research tab called measure() — that is the cost the split removed"


def test_each_tab_shows_only_its_own_content(research_page):
    """The tab must identify itself whether or not anything is outstanding.

    The first version of this test asserted the *pending-prompts* header, which vanished the hour
    both prompts got answered — the guard rendered nothing and the tab became a blank page under
    a nav link. What should always hold is that the tab says what it is; what is conditional is
    whether it has work to offer.
    """
    assert "Run a research pass" in research_page or "<h1>Research</h1>" in research_page, (
        "the research tab rendered neither outstanding prompts nor an empty state")
    assert "Start here" not in research_page, "lane content leaked onto the research tab"


def test_a_filed_answer_is_still_visible_somewhere(research_page):
    """Answered work must not become invisible work.

    The prompt drops off the outstanding list once answered — that is the self-clearing behaviour
    — but the answer itself is the thing most worth re-reading, so it has to remain findable.
    """
    import pathlib
    adir = pathlib.Path(lt.FACTORY) / "docs" / "research" / "answers"
    filed = sorted(adir.glob("R[0-9]*-answer*.md"))
    if not filed:
        pytest.skip("no answers filed yet")
    assert "<h1>Answered</h1>" in research_page
    for a in filed:
        assert a.name in research_page, f"{a.name} is filed but not listed on the research tab"


def test_the_research_tab_offers_only_unanswered_prompts(research_page):
    """R5 has an answer on disk and R6 does not, so the page must offer R6 and not R5.

    This is the behaviour that makes the tab self-clearing: file an answer and the prompt stops
    being advertised, with no list to maintain by hand.
    """
    import pathlib

    from factory.dispatch import prompts

    rdir = pathlib.Path(lt.FACTORY) / "docs" / "research"
    adir = rdir / "answers"
    # Ask the canonical function which files are prompts rather than re-globbing. This test used
    # its own `R[0-9]*.md` and so counted a generated evidence pack as a prompt and demanded the
    # tab advertise it. Three places encoded "what is a prompt"; now one does.
    for f in prompts(rdir).values():
        stem = f.name.split("-")[0]
        answered = any(a.name.startswith(f"{stem}-answer") for a in adir.glob("*.md"))
        offered = f'data-copy="rs-{f.stem}"' in research_page
        assert offered != answered, (
            f"{f.name}: answered={answered} but offered={offered} — the research tab should "
            "advertise exactly the prompts with no filed answer")
