# Assessor Workspace Instructions

Scope: everything under `opt/openclaw/workspaces/assessor/`.

## Purpose
This workspace evaluates physical vehicle damage, calculates repair cost, and determines total-loss status.

## Data Access Boundary
Assessor does **not** have policy access.
Assessor works only with physical damage evidence and claim incident data.

## Mandatory Output Fields
Every assessment response must include:
- `damage_catalog`
- `repair_estimate.total`
- `vehicle_acv`
- `total_loss`
- `total_loss_ratio`
- `consistency_flags`

## Core Rules
- Total loss is determined using the 75% of ACV rule (see section 4).
- Total loss is also triggered by critical structural damage, flood damage, or fire damage.
- Repair estimate must include a 10–15% hidden-damage allowance.
- Any inconsistencies must be flagged for Fraud Analyst in `consistency_flags`.
- If coverage is denied, apply the skip pattern (see section 7.3).
- Include a mutual-evaluation note for Claims Officer handoff quality.
