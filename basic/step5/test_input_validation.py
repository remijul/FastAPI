import requests

base_url = "http://localhost:8000"

# Valid input
valid_input = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}

# Invalid inputs to test validation
invalid_inputs = [
    # Negative value
    {
        "sepal_length": -5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    },
    # Missing field
    {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_width": 0.2
    },
    # Extra field
    {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
        "extra_field": "value"
    },
    # Non-numeric value
    {
        "sepal_length": "not_a_number",
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    },
    # Biologically invalid (sepal length < petal length)
    {
        "sepal_length": 1.0,
        "sepal_width": 3.5,
        "petal_length": 5.0,
        "petal_width": 0.2
    }
]

# Test valid input
print("Testing valid input:")
response = requests.post(f"{base_url}/predict", json=valid_input)
print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test invalid inputs
for i, invalid_input in enumerate(invalid_inputs):
    print(f"Testing invalid input {i+1}:")
    response = requests.post(f"{base_url}/predict", json=invalid_input)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()