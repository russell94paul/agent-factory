# Control-plane safety for autonomous data-engineering agents

## Executive verdict and graded prescription

The production measurements supplied for 21 August 2026 are enough to make the central decision without relying on the weaker prior review. **This system should not be optimised yet. It should first be made bounded, reapable, fail-closed and independently evaluable.** The [R] report about an in-memory retry counter is consistent with the observed failure mode, but it is not needed to reach that conclusion and I do not treat it as verified.

The most important [M] facts are not merely “poor reliability”: a 14.2% stage-attempt success rate; 1,004 uncapped restarts; one stage restarted 352 times; four runs ending at `stage_started` with no terminal event; three nominally completed runs containing 115, 21 and 15 stage failures; one orchestrator state disagreeing with its event log; one stage consuming 97.6% of a 95,098-second run in a retry loop; 22/22 gate approvals; and failed attempts being assigned zero recorded cost. Those observations show that **termination, correctness, resource ownership, retry budget, gate decisions and spend accounting are currently not trustworthy invariants**.

I use these classifications throughout:

**ESTABLISHED PRACTICE** means the underlying control pattern is well established in workflow/distributed systems. It does not mean adoption has been empirically proved to improve this company's reliability.

**VENDOR CAPABILITY / CLAIM** means current product documentation says a mechanism exists. That is not evidence that enabling it will solve the incident class.

**OPEN RESEARCH / LOCAL POLICY** means I found no credible published basis for claiming that the exact threshold, heuristic or design is standard for autonomous software-engineering agents.

### Grading the six prior recommendations

| Part B item | Grade | Classification | Verdict |
|---|---:|---|---|
| Four business terminal outcomes | **B+** | Local design built on established fail-closed principles | Keep the projection, but fix the semantics of `NEEDS_HUMAN`. Exactly four terminal business states is **not an industry standard**. |
| `EXECUTION_TERMINATED` distinct from `CONTRACT_PASS` | **A** | Established practice; vocabulary is local | Essential. Prefect explicitly allows a flow to be `COMPLETED` because it returned normally even when child work failed, depending on how the child state is handled. citeturn0search0turn0search2turn0search4 |
| Lease/heartbeat and orphan timeout | **A** | Established distributed-systems practice | Correct, but incomplete without an independent reaper, cloud-side timeout where available, cancellation propagation and restart reconciliation. Kubernetes' Lease/heartbeat and controller reconciliation models are useful examples of the established pattern. citeturn15search0turn15search1turn15search10 |
| External retry cap, initial three attempts, earlier identical-failure stop | **A- / B / C+**, respectively | Established / plausible / open-local | External ownership of the cap is A-level. Three total attempts is a defensible safety default, not validated for this workload. “Same failure” for an LLM software agent has no mature standard definition. |
| External concurrency limit and reserved capacity | **A** | Established practice | Correct and urgent given the documented 10-core quota incident. Azure itself exposes quotas/capacity limits; the control plane, rather than agents, must decide how much of that quota agents may consume. citeturn20search4turn20search17 |
| `producer_done != handoff_done` | **A** | Established producer/consumer correctness pattern; exact receipt design is local | Correct. Completion needs a downstream acceptance receipt bound to the exact producer output, not simply evidence that the producer exited. |

The four-state proposal needs one precise correction. Prefect and other orchestrators have richer operational state machines; Prefect, for example, distinguishes scheduled, pending, running, completed, failed, cancelled, crashed, paused and cancelling states. There is therefore no basis for saying that “four states” is standard. citeturn0search10 What is useful is a **small external business-outcome projection over a richer internal lifecycle**.

I would retain:

`SUCCEEDED | FAILED | NEEDS_HUMAN | CANCELLED`

but make these **immutable outcomes of a closed run**, not the complete runtime state machine. Internally you still need states such as `RESERVED`, `DISPATCHING`, `RUNNING`, `CANCEL_REQUESTED`, `REAPING` and `ORPHANED`.

`NEEDS_HUMAN` is the awkward one. If an operator can “resume” the same run from it, it is not terminal. There are only two clean choices:

* close the current run as `NEEDS_HUMAN` and, after intervention, create a new continuation run with `parent_run_id`; or
* model `PAUSED_FOR_HUMAN` as a non-terminal operational state and reserve `NEEDS_HUMAN` for runs that have actually been closed.

For auditability I prefer the first. A terminal row should never go back to `RUNNING`.

**The biggest missing control is scope/evidence closure.** The six prescriptions can still report success over work they never knew existed. Your successful outcome needs an independently established *expected-work manifest* before work begins. That manifest should be written by the trusted control plane, not the agent:

```json
{
  "tenant_id": "client-123",
  "scope_version": 7,
  "expected_source_account_ids": ["a1", "a2", "a3"],
  "expected_pipeline_stages": ["discover", "extract", "blob", "load", "verify", "publish"],
  "required_gate_ids": ["source_tenancy", "blob_handoff", "snowflake_load", "publish"],
  "required_target_objects": ["db.schema.table_a", "db.schema.table_b"],
  "data_window": ["2026-08-01", "2026-08-21"],
  "verifier_version": "sha256:...",
  "evaluator_bundle": "sha256:..."
}
```

`scope_hash = SHA256(canonical_json(manifest))` becomes immutable run metadata. `SUCCEEDED` is derived, never assigned ad hoc:

```text
SUCCEEDED :=
    execution_terminated
AND all_expected_work_items_have_terminal_receipts
AND observed_work_item_set == expected_work_item_set
AND every_required_contract_verdict == PASS
AND every_required_gate == ALLOW
AND every_required_handoff_receipt_matches_producer_sha256
AND no_unreconciled_cloud_resource_exists
AND no_tenancy_violation_exists
AND evaluator_bundle == pinned_bundle
```

If the authoritative source cannot tell you what the complete work set should have been, **completeness is unmeasurable and success must be unavailable**. There is no control-plane trick that can prove absence of unseen work when no independent source of scope exists. That is a genuine measurement limit, not an engineering bug.

I would add four more missing invariants: cloud-resource reconciliation before terminal closure; append-only durable transition evidence; tenant capability binding before dispatch; and an evaluator trust boundary. Those complete the previous prescription.

## Bounded execution and orphan reaping

### The persisted attempt and spend budget

**ESTABLISHED PRACTICE:** use a trusted compare-and-swap/transactional store and reserve resources *before* external side effects. Azure Table Storage supports optimistic concurrency with entity ETags, and its entity-group transactions provide atomic multi-entity operations when all entities share a partition key. Cosmos DB offers full ACID transactions/transactional batches within a logical partition, but it is unnecessary complexity here unless the control-plane workload grows materially. citeturn3search5turn3search2turn3search4turn3search0turn3search1

For a four-engineer company, I would implement this with **Azure Table Storage**, deliberately arranging active budget records for a region under one partition so that a dispatch reservation can be atomic.

Use:

```text
PartitionKey = "POOL#canadacentral"

RowKey = "POLICY#<policy-version>"
RowKey = "POOL"
RowKey = "RUN#<run-id>"
RowKey = "STAGE#<run-id>#<stage-id>"
RowKey = "ATTEMPT#<attempt-id>"
```

The policy record is written only by the trusted control-plane deployment identity. At run creation, copy the applicable immutable values into `RUN`, including:

```text
policy_version
max_run_attempts
max_run_cost_micro_usd
default_stage_attempt_cap
stage_specific_caps
max_stage_runtime_seconds
max_agent_vcpu_millis
max_llm_input_tokens
max_llm_output_tokens
scope_hash
```

