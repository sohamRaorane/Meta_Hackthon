import streamlit as st
import requests
import json
import time
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mumbai LastMile · RL Agent",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state ─────────────────────────────────────────────────────────────
if "result"      not in st.session_state: st.session_state.result      = None
if "thinking"    not in st.session_state: st.session_state.thinking    = False
if "theme"       not in st.session_state: st.session_state.theme       = "dark"
if "api_url"     not in st.session_state: st.session_state.api_url     = "http://localhost:8000"
if "fastapi_url" not in st.session_state: st.session_state.fastapi_url = "http://localhost:8000/docs"

# ── Theme CSS ─────────────────────────────────────────────────────────────────
if st.session_state.theme == "light":
    st.markdown("""
    <style>
    :root {
        --bg:        #f8fafc;
        --surface:   #ffffff;
        --surface2:  #f1f5f9;
        --border:    #cbd5e1;
        --accent:    #ea580c;
        --accent2:   #0ea5e9;
        --green:     #16a34a;
        --red:       #dc2626;
        --yellow:    #d97706;
        --text:      #0f172a;
        --muted:     #475569;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    :root {
        --bg:        #0a0e17;
        --surface:   #111827;
        --surface2:  #1a2236;
        --border:    #1f2d45;
        --accent:    #f97316;
        --accent2:   #38bdf8;
        --green:     #22c55e;
        --red:       #ef4444;
        --yellow:    #facc15;
        --text:      #e2e8f0;
        --muted:     #64748b;
    }
    </style>
    """, unsafe_allow_html=True)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

:root {
    --font-logo: 'Syne', sans-serif;
    --font-head: 'Plus Jakarta Sans', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --font-body: 'Inter', sans-serif;
}

/* ── global reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: var(--font-body);
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--surface) !important; }
.block-container { padding: 0 2rem 4rem !important; max-width: 1400px !important; }

/* ── topbar ── */
.topbar {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -2rem 2rem -2rem;
    position: sticky; top: 0; z-index: 100;
}
.topbar-title {
    font-family: var(--font-logo);
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: var(--text);
}
.topbar-title span { color: var(--accent); }
.badge {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.25rem 0.75rem;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--accent2);
    letter-spacing: 0.05em;
}

/* ── section labels ── */
.section-label {
    font-family: var(--font-head);
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.section-label::after {
    content: ''; flex: 1;
    height: 1px; background: var(--border);
}

/* ── input card ── */
.input-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

/* ── streamlit input overrides ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] select {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(249,115,22,0.15) !important;
}
label[data-testid="stWidgetLabel"] p {
    font-family: var(--font-head) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ── submit button ── */
[data-testid="stButton"] > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--font-head) !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.65rem 2rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}
[data-testid="stButton"] > button:hover {
    background: #ea6c0a !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(249,115,22,0.35) !important;
}

/* ── decision panel ── */
.decision-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    min-height: 220px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.decision-panel::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.decision-empty {
    display: flex; align-items: center; justify-content: center;
    height: 160px;
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 0.8rem;
    letter-spacing: 0.05em;
    flex-direction: column; gap: 0.5rem;
}

