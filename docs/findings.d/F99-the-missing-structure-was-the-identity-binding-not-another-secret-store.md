### F99 — a credential pairing was carried in a handoff, had never once been used, and was wrong in both halves

Filed 2026-09-01 by the Mission Commander session, from the R3 access work. **DESIGN — recorded,
deliberately not implemented.** The blocker it describes is already removed; this is the durable
rule, not a project.

## What happened

The mission checkpoint named R3's credential as:

```
user      TEST_DG1_CORE_ADMIN
password  azure-kv:aldc-vault-test/snowflake-admin-nonprod
```

It had been "confirmed" by retrieving the secret and observing it was *a bare password, not JSON* —
its **shape**. No login was ever attempted. Both halves were wrong:

```
250001 (08001): Incorrect username or password was specified.
```

`wiki/tickets/gep/GP-281.md:44` records that secret as **`PAULRUSSELLADMIN`'s**, and
`…/phase-0-prefect-foundation.md:171` says **`TEST_DG1_CORE_ADMIN` holds `USAGE` only — "Do NOT
use."** So the named identity could not have run the DDL even with the right password. The correct
pairing existed only in the prose of a ticket note.

⭐ **The fact that was missing is not secret.** "Which user does this secret authenticate, against
which account, in which role, for what scope" contains nothing confidential — and it was the only
thing standing between a working credential and two hours of recovery.

## The distinction worth keeping

```
SECRET MATERIAL                              -> Key Vault only
  the password or private key

IDENTITY BINDING                             -> committed, non-secret configuration
  account / user / role / auth method / intended scope

VERIFICATION                                 -> a recorded measurement
  whether that binding has actually worked, when, and against what
```

The wiki vault holds all three in one plaintext file, which is why it cannot be read safely, cannot
be diffed, and drifts — it had no entry for the identity created that same day. Key Vault holds
only the first, which is why a markdown file was still needed. **Neither store is missing; the
binding between them is.**

## The rule, which is the point of this finding

> **`verified_at` is evidence of an actual successful verification, not a declarative claim. An
> identity with no valid verification evidence is `UNVERIFIED`.**

⛔ **Do not silently equate `configured`, `plausible`, `shape-compatible` or `documented` with
`verified`.** This finding exists because `shape-compatible` was recorded as good enough, and it
is the same defect as a gate passing over an absence — the instrument ran, returned something, and
nobody asked whether it could have returned a failure.

## Likely future shape — NOT built, and not to be built during D1–D5

```
non-secret identity manifest
        ↓
single credential resolver          (returns a connection, never a value; logs the use itself)
        ↓
Key Vault secret / key retrieval
        ↓
scope verification                  (assert the role holds ONLY what the manifest declares)
        ↓
measured verification stamp
```

Also worth preserving: **machine identities should prefer key-pair authentication where supported.**
Password auth for `R3_CARTOGRAPHY` was refused account-wide — *"Multi-factor authentication is
required for this account"* — which a service identity cannot satisfy and should not try to. Key
pairs are MFA-exempt, and rotation becomes unattended (`SET RSA_PUBLIC_KEY_2` → verify → unset the
old). This is a preference to apply to new identities, **not a migration project**.

⛔ **Explicitly out of scope**: another secrets manager, encrypted credential markdown, secrets
duplicated into git in any form, and a sweeping migration of the 20+ scripts across `clients/` that
call `snowflake.connector.connect` directly. That belongs in a later bounded infrastructure mission.

- **BELIEVED** — the credential problem is a storage problem, so the fix is a better or safer
  secret store; and a credential documented in the vault is a credential you can use.

- **ACTUALLY** — both stores were adequate. What did not exist anywhere machine-readable was the
  *binding* — and no artefact recorded whether the binding had ever authenticated, so a pairing
  that had never worked propagated through a checkpoint into a mission brief as settled fact.

- **MEASURED BY** — attempting the login named in the checkpoint and reading the error
  (`250001 (08001)`), then recovering the true pairing from two non-vault wiki sources and
  connecting successfully. The discriminating step is the one that had never been run: **a login.**
  Reproduce with `python scripts/snowflake_bootstrap_r3.py --discover`, whose whole purpose is to
  confirm names against the account rather than against a document.

- **AFFECTS** — **every lane** that touches a credential, and the 20+ direct
  `snowflake.connector.connect` callers under `clients/`. Immediately:
  `scripts/snowflake_bootstrap_r3.py` (which now carries the corrected pairing and its citations in
  a comment), `scripts/credential_use.py`, `wiki/vault/infra-credentials.md` (stale — no entry for
  `R3_CARTOGRAPHY` / `snowflake-r3-cartography-nonprod`, and no row format for a key-pair identity
  with no password), and `docs/specs/marketing-model-reconstruction-v1.md` §2.1.

- **KIND** — DESIGN

- **CHANGES** — a committed non-secret identity manifest, plus one resolver that is the only code
  path to a credential and that refuses any identity whose `verified_at` is absent or stale. Lands
  as `factory/credentials.py` + `credentials/identities.yaml` + a `verify` CLI. ⛔ **Deferred by
  commander decision 2026-09-01: not to be built before D5.** R3 already removed the blocker this
  would have unblocked, so building it now would be infrastructure ahead of delivery.

- **STATUS** — OPEN
