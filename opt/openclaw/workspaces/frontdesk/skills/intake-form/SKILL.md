# Skill: intake-form

## Purpose
Transform raw intake conversation into a normalized FNOL record for downstream claims processing.

## Input
Unstructured report details from claimant, witness, or call-center transcript.

## Output Schema
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

## Classification Rules
1. `category` is mandatory, even with incomplete details.
2. If injuries are present, category must be `collision_with_injury`.
3. Use `hit_and_run` when another party left the scene and identity is unknown.
4. Use `theft` for stolen vehicle/property events.
5. Use `vandalism` for intentional damage without collision dynamics.
6. Use `comprehensive` for non-collision losses (weather, fire, falling objects, etc.).
7. Use `collision` for vehicle impact events without reported injury.

## Severity Heuristic
- `low`: minor damage, no injuries, vehicle operable.
- `moderate`: meaningful damage or partial inoperability, no severe injuries.
- `high`: injuries, total loss indicators, major safety risk, or multi-party impact.

## Priority Heuristic
- `urgent`: injuries, active safety risk, or immediate escalation need.
- `high`: major damage, non-drivable vehicle, police/legal urgency.
- `standard`: typical claim flow without acute risk.
- `low`: minor damage and low operational urgency.

## Completeness Rules
Set `fnol_complete` to `false` when critical data is missing (for example: date/time, location, incident description, contact data, vehicle details, police report when required).

If estimated damage is above `$1000` and no police report is available, append a clear item in `missing_info` such as:
- `"Police report is required for damage estimates above $1000."`

## Prohibited Actions
- Do not evaluate policy coverage.
- Do not determine fraud.
