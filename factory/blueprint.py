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
        blob = json.dumps(
            {"team": self.name, "topology": self.topology, "contract": self.contract,
             "agents": sorted(a.version for a in self.agents)},
            sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:12]

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
