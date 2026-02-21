# TASK-19: Training Loop
> Status: DONE → Goal: run training loop, verify rollback, oscillation detection, MIN_AGENT_SCORE

## Context

Section 11 defines the self-improving training loop: Run → Evaluate → Improve → Repeat.

**Three phases per iteration:**
1. **Run:** 36 scenarios through pipeline + Claims Manager → logs/iter_NNN/TC-XXX/pipeline.json
2. **Evaluate:** evaluator.py extracts Manager grades, verdict, improvement_notes → logs/iter_NNN/TC-XXX/eval.json
3. **Improve:** improver.py rewrites prompts for agents below threshold

**Improvement criteria:**
- Score >= 90 + no improvement_notes → skip
- Score >= 85 + no notes + no issues → skip
- Everything else → rewrite prompt

**Safety mechanisms:**
- **Rollback on regression:** > 5 points overall OR > 10 points per agent → restore from backup
- **Oscillation detection (lib/oscillation.py):** >= 3 direction changes (up→down→up) → exclude agent from rewriting
- **MIN_AGENT_SCORE = 70:** loop continues while any agent is below this threshold
- **Max iterations:** default 10
- **Passing score:** default 85/100
- **Plateau detection:** stop if no agents improved

**Improver rules:**
- Reads current prompt + improvement_notes + issues + strengths
- Generates complete new prompt (not diff)
- Saves backup to agents/backups/iter_NNN/
- Preserves business rules and output format

## Current State

- loop.py, evaluator.py, improver.py all implemented
- lib/oscillation.py implemented
- Backup mechanism works
- Need to verify all safety mechanisms

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Pipeline Analyst | eval-analyst | Analyze loop behavior, verify safety mechanisms |
| General | general-purpose | Read loop.py code, verify implementation matches PRD |
| Runner | Bash | Run training loop iterations |

## Work Plan

1. **general-purpose**: Read and verify code:
   - `loop.py` — main controller, iteration logic, stopping conditions
   - `evaluator.py` — grade extraction from Manager output
   - `improver.py` — prompt rewriting logic, backup mechanism
   - `lib/oscillation.py` — oscillation detection algorithm
   - `lib/config.py` — MIN_AGENT_SCORE, passing score, max iterations

2. **Bash**: Run single iteration:
   ```bash
   cd openclaw-hackathon
   python3 loop.py --run-once --scenario TC-001
   ```

3. **eval-analyst**: Verify safety mechanisms:
   - Check: does rollback trigger on > 5 point regression?
   - Check: does oscillation detection work with >= 3 direction changes?
   - Check: does MIN_AGENT_SCORE prevent premature stopping?
   - Check: are backups saved to agents/backups/iter_NNN/?
   - Check: does plateau detection stop the loop?
   - Read results/loop_summary.json for score progression

4. **Bash**: Test rollback (if safe to do):
   ```bash
   python3 loop.py --dry-run  # Evaluate without rewriting
   ```

5. **Document** any discrepancies between PRD and implementation

## Key Files

- `loop.py` — main controller (DO NOT MODIFY unless bugs found)
- `evaluator.py` — grade extraction (DO NOT MODIFY)
- `improver.py` — prompt rewriting (DO NOT MODIFY)
- `lib/oscillation.py` — oscillation detection
- `lib/config.py` — thresholds and constants
- `results/loop_summary.json` — score progression
- `docs/business-analysis.md` — Section 11 (lines 1003-1051)

## Acceptance Criteria

- [ ] loop.py runs without errors for at least 1 iteration
- [ ] evaluator.py correctly parses Manager output
- [ ] improver.py generates complete new prompts (not diffs)
- [ ] Backups saved to agents/backups/iter_NNN/
- [ ] Rollback threshold: > 5 overall OR > 10 per agent
- [ ] Oscillation detection: >= 3 direction changes → exclude agent
- [ ] MIN_AGENT_SCORE = 70 prevents stopping with weak agents
- [ ] loop_summary.json tracks score progression
- [ ] Plateau detection works (no improvement → stop)

## Verification

```bash
cd openclaw-hackathon
# Verify config
python3 -c "from lib.config import *; print('MIN_AGENT_SCORE:', MIN_AGENT_SCORE)"
# Run dry (evaluate only)
python3 loop.py --dry-run
# Check loop summary
python3 -c "import json; print(json.dumps(json.load(open('results/loop_summary.json')), indent=2))" 2>/dev/null || echo "No loop_summary yet"
```

## Constraints

- Do NOT modify loop.py, evaluator.py, improver.py unless actual bugs found
- Do NOT change MIN_AGENT_SCORE, passing score, or rollback thresholds
- Training loop is the core differentiator — handle with care
