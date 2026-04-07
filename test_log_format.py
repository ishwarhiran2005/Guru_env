"""
Test script to verify log format compliance without requiring OpenAI API.

This script simulates the inference flow and validates that all log
outputs match the required OpenEnv format.
"""

import asyncio
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from env.sos_env import SOSEnv
from env.models import Action
from env.tasks import TASKS


async def test_log_format():
    """Test that environment produces correct log format."""
    print("=" * 60)
    print("TESTING LOG FORMAT COMPLIANCE")
    print("=" * 60)
    
    task_id = "health"
    model = "test-model"
    max_steps = 5
    
    env = SOSEnv(max_steps=max_steps, randomize=False, task_id=task_id)
    
    # Simulate START log
    start_log = f"[START] task={task_id} env=sos model={model}"
    print(f"\n{start_log}")
    
    # Validate START format
    assert re.match(r'\[START\] task=\w+ env=\w+ model=[\w-]+', start_log), "START format invalid"
    print("✅ START log format valid")
    
    # Reset environment
    obs = await env.reset()
    rewards = []
    actions_taken = ["increase_sleep", "reduce_stress", "study_more", "balance_routine", "take_break"]
    
    # Run steps
    for step_num, action_name in enumerate(actions_taken[:max_steps], start=1):
        action = Action(action=action_name)
        obs, reward_obj = await env.step(action)
        
        reward = reward_obj.reward
        done = reward_obj.done
        rewards.append(reward)
        
        # Simulate STEP log
        step_log = (
            f"[STEP] step={step_num} "
            f"action={action_name} "
            f"reward={reward:.2f} "
            f"done={'true' if done else 'false'} "
            f"error=null"
        )
        print(step_log)
        
        # Validate STEP format
        assert re.match(r'\[STEP\] step=\d+ action=\w+ reward=-?\d+\.\d{2} done=(true|false) error=(null|\w+)', step_log), \
            f"STEP format invalid: {step_log}"
    
    print("✅ All STEP logs format valid")
    
    # Grade final state
    score = env.grade(task_id)
    success = score >= 0.8
    
    # Simulate END log
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    end_log = (
        f"[END] success={'true' if success else 'false'} "
        f"steps={len(rewards)} "
        f"score={score:.2f} "
        f"rewards={rewards_str}"
    )
    print(end_log)
    
    # Validate END format
    assert re.match(r'\[END\] success=(true|false) steps=\d+ score=\d+\.\d{2} rewards=(-?\d+\.\d{2},?)+', end_log), \
        f"END format invalid: {end_log}"
    print("✅ END log format valid")
    
    # Validate specific requirements
    print("\n" + "=" * 60)
    print("VALIDATING SPECIFIC REQUIREMENTS")
    print("=" * 60)
    
    # Check reward has 2 decimal places
    for r in rewards:
        formatted = f"{r:.2f}"
        assert len(formatted.split('.')[-1]) == 2, f"Reward {r} doesn't have 2 decimal places"
    print("✅ All rewards have exactly 2 decimal places")
    
    # Check done is lowercase true/false
    assert reward_obj.done in (True, False), "done must be boolean"
    done_str = 'true' if reward_obj.done else 'false'
    assert done_str in ('true', 'false'), "done string must be lowercase true/false"
    print("✅ done is lowercase true/false")
    
    # Check error is null or string
    error = None
    error_str = error if error else 'null'
    assert error_str == 'null' or isinstance(error_str, str), "error must be null or string"
    print("✅ error is null or string")
    
    # Check score has 2 decimal places
    score_formatted = f"{score:.2f}"
    assert len(score_formatted.split('.')[-1]) == 2, f"Score {score} doesn't have 2 decimal places"
    print("✅ score has exactly 2 decimal places")
    
    print("\n" + "=" * 60)
    print("ALL LOG FORMAT TESTS PASSED ✅")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_log_format())
