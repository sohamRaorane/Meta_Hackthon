# inference.py
# ──────────────────────────────────────────────────────────────
# Mandatory format: [START], [STEP], [END] stdout logs
# Reads credentials from environment variables
# Score normalized to [0, 1] per task
# ──────────────────────────────────────────────────────────────

import os
import json
import requests
from typing import List, Optional
from openai import OpenAI
from server.graders import grade_task

# ── Credentials from environment variables (MANDATORY) ──────────
# API_BASE_URL = os.getenv("API_BASE_URL", "https://api.featherless.ai/v1")
# MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-7B-Instruct")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.featherless.ai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
API_KEY = HF_TOKEN or os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY", "")

SERVER_URL   = os.getenv("SERVER_URL", "http://localhost:7860")
BENCHMARK    = "mumbai-lastmile"

# Max possible reward per task (used to normalize score to [0,1])
# Based on reward function: per-leg rewards + destination + buffer + efficiency
# Easy: 2 legs, max ~1.5 per step realistically
# We use a fixed normalization ceiling


TASKS = ["easy", "medium", "hard", "bonus"]
TASK_SEEDS = {"easy": 42, "medium": 7, "hard": 13, "bonus": 99}

# ── Mandatory logging functions ──────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float,
             done: bool, error) -> None:
    action_clean = str(action).replace("\n", " ").replace("\r", "")[:80]
    error_val    = error if error else "null"
    done_val     = str(done).lower()
    print(
        f"[STEP] step={step} action={action_clean} "
        f"reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int,
            score: float, rewards: list) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.3f} rewards={rewards_str}",
        flush=True,
    )

# ── System Prompt ────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert Mumbai commuter agent navigating a MULTI-LEG journey.

Before choosing a transport mode, you MUST reason through ALL FOUR sections below.
This structured reasoning is required — do not skip any section.

═══════════════════════════════════════
SECTION 1: SITUATION ASSESSMENT
═══════════════════════════════════════
State the current leg (X of Y), time remaining, budget remaining, and weather.
Example: "Leg 2 of 3. Time: 45min. Budget: ₹40. Weather: heavy_rain."

═══════════════════════════════════════
SECTION 2: ELIMINATION ROUND
═══════════════════════════════════════
List every mode and state whether it is ELIMINATED or VIABLE with one reason.
Example:
  train: ELIMINATED — Western line signal failure confirmed
  auto:  ELIMINATED — heavy_rain + confidence 0.3, availability near zero
  bus:   VIABLE — available, confirmed, ₹15
  metro: VIABLE — weather-proof, confirmed, ₹40 within budget
  walk:  ELIMINATED — 300min, time remaining only 45min

═══════════════════════════════════════
SECTION 3: SCORE THE VIABLE MODES
═══════════════════════════════════════
For each VIABLE mode, compute:
  time_score   = 1.0 - (est_time_min / time_remaining)
  cost_score   = 1.0 - (est_cost / budget_remaining)
  reliability  = confidence value shown
  total = (time_score * 0.4) + (cost_score * 0.3) + (reliability * 0.3)

Show the calculation. Pick the highest total.

═══════════════════════════════════════
SECTION 4: DECISION
═══════════════════════════════════════
State your final choice and the single most important reason.

═══════════════════════════════════════
OUTPUT — AFTER YOUR REASONING, OUTPUT ONLY THIS JSON ON THE LAST LINE:
{"mode": "metro", "reason": "Leg 2 of 3: metro scores 0.87 vs bus 0.52. Weather-proof, within budget."}

mode must be exactly: metro / train / auto / bus / walk
The JSON must be the last line of your response. Nothing after it.
"""

# ── Server calls ─────────────────────────────────────────────────

def call_reset(task_name: str, seed: int) -> dict:
    r = requests.post(
        f"{SERVER_URL}/reset",
        json={"task_name": task_name, "seed": seed},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def call_step(episode_id: str, message: str) -> dict:
    r = requests.post(
        f"{SERVER_URL}/step",
        json={"episode_id": episode_id, "action": {"message": message}},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()

# ── Model call ───────────────────────────────────────────────────

def ask_model(client: OpenAI, situation: str, mid_event: str = None) -> dict:
    prompt = situation
    if mid_event:
        prompt = f"MID-JOURNEY EVENT — RE-PLAN:\n{mid_event}\n\n{situation}"

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=150,
            temperature=0.1,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
        )
        raw = response.choices[0].message.content.strip()
    except Exception as e:
        return {"mode": "bus", "reason": f"API error: {str(e)[:50]}"}

    # Strip markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        decision = json.loads(raw)
        if decision.get("mode") not in ["metro","train","auto","bus","walk"]:
            raise ValueError("invalid mode")
        return decision
    except (json.JSONDecodeError, ValueError):
        for mode in ["metro","train","bus","auto","walk"]:
            if mode in raw.lower():
                return {"mode": mode, "reason": f"parsed from: {raw[:60]}"}
        return {"mode": "bus", "reason": "fallback"}

# ── Task runner ──────────────────────────────────────────────────

def run_task(task_name: str, seed: int, client: OpenAI) -> dict:
    """
    Run one complete task. Returns normalized score in [0, 1].
    Emits mandatory [START], [STEP], [END] log lines.
    """
    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    rewards       = []
    steps_taken   = 0
    success       = False
    pending_event = None
    final_obs     = {}

    try:
        reset_data = call_reset(task_name, seed)
        episode_id = reset_data["observation"]["episode_id"]
        obs        = reset_data["observation"]
        done       = False

        while not done:
            steps_taken += 1

            decision    = ask_model(client, obs["echoed_message"], mid_event=pending_event)
            pending_event = None
            chosen_mode = decision["mode"]
            reason      = decision.get("reason", "")
            action_msg  = f"Take {chosen_mode}. {reason}"

            step_data = call_step(episode_id, action_msg)
            obs       = step_data["observation"]
            final_obs = obs
            reward    = float(step_data.get("reward") or 0.0)
            done      = bool(step_data.get("done", False))
            error     = None

            rewards.append(reward)

            log_step(
                step=steps_taken,
                action=f"Take {chosen_mode}",
                reward=reward,
                done=done,
                error=error,
            )

            # Store mid-journey event for next step
            if obs.get("mid_journey_update"):
                pending_event = obs["mid_journey_update"]

        # Check success: reached destination
        success = obs["current_location"] == obs["destination"]

    except Exception as e:
        error_msg = str(e)[:80]
        log_step(step=steps_taken+1, action="error", reward=0.0, done=True, error=error_msg)

    # Normalize total reward to [0, 1]
    total_reward = sum(rewards)
    max_reward   = MAX_REWARD_PER_TASK.get(task_name, 2.0)
    raw_score = total_reward / max_reward
    score = round(min(max(raw_score, 0.001), 0.999), 3)
    grader_score = grade_task(task_name, final_obs, rewards, steps_taken)

    log_end(
        success=success,
        steps=steps_taken,
        score=grader_score,        # ← grader_score, not raw_score
        rewards=rewards,
    )

    return {
        "task_name":  task_name,
        "score":      grader_score,
        "steps":      steps_taken,
        "success":    success,
        "rewards":    rewards,
    }

# ── Main ─────────────────────────────────────────────────────────

def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    for task_name in TASKS:
        run_task(task_name, TASK_SEEDS[task_name], client)


if __name__ == "__main__":
    main()