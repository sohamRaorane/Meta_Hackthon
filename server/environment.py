# server/environment.py
# ──────────────────────────────────────────────────────────────
# This is the CORE of your OpenEnv project.
# It defines the MumbaiLastMileEnvironment class.
#
# Think of this as the "game engine":
#   - reset()  → starts a new round/episode
#   - step()   → processes the agent's decision and returns what happened
#   - state    → returns the current internal status
# ──────────────────────────────────────────────────────────────

import random   # Python's built-in random number generator
import uuid     # Generates unique IDs (like a session ID)
from typing import List, Optional

# openenv imports — these come from the openenv-core package you installed
from openenv.core.env_server import Environment

# Your own files
from models import MumbaiAction, MumbaiObservation, MumbaiState, ModeInfo
from data.routes import CORRIDORS, WEATHER_MODIFIERS, TASKS


class MumbaiLastMileEnvironment(Environment):
    """
    The Mumbai Last-Mile Crisis Response Environment.

    An AI agent plays the role of a commuter who must choose
    the best transport mode(s) under partial information,
    weather disruptions, and budget/time constraints.
    """

    # This tells openenv that multiple sessions can run at the same time.
    # Important for the hackathon validator which runs parallel tests.
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        # All the variables that track the current state of one episode
        self._task_cfg = None          # Which task is currently running (easy/medium/hard)
        self._location = ""            # Where the agent currently is
        self._budget = 0.0             # How much money is left (in ₹)
        self._time_remaining = 0       # How many minutes are left to reach destination
        self._weather = "clear"        # Current weather condition
        self._disruptions: List[str] = []  # List of active disruptions the agent knows about
        self._timestep = 0             # How many steps have passed in this episode
        self._reached = False          # Has the agent reached the destination yet?
        self._rng = random.Random()    # Our random number generator (seeded for reproducibility)
        self._state = MumbaiState()    # The State object returned by the state property

    def reset(
        self,
        task_name: str = "easy",
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs,
    ) -> MumbaiObservation:
        """
        Start a new episode.

        Called by the AI agent (or validator) to begin a fresh run.
        Sets everything back to the starting conditions for the chosen task.
        Returns the first Observation — what the agent sees at the start.
        """
        # Look up the task configuration from data/routes.py
        # If task_name isn't found, default to "easy"
        cfg = TASKS.get(task_name, TASKS["easy"])
        self._task_cfg = cfg

        # Seed the random number generator.
        # Using a fixed seed means: same seed = same random outcomes every time.
        # This makes the environment deterministic and fair for all agents.
        self._rng.seed(seed if seed is not None else cfg["seed"])

        # Set up the starting state from the task config
        self._location = cfg["origin"]           # e.g., "Andheri East"
        self._budget = cfg["budget"]             # e.g., 100.0
        self._time_remaining = cfg["time_limit"] # e.g., 45 minutes
        self._weather = cfg["weather"]           # e.g., "clear"
        self._disruptions = list(cfg["disruptions"])  # Copy the list (not reference)
        self._timestep = 0
        self._reached = False

        # Create a new State object with a unique episode ID
        self._state = MumbaiState(
            episode_id=episode_id or str(uuid.uuid4()),  # Unique ID for this run
            step_count=0,
            task_name=task_name,
            origin=cfg["origin"],
            destination=cfg["destination"],
            seed=seed if seed is not None else cfg["seed"],
        )

        # Build the list of available transport modes (with real-time data)
        modes = self._get_modes()

        # Build the human-readable situation text the agent will read
        echoed = self._build_echoed(modes)

        # Return the first Observation (no reward yet — episode just started)
        return MumbaiObservation(
            done=False,              # Episode is not over
            reward=None,             # No reward on the first observation
            echoed_message=echoed,   # The situation text
            current_location=self._location,
            destination=cfg["destination"],
            time_remaining_minutes=self._time_remaining,
            budget_remaining=self._budget,
            weather=self._weather,
            available_modes=modes,
            known_disruptions=self._disruptions,
            mid_journey_update=None,
            timestep=self._timestep,
        )

    def step(
        self,
        action: MumbaiAction,
        timeout_s: Optional[float] = None,
        **kwargs,
    ) -> MumbaiObservation:
        """
        Process one agent decision.

        The agent sends a message like "Take metro to Kurla".
        This method:
          1. Figures out which transport mode was chosen
          2. Simulates the journey leg (did it work? how long? how much?)
          3. Updates budget and time
          4. Calculates the reward
          5. Checks if the episode is over (reached destination, out of time, or max steps)
          6. Returns the new Observation
        """
        # Increment counters
        self._timestep += 1
        self._state.step_count += 1
        cfg = self._task_cfg

        # Step 1: Parse the agent's message to find the transport mode
        chosen_mode = self._parse_mode(action.message)

        # Step 2: Simulate the journey leg (random outcome based on data + weather)
        outcome = self._simulate_leg(chosen_mode)

        # Step 3: Update the environment state based on what happened
        self._budget -= outcome["cost"]
        self._time_remaining -= outcome["time_taken"]
        if outcome["moved"]:
            # Agent successfully moved — they're now at the destination
            self._location = cfg["destination"]
            self._reached = True

        # Step 4: Check if a mid-journey surprise should be injected
        # (Only happens in the "hard" task at step 2)
        mid_update = None
        inject_step = cfg.get("mid_journey_inject_step")
        if inject_step and self._timestep == inject_step:
            mid_update = cfg.get("mid_journey_event", "")
            if mid_update:
                # Add the surprise event to the disruptions list
                self._disruptions.append(mid_update)

        # Step 5: Calculate the reward for this step
        reward = self._calc_reward(outcome, chosen_mode)

        # Step 6: Check if the episode should end
        max_steps = cfg.get("max_steps", 3)
        done = (
            self._reached                       # Reached destination → done
            or self._time_remaining <= 0        # Ran out of time → done
            or self._timestep >= max_steps      # Used all steps → done
        )

        # Step 7: Build updated mode list and situation text
        modes = self._get_modes()
        echoed = self._build_echoed(modes, outcome["message"])

        # Step 8: Return the new Observation
        return MumbaiObservation(
            done=done,
            reward=reward,
            echoed_message=echoed,
            current_location=self._location,
            destination=cfg["destination"],
            time_remaining_minutes=max(0, self._time_remaining),  # Never go below 0
            budget_remaining=self._budget,
            weather=self._weather,
            available_modes=modes,
            known_disruptions=self._disruptions,
            mid_journey_update=mid_update,
            timestep=self._timestep,
        )

    @property
    def state(self) -> MumbaiState:
        """Returns the current internal state of the environment."""
        return self._state

    # ──────────────────────────────────────────────────────────
    # PRIVATE HELPER METHODS (used internally, not called by agent)
    # ──────────────────────────────────────────────────────────

    def _parse_mode(self, message: str) -> str:
        """
        Read the agent's text message and figure out which transport mode they chose.

        Example: "Take metro to Kurla" → returns "metro"
        Example: "I'll take an auto" → returns "auto"
        Example: "rickshaw please" → returns "auto" (rickshaw = auto)
        If nothing matches, default to "bus" (safest fallback).
        """
        msg = message.lower()
        for mode in ["metro", "train", "auto", "rickshaw", "bus", "walk"]:
            if mode in msg:
                return "auto" if mode == "rickshaw" else mode
        return "bus"  # Default fallback

    def _simulate_leg(self, mode: str) -> dict:
        """
        Simulate one journey leg for the chosen transport mode.

        This is where randomness happens:
        - Did the mode actually show up? (based on availability probability)
        - How long did it take? (random between time_min and time_max)
        - Weather affects both availability and time

        Returns a dict with: cost, time_taken, moved (bool), success (bool), message
        """
        cfg = self._task_cfg
        # Get the route data for the current corridor (e.g., Andheri to Kurla)
        corridor = CORRIDORS.get(cfg["corridor_key"], CORRIDORS["default"])
        # Get the specific mode's data
        mode_data = corridor.get(mode, corridor["bus"])
        # Get weather effects
        weather_mod = WEATHER_MODIFIERS.get(self._weather, {})

        # Calculate effective availability after weather adjustment
        base_avail = mode_data["availability"]
        avail_factor = weather_mod.get(f"{mode}_availability", 1.0)
        final_avail = base_avail * avail_factor
        # Example: auto base = 0.70, heavy_rain factor = 0.2 → final = 0.14 (14% chance!)

        # Roll the dice: is the mode available?
        available = self._rng.random() < final_avail

        if not available:
            # Mode failed — agent wasted 12 minutes waiting for something that didn't come
            return {
                "cost": 0,
                "time_taken": 12,       # 12 min penalty for waiting in vain
                "moved": False,
                "success": False,
                "mode_unavailable": True,
                "message": (
                    f"{mode.capitalize()} was not available. "
                    f"Lost 12 minutes waiting."
                ),
            }

        # Mode is available — simulate the journey time
        time_factor = weather_mod.get(f"{mode}_time_factor", 1.0)
        time_taken = int(
            self._rng.uniform(
                mode_data["time_min"],
                mode_data["time_max"] * time_factor,
            )
        )

        return {
            "cost": mode_data["cost"],
            "time_taken": time_taken,
            "moved": True,
            "success": True,
            "mode_unavailable": False,
            "message": (
                f"Took {mode} — arrived in {time_taken} min, "
                f"spent ₹{mode_data['cost']:.0f}."
            ),
        }

    def _calc_reward(self, outcome: dict, mode: str) -> float:
        """
        Calculate the reward score for this step.

        Reward breakdown:
          +0.25  → Mode was successfully available and used
          +1.0   → Agent reached the destination
          +0.0 to +0.30 → Time buffer bonus (reached early = higher bonus)
          +0.0 to +0.15 → Budget efficiency bonus
          -0.25  → Chose auto in heavy rain (bad decision)
          -0.30  → Mode was unavailable (agent should have predicted this)
          -0.40  → Went over budget
          -0.50  → Ran out of time without reaching destination

        Total is clamped between -1.0 and 1.5.
        """
        reward = 0.0
        cfg = self._task_cfg

        # Reward: mode worked
        if outcome["success"]:
            reward += 0.25

        # Reward: reached destination (biggest reward)
        if self._reached:
            reward += 1.0

        # Reward: time buffer — arrived with time to spare?
        if self._reached and self._time_remaining > 5:
            buffer_ratio = self._time_remaining / cfg["time_limit"]
            reward += round(buffer_ratio * 0.3, 4)

        # Reward: budget efficiency
        if 0 <= self._budget <= cfg["budget"]:
            spent_ratio = 1.0 - (self._budget / cfg["budget"])
            reward += round((1.0 - spent_ratio) * 0.15, 4)
        elif self._budget < 0:
            reward -= 0.4   # Penalty: went over budget

        # Penalty: chose auto in heavy rain (a bad call the agent should know to avoid)
        if self._weather == "heavy_rain" and mode == "auto":
            reward -= 0.25

        # Penalty: mode was unavailable (lost time waiting)
        if outcome.get("mode_unavailable"):
            reward -= 0.3

        # Penalty: ran out of time
        if self._time_remaining <= 0 and not self._reached:
            reward -= 0.5

        # Clamp between -1.0 and 1.5 (can't go below -1.0 or above 1.5)
        return round(max(-1.0, min(1.5, reward)), 4)

    def _get_modes(self) -> List[ModeInfo]:
        """
        Build the list of ModeInfo objects for the current situation.

        This is what the agent sees: for each transport mode,
        what is estimated cost, time range, availability, and confidence?
        Confidence is how reliable the data is (sensor_reliability from task config).
        """
        cfg = self._task_cfg
        corridor = CORRIDORS.get(cfg["corridor_key"], CORRIDORS["default"])
        weather_mod = WEATHER_MODIFIERS.get(self._weather, {})
        reliability = cfg.get("sensor_reliability", [1.0] * 5)

        mode_order = ["train", "auto", "bus", "metro", "walk"]
        modes = []
        for i, mode in enumerate(mode_order):
            data = corridor.get(mode, corridor.get("bus"))
            avail_factor = weather_mod.get(f"{mode}_availability", 1.0)
            time_factor = weather_mod.get(f"{mode}_time_factor", 1.0)
            # Reliability/confidence comes from sensor_reliability list in the task
            conf = reliability[i] if i < len(reliability) else 1.0
            modes.append(
                ModeInfo(
                    mode=mode,
                    # Mode is considered "available" if probability > 25%
                    available=(data["availability"] * avail_factor) > 0.25,
                    confidence=conf,         # How reliable is this info? (0.0–1.0)
                    est_cost=data["cost"],
                    est_time_min=data["time_min"],
                    est_time_max=int(data["time_max"] * time_factor),
                )
            )
        return modes

    def _build_echoed(
        self,
        modes: List[ModeInfo],
        last_msg: str = "",
    ) -> str:
        """
        Build the human-readable situation text that the AI agent reads.

        This is what gets sent to the LLM as context.
        It summarizes: where you are, time left, budget, weather,
        disruptions, and each transport option with its data.
        """
        cfg = self._task_cfg
        lines = []
        for m in modes:
            # Show "uncertain" if confidence is low (sensor is unreliable)
            conf_str = "uncertain" if m.confidence < 0.6 else "confirmed"
            avail_str = "available" if m.available else "UNAVAILABLE"
            lines.append(
                f"  {m.mode}: {avail_str} ({conf_str}), "
                f"~₹{m.est_cost:.0f}, "
                f"{m.est_time_min}–{m.est_time_max} min"
            )

        disruptions = (
            ", ".join(self._disruptions) if self._disruptions else "none"
        )

        # Build the full situation message
        msg = (
            f"Location: {self._location} → {cfg['destination']}\n"
            f"Time remaining: {self._time_remaining} min | "
            f"Budget: ₹{self._budget:.0f}\n"
            f"Weather: {self._weather}\n"
            f"Known disruptions: {disruptions}\n"
            f"Transport options:\n" + "\n".join(lines)
        )

        # If a previous step happened, show what the result was
        if last_msg:
            msg = f"Last action result: {last_msg}\n\n{msg}"

        return msg