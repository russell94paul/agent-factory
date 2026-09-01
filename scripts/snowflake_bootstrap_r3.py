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
import secrets
import shutil
import string
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# --- the target, from mission-wave1-checkpoint-2026-09-01.md §3 (Paul's directive: TEST, not PROD)
ACCOUNT = "og35375.canada-central.azure"
DATABASE = "TEST_DG1_GEP"
# ⚠ The checkpoint named TEST_DG1_CORE_ADMIN here. It was wrong on both counts and the pairing had
# never been exercised — it was confirmed by the secret's *shape*, not by a login. Measured
# 2026-09-01: connecting as TEST_DG1_CORE_ADMIN with this secret returns
# `250001 (08001) Incorrect username or password`. Two non-vault wiki sources say why:
#   wiki/tickets/gep/GP-281.md:44  — "TEST og35375 PAULRUSSELLADMIN (vault KV
#                                     aldc-vault-test/snowflake-admin-nonprod)"  <- whose password
#   wiki/processes/distributed-workflow/active/navira/active/phase-0-prefect-foundation.md:171
#                                   — "TEST_DG1_CORE_ADMIN | Only has USAGE role ... Do NOT use."
# So the secret belongs to PAULRUSSELLADMIN, and the named user could not have run this DDL anyway.
ADMIN_USER = "PAULRUSSELLADMIN"
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

def _az() -> str:
    """`az` on Windows is a .cmd shim, which CreateProcess will not run from a bare argv[0].
    Resolve it once rather than shelling out through a shell (which would put the secret-bearing
    command line through a command interpreter)."""
    found = shutil.which("az") or shutil.which("az.cmd")
    if not found:
        raise SystemExit("az CLI not found on PATH")
    return found


def _kv_get(name: str) -> str:
    """Fetch a secret value. The return value is passed straight into a connection and dropped.
    It is never printed and never stored beyond the call that uses it."""
    out = subprocess.run(
        [_az(), "keyvault", "secret", "show", "--vault-name", VAULT, "--name", name,
         "--query", "value", "-o", "tsv"],
        capture_output=True, text=True, check=True,
    )
    value = out.stdout.strip()
    if not value:
        raise SystemExit(f"secret {name!r} in {VAULT} is empty")
    return value


def _kv_set(name: str, value: str) -> None:
    """Write a secret without it appearing in argv, where any process lister on the box would see
    it. `--file` is the only argv-free route the CLI offers, so the value goes through a
    private temp file that is deleted in a finally."""
    tmp = Path(tempfile.mkdtemp()) / "v"
    try:
        tmp.write_text(value, encoding="utf-8")
        subprocess.run(
            [_az(), "keyvault", "secret", "set", "--vault-name", VAULT, "--name", name,
             "--file", str(tmp), "-o", "none"],
            check=True,
        )
    finally:
        if tmp.exists():
            tmp.write_text("0" * len(value), encoding="utf-8")
            tmp.unlink()
        tmp.parent.rmdir()


def _log_use(secret: str, access: str, purpose: str) -> None:
    subprocess.run(
        [sys.executable, str(REPO / "scripts" / "credential_use.py"),
         "--secret", secret, "--source", f"azure-kv:{VAULT}",
         "--task", "R3", "--access", access, "--purpose", purpose],
        check=True, cwd=REPO,
    )


def _connect(user: str, secret_name: str, role: str | None, warehouse: str | None,
             purpose: str = ""):
    """The credential-use record is written *after* the retrieval succeeds and before the
    connection is attempted.

    ⚠ It used to be written first, which meant a run that died resolving the `az` shim left a row
    claiming a use that never happened. A log that over-reports is a log nobody can reconcile —
    the same class of defect as a gate that passes over an absence."""
    import snowflake.connector

    credential = _kv_get(secret_name)
    if purpose:
        _log_use(secret_name, "READ", purpose)

    kwargs = dict(account=ACCOUNT, user=user, database=DATABASE, client_session_keep_alive=False)
    if "-----BEGIN" in credential:
        # A PEM private key, not a password — the service identity's only credential. Deserialised
        # to DER in memory and handed to the driver; the PEM text is not retained.
        from cryptography.hazmat.primitives import serialization
        kwargs["private_key"] = serialization.load_pem_private_key(
            credential.encode(), password=None
        ).private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    else:
        kwargs["password"] = credential
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


