"""RunController — the assembly line. Ticket in, verdict and a durable record out.

Every part below already existed and was tested. **Nothing called them in order**, which is why
`presets`, `worktrees`, `claims`, `deploy` and `runs` sat at zero consumers between them. This
module is the caller, and it is deliberately thin: its job is sequencing and honesty, not
cleverness.

    ticket
      -> presets            which configurations were eligible, and which was taken   [the choice]
      -> blueprint          AgentSpec / TeamSpec, hashed, so the version IS the config
      -> worktrees          an isolated checkout, because different-agent PRs collided 41.7%
      -> claims             so two controllers cannot put two agents on one checkout
      -> provider           the only thing that knows how an agent is started
      -> GreenContract      which assigns the verdict — never the agent, never the provider
      -> events + runs      the stream, and the one-row-per-run fold of it

⭐ **The verdict is assigned here, from evidence, by a contract.** The provider reports what it
observed and whether it was in a position to observe anything; the contract turns that into one of
five verdicts. There is no code path by which a green run can be reported without something having
measured it, and `assertions()` below is a short enough list to read and disagree with.

⛔ **A green run is not the goal.** Most runs this can currently execute end UNMEASURABLE, and
that is the correct answer rather than a gap to paper over: four of the five presets name a
verifier that nobody has wired, so nothing can say whether the ticket's actual work was done. A
controller that reported PASS on "the agent exited 0" would be measuring that the process started,
and labelling it as the client's problem being solved.

⚠ **What this does NOT do.** It does not decide whether work is safe to dispatch against
production, it does not raise a cap, and it never converts an unobserved outcome into a pass. It
also does not replace the supervised terminal path — see `factory.provider.SupervisedProvider`.
"""
from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from . import claims as _claims
from . import events as _events
from . import presets as _presets
from . import repo as _repo
from . import runs as _runs
from . import verifiers as _verifiers
from . import worktrees as _worktrees
from .blueprint import AgentSpec, TeamSpec
from .contract import ContractResult, GreenContract, Unmeasurable, Verdict
from .presets import WIRED, Preset
from .provider import AgentResult, ProviderError


@dataclass
class Ticket:
    """One unit of work, as the controller needs to see it.

    Deliberately not the task store's `Task`. The store is an event log of everything anybody ever
    recorded about a work item; a run needs five fields, and taking them explicitly means the
    controller can be driven from a ticket, a CLI argument or a test without any of them
    pretending to be the others.
    """
    id: str
    title: str
    task: str = ""
    #: The operator's declared ticket type, when they named one. `None` means they did not, and
    #: the eligible set widens accordingly — which is the interesting case to record.
    type_id: Optional[str] = None
    layers: Sequence[str] = ()
    repo: str = ""

    def prompt_task(self) -> str:
        return self.task.strip() or self.title.strip()

    @property
    def key(self) -> str:
        """The id as a worktree branch and claim key: lowercase, punctuation collapsed to dashes.

        ⚠ Separate from `id` on purpose. `worktrees.path_for` and `claims._task_path` both enforce
        ``^[a-z0-9][a-z0-9-]{0,63}$``, so a real ticket id — `GP-327`, `FU92-420` — is rejected by
        both. Normalising silently inside those modules would change what a lane claim means for
        every other caller; normalising here keeps `GP-327` in the ledger, where a human reads it,
        while `gp-327` is what git and the lock file see.
        """
        import re as _re
        k = _re.sub(r"[^a-z0-9]+", "-", (self.id or "").lower()).strip("-")[:64]
        return k or "unnamed-ticket"


# --------------------------------------------------------------------------------- selection

#: Named so the rule that produced an eligible set is a string an operator can disagree with,
#: not a sentence buried in a function.
RULE_DECLARED = "the preset whose type_id the operator declared on the ticket"
RULE_LAYERS = "every preset touching all of the ticket's declared layers"
RULE_NONE = "no type and no layers were declared, so every preset is eligible"

#: How a tie is broken when more than one preset is eligible and nobody named a type.
#:
#: ⚠ Stated out loud because a tie-break is a decision, and a decision nobody wrote down becomes
#: a behaviour nobody can argue with. The cheapest is taken because an operator who did not name a
#: ticket type has not authorised the expensive configuration — `wrong-number` and
#: `model-redesign` are opus at $15 and $25. The full eligible set is recorded either way, so the
#: choice that was not taken is visible rather than gone.
TIEBREAK = "the cheapest eligible preset by budget_usd, because an undeclared type has not " \
           "authorised the expensive configuration"


