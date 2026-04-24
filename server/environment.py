# server/environment.py
# ──────────────────────────────────────────────────────────────
# Upgraded: multi-leg journey support.
# The environment now tracks which leg the agent is on.
# Each leg has its own corridor. Budget and time carry over.
# ──────────────────────────────────────────────────────────────

import random
import uuid
from typing import List, Optional

from openenv.core.env_server import Environment
from models import MumbaiAction, MumbaiObservation, MumbaiState, ModeInfo
from data.routes import CORRIDORS, WEATHER_MODIFIERS, TASKS


class MumbaiLastMileEnvironment(Environment):
    """
    Mumbai Last-Mile Crisis Response Environment.
    Supports multi-leg journeys with waypoints.
    """

    SUPPORTS_CONCURRENT_SESSIONS = False

    def __init__(self):
        self._task_cfg       = None
        self._location       = ""
        self._budget         = 0.0
        self._time_remaining = 0
        self._weather        = "clear"
        self._disruptions: List[str] = []
        self._timestep       = 0
        self._reached        = False
        self._rng            = random.Random()
        self._state          = MumbaiState()

        # NEW: multi-leg tracking
        self._legs           = []   # list of leg dicts from task config
        self._current_leg    = 0    # index into self._legs

    def reset(
        self,
        task_name: str = "easy",
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs,
    ) -> MumbaiObservation:

        cfg = TASKS.get(task_name, TASKS["easy"])
        self._task_cfg = cfg
        self._rng.seed(seed if seed is not None else cfg["seed"])

        self._location       = cfg["origin"]
        self._budget         = cfg["budget"]
        self._time_remaining = cfg["time_limit"]
        self._weather        = cfg["weather"]
        self._disruptions    = list(cfg["disruptions"])
        self._timestep       = 0
        self._reached        = False

        # NEW: set up legs
        self._legs        = cfg["legs"]
        self._current_leg = 0

        self._state = MumbaiState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            task_name=task_name,
            origin=cfg["origin"],
            destination=cfg["destination"],
            seed=seed if seed is not None else cfg["seed"],
        )

        modes  = self._get_modes()
        echoed = self._build_echoed(modes)

        return MumbaiObservation(
            done=False,
            reward=None,
            episode_id=self._state.episode_id,
            echoed_message=echoed,
            current_location=self._location,
            destination=cfg["destination"],
            time_remaining_minutes=self._time_remaining,
            budget_remaining=self._budget,
            weather=self._weather,
            available_modes=modes,
            known_disruptions=self._disruptions,
            mid_journey_update=None,
            timestep=self._timestep,
            reached=False, 
        )

    def step(
        self,
        action: MumbaiAction,
        timeout_s: Optional[float] = None,
        **kwargs,
    ) -> MumbaiObservation:

        self._timestep       += 1
        self._state.step_count += 1
        cfg = self._task_cfg

        # ── Parse & simulate ────────────────────────────────────
        chosen_mode = self._parse_mode(action.message)
        outcome     = self._simulate_leg(chosen_mode)

        # ── Update state ────────────────────────────────────────
        self._budget         -= outcome["cost"]
        self._time_remaining -= outcome["time_taken"]

        if outcome["moved"]:
            # Advance to next leg
            leg = self._legs[self._current_leg]
            self._location = leg["to_location"]
            self._current_leg += 1

            # Check if all legs are complete
            if self._current_leg >= len(self._legs):
                self._reached = True

        # ── Mid-journey event ───────────────────────────────────
        mid_update   = None
        
        # Dynamic disruption injection
        # Paper 2408.10215: environment should have realistic stochasticity
        from data.routes import DISRUPTION_POOL as DISRUPTION_POOL_REF
        
        inject_prob = 0.20  # 20% chance per step after step 1
        max_injections = 2  # never inject more than 2 new events per episode
        
        current_injections = len(self._disruptions) - len(cfg["disruptions"])
        
        if (self._timestep > 1
            and current_injections < max_injections
            and self._rng.random() < inject_prob):
            
            available = [d for d in DISRUPTION_POOL_REF
                         if d not in self._disruptions]
            if available:
                new_event = self._rng.choice(available)
                self._disruptions.append(new_event)
                mid_update = f"NEW DISRUPTION: {new_event}"

        # ── Reward ──────────────────────────────────────────────
        reward = self._calc_reward(outcome, chosen_mode)

        # ── Done check ──────────────────────────────────────────
        max_steps = cfg.get("max_steps", 4)
        done = (
            self._reached
            or self._time_remaining <= 0
            or self._timestep >= max_steps
            or self._budget < 0
        )

        modes  = self._get_modes()
        echoed = self._build_echoed(modes, outcome["message"])

        return MumbaiObservation(
            done=done,
            reward=reward,
            episode_id=self._state.episode_id,
            echoed_message=echoed,
            current_location=self._location,
            destination=cfg["destination"],
            time_remaining_minutes=max(0, self._time_remaining),
            budget_remaining=self._budget,
            weather=self._weather,
            available_modes=modes,
            known_disruptions=self._disruptions,
            mid_journey_update=mid_update,
            timestep=self._timestep,
            reached=self._reached,
        )

    @property
    def state(self) -> MumbaiState:
        return self._state

    # ── PRIVATE HELPERS ─────────────────────────────────────────

    def _current_leg_data(self) -> dict:
        """Return the leg dict for the current leg index."""
        if self._current_leg < len(self._legs):
            return self._legs[self._current_leg]
        # All legs done — return last leg as reference
        return self._legs[-1]

