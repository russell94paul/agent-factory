"""The evaluator, as a principal rather than a function call.

Everything the grading depends on is resolved **here**, from this service's own configuration, on
every request:

    the corpus            $AGENT_FACTORY_EVALUATOR_CORPUS   (never from the submission)
    the corpus root       $AGENT_FACTORY_EVALS              (this service's copy)
    the assertion set     factory.connector_contract        (hashed into every verdict)
    the identity          $AGENT_FACTORY_EVALUATOR_IDENTITY
    the verdict store     $AGENT_FACTORY_VERDICTS           (write-once, see store.py)

The submission carries three fields and cannot carry a fourth: a body with an unknown key is
refused, not quietly filtered. Silently ignoring a key is how an assertion stops being made — the
same failure ``targets.load_target`` already guards against for blueprints.

Four things this service refuses, each with its own verdict rather than a FAIL that hides the
reason:

  REFUSED  the submitted sha256 does not match the bytes on disk. The artefact was swapped
           between claiming and reading, or the claim was never true. Not a FAIL — we never
           scored anything.
  REFUSED  the body carries a field outside the submission vocabulary.
  REFUSED  the artefact is a blueprint weakened below the floor this service holds (see
           ``_enforce_target_floor``).
  UNMEASURABLE  the corpus will not verify. Read *before* scoring, so an unverifiable world
           raises here rather than producing an unattributable verdict.

⚠ **The weakness this design does not close, named rather than papered over.** The contract is
parameterised by a target, and the target is a blueprint the graded party writes. An agent that
softens its own blueprint — ``expect_rows: false``, an empty ``primary_key`` — softens its own
grading no matter where the evaluator runs. Two partial answers are implemented, and neither is
complete: the artefact hash travels with the verdict, so a weakened blueprint is attributable
rather than silent; and ``_enforce_target_floor`` holds a small set of expectations the submitter
may not drop below. The real fix is a target pinned by the evaluator, which needs a per-connector
policy nobody has written yet. It is a finding, not a solved problem.
"""
from __future__ import annotations

import datetime
import hashlib
import os
import pathlib
import urllib.parse
from dataclasses import replace
from typing import Any, Dict, List, Optional, Tuple

from factory import corpus
from factory.connector_contract import CtxProbes, ConnectorTarget, build_contract
from factory.contract import Verdict
from factory.evaluator import SUBMISSION_FIELDS
from factory.targets import load_target

from . import store

#: The files that decide what a verdict means. Hashed together into every verdict so two verdicts
#: produced by different evaluator builds can never be compared as though they agreed.
BUNDLE = ("factory/contract.py", "factory/connector_contract.py", "factory/corpus.py",
          "factory/targets.py", "evaluator_service/service.py", "evaluator_service/store.py")

REPO = pathlib.Path(__file__).resolve().parent.parent

REFUSED = "REFUSED"


class Refused(Exception):
    """The submission was not scored, and the reason is not the artefact being wrong."""


def identity() -> str:
    return os.environ.get("AGENT_FACTORY_EVALUATOR_IDENTITY", "local-process").strip() or "local-process"


def corpus_id() -> str:
    return os.environ.get("AGENT_FACTORY_EVALUATOR_CORPUS", "windsorai-2026-08-20").strip()


def bundle_sha256() -> str:
    """One hash over the evaluator's own source.

    Not a signature and not claimed to be one — a signing key inside the agent sandbox is
    theatre, and R3 says so. This is the weaker, useful property: two verdicts that disagree can
    be checked for whether they were even produced by the same grader.
    """
    h = hashlib.sha256()
    for rel in BUNDLE:
        p = REPO / rel
        h.update(rel.encode("utf-8"))
        h.update(hashlib.sha256(p.read_bytes()).digest() if p.is_file() else b"\0" * 32)
    return h.hexdigest()


def describe() -> Dict[str, Any]:
    """What this evaluator is, for /health and for the attribution block on every verdict."""
    return {"identity": identity(), "bundle_sha256": bundle_sha256(),
            "corpus_id": corpus_id(), "corpus_root": str(corpus.CORPUS_ROOT),
            "verdict_store": str(store.store_root()), "submission_fields": list(SUBMISSION_FIELDS)}


# --------------------------------------------------------------------------- submission

def parse_submission(body: Dict[str, Any]) -> Dict[str, str]:
    """Accept exactly the three fields, and refuse a body carrying anything else."""
    if not isinstance(body, dict):
        raise Refused("submission must be a JSON object")
    unknown = sorted(set(body) - set(SUBMISSION_FIELDS))
    if unknown:
        raise Refused(
            f"submission carries field(s) {unknown}, which are not part of the submission "
            f"vocabulary {list(SUBMISSION_FIELDS)}. The graded party supplies the artefact and "
            "nothing else — not the corpus, not the manifest, not the evaluator.")
    missing = [f for f in SUBMISSION_FIELDS if not str(body.get(f, "")).strip()]
    if missing:
        raise Refused(f"submission is missing {missing}")
    return {f: str(body[f]).strip() for f in SUBMISSION_FIELDS}


