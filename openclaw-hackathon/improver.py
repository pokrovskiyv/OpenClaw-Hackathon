#!/usr/bin/env python3
"""
Prompt Improver — Analyzes Claims Manager evaluation results and rewrites agent prompts.
The "coach" that reads the manager's feedback and adjusts the playbook.
"""
import json
import os
from datetime import datetime, timezone

from lib.config import IMPROVER_MODEL, AGENT_ORDER, AGENTS_DIR
from lib.llm import call_llm


IMPROVER_SYSTEM_PROMPT = """You are an expert prompt engineer specializing in insurance claims processing AI agents.

Your job is to analyze Claims Manager evaluation results and rewrite agent system prompts to fix identified weaknesses.

## Rules
1. PRESERVE all existing business rules and output format requirements
2. ADD specificity where the agent was too vague
3. ADD examples where the agent made wrong decisions
4. STRENGTHEN instructions for areas with low scores
5. DO NOT remove any existing rules unless they caused errors
6. DO NOT change the JSON output format structure
7. ADD "Common Mistakes to Avoid" section if critical issues were found
8. Keep the prompt focused — don't add irrelevant instructions
9. If the agent scored > 85 on all dimensions, make minimal changes only
10. RETURN the complete rewritten prompt — not a diff, not instructions, the FULL prompt

## Approach
- Read the manager's improvement note carefully — it is the primary signal
- Identify the root cause of each error (not just the symptom)
- Write targeted additions to the prompt that address root causes
- Add concrete examples for ambiguous situations
- Strengthen scoring criteria if agent was too lenient/strict
"""


def analyze_agent_performance(agent_name: str, eval_results: list) -> dict:
    """Aggregate manager evaluation data for a specific agent across all scenarios."""
    performance = {
        "agent_name": agent_name,
        "scenario_count": len(eval_results),
        "avg_score": 0,
        "all_issues": [],
        "all_strengths": [],
        "failing_scenarios": [],
        "improvement_notes": [],
    }

    scores = []

    for ev in eval_results:
        agent_data = ev.get("agents", {}).get(agent_name, {})
        if not agent_data:
            continue

        score = agent_data.get("score", 0)
        scores.append(score)

        for issue in agent_data.get("issues", []):
            performance["all_issues"].append({"scenario": ev["scenario_id"], "issue": issue})
        for strength in agent_data.get("strengths", []):
            performance["all_strengths"].append({"scenario": ev["scenario_id"], "strength": strength})

        # Collect manager's improvement note for this agent
        note = ev.get("improvement_notes", {}).get(agent_name)
        if note:
            performance["improvement_notes"].append({"scenario": ev["scenario_id"], "note": note})

        if score < 70:
            performance["failing_scenarios"].append(ev["scenario_id"])

    performance["avg_score"] = round(sum(scores) / len(scores), 1) if scores else 0
    return performance


def improve_agent_prompt(agent_name: str, current_prompt: str, performance: dict) -> str:
    """Use LLM to rewrite an agent's prompt based on Claims Manager feedback."""

    # Prioritize manager's specific improvement notes
    primary_feedback = "\n".join(
        f"[{n['scenario']}] {n['note']}" for n in performance["improvement_notes"]
    ) or "No specific improvement note — use issues list below."

    user_msg = f"""## Agent: {agent_name.replace('_', ' ').title()}

## Performance Summary
- Average Score: {performance['avg_score']}/100
- Failing Scenarios: {performance['failing_scenarios']}

## Claims Manager Improvement Instructions (PRIMARY SIGNAL)
{primary_feedback}

## Specific Issues Found
{json.dumps(performance['all_issues'][:10], indent=2)}

## Strengths (keep these)
{json.dumps(performance['all_strengths'][:5], indent=2)}

## Current Prompt
```markdown
{current_prompt}
```

## Task
Rewrite the complete agent prompt to fix the identified issues. Focus primarily on the Claims Manager's improvement instructions above. Return ONLY the full markdown prompt text, nothing else. Do not wrap in code blocks."""

    improved = call_llm(IMPROVER_SYSTEM_PROMPT, user_msg, IMPROVER_MODEL, max_tokens=6000)

    # Strip markdown code block wrapping if present
    if improved.strip().startswith("```"):
        lines = improved.strip().split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        improved = "\n".join(lines)

    return improved.strip()


def run_improvement_cycle(eval_results: list, dry_run: bool = False, iteration: int = 0) -> dict:
    """Analyze all agents and improve the weakest ones based on manager feedback."""
    improvement_log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents_analyzed": {},
        "agents_improved": [],
        "agents_skipped": [],
    }

    # Find the global weakest agent across all evals
    weakest_counts: dict = {}
    for ev in eval_results:
        w = ev.get("weakest_agent")
        if w:
            weakest_counts[w] = weakest_counts.get(w, 0) + 1
    global_weakest = max(weakest_counts, key=weakest_counts.get) if weakest_counts else None

    for agent_name in AGENT_ORDER:
        print(f"\n  Analyzing {agent_name}...", end=" ", flush=True)
        performance = analyze_agent_performance(agent_name, eval_results)
        improvement_log["agents_analyzed"][agent_name] = {
            "avg_score": performance["avg_score"],
            "issue_count": len(performance["all_issues"]),
            "improvement_note_count": len(performance["improvement_notes"]),
        }

        # Skip agents that are performing well and have no manager improvement notes
        if performance["avg_score"] >= 90 and not performance["improvement_notes"]:
            print(f"Score {performance['avg_score']} ✓ (skipping)")
            improvement_log["agents_skipped"].append(agent_name)
            continue

        # Skip agents with no issues if score is high enough
        if performance["avg_score"] >= 85 and not performance["improvement_notes"] and not performance["all_issues"]:
            print(f"Score {performance['avg_score']} ✓ (skipping)")
            improvement_log["agents_skipped"].append(agent_name)
            continue

        print(f"Score {performance['avg_score']} → Improving...", flush=True)
        if global_weakest == agent_name:
            print(f"    ★ Flagged as weakest agent across scenarios")

        # Load current prompt
        prompt_path = os.path.join(AGENTS_DIR, f"{agent_name}.md")
        with open(prompt_path, "r") as f:
            current_prompt = f.read()

        # Generate improved prompt
        improved_prompt = improve_agent_prompt(agent_name, current_prompt, performance)

        if dry_run:
            print(f"    [DRY RUN] Would update {agent_name}.md ({len(improved_prompt)} chars)")
        else:
            # Backup current prompt grouped by iteration
            backup_dir = os.path.join(AGENTS_DIR, "backups", f"iter_{iteration:03d}")
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"{agent_name}.md")
            with open(backup_path, "w") as f:
                f.write(current_prompt)

            # Write improved prompt
            with open(prompt_path, "w") as f:
                f.write(improved_prompt)

            print(f"    ✓ Updated {agent_name}.md (backup: {backup_path})")

        improvement_log["agents_improved"].append({
            "agent": agent_name,
            "prev_score": performance["avg_score"],
            "issues_addressed": len(performance["all_issues"]),
            "manager_notes_used": len(performance["improvement_notes"]),
        })

    return improvement_log
