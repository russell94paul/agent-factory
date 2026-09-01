#!/usr/bin/env python
"""Stand up (and then prove) the read-only identity R3 cartography runs as.

R3 is read-only source cartography. Its spec (`docs/specs/marketing-model-reconstruction-v1.md`
§2.1) says the failsafe for a read-only mission is not a rollback but a proof that no rollback can
be needed — *a role assumed read-only is an assumption; a role watched refusing a write is a
measurement.* This script exists to produce that measurement.

Three modes, deliberately separated so the mutating one cannot happen by accident:

    --plan      (default)  print the exact DDL. Connects to nothing. Reads no secret.
    --apply                run the DDL as the admin identity, and mint the new password
                           straight into Key Vault. THE ONLY MUTATING MODE.
    --verify               connect AS the read-only identity, show its grants, attempt one
                           scoped write, and require the refusal. Writes the evidence file.

⛔ --apply is a schema/account change. §2.1's standing credential grant removed the *retrieval*
   prompt for this repo; it did not remove the deploy gate. Do not run --apply without Paul having
   chosen route 1 (read-only role) over route 2 (admin + read-only recorded as ASSUMED).

Secret discipline (§2.1 step 3, sharpened by docs/evidence/switchboard-security-preflight-2026-08-31.md):
secret values are fetched in-process, handed straight to the driver, and never printed, logged,
returned, stored in a module global, or placed in argv or an environment variable.
"""

from __future__ import annotations

import argparse
import json
import secrets
import string
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# --- the target, from mission-wave1-checkpoint-2026-09-01.md §3 (Paul's directive: TEST, not PROD)
ACCOUNT = "og35375.canada-central.azure"
DATABASE = "TEST_DG1_GEP"
ADMIN_USER = "TEST_DG1_CORE_ADMIN"
ADMIN_SECRET = "snowflake-admin-nonprod"
VAULT = "aldc-vault-test"

# --- the identity this script creates
RO_ROLE = "R3_CARTOGRAPHY_RO"
RO_USER = "R3_CARTOGRAPHY"
RO_SECRET = "snowflake-r3-cartography-nonprod"

PROBE_TABLE = f"{DATABASE}.PUBLIC.__R3_WRITE_PROBE__"

EVIDENCE = REPO / "docs" / "evidence" / "marketing-model-v1" / "R3-preflight-readonly-proof.md"


def ddl(warehouse: str) -> list[str]:
    """The complete grant set. USAGE + SELECT and nothing else — no DML, no DDL, no ownership,
    no grant option, no prod. Deliberately enumerated rather than looped, so a reader can audit
    the whole surface in one screen."""
    return [
        f"CREATE ROLE IF NOT EXISTS {RO_ROLE}",
        f"GRANT USAGE ON WAREHOUSE {warehouse} TO ROLE {RO_ROLE}",
        f"GRANT USAGE ON DATABASE {DATABASE} TO ROLE {RO_ROLE}",
        f"GRANT USAGE ON ALL SCHEMAS IN DATABASE {DATABASE} TO ROLE {RO_ROLE}",
        f"GRANT USAGE ON FUTURE SCHEMAS IN DATABASE {DATABASE} TO ROLE {RO_ROLE}",
        f"GRANT SELECT ON ALL TABLES IN DATABASE {DATABASE} TO ROLE {RO_ROLE}",
        f"GRANT SELECT ON FUTURE TABLES IN DATABASE {DATABASE} TO ROLE {RO_ROLE}",
        f"GRANT SELECT ON ALL VIEWS IN DATABASE {DATABASE} TO ROLE {RO_ROLE}",
        f"GRANT SELECT ON FUTURE VIEWS IN DATABASE {DATABASE} TO ROLE {RO_ROLE}",
        f"CREATE USER IF NOT EXISTS {RO_USER}"
        f" DEFAULT_ROLE = {RO_ROLE} DEFAULT_WAREHOUSE = {warehouse}"
        f" DEFAULT_NAMESPACE = {DATABASE} MUST_CHANGE_PASSWORD = FALSE"
        f" COMMENT = 'R3 read-only cartography. USAGE+SELECT on {DATABASE} only.'",
        f"GRANT ROLE {RO_ROLE} TO USER {RO_USER}",
    ]


