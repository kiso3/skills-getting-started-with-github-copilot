"""
Tests for the Mergington High School Activities API
Using the AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        # Arrange
        expected_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert len(data) > 0
        first_activity = next(iter(data.values()))
        assert expected_keys.issubset(first_activity.keys())

    def test_get_activities_contains_chess_club(self):
        """Test that Chess Club is in activities"""
        # Arrange
        expected_activity = "Chess Club"
        expected_description = "Learn strategies and compete in chess tournaments"

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert expected_activity in data
        assert data[expected_activity]["description"] == expected_description


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent123@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        result = response.json()

        # Assert
        assert response.status_code == 200
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_signup_duplicate_email(self):
        """Test signup fails when student is already registered"""
        # Arrange
        activity_name = "Programming Class"
        email = "duplicate@mergington.edu"
        
        # Act - First signup
        response_first = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        # Act - Second signup with same email
        response_second = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        result = response_second.json()

        # Assert
        assert response_first.status_code == 200
        assert response_second.status_code == 400
        assert "already signed up" in result["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signup fails for non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        result = response.json()

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in result["detail"]


class TestRemoveParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_remove_participant_success(self):
        """Test successful removal of a participant"""
        # Arrange
        activity_name = "Soccer Team"
        email = "removetest@mergington.edu"
        # First, sign up the participant
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        result = response.json()

        # Assert
        assert response.status_code == 200
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_remove_nonexistent_participant(self):
        """Test removal fails when participant is not in activity"""
        # Arrange
        activity_name = "Basketball Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        result = response.json()

        # Assert
        assert response.status_code == 400
        assert "Participant not found" in result["detail"]

    def test_remove_from_nonexistent_activity(self):
        """Test removal fails for non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        result = response.json()

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in result["detail"]

    def test_remove_then_signup_again(self):
        """Test that a removed participant can sign up again"""
        # Arrange
        activity_name = "Art Club"
        email = "reagain@mergington.edu"

        # Act - Sign up
        response_signup_1 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Act - Remove
        response_remove = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Act - Sign up again
        response_signup_2 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response_signup_1.status_code == 200
        assert response_remove.status_code == 200
        assert response_signup_2.status_code == 200

    def test_verify_participant_removed_from_list(self):
        """Test that removed participant is no longer in activity participants list"""
        # Arrange
        activity_name = "Drama Club"
        email = "verify_removal@mergington.edu"
        # Sign up the participant
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act - Remove the participant
        client.delete(f"/activities/{activity_name}/participants/{email}")
        # Get updated activities list
        response = client.get("/activities")
        participants_list = response.json()[activity_name]["participants"]

        # Assert
        assert email not in participants_list


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_redirect(self):
        """Test that root path redirects to index.html"""
        # Arrange
        expected_status = 307
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == expected_status
        assert response.headers["location"] == expected_location
