"""Identify research answers by their content and file them under the right name.

    python scripts/file_answers.py            # show what it would do
    python scripts/file_answers.py --apply    # rename

Drop the raw answers into docs/research/answers/ under any filename. This reads each one, works
out which prompt it answers from distinctive phrases in the answer itself, and renames it to
R<n>-answer-<slug>.md.

This exists because the first two answers arrived with their contents SWAPPED — the file named
for the eval harness held the topology answer. A filename is a claim about content, and an
unchecked claim is how a future session reads the wrong document and never notices.

It refuses to guess. If two prompts score close together, or nothing scores, it says so and
changes nothing — a misfiled answer is worse than an unfiled one.
"""
from __future__ import annotations

import pathlib
import re
import sys

ANSWERS = pathlib.Path(__file__).resolve().parent.parent / "docs" / "research" / "answers"

# Weighted markers. Chosen to be things the ANSWER says, not things the prompt asked, so a file
# that merely quotes the question back does not match. Weight 3 = near-decisive, 1 = supporting.
PROMPTS = {
    1: ("eval-harness", [
        (3, r"green\s*contract"), (3, r"seven design decisions"), (3, r"mutation registry"),
        (2, r"\bUNMEASURABLE\b"), (2, r"negative control"), (2, r"corpus"),
        (2, r"tamper[- ]evident"), (1, r"session[- ]stamp"), (1, r"Inspect AI"),
        (1, r"promptfoo|braintrust|deepeval|langsmith"),
    ]),
    2: ("topology", [
        (3, r"multi[- ]agent"), (3, r"architect.{0,40}implementer.{0,40}tester"),
        (3, r"single[- ]agent baseline"), (2, r"\bseam"), (2, r"topolog"),
        (2, r"deferral list"), (1, r"langgraph|crewai|autogen|swarm"),
        (1, r"hierarch"), (1, r"handoff"),
    ]),
    3: ("control-plane", [
        (3, r"orphan"), (3, r"attempt cap|retry cap"), (3, r"reap"),
        (2, r"terminal state|terminal semantics"), (2, r"lease|heartbeat"),
        (2, r"sandbox"), (2, r"tenanc"), (1, r"firecracker|gvisor|\bE2B\b|modal|daytona"),
        (1, r"kill switch"),
    ]),
    4: ("agnostic-optimizer", [
        (3, r"agnostic"), (3, r"fitness (discovery|function)"), (3, r"\bDSPy\b|\bGEPA\b|TextGrad"),
        (2, r"transfer"), (2, r"repo interface|repository interface"),
        (2, r"OpenEvolve|AlphaEvolve|autoresearch"), (2, r"devcontainer|SWE-bench"),
        (1, r"changepoint|degradation detection"),
    ]),
    # ---- added 2026-08-23, when R10/R11/R12 landed together and nothing could file them.
    # R5-R7 are deliberately ABSENT. R7's answer already discusses switchboard, PTYs, Electron
    # and SQLite — the whole of R12's subject — so no marker set separates them by content, and
    # inventing one would risk renaming a correctly-filed answer. Unclassifiable is the safe
    # verdict here: the script changes nothing and says so.
    8: ("data-engineering-agent-factory", [
        (3, r"zero[- ]copy|clone schema"), (3, r"isolation (tier|ladder)"),
        (2, r"blast radius"), (2, r"data engineering"), (1, r"dbt|--defer"),
    ]),
    10: ("hierarchical-wiki-agent-training", [
        (3, r"hierarchical wiki"), (3, r"\bRAG\b"), (2, r"knowledge base"),
        (2, r"context window"), (1, r"auto[- ]?research"),
    ]),
    11: ("factory-concept-diff", [
        # `first-class` and `vocabular` were the obvious markers and are useless: R1, R2 and R3
        # all use them, and R11 tied 8-8 with R2. These are named products the concept survey
        # reports on and no other answer mentions at all.
        (3, r"factory\.ai|sierra"), (3, r"ADK"), (3, r"26 concepts|our 26"),
        (2, r"guardrail"), (2, r"make first[- ]class"), (2, r"packaged"), (1, r"cursor"),
    ]),
    # Every R12 marker is chosen to be ABSENT from R7's answer — see the note above.
    12: ("session-manager-ui", [
        (3, r"doctly"), (3, r"tmux|zellij"), (2, r"reattach"),
        (2, r"full[- ]text search"), (2, r"cost track"), (1, r"session registry"),
    ]),
}

CANONICAL = {n: f"R{n}-answer-{slug}.md" for n, (slug, _) in PROMPTS.items()}



