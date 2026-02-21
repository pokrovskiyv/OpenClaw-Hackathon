# Skill: damage-assessment

## Purpose
Assess physical damage severity, estimate repair cost, and determine total-loss status without using policy data.

## Input
- Incident and vehicle details from upstream workflow
- Visual/inspection evidence (photos, notes, diagnostics)
- Optional workflow state signals (for example: coverage denied indicator)

## Output Schema
```json
{
  "damage_catalog": [{"area": "string", "damage_type": "string", "severity": "minor | moderate | severe", "evidence_ref": "string"}],
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

## Estimation Rules
1. Build `damage_catalog` from observed evidence only.
2. Compute base repair cost from labor + parts + paint/materials + sublet.
3. Add hidden-damage allowance in the 10–15% range.
4. Set `repair_estimate.total` to base cost plus hidden-damage allowance.

## Total-Loss Rules
1. Compute `total_loss_ratio = repair_estimate.total / vehicle_acv`.
2. Mark `total_loss = true` when `total_loss_ratio >= 0.75` (section 4).
3. Mark `total_loss = true` even below 0.75 when any of the following exists:
   - critical structural damage,
   - flood damage,
   - fire damage.

## Consistency and Fraud-Analyst Flags
- Record any contradiction between evidence, incident narrative, and damage pattern in `consistency_flags`.
- Use specific, auditable flags (for example: `impact_direction_mismatch`, `severity_mismatch`, `duplicate_damage_pattern`).

## Coverage-Denied Skip Pattern
- If upstream workflow indicates coverage denied, apply skip pattern (section 7.3):
  - keep technical findings and totals,
  - do not expand into non-required downstream valuation steps,
  - add `coverage_denied_skip_pattern_applied` to `consistency_flags`.

## Mutual Evaluation Requirement
Always include `claims_officer_evaluation` with a brief quality assessment of Claims Officer handoff data.

## Prohibited Actions
- Do not evaluate policy validity or coverage applicability.
- Do not issue final fraud determinations.
