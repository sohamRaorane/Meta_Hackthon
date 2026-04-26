import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import requests

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")
TASKS = ["easy", "medium", "hard", "bonus"]
TASK_SEEDS = {"easy": 42, "medium": 7, "hard": 13, "bonus": 99}


@dataclass
class CheckResult:
    task: str
    endpoint: str
    ok: bool
    details: str


def _get(path: str) -> requests.Response:
    return requests.get(f"{SERVER_URL}{path}", timeout=20)


def _post(path: str, payload: dict) -> requests.Response:
    return requests.post(f"{SERVER_URL}{path}", json=payload, timeout=30)


def check_global_endpoints() -> List[CheckResult]:
    results: List[CheckResult] = []

    try:
        r = _get("/health")
        data = r.json()
        ok = r.status_code == 200 and data.get("status") == "healthy"
        results.append(CheckResult("ALL", "/health", ok, json.dumps(data)))
    except Exception as e:
        results.append(CheckResult("ALL", "/health", False, str(e)))

    try:
        r = _get("/tasks")
        data = r.json()
        ok = r.status_code == 200 and all(task in data for task in TASKS)
        results.append(CheckResult("ALL", "/tasks", ok, f"keys={list(data.keys())}"))
    except Exception as e:
        results.append(CheckResult("ALL", "/tasks", False, str(e)))

    return results


def check_task_flow(task_name: str, seed: int) -> List[CheckResult]:
    results: List[CheckResult] = []

    episode_id = ""
    try:
        r = _post("/reset", {"task_name": task_name, "seed": seed})
        data = r.json()
        obs = data.get("observation", {})
        episode_id = obs.get("episode_id", "")
        has_obs = isinstance(obs, dict) and bool(episode_id)
        ok = r.status_code == 200 and has_obs and obs.get("echoed_message")
        results.append(CheckResult(task_name, "/reset", bool(ok), f"episode_id={episode_id}"))
    except Exception as e:
        results.append(CheckResult(task_name, "/reset", False, str(e)))
        return results

    if not episode_id:
        results.append(CheckResult(task_name, "/step", False, "missing episode_id from reset"))
        return results

    try:
        payload = {
            "episode_id": episode_id,
            "action": {"message": "Choose best mode considering full trip budget and remaining legs"},
        }
        r = _post("/step", payload)
        data = r.json()
        obs = data.get("observation", {})
        ok = r.status_code == 200 and isinstance(obs, dict) and "echoed_message" in obs and "reward" in data and "done" in data
        results.append(CheckResult(task_name, "/step", bool(ok), f"reward={data.get('reward')} done={data.get('done')}"))
    except Exception as e:
        results.append(CheckResult(task_name, "/step", False, str(e)))

    return results


def print_table(rows: List[CheckResult]) -> None:
    print("\n=== ENVIRONMENT VALIDATION ===")
    print(f"{'task':<8} {'endpoint':<8} {'status':<6} details")
    print("-" * 72)
    for row in rows:
        status = "PASS" if row.ok else "FAIL"
        print(f"{row.task:<8} {row.endpoint:<8} {status:<6} {row.details}")


def main() -> int:
    all_rows: List[CheckResult] = []
    all_rows.extend(check_global_endpoints())

    for task in TASKS:
        all_rows.extend(check_task_flow(task, TASK_SEEDS[task]))

    print_table(all_rows)

    failed = [r for r in all_rows if not r.ok]
    if failed:
        print("\nValidation result: FAIL")
        return 1

    print("\nValidation result: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
