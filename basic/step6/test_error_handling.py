import requests

base_url = "http://localhost:8000"

# Test health endpoint
print("Testing health endpoint:")
response = requests.get(f"{base_url}/health")
print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test non-existent model version
print("Testing non-existent model version:")
response = requests.get(f"{base_url}/info?version=non_existent")
print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test rate limiting (in a loop)
print("Testing rate limiting (sending many requests):")
for i in range(65):  # More than our rate limit (60 per minute)
    response = requests.get(f"{base_url}/info")
    print(f"Request {i+1}: Status code: {response.status_code}")
    if response.status_code == 429:
        print(f"Rate limited after {i+1} requests")
        print(f"Response: {response.json()}")
        break