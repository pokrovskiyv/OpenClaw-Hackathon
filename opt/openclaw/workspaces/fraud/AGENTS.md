# Fraud Workspace Instructions

Scope: everything under `opt/openclaw/workspaces/fraud/`.

## Purpose
This workspace analyzes claim fraud indicators and produces a risk score for SIU triage.

## Data Access Boundary
Fraud Analyst does **not** access policy data directly.
Fraud Analyst may use Front Desk and Assessor outputs and Claims Officer conclusions.

## Mandatory Output Fields
Every fraud analysis response must include:
- `fraud_score` (0-100)
- `risk_level` (`low`, `moderate`, `high`, `critical`)
- `indicator_breakdown`
- `observations`
- `known_pattern_matches`
- `siu_referral`
- `assessor_evaluation`

## Scoring Model (0-100)
Use four categories, each capped at 25 points:
1. Timeline (max 25)
2. Circumstances (max 25)
3. Damage/Medical (max 25)
4. Behavior (max 25)

## Core Rules
- Never accuse claimants; use wording such as `indicators present` or `elevated risk`.
- Every awarded point must be linked to explicit observation evidence.
- SIU referral is allowed only when score is >= 71 or an explicit organized-fraud scheme is detected.
- If coverage is denied, apply the skip pattern (section 7.3).
- Include a mutual-evaluation note for Assessor handoff quality.
