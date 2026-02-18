#!/usr/bin/env python3
"""
LLM Evaluator — Scores agent outputs against expected results using LLM-as-judge.
Combines rule-based checks (objective) with LLM judgment (subjective).
"""
import json
import os
from datetime import datetime, timezone

from lib.config import EVAL_MODEL, AGENT_ORDER, LOGS_DIR, RESULTS_DIR
from lib.llm import call_llm_json


# ── Rule-Based Scoring (objective, fast, deterministic) ──────────────────────

def check_field_match(actual: dict, expected_key: str, expected_val, tolerance=None) -> tuple[float, str]:
    """Check if a field matches expected value. Returns (score 0-1, explanation)."""
    actual_val = actual.get(expected_key)

    if actual_val is None:
        return 0.0, f"Missing field '{expected_key}'"

    # Boolean match
    if isinstance(expected_val, bool):
        if actual_val == expected_val:
            return 1.0, f"'{expected_key}' correctly = {expected_val}"
        return 0.0, f"'{expected_key}' expected {expected_val}, got {actual_val}"

    # String match (case-insensitive)
    if isinstance(expected_val, str):
        if str(actual_val).lower() == expected_val.lower():
            return 1.0, f"'{expected_key}' correctly = '{expected_val}'"
        # Partial credit for close matches
        if expected_val.lower() in str(actual_val).lower():
            return 0.5, f"'{expected_key}' partial match: expected '{expected_val}', got '{actual_val}'"
        return 0.0, f"'{expected_key}' expected '{expected_val}', got '{actual_val}'"

    # Numeric match with tolerance
    if isinstance(expected_val, (int, float)):
        try:
            actual_num = float(actual_val)
            if tolerance:
                if abs(actual_num - expected_val) <= tolerance:
                    return 1.0, f"'{expected_key}' = {actual_num} (within tolerance of {expected_val})"
            elif actual_num == expected_val:
                return 1.0, f"'{expected_key}' correctly = {expected_val}"
            return 0.0, f"'{expected_key}' expected {expected_val}, got {actual_num}"
        except (ValueError, TypeError):
            return 0.0, f"'{expected_key}' expected number {expected_val}, got '{actual_val}'"

    return 0.5, f"'{expected_key}' present but complex comparison skipped"


def check_range(actual: dict, key: str, expected_range: list) -> tuple[float, str]:
    """Check if a numeric value falls within expected range [min, max]."""
    val = actual.get(key)
    if val is None:
        # Try nested paths
        parts = key.split(".")
        val = actual
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                val = None
                break

    if val is None:
        return 0.0, f"Missing field '{key}'"

    try:
        num = float(val)
        low, high = expected_range
        if low <= num <= high:
            return 1.0, f"'{key}' = {num} (within [{low}, {high}])"
        elif num < low:
            ratio = num / low if low > 0 else 0
            return max(0, ratio * 0.5), f"'{key}' = {num} below range [{low}, {high}]"
        else:
            ratio = high / num if num > 0 else 0
            return max(0, ratio * 0.5), f"'{key}' = {num} above range [{low}, {high}]"
    except (ValueError, TypeError):
        return 0.0, f"'{key}' not numeric: {val}"


def check_flags_present(actual: dict, flag_key: str, expected_flags: list) -> tuple[float, str]:
    """Check what fraction of expected flags were detected."""
    actual_flags = actual.get(flag_key, [])
    if isinstance(actual_flags, str):
        actual_flags = [actual_flags]

    # Normalize flags for comparison
    actual_lower = set()
    for f in actual_flags:
        if isinstance(f, dict):
            actual_lower.add(f.get("indicator", "").lower())
        else:
            actual_lower.add(str(f).lower())

    found = 0
    details = []
    for exp in expected_flags:
        exp_lower = exp.lower()
        # Check if any actual flag contains the expected keyword
        if any(exp_lower in a or a in exp_lower for a in actual_lower):
            found += 1
            details.append(f"✓ {exp}")
        else:
            details.append(f"✗ {exp}")

    score = found / len(expected_flags) if expected_flags else 1.0
    return score, f"Flags ({found}/{len(expected_flags)}): " + ", ".join(details)


