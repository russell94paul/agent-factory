# R6: Automation and Alerts for Parallel Agent Sessions

## 1. Automated Regression Checks  

**Recommendation (Observed):** Run periodic (e.g. nightly) full test suites and diff the 30 gates against the last good state. In practice, teams use “scheduled pipelines” or cron jobs to do exactly this. For a private Windows‐only repo, a Task Scheduler job can run `pytest` nightly and compare outputs to the last commit. This will catch any gate switching from PASS→FAIL without relying on developers noticing.  

- *What it catches:* Any regression in tests or gate logic (including subtle errors agents introduce) that persists into the next day.  
- *What it cannot catch:* A broken gate that is immediately fixed by a subsequent commit (the diff might never show a failure window). Also, very fast break/fix cycles between runs can slip through.  
- *How to test it:* Intentionally break a gate (e.g. introduce an assertion failure) in one agent session, skip the fix, then wait for the scheduled run. The job should report the diff and trigger our alert mechanism (e.g. email or bot comment).  

**Recommendation (Observed):** Add a **pre-push hook** that runs the tests (at least a quick subset) before any `git push`. Developers (or agent scripts) can’t push code that fails these checks. This mirrors human workflows: if a shared branch sees failing tests, devs often enforce local checks first. A pre-push hook is easy to set up and will at least stop the *easiest* cases of regressions from reaching the repo.  

- *What it catches:* Simple mistakes that break tests or gates on the *next* commit. It prevents “obvious” failures from propagating.  
- *What it cannot catch:* Hooks run on the local machine only. Agents could bypass them (e.g. by using `--no-verify`) or push from environments without the hook installed. It also slows down each push, which may frustrate fast iteration (Doc Brown warns that long-running checks on push can hamper flow).  
- *How to test it:* Install the hook and try to push a commit with a failing test. The push should be rejected. (Use `git push --no-verify` to confirm the hook can be bypassed in a real break, and ensure we do alert instead of silently accepting it.)  

**Recommendation (Extrapolated):** Introduce lightweight *“fast”* checks on push and slow checks on schedule. For example, split validations into quick lint/generation checks in the hook and full pytest nightly. This follows best practice: quick feedback early, heavy checks later.  

- *What it catches:* Quick failures (syntax, lint) on push; in-depth regressions on schedule.  
- *What it cannot catch:* Any check that’s too slow for a hook might be missed until nightly, and the nightly job has the same limitations as above.  

**Recommendations to *defer or avoid*:** A full CI on every push (e.g. GitHub Actions) would be ideal, but “no runner budget” means we cannot rely on cloud CI here. Given private repos and no runner, spinning up a full CI pipeline is not feasible. Similarly, a noisy bot that tries to comment on every build might be ignored — we must prioritize something that will actually *fire*. Instead of many un-watched checks, prefer one reliable scheduled job.

## 2. Attribution of Regressions  

**Context:** Once a regression (PASS→FAIL) is detected, we must blame the correct change. With multiple sessions pushing in one branch, “last commit” is not enough. We need finer attribution.  

**Recommendation (Extrapolated):** Use **per-commit testing or `git bisect`** to pinpoint the culprit. A standard approach is to roll back to the last known good state and run a binary search with tests (the classic `git bisect` workflow). In our setting, this could be automated: when a gate flips, run a bisect script that tests each commit in the affected range.  

- *What it catches:* The exact commit (within the merged history) that first broke the gate.  
- *What it cannot catch:* If multiple commits from different sessions interleave, the bisect assumes a linear history. It might label as “good” a merge commit that mixed two sessions. Complex merges or rebases can confuse it. Also, bisect can be time-consuming if the history is long.  
- *How to test it:* Create a short sequence of commits on main where only one introduces a failing gate. Run `git bisect` pointing at a good commit and the failing HEAD, with a script that checks the gate. The script should mark the known-bad commit on the first try.  

**Recommendation (Observed):** Adopt a **branch-per-lane/worktree-per-agent** strategy. Give each agent session its own branch (and worktree) and merge them one at a time into the main branch. This isolates changes: when a merge triggers a failure, you know *which branch* caused it. MindStudio notes that “each agent gets its own branch and its own directory… No file conflicts, no state bleed”.  

- *What it catches:* Now regressions can be attributed to a branch/agent rather than a single commit in a tangled history. If Branch A merge breaks a gate, blame that branch’s changes.  
- *What it cannot catch:* If an agent’s branch itself has multiple commits and only their combination breaks a gate, you still need to bisect *within* that branch. Also, this requires a workflow change (agents must not push directly to main).  
- *How to test it:* Simulate two branches merging: create branch **A** with a fix, branch **B** that introduces a bug. Merge A into main (no failure), then merge B (gate fails). Confirm we correctly attribute failure to branch B’s merge.  