Do **not** put authoritative caps in `pyproject.toml`, YAML in the agent repository, environment variables the agent can change, or Prefect parameters supplied by the agent. Repository configuration may request *less* than the policy maximum; the server policy remains authoritative.

Before **every dispatch**, the trusted dispatcher reads `POOL`, `RUN` and `STAGE`, calculates a worst-case reservation, and performs one Table entity-group transaction:

```text
IF-MATCH pool.etag
IF-MATCH run.etag
IF-MATCH stage.etag

assert stage.attempts_used < stage.attempt_cap
assert run.reserved_cost + new_reserve <= run.max_run_cost
assert pool.leased_vcpu_millis + requested_vcpu_millis <= pool.agent_vcpu_cap

UPDATE STAGE:
    attempts_used += 1

UPDATE RUN:
    reserved_cost_micro_usd += worst_case_reserve
    attempts_used += 1

UPDATE POOL:
    leased_vcpu_millis += requested_vcpu_millis

INSERT ATTEMPT:
    attempt_id
    attempt_no
    status = "RESERVED"
    reserved_cost_micro_usd
    requested_vcpu_millis
    lease_expires_at
    policy_version
    scope_hash
```

Any ETag mismatch or duplicate attempt-row insertion aborts the transaction. The caller rereads and tries the reservation again; **it does not launch first and reconcile the counter afterwards**. Azure Table's conditional ETag semantics and same-partition transaction support are exactly what make concurrent dispatchers safe here. citeturn3search5turn3search2turn3search4

The attempt ID then becomes the dispatch capability:

```text
attempt_id = UUIDv7(...)
dispatch_token = HMAC(control_plane_key, attempt_id || policy_version || expiry)
```

Only a successfully committed `RESERVED` attempt gets launched. If Table Storage is unavailable, dispatch fails closed. A storage outage is preferable to another overnight quota exhaustion.

Use integer quantities, not floating-point money. Better still, make **resource quantities the hard budget** and money a derived budget:

```text
compute reserve =
  max_runtime_seconds *
  (vCPU * current_vCPU_rate + GiB * current_memory_rate)

LLM reserve =
  max_input_tokens * input_rate
+ max_output_tokens * output_rate
```

Exact cloud-dollar ceilings are intrinsically weaker than resource ceilings because provider billing and some ancillary charges arrive after the fact. A hard limit on vCPU-seconds, GiB-seconds, elapsed execution seconds and model tokens is enforceable; the dollar conversion is an estimate until provider billing settles. Azure Container Apps and ACI both meter compute by duration/resource allocation, making these units suitable for reconstruction. citeturn15search2turn15search5turn20search6turn20search9

For LLM/API spend, a cap is only hard if the agent cannot bypass it. Put model credentials behind a small **budget proxy**. The agent gets an attempt-scoped bearer token; the proxy owns the actual provider credential, counts input/output tokens against the attempt reservation and refuses the next call when the remaining token budget is insufficient. Direct egress to the model provider using another secret must not exist.

At terminal reconciliation, unused reservations are released and actual measured usage is recorded. A reservation is not erased: the append-only attempt ledger remains.

### The bounded party must not own its limiter

This is the critical enforcement rule for an agent with shell access and repository write permission:

**the agent may propose a deployment; it must not possess the Azure capability that performs the deployment.**

The agent sandbox should therefore lack:

```text
Microsoft.App/jobs/write
Microsoft.App/jobs/.../start
Microsoft.ContainerInstance/containerGroups/write
Microsoft.Authorization/roleAssignments/write
budget-table write permission
control-policy write permission
evaluator-repository write permission
```

Instead:

```text
agent shell
    |
    | POST /dispatch {tenant, stage, artifact_sha, requested_resources}
    v
trusted control-plane API
    |
    | checks policy + tenancy + attempt/spend/concurrency transaction
    v
dispatcher managed identity
    |
    +--> Azure Container Apps Job / ACI
```

The same applies to infrastructure-as-code. Let the agent write Bicep/Terraform/code and produce a plan. A **trusted deployment runner** applies it after policy and tenancy gates. Giving an autonomous shell an Azure identity that can create arbitrary resources and then trying to protect a `max_attempts = 3` variable inside its repository is not an enforcement boundary.

Azure managed identities and RBAC support this separation: Container Apps can use system- or user-assigned identities, and RBAC can restrict those identities to specific resources/scopes. citeturn18search2turn18search5turn15search22

Concurrency should use the same reservation system. Do not set “10 because the regional quota is 10”. Define:

```text
agent_vcpu_cap = regional_quota - reserved_human_capacity - safety_margin
```

Given the documented incident exhausted a 10-core region, an initial local policy such as a 4-core autonomous pool and 6 cores reserved for operators is conservative and defensible, but **4/6 is a local safety choice, not published best practice**.

### Same-failure stopping

There is a useful distinction here.

**ESTABLISHED PRACTICE:** mature retry systems classify errors and retry only conditions believed transient. Azure's Retry pattern says failures expected to persist should fail fast and transient faults should use bounded retry policies; Google SRE similarly recommends limiting retries and using backoff/retry budgets rather than blindly retrying every error. citeturn4search3turn4search7turn4search2turn4search6

**OPEN RESEARCH:** there is no mature standard that tells an autonomous coding system whether two complex software-development failures are “the same failure”.

Implement a deterministic classifier rather than asking the agent whether it has made progress. Generate a versioned fingerprint from control-plane-observed evidence:

```python
failure_fingerprint = sha256(canonical_json({
    "classifier_version": 3,
    "error_family": "TEST_FAILURE",
    "http_status": None,
    "command": "pytest",
    "exit_code": 1,
    "failed_assertion_ids": sorted([...]),
    "failed_test_nodeids": sorted([...]),
    "stack_symbols": normalise_stack(...),
    "contract_failure_codes": sorted([...]),
}))
```

Strip volatile values such as timestamps, temporary paths, request IDs and random ports.

Keep a separate progress vector:

```text
contract_assertions_passed
contract_assertions_failed
required_tests_passed
required_tests_failed
accepted_handoff_count
output_manifest_sha256
git_tree_sha
```

A changed git tree is **not sufficient progress**: an agent can churn files indefinitely. Progress must ultimately be visible to the verifier or downstream acceptance contract.

My starting local rule would be:

```text
if deterministic_failure_fingerprint == previous_fingerprint
and verifier_progress_vector did not improve:
    repeated_same_failure += 1

if repeated_same_failure >= 2:
    stop stage
```

That “two identical failures” threshold is **LOCAL POLICY**, not established science.

Do not apply it mechanically to transient 429/5xx/network failures: those are classified separately and use provider-appropriate backoff/`Retry-After`.

### Is three attempts defensible?

Yes as a **starting hard ceiling**, but not as an empirically optimal value for autonomous connector migration.

Google SRE gives examples of bounding a request to three attempts and separately using retry budgets; AWS and Azure retry guidance similarly emphasise a small predetermined retry count, exponential backoff and failing fast for non-transient errors. Those are service/RPC precedents, not evidence that a coding agent should receive exactly three independent shots at modifying a repository. citeturn4search6turn4search4turn4search13

I would therefore encode error-specific policy from day one:

| Error family | Total stage attempts initially | Action |
|---|---:|---|
| Tenant mismatch, forbidden scope, policy violation | **1** | `NEEDS_HUMAN`/`FAILED`; never retry |
| Authentication/authorisation 401/403 | **1** | Credentials need repair, not another agent attempt |
| Deterministic contract/schema/compiler failure | **≤2** | Second attempt only if verifier-observed progress occurred |
| Agent-generated implementation/test failure | **3 hard maximum** | Stop at second identical no-progress fingerprint |
| 408/429/5xx/provisioning transient | **3** | Exponential backoff + jitter, honour provider guidance |
| Timeout | **2 at most** | Retry only after prior workload is positively killed |
| Orphan / unknown cloud state | **0 new attempt until reconciled** | Never overlap the replacement with an unresolved predecessor |

