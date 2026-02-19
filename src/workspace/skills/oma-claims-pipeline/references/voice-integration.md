# Voice Integration Blueprint

## Objective

Connect phone conversations to the claims pipeline while keeping business decisions inside the role workflow.

## Runtime Flow

Phone call -> STT/TTS provider -> WebSocket client -> OpenClaw Gateway -> main orchestrator -> 6-role pipeline -> voice-safe summary.

## Technical Interfaces

- Chat completion endpoint: `/v1/chat/completions`
- Tool invocation endpoint: `/tools/invoke`
- Session proxy tool: `sessions_send`

## Pre-Auth Gate (before role execution)

1. Look up customer by phone index (`workspace/customers/index.json`).
2. Load `tg_{telegram_id}/client.json`.
3. Verify policy status and PIN.
4. Only then allow role execution.

## Live Operator Escape (mandatory)

The customer can request a live operator at any step, without explanation.

Escalate immediately to human operator when any of the following is true:

- customer explicitly asks for human support,
- injury or possible injury is reported,
- identity or policy verification fails,
- repeated understanding failures (3+),
- stress/aggression signals indicate poor bot fit.

Do not force repeated authentication after transfer if pre-auth already succeeded.

## Customer Data Contract

- Client profile: `workspace/customers/tg_{telegram_id}/client.json`
- Policy files: `workspace/customers/tg_{telegram_id}/policies/policy_<policy_id>.json`
- Claim file: `workspace/customers/tg_{telegram_id}/claims/<claim_id>/claim.json`
- Phone index: `workspace/customers/index.json`
- Photo media: `workspace/customers/tg_{telegram_id}/claims/<claim_id>/photos/`

## Operational Checks

- Validate path layout with `scripts/path_doctor.py`.
- Build customer files and index with `scripts/generate_customers.py`.
- Validate caller with `scripts/preauth_check.py`.