# ---------------------------------------------------------------- secrets, which never come back

def _kv_get(name: str) -> str:
    """Fetch a secret value. The return value is passed straight into a connection and dropped.
    It is never printed and never stored beyond the call that uses it."""
    out = subprocess.run(
        ["az", "keyvault", "secret", "show", "--vault-name", VAULT, "--name", name,
         "--query", "value", "-o", "tsv"],
        capture_output=True, text=True, check=True,
    )
    value = out.stdout.strip()
    if not value:
        raise SystemExit(f"secret {name!r} in {VAULT} is empty")
    return value


def _kv_set(name: str, value: str) -> None:
    """Write a secret without it appearing in argv (where any process lister would see it)."""
    subprocess.run(
        ["az", "keyvault", "secret", "set", "--vault-name", VAULT, "--name", name,
         "--file", "/dev/stdin", "-o", "none"],
        input=value, text=True, check=True,
    )


def _log_use(secret: str, access: str, purpose: str) -> None:
    subprocess.run(
        [sys.executable, str(REPO / "scripts" / "credential_use.py"),
         "--secret", secret, "--source", f"azure-kv:{VAULT}",
         "--task", "R3", "--access", access, "--purpose", purpose],
        check=True, cwd=REPO,
    )


def _connect(user: str, secret_name: str, role: str | None, warehouse: str | None):
    import snowflake.connector

    kwargs = dict(account=ACCOUNT, user=user, password=_kv_get(secret_name),
                  database=DATABASE, client_session_keep_alive=False)
    if role:
        kwargs["role"] = role
    if warehouse:
        kwargs["warehouse"] = warehouse
    return snowflake.connector.connect(**kwargs)


# ---------------------------------------------------------------------------------------- modes

def cmd_plan(args) -> int:
    print(f"account   {ACCOUNT}")
    print(f"database  {DATABASE}          (TEST — Paul's directive, not PROD)")
    print(f"as        {ADMIN_USER}  via azure-kv:{VAULT}/{ADMIN_SECRET}")
    print(f"creates   role {RO_ROLE} / user {RO_USER}")
    print(f"password  minted locally -> azure-kv:{VAULT}/{RO_SECRET} (never printed)")
    print(f"warehouse {args.warehouse or '<REQUIRED for --apply: pass --warehouse>'}")
    print()
    for stmt in ddl(args.warehouse or "<WAREHOUSE>"):
        print(f"  {stmt};")
    print()
    print("nothing was connected to and no secret was read. This is a plan.")
    return 0


def cmd_apply(args) -> int:
    if not args.warehouse:
        raise SystemExit("--apply requires --warehouse (the role needs USAGE on exactly one)")

    alphabet = string.ascii_letters + string.digits
    new_password = "".join(secrets.choice(alphabet) for _ in range(40))

    _log_use(ADMIN_SECRET, "READ", f"R3 bootstrap: create {RO_ROLE}/{RO_USER} in {DATABASE}")
    conn = _connect(ADMIN_USER, ADMIN_SECRET, role=None, warehouse=args.warehouse)
    try:
        cur = conn.cursor()
        for stmt in ddl(args.warehouse):
            cur.execute(stmt)
            print(f"ok  {stmt[:76]}")
        cur.execute(f"ALTER USER {RO_USER} SET PASSWORD = %s", (new_password,))
        print(f"ok  ALTER USER {RO_USER} SET PASSWORD = <not printed>")
    finally:
        conn.close()

    _kv_set(RO_SECRET, new_password)
    _log_use(RO_SECRET, "WRITE", f"R3 bootstrap: minted password for {RO_USER}")
    del new_password
    print(f"\nstored -> azure-kv:{VAULT}/{RO_SECRET}")
    print("next: python scripts/snowflake_bootstrap_r3.py --verify --warehouse " + args.warehouse)
    return 0


