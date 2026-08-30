"""The reload button must reload every factory module the tracker actually imports.

⛔ The failure this pins, measured 2026-08-29. The reload set was two hand-written lists — `_HOT`
(6 modules) and an `_EXTRA` block (9 more) — against **19** factory modules the script imports.
Missing: `factory.flow`, `factory.runs`, `factory.sessions`. So "↻ reload code & re-measure"
re-served the session code the process started with and reported success.

That is not a missing feature, it is a **claim of freshness that is false** — the same defect
already recorded in that file's own comments against `factory.dispatch`, fixed once by adding a
line, and therefore guaranteed to recur on the next import anyone added. It recurred.

⭐ This is the third hand-maintained allow-list to under-cover in one session, after
`TeamSpec.version`'s enumerated hash keys and `synthesis.session_prompt`'s `or` fallback. The
shared shape: a list that is supposed to mirror something, kept in step by hand, silently missing
an entry. The fix is the same each time — derive it — and this test is what makes the derivation
falsifiable rather than merely asserted.
"""
from __future__ import annotations

import ast
import pathlib

from scripts import local_tracker as lt


def test_every_imported_factory_module_is_reloadable():
    """The regression: no factory import may sit outside the reload set."""
    imported = set(lt._imported_factory_modules())
    hot = {n.split(".", 1)[1] for n in lt._HOT}
    missing = sorted(imported - hot)
    assert not missing, (
        f"these factory modules are imported but never reloaded: {missing}. The reload button "
        "would report success while continuing to serve their old code.")


def test_the_reload_set_is_derived_not_typed():
    """A literal list of module names in the source is the defect coming back.

    Checks the module-name strings are not sitting in a tuple/list literal anywhere in the file —
    the derivation is only worth having if nobody quietly reintroduces the hand-written copy.
    """
    src = pathlib.Path(lt.__file__).read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Tuple, ast.List)):
            continue
        strs = [e.value for e in node.elts
                if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        hits = [s for s in strs if s.startswith("factory.")]
        assert len(hits) < 3, (
            f"a hand-written list of factory modules is back in local_tracker.py: {hits[:5]}. "
            "Derive it from the imports instead — that list under-covered twice.")


def test_dependency_order_puts_a_module_after_what_it_imports():
    """Reload order is load-bearing: board and lanes hold references to readiness's Gate objects.

    Reloading an importer before its dependency leaves it holding the OLD objects, so the button
    reports a reload that partly did not happen. The old tuple maintained this ordering by hand,
    invisibly.
    """
    order = lt._dependency_order(lt._imported_factory_modules())
    assert set(order) == set(lt._imported_factory_modules()), "ordering dropped or invented a module"
    pos = {n: i for i, n in enumerate(order)}
    assert pos["readiness"] < pos["board"], "board imports from readiness"
    assert pos["readiness"] < pos["lanes"], "lanes imports from readiness"


def test_value_imports_are_parsed_not_regexed():
    """Every rebound name must really be exported by the module it is attributed to.

    ⚠ The first attempt at this derivation used a regex, which ran past the end of the import
    statement and produced 125 "names" — including `E402`, scraped out of a `# noqa` comment.
    A derivation that derives the wrong thing is worse than the hand-written list, because it
    looks principled. This asserts the parse is real.
    """
    import importlib

    for mod, names in lt._value_imports():
        m = importlib.import_module(f"factory.{mod}")
        for n in names:
            assert n.isidentifier(), f"{n!r} is not an identifier — the parse is scraping text"
            assert hasattr(m, n), f"factory.{mod} does not export {n!r}"


def test_hot_reload_runs_and_reports_what_it_did():
    """It must succeed, and its message must be counted from what ran, not from a literal.

    The old message added two hand-maintained list lengths and was wrong by 10 for a period —
    the one number an operator had for "did my edit land".

    ⚠ **Runs in a SUBPROCESS, and that is not tidiness.** Calling `hot_reload()` in-process
    reloads `factory.tasks`, which rebuilds `EvidenceRequired` as a NEW class object — so
    `tests/test_tasks.py`'s `pytest.raises(EvidenceRequired)`, holding the old one, stops
    matching and two unrelated tests fail. Found by running the suite: this test broke them on
    its first outing. A test that mutates interpreter-wide module state is a test that makes
    other tests lie, and widening the reload set from 6 modules to 20 widened that blast radius
    with it.

    ⭐ The same caveat applies to the button in the running server, and is why it re-measures per
    request: any object built before a reload is an instance of the pre-reload class. The server
    constructs its objects fresh on each request, so it is safe there — but a reload is not a
    free operation, and nothing should hold a factory object across one.
    """
    import subprocess
    import sys

    code = (
        "import importlib.util;"
        "s=importlib.util.spec_from_file_location('lt',r'scripts/local_tracker.py');"
        "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
        "ok,msg=m.hot_reload();print(int(ok));print(len(m._HOT));print(msg)"
    )
    r = subprocess.run([sys.executable, "-c", code],
                       capture_output=True, text=True,
                       cwd=pathlib.Path(lt.__file__).resolve().parent.parent)
    assert r.returncode == 0, f"reload subprocess failed:\n{r.stderr[-2000:]}"
    ok, n_hot, msg = r.stdout.strip().split("\n", 2)
    assert ok == "1", f"hot_reload failed: {msg}"
    assert f"reloaded {n_hot} modules" in msg, (
        f"the reload message must count what it actually reloaded; got {msg!r}")
    assert "no longer exported" not in msg, msg
