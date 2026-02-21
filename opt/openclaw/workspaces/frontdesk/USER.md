# User Contract: Front Desk Output

When processing a new intake, always return this structure:

```json
{
  "claim_id": "string",
  "category": "collision | comprehensive | hit_and_run | collision_with_injury | theft | vandalism",
  "severity": "low | moderate | high",
  "priority": "urgent | high | standard | low",
  "fnol_complete": true,
  "missing_info": ["string"],
  "summary": "string"
}
```

## Field Guidance
- `claim_id`: unique ID from intake system or generated case reference.
- `category`: always required, even if some details are missing.
- `severity`: operational impact level based on reported incident facts.
- `priority`: queue priority for handling.
- `fnol_complete`: `true` only when required intake facts are present.
- `missing_info`: explicit list of missing critical fields.
- `summary`: concise factual digest of what happened and what is missing.

## Required Rule Checks
- If injuries are reported, set category to `collision_with_injury`.
- If damage is estimated above `$1000` and no police report is provided, add a missing info item indicating police report is required.

## Hard Limits
- Do not evaluate insurance coverage.
- Do not classify fraud risk.
