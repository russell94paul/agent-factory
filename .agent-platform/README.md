# `.agent-platform/` — an imported pack, and one map of where its ideas already live

**Installed 2026-08-31.** This directory holds an externally-generated bootstrap pack plus a single
reconciliation document. It is **not** a source of truth about this repository, and nothing in
`bootstrap/` describes running code.

## ⛔ The failure mode this README exists to prevent

`docs/agent-army/README.md` names it exactly:

> someone reads a well-written speculative architecture document, sees vocabulary they recognise,
> and builds on it as though it described the running system.

Everything under `bootstrap/` is that kind of document. It was written without access to this
repository. Where it describes a subsystem, treat the description as a **proposal from a stranger**,
never as a specification and never as evidence that the subsystem exists.

## What is here

| Path | What it is | Authority |
|---|---|---|
| `bootstrap/` | The imported pack, verbatim. 109 manifest files, unmodified. | **None.** Reference only. |
| `RECONCILIATION.md` | Written here, from measurement: every pack concept mapped to its existing home in this estate, with a disposition. | The only file here worth citing. |

Regenerate the install check with:

```bash
cd .agent-platform/bootstrap
grep -oP '(?<=^- `)[^`]+' PACK_MANIFEST.md | sort -u > /tmp/m.txt
find . -type f -not -name PACK_MANIFEST.md | sed 's|^\./||' | sort -u > /tmp/a.txt
comm -3 /tmp/m.txt /tmp/a.txt    # empty output = complete install
```

## What is deliberately NOT here

**No `PROJECT_STATE.yaml`.** The pack ships `bootstrap/PROJECT_STATE.template.yaml` and expects it
to be filled in. It has not been, and should not be. This estate already keeps that state, in
places that are read by code rather than by convention — see `RECONCILIATION.md` §2. A second state
file would be a hand-maintained mirror that rots silently, which is the defect family this
repository has recorded five times in eleven days.

**No `.agent-platform/research/` queue.** The pack's `scripts/prepare_claude_research_wave.py` would
generate one. Research in this estate lives in the sibling repo `agent-army-research`, under a
protocol with evidence tiers, a hypothesis ledger and a graduation rule
(`agent-army-research/repo-boundary/RESEARCH-VS-PRODUCT.md`). Running that script would create a
competing research system with weaker epistemics. It has not been run.

## The one hard constraint the pack gets right

No metered model API is required. `bootstrap/RELEASE_NOTES.md` records the removal of the OpenAI
Deep Research bridge, and no code path here reads `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`. Deep
research is a human-triggered Claude Research run; everything around the trigger is automated.
