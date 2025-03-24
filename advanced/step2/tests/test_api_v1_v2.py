import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.utils.security import get_current_active_user

# Create a mock user object
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

# Test v1 prediction
def test_v1_prediction():
    data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/v1/predict", json=data)
    assert response.status_code == 200
    assert "prediction" in response.json()
    #assert "model_version" in response.json()  # Check for model_version

# Test v2 prediction
def test_v2_prediction():
    data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
        "include_importance": True
    }
    response = client.post("/v2/predict", json=data)
    assert response.status_code == 200
    result = response.json()
    assert "prediction" in result
    #assert "model_version" in result  # Check for model_version
    #assert result["model_version"] == "v2"  # Confirm it's v2
    assert "feature_importance" in result  # Check for v2-specific field