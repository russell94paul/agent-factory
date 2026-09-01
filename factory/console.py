"""Session console — read what a session said, and reply to it.

⛔ **This is NOT a terminal, and it must never be presented as one.** It cannot attach to a running
process's TTY: the sessions run as `claude` inside Windows Terminal tabs, and nothing in a browser
can take over that PTY. Calling this a terminal would be the same defect as a button that wears an
imperative verb and only navigates — a label promising a capability the thing does not have.

What it genuinely does, both halves measured on 2026-09-01:

    read     ~/.claude/projects/**/<session_id>.jsonl   — the session's own transcript.
             The registry's `session_id` IS the transcript filename: all 5 newest transcripts
             joined to a live registry row, 735 on disk.
    reply    factory.switchboard + local_tracker.quick_dispatch — the P0 mechanism that already
             routes a typed prompt to ONE named session and refuses rather than guess.

So it is a **conversation pane**. That is a smaller claim than a terminal and it is a true one.

## ⛔ Two things this module is careful about

**Transcripts are large.** The live one measured 6.4 MB. Reading it to show the last few messages
would make the page unopenable, so `tail_events` seeks from the END and parses only complete lines
inside a bounded window. It never loads the file.

**Transcripts can contain secrets.** They are a verbatim record of everything a session was told,
including anything pasted into it. This surface is reachable through a phone tunnel, so
:func:`redact` runs over every rendered string. It is a **best-effort reducer, not a guarantee** —
it catches the shapes we know (keys, tokens, connection strings, `Authorization:` headers) and
cannot catch a credential that looks like prose. That limitation is rendered on the page rather
than kept here.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
import re
import time
from typing import Dict, List, Optional

#: Where Claude Code writes transcripts. One directory per project slug, one .jsonl per session.
PROJECTS = pathlib.Path.home() / ".claude" / "projects"

#: How much of the tail to read. 256 KB holds far more than the pane shows even for long turns,
#: and bounds the read on a 6.4 MB file to something a page refresh can afford.
TAIL_BYTES = 256 * 1024

#: Messages rendered per pane. Small on purpose: a pane is for "what is it saying now", and the
#: full transcript is on disk for anyone who needs it.
PANE_EVENTS = 14

#: Per-message display cap. A single assistant turn can be tens of KB; four panes of that is a page
#: nobody can scroll.
MESSAGE_CHARS = 1400


# --------------------------------------------------------------------------- redaction

#: Shapes that are credentials wherever they appear. Ordered longest-first so a specific pattern
#: wins over a general one.
#:
#: ⚠ A REDUCER, not a guarantee. It cannot catch a password that looks like a word, and it is not
#: a reason to treat this surface as safe to share.
_SECRET_PATTERNS = (
    (re.compile(r"(?i)\b(sk-[A-Za-z0-9_-]{16,})"), "sk-***"),
    (re.compile(r"(?i)\b(gh[pousr]_[A-Za-z0-9]{20,})"), "gh*_***"),
    (re.compile(r"(?i)\b(xox[baprs]-[A-Za-z0-9-]{10,})"), "xox*-***"),
    # ⛔ `.+` to end of line, NOT `\S+`. As `\S+` this matched only the scheme word and left the
    # credential standing: `Authorization: Bearer eyJhbGci…` redacted to `Authorization: *** eyJhbGci…`
    # — a redactor that looks like it fired and publishes the token anyway. Caught by its own probe,
    # which is the entire reason the probe enumerates real credential shapes rather than one.
    (re.compile(r"(?i)(authorization\s*:\s*).+"), r"\1***"),
    (re.compile(r"(?i)\b(bearer\s+)([A-Za-z0-9._~+/-]{16,})"), r"\1***"),
    (re.compile(r"(?i)(-----BEGIN [A-Z ]*PRIVATE KEY-----)"), "***PRIVATE KEY REDACTED***"),
    (re.compile(r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|token|sfpw)"
                r"(\s*[=:]\s*)(\"?)([^\s\"',;]{6,})"), r"\1\2\3***"),
    (re.compile(r"(?i)\b([A-Za-z0-9_.-]+:)([^\s@/]{8,})(@[A-Za-z0-9_.-]+)"), r"\1***\3"),
    (re.compile(r"\b([A-Za-z0-9+/]{40,}={0,2})\b"), "***"),
)


def redact(text: str) -> str:
    """Reduce the obvious credential shapes. Best-effort; see the module docstring."""
    out = text or ""
    for pat, repl in _SECRET_PATTERNS:
        out = pat.sub(repl, out)
    return out


# --------------------------------------------------------------------------- reading


@dataclasses.dataclass
class Message:
    role: str          # user | assistant | system | tool
    text: str
    at: float = 0.0
    kind: str = ""     # a tool name, when the event is a tool use

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def transcript_path(session_id: str) -> Optional[pathlib.Path]:
    """The transcript for a session id, or None. Newest wins if a slug was reused.

    ⚠ Returns None rather than raising. A session with no transcript on disk is a real state —
    a brand-new session, or one whose project directory was cleaned — and it must render as
    "nothing recorded yet", never as an error.
    """
    sid = (session_id or "").strip()
    if not sid or not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", sid):
        return None
    if not PROJECTS.is_dir():
        return None
    hits = sorted(PROJECTS.rglob(f"{sid}.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return hits[0] if hits else None


def tail_events(path: pathlib.Path, limit: int = PANE_EVENTS) -> List[dict]:
    """The last `limit` parseable JSON lines, read from the END of the file.

    ⛔ Never reads the whole file — the live transcript measured 6.4 MB and four panes of that on
    every page refresh is a surface nobody can open. Seeks back `TAIL_BYTES`, discards the first
    (probably partial) line, and parses forward.
    """
    try:
        size = path.stat().st_size
        with path.open("rb") as fh:
            if size > TAIL_BYTES:
                fh.seek(size - TAIL_BYTES)
                fh.readline()               # drop the partial line the seek landed inside
            raw = fh.read()
    except OSError:
        return []
    out: List[dict] = []
    for line in raw.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out[-limit:]


def _text_of(content) -> tuple:
    """(text, tool-name) from Claude's content, which is a string OR a list of typed blocks."""
    if isinstance(content, str):
        return content, ""
    if not isinstance(content, list):
        return "", ""
    parts, tool = [], ""
    for b in content:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t == "text":
            parts.append(str(b.get("text") or ""))
        elif t == "thinking":
            continue                        # never rendered; it is not what the session SAID
        elif t == "tool_use":
            tool = str(b.get("name") or "tool")
            parts.append(f"[{tool}]")
        elif t == "tool_result":
            body = b.get("content")
            parts.append("[result] " + (body if isinstance(body, str) else "…"))
    return "\n".join(p for p in parts if p), tool


