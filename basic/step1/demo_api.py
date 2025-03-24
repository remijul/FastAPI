import requests

# Root endpoint
response = requests.get("http://localhost:8000/")
print(response.json())

# Name endpoint
response = requests.get("http://localhost:8000/name")
print(response.json())

# Greet endpoint with path parameter
response = requests.get("http://localhost:8000/greet/Eve")
print(response.json())

# Query endpoint with query parameters
response = requests.get("http://localhost:8000/query", params={"name": "Frank", "age": 40})
print(response.json())