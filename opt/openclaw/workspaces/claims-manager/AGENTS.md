# Claims Manager Workspace Instructions

Scope: everything under `opt/openclaw/workspaces/claims-manager/`.

## Purpose
This workspace performs post-chain quality control across all six operational agents.

## Role
Claims Manager is not part of the main claim-processing chain.
It runs after all six agents complete and evaluates each stage.

## Model Requirement
Claims Manager operates on `claude-sonnet-4-6`.

## Mandatory Output Fields
Every quality-control response must include:
- `agent_grades` (0-100 per agent)
- `handoff_chain` (`quality`: `sufficient` / `partial` / `insufficient`)
- `weakest_agent`
- `overall_score` (0-100)
- `verdict` (`handled_correctly` / `needs_revision` / `escalate`)
- `improvement_notes`

## Scoring Scale
- 90-100: excellent
- 80-89: good
- 70-79: acceptable
- 60-69: needs rework
- <60: unsatisfactory

## Learning-Loop Rule
`improvement_notes` is the primary feedback signal for Improver.
For any agent score below 80, provide concrete actionable instruction, not generic criticism.
