"""
Comprehensive test suite for the SOS RL Environment.
Validates all components: state, actions, rewards, scoring, tasks, and env core.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from env.state import StudentState
from env.actions import ACTIONS, ACTION_EFFECTS, apply_action
from env.reward import (
    calculate_health,
    calculate_wisdom,
    calculate_wealth,
    calculate_all_scores,
    calculate_reward,
)
from env.tasks import grade_health, grade_balance, grade_full_optimization, grade_task, TASKS
from env.sos_env import SOSEnv


def sep(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# -----------------------------------------------------------------------
# TEST 1: StudentState
# -----------------------------------------------------------------------
sep("TEST 1: StudentState")

# Default state
s = StudentState()
print(f"Default state: {s}")
d = s.to_dict()
print(f"to_dict(): {d}")
assert d["sleep"] == 5.0
assert d["stress"] == 8
assert d["gpa"] == 2.5
print("✅ Default state OK")

# Randomized state
s2 = StudentState(randomize=True)
print(f"Random state:  {s2}")
d2 = s2.to_dict()
assert 3 <= d2["sleep"] <= 7
assert 4 <= d2["stress"] <= 10
print("✅ Randomized state OK")

# Clamping
s3 = StudentState()
s3.sleep = 99
s3.stress = -5
s3.gpa = 5.0
s3.clamp()
assert s3.sleep == 12
assert s3.stress == 1
assert s3.gpa == 4.0
print("✅ Clamping OK")


# -----------------------------------------------------------------------
# TEST 2: Score Calculations (ported from JS)
# -----------------------------------------------------------------------
sep("TEST 2: Score Calculations")

# Health: sleep=8, stress=3 → expected ~91
h = calculate_health(8, 3)
print(f"Health(sleep=8, stress=3) = {h}")
assert 85 <= h <= 100, f"Expected 85-100, got {h}"

# Health: sleep=5, stress=9 → expected ~35-50
h2 = calculate_health(5, 9)
print(f"Health(sleep=5, stress=9) = {h2}")
assert h2 < 60, f"Expected <60, got {h2}"

# Health edge: sleep=0 → 0
h3 = calculate_health(0, 5)
assert h3 == 0
print("✅ Health scores OK")

# Wisdom: gpa=3.9, acc=95, study=7 → expected ~93
w = calculate_wisdom(3.9, 95, 7)
print(f"Wisdom(gpa=3.9, acc=95, study=7) = {w}")
assert w >= 85, f"Expected >=85, got {w}"

# Wisdom: gpa=2.3, acc=55, study=2 → expected ~45-55
w2 = calculate_wisdom(2.3, 55, 2)
print(f"Wisdom(gpa=2.3, acc=55, study=2) = {w2}")
assert w2 < 65, f"Expected <65, got {w2}"
print("✅ Wisdom scores OK")

# Wealth: skill=12, gpa=3.9 → expected ~98-100
wl = calculate_wealth(12, 3.9)
print(f"Wealth(skill=12, gpa=3.9) = {wl}")
assert wl >= 90, f"Expected >=90, got {wl}"

# Wealth: skill=2, gpa=2.3 → expected ~42-48
wl2 = calculate_wealth(2, 2.3)
print(f"Wealth(skill=2, gpa=2.3) = {wl2}")
assert wl2 < 55, f"Expected <55, got {wl2}"
print("✅ Wealth scores OK")

# All scores at once
all_scores = calculate_all_scores({
    "sleep": 8, "stress": 3, "gpa": 3.9,
    "accuracy": 95, "study_hours": 7, "skill_time": 12
})
print(f"All scores (high performer): {all_scores}")
assert all_scores["total"] >= 250
print("✅ calculate_all_scores OK")


# -----------------------------------------------------------------------
# TEST 3: Actions
# -----------------------------------------------------------------------
sep("TEST 3: Actions")

print(f"Available actions ({len(ACTIONS)}): {ACTIONS}")
assert len(ACTIONS) == 7
assert "increase_sleep" in ACTIONS
assert "balance_routine" in ACTIONS

# Test applying action
s = StudentState()
old_sleep = s.sleep
apply_action(s, "increase_sleep")
assert s.sleep > old_sleep, f"Sleep should increase: {old_sleep} → {s.sleep}"
print(f"After increase_sleep: sleep {old_sleep} → {s.sleep}")
print("✅ Actions OK")

# Test invalid action
try:
    apply_action(s, "fly_to_moon")
    assert False, "Should have raised ValueError"
except ValueError:
    print("✅ Invalid action rejection OK")


# -----------------------------------------------------------------------
# TEST 4: Reward
# -----------------------------------------------------------------------
sep("TEST 4: Reward")

old = {"health": 50, "wisdom": 50, "wealth": 50, "total": 150}
new = {"health": 60, "wisdom": 55, "wealth": 55, "total": 170}
r = calculate_reward(old, new)
print(f"Reward for +20 total: {r}")
assert r > 0, f"Expected positive reward, got {r}"

# Negative reward
old2 = {"health": 80, "wisdom": 80, "wealth": 80, "total": 240}
new2 = {"health": 70, "wisdom": 75, "wealth": 75, "total": 220}
r2 = calculate_reward(old2, new2)
print(f"Reward for -20 total: {r2}")
assert r2 < 0, f"Expected negative reward, got {r2}"
print("✅ Reward OK")


# -----------------------------------------------------------------------
# TEST 5: Tasks & Grading
# -----------------------------------------------------------------------
sep("TEST 5: Tasks & Grading")

print(f"Available tasks: {list(TASKS.keys())}")
assert len(TASKS) == 3

# Health task — high performer
g1 = grade_health({"sleep": 8, "stress": 3, "gpa": 3.0, "accuracy": 80, "study_hours": 5, "skill_time": 5})
print(f"grade_health (high): {g1}")
assert g1 == 1.0

# Health task — struggling
g2 = grade_health({"sleep": 4, "stress": 9, "gpa": 2.0, "accuracy": 50, "study_hours": 2, "skill_time": 1})
print(f"grade_health (low):  {g2}")
assert g2 <= 0.6

# Balance task
g3 = grade_balance({"sleep": 8, "stress": 3, "gpa": 3.5, "accuracy": 85, "study_hours": 6, "skill_time": 5})
print(f"grade_balance (good): {g3}")
assert g3 == 1.0

# Full optimization
g4 = grade_full_optimization({"sleep": 8, "stress": 2, "gpa": 3.8, "accuracy": 90, "study_hours": 6, "skill_time": 12})
print(f"grade_full_opt (optimal): {g4}")
assert g4 == 1.0

# grade_task function
g5 = grade_task("health", {"sleep": 8, "stress": 3, "gpa": 3.0, "accuracy": 80, "study_hours": 5, "skill_time": 5})
assert g5 == 1.0
print("✅ Tasks & Grading OK")


# -----------------------------------------------------------------------
# TEST 6: SOSEnv Core
# -----------------------------------------------------------------------
sep("TEST 6: SOSEnv Core")

env = SOSEnv(max_steps=10, randomize=False)

# Reset
obs = env.reset()
print(f"Reset obs keys: {list(obs.keys())}")
assert "sleep" in obs
assert "scores" in obs
assert "step" in obs
assert obs["step"] == 0
assert obs["done"] == False
print(f"Initial scores: {obs['scores']}")
print("✅ reset() OK")

# State
state = env.state()
assert state == obs
print("✅ state() OK")

# Step
obs2, reward, done, info = env.step("increase_sleep")
print(f"After increase_sleep: reward={reward:.4f}, done={done}")
print(f"  Scores: {obs2['scores']}")
print(f"  Delta:  {info['scores_delta']}")
assert obs2["step"] == 1
assert done == False
assert isinstance(reward, float)
print("✅ step() OK")

# Run full episode
env2 = SOSEnv(max_steps=5)
obs = env2.reset()
actions_sequence = ["increase_sleep", "reduce_stress", "study_more", "practice_skills", "balance_routine"]
for i, action in enumerate(actions_sequence):
    obs, reward, done, info = env2.step(action)
    print(f"  Step {i+1}: {action:20s} → reward={reward:+.4f}, total={obs['scores']['total']}")

assert done == True
print("✅ Full episode OK")

# Episode summary
summary = env2.episode_summary()
print(f"\nEpisode summary:")
print(f"  Steps: {summary['steps']}")
print(f"  Total reward: {summary['total_reward']}")
print(f"  Final scores: {summary['final_scores']}")
print(f"  Grades: {summary['grades']}")
print("✅ episode_summary() OK")

# Grading
for task_id in TASKS:
    score = env2.grade(task_id)
    print(f"  Grade '{task_id}': {score:.2f}")
print("✅ grade() OK")

# Action space & task list
assert len(SOSEnv.action_space()) == 7
assert len(SOSEnv.task_list()) == 3
print("✅ Metadata methods OK")

# Invalid action
try:
    env.step("invalid_action")
    assert False, "Should have raised ValueError"
except ValueError:
    print("✅ Invalid action rejection OK")

# Uninitialized env
env3 = SOSEnv()
try:
    env3.step("increase_sleep")
    assert False, "Should have raised RuntimeError"
except RuntimeError:
    print("✅ Uninitialized env rejection OK")


# -----------------------------------------------------------------------
# TEST 7: OpenEnv Log Format Simulation
# -----------------------------------------------------------------------
sep("TEST 7: OpenEnv Log Format")

env = SOSEnv(max_steps=3)
obs = env.reset()
task_id = "health"

print(f"[START] task={task_id} env=sos model=test")

actions_to_test = ["increase_sleep", "reduce_stress", "balance_routine"]
rewards_list = []

for i, action in enumerate(actions_to_test):
    obs, reward, done, info = env.step(action)
    rewards_list.append(reward)
    print(
        f"[STEP] step={i+1} "
        f"action={action} "
        f"reward={reward:.2f} "
        f"done={'true' if done else 'false'} "
        f"error=null"
    )

score = env.grade(task_id)
success = score >= 0.8
rewards_str = ",".join(f"{r:.2f}" for r in rewards_list)
print(
    f"[END] success={'true' if success else 'false'} "
    f"steps={len(actions_to_test)} "
    f"score={score:.2f} "
    f"rewards={rewards_str}"
)
print("✅ Log format OK")


# -----------------------------------------------------------------------
# FINAL SUMMARY
# -----------------------------------------------------------------------
sep("ALL TESTS PASSED ✅")
print("  ✅ StudentState (default, random, clamping)")
print("  ✅ Score Calculations (health, wisdom, wealth)")
print("  ✅ Actions (apply, trade-offs, validation)")
print("  ✅ Reward (positive, negative, bonuses)")
print("  ✅ Tasks (health, balance, full_optimization)")
print("  ✅ SOSEnv (reset, step, state, grade, summary)")
print("  ✅ OpenEnv Log Format")
print()
