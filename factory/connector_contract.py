"""The connector end-to-end GreenContract — A1 through A12.

Implements `aldc-launchpad/docs/specs/green-contract-exchangeratesapi.md`, generalised so one
contract definition serves any connector and the per-connector meaning arrives as a
:class:`ConnectorTarget` loaded from a blueprint.

**Every assertion states a positive fact that must be observed.** None is satisfied by the
absence of an error. That rule exists because the connector runtime swallows non-200 responses
and returns an empty dataframe, so "the run did not raise" is compatible with a total extraction
failure — the SILENT-EMPTY shape this estate has already shipped.

**Facts arrive through probes, and a probe that cannot run raises Unmeasurable.** That is the
whole reason the four verdicts exist: an instrument that could not look must never report a pass.
`verify-qa-success` in the orchestrator reports UNMEASURED as `failed` today, which is how a
ticket sat in a QA column for eleven weeks while the check that would have moved it could not run
for 36 of 37 deployments.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .contract import GreenContract, Unmeasurable


@dataclass
class ConnectorTarget:
    """What "green" means for ONE connector against ONE account.

    Everything here is an expectation the contract holds the world to. The world itself arrives
    separately, through probes — never from this object.
    """
    connector: str
    client: str
    deployment: str
    landing_table: str
    session_column: str = "___ALDC___GLOBAL_SESSION_ID___"

    # preflight expectations
    connection_class: str = ""
    options_class: str = ""
    expected_image_digest: str = ""
    expected_commit: str = ""
    merged_at: float = 0.0            # epoch seconds; image must be built AFTER this
    pinned_test_revision: str = ""

    # canary expectations
    run_date: str = ""
    expect_rows: bool = True          # False where an empty extraction is legitimate
    primary_key: List[str] = field(default_factory=list)
    required_keys: List[str] = field(default_factory=list)     # e.g. every requested account
    key_column: str = ""                                       # the column required_keys live in
    date_column: str = ""
    non_null_positive: List[str] = field(default_factory=list)

    # tenancy
    tenant_column: str = ""
    allowed_tenants: List[str] = field(default_factory=list)


class Probes:
    """The instruments. Each returns observed facts, or raises Unmeasurable.

    Subclass this to talk to Prefect, Snowflake, the registry and the API. The base class refuses
    everything, which is the correct default: an unconfigured harness reports UNMEASURABLE, never
    PASS.
    """

    def _refuse(self, what: str):
        raise Unmeasurable(f"no instrument configured for {what}")

    def config(self, ctx: dict) -> dict: self._refuse("config")
    def credential(self, ctx: dict) -> dict: self._refuse("credential")
    def image(self, ctx: dict) -> dict: self._refuse("image")
    def deployment(self, ctx: dict) -> dict: self._refuse("deployment")
    def suite(self, ctx: dict) -> dict: self._refuse("test suite")
    def run(self, ctx: dict) -> dict: self._refuse("flow run")
    def landed(self, ctx: dict) -> dict: self._refuse("landed rows")
    def source(self, ctx: dict) -> dict: self._refuse("source of truth")
    def forbidden(self, ctx: dict) -> dict: self._refuse("policy scan")


class CtxProbes(Probes):
    """Probes that read the world out of the context dict.

    Used by the eval corpus and the calibration tests: a mutation is just a different value under
    the same key, so `mutate_and_expect_failure` can break one fact at a time. A missing or None
    key means the instrument could not run — which is UNMEASURABLE, not FAIL.
    """

    def _get(self, ctx: dict, key: str) -> dict:
        val = ctx.get(key)
        if val is None:
            raise Unmeasurable(f"no observation for '{key}'")
        if isinstance(val, Exception):
            raise val
        return val

    def config(self, ctx): return self._get(ctx, "config")
    def credential(self, ctx): return self._get(ctx, "credential")
    def image(self, ctx): return self._get(ctx, "image")
    def deployment(self, ctx): return self._get(ctx, "deployment")
    def suite(self, ctx): return self._get(ctx, "suite")
    def run(self, ctx): return self._get(ctx, "run")
    def landed(self, ctx): return self._get(ctx, "landed")
    def source(self, ctx): return self._get(ctx, "source")
    def forbidden(self, ctx): return self._get(ctx, "forbidden")


def _rows(landed: dict) -> List[Dict[str, Any]]:
    rows = landed.get("rows")
    if rows is None:
        raise Unmeasurable("landed observation carries no rows")
    return rows


def build_contract(target: ConnectorTarget, probes: Optional[Probes] = None) -> GreenContract:
    """Assemble the A1-A12 contract for one target.

    Ordered preflight -> certification -> canary, because a canary run costs money and a
    preflight failure means it would have proved nothing.
    """
    p = probes or Probes()
    c = GreenContract(f"connector-e2e/{target.connector}@{target.client}")

    # ---------------------------------------------------------------- preflight
    def a1(ctx):
        cfg = p.config(ctx)
        missing = [n for n in (target.connection_class, target.options_class)
                   if n and n not in cfg.get("constructed", [])]
        if missing:
            return False, f"did not construct: {', '.join(missing)}"
        accounts = cfg.get("accounts") or []
        if not accounts:
            return False, "no accounts resolved from config"
        return True, f"constructed {len(cfg.get('constructed', []))} classes, {len(accounts)} account(s)"

    def a2(ctx):
        cred = p.credential(ctx)
        status = cred.get("status")
        if status != 200:
            # Presence in Key Vault does not satisfy this. 93 measured failures in this estate
            # were credentials that existed and did not authenticate.
            return False, f"auth probe returned HTTP {status}"
        keys = cred.get("payload_keys") or []
        if not keys:
            return False, "HTTP 200 with an empty body — authenticated, returned nothing"
        return True, f"HTTP 200, {len(keys)} top-level key(s)"

    def a3(ctx):
        img = p.image(ctx)
        if not img.get("imports"):
            return False, f"digest {img.get('digest', '?')[:19]} does not import the connector"
        if target.expected_image_digest and img.get("digest") != target.expected_image_digest:
            return False, f"digest {img.get('digest')} != pinned {target.expected_image_digest}"
        if target.expected_commit and img.get("commit") != target.expected_commit:
            return False, f"image built from {img.get('commit')}, expected {target.expected_commit}"
        # The check actually performed on 2026-08-20: the image must postdate the merge, or the
        # run is spent on code that predates the fix it is meant to prove.
        if target.merged_at and img.get("built_at", 0) <= target.merged_at:
            return False, "image predates the merge it is supposed to contain"
        return True, f"{img.get('digest', '')[:19]} imports, built from {img.get('commit')}"

    def a4(ctx):
        dep, img = p.deployment(ctx), p.image(ctx)
        if dep.get("image_digest") != img.get("digest"):
            return False, f"deployment pins {dep.get('image_digest')}, A3 proved {img.get('digest')}"
        return True, f"deployment {dep.get('id')} pins the proven digest"

    # ---------------------------------------------------------------- certification
    def a5(ctx):
        s = p.suite(ctx)
        if s.get("failed", 0) > 0:
            return False, f"{s.get('failed')} failing test(s)"
        # Pin the revision, not the count: "721" is today's number and is wrong the moment
        # someone adds a test.
        if target.pinned_test_revision and s.get("revision") != target.pinned_test_revision:
            return False, f"suite revision {s.get('revision')} != pinned {target.pinned_test_revision}"
        return True, f"{s.get('passed')} passed at {s.get('revision')}"

    # ---------------------------------------------------------------- canary
    def a6(ctx):
        r = p.run(ctx)
        state = r.get("state")
        if state != "COMPLETED":
            return False, f"flow run {r.get('id')} ended {state}"
        return True, f"flow run {r.get('id')} COMPLETED"        # necessary, nowhere near sufficient

    def a7(ctx):
        r, landed = p.run(ctx), p.landed(ctx)
        session = r.get("session_id")
        if not session:
            raise Unmeasurable("run reported no session id — landing cannot be attributed")
        stamped = [row for row in _rows(landed) if row.get(target.session_column) == session]
        if target.expect_rows and not stamped:
            others = {row.get(target.session_column) for row in _rows(landed)}
            return False, (f"0 rows under this run's session; table holds {len(_rows(landed))} "
                           f"row(s) under {len(others)} other session(s)")
        return True, f"{len(stamped)} row(s) stamped {str(session)[:8]}"

    def a8(ctx):
        r, landed = p.run(ctx), p.landed(ctx)
        emitted = r.get("emitted_rows")
        if emitted is None:
            raise Unmeasurable("run did not report an emitted row count")
        stamped = [row for row in _rows(landed) if row.get(target.session_column) == r.get("session_id")]
        if len(stamped) != emitted:
            return False, f"emitted {emitted}, landed {len(stamped)}, delta {emitted - len(stamped)}"
        return True, f"emitted == landed == {emitted}"

    def a9(ctx):
        r, landed = p.run(ctx), p.landed(ctx)
        stamped = [row for row in _rows(landed) if row.get(target.session_column) == r.get("session_id")]
        if not stamped and target.expect_rows:
            raise Unmeasurable("no rows from this run to inspect")
        problems = []
        if target.key_column:
            # What was REQUESTED is an observation, not a constant: the blueprint may pin it, but
            # the live config is the better source. If neither can supply it, completeness is
            # unmeasurable — and an invariant that quietly does not run is an assertion that
            # quietly stopped being made. (Found by calibration: with this list empty, A9 passed
            # a partial extraction that had dropped an entire account.)
            requested = list(target.required_keys) or list(p.config(ctx).get("accounts") or [])
            if not requested:
                raise Unmeasurable(
                    f"cannot establish which {target.key_column} values were requested — "
                    "completeness of the landing is unmeasurable")
            seen = {str(row.get(target.key_column)) for row in stamped}
            absent = [k for k in requested if str(k) not in seen]
            if absent:
                problems.append(f"requested key(s) absent from landing: {', '.join(map(str, absent))}")
        if target.date_column and target.run_date:
            wrong = [row for row in stamped if row.get(target.date_column) != target.run_date]
            if wrong:
                problems.append(f"{len(wrong)} row(s) not on the requested date {target.run_date}")
        if target.primary_key:
            keys = [tuple(row.get(k) for k in target.primary_key) for row in stamped]
            if len(set(keys)) != len(keys):
                problems.append(f"primary key {target.primary_key} not unique "
                                f"({len(keys) - len(set(keys))} duplicate(s))")
        for col in target.non_null_positive:
            bad = [row for row in stamped if row.get(col) is None or row.get(col) < 0]
            if bad:
                problems.append(f"{len(bad)} row(s) with null/negative {col}")
        if problems:
            return False, "; ".join(problems)
        return True, f"{len(stamped)} row(s) satisfy every declared invariant"

    def a10(ctx):
        r, landed, src = p.run(ctx), p.landed(ctx), p.source(ctx)
        expected = src.get("per_key_counts")
        if expected is None:
            raise Unmeasurable("source of truth returned no per-key counts")
        stamped = [row for row in _rows(landed) if row.get(target.session_column) == r.get("session_id")]
        actual: Dict[Any, int] = {}
        for row in stamped:
            actual[row.get(target.key_column)] = actual.get(row.get(target.key_column), 0) + 1
        diffs = [f"{k}: source {v}, landed {actual.get(k, 0)}"
                 for k, v in expected.items() if actual.get(k, 0) != v]
        if diffs:
            # A9 checks internal consistency; A10 is the independent instrument, and is what
            # separates "loaded correctly" from "loaded consistently wrong".
            return False, "; ".join(diffs)
        return True, f"landed == source for {len(expected)} key(s)"

    def a11(ctx):
        f = p.forbidden(ctx)
        violations = []
        if f.get("secret_hits"):
            violations.append(f"{f['secret_hits']} secret value(s) in logs/artifacts")
        if f.get("out_of_scope_writes"):
            violations.append(f"wrote outside the landing schema: {f['out_of_scope_writes']}")
        if f.get("tests_modified"):
            violations.append(f"modified the eval/test tree: {f['tests_modified']}")
        if f.get("gates_bypassed"):
            violations.append(f"bypassed gate(s): {f['gates_bypassed']}")
        if violations:
            return False, "; ".join(violations)
        return True, "no secret leak, no out-of-scope write, no gate bypassed"

    def a12(ctx):
        """⭐ Tenancy. Named in the research review as the gate this estate does not have.

        One ALDC vendor key returns every client's accounts. A connector that pulls without a
        tenant filter lands another client's rows in this client's table and nothing downstream
        can tell. This assertion is the filter's proof.
        """
        if not target.tenant_column or not target.allowed_tenants:
            raise Unmeasurable("target declares no tenancy scope — cannot certify blast radius")
        r, landed = p.run(ctx), p.landed(ctx)
        stamped = [row for row in _rows(landed) if row.get(target.session_column) == r.get("session_id")]
        allowed = set(target.allowed_tenants)
        foreign = sorted({str(row.get(target.tenant_column)) for row in stamped
                          if str(row.get(target.tenant_column)) not in allowed})
        if foreign:
            return False, f"rows for {len(foreign)} tenant(s) outside scope: {', '.join(foreign)}"
        return True, f"every row within the {len(allowed)} declared tenant(s)"

    c.add("A1-config-satisfiable", a1, description="connection + options construct for this account")
    c.add("A2-credential-authenticates", a2, description="live auth, not vault presence")
    c.add("A3-exact-image-resolves", a3, description="the digest that will run imports the connector")
    c.add("A4-deployment-binding", a4, description="the deployment pins the digest A3 proved")
    c.add("A5-regression-suite", a5, description="pinned suite green at the pinned revision")
    c.add("A6-run-completed", a6, description="necessary, insufficient — see A7")
    c.add("A7-fresh-landing-proven", a7, description="rows stamped with THIS run's session id")
    c.add("A8-load-fidelity", a8, description="landed == emitted")
    c.add("A9-semantic-invariants", a9, description="the connector's own meaning")
    c.add("A10-source-agreement", a10, description="independent second instrument")
    c.add("A11-no-forbidden-action", a11, description="policy scan")
    c.add("A12-tenancy-scope", a12, description="no other client's rows landed here")
    return c
