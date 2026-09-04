# Artifacts + the real venture — boot prompt

**Written 2026-09-01 by the artifact session, at a context checkpoint (41% of 1M).**

⚠ **Every number below was measured when this was written and will have moved.** Multiple sessions
share this checkout. Re-measure `git rev-parse --abbrev-ref HEAD` and HEAD before any `git add`.

---

## `next:` — pick up the real venture, starting with RECON

Paul confirmed two things at the end of the last session:

1. **Audience for both artifacts is Paul himself.** Keep the repo internals; do not sanitise them into
   a client deck. A separate client-facing cut, if ever wanted, is a different artifact.
2. ⭐ **The venture in the Field Manual is real, not illustrative.** That changes the work: the
   six-topic picker should collapse to **one chosen topic**, and the RECON phase needs actual
   reconnaissance rather than a warning label.

**So the next session's first job is RECON on one topic — and RECON is allowed to return "no".**

Paul has not yet named the topic. Ask before building anything. The six on offer are in the Field
Manual's Venture mode; the two with the clearest buyers are `leads` (planning/permit filings →
installers) and `dataprod` (dashboard-as-a-service for owner-operators).

⛔ **RECON is a legal and technical feasibility question before it is a build question.** For the
`leads` topic specifically: portal terms of service, and UK GDPR/PECR for any outreach. Do not write
a scraper before that is answered in writing. The phase most likely to kill a venture is the one
people skip.

---

## STATE AT HANDOFF

```
branch    main
HEAD      ab13977          (unchanged by this session — nothing committed)
```

### ⛔ NOTHING FROM THIS SESSION IS COMMITTED

Paul's standing rule is to ask before committing. **Six untracked paths are mine and are waiting:**

```
?? docs/artifacts/agent-factory-atlas.html          157 KB  published
?? docs/artifacts/agent-factory-field-manual.html   102 KB  published
?? docs/evidence/atlas-2026-09-01/                  12 PNGs
?? docs/evidence/manual-2026-09-01/                 render evidence
?? scripts/atlas_render_check.py
?? scripts/manual_render_check.py
 M .impeccable/config.json                          removed a dead ignore I had added
```

⚠ **Other dirty paths in this checkout are NOT mine** — the modified
`docs/artifacts/client-review-navira.html`, the fourteen
`docs/evidence/client-review-readiness-2026-09-01/*` files, and the untracked `docs/release-gate/`
belong to concurrent sessions. **Do not stage with `git add .`.** Use
`git commit -F <msg> -- <explicit paths>`.

### Published artifacts (private by default; Paul shares if he wants to)

| | URL |
|---|---|
| Agent Factory Atlas | `https://claude.ai/code/artifact/b0fbae92-3531-48e3-8776-a35b597538d6` |
| Agent Factory Field Manual | `https://claude.ai/code/artifact/71ec1883-a64c-429e-b70c-cabb0e9d0bc5` |

Republishing the same file path from a session that published it keeps the URL. From any other
conversation, pass the URL as `url` or you will create a second artifact.

---

## MEASURED THIS SESSION — cite these, do not re-derive them casually

| Fact | Command |
|---|---|
| **PASS 13 · FAIL 12 · UNMEASURABLE 4 · NOT_RUN 1** of 30 gates, 542.4 s | `python -m factory.readiness` |
| 62 modules / 19,897 lines in `factory/` | `ls factory/*.py \| wc -l` · `cat factory/*.py \| wc -l` |
| 733 `def test_` across 48 files | `grep -rc "def test_" tests/*.py` |
| 34 findings · 253 task events · 10 run rows · 165 docs | `ls docs/findings.d/ \| wc -l` etc. |
| **0 Zeus references in Factory code** | `grep -rniE "zeus\|ccx\|opentribe\|cce_" factory/ scripts/ evaluator_service/` |
| Zeus Chat: **44 tools** | `grep -cE '^\s*name: "[a-z_]+"' src/tools/schemas.ts` *(in `zeus-chat-exp`)* |
| agent-army: 26 prompts, 3 answers, 27 NOT_RUN, **0 approved concepts** | `agent-army-research/research/` + `docs/agent-army/APPROVED_CONCEPTS.md` |

⚠ **The readiness board is cwd-dependent** — it reads differently from a linked worktree at the same
commit. State the cwd with any before/after claim.

---

## OPEN THREADS

### 1. The Net, as real code — and Paul asked about a hybrid

Paul's answer to "should the Net become real code?" was **"Could we use a hybrid? Wonder which would
perform best"**. The design answer given, and the one to build against:

**A hybrid is right, but the weak version is a mode toggle. The strong version is per-step
modality**, chosen by the shape of each question:

