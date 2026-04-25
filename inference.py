# inference.py
import os
import json
import requests
from openai import OpenAI
from server.graders import grade_task

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.featherless.ai/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-1.5B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN")
API_KEY      = HF_TOKEN or os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY", "")
SERVER_URL   = os.getenv("SERVER_URL", "http://localhost:8000")
BENCHMARK    = "mumbai-lastmile"

MAX_REWARD_PER_TASK = {"easy": 2.0, "medium": 2.0, "hard": 2.5, "bonus": 2.0}
TASKS      = ["easy", "medium", "hard", "bonus"]
TASK_SEEDS = {"easy": 42, "medium": 7, "hard": 13, "bonus": 99}

# ── Stripped prompt — Qwen 1.5B can actually follow this ─────────
SYSTEM_PROMPT = """You are a Mumbai commute agent. 
You will be given available transport options with times and costs.
Pick the best option from the list provided.
Respond ONLY with JSON: {"mode": "chosen_mode", "reason": "brief reason"}
mode must be exactly one of: metro, train, auto, bus, walk"""


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error):
    action_clean = str(action).replace("\n", " ")[:80]
    print(f"[STEP] step={step} action={action_clean} reward={reward:.2f} done={str(done).lower()} error={error if error else 'null'}", flush=True)

def log_end(success, steps, score, rewards):
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={','.join(f'{r:.2f}' for r in rewards)}", flush=True)


def call_reset(task_name, seed):
    r = requests.post(f"{SERVER_URL}/reset", json={"task_name": task_name, "seed": seed}, timeout=15)
    r.raise_for_status()
    return r.json()

def call_step(episode_id, message):
    r = requests.post(f"{SERVER_URL}/step", json={"episode_id": episode_id, "action": {"message": message}}, timeout=15)
    r.raise_for_status()
    return r.json()


import re

def parse_available_modes(situation_text: str) -> dict:
    modes_found = {}
    lines = situation_text.split("\n")
    disruption_text = situation_text.lower()
    signal_failure = any(
        phrase in disruption_text
        for phrase in [
            "signal failure",
            "western line signal",
            "harbour line signal",
            "severe delays",
            "line delayed",
        ]
    )
    
    for line in lines:
        stripped = line.strip().lower()
        
        for mode in ["metro", "train", "auto", "bus", "walk"]:
            # Match any of these formats:
            # "  train: available — 15 min, ₹10"
            # "- train: 15 min, ₹10, confidence 0.9"
            # "train (available): ..."
            # "train: NOT available"
            if not (stripped.startswith(mode + ":") or 
                    stripped.startswith("- " + mode + ":") or
                    stripped.startswith("* " + mode + ":")):
                continue
            
            is_available = (
                "not available" not in stripped and
                "unavailable"   not in stripped and
                "no service"    not in stripped and
                "suspended"     not in stripped
            )
            
            cost_match = re.search(r'₹(\d+)', line)
            time_match = re.search(r'(\d+)\s*min', line)
            conf_match = re.search(r'confidence\s*([\d.]+)', line, re.IGNORECASE)
            confidence = float(conf_match.group(1)) if conf_match else 1.0
            if mode == "train" and signal_failure:
                confidence = min(confidence, 0.3)
            
            modes_found[mode] = {
                "available": is_available,
                "cost":      int(cost_match.group(1))   if cost_match else 999,
                "time":      int(time_match.group(1))   if time_match else 999,
                "confidence": confidence,
            }
    
    return modes_found


def build_clean_prompt(situation_text: str, available_modes: dict) -> str:
    budget_match  = re.search(r'Budget[:\s]*₹(\d+)', situation_text)
    time_match    = re.search(r'Time remaining[:\s]*(\d+)\s*min', situation_text)
    weather_match = re.search(r'Weather[:\s]*(\w+)', situation_text)
    leg_match     = re.search(r'\[Leg (\d+) of (\d+)\]', situation_text)

    budget   = int(budget_match.group(1))  if budget_match  else 999
    time_rem = int(time_match.group(1))    if time_match    else 999
    weather  = weather_match.group(1)      if weather_match else "clear"
    leg_info = f"Leg {leg_match.group(1)} of {leg_match.group(2)}" if leg_match else "Journey"

    # Filter to only affordable available modes
    viable = {
        m: i for m, i in available_modes.items()
        if i["available"] and i["cost"] <= budget
    }

    if not viable:
        viable = {"walk": {"cost": 0, "time": 999, "confidence": 1.0}}

    # Prefer modes that are both fast and reliable.
    sorted_modes = sorted(
        viable.items(),
        key=lambda x: x[1]["time"] / max(x[1].get("confidence", 1.0), 0.1),
    )

    # Build numbered list with BEST label on #1
    options_lines = []
    for idx, (mode, info) in enumerate(sorted_modes):
        label = " ← BEST CHOICE" if idx == 0 else ""
        options_lines.append(
            f"  {idx+1}. {mode}: {info['time']} min, ₹{info['cost']}{label}"
        )
    options_str = "\n".join(options_lines)

    best_mode = sorted_modes[0][0]
    best_time = sorted_modes[0][1]["time"]

    warnings = []
    if "heavy" in weather:
        warnings.append("Heavy rain: do not pick auto.")
    if time_rem < 20:
        warnings.append(f"Only {time_rem} min left: pick option 1 immediately.")
    elif time_rem < best_time + 5:
        warnings.append(f"Tight on time: pick option 1 ({best_mode}, {best_time} min).")

    warning_str = "\n".join(warnings)

    prompt = f"""{leg_info} | Weather: {weather} | Time left: {time_rem} min | Budget: ₹{budget}

OPTIONS (sorted fastest first):
{options_str}

{warning_str}

Pick option 1 unless you have a strong reason not to.
Reply ONLY with JSON: {{"mode": "{best_mode}", "reason": "one line reason"}}"""

    return prompt