That is far preferable to trying to discover a single globally optimal retry count.

### Azure orphan reaping

The documented incident exposes a second independent budget: **workload lifetime**. A Prefect timeout is not a cloud kill.

For new autonomous stages, prefer **Azure Container Apps Jobs** over ACI. Microsoft documents Jobs as finite-duration container tasks. Jobs have `replicaTimeout` and `replicaRetryLimit`, and current REST APIs expose an explicit stop-execution operation. citeturn18search8turn2search10turn2search0turn1search15

Configure every agent job:

```text
replicaTimeout = policy.max_stage_runtime_seconds
replicaRetryLimit = 0
parallelism = 1
```

Set Prefect's own retry count to zero for these externally budgeted stages. Otherwise you have Prefect retries, Container Apps retries and control-plane retries simultaneously, making the real retry budget ambiguous.

`replicaTimeout` is particularly valuable because it is an **independent Azure-side fuse**: if your Prefect process and your reaper both disappear, Azure still has a configured execution timeout. That is a much stronger response to the actual overnight incident than heartbeats alone. citeturn2search10turn18search8

For ACI, set:

```text
restartPolicy = Never
```

ACI exposes stop/delete operations; stopping deallocates the group's compute, and Azure says billing stops once the group is stopped. Delete afterwards to clean the resource. citeturn1search32turn1search21turn1search10turn1search18

I found no equivalent ACI server-side “this external orchestrator attempt expires at T” mechanism in the current material. **That is where ACI simply does not provide the safety property you need.** ACI can be stopped or deleted, but your control plane has to do it. Under a management-plane/network outage, an ACI workload can therefore outlive your controller. Container Apps Jobs' configured timeout is the better independent fuse.

Use this attempt lifecycle:

```text
RESERVED
  -> DISPATCHING
  -> RUNNING
  -> SUCCEEDED | FAILED
  -> CANCEL_REQUESTED
  -> REAPING
  -> KILLED
```

`RUNNING` owns:

```text
provider_resource_id
provider_execution_id
lease_id
lease_expires_at
hard_deadline_at
last_heartbeat_at
```

A lightweight trusted wrapper around the agent process sends a heartbeat every, say, 30 seconds to the control API. A heartbeat extends the lease to `now + 120 seconds`. Those exact intervals are local tuning parameters; the important property is that the TTL is many times the normal heartbeat jitter.

Do not interpret the heartbeat as evidence of useful work. It means only “the execution wrapper is still alive”.

A separate scheduled reaper—an Azure Function or scheduled Container Apps Job with a **different managed identity from the agent**—runs continuously:

```text
for attempt in control_store where status in RUNNING/CANCEL_REQUESTED:
    if desired_run_state == CANCELLED:
        claim_for_reaping(attempt)

    elif lease_expires_at < now:
        claim_for_reaping(attempt)

    elif hard_deadline_at < now:
        claim_for_reaping(attempt)
```

Claiming is an ETag compare-and-swap:

```text
RUNNING -> REAPING
```

Only the reaper that wins that write may perform the kill.

The kill operation itself is deliberately idempotent at your abstraction layer:

```text
kill(attempt):
    if Container Apps Job execution:
        POST .../executions/{execution}/stop
    elif ACI:
        STOP container group
        DELETE container group

    if cloud says "already terminal" or "not found":
        treat desired killed state as satisfied

    poll/read cloud state
    until terminal/not-found or reconciliation deadline
```

Container Apps exposes both execution inspection and explicit termination. ACI exposes stop/delete management operations. citeturn1search15turn1search33turn1search21turn1search10

Cancellation is propagated in three layers:

```text
Prefect/owner cancellation
       |
       +--> best-effort immediate control-plane CANCEL_REQUESTED
       |
       +--> external controller invokes cloud kill
       |
       +--> lease expiry catches the case where the notification never happened
```

Do not make a Prefect hook your only cleanup mechanism. Prefect's own documentation warns that state hooks run client-side and their execution cannot be guaranteed; Prefect recommends Automations for more robust state-change reactions. citeturn0search3 The independent reconciler remains necessary even with either mechanism.

On orchestrator restart, **never reconstruct in-flight state from Prefect memory**. Run reconciliation first:

```text
D = durable attempts in {DISPATCHING, RUNNING, CANCEL_REQUESTED, REAPING}
C = live Azure resources/executions owned by agent control plane
```

Then compute:

```text
D ∩ C:
    query actual cloud state
    refresh/kill/close according to durable desired state

D - C:
    cloud resource disappeared
    mark LOST/FAILED unless terminal evidence already proves completion

C - D:
    cloud work exists with no live control record
    classify ORPHAN
    kill after a short safety/creation grace period
```

This is the same desired-state/current-state reconciliation pattern used by established controller systems such as Kubernetes. citeturn15search1turn15search10

For ACI, tag groups with `controller=agent-control`, `run_id`, `attempt_id`, `tenant_id`. For Container Apps Jobs, persist every returned execution identifier and enumerate active executions during reconciliation. If a start request times out in an ambiguous state, **query the provider before issuing another start**. Never resolve an uncertain dispatch by blindly starting again.

No system can guarantee a kill while Azure's management plane is unreachable. The defensible guarantee is: *no replacement attempt launches while its predecessor is unresolved; the controller continuously reconciles when Azure is reachable; and Container Apps Jobs have a server-side runtime fuse independent of the controller*. That is the strongest practical answer to the incident class.

## Terminal semantics and gates that can actually refuse

### The Prefect trap

The previous review was correct and current Prefect 3 documentation is unusually explicit about this behaviour.

A flow that raises an uncaught exception becomes `FAILED`. A flow that returns normally ordinarily becomes `COMPLETED`. If a flow explicitly returns a Prefect `State`, that state can determine the flow's final state; if it returns an iterable of states/futures and any are non-completed, Prefect can derive failure. Critically, capturing a failed child state and then returning normally can yield a `COMPLETED` parent. Prefect's migration documentation also states that child failure does not automatically make the parent fail in Prefect 3 unless it affects the return value or an exception propagates. citeturn0search0turn0search2turn0search4turn0search12

`return_state=True` means “give me the state object rather than following the normal result path”; it is **not** “propagate failure”. `State.result(raise_on_failure=True)` raises the underlying failure; suppressing that with `raise_on_failure=False` removes one of the propagation mechanisms. citeturn0search6

The safest idiom for required child work is therefore boring:

```python
from prefect import flow, task

@task(retries=0)
def required_stage(...) -> StageResult:
    ...

@flow
def pipeline(...) -> PipelineExecutionResult:
    futures = [
        required_stage.submit(...),
        required_stage.submit(...),
    ]

    # Every required child is observed.
    # result() propagates task failure into this flow.
    results = [future.result() for future in futures]

    return PipelineExecutionResult(results=results)
```

If the workflow intentionally captures states:

```python
@flow
def pipeline(...):
    states = [
        required_stage(..., return_state=True),
        required_stage(..., return_state=True),
    ]

    for state in states:
        # Explicitly turn required child failures into parent failures.
        state.result(raise_on_failure=True)

    return make_result(...)
```

Alternatively, explicitly returning all required states/futures allows Prefect's aggregate final-state rules to see their failure status. citeturn0search0turn0search2turn0search12

