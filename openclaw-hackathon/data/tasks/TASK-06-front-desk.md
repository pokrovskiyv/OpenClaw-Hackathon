# TASK-06: Front Desk Agent
> Status: DONE → Goal: verify, improve categorization accuracy, test fast-track, validate FNOL completeness

## Context

Front Desk is Agent #1 — first point of contact. Registers the case, categorizes the incident, assesses severity and priority. Does NOT receive policy data.

**Key output fields:** claim_id, category, severity, priority, fnol_complete, missing_info, summary, fast_track, claim_status_update, confidence.

**Categories:** collision, comprehensive, hit_and_run, collision_with_injury, theft, vandalism.
**Severity:** low, moderate, high.
**Priority:** urgent, high, standard, low.

**Business rules:**
- Categorization mandatory even with incomplete data
- Injuries → `_with_injury` suffix
- Missing police report when damage > $1,000 → flag
- Does NOT evaluate coverage or fraud
- Generates `claim_status_update` — maps internal stages to customer-friendly language (Secret Addition — Marcus Chen)
- Generates `fast_track: true` when: active policy + no injuries + expected damage < $10K + no fraud indicators + police report filed (Secret Addition — Daniel Kowalski)

**Confidence Score** (Section 5.4):
- Threshold: < 60 → escalate to human front-office
- Penalty factors: missing FNOL fields (−10 each), ambiguous category (−15), contradictory description (−20), no photos (−10), no police report when > $1K (−5)

## Current State

- `agents/front_desk.md` exists and is deployed
- Agent runs in pipeline via runner.py
- Should be tested against all 36 scenarios

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Prompt Engineer | prompt-engineer | Review and improve front_desk.md based on eval results |
| Pipeline Analyst | eval-analyst | Run pipeline, analyze Front Desk output across scenarios, identify weak spots |
| Runner | Bash | Execute pipeline runs and benchmark |

## Work Plan

1. **Bash**: Run full benchmark to establish baseline:
   ```bash
   cd openclaw-hackathon && python3 benchmark.py --no-llm-judge
   ```

2. **eval-analyst**: Analyze Front Desk performance:
   - Read latest pipeline logs for all scenarios
   - Check: is `category` correct for each scenario?
   - Check: is `fast_track` correctly set (true only when all conditions met)?
   - Check: does `claim_status_update` exist and use customer-friendly language?
   - Check: is `confidence` calculated with correct penalty factors?
   - Check: does severity match injury status?
   - Identify the 3 weakest scenarios for Front Desk

3. **prompt-engineer**: Improve `agents/front_desk.md`:
   - Address weaknesses found by eval-analyst
   - Ensure all confidence penalty factors from Section 5.4.2 are in the prompt
   - Ensure fast_track conditions are explicitly listed
   - Ensure claim_status_update mapping is complete
   - Preserve: single-point-of-contact principle, never "call another department"

4. **Bash**: Re-run benchmark to verify improvement:
   ```bash
   cd openclaw-hackathon && python3 benchmark.py --no-llm-judge
   ```

## Key Files

- `agents/front_desk.md` — agent prompt (PRIMARY edit target)
- `runner.py` — pipeline execution
- `test_cases/all_scenarios.json` — test scenarios with Front Desk assertions
- `docs/business-analysis.md` — Section 6.1 (lines 561-574), Section 5.4.2 Front Desk penalties

## Acceptance Criteria

- [ ] Front Desk correctly categorizes all 36 scenarios
- [ ] fast_track is true only when all 5 conditions are met
- [ ] claim_status_update present in output with customer-friendly language
- [ ] confidence field present with score, factors, and escalation_triggered
- [ ] No regression in benchmark score after prompt changes
- [ ] Missing police report flagged when damage > $1,000

## Verification

```bash
cd openclaw-hackathon
python3 benchmark.py --no-llm-judge  # Full benchmark
python3 loop.py --run-once --scenario TC-001  # Standard collision (should be fast_track=true)
python3 loop.py --run-once --scenario TC-005  # Staged accident (should NOT be fast_track)
```

## Constraints

- Do NOT modify runner.py, loop.py, evaluator.py, improver.py
- Do NOT add coverage or fraud logic to Front Desk
- Preserve ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER whitelist
- Back up front_desk.md before changes
