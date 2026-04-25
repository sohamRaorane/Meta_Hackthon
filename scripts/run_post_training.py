import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI

from inference import API_BASE_URL, API_KEY, MODEL_NAME, TASK_SEEDS, TASKS, run_task


def pct_change_str(baseline: float, post: float) -> str:
    delta = post - baseline
    if baseline <= 0:
        if delta > 0:
            return "+999.0%"
        if delta < 0:
            return "-999.0%"
        return "+0.0%"

    pct = (delta / baseline) * 100.0
    if pct > 999:
        pct = 999
    if pct < -999:
        pct = -999
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def main() -> None:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(root_dir, "results")
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
        "phase": "post_training",
        "model_name": MODEL_NAME,
        "environment": "mumbai-lastmile",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tasks": task_results,
        "avg_score": avg_score,
        "tasks_succeeded": sum(1 for t in task_results if t["success"]),
        "tasks_total": len(task_results),
    }

    output_path = os.path.join(results_dir, "post_training_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    baseline_path = os.path.join(results_dir, "baseline_results.json")
    try:
        with open(baseline_path, "r", encoding="utf-8") as f:
            baseline_data = json.load(f)
    except FileNotFoundError:
        print("Warning: results/baseline_results.json not found. Skipping comparison.")
        return

    baseline_by_task = {t["task_name"]: t for t in baseline_data.get("tasks", [])}
    post_by_task = {t["task_name"]: t for t in task_results}

    print("=== IMPROVEMENT SUMMARY ===")
    print(f"{'task':<10} {'baseline':<9} {'post_training':<13} {'delta':<7} pct_change")

    baseline_scores = []
    post_scores = []
    for task_name in TASKS:
        b = float(baseline_by_task.get(task_name, {}).get("score", 0.0))
        p = float(post_by_task.get(task_name, {}).get("score", 0.0))
        delta = p - b
        delta_sign = "+" if delta >= 0 else ""
        print(
            f"{task_name:<10} {b:<9.3f} {p:<13.3f} {delta_sign}{delta:<7.3f} {pct_change_str(b, p)}"
        )
        baseline_scores.append(b)
        post_scores.append(p)

    baseline_avg = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0.0
    post_avg = sum(post_scores) / len(post_scores) if post_scores else 0.0
    avg_delta = post_avg - baseline_avg
    avg_delta_sign = "+" if avg_delta >= 0 else ""
    print(
        f"{'avg':<10} {baseline_avg:<9.3f} {post_avg:<13.3f} {avg_delta_sign}{avg_delta:<7.3f} {pct_change_str(baseline_avg, post_avg)}"
    )


if __name__ == "__main__":
    main()
