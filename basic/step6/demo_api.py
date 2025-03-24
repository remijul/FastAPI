import requests

base_url = "http://localhost:8000"

# Get API information
response = requests.get(f"{base_url}/")
print("API Info:", response.json())

# Get model information
response = requests.get(f"{base_url}/info")
print("Model Info:", response.json())

# Make a prediction
data = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}
response = requests.post(f"{base_url}/predict", json=data)
print("Prediction:", response.json())