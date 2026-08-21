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


def test_crashing_instrument_is_unmeasurable_not_pass():
    c = GreenContract("x").add("boom", lambda ctx: 1 / 0)
    assert c.run({}).verdict is Verdict.UNMEASURABLE


def test_empty_contract_is_not_run():
    assert GreenContract("empty").run({}).verdict is Verdict.NOT_RUN
