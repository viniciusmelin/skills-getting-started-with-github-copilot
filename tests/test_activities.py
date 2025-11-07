import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    """Make a deep copy of the activities dict and restore after each test so tests are isolated."""
    snapshot = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(snapshot)


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect at least one known activity
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister_flow():
    client = TestClient(app)
    activity = "Chess Club"
    # Avoid special characters that are interpreted in query strings; use underscore
    email = "testuser_signup@example.com"

    # Ensure email not already present
    assert email not in activities[activity]["participants"]

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body["message"]
    assert email in activities[activity]["participants"]

    # Duplicate signup returns 400
    resp_dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp_dup.status_code == 400

    # Unregister
    resp_un = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp_un.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_existing_returns_400():
    client = TestClient(app)
    activity = "Chess Club"
    existing = activities[activity]["participants"][0]

    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_nonexistent_returns_400():
    client = TestClient(app)
    activity = "Chess Club"
    nonexist = "doesnotexist@example.com"

    # Ensure nonexist not present
    assert nonexist not in activities[activity]["participants"]

    resp = client.post(f"/activities/{activity}/unregister?email={nonexist}")
    assert resp.status_code == 400
