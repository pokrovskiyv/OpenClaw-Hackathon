---
name: oma-claims-pipeline
description: "Ohio Mutual Auto claims workflow for 6-role pipeline, voice-ready orchestration, and strict JSON handoff contracts. Keywords: insurance claims, multi-agent, front desk, fraud, finance."
---

# OMA Claims Pipeline

Use this skill to run a deterministic 7-stage insurance claim workflow (6 operational roles + 1 quality controller).

## When to Use

- Incoming motor claim must be processed through all business roles.
- Voice call ingress is used, but decision logic must remain role-based.
- You need auditable handoff across Front Desk -> Claims Officer -> Assessor -> Fraud Analyst -> Senior Reviewer -> Finance -> Claims Manager.

## Required Flow

1. Start with customer care triage:

- Ask if the customer is safe.
- Ask if there are injuries.
- If injury risk exists, instruct emergency call and pause standard flow.

2. Verify caller context (`registered customer`, `policy active`) before expensive processing.
3. Provide step-by-step incident guidance (photos, data exchange, police/reporting rules by state).
4. Collect FNOL essentials.
5. Execute roles in strict order:
   - `front_desk`
   - `claims_officer`
   - `assessor`
   - `fraud_analyst`
   - `senior_reviewer`
   - `finance`

- `claims_manager`

6. Persist full internal result and return short customer-safe summary.
7. Keep customer informed about next steps and expected timing until payout completion.

## Outcome Objectives

- Customer objective: clear guidance from accident start to payout completion with low stress.
- Operations objective: remove manual routine work via deterministic handoff and reusable artifacts.
- Business objective: profitable and defensible decisions while maintaining strong customer trust and referral potential.

## Role Prompts (source of truth)

- `references/roles/front_desk.md`
- `references/roles/claims_officer.md`
- `references/roles/assessor.md`
- `references/roles/fraud_analyst.md`
- `references/roles/senior_reviewer.md`
- `references/roles/finance.md`
- `references/roles/claims_manager.md`

## Output Contracts

- Every role returns valid JSON only.
- Every role includes `routing` or explicit skip reason.
- Every role (including front desk against caller input) includes `upstream_validation` with `status: pass|soft_fail|hard_fail`.
- Pipeline must proceed only when `upstream_validation.status = pass`.
- Roles 2-6 must include structured `input_assessment` with `prior_agent`, `quality (sufficient|partial|insufficient)`, `score`, and `issues`.
- Every role includes `customer_message` with both `voice_text` and `chat_text` that keep the same semantic intent.
- No silent fallback.
- If coverage is invalid, downstream roles must return skip/acknowledge artifacts.
- Human review escalation triggers: `fraud_score >= 46`, `approved_amount > 25000`, or Senior Reviewer decision `investigate|referred`.

## Operational Scripts

Run from the skill directory:

- Path validation for deployed OpenClaw home:
  - `python scripts/path_doctor.py --openclaw-home ~/.openclaw`
- Generate customer files from policy fixtures:
  - `python scripts/generate_customers.py --policies-dir /path/to/policies`
- Pre-auth check (registered customer + active policy + demo PIN rule):
  - `python scripts/preauth_check.py --policy OMA-2025-19450 --phone +1-614-555-1945 --pin 9450`
  - or with stronger identity binding: `python scripts/preauth_check.py --telegram-id 119450 --policy OMA-2025-19450 --phone +1-614-555-1945 --pin 9450`
- Validate upstream handoff JSON before next stage:
  - `python scripts/handoff_validate.py --role claims_officer --input /path/to/claims_officer_output.json`
- Orchestrator gate (validate sequentially and decide whether next agent can run):
  - `python scripts/orchestrator_wrapper.py --artifacts-dir /path/to/artifacts --claim-id CLM-2026-0001`
  - optional auto-invoke mode: `python scripts/orchestrator_wrapper.py --artifacts-dir /path/to/artifacts --claim-id CLM-2026-0001 --invoke-next-cmd "python run_agent.py --agent {next_agent} --claim {claim_id}"`
- Initialize claim folder and claim.json:
  - `python scripts/claim_init.py --telegram-id 119450 --claim-id CLM-2026-0001 --policy-id OMA-2025-19450 --incident-type collision --summary "rear-end at low speed"`
- Move claim through status state-machine:
  - `python scripts/claim_status.py --telegram-id 119450 --claim-id CLM-2026-0001 --to preauth_verified --reason "identity and policy verified"`
- Store incoming photo evidence for a claim:
  - `python scripts/photo_intake.py --claim-id CLM-2026-0001 --telegram-id 119450 --source /tmp/photo.jpg --part front_bumper --note "impact close-up"`
- Build deterministic pipeline plan after successful pre-auth:
  - `python scripts/workflow_plan.py --claim-id CLM-2026-0001 --policy OMA-2025-19450 --customer "Sarah Johnson" --phone +1-614-555-1945 --incident-type collision --verified`

## Data Layout

- Runtime uses customer records from `workspace/customers` only.
- No local policy bootstrap directory is required inside this skill.
- Customer profile: `../../customers/tg_{telegram_id}/client.json`
- Customer policies: `../../customers/tg_{telegram_id}/policies/policy_<policy_id>.json`
- Customer claims: `../../customers/tg_{telegram_id}/claims/<claim_id>/claim.json`
- Claim photos: `../../customers/tg_{telegram_id}/claims/<claim_id>/photos/*`
- Customer phone index: `../../customers/index.json`
- Role prompts: `references/roles/*.md`
- Integration notes: `references/voice-integration.md`
- Business requirements: `references/business-requirements.md`

## Information Architecture — Role-Based Data Access

The pipeline enforces **regulatory data separation** between damage assessment and financial data.

### Data Access Matrix

| Data Field | Front Desk | Claims Officer | Assessor | Fraud Analyst | Senior Reviewer | Finance |
|---|---|---|---|---|---|---|
| Claim details | YES | YES | YES | YES | YES | YES |
| Policy status | — | YES | YES (valid/invalid only) | YES | YES | YES |
| Coverage type | — | YES | YES | YES | YES | YES |
| **Deductible** | — | YES (produces) | **NO** | YES | YES | YES |
| **Coverage limit** | — | YES (produces) | **NO** | YES | YES | YES |
| Damage estimate | — | — | YES (produces) | YES | YES | YES |
| Fraud score | — | — | — | YES (produces) | YES | — |

### Why This Matters

- **Assessor firewall**: Regulators require separation between assessment and financial data. An assessor who sees policy limits may match estimates to those limits — this caused $4.1M in compliance fines.
- **Fraud cross-reference**: Fraud Analyst MUST see both damage estimates AND policy limits to detect padding fraud ($8.3M in losses from inflated estimates matched to limits).
- **Customer transparency**: Voice agent and Front Desk have read access to claim status — customer never hears "call another department."
- **Speed**: Pipeline targets 48h resolution for routine claims — no unnecessary bottlenecks or handoff delays.

### Enforcement

- The orchestrator filters Claims Officer financial fields before passing context to Assessor
- Assessor prompt includes explicit compliance firewall instructions
- Fraud Analyst prompt explicitly requires policy limit cross-referencing
- `handoff_validate.py` validates output contracts per role

## Prohibitions

- Do not skip roles in the sequence.
- Do not produce final customer decision before `senior_reviewer`.
- Do not trigger payment before `finance` validation.
- Do not expose internal fraud heuristics in customer-facing voice output.
- Do not pass `deductible` or `coverage_limit` to the Assessor.

## References

- `references/voice-integration.md`
- `references/business-requirements.md`
- `references/customer-journey-workflow.md`
