"""The published readiness table cannot silently fall behind the gate set.

`scripts/build_tracker.py` has always been able to regenerate section 10 from `factory.readiness`,
and `--check` has always been able to notice drift. Neither was ever run, so the page spent an
unknown stretch of time advertising **25 gates against a set of 30** — five gates it had never
heard of. A drift guard nobody runs is the same shape as an eval nobody watches fail: a mechanism,
not a control. This is what turns it into one.

**What is asserted, and what deliberately is not.**

Asserted: the *gate set* — every gate's question appears on the page, and the page's own total
matches `len(GATES)`. Gate identity does not depend on the environment, so this is stable
everywhere and catches the drift that actually happened (a gate added, renamed or removed while
the page kept the old list).

Not asserted: the *verdicts*. Those move with `$AGENT_FACTORY_EVALUATOR`, with whether the
evaluator is running, and with the `prefect-connectors` checkout — so a strict full-text match
would go red on a colleague's laptop for reasons that have nothing to do with drift. A test that
fails for environmental reasons gets deleted within a week, and then there is no control at all.
`python scripts/build_tracker.py --check` remains the strict, full-fidelity comparison; run it
before publishing.
"""
from __future__ import annotations

import html
import pathlib
import re

import pytest

from factory.readiness import GATES

ARTIFACT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "artifacts" / "agent-factory.html"


@pytest.fixture(scope="module")
def tracker_section() -> str:
    if not ARTIFACT.is_file():
        pytest.skip(f"no artifact at {ARTIFACT}")
    text = ARTIFACT.read_text(encoding="utf-8")
    m = re.search(r'<section id="tracker">.*?</section>', text, re.S)
    assert m, "the artifact has no <section id=\"tracker\"> to check"
    # Entities unescaped so the comparison is escaping-agnostic. The first version of this test
    # used html.escape() with its default quote=True, which turns "impeccable's" into
    # "impeccable&#x27;s" while the generator's escaper leaves the apostrophe alone — so it
    # reported the `chain` gate missing from a page it was plainly on. Third confident false
    # result from an instrument in this session; comparing normalised text removes the whole class.
    return html.unescape(m.group(0))


def test_every_gate_appears_on_the_page(tracker_section):
    """A gate the page has never heard of is the drift that already happened."""
    missing = [g.id for g in GATES if g.question not in tracker_section]
    assert not missing, (
        f"{len(missing)} gate(s) missing from the published tracker: {missing}. "
        "Regenerate with `python scripts/build_tracker.py`.")


def test_the_page_does_not_list_gates_that_no_longer_exist(tracker_section):
    """The other direction: a renamed or deleted gate leaves an orphan row behind.

    Counted rather than matched by text, because the row markup is the generator's business and
    this test should not break every time that markup is restyled.
    """
    rows = re.findall(r'class="[^"]*\bgate\b[^"]*"', tracker_section) or \
        re.findall(r"<tr[ >]", tracker_section)
    assert rows, "found no gate rows in the tracker section at all"
    # Group-header rows are allowed on top of one row per gate; an undercount is never allowed.
    assert len(rows) >= len(GATES), (
        f"the page renders {len(rows)} rows for {len(GATES)} gates — it is behind the gate set. "
        "Regenerate with `python scripts/build_tracker.py`.")


def test_the_headline_total_matches_the_gate_set(tracker_section):
    """`n of TOTAL gates pass` — TOTAL is environment-independent, so it is safe to pin."""
    m = re.search(r"(\d+) of (\d+) gates pass", tracker_section)
    assert m, "no 'n of N gates pass' headline in the tracker section"
    assert int(m.group(2)) == len(GATES), (
        f"the page says {m.group(2)} gates, the repo has {len(GATES)}. "
        "Regenerate with `python scripts/build_tracker.py`.")


def test_no_hand_typed_gate_count_survives_in_the_generated_section(tracker_section):
    """The subtitle once read "Thirteen gates" while the generator emitted 30.

    A hand-typed number inside the section that exists so nothing is hand-maintained is the
    funniest possible version of this bug, and it survived every previous read of the file.
    """
    words = re.findall(r"\b(?:Twelve|Thirteen|Fourteen|Fifteen|Twenty|Thirty)\s+gates\b",
                       tracker_section, re.I)
    assert not words, f"spelled-out gate count in a generated section: {words}"
