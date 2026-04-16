"""
Tests for DELETE /activities/{activity_name}/unregister endpoint using AAA pattern.
"""

import pytest


class TestUnregister:
    """Test suite for student unregister functionality."""
    
    def test_unregister_valid_student_succeeds(self, client, reset_activities):
        """Test that a valid unregister returns success."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
    
    def test_unregister_removes_student_from_participants(self, client, reset_activities):
        """Test that a student is actually removed from the participants list."""
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"
        
        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity_name]["participants"]
        assert len(data[activity_name]["participants"]) == 1
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that unregister from non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_non_registered_student_returns_400(self, client, reset_activities):
        """Test that unregistering a non-registered student returns 400."""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"  # Not signed up
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_with_special_characters_in_email(self, client, reset_activities):
        """Test that unregister works with emails containing special characters."""
        # Arrange
        activity_name = "Programming Class"
        email = "test.student+special@mergington.edu"
        # First signup the student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        response_get = client.get("/activities")
        data = response_get.json()
        assert email not in data[activity_name]["participants"]
    
    def test_unregister_then_reregister_same_student(self, client, reset_activities):
        """Test that a student can unregister and then re-register."""
        # Arrange
        activity_name = "Gym Class"
        email = "student@mergington.edu"
        
        # Act - signup
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response_get1 = client.get("/activities")
        data1 = response_get1.json()
        count_after_signup = len(data1[activity_name]["participants"])
        
        # Act - unregister
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        response_get2 = client.get("/activities")
        data2 = response_get2.json()
        count_after_unregister = len(data2[activity_name]["participants"])
        
        # Act - re-register
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response_get3 = client.get("/activities")
        data3 = response_get3.json()
        count_after_reregister = len(data3[activity_name]["participants"])
        
        # Assert
        assert count_after_signup == count_after_unregister + 1
        assert count_after_reregister == count_after_signup
        assert email in data3[activity_name]["participants"]
