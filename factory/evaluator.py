"""EvaluatorClient — the agent's only route to a verdict, and deliberately a narrow one.

R3 ranked five ways to stop an agent grading itself. Rank 1 is an external evaluator service
holding its own identity; rank 5 — "mostly theatre" — is a separate local process. What separates
them is not the process boundary. It is *who holds the credential* and *what the submitter is
allowed to supply*.

So the load-bearing sentence of the design is a statement about this file:

    The agent never supplies the evaluator implementation, the corpus, or the manifest to be
    trusted. It supplies only the artefact to evaluate.

That is enforced here by having nowhere to put those things. :class:`Submission` has exactly three
fields, the service rejects any body carrying a fourth, and this module imports neither
``connector_contract`` nor ``corpus`` nor ``calibration`` — there is no code path from a client to
a locally-computed verdict. ``tests/test_evaluator_isolation.py`` holds that to be true.

**No fallback, ever.** When the service cannot be reached the honest answer is UNMEASURABLE, and
this client will raise rather than grade. A client that quietly scored locally when the grader was
down would reintroduce the whole defect on the one day it mattered — this estate has already
shipped ``verify-qa-success``, which reports "I could not check" as ``failed``, and a pipeline
whose stage ended ``failed`` while its run closed ``succeeded``.

**A verdict must say who produced it.** An unattributed ``{"verdict": "PASS"}`` is refused rather
than believed: anything on a socket can emit that string. A verdict is accepted only if it names
the evaluator identity, the evaluator bundle hash, and the corpus it was scored against.

Known limit, stated rather than hidden: on one machine under one uid, a loopback endpoint is R3's
rank 5. The *shape* here is rank 1, and the move to rank 1 is deployment plus a managed identity,
not a rewrite. ``factory.readiness`` reports which of the two you are actually running.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

ENDPOINT_VAR = "AGENT_FACTORY_EVALUATOR"

#: The complete submission vocabulary. Frozen on purpose — every field added here is one more
#: thing the graded party gets to influence about its own grading.
SUBMISSION_FIELDS = ("artifact_uri", "artifact_sha256", "run_id")

#: A verdict is believed only if it carries all of these. See the module docstring.
ATTRIBUTION_FIELDS = ("evaluator", "scored_against")


class EvaluatorError(Exception):
    """Base for every way this client declines to produce a verdict."""


class EvaluatorNotConfigured(EvaluatorError):
    """No endpoint. Not a pass, and not a reason to grade locally."""


class EvaluatorUnreachable(EvaluatorError):
    """The evaluator could not be reached, or answered something unusable.

    Callers must map this to UNMEASURABLE. It is not FAIL either: we did not observe a failing
    artefact, we failed to observe at all.
    """


class UnattributedVerdict(EvaluatorError):
    """A verdict that will not say who produced it, or what it was scored against."""


@dataclass(frozen=True)
class Submission:
    """Everything the graded party is permitted to say about its own grading.

    ``artifact_sha256`` is a *claim*, not an instruction. The service reads the artefact itself
    and refuses when the bytes disagree — so this field can only ever narrow what is accepted,
    never widen it.
    """
    artifact_uri: str
    artifact_sha256: str
    run_id: str

    def body(self) -> Dict[str, str]:
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass(frozen=True)
class RemoteVerdict:
    """A verdict produced elsewhere, by someone who said who they were."""
    run_id: str
    verdict: str
    promotable: bool
    evaluator: Dict[str, Any]
    scored_against: Optional[Dict[str, Any]]
    assertions: List[Any]
    raw: Dict[str, Any]

    @classmethod
    def parse(cls, payload: Dict[str, Any]) -> "RemoteVerdict":
        missing = [f for f in ATTRIBUTION_FIELDS if f not in payload]
        if missing:
            raise UnattributedVerdict(
                f"verdict is missing {missing} — refusing to believe a verdict that will not say "
                "who produced it or what it was scored against")
        verdict = str(payload.get("verdict", "")).upper()
        if not verdict:
            raise UnattributedVerdict("verdict payload carries no verdict")
        # Believe the service's promotability only where it agrees with the verdict it published.
        # A payload claiming promotable on a non-PASS is malformed, not permissive.
        promotable = bool(payload.get("promotable")) and verdict == "PASS"
        return cls(run_id=str(payload.get("run_id", "")), verdict=verdict, promotable=promotable,
                   evaluator=payload.get("evaluator") or {},
                   scored_against=payload.get("scored_against"),
                   assertions=list(payload.get("assertions") or []), raw=payload)

    @property
    def is_pass(self) -> bool:
        return self.verdict == "PASS"

    def summary(self) -> str:
        who = self.evaluator.get("identity", "unidentified")
        bundle = str(self.evaluator.get("bundle_sha256", ""))[:12] or "?"
        return f"{self.verdict} for {self.run_id} - by {who}, bundle {bundle}"


class EvaluatorClient:
    """Submit an artefact; receive a verdict. There is no third verb.

    Nothing here can name a corpus, a manifest, an assertion set or an evaluator build. Those live
    with the service, which resolves them from its own configuration on every request.
    """

    def __init__(self, endpoint: Optional[str] = None, timeout: float = 10.0):
        endpoint = (endpoint if endpoint is not None
                    else os.environ.get(ENDPOINT_VAR, "")).strip()
        if not endpoint:
            raise EvaluatorNotConfigured(
                f"${ENDPOINT_VAR} is unset. The evaluator is a separate principal; without its "
                "endpoint there is no verdict to be had, and grading in-process is the thing this "
                "client exists to prevent.")
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------ transport
    def _call(self, path: str, body: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.endpoint}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(
            url, data=data, method="POST" if data else "GET",
            headers={"Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            # A 4xx is the service *refusing*, which is a real answer and must reach the caller
            # intact — collapsing it into "unreachable" would hide a rejected submission.
            detail = exc.read().decode("utf-8", "replace")[:400]
            try:
                payload = json.loads(detail)
            except Exception:                                      # noqa: BLE001
                payload = {"error": detail}
            payload.setdefault("http_status", exc.code)
            return payload
        except Exception as exc:                                   # noqa: BLE001
            raise EvaluatorUnreachable(
                f"{type(exc).__name__} calling {url}: {exc}. This is UNMEASURABLE - not a pass, "
                "and not a licence to score locally.") from exc

    # ------------------------------------------------------------------ verbs
    def health(self) -> Dict[str, Any]:
        """What the evaluator says it is. Used by the readiness probe, not by grading."""
        return self._call("/health")

    def submit(self, submission: Submission) -> RemoteVerdict:
        payload = self._call("/evaluate", submission.body())
        if "error" in payload and "verdict" not in payload:
            raise EvaluatorUnreachable(
                f"evaluator refused the submission: {payload.get('error')}")
        return RemoteVerdict.parse(payload)

    def verdict(self, run_id: str) -> RemoteVerdict:
        """Read back a verdict. Read-only: this client has no verb that writes one."""
        payload = self._call(f"/verdict/{urllib.parse.quote(run_id, safe='')}")
        if "error" in payload and "verdict" not in payload:
            raise EvaluatorUnreachable(f"no verdict for {run_id}: {payload.get('error')}")
        return RemoteVerdict.parse(payload)


def endpoint_mode(endpoint: str) -> str:
    """Rank the *deployment*, which is not the same as ranking the design.

    R3's table: an external service with its own identity is rank 1; a separate local process is
    rank 5 and "mostly theatre". Same code, same client, a different amount of protection — so
    the readiness gate reports this rather than letting a loopback URL read as isolation.
    """
    try:
        host = (urllib.parse.urlparse(endpoint).hostname or "").lower()
    except Exception:                                              # noqa: BLE001
        return "unparseable"
    if host in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        return "loopback"
    return "remote"
