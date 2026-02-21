"""
Oscillation Detection — Tracks per-agent score history and detects
alternating score patterns that indicate prompt instability.
"""


def detect_oscillation(score_history: list, min_swings: int = 3) -> bool:
    """Return True if scores alternate direction for min_swings consecutive iterations.

    A "swing" is a direction change: up->down or down->up.
    Three consecutive swings (e.g. up, down, up) over 4 data points means oscillation.

    Args:
        score_history: List of numeric scores ordered by iteration.
        min_swings: Minimum number of direction changes to flag oscillation.
    """
    if len(score_history) < min_swings + 1:
        return False

    # Compute direction changes: +1 = up, -1 = down, 0 = flat
    directions = []
    for i in range(1, len(score_history)):
        diff = score_history[i] - score_history[i - 1]
        if diff > 0:
            directions.append(1)
        elif diff < 0:
            directions.append(-1)
        else:
            directions.append(0)

    # Count consecutive alternations from the end of the history
    consecutive_swings = 0
    for i in range(len(directions) - 1, 0, -1):
        curr = directions[i]
        prev = directions[i - 1]
        # A swing = two consecutive non-zero directions with opposite signs
        if curr != 0 and prev != 0 and curr != prev:
            consecutive_swings += 1
        else:
            break

    return consecutive_swings >= min_swings


def check_oscillations(agent_score_history: dict, min_swings: int = 3) -> list:
    """Check all agents for oscillation.

    Args:
        agent_score_history: {agent_name: [score_iter1, score_iter2, ...]}
        min_swings: Minimum direction changes to flag.

    Returns:
        List of agent names that are oscillating.
    """
    oscillating = []
    for agent_name, scores in agent_score_history.items():
        if detect_oscillation(scores, min_swings):
            oscillating.append(agent_name)
    return oscillating
