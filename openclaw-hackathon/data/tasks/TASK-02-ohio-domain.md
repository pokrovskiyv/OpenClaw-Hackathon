# TASK-02: Ohio Insurance Domain Knowledge
> Status: DOC → Goal: verify all regulatory references, validate coverage taxonomy, check for missing regulations

## Context

Section 4 of the PRD covers US auto insurance mechanics specific to Ohio — a tort (at-fault) state. This is the domain foundation all 6 pipeline agents rely on. Errors here cascade through the entire system.

Key areas:
1. **Coverage taxonomy**: Liability (BI/PD), Collision, Comprehensive, UM/UIM, PIP/MedPay
2. **Key terms**: deductible, coverage limit, exclusions, total loss (75% ACV), subrogation
3. **Ohio regulatory requirements**: OAC 3901-1-54 timelines, bad faith doctrine, comparative fault
4. **Agent-specific implications**: what each coverage type means for each agent

Critical Ohio-specific rules:
- **OAC 3901-1-54**: Claims handling timelines (15-day ack, 21-day investigation, 21-day decision, 10-day payment)
- **ORC 3901.21**: Unfair settlement practices (statutory bad faith)
- **ORC 2315.33**: Modified comparative fault with 51% bar
- **ORC 2315.21(D)**: Punitive damages up to 2x compensatory
- **ORC 4505.11**: Salvage title threshold (total loss)
- **ORC 3937.18**: UM/UIM offering requirement
- **ORC 3999.41-3999.49**: Mandatory fraud reporting

## Current State

- Section 4 is written but needs verification against current Ohio law
- PIP/MedPay correctly noted as optional in Ohio (tort state)
- Total loss 75% ACV noted as company policy (not state mandate)
- UM/UIM verification added in TASK-07 references ORC 3937.18

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Domain Expert | insurance-analyst | Verify every ORC/OAC reference against current Ohio law. Identify missing regulations. Check coverage edge cases. |

## Work Plan

1. **Verify OAC 3901-1-54 timelines**: Confirm each deadline (15d, 21d, 21d, 10d) is accurate.
2. **Verify bad faith doctrine**: ORC 3901.21, *Zoppo v. Homestead* (1994), ORC 2315.21(D) punitive damages.
3. **Verify comparative fault**: ORC 2315.33 — 51% bar, subrogation blocking, deductible inclusion in demand.
4. **Verify UM/UIM**: ORC 3937.18 — offering requirement, absence of rejection form = coverage by law.
5. **Verify total loss**: ORC 4505.11 — salvage title vs total loss threshold distinction.
6. **Verify fraud reporting**: ORC 3999.41-3999.49 — mandatory reporting requirements and thresholds.
7. **Check missing regulations**: Prompt Payment Act, UM/UIM stacking, grace periods, material misrepresentation.
8. **Validate coverage edge cases**: Hit-and-run (Collision vs UMPD), rideshare gaps, permissive use, glass-only claims.

## Key Files

- `docs/business-analysis.md` — Section 4 (lines 104-179)
- `agents/claims_officer.md` — uses coverage rules
- `agents/fraud_analyst.md` — uses fraud reporting rules
- `agents/senior_reviewer.md` — uses bad faith doctrine
- `agents/finance.md` — uses subrogation and payment rules

## Acceptance Criteria

- [ ] Every ORC/OAC citation verified against current Ohio law
- [ ] *Zoppo v. Homestead* case details confirmed
- [ ] Modified comparative fault 51% bar confirmed
- [ ] UM/UIM offering requirement confirmed
- [ ] Total loss 75% ACV confirmed as company policy (not state mandate)
- [ ] Fraud reporting requirements documented with specific thresholds
- [ ] At least 3 missing edge cases or regulations identified

## Constraints

- Do NOT change agent prompts — only document findings
- Focus on Ohio-specific rules, not general US insurance