I would still **not use Prefect `COMPLETED` as business success**. Make the control-plane aggregator the only component authorised to write `SUCCEEDED`.

Conceptually:

```text
Prefect final state       Business outcome
---------------------     ------------------------
COMPLETED                 maybe SUCCEEDED, maybe FAILED/NEEDS_HUMAN
FAILED                    cannot be SUCCEEDED
CANCELLED                 cannot be SUCCEEDED
CRASHED                   cannot be SUCCEEDED
```

A Prefect `COMPLETED` event says that orchestration semantics reached completion. It does not establish your connector contract.

### Negative control for “false COMPLETED”

You need two kinds of tests.

The first demonstrates the **known bad semantics** so nobody can later argue the trap is hypothetical:

```python
@task
def explodes():
    raise RuntimeError("injected")

@flow
def deliberately_broken_parent():
    failed_state = explodes(return_state=True)
    failed_state.result(raise_on_failure=False)
    return "looks fine"
```

The test should confirm that this construct can reach a completed parent under the documented rules. That is your control specimen. citeturn0search0turn0search4

The production test is a parameterised fault-injection suite. For every one of the 18 required stages:

```text
inject child failure at stage N
run production parent
assert Prefect final state != COMPLETED
assert business outcome != SUCCEEDED
```

Then run independent terminal-closure negatives:

```text
remove one required handoff receipt       -> cannot SUCCEED
verifier returns FAIL                     -> cannot SUCCEED
verifier returns UNMEASURABLE             -> cannot SUCCEED
verifier returns NOT_RUN                  -> cannot SUCCEED
required gate DENY                        -> cannot SUCCEED
required gate missing                     -> cannot SUCCEED
expected tenant account absent            -> cannot SUCCEED
unexpected tenant account present         -> cannot SUCCEED
cloud attempt still RUNNING/UNKNOWN        -> cannot SUCCEED
evaluator bundle hash differs             -> cannot SUCCEED
```

Finally, mutation-test the terminal code itself. A mutation that changes:

```python
state.result(raise_on_failure=True)
```

to:

```python
state.result(raise_on_failure=False)
```

must cause CI to fail. A mutation that deletes one required-stage observation must also be killed by the test suite.

This is stronger than simply testing the happy path: it demonstrates that the implementation notices exactly the failure mode Prefect permits.

### Gates that prove they can refuse

The measured 22 approvals, zero refusals, and five of seven gates with `gate_check = None` mean the present evidence supports only **“an approval event can be emitted”**, not “a safety gate exists”.

First make `None` structurally invalid:

```python
class GateDefinition(BaseModel):
    gate_id: str
    predicate: PredicateDefinition

    @model_validator(mode="after")
    def predicate_required(self):
        if self.predicate is None:
            raise ValueError("mandatory gate without predicate")
        return self
```

The gate evaluator should be a trusted pure function/service:

```text
GateDecision evaluate(
    gate_id,
    policy_version,
    evidence_bundle_hash,
    evidence
)

GateDecision = {
  ALLOW | DENY,
  reason_code,
  policy_version,
  evidence_hash,
  decided_at
}
```

No empty approval is valid.

**ESTABLISHED PRACTICE:** mutation testing proves that an assertion/test suite notices deliberately introduced faults. Tools such as Stryker define the familiar killed-versus-survived-mutant model. citeturn5search2

**ESTABLISHED ANALOGUE, not gate-specific standard:** resilience organisations conduct controlled failure exercises/game days; Google's Disaster Recovery Testing/DiRT work is prior art for deliberately exercising controls rather than assuming they work, and Azure Chaos Studio is a vendor implementation of controlled fault injection. citeturn5search0turn5search6turn5search1

**OPEN/LOCAL:** I found no recognised industry standard called “approval-gate mutation testing” for autonomous software promotion. The correct answer is to borrow these two established ideas.

For every gate maintain:

```text
one known-ALLOW fixture
one or more single-fault DENY mutants
```

Example tenancy gate fixture:

```text
PASS:
  run tenant = client-A
  source accounts = [A1, A2]
  allowed accounts = [A1, A2]

MUTANT:
  run tenant = client-A
  source accounts = [A1, A2, B7]
  allowed accounts = [A1, A2]

EXPECTED:
  DENY / UNEXPECTED_SOURCE_ACCOUNT
```

Define:

```text
gate_mutation_score =
    refusal mutants correctly denied
    ----------------------------------
    non-equivalent refusal mutants
```

A safety gate should ship only at **100% of the explicit refusal-mutant set**. That is a project rule, not a universal statistical measure.

A credible promotion drill then traverses the **actual production promotion path**, not a unit-test substitute:

```text
1. Create a canary candidate in an isolated canary tenant/namespace.
2. Introduce exactly one deliberate policy violation.
3. Invoke the same promotion API used by normal production promotion.
4. Expect a real DENY, not a dry-run warning.
5. Independently read the target system.
6. Assert that no production/publish state changed.
7. Record drill_id, policy hash, evidence hash, DENY reason and target readback.
```

Run this after every gate-policy change and periodically thereafter. Do not deliberately corrupt a real client's production data; use a canary target that still exercises the real broker and policy service.

A gate is “armed” only if its latest refusal drill passed. I would put that timestamp into the gate registry and make a stale or never-drilled mandatory gate itself fail closed.

## Sandboxing and tenant isolation

The most important conclusion in this comparison is easy to miss: **compute isolation and credential blast radius are different problems**. A Firecracker VM can perfectly isolate the host and still allow the code inside it to delete every Azure resource that its credential legitimately authorises. For this company, the primary containment control should therefore be **credential/capability removal**, with runtime sandboxing as defence in depth.

### Sandbox comparison

The following costs are illustrative marginal compute costs for **1 vCPU, 2 GiB, 30 minutes**, excluding taxes, storage, network, plan minimums and discounts. External-provider prices are current advertised prices, therefore **VENDOR CLAIMS**, not observed costs.

| Option | Startup | Isolation boundary | Approx. marginal 30-min cost | Azure/Snowflake credential story | Verdict here |
|---|---|---|---:|---|---|
| Docker/runc | Very low; no useful universal SLA | Shared host kernel; rootless/user namespaces/seccomp reduce privilege but do not create a VM boundary | Underlying Azure VM allocation | Easy, but dangerous if sandbox receives broad MI/SP | **Not enough alone for untrusted generated code** |
| gVisor | Project describes millisecond-scale startup | User-space kernel interposes on application syscalls; stronger isolation than ordinary containers | Underlying Azure VM/AKS allocation + overhead | Azure-native if self-hosted | Strong technically, **too much platform work for four engineers** |
| Firecracker | Project claims application startup in as little as 125 ms and <5 MiB VMM overhead | KVM microVM, separate guest kernel | Underlying Azure VM host allocation | Possible when self-hosted, but you now own a microVM platform | Strongest self-managed boundary here; **do not build this yourselves now** |
| E2B | E2B claims roughly 150 ms in customer material | E2B states each sandbox is a Firecracker microVM | **~US$0.0414** | External to native Azure MI; credential federation/injection becomes your problem | Good build/test sandbox; weak fit for direct Azure deployment |
| Modal Sandbox | Vendor positions it as rapid serverless startup | gVisor | **~US$0.0595** | External service; native Azure MI not naturally attached | Similar conclusion to E2B; weaker isolation boundary than microVM |
| Daytona | Vendor advertises millisecond/sub-second provisioning | Current docs say each sandbox has a dedicated kernel/filesystem/network stack | **~US$0.0414** | Again external to Azure's MI boundary | Attractive developer sandbox; not the deployment trust boundary |
| Azure Container Apps Jobs | No fixed cold-start SLO I would rely upon | Azure-managed container service; retrieved docs do not promise a Firecracker/gVisor-style per-sandbox kernel boundary | Formula below; roughly **US$0.054 at common reference rates** before free grant, not a Canada Central quote | **Excellent**: attach one tenant UAMI and use Snowflake WIF | **Recommended execution substrate with a separate deployment broker** |
| ACI | Image size materially affects deployment time | Azure-managed container group | Per-second vCPU/memory; current regional quote must be checked | Good MI/RBAC fit | Keep only where needed; Jobs give better lifecycle controls |

