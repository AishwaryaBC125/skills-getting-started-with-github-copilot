import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # At least one known activity exists
    assert "Chess Club" in data


def test_signup_and_prevent_duplicate():
    activity = "Chess Club"
    email = "testuser@mergington.edu"

    # Ensure clean state
    if activity in activities and "participants" in activities[activity]:
        if email in activities[activity]["participants"]:
            activities[activity]["participants"].remove(email)

    # Signup should succeed
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]

    # Duplicate signup should be rejected
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400
    assert "already" in resp2.json().get("detail", "").lower()
    # Cleanup
    if activity in activities and "participants" in activities[activity]:
        if email in activities[activity]["participants"]:
            activities[activity]["participants"].remove(email)
    activities[activity]["participants"].remove(email)


def test_unregister_participant():
    # Ensure participant is present
    if activity in activities and "participants" in activities[activity]:
        if email not in activities[activity]["participants"]:
            activities[activity]["participants"].append(email)
    # Ensure participant is present
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]

    # Deleting again should return 404
    resp2 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp2.status_code == 404


@pytest.mark.asyncio
async def test_async_client_signup_and_unregister():
    # Use httpx AsyncClient to exercise async flow (if any)
    import httpx
    # Cleanup from previous runs
    if activity in activities and "participants" in activities[activity]:
        if email in activities[activity]["participants"]:
            activities[activity]["participants"].remove(email)

    # Cleanup from previous runs
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post(f"/activities/{activity}/signup?email={email}")
        assert r.status_code == 200
        assert email in activities[activity]["participants"]

        r2 = await ac.delete(f"/activities/{activity}/participants?email={email}")
        assert r2.status_code == 200
        assert email not in activities[activity]["participants"]
