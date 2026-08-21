"""⭐ The negative control. If this file passes trivially, the whole factory is decoration."""
from factory.contract import GreenContract, Verdict
from factory.evals import mutate_and_expect_failure


def _contract():
    return (GreenContract("connector-green")
            .add("rows", lambda ctx: (ctx.get("rows", 0) > 0, str(ctx.get("rows"))))
            .add("marker", lambda ctx: (bool(ctx.get("session_id")), str(ctx.get("session_id"))))
            .add("agrees", lambda ctx: (ctx.get("source_rows") == ctx.get("rows"), "parity")))


GOOD = {"rows": 100, "session_id": "ses_1", "source_rows": 100}


def test_every_mutation_is_caught():
    reports = mutate_and_expect_failure(_contract(), GOOD, {
        "rows": 0,
        "session_id": None,
        "source_rows": 7,
    })
    holes = [r.case for r in reports if not r.ok]
    assert not holes, f"contract did not notice: {holes}"


def test_a_contract_that_cannot_fail_is_reported_as_a_hole():
    """A vacuous contract must be caught BY the harness, not slip through green."""
    vacuous = GreenContract("vacuous").add("always", lambda ctx: (True, "always true"))
    reports = mutate_and_expect_failure(vacuous, GOOD, {"rows": 0})
    assert any(not r.ok for r in reports), "harness failed to expose a vacuous contract"