Docker provides rootless mode, user namespaces and seccomp hardening, but those controls remain Linux-container isolation rather than a distinct guest-kernel boundary. citeturn7search8turn7search2turn7search5 gVisor's `runsc` supplies an OCI runtime with a user-space kernel; its own documentation acknowledges syscall/filesystem/network overhead and advertises millisecond startup. citeturn20search2turn20search3turn20search5turn20search16 Firecracker uses KVM microVMs and its project currently claims application startup as low as 125 ms and a VMM memory footprint below 5 MiB. citeturn19search2

E2B currently advertises $0.000014 per vCPU-second and $0.0000045 per GiB-second, yielding:

```text
1800 * (1 * 0.000014 + 2 * 0.0000045)
= US$0.0414
```

E2B also states that its sandboxes run in individual Firecracker microVMs. Its Pro plan currently lists a 24-hour maximum sandbox session, worth noting because your [M] worst stage lasted roughly 25.8 hours and your completed-run median was 26.4 hours. citeturn19search0turn23search1turn23search4

Modal's current Sandbox rate is $0.00003942 per physical core-second, where a physical core is described as two vCPUs, plus $0.00000667/GiB-second. At 1 vCPU-equivalent and 2 GiB:

```text
1800 * (0.5 * 0.00003942 + 2 * 0.00000667)
= about US$0.0595
```

Modal documents Sandboxes as gVisor-based. citeturn19search1turn18search0turn18search6

Daytona currently advertises $0.0504/vCPU-hour and $0.0162/GiB-hour with per-second billing:

```text
0.5 hours * (0.0504 + 2 * 0.0162)
= US$0.0414
```

Its current documentation describes a dedicated kernel, filesystem and network stack per sandbox; those are **vendor assertions**, not an independent security evaluation. citeturn18search1turn18search7

Azure Container Apps officially bills Consumption resources per second and grants 180,000 vCPU-seconds and 360,000 GiB-seconds per subscription each month. The Azure pricing pages available through this research interface do not expose a reliable numeric Canada Central rate, so I will not fabricate one. Using commonly published active reference rates of $0.000024/vCPU-second and $0.000003/GiB-second merely as a planning example gives about $0.054 for 30 minutes at 1 vCPU/2 GiB; obtain the actual Canada Central rate from the Azure retail calculator at deployment time. citeturn15search2turn20search6turn22search0turn22search2

For multi-hour software work, all of those cold-start differences are immaterial beside the measured 11.3-hour median live evaluation. Choose based on isolation, identity and lifecycle control, not 100 ms versus 1 second.

**Recommendation:** use Container Apps Jobs for Azure-hosted autonomous executions, but do **not** make the Job's credential powerful enough to deploy arbitrary infrastructure. The agent builds/tests/proposes. A trusted deployment service applies. E2B would be my first external option for credential-free build/test workloads when a stronger Firecracker boundary is worth sending execution outside Azure. Do not build a self-hosted Firecracker or gVisor platform for a four-person team unless an external security requirement forces it.

### Tenant isolation after the 45-account incident

The observed vendor-key incident proves that the vendor credential was not a client isolation boundary.

Use a **tenant cell** around a shared control plane:

```text
Tenant registry (trusted)
  client-A
    source allowed account IDs
    Azure UAMI-A
    Blob container-A
    Azure resource group/scope-A
    Snowflake service user-A
    Snowflake role-A
    database/schema-A
    BI workspace-A

  client-B
    ...completely separate capabilities...
```

The agent does not select arbitrary credentials. `tenant_id` is fixed when the run is created, and the trusted dispatcher resolves it to the tenant cell.

Azure Container Apps supports user-assigned managed identities and Azure RBAC can scope permissions to the required resource hierarchy. Snowflake supports Workload Identity Federation with Microsoft Entra identities, including Azure managed-identity principals, so a Snowflake service user can be bound to a particular workload identity rather than receiving a long-lived password/key. Snowflake RBAC then limits that service user to the tenant's target objects. citeturn18search2turn18search5turn11search1turn11search4turn11search10turn11search2

For this team I would provision **one user-assigned managed identity per tenant**, not per attempt. Attach only that identity to that tenant's job. Do not attach identities for several customers to the same sandbox and hope the application chooses the correct one.

For Snowflake:

```text
Azure UAMI client-A
       |
       | Workload Identity Federation
       v
Snowflake service user svc_client_A
       |
       v
role CLIENT_A_LOADER
       |
       +-- USAGE specific warehouse
       +-- USAGE client_A database/schema
       +-- required INSERT/MERGE/COPY privileges
       +-- no client_B roles
```

Snowflake's WIF and RBAC mechanisms make this achievable without distributing a permanent Snowflake password to the agent. citeturn11search1turn11search10turn11search9

The vendor API deserves the same treatment. If a vendor offers genuinely tenant-scoped credentials, use them. If one unavoidable credential can enumerate many customers, **the agent should never receive that global credential**. Put it behind a source-access broker:

```text
agent: fetch(account_id=A1, tenant=client-A)

broker:
  verify A1 in trusted tenant registry for client-A
  call vendor using broad credential
  return only authorised result
```

A discovery operation that expected six accounts and receives 45 should produce a hard tenancy violation before customer data is extracted. Silently filtering 39 extras hides the fact that your source credential boundary is broken.

The minimum non-skippable tenancy checks are not a single “tenancy gate”. They sit at every capability/persistence boundary:

| Boundary | Mandatory condition |
|---|---|
| **Dispatch / infrastructure apply** | Run tenant, selected Azure identity, subscription/resource group and proposed resource IDs all belong to the same tenant cell |
| **Source discovery before data fetch** | Every discovered source account is in the tenant allow-list; unexpected extras deny the run |
| **Azure handoff before accepting blob/object** | Manifest tenant/account IDs are authorised; destination container/path is the matching tenant destination |
| **Snowflake before COPY/MERGE** | Distinct tenant/account IDs in staging are authorised and target database/schema/role belongs to that tenant |
| **BI/chat promotion before publish** | Target workspace/dataset/semantic surface is the tenant's and downstream access test reveals no foreign tenant |

These checks must be inside the **broker operation itself**, not optional stages an agent is expected to remember to call. An agent with a raw Snowflake credential plus a separate `check_tenancy()` tool can simply skip the tool. A Snowflake loader service that checks the tenant before executing the statement cannot.

Per-tenant identity scoping is therefore achievable on Azure + Snowflake today. The cost is primarily operational: the number of managed identities, Snowflake users/roles/grants and tenant registry entries grows linearly with clients. Automate those objects from one declarative registry. I would not pay the complexity cost of a new identity for every run; use a durable per-tenant identity and short-lived per-run **capabilities** issued by the control plane.

## Telemetry, reliability and evaluator isolation

### Minimum event model that makes spend reconstructable

Your current [M] rule “record cost only on `stage_completed`” structurally guarantees undercounting precisely when the system is least reliable.

