# CLAUDE.md — OpenClaw Hackathon

## Project Overview

Multi-agent **car insurance claims processing system** for Ohio Mutual Auto.
Built for the OpenClaw Business Engineering Hackathon (Belgrade, Feb 21).

The system automates a 6-step human pipeline using Claude agents, with an
eval-driven training loop that automatically improves agent prompts.

## Repository Layout

```
HACKATHON.md              ← Competition rules and judging criteria
openclaw-hackathon/
├── loop.py               ← Main controller: Run → Eval → Improve → Repeat
├── runner.py             ← Runs claims through 6-agent pipeline sequentially
├── evaluator.py          ← Scores outputs (rule-based 40% + LLM-as-judge 60%)
├── improver.py           ← Reads eval logs, rewrites agent prompts
├── lib/
│   ├── config.py         ← Models, paths, thresholds (edit here first)
│   └── llm.py            ← Anthropic API wrapper
├── agents/               ← Agent system prompts (Markdown files)
│   ├── front_desk.md
│   ├── claims_officer.md
│   ├── assessor.md
│   ├── fraud_analyst.md
│   ├── senior_reviewer.md
│   ├── finance.md
│   └── backups/          ← Auto-saved before each prompt rewrite
├── test_cases/
│   ├── scenarios.json    ← 7 base test scenarios with ground truth
│   └── all_scenarios.json← 30-case merged file (used if present)
├── logs/                 ← Raw pipeline outputs per iteration
└── results/              ← Eval scores + loop_summary.json
```

## The 6-Agent Pipeline

| # | Agent | File | Responsibility |
|---|-------|------|----------------|
| 1 | Front Desk | `front_desk.md` | Register & categorize the claim |
| 2 | Claims Officer | `claims_officer.md` | Verify coverage applies |
| 3 | Assessor | `assessor.md` | Estimate damage amount |
| 4 | Fraud Analyst | `fraud_analyst.md` | Detect suspicious patterns |
| 5 | Senior Reviewer | `senior_reviewer.md` | Final approval decision |
| 6 | Finance | `finance.md` | Execute payment |

Agents run **sequentially** — each receives the full prior context.

## Models (lib/config.py)

| Role | Model | Reason |
|------|-------|--------|
| Agent workers | `claude-haiku-4-5-20251001` | Fast + cost-efficient |
| Evaluator (judge) | `claude-sonnet-4-6` | Strong reasoning |
| Improver (coach) | `claude-sonnet-4-6` | Strong reasoning |

## Quick Commands

```bash
cd openclaw-hackathon

# Setup
pip install -r requirements.txt
export ANTHROPIC_API_KEY='sk-ant-...'

# Single run + eval (smoke test)
python loop.py --run-once

# Run specific scenario
python loop.py --run-once --scenario TC-005

# Full training loop (10 iterations)
python loop.py --iterations 10

# Dry-run: evaluate but don't rewrite prompts
python loop.py --dry-run

# Custom passing threshold
python loop.py --iterations 5 --passing-score 90
```

## Eval Scoring

- **Rule-based checks** (40%): field presence, value ranges, required flags
- **LLM-as-judge** (60%): correctness, business logic, reasoning quality
- **Passing threshold**: 85/100 — loop stops when reached
- **Improvement trigger**: any agent scoring < 90 gets its prompt rewritten

## Editing Agent Prompts

Agent prompts live in `agents/*.md`. The improver auto-rewrites them
and saves backups to `agents/backups/` before each change.

When editing manually:
- Keep prompts focused on the agent's single responsibility
- Include Ohio Mutual Auto policy rules relevant to that role
- Reference prior agent outputs that should be consumed
- State the exact JSON/structured output format expected

## Key Business Rules (from HACKATHON.md)

- Regulations and business priorities MUST both be respected
- The "secret addition" on hackathon day adds new business context —
  agent prompts must handle reasoning, not hardcoded rules
- Judging: 50% Business Thinking + 50% System Thinking

## Test Scenarios

| ID | Name | Difficulty |
|----|------|-----------|
| TC-001 | Standard Collision | Easy |
| TC-002 | Suspicious Claim | Medium |
| TC-003 | Total Loss | Medium |
| TC-004 | Expired Policy | Easy |
| TC-005 | Staged Accident | Hard |
| TC-006 | Excluded Coverage | Medium |
| TC-007 | Hit and Run | Hard |

## Development Notes

- All outputs are **immutable**: agents return new structured data, never mutate input
- Python stdlib only + `anthropic` — keep dependencies minimal
- The `loop.py` controller reads `all_scenarios.json` if present, else `scenarios.json`
- Logs go to `logs/run_<N>.json`, evals to `results/eval_<N>.json`
- `results/loop_summary.json` tracks score progression across iterations
