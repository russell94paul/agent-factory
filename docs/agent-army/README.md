# Agent Army — the production-facing boundary

Agent Army research **no longer lives in this repository.** It lives in the sibling repository
`agent-army-research` (see [RESEARCH_REPO.md](RESEARCH_REPO.md)).

This directory is the boundary between the two. It holds four things and nothing else:

| File | Answers |
|---|---|
| [CURRENT_STATE.md](CURRENT_STATE.md) | What of Agent Army actually exists in this code — with file and line evidence |
| [APPROVED_CONCEPTS.md](APPROVED_CONCEPTS.md) | Which Agent Army concepts have been accepted for product development |
| [IMPLEMENTATION_HANDOFFS.md](IMPLEMENTATION_HANDOFFS.md) | Which research has formally graduated into implementation work |
| [RESEARCH_REPO.md](RESEARCH_REPO.md) | Where the research is, and which repository is authoritative about what |

## The one rule

> **Research does not imply implementation.**

A document in `agent-army-research` describing intent contracts, a staff mesh, doctrine, an
evolution chamber or a command world is a *hypothesis about what should exist*. It is not a
specification, not a commitment, and not evidence that anything was built.

The failure mode this directory exists to prevent is specific and cheap to fall into: someone
reads a well-written speculative architecture document, sees vocabulary they recognise, and
builds on it as though it described the running system. `CURRENT_STATE.md` is the antidote —
every `IMPLEMENTED` or `PARTIAL` claim in it carries a path and a line number you can open.

## Direction of travel

```text
agent-army-research                    agentic-factory
───────────────────                    ─────────────
research → synthesis → ADR
        → approved handoff  ──────────▶ implementation → tests → completion evidence
                            ◀────────── CURRENT_STATE.md keeps the research honest
```

Research reaches this repository **only** through an approved handoff in
`agent-army-research/implementation-handoffs/approved/`, logged in
[IMPLEMENTATION_HANDOFFS.md](IMPLEMENTATION_HANDOFFS.md). There is no other route, and in
particular a research document is never itself a ticket.

## What did not move

Documentation that describes *this* system stayed where it is, beside the code that reads it:

- `docs/research/` — this repository's own R1–R19 programme and `SYNTHESIS.md`. **It is imported.**
  `factory/dispatch.py` globs it for prompt ids at module scope, `factory/synthesis.py` reads
  `SYNTHESIS.md` and `answers/`, and `factory/readiness.py` gates on both. Moving it breaks the
  build. It is code that happens to be Markdown.
- `docs/specs/`, `docs/findings.d/`, `docs/artifacts/`, `docs/evidence/`, `docs/board/` — likewise
  read by `factory/readiness.py`, `factory/findings.py` and `factory/schedule.py`.
- `BRAIN-DUMP.md` — the verbatim recovered origin record of the R1–R19 programme. Its Agent Army
  fragments are *excerpted* into the research repo with line references; the original is intact.

Full pre-migration classification: `agent-army-research/migration/agent-factory-inventory-before.md`.
