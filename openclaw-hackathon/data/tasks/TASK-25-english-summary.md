# TASK-25: English Executive Summary
> Status: DOC → Goal: verify English version matches Russian PRD, check all facts/numbers

## Context

Appendix A (Section 20) provides a self-contained English executive summary for international judges who may not read Russian. It must accurately mirror the Russian PRD sections while being independently coherent.

The summary covers: Product Vision, Architecture (7 agents), Blind Assessment, Self-Improving Loop, Benchmark System, ROI, and Hackathon Readiness.

## Current State

- English summary exists but may be outdated vs latest Russian PRD changes
- Numbers and facts need cross-checking against Russian sections
- Secret Addition resolution should be clearly explained in English

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Domain Expert | insurance-analyst | Verify domain accuracy of English text |
| Writer | general-purpose | Cross-reference every fact/number with Russian PRD, fix mismatches |

## Work Plan

1. **general-purpose**: Cross-reference English summary against Russian PRD:
   - Read English summary (Appendix A, lines ~1555-1658)
   - Compare each fact/number against corresponding Russian section
   - Check: are 36 scenarios mentioned (not 30)?
   - Check: are 387 assertions mentioned (not 310)?
   - Check: is ROR decision type mentioned?
   - Check: does Blind Assessment explanation match Section 7.2a?
   - Check: does ROI match Section 5.5.4 ($662,700 savings, 167% year 1)?
   - Check: does benchmark formula match Section 10.2 (40% assertions + 60% LLM judge)?
   - Check: is oscillation detection mentioned?
   - Check: is MIN_AGENT_SCORE mentioned?

2. **insurance-analyst**: Verify domain accuracy of English text:
   - Are Ohio regulatory references correctly translated?
   - Is the coverage taxonomy accurate in English?
   - Is the bad faith explanation correct for English-speaking judges?
   - Is the subrogation explanation clear?

3. **Produce corrected English summary** if any mismatches found

## Key Files

- `docs/business-analysis.md` — Appendix A (lines ~1555-1658)
- `docs/business-analysis.md` — Russian sections for cross-reference (all sections)

## Acceptance Criteria

- [ ] Every number in English matches current Russian PRD
- [ ] Scenario count correct (36, not 30 or 7)
- [ ] Assertion count correct (387)
- [ ] ROR decision type mentioned
- [ ] Blind Assessment Architecture explained correctly
- [ ] ROI figures match Section 5.5.4
- [ ] Benchmark formula matches Section 10.2
- [ ] No facts exclusive to English that contradict Russian PRD
- [ ] Text reads naturally for English-speaking judges

## Constraints

- English summary should be self-contained (judges may read only this)
- Do NOT remove Russian content — only update Appendix A
- Keep concise — judges have limited time
