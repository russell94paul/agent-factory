"""Operator answers to the blockers lanes declare up front.

`Lane.needs_paul` names a decision only a human can make — a credential approval, a fact they may
simply know. It is knowable before the session starts, so a session that launches and then blocks
on it has wasted the trip.

Answers live in `.data/operator/<lane>.json`, gitignored: an approval is a local act by one person
and committing it would assert that everyone who clones has given it.

⚠ An answer here is appended to the launched prompt. It is the one piece of browser-supplied text
that reaches a spawned agent — bounded to one labelled field per lane, rendered into the preview
before launch, and kept on disk so what was sent stays recoverable.
"""
from __future__ import annotations

import datetime as _dt
import json
import pathlib

from . import repo as _repo
import re
from typing import Dict, Optional

# ⚠ PRIMARY. Paul answers a lane's blocking question from the tracker in the primary
# checkout; the lane reads it from inside its worktree. Split those and the answer is
# written where the asker cannot see it. See factory/repo.py.
ROOT = _repo.data() / "operator"
_SAFE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

#: An answer longer than this is a conversation, not a decision, and belongs in the lane prompt.
MAX_LEN = 4000


class OperatorError(Exception):
    """The answer was not recorded, and the message says why."""


def answers() -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not ROOT.is_dir():
        return out
    for f in sorted(ROOT.glob("*.json")):
        try:
            out[f.stem] = json.loads(f.read_text(encoding="utf-8"))
        except Exception:                                          # noqa: BLE001
            out[f.stem] = {"text": "(answer file will not parse)", "at": "", "broken": True}
    return out


def get(lane: str) -> Optional[dict]:
    return answers().get(lane)


def record(lane: str, text: str) -> dict:
    if not _SAFE.match(lane or ""):
        raise OperatorError(f"{lane!r} is not a valid lane id")
    text = (text or "").strip()
    if not text:
        raise OperatorError("nothing to record — an empty answer is not an answer")
    if len(text) > MAX_LEN:
        raise OperatorError(f"{len(text):,} characters is over the {MAX_LEN:,} limit; that is a "
                            "conversation, not a decision — put it in the lane prompt instead")
    ROOT.mkdir(parents=True, exist_ok=True)
    payload = {"text": text, "at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")}
    (ROOT / f"{lane}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def clear(lane: str) -> bool:
    p = ROOT / f"{lane}.json"
    if not _SAFE.match(lane or "") or not p.exists():
        return False
    p.unlink()
    return True


def block(lane) -> str:
    """The text appended to a lane's prompt, or "" when nothing has been answered."""
    a = get(lane.id)
    if not a or a.get("broken"):
        return ""
    return (f"\n\nOPERATOR ANSWER — recorded {a['at']} in response to this lane's declared "
            f"blocker ({lane.needs_paul}):\n\n{a['text']}\n\nTreat it as Paul's decision. If it "
            "does not actually resolve the blocker, say so and stop rather than improvising "
            "around it.")
