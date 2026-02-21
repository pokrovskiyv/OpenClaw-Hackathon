# Skill: payment-execution

## Purpose
Execute approved payouts with transparent formulas, policy-limit enforcement, and subrogation/rental handling.

## Input
- Senior Reviewer output (`decision`, approved values, coverage path)
- Policy limits and payment constraints
- Assessor values (for ACV/salvage when total loss)
- Medical billing values for PIP/MedPay when applicable

## Output Schema
```json
{
  "payment_authorized": true,
  "payment_details": {
    "amount": "number",
    "calculation": ["string"],
    "method": "ACH | check | two_party_check | wire",
    "recipient": "string"
  },
  "subrogation": {"applicable": false, "target_insurer": "string|null", "demand_amount": "number"},
  "rental_reimbursement": {"applicable": false, "amount": "number", "basis": "string"},
  "financial_summary": "string",
  "senior_reviewer_evaluation": "string"
}
```

## Authorization Rules
1. Payment requires Senior Reviewer approval.
2. If approval is missing or decision is non-payable (`investigate`, `referred`, `denied`), set `payment_authorized=false`.

## Formula Rules
1. Repair payout: `MIN(approved_amount - deductible_applied, coverage_limit)`.
2. Total-loss payout: `MIN(vehicle_acv - deductible_applied - salvage_value, coverage_limit) + rental_reimbursement.amount`.
3. Medical payout: `MIN(medical_amount, medpay_limit)` (typically no deductible).
4. Never exceed policy limits.

## Operational Rules
- Emit full calculation trace in `payment_details.calculation` (show-the-math requirement).
- If lienholder exists, enforce `method = two_party_check`.
- If arithmetic inputs conflict or reconciliation fails, stop and escalate (`payment_authorized=false`).
- If subrogation applies, set subrogation fields and mark demand scheduling within 30 days in summary/calculation trace.

## Mutual Evaluation Requirement
Always include `senior_reviewer_evaluation` with concise feedback about Senior Reviewer handoff completeness.

## Prohibited Actions
- Do not disburse funds on unresolved numeric mismatch.
- Do not bypass policy limits or approval prerequisites.
