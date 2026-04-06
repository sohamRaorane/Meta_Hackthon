import os
import re
import sys
import threading
import time

import requests
import streamlit as st
import uvicorn

# Add server directory to path
sys.path.insert(0, os.path.dirname(__file__))

SERVER_URL = "http://localhost:7861"
SERVER_HEALTH_URL = f"{SERVER_URL}/health"
TASK_SEEDS = {"easy": 42, "medium": 7, "hard": 13, "bonus": 99}
TASK_INFO = {
    "easy": "EASY - Andheri East -> Kurla (2 legs, clear weather, Rs120)",
    "medium": "MEDIUM - Borivali -> CST (3 legs, heavy rain, Rs80)",
    "hard": "HARD - Churchgate -> BKC (4 legs, cascading failures, Rs75)",
    "bonus": "BONUS - Bandra -> Juhu (2 legs, tight Rs30 budget)",
}
MAX_GRADE_BY_TASK = {"easy": 2.0, "medium": 2.0, "hard": 2.5, "bonus": 2.0}


def clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def is_api_server_healthy(timeout: float = 1.0) -> bool:
    try:
        response = requests.get(SERVER_HEALTH_URL, timeout=timeout)
        return response.ok
    except Exception:  # noqa: BLE001
        return False


def start_fastapi() -> None:
    """Run the FastAPI environment server in a background thread."""
    from server.app import app as fastapi_app

    try:
        uvicorn.run(fastapi_app, host="0.0.0.0", port=7861, log_level="error")
    except OSError as exc:
        # Windows can raise WSAEADDRINUSE when another process already owns 7861.
        if getattr(exc, "winerror", None) != 10048:
            raise


