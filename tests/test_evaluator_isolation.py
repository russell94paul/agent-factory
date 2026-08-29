"""The isolation, proved able to refuse.

Same rule as ``test_corpus.py``: a boundary nobody has watched reject something is a diagram, not
a control. So every test here makes the evaluator *say no* to a specific attack an agent with
shell and repo write could actually mount — which is the threat model R3 ranked against, not a
malicious administrator.

The five refusals, and why each one is the interesting case:

  a fourth submission field   the agent trying to name its own corpus, manifest or grader
  a swapped artefact          claim one artefact, present another between claim and read
  a weakened blueprint        soften the target until the contract cannot fail
  substituted tenants         supply the answer key to A12 in the thing being graded
  a second verdict            replace an unkind verdict with a kinder one

Plus the one that is not a refusal but a *shape*: with the evaluator unreachable the client
produces UNMEASURABLE and never a pass. A client that graded locally when the grader was down
would make every other test here decorative.
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import threading
import urllib.error
import urllib.request

import pytest

from evaluator_service import service, store
from evaluator_service.app import make_server
from factory.evaluator import (ATTRIBUTION_FIELDS, SUBMISSION_FIELDS, EvaluatorClient,
                               EvaluatorNotConfigured, EvaluatorUnreachable, RemoteVerdict,
                               Submission, UnattributedVerdict, endpoint_mode)

REPO = pathlib.Path(__file__).resolve().parent.parent
BLUEPRINT = REPO / "blueprints" / "windsorai_gep.yaml"


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture()
def verdicts(tmp_path, monkeypatch):
    d = tmp_path / "verdicts"
    monkeypatch.setenv("AGENT_FACTORY_VERDICTS", str(d))
    return d


@pytest.fixture()
def evaluator(verdicts):
    """A real service on a real socket. The point is the transport, so do not fake it."""
    srv = make_server("127.0.0.1", 0, quiet=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        yield EvaluatorClient(f"http://127.0.0.1:{srv.server_address[1]}", timeout=20)
    finally:
        srv.shutdown()
        srv.server_close()


def _post(client: EvaluatorClient, body: dict):
    """Bypass Submission to send a body it could never construct. That is the whole test in a
    couple of cases: the dataclass has three fields, and an attacker does not have to use it."""
    req = urllib.request.Request(f"{client.endpoint}/evaluate",
                                 data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


# --------------------------------------------------------------------------- the shape

def test_the_client_has_no_import_path_to_the_grader():
    """``factory/evaluator.py`` must not import the contract, the corpus or the calibration.

    Read as an AST rather than grepped for strings — a probe that searches source text can match
    its own search terms, which has already cost this project one false PASS.

    Honest about what it proves: the agent could still write ``import
    factory.connector_contract`` in a new file. This asserts the *client* offers no such path, so
    grading locally is a deliberate act rather than a fallback that fires under load.
    """
    tree = ast.parse((REPO / "factory" / "evaluator.py").read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
            imported.update(f"{node.module}.{a.name}" for a in node.names)
    forbidden = {"connector_contract", "corpus", "calibration", "certify", "targets"}
    leaked = sorted(m for m in imported if any(f in m.split(".") for f in forbidden))
    assert not leaked, f"the client can reach the grader through {leaked}"


def test_no_endpoint_is_not_a_licence_to_grade_locally(monkeypatch):
    monkeypatch.delenv("AGENT_FACTORY_EVALUATOR", raising=False)
    with pytest.raises(EvaluatorNotConfigured):
        EvaluatorClient()


def test_an_unreachable_evaluator_is_unmeasurable_and_never_a_pass(verdicts):
    """Port 1 on loopback answers nothing. The client must refuse, not improvise."""
    client = EvaluatorClient("http://127.0.0.1:1", timeout=2)
    with pytest.raises(EvaluatorUnreachable) as exc:
        client.submit(Submission(BLUEPRINT.as_uri(), _sha(BLUEPRINT), "run-dead"))
    assert "UNMEASURABLE" in str(exc.value)


def test_the_submission_vocabulary_is_three_fields():
    assert SUBMISSION_FIELDS == ("artifact_uri", "artifact_sha256", "run_id")
    assert set(Submission.__dataclass_fields__) == set(SUBMISSION_FIELDS)


# --------------------------------------------------------------------------- the refusals

def test_a_fourth_submission_field_is_refused_not_ignored(evaluator):
    """An agent naming its own corpus. Refused loudly — silently dropping the key would let the
    submitter believe it had been honoured, and would let a future field slip in unnoticed."""
    status, payload = _post(evaluator, {"artifact_uri": BLUEPRINT.as_uri(),
                                        "artifact_sha256": _sha(BLUEPRINT),
                                        "run_id": "run-smuggle",
                                        "corpus_path": "/tmp/my-friendly-corpus"})
    assert status == 400
    assert "corpus_path" in payload["error"]
    assert "verdict" not in payload


def test_a_swapped_artefact_is_refused_rather_than_scored(evaluator, tmp_path):
    """Claim the real blueprint's hash, present a different file. The service reads the bytes."""
    other = tmp_path / "other.yaml"
    other.write_text("connector: x\nclient: y\ndeployment: z\nlanding_table: t\n", encoding="utf-8")
    verdict = evaluator.submit(Submission(other.as_uri(), _sha(BLUEPRINT), "run-swap"))
    assert verdict.verdict == "REFUSED"
    assert not verdict.promotable
    assert "sha256 mismatch" in verdict.raw["detail"]


