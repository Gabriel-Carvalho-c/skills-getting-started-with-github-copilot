import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from fastapi.testclient import TestClient
from app import app, activities
import copy

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

def test_signup_success():
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@mergington.edu for Chess Club" in data["message"]

    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "test@mergington.edu" in data["Chess Club"]["participants"]

def test_signup_activity_not_found():
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    # Second
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]

def test_signup_activity_full():
    # Chess Club has max 12, currently 2 participants
    for i in range(10):
        email = f"user{i}@mergington.edu"
        client.post(f"/activities/Chess%20Club/signup?email={email}")
    # Now should be full
    response = client.post("/activities/Chess%20Club/signup?email=last@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "Activity is full" in data["detail"]

def test_unregister_success():
    # First signup
    client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    # Then unregister
    response = client.delete("/activities/Chess%20Club/participants/test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered test@mergington.edu from Chess Club" in data["message"]

    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "test@mergington.edu" not in data["Chess Club"]["participants"]

def test_unregister_activity_not_found():
    response = client.delete("/activities/NonExistent/participants/test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Chess%20Club/participants/notsigned@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "Student not signed up for this activity" in data["detail"]