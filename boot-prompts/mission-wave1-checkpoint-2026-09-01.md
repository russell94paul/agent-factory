# Checkpoint — Wave 1 blocked on a credential decision, and a credential I exposed

**Written 2026-09-01, mid-mission, at Paul's request.** Continues the
`marketing-model-reconstruction-v1` mission. Does not supersede
`first-real-dispatch-2026-08-31.md` — that thread is paused, not retired.

`next:` **Paul's decision on credential rotation, then Wave 1.** R1 and R2 are unblocked and can
start immediately; R3 waits.

---

## 0. State

`main @ 44bf6b8`, clean, nothing unpushed. Suite green as of the last full run.

⚠ **`agent-factory-de [372331]` was live and `busy`** during this session — another interactive
session with this repo as cwd. Not touched, not terminated. Re-check before assuming sole ownership.

## 1. ⛔ READ FIRST — three credentials were exposed into a session transcript

**By me, on 2026-08-31, extracting Snowflake account details from `wiki/vault/infra-credentials.md`.**

I filtered with a **deny-list** (drop lines containing "password"). The vault stores credentials in
**markdown tables**, so the word "password" is in the header row and never in the data rows. Three
plaintext values passed straight through:

| Account | Environment | Severity |
|---|---|---|
| `paulrussell` | ⛔ **the same password is listed for `og35375` non-prod AND `wj66376` PRODUCTION** | **highest — rotate first** |
| `TEST_DG1_CORE_ADMIN` | non-prod | rotate |
| `MIKESTUARTADMIN` | non-prod, recorded as issued **without MFA** | rotate |

**The values are not repeated here and must not be.** They are in the 2026-08-31 session
transcript. `docs/evidence/switchboard-security-preflight-2026-08-31.md` records that a session
manager indexes the first ~500 chars of the first ~16 messages into a searchable FTS table **and
that deletion does not stick** — this exposure was around message 90, so *probably* outside that
window. Probably is not verified.

⭐ **The rule that would have prevented it, stated so it is not re-learned:** when extracting from a
credential file, **allow-list the columns you want** (account, user), never deny-list the ones you
do not. A deny-list over free text is a guard only as wide as the relation it derives over — the
same defect fixed in `readiness.py` that same morning (F91), violated against a credential file
that afternoon. **Worth filing as a finding; not yet filed.**

## 2. The mission

`marketing-model-reconstruction-v1` — spec at `docs/specs/marketing-model-reconstruction-v1.md`,
record at `.data/missions/marketing-model-reconstruction-v1.json`.

```
R1 ──┐
R2 ──┼──▶ D1 ──▶ D2 ──▶ D3 ──▶ D4 ──▶ D5
R3 ──┘
```

**Wave 1 is `[R1, R2, R3]`** — all READ on disjoint scopes, so `claims.task_claim()` grants all
three. D1–D5 all write `res:mission-artifacts`, so the claim refuses a second writer — **that
refusal is the mission's negative control** (§5).

| | State | Why |
|---|---|---|
| **R1** stakeholder / client evidence | **UNBLOCKED** | no credential |
| **R2** repo + wiki diff | **UNBLOCKED** | no credential |
| **R3** Snowflake cartography | ⛔ **BLOCKED** | credential decision below |

⭐ **The subject is Navira, not "GEP".** GEP is the Jira project and the client; the modelled entity
is Navira (`wiki/entities/repos/navira-marketing-dashboard.md:18`, `MARKETING_DIM_AGENCY`). R2 and
R3 must search for **Navira**-named objects or they will look for the wrong things — spec §0.5.

## 3. ⭐ Paul's directive that changed the target: TEST, not PROD

Established 2026-08-31, and it supersedes the spec's implied target:

```
account   og35375.canada-central.azure
user      TEST_DG1_CORE_ADMIN              covers TEST_DG1_* and QA_DG1_*
database  TEST_DG1_GEP                     deployed from branch GEP/user-testing
password  azure-kv:aldc-vault-test/snowflake-admin-nonprod    (subshell only, never a variable)
```

`wiki/CLAUDE.md` §Environment Model: `GEP/user-testing → TEST_DG1_GEP`, `main → PROD_DG1_GEP`.
Deploys are manual; a code merge does not deploy.

**The credential retrieval IS logged** — `.data/credential-use.jsonl`, one row, R3, READ. It was
retrieved once to confirm its shape (a bare password, not JSON); **no Snowflake connection has been
made**.

### ⚠ TEST fixed the severity, not the failsafe

Spec §2.1 pre-flight step 1 requires proving read-only by **watching the role refuse a write**.
`snowflake-admin-nonprod` is an **admin** account — it will not refuse. So the failsafe cannot pass
as written, in TEST or PROD.

What changed is the cost: the failsafe exists to prove *no rollback can be needed*, and in TEST a
rollback **is** possible. Two honest routes, **and Paul has not yet chosen**:

1. **A read-only role in TEST** — `SELECT` + `INFORMATION_SCHEMA` on `TEST_DG1_GEP`, nothing else.
   The pre-flight then means what it says. Cheap in non-prod. *Preferred.*
2. **Use `snowflake-admin-nonprod` and amend the failsafe honestly** — record read-only as
   `ASSUMED`, never `MEASURED`, with TEST's recoverability as the stated compensating control.

⛔ **What must not happen: running the pre-flight against an admin account and reporting it as a
read-only proof.** That is the vacuous-verification shape this repo has now met nine times.

### ⚠ And a condition on R3's output regardless of route

**TEST's marketing-data currency is unverified.**
`wiki/processes/distributed-workflow/active/navira/active/navira-dwh-data-landing.md` records a
Navira re-land into TEST that was **planned, not executed**, and Lectric confirmed *"greenfield in
TEST (no objects)"*. So R3's first queries must establish what TEST actually holds — object
presence, row counts, max dates — and every grain claim must be labelled against that. **Structure
in TEST is trustworthy; row-level distributions may not be. A grain claim from a stale copy is
worse than none.**

First pre-flight query is the vault's own instruction: `SHOW GRANTS TO USER TEST_DG1_CORE_ADMIN`.

## 4. Queued, explicitly not started

**Client Review Loop V0** — `docs/specs/client-review-loop-v0.md`, filed `44bf6b8`. Gated by its
own first line: no UI, and no interruption of this mission. Its `next:` fires when the TEST
candidate exists, and **step one is the repo inspection, not the design**. It carries a leads table
of candidate primitives with two warnings that matter: ticket-level `blocked_by` is `[]` in all 189
task events, and `presets.needs_paul` is display-only — an approval gate built on it would not gate.

⚠ Paul pasted this spec twice; it is filed once. Do not file it again.

## 5. Open, and not done

- **The rotation decision** (§1) and **the failsafe route** (§3). Both are Paul's.
- **Two F96 candidates, unfiled** — `WAVE_0.yaml` invisible to `factory.dispatch`; `task_claim`
  only observes `claude.exe` holders. Prior instruction: file only if ≤10 minutes, and **do not fix
  either unless one blocks this mission**.
- **The deny-list finding** (§1) — worth filing.
- **Wave 1 has not started.** No worker has run.
- `first-real-dispatch-2026-08-31.md` — F90 remedy (a) + sparse-checkout, paused for this mission.

## 6. Verify in one command each

```bash
git -C ~/repos/agent-factory status --porcelain          # expect clean
python -m factory.session                                 # the board, derived
python scripts/credential_use.py --list                   # 1 row, R3, READ
python -c "from factory import findings; print([f.id for f in findings.design_debt()])"
ls .data/missions/
```
