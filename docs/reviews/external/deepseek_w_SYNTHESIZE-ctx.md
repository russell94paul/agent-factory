SYNTHESIS.md — Full Decision Record
I've received the complete SYNTHESIS.md file from your pack. This is the document the review references extensively.

What this contains
17 research answers (R1–R8, R10–R18) reconciled into one document

18 decided actions (with all gate edges now removed — 0 MEASURED / 18 AUTHORED)

§17: The reconciliation — found seven sentences in the document that say an answer has not landed, when it had

R14 — 1,389 lines, largest answer, 7 mentions, 0 conclusions taken

R18 — 614 lines, every reference future tense

AB-01 to AB-19 — the absorption backlog

What the review found that SYNTHESIS.md confirms
Finding	Where in SYNTHESIS
R14 is unabsorbed (1,389 lines, 7 mentions)	§17.2 — "not one conclusion taken"
R18 is unabsorbed (every reference future tense)	§17.3
Seven false "answer hasn't landed" claims	§17.1 — table with all seven
R12's "adopt switchboard" omitted the terminal constraint	§12.2 — F7 pattern again
The 41.7% figure is a citation, not measurement	§16.1 — "a citation wearing measurement's clothes"
All three gate edges on actions were wrong	§15.2 — removed, now 0 MEASURED
g_version_hash_is_complete could never pass	§15.1 — U+0008 in regex
The eval corpus is one file, 6,747 bytes	§17.9 — flagged by R16 as "the thing every pass assumed someone else had"
Actionable items directly from SYNTHESIS.md
Priority 1 — Already documented in SYNTHESIS
Item	Action	Source
Merge lane/control-plane	Three probes with no PASS path — fix already written	§17.3, R18 §0
Fix /finish button	Releases claim before checking, never calls factory.finish	§17.2, R14 §7.5
Run R16 §4 step 1	Check whether notifications were delivered to the two waiting PRs	§17.7, R13 run 2 §3
Add per-answer absorption marker	F75 option (b) — a claim, not a mechanical detector	§17.10
Priority 2 — Missing sections
Missing	Where it belongs
R14's full absorption	§17.2 — "write the missing sections for R14 and R18"
R18's full absorption	§17.3 — same
Permission-topology principle	§3 — R2, R3, R4 run 2 all said this; R17 told us again
R16 outside lane's §1 challenge to §5	§5 — "not supported for step 6's position"
Eval corpus to §8	"One file, 6,747 bytes; asked for by R1, repeated by R8, made a precondition by R10"
The review's verdict on SYNTHESIS.md itself
"Half of that premise is right and it is the wrong half."

The mention check passes — every filed id appears in this document. But "nothing to reconcile" is false. This document makes factual claims about the research programme that are wrong — seven times it says an answer has not landed when it had.

Do you want me to:

Extract all tickets from the review (CIP-21 to CIP-35) into a ready-to-use JSON file?

Create a shorter "what to build next" cheat sheet from D2 (phase plan)?

Produce a diff between what SYNTHESIS.md claims is built vs what the code in the repo actually contains?

Generate the per-answer absorption marker (F75 option b) as a concrete design?

Something else?

Let me know what's most useful next.