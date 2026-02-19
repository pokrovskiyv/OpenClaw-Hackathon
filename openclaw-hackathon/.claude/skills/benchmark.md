---
name: benchmark
description: Run benchmark against the claims pipeline (deterministic assertions + LLM judge) and provide insights
---

# Claims Pipeline Benchmark

## When to Use

Invoke this skill when the user types:
- `/benchmark` (with any flags)
- "run benchmark"
- "how is the pipeline performing?"
- "benchmark results"
- "what's the current score?"
- "show me the benchmark"

---

## Evaluation Modes

| Mode | Command Flag | Speed | Weight |
|------|-------------|-------|--------|
| Deterministic assertions only | `--no-llm` | Fast (~5s) | 100% of score |
| LLM judge (claude-opus-4-6) | *(default)* | Slow (~60s) | 40% assert + 60% LLM |
| Specific iteration | `--iter N` | Same as above | — |
| History trend | `--history` | Fast | — |
| Single scenario deep-dive | `--scenario TC-XXX` | Fastest | — |

> **Score formula (full mode):** `benchmark_score = assertions_pass_rate × 100 × 0.40 + llm_judge_overall × 0.60`
> **Score formula (no-llm mode):** `benchmark_score = assertions_pass_rate × 100`

---

## Argument Parsing

Parse the user's invocation text to determine flags:

| User typed | benchmark.py flags |
|------------|-------------------|
| `/benchmark` | *(none — full mode, latest iter)* |
| `/benchmark --no-llm` | `--no-llm-judge` |
| `/benchmark --iter 3` | `--iter 3` |
| `/benchmark --history` | `--history` |
| `/benchmark --scenario TC-005` | Run pipeline for one scenario, then benchmark it |

Multiple flags can combine: `/benchmark --no-llm --iter 2` → `--no-llm-judge --iter 2`

---

## Step-by-Step Workflow

### Step 1 — Parse invocation arguments

Read the text after `/benchmark` and determine:
- `mode`: `full` | `no-llm` | `history` | `scenario`
- `iter`: integer or `None` (latest)
- `scenario`: scenario ID string or `None`

### Step 2 — Run benchmark.py via Bash

Always `cd openclaw-hackathon` first. Use `/tmp/bm_result.json` as the output file.

**History mode:**
```bash
cd openclaw-hackathon && python3 benchmark.py --history
```
*(No JSON output needed — the CLI table is the result. Print it directly.)*

**Assertions only (fast):**
```bash
cd openclaw-hackathon && python3 benchmark.py --no-llm-judge --output /tmp/bm_result.json
```

**Full benchmark (default):**
```bash
cd openclaw-hackathon && python3 benchmark.py --output /tmp/bm_result.json
```

**Specific iteration:**
```bash
cd openclaw-hackathon && python3 benchmark.py --iter N --output /tmp/bm_result.json
# or with no-llm:
cd openclaw-hackathon && python3 benchmark.py --iter N --no-llm-judge --output /tmp/bm_result.json
```

**Single scenario deep-dive:**
```bash
# First run the pipeline for that scenario
cd openclaw-hackathon && python3 loop.py --run-once --scenario TC-XXX
# Then benchmark latest iter with no-llm for speed
cd openclaw-hackathon && python3 benchmark.py --no-llm-judge --output /tmp/bm_result.json
```

### Step 3 — Read /tmp/bm_result.json

Use the Read tool to load `/tmp/bm_result.json`. Parse the JSON to extract key fields:

```
result.benchmark_score          — final score (0–100)
result.assertions_pass_rate     — deterministic pass rate (0.0–1.0)
result.llm_judge_overall        — LLM judge score (0–100), 0 if skipped
result.overall_pass_rate        — fraction of scenarios that PASS
result.scenarios_passed         — int
result.scenarios_total          — int
result.agent_pass_rates         — dict: agent_name → {passed, total, rate}
result.business_rules_pass_rate — fraction of business rules passing (0.0–1.0)
result.scenario_details         — list of per-scenario results
result.judge_results            — dict: scenario_id → {overall_score, narrative, agent_scores}
```

### Step 4 — Display results in chat

Show the raw CLI output (from Bash stdout) — it already has nicely formatted tables. Then add the analytical section below.

