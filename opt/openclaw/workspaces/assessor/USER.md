# User Contract: Assessor Output

When processing damage assessment, always return this structure:

```json
{
  "damage_catalog": [
    {
      "area": "string",
      "damage_type": "string",
      "severity": "minor | moderate | severe",
      "evidence_ref": "string"
    }
  ],
  "repair_estimate": {
    "labor": "number",
    "parts": "number",
    "paint_materials": "number",
    "sublet": "number",
    "hidden_damage_allowance_pct": "number",
    "total": "number"
  },
  "vehicle_acv": "number",
  "total_loss": true,
  "total_loss_ratio": "number",
  "consistency_flags": ["string"],
  "claims_officer_evaluation": "string"
}
```

## Field Guidance
- `damage_catalog`: objective list of observed damages tied to evidence.
- `repair_estimate.total`: must include hidden-damage allowance of 10–15%.
- `vehicle_acv`: actual cash value used as total-loss baseline.
- `total_loss_ratio`: `repair_estimate.total / vehicle_acv`.
- `total_loss`: `true` when ratio >= 0.75 or critical-trigger conditions are met.
- `consistency_flags`: mismatch indicators for Fraud Analyst follow-up.
- `claims_officer_evaluation`: concise quality note on Claims Officer handoff quality.

## Required Rule Checks
- Apply the 75% ACV total-loss rule (section 4).
- Force total-loss when critical structural damage, flood, or fire conditions are present.
- Apply denial skip pattern when coverage-denied state is provided by upstream workflow (section 7.3).

## Hard Limits
- Do not evaluate policy coverage.
- Do not classify fraud risk as final decision.
