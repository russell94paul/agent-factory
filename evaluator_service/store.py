"""The verdict store — write-once, and written by exactly one principal.

R3's design ends with the evaluator writing "the verdict directly to the trusted control store".
Two properties make a store trusted, and only two:

  WRITE-ONCE     a verdict already recorded cannot be replaced by a later, kinder one. Rollback
                 to a nicer answer is the cheapest attack on a certification scheme, and it needs
                 no cleverness at all if the store accepts overwrites.
  ONE WRITER     the graded party can read verdicts and cannot write them. ``factory.evaluator``
                 has no verb that writes; this module is imported only by the service.

The store lives **outside the repository** by default (``~/.agent-factory/verdicts``, override
with ``$AGENT_FACTORY_VERDICTS``). Inside the repo it would sit in the tree the graded agent edits
all day, and ``.data/`` is gitignored besides, so a verdict there would evaporate on a fresh
clone — a control store that disappears when you move machines was never a control store.

⚠ **The honest limit.** On one machine under one uid, "one writer" is a convention, not an
enforcement: anything that can run this Python can also write these files. That is precisely why
R3 ranks a separate local process 5th and "mostly theatre", and why the readiness gate reports the
deployment mode rather than letting a loopback URL read as isolation. Enforcement arrives with a
managed identity the agent sandbox does not hold — a deployment change, and this file does not
change with it.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
from typing import Any, Dict, List, Optional

#: Verdicts are addressed by run id, and a run id becomes a filename. Anything outside this
#: alphabet is rejected rather than sanitised: a submitter that can shape the path can overwrite
#: a neighbour's verdict, and silently repairing hostile input teaches you nothing.
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class StoreError(Exception):
    """The verdict could not be recorded, or the request to record it was malformed."""


class VerdictExists(StoreError):
    """A verdict for this run id is already recorded. Write-once means write once."""


def store_root() -> pathlib.Path:
    return pathlib.Path(
        os.environ.get("AGENT_FACTORY_VERDICTS", pathlib.Path.home() / ".agent-factory" / "verdicts")
    ).expanduser()


def _path(root: pathlib.Path, run_id: str) -> pathlib.Path:
    if not RUN_ID.match(run_id or ""):
        raise StoreError(
            f"run_id {run_id!r} is not a safe key — expected {RUN_ID.pattern}. Refusing rather "
            "than sanitising: a submitter that can shape the path can overwrite another verdict.")
    return root / f"{run_id}.json"


def record(payload: Dict[str, Any], root: Optional[pathlib.Path] = None) -> pathlib.Path:
    """Write one verdict. Raises :class:`VerdictExists` rather than replacing one."""
    root = root or store_root()
    root.mkdir(parents=True, exist_ok=True)
    path = _path(root, str(payload.get("run_id", "")))
    if path.exists():
        raise VerdictExists(
            f"a verdict for run {payload['run_id']!r} is already recorded at {path}. The store is "
            "write-once: re-scoring an artefact means a new run id, not a replaced verdict.")
    # x mode is the check: two services racing on the same run id cannot both believe they won.
    with open(path, "x", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return path


def read(run_id: str, root: Optional[pathlib.Path] = None) -> Dict[str, Any]:
    root = root or store_root()
    path = _path(root, run_id)
    if not path.is_file():
        raise StoreError(f"no verdict recorded for run {run_id!r}")
    return json.loads(path.read_text(encoding="utf-8"))


def recorded(root: Optional[pathlib.Path] = None) -> List[str]:
    """Run ids with a recorded verdict. An absent store is empty, not an error — nothing has been
    evaluated yet, which is a true and useful thing to be able to say."""
    root = root or store_root()
    if not root.is_dir():
        return []
    return sorted(p.stem for p in root.glob("*.json"))
