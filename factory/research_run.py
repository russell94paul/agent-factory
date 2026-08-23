"""Starting a research pass from the board — and being honest that only one kind can be started.

`factory.dispatch` reports five states and says plainly what it cannot see: it **"cannot see whether
a prompt was ever actually pasted anywhere."** So a prompt only leaves `UNDISPATCHED` when a human
hand-edits its `**Status:**` line, and R8's header proved what that costs — it read `NOT DISPATCHED`
for a day after run 1 had actually been sent. This module closes that gap by making a dispatch a
**recorded event** rather than a remembered one.

⭐ **Three passes, three different meanings of "start", and one button label would lie about two of
them.** A launcher that announced the model it was running while running a different one is already
in this repo's findings ledger; a button saying "start" that silently only copied text would be the
same defect wearing a nicer coat.

    CLAUDE_CODE       a Claude Code session in this repo. Genuinely launchable — same machinery
                      as a lane: write the prompt to a file, open a titled terminal running it.
    CLAUDE_RESEARCH   claude.ai Research. NOT launchable from here. We can prepare the payload
                      and record that you sent it; the paste is yours.
    DEEP_RESEARCH     ChatGPT Deep Research, usually with an evidence pack. Same as above, plus
                      rebuilding the pack.
    UNDECLARED        the prompt does not say. **No button at all** — see below.

⛔ **Both facts are DECLARED in the prompt, never inferred.** A regex over prose guessing "this one
smells like Claude Code" is exactly the instrument that reports a confident wrong answer, and this
repo has three of those on record in one day. A prompt that does not declare gets no button and says
why. Fail closed.

    **Runs on:** CLAUDE_CODE
    **Depends on:** R17

⚠ **Eligibility is dependency-gated.** A pass whose declared dependency is not yet ANSWERED is shown
`WAITING` with the blocker named, and its button is disabled. R18 audits R17's recommendations
against our code, so running it first does not fail — it silently produces a worse answer, which is
harder to notice than a crash.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import re
import subprocess
from typing import Dict, List, Optional

from . import dispatch as _disp
from . import repo as _repo

CLAUDE_CODE = "CLAUDE_CODE"
CLAUDE_RESEARCH = "CLAUDE_RESEARCH"
DEEP_RESEARCH = "DEEP_RESEARCH"
UNDECLARED = "UNDECLARED"

RUNNERS = (CLAUDE_CODE, CLAUDE_RESEARCH, DEEP_RESEARCH)

READY, WAITING, NOT_ELIGIBLE, ALREADY = "READY", "WAITING", "NOT-ELIGIBLE", "ALREADY-SENT"

#: Where each runner is actually driven, for the UI to say so rather than imply it.
WHERE = {
    CLAUDE_CODE: "a Claude Code session in this repo",
    CLAUDE_RESEARCH: "claude.ai Research — paste it there",
    DEEP_RESEARCH: "ChatGPT Deep Research — paste it there",
}

_RID = re.compile(r"^R\d+$")
_RUNS_ON = re.compile(r"\*\*Runs on:\*\*\s*([A-Z_]+)")
_DEPENDS = re.compile(r"\*\*Depends on:\*\*\s*([^\n*]+)")
_STATUS = re.compile(r"\*\*Status:\s*([^*]+?)\s*\*\*")
_PLACEHOLDER = re.compile(r"^\|\s*—\s*\|\s*—\s*\|\s*not yet dispatched\s*\|\s*$", re.M)


class ResearchError(Exception):
    """The action was refused, and the message says why."""


def _root() -> pathlib.Path:
    return _repo.primary()


def ledger() -> pathlib.Path:
    return _root() / ".data" / "research-dispatch.jsonl"


def _prompt_path(rid: str) -> pathlib.Path:
    if not _RID.match(rid or ""):
        raise ResearchError(f"{rid!r} is not a research id")
    found = _disp.prompts(_root() / "docs" / "research").get(rid.upper())
    if found is None:
        raise ResearchError(f"no prompt file for {rid}")
    return found


def _head(path: pathlib.Path) -> str:
    """Only the header is parsed. A `**Runs on:**` written into a question halfway down the file is
    prose about the field, not a declaration about this prompt."""
    return path.read_text(encoding="utf-8", errors="replace")[:3000]


def runner(rid: str) -> str:
    """Where this prompt is meant to run, as DECLARED. UNDECLARED when it does not say, and when
    it names something we do not know — an unrecognised runner is not a licence to guess."""
    m = _RUNS_ON.search(_head(_prompt_path(rid)))
    val = (m.group(1).strip().upper() if m else "")
    return val if val in RUNNERS else UNDECLARED


def depends_on(rid: str) -> List[str]:
    """Declared prerequisites. `none` is a declaration; a missing line is also treated as none,
    because most passes genuinely have none and demanding the line everywhere would just get it
    written without thought."""
    m = _DEPENDS.search(_head(_prompt_path(rid)))
    if not m:
        return []
    raw = m.group(1).strip()
    if raw.lower().startswith("none"):
        return []
    return sorted({x.upper() for x in re.findall(r"R\d+", raw)})


def pack_builder(rid: str) -> Optional[pathlib.Path]:
    p = _root() / "scripts" / f"build_{rid.lower()}_pack.py"
    return p if p.is_file() else None


def plan(rid: str, state: Optional[Dict[str, str]] = None) -> dict:
    """Everything the UI needs to draw one row, and to refuse to draw a button it cannot honour."""
    rid = rid.upper()
    state = _disp.state() if state is None else state
    run, deps = runner(rid), depends_on(rid)
    unmet = [d for d in deps if state.get(d) != _disp.ANSWERED]
    cur = state.get(rid, _disp.UNKNOWN)
    builder = pack_builder(rid)

    if cur == _disp.ANSWERED:
        elig, why = NOT_ELIGIBLE, "already answered"
    elif cur in (_disp.IN_FLIGHT, _disp.STALE_STATUS):
        elig, why = ALREADY, "already dispatched — resending is a decision, not a click"
    elif run == UNDECLARED:
        elig, why = (NOT_ELIGIBLE,
                     "the prompt does not declare **Runs on:** — nothing here will guess it")
    elif unmet:
        elig, why = (WAITING,
                     "waits on " + ", ".join(f"{d} ({state.get(d, 'UNKNOWN')})" for d in unmet))
    else:
        elig, why = READY, ""

    return {
        "id": rid, "state": cur, "runner": run, "where": WHERE.get(run, "not declared"),
        "depends_on": deps, "unmet": unmet, "eligible": elig, "why": why,
        "launchable": run == CLAUDE_CODE,
        "pack": builder.name if builder else "",
        # The label is the honesty surface. Only one of these three actually starts anything.
        "action": ("launch a session" if run == CLAUDE_CODE else
                   "prepare & mark sent" if run in (CLAUDE_RESEARCH, DEEP_RESEARCH) else ""),
    }


def board(state: Optional[Dict[str, str]] = None) -> List[dict]:
    state = _disp.state() if state is None else state
    rows = [plan(rid, state) for rid in state]
    return sorted(rows, key=lambda r: int(r["id"][1:]) if r["id"][1:].isdigit() else 999)


def payload(rid: str) -> pathlib.Path:
    """Write the prompt where a launcher or a human can pick it up, verbatim.

    A copy on disk rather than an interpolated command line: `Get-Content -Raw` hands the whole
    file over as one argument, and interpolating a 20 KB prompt into a command line is how quoting
    silently truncates it (F10).
    """
    src = _prompt_path(rid)
    d = _root() / ".data" / "research-prompts"
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{rid.upper()}.txt"
    out.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return out


def build_pack(rid: str, timeout: int = 600) -> str:
    """Regenerate this pass's evidence pack, if it has one. Packs are gitignored and go stale."""
    b = pack_builder(rid)
    if b is None:
        return ""
    r = subprocess.run(["python", str(b)], cwd=str(_root()), capture_output=True,
                       text=True, timeout=timeout)
    if r.returncode != 0:
        raise ResearchError(f"{b.name} failed: {(r.stderr or r.stdout or '')[-200:]}")
    return b.name