def messages(session_id: str, limit: int = PANE_EVENTS) -> List[Message]:
    """The tail of one session's conversation, redacted and capped for display."""
    path = transcript_path(session_id)
    if path is None:
        return []
    out: List[Message] = []
    for ev in tail_events(path, limit * 3):     # over-read: many rows are not messages
        msg = ev.get("message")
        if not isinstance(msg, dict):
            continue
        role = str(msg.get("role") or ev.get("type") or "")
        if role not in ("user", "assistant"):
            continue
        text, tool = _text_of(msg.get("content"))
        text = text.strip()
        if not text:
            continue
        at = 0.0
        ts = ev.get("timestamp")
        if isinstance(ts, str):
            try:
                import datetime as _dt
                at = _dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except ValueError:
                at = 0.0
        clipped = redact(text)[:MESSAGE_CHARS]
        if len(text) > MESSAGE_CHARS:
            clipped += f"\n… +{len(text) - MESSAGE_CHARS:,} chars"
        out.append(Message(role=role, text=clipped, at=at, kind=tool))
    return out[-limit:]


def pane(session_id: str, sessions_by_id: Dict[str, dict]) -> dict:
    """Everything one pane needs: identity, liveness, the tail, and what it cannot see."""
    row = sessions_by_id.get(session_id) or {}
    path = transcript_path(session_id)
    msgs = messages(session_id) if path else []
    return {
        "session_id": session_id,
        "title": str(row.get("topic") or row.get("name") or session_id)[:70],
        "state": row.get("state") or "NOT IN REGISTRY",
        "is_live": bool(row.get("is_live")),
        "cwd": row.get("cwd") or "",
        "needs": row.get("needs") or "",
        "messages": [m.to_dict() for m in msgs],
        # ⚠ Rendered on the pane. An empty pane and an unreadable one must not look identical.
        "basis": ("MEASURED" if path else "NOT-RECORDED"),
        "note": ("" if path else
                 "no transcript on disk for this session — it may be new, or its project "
                 "directory was cleaned. This is not evidence that nothing was said."),
        "age": (int(time.time() - path.stat().st_mtime) if path else None),
    }


#: Pane layouts the console offers. `cols`/`rows` drive a CSS grid; nothing else varies.
LAYOUTS = {
    "1":   {"n": 1, "cols": 1, "rows": 1, "label": "single"},
    "2h":  {"n": 2, "cols": 2, "rows": 1, "label": "2 side by side"},
    "2v":  {"n": 2, "cols": 1, "rows": 2, "label": "2 stacked"},
    "4":   {"n": 4, "cols": 2, "rows": 2, "label": "4 grid"},
}
DEFAULT_LAYOUT = "1"


def layout(name: str) -> dict:
    return LAYOUTS.get((name or "").lower(), LAYOUTS[DEFAULT_LAYOUT])