def eligible(ticket: Ticket) -> Tuple[List[dict], Optional[str], str]:
    """(eligible set, chosen id, rule). The one thing that cannot be reconstructed afterwards.

    Returns every configuration that passed the filter — not just the winner — each marked with
    whether it was chosen and why. R19 §5: this costs nothing to write now and is gone the instant
    the process exits.
    """
    if ticket.type_id:
        p = _presets.by_id(ticket.type_id)
        cands = [p] if p else []
        rule = RULE_DECLARED
    elif ticket.layers:
        cands = _presets.for_layers(*ticket.layers)
        rule = RULE_LAYERS
    else:
        cands = list(_presets.PRESETS)
        rule = RULE_NONE

    if not cands:
        return [], None, rule

    if len(cands) == 1:
        chosen = cands[0]
        why_chosen = "the only preset the filter admitted"
    else:
        chosen = min(cands, key=lambda p: (p.budget_usd, p.type_id))
        why_chosen = TIEBREAK

    out = []
    for p in cands:
        out.append({
            "id": p.type_id,
            "chosen": p.type_id == chosen.type_id,
            "why": why_chosen if p.type_id == chosen.type_id else "eligible, not taken",
            "model": p.model,
            "budget_usd": p.budget_usd,
            "max_turns": p.max_turns,
            "verifier_state": p.verifier_state,
        })
    return out, chosen.type_id, rule


def _evidence_clause(preset: Preset) -> str:
    """What a WIRED preset obliges the agent to leave behind, stated in the agent's own prompt.

    ⛔ Without this the wiring is only half-built. `verifiers.pbi_model_change` adjudicates the
    file at `.factory/verification.json`; an agent never told to write one cannot produce anything
    but UNMEASURABLE, and would be failing an obligation nobody ever stated. **A verifier the
    agent cannot satisfy is not a gate, it is a trap.**

    ⚠ The last paragraph is the load-bearing one. The whole apparatus is worth nothing if an agent
    under pressure to go green invents an observation, so *omit rather than guess* is stated where
    the agent will actually read it — not only in a design note nobody passes to the model.
    """
    if preset.verifier_state != WIRED:
        return ""
    return (
        "EVIDENCE — this is how your work gets a verdict, and it is not optional:\n"
        f"  Write {_verifiers.EVIDENCE_RELPATH} inside this worktree before you finish. It is "
        "JSON with two objects: 'target' (what the change is held to — the dataset id, the "
        "anchors, the baseline, the bound reports) and 'observations' (what you actually "
        "measured, one key per probe).\n"
        "  The verifier reads THAT FILE. It does not go and look for itself, so an observation "
        "you did not write down did not happen as far as the verdict is concerned. No file at all "
        "is UNMEASURABLE — not a failure, but not a pass either, and the ticket cannot be signed "
        "off on it.\n"
        "  ⛔ OMIT anything you did not measure. Never invent a value to fill a key. An absent "
        "observation is reported honestly as 'nobody looked'; a fabricated one turns every check "
        "downstream into decoration, and is far worse than an unmeasured ticket.\n\n"
    )


def team_for(ticket: Ticket, preset: Preset) -> TeamSpec:
    """A one-agent team from the preset, with the ticket supplying what a preset must not guess.

    `Preset.as_spec_kwargs()` is deliberately partial — name, role and prompt are the operator's,
    and a preset that filled them would be pretending to know the task. The prohibition comes
    from the preset and is carried at BOTH levels: the agent's, and the team's, which is inside
    the team version hash. Deleting a team-level prohibition used to leave the version identical;
    that was fixed on 2026-08-29 and this relies on the fix.
    """
    agent = AgentSpec(
        name=f"{preset.type_id}-agent",
        role=preset.title,
        prompt=(
            f"You are working one ticket of type '{preset.type_id}' ({preset.title}).\n\n"
            f"MUST NOT: {preset.prohibition}\n\n"
            f"The check that owns the verdict for this ticket type is: {preset.verifier}\n"
            f"Its state is {preset.verifier_state.upper()} — if it is not WIRED, nothing "
            f"downstream can confirm your work, so say so plainly rather than claiming success.\n\n"
            + _evidence_clause(preset) +
            f"ESCALATE AND STOP rather than proceeding when: {preset.escalate_when}\n"
        ),
        **preset.as_spec_kwargs(),
    )
    return TeamSpec(
        name=f"{preset.type_id}-team",
        purpose=ticket.title,
        agents=[agent],
        contract=CONTRACT_NAME,
        repo=ticket.repo or str(_repo.primary()),
        prohibition=preset.prohibition,
    )


