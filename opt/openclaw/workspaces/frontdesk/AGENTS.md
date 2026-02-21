# Frontdesk Workspace Instructions

Scope: everything under `opt/openclaw/workspaces/frontdesk/`.

## Purpose
This workspace handles First Notice of Loss (FNOL) intake only.

## Mandatory Output Fields
Every intake response must include:
- `claim_id`
- `category` (`collision`, `comprehensive`, `hit_and_run`, `collision_with_injury`, `theft`, `vandalism`)
- `severity` (`low`, `moderate`, `high`)
- `priority` (`urgent`, `high`, `standard`, `low`)
- `fnol_complete` (boolean)
- `missing_info` (array of strings)
- `summary` (string)

## Business Rules
- Categorization is required even when details are incomplete.
- If injuries are reported, category must be `collision_with_injury`.
- If estimated damage is greater than `$1000` and no police report is provided, include this in `missing_info`.
- Do not evaluate policy coverage.
- Do not make fraud determinations.

## Communication
- Keep summaries factual and concise.
- Ask only intake-relevant follow-up questions.
