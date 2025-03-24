import requests
import sys

print("=== Authentication Test ===")

# Test with valid data
response = requests.post(
    "http://localhost:8000/auth/token",
    data={
        "username": "user@example.com",
        "password": "SecureP@ss123"
    }
)

print("Authentication Response Status:", response.status_code)
print("Authentication Response Body:", response.text)

# Check if authentication was successful
if response.status_code == 200:
    try:
        token_data = response.json()
        if "access_token" in token_data:
            token = token_data["access_token"]
            print("Token received:", token[:10] + "...")  # Show just the beginning
        else:
            print("ERROR: Response doesn't contain access_token key.")
            print("Response keys:", token_data.keys())
            sys.exit(1)
    except ValueError as e:
        print("ERROR: Could not parse JSON response:", e)
        sys.exit(1)
else:
    print("Authentication failed with status code:", response.status_code)
    print("Make sure you've created a user with email 'user@example.com' and password 'SecureP@ss123'")
    sys.exit(1)

# Test with valid data
response = requests.post(
    "http://localhost:8000/auth/token",
    data={
        "username": "user@example.com",
        "password": "SecureP@ss123"
    }
)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test with valid prediction data
valid_data = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}

response = requests.post(
    "http://localhost:8000/predict",
    headers=headers,
    json=valid_data
)

print("Valid data response:", response.status_code)
print(response.json())

# Test with invalid data (negative value)
invalid_data = {
    "sepal_length": -5.1,  # Negative value, should be rejected
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}

response = requests.post(
    "http://localhost:8000/predict",
    headers=headers,
    json=invalid_data
)

print("Invalid data response:", response.status_code)
print(response.json())

# Test with biologically implausible data
implausible_data = {
    "sepal_length": 5.1,
    "sepal_width": 12.0,  # Too wide compared to length
    "petal_length": 1.4,
    "petal_width": 0.2
}

response = requests.post(
    "http://localhost:8000/predict",
    headers=headers,
    json=implausible_data
)

print("Implausible data response:", response.status_code)
print(response.json())