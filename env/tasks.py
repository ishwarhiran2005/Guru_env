"""
Task Definitions & Graders for SOS RL Environment.

Each task defines a specific optimization goal the agent must achieve.
Grading functions return a float in [0.0, 1.0] where 1.0 = perfect.
"""

from .reward import calculate_all_scores


# ---------------------------------------------------------------------------
# Task 1: Health Optimization
# ---------------------------------------------------------------------------
def grade_health(state_dict: dict) -> float:
    """Grade the agent on health optimization.

    DIFFICULTY-CALIBRATED: Requires health >= 85 for perfect score.

    Scoring:
        health >= 85 → 1.0 (excellent)
        health 70-85 → 0.6-1.0 (smooth interpolation)
        health 50-70 → 0.2-0.6 (smooth interpolation)
        health < 50  → 0.0-0.2 (smooth interpolation)
    """
    scores = calculate_all_scores(state_dict)
    health = scores["health"]

    if health >= 85:
        return 1.0
    elif health >= 70:
        # Smooth interpolation: 70→0.6, 85→1.0
        return 0.6 + 0.4 * ((health - 70) / 15)
    elif health >= 50:
        # Smooth interpolation: 50→0.2, 70→0.6
        return 0.2 + 0.4 * ((health - 50) / 20)
    else:
        # Smooth interpolation: 0→0.0, 50→0.2
        return 0.2 * (health / 50)


# ---------------------------------------------------------------------------
# Task 2: Balance (Health + Wisdom)
# ---------------------------------------------------------------------------
def grade_balance(state_dict: dict) -> float:
    """Grade the agent on maintaining a balanced lifestyle.

    DIFFICULTY-CALIBRATED: Requires both >= 72 for perfect score.

    Requires:
        health >= 72  AND  wisdom >= 72

    Scoring:
        Both >= 72    → 1.0
        Average of normalized distances from 72
    """
    scores = calculate_all_scores(state_dict)
    health = scores["health"]
    wisdom = scores["wisdom"]

    # Calculate how close each metric is to target (72)
    health_score = min(1.0, health / 72)
    wisdom_score = min(1.0, wisdom / 72)

    # Both must be good for high score
    if health >= 72 and wisdom >= 72:
        return 1.0
    elif health >= 72 or wisdom >= 72:
        # One met: average of both normalized scores
        return (health_score + wisdom_score) / 2 * 0.75
    else:
        # Neither met: lower score based on average
        return (health_score + wisdom_score) / 2 * 0.5


# ---------------------------------------------------------------------------
# Task 3: Full Optimization (All Three ≥ 80)
# ---------------------------------------------------------------------------
def grade_full_optimization(state_dict: dict) -> float:
    """Grade the agent on full life optimization.

    DIFFICULTY-CALIBRATED: Requires all three >= 85 for perfect score.

    Requires:
        health >= 85  AND  wisdom >= 85  AND  wealth >= 85

    Scoring:
        All three >= 85 → 1.0
        Based on weakest metric (encourages balanced growth)
    """
    scores = calculate_all_scores(state_dict)
    health = scores["health"]
    wisdom = scores["wisdom"]
    wealth = scores["wealth"]

    # Count how many meet the 85 threshold
    met = sum(1 for s in (health, wisdom, wealth) if s >= 85)

    if met == 3:
        return 1.0
    elif met == 2:
        # Two met: score based on the weakest metric
        min_score = min(health, wisdom, wealth)
        return 0.65 + 0.35 * (min_score / 85)
    elif met == 1:
        # One met: score based on average
        avg_score = (health + wisdom + wealth) / 3
        return 0.35 + 0.30 * (avg_score / 85)
    else:
        # None met: score based on weakest metric
        min_score = min(health, wisdom, wealth)
        return 0.35 * (min_score / 85)


# ---------------------------------------------------------------------------
# Task Registry
# ---------------------------------------------------------------------------
TASKS = {
    "health": {
        "name": "Health Optimization",
        "description": "Optimize the student's health score to 80+",
        "grader": grade_health,
    },
    "balance": {
        "name": "Balanced Lifestyle",
        "description": "Achieve health >= 70 AND wisdom >= 70",
        "grader": grade_balance,
    },
    "full_optimization": {
        "name": "Full Life Optimization",
        "description": "Achieve health, wisdom, AND wealth all >= 80",
        "grader": grade_full_optimization,
    },
}


def grade_task(task_id: str, state_dict: dict) -> float:
    """Grade a task by ID.

    Args:
        task_id: One of 'health', 'balance', 'full_optimization'.
        state_dict: Output of StudentState.to_dict().

    Returns:
        Float score in [0.0, 1.0].

    Raises:
        KeyError: If task_id is not recognized.
    """
    if task_id not in TASKS:
        raise KeyError(
            f"Unknown task '{task_id}'. Available: {list(TASKS.keys())}"
        )
    return TASKS[task_id]["grader"](state_dict)
