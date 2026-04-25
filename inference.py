# inference.py
# ──────────────────────────────────────────────────────────────
# Mandatory format: [START], [STEP], [END] stdout logs
# Reads credentials from environment variables
# Score normalized to [0, 1] per task
# ──────────────────────────────────────────────────────────────

import os
import json
import requests
from typing import Optional
from openai import OpenAI
from server.graders import grade_task

# ── Credentials from environment variables (MANDATORY) ──────────
# API_BASE_URL = os.getenv("API_BASE_URL", "https://api.featherless.ai/v1")
# MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-7B-Instruct")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.featherless.ai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")
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

SYSTEM_PROMPT = """You are a Mumbai commuter agent. You must pick the best transport mode for each leg of your journey.

You will be given:
- Your current leg (e.g., Leg 1 of 2)
- Time remaining (minutes)
- Budget remaining (₹)
- Weather condition (clear / light_rain / heavy_rain)
- Known disruptions on routes
- Available transport modes with their cost, estimated time, and reliability

Rules to keep in mind:
- In heavy rain, auto-rickshaws are often unavailable or unsafe. Prefer metro or train.
- If a mode is marked unavailable, do not choose it.
- Stay within your budget.
- Prefer faster modes if time is low.
- Metro and train are more reliable in bad weather.
- Walk is slow. Use only last resort.

Respond with ONLY one JSON object on the last line:

{"mode":"metro","reason":"Fastest reliable option within budget"}

mode must be exactly one of:
metro / train / auto / bus / walk
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

def choose_fallback_mode(situation: str) -> str:
    """Heuristic fallback so we do not always collapse to one fixed mode."""
    text = (situation or "").lower()

    if "heavy_rain" in text:
        preferred = ["metro", "train", "bus", "walk"]
    elif "light_rain" in text:
        preferred = ["metro", "bus", "train", "auto", "walk"]
    else:
        preferred = ["metro", "train", "auto", "bus", "walk"]

    for mode in preferred:
        unavailable_markers = [
            f"{mode}: unavailable",
            f"{mode} unavailable",
            f"{mode} - unavailable",
        ]
        if any(marker in text for marker in unavailable_markers):
            continue
        return mode

    return "walk"

def ask_model(client: OpenAI, situation: str, mid_event: str = None) -> dict:
    prompt = situation + "\n\nReturn ONLY a JSON object like {\"mode\":\"metro\",\"reason\":\"brief\"}"
    if mid_event:
        if mid_event:
            prompt = f"MID-JOURNEY EVENT — RE-PLAN:\n{mid_event}\n\n{situation}\n\nReturn ONLY a JSON object like {{\"mode\":\"metro\",\"reason\":\"brief\"}}"

    # Retry logic with exponential backoff: 1s, 2s, 4s
    import time
    max_attempts = 3
    backoff_seconds = [1, 2, 4]
    
    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                max_tokens=80,
                temperature=0.1,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
            )
            raw = response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_attempts - 1:
                wait_time = backoff_seconds[attempt]
                time.sleep(wait_time)
                continue
            else:
                mode = choose_fallback_mode(situation)
                return {
                    "mode": mode,
                    "reason": f"fallback({mode}) after API error: {str(e)[:60]}",
                }

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
            raw_lower = raw.lower()

            for mode in ["metro","train","auto","bus","walk"]:
                if f'"mode":"{mode}"' in raw_lower or f'"mode": "{mode}"' in raw_lower:
                 return {"mode": mode, "reason": "parsed json fragment"}

            for mode in ["metro","train","auto","bus","walk"]:
                if raw_lower.strip() == mode:
                 return {"mode": mode, "reason": "single word"}

            mode = choose_fallback_mode(situation)
            return {"mode": mode, "reason": f"fallback({mode}) parse"}
    
    # Should not reach here
    return {"mode": "bus", "reason": "max_attempts exhausted"}

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

        # Check success: reached final destination
        success = bool(final_obs.get("reached", False))

    except Exception as e:
        error_msg = str(e)[:80]
        log_step(step=steps_taken+1, action="error", reward=0.0, done=True, error=error_msg)

    # Normalize total reward to [0, 1]
    total_reward = sum(rewards)
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
    if not API_KEY:
        raise RuntimeError(
            "No API key found. Set HF_TOKEN or OPENAI_API_KEY or API_KEY before running inference.py"
        )

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    for task_name in TASKS:
        run_task(task_name, TASK_SEEDS[task_name], client)


if __name__ == "__main__":
    main()