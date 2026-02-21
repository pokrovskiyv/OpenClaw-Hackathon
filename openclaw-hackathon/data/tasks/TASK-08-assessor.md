# TASK-08: Assessor + Blind Assessment Architecture
> Status: DONE → Goal: verify blind assessment works, total loss accuracy, hidden damage estimation

## Context

Assessor is Agent #3 — evaluates physical damage, calculates repair cost, determines total loss. Does NOT receive policy data (Blind Assessment Architecture).

**Key output fields:** damage_catalog, repair_estimate.total, vehicle_acv, total_loss, total_loss_ratio, consistency_flags, confidence, action (="skip" when coverage denied).

**Blind Assessment Architecture (Section 7.2a):**
Field-level whitelist in runner.py filters Claims Officer output for Assessor:
```python
ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER = {
    "claim_id", "coverage_valid", "recommendation",
    "flags", "notes", "confidence", "input_assessment",
    "processed_at", "routing",
}
```
Assessor does NOT see: coverage_limit, deductible, coverage_type, exclusions_triggered, policy_status.
Filtered output includes `_redacted: true` marker.

**Why this matters:** If Assessor sees coverage limits, it may subconsciously match estimates to limits (bad faith per ORC 3901.21, *Zoppo v. Homestead*). The blind assessment makes Estimate-to-Limit correlation a powerful fraud signal for Fraud Analyst.

**Business rules:**
- Total loss: repair > 75% ACV (company policy, aligned with ORC 4505.11 salvage title)
- Also total loss: critical structural damage, flood, fire
- Repair estimate includes 10-15% for hidden damage
- Inconsistencies noted for Fraud Analyst
- Skip pattern: if coverage_valid=false → `{"action": "skip", "reason": "no_coverage"}`
- **Peer assessment:** evaluates Claims Officer (filtered version)

**Confidence Score** (Section 5.4):
- Threshold: < 65 → escalate to field appraiser
- Penalty factors: estimate spread > 30% (−15), total loss ratio in grey zone 65-85% (−20), few photos < 3 (−10), hidden damage uncertainty (−10), no market data for model (−10)

## Current State

- `agents/assessor.md` exists
- Blind Assessment whitelist implemented in runner.py
- Skip pattern implemented for denied coverage
- Need to verify total loss calculation accuracy

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Prompt Engineer | prompt-engineer | Review and improve assessor.md |
| Pipeline Analyst | eval-analyst | Analyze Assessor output, verify blind assessment, check total loss accuracy |
| Runner | Bash | Execute pipeline runs and benchmark |

## Work Plan

1. **Bash**: Run baseline benchmark
2. **eval-analyst**: Analyze Assessor performance:
   - Verify Assessor output NEVER contains coverage_limit, deductible
   - Verify `_redacted: true` present in Assessor's view of Claims Officer output
   - Check total_loss flag for TC-003 (total loss scenario) — should be true
   - Check total_loss_ratio calculation: repair_estimate.total / vehicle_acv
   - Check skip pattern for TC-004 (expired policy) and TC-006 (excluded coverage)
   - Verify 10-15% hidden damage supplemental is included
   - Check consistency_flags for suspicious scenarios (TC-002, TC-005)
3. **prompt-engineer**: Improve assessor.md:
   - Strengthen total loss determination logic (75% ACV rule + structural exceptions)
   - Ensure hidden damage supplemental is always applied
   - Improve consistency flag detection
   - Verify confidence penalty factors match PRD Section 5.4.2
   - CRITICAL: NEVER add coverage_limit or deductible references ($4.1M fine risk)
4. **Bash**: Re-run benchmark

## Key Files

- `agents/assessor.md` — agent prompt (PRIMARY edit target)
- `runner.py` — ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER whitelist (DO NOT MODIFY)
- `test_cases/all_scenarios.json` — total loss assertions, skip pattern assertions
- `docs/business-analysis.md` — Section 6.3 (lines 589-598), Section 7.2a (lines 709-743)

## Acceptance Criteria

- [ ] Assessor output NEVER contains coverage_limit or deductible in any scenario
- [ ] `_redacted: true` marker present in Claims Officer data passed to Assessor
- [ ] TC-003 (total loss): total_loss=true, total_loss_ratio >= 0.75
- [ ] TC-004/TC-006 (denied coverage): action="skip"
- [ ] repair_estimate.total includes 10-15% hidden damage buffer
- [ ] consistency_flags populated for suspicious scenarios (TC-002, TC-005)
- [ ] Confidence calculated with correct penalty factors
- [ ] No regression in benchmark score

## Verification

```bash
cd openclaw-hackathon
python3 benchmark.py --no-llm-judge
python3 loop.py --run-once --scenario TC-003  # Total loss
# Verify blind assessment
python3 -c "import json; d=json.load(open('logs/iter_000/TC-003/pipeline.json')); a=d['pipeline_state']['assessor']; print('total_loss:', a.get('total_loss'), 'ratio:', a.get('total_loss_ratio'))"
```

## Constraints

- **CRITICAL: NEVER add coverage_limit or deductible to assessor.md** ($4.1M bad-faith fine risk)
- Do NOT modify ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER whitelist in runner.py
- Do NOT modify loop.py, evaluator.py, improver.py
