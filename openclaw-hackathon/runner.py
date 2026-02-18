#!/usr/bin/env python3
"""
Pipeline Runner — Simulates the 6-agent claims processing pipeline.
Each agent receives the claim data + all previous agent outputs.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

from lib.config import AGENT_MODEL, AGENT_ORDER, AGENTS_DIR, LOGS_DIR
from lib.llm import call_llm_json


def load_agent_prompt(agent_name: str) -> str:
    """Load agent SKILL.md as system prompt."""
    path = os.path.join(AGENTS_DIR, f"{agent_name}.md")
    with open(path, "r") as f:
        return f.read()


def build_user_message(agent_name: str, scenario: dict, pipeline_state: dict) -> str:
    """Build the user message for an agent, including claim input and prior outputs."""
    parts = []

    # Always include the original claim input
    parts.append("## Incoming Claim\n```json\n" + json.dumps(scenario["input"], indent=2) + "\n```")

    # Include policy data (agents that need it)
    if agent_name in ("claims_officer", "senior_reviewer", "finance"):
        parts.append("\n## Policy Data\n```json\n" + json.dumps(scenario["policy"], indent=2) + "\n```")

    # Include all previous agent outputs
    for prev_agent in AGENT_ORDER:
        if prev_agent == agent_name:
            break
        if prev_agent in pipeline_state:
            parts.append(
                f"\n## {prev_agent.replace('_', ' ').title()} Output\n```json\n"
                + json.dumps(pipeline_state[prev_agent], indent=2)
                + "\n```"
            )

    parts.append(
        "\n## Your Task\n"
        "Process this claim according to your role. Respond with ONLY a valid JSON object matching your output format. "
        "No markdown, no explanation — just the JSON."
    )

    return "\n".join(parts)


def run_pipeline(scenario: dict, verbose: bool = True) -> dict:
    """Run a single claim through the entire 6-agent pipeline."""
    pipeline_state = {}
    run_log = {
        "scenario_id": scenario["id"],
        "scenario_name": scenario["name"],
        "started_at": datetime.now(timezone.utc).isoformat(),
        "agents": {},
    }

    for agent_name in AGENT_ORDER:
        if verbose:
            print(f"  [{agent_name}] Processing...", end=" ", flush=True)

        t0 = time.time()
        system_prompt = load_agent_prompt(agent_name)
        user_message = build_user_message(agent_name, scenario, pipeline_state)

        try:
            result = call_llm_json(system_prompt, user_message, AGENT_MODEL)
            elapsed = time.time() - t0

            pipeline_state[agent_name] = result
            run_log["agents"][agent_name] = {
                "output": result,
                "elapsed_seconds": round(elapsed, 2),
                "success": not result.get("_parse_error", False),
            }

            if verbose:
                status = "✓" if not result.get("_parse_error") else "⚠ JSON parse error"
                print(f"{status} ({elapsed:.1f}s)")

            # Early termination: if claims officer denies, downstream agents should skip
            if agent_name == "claims_officer" and result.get("coverage_valid") is False:
                if verbose:
                    print(f"  [pipeline] Coverage denied — downstream agents will acknowledge skip")

        except Exception as e:
            elapsed = time.time() - t0
            pipeline_state[agent_name] = {"_error": str(e)}
            run_log["agents"][agent_name] = {
                "output": {"_error": str(e)},
                "elapsed_seconds": round(elapsed, 2),
                "success": False,
            }
            if verbose:
                print(f"✗ Error: {e}")

    run_log["completed_at"] = datetime.now(timezone.utc).isoformat()
    run_log["pipeline_state"] = pipeline_state

    return run_log


def run_all_scenarios(scenarios: list, verbose: bool = True) -> list:
    """Run all test scenarios through the pipeline."""
    results = []
    for i, scenario in enumerate(scenarios):
        if verbose:
            print(f"\n{'='*60}")
            print(f"Scenario {i+1}/{len(scenarios)}: {scenario['name']} [{scenario['id']}]")
            print(f"{'='*60}")

        result = run_pipeline(scenario, verbose)
        results.append(result)

    return results


def save_run_log(results: list, iteration: int = 0) -> str:
    """Save pipeline run results to logs directory."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"run_iter{iteration}_{timestamp}.json"
    filepath = os.path.join(LOGS_DIR, filename)

    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)

    return filepath


if __name__ == "__main__":
    from lib.config import TEST_CASES_DIR

    # Load test scenarios (prefer merged file with all 30 cases)
    all_path = os.path.join(TEST_CASES_DIR, "all_scenarios.json")
    fallback_path = os.path.join(TEST_CASES_DIR, "scenarios.json")
    scenarios_path = all_path if os.path.exists(all_path) else fallback_path
    with open(scenarios_path, "r") as f:
        scenarios = json.load(f)
    print(f"Loaded {len(scenarios)} scenarios from {os.path.basename(scenarios_path)}")

    # Optional: run specific scenario by ID
    if len(sys.argv) > 1:
        scenario_id = sys.argv[1]
        scenarios = [s for s in scenarios if s["id"] == scenario_id]
        if not scenarios:
            print(f"Scenario {scenario_id} not found")
            sys.exit(1)

    results = run_all_scenarios(scenarios)
    log_path = save_run_log(results)
    print(f"\nResults saved to: {log_path}")
