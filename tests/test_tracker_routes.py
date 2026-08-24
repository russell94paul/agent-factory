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


# ------------------------------------------------------------------ the reconcile control


def test_the_synthesize_button_appears_only_when_there_is_something_to_reconcile(monkeypatch):
    """⛔ This page used to state in print that no synthesize button exists, "because synthesis is
    judgement, and a button that cannot exercise it would either fake it or do nothing". That held
    while the only mechanism was a paste loop. The button now DISPATCHES judgement to a session,
    the same move that replaced the research paste loop.

    Both states are asserted, because a control that is always enabled is not a control.
    """
    monkeypatch.setattr(lt.synth, "unsynthesised", lambda: ["R99"])
    monkeypatch.setattr(lt.synth, "unreconciled", lambda: [])
    # R99 has no file on disk, so the real prompt builders would raise looking it up. They are
    # exercised by their own tests; what is under test here is the CONTROL's presence.
    monkeypatch.setattr(lt.synth, "prompt", lambda: "stub reconciling prompt")
    monkeypatch.setattr(lt.synth, "session_prompt", lambda: "stub session prompt")
    # ⛔ Stub the CLAIM STORE too. Without this the test reads the real .data/claims and passes
    # only while no reconcile session happens to be running — which is a test coupled to the
    # machine's live state, i.e. green for a reason unrelated to what it asserts. Caught on
    # 2026-08-23 the first time a real reconcile held the claim during a suite run.
    monkeypatch.setattr(lt.claimlib, "task_holder", lambda k: (lt.claimlib.HELD_GONE, None))
    page = lt.render(datetime.datetime(2026, 8, 22, 12, 0), "research")
    assert 'action="/synthesize/start"' in page
    assert "reconcile it here" in page

    monkeypatch.setattr(lt.synth, "unsynthesised", lambda: [])
    page = lt.render(datetime.datetime(2026, 8, 22, 12, 0), "research")
    assert 'action="/synthesize/start"' not in page, (
        "the button is offered with nothing outstanding — it would open a session to do nothing"
    )
    assert "nothing outstanding" in page


def test_the_page_no_longer_claims_the_button_does_not_exist():
    """The old copy read 'There is no synthesize button: synthesis is judgement.' A page that
    denies the existence of one of its own controls is the same class of defect as the page that
    said it caches nothing while caching."""
    page = lt.render(datetime.datetime(2026, 8, 22, 12, 0), "research")
    assert "no synthesize button" not in page.lower()


def test_a_dry_synthesis_run_writes_nothing_and_opens_nothing(monkeypatch):
    """The dry-run lesson from `start_research_pass`, not re-introduced here.

    `dry` is checked BEFORE anything is prepared, so there is no file to assert the absence of —
    which is exactly the property. Popen is monkeypatched to prove no terminal is opened; a test
    that actually opened a window would not be a test.
    """
    import subprocess

    monkeypatch.setattr(lt.synth, "unsynthesised", lambda: ["R99"])
    monkeypatch.setattr(lt.synth, "unreconciled", lambda: [])
    monkeypatch.setattr(lt.synth, "session_prompt", lambda: "stub session prompt")
    opened = []
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: opened.append(a))

    ok, msg = lt.start_synthesis_pass(dry=True)
    assert ok and "DRY RUN" in msg and "nothing written" in msg
    assert not opened, "a dry run opened a terminal"
    # DELIBERATELY not asserting the session file is absent: it can legitimately pre-exist from an
    # earlier real run, so that check would be flaky in one direction and vacuous in the other.
    # The property under test is that `dry` returns BEFORE any preparation, and "no process was
    # spawned" is the observable that proves it.


def test_synthesis_refuses_when_there_is_nothing_outstanding(monkeypatch):
    monkeypatch.setattr(lt.synth, "unsynthesised", lambda: [])
    monkeypatch.setattr(lt.synth, "unreconciled", lambda: [])
    ok, msg = lt.start_synthesis_pass(dry=True)
    assert not ok and "nothing to reconcile" in msg


def test_the_button_is_disabled_while_a_reconcile_session_holds_the_claim(monkeypatch):
    """The third state, and the one the first version of these tests forgot.

    A control that renders enabled and then refuses on POST is a control lying about its own
    availability. With a gap outstanding AND the claim held, the button must render disabled and
    offer the release route — the same shape a held lane claim gets.
    """
    monkeypatch.setattr(lt.synth, "unsynthesised", lambda: ["R99"])
    monkeypatch.setattr(lt.synth, "unreconciled", lambda: [])
    monkeypatch.setattr(lt.synth, "prompt", lambda: "stub reconciling prompt")
    monkeypatch.setattr(lt.synth, "session_prompt", lambda: "stub session prompt")
    monkeypatch.setattr(lt.claimlib, "task_holder",
                        lambda k: (lt.claimlib.HELD_UNVERIFIED, {"since": "2026-08-23T18:04:35+00:00",
                                                                 "note": "reconciling R99"}))
    page = lt.render(datetime.datetime(2026, 8, 22, 12, 0), "research")
    assert 'action="/synthesize/start"' not in page, (
        "the button is offered while a session already holds the claim — a second one would write "
        "the same file and the loser's pass would vanish"
    )
    assert "a session is reconciling now" in page
    assert "/release-task/synthesis" in page, "no way out of a held claim is a wedged button"
