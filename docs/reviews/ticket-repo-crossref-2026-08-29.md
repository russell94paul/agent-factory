# Ticket ↔ repo cross-reference — what the tickets say vs what the code holds

**Run:** 2026-08-29, on `feat/readiness-generator` @ `8509a37`.
**Scope:** all 33 CIP tickets checked against the working tree. Every verdict cites a file:line.
**Why:** CIP-22 and CIP-33 were both rejected because *the thing already existed* — 2 of the 15
review-generated tickets, and nobody had checked the other 33.

**Result: 9 of 33 tickets are wrong about the repo.** Two are already built, one rests on a false
premise, one is infeasible as written, three need rescoping from *build* to *prove* or *finish*,
one will collide with an existing name, and two are ambiguous about which connector they mean.

**The base rate held.** It was 2 of 15 (13%). Checking the rest found 9 of 33 (27%).

---

## REJECT — already built (the CIP-22 class)

### CIP-23 · "Surface the `needs` field from `~/.claude/jobs/*/state.json`"
**Already built, including the part the spec calls hardest.**

- `factory/sessions.py:257` — `"needs": job.get("needs") or "", # the question nobody was reading`
- `factory/sessions.py:265` — sorts needs-first
- `factory/sessions.py:286` — `blocked()`, reading **from JOBS, not the session registry**, with the
  subtle bug already found *and fixed*: *"a question whose session had exited was filtered out of
  the one surface built to display it: on 2026-08-23, five agents were blocked and the Sessions tab
  showed two … a session-keyed inbox **systematically hides the questions that have been waiting
  longest**, which on that day were both credential requests."*
- The **intrusive** half exists too — `scripts/hooks/lane-attention.py` flashes the real
  WindowsTerminal window and marks the tab with a bell glyph, which is control-room §5 Slice 1's
  *"intrusive, not passive"* requirement.

⚠ **Do not close it — rescope it from BUILD to PROVE.** Slice 1's gate is *"a fire drill. Block a
real agent on a real question, and time how long until a human sees it. Before: unbounded (4 sat
all day). Target: under a minute."* **That drill has never been run** — no evidence file exists.
The mechanism is built and ungated. New title: *"Fire-drill the blocked-question inbox — mechanism
exists, latency unmeasured."*

### CIP-32 · "Denominate budgets in dollars, not tokens"
**Premise false — already dollars, and there is no token-denominated budget anywhere.**

- `factory/blueprint.py:27` — `budget_usd: float = 3.0`
- `factory/deploy.py:232` — passes `--max-budget-usd`
- `factory/deploy.py:4-7` — *"a turn cap and a **dollar cap** … Per-session — `--max-turns` and
  `--max-budget-usd`"*
- `grep -rn budget factory/*.py | grep -i token` → **no matches**

**REJECT in writing.** The only real work is that this dollar cap is enforced by code nothing
calls — which is **CIP-21** (*"Wire deploy.py budget enforcement into the live launch path"*).
**CIP-32 is subsumed by CIP-21; working it separately produces nothing.**

---

## REJECT — infeasible as written

### CIP-31 · "Enable strictAllowlist + mask from managed settings"
**Not a settings edit. Our own audit already established it cannot be done this way.**

`docs/research/answers/R18-answer-our-factory-internal-audit.md:95` graded exactly this action
**BLOCKED**, with the measurement:

> `~/.claude/settings.json` has … **no `sandbox`, `network` or `credentials` block**. And lanes are
> launched into **PowerShell on native Windows**, not WSL2 … **BLOCKED as the launcher is built** —
> R17's own B-15 ✓ says the sandbox is **unsupported on native Windows**. BUILDABLE only if lane
> launch moves into WSL2, which is a **rewrite of `_launch_script`**, not a settings edit.
> ⚠ **R17 assumed the box runs lanes in WSL2. It does not.**

The ticket was written from R17's recommendation without carrying R18's refutation of it. **This is
D-3's failure mode reproduced internally** — a downstream artifact inheriting an upstream claim
whose correction it never saw. Retitle to name the real cost, or reject: *"Move lane launch into
WSL2 (`_launch_script` rewrite) — prerequisite for any sandbox/allowlist work."*

---

## RESCOPE — real work, wrong description

