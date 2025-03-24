import requests
import time

# First, make sure your API is running
# Then run this script to register a user

# Wait for API to be ready
print("Waiting for API to start...")
time.sleep(2)

# Try to access API
try:
    health_check = requests.get("http://localhost:8000/info")
    print(f"API Health check: {health_check.status_code}")
except Exception as e:
    print(f"Error accessing API: {e}")
    exit(1)

# Register a new user
print("\nRegistering new user...")
response = requests.post(
    "http://localhost:8000/auth/register",
    json={
        "email": "user@example.com",
        "username": "testuser",
        "password": "SecureP@ss123",
        "role": "user"
    }
)

print(f"Registration Response: {response.status_code}")
print(response.json())

if response.status_code == 201:
    print("\nUser registered successfully!")
    
    # Now try to authenticate
    print("\nAuthenticating user...")
    auth_response = requests.post(
        "http://localhost:8000/auth/token",
        data={
            "username": "user@example.com",
            "password": "SecureP@ss123"
        }
    )
    
    print(f"Authentication Response: {auth_response.status_code}")
    print(auth_response.json())