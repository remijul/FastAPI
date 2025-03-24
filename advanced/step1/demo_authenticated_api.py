import requests

# Authenticate and get token
response = requests.post(
    "http://localhost:8000/auth/token",
    data={
        "username": "user@example.com",  # Using email as username
        "password": "SecureP@ss123"
    }
)

print("Authentication Response:", response.status_code)
token_data = response.json()
print(token_data)

# Save token for subsequent requests
access_token = token_data["access_token"]

# Use the token for authenticated requests
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Get user info
response = requests.get(
    "http://localhost:8000/auth/me",
    headers=headers
)

print("User Info Response:", response.status_code)
print(response.json())

# Make a prediction (authenticated)
prediction_response = requests.post(
    "http://localhost:8000/predict",
    headers=headers,
    json={
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
)

print("Prediction Response:", prediction_response.status_code)
print(prediction_response.json())

# Try to access admin endpoint (will fail for regular user)
admin_response = requests.get(
    "http://localhost:8000/admin",
    headers=headers
)

print("Admin Access Response:", admin_response.status_code)
print(admin_response.json())