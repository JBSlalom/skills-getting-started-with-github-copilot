import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app, activities

client = TestClient(app)


def test_unregister_existing_participant():
    """Test unregistering an existing participant"""
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    
    # Verify participant exists before unregistering
    assert email in activities[activity_name]["participants"]
    
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    
    # Verify participant was removed
    assert email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_participant():
    """Test unregistering a participant who isn't registered"""
    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"]


def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.post(
        "/activities/Fake Club/unregister",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_updates_participant_count():
    """Test that unregister correctly updates participant count"""
    activity_name = "Art Studio"
    email = "isabella@mergington.edu"
    
    initial_count = len(activities[activity_name]["participants"])
    
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    assert len(activities[activity_name]["participants"]) == initial_count - 1


def test_signup_then_unregister():
    """Test the flow of signing up and then unregistering"""
    activity_name = "Debate Team"
    email = "tempstudent@mergington.edu"
    
    # Sign up
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    assert email in activities[activity_name]["participants"]
    
    # Unregister
    unregister_response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    assert unregister_response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_multiple_participants():
    """Test unregistering multiple participants from the same activity"""
    activity_name = "Debate Team"
    emails = ["lucas@mergington.edu", "mia@mergington.edu"]
    
    for email in emails:
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    
    # Verify both were removed
    for email in emails:
        assert email not in activities[activity_name]["participants"]
