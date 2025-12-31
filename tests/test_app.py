import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    # Backup the activities state and restore after each test to avoid cross-test pollution
    original = copy.deepcopy(app_module.activities)
    client = TestClient(app_module.app)
    yield client
    app_module.activities = original


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Some known activities present
    assert "Chess Club" in data


def test_signup_and_unregister(client):
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure email not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Sign up
    signup_resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")

    # Verify participant is listed
    resp_after = client.get("/activities")
    assert email in resp_after.json()[activity]["participants"]

    # Unregister
    unregister_resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert unregister_resp.status_code == 200
    assert "Unregistered" in unregister_resp.json().get("message", "")

    # Verify participant removed
    resp_final = client.get("/activities")
    assert email not in resp_final.json()[activity]["participants"]