def _next_run_name(want: str, root: pathlib.Path, planned: dict) -> str:
    """R4-answer-x.md -> R4-answer-x-run2.md, skipping any run number already taken."""
    stem, suffix = want[:-3], want[-3:]
    n = 2
    while True:
        candidate = f"{stem}-run{n}{suffix}"
        if not (root / candidate).exists() and candidate not in planned:
            return candidate
        n += 1


def score(text: str) -> dict[int, int]:
    low = text.lower()
    out = {}
    for n, (_, markers) in PROMPTS.items():
        out[n] = sum(w for w, pat in markers if re.search(pat, low, re.I | re.S))
    return out


def classify(path: pathlib.Path):
    """Return (prompt_number, scores) or (None, scores) when it will not guess."""
    text = path.read_text(encoding="utf-8", errors="replace")
    s = score(text)
    ranked = sorted(s.items(), key=lambda kv: -kv[1])
    best, runner = ranked[0], ranked[1]
    if best[1] < 6:
        return None, s                      # nothing looks like an answer
    if best[1] - runner[1] < 4:
        return None, s                      # too close to call
    return best[0], s


def main(argv=None) -> int:
    apply = "--apply" in (argv or sys.argv[1:])
    if not ANSWERS.is_dir():
        print(f"no answers directory at {ANSWERS}")
        return 2

    files = [p for p in sorted(ANSWERS.glob("*.md")) if p.name != "README.md"]
    if not files:
        print(f"{ANSWERS} holds no answers yet.")
        return 0

    planned, problems = {}, []
    for p in files:
        # `R2-followup.md` is a correctly-named follow-up exchange, not an answer to a prompt.
        # It scores on whatever it DISCUSSES, and R2's follow-up discusses the control plane —
        # so without this guard --apply renames it to `R3-answer-control-plane-run2.md` and a
        # follow-up is silently reclassified as a second run of someone else's prompt. Latent
        # since the follow-ups were written; caught 2026-08-23 by reading a dry run instead of
        # trusting it.
        if re.fullmatch(r"R\d+-followup\.md", p.name):
            print(f"  = {p.name:<34} follow-up, not an answer — left alone")
            continue
        n, s = classify(p)
        detail = " ".join(f"R{k}={v}" for k, v in sorted(s.items()))
        if n is None:
            problems.append(f"  ? {p.name:<34} cannot tell  [{detail}]")
            continue
        want = CANONICAL[n]
        # `R4-answer-x.md` and `R4-answer-x-run2.md` are BOTH already-correct names for prompt 4.
        # Comparing only against the base name made this non-idempotent: every run re-classified
        # run2 as a fresh second run and bumped it to run3, then run4, forever.
        if p.name == want or re.fullmatch(re.escape(want[:-3]) + r"-run\d+\.md", p.name):
            print(f"  = {p.name:<34} already correct  [{detail}]")
            continue
        if want in planned:
            problems.append(f"  ! {p.name:<34} also claims {want}  [{detail}]")
            continue

        # A second answer to the same prompt is not an error — running a prompt twice is a
        # legitimate thing to do, and where two runs disagree is a finding. But the target may
        # already be occupied, and renaming onto it would destroy the earlier answer silently.
        # This branch exists because that nearly happened: a second R4 run appeared under a
        # generic filename and the first version of this script would have overwritten the first.
        occupied = ANSWERS / want
        if occupied.exists() and occupied.resolve() != p.resolve():
            if occupied.read_bytes() == p.read_bytes():
                problems.append(
                    f"  = {p.name:<34} byte-identical to {want} — a re-drop, not a second run. "
                    f"Delete it or leave it; nothing to file.")
                continue
            want = _next_run_name(want, ANSWERS, planned)
            print(f"  -> {p.name:<33} becomes {want}   SECOND RUN of this prompt  [{detail}]")
            planned[want] = p
            continue

        planned[want] = p
        flag = "SWAPPED/MISNAMED" if p.name != want else ""
        print(f"  -> {p.name:<33} becomes {want}   {flag}  [{detail}]")

    for line in problems:
        print(line)

    if not planned:
        print("\nnothing to rename.")
        return 1 if problems else 0

    if not apply:
        print(f"\n{len(planned)} file(s) would be renamed. Re-run with --apply.")
        return 0

    # Two-phase, so a straight swap of two names cannot clobber either one.
    tmp = {}
    for want, src in planned.items():
        t = src.with_name(src.name + ".renaming")
        src.rename(t)
        tmp[want] = t
    for want, t in tmp.items():
        t.rename(ANSWERS / want)
        print(f"  renamed -> {want}")
    print(f"\n{len(tmp)} file(s) filed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
