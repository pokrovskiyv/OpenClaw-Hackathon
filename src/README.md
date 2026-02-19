# src template for .openclaw migration

This folder is structured as a transfer-ready template for a target OpenClaw home directory.

## Mapping

- `src/openclaw.json` -> `~/.openclaw/openclaw.json`
- `src/workspace` -> `~/.openclaw/workspace`
- `src/workspace/skills/oma-claims-pipeline` -> `~/.openclaw/workspace/skills/oma-claims-pipeline`
- `src/workspace/customers/tg_{telegram_id}/client.json` -> `~/.openclaw/workspace/customers/tg_{telegram_id}/client.json`
- `src/workspace/customers/tg_{telegram_id}/policies/policy_<policy_id>.json` -> `~/.openclaw/workspace/customers/tg_{telegram_id}/policies/policy_<policy_id>.json`

Important:

- If you copy only `agents.list` into an existing config but do not copy the workspace skill folder to the matching workspace path, OpenClaw will not find the skill files.
- The path in `agents.list[].workspace` must point to the workspace where `skills/oma-claims-pipeline` actually exists.

## What is already prepared

- 6 role prompts copied from project agents into `references/roles/*`.
- Voice integration notes copied into `references/voice-integration.md`.
- Business requirements copied into `references/business-requirements.md`.

## Minimal transfer steps

1. Copy `src/openclaw.json` to `~/.openclaw/openclaw.json`.
2. Copy `src/workspace/skills/oma-claims-pipeline` to `~/.openclaw/workspace/skills/`.
3. Start a new OpenClaw session so skills snapshot refreshes.

## Validation after copy

Run:

1. `python ~/.openclaw/workspace/skills/oma-claims-pipeline/scripts/path_doctor.py --openclaw-home ~/.openclaw`
2. `python ~/.openclaw/workspace/skills/oma-claims-pipeline/scripts/generate_customers.py --policies-dir /path/to/policies`
3. `python ~/.openclaw/workspace/skills/oma-claims-pipeline/scripts/preauth_check.py --policy OMA-2025-19450 --phone +1-614-555-1945 --pin 9450`
4. `python ~/.openclaw/workspace/skills/oma-claims-pipeline/scripts/handoff_validate.py --role front_desk --input /path/to/front_desk_output.json`
5. `python ~/.openclaw/workspace/skills/oma-claims-pipeline/scripts/claim_init.py --telegram-id 119450 --claim-id CLM-2026-0001 --policy-id OMA-2025-19450 --incident-type collision --summary "rear-end at low speed"`
6. `python ~/.openclaw/workspace/skills/oma-claims-pipeline/scripts/claim_status.py --telegram-id 119450 --claim-id CLM-2026-0001 --to preauth_verified --reason "identity and policy verified"`
7. `python ~/.openclaw/workspace/skills/oma-claims-pipeline/scripts/photo_intake.py --claim-id CLM-2026-0001 --telegram-id 119450 --source /tmp/photo.jpg --part front_bumper`
8. `python ~/.openclaw/workspace/skills/oma-claims-pipeline/scripts/workflow_plan.py --claim-id CLM-2026-0001 --policy OMA-2025-19450 --customer "Sarah Johnson" --phone +1-614-555-1945 --incident-type collision --verified --upstream-validation pass --upstream-source front_desk`
9. `python ~/.openclaw/workspace/skills/oma-claims-pipeline/scripts/orchestrator_wrapper.py --artifacts-dir /path/to/artifacts --claim-id CLM-2026-0001`
10. `python ~/.openclaw/workspace/skills/oma-claims-pipeline/scripts/orchestrator_wrapper.py --artifacts-dir /path/to/artifacts --claim-id CLM-2026-0001 --invoke-next-cmd "python run_agent.py --agent {next_agent} --claim {claim_id}"`

Customer source of truth:

- `~/.openclaw/workspace/customers/tg_{telegram_id}/client.json`
- `~/.openclaw/workspace/customers/tg_{telegram_id}/policies/policy_<policy_id>.json`
- `~/.openclaw/workspace/customers/tg_{telegram_id}/claims/<claim_id>/claim.json`
- `~/.openclaw/workspace/customers/tg_{telegram_id}/claims/<claim_id>/photos/*`
- `~/.openclaw/workspace/customers/index.json` (phone -> customer_key, e.g. `tg_119450`)

Runtime note:

- Runtime flow uses `workspace/customers/*` only.
- Source policy files are imported explicitly via `--policies-dir` when needed.
