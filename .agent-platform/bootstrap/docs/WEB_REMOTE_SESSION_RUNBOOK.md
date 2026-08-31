# Web / Remote Session Operations Runbook

**Purpose:** run the Agent Factory bootstrap with the least terminal babysitting while keeping local tools, MCP servers, credentials, and repository state available where they matter.

**Last checked against official Claude Code docs:** 2026-08-31.

## Recommended operating model

Use a **hybrid session topology** rather than forcing every task onto one surface.

```text
                           YOU
                            │
                    claude.ai/code / mobile
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
     LOCAL REMOTE-CONTROL POOL      CLOUD WEB SESSIONS
     (runs on your machine)         (Anthropic-managed VMs)
                │                       │
       local repo + MCP + tools       isolated branches
       local secrets/services         independent tasks
       Claude Research workflow         docs/refactors/tests
                │                       │
                └───────────┬───────────┘
                            ▼
                    BOOTSTRAP COMMANDER
                            │
                    synthesis / gates
                            │
                            ▼
                         Git / PR
```

### Default rule

- **Use Remote Control** for the coordinator, repo-context recovery, Claude Research queue/workflow, local Prefect/services, private local MCP servers, and anything that depends on your machine.
- **Use Claude Code on the web** for self-contained tasks that can run from a pushed GitHub branch in an isolated cloud VM.
- **Use isolated worktrees/branches** for parallel write tasks. Do not let several agents edit one working tree concurrently unless the work is provably non-overlapping.

## Option A — best fit for this bootstrap: Remote Control server mode

From the Agent Factory repo root:

```bash
claude remote-control \
  --spawn worktree \
  --capacity 8 \
  --sandbox \
  --remote-control-session-name-prefix agent-factory
```

Why this mode is useful:

- one terminal process stays alive as the local server;
- you interact from `claude.ai/code` or the Claude mobile app;
- sessions still execute on your machine;
- local filesystem, project settings, tools and MCP servers remain available;
- `--spawn worktree` gives each on-demand session a separate git worktree;
- `--capacity 8` gives a deliberately bounded local pool instead of an unbounded swarm;
- `--sandbox` provides filesystem/network isolation where compatible.

Claude Code's documented server-mode default capacity is higher; this pack intentionally recommends starting smaller and increasing only after observing CPU/RAM, model usage, git contention, and operator load.

### If you only need one session

Start a normal interactive local session that is also visible on the web:

```bash
claude --remote-control "Agent Factory Bootstrap"
```

Or, from an already-running Claude Code conversation:

```text
/remote-control Agent Factory Bootstrap
```

Alias:

```text
/rc Agent Factory Bootstrap
```

## Option B — true browser/cloud execution

Go directly to `claude.ai/code` and start a Claude Code web session against the GitHub repository, or create cloud sessions from the CLI:

```bash
claude --remote "Review the communication protocol spec and propose tests"
```

Multiple `--remote` calls create independent cloud sessions and can run concurrently. Monitor them on `claude.ai/code`, mobile, or with `/tasks` locally.

Cloud sessions are particularly useful for:

- isolated implementation tasks;
- documentation work;
- codebase exploration;
- independent review/evaluation;
- tasks that do not require your local environment.

## Important difference: Remote Control vs web cloud sessions

| Property | Remote Control | Claude Code on the web |
|---|---|---|
| Code executes | your machine | Anthropic-managed cloud VM |
| Browser/mobile UI | yes | yes |
| Local files/tools/MCP | yes | no, unless repo/cloud config supplies them |
| Survives browser closing | only while local Claude process remains running | yes |
| Parallel isolation | use `--spawn worktree` | each cloud task gets its own session/branch |
| Best for local secrets/services | yes | usually no |
| Best for hands-off independent tasks | good | excellent |

## Research recommendation

The active bootstrap uses **Claude Research on the operator's subscription**, not a paid model API.

Use repository evidence and Claude Code web search first. When deep research is justified, the local coordinator prepares an exact Claude Research packet under `.agent-platform/research/queue/`. The operator triggers the Research run in Claude and returns the raw report. Claude Code then ingests and synthesizes it.

Do not place model API credentials in cloud sessions because none are required for this research path.

## Suggested session names

Use mission-oriented names rather than generic terminal numbers:

```text
AF-COMMANDER
AF-RESEARCH-R25
AF-RESEARCH-ACIP
AF-COGNITION
AF-EVAL
AF-SESSION-UI
AF-REFERENCE-MINER
AF-REVIEW
```

## Keep the local coordinator alive

Remote Control runs locally. Closing the `claude` process ends that Remote Control server/session. Keep the host awake and connected while relying on it. Claude documents reconnection after normal interruptions, but extended outages can terminate the process.

For long tasks that truly need to continue with your laptop closed, use Claude Code web/cloud sessions instead.

## Mobile / web workflow

1. Start the Remote Control server once at the Agent Factory repo root.
2. Open `claude.ai/code` or the Claude mobile app.
3. Keep `AF-COMMANDER` as the control session.
4. Spawn separate worktree sessions for tasks that write code.
5. Let read-only research/reference-mining sessions run concurrently.
6. Route completed outputs to the Synthesis Inbox / research synthesizer.
7. Merge only after tests/evals and explicit gates.
8. End idle sessions rather than accumulating stale contexts.

## Useful current Claude Code features

- Remote Control server mode can spawn `same-dir`, `worktree`, or single `session` modes.
- The server supports a concurrency `--capacity` bound.
- `/config` can enable Remote Control automatically for interactive sessions.
- Claude Code on the web can run many independent tasks in parallel.
- `/tasks` monitors cloud sessions from the CLI.
- `/remote-env` selects a default cloud environment for `--remote` sessions.
- Cloud sessions expose `CLAUDE_CODE_REMOTE=true`, allowing hooks/scripts to behave differently in cloud execution.

## Sources

Official Anthropic / Claude Code documentation consulted:

- https://code.claude.com/docs/en/remote-control
- https://code.claude.com/docs/en/claude-code-on-the-web
- https://code.claude.com/docs/en/web-quickstart
- https://code.claude.com/docs/en/cli-usage

Treat specific CLI flags as version-sensitive. If Claude Code reports an unknown flag, run `claude --version` and consult the current CLI help/docs before changing architecture around it.
