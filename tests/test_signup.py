import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app, activities

client = TestClient(app)


def test_signup_new_participant():
    """Test signing up a new participant for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    
    # Verify participant was added
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant():
    """Test that duplicate signups are rejected"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/Fake Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_updates_participant_count():
    """Test that signup correctly updates participant count"""
    activity_name = "Basketball Team"
    initial_count = len(activities[activity_name]["participants"])
    
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "newplayer@mergington.edu"}
    )
    
    assert response.status_code == 200
    assert len(activities[activity_name]["participants"]) == initial_count + 1


def test_signup_at_capacity():
    """Test that we can still sign up even at capacity (no limit enforcement in current code)"""
    # Note: The current implementation doesn't enforce max_participants limit
    # This test documents current behavior
    response = client.post(
        "/activities/Tennis Club/signup",
        params={"email": "student1@mergington.edu"}
    )
    assert response.status_code == 200


def test_multiple_signups():
    """Test signing up multiple different participants"""
    emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
    
    for email in emails:
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all were added
    participants = activities["Programming Class"]["participants"]
    for email in emails:
        assert email in participants
