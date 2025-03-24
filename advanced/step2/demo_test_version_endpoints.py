import requests
import time

# Base URL
BASE_URL = "http://localhost:8000"

# Step 1: Check if the API is running
try:
    root_response = requests.get(f"{BASE_URL}/")
    print(f"API Root Response: {root_response.status_code}")
    print(f"Message: {root_response.json().get('message', 'No message')}")
except Exception as e:
    print(f"Error connecting to API: {e}")
    print("Make sure the API is running at http://localhost:8000")
    exit(1)

# Step 2: Authenticate to get a token
print("\nAuthenticating...")
try:
    auth_response = requests.post(
        f"{BASE_URL}/auth/token",
        data={
            "username": "user@example.com",  # Use your registered email
            "password": "SecureP@ss123"      # Use your registered password
        }
    )
    
    if auth_response.status_code == 200:
        token_data = auth_response.json()
        token = token_data.get("access_token")
        if token:
            print(f"Authentication successful! Token: {token[:10]}...")
        else:
            print(f"Token not found in response: {token_data}")
            exit(1)
    else:
        print(f"Authentication failed: {auth_response.status_code}")
        print(f"Response: {auth_response.text}")
        print("\nPlease run init_db.py to create a user or register a new user.")
        exit(1)
except Exception as e:
    print(f"Error during authentication: {e}")
    exit(1)

# Step 3: Test versioned endpoints with authentication
print("\nTesting versioned endpoints:")

# Test headers with authentication
headers = {"Authorization": f"Bearer {token}"}

# Test v1 info endpoint
try:
    print("\n1. Testing V1 Info endpoint...")
    v1_info = requests.get(f"{BASE_URL}/v1/info")
    print(f"V1 Info Status: {v1_info.status_code}")
    print(f"V1 Info Response: {v1_info.text}")
except Exception as e:
    print(f"Error testing V1 Info: {e}")

# Test v2 info endpoint
try:
    print("\n2. Testing V2 Info endpoint...")
    v2_info = requests.get(f"{BASE_URL}/v2/info")
    print(f"V2 Info Status: {v2_info.status_code}")
    print(f"V2 Info Response: {v2_info.text}")
except Exception as e:
    print(f"Error testing V2 Info: {e}")

# Test v1 prediction with authentication
try:
    print("\n3. Testing V1 Prediction endpoint...")
    v1_prediction = requests.post(
        f"{BASE_URL}/v1/predict",
        json={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        },
        headers=headers
    )
    print(f"V1 Prediction Status: {v1_prediction.status_code}")
    print(f"V1 Prediction Response: {v1_prediction.text}")
except Exception as e:
    print(f"Error testing V1 Prediction: {e}")

# Test v2 prediction with authentication
try:
    print("\n4. Testing V2 Prediction endpoint...")
    v2_prediction = requests.post(
        f"{BASE_URL}/v2/predict",
        json={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
            "include_importance": True
        },
        headers=headers
    )
    print(f"V2 Prediction Status: {v2_prediction.status_code}")
    print(f"V2 Prediction Response: {v2_prediction.text}")
except Exception as e:
    print(f"Error testing V2 Prediction: {e}")

print("\nTesting complete!")