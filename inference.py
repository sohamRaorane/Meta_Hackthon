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

# ── Credentials from environment variables (MANDATORY) ──────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.featherless.ai/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-7B-Instruct")
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "rc_cba4823093bb28e6f9d32b4dc41b54976405c30722feadf9baa065fe255d450d")

SERVER_URL   = os.getenv("SERVER_URL", "http://localhost:8000")
BENCHMARK    = "mumbai-lastmile"

# Max possible reward per task (used to normalize score to [0,1])
# Based on reward function: per-leg rewards + destination + buffer + efficiency
# Easy: 2 legs, max ~1.5 per step realistically
# We use a fixed normalization ceiling
MAX_REWARD_PER_TASK = {
    "easy":   2.0,
    "medium": 2.0,
    "hard":   2.5,
    "bonus":  2.0,
}

TASKS = ["easy", "medium", "hard", "bonus"]
TASK_SEEDS = {"easy": 42, "medium": 7, "hard": 13, "bonus": 99}

# ── Mandatory logging functions ──────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    # Sanitize action string — remove newlines, truncate
    action_clean = action.replace("\n", " ").replace("\r", "")[:80]
    error_val    = error if error else "null"
    done_val     = str(done).lower()
    print(
        f"[STEP] step={step} action={action_clean} "
        f"reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.3f} rewards={rewards_str}",
        flush=True,
    )

# ── System Prompt ────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert Mumbai commuter agent navigating a MULTI-LEG journey.

You will be given one leg at a time. Budget and time carry over between legs.

═══════════════════════════════════════════
MULTI-LEG AWARENESS
═══════════════════════════════════════════
You will see: [Leg X of Y] at the top.
- Leg 1 of 3: spend max 40% of budget here
- Leg 2 of 3: keep at least ₹20 for final leg
- Final leg: spend freely

RAIN RULES:
- heavy_rain → NEVER pick auto. Metro first choice.
- heavy_rain → Bus 30-50% slower. Last resort only.
- light_rain → Prefer metro/train over auto.

DISRUPTION RULES:
- "Harbour line delayed" → no train
- "Western line signal failure" → no train, use metro
- "signal failure" → treat train as unavailable
- "bus diverted" or "bus suspended" → no bus
- "auto strike" → no auto
- Confidence below 0.5 → treat as unavailable

BUDGET RULES:
- Never pick mode costing more than budget_remaining
- Budget under ₹20 → only train or bus
- Budget under ₹50 → no auto

TIME RULES:
- Under 15 min → fastest mode only
- Under 25 min → no bus
- Under 30 min with legs remaining → metro or train only

PRIORITY: metro > train > auto > bus > walk

WEIGHTED SCORING (apply mentally):
  time_score   = 1.0 - (est_time_min / time_remaining)
  cost_score   = 1.0 - (est_cost / budget_remaining)
  reliability  = confidence * availability
  total = (time_score*0.4) + (cost_score*0.3) + (reliability*0.3)
  Penalize -0.5 for auto in rain.

MID-JOURNEY REPLAN:
- If event says "Re-plan now": cancel previous plan, pick fresh.

OUTPUT FORMAT — ONLY THIS JSON, NOTHING ELSE:
{"mode": "metro", "reason": "Leg 1 of 2: metro scores highest — 20min, ₹40, confidence 1.0, weather-proof."}

mode must be exactly one of: metro / train / auto / bus / walk
No markdown. No backticks. No extra text.
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
    score        = round(min(max(total_reward / max_reward, 0.0), 1.0), 3)

    log_end(
        success=success,
        steps=steps_taken,
        score=score,
        rewards=rewards,
    )

    return {
        "task_name": task_name,
        "score":     score,
        "steps":     steps_taken,
        "success":   success,
        "rewards":   rewards,
    }

# ── Main ─────────────────────────────────────────────────────────

def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    results = []
    for task_name in TASKS:
        result = run_task(task_name, TASK_SEEDS[task_name], client)
        results.append(result)

    # Human-readable summary (goes to stdout after all tasks)
    print("\n========== FINAL SUMMARY ==========", flush=True)
    for r in results:
        status = "SUCCESS" if r["success"] else "FAIL"
        print(
            f"{r['task_name']:<10} score={r['score']:.3f}  "
            f"steps={r['steps']}  {status}",
            flush=True,
        )
    total = sum(r["score"] for r in results) / len(results)
    print(f"\nAVERAGE SCORE: {total:.3f}", flush=True)
    print("====================================", flush=True)


if __name__ == "__main__":
    main()