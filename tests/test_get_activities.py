"""
Tests for GET /activities endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Test suite for retrieving all activities."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities."""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(activity in data for activity in expected_activities)
    
    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        """Test that activities have the correct data structure."""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_get_activities_shows_correct_participant_count(self, client, reset_activities):
        """Test that activities display correct participant counts."""
        # Arrange + Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data["Chess Club"]["participants"]) == 2
        assert len(data["Programming Class"]["participants"]) == 2
        assert len(data["Gym Class"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_get_activities_with_empty_participants(self, client, reset_activities):
        """Test that activities can show with no participants."""
        # Arrange
        activities_to_test = reset_activities
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert - verify participants field exists and is a list (even if empty)
        for activity_data in data.values():
            assert isinstance(activity_data["participants"], list)
