#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def resolve_home(path: str) -> Path:
    return Path(path).expanduser().resolve()


def check_file(path: Path, label: str, problems: list[str]) -> None:
    if not path.exists():
        problems.append(f"missing:{label}:{path}")


def normalize_workspace(raw: str | None) -> str:
    if not raw:
        return ""
    return str(Path(raw).expanduser().resolve())


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate OpenClaw path layout for this skill")
    parser.add_argument("--openclaw-home", default="~/.openclaw", help="Target OpenClaw home path")
    parser.add_argument("--skill-name", default="oma-claims-pipeline", help="Skill folder name")
    args = parser.parse_args()

    base = resolve_home(args.openclaw_home)
    openclaw_json = base / "openclaw.json"
    workspace = base / "workspace"
    skill_dir = workspace / "skills" / args.skill_name
    customers_dir = workspace / "customers"

    problems: list[str] = []
    check_file(openclaw_json, "openclaw.json", problems)
    check_file(workspace, "workspace", problems)
    check_file(skill_dir, "skill_dir", problems)
    check_file(skill_dir / "SKILL.md", "skill_md", problems)
    check_file(customers_dir, "customers_dir", problems)
    if customers_dir.exists():
        customer_folders = sorted([path for path in customers_dir.glob("tg_*") if path.is_dir()])
        if not customer_folders:
            problems.append(f"missing:customer_folders:{customers_dir}/tg_*")
        else:
            for folder in customer_folders:
                if not (folder / "client.json").exists():
                    problems.append(f"missing:client_json:{folder}/client.json")
                if not (folder / "policies").exists():
                    problems.append(f"missing:policies_dir:{folder}/policies")
                if not (folder / "claims").exists():
                    problems.append(f"missing:claims_dir:{folder}/claims")
        if not (customers_dir / "index.json").exists():
            problems.append(f"missing:customers_index:{customers_dir}/index.json")

    agents_summary = []
    if openclaw_json.exists():
        try:
            with openclaw_json.open("r", encoding="utf-8") as file:
                config = json.load(file)
            for agent in config.get("agents", {}).get("list", []):
                workspace_raw = agent.get("workspace")
                workspace_norm = normalize_workspace(workspace_raw)
                agents_summary.append(
                    {
                        "id": agent.get("id"),
                        "workspace": workspace_raw,
                        "workspace_resolved": workspace_norm,
                    }
                )
                if workspace_norm and workspace_norm != str(workspace.resolve()):
                    problems.append(
                        "workspace_mismatch:"
                        + str(agent.get("id"))
                        + ":"
                        + workspace_norm
                        + "!="
                        + str(workspace.resolve())
                    )
        except Exception as error:
            problems.append(f"invalid_openclaw_json:{error}")

    result = {
        "ok": len(problems) == 0,
        "openclaw_home": str(base),
        "expected": {
            "openclaw_json": str(openclaw_json),
            "workspace": str(workspace),
            "skill_dir": str(skill_dir),
            "customers_dir": str(customers_dir),
            "customers_index": str(customers_dir / "index.json"),
        },
        "agents": agents_summary,
        "problems": problems,
        "fix_hint": [
            "copy src/openclaw.json -> ~/.openclaw/openclaw.json",
            "copy src/workspace/skills/oma-claims-pipeline -> ~/.openclaw/workspace/skills/",
            "copy src/workspace/customers -> ~/.openclaw/workspace/customers",
            "start a new OpenClaw session",
        ],
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
