import requests

# API endpoint
url = "http://localhost:8000/root"

# Make predictions
response = requests.post(url)#, json=setosa_sample)

print(response)#.json())
