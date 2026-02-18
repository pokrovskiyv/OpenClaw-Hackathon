#!/usr/bin/env python3
"""
Runtime CLI — Process a single real insurance claim through the 6-agent pipeline.

Usage:
  python cli.py --claim <input.json>

The claim input file must include a 'policy_number' field that corresponds to
a policy JSON file in data/policies/.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

from lib.config import ANTHROPIC_API_KEY, CLAIMS_DIR, DATA_DIR
from runner import AGENT_ORDER, run_pipeline, save_claim_output


def load_policy(policy_number: str) -> dict:
    """Load policy from data/policies/{policy_number}.json."""
    policy_path = os.path.join(DATA_DIR, f"{policy_number}.json")
    if not os.path.exists(policy_path):
        raise FileNotFoundError(
            f"Policy '{policy_number}' not found at {policy_path}\n"
            f"Available policies are in: {DATA_DIR}"
        )
    with open(policy_path) as f:
        return json.load(f)


def generate_claim_id() -> str:
    """Generate the next sequential claim ID based on existing claims."""
    os.makedirs(CLAIMS_DIR, exist_ok=True)
    existing = [d for d in os.listdir(CLAIMS_DIR) if d.startswith("CLM-")]
    numbers = []
    for d in existing:
        parts = d.split("-")
        if len(parts) == 3:
            try:
                numbers.append(int(parts[2]))
            except ValueError:
                pass
    next_num = max(numbers) + 1 if numbers else 1
    year = datetime.now().year
    return f"CLM-{year}-{next_num:04d}"


def update_policy_claims_history(policy_number: str, claim_id: str, run_log: dict):
    """Append the processed claim entry to the policy's claims_history."""
    policy_path = os.path.join(DATA_DIR, f"{policy_number}.json")
    if not os.path.exists(policy_path):
        return

    with open(policy_path) as f:
        policy = json.load(f)

    reviewer_output = run_log["agents"].get("senior_reviewer", {}).get("output", {})
    new_entry = {
        "claim_id": claim_id,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "type": "processed",
        "decision": reviewer_output.get("decision", "unknown"),
    }

    updated_policy = {
        **policy,
        "claims_history": policy.get("claims_history", []) + [new_entry],
    }

    with open(policy_path, "w") as f:
        json.dump(updated_policy, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw Runtime CLI — Process a real insurance claim"
    )
    parser.add_argument("--claim", required=True, help="Path to claim input JSON file")
    parser.add_argument("--no-verbose", action="store_true", help="Suppress per-agent output")
    args = parser.parse_args()

    if not ANTHROPIC_API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    if not os.path.exists(args.claim):
        print(f"ERROR: Claim file not found: {args.claim}")
        sys.exit(1)

    with open(args.claim) as f:
        input_data = json.load(f)

    policy_number = input_data.get("policy_number")
    if not policy_number:
        print("ERROR: Claim input must include a 'policy_number' field")
        sys.exit(1)

    try:
        policy = load_policy(policy_number)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    claim_id = generate_claim_id()
    verbose = not args.no_verbose

    print(f"\n OpenClaw Runtime — Processing Claim")
    print(f"   Claim ID:      {claim_id}")
    print(f"   Claimant:      {input_data.get('claimant_name', 'Unknown')}")
    print(f"   Policy:        {policy_number}")
    print(f"   Incident Type: {input_data.get('incident_type', 'Unknown')}")
    print(f"   Policy Status: {policy.get('status', 'unknown')}")

    # Build a scenario dict compatible with runner.run_pipeline()
    scenario = {
        "id": claim_id,
        "name": f"Runtime Claim — {input_data.get('claimant_name', 'Unknown')}",
        "input": input_data,
        "policy": policy,
    }

    print(f"\nRunning 6-agent pipeline...")
    run_log = run_pipeline(scenario, verbose=verbose)

    claim_dir = save_claim_output(claim_id, input_data, policy, run_log)
    update_policy_claims_history(policy_number, claim_id, run_log)

    reviewer = run_log["agents"].get("senior_reviewer", {}).get("output", {})
    finance = run_log["agents"].get("finance", {}).get("output", {})

    print(f"\n{'='*60}")
    print(f"CLAIM PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"  Claim ID:   {claim_id}")
    print(f"  Decision:   {str(reviewer.get('decision', 'unknown')).upper()}")
    if finance.get("action"):
        print(f"  Finance:    {finance['action']}")
    print(f"  Output:     {claim_dir}/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
