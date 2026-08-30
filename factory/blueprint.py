"""The config that IS the version.

An agent is not a name — it is a (prompt, model, effort, tools, retry policy) tuple. Change any
element and it is a different agent, whose certification does not transfer. The version id is a
hash of the config, so a silent upgrade cannot inherit a guarantee nobody re-checked.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass
class AgentSpec:
    name: str
    role: str
    model: str = "sonnet"
    effort: str = "medium"
    prompt: str = ""
    tools: List[str] = field(default_factory=list)
    max_turns: int = 50
    budget_usd: float = 3.0
    prohibition: str = ""      # every agent carries an explicit "must not"

    @property
    def version(self) -> str:
        blob = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:12]


#: The ONLY `TeamSpec` fields outside the version hash. Deny-list on purpose — see
#: `TeamSpec.version`. Adding a name here removes a field from the team's identity and must be
#: argued for; `tests/test_blueprint.py` fails the moment this list and the dataclass disagree.
NOT_IDENTITY = ("purpose", "agents")


@dataclass
class TeamSpec:
    name: str
    purpose: str
    agents: List[AgentSpec] = field(default_factory=list)
    topology: str = "manager_to_agent"     # the only one supported, deliberately
    contract: str = ""                     # name of the GreenContract that certifies it
    repo: str = ""
    prohibition: str = ""

    @property
    def version(self) -> str:
        """Every field except `purpose` and the agent list, plus the agents by their own version.

        ⚠ **This was wrong until 2026-08-29 and the wrongness was the dangerous kind.** The hash
        enumerated four keys by hand — team, topology, contract, agents — so `repo` and the
        team-level `prohibition` were outside it. A team certified against `prefect-connectors`
        under *"must not deploy to production"* kept the **identical** version when repointed at
        another repo with the prohibition deleted. Those are precisely the two edits that change
        blast radius, and the module whose docstring is "the config that IS the version" could not
        see either. Proven by discriminating test, result predicted before it ran (R19 §6.1).

        So the list is now a **deny-list, not an allow-list**: a new field is identity by default
        and must be argued out, because the failure mode of forgetting to add one is a
        certification that transfers silently. `purpose` is out because it is prose written for a
        human — changing it does not change what the team does. `agents` is out only because it is
        replaced by the agents' own version hashes on the next line.
        """
        rest = {k: v for k, v in asdict(self).items() if k not in NOT_IDENTITY}
        rest["agents"] = sorted(a.version for a in self.agents)
        return hashlib.sha256(json.dumps(rest, sort_keys=True).encode()).hexdigest()[:12]

    def pinned(self) -> Dict[str, str]:
        """The exact agent versions this team's certification is valid for."""
        return {a.name: a.version for a in self.agents}


SUPPORTED_TOPOLOGIES = {"manager_to_agent"}


def load_team(path: Path) -> TeamSpec:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    agents = [AgentSpec(**a) for a in raw.pop("agents", [])]
    team = TeamSpec(agents=agents, **raw)
    if team.topology not in SUPPORTED_TOPOLOGIES:
        raise ValueError(
            f"topology {team.topology!r} is not supported. Only {sorted(SUPPORTED_TOPOLOGIES)} "
            "exist until a second team demonstrably needs another.")
    return team
