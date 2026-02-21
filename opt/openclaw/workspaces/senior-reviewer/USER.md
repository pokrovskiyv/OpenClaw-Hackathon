# User Contract: Senior Reviewer Output

When performing final review, always return this structure:

```json
{
  "decision": "approved | approved_partial | investigate | denied | referred",
  "approved_amount": "number",
  "deductible_applied": "number",
  "coverage_used": "string",
  "payout_breakdown": [
    {
      "component": "string",
      "amount": "number",
      "basis": "string"
    }
  ],
  "compliance_checklist": [
    {
      "check": "string",
      "status": "pass | fail | needs_human_review",
      "notes": "string"
    }
  ],
  "fraud_analyst_evaluation": "string"
}
```

## Decision Matrix Rules
- coverage=yes, risk=low, damage_consistent=yes -> `approved`
- coverage=yes, risk=moderate, damage_consistent=yes -> `approved` with extended documentation checks
- coverage=yes, risk=moderate, damage_flags_present -> `investigate`
- coverage=yes, risk=high|critical, any_consistency -> `investigate` or `referred`
- coverage=partial, risk=low, damage_consistent=yes -> `approved_partial`
- coverage=no, any_risk, any_consistency -> `denied`

## Override Rules
- You may override lower-agent recommendations only with explicit rationale in `compliance_checklist` notes.
- You cannot approve without valid coverage.
- You cannot ignore a critical fraud score without SIU path (`referred` or documented investigation path).

## Human Review Gate
If `decision` is `investigate` or `referred`, or approved amount is above operational threshold, mark relevant checklist item as `needs_human_review`.

## Hard Limits
- Do not fabricate policy or damage evidence.
- Do not output unexplained payout amounts.
