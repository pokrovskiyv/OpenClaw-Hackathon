#!/usr/bin/env python3
"""
Prompt Improver — Analyzes evaluation results and rewrites agent prompts.
The "coach" that reads the game tape and adjusts the playbook.
"""
import json
import os
from datetime import datetime, timezone

from lib.config import IMPROVER_MODEL, AGENT_ORDER, AGENTS_DIR
from lib.llm import call_llm


IMPROVER_SYSTEM_PROMPT = """You are an expert prompt engineer specializing in insurance claims processing AI agents.

Your job is to analyze evaluation results and rewrite agent system prompts to fix identified weaknesses.

## Rules
1. PRESERVE all existing business rules and output format requirements
2. ADD specificity where the agent was too vague
3. ADD examples where the agent made wrong decisions
4. STRENGTHEN instructions for areas with low scores
5. DO NOT remove any existing rules unless they caused errors
6. DO NOT change the JSON output format structure
7. ADD "Common Mistakes to Avoid" section if critical errors were found
8. Keep the prompt focused — don't add irrelevant instructions
9. If the agent scored > 85 on all dimensions, make minimal changes only
10. RETURN the complete rewritten prompt — not a diff, not instructions, the FULL prompt

## Approach
- Read the evaluation carefully
- Identify the root cause of each error (not just the symptom)
- Write targeted additions to the prompt that address root causes
- Add concrete examples for ambiguous situations
- Strengthen scoring criteria if agent was too lenient/strict
"""


def analyze_agent_performance(agent_name: str, eval_results: list) -> dict:
    """Aggregate evaluation data for a specific agent across all scenarios."""
    performance = {
        "agent_name": agent_name,
        "scenario_count": len(eval_results),
        "avg_combined_score": 0,
        "dimension_scores": {},
        "all_weaknesses": [],
        "all_critical_errors": [],
        "all_strengths": [],
        "failing_scenarios": [],
        "rule_failures": [],
    }

    combined_scores = []
    dim_scores = {}

    for ev in eval_results:
        agent_eval = ev.get("agents", {}).get(agent_name, {})
        if not agent_eval:
            continue

        combined_scores.append(agent_eval.get("combined_score", 0))

        # Collect LLM eval dimensions
        llm_eval = agent_eval.get("llm_eval", {})
        for dim in ["correctness", "completeness", "business_logic", "format_compliance", "reasoning_quality"]:
            score = llm_eval.get(dim, 0)
            dim_scores.setdefault(dim, []).append(score)

        # Collect feedback
        for w in llm_eval.get("weaknesses", []):
            performance["all_weaknesses"].append({"scenario": ev["scenario_id"], "weakness": w})
        for e in llm_eval.get("critical_errors", []):
            performance["all_critical_errors"].append({"scenario": ev["scenario_id"], "error": e})
        for s in llm_eval.get("strengths", []):
            performance["all_strengths"].append({"scenario": ev["scenario_id"], "strength": s})

        # Collect rule-based failures
        rule_based = agent_eval.get("rule_based", {})
        for check in rule_based.get("checks", []):
            if check["score"] < 0.5:
                performance["rule_failures"].append(
                    {"scenario": ev["scenario_id"], "field": check.get("field"), "detail": check["detail"]}
                )

        if agent_eval.get("combined_score", 0) < 70:
            performance["failing_scenarios"].append(ev["scenario_id"])

    performance["avg_combined_score"] = round(sum(combined_scores) / len(combined_scores), 1) if combined_scores else 0
    for dim, scores in dim_scores.items():
        performance["dimension_scores"][dim] = round(sum(scores) / len(scores), 1)

    return performance


def improve_agent_prompt(agent_name: str, current_prompt: str, performance: dict) -> str:
    """Use LLM to rewrite an agent's prompt based on evaluation feedback."""

    user_msg = f"""## Agent: {agent_name.replace('_', ' ').title()}

## Current Performance
- Average Score: {performance['avg_combined_score']}/100
- Dimension Scores: {json.dumps(performance['dimension_scores'], indent=2)}
- Failing Scenarios: {performance['failing_scenarios']}

## Critical Errors Found
{json.dumps(performance['all_critical_errors'], indent=2)}

## Weaknesses Identified
{json.dumps(performance['all_weaknesses'], indent=2)}

## Rule-Based Failures (specific field mismatches)
{json.dumps(performance['rule_failures'], indent=2)}

## Strengths (keep these)
{json.dumps(performance['all_strengths'][:5], indent=2)}

## Current Prompt
```markdown
{current_prompt}
```

## Task
Rewrite the complete agent prompt to fix the identified issues. Return ONLY the full markdown prompt text, nothing else. Do not wrap in code blocks."""

    improved = call_llm(IMPROVER_SYSTEM_PROMPT, user_msg, IMPROVER_MODEL, max_tokens=6000)

    # Clean up markdown code block wrapping if present
    if improved.strip().startswith("```"):
        lines = improved.strip().split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        improved = "\n".join(lines)

    return improved.strip()


def run_improvement_cycle(eval_results: list, dry_run: bool = False, iteration: int = 0) -> dict:
    """Analyze all agents and improve the weakest ones."""
    improvement_log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents_analyzed": {},
        "agents_improved": [],
        "agents_skipped": [],
    }

    for agent_name in AGENT_ORDER:
        print(f"\n  Analyzing {agent_name}...", end=" ", flush=True)
        performance = analyze_agent_performance(agent_name, eval_results)
        improvement_log["agents_analyzed"][agent_name] = {
            "avg_score": performance["avg_combined_score"],
            "dimensions": performance["dimension_scores"],
            "critical_errors": len(performance["all_critical_errors"]),
            "rule_failures": len(performance["rule_failures"]),
        }

        # Decide whether to improve
        if performance["avg_combined_score"] >= 90 and not performance["all_critical_errors"]:
            print(f"Score {performance['avg_combined_score']} ✓ (skipping)")
            improvement_log["agents_skipped"].append(agent_name)
            continue

        print(f"Score {performance['avg_combined_score']} → Improving...", flush=True)

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
            "prev_score": performance["avg_combined_score"],
            "issues_fixed": len(performance["all_critical_errors"]) + len(performance["rule_failures"]),
        })

    return improvement_log
