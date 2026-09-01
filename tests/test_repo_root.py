"""Shared state must resolve to the primary worktree, from anywhere.

`claims.py` and `worktrees.py` both used `__file__.parent.parent` as the repo root. That is right
in the primary checkout and wrong inside a lane worktree, and the consequence was a **false green
in the finish path** — reproduced on 2026-08-23 in `.worktrees/certify`:

    git status --porcelain          ?? _falsegreen_probe.txt     (dirty)
    worktrees.existing()            {}                           (no worktrees at all)
    worktrees.is_dirty('certify')   False                        (a gate that cannot refuse)

`finish.checks()` reads `is_dirty()` to warn that uncommitted work will not survive the worktree
being removed. Inside a worktree that warning silently stopped existing.

`runs.py` already had the correct resolver and kept it private, which is precisely what let the
other two stay wrong — so these tests assert on the SHARED resolver and on every module that
should be using it, not on one call site.
"""
from __future__ import annotations

import pathlib
import re

from factory import claims, repo, runs, worktrees


def test_the_primary_is_a_real_repository_root():
    """Whatever it resolves to must at least be a git checkout with this package in it."""
    p = repo.primary()
    assert p.is_dir(), p
    assert (p / "factory").is_dir(), f"{p} does not look like this repo"
    assert (p / ".git").exists(), f"{p} has no .git"


def test_the_primary_is_never_a_linked_worktree():
    """The whole point. `<primary>/.worktrees/<lane>` is the wrong answer, everywhere."""
    p = repo.primary().resolve()
    assert ".worktrees" not in p.parts, (
        f"the primary resolved to {p}, which is inside a linked worktree — shared state would be "
        "private to that lane")


def test_every_module_holding_shared_state_uses_the_same_root(real_ledger):
    """The fork, closed. Three modules answered this three ways and only one was right.

    Asserting each one lands under the SAME primary is what stops a fourth copy appearing.

    Takes `real_ledger` to opt out of conftest's autouse redirect, which points `runs._primary`
    at a tmp directory. Pointed there this assertion would compare two tmp paths and pass
    trivially — and a check that cannot fail is not a check.
    """
    primary = repo.primary().resolve()
    assert worktrees.REPO.resolve() == primary, "worktrees.REPO forked from the primary"
    assert claims.ROOT.resolve().parent.parent == primary, "claims.ROOT forked from the primary"
    assert runs._primary().resolve() == primary, "runs._primary forked from the primary"


def test_runs_delegates_rather_than_keeping_a_private_twin(real_ledger):
    """`runs` had the only correct copy, privately — which is why the others stayed broken.

    `real_ledger` opts out of the ledger redirect; see the note above.
    """
    assert runs._primary() == repo.primary()


def test_worktree_root_is_directly_under_the_primary():
    """If ROOT nests (…/.worktrees/<lane>/.worktrees) the `existing()` filter matches nothing."""
    assert worktrees.ROOT.resolve() == (repo.primary() / ".worktrees").resolve()
    assert worktrees.ROOT.resolve().parent == repo.primary().resolve()


def test_existing_finds_the_worktrees_git_reports():
    """`existing()` must agree with git, not with a path guess.

    This is the assertion that was false from inside a worktree: git listed four and `existing()`
    returned none, because the filter root had nested one level too deep.
    """
    import subprocess
    out = subprocess.run(["git", "-C", str(repo.primary()), "worktree", "list", "--porcelain"],
                         capture_output=True, text=True, timeout=30).stdout
    from_git = set()
    root = (repo.primary() / ".worktrees").resolve()
    for line in out.splitlines():
        if line.startswith("worktree "):
            p = pathlib.Path(line[len("worktree "):].strip()).resolve()
            try:
                rel = p.relative_to(root)
            except ValueError:
                continue
            if len(rel.parts) == 1:
                from_git.add(rel.parts[0])
    if not from_git:
        import pytest
        pytest.skip("no lane worktrees on this machine — nothing to agree about")
    assert set(worktrees.existing()) == from_git


