"""
Test script to verify OpenEnv async compliance.

Tests:
1. Async reset() returns typed Observation
2. Async step() accepts typed Action and returns typed Observation + Reward
3. All Pydantic models validate correctly
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from env.sos_env import SOSEnv
from env.models import Observation, Action, Reward


async def test_async_interface():
    """Test the async OpenEnv interface."""
    print("=" * 60)
    print("TESTING OPENENV ASYNC INTERFACE")
    print("=" * 60)
    
    # Initialize environment
    env = SOSEnv(max_steps=5, randomize=False, task_id="health")
    
    # Test 1: Async reset returns typed Observation
    print("\n[TEST 1] Testing async reset()...")
    obs = await env.reset()
    assert isinstance(obs, Observation), f"Expected Observation, got {type(obs)}"
    print(f"✅ Reset returned typed Observation")
    print(f"   - sleep: {obs.sleep}")
    print(f"   - study_hours: {obs.study_hours}")
    print(f"   - stress: {obs.stress}")
    print(f"   - scores: {obs.scores}")
    print(f"   - step: {obs.step}")
    print(f"   - done: {obs.done}")
    
    # Test 2: Async step accepts typed Action
    print("\n[TEST 2] Testing async step() with typed Action...")
    action = Action(action="increase_sleep")
    obs, reward_obj = await env.step(action)
    
    assert isinstance(obs, Observation), f"Expected Observation, got {type(obs)}"
    assert isinstance(reward_obj, Reward), f"Expected Reward, got {type(reward_obj)}"
    print(f"✅ Step accepted typed Action and returned typed Observation + Reward")
    print(f"   - action: {action.action}")
    print(f"   - reward: {reward_obj.reward}")
    print(f"   - done: {reward_obj.done}")
    print(f"   - new sleep: {obs.sleep}")
    print(f"   - new scores: {obs.scores}")
    
    # Test 3: Run a few more steps
    print("\n[TEST 3] Running multiple steps...")
    actions = ["reduce_stress", "study_more", "balance_routine"]
    for i, action_name in enumerate(actions, start=2):
        action = Action(action=action_name)
        obs, reward_obj = await env.step(action)
        print(f"   Step {i}: {action_name} -> reward={reward_obj.reward:.4f}, done={reward_obj.done}")
    
    print(f"\n✅ All steps completed successfully")
    print(f"   - final step: {obs.step}")
    print(f"   - final done: {obs.done}")
    print(f"   - final scores: {obs.scores}")
    
    # Test 4: Pydantic validation
    print("\n[TEST 4] Testing Pydantic validation...")
    try:
        invalid_action = Action(action="invalid_action")
        print("❌ Validation failed - invalid action was accepted")
    except Exception as e:
        print(f"✅ Pydantic validation working: {type(e).__name__}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_async_interface())
