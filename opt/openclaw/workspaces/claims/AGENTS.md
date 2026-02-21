# Claims Workspace Instructions

Scope: everything under `opt/openclaw/workspaces/claims/`.

## Purpose
This workspace validates policy and coverage applicability for reported claims.

## Mandatory Output Fields
Every coverage assessment must include:
- `policy_status`
- `coverage_valid` (`true`, `false`, or `"partial"`)
- `coverage_type`
- `deductible`
- `coverage_limit`
- `exclusions_triggered` (array of strings)
- `recommendation` (`proceed`, `deny`, `partial_deny`, `escalate`)

## Business Rules
- If policy is expired, recommendation must be `deny`.
- If multiple coverage options apply, choose the most beneficial valid option for the customer.
- Policies younger than 60 days must be flagged for Fraud Analyst review.
- Claims Officer does not make final claim decisions; it only confirms or rejects coverage basis.
- Include a mutual evaluation note for Front Desk handoff quality.

## Access
Claims Officer has policy access and may use policy terms, deductible schedules, and limits data.
