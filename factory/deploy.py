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
from typing import Optional

from .blueprint import AgentSpec


class AttemptLedger:
    """Persisted attempt counter. In-memory counters do not survive a restart, and a cap that
    resets on restart is not a cap."""

    def __init__(self, path: Path, max_attempts: int = 2):
        self.path = Path(path)
        self.max_attempts = max_attempts
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._d = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}

    def attempts(self, key: str) -> int:
        return self._d.get(key, 0)

    def exhausted(self, key: str) -> bool:
        return self.attempts(key) >= self.max_attempts

    def record(self, key: str) -> int:
        self._d[key] = self.attempts(key) + 1
        self.path.write_text(json.dumps(self._d, indent=2), encoding="utf-8")
        return self._d[key]


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
        if ledger:
            ledger.record(key)

        transcript = self.sessions_dir / f"{spec.name}-{int(time.time())}.jsonl"
        cmd = ["claude", "-p", "--verbose", "--output-format", "stream-json",
               "--max-turns", str(spec.max_turns),
               "--max-budget-usd", str(spec.budget_usd),
               "--model", spec.model,
               "--dangerously-skip-permissions"]   # safe ONLY because wt is an isolated worktree
        if dry_run:
            transcript.write_text(json.dumps({"dry_run": True, "cmd": cmd, "task": task}) + "\n",
                                  encoding="utf-8")
            return Deployment(wt, wt.name, transcript, returncode=0)

        with transcript.open("w", encoding="utf-8") as fh:
            proc = subprocess.Popen(cmd, cwd=str(wt), stdin=subprocess.PIPE,
                                    stdout=fh, stderr=subprocess.PIPE, text=True)
            proc.communicate(input=f"{spec.prompt}\n\nTASK:\n{task}\n")
        return Deployment(wt, wt.name, transcript, returncode=proc.returncode)