```
1 objective   open, unbounded            -> type
2 proof       open, domain-shaped        -> type + suggested contracts
3 boundary    closed, 4 options          -> chips
4 evidence    closed, multi-select       -> chips
5 budget      closed + numeric           -> chips + a number
6 gates       closed, multi-select       -> chips
7 doctrine    pre-filled from memory     -> confirm / reject only
8 muster      review                     -> card
```

Feed-vs-one-card density stays a *presentation* preference (expert vs client) and must never change
what is collected.

⛔ **"Which performs best" has not been measured and must not be asserted.** The three metrics to
record, all of which the existing ledger can hold: **time to sealed spec**, **fields left
`NOT_RECORDED`**, and ⭐ **correction rate** — how often a field is edited after sealing. The third is
the real one: a fast flow producing specs people immediately edit is worse than a slow one that does
not. Prior art (forms beat chat on enumerable fields; chat wins where the option space cannot be
shown) is a prior, not a finding.

Estimated size if built: ~400 lines against `TaskStore` + `blueprints/*.yaml`. It would be **the
first surface in this repo that writes a spec rather than reading one**.

### 2. The Mesh — the small first step, which stands alone

The full three-layer design is in the Field Manual's Mesh mode and in the wiki. **Do not build a
mesh.** The step that is worth doing regardless:

> Give every finding in `docs/findings.d/` a **typed identity and a machine-readable scope** — what
> class of work it applies to, what basis it carries, what the discriminating test was. Today they
> are Markdown with four conventional fields.

That turns the existing ledger into something an index can rank and a mesh can page, and it is useful
with no mesh at all — which is the test every first step should pass. It also directly addresses F86,
where a parser silently dropped eight findings and no lane was ever told.

### 3. Held back on purpose — the Sandtable

A rehearsal surface (run three candidate compositions against a recorded scenario, compare cost,
quality and human interventions) is the most attractive idea in the set and is **two gates away, not
one**: it needs the optimizer, which needs a corpus that can tell two configurations apart, which
needs the ten dark contract assertions wired. Building it now would produce a confident comparison of
configurations nothing can score — the 965-run loop with better graphics. **Do not start it.**

---

## GOTCHAS EARNED, THAT WILL COST YOU TIME OTHERWISE

⭐ **`display:none` on a CSS grid item removes it from the grid entirely.** Hiding a 196px rail made
the content pane slide into the 196px track and render at 196px wide. **Collapse the track**
(`grid-template-columns: minmax(0,1fr)` via a class on the container), never the item.

⭐ **`[hidden]` loses to `.rail{display:flex}`.** The published Artifact wrapper adds
`[hidden]{display:none!important}`; a local `file://` render does not. Write the explicit
`.thing[hidden]{display:none}` rule and never rely on the wrapper.

⚠ **A render probe is only as honest as the half it did not supply itself.** Two of this session's
"defects" were the instrument: it measured a *hidden* view's zero-size rects as broken nodes, and
flagged SVG internals inside an `overflow:hidden` canvas as page-level overflow. Both are now scoped
in `scripts/*_render_check.py`. Same family as the two errors already recorded against
`scripts/render_pass.py`.

⛔ **A background `python -c ... > "$TMPDIR/f.json"` in Git Bash writes to an MSYS path
(`/tmp/f.json` → `C:\Users\...\AppData\Local\Temp\f.json`) that Python cannot then open by the MSYS
name.** Worse, the task-completion notification reported **exit 0 over a zero-byte task output file**,
which reads exactly like a run that produced nothing. Resolve the path with `cygpath -w` before
handing it to Python.

⚠ **`impeccable`'s `hook-admin.mjs ignore-value` did not suppress its own hook** for
`layout-transition` / `transition: width`. Fixing the page at source (`transform: scaleX()`) was
better than fighting the suppression, and the dead ignore was then removed from
`.impeccable/config.json` — a standing ignore for a condition that no longer exists will mask a
genuine future hit.

⚠ **`readiness.measure()` is 542.4 s cold.** Kick it off in the background at the start of a session
if you will need the number, and never put it behind a page refresh.

---

## WHAT IS NOT DONE

- **Nothing is committed in this repo.** Six paths are untracked and one is modified.
- **Nothing is pushed.** The publication boundary work (`AF-RELEASE-GATE-01`, task `52407de5`) is
  owned by another session and is still open. **Neither artifact has been classified against it.**
  They contain no client data and no credentials, but that is a judgement, not a classification, and
  the classification is that task's job.
- **No Jira ticket exists or was created.** The repo's own `ticket` readiness gate reads
  `PASS · NONE-BY-DECISION`.
- **The venture topic is unchosen and RECON has not started.** This is the `next:` item.
- **The Net is a demo, not a mechanism.** It writes no `TaskStore` record and no blueprint.
- **No performance claim about any UI modality has been measured.** The three metrics above are
  proposed, not collected.
