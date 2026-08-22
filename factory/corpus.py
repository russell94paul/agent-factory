"""The eval corpus, loaded as tamper-evident data rather than executed as code.

The corpus is the known-good world every assertion is scored against. It used to be a Python
module inside this package, which meant two things, both bad:

  1. It was CODE. A module can construct any world it likes at import time, so "the corpus
     changed" and "the corpus computes something different today" were indistinguishable.
  2. It sat in a tree an agent working on this repo could write to. An agent that can edit its
     own grader is not graded.

Now it is a JSON document under `evals/`, hashed in `evals/MANIFEST.sha256`, and verified on every
load. Tampering is still *possible* — anyone with write access can edit both the file and the
manifest — but it is no longer *silent*, and the corpus id and hash travel with every verdict, so
a certification can be tied back to the exact world that produced it.

The three properties this gives, in the order they matter:

  EVIDENT     a changed corpus fails the hash check and raises, rather than quietly scoring
              differently
  ATTRIBUTED  every verdict records which corpus and which hash it was scored against
  SEPARABLE   `evals/` is a leaf with no imports from `factory/`, so it can be lifted into its own
              repository without touching a line of contract code

The remaining gap, stated plainly: separation is not yet *enforced*. Enforcement means the corpus
living in a repository the scored agent has no write credential for. `CORPUS_ROOT` honours
$AGENT_FACTORY_EVALS so that move is a config change, not a refactor.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
from typing import Any, Dict

_HERE = pathlib.Path(__file__).resolve().parent.parent

CORPUS_ROOT = pathlib.Path(os.environ.get("AGENT_FACTORY_EVALS", _HERE / "evals"))
MANIFEST = CORPUS_ROOT / "MANIFEST.sha256"


class CorpusError(Exception):
    """The corpus could not be loaded, or does not match its manifest.

    Deliberately not a plain ValueError: a corpus that will not verify must stop a run, never
    degrade into scoring against whatever was found on disk.
    """


def _manifest() -> Dict[str, str]:
    if not MANIFEST.is_file():
        raise CorpusError(
            f"no manifest at {MANIFEST} — refusing to score against an unverified corpus. "
            "Set $AGENT_FACTORY_EVALS to the corpus root.")
    out = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        sha, _, rel = line.partition("  ")
        if not sha or not rel:
            raise CorpusError(f"malformed manifest line: {line!r}")
        out[rel.strip()] = sha.strip()
    if not out:
        raise CorpusError(f"{MANIFEST} lists no corpus files")
    return out


def available() -> Dict[str, str]:
    """Corpus id -> expected sha256, from the manifest."""
    return {pathlib.Path(rel).stem: sha for rel, sha in _manifest().items()}


def load(corpus_id: str) -> Dict[str, Any]:
    """Load one corpus document, verifying its hash first.

    Returns the whole document — world plus provenance — so a caller can record what it scored
    against. Raises CorpusError on anything unexpected; never returns a partial or unverified
    world.
    """
    manifest = _manifest()
    rel = next((r for r in manifest if pathlib.Path(r).stem == corpus_id), None)
    if rel is None:
        raise CorpusError(
            f"corpus {corpus_id!r} is not in the manifest. Known: {sorted(available())}")
    path = CORPUS_ROOT / rel
    if not path.is_file():
        raise CorpusError(f"{rel} is listed in the manifest but missing from {CORPUS_ROOT}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != manifest[rel]:
        raise CorpusError(
            f"{rel} does not match its manifest.\n"
            f"  expected {manifest[rel]}\n  actual   {actual}\n"
            "The corpus has changed since it was pinned. If the change is intentional, re-pin it "
            "deliberately with scripts/pin_corpus.py and say why in the commit. Do not edit the "
            "manifest to make this go away.")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CorpusError(f"{rel} will not parse: {exc}") from exc
    doc["sha256"] = actual
    return doc


def stamp(corpus_id: str) -> Dict[str, str]:
    """The provenance block to attach to a verdict scored against this corpus."""
    doc = load(corpus_id)
    return {"corpus": doc["id"], "sha256": doc["sha256"],
            "recorded": doc.get("provenance", {}).get("recorded", "unknown"),
            "basis": doc.get("provenance", {}).get("basis", "unstated")}
