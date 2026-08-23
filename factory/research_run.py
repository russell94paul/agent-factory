"""Running a research pass here, in the repo, instead of pasting it into somebody else's product.

⛔ **This module's first version was wrong about its central claim and the correction is the
point.** It declared three runners — `CLAUDE_CODE`, `CLAUDE_RESEARCH`, `DEEP_RESEARCH` — and let
only the first be started, on the reasoning that the other two are pasted into a web product by a
human. That reasoning was never checked. The `deep-research` skill already replaces the paste loop:
it has `WebSearch`/`WebFetch`, sweeps the open web first, and states outright that **the default is
that a pass runs here**. The taxonomy was inferred from what the prompts said about themselves,
which is exactly the *handoff-is-a-hypothesis* failure this estate keeps paying for.

So there is one runner — a Claude Code session in this repo — and every pass is launchable.

⭐ **What a prompt declares now is its PASS TYPE, because that is what configures the run.** The
skill's own table maps pass type to lane count, search modality and independence risk, and getting
it wrong is named there as "the main way a run wastes a day":

    EXTERNAL_SURVEY     3-5 parallel lanes, different search modalities, web-heavy   risk LOW
    SOURCE_CRAWL        1-2 deep on real source + a mandatory verifier               risk LOW
    STRUCTURE_CRITIQUE  1 deep with repo access + a web lane                         risk HIGH
    DECISION_REVIEW     1 deep, blind-first, + an outside-evidence lane              risk SEVERE
    NARROW_REPAIR       1 lane, tightly scoped, length-capped                        risk MEDIUM

⚠ **A local run trades independence for sources, and the record must say so.** The skill requires
the run log to record *how* a pass ran, because that decides how the next reader weighs it. A local
agent reading our repo, our conventions and our conclusions is pulled toward agreement; the outside
model at least started from nowhere. `record()` therefore stamps the runner, not just the date.

⛔ **Stamp on CONFIRMATION, not announcement.** The skill is explicit, and this repo has the scar: a
prompt read `NOT DISPATCHED` for a day after it had been sent. For a launched local run the two
coincide — the click *is* the start — which is precisely why the paste path was the wrong shape.

⚠ **Eligibility is dependency-gated.** A pass whose declared dependency is not yet ANSWERED shows
`WAITING` with the blocker named and its button disabled. R18 audits R17's recommendations against
our code; running it first does not fail, it silently produces a worse answer.

Both facts are DECLARED in the prompt header, never inferred. A prompt that does not declare gets
no button and says why. Fail closed.

    **Pass type:** EXTERNAL_SURVEY
    **Depends on:** none
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

EXTERNAL_SURVEY = "EXTERNAL_SURVEY"
SOURCE_CRAWL = "SOURCE_CRAWL"
STRUCTURE_CRITIQUE = "STRUCTURE_CRITIQUE"
DECISION_REVIEW = "DECISION_REVIEW"
NARROW_REPAIR = "NARROW_REPAIR"
UNDECLARED = "UNDECLARED"

PASS_TYPES = (EXTERNAL_SURVEY, SOURCE_CRAWL, STRUCTURE_CRITIQUE, DECISION_REVIEW, NARROW_REPAIR)

#: Everything runs in one place now. Kept as a named constant so the run log records it and a
#: future outside-model run can be recorded as something else.
IN_REPO = "IN_REPO"

READY, WAITING, NOT_ELIGIBLE, ALREADY = "READY", "WAITING", "NOT-ELIGIBLE", "ALREADY-SENT"

#: How each pass type is run, from the deep-research skill's own lane table. Shown on the button
#: row so the operator knows what they are about to spend before they spend it.
SHAPE = {
    EXTERNAL_SURVEY: "3-5 parallel lanes, different search modalities, web-heavy",
    SOURCE_CRAWL: "1-2 deep lanes on real source, plus a mandatory verifier",
    STRUCTURE_CRITIQUE: "1 deep lane with repo access, plus a web lane",
    DECISION_REVIEW: "1 deep lane, blind-first, plus an outside-evidence lane",
    NARROW_REPAIR: "1 tightly-scoped lane, length-capped",
}

#: How much the pass is pulled toward agreeing with us, same source. The two highest are the two
#: that read our own code and our own conclusions.
INDEPENDENCE_RISK = {
    EXTERNAL_SURVEY: "LOW", SOURCE_CRAWL: "LOW", STRUCTURE_CRITIQUE: "HIGH",
    DECISION_REVIEW: "SEVERE", NARROW_REPAIR: "MEDIUM",
}

_RID = re.compile(r"^R\d+$")
_PASS_TYPE = re.compile(r"\*\*Pass type:\*\*\s*([A-Z_]+)")
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
    """Only the header is parsed. A `**Pass type:**` written into a question halfway down the file
    is prose about the field, not a declaration about this prompt."""
    return path.read_text(encoding="utf-8", errors="replace")[:3000]


def pass_type(rid: str) -> str:
    """What SHAPE of run this is, as DECLARED. UNDECLARED when it does not say, and when it names
    something we do not know — an unrecognised pass type is not a licence to guess, because the
    type is what decides how many lanes run and what they search."""
    m = _PASS_TYPE.search(_head(_prompt_path(rid)))
    val = (m.group(1).strip().upper() if m else "")
    return val if val in PASS_TYPES else UNDECLARED


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
    ptype, deps = pass_type(rid), depends_on(rid)
    unmet = [d for d in deps if state.get(d) != _disp.ANSWERED]
    cur = state.get(rid, _disp.UNKNOWN)
    builder = pack_builder(rid)

    if cur == _disp.ANSWERED:
        elig, why = NOT_ELIGIBLE, "already answered"
    elif cur in (_disp.IN_FLIGHT, _disp.STALE_STATUS):
        elig, why = ALREADY, "already dispatched — resending is a decision, not a click"
    elif ptype == UNDECLARED:
        elig, why = (NOT_ELIGIBLE,
                     "the prompt does not declare **Pass type:** — nothing here will guess it, "
                     "because the type is what decides how the run is configured")
    elif unmet:
        elig, why = (WAITING,
                     "waits on " + ", ".join(f"{d} ({state.get(d, 'UNKNOWN')})" for d in unmet))
    else:
        elig, why = READY, ""

    return {
        "id": rid, "state": cur, "pass_type": ptype,
        "shape": SHAPE.get(ptype, "not declared"),
        "risk": INDEPENDENCE_RISK.get(ptype, ""),
        "depends_on": deps, "unmet": unmet, "eligible": elig, "why": why,
        "pack": builder.name if builder else "",
        # Every pass runs here now. The label says so plainly rather than implying a paste.
        "action": "run it here" if ptype != UNDECLARED else "",
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
                             "id": rid, "how": how, "runner": IN_REPO,
                             "pass_type": pass_type(rid)}) + "\n")
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
    """Prepare a pass and hand back everything needed to launch it. **Never spawns** — the caller
    owns process creation, the same split `launch_command` uses, so a dry run cannot open a
    terminal by accident.

    Recording happens here, AFTER the payload is on disk: a dispatch marked before its prompt was
    written would be a lie about a file that does not exist.
    """
    pl = plan(rid, state)
    if pl["eligible"] != READY:
        raise ResearchError(f"{pl['id']} is not ready: {pl['why']}")

    notes = []
    out = payload(pl["id"])
    notes.append(f"prompt written to {out.name}")
    if pl["pack"]:
        notes.append(f"rebuilt {build_pack(pl['id'])}")
    notes.append(record(pl["id"], f"{pl['pass_type']} run in-repo via the deep-research skill"))
    return {"ok": True, "note": " · ".join(notes), "prompt_path": out,
            "session_prompt": session_prompt(pl, out), "plan": pl}


def session_prompt(pl: dict, payload_path) -> str:
    """What the launched session is actually told.

    ⛔ It does NOT restate the brief — the brief is a file and the skill's own rule is *read the
    real file, not a summary of it*. Paraphrasing it here would be a second source of truth for the
    question, and the two would drift.

    The lines that are not obvious, and why each is here rather than left to the agent:

    · the pass type, because it decides lane count and search modality, and guessing it is named
      in the skill as the main way a run wastes a day;
    · the independence instruction for that type — a STRUCTURE_CRITIQUE or DECISION_REVIEW is
      reading our own code and our own conclusions, and is pulled toward agreeing with us;
    · exactly one file it may write, and an explicit ban on `git add`/commit, because other
      sessions are working in this checkout and a research agent editing a run-log table while
      another session rewrites the same file is a collision that has already happened here.
    """
    blind = ""
    if pl["pass_type"] in (STRUCTURE_CRITIQUE, DECISION_REVIEW):
        blind = (
            "\nBLIND-FIRST. Read the PRIMARY SOURCE and form your own view BEFORE "
            "reading what we concluded about it. Reversing that order is the difference "
            "between a review and a rubber stamp. Independence risk for this pass type "
            f"is {pl['risk']} - you are reading our own material.\n"
        )
    return f"""Run research pass {pl['id']}.

Invoke the deep-research skill and follow it literally.

  brief        {payload_path}   — read it IN FULL, obey it literally, do not summarise it
  pass type    {pl['pass_type']}
  shape        {pl['shape']}
  answer file  docs/research/answers/{pl['id']}-answer-<topic>.md
{blind}
⛔ You may write EXACTLY ONE file: the answer file above. Do NOT `git add`, commit, stage, or edit
any other file — other sessions are working in this checkout right now.

⛔ Verify every citation you lean on before promoting it to a finding. A prior pass cited a real
commit whose line numbers were wrong. "Substance confirmed, line numbers off" is a publishable
result; silent promotion is not.

Tier every claim OBSERVED / DERIVED / ASSUMED / MARKETED. A MARKETED claim may not be a design
premise. If something you need is not available, write NOT-SUPPLIED and name it — do not infer it.

When you finish, say in the answer how the pass ran: LOCAL SUBAGENTS, less independent than an
outside model and stronger on file-and-line claims. Both halves.
"""
