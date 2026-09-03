"""Does TEST hold current marketing data? Read-only, as R3_CARTOGRAPHY.

⛔ WHY THIS RUNS BEFORE THE RENDER LANE. The mission checkpoint flags TEST's marketing-data
currency as UNVERIFIED: a Navira re-land into TEST was *planned, not executed*, and Lectric
confirmed "greenfield in TEST (no objects)". The warehouse Playwright lane asserts presence /
non-blank / positivity. If the tables behind it are empty, the lane fails **correctly** and filing
that as a dashboard defect would be a false FAIL aimed at the wrong layer.

  PRESENT_WITH_DATA  rows > 0
  PRESENT_EMPTY      the object exists and holds nothing   <- NOT the same as missing
  ABSENT             no such object
  UNREADABLE         exists, this role cannot select it

⚠ AUTH. R3_CARTOGRAPHY is **key-pair**, not password — a first version of this script assumed a
password and got `250001 (08001) Incorrect username or password`, which reads like a wrong
credential and is actually a wrong *auth method*. So this does not reimplement the connection: it
imports `_connect` from scripts/snowflake_bootstrap_r3.py, the path already proved today, which
branches on `-----BEGIN` and logs the credential use itself.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = "WAREHOUSE_TEST_GP226"          # warehouse.ts:2029 — the app's default schema

TABLES = [
    "MARKETING_FCT_ACTIVITY_UNIFIED",
    "MARKETING_ATTRIBUTED_ROAS_BY_BRAND",
    "MARKETING_ATTRIBUTED_SALES_BY_DEST",
    "MARKETING_GOOGLE_SPEND_BY_DEST",
    "MARKETING_META_SPEND_BY_DEST",
    "SHARED_DIM_MARKETPLACE",
]

spec = importlib.util.spec_from_file_location(
    "r3boot", REPO / "scripts" / "snowflake_bootstrap_r3.py")
r3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r3)


def main() -> int:
    conn = r3._connect(r3.RO_USER, r3.RO_SECRET, role=r3.RO_ROLE, warehouse="COMPUTE_WH",
                       purpose="TEST marketing-data currency probe (read-only)")
    try:
        cur = conn.cursor()
        cur.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 180")

        cur.execute(
            "SELECT TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s",
            (SCHEMA,))
        cat = {r[0]: r[1] for r in cur.fetchall()}
        print(f"{r3.DATABASE}.{SCHEMA} — {len(cat)} objects visible to {r3.RO_ROLE}\n")

        for t in TABLES:
            if t not in cat:
                print(f"  ABSENT              {t}")
                continue
            try:
                cur.execute(f"SELECT COUNT(*) FROM {r3.DATABASE}.{SCHEMA}.{t}")
                n = cur.fetchone()[0]
            except Exception as exc:                                    # noqa: BLE001
                print(f"  UNREADABLE          {t}  ({type(exc).__name__})")
                continue

            when = ""
            cur.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND "
                "TABLE_NAME=%s AND DATA_TYPE IN ('DATE','TIMESTAMP_NTZ','TIMESTAMP_LTZ',"
                "'TIMESTAMP_TZ') ORDER BY ORDINAL_POSITION LIMIT 1", (SCHEMA, t))
            row = cur.fetchone()
            if row and n:
                col = row[0]
                cur.execute(f"SELECT MIN({col}), MAX({col}) FROM {r3.DATABASE}.{SCHEMA}.{t}")
                lo, hi = cur.fetchone()
                when = f"   {col}  {lo} -> {hi}"
            elif not row:
                when = "   (no date column)"

            print(f"  {'PRESENT_WITH_DATA ' if n else 'PRESENT_EMPTY     '}  {t}"
                  f"  rows={n:,}{when}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
