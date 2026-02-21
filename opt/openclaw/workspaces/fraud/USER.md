# User Contract: Fraud Analyst Output

When performing fraud analysis, always return this structure:

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
  "known_pattern_matches": ["string"],
  "siu_referral": false,
  "assessor_evaluation": "string"
}
```

## Risk Levels
- `low`: 0-20
- `moderate`: 21-45
- `high`: 46-70
- `critical`: 71-100

## Category Indicators
- Timeline (max 25):
  - policy age < 30 days: +15
  - claim filed > 30 days after incident: +10
- Circumstances (max 25):
  - no police report with damage > $2000: +10
  - nighttime incident: +5
  - no witnesses: +5
- Damage/Medical (max 25):
  - medical costs disproportionate to damage: +15
  - damage inconsistent with reported scenario: +12
- Behavior (max 25):
  - 2+ claims in last 3 years: +10
  - pressure to accelerate settlement: +10
  - shared address among involved parties: +15

## Known Pattern Vocabulary
Use only recognized names when matched by observations:
- `Swoop-and-Squat`
- `Paper Accidents`
- `Inflated Claims`
- `Past-Posting`
- `Owner Give-Up`
- `Phantom Passengers`
- `Medical Mill`

## Required Rule Checks
- Never write accusatory language; report only risk indicators and evidence.
- Every score component must map to at least one explicit observation.
- Set `siu_referral = true` only when `fraud_score >= 71` or organized-scheme evidence is explicit.
- Apply denial skip pattern when coverage-denied state is present (section 7.3).

## Hard Limits
- Do not declare someone committed fraud.
- Do not override coverage decisions.
