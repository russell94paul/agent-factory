"""One relation, one implementation — and proof the guard can fail.

⛔ **The defect this file exists to prevent, stated plainly.** "Which prompts must R18 wait for"
had TWO implementations. `dispatch.DEPENDS` was a hardcoded map; `research_run.depends_on` parsed
the prompt's own `**Depends on:**` header. R17 and R18 were written declaring the edge in the
header and nobody added it to the map, so on 2026-08-23:

    Research tab   R18 button DISABLED — "waits on R17 (UNDISPATCHED)"     ← correct
    Readiness board R18 "send it — written and waiting on you,
                    nothing is working on it"                              ← wrong, and it invited
                                                                             the click

⭐ **The surface that said "go" was the unguarded one.** `_validate` could not catch it: it checks
that every authored edge names a live prompt — a DANGLING edge — and a MISSING edge is invisible to
it by construction. So no test here asserts the map's contents. They assert that the two READERS
agree, which is the property that actually broke.

Every test below is paired with a negative control that constructs the disagreement on disk and
asserts the guard fires. A guard nobody has watched fail is decoration (F11).
"""

from __future__ import annotations

import pathlib

import pytest

from factory import dispatch as d
from factory import research_run as rr


# --------------------------------------------------------------------------- live


def test_the_button_and_the_board_read_the_same_edges():
    """For every real prompt, the Research tab and the readiness board must agree on prerequisites.

    ⚠ **Be honest about what this can and cannot catch.** Now that `depends_on` DELEGATES to
    `edges`, both sides call one function and this assertion is close to tautological — it cannot
    fail while the delegation stands. Verified: with `edges` monkeypatched back to the old
    map-only behaviour, this test still passed, because both readers moved together.

    It is kept for the one thing it does catch: somebody re-implementing the header parser in
    `research_run` — which is precisely how the defect arose the first time. The guards that
    actually stand behind the behaviour are `test_a_header_only_edge_is_honoured_with_nothing_in
    _the_map` (proven to fail against the old code) and `test_r18_waits_on_r17_from_its_header
    _alone`. Do not read a pass here as evidence the edge works.
    """
    for rid in sorted(d.prompts()):
        assert set(rr.depends_on(rid)) == set(d.edges(rid)), (
            f"{rid}: the Research tab and the readiness board disagree about what it waits on — "
            f"button says {rr.depends_on(rid)}, board says {d.edges(rid)}. "
            "That is the R18 defect returning: two implementations of one relation."
        )


def test_r18_waits_on_r17_from_its_header_alone():
    """The concrete edge that was missing, asserted at both surfaces.

    ⚠ Deliberately NOT asserted via `DEPENDS`. R18's edge lives only in its header, and the whole
    point is that this is now sufficient. If someone later adds it to the map too, this still
    passes — the union is the contract, not the source.
    """
    assert "R17" in d.declared_depends("R18"), (
        "R18-our-factory-internal-audit.md no longer declares '**Depends on:** R17'. It audits "
        "R17's recommendations against our code; running it first does not fail, it silently "
        "produces a worse answer."
    )
    assert "R17" in d.edges("R18")
    assert "R17" in rr.depends_on("R18")


def test_a_pass_is_only_free_when_its_dependency_is_answered_and_owes_no_run():
    """`plan()` must use `blocked_by`, not a re-derivation of it from `state` alone.

    The stricter rule — ANSWERED **and** no pending run-log row — is the R13 scar, and it lived
    only on the board until the two readers were merged. A `plan()` that recomputed "unmet" from
    `state` would have re-created the same two-answers-to-one-question defect one layer down.
    """
    for rid in sorted(d.prompts()):
        assert set(rr.plan(rid)["unmet"]) == set(d.blocked_by(rid)), (
            f"{rid}: plan() and blocked_by() disagree about unmet dependencies"
        )


def test_no_prompt_declares_a_dependency_that_does_not_exist():
    """`_validate` now stands behind declared edges too, not only authored ones."""
    d._validate()


