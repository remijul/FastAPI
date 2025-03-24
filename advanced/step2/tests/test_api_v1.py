import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.utils.security import get_current_active_user

# Create a mock user object (not a dictionary)
class MockUser:
    def __init__(self):
        self.id = 1
        self.email = "test@example.com"
        self.username = "testuser"
        self.role = "user"
        self.is_active = True

# Override the get_current_active_user dependency
async def override_get_current_user():
    return MockUser()

app.dependency_overrides[get_current_active_user] = override_get_current_user
client = TestClient(app)

# Test root endpoint
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()  # Check for message key

# Test v1 info endpoint
def test_v1_info():
    response = client.get("/v1/info")
    assert response.status_code == 200
    assert response.json()["version"] == "1.0"

# Test v1 prediction with valid data
def test_predict_valid():
    data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/v1/predict", json=data)
    assert response.status_code == 200
    assert "prediction" in response.json()
    #assert "model_version" in response.json()  # Ensure model_version is in the response