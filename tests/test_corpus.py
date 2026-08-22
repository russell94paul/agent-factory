"""The corpus guard, proved able to fail.

A hash check nobody has watched reject something is the same as an eval nobody has watched fail:
you have a mechanism, not a control. These tests mutate a real corpus on disk and require the
loader to refuse — including the one mutation that matters, where the tampered world would turn a
red run green.
"""
from __future__ import annotations

import hashlib
import json
import shutil

import pytest

from factory import corpus


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    """A throwaway copy of the real corpus, so a failing test cannot damage the pinned one."""
    src = corpus.CORPUS_ROOT
    dst = tmp_path / "evals"
    shutil.copytree(src, dst)
    monkeypatch.setattr(corpus, "CORPUS_ROOT", dst)
    monkeypatch.setattr(corpus, "MANIFEST", dst / "MANIFEST.sha256")
    return dst


def _corpus_file(root):
    return next((root / "corpus").glob("*.json"))


def test_the_pinned_corpus_verifies(sandbox):
    ids = corpus.available()
    assert ids, "the manifest should pin at least one corpus"
    for cid in ids:
        doc = corpus.load(cid)
        assert doc["sha256"] == ids[cid]


def test_a_tampered_world_is_refused(sandbox):
    """The mutation that matters: make the recorded run claim a state it did not have.

    Without the hash check this edit is invisible — the contract would score a FAILED run as a
    completed one and report PASS, which is the exact defect the whole programme exists to stop.
    """
    p = _corpus_file(sandbox)
    doc = json.loads(p.read_text(encoding="utf-8"))
    doc["world"]["run"]["state"] = "FAILED"
    p.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(corpus.CorpusError) as exc:
        corpus.load(doc["id"])
    assert "does not match its manifest" in str(exc.value)


def test_a_single_byte_is_enough(sandbox):
    p = _corpus_file(sandbox)
    p.write_bytes(p.read_bytes() + b" ")
    with pytest.raises(corpus.CorpusError):
        corpus.load(next(iter(corpus.available())))


def test_a_missing_manifest_refuses_rather_than_trusting_disk(sandbox):
    (sandbox / "MANIFEST.sha256").unlink()
    with pytest.raises(corpus.CorpusError) as exc:
        corpus.available()
    assert "refusing to score" in str(exc.value)


def test_a_corpus_listed_but_absent_is_an_error_not_an_empty_world(sandbox):
    _corpus_file(sandbox).unlink()
    with pytest.raises(corpus.CorpusError) as exc:
        corpus.load(next(iter(corpus.available())))
    assert "missing" in str(exc.value)


def test_an_unknown_corpus_id_names_what_is_known(sandbox):
    with pytest.raises(corpus.CorpusError) as exc:
        corpus.load("no-such-corpus")
    assert "Known:" in str(exc.value)


def test_the_stamp_carries_enough_to_attribute_a_verdict(sandbox):
    cid = next(iter(corpus.available()))
    stamp = corpus.stamp(cid)
    assert stamp["corpus"] == cid
    assert len(stamp["sha256"]) == 64
    # A verdict that cannot say WHEN its world was recorded cannot be aged out.
    assert stamp["recorded"] != "unknown"


def test_editing_the_manifest_to_match_is_possible_and_that_is_the_known_gap(sandbox):
    """Documents the limit honestly: this is tamper-EVIDENT, not tamper-PROOF.

    Anyone with write access to both files can re-pin silently. The gate in factory.readiness
    reports exactly this, and the fix is credential separation, not a cleverer hash.
    """
    p = _corpus_file(sandbox)
    doc = json.loads(p.read_text(encoding="utf-8"))
    doc["world"]["run"]["state"] = "FAILED"
    p.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rel = p.relative_to(sandbox).as_posix()
    (sandbox / "MANIFEST.sha256").write_text(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}\n", encoding="utf-8")

    assert corpus.load(doc["id"])["world"]["run"]["state"] == "FAILED"