For a four-person team I would not introduce a large telemetry platform first. Keep transactional state in Azure Table Storage and write an append-only event row for every lifecycle transition, periodically exporting those rows to Blob/Parquet for analysis.

Every event needs this common envelope:

```text
schema_version
event_id
event_type
occurred_at_utc
ingested_at_utc

tenant_id
run_id
stage_id
attempt_id
attempt_no

trace_id
parent_event_id

policy_version
scope_hash
code_git_sha
container_image_digest
config_hash
```

The minimum lifecycle event set is:

```text
RUN_CREATED
ATTEMPT_RESERVED
DISPATCH_REQUESTED
WORKLOAD_CREATED
WORKLOAD_RUNNING
HEARTBEAT
STAGE_RESULT
FAILURE_CLASSIFIED
CANCEL_REQUESTED
KILL_REQUESTED
WORKLOAD_TERMINATED
ORPHAN_DETECTED
COST_SETTLED
HANDOFF_ACCEPTED
GATE_DECISION
CONTRACT_VERDICT
RUN_TERMINAL
```

`WORKLOAD_CREATED`/`WORKLOAD_TERMINATED` need:

```text
provider
subscription_id
region
resource_type
resource_id
provider_execution_id

requested_vcpu
requested_memory_gib

provider_created_at
provider_running_at
provider_terminal_at
termination_cause
```

This distinction matters because ACI's billable duration starts from image pulling/restart and continues until the group is stopped; it is not synonymous with your Prefect stage's start/end timestamps. Azure Container Apps likewise bills resource allocation by duration. citeturn15search5turn20search6

Cost fields need:

```text
reserved_cost_micro_usd

meter_name
usage_quantity
usage_unit

price_per_unit
currency
price_snapshot_at

estimated_cost_micro_usd
provider_actual_cost_micro_usd   # later settlement, nullable
provider_billing_id              # later settlement, nullable

llm_provider
llm_model
input_tokens
cached_input_tokens
output_tokens
tool_api_units
```

For a killed attempt, the reaper supplies the terminal cloud observation and duration. For an orphan, emit `ORPHAN_DETECTED`, then kill/reconcile it and record the eventual provider terminal time. If exact billing cannot yet be obtained, you can at least reconstruct:

```text
allocated resource quantity × observed billable duration × recorded rate
```

instead of `$0.00`.

Events describing state transitions and their attempt record should ideally be committed transactionally where practical. At minimum, a run must never reach terminal closure while an attempt has no reconciled terminal/resource state.

### Reliability independent of retries

There is no single universally standard LLM-agent metric for this. The useful established concept is *first-attempt/first-pass success*: retries can mask underlying unreliability, which is why SRE systems treat retries as additional load rather than pretending a recovered request was originally healthy. citeturn4search2turn4search6

I would name your canonical metric:

**First-Attempt Contract Pass Rate — FACPR**

At stage level:

```text
FACPR =
  required stage instances whose first attempt reached
  CONTRACT_PASS + HANDOFF_ACCEPTED
  -----------------------------------------------------
  required stage instances that were attempted
```

The numerator must use **contract acceptance**, not `stage_completed`.

Then publish:

**First-Pass Run Yield**

```text
runs where every required stage passed its contract
on attempt 1 and every mandatory gate passed
-------------------------------------------------
all eligible runs
```

And alongside it:

```text
Attempt Amplification =
    total stage attempts
    --------------------
    unique required stage instances
```

A stage succeeding on attempt 352 therefore contributes:

```text
FACPR:                 0 for that stage
first-pass run yield:  0 for that run
attempt amplification: 352 for that stage
```

It can still be reported as “eventually recovered”, but it receives no first-pass reliability credit.

Also retain a survival curve:

```text
P(CONTRACT_PASS by attempt 1)
P(CONTRACT_PASS by attempt 2)
P(CONTRACT_PASS by attempt 3)
```

That makes the marginal value of retries visible and gives you actual evidence for revising the three-attempt policy later.

The current aggregate [M] stage-attempt success rate of 14.2% cannot be converted reliably into FACPR from the supplied data because it does not tell us which `stage_completed` events were contract passes on first attempts. That metric becomes computable only after `attempt_no` and contract outcomes are recorded explicitly.

### Evaluator isolation: what actually stops the LLM shell

For the stated threat model—an LLM agent with shell/repository access, not a malicious company administrator—the measures rank as follows.

| Rank | Measure | What it actually stops | What it does **not** stop | Value |
|---:|---|---|---|---|
| **1** | External evaluator service with separate identity | Agent rewriting evaluator/corpus locally; invoking a modified evaluator; stealing same-process credentials; writing canonical verdicts | A human/cloud admin; flaws in evaluator itself | **Strongest real boundary** |
| **2** | Separate evaluator credentials, inaccessible to agent | Agent pushing evaluator/corpus changes or writing verdict storage | Credential theft if credentials are placed in the same sandbox | **Essential ingredient** |
| **3** | Separate repository, agent has no write permission, evaluator fetches independently | Canonical source/corpus mutation through Git | Agent altering a local clone if evaluator trusts that clone | **Worth doing; cheap** |
| **4** | Signing key held outside agent sandbox | Forging a manifest/verdict or undetected transport/storage modification | Agent selecting an old valid signed bundle unless anti-rollback exists; evaluator logic bugs | **Useful for provenance, optional initially** |
| **5** | Separate local process with same effective trust boundary | Accidental in-process mutation | Shell can still influence shared files/process inputs; little meaningful protection | **Mostly theatre** |

Git hosting can enforce branch/repository permissions, but the important property is that the evaluator independently retrieves the canonical protected commit rather than evaluating a checkout the agent can edit. Azure Key Vault/RBAC likewise becomes meaningful only when the agent identity has no signing/write capability. citeturn13search0turn13search2turn13search1

The implementation I recommend is deliberately small:

```text
agent sandbox
    |
    | submit {artifact_uri, artifact_sha256, run_id}
    v
Evaluator API  [separate Azure Container App/Function]
    |
    | managed identity not available to agent
    |
    +--> read canonical evaluator bundle/corpus
    +--> read submitted artifact independently
    +--> run 12-assertion verifier
    +--> write verdict directly to trusted control store
```

The agent never supplies the evaluator implementation, corpus path or manifest to be trusted. It supplies only the artefact to evaluate.

Keep the evaluator and corpus in a separate protected repository or immutable/versioned object store. Pin its commit/hash in the run scope. The evaluator service independently loads that version.

A signing key is **not required for the first secure version** if the external evaluator is the only principal that can write canonical verdict records directly to the trusted control database. Adding cryptographic signatures is useful if verdicts travel through untrusted storage or need independent offline verification. Putting a signing key in the same agent sandbox would be security theatre.

Your existing hash-pinned corpus remains useful as tamper **evidence**, but its current property—agent can rewrite corpus and manifest together—means it is not a trust boundary. Moving only the files to another directory changes nothing; moving ownership/credentials out of the agent's capability set does.

## Scaffolding and the optimiser

### Repository scaffolding

For this team, the clearest answer is:

**Copier for project generation and upgrades, uv workspaces for the Python monorepo, and one separate evaluator repository because that separation is a trust boundary.**

Copier is unusually well matched to template drift because updating generated projects is a first-class feature: it records template answers, can compare an existing generated project with later template versions, and supports migrations for changes that cannot be represented as a simple file update. citeturn14search0turn14search3turn14search6

`uv` workspaces are complementary rather than competing: they let multiple Python packages live and be managed together in one workspace. citeturn14search1

My grading:

