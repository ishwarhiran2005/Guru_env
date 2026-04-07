"""
SOS RL Environment — Core.

OpenEnv-compatible reinforcement learning environment where an AI agent
optimizes a student's life across Health, Wisdom, and Wealth dimensions.

Follows the OpenEnv async interface:
    await env.reset()          → Observation (typed)
    await env.step(action)     → (Observation, Reward) (typed)
    env.state()                → current observation dict

Score calculation logic is ported directly from the original SOS React
application (src/utils/scoreCalculations.js).
"""

from .state import StudentState
from .actions import ACTIONS, apply_action
from .reward import calculate_all_scores, calculate_reward
from .tasks import grade_task, TASKS
from .models import Observation, Action, Reward


class SOSEnv:
    """Student Optimization System — RL Environment.

    An episode starts with a struggling student (or randomized state).
    The agent takes sequential actions to improve the student's life
    metrics. The episode ends after `max_steps` actions.

    Attributes:
        max_steps: Maximum number of steps per episode.
        randomize: Whether to randomize the initial state.
        state_obj: Current StudentState instance.
        steps: Number of steps taken in current episode.
        current_scores: Latest calculated scores dict.
        reward_history: List of rewards received this episode.
    """

    def __init__(self, max_steps: int = 10, randomize: bool = False, task_id: str = None):
        self.max_steps = max_steps
        self.randomize = randomize
        self.task_id = task_id  # For task-aware rewards
        self.state_obj = None
        self.steps = 0
        self.current_scores = None
        self.reward_history = []
        self.action_history = []  # Track actions for diminishing returns

    # ------------------------------------------------------------------
    # Core API (OpenEnv Async Interface)
    # ------------------------------------------------------------------

    async def reset(self) -> Observation:
        """Reset environment to initial state.

        Returns:
            Observation: Typed initial observation including raw state + computed scores.
        """
        self.state_obj = StudentState(randomize=self.randomize)
        self.steps = 0
        self.current_scores = calculate_all_scores(self.state_obj.to_dict())
        self.reward_history = []
        self.action_history = []  # Reset action history
        return self._typed_observation()

    async def step(self, action: Action) -> tuple[Observation, Reward]:
        """Take a single environment step.

        Args:
            action: Typed Action object with action name.

        Returns:
            tuple: (Observation, Reward) - both typed Pydantic models
        """
        if self.state_obj is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")

        action_name = action.action
        if action_name not in ACTIONS:
            raise ValueError(
                f"Invalid action '{action_name}'. Must be one of: {ACTIONS}"
            )

        # Snapshot scores before action
        old_scores = self.current_scores.copy()

        # Apply action to state with diminishing returns
        apply_action(self.state_obj, action_name, self.action_history)
        self.action_history.append(action_name)
        self.steps += 1

        # Calculate new scores
        self.current_scores = calculate_all_scores(self.state_obj.to_dict())

        # Calculate reward (task-aware)
        reward_value = calculate_reward(old_scores, self.current_scores, self.task_id)
        self.reward_history.append(reward_value)

        # Check done condition
        done = self.steps >= self.max_steps

        # Build info dict
        info = {
            "step": self.steps,
            "action": action_name,
            "old_scores": old_scores,
            "new_scores": self.current_scores.copy(),
            "scores_delta": {
                k: self.current_scores[k] - old_scores[k]
                for k in ("health", "wisdom", "wealth", "total")
            },
        }

        # Return typed models
        observation = self._typed_observation()
        reward_obj = Reward(reward=reward_value, done=done, info=info)
        
        return observation, reward_obj

    def state(self) -> dict:
        """Return current observation (read-only).

        Returns:
            dict: Current state + scores, or empty dict if not initialized.
        """
        if self.state_obj is None:
            return {}
        return self._observation()

    # ------------------------------------------------------------------
    # Task Grading
    # ------------------------------------------------------------------

    def grade(self, task_id: str) -> float:
        """Grade the current state against a specific task.

        Args:
            task_id: One of 'health', 'balance', 'full_optimization'.

        Returns:
            Float score in [0.0, 1.0].
        """
        if self.state_obj is None:
            return 0.0
        return grade_task(task_id, self.state_obj.to_dict())

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @staticmethod
    def action_space() -> list:
        """Return list of valid action names."""
        return list(ACTIONS)

    @staticmethod
    def task_list() -> dict:
        """Return available tasks with descriptions."""
        return {
            tid: {"name": t["name"], "description": t["description"]}
            for tid, t in TASKS.items()
        }

    def episode_summary(self) -> dict:
        """Return summary of the current/completed episode."""
        return {
            "steps": self.steps,
            "total_reward": round(sum(self.reward_history), 4),
            "rewards": [round(r, 4) for r in self.reward_history],
            "final_scores": self.current_scores.copy() if self.current_scores else {},
            "grades": {
                tid: self.grade(tid) for tid in TASKS
            } if self.state_obj else {},
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _observation(self) -> dict:
        """Build the full observation dict (legacy format)."""
        obs = self.state_obj.to_dict()
        obs["scores"] = self.current_scores.copy()
        obs["step"] = self.steps
        obs["done"] = self.steps >= self.max_steps
        return obs

    def _typed_observation(self) -> Observation:
        """Build typed Observation model for OpenEnv compliance."""
        obs_dict = self._observation()
        return Observation(**obs_dict)
