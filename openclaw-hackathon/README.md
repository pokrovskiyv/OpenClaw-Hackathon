# OpenClaw Hackathon — Agent Training Loop

Automated eval-driven training system for 6 insurance claims processing agents.

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY='sk-ant-...'

# 3. Single run + eval (test that everything works)
python loop.py --run-once

# 4. Full training loop
python loop.py --iterations 10

# 5. Run specific scenario only
python loop.py --run-once --scenario TC-005
```

## Architecture

```
loop.py          ← Main controller (Run → Eval → Improve → Repeat)
├── runner.py    ← Runs claims through 6-agent pipeline
├── evaluator.py ← Scores outputs (rule-based + LLM-as-judge)
├── improver.py  ← Reads eval logs, rewrites agent prompts
└── lib/
    ├── config.py  ← Models, paths, thresholds
    └── llm.py     ← Anthropic API wrapper

agents/          ← Agent system prompts (SKILL.md format)
├── front_desk.md
├── claims_officer.md
├── assessor.md
├── fraud_analyst.md
├── senior_reviewer.md
├── finance.md
└── backups/     ← Auto-backups before each rewrite

test_cases/      ← Insurance claim scenarios with ground truth
└── scenarios.json

logs/            ← Raw pipeline outputs per iteration
results/         ← Evaluation scores + loop summary
```

## How It Works

1. **Runner** sends each test claim through all 6 agents sequentially
2. **Evaluator** scores each agent output:
   - Rule-based checks (field matches, ranges, flags) → 40% weight
   - LLM-as-judge (correctness, business logic, reasoning) → 60% weight
3. **Improver** rewrites prompts for agents scoring < 90
4. **Loop** repeats until passing score (85) or max iterations

## Test Scenarios

| ID | Name | Difficulty | Tests |
|----|------|-----------|-------|
| TC-001 | Standard Collision | Easy | Happy path, subrogation |
| TC-002 | Suspicious Claim | Medium | Fraud indicators, new policy |
| TC-003 | Total Loss | Medium | Comprehensive, ACV calc |
| TC-004 | Expired Policy | Easy | Coverage denial flow |
| TC-005 | Staged Accident | Hard | Organized fraud ring, SIU referral |
| TC-006 | Excluded Coverage | Medium | Commercial use exclusion |
| TC-007 | Hit and Run | Hard | UMPD coverage, emotional claimant |
