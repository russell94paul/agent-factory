import dataclasses

import pytest

from factory.blueprint import NOT_IDENTITY, AgentSpec, TeamSpec, load_team


def _distinct(field: str):
    """Two values of the right type for `field`, guaranteed different."""
    return {
        "name": ("t", "OTHER"),
        "purpose": ("p", "OTHER"),
        "topology": ("manager_to_agent", "manager_to_agent"),   # only one is legal; see below
        "contract": ("connector-green", "OTHER"),
        "repo": ("prefect-connectors", "OTHER"),
        "prohibition": ("must not deploy to production", ""),
    }[field]


def test_version_changes_with_config():
    a = AgentSpec("impl", "build", model="sonnet")
    b = AgentSpec("impl", "build", model="opus")
    assert a.version != b.version, "a model change must produce a new version"


def test_team_version_tracks_its_agents():
    t1 = TeamSpec("t", "p", [AgentSpec("a", "r", model="sonnet")])
    t2 = TeamSpec("t", "p", [AgentSpec("a", "r", model="opus")])
    assert t1.version != t2.version, "bumping an agent must uncertify the team"


def test_repo_is_part_of_the_team_identity():
    """R19 §6.1 — the regression. Predicted FAIL before the fix, and it did.

    A team certified against one repo must not carry that certification to another. This is the
    half of the defect that changes WHERE the agents can write.
    """
    t1 = TeamSpec("t", "p", [AgentSpec("a", "r")], repo="prefect-connectors")
    t2 = TeamSpec("t", "p", [AgentSpec("a", "r")], repo="clients")
    assert t1.version != t2.version, "repointing a team at another repo must uncertify it"


def test_team_prohibition_is_part_of_the_team_identity():
    """The other half, and the worse one: deleting the team's "must not" must uncertify it.

    A prohibition that can be removed without changing the version is not a control — it is a
    comment that the certification silently outlives.
    """
    t1 = TeamSpec("t", "p", [AgentSpec("a", "r")], prohibition="must not deploy to production")
    t2 = TeamSpec("t", "p", [AgentSpec("a", "r")], prohibition="")
    assert t1.version != t2.version, "dropping the team prohibition must uncertify it"


def test_every_identity_field_has_been_proved_able_to_move_the_hash():
    """The negative control, and the reason the deny-list exists.

    The two tests above pin the two fields that were actually broken. This one pins the
    *property*: every `TeamSpec` field not explicitly excused in `NOT_IDENTITY` must be shown —
    by construction, not by reading the source — to change the version. A future field added to
    the dataclass and forgotten in the hash fails here on the day it is added, rather than on the
    day a certification is laundered through it.

    ⭐ This is deliberately the same shape as
    `test_connector_contract.py::test_every_assertion_has_been_proved_able_to_fail`. A hash whose
    sensitivity to a field has never been demonstrated is the same species of claim as an
    assertion that has never been shown able to fail.
    """
    fields = [f.name for f in dataclasses.fields(TeamSpec)]
    identity = [f for f in fields if f not in NOT_IDENTITY]
    assert identity, "TeamSpec has no identity fields — the hash cannot mean anything"

    unmoved = []
    for f in identity:
        lo, hi = _distinct(f)
        if lo == hi:
            continue          # topology: only one value is legal, so it cannot be varied here
        base = {"name": "t", "purpose": "p", "agents": [AgentSpec("a", "r")]}
        if TeamSpec(**{**base, f: lo}).version == TeamSpec(**{**base, f: hi}).version:
            unmoved.append(f)

    assert not unmoved, (
        f"these TeamSpec fields do not change the version: {unmoved}. Either hash them or add "
        f"them to NOT_IDENTITY with the argument for why they are not identity.")


def test_not_identity_names_only_real_fields():
    """A stale exclusion is worse than none — it excuses a field nobody can find."""
    fields = {f.name for f in dataclasses.fields(TeamSpec)}
    unknown = [n for n in NOT_IDENTITY if n not in fields]
    assert not unknown, f"NOT_IDENTITY names fields TeamSpec does not have: {unknown}"


def test_unsupported_topology_is_refused(tmp_path):
    p = tmp_path / "team.yaml"
    p.write_text("name: t\npurpose: p\ntopology: army_to_army\nagents: []\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_team(p)
