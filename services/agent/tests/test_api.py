from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "agent"}


def test_api_lists_seeded_properties():
    client = TestClient(app)

    response = client.get("/properties")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["id"] == "prop-a"
    assert any(item["id"] == "prop-b" for item in body)


def test_api_starts_task_and_returns_approval_state():
    client = TestClient(app)

    response = client.post(
        "/tasks",
        json={
            "property_id": "prop-b",
            "task": "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "waiting_approval"
    assert body["approval_required"] is True
    assert body["approval_request"]["cost_estimate"] == 850


def test_api_approves_waiting_task():
    client = TestClient(app)
    created = client.post(
        "/tasks",
        json={
            "property_id": "prop-b",
            "task": "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
        },
    ).json()

    response = client.post(f"/tasks/{created['id']}/approve")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"

