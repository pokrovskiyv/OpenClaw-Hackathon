# TASK-07: Claims Officer Agent
> Status: DONE → Goal: improve coverage validation, UM/UIM logic, multi-coverage routing

## Context

Claims Officer is Agent #2 — verifies policy validity, determines applicable coverage, deductible, and limits. One of three agents with full policy access.

**Key output fields:** policy_status, coverage_valid (true/false/"partial"), coverage_type, deductible, coverage_limit, exclusions_triggered, recommendation (proceed/deny/partial_deny/escalate), confidence.

**Business rules:**
- Expired policy → recommend denial
- Multiple applicable coverages → choose most favorable for client (e.g., glass: Comprehensive $50 deductible vs Collision $500)
- Policy < 60 days → flag for Fraud Analyst
- Does NOT make decisions — only confirms/denies coverage
- **Peer assessment:** evaluates Front Desk output quality
- **UM/UIM verification (ORC 3937.18):** Check UM/UIM for hit-and-run or insufficient at-fault coverage. Missing signed rejection form = coverage by operation of law.

**Confidence Score** (Section 5.4):
- Threshold: < 70 → escalate to human coverage specialist
- Penalty factors: multiple applicable coverages (−15), unclear exclusion (−20), policy < 60 days (−5), partial coverage (−10), non-standard terms (−15)

## Current State

- `agents/claims_officer.md` exists and is deployed
- UM/UIM verification added per ORC 3937.18
- Multi-coverage routing logic present but needs testing

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Prompt Engineer | prompt-engineer | Review and improve claims_officer.md |
| Pipeline Analyst | eval-analyst | Analyze coverage validation accuracy across scenarios |
| Domain Expert | insurance-analyst | Verify UM/UIM rules, coverage routing edge cases |
| Runner | Bash | Execute pipeline runs and benchmark |

## Work Plan

1. **Bash**: Run baseline benchmark
2. **eval-analyst**: Analyze Claims Officer performance:
   - Check coverage_valid for each scenario (especially TC-004 expired, TC-006 excluded, TC-007 hit-and-run)
   - Check UM/UIM handling for hit-and-run scenarios
   - Check multi-coverage routing (is cheapest deductible chosen?)
   - Check exclusions_triggered accuracy
   - Verify policy_status reflects actual policy state
3. **insurance-analyst**: Research edge cases:
   - UM/UIM stacking rules in Ohio
   - Permissive use driver exclusions
   - Material misrepresentation rules
   - Grace period after policy expiration
4. **prompt-engineer**: Improve claims_officer.md:
   - Strengthen UM/UIM verification logic
   - Add multi-coverage routing examples
   - Ensure peer assessment of Front Desk is meaningful
   - Add edge cases found by insurance-analyst
5. **Bash**: Re-run benchmark

## Key Files

- `agents/claims_officer.md` — agent prompt (PRIMARY edit target)
- `runner.py` — policy data feeding, whitelist logic
- `test_cases/all_scenarios.json` — coverage-related assertions
- `docs/business-analysis.md` — Section 6.2 (lines 576-587)

## Acceptance Criteria

- [ ] coverage_valid correct for all 36 scenarios
- [ ] Expired policy (TC-004) → coverage_valid=false, recommendation=deny
- [ ] Hit-and-run (TC-007) → UM/UIM check performed
- [ ] Multi-coverage routing selects cheapest deductible for client
- [ ] Policy < 60 days flagged for Fraud Analyst
- [ ] Exclusions correctly identified (DUI, commercial use, racing, etc.)
- [ ] No regression in benchmark score

## Verification

```bash
cd openclaw-hackathon
python3 benchmark.py --no-llm-judge
python3 loop.py --run-once --scenario TC-004  # Expired policy
python3 loop.py --run-once --scenario TC-007  # Hit-and-run (UM/UIM test)
```

## Constraints

- Do NOT modify runner.py whitelist logic
- Do NOT add decision-making to Claims Officer (it only validates coverage)
- Preserve ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER whitelist
