import pytest
from fastapi.testclient import TestClient
import numpy as np
import os
import sys

# Add the parent directory to sys.path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

# Create a test client
client = TestClient(app)

def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "docs_url" in response.json()

def test_health():
    """Test the health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_model_info():
    """Test the model info endpoint"""
    response = client.get("/info")
    assert response.status_code == 200
    assert "model_name" in response.json()
    assert "version" in response.json()
    assert "model_type" in response.json()

def test_predict_valid():
    """Test prediction with valid input"""
    data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/predict", json=data)
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert "prediction_index" in response.json()

def test_predict_invalid():
    """Test prediction with invalid input"""
    # Missing field
    data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_width": 0.2
    }
    response = client.post("/predict", json=data)
    assert response.status_code == 422  # Validation error

    # Negative value
    data = {
        "sepal_length": -5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/predict", json=data)
    assert response.status_code in [400, 422]  # Bad request or validation error

def test_batch_predict():
    """Test batch prediction"""
    data = [
        {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        },
        {
            "sepal_length": 6.2,
            "sepal_width": 2.9,
            "petal_length": 4.3,
            "petal_width": 1.3
        }
    ]
    response = client.post("/predict/batch", json=data)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2

def test_array_predict():
    """Test prediction with array input"""
    data = {
        "features": [5.1, 3.5, 1.4, 0.2]
    }
    response = client.post("/predict/array", json=data)
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert "prediction_index" in response.json()

def test_documentation_page():
    """Test the documentation page"""
    response = client.get("/documentation")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]