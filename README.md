---
title: Guru Env - Student Optimization System
emoji: 🎓
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# SOS — Student Optimization System (v2.0)
## OpenEnv RL Environment (Async + Typed)

> An AI agent learns to optimize a student's life across **Health**, **Wisdom**, and **Wealth** — one action at a time.

---

## 🧠 What Is This?

SOS v2.0 is an **OpenEnv-compliant reinforcement learning environment** where an AI agent takes sequential actions to improve a simulated student's life metrics. The environment uses:

- **Async methods** (`async def reset()`, `async def step()`) for OpenEnv compatibility
- **Pydantic typed models** (Observation, Action, Reward) for type safety
- **Direct port** of scoring algorithms from the original SOS React app

---

## 📁 Project Structure

```
openenv_sos/
├── env/
│   ├── __init__.py          # Package exports
│   ├── sos_env.py           # Core RL environment (async reset/step)
│   ├── models.py            # Pydantic models (Observation, Action, Reward)
│   ├── state.py             # StudentState class definition
│   ├── actions.py           # Action space + effect definitions
│   ├── reward.py            # Score calculation & reward function
│   └── tasks.py             # Task definitions & grading functions
│
├── server/
│   ├── __init__.py          # Server package
│   └── app.py               # OpenEnv server entry point
│
├── inference.py             # AI agent inference (async, OpenEnv format)
├── openenv.yaml             # Environment configuration
├── pyproject.toml           # Python package configuration
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container definition
└── README.md                # This file
```

---

## 🎯 State Space

The student's observable state consists of 6 variables:

| Variable       | Type  | Range   | Unit        | Description                        |
|---------------|-------|---------|-------------|------------------------------------|
| `sleep`       | float | 0–12    | hrs/night   | Average sleep hours per night      |
| `study_hours` | float | 0–16    | hrs/day     | Daily study hours                  |
| `stress`      | int   | 1–10    | scale       | Self-reported stress level         |
| `accuracy`    | float | 0–100   | percent     | Assignment accuracy percentage     |
| `gpa`         | float | 0.0–4.0 | GPA         | Current grade point average        |
| `skill_time`  | float | 0–40    | hrs/week    | Weekly skill development hours     |

**Default initial state** (struggling student):
sleep=5.0, study=2.0, stress=8, accuracy=60, gpa=2.5, skill_time=1.0
```

---

## 🎮 Action Space

7 discrete actions, each with realistic trade-offs:

| Action              | Primary Effect          | Trade-off                    |
|--------------------|------------------------|------------------------------|
| `increase_sleep`   | +1 sleep, -0.5 stress  | -0.5 study hours             |
| `reduce_stress`    | -1.5 stress, +2 acc    | +0.5 sleep                   |
| `study_more`       | +1.5 study, +0.1 GPA   | +1.0 stress, -0.5 sleep      |
| `practice_skills`  | +3.0 skill time        | +0.5 stress, -0.5 study      |
| `take_break`       | -2.0 stress, +0.5 sleep| -1.0 study, -0.5 skill       |
| `improve_accuracy` | +3.0 accuracy, +0.10 GPA| +1.0 stress, -0.5 sleep     |
| `balance_routine`  | Small gains across all | Balanced, no major effects   |

---

## 📊 Score Calculation

Three scores are computed from the state, using formulas ported from the original SOS app:

### Health Score (0–100)
```
sleep_score = {7-9h: 100, 6-7h: 85, 5-6h: 65, <5h: 40, >9h: 75}
stress_impact = (11 - stress) × 10
health = (sleep_score × 0.70) + (stress_impact × 0.30)
```

### Wisdom Score (0–100)
```
gpa_score = (gpa / 4.0) × 100
study_score = {5-8h: 100, 3-5h: 75, 2-3h: 50, <2h: 30}
wisdom = (gpa_score × 0.40) + (accuracy × 0.35) + (study_score × 0.25)
```

### Wealth Score (0–100)
```
skill_score = {≥10h: 100, 7-10h: 85, 5-7h: 70, 3-5h: 55, <3h: 40}
gpa_bonus = (gpa / 4.0) × 20
wealth = (skill_score × 0.80) + gpa_bonus
```

---

## 🏆 Tasks

Three tasks with increasing difficulty:

| Task ID              | Difficulty | Goal                                        | Episode Length |
|---------------------|-----------|---------------------------------------------|----------------|
| `health`            | Easy      | Health ≥ 85                                 | 12 steps       |
| `balance`           | Medium    | Health ≥ 72 AND Wisdom ≥ 72                 | 18 steps       |
| `full_optimization` | Hard      | Health ≥ 85 AND Wisdom ≥ 85 AND Wealth ≥ 85 | 25 steps       |

All tasks return scores between 0.0–1.0 with smooth grading (partial progress rewarded).

### Why This Environment is Challenging

1. **Strong Trade-offs**: Every action has significant costs
   - Studying increases stress and reduces sleep
   - Practicing skills hurts academic performance
   - Taking breaks reduces productivity

2. **Diminishing Returns**: Repeating the same action becomes 30% less effective each time
   - Forces strategic variety
   - Prevents trivial "spam one action" solutions

3. **Balanced Optimization**: Success requires managing competing metrics
   - Can't ignore any dimension
   - Must sequence actions carefully

### Baseline Performance

| Strategy | Health Task | Balance Task | Full Optimization |
|----------|-------------|--------------|-------------------|
| Random actions | 0.2-0.3 | 0.2-0.3 | 0.2-0.3 |
| Single action spam | 0.3-0.7 | 0.3-0.5 | 0.2-0.4 |
| Strategic planning | 0.8-1.0 | 0.8-1.0 | 0.7-0.9 |

**Key Insight**: Only intelligent, strategic action sequences succeed. The environment requires genuine decision-making.

---

## 🚀 Setup & Usage

### Prerequisites
- Python 3.10+
- OpenAI API key

### Install
```bash
pip install openai
```

### Run Inference
```bash
# Set API key
export OPENAI_API_KEY="your-key-here"

