# TASK-10: Senior Reviewer Agent
> Status: DONE → Goal: verify decision matrix, ROR logic, override documentation

## Context

Senior Reviewer is Agent #5 — makes the final claim decision by synthesizing all previous agent outputs. Last line of defense for the company AND final protector of claimant rights. One of three agents with full policy access.

**Decision matrix:**
| Coverage | Fraud Risk | Damage Consistent | Decision |
|----------|-----------|-------------------|---------|
| Yes | Low | Yes | approved |
| Yes | Moderate | Yes | approved + extended documentation |
| Yes | Moderate | Flags | investigate |
| Yes | High/Critical | Any | investigate / referred (SIU) |
| Partial | Low | Yes | approved_partial |
| No | Any | Any | denied |

**Key output fields:** decision (approved/approved_partial/investigate/denied/referred/ror), approved_amount, deductible_applied, coverage_used, payout_breakdown, compliance_checklist, confidence.

**Reservation of Rights (ROR):** When coverage formally applies but grounds for possible denial exist (e.g., suspected material misrepresentation, borderline exclusion). ROR allows processing while preserving right to later deny — standard practice to prevent bad faith claims.

**Override rights:** Can override lower agent recommendations with justification. CANNOT: approve without coverage, ignore critical fraud_score without SIU.

**Stakeholder priority rules (Section 7.7):**
1. Fast-track + elevated fraud → cancel fast-track, full review
2. Assessment ≈ coverage limit → do NOT adjust, pass to fraud analyst
3. Client requests status → provide in customer language
4. High amount ($25K+) → escalate to Claims Director regardless

**Compliance checklist output:**
- [ ] Decision within 30 days of FNOL (or extension documented)
- [ ] Claimant notification letter drafted
- [ ] If denied: specific policy language cited
- [ ] If denied: appeal rights explained
- [ ] Full audit trail
- [ ] No conflicts of interest

**Confidence Score** (Section 5.4):
- Threshold: < 70 → escalate to Claims Director
- Penalty factors: insufficient handoff (−20), 2+ partial handoffs (−15), override needed (−15), assessor-fraud contradiction (−20), grey zone fraud + approve (−10)

## Current State

- `agents/senior_reviewer.md` exists with decision matrix
- ROR decision type added to taxonomy
- Need to verify override logic and compliance checklist output

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Prompt Engineer | prompt-engineer | Review and improve senior_reviewer.md |
| Pipeline Analyst | eval-analyst | Analyze decision accuracy across scenarios |
| Runner | Bash | Execute pipeline runs and benchmark |

## Work Plan

1. **Bash**: Run baseline benchmark
2. **eval-analyst**: Analyze Senior Reviewer performance:
   - TC-001: decision=approved, correct amount
   - TC-002: decision should reflect elevated fraud indicators
   - TC-003: decision handling for total loss
   - TC-004: decision=denied with specific policy citation
   - TC-005: decision=investigate or referred (staged accident)
   - TC-006: decision=denied (excluded coverage)
   - TC-007: decision appropriate for hit-and-run
   - Verify compliance_checklist is output
   - Check payout_breakdown includes deductible_applied
   - Verify override justifications when used
3. **prompt-engineer**: Improve senior_reviewer.md:
   - Strengthen decision matrix with more edge cases
   - Ensure ROR logic is clear (when to use vs deny vs investigate)
   - Verify all 4 stakeholder priority rules are in prompt
   - Ensure compliance checklist is generated
   - Preserve 48h resolution target and single-pass decision-making
4. **Bash**: Re-run benchmark

## Key Files

- `agents/senior_reviewer.md` — agent prompt (PRIMARY edit target)
- `runner.py` — full pipeline context for Senior Reviewer
- `test_cases/all_scenarios.json` — decision-related assertions
- `docs/business-analysis.md` — Section 6.5 (lines 622-643), Section 7.7 (lines 813-835)

## Acceptance Criteria

- [ ] Decision correct for all 36 scenarios
- [ ] TC-004: denied with specific policy exclusion cited
- [ ] TC-005: investigate or referred (never approved for staged accident)
- [ ] approved_amount calculated correctly (damage − deductible, ≤ limit)
- [ ] compliance_checklist output present
- [ ] Override justification provided when overriding lower agent
- [ ] ROR used appropriately (borderline coverage, not as default)
- [ ] No regression in benchmark score

## Verification

```bash
cd openclaw-hackathon
python3 benchmark.py --no-llm-judge
python3 loop.py --run-once --scenario TC-004  # Expired policy → denied
python3 loop.py --run-once --scenario TC-005  # Staged accident → investigate
```

## Constraints

- Preserve 48h resolution target in prompt
- Preserve single-pass decision-making principle
- Do NOT allow approving without coverage
- Do NOT allow ignoring critical fraud_score without SIU referral
