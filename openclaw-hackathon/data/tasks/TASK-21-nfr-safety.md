# TASK-21: Non-Functional Requirements, Risks, and Safety
> Status: DONE → Goal: verify error handling, immutability, logging structure, oscillation module

## Context

Sections 13-14 of the PRD define NFRs and risk mitigation:

**NFRs (Section 13):**
- Performance: sequential pipeline, ~2-5s per LLM call, ~15-30s per scenario, ~10-18 min full run
- Dependencies: Python stdlib + anthropic SDK only
- Immutability: agents return new objects, never mutate input
- Error handling: JSON parse fallback, pipeline doesn't crash on single agent error
- Logging: hierarchical logs/iter_NNN/TC-XXX/ structure

**Business Logic Risks (Section 14):**
| Risk | Agent | Detection | Criticality |
|------|-------|-----------|-------------|
| Missed fraud | Fraud Analyst | fraud_score below threshold for suspicious scenarios | Critical |
| Paying uncovered | Claims Officer | coverage_valid=true on expired policy | Critical |
| Missing total loss | Assessor | total_loss=false when ratio >= 0.75 | High |
| Wrong deductible | Claims Officer | Collision instead of Comprehensive when cheaper | High |
| Missing subrogation | Finance | subrogation.applicable=false with at-fault party | Medium |
| Approving with SIU flag | Senior Reviewer | approved with high/critical risk_level | Critical |
| Payment without approval | Finance | payment_authorized=true without approved decision | Critical |

**System Risks:**
- Model hallucinations → assertions + LLM judge + peer assessment
- Cascading errors → Manager handoff chain quality + peer assessment
- Single evaluator bias → two channels (40% deterministic + 60% external LLM judge)
- Prompt oscillation → lib/oscillation.py (>= 3 direction changes → exclude)
- Secret Addition uncertainty → reasoning-based instructions, not hardcoded rules

## Current State

- lib/oscillation.py implemented
- JSON parse fallback in runner.py
- Hierarchical logging implemented
- Need to verify all safety mechanisms

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| General | general-purpose | Read code, verify NFR implementation |
| Pipeline Analyst | eval-analyst | Test error handling, verify logging |
| Runner | Bash | Execute tests and check outputs |

## Work Plan

1. **general-purpose**: Verify NFR implementations:
   - Read runner.py — immutability (new objects, no mutation)
   - Read runner.py — JSON parse fallback
   - Read runner.py — single agent error handling
   - Read lib/oscillation.py — algorithm correctness
   - Verify: no external dependencies beyond anthropic SDK

2. **Bash**: Test error scenarios:
   ```bash
   cd openclaw-hackathon
   # Verify logging structure
   ls -la logs/iter_000/ 2>/dev/null || echo "No logs yet"
   # Verify oscillation module
   python3 -c "from lib.oscillation import *; print('Oscillation module loaded')"
   ```

3. **eval-analyst**: Verify risk mitigation:
   - Run benchmark and check for each business logic risk
   - Are there assertions for each critical risk? (e.g., payment without approval)
   - Does the assertion engine catch the critical risks?
   - Check lib/oscillation.py — does it correctly detect 3+ direction changes?

4. **Document** any unmitigated risks or missing safety checks

## Key Files

- `runner.py` — immutability, error handling, JSON fallback
- `lib/oscillation.py` — oscillation detection
- `lib/config.py` — thresholds
- `docs/business-analysis.md` — Sections 13-14 (lines 1084-1131)

## Acceptance Criteria

- [ ] No mutation of input data in runner.py (new objects only)
- [ ] JSON parse fallback works (invalid JSON wrapped, not crashed)
- [ ] Single agent error doesn't crash entire pipeline
- [ ] Logging structure matches: logs/iter_NNN/TC-XXX/pipeline.json
- [ ] lib/oscillation.py detects >= 3 direction changes
- [ ] Each critical business risk has at least one assertion in test scenarios
- [ ] Only anthropic SDK as external dependency (no frameworks, databases)

## Verification

```bash
cd openclaw-hackathon
# Check dependencies
pip list | grep -v "^Package\|^---" | wc -l
# Verify oscillation module
python3 -c "
from lib.oscillation import detect_oscillation
# Test with oscillating scores
scores = [80, 85, 78, 84, 77]
result = detect_oscillation(scores)
print(f'Oscillation detected: {result}')
"
# Check immutability (no .update() or dict[key]= in agent processing)
grep -n '\.update\|dict\[' runner.py | head -20
```

## Constraints

- Do NOT modify oscillation detection algorithm
- Do NOT add external dependencies
- If immutability violations found, document them for fix
