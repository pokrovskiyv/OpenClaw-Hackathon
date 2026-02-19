# Customer Journey Workflow (No-Injury Scope)

## Scope

This workflow handles accident support from first contact to payout for **no-injury** scenarios.
If injury is reported or suspected, switch to emergency-first mode and route to human handling.

## Phase 1 — First Contact (Care + Safety)

1. Greet calmly and show empathy.
2. Confirm immediate safety state.
3. Confirm no injuries (driver/passengers/other party).
4. If injury signal appears at any point, stop standard path and escalate.

## Phase 2 — Immediate Incident Guidance

Agent gives the customer a clear checklist:

- Move to safe location if possible.
- Exchange required details with other driver.
- Capture photos: damage, plates, road signs, scene angles.
- Capture witness contacts if available.
- Follow state-specific reporting expectations for police/DMV self-report thresholds.

Photo handling (simple server-local setup):

- Store photos under `workspace/customers/tg_<telegram_id>/claims/<claim_id>/photos/`.
- Maintain `workspace/customers/tg_<telegram_id>/claims/<claim_id>/photos/manifest.json` for indexed retrieval.

## Phase 3 — Pre-Auth + Claim Initialization

1. Resolve customer via `customers/index.json` and `customer_{telegram_id}.json`.
2. Validate policy status and PIN.
3. Open claim context with a deterministic claim ID.

## Phase 4 — 6-Role Adjudication Pipeline

1. Front Desk — complete FNOL package.
2. Claims Officer — coverage validation and best path selection.
3. Assessor — estimate and total-loss logic.
4. Fraud Analyst — risk scoring with evidence.
5. Senior Reviewer — final decision and rationale.
6. Finance — payout execution and subrogation handling.

## Phase 5 — Customer Communication Until Payout

- Keep customer updates short and specific.
- Provide clear next action and expected timeline.
- Avoid internal fraud language in customer-facing messages.
- Confirm payout method/status and completion signal.

## Automation Principles

- Use strict JSON contracts per role.
- Avoid repeated manual data entry by carrying `claim_context` end-to-end.
- Use deterministic routing and auditable decisions.
- Escalate uncertainty instead of guessing.

## Business Balance Rules

- Do not pay invalid or excluded claims.
- Prefer customer-favorable valid coverage route when multiple options exist.
- Keep processing predictable and transparent.
- Optimize for both financial discipline and long-term trust.
