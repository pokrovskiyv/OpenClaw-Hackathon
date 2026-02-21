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
    MAX_ITERATIONS, PASSING_SCORE, MIN_AGENT_SCORE, ANTHROPIC_API_KEY
)
from lib.oscillation import check_oscillations
from runner import run_all_scenarios, save_run_log
from evaluator import evaluate_all, save_eval_results, print_eval_summary
from improver import run_improvement_cycle, check_and_rollback


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


def compute_agent_avg_scores(eval_results: list) -> dict:
    """Return {agent_name: avg_score} from a list of eval results."""
    agent_scores = {}
    for agent_name in AGENT_ORDER:
        scores = [e["scores"].get(agent_name, 0) for e in eval_results]
        agent_scores[agent_name] = round(sum(scores) / len(scores), 1) if scores else 0
    return agent_scores


def agents_below_minimum(agent_scores: dict, min_score: float) -> list:
    """Return list of (agent_name, score) tuples for agents below min_score."""
    return [(name, score) for name, score in agent_scores.items() if score < min_score]


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
    parser.add_argument("--min-agent-score", type=float, default=MIN_AGENT_SCORE,
                        help="Minimum per-agent score; loop continues if any agent is below this")
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
    print(f"   Min agent score: {args.min_agent_score}")
    print(f"   Dry run: {args.dry_run}")

    summary_path = None
    previous_agent_scores = {}      # {agent_name: avg_score} from previous iteration
    agent_score_history = {a: [] for a in AGENT_ORDER}  # per-agent score across iterations
    frozen_agents = set()           # agents frozen due to oscillation

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

        # ── Compute per-agent scores ──
        current_agent_scores = compute_agent_avg_scores(eval_results)
        for agent_name in AGENT_ORDER:
            agent_score_history[agent_name].append(current_agent_scores[agent_name])

        # ── Check per-agent minimum threshold ──
        weak_agents = agents_below_minimum(current_agent_scores, args.min_agent_score)
        if weak_agents:
            print(f"\n⚠ Agents below minimum ({args.min_agent_score}):")
            for name, score in weak_agents:
                print(f"    {name}: {score}")

        # ── Detect oscillation ──
        oscillating = check_oscillations(agent_score_history, min_swings=3)
        newly_frozen = [a for a in oscillating if a not in frozen_agents]
        if newly_frozen:
            print(f"\n🔄 Oscillation detected — freezing prompts for: {', '.join(newly_frozen)}")
            for a in newly_frozen:
                history_str = " -> ".join(str(s) for s in agent_score_history[a])
                print(f"    {a}: {history_str}")
            frozen_agents.update(newly_frozen)

        # ── Phase 3: Improve ──
        needs_improvement = overall < args.passing_score or weak_agents
        if not args.run_once and needs_improvement:
            print(f"\n🔧 PHASE 3: Improving agents (score {overall}, target {args.passing_score})...")
            improvement_log = run_improvement_cycle(
                eval_results,
                dry_run=args.dry_run,
                iteration=iteration,
                frozen_agents=frozen_agents,
            )

            # ── Phase 3b: Rollback check ──
            if previous_agent_scores and not args.dry_run:
                rolled_back = check_and_rollback(current_agent_scores, previous_agent_scores, iteration)
                if rolled_back:
                    improvement_log.setdefault("agents_rolled_back", []).extend(rolled_back)
        else:
            improvement_log = {"agents_improved": [], "agents_skipped": list(AGENT_ORDER)}
            if overall >= args.passing_score and not weak_agents:
                print(f"\n✅ Score {overall} >= {args.passing_score} — agents are ready!")

        previous_agent_scores = dict(current_agent_scores)

        # ── Save iteration summary ──
        summary_path = save_iteration_summary(iteration, iter_log_dir, improvement_log, overall)

        # ── Check stopping condition ──
        # Stop only if overall score passes AND all agents meet minimum threshold
        if overall >= args.passing_score and not weak_agents:
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