def rule_based_eval(agent_name: str, actual_output: dict, expected: dict) -> dict:
    """Run rule-based checks for an agent's output."""
    checks = []

    if actual_output.get("_error") or actual_output.get("_parse_error"):
        return {"score": 0, "checks": [{"score": 0, "detail": "Agent returned error or invalid JSON"}]}

    exp = expected.get(agent_name, {})
    if not exp:
        return {"score": 0.5, "checks": [{"score": 0.5, "detail": "No expected values defined for this agent"}]}

    for key, val in exp.items():
        if key.endswith("_range"):
            base_key = key.replace("_range", "")
            s, d = check_range(actual_output, base_key, val)
            checks.append({"field": base_key, "score": s, "detail": d})
        elif key.endswith("_min"):
            base_key = key.replace("_min", "")
            actual_val = actual_output.get(base_key)
            if actual_val is not None:
                try:
                    s = 1.0 if float(actual_val) >= val else 0.0
                    d = f"'{base_key}' = {actual_val} (min expected: {val})"
                except (ValueError, TypeError):
                    s, d = 0.0, f"'{base_key}' not numeric"
            else:
                s, d = 0.0, f"Missing '{base_key}'"
            checks.append({"field": base_key, "score": s, "detail": d})
        elif key.endswith("_max"):
            base_key = key.replace("_max", "")
            actual_val = actual_output.get(base_key)
            if actual_val is not None:
                try:
                    s = 1.0 if float(actual_val) <= val else 0.0
                    d = f"'{base_key}' = {actual_val} (max expected: {val})"
                except (ValueError, TypeError):
                    s, d = 0.0, f"'{base_key}' not numeric"
            else:
                s, d = 0.0, f"Missing '{base_key}'"
            checks.append({"field": base_key, "score": s, "detail": d})
        elif key == "flags_expected":
            s, d = check_flags_present(actual_output, "indicators_found", val)
            checks.append({"field": "flags", "score": s, "detail": d})
            # Also check "flags" key
            s2, d2 = check_flags_present(actual_output, "flags", val)
            if s2 > s:
                checks[-1] = {"field": "flags", "score": s2, "detail": d2}
        elif isinstance(val, list):
            # Skip lists that aren't ranges or flags
            continue
        else:
            s, d = check_field_match(actual_output, key, val)
            checks.append({"field": key, "score": s, "detail": d})

    avg_score = sum(c["score"] for c in checks) / len(checks) if checks else 0
    return {"score": round(avg_score * 100, 1), "checks": checks}


# ── LLM-Based Scoring (subjective, nuanced) ────────────────────────────────

EVAL_SYSTEM_PROMPT = """You are an expert insurance claims evaluator. You assess AI agent outputs for quality, accuracy, and business appropriateness.

Score each dimension from 0-100:
1. **correctness**: Did the agent reach the right conclusion given the inputs?
2. **completeness**: Did the agent address all required aspects of their role?
3. **business_logic**: Are the business decisions sound? Would a real professional approve?
4. **format_compliance**: Does the output match the expected JSON structure?
5. **reasoning_quality**: Is the reasoning clear, documented, and defensible?

Respond with ONLY a JSON object:
{
  "correctness": <0-100>,
  "completeness": <0-100>,
  "business_logic": <0-100>,
  "format_compliance": <0-100>,
  "reasoning_quality": <0-100>,
  "overall": <0-100>,
  "strengths": ["<list>"],
  "weaknesses": ["<list>"],
  "critical_errors": ["<list of serious mistakes>"]
}"""


def llm_eval_agent(agent_name: str, agent_output: dict, scenario: dict, expected: dict) -> dict:
    """Use LLM to evaluate an agent's output quality."""
    user_msg = f"""## Agent: {agent_name.replace('_', ' ').title()}

## Scenario: {scenario['name']}
{scenario['description']}

## Claim Input
```json
{json.dumps(scenario['input'], indent=2)}
```

## Agent Output
```json
{json.dumps(agent_output, indent=2)}
```

## Expected Results
```json
{json.dumps(expected.get(agent_name, {}), indent=2)}
```

Evaluate this agent's output. Be strict but fair. Focus on business impact of any errors."""

    try:
        result = call_llm_json(EVAL_SYSTEM_PROMPT, user_msg, EVAL_MODEL)
        if result.get("_parse_error"):
            return {"overall": 50, "error": "LLM eval parse error"}
        return result
    except Exception as e:
        return {"overall": 50, "error": str(e)}