def cmd_discover(args) -> int:
    """Read-only. Confirm the warehouse and database NAMES against the account itself before
    --apply hard-codes either into a grant.

    `COMPUTE_WH` is grounded in `wiki/processes/deployment/environment-setup.md`, which names it in
    the same env block as this exact account — but a name read from a doc is a hypothesis, and
    granting USAGE on a warehouse that does not exist fails late and confusingly. This asks the
    target."""
    conn = _connect(ADMIN_USER, ADMIN_SECRET, role=None, warehouse=None,
                    purpose="R3 grounding: confirm warehouse/database names before --apply")
    try:
        cur = conn.cursor()
        cur.execute("SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()")
        print("identity  {} / {} / {}".format(*cur.fetchone()))
        cur.execute("SHOW WAREHOUSES")
        whs = [(r[0], r[1], r[3]) for r in cur.fetchall()]  # name, state, size
        print(f"\nwarehouses ({len(whs)}):")
        for name, state, size in whs:
            print(f"  {name:<28} {state:<12} {size}")
        cur.execute("SHOW DATABASES")
        dbs = [r[1] for r in cur.fetchall()]
        print(f"\ndatabases ({len(dbs)}): {len(dbs)} total")
        print(f"{DATABASE} present: {DATABASE in dbs}")

        # CURRENT_ROLE() is PUBLIC by default, which cannot CREATE ROLE. Enumerate what this user
        # can actually assume rather than assuming ACCOUNTADMIN is reachable.
        # ⚠ Read these by COLUMN NAME. Indexing SHOW output by position is how you end up printing
        # privileges under a heading that says roles — which this function did on its first run.
        cur.execute(f"SHOW GRANTS TO USER {ADMIN_USER}")
        cols = [d[0].lower() for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        print(f"\nSHOW GRANTS TO USER columns: {cols}")
        key = "role" if "role" in cols else cols[1]
        print(f"roles held by {ADMIN_USER}: {', '.join(sorted({str(r[key]) for r in rows})) or '(none)'}")
    finally:
        conn.close()
    return 0


def cmd_apply(args) -> int:
    if not args.warehouse:
        raise SystemExit("--apply requires --warehouse (the role needs USAGE on exactly one)")

    alphabet = string.ascii_letters + string.digits
    new_password = "".join(secrets.choice(alphabet) for _ in range(40))

    # PAULRUSSELLADMIN's default role is PUBLIC, which cannot CREATE ROLE. Measured 2026-09-01:
    # SHOW GRANTS TO USER reports ACCOUNTADMIN, so ask for it explicitly rather than inheriting.
    conn = _connect(ADMIN_USER, ADMIN_SECRET, role="ACCOUNTADMIN", warehouse=args.warehouse,
                    purpose=f"R3 bootstrap: create {RO_ROLE}/{RO_USER} in {DATABASE}")
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


def cmd_rekey(args) -> int:
    """Move the read-only user from password auth to an RSA key pair.

    ⚠ Why this mode exists. `--apply` set a password, and the login was refused:
    `250001 (08001) Multi-factor authentication is required for this account. Log in to Snowsight
    to enroll.` The account enforces MFA on password auth, which a service identity cannot satisfy
    and should not try to — enrolling a human second factor for an unattended reader would be the
    wrong fix. Key-pair auth is Snowflake's supported service-account mechanism, is exempt from the
    MFA policy, and is strictly better than the password it replaces.

    The password is UNSET afterwards, so the identity has exactly one usable credential."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    # Snowflake wants the base64 body only — no PEM header, footer or newlines.
    public_body = "".join(l for l in public_pem.splitlines() if "-----" not in l)

    conn = _connect(ADMIN_USER, ADMIN_SECRET, role="ACCOUNTADMIN", warehouse=args.warehouse,
                    purpose=f"R3 bootstrap: set RSA public key on {RO_USER} (MFA blocks passwords)")
    try:
        cur = conn.cursor()
        cur.execute(f"ALTER USER {RO_USER} SET RSA_PUBLIC_KEY = '{public_body}'")
        print(f"ok  ALTER USER {RO_USER} SET RSA_PUBLIC_KEY = <not printed>")
        cur.execute(f"ALTER USER {RO_USER} UNSET PASSWORD")
        print(f"ok  ALTER USER {RO_USER} UNSET PASSWORD")
    finally:
        conn.close()

    _kv_set(RO_SECRET, private_pem)
    _log_use(RO_SECRET, "WRITE", f"R3 bootstrap: replaced {RO_USER} password with an RSA private key")
    print(f"\nprivate key -> azure-kv:{VAULT}/{RO_SECRET} (replaces the password; never printed)")
    return 0


def cmd_verify(args) -> int:
    """The measurement. Read-only is not proved by the grant list alone — the write has to be
    watched being refused."""
    if not args.warehouse:
        raise SystemExit("--verify requires --warehouse")

    conn = _connect(RO_USER, RO_SECRET, role=RO_ROLE, warehouse=args.warehouse,
                    purpose="R3 pre-flight: prove the cartography role cannot mutate")
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


CARTOGRAPHY = REPO / "docs" / "evidence" / "marketing-model-v1" / "R3-cartography.md"

# Navira is the modelled entity; GEP is the Jira project. Searching for "GEP" finds the wrong
# things — checkpoint §"The subject is Navira, not GEP".
#
# ⚠ The first run of this used a broad term list (SALES, PRODUCT, GOOGLE, AMAZON...) and matched
# 872 of 1271 objects — 69%, which discriminates nothing, and swept WAREHOUSE_TEST_PAUL and
# WAREHOUSE_ROLLBACK_GP254 into a document describing the client's estate. The subject is the
# MARKETING_* family; everything else is context for it.
SUBJECT_PREFIX = "MARKETING_"

# Authoritative vs scratch. A schema named for a ticket, a person or a rollback is somebody's
# working copy — it may hold the newest code, and it is still not the source of truth.
AUTHORITATIVE = ("WAREHOUSE", "WAREHOUSE_SOURCE", "REPORT_COMMON", "DATA_SHARE",
                 "AMAZON", "AMAZON_ADS", "AMAZON_LECTRIC", "GOOGLE_ADS", "META",
                 "SELLERCLOUD", "SELLERCLOUD_SQL", "SUPPLEMENT", "OPS", "DASHBOARD",
                 "DASHBOARD_SOURCE", "PUBLIC")


def _is_scratch(schema: str) -> bool:
    return schema.upper() not in AUTHORITATIVE


def cmd_cartograph(args) -> int:
    """R3 proper. What actually exists, at what grain, with what keys — read-only.

    Two conditions from the checkpoint are honoured in the output rather than assumed away:
    TEST's marketing-data currency is unverified (a re-land was planned, not executed, and Lectric
    confirmed "greenfield in TEST (no objects)"), so every object is reported with its row count
    and every empty one is labelled — an absent row set is NOT-POPULATED, never a zero. And
    WAREHOUSE_TEST_GP226 is a clone: it is INVENTORIED so the authoritative-vs-clone delta can be
    measured, but the role was not widened to it and no claim rests on its contents."""
    if not args.warehouse:
        raise SystemExit("--cartograph requires --warehouse")

    conn = _connect(RO_USER, RO_SECRET, role=RO_ROLE, warehouse=args.warehouse,
                    purpose="R3: read-only cartography of TEST_DG1_GEP")
    try:
        cur = conn.cursor()
        cur.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 300")

        def rows(sql):
            cur.execute(sql)
            cols = [d[0].lower() for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]

        schemas = rows(
            "SELECT SCHEMA_NAME, LAST_ALTERED FROM TEST_DG1_GEP.INFORMATION_SCHEMA.SCHEMATA"
            " ORDER BY SCHEMA_NAME")
        objects = rows(
            "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE, ROW_COUNT, LAST_ALTERED"
            " FROM TEST_DG1_GEP.INFORMATION_SCHEMA.TABLES ORDER BY TABLE_SCHEMA, TABLE_NAME")
        cols = rows(
            "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE, ORDINAL_POSITION"
            " FROM TEST_DG1_GEP.INFORMATION_SCHEMA.COLUMNS"
            " WHERE STARTSWITH(TABLE_NAME, 'MARKETING_')"
            " ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION")

        by_obj = {}
        for c in cols:
            by_obj.setdefault((c["table_schema"], c["table_name"]), []).append(c)

        CARTOGRAPHY.parent.mkdir(parents=True, exist_ok=True)
        CARTOGRAPHY.write_text(
            _cartography_md(schemas, objects, by_obj, args.warehouse), encoding="utf-8")
    finally:
        conn.close()

    fam = [o for o in objects if o["table_name"].upper().startswith(SUBJECT_PREFIX)]
    print(f"schemas {len(schemas)}  objects {len(objects)}  MARKETING_* {len(fam)}")
    print(f"evidence -> {CARTOGRAPHY.relative_to(REPO)}")
    return 0


def _cartography_md(schemas, objects, by_obj, warehouse) -> str:
    when = datetime.now(timezone.utc).isoformat()
    fam = [o for o in objects if o["table_name"].upper().startswith(SUBJECT_PREFIX)]
    auth = [o for o in fam if not _is_scratch(o["table_schema"])]
    scratch = [o for o in fam if _is_scratch(o["table_schema"])]

    auth_names = {o["table_name"].upper() for o in auth}
    clone = [o for o in scratch if o["table_schema"].upper().startswith("WAREHOUSE_TEST_GP226")]
    clone_only = sorted({o["table_name"].upper() for o in clone} - auth_names)

    by_schema = {}
    for o in fam:
        by_schema.setdefault(o["table_schema"], []).append(o)

    nl = "\n"

    def table(objs):
        if not objs:
            return "_none_" + nl
        out = ["| schema | object | type | rows | last altered |", "|---|---|---|---:|---|"]
        for o in sorted(objs, key=lambda x: (x["table_schema"], x["table_name"])):
            rc = o["row_count"]
            shown = "NOT-REPORTED (view)" if o["table_type"] == "VIEW" else (
                f"{rc:,}" if rc else "NOT-POPULATED")
            out.append(f"| `{o['table_schema']}` | `{o['table_name']}` | {o['table_type']} | "
                       f"{shown} | {str(o['last_altered'])[:19]} |")
        return nl.join(out) + nl

    grain = []
    for o in sorted(auth, key=lambda x: x["table_name"]):
        cs = by_obj.get((o["table_schema"], o["table_name"]), [])
        keyish = [c["column_name"] for c in cs
                  if c["column_name"].upper().endswith(("_ID", "_KEY", "_CODE", "_DATE",
                                                        "_MONTH", "_SKU", "_ASIN"))]
        grain.append(f"- **`{o['table_schema']}.{o['table_name']}`** — {len(cs)} columns. "
                     f"Key-shaped by name: "
                     f"{', '.join('`' + k + '`' for k in keyish[:8]) or '_none_'}")

    clone_only_md = nl.join("- `" + n + "`" for n in clone_only) or (
        "_none — every clone object has an authoritative counterpart_")
    grain_md = nl.join(grain) or "_no authoritative MARKETING_* objects_"
    schema_rows = nl.join(
        f"| `{s['schema_name']}` | "
        f"{'scratch' if _is_scratch(s['schema_name']) else '**authoritative**'} | "
        f"{len(by_schema.get(s['schema_name'], []))} | {str(s['last_altered'])[:19]} |"
        for s in schemas)

    return f"""# R3 — source cartography of `TEST_DG1_GEP`

