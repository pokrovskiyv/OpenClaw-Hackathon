# Ohio Mutual Auto — Business Requirements

## Goal

Automate end-to-end auto-claim handling with a deterministic 6-role process while preserving compliance, customer fairness, and financial control.

## Required Roles

1. Front Desk
2. Claims Officer
3. Assessor
4. Fraud Analyst
5. Senior Reviewer
6. Finance

## Core Business Priorities

- Detect fraud early and document evidence.
- Validate coverage against active policy terms.
- Route to the most favorable eligible coverage path for the customer.
- Assess damages consistently and enforce total-loss thresholds.
- Identify subrogation opportunities when third-party liability exists.

## Output Expectations

- Each role returns structured JSON.
- Every handoff is explicit and auditable.
- Final decision must be explainable and legally defensible.
- Customer-facing response must be concise and safe.

## Compliance Constraints

- Denials require specific policy-grounded reasoning.
- Payment cannot run before senior review approval.
- Investigation paths must preserve full evidence trail.
- Sensitive internal fraud logic must not be exposed in customer messaging.
