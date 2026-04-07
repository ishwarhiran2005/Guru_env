"""
SOS RL Environment — Inference Script (OpenEnv MANDATORY Format).

This script runs the AI agent against the SOS environment using an
OpenAI-compatible model. It prints logs in the EXACT format required
by the OpenEnv evaluation framework.

Uses async/await for OpenEnv compliance.

Usage:
    python inference.py                          # Run all tasks
    python inference.py --task health            # Run specific task
    python inference.py --model gpt-4o           # Use specific model
    python inference.py --randomize              # Randomized initial state
    python inference.py --max-steps 15           # Custom episode length

Environment variables:
    OPENAI_API_KEY   — Required. Your OpenAI API key.
    OPENAI_BASE_URL  — Optional. Custom API base URL.
"""

import os
import sys
import json
import argparse
import asyncio

# Ensure the parent directory is in the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import AsyncOpenAI
from env.sos_env import SOSEnv
from env.actions import ACTIONS
from env.tasks import TASKS
from env.models import Action


# -----------------------------------------------------------------------
# System prompt for the AI agent
# -----------------------------------------------------------------------
SYSTEM_PROMPT = """You are an AI agent optimizing a student's life in a simulation.

You control a student through sequential actions. Your goal is to maximize
their Health, Wisdom, and Wealth scores.

AVAILABLE ACTIONS (choose EXACTLY one per turn):
{actions}

CURRENT TASK: {task_name}
TASK GOAL: {task_description}

SCORING RULES:
- Health (0-100): Based on sleep hours and stress level.
  * Optimal sleep: 7-9 hours. Stress scale: 1 (low) to 10 (high).
  * Formula: 70% sleep quality + 30% stress management.

- Wisdom (0-100): Based on GPA, accuracy, and study hours.
  * Formula: 40% GPA + 35% accuracy + 25% study hours.

- Wealth (0-100): Based on skill development time and GPA.
  * Formula: 80% skill time + 20% GPA bonus.

TRADE-OFFS:
- Studying more increases stress and reduces sleep.
- Taking breaks reduces stress but cuts study/skill time.
- Sleeping more helps health but reduces study time.
- Practicing skills increases stress slightly.

STRATEGY TIPS:
- Start with health fundamentals (sleep, stress reduction).
- Then build academics (study, accuracy).
- Finally optimize wealth (skill development).
- Use "balance_routine" for moderate gains across all areas.

You have {max_steps} steps. Make each one count.

IMPORTANT: Respond with ONLY the action name. No explanation, no quotes,
no extra text. Just the action name exactly as listed above."""


def build_user_message(observation: dict, step: int, max_steps: int) -> str:
    """Build the user message showing the current state to the agent."""
    scores = observation.get("scores", {})
    return (
        f"Step {step}/{max_steps}\n"
        f"\n"
        f"STUDENT STATE:\n"
        f"  Sleep:       {observation['sleep']} hrs/night\n"
        f"  Study Hours: {observation['study_hours']} hrs/day\n"
        f"  Stress:      {observation['stress']}/10\n"
        f"  Accuracy:    {observation['accuracy']}%\n"
        f"  GPA:         {observation['gpa']}\n"
        f"  Skill Time:  {observation['skill_time']} hrs/week\n"
        f"\n"
        f"SCORES:\n"
        f"  Health:  {scores.get('health', 0)}\n"
        f"  Wisdom:  {scores.get('wisdom', 0)}\n"
        f"  Wealth:  {scores.get('wealth', 0)}\n"
        f"  Total:   {scores.get('total', 0)}\n"
        f"\n"
        f"Choose your next action:"
    )


