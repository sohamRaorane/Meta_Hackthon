import json
import os
from typing import Dict, List

BASELINE_PATH = os.path.join("results", "baseline_results.json")
POST_PATH = os.path.join("results", "post_training_results.json")


def _load(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _pct(before: float, after: float) -> str:
    if abs(before) < 1e-9:
        if abs(after) < 1e-9:
            return "0.0%"
        return "N/A"
    change = ((after - before) / abs(before)) * 100.0
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.1f}%"


def main() -> int:
    if not os.path.exists(BASELINE_PATH):
        print(f"Missing baseline file: {BASELINE_PATH}")
        return 1
    if not os.path.exists(POST_PATH):
        print(f"Missing post-training file: {POST_PATH}")
        return 1

    baseline = _load(BASELINE_PATH)
    post = _load(POST_PATH)

    base_tasks = {t["task_name"]: t for t in baseline.get("tasks", [])}
    post_tasks = {t["task_name"]: t for t in post.get("tasks", [])}

    ordered_tasks: List[str] = ["easy", "medium", "hard", "bonus"]

    print("\n=== BASELINE vs POST-TRAINING ===")
    print(f"baseline_model: {baseline.get('model_name')}")
    print(f"post_model:     {post.get('model_name')}")
    print(f"{'task':<10} {'base_score':<11} {'post_score':<11} {'delta':<9} {'pct':<8} {'base_sr':<9} post_sr")

    for task in ordered_tasks:
        b = base_tasks.get(task, {})
        p = post_tasks.get(task, {})

        b_score = float(b.get("mean_score", b.get("score", 0.0)))
        p_score = float(p.get("mean_score", p.get("score", 0.0)))
        delta = p_score - b_score
        delta_str = f"{delta:+.4f}"

        b_sr = float(b.get("success_rate", 1.0 if b.get("success") else 0.0))
        p_sr = float(p.get("success_rate", 1.0 if p.get("success") else 0.0))

        print(
            f"{task:<10} {b_score:<11.4f} {p_score:<11.4f} {delta_str:<9} {_pct(b_score, p_score):<8} "
            f"{b_sr:<9.1%} {p_sr:.1%}"
        )

    b_avg = float(baseline.get("avg_score", 0.0))
    p_avg = float(post.get("avg_score", 0.0))
    print("-" * 80)
    print(f"{'avg':<10} {b_avg:<11.4f} {p_avg:<11.4f} {p_avg - b_avg:+.4f} {_pct(b_avg, p_avg)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
