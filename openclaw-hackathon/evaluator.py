#!/usr/bin/env python3
"""
Evaluator — Reads Claims Manager evaluation from the pipeline run log.
Manager scores replace rule-based + LLM-as-judge approach.
"""
import json
import os
from datetime import datetime, timezone

from lib.config import AGENT_ORDER, LOGS_DIR, RESULTS_DIR


def evaluate_run(run_log: dict, scenario: dict) -> dict:
    """Extract manager evaluation from a completed pipeline run."""
    manager_eval = run_log.get("manager_eval", {})
    agent_grades = manager_eval.get("agent_grades", {})

    agents_result = {}
    scores_compat = {}  # backward-compat for loop.py save_agent_progress

    for agent_name in AGENT_ORDER:
        grade = agent_grades.get(agent_name, {})
        score = grade.get("score", 0)
        agents_result[agent_name] = {
            "score": score,
            "issues": grade.get("issues", []),
            "strengths": grade.get("strengths", []),
        }
        scores_compat[agent_name] = score

    overall = manager_eval.get("overall_score", 0)

    return {
        "scenario_id": scenario["id"],
        "scenario_name": scenario.get("name", ""),
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "overall_score": overall,
        "verdict": manager_eval.get("verdict", "unknown"),
        "weakest_agent": manager_eval.get("weakest_agent"),
        "agents": agents_result,
        "scores": scores_compat,  # backward-compat: loop.py uses e["scores"][agent_name]
        "improvement_notes": manager_eval.get("improvement_notes", {}),
        "handoff_chain": manager_eval.get("handoff_chain", []),
        "summary": manager_eval.get("summary", ""),
    }


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
            print(f"Score: {ev['overall_score']}  Verdict: {ev['verdict']}")
            evals.append(ev)

    return evals


def save_eval_results(evals: list, iteration: int = 0) -> str:
    """Save evaluation results to logs/iter_{N:03d}/{scenario_id}/eval.json."""
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
    print("EVALUATION SUMMARY  (Claims Manager Grades)")
    print("=" * 70)

    overall = round(sum(e["overall_score"] for e in evals) / len(evals), 1) if evals else 0
    print(f"\nOverall Score: {overall}/100")

    print(f"\n{'Agent':<20} {'Avg Score':<12} {'Status'}")
    print("-" * 50)
    for agent_name in AGENT_ORDER:
        scores = [e["agents"].get(agent_name, {}).get("score", 0) for e in evals]
        avg = round(sum(scores) / len(scores), 1) if scores else 0
        status = "✓ Good" if avg >= 80 else "⚠ Needs work" if avg >= 60 else "✗ Poor"
        print(f"  {agent_name:<18} {avg:<12} {status}")

    print(f"\n{'Scenario':<40} {'Score':<10} {'Verdict'}")
    print("-" * 65)
    for ev in evals:
        print(f"  {ev['scenario_name'][:38]:<38} {ev['overall_score']:<10} {ev.get('verdict', '—')}")

    # Show weakest agents
    weakest_counts: dict = {}
    for ev in evals:
        w = ev.get("weakest_agent")
        if w:
            weakest_counts[w] = weakest_counts.get(w, 0) + 1
    if weakest_counts:
        top = sorted(weakest_counts.items(), key=lambda x: -x[1])
        print(f"\nMost frequently weakest: {', '.join(f'{a} ({n}x)' for a, n in top[:3])}")

    # Show improvement notes
    all_notes: dict = {}
    for ev in evals:
        for agent, note in ev.get("improvement_notes", {}).items():
            all_notes.setdefault(agent, []).append(note)
    if all_notes:
        print(f"\nImprovement targets: {', '.join(all_notes.keys())}")

    print("=" * 70)