def ask_model(client, situation, mid_event=None, failed_modes=None):
    if failed_modes is None:
        failed_modes = []

    available_modes = parse_available_modes(situation)

    for mode in failed_modes:
        if mode in available_modes:
            available_modes[mode]["available"] = False
    
    
    # Build prompt — always assign before use
    if available_modes:
        prompt = build_clean_prompt(situation, available_modes)
    else:
        prompt = situation + "\n\nReply ONLY with JSON: {\"mode\": \"...\", \"reason\": \"...\"}"

    if failed_modes:
        prompt += f"\n\nDO NOT retry: {', '.join(failed_modes)} - already failed this leg."
    
  
    
    if mid_event:
        prompt = f"MID-JOURNEY ALERT: {mid_event}\n\n" + prompt
    
    # rest of function continues...

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=80,
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
        )
        raw = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  [API ERROR] {type(e).__name__}: {str(e)[:120]}", flush=True)
        # Pick cheapest available mode as fallback
        cheapest = min(
            [(m, i) for m, i in available_modes.items() if i["available"]],
            key=lambda x: x[1]["cost"],
            default=(None, None)
        )
        fallback_mode = cheapest[0] if cheapest[0] else "bus"
        return {"mode": fallback_mode, "reason": "API error fallback"}

    # Strip markdown fences
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else parts[0]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        decision = json.loads(raw)
        mode = decision.get("mode", "").lower().strip()
        if mode not in ["metro", "train", "auto", "bus", "walk"]:
            raise ValueError(f"invalid mode: {mode}")
        
        # Validate against parsed availability — hard block if mode not available
        if available_modes and mode in available_modes and not available_modes[mode]["available"]:
            # Find best available alternative
            available = {m: i for m, i in available_modes.items() if i["available"] and i["cost"] <= 999}
            if available:
                best = min(available.items(), key=lambda x: x[1]["time"])
                print(f"  [BLOCK] {mode} not available → using {best[0]}", flush=True)
                decision["mode"] = best[0]
                decision["reason"] = f"switched from unavailable {mode}"
        
        return decision

    except (json.JSONDecodeError, ValueError):
        # Word scan fallback — prefer available modes
        for mode in ["metro", "train", "auto", "bus", "walk"]:
            if mode in raw.lower():
                if not available_modes or available_modes.get(mode, {}).get("available", True):
                    return {"mode": mode, "reason": "parsed from raw"}
        print(f"  [PARSE FAIL] raw: {raw[:100]}", flush=True)
        # Pick fastest available
        if available_modes:
            available = {m: i for m, i in available_modes.items() if i["available"]}
            if available:
                best = min(available.items(), key=lambda x: x[1]["time"])
                return {"mode": best[0], "reason": "parse fallback — fastest available"}
        return {"mode": "bus", "reason": "hard fallback"}

def run_task(task_name, seed, client):
    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    rewards, steps_taken, success, pending_event, final_obs = [], 0, False, None, {}
    failed_modes_this_leg = []
    last_leg_number = None

    try:
        reset_data = call_reset(task_name, seed)
        episode_id = reset_data["observation"]["episode_id"]
        obs        = reset_data["observation"]
        done       = False

        while not done:
            steps_taken += 1

            leg_match = re.search(r'\[Leg (\d+) of \d+\]', obs["echoed_message"])
            current_leg = int(leg_match.group(1)) if leg_match else 0
            if current_leg != last_leg_number:
                failed_modes_this_leg = []
                last_leg_number = current_leg

            decision    = ask_model(
                client,
                obs["echoed_message"],
                mid_event=pending_event,
                failed_modes=failed_modes_this_leg,
            )
            pending_event = None
            chosen_mode = decision["mode"]
            reason      = decision.get("reason", "")
            action_msg  = f"Take {chosen_mode}. {reason}"

            step_data = call_step(episode_id, action_msg)
            obs       = step_data["observation"]
            final_obs = obs
            reward    = float(step_data.get("reward") or 0.0)
            done      = bool(step_data.get("done", False))

            if reward < 0 and chosen_mode not in failed_modes_this_leg:
                failed_modes_this_leg.append(chosen_mode)
                print(
                    f"  [FAILED] {chosen_mode} gave negative reward, excluding from next attempt",
                    flush=True,
                )

            rewards.append(reward)
            log_step(step=steps_taken, action=f"Take {chosen_mode}", reward=reward, done=done, error=None)

            if obs.get("mid_journey_update"):
                pending_event = obs["mid_journey_update"]

        success = bool(obs.get("reached", False)) or (obs.get("current_location") == obs.get("destination"))

    except Exception as e:
        error_msg = str(e)[:80]
        log_step(step=steps_taken+1, action="error", reward=0.0, done=True, error=error_msg)

    total_reward = sum(rewards)
    max_reward   = MAX_REWARD_PER_TASK.get(task_name, 2.0)
    score = round(min(max(total_reward / max_reward, 0.001), 0.999), 3)
    grader_score = grade_task(task_name, final_obs, rewards, steps_taken)

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return {"task_name": task_name, "score": score, "steps": steps_taken,
            "success": success, "rewards": rewards, "grader_score": grader_score}


def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    for task_name in TASKS:
        run_task(task_name, TASK_SEEDS[task_name], client)

if __name__ == "__main__":
    main()