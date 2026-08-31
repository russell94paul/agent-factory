"""The provider seam — the only place that knows how an agent is actually started.

⭐ **This exists so that "how the agent runs" is one swappable ~40-line object rather than a
decision spread through the controller.** `deploy.py:230` hard-codes `--max-turns`,
`--max-budget-usd`, `--output-format stream-json` and `--model` against an argv surface that is
undocumented, unversioned and unpinned. That coupling is real either way; the seam makes it
*visible and replaceable* instead of load-bearing and invisible. When the Claude Agent SDK is
adopted as transport it goes behind this interface — below `GreenContract`, never as the thing
that decides an outcome.

⛔ **A provider never names its own verdict.** It returns what it observed and, crucially, whether
it was in a position to observe anything at all. `GreenContract` turns that into PASS / FAIL /
UNMEASURABLE / ERROR. A provider that returned "success" would be an agent grading itself with
extra steps, which is the single thing this estate is built to refuse (R3).

⚠ **`observable` is the field that carries the honesty, and it is not a detail.** The supervised
path — a human watching a terminal — genuinely cannot report an outcome to this process. That is
not a failure and it is not a pass: it is UNMEASURABLE, and the only way the controller can know
to say so is if the provider admits it could not look. Defaulting it to True would turn every
supervised launch into a silent PASS the moment somebody added an exit code.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .blueprint import AgentSpec
from .deploy import UNDETERMINED, LIMIT_NONE, AttemptLedger, RepoDeployer


@dataclass(frozen=True)
class AgentResult:
    """What a provider observed. Deliberately holds no verdict.

    `observable=False` means *this provider cannot see the outcome*, which is different from
    every field being empty because nothing happened. `dispatched` separates those two: a
    supervised run is dispatched-but-unobservable; a failed spawn is neither.
    """
    provider: str
    dispatched: bool
    observable: bool
    #: Is the agent STILL WORKING as this returns.
    #:
    #: ⚠ Not derivable from `observable`, and the controller tried to derive it for one commit.
    #: A supervised terminal is unobservable *and still running*; a dry run is unobservable *and
    #: finished*. Deriving one from the other made a dry run retain its lane claim, which then
    #: blocked the next launch of that ticket with "liveness could NOT be verified" — a deadlock
    #: caused by nothing at all. Two questions, two fields.
    in_flight: bool = False
    returncode: Optional[int] = None
    transcript: Optional[pathlib.Path] = None
    #: `deploy.LIMIT_HIT` / `LIMIT_NONE` / `UNDETERMINED` — "did it run out of room", asked
    #: separately from "did it work". Never guessed; UNDETERMINED is the honest default.
    limit: str = UNDETERMINED
    detail: str = ""
    duration_s: float = 0.0
    extra: Dict[str, Any] = field(default_factory=dict)

    def as_event(self) -> dict:
        return {"provider": self.provider, "dispatched": self.dispatched,
                "observable": self.observable, "in_flight": self.in_flight,
                "returncode": self.returncode,
                "transcript": str(self.transcript) if self.transcript else None,
                "limit": self.limit, "detail": self.detail[:2000],
                "duration_s": round(self.duration_s, 3), **self.extra}


class ProviderError(RuntimeError):
    """The provider could not dispatch at all. Distinct from an agent that ran and failed."""


# ---------------------------------------------------------------------------------- headless

class HeadlessProvider:
    """`claude -p` inside the worktree, with the caps the CLI enforces. Observable.

    Thin on purpose: `RepoDeployer.run_agent` already carries the caps, the transcript and the
    `AttemptLedger` — 140 of `deploy.py`'s 265 lines are that ledger, a cap that survives a
    restart, and no orchestration framework surveyed replaces it. This wraps it rather than
    reimplementing it.
    """

    name = "headless-cli"

    def __init__(self, repo_root: pathlib.Path, sessions_dir: pathlib.Path,
                 ledger: Optional[AttemptLedger] = None, dry_run: bool = False):
        self.deployer = RepoDeployer(pathlib.Path(repo_root), pathlib.Path(sessions_dir))
        self.ledger = ledger
        self.dry_run = dry_run

    def run(self, spec: AgentSpec, task: str, wt: pathlib.Path) -> AgentResult:
        t0 = time.time()
        try:
            dep = self.deployer.run_agent(spec, task, pathlib.Path(wt),
                                          ledger=self.ledger, dry_run=self.dry_run)
        except RuntimeError as exc:
            # The attempt cap refusing is NOT a dispatch. It is also not the agent failing — it
            # is the ledger doing its job, and the controller must be able to tell the two apart.
            raise ProviderError(str(exc)) from exc
        # ⚠ LIMIT stays UNDETERMINED on a non-zero exit, matching `deploy.note_outcome`. The CLI
        # gives no documented signal separating a cap-kill from a crash, and asserting "not a cap"
        # would make the retry advice confidently wrong. The Agent SDK's `ResultMessage` carries
        # `stop_reason`; adopting it is what converts this UNDETERMINED into a measurement.
        limit = LIMIT_NONE if dep.returncode == 0 else UNDETERMINED
        return AgentResult(
            provider=self.name, dispatched=True,
            # ⛔ A dry run is NOT observable, and the exit 0 it returns is the *recorder's*, not
            # an agent's. Reporting it as observable would send a clean returncode and a written
            # transcript into the contract from a run in which no agent ever executed — the
            # contract would then FAIL it for changing nothing, which reads as "the agent did no
            # work" when the truth is "no agent ran". Those need different remedies, so they get
            # different verdicts: a dry run is UNMEASURABLE.
            observable=not self.dry_run,
            in_flight=False,        # the subprocess has exited by the time run_agent returns
            returncode=dep.returncode, transcript=dep.transcript, limit=limit,
            detail=("dry run — the command and the prompt were recorded and no agent executed"
                    if self.dry_run else ""),
            duration_s=time.time() - t0,
            extra={"branch": dep.branch, "dry_run": self.dry_run})


# -------------------------------------------------------------------------------- supervised

class SupervisedProvider:
    """Spawn a terminal a human watches, and admit that the outcome is not visible from here.

    ⭐ **This is the path that actually runs today**, and routing it through the controller is the
    whole reason the controller is not a second unwired thing. `launch.py`'s three-question model
    says the supervised path is legitimate — a human wants to watch and type, and a watching human
    IS the cap, the reaper and the spend ceiling. The headless runner is a second path, not a
    replacement for this one.

    ⛔ It reports `observable=False`, always. The process this code runs in exits long before the
    human finishes; anything it claimed about the outcome would be invented. The run's verdict is
    therefore UNMEASURABLE at dispatch, and stays that way until something else observes it. That
    is the true state, and recording it is strictly better than recording nothing — which is what
    happens today.
    """

    name = "supervised-terminal"

    def __init__(self, spawn: Callable[[AgentSpec, str, pathlib.Path], Any]):
        #: A callable that starts the terminal and returns anything truthy. Injected rather than
        #: hard-coded so the tracker keeps owning its own `.ps1`/`wt` machinery, and so this can
        #: be tested without opening a window.
        self.spawn = spawn

    def run(self, spec: AgentSpec, task: str, wt: pathlib.Path) -> AgentResult:
        t0 = time.time()
        try:
            handle = self.spawn(spec, task, pathlib.Path(wt))
        except Exception as exc:                                   # noqa: BLE001
            raise ProviderError(f"{type(exc).__name__}: {exc}") from exc
        return AgentResult(
            provider=self.name, dispatched=True, observable=False,
            in_flight=True,         # the human is still typing; the claim must outlive this call
            returncode=None, transcript=None, limit=UNDETERMINED,
            detail=("a human is supervising this run; its outcome is not observable from the "
                    "dispatching process and must not be inferred"),
            duration_s=time.time() - t0,
            # ⚠ Recorded because it is not true of the other provider, and a reader comparing two
            # rows would otherwise assume the caps in the AgentSpec were enforced on both. They
            # are not: the supervised terminal runs an INTERACTIVE `claude`, which takes no
            # `--max-turns` or `--max-budget-usd` — the watching human is the cap, which is the
            # bargain `launch.py` names explicitly. The spec's caps are still recorded on
            # `agent_dispatched`, as the configuration that WOULD have bounded a headless run.
            extra={"handle": str(handle)[:200], "caps_enforced": False,
                   "caps_enforced_by": "the supervising human, not the CLI"})


# -------------------------------------------------------------------------------------- fake

class FakeProvider:
    """A scripted provider, for proving the seam is real.

    ⭐ **This is the evidence that the boundary exists, and it is deliberately not a second real
    provider.** A controller that drives a fake identically to the CLI has a boundary; a second
    real provider would be scope, and would prove less — it would still be running the same
    argv-shaped thing.
    """

    name = "fake"

    def __init__(self, results: Optional[List[AgentResult]] = None,
                 result: Optional[AgentResult] = None, raises: Optional[Exception] = None):
        self.calls: List[tuple] = []
        self.raises = raises
        self._queue = list(results or ([result] if result else []))

    def run(self, spec: AgentSpec, task: str, wt: pathlib.Path) -> AgentResult:
        self.calls.append((spec, task, pathlib.Path(wt)))
        if self.raises is not None:
            raise self.raises
        if self._queue:
            return self._queue.pop(0)
        return AgentResult(provider=self.name, dispatched=True, observable=True,
                           returncode=0, transcript=None, limit=LIMIT_NONE,
                           detail="fake provider default result")


def default_ledger_path() -> pathlib.Path:
    """The attempt ledger lives with the rest of the shared state, in the PRIMARY worktree.

    A per-worktree attempt counter is not a cap: the lane that keeps failing gets a fresh budget
    every time it is re-created. Same rule as `events.path()` and `runs.path()`.
    """
    from . import repo as _repo
    return _repo.data() / "attempts.json"
