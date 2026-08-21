"""Load a :class:`ConnectorTarget` from a blueprint file.

The contract is code; what "green" means for one connector is data. Keeping them apart is what
lets the same twelve assertions judge every connector, and what lets a target be pinned in a
lockfile beside the code it judges.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .connector_contract import ConnectorTarget

_ALLOWED = set(ConnectorTarget.__dataclass_fields__)


def load_target(path: str | Path) -> ConnectorTarget:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    unknown = sorted(set(data) - _ALLOWED)
    if unknown:
        # A typo'd key that is silently ignored is an assertion that quietly stops being made.
        raise ValueError(f"{path}: unknown field(s) {unknown}")
    return ConnectorTarget(**data)