def ensure_api_server_started() -> None:
    """Start the backend once for this Streamlit process."""
    if st.session_state.get("api_server_started"):
        return

    if is_api_server_healthy():
        st.session_state.api_server_started = True
        return

    thread = threading.Thread(target=start_fastapi, daemon=True)
    thread.start()

    # Wait briefly for the backend to become ready.
    deadline = time.time() + 3.0
    while time.time() < deadline:
        if is_api_server_healthy(timeout=0.5):
            st.session_state.api_server_started = True
            return
        time.sleep(0.2)

    st.session_state.api_server_started = False
    st.session_state.api_server_error = (
        "Backend API failed to start on port 7861. "
        "If another process is using that port, stop it or restart the app."
    )


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
        json={"episode_id": episode_id, "action": {"message": message}},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def init_ui_state() -> None:
    defaults = {
        "episode_id": None,
        "done": False,
        "step": 0,
        "total_score": 0.0,
        "last_step_score": 0.0,
        "task": "easy",
        "latest_observation": None,
        "last_result": "No action taken yet.",
        "last_error": "",
        "api_server_started": False,
        "api_server_error": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def extract_leg_progress(echoed_message: str) -> tuple[int, int]:
    match = re.search(r"\[Leg\s+(\d+)\s+of\s+(\d+)\]", echoed_message)
    if not match:
        return (0, 0)
    return (int(match.group(1)), int(match.group(2)))


def start_task(task_name: str) -> None:
    try:
        seed = TASK_SEEDS.get(task_name, 42)
        data = call_reset(task_name, seed)
        obs = data["observation"]

        st.session_state.episode_id = obs["episode_id"]
        st.session_state.done = False
        st.session_state.step = 0
        st.session_state.total_score = 0.0
        st.session_state.last_step_score = 0.0
        st.session_state.task = task_name
        st.session_state.latest_observation = obs
        st.session_state.last_result = "Task started. Choose a transport mode to begin."
        st.session_state.last_error = ""
    except Exception as exc:  # noqa: BLE001
        st.session_state.last_error = f"Failed to start task: {exc}"


def take_action(mode: str) -> None:
    if st.session_state.done or st.session_state.episode_id is None:
        st.session_state.last_error = "Start a task before taking an action."
        return

    try:
        st.session_state.step += 1
        action_message = f"Take {mode}. Chosen by user."

        data = call_step(st.session_state.episode_id, action_message)
        obs = data["observation"]
        raw_reward = float(data.get("reward") or 0.0)
        reward = clamp_unit(raw_reward)
        done = bool(data.get("done", False))

        st.session_state.done = done
        st.session_state.last_step_score = reward
        st.session_state.total_score = clamp_unit(st.session_state.total_score + reward)
        st.session_state.latest_observation = obs
        st.session_state.last_error = ""

        result_lines = [
            f"Step {st.session_state.step}: chose {mode.upper()}",
            f"Step score (0-1): {reward:.4f}",
            f"Time left: {obs['time_remaining_minutes']} min | Budget: Rs{obs['budget_remaining']:.0f}",
        ]

        if obs.get("mid_journey_update"):
            result_lines.append(f"Mid-journey update: {obs['mid_journey_update']}")

        if done:
            reached = obs["current_location"] == obs["destination"]
            max_reward = MAX_GRADE_BY_TASK.get(st.session_state.task, 2.0)
            score = clamp_unit(st.session_state.total_score / max_reward)
            status = "DESTINATION REACHED" if reached else "EPISODE ENDED BEFORE DESTINATION"
            result_lines.append(f"Status: {status}")
            result_lines.append(f"Final score (0-1): {score:.3f}")

        st.session_state.last_result = "\n".join(result_lines)
    except Exception as exc:  # noqa: BLE001
        st.session_state.last_error = f"Failed to apply action: {exc}"


def mode_table_rows(available_modes: list[dict]) -> list[dict]:
    ordered_modes = ["metro", "train", "auto", "bus", "walk"]
    modes_by_name = {mode["mode"]: mode for mode in available_modes}
    rows = []

    for mode_name in ordered_modes:
        mode = modes_by_name.get(mode_name)
        if not mode:
            continue
        rows.append(
            {
                "Mode": mode_name.upper(),
                "Status": "AVAILABLE" if mode["available"] else "UNAVAILABLE",
                "Confidence": f"{mode['confidence']:.2f}",
                "Est Cost": f"Rs{mode['est_cost']:.0f}",
                "Est Time": f"{mode['est_time_min']}-{mode['est_time_max']} min",
            }
        )
    return rows


st.set_page_config(page_title="Mumbai Last-Mile Simulator", page_icon="🚇", layout="wide")
init_ui_state()
ensure_api_server_started()

st.title("Mumbai Last-Mile Crisis Response")
st.caption("OpenEnv AI Environment - Multi-Leg Journey Simulator")

with st.sidebar:
    st.subheader("Task Setup")
    selected_task = st.selectbox("Select task", ["easy", "medium", "hard", "bonus"], index=1)
    st.write("Difficulty: easy -> medium -> hard")
    st.markdown("\n".join([f"- {info}" for info in TASK_INFO.values()]))

    if st.button("Start Task", type="primary", use_container_width=True):
        start_task(selected_task)
        st.rerun()

obs = st.session_state.latest_observation

if st.session_state.last_error:
    st.error(st.session_state.last_error)

if st.session_state.api_server_error:
    st.error(st.session_state.api_server_error)

if obs is None:
    st.info("Select a task in the sidebar and click Start Task.")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current", obs["current_location"])
    col2.metric("Destination", obs["destination"])
    col3.metric("Time Remaining", f"{obs['time_remaining_minutes']} min")
    col4.metric("Budget Remaining", f"Rs{obs['budget_remaining']:.0f}")

    progress_current, progress_total = extract_leg_progress(obs["echoed_message"])
    if progress_total > 0:
        completed = max(progress_current - 1, 0)
        st.progress(completed / progress_total, text=f"Journey progress: leg {progress_current} of {progress_total}")

    info_col, score_col = st.columns([2, 1])

    with info_col:
        st.subheader("Current Situation")
        disruptions = obs.get("known_disruptions") or []
        weather = obs.get("weather", "unknown")
        st.write(f"Weather: {weather}")
        st.write(f"Known disruptions: {', '.join(disruptions) if disruptions else 'None'}")

        st.subheader("Transport Options")
        st.table(mode_table_rows(obs["available_modes"]))

    with score_col:
        st.subheader("Step Result")
        st.text(st.session_state.last_result)

        st.subheader("Core Scores")
        st.metric("Current Step Score", f"{st.session_state.last_step_score:.4f}")
        st.metric("Bounded Total Score", f"{st.session_state.total_score:.4f}")

    st.subheader("Choose Transport Mode")
    action_cols = st.columns(5)
    modes = ["metro", "train", "auto", "bus", "walk"]
    labels = ["Metro", "Train", "Auto", "Bus", "Walk"]
    disabled = st.session_state.done or st.session_state.episode_id is None

    for idx, (mode, label) in enumerate(zip(modes, labels)):
        if action_cols[idx].button(label, use_container_width=True, disabled=disabled):
            take_action(mode)
            st.rerun()

    if st.session_state.done:
        reached_destination = obs["current_location"] == obs["destination"]
        if reached_destination:
            st.success("Episode complete: destination reached. Start another task to try a different strategy.")
        else:
            st.warning("Episode complete: destination not reached. Restart and try a different mode sequence.")
