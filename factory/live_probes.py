"""Real instruments for the connector GreenContract — wired against a prefect-connectors
checkout on disk.

Only two verbs are implemented here: `config` (A1) and `suite` (A5). Both are reachable with
**no credential and no network call** — `config` constructs the real connector/options classes
declared for windsorai@GEP (pydantic validates shape; a `SecretStr` field accepts any string, so
construction proves nothing about whether the key authenticates — that is A2's job, still
unwired), and `suite` shells out to the connectors repo's own pytest.

Every other verb (`credential`, `image`, `deployment`, `run`, `landed`, `source`, `forbidden`) is
left unimplemented on purpose and inherits `Probes._refuse` — this module must never let
UNMEASURABLE quietly become PASS just because *some* instrument now exists for this target.
Wiring another assertion means writing (and calibrating) another method, not loosening this one.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .connector_contract import ConnectorTarget, Probes
from .contract import Unmeasurable

_ENV_VAR = "PREFECT_CONNECTORS"
_MISSING = object()


def _repo_root() -> Path:
    """This clone's root, whether `live_probes.py` sits inside a worktree or the main checkout.

    A hardcoded parent-count (`parent.parent.parent`) is only correct at one nesting depth — it
    was silently wrong the moment this file was imagined running from the main clone instead of
    `.worktrees/<lane>/factory/` (caught in review, not by any test — see docs/findings.md F30's
    sibling entry on this same file). `git rev-parse --git-common-dir` always names the MAIN
    clone's `.git`, worktree or not, so anchoring there is depth-independent.
    """
    here = Path(__file__).resolve().parent
    try:
        r = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=here,
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            common = Path(r.stdout.strip())
            if not common.is_absolute():
                common = here / common
            return common.resolve().parent
    except Exception:
        pass
    return here.parent   # best-effort fallback if git itself is unavailable


def _default_connectors_root() -> Path:
    """The canonical checkout, a sibling of this clone at `repos/prefect-connectors` — NOT the
    sibling `.worktrees/prefect-connectors` factory/readiness.py defaults to.

    That sibling path is not a stable "no checkout here" absence: another lane can create it
    mid-session (a control-plane lane doing its own work in prefect-connectors did, here, at
    05:23 while this module was being written) and it then names a different, concurrently
    mutating checkout on a different branch. Preferring it by path-existence alone would make
    this instrument's answer depend on another lane's timing and edits, not on the code we mean
    to certify. Use $PREFECT_CONNECTORS to point at anything else on purpose.
    """
    env = os.environ.get(_ENV_VAR)
    if env:
        return Path(env)
    return _repo_root().parent / "prefect-connectors"


def _revision(root: Path) -> str:
    """HEAD, plus a `-dirty` suffix when the tree doesn't match it.

    `suite()` runs the WORKING TREE, not the commit — reporting a clean sha for a dirty checkout
    would attribute a suite result to a state that never existed. A failed `rev-parse` (not a
    git repo, git missing) is UNMEASURABLE, not an empty string: an empty revision would still
    let A5 report a PASS with no provenance at all whenever `pinned_test_revision` is unset.
    """
    try:
        rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                             capture_output=True, text=True, timeout=30)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                                capture_output=True, text=True, timeout=30)
    except Exception as exc:
        raise Unmeasurable(f"could not read {root}'s git revision: {exc}")
    sha = rev.stdout.strip()
    if rev.returncode != 0 or not sha:
        raise Unmeasurable(f"git rev-parse HEAD failed in {root}: {rev.stderr.strip()}")
    dirty = status.returncode == 0 and bool(status.stdout.strip())
    return f"{sha}-dirty" if dirty else sha


def _count(clean: str, word: str) -> Optional[int]:
    hits = re.findall(rf"(\d+) {word}", clean)
    return int(hits[-1]) if hits else None


class WindsorAiGepProbes(Probes):
    """Live instrument for connector-e2e/windsorai@GEP. A1 and A5 only — see module docstring."""

    def __init__(self, connectors_root: Optional[Path] = None, test_paths: Optional[list] = None):
        self.root = Path(connectors_root) if connectors_root else _default_connectors_root()
        if not self.root.is_dir():
            raise Unmeasurable(f"no prefect-connectors checkout at {self.root} — set ${_ENV_VAR}")
        # Full regression suite by default; a narrower list is for this module's own tests only,
        # so a real end-to-end check does not cost the whole repo's suite on every test run.
        self.test_paths = list(test_paths) if test_paths else []
        self._root_str = str(self.root)
        if self._root_str not in sys.path:
            sys.path.insert(0, self._root_str)

    # ---------------------------------------------------------------- A1

    def config(self, ctx: dict) -> dict:
        try:
            # Imported lazily, not at module load: pydantic is a prefect-connectors dependency,
            # not an agent-factory one, and this module must still degrade to Unmeasurable (not
            # an ImportError crash out of `factory.certify`) when the checkout — and therefore
            # pydantic — isn't on this machine at all.
            from pydantic import ValidationError
            connectors_mod = __import__("connector.connectors.windsorai", fromlist=["_"])
            deploy_mod = __import__("connector.accounts.GEP.deployments.windsorai", fromlist=["_"])
        except Exception as exc:
            raise Unmeasurable(f"could not import the windsorai connector/deployment: {exc}")

        # These are the probe's own hooks into the real deployment module — private constants an
        # upstream refactor is free to rename. If they disappear, that is THIS INSTRUMENT going
        # blind, not evidence the connector's config is wrong; collapsing the two would report a
        # FAIL for a probe defect, which is the exact inversion `verify-qa-success` already ships.
        account_ids_raw = getattr(deploy_mod, "_GOOGLE_ADS_ACCOUNT_IDS", _MISSING)
        if account_ids_raw is _MISSING:
            raise Unmeasurable(
                "connector/accounts/GEP/deployments/windsorai.py no longer defines "
                "_GOOGLE_ADS_ACCOUNT_IDS — this probe's hook into the real deployment moved")
        account_ids = list(account_ids_raw or [])

        fields_raw = getattr(deploy_mod, "_GOOGLE_ADS_FIELDS", _MISSING)
        if fields_raw is _MISSING:
            raise Unmeasurable(
                "connector/accounts/GEP/deployments/windsorai.py no longer defines "
                "_GOOGLE_ADS_FIELDS — this probe's hook into the real deployment moved")

        constructed = []

        connection_cls = getattr(connectors_mod, "WindsorAIConnection", None)
        if connection_cls is None:
            raise Unmeasurable("connector.connectors.windsorai no longer defines WindsorAIConnection")
        try:
            # A placeholder value on purpose: this proves the class CONSTRUCTS for this
            # account, not that the key authenticates — SecretStr accepts any string, and
            # `validate_connection()` (the live auth call) is never invoked here. That is A2.
            connection_cls(api_key="unmeasured-a1-does-not-authenticate")
            constructed.append(connection_cls.__name__)
        except ValidationError:
            pass   # genuinely did not construct; a1 reports it missing — not this probe crashing

        options_cls = getattr(connectors_mod, "WindsorAIOptions", None)
        if options_cls is None:
            raise Unmeasurable("connector.connectors.windsorai no longer defines WindsorAIOptions")
        if account_ids:
            try:
                options_cls(
                    category="google_ads",
                    table_name="CAMPAIGN",
                    primary_key=["account_id", "date", "campaign_id", "source"],
                    fields=fields_raw,
                    account_ids=account_ids,
                )
                constructed.append(options_cls.__name__)
            except ValidationError:
                pass

        return {"constructed": constructed, "accounts": account_ids, "fields_count": len(fields_raw or [])}

    # ---------------------------------------------------------------- A5

    def suite(self, ctx: dict) -> dict:
        # "-o addopts=" overrides whatever addopts the target repo's own pyproject.toml sets
        # (prefect-connectors has none today, but a probe that only works on an unconfigured repo
        # is not a real instrument) so our own -q/--tb flags are never silently doubled into a
        # suppressed summary line (the exact "-qq hides the summary" trap this session's own
        # findings ledger already names). sys.executable, not the bare "python" name, so the suite
        # runs under the same interpreter certifying it, not whatever resolves first on PATH.
        cmd = [sys.executable, "-m", "pytest", "-o", "addopts=", "--no-header", "--tb=no",
               "-q", "-p", "no:cacheprovider"]
        cmd += self.test_paths
        try:
            r = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, timeout=300)
        except Exception as exc:
            raise Unmeasurable(f"could not run the prefect-connectors suite: {exc}")

        clean = re.sub(r"\x1b?\[[0-9;]*m", "", r.stdout + "\n" + r.stderr)
        passed = _count(clean, "passed")
        failed = _count(clean, "failed")
        errored = _count(clean, "error")
        if passed is None and failed is None and errored is None:
            raise Unmeasurable(f"pytest printed no summary line (exit {r.returncode}): {clean[-500:]!r}")

        # pytest's own exit codes: 0 clean, 1 some test failed/errored, 2 interrupted,
        # 3 internal error, 4 usage error, 5 no tests collected. Only 0/1 describe "the suite
        # ran to completion and here is its verdict" — anything else means the RUN broke, which
        # is unmeasurable, not a number to report.
        if r.returncode not in (0, 1):
            raise Unmeasurable(f"pytest exited {r.returncode} (run did not complete cleanly): "
                               f"{clean[-500:]!r}")

        # A failed/errored test always exits 1 — errors are folded into `failed` because A5 only
        # asks "is the suite green", and a fixture that raised is not green just because it isn't
        # spelled "failed" in pytest's own vocabulary.
        failed_total = (failed or 0) + (errored or 0)
        if r.returncode == 0 and failed_total > 0:
            raise Unmeasurable(f"pytest exited 0 but the summary reports failures/errors — "
                               f"parsing disagrees with the exit code: {clean[-300:]!r}")
        if r.returncode == 1 and failed_total == 0:
            raise Unmeasurable(f"pytest exited 1 but no failed/error count was parsed — "
                               f"parsing is incomplete: {clean[-300:]!r}")

        return {"passed": passed or 0, "failed": failed_total, "revision": _revision(self.root)}


class _BlindWindsorAiProbes(Probes):
    """The live instrument exists in code but could not reach its subject — no checkout, an
    unreadable one, or anything else `WindsorAiGepProbes.__init__` raised.

    This is deliberately NOT the same as the base `Probes()` fallback. The contract's own
    doctrine separates NOT-RECORDED from NOT-VISIBLE; collapsing "an instrument was wired and
    went blind" into "nobody has wired one yet" hides a real regression (a checkout that
    vanished, an env var that stopped being set) behind text byte-identical to the pre-wiring
    baseline — the same shape of loss `docs/findings.md` names in F30/F31 for other instruments.
    """

    def __init__(self, reason: str):
        self._reason = reason

    def config(self, ctx: dict) -> dict:
        raise Unmeasurable(self._reason)

    def suite(self, ctx: dict) -> dict:
        raise Unmeasurable(self._reason)


def probes_for(target: ConnectorTarget) -> Probes:
    """Return the best available live instrument for this target.

    Only windsorai@GEP has one today. Every other target gets the base `Probes()`, which refuses
    and reports UNMEASURABLE with "no instrument configured" — the honest message for "nobody has
    wired this yet". windsorai@GEP with an unreachable checkout gets `_BlindWindsorAiProbes`
    instead, which raises the SPECIFIC reason (e.g. which path was missing) rather than the
    generic unwired message, on A1/A5 only.
    """
    if target.connector == "windsorai" and target.client == "GEP":
        try:
            return WindsorAiGepProbes()
        except Unmeasurable as exc:
            return _BlindWindsorAiProbes(str(exc))
    return Probes()