**Recommendation (Extrapolated):** Label “gate health” on PRs or merge actions. For example, require a CI pass summary as part of the merge commit. Then a bot or grep can tag which PR introduced the failure. This is less common in practice but mirrors human branch-protection: annotate merges with test status.  

- *What it catches:* It ties a failure to the merge event (thus to the PR/branch), which is often sufficient.  
- *What it cannot catch:* If multiple PRs merged together (squash merges or batches), it may misattribute.  

## 3. Agent Session Liveness  

**Recommendation (Observed): Heartbeat + Progress Monitoring.** Don’t rely solely on heartbeats – track *progress markers*. AI agent monitoring guides emphasize that “alive” ≠ “working”. In practice, each agent should emit a heartbeat (timestamp) and we should also log an unforgeable “progress” signal (e.g. commit made, task completed, or an append-only log entry). The strategy is: treat missing *progress* as the true stall indicator, not just missing heartbeat.  

- *What it catches:* A session stuck in a silent loop (e.g. polling/waiting) will stop advancing its progress marker. We can then alert that *specific* session (since we track session IDs). Heartbeat alone would have falsely reported “all good”.  
- *What it cannot catch:* A session actively consuming tokens or generating output (even garbage) will advance progress and look “healthy” by this metric, even if the output is wrong quality. (Quality monitoring is a separate concern.) Very short-lived stalls (below threshold) will also slip through.  
- *How to test it:* Simulate a hung session: have an agent enter a no-op loop and still emit heartbeats. Ensure our monitor flags it. The StackOverflow blueprint shows that an agent emitting heartbeats but no output stays green under liveness-only monitoring, whereas a progress check would flag it. We can hard-code a long sleep and verify our monitor notices the missing progress.  

**Implementation Notes:** Use a watchdog timer on each session ID. Each session reports (or is observed) at least one **progress event** per N minutes (threshold tuned to expected task durations). If no progress arrives in 2×N, trigger an alert. This follows the “heartbeat liveness interval” pattern: e.g. missing two heartbeats ⇒ restart, but here with progress as the heartbeat equivalent.  

## 4. Alerts vs Dashboard  

We must balance “urgent notifications” against “checkable status board”. In small teams, *too many alerts are ignored*. Best practice (from SRE/DevOps) is to alert only on **serious, actionable events**.  

- **Critical alerts:** E.g. “session crashed or wedged > threshold”, or “regression detected and unresolved for X minutes”. These should send a push notification (email or chat) to the lead developer.  
- **Non-critical signals:** Smaller issues (minor gate dips, low-level warnings) belong on a **dashboard or status board** where someone periodically refreshes. For example, commit counts or open findings can be tracked on the readiness board rather than alerting immediately. This avoids alert fatigue.  

A good rule: apply *severity tuning*. As Netdata advises, “tune your alert rules so only serious problems… trigger alarms”. In our case: missing a heartbeat (session hang) or failing a gate with no quick fix merits an active alert. Slight coverage drops or cosmetic generator warnings could wait to be seen on the web dashboard.  

We must also consider **alert fatigue**: many false alarms will be ignored. Keep alerts for when *action is required now*. All other signals should be surfaced in the human-refreshable board (or in a summary comment). For instance, we could have an hourly bot post a summary of gate changes to a team chat, rather than every tiny event. Only if a gate fails twice in a row or stays failed beyond a window do we send a “break” alert.  

## 5. Prior Art: Multi-Agent Dev Practices  

**Parallel human Dev:** Classic practices (CI, PR reviews, protected branches, merge queues) remain valid. We should borrow them where possible: use separate branches for independent work, require reviews or checks on merge, etc. These are *observed* effective methods in human teams and directly transferable.  

**Where it breaks (New challenges):** AI agents differ: they can create large changes fast and confidently (including wrong code). False positives (spurious findings) are common. We have already seen agents “report everything” and even rubber-stamp changes. As Heym’s analysis of AI code review notes, a single model tends to over-report and needs adversarial checks. In short, agents introduce noise that human processes did not face.  

**Agent-specific strategies (Observed):** Some teams have begun multi-agent-specific workflows. For example, Anthropic’s Claude Code and tools like Heym employ *multiple AI reviewers* on each change. The pattern is “not one big model but several agents”. One agent proposes issues, another challenges them, and an arbiter decides (an *adversarial review* setup). This mirrors how human teams debate code. It’s an observed pattern in tools shipping in 2025–26. We should consider a similar approach: e.g. have two agents independently run the gate tests or review results, and only alert if both agree there’s a regression.  

