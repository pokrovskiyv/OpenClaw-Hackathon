#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize claim folder with claim.json")
    parser.add_argument("--telegram-id", required=True)
    parser.add_argument("--claim-id", required=True)
    parser.add_argument("--policy-id", required=True)
    parser.add_argument("--incident-type", required=True)
    parser.add_argument("--summary", default="")
    parser.add_argument(
        "--workspace",
        default=str(Path(__file__).resolve().parents[3]),
        help="OpenClaw workspace root",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    customer_dir = workspace / "customers" / f"tg_{args.telegram_id}"
    client_path = customer_dir / "client.json"
    if not client_path.exists():
        raise FileNotFoundError(f"Customer client.json not found: {client_path}")

    claim_dir = customer_dir / "claims" / args.claim_id
    photos_dir = claim_dir / "photos"
    claim_dir.mkdir(parents=True, exist_ok=True)
    photos_dir.mkdir(parents=True, exist_ok=True)

    now = now_iso()
    claim_path = claim_dir / "claim.json"
    if claim_path.exists():
        raise FileExistsError(f"Claim already initialized: {claim_path}")

    claim_payload = {
        "claim_id": args.claim_id,
        "telegram_id": str(args.telegram_id),
        "customer_id": f"tg_{args.telegram_id}",
        "policy_id": args.policy_id,
        "incident_type": args.incident_type,
        "summary": args.summary,
        "status": "intake",
        "status_history": [
            {
                "from": None,
                "to": "intake",
                "at": now,
                "reason": "claim_initialized",
                "actor": "system"
            }
        ],
        "photo_count": 0,
        "created_at": now,
        "updated_at": now,
    }

    with claim_path.open("x", encoding="utf-8") as file:
        json.dump(claim_payload, file, indent=2)

    print(
        json.dumps(
            {
                "ok": True,
                "claim_json": str(claim_path),
                "photos_dir": str(photos_dir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
