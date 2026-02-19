#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone

AGENT_ORDER = [
    "front_desk",
    "claims_officer",
    "assessor",
    "fraud_analyst",
    "senior_reviewer",
    "finance",
    "claims_manager",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic execution plan for OMA claim pipeline")
    parser.add_argument("--claim-id", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--customer", required=True)
    parser.add_argument("--phone", required=True)
    parser.add_argument("--incident-type", required=True)
    parser.add_argument("--verified", action="store_true", help="Mark caller as pre-auth verified")
    parser.add_argument(
        "--upstream-validation",
        default="pass",
        choices=["pass", "soft_fail", "hard_fail"],
        help="Validation result from previous stage",
    )
    parser.add_argument(
        "--upstream-source",
        default="front_desk",
        help="Previous stage id/name",
    )
    args = parser.parse_args()

    if not args.verified:
        print(
            json.dumps(
                {
                    "claim_id": args.claim_id,
                    "status": "blocked",
                    "reason": "preauth_required",
                    "next": "run scripts/preauth_check.py first",
                },
                indent=2,
            )
        )
        raise SystemExit(1)

    if args.upstream_validation != "pass":
        next_action = "request_fix" if args.upstream_validation == "soft_fail" else "escalate"
        exit_code = 1 if args.upstream_validation == "soft_fail" else 2
        print(
            json.dumps(
                {
                    "claim_id": args.claim_id,
                    "status": "blocked",
                    "reason": "upstream_validation_failed",
                    "upstream": {
                        "source": args.upstream_source,
                        "status": args.upstream_validation,
                    },
                    "next": next_action,
                },
                indent=2,
            )
        )
        raise SystemExit(exit_code)

    output = {
        "claim_id": args.claim_id,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "journey": {
            "phase_1": "care_and_safety_triage",
            "phase_2": "incident_guidance",
            "phase_3": "preauth_and_claim_init",
            "phase_4": "six_role_pipeline",
            "phase_5": "payout_status_updates",
            "phase_6": "quality_control_review",
        },
        "caller": {
            "customer_name": args.customer,
            "phone": args.phone,
        },
        "policy": {
            "policy_number": args.policy,
        },
        "incident": {
            "type": args.incident_type,
        },
        "execution": {
            "mode": "sequential",
            "agents": AGENT_ORDER,
            "handoff_policy": {
                "required_upstream_validation": "pass",
                "on_soft_fail": "request_fix",
                "on_hard_fail": "escalate",
            },
            "customer_message_policy": {
                "require_voice_and_chat_variants": True,
                "same_semantic_intent": True,
                "single_next_action": True,
            },
            "business_objectives": {
                "customer_support": True,
                "routine_automation": True,
                "profitability_and_reputation_balance": True,
            },
        },
        "state": {
            "current": AGENT_ORDER[0],
            "completed": [],
            "pending": AGENT_ORDER,
        },
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
