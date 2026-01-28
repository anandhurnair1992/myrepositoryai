"""
Tests for the FastAPI application endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    initial_state = {
        "Basketball": {
            "description": "Team basketball practice and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis training and friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater production and acting workshops",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture classes",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["ryan@mergington.edu", "sophia@mergington.edu"]
        },
        "Math Club": {
            "description": "Advanced mathematics problem-solving and competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Store current state
    yield
    
    # Restore initial state
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Test cases for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        """Test that get_activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert "Drama Club" in data
    
    def test_get_activities_contains_required_fields(self):
        """Test that each activity contains required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_has_participants(self):
        """Test that activities have at least one participant"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert len(activity_details["participants"]) > 0


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        email = "newstudent@mergington.edu"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Basketball"]["participants"])
        
        # Sign up
        response = client.post(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 200
        
        # Check that participant was added
        response = client.get("/activities")
        new_count = len(response.json()["Basketball"]["participants"])
        assert new_count == initial_count + 1
        assert email in response.json()["Basketball"]["participants"]
    
    def test_signup_nonexistent_activity(self, reset_activities):
        """Test signup for activity that doesn't exist"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email(self, reset_activities):
        """Test that duplicate email signup is rejected"""
        response = client.post(
            "/activities/Basketball/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_different_activities(self, reset_activities):
        """Test that same student can sign up for multiple activities"""
        email = "newstudent@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(f"/activities/Basketball/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(f"/activities/Tennis Club/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball"]["participants"]
        assert email in data["Tennis Club"]["participants"]


class TestRootRedirect:
    """Test cases for root endpoint"""
    
    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
