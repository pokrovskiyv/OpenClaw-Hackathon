# TASK-17: Business Priorities and Cost of Error
> Status: DOC → Goal: verify fraud figures, validate priority hierarchy, check agent mappings

## Context

Section 9 of the PRD ranks business priorities by cost of error, from critical (fraud — hundreds of thousands) to basic (missed subrogation — slow accumulating loss). Each priority maps to specific agents and metrics.

Priority hierarchy: **Compliance > Fraud Detection > Customer Experience > Speed**

Priority breakdown:
1. **CRITICAL: Fraud Detection** — ~10% of P&C payouts, $50K-$150K per staged accident, $8.3M/year (Priya). Estimate-to-Limit as strongest signal. Responsible: Fraud Analyst + Senior Reviewer.
2. **CRITICAL: Compliance & Information Barriers** — $4.1M fines (Rachel). Blind Assessment Policy. ORC 3901.21, *Zoppo v. Homestead*. Responsible: runner.py + Assessor + Senior Reviewer.
3. **HIGH: Coverage Validation** — errors costly both ways (paying uncovered = pure loss, denying covered = bad faith). Responsible: Claims Officer.
4. **HIGH: Coverage Routing** — wrong coverage = $450 out of pocket (glass example). Responsible: Claims Officer.
5. **MEDIUM: Damage Assessment** — 75% ACV total loss rule. Responsible: Assessor.
6. **BASIC: Subrogation Identification** — no immediate crisis but accumulated misses = hundreds of thousands/year. Responsible: Finance.
7. **MEDIUM: Customer Experience** — $4,200/year per lost customer (Marcus). claim_status_update mapping. Responsible: Front Desk.
8. **MEDIUM: Processing Speed** — $340/claim, $4M+/year (Daniel). 48h SLA via fast-track. Responsible: Front Desk.

## Current State

- Section 9 is written with $ figures from Secret Addition stakeholders
- Priority hierarchy is documented but needs verification against agent prompt implementations
- Agent mappings need cross-checking with actual prompt content

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Domain Expert | insurance-analyst | Verify fraud cost figures, validate priority hierarchy against industry practice |
| Pipeline Analyst | eval-analyst | Check that each agent prompt actually implements the priority rules mapped to it |

## Work Plan

1. **insurance-analyst**: Verify business priority claims:
   - ~10% fraud rate in P&C — check CAIF/III data
   - $50K-$150K per staged accident — validate range
   - $8.3M/year fraud losses for regional insurer — check reasonableness
   - $4.1M compliance fines — verify ORC penalty structures
   - $4,200/year customer churn cost — validate CLV for auto insurance
   - $340/claim delay cost — validate industry benchmark

2. **eval-analyst**: Verify agent prompt alignment with priorities:
   - Read each agent prompt (front_desk.md through finance.md)
   - Check: does Fraud Analyst mention Estimate-to-Limit cross-reference?
   - Check: does Claims Officer implement multi-coverage routing (glass example)?
   - Check: does Front Desk generate claim_status_update?
   - Check: does Front Desk implement fast_track logic?
   - Check: does Finance implement subrogation identification?
   - Run benchmark scenarios that test each priority (TC-002 for fraud, TC-004 for expired policy, TC-006 for excluded coverage)

## Key Files

- `docs/business-analysis.md` — Section 9 (lines 898-959)
- `agents/front_desk.md` — fast_track, claim_status_update
- `agents/claims_officer.md` — coverage routing
- `agents/fraud_analyst.md` — Estimate-to-Limit, fraud scoring
- `agents/assessor.md` — total loss rule
- `agents/finance.md` — subrogation identification
- `agents/senior_reviewer.md` — override rules per priority hierarchy

## Acceptance Criteria

- [ ] All $ figures verified or marked as estimates with sources
- [ ] Priority hierarchy (Compliance > Fraud > CX > Speed) confirmed as industry-standard
- [ ] Each agent prompt contains the rules mapped to it in Section 9
- [ ] Estimate-to-Limit cross-reference present in fraud_analyst.md
- [ ] claim_status_update present in front_desk.md
- [ ] fast_track logic present in front_desk.md
- [ ] Subrogation identification present in finance.md
- [ ] Glass routing example (Collision $500 vs Comprehensive $50) handled by claims_officer.md

## Constraints

- Do NOT modify agent prompts — only document gaps
- If prompts are missing mapped rules, list them as findings for TASK-06 through TASK-11
