"""Restore — and stop the decay of — a reader role's SELECT on a task-refreshed schema.

⛔ **THE DEFECT THIS FIXES.** `WAREHOUSE_SOURCE` copies into `WAREHOUSE` through a task chain. A
task doing `CREATE OR REPLACE` **drops the object and takes its grants with it**, so a role granted
`SELECT ON ALL` goes blind on every refresh. MEASURED 2026-09-03 in `TEST_DG1_GEP`: of the 34
`WAREHOUSE` objects `R3_CARTOGRAPHY_RO` could see, **zero were created after its grant date**, and it
held **no** grant on `SALES_FCT_ORDERLINE` — only on that object's two rollback copies. The
dashboard's warehouse mode returned HTTP 500 as a result.

⭐ **The load-bearing half is the FUTURE grant, not the ALL grant.** `ON ALL` is point-in-time and
will decay again on the next refresh; a **schema-level** future grant survives `CREATE OR REPLACE`
and takes precedence over the database-level future grant that proved inert here. Running only the
`ALL` half buys one render check and re-earns the same incident.

Three modes, the mutating one separated so it cannot happen by accident::

    --plan     (default)  print the GRANTs and their REVOKEs. Connects to nothing, reads no secret.
    --apply               as ACCOUNTADMIN: prove the target exists, write the rollback file, GRANT.
    --verify              as the READER: prove the object is now selectable. No admin, no mutation.

⚠ `--apply` writes to the account. It refuses unless the target object is first observed to exist,
because a grant on an absent object succeeds silently and would leave a false fix in place — the
absence would then be discovered at the next render instead of now.

Secret discipline: both identities' credentials are fetched in-process by
`snowflake_bootstrap_r3._connect` (which also logs the use and branches on key-pair vs password) and
are never printed, logged, or placed in argv or the environment.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parents[1]

DATABASE = "TEST_DG1_GEP"
SCHEMA = "WAREHOUSE"
READER_ROLE = "R3_CARTOGRAPHY_RO"

#: The object whose absence produced the 500. Proven to exist before any grant is issued.
CANARY = "SALES_FCT_ORDERLINE"

ROLLBACK = REPO / "docs" / "evidence" / "marketing-model-v1" / "rollback-reader-grants.sql"

spec = importlib.util.spec_from_file_location(
    "r3boot", REPO / "scripts" / "snowflake_bootstrap_r3.py")
r3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r3)


def grants() -> list[str]:
    """Enumerated rather than looped, so the whole surface is auditable in one screen.
    SELECT only — no DML, no DDL, no ownership, no grant option."""
    q = f"{DATABASE}.{SCHEMA}"
    return [
        f"GRANT SELECT ON ALL TABLES IN SCHEMA {q} TO ROLE {READER_ROLE}",
        f"GRANT SELECT ON ALL VIEWS IN SCHEMA {q} TO ROLE {READER_ROLE}",
        f"GRANT SELECT ON FUTURE TABLES IN SCHEMA {q} TO ROLE {READER_ROLE}",
        f"GRANT SELECT ON FUTURE VIEWS IN SCHEMA {q} TO ROLE {READER_ROLE}",
    ]


def revokes() -> list[str]:
    """The rollback. FUTURE grants are revoked first — leaving them behind would keep re-granting
    after the ALL grants were removed, which is a rollback that does not roll back."""
    q = f"{DATABASE}.{SCHEMA}"
    return [
        f"REVOKE SELECT ON FUTURE VIEWS IN SCHEMA {q} FROM ROLE {READER_ROLE}",
        f"REVOKE SELECT ON FUTURE TABLES IN SCHEMA {q} FROM ROLE {READER_ROLE}",
        f"REVOKE SELECT ON ALL VIEWS IN SCHEMA {q} FROM ROLE {READER_ROLE}",
        f"REVOKE SELECT ON ALL TABLES IN SCHEMA {q} FROM ROLE {READER_ROLE}",
    ]


def cmd_plan(_args) -> int:
    print(f"target    {DATABASE}.{SCHEMA}   (TEST, not PROD)")
    print(f"reader    {READER_ROLE}")
    print(f"as        {r3.ADMIN_USER} / ACCOUNTADMIN via azure-kv:{r3.VAULT}/{r3.ADMIN_SECRET}")
    print(f"canary    {CANARY}  — --apply refuses if this is not observed to exist\n")
    for s in grants():
        print(f"  {s};")
    print("\nrollback:")
    for s in revokes():
        print(f"  {s};")
    print("\nnothing was connected to and no secret was read. This is a plan.")
    return 0


def cmd_apply(_args) -> int:
    conn = r3._connect(r3.ADMIN_USER, r3.ADMIN_SECRET, role="ACCOUNTADMIN", warehouse="COMPUTE_WH",
                       purpose=f"restore + future-proof {READER_ROLE} SELECT on {DATABASE}.{SCHEMA}")
    try:
        cur = conn.cursor()
        cur.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 300")

        # ⭐ THE DECISIVE READING, finally available. A reader role cannot distinguish absent from
        # invisible; ACCOUNTADMIN can. Do this BEFORE mutating: a grant on a missing object
        # succeeds silently and would ship a fix that fixes nothing.
        found = []
        for kind in ("VIEWS", "TABLES"):
            cur.execute(f"SHOW {kind} LIKE '{CANARY}' IN SCHEMA {DATABASE}.{SCHEMA}")
            found += [(kind[:-1], r[1]) for r in cur.fetchall()]
        print(f"as ACCOUNTADMIN, {DATABASE}.{SCHEMA}.{CANARY} ->"
              f" {found if found else 'NOT FOUND'}")
        if not found:
            raise SystemExit(
                f"⛔ STOP. {CANARY} does not exist in {DATABASE}.{SCHEMA} even to ACCOUNTADMIN. "
                "The diagnosis was wrong: this is an absent object, not an under-granted role, and "
                "granting SELECT would succeed while changing nothing. Do not run --apply again "
                "until the object is restored.")

        ROLLBACK.parent.mkdir(parents=True, exist_ok=True)
        ROLLBACK.write_text(
            f"-- Rollback for scripts/grant_reader_refresh.py --apply\n"
            f"-- Written {datetime.now(timezone.utc).isoformat()} BEFORE the grants were issued.\n"
            f"-- Run as ACCOUNTADMIN. Revokes FUTURE first; see the module docstring for why.\n"
            f"USE ROLE ACCOUNTADMIN;\n" + "".join(f"{s};\n" for s in revokes()),
            encoding="utf-8")
        print(f"rollback captured -> {ROLLBACK.relative_to(REPO)}")

        for s in grants():
            cur.execute(s)
            print(f"  ok  {s}")
    finally:
        conn.close()
    print("\nnow run --verify. The grant is not the evidence; the reader's SELECT is.")
    return 0


def cmd_verify(_args) -> int:
    """Validate at the layer that failed: the reader role, on the object that 500'd."""
    conn = r3._connect(r3.RO_USER, r3.RO_SECRET, role=r3.RO_ROLE, warehouse="COMPUTE_WH",
                       purpose=f"verify {READER_ROLE} can now select {CANARY}")
    try:
        cur = conn.cursor()
        cur.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 300")
        fq = f"{DATABASE}.{SCHEMA}.{CANARY}"
        cur.execute(f"SELECT 1 FROM {fq} LIMIT 1")
        got = cur.fetchone()
        print(f"  {fq}  -> {'READABLE' if got else 'READABLE but returned no row'}")

        cur.execute(f"SHOW GRANTS TO ROLE {r3.RO_ROLE}")
        n = sum(1 for row in cur.fetchall() if f".{SCHEMA}." in str(row[3]))
        print(f"  grants held on {DATABASE}.{SCHEMA}: {n}   (was 34 before the fix)")
    finally:
        conn.close()
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group()
    g.add_argument("--plan", action="store_true")
    g.add_argument("--apply", action="store_true")
    g.add_argument("--verify", action="store_true")
    a = p.parse_args()
    if a.apply:
        return cmd_apply(a)
    if a.verify:
        return cmd_verify(a)
    return cmd_plan(a)


if __name__ == "__main__":
    sys.exit(main())
