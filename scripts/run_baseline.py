import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI

from inference import API_BASE_URL, API_KEY, MODEL_NAME, TASK_SEEDS, TASKS, run_task


def main() -> None:
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    task_results = []
    for task_name in TASKS:
        result = run_task(task_name, TASK_SEEDS[task_name], client)
        task_results.append(
            {
                "task_name": result["task_name"],
                "score": result["score"],
                "steps": result["steps"],
                "success": result["success"],
                "rewards": result["rewards"],
                "total_reward": round(sum(result["rewards"]), 3),
                "grader_score": result["grader_score"],
            }
        )

    avg_score = round(sum(t["score"] for t in task_results) / len(task_results), 3) if task_results else 0.0
    payload = {
        "phase": "baseline",
        "model_name": MODEL_NAME,
        "environment": "mumbai-lastmile",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tasks": task_results,
        "avg_score": avg_score,
        "tasks_succeeded": sum(1 for t in task_results if t["success"]),
        "tasks_total": len(task_results),
    }

    output_path = os.path.join(results_dir, "baseline_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print("=== BASELINE RESULTS ===")
    print(f"{'task':<10} {'score':<8} {'steps':<5} success")
    for task in task_results:
        success_text = str(task["success"]).lower()
        print(f"{task['task_name']:<10} {task['score']:<8.3f} {task['steps']:<5} {success_text}")
    print(f"{'avg_score':<10} {avg_score:<8.3f}")


if __name__ == "__main__":
    main()
