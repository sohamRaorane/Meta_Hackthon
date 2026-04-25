from __future__ import annotations

from typing import Any


def _clamp01(value: float) -> float:
    """Clamp to strictly open interval (0, 1) — 0.0 and 1.0 are not valid."""
    clamped = max(0.0, min(1.0, round(value, 4)))
    if clamped <= 0.0:
        return 0.001
    if clamped >= 1.0:
        return 0.999
    return clamped


def _base_grade(final_observation: dict[str, Any], rewards: list[float], steps_taken: int) -> float:
    reached = (
    final_observation.get("reached", False) or
    final_observation.get("current_location") == final_observation.get("destination")
)
    time_left = max(0.0, float(final_observation.get("time_remaining_minutes", 0)))
    budget_left = float(final_observation.get("budget_remaining", 0.0))

    success_score = 0.6 if reached else 0.0
    reward_score = 0.25 * _clamp01(sum(rewards) / 2.5)
    time_score = 0.1 * _clamp01(time_left / 90.0)
    budget_score = 0.05 * _clamp01(max(0.0, budget_left) / 120.0)

    # Mild penalty for excessive wandering.
    step_penalty = 0.03 * max(0, steps_taken - 4)
    return _clamp01(success_score + reward_score + time_score + budget_score - step_penalty)


def grade_easy(final_observation: dict[str, Any], rewards: list[float], steps_taken: int) -> float:
    return _base_grade(final_observation, rewards, steps_taken)


def grade_medium(final_observation: dict[str, Any], rewards: list[float], steps_taken: int) -> float:
    base = _base_grade(final_observation, rewards, steps_taken)
    # Medium expects better handling under constraints.
    return _clamp01(base * 0.95)


def grade_hard(final_observation: dict[str, Any], rewards: list[float], steps_taken: int) -> float:
    base = _base_grade(final_observation, rewards, steps_taken)
    # Hard task keeps a stricter cap.
    return _clamp01(base * 0.9)


def grade_bonus(final_observation: dict[str, Any], rewards: list[float], steps_taken: int) -> float:
    # Bonus uses same rubric as medium due tight budget dynamics.
    return grade_medium(final_observation, rewards, steps_taken)


def grade_task(task_name: str, final_observation: dict[str, Any], rewards: list[float], steps_taken: int) -> float:
    graders = {
        "easy": grade_easy,
        "medium": grade_medium,
        "hard": grade_hard,
        "bonus": grade_bonus,
    }
    grader = graders.get(task_name, grade_easy)
    return grader(final_observation, rewards, steps_taken)
