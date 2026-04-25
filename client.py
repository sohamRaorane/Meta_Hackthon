# client.py
# ──────────────────────────────────────────────────────────────
# This file is the "waiter" between the AI agent and the server.
#
# The agent calls methods on this class (like reset() and step()),
# and this class handles all the communication with the web server,
# converting raw JSON back into proper Python objects.
#
# You do NOT run this file directly. It is imported by inference.py.
# ──────────────────────────────────────────────────────────────

# EnvClient is a base class from openenv that handles the HTTP requests.
# StepResult is a container that wraps: observation + reward + done flag.
from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult

# Import our custom models that we defined in models.py
from models import MumbaiAction, MumbaiObservation, MumbaiState, ModeInfo


class MumbaiLastMileEnv(
    EnvClient[MumbaiAction, MumbaiObservation, MumbaiState]
):
    """
    The client-side interface for the Mumbai Last-Mile Environment.

    This class inherits from EnvClient, which already knows how to:
      - Send POST /reset requests to the server
      - Send POST /step requests to the server
      - Get GET /state from the server

    We only need to define 3 things:
      1. How to convert an Action into a request payload (dict)
      2. How to convert a server response into a StepResult
      3. How to convert a server state response into a MumbaiState
    """

    def _step_payload(self, action: MumbaiAction) -> dict:
        """
        Convert our MumbaiAction into the JSON body for POST /step.

        The server's step() function expects a dict with one key: "message".
        This is the plain English transport decision the agent made.

        Example:
          Input:  MumbaiAction(message="Take metro to Kurla")
          Output: {"message": "Take metro to Kurla"}

        Why not just send the whole action object?
        Because HTTP requests send JSON, not Python objects.
        We need to convert it first.
        """
        return {"message": action.message}

    def _parse_result(self, payload: dict) -> StepResult:
        """
        Convert the raw JSON response from POST /step into a StepResult.

        When the server returns a response, it's a raw dictionary (JSON).
        We need to convert it back into proper Python objects so the
        agent can work with them cleanly.

        The server returns something like:
        {
          "done": false,
          "reward": 0.75,
          "observation": {
            "echoed_message": "Location: Andheri East → Kurla...",
            "current_location": "Andheri East",
            "available_modes": [
              {"mode": "train", "available": true, "confidence": 0.9, ...},
              ...
            ],
            ...
          }
        }

        This method unpacks all of that into proper Python objects.
        """
        # Get the nested "observation" dict from the response
        obs_data = payload.get("observation", {})

        # The available_modes comes as a list of dicts — we need to
        # convert each dict into a proper ModeInfo object
        raw_modes = obs_data.get("available_modes", [])
        modes = [ModeInfo(**m) for m in raw_modes]
        # The ** unpacks a dict into keyword arguments.
        # Example: ModeInfo(**{"mode": "train", "available": True, ...})
        # is the same as: ModeInfo(mode="train", available=True, ...)

        # Build the full MumbaiObservation object from the response data
        obs = MumbaiObservation(
            done=payload.get("done", False),
            reward=payload.get("reward"),
            echoed_message=obs_data.get("echoed_message", ""),
            current_location=obs_data.get("current_location", ""),
            destination=obs_data.get("destination", ""),
            time_remaining_minutes=obs_data.get("time_remaining_minutes", 0),
            budget_remaining=obs_data.get("budget_remaining", 0.0),
            weather=obs_data.get("weather", "clear"),
            available_modes=modes,
            known_disruptions=obs_data.get("known_disruptions", []),
            mid_journey_update=obs_data.get("mid_journey_update"),
            timestep=obs_data.get("timestep", 0),
        )

        # Wrap everything into a StepResult and return
        return StepResult(
            observation=obs,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> MumbaiState:
        """
        Convert the raw JSON response from GET /state into a MumbaiState.

        The state is the internal snapshot of where the environment is —
        episode ID, step count, task name, origin, destination, seed.
        This is used by the openenv validator to check your environment.
        """
        return MumbaiState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            task_name=payload.get("task_name", ""),
            origin=payload.get("origin", ""),
            destination=payload.get("destination", ""),
            seed=payload.get("seed", 42),
        )