def record(rid: str, how: str, when: Optional[str] = None) -> str:
    """Append to the ledger AND flip the prompt's own status line.

    Both, because they answer different questions and neither substitutes. The ledger is the
    durable machine-readable history; the status line is what `dispatch` actually reads, so a
    dispatch that only wrote the ledger would still render `UNDISPATCHED` — a recorded event
    nothing can see, which is the failure this module exists to end.
    """
    rid = rid.upper()
    day = when or datetime.date.today().isoformat()
    p = _prompt_path(rid)
    s = p.read_text(encoding="utf-8")

    m = _STATUS.search(s)
    if not m:
        raise ResearchError(f"{p.name} has no **Status:** line — refusing to invent one")
    s = s[:m.start()] + f"**Status: DISPATCHED {day}.**" + s[m.end():]

    row = f"| {_next_run_no(s)} | {day} | Dispatched from the readiness board — {how} |"
    if _PLACEHOLDER.search(s):
        s = _PLACEHOLDER.sub(row, s, count=1)
    else:
        s = _append_run_row(s, row)
    p.write_text(s, encoding="utf-8")

    lg = ledger()
    lg.parent.mkdir(parents=True, exist_ok=True)
    with lg.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                             "id": rid, "how": how, "runner": runner(rid)}) + "\n")
    return f"{rid} marked dispatched {day}"


def _next_run_no(s: str) -> int:
    nums = [int(x) for x in re.findall(r"^\|\s*(\d+)\s*\|", s, re.M)]
    return (max(nums) + 1) if nums else 1


def _append_run_row(s: str, row: str) -> str:
    """Insert after the Run log table's last row. Refuses rather than guessing a location."""
    i = s.find("## Run log")
    if i < 0:
        raise ResearchError("no '## Run log' section — refusing to guess where a row goes")
    lines = s[i:].splitlines(keepends=True)
    last = None
    for n, ln in enumerate(lines):
        if ln.lstrip().startswith("|"):
            last = n
        elif last is not None and ln.strip() == "":
            break
    if last is None:
        raise ResearchError("the Run log section holds no table")
    lines.insert(last + 1, row + "\n")
    return s[:i] + "".join(lines)


def start(rid: str, state: Optional[Dict[str, str]] = None) -> dict:
    """Prepare a pass for dispatch. **Never spawns** — the caller owns process creation, the same
    split `launch_command` uses, so a dry run cannot accidentally open a terminal.

    Returns {ok, note, prompt_path, launchable, plan}. Recording happens here, after the payload
    is on disk: a dispatch marked before its prompt was written would be a lie about a file that
    does not exist.
    """
    pl = plan(rid, state)
    if pl["eligible"] != READY:
        raise ResearchError(f"{pl['id']} is not ready: {pl['why']}")

    notes = []
    out = payload(pl["id"])
    notes.append(f"prompt written to {out.name}")
    if pl["pack"]:
        notes.append(f"rebuilt {build_pack(pl['id'])}")
    how = ("launched a Claude Code session" if pl["launchable"]
           else f"prepared for {pl['where']}")
    notes.append(record(pl["id"], how))
    return {"ok": True, "note": " · ".join(notes), "prompt_path": out,
            "launchable": pl["launchable"], "plan": pl}