def unreachable_repo(ticket: Ticket) -> Optional[str]:
    """The repository this run would be *recorded* against, when the executor cannot reach it.

    ⛔ **F90.** `TeamSpec.repo` is inside the team version hash — a team certified against
    `clients` is a different team from one certified against `agent-factory`, which is the whole
    point of putting it there. But nothing downstream honoured it: `worktrees.REPO` is
    ``_repo.primary()`` bound at import, and no function in `worktrees.py` accepts a repository
    argument. The hash was carrying an assurance the run could not keep.

    So the controller refuses. This is remedy **(b)** of the two F90 names, and deliberately the
    smaller one: it cannot make a cross-repo run happen, it only stops the ledger claiming one
    did. Remedy (a) — threading the repository through `worktrees.ensure` and the providers — is
    the feature, and it is not this.

    ⚠ The comparison is against `worktrees.REPO`, **not** `repo.primary()`, even though they are
    the same object today. The rule F90 states is *a field that is part of an identity must be
    read by whatever acts on that identity*; the thing that acts is the worktree maker, so that is
    what this must track. If someone later gives `worktrees` a second root, this check follows it.

    Returns None when the run may proceed — including for an empty `ticket.repo`, which means the
    operator named no repository and `team_for` defaults it to this checkout.
    """
    declared = (ticket.repo or "").strip()
    if not declared:
        return None
    try:
        want = pathlib.Path(declared).resolve()
        have = pathlib.Path(_worktrees.REPO).resolve()
    except OSError as exc:                                         # noqa: BLE001
        return f"could not resolve the declared repository {declared!r}: {exc}"
    if os.path.normcase(str(want)) == os.path.normcase(str(have)):
        return None
    return (f"ticket declares repo {want} but the executor can only create worktrees under "
            f"{have}. The run record and the team version would both name a repository the "
            f"agent was never placed in (F90). Refusing rather than recording a false "
            f"attribution.")


# ---------------------------------------------------------------------------------- contract

CONTRACT_NAME = "run"

#: A verifier callable takes the run context and returns `(ok, detail)`, exactly like any other
#: assertion check. It may raise `Unmeasurable`. It is injected rather than looked up because a
#: preset's `verifier` field is prose describing a check, not a reference to one — pretending
#: otherwise is how a named verifier becomes a claim that one has been run.
Verifier = Callable[[dict], Tuple[bool, str]]


