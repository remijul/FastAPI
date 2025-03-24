import requests

base_url = "http://localhost:8000"

# Get overall metrics
response = requests.get(f"{base_url}/metrics")
print("API Metrics:", response.json())

# Get recent requests
response = requests.get(f"{base_url}/metrics/requests?limit=5")
print("Recent Requests:", response.json())

# Get recent errors
response = requests.get(f"{base_url}/metrics/errors?limit=5")
print("Recent Errors:", response.json())