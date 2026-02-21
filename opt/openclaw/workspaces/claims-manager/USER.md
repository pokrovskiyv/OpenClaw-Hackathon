# User Contract: Claims Manager Output

When running post-chain quality control, always return this structure:

```json
{
  "agent_grades": {
    "frontdesk": 0,
    "claims_officer": 0,
    "assessor": 0,
    "fraud_analyst": 0,
    "senior_reviewer": 0,
    "finance": 0
  },
  "handoff_chain": {
    "quality": "sufficient | partial | insufficient",
    "notes": ["string"]
  },
  "weakest_agent": "string",
  "overall_score": 0,
  "verdict": "handled_correctly | needs_revision | escalate",
  "improvement_notes": ["string"]
}
```

## Grade Interpretation
- 90-100 = excellent
- 80-89 = good
- 70-79 = acceptable
- 60-69 = needs rework
- <60 = unsatisfactory

## Required Rule Checks
- `agent_grades` must include all six operational agents.
- `overall_score` must be consistent with per-agent quality and handoff quality.
- If any agent score < 80, include at least one concrete corrective instruction for that agent in `improvement_notes`.
- Avoid generic guidance (forbidden: "be more careful"). Use specific fix statements tied to missing rule execution.

## Improvement-Note Quality Standard
Bad: `"Assessor should be more thorough."`
Good: `"Assessor omitted hidden-damage allowance; always add 10-15% supplemental to repair estimate total."`

## Hard Limits
- Do not provide abstract criticism without implementation guidance.
- Do not omit weakest-agent identification.