def assertions(preset: Preset, verifier: Optional[Verifier] = None) -> GreenContract:
    """What "this run worked" means, as falsifiable claims over the run context.

    Read in order, they answer: was it started, could anyone see the outcome, did it end cleanly,
    is there a record of what it did, did anything change, was the ticket's own check satisfied,
    and did we measure what it cost.

    ⭐ The last-but-one is the load-bearing one. Every assertion above it is about the *harness*;
    only `ticket_verifier` is about the client's problem. A contract made only of the others would
    go green on a run that did nothing useful, which is exactly the shape of a gate that cannot
    fail.
    """
    gc = GreenContract(CONTRACT_NAME)

    def _result(ctx) -> AgentResult:
        r = ctx.get("result")
        if r is None:
            raise Unmeasurable("no provider result in the run context — nothing to look at")
        return r

    def dispatched(ctx):
        r = _result(ctx)
        return r.dispatched, ("the provider dispatched the agent" if r.dispatched
                              else "the provider did not dispatch anything")

    def observable(ctx):
        r = _result(ctx)
        if not r.observable:
            # ⛔ The negative control lives here. A provider that could not watch the run has not
            # observed a pass, and inferring one from a clean spawn is the exact collapse this
            # repository exists to refuse. Delete this raise and a supervised launch — the path
            # that actually runs today — starts reporting PASS for having opened a window.
            raise Unmeasurable(
                f"{r.provider} cannot observe this run's outcome ({r.detail or 'no detail'}). "
                "Not a pass and not a failure — nobody looked.")
        return True, "the provider was in a position to observe the outcome"

    def exited_clean(ctx):
        r = _result(ctx)
        if not r.observable:
            raise Unmeasurable("the outcome was not observable, so the exit status is unknown")
        if r.returncode is None:
            raise Unmeasurable(
                "the provider reported no exit status. An absent status is NOT a zero.")
        return r.returncode == 0, (
            f"exit {r.returncode}" + ("" if r.returncode == 0 else f"; limit={r.limit}"))

    def transcript_kept(ctx):
        r = _result(ctx)
        if not r.observable:
            raise Unmeasurable("no transcript is expected from an unobservable run")
        if r.transcript is None:
            raise Unmeasurable(
                "no transcript path was recorded — what the agent did cannot be read back")
        p = pathlib.Path(r.transcript)
        if not p.is_file():
            return False, f"transcript {p.name} was named but does not exist"
        return p.stat().st_size > 0, f"{p.name} is {p.stat().st_size} bytes"

    def work_landed(ctx):
        """Did anything actually change in the worktree.

        ⚠ FAIL, not UNMEASURABLE, when nothing changed and we could look: an agent that ran
        cleanly and altered nothing has failed the ticket. UNMEASURABLE only when we cannot see
        the worktree at all.

        ⛔ **And when the run itself was not observable.** Caught by the first real dry run
        through this controller, 2026-08-30: every other assertion gated on `observable` and this
        one did not, so a dry run — in which no agent executes and the worktree is therefore
        untouched *by design* — was reported as **FAIL: the agent altered nothing**. The same
        would have happened to every supervised launch, which returns the instant the terminal
        opens with the human yet to type a word. An unchanged worktree is evidence about an agent
        only if an agent ran and somebody watched it.
        """
        r = _result(ctx)
        if not r.observable:
            raise Unmeasurable(
                "the run was not observable, so the worktree's state now says nothing about what "
                "the agent did — it may not have started yet, or may never have run at all")
        wt = ctx.get("worktree")
        if not wt:
            raise Unmeasurable("no worktree in the run context")
        p = pathlib.Path(wt)
        if not p.is_dir():
            raise Unmeasurable(f"{p} is not a directory — the worktree cannot be inspected")
        changed = ctx.get("changed")
        if changed is None:
            raise Unmeasurable("the worktree's change state was not measured")
        return bool(changed), (f"{changed}" if changed else
                               "the worktree is unchanged — the agent altered nothing")

    def ticket_verifier(ctx):
        """The deterministic check the preset names as owning this ticket type's verdict.

        ⛔ UNMEASURABLE when the preset's verifier is not WIRED, and that is the honest answer for
        four of the five presets today. `presets.unwired()` says which; a row naming a verifier is
        a claim that one APPLIES, never that one has been run.
        """
        if preset.verifier_state != WIRED:
            raise Unmeasurable(
                f"the verifier for '{preset.type_id}' is {preset.verifier_state.upper()}, not "
                f"WIRED: \"{preset.verifier}\". Nothing can say whether the ticket's work was "
                "done, so this is not a pass.")
        if verifier is None:
            raise Unmeasurable(
                f"preset '{preset.type_id}' declares a WIRED verifier but the controller was "
                "given no callable to run. The declaration and the wiring disagree.")
        return verifier(ctx)

    def cost_measured(ctx):
        c = ctx.get("cost") or {}
        if c.get("basis") != _runs.MEASURED:
            raise Unmeasurable(
                f"cost basis is {c.get('basis', 'absent')}, not MEASURED — no transcript was "
                "found for this working directory, so what it spent is NOT-RECORDED rather "
                "than zero.")
        return True, (f"{c.get('sessions')} session(s), {c.get('input', 0)} in / "
                      f"{c.get('output', 0)} out tokens")

    gc.add("agent_dispatched", dispatched,
           description="the provider started an agent at all")
    gc.add("outcome_observable", observable,
           description="somebody was in a position to see how it ended")
    gc.add("exited_clean", exited_clean,
           description="the agent process ended with status 0")
    gc.add("transcript_kept", transcript_kept,
           description="there is a readable record of what the agent did")
    gc.add("work_landed", work_landed,
           description="the worktree changed — the agent altered something")
    gc.add("ticket_verifier", ticket_verifier,
           description="the deterministic check this ticket type says owns the verdict")
    gc.add("cost_measured", cost_measured,
           description="what the run spent was measured, not estimated")
    return gc


