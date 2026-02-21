# Skill: quality-control-review

## Purpose
Run post-process quality control over the full six-agent chain and generate actionable improvement instructions.

## Runtime Requirement
Execute using model `claude-sonnet-4-6`.

## Input
- Outputs from: Front Desk, Claims Officer, Assessor, Fraud Analyst, Senior Reviewer, Finance
- Handoff artifacts between each adjacent stage
- Final claim outcome metadata

## Output Schema
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
  "handoff_chain": {"quality": "sufficient | partial | insufficient", "notes": ["string"]},
  "weakest_agent": "string",
  "overall_score": 0,
  "verdict": "handled_correctly | needs_revision | escalate",
  "improvement_notes": ["string"]
}
```

## Evaluation Rules
1. Score each of the six agents from 0-100.
2. Evaluate handoff continuity and classify as `sufficient`, `partial`, or `insufficient`.
3. Set `weakest_agent` to the lowest-performing stage (or most impactful defect source in tie).
4. Set `overall_score` as chain-level quality synthesis.
5. Set verdict:
   - `handled_correctly` when chain quality is strong and no blocking defects,
   - `needs_revision` when correctable quality defects exist,
   - `escalate` when severe control/risk failures exist.

## Grading Scale
- 90-100: excellent
- 80-89: good
- 70-79: acceptable
- 60-69: needs rework
- <60: unsatisfactory

## Improvement-Loop Rules
- `improvement_notes` is the primary signal for Improver.
- For each agent score < 80, provide at least one specific implementation instruction.
- Instructions must be operational and testable, not generic.

### Example Instruction Quality
- Weak: `"Assessor should be more thorough."`
- Strong: `"Assessor did not apply hidden-damage allowance; enforce 10-15% supplemental in repair total before total-loss ratio calculation."`

## Prohibited Actions
- Do not output generic coaching without concrete next steps.
- Do not omit any of the six agent grades.
