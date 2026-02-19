#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROLE_REQUIRED_FIELDS: dict[str, list[str]] = {
    "caller_input": ["claimant", "phone", "incident_summary"],
    "front_desk": ["claim_id", "policy_number", "category", "customer_care", "fnol_complete", "routing"],
    "claims_officer": [
        "claim_id",
        "input_assessment",
        "coverage_valid",
        "coverage_type",
        "deductible",
        "coverage_limit",
        "recommendation",
        "routing",
    ],
    "assessor": [
        "claim_id",
        "input_assessment",
        "damage_catalog",
        "repair_estimate",
        "total_loss",
        "recommendation",
        "routing",
    ],
    "fraud_analyst": [
        "claim_id",
        "input_assessment",
        "fraud_score",
        "risk_level",
        "indicators_found",
        "recommendation",
        "routing",
    ],
    "senior_reviewer": [
        "claim_id",
        "input_assessment",
        "decision",
        "approved_amount",
        "deductible_applied",
        "payout_breakdown",
        "routing",
    ],
    "finance": ["claim_id", "input_assessment", "payment_authorized", "payment_details", "financial_summary"],
    "claims_manager": [
        "claim_id",
        "agent_grades",
        "handoff_chain",
        "overall_score",
        "verdict",
        "improvement_notes",
    ],
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
        if field not in payload:
            missing.append(field)
            continue
        value = payload[field]
        if value is None:
            missing.append(field)
            continue
        if isinstance(value, str) and value == "":
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

    if role in {"claims_officer", "assessor", "fraud_analyst", "senior_reviewer", "finance"}:
        input_assessment = payload.get("input_assessment")
        if isinstance(input_assessment, str):
            if input_assessment not in {"sufficient", "partial", "insufficient"}:
                issues.append(f"{role}:invalid_input_assessment")
        elif isinstance(input_assessment, dict):
            quality = input_assessment.get("quality")
            prior_agent = input_assessment.get("prior_agent")
            score = input_assessment.get("score")
            assessment_issues = input_assessment.get("issues")

            if quality not in {"sufficient", "partial", "insufficient"}:
                issues.append(f"{role}:invalid_input_assessment_quality")
            if not isinstance(prior_agent, str) or not prior_agent:
                issues.append(f"{role}:missing_input_assessment_prior_agent")
            if score in (None, ""):
                issues.append(f"{role}:missing_input_assessment_score")
            if not isinstance(assessment_issues, list):
                issues.append(f"{role}:invalid_input_assessment_issues")
        else:
            issues.append(f"{role}:invalid_input_assessment")

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

    if role == "claims_manager":
        handoff_chain = payload.get("handoff_chain", {})
        if not isinstance(handoff_chain, dict) or handoff_chain.get("quality") not in {
            "sufficient",
            "partial",
            "insufficient",
        }:
            issues.append("claims_manager:invalid_handoff_chain_quality")

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
