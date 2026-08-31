# Agent Factory Kickoff Guide — Exact Steps

This is the shortest reliable path to start the autonomous bootstrap **without API billing**.

## Step 1 — Install the pack

From the Agent Factory repository root:

```bash
mkdir -p .agent-platform/bootstrap
```

Copy/unzip the contents of this pack into `.agent-platform/bootstrap/`.

Verify:

```text
.agent-platform/bootstrap/CLAUDE_KICKOFF_PROMPT.md
.agent-platform/bootstrap/START_CLAUDE_HERE.md
.agent-platform/bootstrap/ROADMAP_TO_VISION.md
.agent-platform/bootstrap/scripts/prepare_claude_research_wave.py
```

Do not reorganize the existing Agent Factory around the pack.

## Step 2 — Install the free local helper dependency

```bash
python -m pip install -r .agent-platform/bootstrap/scripts/requirements.txt
```

This installs PyYAML for reading the research-wave manifests. It makes no network/API calls.

**No OpenAI API key and no Anthropic API key are required for the active research workflow.**

## Step 3 — Start Claude Code from the Agent Factory root

```bash
claude
```

Use the first session as the Bootstrap Commander.

## Step 4 — Paste this exact kickoff message

```text
Read `.agent-platform/bootstrap/CLAUDE_KICKOFF_PROMPT.md` and `.agent-platform/bootstrap/START_CLAUDE_HERE.md` in full.

Treat START_CLAUDE_HERE.md as the authoritative bootstrap execution contract.

Begin now with repository recovery.

Important cost constraint: do not use OpenAI API, Anthropic API, or any metered research API. Use the Claude subscription workflow defined in `docs/CLAUDE_RESEARCH_WORKFLOW.md`.

Do not redesign Agent Factory from scratch.
Do not launch broad research before inspecting what already exists.
Do not start a large implementation wave yet.

Your first job is to:
1. recover the real repository architecture and capabilities;
2. create/update durable project state;
3. reconcile the existing Factory against the north-star roadmap;
4. identify KEEP / EXTEND / REFACTOR / MOVE / DELETE / RESEARCH;
5. classify unresolved research as repo-only, narrow Claude Code web search, or Claude Research;
6. compile any deep research into exact Claude Research packets and a prioritized queue;
7. determine which implementation/review tasks can safely execute in parallel;
8. construct the first evidence-gated research/build DAG;
9. show me the exact skills you intend to invoke;
10. show me the current Agent Army roadmap rank and next promotion criteria;
11. stop for my approval before a major build wave.

Do not ask me to manually rewrite or reconcile research. If Claude Research is needed, generate the exact prompt and return path; I will only trigger the Research run and return the raw report.

Proceed.
```

## Step 5 — Review Claude's first SITREP

Claude should return:

1. repository context recovered;
2. existing capabilities worth preserving;
3. largest gaps vs north star;
4. reference patterns worth testing;
5. research jobs that are actually needed;
6. which questions can use normal web search vs Claude Research;
7. exact Claude Research queue/packet plan;
8. execution/isolation plan;
9. skills to invoke;
10. first build DAG;
11. genuine human questions only;
12. current roadmap/rank + next evidence gate.

## Step 6 — Prepare the Claude Research queue

Claude should run something like:

```bash
python .agent-platform/bootstrap/scripts/prepare_claude_research_wave.py \
  .agent-platform/bootstrap/research/manifests/WAVE_0.yaml \
  --out .agent-platform/research
```

Then open:

```text
.agent-platform/research/RESEARCH_QUEUE.md
```

Do **not** blindly run every research prompt in the pack. Claude should prune and/or create a smaller manifest first based on the actual repo.

## Step 7 — Run Research jobs only when requested

For each job marked `READY_FOR_CLAUDE_RESEARCH`:

1. Open Claude.
2. Turn on **Research**.
3. Paste that job's `PROMPT.md` exactly.
4. Let Claude Research finish.
5. Save/copy the raw report into the exact `RAW_REPORT.md` path listed in the queue, or paste it to the Bootstrap Commander and tell it to save it there.
6. Send the coordinator: `research returned <research-id>`.

The coordinator should then run:

```bash
python .agent-platform/bootstrap/scripts/ingest_claude_research.py \
  --job-dir .agent-platform/research/queue/<research-id>
```

and invoke `research-synthesizer`.

This keeps the human step to **one launch + one raw return** per deep research job.

## Step 8 — Approve the build wave

After required research is synthesized, send:

```text
GO. Execute the approved bootstrap wave.

Use no metered model API for research. Continue using repository evidence, Claude Code web search for narrow questions, and the prepared Claude Research workflow for deep research.

Run independent implementation/review tasks in parallel using isolated worktrees/branches where safe. Persist project state, research artifacts, decisions, evidence, and task status after each task. Use deterministic gates for known checks.

Stop only at an explicit human approval gate, a credential/security boundary, a consequential architectural decision where evidence is genuinely inconclusive, a Claude Research job that I need to trigger, or an unrecoverable blocker.

Otherwise continue through the approved wave and return an after-action report covering what changed, what was proven, what failed, what was learned, what rank/capability was earned, and the recommended next wave.
```

## Step 9 — The intended operating rhythm

```text
You set direction
    ↓
Claude Code recovers state / compiles DAG
    ↓
repo evidence + narrow web research
    ↓
only high-value gaps enter Claude Research queue
    ↓
You trigger Research and return raw report
    ↓
Claude Code synthesizes automatically
    ↓
parallel build/review/test
    ↓
evidence + roadmap update
    ↓
next wave
```

As Agent Factory hardens, even the Research queue and cross-session handoff should become visible in the Session Console.