**Measured {when}** as `R3_CARTOGRAPHY` / `R3_CARTOGRAPHY_RO`, warehouse `{warehouse}`.
`evidence_class` **TARGET** · basis **MEASURED**.
Read-only proof: [`R3-preflight-readonly-proof.md`](R3-preflight-readonly-proof.md).

R3 answers one question — **what actually exists?** It does not design, and it does not resolve
the contradictions it finds.

## ⚠ Basis discipline

`ROW_COUNT` comes from `INFORMATION_SCHEMA.TABLES`. It is **MEASURED** for base tables and
**NOT-REPORTED** for views, which carry none — a view showing no count is not an empty view.
`NOT-POPULATED` means a base table's count is zero or absent. **None of these is a statement about
what the client has**: a Navira re-land into TEST was *planned and not executed*, and Lectric
confirmed *"greenfield in TEST (no objects)"* for the agency slice.

⭐ **Structure in TEST is trustworthy. Row-level distribution is not.** No grain claim below is
promoted on the strength of a TEST row count, and every key is identified **by naming convention
only** — a column called `CAMPAIGN_ID` is a hypothesis about the grain, not a measurement of it.
Proving uniqueness is D3's job and it has not been done here.

## Scale

```
schemas                                    {len(schemas)}
objects (base tables + views)              {len(objects)}
MARKETING_* family                         {len(fam)}
  in authoritative schemas                 {len(auth)}
  in scratch / ticket / rollback schemas   {len(scratch)}
```