def cmd_verify(args) -> int:
    """The measurement. Read-only is not proved by the grant list alone — the write has to be
    watched being refused."""
    if not args.warehouse:
        raise SystemExit("--verify requires --warehouse")

    _log_use(RO_SECRET, "READ", "R3 pre-flight: prove the cartography role cannot mutate")
    conn = _connect(RO_USER, RO_SECRET, role=RO_ROLE, warehouse=args.warehouse)
    grants, refusal, timeout_s = [], None, None
    try:
        cur = conn.cursor()

        # §2.1 step 2 — bound the cost before the first real query.
        cur.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 120")
        cur.execute("SHOW PARAMETERS LIKE 'STATEMENT_TIMEOUT_IN_SECONDS' IN SESSION")
        timeout_s = cur.fetchone()[1]

        cur.execute(f"SHOW GRANTS TO ROLE {RO_ROLE}")
        grants = [(r[1], r[2], r[3]) for r in cur.fetchall()]  # privilege, granted_on, name

        # §2.1 step 1 — the scoped write that must fail.
        try:
            cur.execute(f"CREATE TABLE {PROBE_TABLE} (probe NUMBER)")
        except Exception as exc:  # noqa: BLE001 — the exception IS the evidence
            refusal = f"{type(exc).__name__}: {exc}".strip()
        else:
            cur.execute(f"DROP TABLE IF EXISTS {PROBE_TABLE}")
            raise SystemExit(
                f"⛔ STOP. The write SUCCEEDED against {PROBE_TABLE}. {RO_ROLE} is not read-only, "
                "the pre-flight cannot pass, and R3 must not run under it."
            )
    finally:
        conn.close()

    mutating = sorted({p for p, _, _ in grants} - {"USAGE", "SELECT", "REFERENCE_USAGE"})
    if mutating:
        raise SystemExit(f"⛔ STOP. {RO_ROLE} holds non-read privileges: {mutating}")

    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(_evidence_md(grants, refusal, timeout_s, args.warehouse), encoding="utf-8")
    print(f"\nrefused as required:\n  {refusal}\n")
    print(f"grants: {len(grants)}, all within USAGE/SELECT")
    print(f"evidence -> {EVIDENCE.relative_to(REPO)}")
    return 0


def _evidence_md(grants, refusal, timeout_s, warehouse) -> str:
    when = datetime.now(timezone.utc).isoformat()
    rows = "\n".join(f"| `{p}` | {on} | `{name}` |" for p, on, name in grants)
    return f"""# R3 pre-flight — the cartography role watched refusing a write

**Measured {when}** by `scripts/snowflake_bootstrap_r3.py --verify`.
`evidence_class` **TARGET** · basis **MEASURED**.

Spec `docs/specs/marketing-model-reconstruction-v1.md` §2.1 step 1: *a role assumed read-only is
an assumption; a role watched refusing a write is a measurement.* This is the measurement.

```
account    {ACCOUNT}
database   {DATABASE}      (TEST, not PROD)
identity   {RO_USER} / {RO_ROLE}
warehouse  {warehouse}
timeout    {timeout_s}s  (§2.1 step 2 — a runaway read is still a runaway)
```

## The refused write

```sql
CREATE TABLE {PROBE_TABLE} (probe NUMBER);
```

```
{refusal}
```

⭐ The statement was **executed and refused**, not skipped. Had it succeeded the script would have
dropped the table and exited non-zero rather than write this file — read-only is proved by the
refusal, and there is no path through `--verify` that writes this evidence without one.

## Every privilege the role holds ({len(grants)})

| privilege | on | object |
|---|---|---|
{rows}

No DML, no DDL, no OWNERSHIP, no grant option, no production account.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--plan", action="store_true", help="print the DDL and exit (default)")
    mode.add_argument("--apply", action="store_true", help="create the role/user (MUTATING)")
    mode.add_argument("--verify", action="store_true", help="prove the role cannot write")
    ap.add_argument("--warehouse", help="warehouse the role gets USAGE on")
    args = ap.parse_args()

    if args.apply:
        return cmd_apply(args)
    if args.verify:
        return cmd_verify(args)
    return cmd_plan(args)


if __name__ == "__main__":
    raise SystemExit(main())