**Agent-specific strategies (Proposed):** Several academic and community frameworks suggest best practices. For instance, the *Claude Code worktrees* approach uses a branch per agent/session to avoid interference. Others propose structured orchestrators (OpenClaw, Lobster) that encode dependencies, handoffs, and approvals into the workflow. These ensure that one agent’s output becomes another’s input in a controlled way. However, such systems are still emerging; there’s no single standard yet.  

**Summary:** We can leverage classic DevOps ideas (branch/isolation, CI, code review) but must adapt them for agents. Multi-agent code review is an observed best practice now. Some recommended practices (like per-agent worktrees or structured pipelines) come from recent AI-Dev tooling, and are mainly *extrapolated* from early reports. In general, it’s a new field: we should be ready to iterate on policies as we learn from experience.  

## 6. Enforcing Pre-Close Checks  

Today the session’s prompt *asks* agents to run tests, checks, reviews, and write a findings entry before closing. To make this reliable, we should *enforce* it rather than rely on memory.  

**Recommendation (Observed):** Use a task-tracker that **requires evidence on close**. For example, the “Beads” system used by TrilogyAI forces every `close` operation to include a reason/proof string. In their words: `bd close <id> --reason "..."` *“requires a reason string – the agent’s proof of work. No silent ‘done’ without evidence.”*. Analogously, our `close_lane` command should verify all checks have passed (tests, etc.) and record the results. If any step is missing, it refuses to close.  

- *What it catches:* Attempts by an agent to mark the lane done without actually doing the work. Since the close command is authorized by our orchestrator, the agent cannot bypass it without manual intervention. It guarantees that “closing” really means all checks passed.  
- *What it cannot catch:* Clever agents might try to trick the checker by e.g. generating fake test outputs. We must validate signatures or timestamps. Also, if the `close_lane` itself is too slow or cumbersome, agents may write a mini script to fake a quick exit. One defense is to make skipping checks expensive (e.g. require solving a puzzle or human approval if the agent tries to skip).  

**Implementation Notes:** Integrate these checks into the agent’s command interface. For example, the orchestrator runs `close_lane` at the end of a session: it executes `pytest`, `nbstripout --check`, runs the generator with `--check`, and ensures an entry in `docs/findings.md`. Any failure aborts the close. This follows the “preflight” pattern. It’s stronger than just asking, because a session *cannot* produce a “done” event without successfully running this command.  

**Caveat:** Agents tend to satisficing (cut corners). To avoid making the gate hated, the checks must be as fast and reliable as possible (e.g. use cached test runs, avoid overly pedantic linting). Also, logging clear error messages when a step fails can help agents (and human overseers) fix issues rather than give up.  

## 7. Open Questions and Gaps  

We have good answers for most parts above, but some areas lack concrete evidence: 

- **Push alerts vs dashboard**: We drew on general monitoring best practices, but there’s little AI-specific guidance on how exactly to set thresholds. We assume “only alert on things that require immediate action” is correct, but the exact cutoff (how long a session must stall, how many missing gates should trigger an alert, etc.) would need tuning.  
- **Formal multi-agent repo practices:** While we cited examples (Heym, mindstudio, OpenClaw), these are early experiences. We could not find any widely adopted “standards” for multi-agent code development. Most guidance is blog posts or academic prototypes. In other words, much of Q5’s advice is extrapolated from a few published accounts, not a consensus standard.  
- **Pre-close enforcement:** Aside from the Beads example, concrete tools are just emerging. It’s unclear how to gracefully recover if a `close_lane` fails (e.g. due to intermittent test flakiness). Do we allow override? This remains a policy question.  

Overall, our plan is an **ordered shortlist**: first implement the nightly/scheduled regression check (with alerts), then add a pre-push hook for fast feedback, then institute branch-based worktrees for isolation. If regressions still slip through, add finer-grained blame tools (git bisect runs, or bots commenting on regressions). Throughout, use dashboards for visibility and reserve alerts for serious stalls or persistent breakages. Each measure can be tested by intentionally breaking its condition (e.g. simulate a hung agent or a failing gate) and verifying that our alert or block fires as designed. 

**Sources:** We draw on CI/CD and DevOps best practices, emerging AI agent monitoring literature, and reports on multi-agent coding workflows. Any novel claims without citation are marked as extrapolated from these sources or noted as assumptions. If any aspect remains uncertain or untested, we’ll treat it as a gap to revisit.