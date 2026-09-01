# Prompt pack — ⛔ DESIGN. None of these is wired to a dispatch path.

Ten prompts, one per role in the protocol. **Priority NEXT**, and only three of them
(`handoff-generator`, `handoff-receiver`, `post-task-aar`) are on the critical path once the
HandoffContract lands. The other seven are written so they are not re-derived.

Every prompt carries the same four blocks, in this order:

```
INPUT CONTRACT        named artifacts + a ContextPack. REFUSE TO START if a ref does not resolve.
OUTPUT CONTRACT       a HandoffContract v1. Nothing else counts as output.
STOP CONDITIONS       always includes: an assumption whose falsity changes the output;
                      a required credential; a WRITE outside the declared resource_claim.
EVIDENCE REQUIREMENTS which evidence classes must exist; which claims may be CONFIRMED.
```

⚠ **A prompt is not a skill.** These are role contracts for agents dispatched by the controller,
not `~/.claude/skills/` entries. They have no `description:` and will never self-trigger — that is
deliberate. See CLAUDE.md on the two-tier skill library before converting any of them.

⭐ **The rule shared by all ten:** an agent may never mark its own claim `CONFIRMED` without an
`evidence_ref`, and may never assign its own verdict. The verdict comes from a `GreenContract`.
