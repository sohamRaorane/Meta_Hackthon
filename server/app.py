# server/app.py
# We bypass openenv's session management entirely and build a simple
# FastAPI server ourselves. This is more reliable and easier to debug.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uuid
import uvicorn

from server.environment import MumbaiLastMileEnvironment
from models import MumbaiAction

app = FastAPI()

# Global store: episode_id → environment instance
# This is the correct way to manage state across requests
ENV_STORE: dict = {}

# ── Request / Response schemas ──────────────────────────────────

class ResetRequest(BaseModel):
    task_name: str = "easy"
    seed: Optional[int] = None
    episode_id: Optional[str] = None

class StepRequest(BaseModel):
    episode_id: str
    action: MumbaiAction

# ── Helper: serialize observation to dict ───────────────────────

def obs_to_dict(obs, reward=None, done=False):
    return {
        "observation": {
            "episode_id":              obs.episode_id,
            "echoed_message":          obs.echoed_message,
            "current_location":        obs.current_location,
            "destination":             obs.destination,
            "time_remaining_minutes":  obs.time_remaining_minutes,
            "budget_remaining":        obs.budget_remaining,
            "weather":                 obs.weather,
            "available_modes": [
                {
                    "mode":         m.mode,
                    "available":    m.available,
                    "confidence":   m.confidence,
                    "est_cost":     m.est_cost,
                    "est_time_min": m.est_time_min,
                    "est_time_max": m.est_time_max,
                }
                for m in obs.available_modes
            ],
            "known_disruptions":  obs.known_disruptions,
            "mid_journey_update": obs.mid_journey_update,
            "timestep":           obs.timestep,
        },
        "reward": reward,
        "done":   done,
    }

# ── Endpoints ───────────────────────────────────────────────────

@app.post("/reset")
def reset(req: ResetRequest):
    # Create a brand new environment instance for this episode
    env = MumbaiLastMileEnvironment()
    episode_id = req.episode_id or str(uuid.uuid4())

    obs = env.reset(
        task_name=req.task_name,
        seed=req.seed,
        episode_id=episode_id,
    )

    # Store the env so /step can find it later
    ENV_STORE[episode_id] = env

    return obs_to_dict(obs, reward=None, done=False)


@app.post("/step")
def step(req: StepRequest):
    env = ENV_STORE.get(req.episode_id)

    if env is None:
        return {
            "error": f"No environment found for episode_id '{req.episode_id}'. Call /reset first."
        }

    obs = env.step(req.action)

    # Clean up finished episodes to save memory
    if obs.done:
        ENV_STORE.pop(req.episode_id, None)

    return obs_to_dict(obs, reward=obs.reward, done=obs.done)


@app.get("/state")
def state(episode_id: str):
    env = ENV_STORE.get(episode_id)
    if env is None:
        return {"error": "No environment found for this episode_id"}
    s = env.state
    return {
        "episode_id":  s.episode_id,
        "step_count":  s.step_count,
        "task_name":   s.task_name,
        "origin":      s.origin,
        "destination": s.destination,
        "seed":        s.seed,
    }


@app.get("/health")
def health():
    return {"status": "healthy", "active_sessions": len(ENV_STORE)}


@app.get("/metadata")
def metadata():
    return {
        "name": "mumbai-lastmile-crisis-response",
        "description": "Mumbai last-mile multi-leg crisis response simulation",
    }


@app.get("/schema")
def schema():
    return {
        "action": MumbaiAction.model_json_schema(),
        "observation": {
            "type": "object",
            "description": "See /reset and /step observation payload fields",
        },
        "state": {
            "type": "object",
            "description": "See /state response payload fields",
        },
    }


@app.post("/mcp")
def mcp_stub(payload: dict):
    request_id = payload.get("id") if isinstance(payload, dict) else None
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32601,
            "message": "MCP not implemented for this environment",
        },
    }


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()