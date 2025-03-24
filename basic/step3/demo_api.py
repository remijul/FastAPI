import requests

# API endpoint
url = "http://localhost:8000/predict"

# Sample data for a setosa iris
setosa_sample = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}

# Sample data for a versicolor iris
versicolor_sample = {
    "sepal_length": 6.0,
    "sepal_width": 2.7,
    "petal_length": 4.2,
    "petal_width": 1.3
}

# Make predictions
setosa_response = requests.post(url, json=setosa_sample)
versicolor_response = requests.post(url, json=versicolor_sample)

print("Setosa prediction:", setosa_response.json())
print("Versicolor prediction:", versicolor_response.json())

# Batch prediction
batch_url = "http://localhost:8000/predict/batch"
batch_data = [setosa_sample, versicolor_sample]
batch_response = requests.post(batch_url, json=batch_data)

print("Batch predictions:")
for i, pred in enumerate(batch_response.json()):
    print(f"Sample {i+1}: {pred}")