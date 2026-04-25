from fastapi.testclient import TestClient

from server.app import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_task_catalog_available_on_both_routes():
    expected_keys = {"easy", "medium", "hard", "bonus"}

    task_response = client.get("/task")
    tasks_response = client.get("/tasks")

    assert task_response.status_code == 200
    assert tasks_response.status_code == 200
    assert set(task_response.json().keys()) == expected_keys
    assert set(tasks_response.json().keys()) == expected_keys
    assert task_response.json() == tasks_response.json()