| Tool | For this company | Reason |
|---|---:|---|
| **Copier** | **A** | The requirement is not generation; it is *updating already-generated repos*. That is Copier's differentiator. |
| **uv workspaces** | **A as companion** | Good Python monorepo/package-management layer; not itself a skeleton generator. |
| **Cookiecutter** | **C+** | Fine if generation is effectively one-shot; template drift is the user's stated failure mode, so I would not make it the centre of this design. |
| **Nx** | **C** | Useful task graph/build tooling, but adds another ecosystem to a mostly-Python four-person team. |
| **Bazel** | **D here** | Powerful hermetic/build-scale tooling, but unjustified operational surface for four engineers and this repository size. |
| **AI scaffolder as source of truth** | **D** | An agent can propose template changes; it should not replace deterministic, versioned regeneration/update semantics. |

The rule that reduces drift most is to **generate less**. Do not copy 2,000 lines of shared control-plane logic into every connector. Generate package wiring, manifests, deployment descriptors and thin adapters; put shared behaviour in versioned internal Python packages.

Use a product monorepo approximately like:

```text
repo/
  packages/
    connector_sdk/
    control_plane_client/
    telemetry/
    tenancy/
  services/
    dispatcher/
    reaper/
    deployment_broker/
  connectors/
    vendor_a/
    vendor_b/
  templates/
    connector/
  pyproject.toml
  uv.lock
```

Keep the canonical evaluator/corpus in the second repository because its repository separation has a security purpose. Do **not** create a separate repository per microservice merely because there are several Azure services. For four engineers, that turns dependency coordination and cross-cutting control-plane changes into unnecessary release choreography.

Pin every generated repository to a Copier template version. Template upgrades happen as deliberate PRs:

```text
template v12 -> project
copier update to v13
CI
review diff
merge
```

An LLM can help resolve an update conflict; the Copier version remains the authoritative migration history.

### The optimiser verdict: not yet

**Do not build an optimiser now.**

The current system's objective function is contaminated:

* runs can be `COMPLETED` while containing failures [M];
* missing work can disappear behind `stage_started` [M];
* retry count is unbounded [M];
* a run can use hundreds of retries [M];
* gates have never demonstrated refusal [M];
* failed-attempt spend is recorded as zero [M];
* only one connector has a recorded successful end-to-end run [M].

An optimiser operating on that signal can learn to maximise **the control plane's mistakes**, not software correctness.

The prerequisite order I would use is:

```text
hard external attempt/spend/concurrency budget
        ↓
cloud timeout + cancellation + orphan reaping + restart reconciliation
        ↓
Prefect failure propagation + external business-outcome closure
        ↓
refusal-capable gates with negative drills
        ↓
tenant capability isolation at every persistence/promotion boundary
        ↓
complete attempt/cost/FACPR telemetry
        ↓
external evaluator trust boundary
        ↓
expand and freeze evaluation corpus
        ↓
only then configuration experiments
```

The first four are the user's Q2-Q5 and are non-negotiable. Tenancy and evaluator integrity should also precede optimisation because otherwise the optimisation score itself is not safe to trust.

### Which configuration dimensions are worth searching?

There is no credible universal ranking for your exact connector-migration workload, and claiming precise effect sizes would overstate the literature.

What current software-agent experiments do show is that **model choice and agent/tool/context design can move pass rates materially**. In one 2026 SWE-Adept comparison using the same broad framework, different model backends differed by roughly 9–13 percentage points on reported resolve rates; architecture/context-management modifications in the same work produced up to roughly 4.7 percentage points improvement. A separate 2026 code-edit-interface study reported a 2.1-point resolve-rate gain and a 17.9% inference-cost reduction. Those figures are benchmark-specific and are not forecasts for your connectors. citeturn21search0turn21search11 Earlier SWE-agent work also established that the agent-computer interface itself can materially affect coding-agent behaviour and success. citeturn15search3

I would therefore screen, in this order:

| Dimension | Search priority | Evidence position |
|---|---:|---|
| **Model** | Very high | Published software-agent results show materially different outcomes; exact effect in your stack unknown. citeturn21search0 |
| **Reasoning effort / token budget** | High | Likely coupled strongly to model and task difficulty, but I found no clean number transferrable to this workload. **OPEN**. |
| **Tool interface / available safe tools** | High | Published agent/interface work reports measurable gains; tool *permissions* themselves are safety policy and must not be optimised away. citeturn15search3turn21search11 |
| **Context selection/layout** | High–medium | Current coding-agent research reports gains from better localisation/context management, generally single-digit points in the retrieved controlled comparisons. citeturn21search0 |
| **Substantive system prompt structure** | Medium | Worth screening, but no robust magnitude specific to long-horizon connector migrations. |
| **Prompt micro-wording/formatting** | Low initially | Do not spend live 11-hour evaluations searching commas, headings and stylistic wording until higher-order variables are understood. |
| **Retry cap** | **Do not optimise** | Safety/control parameter. Optimising eventual success can simply reward more retries. |
| **Gate thresholds / tenancy checks** | **Do not optimise** | Safety specification, not an agent quality hyperparameter. |
| **Timeout/concurrency limits** | **Do not optimise for benchmark score** | Operational policy; tune from SLO/cost evidence separately. |
| **Evaluator thresholds/corpus** | **Never optimise on the candidate's score** | That changes the ruler rather than the system. |

The order-of-magnitude conclusion is therefore modest: model choice can plausibly produce **high-single- to low-double-digit absolute percentage-point differences** in comparable public software-agent evaluations; recent interface/context improvements often appear in the **low-single-digit percentage-point range**; there is no defensible transfer estimate for your prompt wording or reasoning-effort knob. citeturn21search0turn21search11

### Search method for hour-long live evaluations

Your fact that the *evaluator* can replay evidence in under a second does **not** mean a new agent configuration can be evaluated in under a second. Recorded evidence describes the old configuration's output. Unless you have a simulator that faithfully changes the generated trajectory when the configuration changes, replay is useful for evaluator regression and re-scoring, **not for producing a score for an unrun candidate configuration**.

That substantially weakens the case for clever optimisation.

Start with **experimental screening**, not black-box optimisation.

One-factor-at-a-time is not the best design. NIST explicitly notes that OFAT works only when interactions are absent; factorial/fractional-factorial designs are designed to expose multi-factor effects and interactions. citeturn17search2turn17search6turn17search18

Suppose the first safe search has four binary-ish dimensions:

```text
model A / B
normal / high reasoning
context strategy A / B
tool interface A / B
```

A full factorial is 16 configurations. An eight-configuration fractional factorial is a reasonable first screen if you accept explicit assumptions about which higher-order interactions are negligible. This gives you considerably more information than sequentially changing one factor and then freezing whichever setting happened to win on a noisy fixture. citeturn17search18turn17search26

After screening, **successive halving** is the best fit if “number of independent tasks evaluated” is a meaningful fidelity. For example:

```text
8 configurations × 4 tasks  = 32 live task-runs
keep 4
4 configurations × 10 tasks = 40
keep 2
2 configurations × 30 tasks = 60
                               ---
                               132 total
```

Evaluating all eight on all 30 tasks would require:

```text
8 × 30 = 240 task-runs
```

so this illustrative schedule uses about **45% fewer live task-runs**. That is arithmetic, not a promised statistical efficiency: it works only if the first four/ten tasks are representative enough not to eliminate the true winner.

Hyperband generalises the allocation idea across several resource schedules. Its original ML paper reported 5–30× speed improvements over selected Bayesian-optimisation baselines on its deep-learning/kernel benchmarks, but those numbers should **not** be transferred to LLM software agents. citeturn17search0turn17search4 In your case, Hyperband is useful only once you have a genuine lower-fidelity resource—such as number of representative tasks—that predicts full-corpus ranking.

