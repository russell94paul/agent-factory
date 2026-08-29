"""Put an agent in a repo, bounded.

Mirrors the pattern already proven in ``orchestrator/server.py``: an isolated git worktree, a CLI
agent launched inside it with a turn cap and a dollar cap, output streamed to a transcript.

⚠ Two bounds, and they are different things:
  * **Per-session** — ``--max-turns`` and ``--max-budget-usd``. Enforced by the CLI, per launch.
  * **Across sessions** — the re-dispatch counter, which MUST be persisted. The prior
    implementation kept it in a module-level dict, so every restart handed a permanently-failing
    stage a fresh budget and it re-dispatched all night. ``AttemptLedger`` below is on disk.
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .blueprint import AgentSpec


#: How many previous failures are replayed into a retry's prompt, newest first. Bounded on
#: purpose: the whole history of a permanently-failing stage would crowd out the task itself.
CONTEXT_ATTEMPTS = 3
#: Per-failure detail is truncated to this before injection, for the same reason.
CONTEXT_DETAIL_CHARS = 400


class AttemptLedger:
    """Persisted attempt counter, and the record of what went wrong each time.

    In-memory counters do not survive a restart, and a cap that resets on restart is not a cap.

    ⭐ It also keeps **why** each attempt ended, not only how many there were. A retry that
    knows only that it is attempt 2 repeats attempt 1 — the agent has no memory of the run
    before it, so the second dispatch is a fresh guess at the same problem. `context()` renders
    the prior failures for injection into the next prompt.

    ⚠ Kept here rather than joined to `factory.runs` deliberately. `runs` is keyed by *lane*,
    derived from a working directory; this is keyed by `agent:worktree`, which is what the cap
    is enforced on. Mapping one onto the other would be a guess, and a wrong key silently
    replays another agent's failures.

    ON-DISK FORMAT — backward compatible. A key's value is either a bare int (written by the
    counter-only version) or ``{"count": int, "attempts": [...]}``. Legacy ints are read as a
    count with no context rather than crashing or being discarded, because an existing ledger
    is holding a live cap and must keep holding it across the upgrade.
    """

    def __init__(self, path: Path, max_attempts: int = 2):
        self.path = Path(path)
        self.max_attempts = max_attempts
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._d = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}

    # ---------------------------------------------------------------- storage shape
    def _entry(self, key: str) -> dict:
        """Normalise either on-disk shape to a dict. Does not write."""
        raw = self._d.get(key)
        if raw is None:
            return {"count": 0, "attempts": []}
        if isinstance(raw, int):                       # legacy counter-only value
            return {"count": raw, "attempts": []}
        return {"count": int(raw.get("count", 0)), "attempts": list(raw.get("attempts", []))}

    def _flush(self) -> None:
        self.path.write_text(json.dumps(self._d, indent=2), encoding="utf-8")

    # ---------------------------------------------------------------- the cap
    def attempts(self, key: str) -> int:
        return self._entry(key)["count"]

    def exhausted(self, key: str) -> bool:
        return self.attempts(key) >= self.max_attempts

    def record(self, key: str, note: str = "") -> int:
        """Count one dispatch. Called BEFORE the agent runs, so the cap holds even on a crash."""
        e = self._entry(key)
        e["count"] += 1
        e["attempts"].append({
            "n": e["count"], "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "note": note, "outcome": None, "detail": "",
        })
        self._d[key] = e
        self._flush()
        return e["count"]

    # ---------------------------------------------------------------- the context
    def note_outcome(self, key: str, outcome: str, detail: str = "") -> None:
        """Attach how the most recent attempt ended. Safe to call when nothing was recorded."""
        e = self._entry(key)
        if not e["attempts"]:
            return
        e["attempts"][-1]["outcome"] = outcome
        e["attempts"][-1]["detail"] = (detail or "")[:CONTEXT_DETAIL_CHARS]
        self._d[key] = e
        self._flush()

    def failures(self, key: str) -> List[dict]:
        """Attempts that ended in anything other than success, newest first.

        An attempt with ``outcome is None`` counts as a failure: the process died before it
        could report, which is a failure the next attempt should know about. Treating an
        unreported outcome as a success is the collapse this repository exists to refuse.
        """
        att = self._entry(key)["attempts"]
        return [a for a in reversed(att) if a.get("outcome") != "ok"]

    def context(self, key: str) -> str:
        """Prior failures, rendered for prompt injection. Empty string when there are none."""
        fails = self.failures(key)[:CONTEXT_ATTEMPTS]
        if not fails:
            return ""
        lines = [
            "PREVIOUS ATTEMPTS AT THIS TASK FAILED. Read this before starting — you are not "
            "the first agent to try, and repeating a failed approach wastes an attempt against "
            "a cap you cannot raise."
        ]
        for a in fails:
            outcome = a.get("outcome") or "no outcome recorded (the process did not report back)"
            detail = (a.get("detail") or "").strip() or "no detail captured"
            lines.append(f"  · attempt {a.get('n')} ({a.get('at')}) — {outcome}: {detail}")
        lines.append(
            "Do something different, or explain in your first message why the same approach "
            "should now succeed."
        )
        return "\n".join(lines)


@dataclass
class Deployment:
    worktree: Path
    branch: str
    transcript: Path
    returncode: Optional[int] = None


class RepoDeployer:
    """Create an isolated worktree and run one agent inside it."""

    def __init__(self, repo_root: Path, sessions_dir: Path):
        self.repo_root = Path(repo_root)
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        gi = self.sessions_dir / ".gitignore"
        if not gi.exists():
            gi.write_text("*\n", encoding="utf-8")

    def create_worktree(self, branch: str) -> Path:
        wt = self.sessions_dir / branch.replace("/", "-")
        subprocess.run(["git", "worktree", "add", str(wt), "-b", branch],
                       cwd=str(self.repo_root), capture_output=True, text=True, check=True)
        return wt

    def remove_worktree(self, wt: Path, branch: str) -> None:
        subprocess.run(["git", "worktree", "remove", str(wt), "--force"],
                       cwd=str(self.repo_root), capture_output=True, text=True)
        subprocess.run(["git", "branch", "-D", branch],
                       cwd=str(self.repo_root), capture_output=True, text=True)

    def run_agent(self, spec: AgentSpec, task: str, wt: Path,
                  ledger: AttemptLedger | None = None, dry_run: bool = False) -> Deployment:
        key = f"{spec.name}:{wt.name}"
        if ledger and ledger.exhausted(key):
            raise RuntimeError(
                f"attempt cap reached for {key} ({ledger.attempts(key)}/{ledger.max_attempts}). "
                "Escalate to a human — do not raise the cap to get past this.")

        # Read the prior failures BEFORE recording this dispatch, so the current attempt is not
        # in its own context block.
        prior = ledger.context(key) if ledger else ""
        if ledger:
            ledger.record(key)

        full_prompt = f"{spec.prompt}\n\nTASK:\n{task}\n"
        if prior:
            full_prompt = f"{spec.prompt}\n\n{prior}\n\nTASK:\n{task}\n"

        transcript = self.sessions_dir / f"{spec.name}-{int(time.time())}.jsonl"
        cmd = ["claude", "-p", "--verbose", "--output-format", "stream-json",
               "--max-turns", str(spec.max_turns),
               "--max-budget-usd", str(spec.budget_usd),
               "--model", spec.model,
               "--dangerously-skip-permissions"]   # safe ONLY because wt is an isolated worktree
        if dry_run:
            # `prompt` is recorded, not just `task`: a dry run whose output omits the prompt
            # cannot show whether retry context was actually injected, which is the one thing
            # a dry run of a retry exists to check.
            transcript.write_text(
                json.dumps({"dry_run": True, "cmd": cmd, "task": task,
                            "prompt": full_prompt, "attempt": ledger.attempts(key) if ledger else None})
                + "\n", encoding="utf-8")
            if ledger:
                ledger.note_outcome(key, "ok", "dry run")
            return Deployment(wt, wt.name, transcript, returncode=0)

        stderr = ""
        with transcript.open("w", encoding="utf-8") as fh:
            proc = subprocess.Popen(cmd, cwd=str(wt), stdin=subprocess.PIPE,
                                    stdout=fh, stderr=subprocess.PIPE, text=True)
            _, stderr = proc.communicate(input=full_prompt)

        # Write back how it ended. Without this the ledger counts dispatches and knows nothing
        # about outcomes, so the next attempt starts as blind as this one did.
        if ledger:
            if proc.returncode == 0:
                ledger.note_outcome(key, "ok", "")
            else:
                ledger.note_outcome(key, f"exit {proc.returncode}",
                                    (stderr or "").strip() or "no stderr captured")
        return Deployment(wt, wt.name, transcript, returncode=proc.returncode)
