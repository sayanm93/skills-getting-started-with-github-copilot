"""
Tests for POST /activities/{activity_name}/signup endpoint using AAA pattern.
"""

import pytest


class TestSignup:
    """Test suite for student signup functionality."""
    
    def test_signup_valid_student_succeeds(self, client, reset_activities):
        """Test that a valid signup returns success."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_adds_student_to_participants(self, client, reset_activities):
        """Test that a student is actually added to the participants list."""
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity_name]["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signup to non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """Test that duplicate signup returns 400 error."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Test that signup works with emails containing special characters."""
        # Arrange
        activity_name = "Gym Class"
        email = "test.student+special@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        response_get = client.get("/activities")
        data = response_get.json()
        assert email in data[activity_name]["participants"]
    
    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """Test that multiple students can sign up for the same activity."""
        # Arrange
        activity_name = "Programming Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        initial_count = 2  # Already has 2 participants
        
        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{activity_name}/signup", params={"email": email2})
        
        # Assert
        response = client.get("/activities")
        data = response.json()
        assert len(data[activity_name]["participants"]) == initial_count + 2
        assert email1 in data[activity_name]["participants"]
        assert email2 in data[activity_name]["participants"]
    
    def test_signup_activity_name_case_sensitive(self, client, reset_activities):
        """Test that activity name matching is case-sensitive."""
        # Arrange
        email = "student@mergington.edu"
        
        # Act - try with different casing
        response = client.post(
            "/activities/chess%20club/signup",  # lowercase
            params={"email": email}
        )
        
        # Assert - should fail because "chess club" != "Chess Club"
        assert response.status_code == 404