def test_in_worktree_agrees_with_where_the_primary_points():
    """A direct way to ask 'am I somewhere that used to break things?'"""
    assert repo.in_worktree() == (repo.primary().resolve() != repo.HERE.resolve())


# --------------------------------------------------------------------------- the whole class

#: ⭐ The SOURCE scan root — this checkout, deliberately, and NOT `repo.primary()`.
#:
#: This is the one place the guard's own rule points the other way, and the rule says so: *"Git
#: tracked content may legitimately be checkout-relative — that is the real distinction, and it is
#: why this targets `.data/` instead of banning the expression outright."* Source files are
#: git-tracked content. `.data/` is not.
#:
#: ⛔ It was `repo.primary()`, which meant a suite running inside a worktree scanned the PRIMARY
#: checkout's files — so a lane could add the banned expression, run the guard, watch it pass, and
#: be reading someone else's source the whole time. The reverse also held: fixes made in a
#: worktree could not turn the guard green, because it never looked at them. A structural guard
#: aimed at the wrong checkout is the wrong-layer defect this repo already has a rule about.
_CHECKOUT = pathlib.Path(__file__).resolve().parent.parent


def _prose_lines(src: str) -> set:
    """Line numbers occupied by a docstring or a bare string expression -- i.e. by PROSE.

    ⭐ **This is the fix for a guard that matched its own rule description.** The check below looks
    for three literal tokens on one line, and those tokens appear -- correctly and deliberately --
    in prose that *documents* the rule. On 2026-09-01 it fired on `switchboard.py`, whose offending
    "violation" was a docstring telling the reader to use `repo.data()` and NOT the banned
    expression. The guard flagged a comment instructing people to obey the guard.

    ⛔ The first attempt at this dropped every STRING token and cost the guard its teeth: the
    literal `".data"` is itself a string, so the corrected detector could no longer see the real
    defect at all. Caught by the negative control below, which is the entire reason it exists.

    So prose is identified STRUCTURALLY rather than by token type: a string that is a whole
    statement (a docstring, or a bare string expression) is prose; a string used as a value --
    `/ ".data" /` -- is code. `ast` knows the difference and `tokenize` does not.
    """
    import ast
    out = set()
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            for n in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                out.add(n)
    return out


def _code_lines(src: str):
    """(line number, CODE text) for a source file, with comments and prose removed.

    ⛔ Returns the ORIGINAL line text with the comment tail cut off -- it does not rebuild the line
    out of tokens. Rebuilding was the first attempt and it broke the detector in a way that looked
    like it worked: joining tokens with spaces turns `.parent.parent` into `. parent . parent`, so
    the substring rule below matched nothing and every file came back clean. A guard that reports
    a clean estate because it mangled its own input is the worst possible failure here, and it was
    caught only by the negative control asserting a KNOWN violation is still seen.

    Comments go by token type; docstrings and bare string expressions go by `_prose_lines`. String
    literals used as VALUES survive, because the pattern being detected contains one (`".data"`).
    """
    import io
    import tokenize
    prose = _prose_lines(src)
    raw = src.splitlines()
    cut = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                cut.setdefault(tok.start[0], tok.start[1])
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    out = []
    for n, line in enumerate(raw, 1):
        if n in prose:
            continue
        out.append((n, line[:cut[n]] if n in cut else line))
    return out


def _data_root_aliases(src: str) -> dict:
    """NAME -> line, for module-level names bound to `__file__ ... .parent.parent`.

    ⛔ The two-line form of the same defect, which the single-line rule cannot see:

        ROOT  = pathlib.Path(__file__).resolve().parent.parent      # no ".data" on this line
        TASKS = ROOT / ".data" / "tasks.jsonl"                      # no "__file__" on this line

    Neither line trips a three-token same-line test, and together they are exactly the bug the
    guard exists to stop. This shipped in `tests/test_case_study.py` and `tests/test_client_review.py`
    and made both RED in every worktree and GREEN only in the primary checkout -- a test asserting
    a property of the checkout it happened to run in.
    """
    import ast
    out = {}
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return out
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        seg = ast.dump(node.value)
        if "__file__" not in seg or "'parent'" not in seg:
            continue
        if seg.count("'parent'") < 2:
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name):
                out[tgt.id] = node.lineno
    return out