### Step 5 — Claude analytical commentary

After showing the tables, provide a structured insight block:

```
## Benchmark Insights

### Score Summary
[benchmark_score]/100 ([assertions only] deterministic | [llm_judge_overall]/100 LLM judge)
Scenarios: [scenarios_passed]/[scenarios_total] passing

### Weakest Agent
[identify the agent with lowest rate from agent_pass_rates]
[quote 1-2 specific failed_assertions from scenario_details to explain WHY]

### Critical Failures
[list the top 3 failed assertions from across scenario_details, with field name + detail]

### Business Rules
[business_rules_pass_rate × 100]% compliance — [comment if < 80%: which scenarios violated rules]

### LLM Judge Observations
[only if llm_judge_overall > 0]
[summarize key narratives from judge_results — what the judge praised or criticized]

### Recommendation
[One of:]
- "Score is [X] — run another training cycle: `python3 loop.py --iterations 1`"
- "Score is above 85 — pipeline is performing well. Consider running full benchmark to verify."
- "Critical assertion failures in [agent] — edit agents/[agent].md to fix [specific field]"
- "Fraud analyst / senior_reviewer disagreements — check for inconsistent thresholds"
```

---

## Interpreting Results & Providing Insights

### Agent weakness analysis
Find the agent with the lowest `rate` in `agent_pass_rates`. Then look at `scenario_details[].failed_assertions` filtered by `agent == weakest_agent`. List the specific fields failing (e.g., `fraud_score`, `coverage_valid`, `decision`).

### Pattern recognition in failures
- Multiple scenarios failing the **same field** → systematic prompt issue in that agent
- Failures only in **specific scenario types** (staged accidents, expired policies) → agent doesn't handle edge cases
- `llm_judge_overall` >> `assertions_pass_rate × 100` → agent reasons correctly but outputs wrong field names
- `llm_judge_overall` << `assertions_pass_rate × 100` → agent fills fields correctly but reasons poorly

### Training loop recommendation
| Score | Recommendation |
|-------|---------------|
| < 60 | Run 3+ more iterations: `python3 loop.py --iterations 3` |
| 60–80 | Run 1–2 iterations; focus on weakest agent prompt |
| 80–85 | One more iteration + check threshold config in lib/config.py |
| > 85 | Pipeline is production-ready. Full benchmark to confirm. |

### Specific agent guidance
- **front_desk**: failures in `category`, `severity`, `priority`, `fnol_complete`
- **claims_officer**: failures in `coverage_valid`, `policy_status`, `exclusions_triggered`
- **assessor**: failures in `total_loss`, `total_loss_ratio`, `repair_estimate.total`
- **fraud_analyst**: failures in `fraud_score` (range 0-100), `risk_level`, `recommendation`
- **senior_reviewer**: failures in `decision` (approved/denied/investigate/referred), `approved_amount`
- **finance**: failures in `payment_authorized`, `subrogation.applicable`, `rental_reimbursement.applicable`

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Running benchmark from wrong directory | Always `cd openclaw-hackathon` first |
| Benchmark shows 0 scenarios | Run `python3 loop.py --run-once` first to generate pipeline data |
| `--scenario` not a benchmark flag | `--scenario` filters test; run pipeline first, then benchmark latest iter |
| Treating no-llm score as final | No-llm score is a lower bound; full score is canonical |
| Ignoring `judge_results.narratives` | The narrative text from Opus often pinpoints the exact issue |
| Forgetting that history mode has no JSON output | For `--history`, just display the CLI table and comment on the trend |

---

## Example Invocation Flow

```
User: /benchmark --no-llm

Claude:
1. Runs: cd openclaw-hackathon && python3 benchmark.py --no-llm-judge --output /tmp/bm_result.json
2. Reads: /tmp/bm_result.json
3. Displays: CLI table output (scenario results + agent pass rates)
4. Provides insight:
   "Benchmark Score: 71.4/100 (assertions only, no LLM judge)
   Weakest agent: fraud_analyst (4/10 — 40% pass rate)
   Top failure: fraud_score out of range in TC-002, TC-005, TC-007
   Recommendation: Edit agents/fraud_analyst.md to enforce numeric fraud_score 0-100.
   Then run: python3 loop.py --iterations 1"
```
