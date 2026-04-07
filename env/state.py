"""
Student State Definition for SOS RL Environment.

Ported from the original SOS React app's InputData fields and score calculations.
Each attribute maps directly to a user input from the original system:
  - sleep       → sleepHours (hours/night, 0-12)
  - study_hours → studyHours (hours/day, 0-16)
  - stress      → stressLevel (1-10 scale)
  - accuracy    → accuracy (0-100%)
  - gpa         → gpa (0.0-4.0)
  - skill_time  → skillTime (hours/week, 0-40)
"""

import random


class StudentState:
    """Represents the observable state of a student agent.

    Default values represent a struggling student — the agent's job is to
    improve these metrics through sequential actions.
    """

    # Bounds for each attribute: (min, max)
    BOUNDS = {
        "sleep": (0, 12),
        "study_hours": (0, 16),
        "stress": (1, 10),
        "accuracy": (0, 100),
        "gpa": (0.0, 4.0),
        "skill_time": (0, 40),
    }

    def __init__(self, randomize: bool = False):
        if randomize:
            self.sleep = round(random.uniform(3, 7), 1)
            self.study_hours = round(random.uniform(1, 5), 1)
            self.stress = random.randint(4, 10)
            self.accuracy = round(random.uniform(40, 75), 1)
            self.gpa = round(random.uniform(1.5, 3.2), 2)
            self.skill_time = round(random.uniform(0, 6), 1)
        else:
            self.sleep = 5.0
            self.study_hours = 2.0
            self.stress = 8
            self.accuracy = 60.0
            self.gpa = 2.5
            self.skill_time = 1.0

    def clamp(self):
        """Enforce hard bounds on all attributes."""
        for attr, (lo, hi) in self.BOUNDS.items():
            val = getattr(self, attr)
            # Special handling for stress - must be integer
            if attr == "stress":
                setattr(self, attr, int(max(lo, min(hi, val))))
            else:
                setattr(self, attr, round(max(lo, min(hi, val)), 2))

    def to_dict(self) -> dict:
        """Return state as a flat dictionary (observation vector)."""
        return {
            "sleep": self.sleep,
            "study_hours": self.study_hours,
            "stress": self.stress,
            "accuracy": self.accuracy,
            "gpa": self.gpa,
            "skill_time": self.skill_time,
        }

    def __repr__(self) -> str:
        return (
            f"StudentState(sleep={self.sleep}, study={self.study_hours}, "
            f"stress={self.stress}, acc={self.accuracy}, "
            f"gpa={self.gpa}, skill={self.skill_time})"
        )
