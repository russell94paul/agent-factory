# R18 — Our own factory, audited from inside the repo: the internal half of R8

**Status: NOT DISPATCHED.** Written 2026-08-23.

**Pass type:** STRUCTURE_CRITIQUE
**Depends on:** R17

⚠ **The researcher for this pass is not a web tool.** It is a **Claude Code session running in the
`agent-factory` checkout**, with the repo readable. That is the whole point: the thing R8 could not
do twice is cite a file and a line, and an agent sitting in the repo can. The answer lands beside it
as `docs/research/answers/R18-answer-our-factory-internal-audit.md`.

⚠ **Every pass on the board runs here now, this one included** — an earlier draft claimed this was
the only launchable one, which was wrong: the `deep-research` skill replaces the paste loop for all
of them. `**Depends on:** R17` keeps this button disabled until R17 is answered; running it first
does not fail, it quietly produces a worse answer.

⛔ **`STRUCTURE_CRITIQUE` means independence risk HIGH, and the run is BLIND-FIRST.** This pass reads
our own code, so it is pulled toward agreeing with us. Form a view from the primary source before
reading what we concluded about it — and take the mandatory web lane, or this is a bubble.

## Run log

| Run | Date | Outcome |
|---|---|---|
| — | — | not yet dispatched |

## ⭐ Why the pack is gone

R8 shipped a **481 KB evidence pack** — R1–R7 answers, `architecture-v0.md`,
`terminal-configuration.md`, seven `factory/*.py` modules, and the corrections ledger from all four
worktrees — because a web researcher cannot read a repository. It was well built and it did not
work: run 2 filed an answer containing **zero** file paths and **zero** line references, against a
pack whose own rule was *"every internal claim you make must cite a file and a line from this
pack."*

**Every file in that pack is already on disk here.** So there is no pack, and no upload. Read the
sources directly. `scripts/build_r8_pack.py` still names them if a manifest is wanted — but its
output is now redundant for this pass, which is the honest verdict on it.

⭐ **The division that makes this work:** a pack should carry what an agent **cannot discover by
grepping** — prior decisions, ticket history, the reasons behind a shape. It should not try to carry
the code, because enumerating "code it might need" is enumerating the repo. An agent in a worktree
reads code directly.

## Order

**R17 first, this second.** R17 surveys the field with no access to us; this checks its
recommendations against what we actually built. Running this first is possible but wastes the
comparison — the interesting output is *where the field's answer and our code disagree*.

⚠ **R17's answer is a hypothesis, not a finding.** Same standing rule this estate applies to a
ticket, a boot prompt or a handoff. Where R17 and the code disagree, **the code wins and the
disagreement is a finding we want reported.**

---

## 1. The deliverable

Every internal claim carries `path:line`. A claim without one is an opinion — label it. Where
something cannot be established from the repo, say `NOT-DETERMINABLE` and name what would settle it.
A named gap is worth more than a filled one.

### 1.1 Audit R17's recommendations against our code

For each load-bearing recommendation in R17's claims table, one row:

| R17 row | Recommendation | Our state, with `path:line` | Verdict |
|---|---|---|---|

Verdicts: `ALREADY-BUILT` · `BUILDABLE` · `BLOCKED` (name the blocker) · `WRONG-FOR-US` (say why,
with the code that makes it wrong) · `NOT-DETERMINABLE`.

⛔ **`WRONG-FOR-US` needs code, not preference.** "We would rather not" is not a verdict; "this
assumes Prefect primitives our build plane does not have, see `orchestrator/pipelines.py`" is.

### 1.2 The isolation ladder — is `architecture-v0.md` right?

`docs/specs/architecture-v0.md` is an explicit strawman written to be attacked. Its central claim:

> **An agent's isolation tier is chosen by what its task touches, not by what kind of agent it is** —
> T0 worktree (files only, no egress, no DB verbs) · T1 container + egress allowlist + read-only
> warehouse role · T2 container + an **ephemeral zero-copy clone schema** where full DDL is
> permitted and thrown away.

It names its own two most likely failures (§7): clone economics, and "data work does not conflict"
being asserted rather than measured. R17 §1.3 answers both from outside. **Your job is what that
means for our conflict graph specifically.**

