import streamlit as st
import requests
import json
import os
from typing import Optional, Dict, Any

# Page config
st.set_page_config(
    page_title="Mumbai Last-Mile Crisis Response",
    page_icon="🚕",
    layout="wide"
)

# Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success { color: #00cc44; font-weight: bold; }
    .error { color: #ff4b4b; font-weight: bold; }
    .info { color: #0099ff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🚕 Mumbai Last-Mile Crisis Response")
st.markdown("""
Navigate through a real-time Mumbai delivery crisis using multi-leg commute strategies.
Your AI agent learns to optimize routes, time, and costs under disruptions.
""")

# Server connection
SERVER_URL = "http://localhost:7860"


def format_available_modes(modes: Any) -> str:
    """Render available modes safely for both string and dict payloads."""
    if not isinstance(modes, list) or not modes:
        return "N/A"

    formatted = []
    for mode in modes:
        if isinstance(mode, str):
            formatted.append(mode)
        elif isinstance(mode, dict):
            mode_name = mode.get("mode", "unknown")
            if mode.get("available", True):
                formatted.append(str(mode_name))
        else:
            formatted.append(str(mode))

    return ", ".join(formatted) if formatted else "N/A"

def check_server_health():
    """Check if server is running"""
    try:
        resp = requests.get(f"{SERVER_URL}/health", timeout=2)
        return resp.status_code == 200
    except:
        return False

# Sidebar controls
st.sidebar.header("⚙️ Controls")

if not check_server_health():
    st.sidebar.error("❌ Server not running on port 7860")
    st.info("Start the server first:\n```\npy -m uvicorn server.app:app --host 0.0.0.0 --port 7860\n```")
    st.stop()

st.sidebar.success("✅ Server connected")

# Task selection
task_name = st.sidebar.selectbox(
    "Select Task",
    ["easy", "medium", "hard", "bonus"],
    help="Choose the difficulty level"
)

task_info = {
    "easy": "🟢 EASY - Andheri East → Kurla (2 legs, clear weather, Rs120)",
    "medium": "🟡 MEDIUM - Borivali → CST (3 legs, heavy rain, Rs80)",
    "hard": "🔴 HARD - Churchgate → BKC (4 legs, cascading failures, Rs75)",
    "bonus": "💎 BONUS - Bandra Station → Juhu Beach (2 legs, tight budget, Rs30)"
}

st.sidebar.markdown(f"**{task_info.get(task_name, '')}**")

# Session state for episode management
if "episode_id" not in st.session_state:
    st.session_state.episode_id = None
if "episode_data" not in st.session_state:
    st.session_state.episode_data = None
if "episode_history" not in st.session_state:
    st.session_state.episode_history = []

# Action buttons
col1, col2, col3 = st.sidebar.columns(3)

reset_button = col1.button("🔄 Reset", use_container_width=True)
step_button = col2.button("⏭️ Step", use_container_width=True)
clear_button = col3.button("🗑️ Clear", use_container_width=True)

if clear_button:
    st.session_state.episode_id = None
    st.session_state.episode_data = None
    st.session_state.episode_history = []
    st.rerun()

# Reset episode
if reset_button:
    try:
        resp = requests.post(
            f"{SERVER_URL}/reset",
            json={"task_name": task_name},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.episode_id = data["observation"]["episode_id"]
            st.session_state.episode_data = data
            st.session_state.episode_history = []
            st.success(f"✅ Episode reset for {task_name} task")
            st.rerun()
        else:
            st.error(f"❌ Reset failed: {resp.status_code}")
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")

# Step episode
if step_button and st.session_state.episode_id:
    try:
        # Get the current observation to pass to the LLM
        current_obs = st.session_state.episode_data["observation"]
        echoed_msg = current_obs.get("echoed_message", "")
        
        # Import and call the ask_model function from inference
        from inference import ask_model, OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        decision = ask_model(client, echoed_msg)
        
        # Use the LLM's decision or fallback to bus
        action = {"message": decision.get("reason", "Take bus")}
        
        resp = requests.post(
            f"{SERVER_URL}/step",
            json={"episode_id": st.session_state.episode_id, "action": action},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.episode_data = data
            
            # Track history
            step_num = len(st.session_state.episode_history) + 1
            st.session_state.episode_history.append({
                "step": step_num,
                "action": action["message"],
                "reward": data.get("reward", 0),
                "done": data.get("done", False),
                "observation": data.get("observation")
            })
            
            st.rerun()
        else:
            st.error(f"❌ Step failed: {resp.status_code}")
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")

# Main display area
if st.session_state.episode_id:
    col1, col2, col3, col4 = st.columns(4)
    
    obs = st.session_state.episode_data.get("observation", {})
    
    with col1:
        st.metric("Episode ID", st.session_state.episode_id[:8] + "...")
    with col2:
        st.metric("Steps", len(st.session_state.episode_history))
    with col3:
        total_reward = sum(h["reward"] for h in st.session_state.episode_history)
        st.metric("Total Reward", f"{total_reward:.3f}")
    with col4:
        is_done = st.session_state.episode_data.get("done", False)
        status = "✅ DONE" if is_done else "🔄 RUNNING"
        st.metric("Status", status)
    
    # Observation details
    st.subheader("📍 Current State")
    obs_col1, obs_col2 = st.columns(2)
    
    with obs_col1:
        st.write("**Location:**", obs.get("current_location", obs.get("location", "Unknown")))
        st.write("**Time Left:**", f"{obs.get('time_remaining_minutes', obs.get('time_left', 0))} mins")
        st.write("**Budget Left:**", f"₹{obs.get('budget_remaining', obs.get('budget_left', 0))}")
    
    with obs_col2:
        st.write("**Weather:**", obs.get("weather", "Unknown"))
        st.write("**Available Modes:**", format_available_modes(obs.get("available_modes", [])))
        if obs.get("mid_journey_update"):
            st.write("**Event:**", obs.get("mid_journey_update"))
    
    # Episode history
    if st.session_state.episode_history:
        st.subheader("📊 Episode History")
        
        for hist_item in st.session_state.episode_history:
            with st.expander(f"Step {hist_item['step']} | Reward: {hist_item['reward']:.3f} | {('✅ Done' if hist_item['done'] else '🔄 Running')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Action:** {hist_item['action']}")
                with col2:
                    st.write(f"**Reward:** {hist_item['reward']:.3f}")
                with col3:
                    st.write(f"**Done:** {hist_item['done']}")
else:
    st.info("👈 Click **Reset** in the sidebar to start an episode")

# Footer
st.divider()
st.caption("🚀 Mumbai Last-Mile Crisis Response Environment | OpenEnv Framework")