async def run_episode(
    client: AsyncOpenAI,
    model: str,
    task_id: str,
    max_steps: int = None,
    randomize: bool = False,
) -> dict:
    """Run one complete episode for a task using async OpenEnv interface.

    Args:
        client: AsyncOpenAI client instance.
        model: Model name to use.
        task_id: Task identifier.
        max_steps: Max steps per episode (None = use task-specific default).
        randomize: Whether to randomize initial state.

    Returns:
        Episode result dict.
    """
    # OPTIMIZED: Task-specific episode lengths
    if max_steps is None:
        task_steps = {
            "health": 12,
            "balance": 18,  # Increased from 15 (harder task)
            "full_optimization": 25,  # Increased from 20 (hardest task)
        }
        max_steps = task_steps.get(task_id, 15)
    
    task = TASKS[task_id]
    env = SOSEnv(max_steps=max_steps, randomize=randomize, task_id=task_id)

    # Print START log (MANDATORY FORMAT)
    print(f"[START] task={task_id} env=sos model={model}")

    # Reset environment (async)
    obs = await env.reset()
    done = False
    step_num = 0
    rewards = []
    actions_taken = []
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(
                actions="\n".join(f"  - {a}" for a in ACTIONS),
                task_name=task["name"],
                task_description=task["description"],
                max_steps=max_steps,
            ),
        }
    ]

    while not done:
        step_num += 1

        # Build user message with current state (convert Observation to dict)
        obs_dict = obs.model_dump()
        user_msg = build_user_message(obs_dict, step_num, max_steps)
        messages.append({"role": "user", "content": user_msg})

        # Get action from AI (async)
        error = None
        action_name = None
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.0,  # Deterministic for reproducibility
                max_tokens=20,
            )
            raw_action = response.choices[0].message.content.strip().lower()

            # Parse action — handle potential formatting issues
            action_name = None
            for valid_action in ACTIONS:
                if valid_action in raw_action:
                    action_name = valid_action
                    break

            if action_name is None:
                # Fallback: default to balance_routine
                action_name = "balance_routine"
                error = f"unparseable_response:{raw_action[:50]}"

        except Exception as e:
            action_name = "balance_routine"
            error = str(e)[:100]

        # Step the environment (async with typed Action)
        try:
            action_obj = Action(action=action_name)
            obs, reward_obj = await env.step(action_obj)
            
            reward = reward_obj.reward
            done = reward_obj.done
            
            rewards.append(reward)
            actions_taken.append(action_name)

            # Add assistant response to conversation history
            messages.append({"role": "assistant", "content": action_name})

        except Exception as e:
            reward = 0.0
            done = True
            error = str(e)[:100]
            rewards.append(reward)

        # Print STEP log (MANDATORY FORMAT)
        print(
            f"[STEP] step={step_num} "
            f"action={action_name} "
            f"reward={reward:.2f} "
            f"done={'true' if done else 'false'} "
            f"error={error if error else 'null'}"
        )

    # Grade the final state
    score = env.grade(task_id)
    success = score >= 0.8

    # Print END log (MANDATORY FORMAT)
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={'true' if success else 'false'} "
        f"steps={step_num} "
        f"score={score:.2f} "
        f"rewards={rewards_str}"
    )

    # Return summary
    summary = env.episode_summary()
    summary["task"] = task_id
    summary["model"] = model
    summary["success"] = success
    summary["score"] = score
    summary["actions"] = actions_taken
    return summary


async def main():
    parser = argparse.ArgumentParser(
        description="SOS RL Environment — AI Agent Inference"
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        choices=list(TASKS.keys()),
        help="Specific task to run (default: run all tasks)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model name (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Maximum steps per episode (default: task-specific)",
    )
    parser.add_argument(
        "--randomize",
        action="store_true",
        help="Randomize initial student state",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Custom OpenAI API base URL",
    )
    args = parser.parse_args()

    # Initialize AsyncOpenAI client
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is required.")
        sys.exit(1)

    client_kwargs = {"api_key": api_key}
    if args.base_url:
        client_kwargs["base_url"] = args.base_url
    elif os.environ.get("OPENAI_BASE_URL"):
        client_kwargs["base_url"] = os.environ["OPENAI_BASE_URL"]

    client = AsyncOpenAI(**client_kwargs)

    # Determine which tasks to run
    task_ids = [args.task] if args.task else list(TASKS.keys())

    results = []
    for task_id in task_ids:
        print(f"\n{'='*60}")
        print(f"  RUNNING TASK: {TASKS[task_id]['name']}")
        print(f"{'='*60}\n")

        result = await run_episode(
            client=client,
            model=args.model,
            task_id=task_id,
            max_steps=args.max_steps,
            randomize=args.randomize,
        )
        results.append(result)
        print()

    # Print final summary
    print(f"\n{'='*60}")
    print("  FINAL RESULTS SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "✅ PASS" if r["success"] else "❌ FAIL"
        print(
            f"  {status}  {r['task']:25s}  "
            f"score={r['score']:.2f}  "
            f"steps={r['steps']}  "
            f"total_reward={r['total_reward']:.4f}"
        )
    print()


if __name__ == "__main__":
    asyncio.run(main())
