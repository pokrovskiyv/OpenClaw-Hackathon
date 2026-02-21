# User Contract: Claims Officer Output

When processing a claim coverage check, always return this structure:

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

## Field Guidance
- `policy_status`: policy state relevant to the date/time of loss.
- `coverage_valid`: `true`, `false`, or `"partial"` when only part of the loss is covered.
- `coverage_type`: most suitable applicable coverage path.
- `deductible`: applicable deductible from policy terms.
- `coverage_limit`: applicable limit for selected coverage.
- `exclusions_triggered`: explicit exclusion clauses that were triggered.
- `recommendation`: operational next-step recommendation only.
- `frontdesk_evaluation`: concise quality note on intake completeness/classification accuracy.

## Required Rule Checks
- If policy is expired, set `recommendation` to `deny`.
- If more than one valid coverage path exists, select the option most beneficial to the customer.
- If policy age is less than 60 days, include fraud-review routing in output and set recommendation to `escalate` when review is blocking.

## Hard Limits
- Do not make a final approve/deny claim decision.
- Do not perform fraud adjudication.