def read_artifact(uri: str, claimed_sha256: str) -> Tuple[pathlib.Path, str]:
    """Read the artefact independently and hold it to the hash that was claimed for it.

    The service reads the bytes; it does not take the submitter's word for what they were. A
    mismatch is a refusal, never a score — "the artefact I graded is not the artefact you named"
    has no honest FAIL to report.
    """
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme in ("", "file"):
        raw = urllib.parse.unquote(parsed.path if parsed.scheme == "file" else uri)
        # file:///C:/x on Windows arrives as /C:/x
        if os.name == "nt" and len(raw) > 2 and raw[0] == "/" and raw[2] == ":":
            raw = raw[1:]
        path = pathlib.Path(raw)
    else:
        raise Refused(
            f"unsupported artifact scheme {parsed.scheme!r}. A deployed evaluator reads from an "
            "object store the agent can write and the evaluator can read; this build reads "
            "file:// only.")
    if not path.is_file():
        raise Refused(f"artifact not readable at {path}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual.lower() != claimed_sha256.strip().lower():
        raise Refused(
            f"artifact sha256 mismatch — claimed {claimed_sha256}, read {actual}. Refusing to "
            "score: the artefact evaluated would not be the artefact submitted.")
    return path, actual


#: Expectations the submitter may not drop below. Deliberately short — a floor nobody can state
#: the reason for is a rule that gets deleted the first time it is inconvenient.
def _enforce_target_floor(target: ConnectorTarget) -> None:
    problems: List[str] = []
    if not target.primary_key:
        problems.append("primary_key is empty — A9 cannot test uniqueness of nothing")
    if not target.non_null_positive:
        problems.append("non_null_positive is empty — the SILENT-EMPTY shape would score green")
    if not target.expect_rows:
        problems.append("expect_rows is false — an empty extraction would satisfy the contract")
    if not target.tenant_column:
        problems.append("tenant_column is unset — A12 cannot test whose rows landed")
    if problems:
        raise Refused(
            "the submitted blueprint is weaker than this evaluator's floor: "
            + "; ".join(problems)
            + ". A target the graded party can soften is a contract the graded party can pass.")


# --------------------------------------------------------------------------- evaluation

def evaluate(body: Dict[str, Any], *, store_root: Optional[pathlib.Path] = None) -> Dict[str, Any]:
    """Score one submission and record the verdict. The whole service, minus transport."""
    sub = parse_submission(body)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    attribution = {"evaluator": describe(), "run_id": sub["run_id"],
                   "artifact_uri": sub["artifact_uri"], "recorded_at": now}

    try:
        path, sha = read_artifact(sub["artifact_uri"], sub["artifact_sha256"])
        target = load_target(path)
        _enforce_target_floor(target)
    except Refused as exc:
        payload = {**attribution, "artifact_sha256": sub["artifact_sha256"],
                   "verdict": REFUSED, "promotable": False, "scored_against": None,
                   "assertions": [], "detail": str(exc)}
        _record(payload, store_root)
        return payload
    except Exception as exc:                                       # noqa: BLE001
        payload = {**attribution, "artifact_sha256": sub["artifact_sha256"],
                   "verdict": REFUSED, "promotable": False, "scored_against": None,
                   "assertions": [], "detail": f"artefact unusable: {type(exc).__name__}: {exc}"}
        _record(payload, store_root)
        return payload

    # Read the stamp BEFORE scoring. An unverifiable corpus must stop the run rather than produce
    # a verdict nobody can tie to a world — same rule certify.py follows, for the same reason.
    try:
        scored_against = corpus.stamp(corpus_id())
        doc = corpus.load(corpus_id())
    except Exception as exc:                                       # noqa: BLE001
        payload = {**attribution, "artifact_sha256": sha, "verdict": Verdict.UNMEASURABLE.value,
                   "promotable": False, "scored_against": None, "assertions": [],
                   "detail": f"corpus {corpus_id()!r} will not verify: {exc}"}
        _record(payload, store_root)
        return payload

    # The tenants come from the SERVICE's corpus, never from the submitted blueprint. This is the
    # one place the two could drift, and letting the submitter set them would hand the graded
    # party the answer key to A12.
    target = replace(target, allowed_tenants=list(doc["tenants"]))
    result = build_contract(target, CtxProbes()).run(doc["world"])

    payload = {**attribution, "artifact_sha256": sha, "contract": result.contract,
               "verdict": result.verdict.value,
               "promotable": result.verdict is Verdict.PASS,
               "scored_against": scored_against,
               "assertions": [{"name": r.name, "verdict": r.verdict.value, "detail": r.detail}
                              for r in result.results]}
    _record(payload, store_root)
    return payload


def _record(payload: Dict[str, Any], root: Optional[pathlib.Path]) -> None:
    """Record the verdict, and say so in the verdict when it could not be recorded.

    A verdict that failed to reach the store is still returned to the caller — but it is marked,
    because an unrecorded verdict is one nobody else can check.
    """
    try:
        payload["recorded_to"] = str(store.record(payload, root))
    except store.StoreError as exc:
        payload["recorded_to"] = None
        payload["store_error"] = str(exc)
