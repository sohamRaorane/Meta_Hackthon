# app_demo.py
# Streamlit Before/After demo — run with: streamlit run app_demo.py

import streamlit as st
import requests
import json
import os

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Mumbai Last-Mile Agent Demo",
    page_icon="🚆",
    layout="wide",
)

# ── Prompts ──────────────────────────────────────────────────────

WEAK_PROMPT = """You are a commuter. Pick a transport mode.
Options: metro, train, auto, bus, walk.
Respond ONLY with JSON: {"mode": "your_choice", "reason": "brief"}"""

TRAINED_PROMPT = """You are an expert Mumbai commuter agent navigating a MULTI-LEG journey.

You will be given one leg at a time. Budget and time carry over between legs.

RAIN RULES:
- heavy_rain → NEVER pick auto. Metro first choice.
- light_rain → Prefer metro/train over auto.

DISRUPTION RULES:
- "signal failure" or "delayed" → treat that line as unavailable
- "bus suspended" → no bus
- "auto strike" → no auto
- Confidence below 0.5 → treat as unavailable

BUDGET RULES:
- Never pick mode costing more than budget_remaining
- Budget under ₹20 → only train or bus

TIME RULES:
- Under 25 min remaining → no bus
- Under 30 min with legs left → metro or train only

PRIORITY: metro > train > auto > bus > walk

OUTPUT FORMAT — ONLY THIS JSON:
{"mode": "metro", "reason": "brief explanation"}
mode must be one of: metro / train / auto / bus / walk"""

# ── Helpers ──────────────────────────────────────────────────────

def call_reset(task_name: str, seed: int = 42) -> dict:
    try:
        r = requests.post(
            f"{SERVER_URL}/reset",
            json={"task_name": task_name, "seed": seed},
            timeout=10,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def call_step(episode_id: str, mode: str, reason: str = "") -> dict:
    try:
        msg = json.dumps({"mode": mode, "reason": reason})
        r = requests.post(
            f"{SERVER_URL}/step",
            json={"episode_id": episode_id, "action": {"message": msg}},
            timeout=10,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def parse_mode_from_llm(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    try:
        d = json.loads(raw)
        m = d.get("mode", "").lower()
        if m in {"metro", "train", "auto", "bus", "walk"}:
            return m
    except Exception:
        pass
    for m in ["metro", "train", "auto", "bus", "walk"]:
        if m in raw.lower():
            return m
    return "bus"


def run_demo_episode(task_name: str, seed: int, prompt_type: str):
    """Run one episode, return list of step dicts."""
    steps = []
    reset_data = call_reset(task_name, seed)
    if "error" in reset_data:
        return steps, reset_data["error"]

    obs = reset_data["observation"]
    episode_id = obs["episode_id"]
    done = False
    total_reward = 0.0

    while not done and len(steps) < 8:
        # For demo: we hard-code the choice based on prompt_type
        # In real use: call your HF model here
        situation = obs["echoed_message"]
        weather = obs.get("weather", "clear")
        budget = obs.get("budget_remaining", 100)
        modes = obs.get("available_modes", [])

        # Simulate weak vs trained decision
        if prompt_type == "weak":
            # Weak: picks auto if available, ignores weather/budget
            chosen = "auto"
            for m in modes:
                if m["available"] and m["mode"] == "auto":
                    chosen = "auto"
                    break
            else:
                chosen = "bus"
            reason = "picked auto (no context)"
        else:
            # Trained: respects weather and budget
            chosen = "bus"
            priority = ["metro", "train", "bus", "auto", "walk"]
            if weather == "heavy_rain":
                priority = ["metro", "train", "bus", "walk", "auto"]
            for pref in priority:
                for m in modes:
                    if m["mode"] == pref and m["available"] and m["est_cost"] <= budget:
                        chosen = pref
                        break
                if chosen == pref:
                    break
            reason = f"weather-aware choice: {weather}"

        step_data = call_step(episode_id, chosen, reason)
        if "error" in step_data:
            break

        obs = step_data["observation"]
        reward = float(step_data.get("reward") or 0.0)
        done = bool(step_data.get("done", False))
        total_reward += reward

        steps.append({
            "leg": len(steps) + 1,
            "mode": chosen,
            "reward": reward,
            "location": obs["current_location"],
            "time_left": obs["time_remaining_minutes"],
            "budget_left": obs["budget_remaining"],
            "weather": obs.get("weather", ""),
            "reached": obs.get("reached", False),
        })

    return steps, None


# ── UI ───────────────────────────────────────────────────────────

st.title("🚆 Mumbai Last-Mile Crisis Response")
st.markdown("**GRPO Training Demo — Before vs After**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    task_name = st.selectbox("Task", ["easy", "medium", "hard", "bonus"])
    seed = st.number_input("Seed", value=42, min_value=0, max_value=9999)

    st.markdown("---")
    st.markdown("**Server URL**")
    server_url_input = st.text_input("Server", value=SERVER_URL)
    SERVER_URL = server_url_input

    st.markdown("---")
    st.markdown("**React Map (optional)**")
    react_url = st.text_input("React App URL", placeholder="http://localhost:3000")
    if react_url:
        st.components.v1.iframe(react_url, height=400)

    # Health check
    try:
        h = requests.get(f"{SERVER_URL}/health", timeout=3)
        if h.status_code == 200:
            st.success("✅ Server connected")
        else:
            st.error("❌ Server error")
    except Exception:
        st.error("❌ Server not reachable")

# Main area — two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔴 Before Training (Weak Prompt)")
    st.code(WEAK_PROMPT[:200] + "...", language="text")

with col2:
    st.subheader("🟢 After Training (Smart Prompt)")
    st.code(TRAINED_PROMPT[:200] + "...", language="text")

st.markdown("---")

if st.button("▶ Run Comparison", type="primary"):
    with st.spinner("Running both agents..."):
        weak_steps, weak_err = run_demo_episode(task_name, seed, "weak")
        trained_steps, trained_err = run_demo_episode(task_name, seed, "trained")

    col1, col2 = st.columns(2)

    with col1:
        if weak_err:
            st.error(f"Error: {weak_err}")
        else:
            total_r = sum(s["reward"] for s in weak_steps)
            success = any(s["reached"] for s in weak_steps)
            st.metric("Total Reward", f"{total_r:.3f}")
            st.metric("Success", "✅ YES" if success else "❌ NO")
            for s in weak_steps:
                color = "🟢" if s["reward"] > 0.3 else "🔴"
                st.markdown(
                    f"{color} **Leg {s['leg']}:** `{s['mode']}` "
                    f"→ reward `{s['reward']:.3f}` "
                    f"| ₹{s['budget_left']:.0f} left "
                    f"| {s['time_left']}min left"
                )

    with col2:
        if trained_err:
            st.error(f"Error: {trained_err}")
        else:
            total_r = sum(s["reward"] for s in trained_steps)
            success = any(s["reached"] for s in trained_steps)
            st.metric("Total Reward", f"{total_r:.3f}")
            st.metric("Success", "✅ YES" if success else "❌ NO")
            for s in trained_steps:
                color = "🟢" if s["reward"] > 0.3 else "🔴"
                st.markdown(
                    f"{color} **Leg {s['leg']}:** `{s['mode']}` "
                    f"→ reward `{s['reward']:.3f}` "
                    f"| ₹{s['budget_left']:.0f} left "
                    f"| {s['time_left']}min left"
                )

st.markdown("---")
st.markdown("**Environment:** `eagle25-mumbai-lastmile-env.hf.space`")