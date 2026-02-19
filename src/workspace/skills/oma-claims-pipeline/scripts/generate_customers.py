#!/usr/bin/env python3
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def build_telegram_id(policy_number: str) -> str:
    suffix = "".join(ch for ch in policy_number.split("-")[-1] if ch.isdigit())
    return str(100000 + int(suffix[-5:]))


def build_pin_hash(policy_number: str) -> str:
    suffix = "".join(ch for ch in policy_number.split("-")[-1] if ch.isdigit())
    pin = suffix[-4:]
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 10:
        return "+1" + digits
    if digits.startswith("1") and len(digits) == 11:
        return "+" + digits
    if phone.startswith("+"):
        return phone
    return "+" + digits


def parse_address(raw: str) -> dict:
    parts = [part.strip() for part in raw.split(",")]
    street = parts[0] if len(parts) > 0 else ""
    city = parts[1] if len(parts) > 1 else ""
    state = ""
    zip_code = ""
    if len(parts) > 2:
        state_zip = parts[2].split()
        if len(state_zip) >= 1:
            state = state_zip[0]
        if len(state_zip) >= 2:
            zip_code = state_zip[1]
    return {
        "street": street.upper(),
        "city": city.upper(),
        "state": state.upper(),
        "zip": zip_code,
    }


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import policies from external source and generate tg_{telegram_id} customer folders")
    parser.add_argument(
        "--policies-dir",
        required=True,
        help="External directory with source policy JSON files",
    )
    parser.add_argument(
        "--customers-dir",
        default=str(Path(__file__).resolve().parents[3] / "customers"),
    )
    args = parser.parse_args()

    policies_dir = Path(args.policies_dir)
    customers_dir = Path(args.customers_dir)
    customers_dir.mkdir(parents=True, exist_ok=True)

    policy_files = sorted(policies_dir.glob("*.json"))
    if not policy_files:
        raise FileNotFoundError(f"No policy files found in {policies_dir}")

    generated_clients = []
    generated_policies = []
    phone_index: dict[str, str] = {}

    for policy_file in policy_files:
        with policy_file.open("r", encoding="utf-8") as file:
            src_policy = json.load(file)

        policy_id = src_policy["policy_number"]
        holder = src_policy.get("holder", {})
        vehicle = src_policy.get("vehicle", {})

        telegram_id = build_telegram_id(policy_id)
        customer_key = f"tg_{telegram_id}"
        customer_dir = customers_dir / customer_key
        policies_subdir = customer_dir / "policies"
        claims_subdir = customer_dir / "claims"
        policies_subdir.mkdir(parents=True, exist_ok=True)
        claims_subdir.mkdir(parents=True, exist_ok=True)

        normalized_phone = normalize_phone(holder.get("phone", ""))
        now = iso_now()

        policy_payload = {
            "policy_id": policy_id,
            "status": str(src_policy.get("status", "UNKNOWN")).upper(),
            "effective_date": src_policy.get("effective_date"),
            "expiration_date": src_policy.get("expiry_date"),
            "premium_paid": bool(src_policy.get("premium_paid", False)),
            "coverage": src_policy.get("coverage", {}),
            "exclusions": src_policy.get("exclusions", []),
            "object_insured": {
                "vehicle": {
                    "vin": vehicle.get("vin"),
                    "make": str(vehicle.get("make", "")).upper(),
                    "model": vehicle.get("model"),
                    "year": vehicle.get("year"),
                    "license_plate": None,
                }
            },
            "created_at": now,
            "updated_at": now,
        }

        client_payload = {
            "customer_id": customer_key,
            "channel": "telegram",
            "telegram_id": telegram_id,
            "phone": normalized_phone,
            "name": holder.get("name"),
            "email": holder.get("email"),
            "address": parse_address(holder.get("address", "")),
            "driver_license": {
                "number": None,
                "state": "OH",
                "expiration_date": None,
            },
            "policies": {
                "current_policy_id": policy_id,
                "all_policy_ids": [policy_id],
            },
            "auth": {
                "pin_sha256": build_pin_hash(policy_id),
                "pin_rule_note": "demo_pin_is_last4_of_policy_suffix",
            },
            "created_at": now,
            "updated_at": now,
        }

        client_path = customer_dir / "client.json"
        with client_path.open("w", encoding="utf-8") as file:
            json.dump(client_payload, file, indent=2)
        generated_clients.append(str(client_path))

        policy_path = policies_subdir / f"policy_{policy_id}.json"
        with policy_path.open("w", encoding="utf-8") as file:
            json.dump(policy_payload, file, indent=2)
        generated_policies.append(str(policy_path))

        phone_index[normalized_phone] = customer_key

    index_path = customers_dir / "index.json"
    with index_path.open("w", encoding="utf-8") as file:
        json.dump(phone_index, file, indent=2)

    print(
        json.dumps(
            {
                "customers_generated": len(generated_clients),
                "client_files": generated_clients,
                "policy_files": generated_policies,
                "index": str(index_path),
                "index_entries": len(phone_index),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
