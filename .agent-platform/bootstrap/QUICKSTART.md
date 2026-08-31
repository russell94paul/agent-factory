# Quickstart — Claude Subscription Research, No API Billing

## 1. Put the pack inside Agent Factory

From the Agent Factory repo root:

```bash
mkdir -p .agent-platform/bootstrap
# unzip/copy this pack's contents into .agent-platform/bootstrap
```

Do not restructure the main repo yet.

## 2. Optional local helper dependency

The research-queue compiler uses PyYAML only; it makes **no API calls**.

```bash
python -m pip install -r .agent-platform/bootstrap/scripts/requirements.txt
```

There is no OpenAI or Anthropic API key to configure for the active workflow.

## 3. Start Claude Code from the Agent Factory root

Use the Claude subscription/Claude Code access you already have.

```bash
claude
```

Remote Control or Claude Code web sessions may still be used for parallel implementation, but the first coordinator should have access to the real repository.

## 4. Give the coordinator the kickoff prompt

Paste `.agent-platform/bootstrap/CLAUDE_KICKOFF_PROMPT.md` into the first Claude Code session.

Claude must inspect the repository before launching broad research.

## 5. Let Claude compile the research/build DAG

The coordinator should:

1. recover repository context;
2. remove questions already answered by repo evidence;
3. use narrow Claude Code web search where enough;
4. compile only deep unresolved questions into Claude Research packets;
5. create `.agent-platform/research/RESEARCH_QUEUE.md`;
6. allocate implementation/review work to isolated worktrees/sessions;
7. present the first gated DAG.

## 6. Run only the queued Claude Research jobs

For each job marked `READY_FOR_CLAUDE_RESEARCH`:

1. open Claude on web/desktop/mobile;
2. turn on **Research**;
3. paste the generated `PROMPT.md` exactly;
4. let Research finish;
5. return/save the raw report into the exact `RAW_REPORT.md` path named by the queue;
6. tell the Claude Code coordinator: `research returned <id>`.

Claude Code then checks and synthesizes the report. You do not manually summarize or reconcile it.

## 7. Approve the first build wave

After the required research is synthesized, Claude returns the executable build DAG and exact `GO` instruction.

The intended human role is now:

```text
approve direction
→ trigger prepared Research jobs when required
→ answer genuine judgment questions
→ review consequential gates
```

Everything else should increasingly move into Agent Factory.