/* ── mode chip ── */
.mode-chip {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    font-weight: 500;
    margin: 0.2rem;
    border: 1px solid;
}
.chip-metro  { background: rgba(56,189,248,0.12); color: #38bdf8; border-color: rgba(56,189,248,0.3); }
.chip-train  { background: rgba(34,197,94,0.12);  color: #22c55e; border-color: rgba(34,197,94,0.3);  }
.chip-auto   { background: rgba(250,204,21,0.12); color: #facc15; border-color: rgba(250,204,21,0.3); }
.chip-bus    { background: rgba(167,139,250,0.12);color: #a78bfa; border-color: rgba(167,139,250,0.3);}
.chip-walk   { background: rgba(251,146,60,0.12); color: #fb923c; border-color: rgba(251,146,60,0.3); }

/* ── result row ── */
.result-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.88rem;
}
.result-row:last-child { border-bottom: none; }
.result-label { color: var(--muted); font-family: var(--font-head); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }
.result-val   { font-family: var(--font-mono); font-weight: 500; }
.val-green { color: var(--green); }
.val-red   { color: var(--red);   }
.val-yellow{ color: var(--yellow);}
.val-blue  { color: var(--accent2);}

/* ── stats cards (pre/post) ── */
.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative; overflow: hidden;
}
.stat-card-pre  { border-top: 2px solid var(--red);    }
.stat-card-post { border-top: 2px solid var(--green);  }
.stat-card-title {
    font-family: var(--font-head);
    font-size: 0.8rem; font-weight: 700;
    letter-spacing: 0.06em; text-transform: uppercase;
    margin-bottom: 1rem;
}
.stat-card-pre  .stat-card-title { color: var(--red);   }
.stat-card-post .stat-card-title { color: var(--green); }
.stat-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.35rem 0;
    font-size: 0.82rem;
    border-bottom: 1px solid var(--border);
}
.stat-row:last-child { border-bottom: none; }
.stat-task { color: var(--muted); font-family: var(--font-head); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }
.stat-val  { font-family: var(--font-mono); font-size: 0.78rem; }

/* ── fastapi bar ── */
.fastapi-bar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.85rem 1.25rem;
    display: flex; align-items: center; gap: 1rem;
    margin-top: 1rem;
}
.fastapi-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    flex-shrink: 0;
}
.fastapi-label {
    font-family: var(--font-head);
    font-weight: 700;
    font-size: 0.75rem; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.1em;
    flex-shrink: 0;
}
.fastapi-link {
    font-family: var(--font-mono);
    font-size: 0.8rem; color: var(--accent2);
    text-decoration: none; flex: 1;
    word-break: break-all;
}
.fastapi-link:hover { color: #7dd3fc; text-decoration: underline; }

/* ── weather pill ── */
.weather-badge {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    font-family: var(--font-mono);
    font-size: 0.68rem;
    font-weight: 500;
}
.w-heavy_rain { background: rgba(56,189,248,0.15); color: #38bdf8; }
.w-light_rain { background: rgba(167,139,250,0.15); color: #a78bfa; }
.w-no_rain    { background: rgba(34,197,94,0.15);  color: #22c55e; }

/* ── thinking animation ── */
@keyframes blink {
    0%, 100% { opacity: 1; } 50% { opacity: 0.2; }
}
.thinking-dot {
    display: inline-block; width: 6px; height: 6px;
    border-radius: 50%; background: var(--accent);
    margin: 0 2px; animation: blink 1.2s infinite;
}
.thinking-dot:nth-child(2) { animation-delay: 0.2s; }
.thinking-dot:nth-child(3) { animation-delay: 0.4s; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* ── misc ── */
.divider { height: 1px; background: var(--border); margin: 1.5rem 0; }
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)



# ── Mock API call (replace with real endpoint) ────────────────────────────────
def call_agent_api(source, destination, time_limit, cost, task_difficulty):
    """
    Calls the FastAPI backend. Replace api_url with your actual endpoint.
    Expected POST /step with observation payload.
    Returns dict with mode, reason, reward, success, weather, steps.
    """
    api_url = st.session_state.api_url

    # Build the observation payload matching the env schema
    payload = {
        "source":      source,
        "destination": destination,
        "time_limit":  time_limit,
        "budget":      cost,
        "task":        task_difficulty,
    }

    try:
        resp = requests.post(f"{api_url}/predict", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {
            "error": "Backend API not reachable. Start FastAPI on port 8000 or update Backend API URL in settings."
        }
    except requests.exceptions.HTTPError as e:
        return {
            "error": f"Backend API request failed: {e}"
        }
    except Exception as e:
        return {"error": str(e)}

TASK_ORDER = ["easy", "medium", "hard", "bonus"]


@st.cache_data(show_spinner=False)
def load_training_results():
    """Load baseline and post-training metrics from project log files."""
    results_dir = Path(__file__).resolve().parent / "results"
    baseline_path = results_dir / "baseline_results.json"
    post_path = results_dir / "post_training_results.json"

    errors = []
    pre_results = {}
    post_results = {}

    try:
        with baseline_path.open("r", encoding="utf-8") as f:
            baseline_data = json.load(f)
        for row in baseline_data.get("tasks", []):
            task = str(row.get("task_name", "")).lower()
            if task:
                pre_results[task] = {
                    "mean_reward": float(row.get("mean_total_reward", 0.0)),
                    "success_rate": float(row.get("success_rate", 0.0)),
                }
    except Exception as e:
        errors.append(f"Failed loading baseline logs: {e}")

    try:
        with post_path.open("r", encoding="utf-8") as f:
            post_data = json.load(f)
        for row in post_data.get("tasks", []):
            task = str(row.get("task_name", "")).lower()
            if not task:
                continue

            reward_val = row.get("mean_total_reward", row.get("total_reward", 0.0))
            success_val = row.get("success_rate", row.get("success", 0.0))
            if isinstance(success_val, bool):
                success_rate = 1.0 if success_val else 0.0
            else:
                success_rate = float(success_val)

            post_results[task] = {
                "mean_reward": float(reward_val),
                "success_rate": success_rate,
            }
    except Exception as e:
        errors.append(f"Failed loading post-training logs: {e}")

    return pre_results, post_results, errors

MODE_ICONS = {
    "metro": "🚇", "train": "🚆", "auto": "🛺",
    "bus": "🚌", "walk": "🚶",
}
WEATHER_ICONS = {"no_rain": "☀️", "light_rain": "🌦️", "heavy_rain": "⛈️"}

# ═══════════════════════════════════════════════════════════════════════════════
# TOPBAR
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="topbar">
  <div class="topbar-title">Mumbai <span>LastMile</span> · RL Agent</div>
  <div style="display:flex;gap:0.5rem;align-items:center;">
    <span class="badge">GRPO · 3-Phase Training</span>
    <span class="badge">Unsloth · Qwen-1.5B</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SETTINGS ROW  (API URL + FastAPI docs URL)
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("⚙️  API Settings & Theme", expanded=False):
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        st.session_state.api_url = st.text_input(
            "Backend API URL",
            value=st.session_state.api_url,
            placeholder="http://localhost:8000",
        )
    with c2:
        st.session_state.fastapi_url = st.text_input(
            "FastAPI Docs URL",
            value=st.session_state.fastapi_url,
            placeholder="http://localhost:8000/docs",
        )
    with c3:
        st.markdown("<div style='margin-bottom: 1.7rem;'></div>", unsafe_allow_html=True)
        is_light = st.toggle("Light Mode", value=st.session_state.theme == "light")
        new_theme = "light" if is_light else "dark"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LAYOUT: left (inputs + decisions) | right (results + viz)
# ═══════════════════════════════════════════════════════════════════════════════
left_col, right_col = st.columns([1.05, 0.95], gap="large")

# ── LEFT COLUMN ───────────────────────────────────────────────────────────────
with left_col:

    # ── Journey Inputs ───────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Journey Parameters</div>', unsafe_allow_html=True)
    st.markdown('<div class="input-card">', unsafe_allow_html=True)

    row1_a, arr, row1_b = st.columns([2, 0.3, 2])
    with row1_a:
        source = st.text_input("Source", placeholder="e.g. Andheri", label_visibility="visible")
    with arr:
        st.markdown("<div style='padding-top:1.85rem;text-align:center;font-size:1.3rem;color:#f97316'>→</div>", unsafe_allow_html=True)
    with row1_b:
        destination = st.text_input("Destination", placeholder="e.g. Churchgate", label_visibility="visible")

    row2_a, row2_b, row2_c = st.columns(3)
    with row2_a:
        time_limit = st.number_input("Time Limit (min)", min_value=5, max_value=180, value=45, step=5)
    with row2_b:
        cost = st.number_input("Budget (₹)", min_value=5, max_value=500, value=60, step=5)
    with row2_c:
        task_difficulty = st.selectbox("Task Difficulty", ["easy", "medium", "hard", "bonus"])

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Submit ───────────────────────────────────────────────────────────────
    submit = st.button("🚀  Run Agent", use_container_width=True)

    if submit:
        if not source.strip() or not destination.strip():
            st.warning("Please enter both Source and Destination.")
        else:
            st.session_state.thinking = True
            st.session_state.result   = None

    # Run API call
    if st.session_state.thinking and st.session_state.result is None:
        with st.spinner(""):
            st.markdown("""
            <div style="text-align:center;padding:0.5rem;color:#64748b;
                        font-family:'IBM Plex Mono',monospace;font-size:0.8rem;">
                Agent thinking
                <span class="thinking-dot"></span>
                <span class="thinking-dot"></span>
                <span class="thinking-dot"></span>
            </div>""", unsafe_allow_html=True)
            time.sleep(0.8)  # slight delay for UX feel
            result = call_agent_api(source, destination, time_limit, cost, task_difficulty)
            st.session_state.result   = result
            st.session_state.thinking = False
            st.rerun()

    # ── Agent Decision Panel ─────────────────────────────────────────────────
    st.markdown('<div class="section-label" style="margin-top:1.5rem">Agent Decisions</div>', unsafe_allow_html=True)
    st.markdown('<div class="decision-panel">', unsafe_allow_html=True)

    res = st.session_state.result

    if res is None:
        st.markdown("""
        <div class="decision-empty">
            <span style="font-size:2rem">🚇</span>
            <span>Awaiting journey parameters…</span>
        </div>""", unsafe_allow_html=True)

    elif "error" in res:
        st.markdown(f"""
        <div class="decision-empty">
            <span style="font-size:1.5rem">⚠️</span>
            <span style="color:#ef4444">{res['error']}</span>
        </div>""", unsafe_allow_html=True)

    else:
        mode    = res.get("mode", "metro")
        reason  = res.get("reason", "—")
        weather = res.get("weather", "no_rain")
        reward  = res.get("reward", 0)
        success = res.get("success", False)
        steps   = res.get("steps", 1)
        budget_rem = res.get("budget_remaining", "—")
        time_rem   = res.get("time_remaining", "—")
        w_icon   = WEATHER_ICONS.get(weather, "☀️")
        m_icon   = MODE_ICONS.get(mode, "🚇")
        chip_cls = f"chip-{mode}"

        st.markdown(f"""
        <div style="margin-bottom:1rem">
            <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem">
                <span style="font-size:2rem">{m_icon}</span>
                <div>
                    <div style="font-family:'Syne',sans-serif;font-size:1.4rem;
                                font-weight:800;letter-spacing:-0.02em">
                        {mode.upper()}
                        <span class="mode-chip {chip_cls}">{mode}</span>
                    </div>
                    <div style="font-size:0.82rem;color:#94a3b8;margin-top:0.1rem">
                        {reason}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c_a, c_b, c_c, c_d = st.columns(4)
        with c_a:
            color = "val-green" if success else "val-red"
            label = "✓ SUCCESS" if success else "✗ FAILED"
            st.markdown(f'<div class="result-label">Outcome</div><div class="result-val {color}">{label}</div>', unsafe_allow_html=True)
        with c_b:
            r_color = "val-green" if reward > 0.5 else ("val-yellow" if reward > 0 else "val-red")
            st.markdown(f'<div class="result-label">Reward</div><div class="result-val {r_color}">{reward:.4f}</div>', unsafe_allow_html=True)
        with c_c:
            st.markdown(f'<div class="result-label">Weather</div><div class="result-val val-blue">{w_icon} {weather.replace("_"," ")}</div>', unsafe_allow_html=True)
        with c_d:
            st.markdown(f'<div class="result-label">Steps</div><div class="result-val">{steps}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        c_e, c_f = st.columns(2)
        with c_e:
            st.markdown(f'<div class="result-label">Budget Remaining</div><div class="result-val val-yellow">₹ {budget_rem}</div>', unsafe_allow_html=True)
        with c_f:
            st.markdown(f'<div class="result-label">Time Remaining</div><div class="result-val val-blue">{time_rem} min</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── RIGHT COLUMN ──────────────────────────────────────────────────────────────
with right_col:
    pre_results, post_results, log_load_errors = load_training_results()

    # ── Pre / Post Training Results ──────────────────────────────────────────
    st.markdown('<div class="section-label">Training Results</div>', unsafe_allow_html=True)
    selected_task = task_difficulty.lower()
    has_training_data = selected_task in pre_results and selected_task in post_results

    if st.session_state.result is None:
        st.markdown("""
        <div style="height: 180px; display: flex; align-items: center; justify-content: center;
                    border: 1px dashed var(--border); border-radius: 12px; color: var(--muted);
                    font-family: var(--font-mono); font-size: 0.8rem; margin-top: 0.2rem; flex-direction: column; gap: 0.5rem;">
            <span style="font-size:1.4rem">🧾</span>
            <span>Run Agent to load training logs for the selected task.</span>
        </div>
        """, unsafe_allow_html=True)
    elif not has_training_data:
        st.warning(f"No training log data found for selected task: {selected_task}")
    else:
        st.markdown('<div class="stats-grid">', unsafe_allow_html=True)

        pre_row = pre_results[selected_task]
        post_row = post_results[selected_task]
        delta_reward = post_row["mean_reward"] - pre_row["mean_reward"]

        pre_sr_pct = f"{pre_row['success_rate'] * 100:.0f}%"
        pre_rw = f"{pre_row['mean_reward']:+.2f}"
        pre_col = "#22c55e" if pre_row["mean_reward"] > 0 else "#ef4444"
        pre_html = (
            '<div class="stat-card stat-card-pre"><div class="stat-card-title">'
            f'Pre-Training (Baseline) · {selected_task.upper()}</div>'
            f'<div class="stat-row"><span class="stat-task">reward</span><span class="stat-val" style="color:{pre_col}">{pre_rw}</span></div>'
            f'<div class="stat-row"><span class="stat-task">success rate</span><span class="stat-val" style="color:#64748b">{pre_sr_pct}</span></div>'
            '<div style="margin-top:0.6rem;font-family:\'IBM Plex Mono\',monospace;font-size:0.62rem;color:#64748b">source: results/baseline_results.json</div></div>'
        )

        post_sr_pct = f"{post_row['success_rate'] * 100:.0f}%"
        post_rw = f"{post_row['mean_reward']:+.2f}"
        delta_col = "#22c55e" if delta_reward > 0 else "#ef4444"
        post_html = (
            '<div class="stat-card stat-card-post"><div class="stat-card-title">'
            f'Post-Training · {selected_task.upper()}</div>'
            f'<div class="stat-row"><span class="stat-task">reward</span><span class="stat-val" style="color:#22c55e">{post_rw}</span></div>'
            f'<div class="stat-row"><span class="stat-task">delta</span><span class="stat-val" style="color:{delta_col}">{delta_reward:+.2f}</span></div>'
            f'<div class="stat-row"><span class="stat-task">success rate</span><span class="stat-val" style="color:#64748b">{post_sr_pct}</span></div>'
            '<div style="margin-top:0.6rem;font-family:\'IBM Plex Mono\',monospace;font-size:0.62rem;color:#64748b">source: results/post_training_results.json</div></div>'
        )

        st.markdown(pre_html + post_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if log_load_errors:
        for msg in log_load_errors:
            st.warning(msg)

    # ── Visualisations (Plotly Grouped Bar Charts) ─────────────────────────────
    st.markdown('<div class="section-label" style="margin-top:0.5rem">Performance Visualisation</div>', unsafe_allow_html=True)

    if st.session_state.result is None:
        st.markdown("""
        <div style="height: 250px; display: flex; align-items: center; justify-content: center; 
                    border: 1px dashed var(--border); border-radius: 12px; color: var(--muted); 
                    font-family: var(--font-mono); font-size: 0.8rem; margin-top: 1rem; flex-direction: column; gap: 0.5rem;">
            <span style="font-size:1.5rem">📊</span>
            <span>Awaiting implementation phase...</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        tasks_list = [t for t in TASK_ORDER if t in pre_results and t in post_results]
        pre_rewards = [pre_results[t]["mean_reward"] for t in tasks_list]
        post_rewards = [post_results[t]["mean_reward"] for t in tasks_list]
        pre_succ = [pre_results[t]["success_rate"] * 100 for t in tasks_list]
        post_succ = [post_results[t]["success_rate"] * 100 for t in tasks_list]

        if not tasks_list:
            st.warning("Training log files are missing task metrics for charting.")
        else:
            import plotly.graph_objects as go

            def create_grouped_bar(y_pre, y_post, is_pct=False):
                fig = go.Figure()
                
                # Colors matching the reference image: easy, medium, hard, bonus
                colors_pre  = ["#93c5fd", "#fcd34d", "#fca5a5", "#c4b5fd"]
                colors_post = ["#1d4ed8", "#ea580c", "#b91c1c", "#5b21b6"]
                
                text_pre = [f"{v:.0f}%" if is_pct else f"{v:.2f}" for v in y_pre]
                text_post= [f"{v:.0f}%" if is_pct else f"{v:.2f}" for v in y_post]

                fig.add_trace(go.Bar(
                    name='Pre-Training', x=tasks_list, y=y_pre,
                    marker_color=colors_pre, text=text_pre, textposition='outside', textfont=dict(size=10)
                ))
                fig.add_trace(go.Bar(
                    name='Post-Training', x=tasks_list, y=y_post,
                    marker_color=colors_post, text=text_post, textposition='outside', textfont=dict(size=10)
                ))
                
                is_light = st.session_state.theme == "light"
                text_col = "#64748b" if is_light else "#94a3b8"
                grid_col = "#e2e8f0" if is_light else "#1e293b"
                
                fig.update_layout(
                    barmode='group', height=280, margin=dict(l=0, r=0, t=30, b=0),
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(size=11, color=text_col)),
                    xaxis=dict(showgrid=False, tickfont=dict(color=text_col, size=12, family="Plus Jakarta Sans")),
                    yaxis=dict(showgrid=True, gridcolor=grid_col, tickfont=dict(color=text_col, size=11, family="JetBrains Mono"), zerolinecolor=grid_col),
                    bargap=0.25, bargroupgap=0.05
                )
                # Ensure y-axis scales accommodate outside text
                if not is_pct:
                    fig.update_yaxes(range=[min(min(y_pre), min(y_post)) - 0.2, max(max(y_pre), max(y_post)) + 0.3])
                else:
                    fig.update_yaxes(range=[0, 110])
                    
                return fig

            tab1, tab2 = st.tabs(["📊 Mean Reward", "✅ Success Rate"])

            with tab1:
                st.plotly_chart(create_grouped_bar(pre_rewards, post_rewards, False), use_container_width=True, config={'displayModeBar': False})

            with tab2:
                st.plotly_chart(create_grouped_bar(pre_succ, post_succ, True), use_container_width=True, config={'displayModeBar': False})

    # ── Transport Mode Reference ──────────────────────────────────────────────
    st.markdown('<div class="section-label" style="margin-top:1rem">Mode Priority Reference</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="input-card" style="padding:1rem 1.25rem">
      <div style="display:flex;flex-wrap:wrap;gap:0.3rem;margin-bottom:0.75rem">
        <span class="mode-chip chip-metro">🚇 metro</span>
        <span class="mode-chip chip-train">🚆 train</span>
        <span class="mode-chip chip-auto">🛺 auto</span>
        <span class="mode-chip chip-bus">🚌 bus</span>
        <span class="mode-chip chip-walk">🚶 walk</span>
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;
                  color:#64748b;line-height:1.7">
        <div>⛈️ <b style="color:#38bdf8">heavy_rain</b> → metro &gt; train &gt; walk (never auto/bus)</div>
        <div>🌦️ <b style="color:#a78bfa">light_rain</b>  → metro &gt; train &gt; auto &gt; bus</div>
        <div>☀️ <b style="color:#22c55e">no_rain</b>    → metro &gt; train &gt; auto &gt; bus &gt; walk</div>
        <div style="margin-top:0.4rem">⏱️ &lt;25 min remaining → metro only</div>
        <div>💰 budget &lt;₹20 → train or walk only</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI DOCS BAR (bottom)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="fastapi-bar">
  <div class="fastapi-dot"></div>
  <span class="fastapi-label">FastAPI Docs</span>
  <a class="fastapi-link" href="{st.session_state.fastapi_url}" target="_blank">
      {st.session_state.fastapi_url}
  </a>
  <span style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#64748b;flex-shrink:0">
      Interactive API Reference →
  </span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;margin-top:1.5rem;
            font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#1f2d45">
    Mumbai LastMile · GRPO 3-Phase RL · Unsloth · Qwen-1.5B-Instruct
</div>
""", unsafe_allow_html=True)