# ── Combined Evaluation ─────────────────────────────────────────────────────

def evaluate_run(run_log: dict, scenario: dict) -> dict:
    """Evaluate a complete pipeline run for one scenario."""
    eval_result = {
        "scenario_id": scenario["id"],
        "scenario_name": scenario["name"],
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "agents": {},
        "scores": {},
    }

    total_rule = 0
    total_llm = 0
    agent_count = 0

    for agent_name in AGENT_ORDER:
        agent_data = run_log.get("agents", {}).get(agent_name, {})
        agent_output = agent_data.get("output", {})

        # Rule-based eval
        rule_result = rule_based_eval(agent_name, agent_output, scenario.get("expected", {}))

        # LLM eval
        llm_result = llm_eval_agent(agent_name, agent_output, scenario, scenario.get("expected", {}))

        # Combined score (40% rule-based, 60% LLM)
        rule_score = rule_result["score"]
        llm_score = llm_result.get("overall", 50)
        combined = round(rule_score * 0.4 + llm_score * 0.6, 1)

        eval_result["agents"][agent_name] = {
            "rule_based": rule_result,
            "llm_eval": llm_result,
            "combined_score": combined,
        }
        eval_result["scores"][agent_name] = combined

        total_rule += rule_score
        total_llm += llm_score
        agent_count += 1

    eval_result["overall_score"] = round(
        (total_rule * 0.4 + total_llm * 0.6) / max(agent_count, 1), 1
    )
    eval_result["rule_based_avg"] = round(total_rule / max(agent_count, 1), 1)
    eval_result["llm_eval_avg"] = round(total_llm / max(agent_count, 1), 1)

    return eval_result


def evaluate_all(run_results: list, scenarios: list) -> list:
    """Evaluate all pipeline runs against their scenarios."""
    scenario_map = {s["id"]: s for s in scenarios}
    evals = []

    for run_log in run_results:
        scenario_id = run_log["scenario_id"]
        scenario = scenario_map.get(scenario_id)
        if scenario:
            print(f"  Evaluating: {scenario['name']}...", end=" ", flush=True)
            ev = evaluate_run(run_log, scenario)
            print(f"Score: {ev['overall_score']}")
            evals.append(ev)

    return evals


def save_eval_results(evals: list, iteration: int = 0) -> str:
    """Save evaluation results to hierarchical logs directory.

    Creates:
      logs/iter_{N:03d}/{scenario_id}/eval.json
    Returns the iteration directory path.
    """
    iter_dir = os.path.join(LOGS_DIR, f"iter_{iteration:03d}")

    for ev in evals:
        scenario_dir = os.path.join(iter_dir, ev["scenario_id"])
        os.makedirs(scenario_dir, exist_ok=True)
        with open(os.path.join(scenario_dir, "eval.json"), "w") as f:
            json.dump(ev, f, indent=2)

    return iter_dir


def print_eval_summary(evals: list):
    """Print a human-readable summary of evaluation results."""
    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    overall = round(sum(e["overall_score"] for e in evals) / len(evals), 1) if evals else 0
    print(f"\nOverall Score: {overall}/100")

    print(f"\n{'Agent':<20} {'Avg Score':<12} {'Status'}")
    print("-" * 50)
    for agent_name in AGENT_ORDER:
        scores = [e["scores"].get(agent_name, 0) for e in evals]
        avg = round(sum(scores) / len(scores), 1) if scores else 0
        status = "✓ Good" if avg >= 80 else "⚠ Needs work" if avg >= 60 else "✗ Poor"
        print(f"  {agent_name:<18} {avg:<12} {status}")

    print(f"\n{'Scenario':<40} {'Score':<12}")
    print("-" * 55)
    for ev in evals:
        print(f"  {ev['scenario_name'][:38]:<38} {ev['overall_score']:<12}")

    # Collect critical errors
    critical = []
    for ev in evals:
        for agent_name, agent_eval in ev["agents"].items():
            errors = agent_eval.get("llm_eval", {}).get("critical_errors", [])
            for err in errors:
                critical.append(f"  [{ev['scenario_id']}][{agent_name}] {err}")

    if critical:
        print(f"\nCRITICAL ERRORS ({len(critical)}):")
        for c in critical[:10]:  # Show top 10
            print(c)

    print("=" * 70)
