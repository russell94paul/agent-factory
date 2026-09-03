### F101 — the instrument was fine; the output was cropped, and the conclusion was drawn from the remainder

Filed 2026-09-02 while clearing the Marketing Model blockers. **No system defect is described here.**
Every tool involved worked correctly and returned complete, accurate output. The wrong answer was
manufactured entirely in the reading, and it survived two rounds of being restated with confidence.

## What happened

The task was to find which Vercel project serves `navira-marketing-dashboard`, in order to read one
deployed environment variable. The listing command was correct:

```bash
vercel projects ls | tail -15
```

`vercel` sorts projects **newest-updated first**. `tail -15` therefore discarded the seven most
recently updated projects — including `navira-marketing-dashboard`, updated 13 hours earlier and
sitting fourth from the top. What survived the crop was a plausible near-miss, `navira-prototype`.

The reasoning then proceeded, out loud and explicitly:

> *"the repo is named `navira-marketing-dashboard`, which is a name match, not evidence. Let me find
> the deployed URL the evidence actually cites."*

No committed evidence named a URL. So a second justification was substituted — `navira-prototype`
holds a `NAVIRA_DEMO_PASSWORD`, which was called *"a content link, not the name match I refused to
rely on."* That is a **weaker** inference wearing the vocabulary of a stronger one: the variable
proves the project is a *Navira* thing, never that it is *this* application.

Two conclusions were then published from the wrong project's environment:

1. *"The deployed dashboard has no Snowflake credentials at all"* — because `navira-prototype` has
   three variables, none of them Snowflake.
2. *"the blocker's verdict was wrong … it is actually **NOT-SET** … serving synthetic data"* —
   presented as a discriminating correction, complete with a basis register separating what was
   `MEASURED` from what was `DERIVED`.

**Both were false.** `aldc/navira-marketing-dashboard` carries the full nine-variable Snowflake set
plus `DATA_SOURCE`, all encrypted. The original `NOT-VISIBLE` verdict had been right the whole time.

## What actually caught it

Not the reasoning, and not the basis register. A structural check:

```bash
find . -name "middleware.ts" -not -path "*/node_modules/*"   # nothing
find . -path "*login*" -name "*.tsx"                          # nothing
```

The deployed site returned `307 → /login`. The local repository has **no login page and no
middleware**. An application cannot redirect to a route it does not contain — so the deployed thing
and the local thing were different applications, and the identification collapsed.

⭐ **The discriminating test was about a mechanism, not a name or a value.** Names matched; a
variable name "linked"; only *"can this codebase emit that HTTP response"* could separate them.

## Why the basis register did not save it

This is the part worth keeping. The false conclusion was published **with** a correctly-formatted
basis register:

> MEASURED: the three-variable list and the default-provider test.
> DERIVED (one hop): the deployed page shows synthetic data.

Every word of that is true *about the wrong project*. **A basis register grades the inference from
the evidence to the claim. It does not grade whether the evidence is about the subject.** Target
identification sits upstream of every basis label, and a register applied to the wrong target
launders a wrong answer into a well-labelled one — which is worse than an unlabelled guess, because
it reads as diligence.

This is `C-PR-02` (*an inherited premise is a hypothesis, not a finding*) with the inheritance
removed: the premise was not inherited from a handoff, it was **self-generated one message earlier**
and then treated as settled.

## The rule

> **A verdict-bearing command's output is read in full, or the verdict is not drawn.**
> `head`, `tail` and `| head -n` are for surveying. The moment output is used to decide *which*
> object is the subject, the crop is part of the measurement — and a crop against an unknown sort
> order is an unmeasured filter.

Corollary, and the cheaper habit: **when a listing will be used to identify a target, sort it
yourself or print all of it.** `vercel projects ls` had 20 rows. The entire error came from paying
15 rows of attention to a 20-row problem.

## The second instance, same session, different shape

Recorded here because it is the same family and arrived within the hour:

```
Error: Process from config.webServer was not able to start. Exit code: 1
[exited with code 0]
```

The Playwright run was piped to `tail`. `[exited with code 0]` is the **pipeline's** status, not the
test's — the test never executed. `CLAUDE.md` already documents this shape for `&&`/`||` chains;
this is the same defect through a pipe, and the same rule covers it: the exit status of a chain is
not a measurement.

Had that been believed, a `NOT_RUN` would have been filed as a pass.

## What would have prevented both

- **The one-line habit:** before using a listing to pick a target, ask *what is this sorted by, and
  did I see all of it?* Both failures answer that question badly.
- ⛔ **Not more caution in the prose.** The wrong conclusion was already hedged, labelled and
  basis-registered. The register cannot see past the subject it was handed.

- **AFFECTS** — any pass that identifies a target from a listing: `vercel`/`az`/`gh` project and
  resource enumeration, `git branch`/`worktree list`, `ls` of an evidence directory, and every
  `| head`/`| tail` in a boot prompt or runbook whose output then names a thing to act on.
  Concretely, this session published two false conclusions about a client-facing deployment before a
  structural check retired them; nothing downstream had consumed them yet.

- **KIND** — PROCESS

- **STATUS** — OPEN
