# server/graders.py
# ─────────────────────────────────────────────────────────────────────────────
# Deterministic episode grader for Mumbai Last-Mile Crisis Response.
#
# Phase 0 fix (issue #1):
#   The old grader used string comparison:
#     reached = obs["current_location"] == obs["destination"]
#   This silently fails on multi-leg journeys where current_location updates
#   to each waypoint, not the final destination string, until the very last leg.
#   Result: episodes that genuinely succeeded were scored as failures.
#
#   Fix: environment now passes reached: bool explicitly in the observation
#   payload. Grader reads obs["reached"] — a bool set by the environment's
#   internal self._reached flag, which is only True when ALL legs complete.
#
# Rubric (applied identically across all tasks, scaled by difficulty):
#   60% — success bonus (reached final destination)
#   20% — cumulative reward quality (normalised to task ceiling)
#   10% — time buffer (arrived early = higher score)
#   10% — budget efficiency (money left proportional to starting budget)
#   Difficulty multiplier: easy=1.0, medium=0.95, hard=0.88, bonus=0.93
#
# Output contract: score is STRICTLY in (0.001, 0.999).
#   0.0 and 1.0 are rejected by the Phase 2 validator.
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from typing import Any

# Per-task reward ceilings — used to normalise cumulative reward to [0, 1].
# These match MAX_REWARD_PER_TASK in inference.py exactly.
_TASK_REWARD_CEILING: dict[str, float] = {
    "easy":   2.0,
    "medium": 2.0,
    "hard":   2.5,
    "bonus":  2.0,
}

# Difficulty multipliers applied to the base score.
# Hard task has stricter cap — a frontier model should still struggle.
_DIFFICULTY_MULTIPLIER: dict[str, float] = {
    "easy":   1.00,
    "medium": 0.95,
    "hard":   0.88,
    "bonus":  0.93,
}


def _strict_clamp(value: float) -> float:
    """
    Clamp to the OPEN interval (0.001, 0.999).

    The Phase 2 validator rejects scores of exactly 0.0 or 1.0.
    This function guarantees we never produce those boundary values.
    """
    return round(max(0.001, min(0.999, value)), 4)


def _base_grade(
    task_name: str,
    final_observation: dict[str, Any],
    rewards: list[float],
    steps_taken: int,
) -> float:
    """
    Core rubric shared by all task graders.

    Parameters
    ----------
    task_name:
        One of "easy" / "medium" / "hard" / "bonus".
    final_observation:
        The last observation dict returned by the environment.
        Must contain the "reached" bool key (added in Phase 0).
    rewards:
        List of per-step reward floats for this episode.
    steps_taken:
        Number of steps the agent took (including failed ones).

    Returns
    -------
    float in (0.001, 0.999)
    """
    # ── Component 1: Success (60%) ──────────────────────────────────────────
    # Read the explicit reached bool — DO NOT use string comparison.
    # String compare silently fails when current_location is a waypoint.
    reached: bool = bool(final_observation.get("reached", False))
    success_score = 0.60 if reached else 0.0

    # ── Component 2: Cumulative reward quality (20%) ────────────────────────
    # Normalise total reward against the task ceiling so this component
    # always contributes between 0 and 0.20 regardless of task difficulty.
    ceiling = _TASK_REWARD_CEILING.get(task_name, 2.0)
    cumulative = sum(rewards)
    reward_score = 0.20 * _strict_clamp(cumulative / ceiling)

    # ── Component 3: Time buffer (10%) ──────────────────────────────────────
    # Agents that arrive early score higher here.
    # Normalised against 90 minutes — the longest task time limit.
    time_left = max(0.0, float(final_observation.get("time_remaining_minutes", 0)))
    time_score = 0.10 * _strict_clamp(time_left / 90.0)

    # ── Component 4: Budget efficiency (10%) ────────────────────────────────
    # Agents that conserve budget score higher here.
    # Normalised against 120 — the largest starting budget (easy task).
    budget_left = float(final_observation.get("budget_remaining", 0.0))
    budget_score = 0.10 * _strict_clamp(max(0.0, budget_left) / 120.0)

    # ── Step penalty ────────────────────────────────────────────────────────
    # Mild penalty for excessive steps — discourages trial-and-error agents.
    # Capped at 0.12 so it cannot wipe out a successful run.
    step_penalty = min(0.04 * max(0, steps_taken - 3), 0.12)

    raw = success_score + reward_score + time_score + budget_score - step_penalty

    # Apply difficulty multiplier before clamping.
    multiplier = _DIFFICULTY_MULTIPLIER.get(task_name, 1.0)
    return _strict_clamp(raw * multiplier)


# ── Public grader functions ───────────────────────────────────────────────────

def grade_easy(
    final_observation: dict[str, Any],
    rewards: list[float],
    steps_taken: int,
) -> float:
    """Grade an easy-task episode. Full multiplier (1.0)."""
    return _base_grade("easy", final_observation, rewards, steps_taken)


def grade_medium(
    final_observation: dict[str, Any],
    rewards: list[float],
    steps_taken: int,
) -> float:
    """Grade a medium-task episode. 0.95 difficulty multiplier."""
    return _base_grade("medium", final_observation, rewards, steps_taken)


def grade_hard(
    final_observation: dict[str, Any],
    rewards: list[float],
    steps_taken: int,
) -> float:
    """Grade a hard-task episode. 0.88 difficulty multiplier."""
    return _base_grade("hard", final_observation, rewards, steps_taken)


def grade_bonus(
    final_observation: dict[str, Any],
    rewards: list[float],
    steps_taken: int,
) -> float:
    """Grade a bonus-task episode. 0.93 difficulty multiplier."""
    return _base_grade("bonus", final_observation, rewards, steps_taken)


def grade_task(
    task_name: str,
    final_observation: dict[str, Any],
    rewards: list[float],
    steps_taken: int,
) -> float:
    """
    Single entry point for all graders.

    Called by inference.py after each episode completes.
    Also called by the hackathon validator to verify score range.

    Parameters
    ----------
    task_name:
        Must be one of "easy" / "medium" / "hard" / "bonus".
        Unknown names fall back to grade_easy.
    final_observation:
        The last observation dict from the episode.
    rewards:
        List of per-step floats from the episode.
    steps_taken:
        Total steps taken including failed mode attempts.

    Returns
    -------
    float strictly in (0.001, 0.999) — never 0.0 or 1.0.
    """
    dispatch = {
        "easy":   grade_easy,
        "medium": grade_medium,
        "hard":   grade_hard,
        "bonus":  grade_bonus,
    }
    grader = dispatch.get(task_name, grade_easy)
    return grader(final_observation, rewards, steps_taken)