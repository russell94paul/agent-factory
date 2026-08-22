# Agent communication — the record, the channel, and why they are not the same thing

**Written 2026-08-22, from one day of three lanes running in parallel.** Every claim below is
something that happened, not something anticipated.

## What actually went wrong

`docs/findings.md` was the designated way one lane tells another something. It could not be:

- **It collided.** Three isolated worktrees each read `F10` as the last id and appended their own
  `F11` and `F12` — correctly, independently, incompatibly. A merge would have destroyed two of
  each ([[F70]]).
- **It arrived too late.** A fragment written on `lane/certify` is invisible to `lane/artifact`
  until both merge, which is after both have finished ([[F71]]).
- **Everything that arrived in time arrived out of band** — over a peer message, routed by a human
  who happened to notice. That is not a system.

One file was being asked to be a permanent, reviewed, mergeable archive *and* a live nudge between
running processes. Those have opposite requirements. Durability wants git; liveness wants a
mutable shared surface the lanes can see right now.

## The split

| | The RECORD | The CHANNEL |
|---|---|---|
| Where | `docs/findings.d/` | `.data/bus/` |
| In git | yes — reviewed, permanent | **no**, and that is correct |
| Lifetime | forever | dies with the lanes |
| Shape | one file per finding | one append-only file per writer |
| Answers | "what did we learn" | "what do you need to know NOW" |

Machine-local is a **property, not a compromise**: the lanes are processes on one machine and the
channel has no meaning outside that run. This is not the [[F53]] defect — nothing is *measured*
from the bus. Anything worth keeping is promoted by the lane that learned it into a finding, which
is in git and merges with the branch.

## Why one file per writer, again

Same reason `findings.d/` is a directory. Two lanes never write the same path, so the collision
that produced three `F11`s cannot recur. Readers hold their own cursor in
`.data/bus/.cursor-<lane>.json`. No locking, no shared mutable state, no merge.

## The read path is the load-bearing half

**A channel nobody reads is decoration** — the defect family this repo keeps meeting. Telling the
agent to poll `factory.bus` at checkpoints is exactly that: it works until the session that does
not bother, which is the session that most needed telling.

So delivery is a **hook**. `scripts/hooks/lane-bus.py` fires on tool use, and when another lane
has posted something unread it returns it as `additionalContext` — injected into the model's
context whether or not anyone thought to look. The cursor advances only after a successful emit,
so a crash re-delivers rather than drops. It is inert outside a lane worktree, silent when nothing
is pending, exits 0 on every error, and **never returns a permission decision**. It only adds text.

## The five kinds

Deliberately small. Every one of them happened on 2026-08-22 with no channel to carry it.

`correction` · your premise is wrong (durable version goes to `findings.d/`)
`claimed` · I am touching this area — the filesystem, not the dependency graph
`blocked` · I need a human; do not wait on me
`finished` · my brief is done and my branch is pushed
`note` · anything else worth a sibling's attention

## Finishing is a message

A lane finishing was the clearest gap: three lanes completed and **nothing happened** — claim held
for four hours, branch unpushed, nothing merged, nothing said. `factory/finish.py` does the five
mechanical steps and **refuses the sixth**:

1. **Assert** — clean tree, commits unique to the lane, a ledger entry or `NOTHING TO REPORT`.
2. **Push** — and if the push fails, *stop and keep the claim*. Losing the branch is the thing
   this exists to prevent, and a released claim tells the next session the lane is done.
3. **Announce** `finished` on the bus.
4. **Release** the claim.
5. **Never merge.** Merging is a judgement about whether the work is *right*; this module only
   knows whether it is *complete*. Only one of those is mechanical.

## What this does not solve

A lane still cannot ask another lane a question and get an answer — the bus is one-way
announcement, not dialogue. That was deliberate: every real question on 2026-08-22 needed a
*human* (a credential approval, a go/no-go), and building agent-to-agent request/response before
one is needed would be inventing a requirement. [[F71]] stays OPEN until a real case appears.