## ⛔ The headline finding — {len(clone_only)} marketing objects exist ONLY in a clone

`WAREHOUSE_TEST_GP226` is a **clone**. It holds **{len(clone)}** `MARKETING_*` objects against
**{len(auth)}** across every authoritative schema combined — comparable in size, so the clone is
not simply a stale copy — and **{len(clone_only)}** of its objects have **no counterpart under any
authoritative name**:

{clone_only_md}

This is recorded as a **LINEAGE CONTRADICTION / SOURCE-OF-TRUTH ISSUE**, exactly as the mission
brief requires, and **not** as evidence that the clone is authoritative. R2 independently found
~10 marketing objects still reading from it and its `MARKETING_EFFICIENCY` copy *"MISSES Amazon US
Sponsored Display ($3,374.90)"* — a clone simultaneously ahead in surface area and behind in data.
R3's role was **not** widened to it; the inventory above comes from `INFORMATION_SCHEMA`, which
lists names without any grant on the objects themselves.

**D1 must not treat any clone-only object as an existing capability.**

## The authoritative marketing family

{table(auth)}

## The same family in scratch, ticket and rollback schemas

⭐ Listed so nobody mistakes one for the estate. `WAREHOUSE_TEST_PAUL`, `WAREHOUSE_TEST_STEVEN`,
`WAREHOUSE_TEST_BRAYDEN` and `WAREHOUSE_ROLLBACK_GP254` are working copies — an earlier draft of
this document had them in the main inventory, which is the same defect as shipping a client a CSV
listing our own engineers' debugging folders.

{table(scratch)}

## Candidate grains in the authoritative family — by name, not yet by proof

{grain_md}

## Every schema, classified

| schema | class | MARKETING_* | last altered |
|---|---|---:|---|
{schema_rows}
"""


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
    mode.add_argument("--discover", action="store_true",
                      help="read-only: list warehouses/databases to ground the names")
    mode.add_argument("--rekey", action="store_true",
                      help="swap the read-only user to RSA key-pair auth (MFA blocks passwords)")
    mode.add_argument("--cartograph", action="store_true",
                      help="R3 proper: read-only cartography of the authoritative schema")
    ap.add_argument("--warehouse", help="warehouse the role gets USAGE on")
    args = ap.parse_args()

    if args.discover:
        return cmd_discover(args)
    if args.rekey:
        return cmd_rekey(args)
    if args.cartograph:
        return cmd_cartograph(args)
    if args.apply:
        return cmd_apply(args)
    if args.verify:
        return cmd_verify(args)
    return cmd_plan(args)


if __name__ == "__main__":
    raise SystemExit(main())
