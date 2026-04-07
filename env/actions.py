"""
Action Space for SOS RL Environment.

Each action modifies the StudentState in a realistic way.
Effects are designed so that no single action is a free win — every choice
has trade-offs (e.g., studying more raises stress).
"""

# Ordered list of valid actions the agent can choose from.
ACTIONS = [
    "increase_sleep",
    "reduce_stress",
    "study_more",
    "practice_skills",
    "take_break",
    "improve_accuracy",
    "balance_routine",
]

# How each action mutates the student state.
# Format: { attribute: delta }
# Positive = increase, Negative = decrease.
# DIFFICULTY-CALIBRATED: Strong trade-offs, no dominant strategies.
ACTION_EFFECTS = {
    "increase_sleep": {
        "sleep": +1.2,
        "stress": -0.6,
        "study_hours": -0.8,      # significant time cost
        "accuracy": -1.5,         # less study time hurts accuracy
    },
    "reduce_stress": {
        "stress": -1.5,
        "accuracy": +2.0,
        "sleep": +0.3,
        "study_hours": -0.5,      # relaxation takes time
    },
    "study_more": {
        "study_hours": +1.5,
        "accuracy": +2.5,
        "gpa": +0.08,
        "stress": +1.5,           # high stress cost
        "sleep": -0.8,            # significant sleep cost
        "skill_time": -0.5,       # time shifted from skills
    },
    "practice_skills": {
        "skill_time": +3.0,
        "accuracy": +0.5,
        "stress": +1.0,           # increased stress
        "study_hours": -1.0,      # significant academic cost
        "gpa": -0.05,             # neglecting academics
    },
    "take_break": {
        "stress": -2.0,
        "sleep": +0.5,
        "study_hours": -1.5,      # major productivity loss
        "skill_time": -1.0,       # major skill loss
        "accuracy": -1.0,         # losing sharpness
    },
    "improve_accuracy": {
        "accuracy": +3.5,
        "gpa": +0.12,
        "study_hours": +1.2,
        "stress": +1.5,           # high stress cost
        "sleep": -1.0,            # significant sleep cost
        "skill_time": -0.8,       # time cost
    },
    "balance_routine": {
        "sleep": +0.1,            # HEAVILY NERFED
        "study_hours": +0.1,      # HEAVILY NERFED
        "stress": -0.1,           # HEAVILY NERFED
        "accuracy": +0.2,         # HEAVILY NERFED
        "skill_time": +0.2,       # HEAVILY NERFED
        "gpa": +0.01,             # HEAVILY NERFED
    },
}


def apply_action(state, action: str, action_history: list = None):
    """Apply an action's effects to a StudentState with diminishing returns.

    Args:
        state: StudentState instance.
        action: One of the keys in ACTIONS.
        action_history: List of recent actions for diminishing returns.

    Raises:
        ValueError: If action is not recognized.
    """
    if action not in ACTION_EFFECTS:
        raise ValueError(
            f"Unknown action '{action}'. Valid actions: {ACTIONS}"
        )

    effects = ACTION_EFFECTS[action].copy()
    
    # DIMINISHING RETURNS: Repeated actions become less effective
    if action_history:
        # Count how many times this action was used in last 3 steps
        recent_count = sum(1 for a in action_history[-3:] if a == action)
        if recent_count > 0:
            # Reduce effectiveness by 30% per repetition
            multiplier = 0.7 ** recent_count
            effects = {k: v * multiplier for k, v in effects.items()}

    for attr, delta in effects.items():
        current = getattr(state, attr)
        setattr(state, attr, current + delta)

    # Enforce bounds after mutation
    state.clamp()
