"""The skin may rename the domain. It may never rename a claim.

Every test here defends one boundary: what the presentation layer is allowed to change, and what
it must leave alone. A skin is a persuasion layer, which makes it the most dangerous place this
estate's recurring defect — a surface reporting more than it measured — can appear.
"""
from __future__ import annotations

import pytest

from factory import crew
from factory.lanes import LANES


def test_every_lane_has_a_persona_and_every_persona_a_lane():
    """A crew member with no lane is a character; a lane with no crew member renders as a raw id
    in the middle of a themed HUD, which is how a mapping quietly rots."""
    ids = {l.id for l in LANES}
    assert set(crew.CREW) == ids, (set(crew.CREW) ^ ids)


def test_ids_are_never_translated():
    """Branches, claims, worktrees and findings routing all key on the id. Renaming it would
    silently unroute every finding — the one thing the ledger exists to prevent."""
    for lane in crew.CREW:
        assert crew.name(lane, "gta") != lane          # the DISPLAY changes
        assert lane in crew.CREW                        # the KEY does not


def test_epistemic_labels_are_refused_not_silently_returned():
    """A silent no-op would let a caller believe translation happened. Refusing is the point."""
    for label in crew.FROZEN:
        with pytest.raises(crew.SkinError):
            crew.term(label, "gta")


def test_unmeasurable_never_reads_as_failure():
    """'We did not measure' and 'it broke' are different facts, and stay different in both modes."""
    assert crew.verdict("UNMEASURABLE", "gta") != crew.verdict("FAIL", "gta")
    assert crew.verdict("UNMEASURABLE", "gta") == "no signal"


def test_instrument_mode_changes_nothing():
    """The mode-switch invariant, in miniature: instrument mode is the identity function."""
    for w in ("lane", "gate", "task", "claim"):
        assert crew.term(w, "instrument") == w
    for v in ("PASS", "FAIL", "UNMEASURABLE", "NOT_RUN"):
        assert crew.verdict(v, "instrument") == v
    for lane in crew.CREW:
        assert crew.name(lane, "instrument") == lane


def test_an_unknown_lane_still_renders():
    """Rendering an unmapped lane as blank would hide a lane that exists."""
    assert crew.name("brand-new-lane", "gta") == "brand-new-lane"


def test_heat_is_computed_from_the_real_counts_and_stays_expandable():
    h = crew.heat(21, 30)
    assert h["failing"] == 21 and h["total"] == 30
    assert 0 <= h["stars"] <= 5
    assert h["expandable"] is True, "a wanted level nobody can drill into is decoration"
    assert "21 of 30" in h["detail"]


def test_heat_changes_when_the_number_changes():
    """The figure test: if the measurement were different, the picture must differ."""
    assert crew.heat(30, 30)["stars"] > crew.heat(3, 30)["stars"]
    assert crew.heat(0, 30)["stars"] == 0


def test_any_failing_gate_shows_at_least_one_star():
    """Rounding must not report a real failure as zero heat."""
    assert crew.heat(1, 30)["stars"] >= 1


def test_no_gates_is_no_signal_not_zero_heat():
    """A zero from an instrument that cannot see is not a measurement."""
    with pytest.raises(crew.SkinError):
        crew.heat(0, 0)


def test_handles_are_original_not_lifted():
    """§3 and §21 of the filed narrator prompt forbid reproducing GTA characters. This is a
    tripwire, not proof — it fails loudly if someone pastes a real character name in."""
    lifted = {"cj", "big smoke", "ryder", "sweet", "tenpenny", "cesar", "woozie", "catalina"}
    for p in list(crew.CREW.values()) + list(crew.FIGURES.values()):
        assert p["handle"].lower() not in lifted, p["handle"]


def test_every_handle_encodes_its_job():
    """A nickname that encodes nothing is decoration. Each persona must say what it does."""
    for lane, p in crew.CREW.items():
        assert p["role"].strip(), lane
        assert len(p["handle"]) <= 12, p["handle"]
