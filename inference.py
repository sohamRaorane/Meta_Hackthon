# inference.py
# ──────────────────────────────────────────────────────────────
# AI agent using Featherless.ai (OpenAI-compatible API)
# Model: Qwen/Qwen2.5-7B-Instruct (free credits)
# ──────────────────────────────────────────────────────────────

import json
import requests
from openai import OpenAI

# ── Configuration ───────────────────────────────────────────────

SERVER_URL = "http://localhost:8000"

# Featherless.ai client — uses OpenAI-compatible format
client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key="rc_cba4823093bb28e6f9d32b4dc41b54976405c30722feadf9baa065fe255d450d",
)

MODEL = "Qwen/Qwen2.5-7B-Instruct"

TASKS = ["easy", "medium", "hard"]

# ── System Prompt ───────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert Mumbai commuter agent with deep knowledge of Mumbai's local transport system.

Your job is to read the current situation and pick the single best transport mode to reach the destination.

═══════════════════════════════════════════
PART 1 — WHO YOU ARE
═══════════════════════════════════════════
You are not a generic travel assistant. You are someone who has lived in Mumbai for 10 years and knows exactly how the transport system behaves in every condition — rain, signal failures, peak hours, and mid-journey disruptions.

You know things that no app tells you:
- Autos vanish in Mumbai rain. They either refuse or charge 3x.
- The Harbour line has the most frequent signal failures.
- Western line signal failure stops fast trains.
- BEST bus ETAs can be off by ±15 minutes.
- Metro Line 1 is weather-proof.
- Walking >1 km in rain is not practical.

═══════════════════════════════════════════
PART 2 — RULES
═══════════════════════════════════════════

RAIN RULES:
- heavy_rain → NEVER auto
- heavy_rain → metro first, train second
- light_rain → prefer metro/train
- clear → all allowed

TRAIN RULES:
- signal failure → no train
- Harbour delay → no train
- unavailable → no train

METRO:
- Always first choice if affordable

AUTO:
- Never in heavy rain
- Only if budget > ₹50 and confidence > 0.5

BUS:
- Last option before walk

WALK:
- Only last resort

TIME:
- <25 min → no bus
- <15 min → fastest only

═══════════════════════════════════════════
OUTPUT FORMAT (STRICT)
═══════════════════════════════════════════
{"mode": "metro", "reason": "mention reason clearly"}
"""

# ── Helper Functions ─────────────────────────────────────────────


def call_reset(task_name: str, seed: int) -> dict:
    response = requests.post(
        f"{SERVER_URL}/reset",
        json={"task_name": task_name, "seed": seed},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def call_step(episode_id: str, message: str) -> dict:
    response = requests.post(
        f"{SERVER_URL}/step",
        json={
            "episode_id": episode_id,
            "action": {"message": message},
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def ask_model(situation_text: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=150,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": situation_text},
        ],
    )

    raw_text = response.choices[0].message.content.strip()

    # Remove markdown if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        decision = json.loads(raw_text)
        valid_modes = ["metro", "train", "auto", "bus", "walk"]

        if decision.get("mode") not in valid_modes:
            raise ValueError("Invalid mode")

    except Exception:
        print(f"[Warning] Bad response: {raw_text}")

        # fallback extraction
        for mode in ["metro", "train", "bus", "auto", "walk"]:
            if mode in raw_text.lower():
                decision = {
                    "mode": mode,
                    "reason": f"Extracted from: {raw_text[:80]}"
                }
                break
        else:
            decision = {
                "mode": "bus",
                "reason": "Fallback response"
            }

    return decision


def run_task(task_name: str, seed: int) -> dict:
    print(f"\n{'='*50}")
    print(f"TASK: {task_name.upper()}")
    print(f"{'='*50}")

    reset_data = call_reset(task_name, seed)
    episode_id = reset_data["observation"]["episode_id"]
    obs = reset_data["observation"]

    total_reward = 0
    steps = 0
    reached = False
    done = False

    while not done:
        steps += 1

        print(f"\n--- Step {steps} ---")
        print(obs["echoed_message"])

        decision = ask_model(obs["echoed_message"])
        mode = decision["mode"]
        reason = decision["reason"]

        print(f"Decision: {mode} | {reason}")

        action_message = f"Take {mode}. {reason}"

        step_data = call_step(episode_id, action_message)

        obs = step_data["observation"]
        reward = step_data.get("reward", 0)
        done = step_data.get("done", False)

        total_reward += reward

        if obs["current_location"] == obs["destination"] and done:
            reached = True

    print(f"\nResult: {'Reached' if reached else 'Failed'}")
    print(f"Reward: {total_reward}")
    print(f"Steps: {steps}")

    return {
        "task": task_name,
        "reward": total_reward,
        "steps": steps,
        "reached": reached,
    }


def main():
    print("Mumbai Transport AI Agent")

    seeds = {"easy": 42, "medium": 7, "hard": 13}

    results = []

    for task in TASKS:
        results.append(run_task(task, seeds[task]))

    print("\nFINAL SUMMARY")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()