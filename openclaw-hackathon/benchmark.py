#!/usr/bin/env python3
"""
Benchmark runner — Measures pipeline quality using deterministic assertions + LLM judge.

Usage:
  python benchmark.py                    # benchmark latest iteration
  python benchmark.py --iter 0           # benchmark specific iteration
  python benchmark.py --no-llm-judge     # fast mode, assertions only
  python benchmark.py --scenario TC-001  # benchmark single scenario
  python benchmark.py --history          # show score trend across iterations

Score formula:
  benchmark_score = assertions_pass_rate * 0.40 + llm_judge_overall * 0.60
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

from lib.assertions import evaluate_scenario
from lib.config import LOGS_DIR, RESULTS_DIR, TEST_CASES_DIR

ASSERTIONS_WEIGHT = 0.40
LLM_JUDGE_WEIGHT = 0.60


def find_latest_iteration():
    """Find the highest-numbered iter_NNN directory in logs/."""
    if not os.path.isdir(LOGS_DIR):
        return None
    dirs = []
    for name in os.listdir(LOGS_DIR):
        if name.startswith("iter_") and os.path.isdir(os.path.join(LOGS_DIR, name)):
            try:
                dirs.append(int(name.split("_")[1]))
            except (ValueError, IndexError):
                continue
    return max(dirs) if dirs else None


def load_scenarios(scenario_filter=None):
    """Load test scenarios from all_scenarios.json or scenarios.json."""
    all_path = os.path.join(TEST_CASES_DIR, "all_scenarios.json")
    fallback_path = os.path.join(TEST_CASES_DIR, "scenarios.json")
    path = all_path if os.path.exists(all_path) else fallback_path

    if not os.path.exists(path):
        print(f"Error: No scenarios file found at {path}")
        sys.exit(1)

    with open(path, "r") as f:
        scenarios = json.load(f)

    if scenario_filter:
        scenarios = [s for s in scenarios if s["id"] == scenario_filter]
        if not scenarios:
            print(f"Error: Scenario '{scenario_filter}' not found")
            sys.exit(1)

    return scenarios


def load_pipeline_state(iter_num, scenario_id):
    """Load pipeline_state from logs/iter_NNN/TC-XXX/pipeline.json."""
    path = os.path.join(LOGS_DIR, f"iter_{iter_num:03d}", scenario_id, "pipeline.json")
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("pipeline_state", {})
    except (json.JSONDecodeError, KeyError):
        return None


def run_assertions(scenarios, iter_num):
    """Run deterministic assertions for all scenarios in an iteration."""
    results = []
    total_passed = 0
    total_assertions = 0
    total_critical_passed = 0
    total_critical = 0

    for scenario in scenarios:
        sid = scenario["id"]
        pipeline_state = load_pipeline_state(iter_num, sid)

        if pipeline_state is None:
            results.append({
                "scenario_id": sid,
                "scenario_name": scenario.get("name", ""),
                "verdict": "SKIP",
                "assertions": {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0},
                "critical": {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0},
                "reason": "No pipeline output found",
            })
            continue

        result = evaluate_scenario(scenario, pipeline_state)
        results.append(result)

        total_passed += result["assertions"]["passed"]
        total_assertions += result["assertions"]["total"]
        total_critical_passed += result["critical"]["passed"]
        total_critical += result["critical"]["total"]

    pass_rate = (total_passed / total_assertions * 100) if total_assertions > 0 else 0
    critical_rate = (total_critical_passed / total_critical * 100) if total_critical > 0 else 0

    return {
        "per_scenario": results,
        "total_assertions": total_assertions,
        "total_passed": total_passed,
        "pass_rate": round(pass_rate, 1),
        "critical_pass_rate": round(critical_rate, 1),
    }


def compute_benchmark_score(assertions_pass_rate, llm_judge_overall):
    """Compute the weighted benchmark score (0-100)."""
    assertion_component = assertions_pass_rate * ASSERTIONS_WEIGHT
    judge_component = (llm_judge_overall / 10.0 * 100) * LLM_JUDGE_WEIGHT
    return round(assertion_component + judge_component, 1)


def supports_color():
    """Check if the terminal supports ANSI colors."""
    if os.environ.get("NO_COLOR"):
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def colorize(text, code):
    """Wrap text in ANSI color code if terminal supports it."""
    if not supports_color():
        return text
    return f"\033[{code}m{text}\033[0m"


def red(text):
    return colorize(text, "31")


def green(text):
    return colorize(text, "32")


def yellow(text):
    return colorize(text, "33")


def bold(text):
    return colorize(text, "1")


def verdict_color(verdict):
    """Color a verdict string."""
    if verdict == "PASS":
        return green(verdict)
    if verdict == "FAIL":
        return red(verdict)
    return yellow(verdict)


def print_assertion_results(assertion_data):
    """Print formatted assertion results table."""
    print(f"\n{bold('ASSERTION RESULTS')}")
    print("=" * 80)

    header = f"  {'Scenario':<35} {'Pass':<8} {'Crit':<8} {'Rate':>6}  {'Verdict'}"
    print(header)
    print("-" * 80)

    for r in assertion_data["per_scenario"]:
        name = r.get("scenario_name", r["scenario_id"])[:33]
        if r.get("verdict") == "SKIP":
            print(f"  {name:<35} {'--':<8} {'--':<8} {'--':>6}  {yellow('SKIP')}")
            continue

        a = r["assertions"]
        c = r["critical"]
        pass_str = f"{a['passed']}/{a['total']}"
        crit_str = f"{c['passed']}/{c['total']}"
        rate_str = f"{a['pass_rate']:>5.1f}%"
        print(f"  {name:<35} {pass_str:<8} {crit_str:<8} {rate_str}  {verdict_color(r['verdict'])}")

    print("-" * 80)
    print(f"  {'TOTAL':<35} {assertion_data['total_passed']}/{assertion_data['total_assertions']:<7}"
          f" {'':8} {assertion_data['pass_rate']:>5.1f}%")
    print(f"  {'Critical pass rate':<35} {'':8} {'':8} {assertion_data['critical_pass_rate']:>5.1f}%")


def print_judge_results(judge_data):
    """Print formatted LLM judge results table."""
    print(f"\n{bold('LLM JUDGE RESULTS')} (model: claude-opus-4-6)")
    print("=" * 80)

    header = f"  {'Scenario':<35} {'Corr':>5} {'Comp':>5} {'Biz':>5} {'Reas':>5} {'Fmt':>5} {'Avg':>6}"
    print(header)
    print("-" * 80)

    for r in judge_data["per_scenario"]:
        sid = r.get("scenario_id", "?")
        s = r.get("scores", {})
        name = sid[:33]
        print(f"  {name:<35} {s.get('correctness', 0):>5.1f} {s.get('completeness', 0):>5.1f}"
              f" {s.get('business_logic', 0):>5.1f} {s.get('reasoning_quality', 0):>5.1f}"
              f" {s.get('format', 0):>5.1f} {r.get('overall', 0):>5.1f}")

    print("-" * 80)
    ca = judge_data.get("criteria_averages", {})
    print(f"  {'AVERAGE':<35} {ca.get('correctness', 0):>5.1f} {ca.get('completeness', 0):>5.1f}"
          f" {ca.get('business_logic', 0):>5.1f} {ca.get('reasoning_quality', 0):>5.1f}"
          f" {ca.get('format', 0):>5.1f} {judge_data.get('overall', 0):>5.1f}")


def print_benchmark_score(score, assertion_rate, judge_overall, use_judge):
    """Print the final benchmark score."""
    print(f"\n{bold('BENCHMARK SCORE')}")
    print("=" * 80)
    print(f"  Assertions pass rate:  {assertion_rate:>6.1f}%  (weight: {ASSERTIONS_WEIGHT:.0%})")

    if use_judge:
        judge_pct = judge_overall / 10.0 * 100
        print(f"  LLM judge overall:     {judge_pct:>6.1f}%  (weight: {LLM_JUDGE_WEIGHT:.0%})")
    else:
        print(f"  LLM judge:             {'skipped':>8}  (weight: {LLM_JUDGE_WEIGHT:.0%})")

    print("-" * 40)

    if use_judge:
        score_str = f"{score:.1f}/100"
    else:
        score_str = f"{assertion_rate:.1f}/100 (assertions only)"

    if score >= 85:
        print(f"  {bold('Final score:')}  {green(score_str)}")
    elif score >= 60:
        print(f"  {bold('Final score:')}  {yellow(score_str)}")
    else:
        print(f"  {bold('Final score:')}  {red(score_str)}")
    print("=" * 80)


def save_benchmark_results(iter_num, assertion_data, judge_data, score, use_judge):
    """Save benchmark results to results/benchmark_NNN.json."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, f"benchmark_{iter_num:03d}.json")

    data = {
        "iteration": iter_num,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmark_score": score,
        "assertions_weight": ASSERTIONS_WEIGHT,
        "llm_judge_weight": LLM_JUDGE_WEIGHT,
        "assertions": {
            "pass_rate": assertion_data["pass_rate"],
            "critical_pass_rate": assertion_data["critical_pass_rate"],
            "total": assertion_data["total_assertions"],
            "passed": assertion_data["total_passed"],
        },
        "llm_judge": {
            "enabled": use_judge,
            "overall": judge_data.get("overall", 0) if judge_data else 0,
            "criteria_averages": judge_data.get("criteria_averages", {}) if judge_data else {},
        },
        "per_scenario": [],
    }

    for a_result in assertion_data["per_scenario"]:
        sid = a_result["scenario_id"]
        entry = {
            "scenario_id": sid,
            "scenario_name": a_result.get("scenario_name", ""),
            "assertions_verdict": a_result.get("verdict", "SKIP"),
            "assertions_pass_rate": a_result.get("assertions", {}).get("pass_rate", 0),
            "critical_pass_rate": a_result.get("critical", {}).get("pass_rate", 0),
        }

        if judge_data:
            j_match = next(
                (j for j in judge_data.get("per_scenario", []) if j.get("scenario_id") == sid),
                None,
            )
            if j_match:
                entry["judge_overall"] = j_match.get("overall", 0)
                entry["judge_scores"] = j_match.get("scores", {})

        data["per_scenario"].append(entry)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return path


