#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROLE_REQUIRED_FIELDS: dict[str, list[str]] = {
    "caller_input": ["claimant", "phone", "incident_summary"],
    "front_desk": ["claim_id", "policy_number", "category", "customer_care", "fnol_complete", "routing"],
    "claims_officer": [
        "claim_id",
        "coverage_valid",
        "coverage_type",
        "deductible",
        "coverage_limit",
        "recommendation",
        "routing",
    ],
    "assessor": ["claim_id", "damage_catalog", "repair_estimate", "total_loss", "recommendation", "routing"],
    "fraud_analyst": ["claim_id", "fraud_score", "risk_level", "indicators_found", "recommendation", "routing"],
    "senior_reviewer": ["claim_id", "decision", "approved_amount", "deductible_applied", "payout_breakdown", "routing"],
    "finance": ["claim_id", "payment_authorized", "payment_details", "financial_summary"],
}

CUSTOMER_MESSAGE_FIELDS = ["voice_text", "chat_text", "next_action", "confirm_question"]


def load_payload(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError("Input payload must be a JSON object")
    return payload


def missing_fields(payload: dict, required: list[str]) -> list[str]:
    missing: list[str] = []
    for field in required:
        if field not in payload or payload[field] in (None, "", []):
            missing.append(field)
    return missing


def validate_customer_message(payload: dict) -> list[str]:
    missing: list[str] = []
    customer_message = payload.get("customer_message")
    if not isinstance(customer_message, dict):
        return ["customer_message"]
    for field in CUSTOMER_MESSAGE_FIELDS:
        if customer_message.get(field) in (None, ""):
            missing.append(f"customer_message.{field}")
    return missing


def detect_inconsistencies(role: str, payload: dict) -> list[str]:
    issues: list[str] = []

    if role == "claims_officer":
        recommendation = payload.get("recommendation")
        routing = payload.get("routing")
        if recommendation in {"deny", "partial_deny", "escalate"} and routing == "assessor":
            issues.append("claims_officer:non_proceed_recommendation_routed_to_assessor")

    if role == "fraud_analyst":
        risk_level = payload.get("risk_level")
        recommendation = payload.get("recommendation")
        if risk_level == "critical" and recommendation == "proceed":
            issues.append("fraud_analyst:critical_risk_cannot_proceed")

    if role == "senior_reviewer":
        decision = payload.get("decision")
        routing = payload.get("routing")
        approved_amount = payload.get("approved_amount")
        if decision in {"investigate", "denied", "referred"} and routing == "finance":
            issues.append("senior_reviewer:non_payable_decision_routed_to_finance")
        if decision in {"approved", "approved_partial"} and approved_amount in (None, ""):
            issues.append("senior_reviewer:approved_decision_missing_amount")

    if role == "finance":
        payment_authorized = payload.get("payment_authorized")
        payment_details = payload.get("payment_details", {})
        if payment_authorized is True:
            if not isinstance(payment_details, dict) or payment_details.get("amount") in (None, ""):
                issues.append("finance:authorized_payment_missing_amount")

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate upstream handoff payload between pipeline agents")
    parser.add_argument(
        "--role",
        required=True,
        choices=list(ROLE_REQUIRED_FIELDS.keys()),
        help="Role that produced the payload",
    )
    parser.add_argument("--input", required=True, help="Path to JSON payload from previous role")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    payload = load_payload(input_path)

    missing = missing_fields(payload, ROLE_REQUIRED_FIELDS[args.role])
    if args.role != "caller_input":
        missing.extend(validate_customer_message(payload))

    inconsistencies = detect_inconsistencies(args.role, payload)

    if inconsistencies:
        status = "hard_fail"
        exit_code = 2
        action = "escalate"
    elif missing:
        status = "soft_fail"
        exit_code = 1
        action = "request_fix"
    else:
        status = "pass"
        exit_code = 0
        action = "continue"

    result = {
        "status": status,
        "role": args.role,
        "input": str(input_path),
        "missing_fields": missing,
        "inconsistencies": inconsistencies,
        "action": action,
    }

    print(json.dumps(result, indent=2))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
