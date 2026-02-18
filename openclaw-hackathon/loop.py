#!/usr/bin/env python3
"""
Main Eval Loop Controller
─────────────────────────
Orchestrates: Run Pipeline → Evaluate → Improve → Repeat

Usage:
  python loop.py                  # Run full loop (default 10 iterations)
  python loop.py --iterations 5   # Custom iteration count
  python loop.py --run-once       # Single run + eval (no improvement)
  python loop.py --dry-run        # Full loop but don't write prompt changes
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

from lib.config import (
    AGENT_ORDER, TEST_CASES_DIR, LOGS_DIR, RESULTS_DIR,
    MAX_ITERATIONS, PASSING_SCORE, ANTHROPIC_API_KEY
)
from runner import run_all_scenarios, save_run_log
from evaluator import evaluate_all, save_eval_results, print_eval_summary
from improver import run_improvement_cycle


def load_scenarios():
    """Load test scenarios (prefer merged file with all 30 cases)."""
    all_path = os.path.join(TEST_CASES_DIR, "all_scenarios.json")
    fallback_path = os.path.join(TEST_CASES_DIR, "scenarios.json")
    path = all_path if os.path.exists(all_path) else fallback_path
    with open(path, "r") as f:
        scenarios = json.load(f)
    print(f"Loaded {len(scenarios)} scenarios from {os.path.basename(path)}")
    return scenarios


def save_iteration_summary(iteration: int, iter_log_dir: str, improvement_log: dict, score: float):
    """Append iteration results to a running summary file."""
    summary_path = os.path.join(RESULTS_DIR, "loop_summary.json")

    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            summary = json.load(f)
    else:
        summary = {"iterations": [], "best_score": 0, "best_iteration": 0}

    entry = {
        "iteration": iteration,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_score": score,
        "iter_log_dir": iter_log_dir,
        "agents_improved": [a["agent"] for a in improvement_log.get("agents_improved", [])],
        "agents_skipped": improvement_log.get("agents_skipped", []),
    }
    summary["iterations"].append(entry)

    if score > summary["best_score"]:
        summary["best_score"] = score
        summary["best_iteration"] = iteration

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary_path


def save_agent_progress(eval_results: list, iteration: int):
    """Append per-agent scores to results/agent_progress/{agent}.json."""
    progress_dir = os.path.join(RESULTS_DIR, "agent_progress")
    os.makedirs(progress_dir, exist_ok=True)

    for agent_name in AGENT_ORDER:
        path = os.path.join(progress_dir, f"{agent_name}.json")
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
        else:
            data = {"agent": agent_name, "iterations": []}

        scores = [e["scores"].get(agent_name, 0) for e in eval_results]
        avg = round(sum(scores) / len(scores), 1) if scores else 0
        data["iterations"].append({
            "iteration": iteration,
            "avg_score": avg,
            "by_scenario": {e["scenario_id"]: e["scores"].get(agent_name, 0) for e in eval_results},
        })

        with open(path, "w") as f:
            json.dump(data, f, indent=2)


def print_iteration_header(iteration: int, max_iter: int):
    print("\n" + "█" * 70)
    print(f"█  ITERATION {iteration}/{max_iter}")
    print("█" * 70)


def print_loop_summary(summary_path: str):
    """Print final loop summary with score progression."""
    with open(summary_path, "r") as f:
        summary = json.load(f)

    print("\n" + "═" * 70)
    print("TRAINING LOOP COMPLETE")
    print("═" * 70)

    print(f"\nBest Score: {summary['best_score']}/100 (iteration {summary['best_iteration']})")
    print(f"\nScore Progression:")

    for entry in summary["iterations"]:
        bar_len = int(entry["overall_score"] / 2)
        bar = "█" * bar_len + "░" * (50 - bar_len)
        marker = " ★" if entry["iteration"] == summary["best_iteration"] else ""
        print(f"  Iter {entry['iteration']:>2}: [{bar}] {entry['overall_score']:>5.1f}{marker}")

        if entry.get("agents_improved"):
            print(f"           Improved: {', '.join(entry['agents_improved'])}")

    print("═" * 70)


def main():
    parser = argparse.ArgumentParser(description="OpenClaw Hackathon Agent Training Loop")
    parser.add_argument("--iterations", type=int, default=MAX_ITERATIONS, help="Max iterations")
    parser.add_argument("--run-once", action="store_true", help="Single run + eval only")
    parser.add_argument("--dry-run", action="store_true", help="Don't write prompt changes")
    parser.add_argument("--scenario", type=str, help="Run specific scenario by ID")
    parser.add_argument("--passing-score", type=float, default=PASSING_SCORE, help="Score to stop at")
    args = parser.parse_args()

    # Validate API key
    if not ANTHROPIC_API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    # Load scenarios
    scenarios = load_scenarios()
    if args.scenario:
        scenarios = [s for s in scenarios if s["id"] == args.scenario]
        if not scenarios:
            print(f"Scenario '{args.scenario}' not found")
            sys.exit(1)

    max_iter = 1 if args.run_once else args.iterations
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    print(f"\n🦞 OpenClaw Agent Training Loop")
    print(f"   Scenarios: {len(scenarios)}")
    print(f"   Max iterations: {max_iter}")
    print(f"   Passing score: {args.passing_score}")
    print(f"   Dry run: {args.dry_run}")

    summary_path = None

    for iteration in range(1, max_iter + 1):
        print_iteration_header(iteration, max_iter)

        # ── Phase 1: Run Pipeline ──
        print("\n📋 PHASE 1: Running pipeline...")
        run_results = run_all_scenarios(scenarios)
        iter_log_dir = save_run_log(run_results, iteration)
        print(f"   Saved: {iter_log_dir}")

        # ── Phase 2: Evaluate ──
        print("\n🔍 PHASE 2: Evaluating outputs...")
        eval_results = evaluate_all(run_results, scenarios)
        save_eval_results(eval_results, iteration)
        print_eval_summary(eval_results)
        print(f"   Saved: {iter_log_dir}")
        save_agent_progress(eval_results, iteration)

        overall = round(sum(e["overall_score"] for e in eval_results) / len(eval_results), 1) if eval_results else 0

        # ── Phase 3: Improve ──
        if not args.run_once and overall < args.passing_score:
            print(f"\n🔧 PHASE 3: Improving agents (score {overall} < {args.passing_score})...")
            improvement_log = run_improvement_cycle(eval_results, dry_run=args.dry_run, iteration=iteration)
        else:
            improvement_log = {"agents_improved": [], "agents_skipped": AGENT_ORDER}
            if overall >= args.passing_score:
                print(f"\n✅ Score {overall} >= {args.passing_score} — agents are ready!")

        # ── Save iteration summary ──
        summary_path = save_iteration_summary(iteration, iter_log_dir, improvement_log, overall)

        # ── Check stopping condition ──
        if overall >= args.passing_score:
            print(f"\n🎉 Passing score reached at iteration {iteration}!")
            break

        if not improvement_log.get("agents_improved") and not args.run_once:
            print(f"\n⚠ No agents improved — possible plateau. Stopping.")
            break

    # ── Final Summary ──
    if summary_path:
        print_loop_summary(summary_path)


if __name__ == "__main__":
    main()
