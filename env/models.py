"""
Pydantic Models for OpenEnv Compliance.

These models define the typed interfaces required by the OpenEnv specification:
- Observation: The state returned by reset() and step()
- Action: The action input to step()
- Reward: The reward output from step()
"""

from pydantic import BaseModel, Field
from typing import Optional


class Observation(BaseModel):
    """Observation returned by the environment.
    
    Includes both raw state variables and computed scores.
    """
    # Raw state variables
    sleep: float = Field(..., ge=0, le=12, description="Hours of sleep per night")
    study_hours: float = Field(..., ge=0, le=16, description="Hours of study per day")
    stress: int = Field(..., ge=1, le=10, description="Stress level (1-10)")
    accuracy: float = Field(..., ge=0, le=100, description="Assignment accuracy percentage")
    gpa: float = Field(..., ge=0.0, le=4.0, description="Current GPA")
    skill_time: float = Field(..., ge=0, le=40, description="Skill development hours per week")
    
    # Computed scores
    scores: dict = Field(..., description="Computed health, wisdom, wealth, and total scores")
    
    # Episode metadata
    step: int = Field(..., ge=0, description="Current step number")
    done: bool = Field(..., description="Whether episode is finished")


class Action(BaseModel):
    """Action input to the environment.
    
    Must be one of the valid action names from the action space.
    """
    action: str = Field(
        ...,
        description="Action name to execute",
        pattern="^(increase_sleep|reduce_stress|study_more|practice_skills|take_break|improve_accuracy|balance_routine)$"
    )


class Reward(BaseModel):
    """Reward output from the environment.
    
    Includes the reward value and additional metadata.
    """
    reward: float = Field(..., description="Reward value for the step")
    done: bool = Field(..., description="Whether episode is finished")
    info: dict = Field(default_factory=dict, description="Additional metadata")
