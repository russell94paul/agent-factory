import pytest

from factory.blueprint import AgentSpec, TeamSpec, load_team


def test_version_changes_with_config():
    a = AgentSpec("impl", "build", model="sonnet")
    b = AgentSpec("impl", "build", model="opus")
    assert a.version != b.version, "a model change must produce a new version"


def test_team_version_tracks_its_agents():
    t1 = TeamSpec("t", "p", [AgentSpec("a", "r", model="sonnet")])
    t2 = TeamSpec("t", "p", [AgentSpec("a", "r", model="opus")])
    assert t1.version != t2.version, "bumping an agent must uncertify the team"


def test_unsupported_topology_is_refused(tmp_path):
    p = tmp_path / "team.yaml"
    p.write_text("name: t\npurpose: p\ntopology: army_to_army\nagents: []\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_team(p)
