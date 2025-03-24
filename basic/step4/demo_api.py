import requests

base_url = "http://localhost:8000"

# Get model information
response = requests.get(f"{base_url}/info")
print("Model info:", response.json())

# Make a prediction
input_data = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}
response = requests.post(f"{base_url}/predict", json=input_data)
print("Prediction:", response.json())

# Make a prediction with array format
array_data = {
    "features": [5.1, 3.5, 1.4, 0.2]
}
response = requests.post(f"{base_url}/predict/array", json=array_data)
print("Array prediction:", response.json())

# Use a specific model version
response = requests.get(f"{base_url}/info?version=v1")
print("Model v1 info:", response.json())