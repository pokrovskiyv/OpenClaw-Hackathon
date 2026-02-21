# Skill: final-decision

## Purpose
Synthesize prior-agent outputs into a final decision recommendation with payout structure and compliance checks.

## Input
- Front Desk output
- Claims Officer output
- Assessor output
- Fraud Analyst output
- Policy and coverage data (for authorized use)

## Output Schema
```json
{
  "decision": "approved | approved_partial | investigate | denied | referred",
  "approved_amount": "number",
  "deductible_applied": "number",
  "coverage_used": "string",
  "payout_breakdown": [{"component": "string", "amount": "number", "basis": "string"}],
  "compliance_checklist": [{"check": "string", "status": "pass | fail | needs_human_review", "notes": "string"}],
  "fraud_analyst_evaluation": "string"
}
```

## Decision Matrix
1. coverage=yes, risk=low, damage_consistent=yes -> `approved`
2. coverage=yes, risk=moderate, damage_consistent=yes -> `approved` + extended documentation
3. coverage=yes, risk=moderate, damage_flags_present -> `investigate`
4. coverage=yes, risk=high|critical, any_consistency -> `investigate` or `referred` (SIU path)
5. coverage=partial, risk=low, damage_consistent=yes -> `approved_partial`
6. coverage=no, any_risk, any_consistency -> `denied`

## Payout Rules
- `approved_amount` must be derived from covered components only.
- `deductible_applied` must reflect policy terms and selected coverage.
- `payout_breakdown` must reconcile to `approved_amount`.

## Override Rule
- Senior Reviewer may override lower recommendations only with explicit rationale captured in `compliance_checklist`.

## Non-Negotiable Constraints
- Never approve without valid coverage.
- Never ignore critical fraud score without SIU handling (`referred` or explicit investigation route).

## Human Specialist Gate
Mark as recommendation for human specialist when:
- decision is `investigate` or `referred`, or
- approved amount exceeds operational threshold.

Record this gate in `compliance_checklist` with `needs_human_review`.

## Mutual Evaluation Requirement
Always include `fraud_analyst_evaluation` with concise feedback on Fraud Analyst handoff quality.

## Prohibited Actions
- Do not produce unsupported final payouts.
- Do not bypass compliance checks.
