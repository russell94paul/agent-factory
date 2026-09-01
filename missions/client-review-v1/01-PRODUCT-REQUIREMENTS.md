# Client Review — Product Requirements

## Primary view

The Client Review should provide a concise executive-level delivery summary with progressive disclosure into technical evidence.

## 1. Delivery Health

Show:

- overall status;
- delivery confidence where supported;
- milestone progress;
- critical blocker count;
- outstanding client decisions;
- readiness for review/acceptance.

Avoid opaque AI-generated health scores unless their basis is inspectable.

## 2. What We Understood

Display the current interpreted requirement / Intent Contract.

Include:

- objective;
- requested outcome;
- important requirements;
- assumptions;
- exclusions;
- acceptance criteria.

Highlight unresolved ambiguity.

## 3. What Changed

Provide a client-friendly summary of meaningful changes since the previous review or selected point in time.

Do not expose irrelevant commit noise.

Group changes by user/business impact where possible.

## 4. Delivery Progress

Show major delivery stages such as:

```text
Understanding
Planning
Implementation
Testing
Validation
Deployment
Client Review
Acceptance
```

Map these to existing Agent Factory mission state rather than creating duplicate state where possible.

## 5. Evidence

For each major delivered outcome, allow the client to inspect supporting evidence such as:

- tests;
- screenshots;
- validation results;
- parity checks;
- sample output;
- deployment verification;
- relevant change/PR;
- acceptance criteria.

Client-facing claims must be traceable to evidence.

## 6. Decisions Required

Present only decisions genuinely requiring client input.

Each should contain:

- question;
- context;
- recommended option;
- alternatives;
- effect on delivery;
- whether it is blocking.

Where supported, allow:

- Approve;
- Choose alternative;
- Ask for explanation;
- Defer.

## 7. Risks and Blockers

Translate internal issues into client-understandable language.

For each:

- what happened;
- impact;
- current owner;
- whether client action is required;
- mitigation;
- affected delivery area.

Do not expose irrelevant internal debugging noise.

## 8. What's Next

Show the next meaningful outcomes rather than a raw task queue.

Example:

```text
NEXT

→ Complete production validation
→ Confirm historical parity
→ Prepare release evidence
→ Client acceptance
```

## 9. Acceptance

Where appropriate provide:

- Ready for Review;
- Ready for Acceptance;
- Accepted;
- Changes Requested.

Acceptance must become an auditable delivery event.

## Client-safe transformation

The Client Review is not a direct visualization of internal Agent Factory state.

It is a transformation layer:

```text
INTERNAL STATE
      ↓
filter
      ↓
ground
      ↓
summarize
      ↓
translate terminology
      ↓
CLIENT REVIEW MODEL
      ↓
UI
```

Internal data that should not be exposed must be filtered before reaching the client view.
