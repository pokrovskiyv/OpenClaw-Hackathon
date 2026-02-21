# TASK-04: Confidence Scores
> Status: DONE → Goal: verify all agents emit confidence correctly, penalty formulas match PRD

## Context

Section 5.4 defines the Confidence Score system. Each of the 6 pipeline agents emits a confidence score (0-100) calculated as: `confidence = 100 − SUM(penalty_factors)`. When confidence drops below a per-agent threshold, the claim escalates to a specialist.

**Thresholds and routing:**
| Agent | Threshold | Routes to |
|-------|-----------|-----------|
| Front Desk | < 60 | Human front-office |
| Claims Officer | < 70 | Coverage specialist |
| Assessor | < 65 | Field appraiser |
| Fraud Analyst | < 60 | SIU investigator |
| Senior Reviewer | < 70 | Claims Director |
| Finance | < 75 | Financial controller |

**Required output format:**
```json
{
  "confidence": {
    "score": 82,
    "factors": [
      {"factor": "multiple_coverage_options", "penalty": -15, "detail": "Hit-and-run: collision vs UMPD"},
      {"factor": "recent_policy", "penalty": -5, "detail": "Policy opened 45 days ago"}
    ],
    "escalation_triggered": false
  }
}
```

**Penalty factors per agent:** (See PRD Section 5.4.2 for complete tables — 5-6 factors per agent with specific penalties from −5 to −25)

**Integration with HITL triggers (Section 5.3):** Confidence does NOT replace hard triggers — it supplements them. Escalation on ANY condition: hard trigger OR confidence below threshold.

## Current State

- All 6 agent prompts include confidence score instructions
- Need to verify: correct penalties, correct thresholds, correct format
- Need to verify: escalation_triggered flag is correctly set

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Prompt Engineer | prompt-engineer | Verify penalty factors in each agent prompt match PRD Section 5.4.2 |
| Pipeline Analyst | eval-analyst | Run pipeline, check confidence output format and values |
| Runner | Bash | Execute pipeline runs |

## Work Plan

1. **Bash**: Run pipeline for several scenarios:
   ```bash
   cd openclaw-hackathon
   python3 loop.py --run-once --scenario TC-001
   python3 loop.py --run-once --scenario TC-002
   ```

2. **eval-analyst**: Check confidence output for each agent:
   - Is `confidence` field present in all 6 agent outputs?
   - Is format correct? (score, factors array, escalation_triggered)
   - Does score = 100 − sum(penalties)?
   - Is escalation_triggered correctly set based on threshold?
   - For TC-001 (standard): should all be high confidence
   - For TC-002 (suspicious): Fraud Analyst should have lower confidence
   - Are penalty factor names meaningful and specific?

3. **prompt-engineer**: Cross-reference each agent prompt with PRD:
   - Front Desk: missing FNOL field (−10), ambiguous category (−15), contradictory description (−20), no photos (−10), no police report > $1K (−5)
   - Claims Officer: multiple coverages (−15), unclear exclusion (−20), policy < 60d (−5), partial coverage (−10), non-standard terms (−15)
   - Assessor: spread > 30% (−15), grey zone 65-85% (−20), few photos (−10), hidden damage uncertainty (−10), no market data (−10)
   - Fraud Analyst: single category (−15), contradicting categories (−20), single indicator (−10), insufficient data (−15), grey zone 35-55 (−10)
   - Senior Reviewer: insufficient handoff (−20), 2+ partial (−15), override needed (−15), assessor-fraud contradiction (−20), grey zone + approve (−10)
   - Finance: divergence > 5% (−25), complex subrogation (−15), lienholder (−5), unknown salvage (−15), non-standard formula (−10)
   - Fix any mismatches between prompt and PRD

4. **Bash**: Re-run and verify corrections

## Key Files

- `agents/front_desk.md` through `agents/finance.md` — all 6 agent prompts
- `runner.py` — pipeline execution
- `docs/business-analysis.md` — Section 5.4 (lines 254-378)
- `test_cases/all_scenarios.json` — scenarios for testing confidence ranges

## Acceptance Criteria

- [ ] All 6 agents output confidence in correct format (score, factors, escalation_triggered)
- [ ] Penalty factors in each prompt match PRD Section 5.4.2 exactly
- [ ] Thresholds correct: FD < 60, CO < 70, AS < 65, FA < 60, SR < 70, FI < 75
- [ ] escalation_triggered=true when score < threshold
- [ ] TC-001 standard: all confidence scores >= threshold (no escalation)
- [ ] Penalty factor names are specific, not generic
- [ ] score = 100 − sum(penalties) for each agent

## Verification

```bash
cd openclaw-hackathon
python3 loop.py --run-once --scenario TC-001
# Check all agents have confidence
python3 -c "
import json
d = json.load(open('logs/iter_000/TC-001/pipeline.json'))
for agent in ['front_desk', 'claims_officer', 'assessor', 'fraud_analyst', 'senior_reviewer', 'finance']:
    conf = d['pipeline_state'].get(agent, {}).get('confidence', 'MISSING')
    print(f'{agent}: {conf}')
"
```

## Constraints

- Do NOT change confidence thresholds without justification
- Do NOT change the confidence output format (score, factors, escalation_triggered)
- Penalty factors should match PRD — if PRD is wrong, document the discrepancy
