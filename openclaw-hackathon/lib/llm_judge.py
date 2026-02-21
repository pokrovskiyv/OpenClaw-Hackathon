"""
LLM-as-judge evaluation for benchmark.
Uses claude-opus-4-6 to score pipeline outputs on 5 quality criteria.
"""
import json

from lib.llm import call_llm_json


JUDGE_MODEL = "claude-opus-4-6"

JUDGE_CRITERIA = [
    "correctness",
    "completeness",
    "business_logic",
    "reasoning_quality",
    "format",
]

JUDGE_SYSTEM_PROMPT = """You are an expert insurance claims auditor evaluating an AI pipeline that processes car insurance claims for Ohio Mutual Auto.

You will receive:
1. The original claim scenario (input + policy data)
2. The expected outcomes
3. The actual pipeline output from 6 agents: front_desk, claims_officer, assessor, fraud_analyst, senior_reviewer, finance

Score the pipeline output on these 5 criteria (1-10 each):

1. **correctness**: Are the factual outputs correct? (coverage decisions, amounts, fraud scores, final verdict)
2. **completeness**: Did each agent produce all required fields? Were any steps skipped that shouldn't have been?
3. **business_logic**: Are business rules followed? (subrogation when other party insured, payment blocked when fraud is high, deductible applied correctly, etc.)
4. **reasoning_quality**: Do the agents show sound reasoning in their analysis? Are justifications logical?
5. **format**: Is the output well-structured JSON with consistent field names and types?

Respond with ONLY a JSON object in this exact format:
{
  "scores": {
    "correctness": <1-10>,
    "completeness": <1-10>,
    "business_logic": <1-10>,
    "reasoning_quality": <1-10>,
    "format": <1-10>
  },
  "overall": <1-10 weighted average>,
  "explanation": "<brief 2-3 sentence summary of strengths and weaknesses>"
}"""


def build_judge_message(scenario, pipeline_state):
    """Build the user message for the LLM judge."""
    parts = [
        "## Scenario",
        f"**ID**: {scenario['id']}",
        f"**Name**: {scenario.get('name', '')}",
        f"**Description**: {scenario.get('description', '')}",
        "",
        "## Claim Input",
        "```json",
        json.dumps(scenario.get("input", {}), indent=2),
        "```",
        "",
        "## Policy Data",
        "```json",
        json.dumps(scenario.get("policy", {}), indent=2),
        "```",
        "",
        "## Expected Outcomes",
        "```json",
        json.dumps(scenario.get("expected", {}), indent=2),
        "```",
        "",
        "## Actual Pipeline Output",
    ]

    agent_order = [
        "front_desk", "claims_officer", "assessor",
        "fraud_analyst", "senior_reviewer", "finance",
    ]
    for agent_name in agent_order:
        output = pipeline_state.get(agent_name, {})
        parts.append(f"\n### {agent_name.replace('_', ' ').title()}")
        parts.append("```json")
        parts.append(json.dumps(output, indent=2))
        parts.append("```")

    return "\n".join(parts)


def judge_scenario(scenario, pipeline_state):
    """Run LLM judge on a single scenario's pipeline output.

    Returns a dict with scores per criterion, overall score, and explanation.
    """
    user_message = build_judge_message(scenario, pipeline_state)

    try:
        result = call_llm_json(JUDGE_SYSTEM_PROMPT, user_message, JUDGE_MODEL, max_tokens=2048)
    except Exception as e:
        return {
            "scores": {c: 0 for c in JUDGE_CRITERIA},
            "overall": 0,
            "explanation": f"Judge API error: {e}",
            "error": str(e),
        }

    if result.get("_parse_error"):
        return {
            "scores": {c: 0 for c in JUDGE_CRITERIA},
            "overall": 0,
            "explanation": "Judge returned unparseable response",
            "error": "parse_error",
            "raw": result.get("_raw", ""),
        }

    scores = result.get("scores", {})
    for criterion in JUDGE_CRITERIA:
        if criterion not in scores:
            scores[criterion] = 0

    overall = result.get("overall")
    if overall is None or not isinstance(overall, (int, float)):
        vals = [v for v in scores.values() if isinstance(v, (int, float))]
        overall = sum(vals) / len(vals) if vals else 0

    return {
        "scores": scores,
        "overall": round(float(overall), 1),
        "explanation": result.get("explanation", ""),
    }


def judge_all(scenarios, pipeline_states):
    """Run LLM judge on all scenarios.

    Args:
        scenarios: list of scenario dicts
        pipeline_states: dict mapping scenario_id -> pipeline_state

    Returns:
        list of per-scenario judge results, plus an overall summary.
    """
    results = []

    for scenario in scenarios:
        sid = scenario["id"]
        pipeline_state = pipeline_states.get(sid, {})

        if not pipeline_state:
            results.append({
                "scenario_id": sid,
                "scores": {c: 0 for c in JUDGE_CRITERIA},
                "overall": 0,
                "explanation": "No pipeline output found",
            })
            continue

        print(f"  Judging {sid}: {scenario.get('name', '')}...", end=" ", flush=True)
        result = judge_scenario(scenario, pipeline_state)
        result["scenario_id"] = sid
        results.append(result)
        print(f"Score: {result['overall']}/10")

    if not results:
        return {"per_scenario": [], "overall": 0.0, "criteria_averages": {}}

    valid = [r for r in results if r["overall"] > 0]
    overall_avg = sum(r["overall"] for r in valid) / len(valid) if valid else 0.0

    criteria_avgs = {}
    for criterion in JUDGE_CRITERIA:
        vals = [r["scores"].get(criterion, 0) for r in valid]
        criteria_avgs[criterion] = round(sum(vals) / len(vals), 1) if vals else 0.0

    return {
        "per_scenario": results,
        "overall": round(overall_avg, 1),
        "criteria_averages": criteria_avgs,
    }
