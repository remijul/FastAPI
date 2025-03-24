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