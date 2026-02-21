# TASK-20: Test Scenarios
> Status: DONE → Goal: verify 36 scenarios cover all edge cases, add missing scenarios if needed

## Context

Section 12 describes the test scenario system. 36 scenarios covering the full spectrum from simple collision to staged accidents, including PIP-only, liability-only, multi-coverage, UIM, and lienholder cases.

**Distribution by difficulty:**
| Difficulty | Examples | Count |
|-----------|---------|-------|
| Easy | Standard collision, expired policy, simple comprehensive | ~10 |
| Medium | Suspicious claim, total loss, excluded coverage, partial coverage | ~12 |
| Hard | Staged accident, hit-and-run, borderline total loss, multi-party | ~8 |

**Scenario structure:** Each contains:
- Input data (incident, policy, client, vehicle)
- Assertions with criticality level (critical/non-critical)
- Business rules for LLM judge
- Expected outcomes per agent

**Current stats:**
- 36 scenarios
- 387 assertions (248 critical, 139 non-critical)
- 95 business rules

**Scenario categories covered:**
- Standard claims (collision, comprehensive, theft, vandalism)
- Policy issues (expired, excluded, partial coverage)
- Fraud patterns (suspicious, staged, inflated)
- Total loss (standard, borderline grey zone)
- Special coverages (PIP-only, liability-only, UM/UIM)
- Complex cases (hit-and-run, multi-party, lienholder)

## Current State

- `test_cases/all_scenarios.json` contains 36 scenarios
- All scenarios have assertions
- Need to verify coverage of all edge cases from PRD

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Pipeline Analyst | eval-analyst | Analyze scenario coverage, identify gaps, design new scenarios |
| Domain Expert | insurance-analyst | Identify missing Ohio-specific edge cases |

## Work Plan

1. **eval-analyst**: Analyze existing scenario coverage:
   - List all 36 scenario IDs and types
   - Map each scenario to: coverage type, fraud type, special condition
   - Check: is every coverage type tested? (Collision, Comprehensive, Liability, UM/UIM, PIP/MedPay)
   - Check: is every fraud scheme tested? (Swoop-and-Squat, Paper Accident, Inflated, Past-Posting, Owner Give-Up, Phantom Passengers, Medical Mill)
   - Check: is every exclusion tested? (DUI, commercial use, racing, unauthorized driver, misrepresentation)
   - Check: are all decision types tested? (approved, approved_partial, investigate, denied, referred, ror)
   - Check: is subrogation tested with comparative fault scenarios?

2. **insurance-analyst**: Identify missing edge cases:
   - Multi-vehicle accident with shared fault
   - Rideshare (Uber/Lyft) coverage gap
   - Permissive use violation
   - Material misrepresentation discovered mid-claim
   - Glass-only claim (Comprehensive with low deductible)
   - Uninsured motorist with known at-fault driver
   - Claim filed after 30-day reporting window
   - Policy in grace period (just expired)
   - Bad faith risk scenario (legitimate claim at risk of under-payment)
   - Catastrophic event (hail, flood) with many simultaneous claims

3. **eval-analyst**: For missing scenarios, design new test cases:
   - Define input data (incident, policy, vehicle)
   - Define expected outcomes per agent
   - Write assertions (critical and non-critical)
   - Write business rules for LLM judge
   - Add to all_scenarios.json

4. **Verify assertion quality**:
   - Check: are assertions testing the right things?
   - Check: are critical assertions truly critical?
   - Check: are there redundant assertions?

## Key Files

- `test_cases/all_scenarios.json` — 36 scenarios (PRIMARY edit target for new scenarios)
- `lib/assertions.py` — assertion engine (operators, dot-notation)
- `docs/business-analysis.md` — Section 12 (lines 1053-1081)

## Acceptance Criteria

- [ ] All coverage types have at least one test scenario
- [ ] All fraud schemes referenced in PRD have test scenarios
- [ ] All exclusion types have test scenarios
- [ ] All decision types (approved, denied, investigate, referred, ror, approved_partial) tested
- [ ] Subrogation tested with and without comparative fault
- [ ] At least 3 new edge case scenarios identified and designed
- [ ] New assertions follow existing format (field, operator, expected, critical flag)
- [ ] Total assertion count grows (currently 387)

## Verification

```bash
cd openclaw-hackathon
# Count scenarios and assertions
python3 -c "
import json
d = json.load(open('test_cases/all_scenarios.json'))
print(f'Scenarios: {len(d)}')
total = sum(len(s.get('assertions', [])) for s in d)
print(f'Assertions: {total}')
# Coverage type distribution
from collections import Counter
types = Counter(s.get('input', {}).get('incident', {}).get('type', 'unknown') for s in d)
print(f'Types: {dict(types)}')
"
```

## Constraints

- New scenarios must follow existing JSON format exactly
- Do NOT remove existing scenarios
- Do NOT change existing assertions (unless they're provably wrong)
- New assertions should use existing operators from lib/assertions.py
