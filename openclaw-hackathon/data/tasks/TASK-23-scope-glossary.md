# TASK-23: Scope, Operations, and Glossary
> Status: DOC → Goal: verify "Running" vs "In progress" status matches code, check glossary completeness

## Context

Sections 16-18 of the PRD cover: what's out of scope (Section 16), how to run the system (Section 17), and domain/system/voice glossary (Section 18).

Section 16 status table:
| Status | Components |
|--------|-----------|
| **Running** | 6-agent pipeline + Claims Manager, benchmark (387 assertions + LLM judge opus), training loop with rollback + oscillation detection, confidence scores, Blind Assessment Architecture |
| **Designed / In Progress** | Demo UI (Lovable + Supabase), ClawdTalk voice, Telegram bot |

Section 17: Installation and command reference (pip install, loop.py flags, benchmark.py flags, log locations).

Section 18: Three glossary sections — insurance terms (14 entries), fraud schemes (7 entries), system terms (14 entries), ClawdTalk terms (5 entries).

## Current State

- Status table may be outdated as development progresses
- Command reference should match actual CLI flags
- Glossary may miss terms added in later sections (e.g., ROR, Blind Assessment)

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Pipeline Analyst | eval-analyst | Verify status table against actual code, check CLI flags, validate log paths |
| Codebase Explorer | Explore | Search codebase for terms not in glossary |

## Work Plan

1. **eval-analyst**: Verify Section 16 status table:
   - For each "Running" component — confirm it exists and works (run benchmark, check oscillation.py, etc.)
   - For each "Designed / In Progress" — check if supabase_sync.py exists, if ClawdTalk config exists
   - Verify "Not Implemented" list is still accurate
   - Check "Known Limitations" — are any resolved?

2. **eval-analyst**: Verify Section 17 commands:
   - Test each command listed (loop.py flags, benchmark.py flags)
   - Verify log directory structure matches documentation
   - Check if any new flags were added but not documented

3. **Explore**: Check glossary completeness:
   - Search codebase for terms like "ROR", "ror", "reservation_of_rights" — is ROR in glossary?
   - Check for "Blind Assessment" — is it in glossary?
   - Check for "whitelist", "field-level filtering" — are they in glossary?
   - Check for "oscillation", "rollback" — system terms that may be missing
   - Check for "fast_track" — should it be in glossary?
   - Check for "claim_status_update" — should it be in glossary?

## Key Files

- `docs/business-analysis.md` — Sections 16-18 (lines 1202-1359)
- `loop.py` — CLI flags reference
- `benchmark.py` — CLI flags reference
- `lib/oscillation.py` — verify it exists and works
- `lib/assertions.py` — verify it exists
- `lib/llm_judge.py` — verify it exists

## Acceptance Criteria

- [ ] Status table accurately reflects current codebase state
- [ ] All CLI commands in Section 17 verified to work
- [ ] Log directory structure matches documentation
- [ ] Glossary contains all domain-specific terms used in the PRD
- [ ] At least 5 missing glossary entries identified
- [ ] "Known Limitations" section reviewed — resolved items flagged

## Constraints

- Do NOT modify code — only verify and document
- Update business-analysis.md Section 16 status if it's inaccurate
