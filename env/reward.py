"""
Score Calculation & Reward for SOS RL Environment.

Ported DIRECTLY from the original SOS codebase:
  - src/utils/scoreCalculations.js
  - src/context/AppContext.jsx (calculateHealth, calculateWisdom, calculateWealth)

The formulas, weights, and thresholds are identical to the original JS implementation.
"""


def calculate_health(sleep: float, stress: int) -> int:
    """Calculate Health score (0-100).

    Ported from scoreCalculations.js → calculateHealth().

    Weights:
        - Sleep hours : 70%
        - Stress level: 30%

    Args:
        sleep: Hours of sleep per night.
        stress: Stress level (1-10).

    Returns:
        Integer health score clamped to [0, 100].
    """
    if sleep <= 0:
        return 0

    # Sleep score (same thresholds as JS)
    if 7 <= sleep <= 9:
        sleep_score = 100
    elif 6 <= sleep < 7:
        sleep_score = 85
    elif 5 <= sleep < 6:
        sleep_score = 65
    elif sleep < 5:
        sleep_score = 40
    else:
        sleep_score = 75  # Over 9 hours

    # Stress impact (inverted: low stress = high score)
    stress_impact = (11 - int(stress)) * 10

    # Weighted combination: 70% sleep, 30% stress
    health = round((sleep_score * 0.7) + (stress_impact * 0.3))
    return max(0, min(100, health))


def calculate_wisdom(gpa: float, accuracy: float, study_hours: float) -> int:
    """Calculate Wisdom score (0-100).

    Ported from scoreCalculations.js → calculateWisdom().

    Weights:
        - GPA        : 40%
        - Accuracy   : 35%
        - Study hours: 25%

    Args:
        gpa: Current GPA (0-4.0).
        accuracy: Assignment accuracy percentage (0-100).
        study_hours: Daily study hours.

    Returns:
        Integer wisdom score clamped to [0, 100].
    """
    if gpa <= 0 or accuracy <= 0 or study_hours <= 0:
        return 0

    gpa_score = (gpa / 4.0) * 100
    accuracy_score = accuracy

    # Study hours thresholds (same as JS)
    if 5 <= study_hours <= 8:
        study_score = 100
    elif study_hours >= 3:
        study_score = 75
    elif study_hours >= 2:
        study_score = 50
    else:
        study_score = 30

    wisdom = round((gpa_score * 0.4) + (accuracy_score * 0.35) + (study_score * 0.25))
    return max(0, min(100, wisdom))


def calculate_wealth(skill_time: float, gpa: float) -> int:
    """Calculate Wealth score (0-100).

    Ported from scoreCalculations.js → calculateWealth().
    NOTE: Fixed operator precedence bug from original AppContext.jsx line 185.

    Weights:
        - Skill dev time: 80%
        - GPA bonus     : 20%

    Args:
        skill_time: Skill development hours per week.
        gpa: Current GPA (0-4.0).

    Returns:
        Integer wealth score clamped to [0, 100].
    """
    if skill_time <= 0:
        return 0

    # Skill time thresholds (same as JS)
    if skill_time >= 10:
        skill_score = 100
    elif skill_time >= 7:
        skill_score = 85
    elif skill_time >= 5:
        skill_score = 70
    elif skill_time >= 3:
        skill_score = 55
    else:
        skill_score = 40

    gpa_bonus = (gpa / 4.0) * 20

    wealth = round((skill_score * 0.8) + gpa_bonus)
    return max(0, min(100, wealth))


def calculate_all_scores(state_dict: dict) -> dict:
    """Calculate all three scores from a state dictionary.

    Args:
        state_dict: Output of StudentState.to_dict().

    Returns:
        {"health": int, "wisdom": int, "wealth": int, "total": int}
    """
    health = calculate_health(state_dict["sleep"], state_dict["stress"])
    wisdom = calculate_wisdom(
        state_dict["gpa"], state_dict["accuracy"], state_dict["study_hours"]
    )
    wealth = calculate_wealth(state_dict["skill_time"], state_dict["gpa"])
    total = health + wisdom + wealth

    return {
        "health": health,
        "wisdom": wisdom,
        "wealth": wealth,
        "total": total,
    }


def calculate_reward(old_scores: dict, new_scores: dict, task_id: str = None) -> float:
    """Calculate step reward as normalized score improvement with task-aware bonuses.

    DIFFICULTY-CALIBRATED: Reduced over-generous rewards.

    Args:
        old_scores: Scores dict before action.
        new_scores: Scores dict after action.
        task_id: Optional task identifier for task-specific rewards.

    Returns:
        Float reward in roughly [-1.0, 1.0] range.
        Positive = improvement, Negative = regression.
    """
    # Base reward: normalized total improvement (REDUCED from /300 to /400)
    delta = new_scores["total"] - old_scores["total"]
    reward = delta / 400.0  # Less generous than before

    # TASK-AWARE REWARD SHAPING (reduced bonuses)
    if task_id == "health":
        # Reward health improvements for health task (reduced from 0.8 to 0.5)
        health_delta = new_scores["health"] - old_scores["health"]
        reward += health_delta / 100.0 * 0.5

    elif task_id == "balance":
        # Reward health + wisdom improvements (reduced from 0.6 to 0.4)
        health_delta = new_scores["health"] - old_scores["health"]
        wisdom_delta = new_scores["wisdom"] - old_scores["wisdom"]
        reward += (health_delta + wisdom_delta) / 200.0 * 0.4

    elif task_id == "full_optimization":
        # Reward balanced growth (reduced from 0.7 to 0.5)
        min_score = min(new_scores["health"], new_scores["wisdom"], new_scores["wealth"])
        old_min = min(old_scores["health"], old_scores["wisdom"], old_scores["wealth"])
        min_delta = min_score - old_min
        reward += min_delta / 100.0 * 0.5

    # MILESTONE BONUSES (reduced)
    for metric in ("health", "wisdom", "wealth"):
        # Crossed 70 threshold
        if old_scores[metric] < 70 and new_scores[metric] >= 70:
            reward += 0.05  # Reduced from 0.10
        # Crossed 85 threshold
        if old_scores[metric] < 85 and new_scores[metric] >= 85:
            reward += 0.08  # Reduced from 0.15

    # IMBALANCE PENALTY (stronger)
    if any(new_scores[m] < 40 for m in ("health", "wisdom", "wealth")):
        reward -= 0.20  # Increased from 0.15

    # BALANCED GROWTH BONUS (reduced)
    if all(new_scores[m] > old_scores[m] for m in ("health", "wisdom", "wealth")):
        reward += 0.03  # Reduced from 0.05

    return round(reward, 4)
