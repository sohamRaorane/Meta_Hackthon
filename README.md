# Mumbai Last-Mile Crisis Response
### OpenEnv Hackathon Submission | Reinforcement Learning Environment for Real-World Urban Routing

Mumbai’s daily commute is one of the most complex transport systems in the world. A route that works at 8:30 AM can fail at 8:45 AM because of rain, signal failure, traffic congestion, crowding, or local disruptions.

We built an **OpenEnv-compatible reinforcement learning environment** where an AI agent learns how to make better travel decisions under these changing conditions. Instead of solving toy games, the agent must solve a real planning problem: **Reach the destination on time, within budget, despite disruptions.**

---

# Live Links

| Resource | URL |
| :--- | :--- |
| **Hugging Face Space** | https://huggingface.co/spaces/eagle25/mumbai-lastmile-env |
| **Live API** | https://eagle25-mumbai-lastmile-env.hf.space |
| **API Docs** | https://eagle25-mumbai-lastmile-env.hf.space/docs |
| **Full Writeup** | See `Blog.md` |

---

# Why This Environment Matters

Many language models can answer questions, but struggle with:

* **Multi-step planning**
* **Dynamic decision making**
* **Adapting to uncertainty**
* **Balancing cost vs speed**
* **Recovering from bad early choices**

Mumbai commuting naturally contains all of these challenges, making it a strong real-world RL benchmark.

---

# Environment Design

The agent is given scenarios such as:
* Andheri East to Kurla Station
* Multi-leg transfer journeys
* Tight budget trips
* Time-critical office commutes
* Weather-disrupted routes

### Observations
At each step, the agent observes:
* Current location and destination
* Time and budget remaining
* Weather and known disruptions
* Available transport modes (with estimated times/costs)

### Action Space
The agent chooses one action:
* **Train**
* **Metro**
* **Bus**
* **Auto**
* **Walk**

---

# Core Logic

The environment simulates real trade-offs:
* **Metro:** Fast but may cost more.
* **Bus:** Cheap but slower.
* **Auto:** May become unreliable in rain.
* **Walking:** Saves money but costs time.
* **Cascading Effects:** A bad first leg can ruin the full journey.

This creates meaningful sequential planning instead of one-step guessing.

---

# Reward Design

The reward system is shaped to teach useful behavior.

| Positive Reward For | Negative Reward For |
| :--- | :--- |
| Reaching destination | Wasting time |
| Saving time | Overspending |
| Staying within budget | Poor choices during disruptions |
| Making progress each step | Failing to complete trip |

---

# OpenEnv Compatibility

This project follows OpenEnv style APIs:
* `reset()`
* `step()`
* Environment state transitions
* Task-based episodes
* Hosted public environment

---

# Training Pipeline

We trained the agent using a **GRPO-based RL pipeline** with lightweight models for rapid iteration.

1. **Phase 1:** Easy scenarios
2. **Phase 2:** Medium scenarios
3. **Phase 3:** Hard disruption-heavy scenarios

The model repeatedly interacts with the environment, receives reward feedback, and improves behavior over time.

---

# Results

### Success Rate Improvement
* **Easy:** 15% to 60%
* **Medium:** 25% to 30%
* **Bonus:** 60% to 85%

### Mean Reward Improvement
* **Easy:** -0.404 to 0.575
* **Bonus:** 0.525 to 0.980

*Hard mode remains challenging, reflecting the difficulty of real-world uncertain planning.*

---

# Training Plot

![Training Results](training_results.png)

*Measured improvement after GRPO training across multiple task categories.*

---

# Example Live Episode

### Scenario
Andheri East to Kurla Station

### Conditions
* 45 minutes left
* Budget: INR 55
* Light rain
* Train disruption warning

### Learned Route
1. **Metro** to Ghatkopar
2. **Train** to Kurla Station

**Result:** Reached successfully with time remaining.

---

# Repository Structure

```text
server/
  environment.py   # route simulation + transitions
  routes.py        # FastAPI endpoints
graders.py         # reward / scoring logic
inference.py       # inference runner
openenv.yaml       # OpenEnv manifest
Blog.md            # detailed writeup
README.md          # project overview


How to Run Locally
Install dependencies:

Bash
pip install -r requirements.txt
Run the server:

Bash
python -m uvicorn server.routes:app --host 0.0.0.0 --port 8000
Access Documentation:
Navigate to http://localhost:8000/docs

Why Judges May Find This Interesting
This environment trains capabilities useful beyond commuting:

Delivery optimization

Field worker routing

Emergency dispatch

Smart mobility systems

Planning under uncertainty

Final Note
We intentionally chose a real-world messy problem over a polished toy problem. Mumbai commuters solve optimization problems every day. This environment teaches AI to do the same.