def show_history():
    """Display benchmark score trend across iterations."""
    if not os.path.isdir(RESULTS_DIR):
        print("No benchmark results found.")
        return

    files = sorted(
        f for f in os.listdir(RESULTS_DIR)
        if f.startswith("benchmark_") and f.endswith(".json")
    )

    if not files:
        print("No benchmark results found.")
        return

    print(f"\n{bold('BENCHMARK HISTORY')}")
    print("=" * 70)
    print(f"  {'Iter':<8} {'Score':>8} {'Assert%':>10} {'Judge':>8} {'Timestamp'}")
    print("-" * 70)

    for fname in files:
        path = os.path.join(RESULTS_DIR, fname)
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        iter_num = data.get("iteration", "?")
        score = data.get("benchmark_score", 0)
        assert_rate = data.get("assertions", {}).get("pass_rate", 0)
        judge_overall = data.get("llm_judge", {}).get("overall", 0)
        ts = data.get("timestamp", "")[:19]

        judge_str = f"{judge_overall:.1f}/10" if data.get("llm_judge", {}).get("enabled") else "skipped"

        print(f"  {iter_num:<8} {score:>7.1f} {assert_rate:>9.1f}% {judge_str:>8} {ts}")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Benchmark pipeline quality")
    parser.add_argument("--iter", type=int, default=None, help="Iteration number to benchmark")
    parser.add_argument("--no-llm-judge", action="store_true", help="Skip LLM judge (assertions only)")
    parser.add_argument("--scenario", type=str, default=None, help="Benchmark a single scenario (e.g., TC-001)")
    parser.add_argument("--history", action="store_true", help="Show benchmark score trend")
    args = parser.parse_args()

    if args.history:
        show_history()
        return

    iter_num = args.iter
    if iter_num is None:
        iter_num = find_latest_iteration()
        if iter_num is None:
            print("Error: No iteration logs found in", LOGS_DIR)
            print("Run the pipeline first: python loop.py --run-once")
            sys.exit(1)

    iter_dir = os.path.join(LOGS_DIR, f"iter_{iter_num:03d}")
    if not os.path.isdir(iter_dir):
        print(f"Error: Iteration directory not found: {iter_dir}")
        sys.exit(1)

    print(f"\n{bold('BENCHMARK')} — Iteration {iter_num}")
    print(f"  Logs: {iter_dir}")

    scenarios = load_scenarios(args.scenario)
    print(f"  Scenarios: {len(scenarios)}")
    print()

    # Phase 1: Deterministic assertions
    print(bold("Phase 1: Deterministic Assertions"))
    print("-" * 40)
    assertion_data = run_assertions(scenarios, iter_num)
    print_assertion_results(assertion_data)

    # Phase 2: LLM judge (optional)
    judge_data = None
    use_judge = not args.no_llm_judge

    if use_judge:
        from lib.llm_judge import judge_all

        print(f"\n{bold('Phase 2: LLM Judge')}")
        print("-" * 40)

        pipeline_states = {}
        for scenario in scenarios:
            ps = load_pipeline_state(iter_num, scenario["id"])
            if ps:
                pipeline_states[scenario["id"]] = ps

        judge_data = judge_all(scenarios, pipeline_states)
        print_judge_results(judge_data)

    # Compute final score
    assertion_rate = assertion_data["pass_rate"]
    judge_overall = judge_data["overall"] if judge_data else 0

    if use_judge:
        score = compute_benchmark_score(assertion_rate, judge_overall)
    else:
        score = assertion_rate

    print_benchmark_score(score, assertion_rate, judge_overall, use_judge)

    # Save results
    path = save_benchmark_results(iter_num, assertion_data, judge_data, score, use_judge)
    print(f"\nResults saved to: {path}")


if __name__ == "__main__":
    main()
