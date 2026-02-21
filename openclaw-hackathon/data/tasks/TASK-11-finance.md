# TASK-11: Finance Agent
> Status: DONE → Goal: verify payment formulas, subrogation logic, rental reimbursement

## Context

Finance is Agent #6 — executes approved payments, manages subrogation, handles rental car reimbursement. Third agent with full policy access. Forms the decision and calculation but does NOT execute the transaction (hackathon scope limitation).

**Key output fields:** payment_authorized, payment_details (amount, calculation, method, recipient), subrogation (applicable, target_insurer, demand_amount), rental_reimbursement, financial_summary, confidence.

**Payment formulas:**
- Repair: `MIN(approved_amount − deductible, coverage_limit)`
- Total loss: `MIN(ACV − deductible − salvage_value, coverage_limit) + rental`
- Medical (PIP/MedPay): `MIN(medical_amount, MedPay_limit)`, usually no deductible

**Payment authorization checklist:**
- [ ] Senior Reviewer decision = "approved" or "approved_partial"
- [ ] Approved amount specified and within policy limits
- [ ] Deductible correctly applied
- [ ] No SIU hold or investigation pending
- [ ] Claimant identity verified
- [ ] Payment destination confirmed

**Subrogation rules:**
- applicable=true when at-fault party data exists
- Demand includes client's deductible (OAC 3901-1-54(H)(10))
- Filed within 30 days
- Blocked when insured's fault >= 51% (ORC 2315.33 modified comparative fault)
- Lienholder gets two-party check

**Confidence Score** (Section 5.4):
- Threshold: < 75 (highest of all agents — financial errors = direct monetary loss)
- Penalty factors: calculation divergence > 5% (−25), complex subrogation (−15), lienholder (−5), unknown salvage value (−15), non-standard formula (−10)

## Current State

- `agents/finance.md` exists
- Payment formulas documented
- Subrogation logic present
- Need to verify accuracy against all scenarios

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Prompt Engineer | prompt-engineer | Review and improve finance.md |
| Pipeline Analyst | eval-analyst | Analyze payment accuracy, subrogation detection |
| Domain Expert | insurance-analyst | Verify Ohio subrogation rules, payment regulations |
| Runner | Bash | Execute pipeline runs and benchmark |

## Work Plan

1. **Bash**: Run baseline benchmark
2. **eval-analyst**: Analyze Finance output:
   - Check payment_authorized matches decision (never true for denied/investigate)
   - Verify payment formulas applied correctly per scenario
   - Check subrogation.applicable for scenarios with at-fault third party
   - Check rental_reimbursement.applicable when applicable
   - Verify skip pattern for denied coverage scenarios
   - Check deductible correctly applied in all payment calculations
3. **insurance-analyst**: Verify rules:
   - OAC 3901-1-54(F) 10-day payment deadline
   - OAC 3901-1-54(H)(10) deductible inclusion in subrogation
   - ORC 2315.33 comparative fault 51% bar
   - Lienholder two-party check requirements
   - Salvage value determination for total loss
4. **prompt-engineer**: Improve finance.md:
   - Strengthen payment formula examples
   - Add lienholder handling logic
   - Verify confidence penalty factors
   - Ensure "show the math" principle enforced
   - Add subrogation demand deadline tracking
5. **Bash**: Re-run benchmark

## Key Files

- `agents/finance.md` — agent prompt (PRIMARY edit target)
- `runner.py` — full pipeline context for Finance
- `test_cases/all_scenarios.json` — payment and subrogation assertions
- `docs/business-analysis.md` — Section 6.6 (lines 646-660)

## Acceptance Criteria

- [ ] payment_authorized=false for all denied/investigate scenarios
- [ ] Payment formula correct: amount = MIN(approved − deductible, limit)
- [ ] Total loss formula includes salvage value deduction
- [ ] Subrogation detected for all scenarios with at-fault third party
- [ ] Subrogation blocked when insured fault >= 51%
- [ ] Deductible included in subrogation demand
- [ ] Rental reimbursement correctly applied
- [ ] Confidence has highest threshold (75)
- [ ] No regression in benchmark score

## Verification

```bash
cd openclaw-hackathon
python3 benchmark.py --no-llm-judge
python3 loop.py --run-once --scenario TC-001  # Standard → payment authorized
python3 loop.py --run-once --scenario TC-004  # Expired → payment NOT authorized
```

## Constraints

- Finance does NOT execute transactions — only forms decisions
- Do NOT authorize payment without Senior Reviewer approval
- Preserve "show the math" principle
