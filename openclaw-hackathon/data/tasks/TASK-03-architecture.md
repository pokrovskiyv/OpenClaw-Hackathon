# TASK-03: Architecture — Pipeline + Models + HITL
> Status: DONE → Goal: verify OpenClaw integration, HITL escalation logic, model assignments

## Context

Section 5 (5.1-5.3) of the PRD defines the system architecture: 7-agent sequential pipeline, model assignments, and Human-in-the-Loop escalation.

**Pipeline structure:** 7 agents sequential — Front Desk → Claims Officer → Assessor → Fraud Analyst → Senior Reviewer → Finance → Claims Manager.

**Model assignments:**
| Role | Model | Reason |
|------|-------|--------|
| Worker agents (1-6) | claude-haiku-4-5-20251001 | Fast + cost-efficient |
| Claims Manager | claude-sonnet-4-6 | Deep quality analysis |
| Evaluator | — (no LLM) | Just parses Manager output |
| Improver | claude-sonnet-4-6 | Prompt rewriting |
| LLM-Judge (benchmark) | claude-opus-4-6 | External objective evaluation |

**HITL escalation (3 levels):**
1. Voice channel — client requests operator, injuries, stress
2. Pipeline — fraud_score >= 46, amount > $25K, decision=investigate/referred, confidence < threshold
3. Final approval — certain categories require human sign-off

**Fast-Track (Daniel Kowalski):** active policy + no injuries + < $10K + no fraud indicators + police report. Prioritized but does NOT skip stages.

**Non-Blocking Escalation:** escalation doesn't stop pipeline. Claim continues with `escalation_triggered` flag. Full data package ready by time human reviews.

**OpenClaw integration:**
| Component | Usage |
|-----------|-------|
| Agent (Skills) | Each agent = OpenClaw agent with markdown instruction |
| Sequential Pipeline | runner.py orchestration |
| Tool Use | Context as tool inputs |
| Gateway | WebSocket for ClawdTalk |
| Tool Governance | Selective policy feeding, field-level whitelist |

## Current State

- runner.py implements sequential pipeline
- lib/config.py defines models
- HITL escalation partially implemented (escalation flags, but no actual human routing)
- OpenClaw integration designed but needs verification against actual src/openclaw.json

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| General | general-purpose | Verify Python pipeline implementation matches PRD |
| Platform | openclawer | Verify OpenClaw integration — gateway config, agent definitions |
| Explorer | Explore | Read runner.py, lib/config.py, src/openclaw.json for cross-reference |

## Work Plan

1. **Explore**: Read and catalog:
   - `runner.py` — AGENT_ORDER, model assignments, escalation logic
   - `lib/config.py` — model constants
   - `src/openclaw.json` — agent definitions, gateway config

2. **general-purpose**: Verify Python pipeline:
   - Is AGENT_ORDER correct? (front_desk, claims_officer, assessor, fraud_analyst, senior_reviewer, finance, manager)
   - Are model assignments in config.py matching PRD?
   - Is escalation logic implemented? (fraud_score >= 46 flag, amount > $25K flag, confidence < threshold)
   - Is fast-track prioritization implemented?
   - Is non-blocking escalation working? (pipeline continues after escalation trigger)

3. **openclawer**: Verify OpenClaw integration:
   - Read src/openclaw.json — are all 7 agents defined?
   - Is gateway configured for chatCompletions?
   - Are tool governance profiles set up for selective policy feeding?
   - Does OpenClaw agent structure match runner.py expectations?

4. **Document gaps** and produce recommendations

## Key Files

- `runner.py` — pipeline orchestration, AGENT_ORDER, escalation logic
- `lib/config.py` — model constants, paths, thresholds
- `src/openclaw.json` — OpenClaw gateway and agent config
- `docs/business-analysis.md` — Section 5.1-5.3 (lines 182-252)

## Acceptance Criteria

- [ ] AGENT_ORDER matches PRD (7 agents in correct sequence)
- [ ] Model assignments match PRD (Haiku for workers, Sonnet for Manager)
- [ ] escalation_triggered flag set when fraud_score >= 46
- [ ] escalation_triggered flag set when amount > $25K
- [ ] Pipeline does NOT stop on escalation (non-blocking confirmed)
- [ ] Fast-track flag recognized and processed
- [ ] OpenClaw agent definitions match pipeline agents
- [ ] Gateway config supports chatCompletions

## Verification

```bash
cd openclaw-hackathon
# Verify model config
python3 -c "from lib.config import *; print('AGENT_MODEL:', AGENT_MODEL); print('MANAGER_MODEL:', MANAGER_MODEL)"
# Run pipeline to verify sequence
python3 loop.py --run-once --scenario TC-001
```

## Constraints

- Do NOT change AGENT_ORDER in runner.py
- Do NOT change model assignments without explicit approval
- Do NOT modify loop.py, evaluator.py, improver.py
