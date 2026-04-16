"""
Integration tests for full workflows using AAA pattern.
"""

import pytest


class TestIntegration:
    """Test suite for complete user workflows."""
    
    def test_full_signup_and_unregister_workflow(self, client, reset_activities):
        """Test complete workflow: signup -> verify -> unregister -> verify."""
        # Arrange
        activity_name = "Programming Class"
        email = "integration.test@mergington.edu"
        
        # Act 1: Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert 1: Signup succeeds
        assert signup_response.status_code == 200
        
        # Act 2: Verify student appears in activity
        get_response1 = client.get("/activities")
        data1 = get_response1.json()
        
        # Assert 2: Student is listed
        assert email in data1[activity_name]["participants"]
        initial_count = len(data1[activity_name]["participants"])
        
        # Act 3: Unregister student
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert 3: Unregister succeeds
        assert unregister_response.status_code == 200
        
        # Act 4: Verify student removed from activity
        get_response2 = client.get("/activities")
        data2 = get_response2.json()
        
        # Assert 4: Student is no longer listed
        assert email not in data2[activity_name]["participants"]
        assert len(data2[activity_name]["participants"]) == initial_count - 1
    
    def test_signup_multiple_activities_same_student(self, client, reset_activities):
        """Test that a student can sign up for multiple activities."""
        # Arrange
        email = "multi.activity@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        activity3 = "Gym Class"
        
        # Act - signup for multiple activities
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        response3 = client.post(
            f"/activities/{activity3}/signup",
            params={"email": email}
        )
        
        # Assert - all signups succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        # Assert - student appears in all activities
        get_response = client.get("/activities")
        data = get_response.json()
        assert email in data[activity1]["participants"]
        assert email in data[activity2]["participants"]
        assert email in data[activity3]["participants"]
    
    def test_activities_availability_updates_correctly(self, client, reset_activities):
        """Test that availability count updates as students sign up/unregister."""
        # Arrange
        activity_name = "Chess Club"
        max_participants = 12
        initial_participants = 2
        email = "availability.test@mergington.edu"
        
        # Act 1: Get initial availability
        response1 = client.get("/activities")
        data1 = response1.json()
        initial_availability = (
            data1[activity_name]["max_participants"] - 
            len(data1[activity_name]["participants"])
        )
        
        # Assert 1
        assert initial_availability == max_participants - initial_participants
        
        # Act 2: Signup a student
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response2 = client.get("/activities")
        data2 = response2.json()
        availability_after_signup = (
            data2[activity_name]["max_participants"] - 
            len(data2[activity_name]["participants"])
        )
        
        # Assert 2: Availability decreased by 1
        assert availability_after_signup == initial_availability - 1
        
        # Act 3: Unregister the student
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        response3 = client.get("/activities")
        data3 = response3.json()
        availability_after_unregister = (
            data3[activity_name]["max_participants"] - 
            len(data3[activity_name]["participants"])
        )
        
        # Assert 3: Availability returned to original
        assert availability_after_unregister == initial_availability
