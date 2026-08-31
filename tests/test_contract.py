from factory.contract import GreenContract, Unmeasurable, Verdict


def _c():
    c = GreenContract("t")

    def rows(ctx):
        n = ctx.get("rows")
        if n is None:
            raise Unmeasurable("no warehouse")
        return n > 0, f"{n}"

    return c.add("rows", rows)


def test_pass():
    assert _c().run({"rows": 5}).verdict is Verdict.PASS


def test_fail():
    assert _c().run({"rows": 0}).verdict is Verdict.FAIL


def test_unmeasurable_is_not_a_pass():
    r = _c().run({})
    assert r.verdict is Verdict.UNMEASURABLE
    assert not r.is_green, "UNMEASURABLE must never count as green"


def test_crashing_instrument_is_not_a_pass():
    # Was asserted as UNMEASURABLE until 2026-08-30. That was the collapse this module
    # exists to prevent; a crash is now ERROR. See the fifth-verdict block below.
    c = GreenContract("x").add("boom", lambda ctx: 1 / 0)
    v = c.run({}).verdict
    assert v is Verdict.ERROR
    assert v is not Verdict.PASS


def test_empty_contract_is_not_run():
    assert GreenContract("empty").run({}).verdict is Verdict.NOT_RUN


# --- the fifth verdict: apparatus failure is not inconclusiveness -------------
#
# TTCN-3 (ISO/IEC 9646; ITU-T Z.140 §24.2) carries FIVE verdicts on a monotone
# lattice — none < pass < inconc < fail < error — where `error` is set by the
# TEST SYSTEM, not the test case, and cannot be overridden. `Unmeasurable` is
# our `inconc`: a probe that knows it cannot look. A bare exception is our
# `error`: OUR apparatus broke, so the run itself is untrustworthy.
#
# Collapsing the two is the defect this block exists to prevent — in a module
# whose whole purpose is refusing to collapse two kinds of not-knowing.


def _boom():
    return GreenContract("x").add("boom", lambda ctx: 1 / 0)


def test_a_crashed_instrument_is_error_not_unmeasurable():
    """A crash is our apparatus failing, not the world declining to be measured."""
    r = _boom().run({})
    assert r.verdict is Verdict.ERROR, (
        "a bare exception means the instrument broke; reporting it as UNMEASURABLE "
        "hides a harness bug inside a legitimate measurement gap")


def test_a_deliberate_unmeasurable_is_still_unmeasurable():
    """Regression guard: the fix must not sweep declared inconclusiveness into ERROR."""
    assert _c().run({}).verdict is Verdict.UNMEASURABLE


def test_error_dominates_fail():
    """If the apparatus broke, we do not know the observed FAIL was real."""
    c = _boom()

    def nope(ctx):
        return False, "observed a real failure"

    c.add("nope", nope)
    assert c.run({}).verdict is Verdict.ERROR


def test_error_is_never_green():
    assert not _boom().run({}).is_green


def test_error_is_reported_in_failures_and_summary():
    r = _boom().run({})
    assert [x.verdict for x in r.failures()] == [Verdict.ERROR]
    assert "ERROR=1" in r.summary()


def test_error_carries_no_score_attribution():
    """An errored run cannot be asked for the corpus it was scored against."""
    from factory.evaluator import UNSCORED_VERDICTS
    assert "ERROR" in UNSCORED_VERDICTS
