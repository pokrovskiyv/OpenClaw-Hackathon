# Skill: claim-checklist

## Purpose
Evaluate policy validity and claim coverage basis from intake + policy records.

## Input
- FNOL payload from Front Desk
- Policy record (status, effective dates, terms, deductibles, limits, exclusions)
- Loss context (incident date, category, reported damage)

## Output Schema
```json
{
  "policy_status": "active | expired | cancelled | pending",
  "coverage_valid": true,
  "coverage_type": "string",
  "deductible": "number|string",
  "coverage_limit": "number|string",
  "exclusions_triggered": ["string"],
  "recommendation": "proceed | deny | partial_deny | escalate",
  "frontdesk_evaluation": "string"
}
```

## Coverage Rules
1. Validate policy status at the time of loss.
2. If policy is expired at time of loss, set `recommendation` to `deny`.
3. If multiple valid coverages apply, pick the most beneficial option for the customer.
4. Set `coverage_valid` to:
   - `true` when loss is fully covered,
   - `false` when no applicable coverage exists,
   - `"partial"` when only part is covered.
5. Enumerate specific exclusion clauses in `exclusions_triggered`.

## Fraud-Review Trigger Rule
- If policy age is below 60 days, add a fraud-review note for Fraud Analyst routing.
- Use `recommendation = "escalate"` when fraud review must occur before proceeding.

## Recommendation Guidance
- `proceed`: coverage validated with no blocking concerns.
- `deny`: coverage not valid (for example, expired policy or direct exclusion).
- `partial_deny`: part of claim is not covered.
- `escalate`: manual review needed (including <60-day policy trigger).

## Mutual Evaluation Requirement
Always include a concise `frontdesk_evaluation` comment covering:
- intake completeness,
- category appropriateness,
- critical omissions impacting coverage verification.

## Prohibited Actions
- Do not make final claim approval or payout decisions.
- Do not make fraud determinations.
