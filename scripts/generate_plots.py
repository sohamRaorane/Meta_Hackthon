import json
import os
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np


TASKS = ["easy", "medium", "hard", "bonus"]


def load_results(path: str) -> Optional[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: missing file {path}")
        return None


def task_map(data: Optional[dict]) -> Dict[str, dict]:
    if not data:
        return {}
    return {t.get("task_name", ""): t for t in data.get("tasks", [])}


def annotate_bars(ax, bars) -> None:
    for bar in bars:
        height = bar.get_height()
        if np.isnan(height):
            continue
        ax.annotate(
            f"{height:.3f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def main() -> None:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(root_dir, "results")
    plots_dir = os.path.join(results_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    baseline_path = os.path.join(results_dir, "baseline_results.json")
    post_path = os.path.join(results_dir, "post_training_results.json")

    baseline_data = load_results(baseline_path)
    post_data = load_results(post_path)

    if baseline_data is None and post_data is None:
        print("Warning: neither baseline nor post-training result file exists. No plots generated.")
        return

    if post_data is None:
        print("Note: post-training results missing. Generating baseline-only plots.")

    baseline_by_task = task_map(baseline_data)
    post_by_task = task_map(post_data)

    baseline_scores = np.array([float(baseline_by_task.get(t, {}).get("score", np.nan)) for t in TASKS], dtype=float)
    post_scores = np.array([float(post_by_task.get(t, {}).get("score", np.nan)) for t in TASKS], dtype=float)

    # Plot 1: Score comparison
    x = np.arange(len(TASKS))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    baseline_bars = ax.bar(x - width / 2, baseline_scores, width, label="baseline", color="tab:blue")
    if post_data is not None:
        post_bars = ax.bar(x + width / 2, post_scores, width, label="post_training", color="tab:orange")
    else:
        post_bars = []

    ax.set_xticks(x)
    ax.set_xticklabels(TASKS)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Normalized Score")
    title_suffix = "" if post_data is not None else " (baseline only)"
    ax.set_title(f"Agent Score: Baseline vs Post-Training{title_suffix}")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend()
    annotate_bars(ax, baseline_bars)
    if post_data is not None:
        annotate_bars(ax, post_bars)
    fig.tight_layout()
    fig.savefig(os.path.join(plots_dir, "score_comparison.png"), dpi=150)
    plt.close(fig)

    # Plot 2: Reward curves
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=False, sharey=False)
    axes = axes.flatten()
    for i, task_name in enumerate(TASKS):
        ax = axes[i]
        b_rewards: List[float] = baseline_by_task.get(task_name, {}).get("rewards", [])
        p_rewards: List[float] = post_by_task.get(task_name, {}).get("rewards", [])

        if b_rewards:
            b_x = np.arange(1, len(b_rewards) + 1)
            ax.plot(b_x, b_rewards, marker="o", color="tab:blue", label="baseline")
        if post_data is not None and p_rewards:
            p_x = np.arange(1, len(p_rewards) + 1)
            ax.plot(p_x, p_rewards, marker="o", color="tab:orange", label="post_training")

        b_score = baseline_by_task.get(task_name, {}).get("score", np.nan)
        if post_data is not None:
            p_score = post_by_task.get(task_name, {}).get("score", np.nan)
            ax.set_title(f"{task_name} | b={b_score:.3f}, p={p_score:.3f}")
        else:
            ax.set_title(f"{task_name} | b={b_score:.3f}")

        ax.axhline(0, linestyle="--", color="gray", linewidth=1)
        ax.set_xlabel("Step")
        ax.set_ylabel("Reward")
        ax.grid(alpha=0.3)
        if b_rewards or (post_data is not None and p_rewards):
            ax.legend(fontsize=8)

    fig.suptitle("Per-Task Reward Curves")
    fig.tight_layout()
    fig.savefig(os.path.join(plots_dir, "reward_curves.png"), dpi=150)
    plt.close(fig)

    # Plot 3: Improvement heatmap
    if post_data is not None:
        heat_values = np.vstack([baseline_scores, post_scores])
        row_labels = ["baseline", "post_training"]
        heat_title = "Score Heatmap: Before and After Training"
    else:
        heat_values = np.vstack([baseline_scores])
        row_labels = ["baseline"]
        heat_title = "Score Heatmap: Before and After Training (baseline only)"

    fig, ax = plt.subplots(figsize=(10, 3 if post_data is not None else 2.3))
    im = ax.imshow(heat_values, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(TASKS)))
    ax.set_xticklabels(TASKS)
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels)
    ax.set_title(heat_title)

    for r in range(heat_values.shape[0]):
        for c in range(heat_values.shape[1]):
            val = heat_values[r, c]
            text = "N/A" if np.isnan(val) else f"{val:.3f}"
            ax.text(c, r, text, ha="center", va="center", color="black", fontsize=9)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(os.path.join(plots_dir, "improvement_heatmap.png"), dpi=150)
    plt.close(fig)

    # Plot 4: Success rate
    baseline_success = np.array([1.0 if baseline_by_task.get(t, {}).get("success", False) else 0.0 for t in TASKS], dtype=float)
    post_success = np.array([1.0 if post_by_task.get(t, {}).get("success", False) else np.nan for t in TASKS], dtype=float)

    fig, ax = plt.subplots(figsize=(10, 5))
    b_bars = ax.bar(x - width / 2, baseline_success, width, label="baseline", color="tab:blue")
    if post_data is not None:
        p_bars = ax.bar(x + width / 2, post_success, width, label="post_training", color="tab:orange")
    else:
        p_bars = []

    ax.set_xticks(x)
    ax.set_xticklabels(TASKS)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Success")
    ax.set_title("Task Success Rate")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend()

    for bar in b_bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, f"{bar.get_height():.0f}", ha="center", fontsize=9)
    if post_data is not None:
        for bar in p_bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, f"{bar.get_height():.0f}", ha="center", fontsize=9)

    fig.tight_layout()
    fig.savefig(os.path.join(plots_dir, "success_rate.png"), dpi=150)
    plt.close(fig)

    print(f"Saved plots to {plots_dir}")


if __name__ == "__main__":
    main()