# -------------------------------------------------------------------------------- the runner

def _branch_of(wt) -> str:
    """The worktree's actual checked-out branch, or "" when it cannot be read.

    "" rather than a guess: an empty branch field reads as *nobody recorded it*, while a wrong one
    reads as a fact, and a ledger is only worth having if its wrong entries are distinguishable
    from its missing ones.
    """
    import subprocess
    try:
        r = subprocess.run(["git", "-C", str(wt), "rev-parse", "--abbrev-ref", "HEAD"],
                           capture_output=True, text=True, timeout=30)
        return (r.stdout or "").strip() if r.returncode == 0 else ""
    except Exception:                                              # noqa: BLE001
        return ""


@dataclass
class RunResult:
    ticket: Ticket
    verdict: Verdict
    run_id: Optional[str] = None
    preset_id: Optional[str] = None
    contract: Optional[ContractResult] = None
    worktree: Optional[pathlib.Path] = None
    team_version: Optional[str] = None
    ledger_row: Optional[dict] = None
    detail: str = ""
    eligible: List[dict] = field(default_factory=list)

    def summary(self) -> str:
        head = f"{self.ticket.id}  {self.verdict.value}"
        if self.preset_id:
            head += f"  preset={self.preset_id}"
        if self.run_id:
            head += f"  run={self.run_id}"
        return head + (f"\n  {self.detail}" if self.detail else "")


