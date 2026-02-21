# Skill: fraud-analysis

## Purpose
Evaluate fraud risk indicators using a 0-100 weighted model and produce SIU triage guidance.

## Input
- Intake summary and incident facts
- Claims Officer conclusions (coverage outcomes, constraints)
- Assessor outputs (damage consistency, severity, estimates)
- Claimant behavior and historical claim context

## Output Schema
```json
{
  "fraud_score": 0,
  "risk_level": "low | moderate | high | critical",
  "indicator_breakdown": {
    "timeline": {"score": 0, "max": 25, "items": ["string"]},
    "circumstances": {"score": 0, "max": 25, "items": ["string"]},
    "damage_medical": {"score": 0, "max": 25, "items": ["string"]},
    "behavior": {"score": 0, "max": 25, "items": ["string"]}
  },
  "observations": ["string"],
  "known_pattern_matches": ["Swoop-and-Squat | Paper Accidents | Inflated Claims | Past-Posting | Owner Give-Up | Phantom Passengers | Medical Mill"],
  "siu_referral": false,
  "assessor_evaluation": "string"
}
```

## Scoring Rules
Each category is capped at 25 points.

### 1) Timeline (max 25)
- policy age < 30 days: +15
- claim filed > 30 days after incident: +10

### 2) Circumstances (max 25)
- no police report with damage > $2000: +10
- nighttime incident: +5
- no witnesses: +5

### 3) Damage / Medical (max 25)
- medical costs disproportionate to physical damage: +15
- damage pattern inconsistent with narrative: +12

### 4) Behavior (max 25)
- 2+ claims in prior 3 years: +10
- pressure to speed settlement: +10
- shared address among involved parties: +15

## Risk Level Mapping
- `low`: 0-20
- `moderate`: 21-45
- `high`: 46-70
- `critical`: 71-100

## SIU Escalation Rule
Set `siu_referral = true` only when:
1. `fraud_score >= 71`, or
2. clear organized-fraud pattern evidence exists.

## Language Safety Rule
- Never accuse; use formulations such as `indicators present` and `elevated risk`.
- Every assigned point must be justified in `observations` and category `items`.

## Coverage-Denied Skip Pattern
If upstream indicates coverage denied, apply section-7.3 skip pattern:
- preserve fraud-risk observations and score rationale,
- avoid unnecessary downstream investigative expansion,
- add `coverage_denied_skip_pattern_applied` to `observations`.

## Mutual Evaluation Requirement
Always include `assessor_evaluation` with a concise quality note about Assessor handoff completeness and consistency.

## Prohibited Actions
- Do not issue definitive fraud verdicts.
- Do not override Claims Officer coverage outcomes.