Bayesian optimisation becomes more attractive after screening leaves a small number of genuinely tunable numerical/ordinal dimensions. BO is explicitly designed for expensive black-box evaluations and reuses information from earlier experiments, but with categorical model/tool choices, stochastic outcomes and a tiny corpus its surrogate can look more sophisticated than the underlying data justifies. citeturn17academia37 I would not introduce it until you have at least a dozen or so trustworthy configuration observations; that threshold is a **local engineering rule**, not a theoretical guarantee.

LLM-proposed mutations are useful as a **candidate generator**, especially after inspecting traces such as “context consistently omitted the schema migration” or “the agent failed to call the verification tool”. They should not be the judge. Generate a few hypothesis-driven variants, feed them through the same fixed evaluation design, and leave the corpus/evaluator inaccessible to the candidate agent.

So the ordering is:

```text
baseline variance measurement
→ fractional-factorial/ablation screen
→ successive halving on task count
→ only then Bayesian or trace-informed candidate generation if still warranted
```

Ablation is therefore the correct *spirit* for the first pass—learn which components matter—but **sequential OFAT optimisation is not**.

### What corpus size replaces one?

There is no published magic minimum for this exact setting. Anyone who tells you “N=20” or “N=50” is scientifically validated for autonomous connector migration is inventing precision.

I would nevertheless replace one fixture with a concrete engineering gate:

**Do not start automated configuration search below 40 independently constructed fixtures: at least 30 development/screening fixtures plus 10 untouched connector-level holdouts.**

That is **OPEN/LOCAL POLICY**, not an established threshold.

Why 40 rather than pretending five or ten is enough? With a binary success rate around 50%, even 30 independent observations have an approximate 95% sampling half-width of about 18 percentage points; at 40 it is still roughly 15.5 points. In other words, a corpus this small can only support decisions about **large effects**. It cannot reliably distinguish 52% from 56%. That is exactly the level of humility a four-person team with expensive evaluations should want.

The 40 fixtures must also be heterogeneous. They should span, at minimum, distinct examples of:

```text
source discovery / pagination
auth and credential errors
schema evolution
API throttling/transient errors
Azure handoff
Prefect failure propagation
Snowflake load/merge
tenancy violations
promotion/gate refusal
```

Hold out entire connectors/vendors where possible rather than randomly holding out adjacent stages from the same connector; otherwise nearly duplicate repository structure leaks into both search and validation.

If producing 40 trustworthy fixtures is too expensive, **the answer is not to optimise on one**. Stay with engineering ablations and incident-driven changes. The existing one-known-good-run corpus remains folklore for configuration selection, exactly as the prior review concluded.

## What is known, what remains open, and what to build

The control-plane design can now be divided cleanly into high-confidence engineering decisions and questions that should remain explicitly unresolved.

**High confidence / established enough to implement now:** external attempt/concurrency ownership; atomic check-and-reserve before dispatch; agent inability to modify its cap; finite cloud workload deadlines; external orphan reaping and desired/current-state reconciliation; retrying only classified transient faults; explicit Prefect failure propagation; business success independent of Prefect `COMPLETED`; downstream acceptance receipts; tenant-scoped Azure/Snowflake identities; first-attempt reliability measurement; mutation-style negative controls for gates; and a separate evaluator capability boundary. Azure, Prefect, Snowflake and the distributed-controller patterns needed to implement those pieces exist today. citeturn3search5turn18search8turn1search15turn0search4turn18search2turn11search10turn15search1

**Vendor capabilities rather than reliability evidence:** Container Apps Jobs expose timeouts/retry limits/stop operations; ACI exposes stop/delete; managed identities and Snowflake WIF provide credential primitives; E2B/Modal/Daytona advertise particular sandbox boundaries/startup times; Copier supports updating generated projects. These facts establish that a mechanism is available, not that its adoption will improve your production success rate. citeturn2search10turn1search21turn18search2turn11search1turn23search1turn18search0turn18search7turn14search0

**Still open or deliberately local:**

| Question | Honest status |
|---|---|
| Are exactly four business terminal states standard? | **No.** It is a sensible local projection, not a standard. |
| What is the optimal stage attempt cap? | **Unknown.** Three total attempts is a conservative initial safety cap backed only indirectly by mature service-retry practice. |
| When are two LLM software attempts “the same failure”? | **Unsolved in general.** Use structured deterministic fingerprints plus verifier-observed progress and validate false-positive rates. |
| Is “two repeated identical failures” the right early-stop threshold? | **Unknown/local policy.** |
| Can a cloud workload be absolutely guaranteed killed? | **No under provider/control-plane unavailability.** Container Apps' server-side timeout provides an independent backstop; ACI is weaker here. |
| Is a refusal-mutation score a standard gate metric? | **No.** Mutation testing and game days are established analogues; this application is a local design. |
| Does Container Apps provide the same sandbox boundary as Firecracker/gVisor? | **Not established by the retrieved Microsoft documentation.** Do not market it as such. |
| Can E2B/Modal/Daytona cleanly obtain one Azure/Snowflake workload identity per sandbox? | **Not established in this research.** Do not assume third-party sandboxing preserves Azure-managed-identity ergonomics. |
| What is the exact Canada Central marginal Container Apps price per run today? | The official billing model is clear, but the retrieved regional pricing page did not expose a trustworthy numeric quote. Use the retail calculator when budgeting. |
| Can historical failed-attempt spend be reconstructed? | **No from the supplied [M] logs**, because failed attempts were recorded at $0.00 and required usage fields are absent. |
| Was the previous in-memory counter definitely responsible for the production loops? | **Not reverified.** That is [R]. The new design does not need the claim to be true; the [M] restart behaviour already demands a durable external cap. |
| What corpus size scientifically guarantees safe optimisation? | **No universal number exists.** Forty is the proposed minimum engineering gate for this team, and even that supports only large-effect decisions. |
| Which prompt/reasoning setting is best? | **Unknown until a trustworthy heterogeneous corpus exists.** |
| Should an optimiser be built now? | **No.** |

The smallest implementation programme I would actually fund is therefore:

```text
Control API
  Azure Table transactional budget/attempt ledger
  agent has no policy/table/deployment write capability

Container Apps Jobs
  replicaRetryLimit = 0
  hard replicaTimeout
  per-tenant managed identity

Reaper/reconciler
  leases + hard deadlines
  explicit Azure stop
  restart reconciliation
  no replacement while predecessor unknown

Business outcome aggregator
  expected-scope manifest
  handoff receipts
  verifier PASS only
  mandatory gate decisions
  no unresolved cloud resources
  Prefect COMPLETED never maps directly to SUCCEEDED

Gate service
  predicates mandatory
  DENY fixtures
  mutation tests
  real-path canary refusal drills

Tenant registry + brokers
  per-tenant Azure identity
  vendor account allow-list
  Snowflake WIF service user/role
  tenancy checks embedded at every irreversible boundary

Telemetry
  attempt_no
  lifecycle/resource timestamps
  cost reservation/settlement
  FACPR + first-pass run yield + attempt amplification

Evaluator service
  separate repository + identity
  canonical bundle independently loaded
  agent can submit artefacts but cannot modify verdict machinery

Copier + uv
  deterministic updatable scaffolding

Optimizer
  NOT BUILT
```

That is intentionally less machinery than a new agent architecture, custom microVM platform or sophisticated optimiser. The measurements supplied indicate that the expected return is in making the existing work **stop, reconcile, refuse and tell the truth** before trying to make it smarter.