class RunController:
    """Drives one ticket through the line. Every collaborator is injectable, none is optional.

    ⚠ The injection points are not test scaffolding — `worktree` and `claim` are how the supervised
    tracker path reuses the controller while keeping its own worktree and claim machinery, and
    `provider` is how the Agent SDK arrives later without this file changing.
    """

    def __init__(self, provider, worktree: Optional[Callable[[str], pathlib.Path]] = None,
                 claim: Optional[Callable[[str], Any]] = None,
                 release: Optional[Callable[[str], Any]] = None,
                 verifier: Optional[Verifier] = None,
                 record: Callable[..., dict] = _runs.record,
                 cost: Callable[[Any], dict] = _runs.cost):
        self.provider = provider
        self._worktree = worktree
        self._claim = claim
        self._release = release
        self.verifier = verifier
        self._record = record
        #: Injected for the same reason as the rest: a test must be able to drive this line to a
        #: PASS, or the negative controls below prove nothing. An instrument that has never
        #: registered a non-zero cannot be trusted to report a zero.
        self._cost = cost

    # ------------------------------------------------------------------ collaborators
    def _make_worktree(self, ticket: Ticket) -> pathlib.Path:
        if self._worktree is not None:
            return pathlib.Path(self._worktree(ticket.key))
        p, _note = _worktrees.ensure(ticket.key)
        return pathlib.Path(p)

    def _take_claim(self, ticket: Ticket):
        if self._claim is not None:
            return self._claim(ticket.key)
        import os
        return _claims.task_claim(ticket.key, pid=os.getpid(),
                                  who="factory.control", note=ticket.title[:120])

    def _drop_claim(self, ticket: Ticket):
        if self._release is not None:
            return self._release(ticket.key)
        return _claims.task_release(ticket.key)

    @staticmethod
    def _changed(wt: pathlib.Path) -> Optional[str]:
        """What the worktree looks like after the run, or None when it cannot be measured.

        None is not 'clean'. A git call that failed is a measurement we did not take, and
        `work_landed` renders that as UNMEASURABLE rather than as an agent that did nothing.
        """
        import subprocess
        try:
            s = subprocess.run(["git", "-C", str(wt), "status", "--porcelain"],
                               capture_output=True, text=True, timeout=60)
            if s.returncode != 0:
                return None
            dirty = len([l for l in (s.stdout or "").splitlines() if l.strip()])
            c = subprocess.run(["git", "-C", str(wt), "rev-list", "--count", "HEAD", "^HEAD@{u}"],
                               capture_output=True, text=True, timeout=60)
            ahead = c.stdout.strip() if c.returncode == 0 and c.stdout.strip().isdigit() else "?"
            if not dirty and ahead in ("0", "?"):
                return ""
            return f"{dirty} uncommitted file(s), {ahead} commit(s) ahead"
        except Exception:                                          # noqa: BLE001
            return None

    # ------------------------------------------------------------------ the run
    def run(self, ticket: Ticket) -> RunResult:
        """Ticket to verdict. Records the eligible set before anything can fail."""
        el, chosen_id, rule = eligible(ticket)
        if not el or chosen_id is None:
            # ⛔ No RunLog: nothing started, so there is no run to open. The considered set is
            # still written, because "we looked and nothing matched" is a finding about the preset
            # table and vanishes otherwise.
            _events.aborted(ticket.id, considered=[{"id": p.type_id, "chosen": False}
                                                   for p in _presets.PRESETS],
                            rule=rule, verdict=Verdict.NOT_RUN,
                            why=(f"no preset was eligible for ticket {ticket.id!r} under: {rule}. "
                                 f"Declared type={ticket.type_id!r}, layers={list(ticket.layers)!r}."))
            return RunResult(ticket, Verdict.NOT_RUN, eligible=[],
                             detail=f"nothing eligible under: {rule}")

        preset = _presets.by_id(chosen_id)
        team = team_for(ticket, preset)
        agent = team.agents[0]

        # ⭐ The eligible set goes to disk BEFORE the worktree, the claim or the agent. Everything
        # after this point can fail and be reconstructed; this cannot.
        log = _events.RunLog.start(
            ticket=ticket.id, eligible=el, chosen=chosen_id, rule=rule,
            title=ticket.title, team=team.name, team_version=team.version,
            agent_versions=team.pinned(), repo=team.repo, provider=self.provider.name)

        # ⛔ F90 — refuse before the worktree, not after. The eligible set is already on disk
        # above, so the refusal is recorded rather than vanishing; but nothing is created, no
        # claim is taken, and no attempt is spent. NOT_RUN because nothing was attempted: the
        # apparatus did not break (ERROR) and no assertion failed (FAIL).
        mismatch = unreachable_repo(ticket)
        if mismatch:
            log.abort(Verdict.NOT_RUN, why=mismatch)
            return RunResult(ticket, Verdict.NOT_RUN, run_id=log.run_id, preset_id=chosen_id,
                             eligible=el, team_version=team.version,
                             detail=f"refused: {mismatch}")

        wt: Optional[pathlib.Path] = None
        claimed = False
        #: ⛔ A claim must outlive this call when the work does. The supervised provider returns
        #: the instant the terminal opens, with a human still typing in it; releasing the claim in
        #: `finally` would let the next launch put a second agent into the same checkout — the
        #: 41.7% different-agent conflict case, and precisely what `launch()` guards lanes
        #: against. So the release is conditional on having actually observed the run end.
        in_flight = False
        try:
            wt = self._make_worktree(ticket)
            log.emit("worktree_ready", worktree=str(wt))
            self._take_claim(ticket)
            claimed = True
            log.emit("claim_taken", key=ticket.id)
        except Exception as exc:                                   # noqa: BLE001
            # Our apparatus, not the agent. TTCN-3 `error`: once the harness has broken we cannot
            # claim anything about the work it was supposed to measure.
            log.abort(Verdict.ERROR, why=f"{type(exc).__name__}: {exc}")
            if claimed:
                self._drop_claim(ticket)
            return RunResult(ticket, Verdict.ERROR, run_id=log.run_id, preset_id=chosen_id,
                             eligible=el, team_version=team.version,
                             detail=f"harness failed before dispatch: {type(exc).__name__}: {exc}")

        try:
            log.emit("agent_dispatched", agent=agent.name, agent_version=agent.version,
                     model=agent.model, effort=agent.effort, max_turns=agent.max_turns,
                     budget_usd=agent.budget_usd, prohibition=agent.prohibition)
            try:
                result = self.provider.run(agent, ticket.prompt_task(), wt)
            except ProviderError as exc:
                # The provider refused to dispatch — an exhausted attempt cap, a terminal that
                # would not open. That is not the agent failing and it is not our harness
                # breaking; nothing ran, so nothing was measured.
                log.abort(Verdict.NOT_RUN, why=str(exc))
                return RunResult(ticket, Verdict.NOT_RUN, run_id=log.run_id, preset_id=chosen_id,
                                 eligible=el, worktree=wt, team_version=team.version,
                                 detail=f"provider refused to dispatch: {exc}")
            in_flight = result.dispatched and result.in_flight
            log.emit("agent_returned", claim_retained=in_flight, **result.as_event())

            cost = self._cost(wt)
            changed = self._changed(wt)
            ctx = {"result": result, "worktree": wt, "changed": changed, "cost": cost,
                   "ticket": ticket, "preset": preset, "team": team}
            log.emit("evidence_gathered", changed=changed, cost=cost)

            # ⭐ An injected verifier wins; otherwise the registry is consulted. Before this
            # fallback existed nothing ever supplied a callable, so `ticket_verifier` reported
            # "the declaration and the wiring disagree" on EVERY run — including the one
            # preset that claimed WIRED. Injection stays first so a test can drive this line
            # to PASS and to FAIL without the registry in the way.
            verifier = self.verifier or _verifiers.for_type(preset.type_id)
            cres = assertions(preset, verifier).run(ctx)
            log.verdict(cres.verdict, contract=cres.contract,
                        results=[{"name": r.name, "verdict": r.verdict.value, "detail": r.detail}
                                 for r in cres.results])

            row = self._record(
                lane=ticket.id, outcome=cres.verdict.value, detail=cres.summary(),
                problems=[str(r) for r in cres.failures()],
                # ⚠ The branch is READ from the worktree, never assembled from the key. A run
                # against a reused worktree can be on any branch, and a ledger row naming
                # `lane/<key>` because that is what the convention says would be a guess printed
                # as a fact — the same shape as `_integration_ref`'s `split("/")[-1]` bug, which
                # made every lane report `commits=None` and read as "no work".
                branch=_branch_of(wt), commits=None, cwd=wt,
                job=ticket.id, team=team.name, team_version=team.version,
                agent_versions=team.pinned())
            log.finish(cres.verdict, ledger_row=True)
            return RunResult(ticket, cres.verdict, run_id=log.run_id, preset_id=chosen_id,
                             contract=cres, worktree=wt, team_version=team.version,
                             ledger_row=row, eligible=el, detail=cres.summary())
        except Exception as exc:                                   # noqa: BLE001
            log.abort(Verdict.ERROR, why=f"{type(exc).__name__}: {exc}")
            return RunResult(ticket, Verdict.ERROR, run_id=log.run_id, preset_id=chosen_id,
                             eligible=el, worktree=wt, team_version=team.version,
                             detail=f"{type(exc).__name__}: {exc}")
        finally:
            if claimed and not in_flight:
                self._drop_claim(ticket)


