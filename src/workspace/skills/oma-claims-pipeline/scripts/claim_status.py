#!/usr/bin/env python3
import argparse
import fcntl
import json
from datetime import datetime, timezone
from pathlib import Path


TRANSITIONS: dict[str, set[str]] = {
    "intake": {"preauth_verified", "cancelled"},
    "preauth_verified": {"docs_collecting", "cancelled"},
    "docs_collecting": {"coverage_review", "cancelled"},
    "coverage_review": {"assessment", "denied", "investigation"},
    "assessment": {"fraud_review", "investigation"},
    "fraud_review": {"senior_review", "investigation"},
    "senior_review": {"finance_processing", "denied", "investigation"},
    "finance_processing": {"payout_scheduled", "payout_completed"},
    "payout_scheduled": {"payout_completed"},
    "investigation": {"senior_review", "denied", "cancelled"},
    "denied": set(),
    "payout_completed": set(),
    "cancelled": set(),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="Claim status state-machine transition tool")
    parser.add_argument("--telegram-id", required=True)
    parser.add_argument("--claim-id", required=True)
    parser.add_argument("--to", required=True, help="Target status")
    parser.add_argument("--reason", default="")
    parser.add_argument("--actor", default="system")
    parser.add_argument(
        "--workspace",
        default=str(Path(__file__).resolve().parents[3]),
        help="OpenClaw workspace root",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    claim_path = workspace / "customers" / f"tg_{args.telegram_id}" / "claims" / args.claim_id / "claim.json"
    if not claim_path.exists():
        raise FileNotFoundError(f"Claim file not found: {claim_path}")

    with claim_path.open("r+", encoding="utf-8") as file:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX)
        claim = json.load(file)

        if "status" not in claim:
            raise KeyError(f"Missing required field 'status' in claim: {claim_path}")

        current = claim["status"]
        target = args.to

        if target not in TRANSITIONS:
            raise ValueError(f"Unknown target status: {target}")

        allowed = TRANSITIONS.get(current, set())
        if target not in allowed:
            raise ValueError(f"Invalid transition: {current} -> {target}. Allowed: {sorted(allowed)}")

        history = claim.get("status_history", [])
        history.append(
            {
                "from": current,
                "to": target,
                "at": now_iso(),
                "reason": args.reason,
                "actor": args.actor,
            }
        )

        claim["status"] = target
        claim["status_history"] = history
        claim["updated_at"] = now_iso()

        file.seek(0)
        file.truncate()
        json.dump(claim, file, indent=2)
        file.flush()
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)

    print(
        json.dumps(
            {
                "ok": True,
                "claim_id": args.claim_id,
                "from": current,
                "to": target,
                "claim_json": str(claim_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
