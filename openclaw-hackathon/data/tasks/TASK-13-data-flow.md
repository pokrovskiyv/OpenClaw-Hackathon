# TASK-13: Data Flow and Runner
> Status: DONE → Goal: verify whitelist filtering, selective policy feeding, skip pattern

## Context

Section 7 of the PRD defines how data flows between agents. Key principles:
1. **Accumulation:** each agent gets original claim + all previous agent outputs
2. **Selective policy feeding:** only 4 of 6 agents get policy data (Claims Officer, Fraud Analyst, Senior Reviewer, Finance)
3. **Field-level whitelist:** Assessor gets filtered Claims Officer output (Blind Assessment)
4. **Skip pattern:** when coverage denied, downstream agents output `{"action": "skip"}`
5. **Peer assessment:** each downstream agent evaluates input quality (sufficient/partial/insufficient)

**Policy access matrix:**
| Agent | Policy Access | Prior Output Filtering |
|-------|--------------|----------------------|
| Front Desk | No | — |
| Claims Officer | **Yes** | — |
| Assessor | No | **Whitelist** from Claims Officer |
| Fraud Analyst | **Yes** | Full access to all |
| Senior Reviewer | **Yes** | Full access to all |
| Finance | **Yes** | Full access to all |

**Whitelist (runner.py):**
```python
ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER = {
    "claim_id", "coverage_valid", "recommendation",
    "flags", "notes", "confidence", "input_assessment",
    "processed_at", "routing",
}
```

**Skip pattern (coverage_valid=false):**
1. Claims Officer → coverage_valid: false
2. Assessor → {"action": "skip", "reason": "no_coverage"}
3. Fraud Analyst → {"action": "skip"}
4. Senior Reviewer → formalizes denial with policy citation
5. Finance → denial notification, no payment

**Peer assessment chain:** FD→CO→AS→FA→SR→FI (each evaluates the previous via `input_assessment`)

## Current State

- runner.py implements all of the above
- Whitelist exists and works
- Skip pattern implemented
- Need end-to-end verification across all scenarios

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| General | general-purpose | Deep-read runner.py, verify all data flow logic |
| Pipeline Analyst | eval-analyst | Test data flow with specific scenarios |
| Runner | Bash | Execute pipeline and inspect outputs |

## Work Plan

1. **general-purpose**: Read runner.py thoroughly:
   - Find `build_context()` or equivalent — how is agent context assembled?
   - Verify ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER whitelist is applied
   - Verify `_redacted: true` marker is added to filtered output
   - Verify policy data is only fed to 4 agents
   - Verify skip pattern detection logic
   - Verify peer assessment (input_assessment) is in each agent's output

2. **Bash**: Run targeted scenarios:
   ```bash
   python3 loop.py --run-once --scenario TC-001  # standard (full pipeline)
   python3 loop.py --run-once --scenario TC-004  # expired policy (skip pattern)
   ```

3. **eval-analyst**: Verify outputs:
   - TC-001: all agents produce full output, no skips
   - TC-004: Assessor and Fraud Analyst produce action=skip
   - TC-004: Senior Reviewer produces denial with policy citation
   - TC-004: Finance produces no payment
   - Check: Assessor output for TC-001 does NOT contain coverage_limit
   - Check: Fraud Analyst output for TC-001 DOES reference policy data
   - Check: input_assessment field present in agents 2-6

4. **Document** any gaps between PRD and implementation

## Key Files

- `runner.py` — PRIMARY file to verify (data flow, whitelist, skip logic)
- `agents/*.md` — all agent prompts (for peer assessment verification)
- `test_cases/all_scenarios.json` — scenarios with skip pattern assertions
- `docs/business-analysis.md` — Section 7 (lines 677-782)

## Acceptance Criteria

- [ ] Policy data fed to exactly 4 agents: CO, FA, SR, FI
- [ ] Assessor gets whitelist-filtered Claims Officer output
- [ ] _redacted: true marker present in filtered output
- [ ] Skip pattern works: coverage_valid=false → downstream action=skip
- [ ] Senior Reviewer still runs for denied claims (provides formal denial)
- [ ] Finance still runs for denied claims (generates denial notification)
- [ ] Peer assessment (input_assessment) present in agents 2-6
- [ ] Accumulation works: each agent sees all previous outputs

## Verification

```bash
cd openclaw-hackathon
python3 loop.py --run-once --scenario TC-004
# Verify skip pattern
python3 -c "
import json
d = json.load(open('logs/iter_000/TC-004/pipeline.json'))
ps = d['pipeline_state']
print('Assessor action:', ps['assessor'].get('action'))
print('Fraud action:', ps['fraud_analyst'].get('action'))
print('Senior decision:', ps['senior_reviewer'].get('decision'))
print('Finance payment:', ps['finance'].get('payment_authorized'))
"
```

## Constraints

- Do NOT modify ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER whitelist
- Do NOT change policy feeding logic without explicit approval
- Do NOT modify loop.py, evaluator.py, improver.py