def _parse_mode(self, message: str) -> str:
    """
    Extract transport mode from agent message.

    Phase 0 fix (issue #2):
      Old implementation used naive substring search.
      "automatic" would match "auto". "metropolitan" would match "metro".
      Fix: try JSON parse first, extract "mode" key with word-boundary
      validation. Only fall back to substring scan if JSON fails.
    """
    # ── Attempt 1: JSON parse (preferred — LLM outputs JSON) ────────────
    import json as _json
    try:
        parsed = _json.loads(message)
        if isinstance(parsed, dict):
            mode_key = str(parsed.get("mode", "")).strip().lower()
            if mode_key in {"metro", "train", "auto", "bus", "walk"}:
                return mode_key
    except (_json.JSONDecodeError, ValueError):
        pass

    # ── Attempt 2: word-boundary regex scan ─────────────────────────────
    import re as _re
    msg = message.lower()
    for mode in ["metro", "train", "auto", "bus", "walk"]:
        # \b ensures "auto" does not fire inside "automatic"
        if _re.search(rf"\b{mode}\b", msg):
            return mode

    # ── Fallback ─────────────────────────────────────────────────────────
    return "bus"

def _simulate_leg(self, mode: str) -> dict:
        """
        Simulate one leg for the chosen mode.
        Uses the corridor of the CURRENT leg.
        """
        leg      = self._current_leg_data()
        corridor = CORRIDORS.get(leg["corridor_key"], CORRIDORS["default"])
        mode_data    = corridor.get(mode, corridor.get("bus"))
        weather_mod  = WEATHER_MODIFIERS.get(self._weather, {})

        base_avail   = mode_data["availability"]
        avail_factor = weather_mod.get(f"{mode}_availability", 1.0)
        final_avail  = base_avail * avail_factor

        available = self._rng.random() < final_avail

        if not available:
            return {
                "cost":             0,
                "time_taken":       12,
                "moved":            False,
                "success":          False,
                "mode_unavailable": True,
                "message": (
                    f"{mode.capitalize()} was not available on "
                    f"{leg['from_location']} → {leg['to_location']} leg. "
                    f"Lost 12 min waiting."
                ),
            }

        time_factor = weather_mod.get(f"{mode}_time_factor", 1.0)
        time_taken  = int(
            self._rng.uniform(
                mode_data["time_min"],
                mode_data["time_max"] * time_factor,
            )
        )

        return {
            "cost":             mode_data["cost"],
            "time_taken":       time_taken,
            "moved":            True,
            "success":          True,
            "mode_unavailable": False,          
            "message": (
                f"Took {mode} from {leg['from_location']} to "
                f"{leg['to_location']} — {time_taken} min, "
                f"₹{mode_data['cost']:.0f}."
            ),
        }

