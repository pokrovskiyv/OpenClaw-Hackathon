#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path


def normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 10:
        return "+1" + digits
    if digits.startswith("1") and len(digits) == 11:
        return "+" + digits
    if phone.startswith("+"):
        return phone
    return "+" + digits


def load_client(customer_dir: Path) -> dict:
    client_path = customer_dir / "client.json"
    if not client_path.exists():
        raise FileNotFoundError(f"Client file not found: {client_path}")
    with client_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_policy(customer_dir: Path, policy_id: str) -> dict:
    policy_path = customer_dir / "policies" / f"policy_{policy_id}.json"
    if not policy_path.exists():
        raise FileNotFoundError(f"Policy file not found: {policy_path}")
    with policy_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_phone_index(customers_dir: Path) -> dict[str, str]:
    index_path = customers_dir / "index.json"
    if not index_path.exists():
        raise FileNotFoundError(f"Phone index not found: {index_path}")
    with index_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)
    if not isinstance(raw, dict):
        raise ValueError("customers/index.json must be an object mapping phone -> customer_key")
    return raw


def find_customer_key(
    customers_dir: Path,
    policy: str,
    phone: str,
    telegram_id: str | None,
    phone_index: dict[str, str],
) -> str | None:
    if telegram_id:
        customer_key = f"tg_{telegram_id}"
        if (customers_dir / customer_key / "client.json").exists():
            return customer_key
        return None

    phone_in = normalize_phone(phone)
    customer_key = phone_index.get(phone_in)
    if not customer_key:
        return None

    client = load_client(customers_dir / customer_key)
    if policy not in client.get("policies", {}).get("all_policy_ids", []):
        return None
    return customer_key


def verify_pin(policy_number: str, pin: str) -> tuple[bool, str]:
    expected_pin = "".join(ch for ch in policy_number.split("-")[-1] if ch.isdigit())[-4:]
    expected_hash = hashlib.sha256(expected_pin.encode("utf-8")).hexdigest()
    provided_hash = hashlib.sha256(pin.encode("utf-8")).hexdigest()
    return provided_hash == expected_hash, "demo_pin_rule:last4_of_policy_suffix"


def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-auth check for registered policy holder")
    parser.add_argument("--policy", required=True, help="Policy number, e.g. OMA-2025-19450")
    parser.add_argument("--phone", required=True, help="Caller phone, any format")
    parser.add_argument("--pin", required=True, help="PIN entered by caller")
    parser.add_argument("--telegram-id", help="Telegram ID (optional strong identifier)")
    parser.add_argument(
        "--customers-dir",
        default=str(Path(__file__).resolve().parents[3] / "customers"),
        help="Directory with customer_{telegram_id}.json files",
    )
    args = parser.parse_args()

    customers_dir = Path(args.customers_dir)
    reasons = []

    try:
        phone_index = load_phone_index(customers_dir)
        customer_key = find_customer_key(customers_dir, args.policy, args.phone, args.telegram_id, phone_index)
        if customer_key is None:
            print(
                json.dumps(
                    {
                        "verified": False,
                        "stage": "customer_lookup",
                        "error": "customer_not_found",
                    }
                )
            )
            raise SystemExit(2)

        customer_dir = customers_dir / customer_key
        client = load_client(customer_dir)
        policy_doc = load_policy(customer_dir, args.policy)
    except Exception as error:
        print(json.dumps({"verified": False, "stage": "customer_lookup", "error": str(error)}))
        raise SystemExit(2)

    phone_in = normalize_phone(args.phone)
    holder_phone = normalize_phone(client.get("phone", ""))
    phone_match = phone_in == holder_phone

    status = str(policy_doc.get("status", "")).upper() == "ACTIVE"
    premium_paid = bool(policy_doc.get("premium_paid", False))
    pin_ok, pin_rule = verify_pin(args.policy, args.pin)

    if not phone_match:
        reasons.append("phone_mismatch")
    if not status:
        reasons.append("policy_not_active")
    if not premium_paid:
        reasons.append("premium_not_paid")
    if not pin_ok:
        reasons.append("pin_invalid")

    verified = len(reasons) == 0

    print(
        json.dumps(
            {
                "verified": verified,
                "policy_number": args.policy,
                "customer_name": client.get("name"),
                "telegram_id": client.get("telegram_id"),
                "customer_key": customer_key,
                "checks": {
                    "phone_match": phone_match,
                    "policy_active": status,
                    "premium_paid": premium_paid,
                    "pin_ok": pin_ok,
                    "pin_rule": pin_rule,
                },
                "reasons": reasons,
            }
        )
    )

    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
