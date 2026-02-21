"""
Deterministic assertion engine for benchmark evaluation.
Evaluates assertions from scenario JSON against pipeline_state output.
"""


def resolve_field(data, field_path):
    """Resolve a dot-notation field path against a nested dict.

    Returns (value, found) tuple. found=False if any segment is missing.
    """
    parts = field_path.split(".")
    current = data
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return None, False
        current = current[part]
    return current, True


def evaluate_op(op, actual, expected):
    """Evaluate a single operator. Returns True if the assertion passes."""
    if op == "eq":
        return _normalize(actual) == _normalize(expected)

    if op == "neq":
        return _normalize(actual) != _normalize(expected)

    if op == "gt":
        return _to_num(actual) > _to_num(expected)

    if op == "gte":
        return _to_num(actual) >= _to_num(expected)

    if op == "lt":
        return _to_num(actual) < _to_num(expected)

    if op == "lte":
        return _to_num(actual) <= _to_num(expected)

    if op == "in":
        if not isinstance(expected, list):
            return False
        return _normalize(actual) in [_normalize(v) for v in expected]

    if op == "not_in":
        if not isinstance(expected, list):
            return True
        return _normalize(actual) not in [_normalize(v) for v in expected]

    if op == "between":
        if not isinstance(expected, list) or len(expected) != 2:
            return False
        num = _to_num(actual)
        return _to_num(expected[0]) <= num <= _to_num(expected[1])

    if op == "contains":
        if isinstance(actual, str) and isinstance(expected, str):
            return expected.lower() in actual.lower()
        if isinstance(actual, list):
            return expected in actual
        return str(expected).lower() in str(actual).lower()

    if op == "exists":
        # 'actual' is checked for existence; the found flag is what matters.
        # This is handled specially in evaluate_assertion.
        return True

    if op == "type_is":
        type_map = {
            "str": str, "string": str,
            "int": int, "integer": int,
            "float": float, "number": (int, float),
            "bool": bool, "boolean": bool,
            "list": list, "array": list,
            "dict": dict, "object": dict,
        }
        expected_type = type_map.get(str(expected).lower())
        if expected_type is None:
            return False
        return isinstance(actual, expected_type)

    return False


def _normalize(value):
    """Normalize values for comparison (handle string/bool/number coercion)."""
    if isinstance(value, str):
        lower = value.lower().strip()
        if lower == "true":
            return True
        if lower == "false":
            return False
        try:
            if "." in value:
                return float(value)
            return int(value)
        except (ValueError, TypeError):
            return lower
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    return value


def _to_num(value):
    """Convert value to a number for comparison."""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def evaluate_assertion(assertion, pipeline_state):
    """Evaluate a single assertion against pipeline_state.

    Returns a dict with: passed, agent, field, op, expected, actual, critical, reason.
    """
    agent = assertion["agent"]
    field = assertion["field"]
    op = assertion["op"]
    expected = assertion.get("value")
    critical = assertion.get("critical", False)

    agent_data = pipeline_state.get(agent)
    if agent_data is None:
        return {
            "passed": False,
            "agent": agent,
            "field": field,
            "op": op,
            "expected": expected,
            "actual": None,
            "critical": critical,
            "reason": f"Agent '{agent}' not found in pipeline_state",
        }

    actual, found = resolve_field(agent_data, field)

    if op == "exists":
        expected_exists = expected if isinstance(expected, bool) else True
        passed = found == expected_exists
        return {
            "passed": passed,
            "agent": agent,
            "field": field,
            "op": op,
            "expected": expected_exists,
            "actual": found,
            "critical": critical,
            "reason": None if passed else f"Field '{field}' exists={found}, expected exists={expected_exists}",
        }

    if not found:
        return {
            "passed": False,
            "agent": agent,
            "field": field,
            "op": op,
            "expected": expected,
            "actual": None,
            "critical": critical,
            "reason": f"Field '{agent}.{field}' not found",
        }

    passed = evaluate_op(op, actual, expected)
    return {
        "passed": passed,
        "agent": agent,
        "field": field,
        "op": op,
        "expected": expected,
        "actual": actual,
        "critical": critical,
        "reason": None if passed else f"Expected {field} {op} {expected!r}, got {actual!r}",
    }


