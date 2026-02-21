# User Contract: Finance Output

When executing finance steps, always return this structure:

```json
{
  "payment_authorized": true,
  "payment_details": {
    "amount": "number",
    "calculation": ["string"],
    "method": "ACH | check | two_party_check | wire",
    "recipient": "string"
  },
  "subrogation": {
    "applicable": false,
    "target_insurer": "string|null",
    "demand_amount": "number"
  },
  "rental_reimbursement": {
    "applicable": false,
    "amount": "number",
    "basis": "string"
  },
  "financial_summary": "string",
  "senior_reviewer_evaluation": "string"
}
```

## Formula Rules
- Repair: `MIN(approved_amount - deductible_applied, coverage_limit)`
- Total loss: `MIN(vehicle_acv - deductible_applied - salvage_value, coverage_limit) + rental_reimbursement.amount`
- Medical (PIP/MedPay): `MIN(medical_amount, medpay_limit)` (typically no deductible)

## Required Rule Checks
- `payment_authorized` must be `false` if Senior Reviewer approval is missing.
- Amount must not exceed policy limit.
- Include explicit step-by-step math in `payment_details.calculation`.
- If lienholder exists, set payment method to `two_party_check`.
- If reconciliation fails, set `payment_authorized=false` and escalate in `financial_summary`.
- If subrogation is applicable, include demand setup within 30 days.

## Hard Limits
- Do not execute payment on unresolved arithmetic mismatch.
- Do not hide adjustments or rounding behavior.
