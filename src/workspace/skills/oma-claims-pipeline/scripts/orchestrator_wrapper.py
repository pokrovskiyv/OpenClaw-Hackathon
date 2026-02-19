#!/usr/bin/env python3
import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

PIPELINE_ORDER = [
    "front_desk",
    "claims_officer",
    "assessor",
    "fraud_analyst",
    "senior_reviewer",
    "finance",
]


def run_validator(script_path: Path, role: str, input_path: Path) -> tuple[int, dict]:
    command = [
        sys.executable,
        str(script_path),
        "--role",
        role,
        "--input",
        str(input_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    payload: dict
    stdout = completed.stdout.strip()
    if not stdout:
        payload = {
            "status": "hard_fail",
            "role": role,
            "input": str(input_path),
            "missing_fields": [],
            "inconsistencies": ["validator_empty_output"],
            "action": "escalate",
        }
    else:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            payload = {
                "status": "hard_fail",
                "role": role,
                "input": str(input_path),
                "missing_fields": [],
                "inconsistencies": ["validator_non_json_output"],
                "action": "escalate",
            }

    return completed.returncode, payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sequential orchestrator gate: validate each role output before next role invocation"
    )
    parser.add_argument("--artifacts-dir", required=True, help="Directory containing <role>.json artifacts")
    parser.add_argument("--claim-id", default="", help="Optional claim id for report")
    parser.add_argument(
        "--validator-script",
        default=str(Path(__file__).resolve().parent / "handoff_validate.py"),
        help="Path to handoff validator script",
    )
    parser.add_argument(
        "--invoke-next-cmd",
        default="",
        help=(
            "Optional command template to auto-invoke next agent when ready. "
            "Placeholders: {next_agent}, {claim_id}, {artifacts_dir}"
        ),
    )
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir).expanduser().resolve()
    validator_script = Path(args.validator_script).expanduser().resolve()

    if not artifacts_dir.exists() or not artifacts_dir.is_dir():
        raise NotADirectoryError(f"Artifacts dir not found: {artifacts_dir}")
    if not validator_script.exists():
        raise FileNotFoundError(f"Validator script not found: {validator_script}")

    checks: list[dict] = []

    for index, role in enumerate(PIPELINE_ORDER):
        artifact = artifacts_dir / f"{role}.json"
        if not artifact.exists():
            next_role = role
            result = {
                "status": "ready_for_next_agent",
                "claim_id": args.claim_id,
                "next_agent": next_role,
                "can_invoke_next": True,
                "reason": f"artifact_missing_for_next_stage:{artifact.name}",
                "checks": checks,
            }

            if args.invoke_next_cmd:
                rendered = args.invoke_next_cmd.format(
                    next_agent=next_role,
                    claim_id=args.claim_id,
                    artifacts_dir=str(artifacts_dir),
                )
                invoke_completed = subprocess.run(
                    shlex.split(rendered),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                result["invocation"] = {
                    "command": rendered,
                    "exit_code": invoke_completed.returncode,
                    "stdout": invoke_completed.stdout.strip(),
                    "stderr": invoke_completed.stderr.strip(),
                }
                result["status"] = "invoked_next_agent" if invoke_completed.returncode == 0 else "invoke_failed"
                result["can_invoke_next"] = invoke_completed.returncode != 0

            print(json.dumps(result, indent=2))
            raise SystemExit(0 if result["status"] in {"ready_for_next_agent", "invoked_next_agent"} else 1)

        return_code, validation = run_validator(validator_script, role, artifact)
        checks.append(
            {
                "role": role,
                "artifact": str(artifact),
                "validator_exit_code": return_code,
                "validation": validation,
            }
        )

        status = validation.get("status")
        if status == "soft_fail":
            result = {
                "status": "blocked",
                "claim_id": args.claim_id,
                "blocked_at": role,
                "next_agent": None,
                "can_invoke_next": False,
                "action": "request_fix",
                "checks": checks,
            }
            print(json.dumps(result, indent=2))
            raise SystemExit(1)

        if status == "hard_fail":
            result = {
                "status": "blocked",
                "claim_id": args.claim_id,
                "blocked_at": role,
                "next_agent": None,
                "can_invoke_next": False,
                "action": "escalate",
                "checks": checks,
            }
            print(json.dumps(result, indent=2))
            raise SystemExit(2)

        if status != "pass":
            result = {
                "status": "blocked",
                "claim_id": args.claim_id,
                "blocked_at": role,
                "next_agent": None,
                "can_invoke_next": False,
                "action": "escalate",
                "checks": checks,
                "reason": f"unknown_validation_status:{status}",
            }
            print(json.dumps(result, indent=2))
            raise SystemExit(2)

        is_last = index == len(PIPELINE_ORDER) - 1
        if is_last:
            result = {
                "status": "completed",
                "claim_id": args.claim_id,
                "next_agent": None,
                "can_invoke_next": False,
                "checks": checks,
            }
            print(json.dumps(result, indent=2))
            return

    print(json.dumps({"status": "completed", "claim_id": args.claim_id, "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
