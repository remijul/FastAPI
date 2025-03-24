import requests
import time

# Wait a moment to ensure the API is running
print("Connecting to the API...")
time.sleep(1)

# 1. Check if API is available
try:
    health_check = requests.get("http://localhost:8000/info")
    print(f"API Health check: {health_check.status_code}")
except Exception as e:
    print(f"Error accessing API: {e}")
    exit(1)

# 2. Register a new user
print("\nRegistering new user...")
response = requests.post(
    "http://localhost:8000/auth/register",
    json={
        "email": "test@example.com",
        "username": "testuser2",
        "password": "SecureP@ss123",
        "role": "user"
    }
)

print(f"Registration Response: {response.status_code}")
if response.status_code == 201:
    print("User registered successfully!")
    user_data = response.json()
    print(f"User ID: {user_data['id']}")
    print(f"Username: {user_data['username']}")
    print(f"Role: {user_data['role']}")
else:
    # The user might already exist, which is fine for this example
    print(f"Registration note: {response.json()}")

# 3. Authenticate and get token
print("\nAuthenticating user...")
auth_response = requests.post(
    "http://localhost:8000/auth/token",
    data={
        "username": "test@example.com",
        "password": "SecureP@ss123"
    }
)

print(f"Authentication Response: {auth_response.status_code}")
if auth_response.status_code == 200:
    token_data = auth_response.json()
    access_token = token_data["access_token"]
    print(f"Received token: {access_token[:10]}...")  # Show just the beginning
    
    # 4. Access protected endpoint
    print("\nAccessing protected endpoint...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    me_response = requests.get(
        "http://localhost:8000/auth/me",
        headers=headers
    )
    
    print(f"Protected endpoint response: {me_response.status_code}")
    if me_response.status_code == 200:
        print("Authentication successful!")
        print(f"User data: {me_response.json()}")
    else:
        print(f"Error: {me_response.json()}")
else:
    print(f"Authentication failed: {auth_response.json()}")