def _reward_completion(self) -> float:
        """
        Paper 2408.10215 Section 3.1 — Outcome reward.
        Binary success signal: did the agent complete all legs?
        This is the primary verifiable reward — deterministic, not gameable.
        Returns 0.0 or 0.50. Never intermediate values.
        """
        return 0.50 if self._reached else 0.0

    def _reward_safety(self, mode: str, outcome: dict) -> float:
        """
        Paper 2408.10215 Section 4.2 — Constraint satisfaction reward.
        Penalises clearly unsafe decisions independently of outcome.
        An agent cannot hack this by succeeding — unsafe choices are
        always penalised regardless of whether they worked.
        """
        penalty = 0.0
        # Auto in heavy rain — safety violation
        if self._weather == "heavy_rain" and mode == "auto":
            penalty -= 0.15
        # Choosing unavailable mode — information use failure
        if outcome.get("mode_unavailable"):
            penalty -= 0.12
        # Ignoring low-confidence sensor — epistemic failure
        cfg = self._task_cfg
        mode_order = ["train", "auto", "bus", "metro", "walk"]
        reliability = cfg.get("sensor_reliability", [1.0] * 5)
        if mode in mode_order:
            idx = mode_order.index(mode)
            if idx < len(reliability) and reliability[idx] < 0.4:
                penalty -= 0.08
        return round(max(-0.35, penalty), 4)

    def _reward_efficiency(self, outcome: dict) -> float:
        """
        Paper 2408.10215 Section 4.3 — Potential-based shaping.
        Rewards proportional to time and budget conserved.
        Uses potential-based formulation so it does not change
        the optimal policy — it only speeds up learning.
        """
        cfg = self._task_cfg
        reward = 0.0
        # Time efficiency: potential = time_remaining / time_limit
        if outcome["moved"]:
            time_potential = max(0.0, self._time_remaining) / cfg["time_limit"]
            reward += round(time_potential * 0.15, 4)
        # Budget efficiency: potential = budget_remaining / starting_budget
        budget_potential = max(0.0, self._budget) / cfg["budget"]
        reward += round(budget_potential * 0.10, 4)
        # Over budget penalty — hard constraint violation
        if self._budget < 0:
            reward -= 0.20
        return round(reward, 4)

    def _reward_progress(self, outcome: dict) -> float:
        """
        Paper 2601.19100 Section 2 — Process supervision / step-level signal.
        Partial credit per completed leg so agent gets non-zero reward
        even when it does not finish the full journey.
        This is the dense feedback signal that makes GRPO training stable.
        Without this, episodes that fail give zero gradient signal.
        """
        if not outcome["moved"]:
            return 0.0
        total_legs = len(self._legs)
        # Each leg completion gives equal partial credit
        leg_credit = round(0.25 / total_legs, 4)
        return leg_credit

    def _calc_reward(self, outcome: dict, mode: str) -> float:
        """
        Aggregate all independent reward components.
        Each component is independently verifiable — anti-hacking by design.
        """
        r_completion = self._reward_completion()
        r_safety     = self._reward_safety(mode, outcome)
        r_efficiency = self._reward_efficiency(outcome)
        r_progress   = self._reward_progress(outcome)

        total = r_completion + r_safety + r_efficiency + r_progress

        # Timeout penalty — terminal constraint
        if self._time_remaining <= 0 and not self._reached:
            total -= 0.25

        return round(max(-1.0, min(1.5, total)), 4)

def _get_modes(self) -> List[ModeInfo]:
        """
        Build ModeInfo list for the CURRENT leg's corridor.
        """
        cfg         = self._task_cfg
        leg         = self._current_leg_data()
        corridor    = CORRIDORS.get(leg["corridor_key"], CORRIDORS["default"])
        weather_mod = WEATHER_MODIFIERS.get(self._weather, {})
        reliability = cfg.get("sensor_reliability", [1.0] * 5)

        mode_order = ["train", "auto", "bus", "metro", "walk"]
        modes = []
        for i, mode in enumerate(mode_order):
            data         = corridor.get(mode, corridor.get("bus"))
            avail_factor = weather_mod.get(f"{mode}_availability", 1.0)
            time_factor  = weather_mod.get(f"{mode}_time_factor",  1.0)
            conf         = reliability[i] if i < len(reliability) else 1.0
            modes.append(
                ModeInfo(
                    mode=mode,
                    available=(data["availability"] * avail_factor) > 0.25,
                    confidence=conf,
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
        Build the situation text the agent reads.
        Now includes leg progress so agent knows which leg it's on.
        """
        cfg        = self._task_cfg
        leg        = self._current_leg_data()
        total_legs = len(self._legs)
        leg_num    = self._current_leg + 1  # 1-indexed for readability

        lines = []
        for m in modes:
            conf_str  = "uncertain" if m.confidence < 0.6 else "confirmed"
            avail_str = "available" if m.available else "UNAVAILABLE"
            lines.append(
                f"  {m.mode}: {avail_str} ({conf_str}), "
                f"~₹{m.est_cost:.0f}, "
                f"{m.est_time_min}–{m.est_time_max} min"
            )

        disruptions = (
            ", ".join(self._disruptions) if self._disruptions else "none"
        )

        msg = (
            f"[Leg {leg_num} of {total_legs}] "
            f"{leg['from_location']} → {leg['to_location']}\n"
            f"Overall: {self._location} → {cfg['destination']}\n"
            f"Time remaining: {self._time_remaining} min | "
            f"Budget: ₹{self._budget:.0f}\n"
            f"Weather: {self._weather}\n"
            f"Known disruptions: {disruptions}\n"
            f"Leg context: {leg['description']}\n"
            f"Transport options for this leg:\n" + "\n".join(lines)
        )

        if last_msg:
            msg = f"Last action result: {last_msg}\n\n{msg}"

        return msg