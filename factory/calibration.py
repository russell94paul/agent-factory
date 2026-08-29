"""The known-good world for windsorai — now loaded from the corpus, not constructed here.

This module used to BUILD the world in Python. It no longer does. `evals/corpus/` holds it as
hashed data and `factory.corpus` verifies it on load, so a changed corpus raises instead of
quietly scoring differently. See `factory/corpus.py` for why that distinction matters.

What remains here is the calibration *policy*: which corpus the windsorai target calibrates
against, and the one field the shipped blueprint deliberately leaves unmeasured.

Every number in the corpus traces to the 2026-08-20 run — flow run `responsible-pigeon`, 20 rows
under session `452d3402…` in `QA_DG1_GEP_PREFECT_PR.WINDSORAI__PR.google_ads_CAMPAIGN`, 18
distinct campaigns, 0 null spend, 0 null account, loaded 09:59:50Z for run date 2026-07-22.

⚠ **A finding, surfaced by building this, and now carried in the corpus document itself.** 20 rows
across 18 distinct campaigns on ONE date cannot satisfy a unique key of
(account_id, campaign_id, date) under a single account. The only arrangement consistent with the
measured counts is more than one account, with two campaign ids appearing under both — which is
what the corpus encodes. If the real table holds one account, then the declared primary key is
wrong and A9 will say so on the first live run. Either way the question is now explicit instead
of assumed.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, List

from . import corpus
from .connector_contract import ConnectorTarget
from .targets import load_target

CORPUS_ID = "windsorai-2026-08-20"
BLUEPRINT = Path(__file__).resolve().parent.parent / "blueprints" / "windsorai_client_a.yaml"


def _doc() -> Dict[str, Any]:
    return corpus.load(CORPUS_ID)


def calibration_target() -> ConnectorTarget:
    """The shipped blueprint, with the one unmeasured field filled so calibration can run.

    Filling it HERE and not in the blueprint is deliberate: the shipped target must keep
    reporting UNMEASURABLE for tenancy until a human supplies the real account ids. The
    calibration tenants come from the corpus, so the world and the target cannot drift apart.
    """
    return replace(load_target(BLUEPRINT), allowed_tenants=list(_doc()["tenants"]))


def known_good_world() -> dict:
    """The recorded world, hash-verified. Raises CorpusError rather than degrading."""
    return _doc()["world"]


def provenance() -> Dict[str, str]:
    """What this calibration was scored against — attach it to any verdict you publish."""
    return corpus.stamp(CORPUS_ID)


def _tenants() -> List[str]:
    return list(_doc()["tenants"])


# Kept for callers that referenced these directly. They now READ the corpus rather than define
# it, so there is one source of truth and no second place to edit.
SESSION = _doc()["session"]
RUN_DATE = _doc()["run_date"]
ACCOUNTS = _tenants()
