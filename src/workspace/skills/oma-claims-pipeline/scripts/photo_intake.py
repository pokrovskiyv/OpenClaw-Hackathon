#!/usr/bin/env python3
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def safe_part_name(part: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in part.lower())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def manifest_path_value(path: Path, workspace: Path) -> str:
    resolved = path.expanduser().resolve()
    try:
        return resolved.relative_to(workspace).as_posix()
    except ValueError:
        return resolved.name


def main() -> None:
    parser = argparse.ArgumentParser(description="Store claim photos in workspace-local claim storage")
    parser.add_argument("--claim-id", required=True, help="Claim ID, e.g. CLM-2026-0001")
    parser.add_argument("--telegram-id", required=True, help="Customer telegram_id")
    parser.add_argument("--source", required=True, help="Path to incoming photo file")
    parser.add_argument("--part", required=True, help="Vehicle part captured (front_bumper, right_fender, etc)")
    parser.add_argument("--note", default="", help="Optional note about this photo")
    parser.add_argument(
        "--workspace",
        default=str(Path(__file__).resolve().parents[3]),
        help="OpenClaw workspace root (default auto-detected)",
    )
    args = parser.parse_args()

    source_path = Path(args.source).expanduser().resolve()
    if not source_path.exists() or not source_path.is_file():
        raise FileNotFoundError(f"Source photo not found: {source_path}")

    workspace = Path(args.workspace).expanduser().resolve()
    customer_key = f"tg_{args.telegram_id}"
    customer_dir = workspace / "customers" / customer_key
    customer_file = customer_dir / "client.json"
    if not customer_file.exists():
        raise FileNotFoundError(f"Customer file not found: {customer_file}")

    claim_root = customer_dir / "claims" / args.claim_id
    claim_json_path = claim_root / "claim.json"
    if not claim_json_path.exists():
        raise FileNotFoundError(f"Claim file not found: {claim_json_path}")

    claims_dir = claim_root / "photos"
    claims_dir.mkdir(parents=True, exist_ok=True)

    ext = source_path.suffix.lower()
    if not ext:
        raise ValueError(f"Source photo has no file extension: {source_path}")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{timestamp}_{safe_part_name(args.part)}{ext}"
    target_path = claims_dir / filename
    shutil.copy2(source_path, target_path)

    manifest_path = claims_dir / "manifest.json"
    if manifest_path.exists():
        with manifest_path.open("r", encoding="utf-8") as file:
            manifest = json.load(file)
    else:
        manifest = {"claim_id": args.claim_id, "created_at": utc_now(), "photos": []}

    entry = {
        "stored_at": utc_now(),
        "telegram_id": str(args.telegram_id),
        "part": args.part,
        "file": manifest_path_value(target_path, workspace),
        "source": manifest_path_value(source_path, workspace),
        "note": args.note,
        "customer_file": manifest_path_value(customer_file, workspace),
    }
    manifest["photos"].append(entry)
    manifest["updated_at"] = utc_now()

    with manifest_path.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2)

    with claim_json_path.open("r", encoding="utf-8") as file:
        claim_doc = json.load(file)
    claim_doc["photo_count"] = len(manifest["photos"])
    current_status = claim_doc.get("status", "intake")
    if current_status in {"intake", "preauth_verified"}:
        claim_doc["status"] = "docs_collecting"
        history = claim_doc.get("status_history", [])
        history.append(
            {
                "from": current_status,
                "to": "docs_collecting",
                "at": utc_now(),
                "reason": "photo_uploaded",
                "actor": "photo_intake",
            }
        )
        claim_doc["status_history"] = history
    claim_doc["updated_at"] = utc_now()
    with claim_json_path.open("w", encoding="utf-8") as file:
        json.dump(claim_doc, file, indent=2)

    print(
        json.dumps(
            {
                "ok": True,
                "claim_id": args.claim_id,
                "telegram_id": str(args.telegram_id),
                "stored_file": str(target_path),
                "manifest": str(manifest_path),
                "claim_json": str(claim_json_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
