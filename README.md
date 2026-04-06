---
title: Mumbai Last-Mile Crisis Response
emoji: 🚇
colorFrom: blue
colorTo: red
sdk: docker
pinned: false
tags:
  - openenv
  - environment
  - reinforcement-learning
  - mumbai
  - transport
---

# Mumbai Last-Mile Crisis Response Environment

An OpenEnv environment where an AI agent must navigate multi-leg Mumbai 
commutes under real-world constraints: weather disruptions, signal failures, 
budget limits, and mid-journey surprises.

## Motivation

Mumbai's last-mile transport problem is one of the most complex real-world 
routing challenges. Every commuter faces dynamic decisions — rain kills auto 
availability, Western line failures cascade into missed connections, budget 
constraints force trade-offs between speed and cost. This environment models 
that complexity faithfully.

## Action Space

Text message describing the chosen transport mode:
- Input: natural language string, e.g. `"Take metro. Fast and weather-proof."`
- Parser extracts mode keyword: `metro / train / auto / bus / walk`

## Observation Space

| Field | Type | Description |
|-------|------|-------------|
| echoed_message | str | Full situation text with leg context |
| current_location | str | Agent's current waypoint |
| destination | str | Final destination |
| time_remaining_minutes | int | Minutes left to reach destination |
| budget_remaining | float | Rupees remaining |
| weather | str | clear / light_rain / heavy_rain |
| available_modes | List[ModeInfo] | Per-mode cost, time, availability, confidence |
| known_disruptions | List[str] | Active disruptions the agent knows about |
| mid_journey_update | str | Surprise event requiring replanning (or null) |
| timestep | int | Current step number |

## Tasks

| Task | Route | Legs | Time | Budget | Weather | Difficulty |
|------|-------|------|------|--------|---------|------------|
| easy | Andheri East → Kurla | 2 | 60min | ₹120 | clear | Baseline |
| medium | Borivali → CST | 3 | 90min | ₹80 | heavy_rain | Mid-journey event |
| hard | Churchgate → BKC | 4 | 85min | ₹75 | heavy_rain | Cascading failures |
| bonus | Bandra → Juhu | 2 | 40min | ₹30 | light_rain | Budget crisis |

Programmatic deterministic graders are implemented in `server/graders.py` for all tasks
(`easy`, `medium`, `hard`, `bonus`) and return scores in `[0.0, 1.0]`.

## Reward Function

- `+0.15` per successful mode (mode was available)
- `+0.4 / total_legs` per completed leg (partial progress)
- `+0.8` for reaching final destination
- `+0 to +0.30` time buffer bonus
- `+0 to +0.15` budget efficiency bonus
- `-0.25` auto chosen in heavy rain
- `-0.30` mode was unavailable (agent picked wrong)
- `-0.50` ran out of time
- `-0.40` went over budget
- Score normalized to `[0.0, 1.0]` per task

## Baseline Scores

| Task | Score | Steps |
|------|-------|-------|
| easy | 0.92 | 2 |
| medium | 0.53 | 3 |
| hard | 0.07 | 2 |
| bonus | 0.60 | 2 |

## Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server (same runtime as Docker)
uvicorn server.app:app --host 0.0.0.0 --port 7860

# Run inference (in another terminal)
export SERVER_URL=http://localhost:7860
export API_BASE_URL=https://api.featherless.ai/v1
export MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
export HF_TOKEN=your-api-key-here
# Optional alternative key variable understood by inference.py
export OPENAI_API_KEY=your-api-key-here
python inference.py
```

Optional local UI (separate terminal):
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## Docker
```bash
docker build -t mumbai-lastmile .
docker run -p 7860:7860 \
  -e API_BASE_URL=https://api.featherless.ai/v1 \
  -e MODEL_NAME=Qwen/Qwen2.5-7B-Instruct \
  -e HF_TOKEN=your-key \
  mumbai-lastmile
```

Container entrypoint serves FastAPI directly on port `7860` via `uvicorn server.app:app`.

## Project Structure
```
├── data/
│   └── routes.py          # All Mumbai transport data + task configs
├── server/
│   ├── app.py             # FastAPI server
│   └── environment.py     # Core simulation engine
├── app.py                 # Streamlit frontend UI
├── models.py              # Pydantic typed models
├── client.py              # Client wrapper
├── inference.py           # Baseline agent script
├── server/Dockerfile      
├── openenv.yaml           
└── README.md              
```