# TASK-15: Stakeholder Priority Resolution
> Status: DONE → Goal: verify priority hierarchy implemented in prompts, test conflict scenarios

## Context

Section 7.7 defines how conflicting stakeholder priorities are resolved. Fixed hierarchy based on cost of error:

**Priority: Compliance > Fraud Detection > Customer Experience > Speed**

| Conflict | Resolution | Rationale |
|----------|-----------|-----------|
| Speed vs Compliance | **Compliance** | $4.1M fines > $4M delays |
| Transparency vs Fraud | **Neutral language** | Client gets status, investigation not compromised |
| Speed vs Fraud | **Fraud Detection** | $8.3M fraud > $4M delays. Fast-track cancelled on fraud indicators |
| Full access vs Compliance | **Field-level filtering** | Blind Assessment — assessor isolated, fraud analyst full access |

**Concrete rules for Senior Reviewer:**
1. Fast-track + elevated fraud → cancel fast-track, full review
2. Assessment ≈ coverage limit → do NOT adjust, pass to fraud analyst
3. Client requests status → provide in customer language
4. High amount ($25K+) → escalate to Claims Director regardless

## Current State

- Priority hierarchy documented in PRD
- Rules should be embedded in relevant agent prompts
- Need to verify each rule is actually in the corresponding prompt

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Pipeline Analyst | eval-analyst | Read all agent prompts, verify priority rules are embedded |
| Domain Expert | insurance-analyst | Validate hierarchy against industry best practice |
| Runner | Bash | Test conflict scenarios |

## Work Plan

1. **eval-analyst**: Check each prompt for priority rules:
   - `agents/senior_reviewer.md`: All 4 concrete rules present?
   - `agents/front_desk.md`: fast_track logic with fraud indicator check?
   - `agents/front_desk.md`: claim_status_update with neutral language?
   - `agents/fraud_analyst.md`: never reveals investigation to client?
   - `agents/assessor.md`: Blind Assessment maintained?
   - `agents/finance.md`: payment timing rules per OAC 3901-1-54?

2. **insurance-analyst**: Validate priority hierarchy:
   - Is Compliance > Fraud Detection standard in insurance?
   - Are there situations where Speed should override?
   - Is the $4.1M vs $8.3M vs $4M ranking defensible?

3. **Bash**: Test conflict scenarios:
   - Find or identify scenarios where fast-track + fraud indicators overlap
   - Run scenarios where assessment ≈ coverage limit
   - Verify Senior Reviewer cancels fast-track on fraud

4. **Document** which rules are missing from which prompts

## Key Files

- `agents/senior_reviewer.md` — should contain all 4 concrete rules
- `agents/front_desk.md` — fast_track + claim_status_update
- `agents/fraud_analyst.md` — non-disclosure
- `runner.py` — Blind Assessment whitelist
- `docs/business-analysis.md` — Section 7.7 (lines 813-835)

## Acceptance Criteria

- [ ] All 4 Senior Reviewer concrete rules present in prompt
- [ ] fast_track cancelled when fraud indicators detected
- [ ] claim_status_update uses neutral language (not "fraud analysis")
- [ ] Blind Assessment maintained via runner.py whitelist
- [ ] Assessment ≈ limit NOT adjusted by Senior Reviewer
- [ ] $25K+ amount triggers escalation regardless of other factors
- [ ] Priority hierarchy validated as industry-standard

## Verification

```bash
cd openclaw-hackathon
# Run a scenario that should trigger priority conflict
python3 loop.py --run-once --scenario TC-002  # Suspicious claim
```

## Constraints

- Do NOT change the priority hierarchy without explicit approval
- If a rule is missing from a prompt, add it (but preserve existing rules)