def test_the_cli_actually_runs_as_a_module():
    """⭐ Run as a SUBPROCESS on purpose — `import` cannot see this class of bug at all.

    `if __name__ == "__main__": main()` sat two-thirds of the way up `dispatch.py`, with `_ROW`,
    `run_log`, `DEPENDS`, `edges`, `blocked_by` and `order` all defined BELOW it. Executing the
    module as `python -m factory.dispatch` therefore fired the entry point before any of those
    existed, and `render()` raised `NameError` the moment it needed one of them.

    Every existing test imports the module, which runs it to the end — so the ordering was
    invisible to the entire suite while being fatal from the command line. The only instrument
    that can see it is one that runs it the way a human does.
    """
    import subprocess
    import sys

    from factory import repo

    r = subprocess.run([sys.executable, "-m", "factory.dispatch"], cwd=str(repo.primary()),
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, (
        f"`python -m factory.dispatch` exited {r.returncode}. Most likely the __main__ guard has "
        f"drifted back above a definition it needs.\n{r.stderr[-600:]}"
    )
    assert "Research dispatch state" in r.stdout


def test_a_held_prompt_is_not_reported_as_waiting_on_a_human():
    """The CLI's third view of the same relation. R18 is unsent because R17 owes it an answer —
    naming Paul as the blocker for something he cannot act on is the same lie as the board's
    "send it — nothing is working on it", in a different font."""
    out = d.render()
    if "R18" in d.prompts() and d.blocked_by("R18"):
        assert "R18 waits on R17" in out
        assert "R18 — waiting on Paul" not in out


# ----------------------------------------------------------------- negative control


def _prompt(dirp: pathlib.Path, name: str, depends: str | None, status: str = "NOT DISPATCHED.") -> None:
    body = f"# {name}\n\n**Status: {status}** Written for a test.\n\n"
    if depends is not None:
        body += f"**Depends on:** {depends}\n\n"
    body += "## Run log\n\n| Run | Dispatched | Outcome |\n|---|---|---|\n| — | — | not yet dispatched |\n"
    (dirp / name).write_text(body, encoding="utf-8")


@pytest.fixture()
def world(tmp_path: pathlib.Path):
    research = tmp_path / "research"
    (research / "answers").mkdir(parents=True)
    return research, research / "answers"


def test_a_header_only_edge_is_honoured_with_nothing_in_the_map(world):
    """⭐ THE negative control. Reproduces R18 exactly: an edge that exists ONLY in the header.

    Under the old code `blocked_by` returned `[]` here and the board said "send it". If this ever
    returns `[]` again, the defect is back.
    """
    research, answers = world
    _prompt(research, "R90-upstream.md", None)
    _prompt(research, "R91-downstream.md", "R90")

    assert "R91" not in d.DEPENDS, "the fixture must not rely on the authored map"
    assert d.declared_depends("R91", research) == ["R90"]
    assert d.blocked_by("R91", research, answers) == ["R90"], (
        "a dependency declared only in the prompt header was ignored — this is the exact R18 "
        "defect, and the board would again invite a send it should refuse"
    )


def test_the_guard_clears_once_the_dependency_is_answered(world):
    """The other half: the edge must also stop blocking. A gate stuck shut is its own defect."""
    research, answers = world
    _prompt(research, "R90-upstream.md", None, status="DISPATCHED 2026-08-23.")
    _prompt(research, "R91-downstream.md", "R90")
    assert d.blocked_by("R91", research, answers) == ["R90"]

    (answers / "R90-answer-x.md").write_text("done", encoding="utf-8")
    assert d.blocked_by("R91", research, answers) == [], (
        "the dependency is answered and owes no further run, but the edge still blocks"
    )


def test_none_is_a_declaration_and_a_missing_line_is_not_an_error(world):
    research, _ = world
    _prompt(research, "R92-standalone.md", "none")
    _prompt(research, "R93-silent.md", None)
    assert d.declared_depends("R92", research) == []
    assert d.declared_depends("R93", research) == []


def test_the_union_keeps_authored_edges_that_the_header_omits(world, monkeypatch):
    """Union, not precedence. An authored edge carries the rationale for the ordering; a header
    that forgets it must not silently delete it."""
    research, answers = world
    _prompt(research, "R94-first.md", None)
    _prompt(research, "R95-second.md", None)          # declares nothing
    monkeypatch.setitem(d.DEPENDS, "R95", ["R94"])
    assert d.declared_depends("R95", research) == []
    assert d.edges("R95", research) == ["R94"]
    assert d.blocked_by("R95", research, answers) == ["R94"]


def test_validate_rejects_a_declared_edge_naming_a_prompt_that_does_not_exist(world):
    research, _ = world
    _prompt(research, "R96-dangling.md", "R99")
    with pytest.raises(ValueError, match="R99"):
        d._validate(research)


def test_a_dependency_answered_but_owing_a_further_run_still_blocks(world):
    """The R13 rule, on a header-declared edge. An answer is not enough if a run is still pending —
    this is what R14's stale `pending` row was falsely triggering across the whole board."""
    research, answers = world
    (research / "R90-upstream.md").write_text(
        "# R90\n\n**Status: DISPATCHED 2026-08-23.**\n\n"
        "## Run log\n\n| Run | Dispatched | Outcome |\n|---|---|---|\n"
        "| 1 | 2026-08-23 | answered |\n| 2 | pending | a rewrite nobody has sent |\n",
        encoding="utf-8")
    _prompt(research, "R91-downstream.md", "R90")
    (answers / "R90-answer-x.md").write_text("done", encoding="utf-8")

    assert d.blocked_by("R91", research, answers) == ["R90"], (
        "R90 is answered but its run log still owes run 2 — the edge must hold"
    )
