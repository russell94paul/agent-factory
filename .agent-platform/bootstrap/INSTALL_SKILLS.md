# Install Bootstrap Skills into Claude Code

The pack can remain under `.agent-platform/bootstrap/`. Install only the skills useful to the current wave.

Example symlinks from the Agent Factory repo root:

```bash
mkdir -p .claude/skills
ln -s ../../.agent-platform/bootstrap/skills/bootstrap-commander .claude/skills/bootstrap-commander
ln -s ../../.agent-platform/bootstrap/skills/repo-context-compiler .claude/skills/repo-context-compiler
ln -s ../../.agent-platform/bootstrap/skills/claude-research-orchestrator .claude/skills/claude-research-orchestrator
ln -s ../../.agent-platform/bootstrap/skills/research-wave-runner .claude/skills/research-wave-runner
ln -s ../../.agent-platform/bootstrap/skills/research-synthesizer .claude/skills/research-synthesizer
ln -s ../../.agent-platform/bootstrap/skills/reference-implementation-miner .claude/skills/reference-implementation-miner
```

On Windows or environments where symlinks are inconvenient, copy the selected skill directories instead.

The research skills in this version prepare/ingest **Claude Research** jobs using the existing Claude subscription. They do not require a model API key.