def test_a_weakened_blueprint_is_refused(evaluator, tmp_path):
    """The attack that survives the process boundary: soften the target instead of the grader.

    ``expect_rows: false`` with no primary key and no non-null column is a contract an empty
    table passes. The floor is held by the evaluator, so the submitter cannot lower it.
    """
    weak = tmp_path / "weak.yaml"
    weak.write_text(
        "connector: windsorai\nclient: GEP\ndeployment: d\n"
        "landing_table: t\nexpect_rows: false\nprimary_key: []\n"
        "non_null_positive: []\ntenant_column: ''\n", encoding="utf-8")
    verdict = evaluator.submit(Submission(weak.as_uri(), _sha(weak), "run-weak"))
    assert verdict.verdict == "REFUSED"
    detail = verdict.raw["detail"]
    assert "weaker than this evaluator's floor" in detail
    for expected in ("primary_key", "non_null_positive", "expect_rows", "tenant_column"):
        assert expected in detail


def test_the_service_supplies_the_tenants_not_the_submission(evaluator, tmp_path):
    """A12's answer key comes from the corpus, so a blueprint listing the wrong tenants is
    irrelevant to calibration rather than fatal to it.

    Discriminating on purpose: the shipped blueprint's six dash-formatted account ids do NOT
    appear in the corpus, whose tenants are two ten-digit ids. If the submission governed
    tenancy, A12 would FAIL here. It passes, which is only possible if the service overrode it.
    """
    text = BLUEPRINT.read_text(encoding="utf-8")
    assert "1234567890" not in text, "the blueprint must not already carry the corpus tenants"
    verdict = evaluator.submit(Submission(BLUEPRINT.as_uri(), _sha(BLUEPRINT), "run-tenants"))
    a12 = next(a for a in verdict.assertions if a["name"].startswith("A12"))
    assert a12["verdict"] == "PASS", a12
    assert "2 declared tenant" in a12["detail"]


def test_a_verdict_cannot_be_replaced_by_a_kinder_one(evaluator, verdicts):
    """Write-once. The second submission under the same run id is scored but not recorded, and
    says so — a silent no-op would leave the caller believing the store had been updated."""
    sub = Submission(BLUEPRINT.as_uri(), _sha(BLUEPRINT), "run-once")
    first = evaluator.submit(sub)
    assert first.raw["recorded_to"], "the first verdict should reach the store"
    second = evaluator.submit(sub)
    assert second.raw["recorded_to"] is None
    assert "write-once" in second.raw["store_error"]
    assert store.read("run-once", verdicts)["recorded_at"] == first.raw["recorded_at"]


def test_a_run_id_that_shapes_a_path_is_refused(verdicts):
    with pytest.raises(store.StoreError) as exc:
        store.record({"run_id": "../../evil"}, verdicts)
    assert "not a safe key" in str(exc.value)


# --------------------------------------------------------------------------- attribution

#: A fully attributed block, to vary one field at a time against.
_WHO = {"identity": "e", "bundle_sha256": "a" * 64}
_WORLD = {"corpus": "c", "sha256": "b" * 64, "recorded": "2026-08-20"}