# Run all tasks
python inference.py

# Run specific task
python inference.py --task health

# Use a specific model
python inference.py --model gpt-4o

# Randomized initial state
python inference.py --randomize

# Custom episode length
python inference.py --max-steps 15
```

### Docker
```bash
docker build -t sos-env .
docker run -e OPENAI_API_KEY="your-key" sos-env
```

### Programmatic Usage
```python
from env import SOSEnv

env = SOSEnv(max_steps=10, randomize=False)
obs = env.reset()

# Take actions
obs, reward, done, info = env.step("increase_sleep")
obs, reward, done, info = env.step("reduce_stress")
obs, reward, done, info = env.step("study_more")

# Check scores
print(env.state())

# Grade against a task
score = env.grade("health")
print(f"Health task score: {score}")

# Episode summary
print(env.episode_summary())
```

---

## 📜 Example Output

```
============================================================
  RUNNING TASK: Health Optimization
============================================================

[START] task=health env=sos model=gpt-4o-mini
[STEP] step=1 action=increase_sleep reward=0.07 done=false error=null
[STEP] step=2 action=reduce_stress reward=0.04 done=false error=null
[STEP] step=3 action=increase_sleep reward=0.05 done=false error=null
[STEP] step=4 action=reduce_stress reward=0.03 done=false error=null
[STEP] step=5 action=balance_routine reward=0.02 done=false error=null
[STEP] step=6 action=study_more reward=0.01 done=false error=null
[STEP] step=7 action=improve_accuracy reward=0.02 done=false error=null
[STEP] step=8 action=practice_skills reward=0.03 done=false error=null
[STEP] step=9 action=balance_routine reward=0.01 done=false error=null
[STEP] step=10 action=reduce_stress reward=0.02 done=true error=null
[END] success=true steps=10 score=1.00 rewards=0.07,0.04,0.05,0.03,0.02,0.01,0.02,0.03,0.01,0.02

============================================================
  FINAL RESULTS SUMMARY
============================================================
  ✅ PASS  health                     score=1.00  steps=10  total_reward=0.3000
```

---

## 🧪 Reward Function

The reward function provides task-aware guidance with intermediate signals:

```python
# Base reward: normalized score improvement
reward = (new_total - old_total) / 300

# Task-specific bonuses (guides agent toward goal)
if task == "health":
    reward += health_improvement * 0.8
elif task == "balance":
    reward += (health + wisdom improvement) * 0.6
elif task == "full_optimization":
    reward += weakest_metric_improvement * 0.7

# Milestone bonuses (early guidance)
+0.10 for crossing 60 threshold
+0.15 for crossing 80 threshold

# Penalties & bonuses
-0.15 if any metric < 40 (imbalance penalty)
+0.05 if all metrics improved (balanced growth)
```

---

## � OpenEnv Compliance

This environment is **fully compliant** with the OpenEnv specification:

### ✅ Async Interface
- `async def reset() -> Observation` - Asynchronous environment reset
- `async def step(action: Action) -> tuple[Observation, Reward]` - Asynchronous step execution

### ✅ Pydantic Typed Models
- **Observation**: Typed state with all student metrics + scores
- **Action**: Validated action input (must be one of 7 valid actions)
- **Reward**: Typed reward output with metadata

### ✅ Validation
Run compliance tests:
```bash
# Test async interface
python test_async_env.py

# Test log format
python test_log_format.py

# Full compliance check
python test_openenv_compliance.py

# OpenEnv validation (Docker mode supported)
openenv validate
```

### ✅ Docker Deployment
The environment is ready for Docker deployment:
```bash
docker build -t sos-env .
docker run -e OPENAI_API_KEY=your_key sos-env
```

---

## 📄 License

Educational project — Student Optimization System v2.0