1. `factory/lanes.py` computes the 3-lane ceiling. **Is `max independent set = 3` genuinely a
   file-conflict property?** Read `conflicts()` and `_touch_set()` and say what the edges actually
   encode — then say what edges a *data* lane would add, and whether the graph shrinks, grows, or
   changes shape.
2. `factory/worktrees.py` is the isolation that exists. **What host state stays shared across
   lanes?** F53 already names one leak (`~/.claude/skills/` is global, so an edit there is instantly
   visible to every lane). Enumerate the rest. This is the answer to "what breaks first if we scale
   to remote sandboxes."
3. Is the ladder's tier assignment **enforceable** with what we have, or only declarable? A tier an
   agent can exceed is a prompt, not a control.

### 1.3 Current vs recommended — the table R8 was asked for and never delivered grounded

Across at least: isolation unit · concurrency ceiling · scheduling · communication · failure
handling · evaluation · cost control · credential boundary · data blast radius · observability.

Every "current" cell cites `path:line`. Every "recommended" cell cites an R17 row number.

Then answer the uncomfortable one honestly: **is worktree-on-one-machine a stepping stone or a dead
end?** It gave us zero cross-lane conflicts and caps at three agents on one laptop.

### 1.4 Sequence the migration

**Smallest change with the largest effect first**, and — equally important — **what must NOT be
built yet**, with the reason. `docs/specs/architecture-v0.md` §8 has a proposed sequence; treat it
as a hypothesis and rewrite it, do not ratify it.

⚠ Cross-check against the live board before recommending anything: `python -m factory.launch` splits
the question into *may I run it watching* / *may I leave it* / *may I trust the output*, and a
migration step that does not move one of those three is decoration.

### 1.5 What the ledger already answered

`docs/findings.d/` and the three lane `findings.md` files carry corrections that were paid for.
Where a recommendation in R17 or in `architecture-v0.md` is already contradicted by a finding, say
so and cite the finding id. **Nobody should pay twice.**

---

## 2. Where to read

The manifest of what R8's pack carried, now read directly:

| Source | For |
|---|---|
| `docs/specs/architecture-v0.md` | the T0/T1/T2 ladder in full — the strawman under audit |
| `docs/specs/terminal-configuration.md` | the terminal/lane layout spec, and its open items |
| `factory/lanes.py` | the conflict graph. Verify the 3-lane ceiling is a *file* property |
| `factory/worktrees.py` | what isolation exists; what host state stays shared |
| `factory/claims.py` | lease semantics, staleness, crash behaviour |
| `factory/bus.py` | the live channel: delivery, ordering, persistence, failure |
| `factory/finish.py` | the close protocol: what evidence actually blocks release |
| `factory/readiness.py` | all 30 gates — meaningful, independent, enforceable, fail-open? |
| `factory/launch.py` | the run/leave/trust split, and what each level needs |
| `factory/runs.py` | the run ledger and per-lane measured cost |
| `docs/findings.d/`, `docs/findings.md` | corrections already paid for |
| `.worktrees/*/docs/findings.md` | the lane ledgers, including the ids that collide |
| `docs/research/answers/R1..R7,R10..R16` | what has already been decided and why |

Do not restrict yourself to this list — it is what the pack happened to carry, not a boundary.

## 3. Out of scope

- **The field survey.** R17 owns it. Do not re-derive what other people built.
- **Supervision UI.** R12, R13 and R14 own it and are answered.
- **Anything that requires a credential.** ⛔ **Ask before retrieving any secret**, name it and its
  source, and get an explicit yes. This audit should not need one; if it does, that is a finding.

## 4. Tier every claim

Same table shape as R17 §3, one row per load-bearing claim, and for internal claims the `Source`
column is `path:line`.

`OBSERVED` — you read the file or ran it · `REPORTED` — a finding, a prior answer, an evidence doc ·
`INFERRED` — your reasoning from the above · `NOT-DETERMINABLE` — and name what would settle it.

⛔ **An object named by a handoff, a boot prompt or a prior research answer is a hypothesis, not a
finding.** Walk the route yourself. R8's own history is the cautionary case: a research answer named
Prefect as the cause of the false-`succeeded` defect, the claim was carried into a second research
question as an entire section, and disproving it took one `grep`.
