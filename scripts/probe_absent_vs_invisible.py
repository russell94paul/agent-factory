"""ABSENT or INVISIBLE — triangulate, because the catalogue alone cannot tell R3 apart from absent.

A secure view executes with its OWNER's rights. So REPORT_COMMON.MARKETING_EFFICIENCY resolving
does not prove R3 can see WAREHOUSE.SALES_FCT_ORDERLINE, and R3 failing to see it does not prove
it is gone. Three readings, printed side by side, so the inference is visible rather than asserted.
"""
from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "r3boot", REPO / "scripts" / "snowflake_bootstrap_r3.py")
r3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r3)

conn = r3._connect(r3.RO_USER, r3.RO_SECRET, role=r3.RO_ROLE, warehouse="COMPUTE_WH",
                   purpose="triangulate absent-vs-invisible for WAREHOUSE.SALES_FCT_ORDERLINE")
cur = conn.cursor()
cur.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 300")

print("1. SHOW VIEWS / TABLES named SALES_FCT_ORDERLINE in WAREHOUSE (role-visible only)")
for kind in ("VIEWS", "TABLES"):
    cur.execute(f"SHOW {kind} LIKE 'SALES_FCT_ORDERLINE%' IN SCHEMA TEST_DG1_GEP.WAREHOUSE")
    rows = cur.fetchall()
    print(f"   SHOW {kind:<7} -> {len(rows)}: {[r[1] for r in rows]}")

print("\n2. direct SELECT as R3 — the dashboard's own path")
try:
    cur.execute("SELECT 1 FROM TEST_DG1_GEP.WAREHOUSE.SALES_FCT_ORDERLINE LIMIT 1")
    print(f"   READ OK -> {cur.fetchone()}")
except Exception as exc:                                                # noqa: BLE001
    print(f"   REFUSED -> {str(exc).splitlines()[0]}")

print("\n3. the secure-view chain that depends on it (owner's rights)")
for v in ("MARKETING_EFFICIENCY", "MARKETING_EFFICIENCY_MARGIN"):
    try:
        cur.execute(f"SELECT COUNT(*) FROM TEST_DG1_GEP.REPORT_COMMON.{v}")
        print(f"   {v:<28} rows={cur.fetchone()[0]:,}")
    except Exception as exc:                                            # noqa: BLE001
        print(f"   {v:<28} REFUSED -> {str(exc).splitlines()[0]}")

print("\n4. is the dependency real? ask the account's own lineage view")
try:
    cur.execute("""
        SELECT REFERENCED_DATABASE, REFERENCED_SCHEMA, REFERENCED_OBJECT_NAME,
               REFERENCED_OBJECT_DOMAIN
        FROM SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES
        WHERE REFERENCING_OBJECT_NAME = 'MARKETING_EFFICIENCY'
          AND REFERENCED_OBJECT_NAME LIKE 'SALES_FCT_ORDERLINE%'
        LIMIT 10""")
    rows = cur.fetchall()
    print(f"   {len(rows)} dependency rows: {rows}")
except Exception as exc:                                                # noqa: BLE001
    print(f"   ACCOUNT_USAGE not readable by this role -> {str(exc).splitlines()[0]}")

conn.close()
