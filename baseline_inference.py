import json
import os
from datetime import datetime
from typing import Dict, List

from openai import OpenAI

import inference

EPISODES_PER_TASK = int(os.getenv("BASELINE_EPISODES", "20"))
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
BASELINE_PATH = os.path.join(RESULTS_DIR, "baseline_results.json")
PRETRAIN_LOGS_PATH = os.path.join(RESULTS_DIR, "pre_training_logs.json")


def run_baseline() -> Dict:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    client = OpenAI(base_url=inference.API_BASE_URL, api_key=inference.API_KEY)

    task_summaries: List[Dict] = []
    full_logs: Dict[str, List[Dict]] = {}

    for task_name in inference.TASKS:
        base_seed = inference.TASK_SEEDS[task_name]
        episodes: List[Dict] = []

        for i in range(EPISODES_PER_TASK):
            seed = base_seed + i
            result = inference.run_task(task_name, seed, client)
            episodes.append(
                {
                    "episode_index": i + 1,
                    "seed": seed,
                    "score": result["score"],
                    "steps": result["steps"],
                    "success": result["success"],
                    "rewards": result["rewards"],
                    "total_reward": round(sum(result["rewards"]), 3),
                    "grader_score": result["grader_score"],
                }
            )

        full_logs[task_name] = episodes

        mean_score = round(sum(e["score"] for e in episodes) / len(episodes), 4)
        success_rate = round(sum(1 for e in episodes if e["success"]) / len(episodes), 4)
        mean_reward = round(sum(e["total_reward"] for e in episodes) / len(episodes), 4)

        task_summaries.append(
            {
                "task_name": task_name,
                "episodes": EPISODES_PER_TASK,
                "mean_score": mean_score,
                "success_rate": success_rate,
                "mean_total_reward": mean_reward,
            }
        )

    baseline_payload = {
        "phase": "baseline",
        "model_name": inference.MODEL_NAME,
        "environment": inference.BENCHMARK,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "episodes_per_task": EPISODES_PER_TASK,
        "tasks": task_summaries,
        "avg_score": round(sum(t["mean_score"] for t in task_summaries) / len(task_summaries), 4),
        "tasks_total": len(task_summaries),
    }

    pretrain_logs_payload = {
        "phase": "pre_training_logs",
        "model_name": inference.MODEL_NAME,
        "environment": inference.BENCHMARK,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "episodes_per_task": EPISODES_PER_TASK,
        "logs": full_logs,
    }

    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(baseline_payload, f, indent=2)

    with open(PRETRAIN_LOGS_PATH, "w", encoding="utf-8") as f:
        json.dump(pretrain_logs_payload, f, indent=2)

    return baseline_payload


def main() -> int:
    payload = run_baseline()

    print("\n=== BASELINE (PRE-TRAINING) SUMMARY ===")
    print(f"model: {payload['model_name']}")
    print(f"episodes_per_task: {payload['episodes_per_task']}")
    print(f"{'task':<10} {'mean_score':<11} {'success_rate':<12} mean_total_reward")
    for task in payload["tasks"]:
        print(
            f"{task['task_name']:<10} {task['mean_score']:<11.4f} "
            f"{task['success_rate']:<12.1%} {task['mean_total_reward']:.4f}"
        )

    print(f"\nSaved baseline JSON: {BASELINE_PATH}")
    print(f"Saved pre-training logs JSON: {PRETRAIN_LOGS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