### CIP-27 · "Make CONNECTORS resolution unconditional (fix F72)" — **half-fixed**
F72 recorded `readiness.py:33` as `FACTORY.parent / "prefect-connectors"` with no override. Today
`readiness.py:35-36` reads `os.environ.get("PREFECT_CONNECTORS", FACTORY.parent / "prefect-connectors")`
— **the env override landed; the cwd-relative default did not change.** So the defect F72 describes
(9 of 30 from the checkout, 10 of 30 from a worktree, same commit) still reproduces whenever the var
is unset. F72's `CHANGES` also asks that **the headline carry its basis**, which is a second,
unstarted piece. Restate as the two remaining halves, and note the interaction: the RED tests on
`trial/wave0-rescue` fail partly *because* `$PREFECT_CONNECTORS` points at a path that does not exist.

### CIP-25 · "Fix `finish.checks()` dead ledger check — per-lane NOTHING TO REPORT" — **valid, now precise**
Confirmed at `factory/finish.py:88-92`: `if not entries and _findings.nothing_to_report() == 0:`.
`entries` is per-lane, but `nothing_to_report()` is a **global count** — so **one** NOTHING TO
REPORT written by **any** lane permanently satisfies the check for **every** lane. Keep; the ticket
can now carry the line and the exact failure.

### CIP-29 · "Introduce `Snapshot` as the measurement scope object" — **name collision**
`factory/schedule.py:59` **already defines `class Snapshot`** — a frozen dataclass
(`when/passed/total/sha`) parsed out of the artifact's git history for schedule projection. It is
not a measurement-scope object and nothing outside `schedule.py` uses it. The ticket is **not**
already done, but whoever picks it up will collide. Say so in the ticket, and pick the other name.

---

## AMBIGUOUS — will be worked wrongly as written

### CIP-05 · "Certify that connector A1–A12 against a recorded run"
### CIP-06 · "Add the recorded run to `evals/corpus` + MANIFEST"
**Both are already true for `windsorai`/CLIENT-A**, verified this session:
`evals/corpus/windsorai-2026-08-20.json` exists, is listed in `evals/MANIFEST.sha256` under hash
`f7cd15c2d379…`, and `python -m factory.certify blueprints/windsorai_client_a.yaml --calibrate`
returns A1–A12 PASS scored against that exact hash.

But P1's whole point is the **pilot** connector, and **CIP-03 (pick the pilot) is still open**. So
each ticket reads two ways — *"done"* against windsorai, *"blocked on CIP-03"* against the pilot —
and nothing in the title says which. **Someone will close them by pointing at windsorai.** Say
"for the pilot connector chosen in CIP-03", and record windsorai explicitly as the **worked
example** these must reproduce.

---

## CONFIRMED NOT STARTED — keep as written

| Ticket | Evidence |
|---|---|
| CIP-02 GAPS.md | no `docs/corpus/` directory at all |
| CIP-21 wire deploy budget | `RepoDeployer` has no caller outside `tests/test_retry_context.py` |
| CIP-24 assert `CLAUDE_CODE_SESSION_NAME` | only `sessions.py:99` (a comment) and `local_tracker.py:345` (sets it in the generated `.ps1`); **no test asserts it** — matches control-room Slice 0 and deepseek D5 |
| CIP-26 tenancy-verified gate | `factory/board.py:49` — *"The missing gate is real, not a tidy-up: `tenancy-verified`, depending on `certified`"*. (A12 in `certify` is a different instrument — do not confuse them.) |
| CIP-28 move evidence packs | 4 packs in `docs/research/`, no `.packs/` |
| CIP-30 `tier` on AgentSpec | no `tier` in `blueprint.py` |
| CIP-34 FACPR | no `FACPR`/`first_attempt` in `metrics.py` |
| CIP-35 second connector | corpus holds one connector |

CIP-01, 03, 04, 07–20, 22, 33 not re-adjudicated here: 01/03/04 and 07–20 are forward design work
with nothing yet to contradict, and 22/33 are already rejected in writing.

---

## The pattern, and what it costs

Every one of the nine is the same shape: **a ticket written from a document rather than from the
code.** CIP-31 inherited R17's recommendation without R18's refutation. CIP-23 was written from
`sessions.py:112`'s comment — *"a `needs` field … that nothing reads"* — which is a **historical
note describing the problem the same file then solved 145 lines later**. CIP-32 was written from a
plan-level intent that the code had already satisfied.

That is D-3's failure mode — inheriting a claim without seeing its correction — occurring
**inside our own repo**, not in an external review. And it is why the estate's rule against
inheriting a premise from a handoff has to extend to tickets: **a ticket is a hypothesis about the
code, and 27% of these were wrong.**

**Cheapest durable fix:** every ticket carries the command that proves it is still needed. CIP-32's
would have been `grep -rn budget factory/*.py | grep -i token` — which returns nothing, and would
have killed the ticket the day it was written.