@pytest.mark.parametrize("payload, why", [
    ({"verdict": "PASS", "promotable": True, "run_id": "x"},
     "the keys are absent"),
    # ⛔ The case the old test could not reach: the keys are PRESENT and say nothing. Until
    # 2026-08-29 this parsed, reported "PASS … by unidentified, bundle ?" with promotable=True,
    # and `certify --remote` exited 0 on it. Key presence is not attribution.
    ({"verdict": "PASS", "promotable": True, "run_id": "x",
      "evaluator": None, "scored_against": None},
     "the keys are present and null"),
    ({"verdict": "PASS", "promotable": True, "run_id": "x",
      "evaluator": {}, "scored_against": _WORLD},
     "the evaluator block is empty"),
    ({"verdict": "PASS", "promotable": True, "run_id": "x",
      "evaluator": {"bundle_sha256": "a" * 64}, "scored_against": _WORLD},
     "no identity"),
    ({"verdict": "PASS", "promotable": True, "run_id": "x",
      "evaluator": {"identity": "e"}, "scored_against": _WORLD},
     "no bundle hash — two disagreeing verdicts could not be told apart"),
    ({"verdict": "PASS", "promotable": True, "run_id": "x",
      "evaluator": {"identity": "  ", "bundle_sha256": "a" * 64}, "scored_against": _WORLD},
     "an identity of whitespace names nobody"),
    ({"verdict": "PASS", "promotable": True, "run_id": "x",
      "evaluator": "local-process", "scored_against": _WORLD},
     "the evaluator is a string, not an attribution block"),
    ({"verdict": "PASS", "promotable": True, "run_id": "x",
      "evaluator": _WHO, "scored_against": None},
     "a scored verdict that names no world"),
    ({"verdict": "FAIL", "promotable": False, "run_id": "x",
      "evaluator": _WHO, "scored_against": {"sha256": "b" * 64}},
     "a scored_against block with no corpus in it"),
])
def test_an_unattributed_verdict_is_not_believed(payload, why):
    """Anything on a socket can emit the string PASS. Only an attributed one counts.

    Each case is a verdict that would otherwise have been believed AND marked promotable. The
    null-keys case is the one the previous version of this test omitted the keys for, and
    therefore pinned presence rather than content — a guarantee whose test cannot catch its own
    violation.
    """
    with pytest.raises(UnattributedVerdict):
        RemoteVerdict.parse(payload)


def test_a_fully_attributed_verdict_still_parses():
    """The positive control. Without it, every case above would also pass if parse() raised on
    everything."""
    v = RemoteVerdict.parse({"verdict": "PASS", "promotable": True, "run_id": "x",
                             "evaluator": _WHO, "scored_against": _WORLD})
    assert v.is_pass and v.promotable
    assert "unidentified" not in v.summary()


@pytest.mark.parametrize("verdict", ["REFUSED", "UNMEASURABLE", "NOT_RUN"])
def test_an_honest_refusal_may_name_no_corpus(verdict):
    """The service emits scored_against=None for these on purpose — nothing was scored. Refusing
    to parse them would turn an honest refusal into an unusable one, and the caller would lose the
    reason. They still have to say who refused."""
    v = RemoteVerdict.parse({"verdict": verdict, "promotable": False, "run_id": "x",
                             "evaluator": _WHO, "scored_against": None})
    assert v.verdict == verdict and not v.is_pass and not v.promotable


def test_promotable_cannot_outrun_the_verdict():
    payload = {"verdict": "FAIL", "promotable": True, "run_id": "x",
               "evaluator": _WHO, "scored_against": _WORLD}
    assert RemoteVerdict.parse(payload).promotable is False


def test_a_real_verdict_names_its_grader_and_its_world(evaluator):
    verdict = evaluator.submit(Submission(BLUEPRINT.as_uri(), _sha(BLUEPRINT), "run-attrib"))
    for field in ATTRIBUTION_FIELDS:
        assert field in verdict.raw
    assert len(verdict.evaluator["bundle_sha256"]) == 64
    assert verdict.scored_against["corpus"] == service.corpus_id()
    assert len(verdict.scored_against["sha256"]) == 64
    # A verdict that cannot say when its world was recorded cannot be aged out.
    assert verdict.scored_against["recorded"] != "unknown"


def test_the_known_good_world_still_scores_green_through_the_service(evaluator):
    """The positive control. Without it, every refusal above could be a service that says no to
    everything — which would also pass all of them."""
    verdict = evaluator.submit(Submission(BLUEPRINT.as_uri(), _sha(BLUEPRINT), "run-green"))
    assert verdict.verdict == "PASS"
    assert verdict.promotable
    assert len(verdict.assertions) == 12
    assert all(a["verdict"] == "PASS" for a in verdict.assertions)


def test_a_verdict_can_be_read_back_but_not_written(evaluator):
    evaluator.submit(Submission(BLUEPRINT.as_uri(), _sha(BLUEPRINT), "run-readback"))
    assert evaluator.verdict("run-readback").verdict == "PASS"
    assert not hasattr(evaluator, "write_verdict")
    # The client's whole verb surface, stated so adding a writer is a visible decision.
    verbs = {n for n in dir(evaluator) if not n.startswith("_") and callable(getattr(evaluator, n))}
    assert verbs == {"health", "submit", "verdict"}


# --------------------------------------------------------------------------- honesty

def test_a_loopback_deployment_is_reported_as_rank_5_not_as_isolation():
    """R3: a separate local process is 'mostly theatre'. The code cannot fix that, so it must at
    least refuse to describe it as something better."""
    assert endpoint_mode("http://127.0.0.1:8787") == "loopback"
    assert endpoint_mode("http://localhost:8787") == "loopback"
    assert endpoint_mode("https://evaluator.internal.aldc.io") == "remote"
