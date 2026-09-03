"""ABSENT or UNAUTHORIZED? Snowflake will not tell you, so measure it separately.

⛔ WHY THIS EXISTS. Snowflake returns one message for two different worlds::

    Object 'TEST_DG1_GEP.WAREHOUSE.SALES_FCT_ORDERLINE' does not exist or not authorized.

*"does not exist OR not authorized"* is a deliberate conflation — it avoids leaking the existence
of objects you cannot see. That is good security and a terrible measurement: one branch means the
data was never landed in TEST, the other means the reading role is under-granted. The fixes are
unrelated, and guessing picks the wrong one half the time.

The catalogue separates them. `INFORMATION_SCHEMA.TABLES` shows what the current role can SEE;
`SHOW GRANTS TO ROLE` shows what it may READ. So:

    in catalogue + select works    -> READABLE
    in catalogue + select refused  -> UNAUTHORIZED_SELECT   (exists, USAGE only)
    not in catalogue               -> ABSENT_OR_INVISIBLE   (see the schema line below it)
    schema itself not listed       -> SCHEMA_ABSENT_OR_NO_USAGE

⚠ The residual ambiguity is named rather than hidden: a role with no USAGE on a schema cannot
distinguish an empty schema from a forbidden one, and this script says so instead of choosing.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Fully-qualified objects to test. Argv overrides.
DEFAULT = [
    "TEST_DG1_GEP.WAREHOUSE.SALES_FCT_ORDERLINE",
]

spec = importlib.util.spec_from_file_location(
    "r3boot", REPO / "scripts" / "snowflake_bootstrap_r3.py")
r3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r3)


def main() -> int:
    targets = sys.argv[1:] or DEFAULT
    conn = r3._connect(r3.RO_USER, r3.RO_SECRET, role=r3.RO_ROLE, warehouse="COMPUTE_WH",
                       purpose="object reachability probe (read-only)")
    try:
        cur = conn.cursor()
        cur.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 300")

        cur.execute(f"SHOW SCHEMAS IN DATABASE {r3.DATABASE}")
        schemas = {r[1] for r in cur.fetchall()}

        for fq in targets:
            parts = fq.split(".")
            if len(parts) != 3:
                print(f"  SKIPPED  {fq}  (need DB.SCHEMA.OBJECT)")
                continue
            db, sch, obj = parts

            if sch not in schemas:
                print(f"  SCHEMA_ABSENT_OR_NO_USAGE   {fq}")
                print(f"      {sch!r} is not among the {len(schemas)} schemas this role can see")
                continue

            cur.execute(
                "SELECT TABLE_TYPE, ROW_COUNT FROM INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s", (sch, obj))
            row = cur.fetchone()
            if not row:
                # In the catalogue's blind spot. Say what IS there, so "absent" is falsifiable.
                cur.execute(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s",
                    (sch,))
                n = cur.fetchone()[0]
                print(f"  ABSENT_OR_INVISIBLE         {fq}")
                print(f"      schema {sch} IS visible and lists {n} objects, but not {obj}")
                cur.execute(
                    "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s "
                    "AND TABLE_NAME LIKE %s ORDER BY TABLE_NAME LIMIT 8",
                    (sch, f"%{obj.split('_')[0]}%"))
                near = [r[0] for r in cur.fetchall()]
                if near:
                    print(f"      nearest names present: {', '.join(near)}")
                continue

            kind, rows = row
            # ⚠ NOT `COUNT(*)`. The question is "may this role read it", and a count on a fact
            # table answers that by scanning it — the first version of this probe timed out at
            # 120s against SALES_FCT_ORDERLINE and reported nothing at all. `LIMIT 1` settles
            # authorization for free; the row count is a separate and much more expensive
            # question, taken from the catalogue instead.
            try:
                cur.execute(f"SELECT 1 FROM {fq} LIMIT 1")
                got = cur.fetchone()
                catalogue = f"catalogue_rows={rows:,}" if rows is not None else "catalogue_rows=n/a"
                empty = "" if got else "   ⚠ readable but returned NO ROW"
                print(f"  READABLE                    {fq}  {kind}  {catalogue}{empty}")
            except Exception as exc:                                    # noqa: BLE001
                print(f"  UNAUTHORIZED_SELECT         {fq}  {kind}")
                print(f"      in the catalogue, SELECT refused: {type(exc).__name__}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
