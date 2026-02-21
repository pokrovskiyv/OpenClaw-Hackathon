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

## Stakeholder Requirements

### Operations (COO) — Speed
- Target: 48h claim resolution for routine cases (saves $340/claim, $4M+/year)
- No handoff bottlenecks — each agent has the data it needs to decide in a single pass
- If an agent needs information, give it access — don't create inter-department delays

### Compliance (CCO) — Regulatory Separation
- Assessor MUST NOT see policy limits (`deductible`, `coverage_limit`)
- Damage assessment must be independent of financial data
- Prior violation: assessor matching estimates to policy limits caused $4.1M in fines
- Every access permission is a liability — grant only what each role strictly needs

### Customer Experience (CX Lead) — Transparency
- Customer never hears "I can't see that" or "call another department"
- Front desk and voice agent provide status updates without transfers
- Single point of contact from first call to payout completion
- Average policy is worth $4,200/year — losing a customer over a bad experience is costly

### Fraud Prevention (Fraud Lead) — Cross-Referencing
- Fraud Analyst MUST see both damage estimates AND policy limits
- Padding detection requires comparing estimates to coverage limits
- Prior losses: $8.3M from inflated estimates matched to policy limits
- Walling off fraud from financial data makes fraud detection impossible

### How These Requirements Are Resolved

The four demands conflict on the surface but resolve through **role-based data access**:

1. **Assessor is firewalled** from financial data → satisfies Compliance
2. **Fraud Analyst receives both** damage and financial data → satisfies Fraud Prevention
3. **Voice/Front Desk have read access** to claim status → satisfies CX
4. **Pipeline runs without bottlenecks**, each agent has what it needs → satisfies Operations

## Compliance Constraints

- Denials require specific policy-grounded reasoning.
- Payment cannot run before senior review approval.
- Investigation paths must preserve full evidence trail.
- Sensitive internal fraud logic must not be exposed in customer messaging.
- Assessor must not have access to policy deductible or coverage limit values.
