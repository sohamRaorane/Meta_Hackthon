import os
import json
import re
import requests
from openai import OpenAI
from server.graders import grade_task

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.featherless.ai/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-1.5B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN")
API_KEY      = HF_TOKEN or os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY", "")
SERVER_URL   = os.getenv("SERVER_URL", "http://localhost:8000")
BENCHMARK    = "mumbai-lastmile"
API_DISABLED_REASON = None

MAX_REWARD_PER_TASK = {"easy": 2.0, "medium": 2.0, "hard": 2.5, "bonus": 2.0}
TASKS      = ["easy", "medium", "hard", "bonus"]
TASK_SEEDS = {"easy": 42, "medium": 7, "hard": 13, "bonus": 99}

# Minimum cost per leg for each task (train is always cheapest at ₹10-15)
# Used to estimate how much budget must be reserved for future legs
MIN_LEG_COST = 10  # train is ₹10 on almost every corridor

SYSTEM_PROMPT = """You are a Mumbai commute agent.
You will be given available transport options with times and costs.
Your budget must last ALL remaining legs of the journey.
Pick the best affordable option from the list provided.
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
    leg_num  = int(leg_match.group(1))     if leg_match     else 1
    leg_total = int(leg_match.group(2))    if leg_match     else 1
    leg_info = f"Leg {leg_num} of {leg_total}" if leg_match else "Journey"

    # Calculate minimum budget needed for FUTURE legs (reserve for them)
    future_legs = leg_total - leg_num  # legs after this one
    min_future_reserve = future_legs * MIN_LEG_COST
    effective_budget = budget - min_future_reserve  # what we can spend NOW

    # Filter: only modes that are available AND affordable NOW (respecting future reserve)
    viable = {
        m: i for m, i in available_modes.items()
        if i["available"] and i["cost"] <= max(effective_budget, 0)
    }

    # If nothing viable with reserve, fall back to modes affordable within full budget
    if not viable:
        viable = {
            m: i for m, i in available_modes.items()
            if i["available"] and i["cost"] <= budget
        }

    # Last resort
    if not viable:
        viable = {"walk": {"cost": 0, "time": 999, "confidence": 1.0}}

    # Sort by time / confidence (fastest reliable option first)
    sorted_modes = sorted(
        viable.items(),
        key=lambda x: x[1]["time"] / max(x[1].get("confidence", 1.0), 0.1),
    )

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
    if future_legs > 0:
        warnings.append(f"You have {future_legs} more leg(s) after this. Budget reserve: ₹{min_future_reserve} kept.")
    if time_rem < 20:
        warnings.append(f"Only {time_rem} min left: pick option 1 immediately.")
    elif time_rem < best_time + 5:
        warnings.append(f"Tight on time: pick option 1 ({best_mode}, {best_time} min).")

    warning_str = "\n".join(warnings)

    prompt = f"""{leg_info} | Weather: {weather} | Time left: {time_rem} min | Budget left: ₹{budget} (can spend ₹{effective_budget} now)

OPTIONS (sorted fastest first, all within affordable range):
{options_str}

{warning_str}

Pick option 1 unless you have a strong reason not to.
Reply ONLY with JSON: {{"mode": "{best_mode}", "reason": "one line reason"}}"""

    return prompt


def pick_fallback_mode(available_modes: dict, situation_text: str = "") -> str:
    candidates = [
        (mode, info) for mode, info in available_modes.items()
        if info.get("available", False)
    ]
    if not candidates:
        return "bus"

    weather_heavy = "heavy" in situation_text.lower()
    non_walk = [(m, i) for (m, i) in candidates if m != "walk"]
    pool = non_walk if non_walk else candidates

    # Prefer affordable, reliable, practical transport in fallback mode.
    # Avoid auto in heavy rain unless there is no better option.
    def rank(item):
        mode, info = item
        rain_penalty = 1000 if (weather_heavy and mode == "auto") else 0
        return (
            rain_penalty,
            info.get("cost", 999),
            info.get("time", 999) / max(info.get("confidence", 1.0), 0.1),
        )

    best_mode, _ = min(pool, key=rank)
    return best_mode


def ask_model(client, situation, mid_event=None, failed_modes=None):
    global API_DISABLED_REASON

    if failed_modes is None:
        failed_modes = []

    available_modes = parse_available_modes(situation)

    for mode in failed_modes:
        if mode in available_modes:
            available_modes[mode]["available"] = False

    if available_modes:
        prompt = build_clean_prompt(situation, available_modes)
    else:
        prompt = situation + "\n\nReply ONLY with JSON: {\"mode\": \"...\", \"reason\": \"...\"}"

    if failed_modes:
        prompt += f"\n\nDO NOT retry: {', '.join(failed_modes)} - already failed this leg."

    if mid_event:
        prompt = f"MID-JOURNEY ALERT: {mid_event}\n\n" + prompt

    if API_DISABLED_REASON is not None:
        fallback_mode = pick_fallback_mode(available_modes, situation)
        return {"mode": fallback_mode, "reason": API_DISABLED_REASON}

    if not API_KEY:
        API_DISABLED_REASON = "missing API credentials fallback"
        print("  [CONFIG] Missing API key (HF_TOKEN/OPENAI_API_KEY/API_KEY). Using local fallback.", flush=True)
        fallback_mode = pick_fallback_mode(available_modes, situation)
        return {"mode": fallback_mode, "reason": API_DISABLED_REASON}

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
        if os.getenv("DEBUG_MODEL_RAW") == "1":
            print(f"  [RAW] {raw}", flush=True)
    except Exception as e:
        print(f"  [API ERROR] {type(e).__name__}: {str(e)[:120]}", flush=True)
        if "AuthenticationError" in type(e).__name__ or "401" in str(e):
            API_DISABLED_REASON = "API authentication failed fallback"
            print("  [CONFIG] Disabling remote LLM calls after auth failure; using local fallback.", flush=True)
        if "NotFoundError" in type(e).__name__ or "404" in str(e):
            API_DISABLED_REASON = "model not found fallback"
            print(
                "  [CONFIG] Disabling remote LLM calls after model-not-found error; using local fallback.",
                flush=True,
            )
        fallback_mode = pick_fallback_mode(available_modes, situation)
        return {"mode": fallback_mode, "reason": "API error fallback"}

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

        if available_modes and mode in available_modes and not available_modes[mode]["available"]:
            available = {m: i for m, i in available_modes.items() if i["available"] and i["cost"] <= 999}
            if available:
                best = min(available.items(), key=lambda x: x[1]["time"])
                print(f"  [BLOCK] {mode} not available → using {best[0]}", flush=True)
                decision["mode"] = best[0]
                decision["reason"] = f"switched from unavailable {mode}"

        return decision

    except (json.JSONDecodeError, ValueError):
        for mode in ["metro", "train", "auto", "bus", "walk"]:
            if mode in raw.lower():
                if not available_modes or available_modes.get(mode, {}).get("available", True):
                    return {"mode": mode, "reason": "parsed from raw"}
        print(f"  [PARSE FAIL] raw: {raw[:100]}", flush=True)
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

    grader_score = grade_task(task_name, final_obs, rewards, steps_taken)
    score = round(grader_score, 3)

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return {"task_name": task_name, "score": score, "steps": steps_taken,
            "success": success, "rewards": rewards, "grader_score": grader_score}


def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    for task_name in TASKS:
        run_task(task_name, TASK_SEEDS[task_name], client)

if __name__ == "__main__":
    main()
