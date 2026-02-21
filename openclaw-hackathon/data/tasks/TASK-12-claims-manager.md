# TASK-12: Claims Manager (Quality Control Agent)
> Status: DONE → Goal: verify grading accuracy, improvement_notes quality, handoff chain assessment

## Context

Claims Manager is Agent #7 — quality control agent that evaluates all 6 pipeline agents after they complete. Runs on claude-sonnet-4-6 (stronger model). Not part of the main chain — runs post-pipeline.

**Key output fields:** agent_grades (0-100 per agent), handoff_chain (quality: sufficient/partial/insufficient), weakest_agent, overall_score (0-100), verdict (handled_correctly/needs_revision/escalate), improvement_notes.

**Grading scale:** 90-100 = excellent, 80-89 = good, 70-79 = acceptable, 60-69 = needs work, < 60 = unsatisfactory.

**Role in training loop:** `improvement_notes` is the PRIMARY signal for Improver. For agents scoring < 80, Manager must give SPECIFIC instructions: not "Assessor should be more thorough" but "Assessor did not calculate hidden damage buffer. Add: always include 10-15% supplemental."

**What Manager evaluates per agent:**
1. Accuracy of output
2. Completeness of analysis
3. Business logic compliance
4. Output format quality
5. Readiness for handoff to next agent

**Manager also uses Confidence Scores** from all agents as additional signal. Agent with confidence below threshold gets special note in handoff_chain.

## Current State

- `agents/manager.md` exists (runs on Sonnet)
- Manager output feeds evaluator.py (which just parses it, no LLM call)
- improvement_notes feed improver.py for prompt rewriting
- Need to verify grading accuracy and notes quality

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Prompt Engineer | prompt-engineer | Review and improve manager.md |
| Pipeline Analyst | eval-analyst | Analyze Manager grading accuracy, check improvement_notes specificity |
| Runner | Bash | Execute pipeline runs and benchmark |

## Work Plan

1. **Bash**: Run pipeline for several scenarios:
   ```bash
   cd openclaw-hackathon
   python3 loop.py --run-once --scenario TC-001
   python3 loop.py --run-once --scenario TC-005
   ```

2. **eval-analyst**: Analyze Manager output:
   - Read manager_eval from pipeline logs
   - Check: are grades reasonable? (TC-001 standard should be mostly 80+)
   - Check: are improvement_notes specific? (not generic)
   - Check: does Manager correctly identify weakest_agent?
   - Check: does handoff_chain quality assessment match actual data quality?
   - Check: does verdict match the scenario complexity?
   - Verify: Manager uses confidence scores as additional signal
   - Compare: Manager grades vs benchmark assertions — do they correlate?

3. **prompt-engineer**: Improve manager.md:
   - Strengthen improvement_notes specificity requirements
   - Add examples of good vs bad improvement_notes
   - Ensure grading criteria are explicit (what makes an 85 vs 75?)
   - Verify Manager checks all 6 agents, not just the weak ones
   - Ensure Manager evaluates Blind Assessment compliance (Assessor didn't see limits)

4. **Bash**: Re-run and compare Manager output quality

## Key Files

- `agents/manager.md` — agent prompt (PRIMARY edit target)
- `runner.py` — Manager invocation, full context feeding
- `evaluator.py` — parses Manager output (DO NOT MODIFY)
- `improver.py` — uses improvement_notes (DO NOT MODIFY)
- `docs/business-analysis.md` — Section 6.7 (lines 662-675)

## Acceptance Criteria

- [ ] Manager grades all 6 agents (not skipping any)
- [ ] Grades are differentiated (not all 85s — reflects actual quality differences)
- [ ] improvement_notes are specific and actionable (cite what went wrong + how to fix)
- [ ] weakest_agent correctly identified
- [ ] handoff_chain quality matches actual data quality between agents
- [ ] verdict appropriate: handled_correctly for standard cases, needs_revision for edge cases
- [ ] Manager detects Blind Assessment compliance/violations
- [ ] No regression in benchmark score

## Verification

```bash
cd openclaw-hackathon
python3 loop.py --run-once --scenario TC-001
python3 -c "
import json
d = json.load(open('logs/iter_000/TC-001/pipeline.json'))
m = d['pipeline_state']['manager_eval']
print('Grades:', json.dumps(m.get('agent_grades', {}), indent=2))
print('Weakest:', m.get('weakest_agent'))
print('Notes:', m.get('improvement_notes', [])[:3])
"
```

## Constraints

- Do NOT modify evaluator.py, improver.py, loop.py
- Manager runs on Sonnet — keep prompt efficient (no unnecessary verbosity)
- Manager is evaluation only — does NOT change pipeline decisions