def evaluate_business_rule(rule, pipeline_state):
    """Evaluate a conditional business rule (if/then).

    Returns a dict with: passed, name, condition_met, reason.
    If the 'if' condition is not met, the rule is vacuously true (skipped).
    """
    name = rule.get("name", "unnamed_rule")
    cond = rule["if"]
    then = rule["then"]

    cond_result = evaluate_assertion(
        {"agent": cond["agent"], "field": cond["field"], "op": cond["op"], "value": cond.get("value")},
        pipeline_state,
    )

    if not cond_result["passed"]:
        return {
            "passed": True,
            "name": name,
            "condition_met": False,
            "reason": "Condition not met — rule vacuously passes",
        }

    then_result = evaluate_assertion(
        {"agent": then["agent"], "field": then["field"], "op": then["op"], "value": then.get("value")},
        pipeline_state,
    )

    return {
        "passed": then_result["passed"],
        "name": name,
        "condition_met": True,
        "reason": then_result["reason"],
    }


def evaluate_scenario(scenario, pipeline_state):
    """Evaluate all assertions and business rules for a scenario.

    Returns a summary dict with per-assertion results, pass rates, and verdict.
    """
    assertions = scenario.get("assertions", [])
    business_rules = scenario.get("business_rules", [])
    verdict_criteria = scenario.get("verdict_criteria", {})

    assertion_results = [evaluate_assertion(a, pipeline_state) for a in assertions]
    rule_results = [evaluate_business_rule(r, pipeline_state) for r in business_rules]

    total = len(assertion_results)
    passed = sum(1 for r in assertion_results if r["passed"])
    critical_results = [r for r in assertion_results if r["critical"]]
    critical_total = len(critical_results)
    critical_passed = sum(1 for r in critical_results if r["passed"])
    non_critical_results = [r for r in assertion_results if not r["critical"]]
    non_critical_total = len(non_critical_results)
    non_critical_passed = sum(1 for r in non_critical_results if r["passed"])

    rules_total = len(rule_results)
    rules_passed = sum(1 for r in rule_results if r["passed"])
    rules_applicable = sum(1 for r in rule_results if r.get("condition_met", False))

    pass_rate = (passed / total * 100) if total > 0 else 100.0
    critical_pass_rate = (critical_passed / critical_total * 100) if critical_total > 0 else 100.0
    non_critical_pass_rate = (non_critical_passed / non_critical_total * 100) if non_critical_total > 0 else 100.0

    # Determine verdict
    require_all_critical = verdict_criteria.get("require_all_critical", True)
    min_nc_rate = verdict_criteria.get("min_non_critical_pass_rate", 0.7)

    all_critical_pass = critical_passed == critical_total
    nc_meets_min = (non_critical_passed / non_critical_total >= min_nc_rate) if non_critical_total > 0 else True

    if require_all_critical:
        verdict = "PASS" if (all_critical_pass and nc_meets_min) else "FAIL"
    else:
        verdict = "PASS" if nc_meets_min else "FAIL"

    return {
        "scenario_id": scenario["id"],
        "scenario_name": scenario.get("name", ""),
        "verdict": verdict,
        "assertions": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(pass_rate, 1),
        },
        "critical": {
            "total": critical_total,
            "passed": critical_passed,
            "failed": critical_total - critical_passed,
            "pass_rate": round(critical_pass_rate, 1),
        },
        "non_critical": {
            "total": non_critical_total,
            "passed": non_critical_passed,
            "failed": non_critical_total - non_critical_passed,
            "pass_rate": round(non_critical_pass_rate, 1),
        },
        "business_rules": {
            "total": rules_total,
            "passed": rules_passed,
            "applicable": rules_applicable,
        },
        "details": assertion_results,
        "rule_details": rule_results,
    }
