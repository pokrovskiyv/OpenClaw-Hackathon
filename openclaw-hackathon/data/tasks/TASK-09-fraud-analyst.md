# TASK-09: Fraud Analyst Agent
> Status: DONE → Goal: improve fraud detection accuracy, verify Estimate-to-Limit, cross-reference logic

## Context

Fraud Analyst is Agent #4 — SIU specialist. Analyzes claims for fraud indicators, calculates risk score (0-100). Has FULL policy access (Secret Addition — Priya Okonkwo) for cross-referencing blind assessment with policy limits.

**Scoring system (0-100, four categories):**
| Category | Max | Examples |
|----------|-----|---------|
| Chronology | 25 | Policy < 30 days (+15), claim > 30 days after incident (+10) |
| Circumstances | 25 | No police report > $2K (+10), night (+5), no witnesses (+5) |
| Damage/Medical | 25 | Disproportionate medical (+15), damage doesn't match description (+12) |
| Behavior | 25 | 2+ claims in 3 years (+10), pressure to expedite (+10), shared address (+15) |

**Risk levels:** low (0-20), moderate (21-45), high (46-70), critical (71-100).

**Estimate-to-Limit Cross-Reference (Section 7.2a):**
- `limit_proximity = repair_estimate.total / coverage_limit`
- If > 0.90: +15 to fraud_score
- If estimate ≈ limit − deductible (within 5%): +20 to fraud_score
- Key insight: because Assessor is blind, match = strongest fraud signal

**Known fraud schemes:** Swoop-and-Squat, Paper Accidents, Inflated Claims, Past-Posting, Owner Give-Up, Phantom Passengers, Medical Mill.

**Business rules:**
- Never accuse — use "indicators present", "elevated risk"
- Every score point backed by observation
- SIU referral only at score >= 71 or organized scheme evidence
- Skip pattern when coverage denied
- **Mandatory reporting (ORC 3999.41-3999.49):** critical risk or organized scheme → flag for Ohio DOI Fraud Division
- **Peer assessment:** evaluates Assessor

**Confidence Score** (Section 5.4):
- Threshold: < 60 → escalate to SIU (supplements hard trigger fraud_score >= 46)
- Penalty factors: single category indicators (−15), contradicting categories (−20), single indicator no pattern (−10), insufficient cross-reference data (−15), grey zone score 35-55 (−10)

## Current State

- `agents/fraud_analyst.md` exists with full policy access
- Estimate-to-Limit cross-reference documented
- 4-category scoring system in prompt
- Needs testing on all fraud-related scenarios

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Prompt Engineer | prompt-engineer | Review and improve fraud_analyst.md |
| Pipeline Analyst | eval-analyst | Analyze fraud detection accuracy, verify Estimate-to-Limit |
| Domain Expert | insurance-analyst | Verify fraud schemes, check scoring weights, validate NICB criteria |
| Runner | Bash | Execute pipeline runs and benchmark |

## Work Plan

1. **Bash**: Run baseline benchmark
2. **eval-analyst**: Analyze Fraud Analyst performance:
   - TC-002 (suspicious): should have moderate-to-high fraud_score
   - TC-005 (staged accident): should have high-to-critical fraud_score
   - TC-001 (standard): should have low fraud_score (< 21)
   - Verify Estimate-to-Limit calculation is performed when data available
   - Check that skip pattern works for denied coverage scenarios
   - Verify peer assessment of Assessor is meaningful
   - Check recommendation field matches risk level
3. **insurance-analyst**: Verify fraud knowledge:
   - Are scoring weights realistic? (NICB, CAIF criteria)
   - Any missing fraud schemes for Ohio?
   - Is mandatory reporting threshold correct (ORC 3999.41-3999.49)?
   - Ohio-specific fraud patterns (e.g., rust belt staged collisions)
4. **prompt-engineer**: Improve fraud_analyst.md:
   - Strengthen Estimate-to-Limit cross-reference section
   - Add any missing fraud schemes
   - Ensure all 4 scoring categories are balanced
   - Verify confidence penalty factors
   - ALWAYS preserve estimate-to-limit padding detection section
5. **Bash**: Re-run benchmark

## Key Files

- `agents/fraud_analyst.md` — agent prompt (PRIMARY edit target)
- `runner.py` — full policy data feeding for Fraud Analyst
- `test_cases/all_scenarios.json` — fraud-related assertions
- `docs/business-analysis.md` — Section 6.4 (lines 600-619), Section 7.2a (lines 734-741)

## Acceptance Criteria

- [ ] TC-005 (staged accident): fraud_score >= 46, risk_level = high or critical
- [ ] TC-001 (standard collision): fraud_score < 21, risk_level = low
- [ ] TC-002 (suspicious): fraud_score reflects actual indicators
- [ ] Estimate-to-Limit cross-reference performed when policy data available
- [ ] Skip pattern works for denied coverage scenarios
- [ ] Language uses "indicators present", never "fraud detected" or accusations
- [ ] Mandatory reporting flag set for critical risk level
- [ ] No regression in benchmark score

## Verification

```bash
cd openclaw-hackathon
python3 benchmark.py --no-llm-judge
python3 loop.py --run-once --scenario TC-005  # Staged accident
python3 -c "import json; d=json.load(open('logs/iter_000/TC-005/pipeline.json')); f=d['pipeline_state']['fraud_analyst']; print('fraud_score:', f.get('fraud_score'), 'risk_level:', f.get('risk_level'))"
```

## Constraints

- ALWAYS preserve Estimate-to-Limit cross-reference section in prompt
- Do NOT remove or weaken fraud detection rules
- Do NOT modify runner.py policy feeding logic
