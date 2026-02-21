# TASK-18: Evaluation and Benchmark System
> Status: DONE → Goal: run full benchmark, verify 387 assertions, check LLM judge scoring

## Context

Section 10 defines two evaluation mechanisms:

**1. Internal evaluation (Claims Manager):**
- Manager grades each agent 0-100 on 5 criteria
- Evaluator.py simply parses Manager output (NO additional LLM call)
- improvement_notes are the training signal for Improver

**2. External benchmark:**
- Formula: `benchmark_score = assertions_pass_rate × 0.40 + llm_judge_overall × 0.60`
- **Assertions (40%):** 387 deterministic checks across 36 scenarios (248 critical, 139 non-critical)
  - Field presence, value correctness, numeric ranges, required flags, regulatory thresholds
  - Dot-notation paths (e.g., `repair_estimate.total`, `subrogation.applicable`)
  - Operators: eq, neq, gt, gte, lt, lte, in, not_in, contains, exists, regex
- **LLM Judge (60%):** claude-opus-4-6 evaluates correctness, completeness, business logic, reasoning, format
- Assertions are defined in `test_cases/all_scenarios.json` per scenario
- LLM judge criteria are also per scenario in `business_rules` array

## Current State

- `benchmark.py` — CLI runner implemented
- `lib/assertions.py` — assertion engine with dot-notation support
- `lib/llm_judge.py` — Opus-based judge
- 36 scenarios with 387 assertions
- Need to run full benchmark and verify all components

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Pipeline Analyst | eval-analyst | Run benchmark, analyze results, identify weak assertions |
| Runner | Bash | Execute benchmark commands |

## Work Plan

1. **Bash**: Run assertions-only benchmark (fast):
   ```bash
   cd openclaw-hackathon
   python3 benchmark.py --no-llm-judge
   ```

2. **eval-analyst**: Analyze benchmark results:
   - What is the overall assertions pass rate?
   - Which scenarios fail the most assertions?
   - Which agents have the most failing assertions?
   - Are there any assertions that always fail? (may indicate wrong assertion, not wrong agent)
   - Are critical assertions (248) more important than non-critical (139)?
   - Check: does every scenario have assertions?
   - Check: do assertion operators work correctly (eq, gt, contains, exists, etc.)?

3. **Bash**: Run full benchmark with LLM judge (if API key available):
   ```bash
   python3 benchmark.py --iter 0
   ```

4. **eval-analyst**: Analyze LLM judge results:
   - Does LLM judge agree with assertions? (correlation check)
   - Are there cases where assertions pass but LLM judge flags issues?
   - Are business_rules meaningful and specific?

5. **Check assertion quality**:
   - Read `lib/assertions.py` — is the engine robust?
   - Read a sample of assertions in `all_scenarios.json` — are they well-constructed?
   - Identify any missing assertions (critical business rules without assertions)

6. **Check benchmark history**:
   ```bash
   python3 benchmark.py --history
   ```

## Key Files

- `benchmark.py` — CLI benchmark runner
- `lib/assertions.py` — assertion engine
- `lib/llm_judge.py` — Opus judge
- `test_cases/all_scenarios.json` — 36 scenarios with 387 assertions
- `docs/business-analysis.md` — Section 10 (lines 961-999)

## Acceptance Criteria

- [ ] `python3 benchmark.py --no-llm-judge` runs without errors
- [ ] All 36 scenarios are evaluated
- [ ] 387 assertions are executed (248 critical + 139 non-critical)
- [ ] Assertion engine handles all operators correctly
- [ ] Dot-notation paths work for nested fields (e.g., repair_estimate.total)
- [ ] LLM judge produces scores for all evaluated scenarios
- [ ] Benchmark score formula: 40% assertions + 60% LLM judge
- [ ] `--history` flag shows iteration trend

## Verification

```bash
cd openclaw-hackathon
python3 benchmark.py --no-llm-judge
python3 benchmark.py --history
# Count assertions
python3 -c "
import json
d = json.load(open('test_cases/all_scenarios.json'))
total = sum(len(s.get('assertions', [])) for s in d)
critical = sum(1 for s in d for a in s.get('assertions', []) if a.get('critical'))
print(f'Total: {total}, Critical: {critical}, Non-critical: {total-critical}')
"
```

## Constraints

- Do NOT modify assertion engine (lib/assertions.py) unless bugs found
- Do NOT modify LLM judge (lib/llm_judge.py) unless bugs found
- Do NOT modify benchmark.py unless bugs found
- If assertions are wrong (testing for wrong value), fix the assertion, not the agent