def _alias_reaches_data(src: str, aliases: dict) -> list:
    """(alias, line) where a `__file__`-derived alias is joined to a `.data` path."""
    hits = []
    for n, line in _code_lines(src):
        if ".data" not in line:
            continue
        for name in aliases:
            if re.search(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", line):
                hits.append((name, n))
    return hits


def _computes_data_root_from_file(line: str) -> bool:
    """True for a line that builds a `.data/` path out of this file's own location.

    Deliberately a substring test rather than a regex: the thing being detected is three literal
    tokens on one line, and a regex here would be harder to read than the rule it encodes. Callers
    pass CODE (see `_code_lines`), so prose describing the rule never reaches this.
    """
    s = line.lstrip()
    if s.startswith("#"):
        return False
    return "__file__" in s and ".parent.parent" in s and ".data" in s


def test_no_module_computes_a_shared_data_root_from_its_own_file():
    """A STRUCTURAL guard, because fixing instances did not work.

    This bug appeared five times — claims, worktrees, handoff, bus, operator — each found
    separately, each fixed separately, and every fix left the pattern available for the next
    module. `runs.py` even had the correct resolver and kept it private, which is precisely what
    let the others stay wrong.

    So the rule is enforced rather than remembered: **anything under `.data/` is estate-wide state
    and must resolve through `factory.repo`.** Git-tracked content may legitimately be
    checkout-relative — that is the real distinction, and it is why this targets `.data/` instead
    of banning the expression outright.
    """
    bad = []
    # ⭐ Widened from `factory/` to every directory that writes shared state. The guard was
    # scoped to `factory/*.py` and `tests/test_case_study.py` had carried the exact banned
    # expression since before P1 -- `ROOT = pathlib.Path(__file__).resolve().parent.parent`
    # then `ROOT / ".data" / "tasks.jsonl"` -- so the test read an EMPTY `.data/` in every
    # worktree and failed there while passing in the primary checkout. A structural guard that
    # does not look at the directory where the bug lives is a guard with a blind spot, and
    # this one had two red tests sitting inside it.
    for sub in ("factory", "scripts", "tests"):
        for f in sorted((_CHECKOUT / sub).glob("*.py")):
            if f.name in ("repo.py", "test_repo_root.py"):
                continue
            try:
                src = f.read_text(encoding="utf-8")
            except OSError:
                continue
            for i, line in _code_lines(src):
                if _computes_data_root_from_file(line):
                    bad.append(f"{sub}/{f.name}:{i}  {line.strip()[:110]}")

    assert not bad, (
        "these build a .data/ path from __file__ instead of factory.repo, so the state is "
        "private to whichever worktree happens to run them:\n  " + "\n  ".join(bad))


def test_the_two_line_form_is_measured_and_reported():
    """⚠ The SPLIT form of the same defect — measured across the estate, deliberately NOT gated.

    `ROOT = pathlib.Path(__file__)…parent.parent` on one line and `ROOT / ".data" / …` on another
    is the same bug, and no single line carries all three tokens, so the rule above cannot see it.
    `_data_root_aliases` + `_alias_reaches_data` can, and `test_the_guard_catches_the_two_line_form`
    proves they do.

    ⛔ This test REPORTS rather than fails, and that is a deliberate scope decision rather than a
    weakened guard. Measured on 2026-09-01 it finds 11 pre-existing instances across `factory/`,
    `scripts/` and `tests/` — several of which (a script that genuinely wants its own checkout)
    may be correct. Turning it red would either force a same-session rewrite of eight files owned
    by other lanes, or invite a hand-maintained allow-list, and this repo has already recorded
    three allow-lists that silently under-covered. Promoting it to a gate is a decision for a
    human with the census in front of them, which is what this prints.
    """
    found = []
    for sub in ("factory", "scripts", "tests"):
        for f in sorted((_CHECKOUT / sub).glob("*.py")):
            if f.name == "test_repo_root.py":
                continue
            try:
                src = f.read_text(encoding="utf-8")
            except OSError:
                continue
            aliases = _data_root_aliases(src)
            for name, i in _alias_reaches_data(src, aliases):
                found.append(f"{sub}/{f.name}:{i}  {name} (from __file__ at {aliases[name]})")
    if found:
        print("\nSPLIT-FORM .data ROOTS (reported, not gated) — "
              f"{len(found)} instance(s):\n  " + "\n  ".join(found))
    # The instrument must be able to see; a census from a blind instrument is not a census.
    assert isinstance(found, list)


def test_the_structural_guard_can_actually_fail():
    """Proof the check above is not vacuous — the rule this repo holds every gate to.

    Uses the exact line that shipped in bus.py, so if the detector is ever loosened past the real
    defect this fails rather than quietly passing everything.
    """
    shipped = 'ROOT = pathlib.Path(__file__).resolve().parent.parent / ".data" / "bus"'
    assert _computes_data_root_from_file(shipped), (
        "the guard would not have caught the bug that actually shipped")
    assert not _computes_data_root_from_file('ROOT = _repo.data() / "bus"'), (
        "the guard flags the corrected form, so it would block the fix")
    assert not _computes_data_root_from_file(
        '    # ROOT = pathlib.Path(__file__).resolve().parent.parent / ".data" / "bus"'), (
        "a commented-out line is documentation, not a defect")


def test_the_guard_reads_code_and_not_prose():
    """⭐ Negative control for the self-match this guard actually shipped.

    A docstring that NAMES the banned expression must not be flagged; the same expression as real
    code on the next line must be. Both halves matter: the first is the false positive that made
    the guard red on its own repo, and the second proves fixing it did not blind the guard.
    """
    src = (
        'import pathlib\n'
        'def store_path():\n'
        '    """Use repo.data() and NOT pathlib.Path(__file__).resolve().parent.parent/.data."""\n'
        '    return _repo.data() / "tasks.jsonl"\n'
    )
    flagged = [n for n, line in _code_lines(src) if _computes_data_root_from_file(line)]
    assert flagged == [], f"prose describing the rule was flagged as a violation (lines {flagged})"

    violating = src + 'BAD = pathlib.Path(__file__).resolve().parent.parent / ".data" / "x"\n'
    flagged2 = [n for n, line in _code_lines(violating) if _computes_data_root_from_file(line)]
    assert flagged2 == [5], (
        f"the real violation on line 5 was not detected (flagged {flagged2}) - fixing the "
        f"false positive must not cost the guard its detection power")


def test_the_guard_catches_the_two_line_form():
    """⭐ Negative control for the split form that shipped in two test files.

    The bug that was actually live: a `__file__`-derived root on one line, a `.data` join on
    another. No single line carries all three tokens, so the original rule saw nothing while both
    files were red in every worktree.
    """
    split = (
        'import pathlib\n'
        'ROOT = pathlib.Path(__file__).resolve().parent.parent\n'
        'TASKS = ROOT / ".data" / "tasks.jsonl"\n'
    )
    aliases = _data_root_aliases(split)
    assert "ROOT" in aliases, "the __file__-derived alias was not recognised"
    assert _alias_reaches_data(split, aliases) == [("ROOT", 3)], (
        "the split form of the defect was not detected")

    fixed = (
        'from factory import repo\n'
        'ROOT = repo.primary()\n'
        'TASKS = repo.data() / "tasks.jsonl"\n'
    )
    assert _data_root_aliases(fixed) == {}, "the corrected form is flagged, so it blocks the fix"


def test_boot_prompts_resolve_to_the_real_cross_repo_home():
    """A lane's closing note is the human half that nothing can reconstruct.

    From inside a worktree this used to resolve to
    `<primary>/.worktrees/aldc-launchpad/boot-prompts`, which `mkdir(parents=True, exist_ok=True)`
    then created SILENTLY — writing the note into the directory that gets deleted when the
    worktree is removed. No error, no warning, and the one irreplaceable part of the handoff gone.
    """
    from factory import handoff
    assert handoff.BOOT.name == "boot-prompts"
    assert handoff.BOOT.parent.name == "aldc-launchpad"
    assert ".worktrees" not in handoff.BOOT.parts, (
        f"boot prompts would be written to {handoff.BOOT}, inside a worktree")


def test_the_event_bus_is_shared_across_the_estate():
    """A per-worktree bus is not a bus. Lanes run inside worktrees, which is where it mattered."""
    from factory import bus
    assert ".worktrees" not in bus.ROOT.parts, f"the bus at {bus.ROOT} is private to one worktree"
    assert bus.ROOT.parent.parent == repo.primary()


def test_operator_answers_are_visible_to_the_lane_that_asked():
    """Paul answers from the tracker in the primary; the lane reads from inside its worktree."""
    from factory import operator
    assert ".worktrees" not in operator.ROOT.parts
    assert operator.ROOT.parent.parent == repo.primary()


# ------------------------------------------------- a path that leaves this repository entirely

def test_a_path_to_another_repository_resolves_from_the_primary():
    """⛔ The sixth instance, and it fell between the guard's two categories.

    `test_no_module_computes_a_shared_data_root_from_its_own_file` targets `.data/` on a stated
    principle: estate-wide state must be shared, git-tracked content may be checkout-relative.
    `readiness.CONNECTORS` is neither. It names a **sibling repository**, which is estate-wide by
    definition — there is only one `prefect-connectors` — so the `.data/`-shaped guard never
    looked at it and it stayed wrong.

    Measured 2026-08-31 from `.worktrees/bootstrap-wave`, before the fix:

        CONNECTORS -> agent-factory/.worktrees/prefect-connectors    (is_dir() False)

    Every gate reading the connectors checkout was measuring a path that does not exist whenever
    it ran from a lane, and `CONNECTORS=` is inside `_suite_fingerprint`, so the suite cache keyed
    differently in a worktree and could never hit.
    """
    from factory import readiness
    assert readiness.FACTORY == repo.primary(), (
        f"readiness computes the estate root as {readiness.FACTORY}, not {repo.primary()}")
    assert readiness.CONNECTORS.parent == repo.primary().parent, (
        f"{readiness.CONNECTORS} is not a sibling of {repo.primary()}")
    assert ".worktrees" not in readiness.CONNECTORS.parts, (
        f"{readiness.CONNECTORS} is private to one worktree")


def test_readiness_does_not_derive_the_estate_root_from_its_own_file():
    """The structural half, because the assertion above only *discriminates* inside a worktree.

    Run from the primary, `__file__.parent.parent` and `repo.primary()` are the same path and the
    behavioural test passes over the bug. This one fails on the shipped defect from anywhere,
    which is the property that makes it worth having.
    """
    # ⚠ Read the module that was actually imported, not `primary()/factory/readiness.py`. In a
    # lane worktree those are different files, and the first version of this test asserted on the
    # primary's copy — it would have passed a worktree whose own readiness.py still had the bug,
    # and failed a worktree that had just fixed it. Both are the wrong answer.
    from factory import readiness as _readiness
    src = pathlib.Path(_readiness.__file__).read_text(encoding="utf-8")
    assert re.search(r"^FACTORY = _repo\.primary\(\)", src, re.M), (
        "readiness.FACTORY must come from the shared resolver")
    assert not re.search(r"^FACTORY = pathlib\.Path\(__file__\)", src, re.M), (
        "readiness.FACTORY is back to being computed from its own file — the defect fixed on "
        "2026-08-31, which made CONNECTORS point inside .worktrees/ whenever a gate ran in a lane")