# -------------------------------------------------------------------------------------- CLI

def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    from .provider import HeadlessProvider, default_ledger_path
    from .deploy import AttemptLedger

    ap = argparse.ArgumentParser(description="Run one ticket through the factory.")
    ap.add_argument("ticket", help="ticket id — also the worktree and claim key")
    ap.add_argument("--title", default="", help="what the ticket asks for")
    ap.add_argument("--task", default="", help="the full task text handed to the agent")
    ap.add_argument("--type", dest="type_id", default=None, help="declared preset type_id")
    ap.add_argument("--layer", dest="layers", action="append", default=[],
                    help="a layer the work touches; repeatable")
    ap.add_argument("--dry-run", action="store_true",
                    help="write the command and the prompt, start no agent")
    ap.add_argument("--plan", action="store_true",
                    help="print the eligible set and stop — records nothing")
    args = ap.parse_args(argv)

    ticket = Ticket(id=args.ticket, title=args.title or args.ticket, task=args.task,
                    type_id=args.type_id, layers=tuple(args.layers))

    if args.plan:
        el, chosen, rule = eligible(ticket)
        print(f"rule: {rule}")
        for e in el:
            print(f"  {'->' if e['chosen'] else '  '} {e['id']:<16} {e['model']:<7} "
                  f"${e['budget_usd']:<6} verifier={e['verifier_state']}  {e['why']}")
        if not el:
            print("  (nothing eligible)")
        return 0 if chosen else 1

    provider = HeadlessProvider(
        repo_root=_repo.primary(), sessions_dir=_repo.primary() / ".sessions",
        ledger=AttemptLedger(default_ledger_path()), dry_run=args.dry_run)
    res = RunController(provider).run(ticket)
    print(res.summary())
    if res.contract is not None:
        for r in res.contract.results:
            print(f"  [{r.verdict.value:<12}] {r.name:<20} {r.detail}")
    print(f"\n{_events.path()}  <- the stream")
    print(f"{_runs.path()}  <- the fold")
    return 0 if res.verdict is Verdict.PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
