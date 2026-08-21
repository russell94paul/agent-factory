"""The known-good world for windsorai, built from measured facts.

Calibration comes before judgement: run the contract against a world we know was green, and
against deliberately broken variants of it, before it is allowed to judge anything unproven.

Every number here traces to the 2026-08-20 run — flow run `responsible-pigeon`, 20 rows under
session `452d3402…` in `QA_DG1_GEP_PREFECT_PR.WINDSORAI__PR.google_ads_CAMPAIGN`, 18 distinct
campaigns, 0 null spend, 0 null account, loaded 09:59:50Z for run date 2026-07-22.

⚠ **A finding, surfaced by building this.** 20 rows across 18 distinct campaigns on ONE date
cannot satisfy a unique key of (account_id, campaign_id, date) under a single account. The only
arrangement consistent with the measured counts is more than one account, with two campaign ids
appearing under both — which is what this world encodes. If the real table holds one account,
then the declared primary key is wrong and A9 will say so on the first live run. Either way the
question is now explicit instead of assumed.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, List

from .connector_contract import ConnectorTarget
from .targets import load_target

SESSION = "452d3402-0000-4000-8000-000000000000"
RUN_DATE = "2026-07-22"
ACCOUNTS = ["1234567890", "9876543210"]          # placeholder ids, real shape (10-digit Google Ads)
MERGE_EPOCH = 1787305611                          # 2026-08-20T09:46:51Z
IMAGE_EPOCH = 1787305818                          # 2026-08-20T09:50:18Z
BLUEPRINT = Path(__file__).resolve().parent.parent / "blueprints" / "windsorai_gep.yaml"


def calibration_target() -> ConnectorTarget:
    """The shipped blueprint, with the two unmeasured fields filled so calibration can run.

    Filling them HERE and not in the blueprint is deliberate: the shipped target must keep
    reporting UNMEASURABLE for tenancy until a human supplies the real account ids.
    """
    return replace(load_target(BLUEPRINT), allowed_tenants=ACCOUNTS)


def _rows() -> List[Dict[str, Any]]:
    rows = []
    for i in range(18):                                   # 18 distinct campaigns
        rows.append({"account_id": ACCOUNTS[0], "campaign_id": f"c{i:03d}",
                     "date": RUN_DATE, "spend": 10.0 + i,
                     "___ALDC___GLOBAL_SESSION_ID___": SESSION})
    for i in range(2):                                    # 2 of them also ran under account 2
        rows.append({"account_id": ACCOUNTS[1], "campaign_id": f"c{i:03d}",
                     "date": RUN_DATE, "spend": 5.0 + i,
                     "___ALDC___GLOBAL_SESSION_ID___": SESSION})
    return rows                                           # 20 rows, matching the measured count


def known_good_world() -> dict:
    rows = _rows()
    per_key: Dict[str, int] = {}
    for r in rows:
        per_key[r["account_id"]] = per_key.get(r["account_id"], 0) + 1
    return {
        "config": {"constructed": ["WindsorAiConnection", "WindsorAiOptions"], "accounts": ACCOUNTS},
        "credential": {"status": 200, "payload_keys": ["data"]},
        "image": {"digest": "sha256:d2d7193bc096ae149", "imports": True,
                  "commit": "4db9556", "built_at": IMAGE_EPOCH},
        "deployment": {"id": "dep-windsorai-gep", "image_digest": "sha256:d2d7193bc096ae149"},
        "suite": {"passed": 721, "failed": 0, "revision": ""},
        "run": {"id": "responsible-pigeon", "state": "COMPLETED",
                "session_id": SESSION, "emitted_rows": len(rows)},
        "landed": {"rows": rows},
        "source": {"per_key_counts": per_key},
        "forbidden": {"secret_hits": 0, "out_of_scope_writes": [],
                      "tests_modified": [], "gates_bypassed": []},
    }
