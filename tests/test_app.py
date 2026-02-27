import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


# fixtures
@pytest.fixture
def client():
    """Return a TestClient instance for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Save and restore global activities between tests.

    This keeps each test independent by resetting the in-memory state.
    """
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities(client):
    # Arrange: nothing to do beyond fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data


def test_signup_success(client):
    # Arrange
    activity = "Chess Club"
    email = "new@student.com"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate(client):
    # Arrange
    activity = "Chess Club"
    # choose an email that isn't already in the default list
    email = "dupuser@mergington.edu"

    # Act
    first = client.post(f"/activities/{activity}/signup", params={"email": email})
    second = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert first.status_code == 200
    assert second.status_code == 400
    assert "already signed up" in second.json()["detail"]


def test_signup_nonexistent_activity(client):
    # Arrange
    activity = "Nonexistent"
    email = "someone@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_success(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_registered(client):
    # Arrange
    activity = "Chess Club"
    email = "not@there.com"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_nonexistent_activity(client):
    # Arrange
    activity = "Invalid"
    email = "someone@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
