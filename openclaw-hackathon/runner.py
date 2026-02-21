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

from lib.config import AGENT_MODEL, AGENT_ORDER, AGENTS_DIR, CLAIMS_DIR, LOGS_DIR, MANAGER_MODEL
from lib.llm import call_llm_json

# ── Blind Assessment: fields Assessor is allowed to see from Claims Officer ──
ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER = frozenset({
    "claim_id", "coverage_valid", "recommendation",
    "flags", "notes", "confidence", "input_assessment",
    "processed_at", "routing",
})


def filter_agent_output(output: dict, allowed_fields: set) -> dict:
    """Return a filtered copy of agent output, keeping only whitelisted fields.

    Adds _redacted metadata so the receiving agent knows filtering occurred.
    """
    filtered = {k: v for k, v in output.items() if k in allowed_fields}
    filtered["_redacted"] = True
    filtered["_redacted_reason"] = "Blind assessment policy — financial details withheld"
    return filtered


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
    if agent_name in ("claims_officer", "fraud_analyst", "senior_reviewer", "finance"):
        parts.append("\n## Policy Data\n```json\n" + json.dumps(scenario["policy"], indent=2) + "\n```")

    # Include all previous agent outputs (with field-level filtering where required)
    for prev_agent in AGENT_ORDER:
        if prev_agent == agent_name:
            break
        if prev_agent in pipeline_state:
            output = pipeline_state[prev_agent]
            # Blind Assessment: Assessor sees only whitelisted fields from Claims Officer
            if agent_name == "assessor" and prev_agent == "claims_officer":
                output = filter_agent_output(output, ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER)
            parts.append(
                f"\n## {prev_agent.replace('_', ' ').title()} Output\n```json\n"
                + json.dumps(output, indent=2)
                + "\n```"
            )

    parts.append(
        "\n## Your Task\n"
        "Process this claim according to your role. Respond with ONLY a valid JSON object matching your output format. "
        "No markdown, no explanation — just the JSON."
    )

    return "\n".join(parts)


def build_manager_message(scenario: dict, pipeline_state: dict) -> str:
    """Build the user message for the Claims Manager, including all agent outputs."""
    parts = []

    parts.append("## Original Claim\n```json\n" + json.dumps(scenario["input"], indent=2) + "\n```")
    parts.append("\n## Policy Data\n```json\n" + json.dumps(scenario.get("policy", {}), indent=2) + "\n```")

    for agent_name in AGENT_ORDER:
        if agent_name in pipeline_state:
            output = pipeline_state[agent_name]
            parts.append(
                f"\n## {agent_name.replace('_', ' ').title()} Output\n```json\n"
                + json.dumps(output, indent=2)
                + "\n```"
            )

    parts.append(
        "\n## Your Task\n"
        "Evaluate the quality of each agent's work on this claim. "
        "Respond with ONLY a valid JSON object matching your output format. "
        "No markdown, no explanation — just the JSON."
    )

    return "\n".join(parts)


def run_manager(scenario: dict, pipeline_state: dict, verbose: bool = True) -> dict:
    """Run the Claims Manager as the final evaluation step."""
    if verbose:
        print(f"  [manager] Evaluating pipeline...", end=" ", flush=True)

    t0 = time.time()
    system_prompt = load_agent_prompt("manager")
    user_message = build_manager_message(scenario, pipeline_state)

    try:
        result = call_llm_json(system_prompt, user_message, MANAGER_MODEL)
        elapsed = time.time() - t0
        if verbose:
            status = "✓" if not result.get("_parse_error") else "⚠ JSON parse error"
            print(f"{status} ({elapsed:.1f}s)")
        return result
    except Exception as e:
        elapsed = time.time() - t0
        if verbose:
            print(f"✗ Error: {e}")
        return {"_error": str(e)}


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

    # ── Manager evaluation (peer-chain review) ──
    manager_eval = run_manager(scenario, pipeline_state, verbose)
    run_log["manager_eval"] = manager_eval
    pipeline_state["manager"] = manager_eval

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
    """Save pipeline run results to hierarchical logs directory.

    Creates:
      logs/iter_{N:03d}/run_summary.json
      logs/iter_{N:03d}/{scenario_id}/pipeline.json
    Returns the iteration directory path.
    """
    iter_dir = os.path.join(LOGS_DIR, f"iter_{iteration:03d}")
    os.makedirs(iter_dir, exist_ok=True)

    for result in results:
        scenario_id = result["scenario_id"]
        scenario_dir = os.path.join(iter_dir, scenario_id)
        os.makedirs(scenario_dir, exist_ok=True)
        with open(os.path.join(scenario_dir, "pipeline.json"), "w") as f:
            json.dump(result, f, indent=2)

    summary = {
        "iteration": iteration,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scenarios_run": [r["scenario_id"] for r in results],
        "agent_order": AGENT_ORDER,
        "total_scenarios": len(results),
    }
    with open(os.path.join(iter_dir, "run_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    return iter_dir


def save_claim_output(claim_id: str, input_data: dict, policy: dict, run_log: dict) -> str:
    """Save runtime claim results to claims/{claim_id}/.

    Creates:
      claims/{claim_id}/input.json
      claims/{claim_id}/pipeline/01_front_desk.json ... 06_finance.json
      claims/{claim_id}/summary.json
    Returns the claim directory path.
    """
    claim_dir = os.path.join(CLAIMS_DIR, claim_id)
    pipeline_dir = os.path.join(claim_dir, "pipeline")
    os.makedirs(pipeline_dir, exist_ok=True)

    with open(os.path.join(claim_dir, "input.json"), "w") as f:
        json.dump(input_data, f, indent=2)

    for i, agent_name in enumerate(AGENT_ORDER, 1):
        if agent_name in run_log["agents"]:
            agent_file = f"{i:02d}_{agent_name}.json"
            with open(os.path.join(pipeline_dir, agent_file), "w") as f:
                json.dump(run_log["agents"][agent_name], f, indent=2)

    reviewer_output = run_log["agents"].get("senior_reviewer", {}).get("output", {})
    finance_output = run_log["agents"].get("finance", {}).get("output", {})

    summary = {
        "claim_id": claim_id,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "policy_number": input_data.get("policy_number"),
        "claimant": input_data.get("claimant_name"),
        "incident_type": input_data.get("incident_type"),
        "decision": reviewer_output.get("decision", "unknown"),
        "finance_action": finance_output.get("action") or finance_output.get("payment_amount"),
        "pipeline_status": "completed",
    }
    with open(os.path.join(claim_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    return claim_dir


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
